"""Servidor falso do contrato de texturas da CAF Mob (feature 014, T003; interfaces/servidor-texturas.md).

Referência executável do contrato `v1` para os testes e para o time do site. Só biblioteca padrão.

    python3 tests/fake_texture_server.py --root dist/texturas-servidor --port 8765 \\
        --account teste@cafmob.local --download-all

`--root` aponta para a saída do `tools/texturas_importar.py` (`manifest.json` + `files/`). Sem `--root`, o servidor
serve um catálogo de demonstração com duas imagens geradas em memória.

Falhas injetáveis (para os testes de robustez):
- `--approve-after N`: o código de dispositivo é aprovado sozinho depois de N consultas a `/auth/token`
  (padrão 1; 0 = só aprova quando alguém abre `/ativar?code=...`, como o navegador faria);
- `--expire-access N`: o token de acesso vale N requisições autenticadas (depois, 401 `expired_token`);
- `--forbid`: a conta não tem acesso a texturas (403 `not_entitled`);
- `--rate-limit-once`: a primeira requisição de arquivo responde 429 com `Retry-After: 1`;
- `--cut-after BYTES`: a primeira resposta de arquivo corta a conexão depois de BYTES bytes;
- `--no-range`: ignora `Range` (responde 200 sempre);
- `--redirect`: `/file` responde 302 para `/storage/<id>` (endereço "assinado").
"""

import argparse
import hashlib
import json
import os
import secrets
import struct
import sys
import threading
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

CLIENT_ID = "caffmob-draw"


def _png(rgb, size=8):
    """PNG RGB sólido (demonstração sem `--root`)."""
    raw = b"".join(b"\x00" + bytes(rgb) * size for _ in range(size))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


class Store:
    """Estado do servidor: catálogo, contas, códigos e tokens."""

    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.files = {}                      # id → (bytes, content-type) ou (caminho, content-type)
        self.catalog = {"version": 1, "items": {}}
        self.devices = {}                    # device_code → {"user_code", "polls", "approved"}
        self.access = {}                     # access_token → requisições restantes (None = sem limite)
        self.refresh = set()
        self.calls = {"file": 0}
        self.log = []
        self._load()

    def _load(self):
        root = self.args.root
        if root:
            manifest = json.load(open(os.path.join(root, "manifest.json"), encoding="utf-8"))
            for tid, item in manifest["items"].items():
                path = os.path.join(root, item["file"])
                kind = "image/png" if path.lower().endswith(".png") else "image/jpeg"
                self.files[tid] = (path, kind)
                self.catalog["items"][tid] = {"sha256": item["sha256"], "bytes": item["bytes"],
                                              "url": f"/v1/textures/{tid}/file"}
            self.catalog["version"] = manifest.get("version", 1)
            return
        for tid, rgb in (("demo/geral/carvalho", (150, 110, 70)), ("demo/geral/branco", (240, 240, 235))):
            data = _png(rgb, 64)
            self.files[tid] = (data, "image/png")
            self.catalog["items"][tid] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                                          "url": f"/v1/textures/{tid}/file"}

    def file_bytes(self, tid):
        source, kind = self.files[tid]
        if isinstance(source, bytes):
            return source, kind
        with open(source, "rb") as handle:
            return handle.read(), kind

    def new_tokens(self):
        access = secrets.token_urlsafe(24)
        refresh = secrets.token_urlsafe(32)
        limit = self.args.expire_access or None
        self.access[access] = limit
        self.refresh.add(refresh)
        return {"access_token": access, "expires_in": 900, "refresh_token": refresh,
                "account": {"email": self.args.account, "name": self.args.account.split("@")[0]}}


class Handler(BaseHTTPRequestHandler):
    server_version = "FakeCAFMob/1"
    store = None                              # Store, definido em make_server

    # Utilidades ---------------------------------------------------------------------------------------------
    def log_message(self, fmt, *args):        # silencioso; o histórico fica em store.log
        self.store.log.append(f"{self.command} {self.path}")

    def _json(self, status, body, headers=None):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, code, message, headers=None):
        self._json(status, {"error": code, "message": message}, headers)

    def _body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def _authorized(self):
        """True se o Bearer é válido; senão já respondeu 401."""
        header = self.headers.get("Authorization", "")
        token = header[7:] if header.startswith("Bearer ") else ""
        with self.store.lock:
            if token not in self.store.access:
                self._error(401, "invalid_token", "Sessão inválida. Entre de novo com a sua conta CAF Mob.")
                return False
            left = self.store.access[token]
            if left is not None:
                if left <= 0:
                    self._error(401, "expired_token", "Sessão expirada.")
                    return False
                self.store.access[token] = left - 1
        return True

    # Rotas --------------------------------------------------------------------------------------------------
    def do_POST(self):
        path = urlparse(self.path).path
        body = self._body()
        if body is None:
            return self._error(400, "invalid_request", "JSON inválido.")
        routes = {"/v1/auth/device": self._device, "/v1/auth/token": self._token,
                  "/v1/auth/refresh": self._refresh, "/v1/auth/logout": self._logout}
        handler = routes.get(path)
        if handler is None:
            return self._error(404, "not_found", "Rota inexistente.")
        return handler(body)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        if path == "/ativar":
            return self._approve(parse_qs(url.query).get("code", [""])[0])
        if path.startswith("/storage/"):
            return self._file(path[len("/storage/"):], signed=True)
        if not path.startswith("/v1/"):
            return self._error(404, "not_found", "Rota inexistente.")
        if not self._authorized():
            return None
        if path == "/v1/me/entitlements":
            return self._json(200, {"textures": not self.store.args.forbid,
                                    "download_all": bool(self.store.args.download_all) and not self.store.args.forbid,
                                    "catalog_versions": [self.store.catalog["version"]]})
        if path == "/v1/textures/catalog":
            etag = '"' + hashlib.sha256(json.dumps(self.store.catalog, sort_keys=True).encode()).hexdigest()[:16] + '"'
            if self.headers.get("If-None-Match") == etag:
                self.send_response(304)
                self.send_header("ETag", etag)
                self.end_headers()
                return None
            return self._json(200, self.store.catalog, {"ETag": etag})
        if path.startswith("/v1/textures/") and path.endswith("/file"):
            return self._file(path[len("/v1/textures/"):-len("/file")])
        return self._error(404, "not_found", "Rota inexistente.")

    def _device(self, body):
        if body.get("client_id") != CLIENT_ID:
            return self._error(400, "invalid_request", "client_id desconhecido.")
        device = secrets.token_urlsafe(16)
        user = "-".join(secrets.token_hex(2).upper() for _ in range(2))
        with self.store.lock:
            self.store.devices[device] = {"user_code": user, "polls": 0, "approved": False}
        host = f"http://{self.headers.get('Host', '127.0.0.1')}"
        return self._json(200, {"device_code": device, "user_code": user, "verification_uri": f"{host}/ativar",
                                "verification_uri_complete": f"{host}/ativar?code={user}",
                                "expires_in": 600, "interval": 1})

    def _approve(self, user_code):
        with self.store.lock:
            for state in self.store.devices.values():
                if state["user_code"] == user_code:
                    state["approved"] = True
                    break
            else:
                return self._error(404, "not_found", "Código não encontrado.")
        data = "<html><body><p>Conta conectada. Pode voltar ao Blender.</p></body></html>".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        return None

    def _token(self, body):
        state = self.store.devices.get(body.get("device_code", ""))
        if state is None:
            return self._error(400, "expired_token", "Código expirado. Peça um novo.")
        with self.store.lock:
            state["polls"] += 1
            after = self.store.args.approve_after
            if after and state["polls"] >= after:
                state["approved"] = True
            if not state["approved"]:
                return self._error(400, "authorization_pending", "Aguardando a confirmação no navegador.")
            del self.store.devices[body["device_code"]]
            return self._json(200, self.store.new_tokens())

    def _refresh(self, body):
        token = body.get("refresh_token", "")
        with self.store.lock:
            if token not in self.store.refresh:
                return self._error(401, "invalid_token", "Sessão encerrada. Entre de novo.")
            self.store.refresh.discard(token)          # rotação
            return self._json(200, self.store.new_tokens())

    def _logout(self, body):
        with self.store.lock:
            self.store.refresh.discard(body.get("refresh_token", ""))
        self.send_response(204)
        self.end_headers()
        return None

    def _file(self, tid, signed=False):
        if tid not in self.store.files:
            return self._error(404, "not_found", "Textura não disponível no servidor.")
        if self.store.args.forbid and not signed:
            return self._error(403, "not_entitled", "Sua conta não tem acesso a esta textura.")
        with self.store.lock:
            self.store.calls["file"] += 1
            first = self.store.calls["file"] == 1
        if first and self.store.args.rate_limit_once:
            return self._error(429, "rate_limited", "Muitas requisições.", {"Retry-After": "1"})
        if self.store.args.redirect and not signed:
            self.send_response(302)
            self.send_header("Location", f"/storage/{tid}")
            self.end_headers()
            return None
        data, kind = self.store.file_bytes(tid)
        start = 0
        ranged = self.headers.get("Range", "")
        if ranged.startswith("bytes=") and not self.store.args.no_range:
            try:
                start = int(ranged[6:].split("-")[0])
            except ValueError:
                start = 0
        start = min(start, len(data))
        payload = data[start:]
        self.send_response(206 if start else 200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("ETag", '"' + hashlib.sha256(data).hexdigest() + '"')
        self.send_header("Accept-Ranges", "none" if self.store.args.no_range else "bytes")
        if start:
            self.send_header("Content-Range", f"bytes {start}-{len(data) - 1}/{len(data)}")
        self.end_headers()
        cut = self.store.args.cut_after
        if cut and first and not start:
            self.wfile.write(payload[:cut])
            self.wfile.flush()
            self.close_connection = True
            return None
        self.wfile.write(payload)
        return None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default="")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--account", default="teste@cafmob.local")
    parser.add_argument("--download-all", action="store_true")
    parser.add_argument("--approve-after", type=int, default=1)
    parser.add_argument("--expire-access", type=int, default=0)
    parser.add_argument("--forbid", action="store_true")
    parser.add_argument("--rate-limit-once", action="store_true")
    parser.add_argument("--cut-after", type=int, default=0)
    parser.add_argument("--no-range", action="store_true")
    parser.add_argument("--redirect", action="store_true")
    return parser.parse_args(argv)


def make_server(args):
    """Servidor pronto para `serve_forever()` (porta 0 = livre; a porta real fica em `server.server_address`)."""
    handler = type("BoundHandler", (Handler,), {"store": Store(args)})
    return ThreadingHTTPServer((args.host, args.port), handler)


def main(argv=None):
    args = parse_args(argv)
    server = make_server(args)
    host, port = server.server_address[:2]
    print(json.dumps({"event": "listening", "url": f"http://{host}:{port}"}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
