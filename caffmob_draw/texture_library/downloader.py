"""Subprocesso de rede das texturas (feature 014, T020; D-11, D-12). Sem `bpy`: roda com o Python do Blender.

    <python do Blender> downloader.py --base https://servidor/v1 --ua "CAFFMobDraw/1 Blender/5.2"

Lê uma mensagem JSON por linha no stdin e responde uma por linha no stdout (`download_core.encode`):
- `token` (value): token de acesso usado nas próximas chamadas;
- `get` (id, url, dest, sha256, bytes): baixa para `<dest>.part`, retoma com `Range` depois de uma queda, confere o
  sha256 e renomeia atômico; responde `progress`, `done` ou `error`. Com 401, pede `need_token` e espera o novo;
- `request` (rid, method, path, body, auth): chamada JSON ao servidor (login, renovação, permissões, catálogo);
  responde `reply` (rid, status, body, retry_after). `status` null = sem rede;
- `cancel` (id): para o download e deixa o `.part` para retomar depois;
- `quit`, ou o stdin fechado (o Blender saiu): cancela tudo e termina.

Os downloads correm em threads deste processo, longe do Blender; o limite de paralelos fica com a fila do lado do
Blender (`download_core.Queue`). O `Authorization` não vai num redirecionamento para outro domínio (endereço
assinado do armazenamento).
"""

import argparse
import hashlib
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import download_core  # noqa: E402  (este arquivo roda fora do pacote)

CHUNK = 64 * 1024
TIMEOUT = 10
IMAGE_TIMEOUT = 60
PROGRESS_EVERY = 0.15
TOKEN_WAIT = 30.0


class Worker:
    def __init__(self, base, user_agent):
        self.base = base.rstrip("/")
        self.user_agent = user_agent
        self.token = ""
        self.token_event = threading.Event()
        self.cancelled = set()
        self.out_lock = threading.Lock()
        self.state_lock = threading.Lock()

    # Saída ---------------------------------------------------------------------------------------------------
    def say(self, **message):
        with self.out_lock:
            try:
                sys.stdout.write(download_core.encode(message))
                sys.stdout.flush()
            except (BrokenPipeError, ValueError):       # o Blender fechou o pipe: nada a fazer
                pass

    # HTTP ----------------------------------------------------------------------------------------------------
    def url(self, path):
        if path.startswith(("http://", "https://")):
            return path
        if path.startswith("/v1/") and self.base.endswith("/v1"):
            path = path[3:]
        return self.base + ("" if path.startswith("/") else "/") + path

    def opener(self, auth_url):
        token, base = self.token, self.base

        class Redirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                new = super().redirect_request(req, fp, code, msg, headers, newurl)
                if new is not None and req.get_header("Authorization") and download_core.same_origin(base, newurl):
                    new.add_unredirected_header("Authorization", "Bearer " + token)
                return new
        return urllib.request.build_opener(Redirect)

    def build(self, url, method="GET", body=None, auth=True, extra=None, form=False):
        data = (urllib.parse.urlencode(body) if form else json.dumps(body)).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Accept", "application/json")
        if data is not None:
            request.add_header("Content-Type", "application/x-www-form-urlencoded" if form else "application/json")
        if auth and self.token and download_core.same_origin(self.base, url):
            request.add_unredirected_header("Authorization", "Bearer " + self.token)   # nunca segue o redirect
        for key, value in (extra or {}).items():
            request.add_header(key, value)
        return request

    @staticmethod
    def _json(raw):
        try:
            return json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            return {"error": "invalid_json"}

    def request(self, rid, method, path, body, auth, headers=None, form=False):
        # (063 RF-10; D-04) As esperas acontecem somente neste subprocesso.
        url, attempt = self.url(path), 0
        while not self.is_cancelled(rid):
            response_headers = {}
            try:
                with self.opener(url).open(self.build(url, method, body, auth, headers, form), timeout=TIMEOUT) as response:
                    status, payload = response.status, self._json(response.read())
                    response_headers = dict(response.headers)
            except urllib.error.HTTPError as exc:
                status, payload = exc.code, self._json(exc.read())
                response_headers = dict(exc.headers)
            except (urllib.error.URLError, OSError, ValueError) as exc:
                status, payload = None, {"error": "network", "message": str(exc)}
            attempt += 1
            delay = download_core.retry_delay(attempt, status, response_headers.get("Retry-After"))
            if delay is None:
                return self.say(type="reply", rid=rid, status=status, body=payload, headers=response_headers,
                                etag=response_headers.get("ETag"), retry_after=response_headers.get("Retry-After"))
            time.sleep(delay)

    # Download ------------------------------------------------------------------------------------------------
    def is_cancelled(self, item_id):
        with self.state_lock:
            return item_id in self.cancelled or "*" in self.cancelled

    def wait_token(self, item_id, old):
        self.token_event.clear()
        self.say(type="need_token", id=item_id)
        deadline = time.monotonic() + TOKEN_WAIT
        while time.monotonic() < deadline and not self.is_cancelled(item_id):
            if self.token_event.wait(0.2) and self.token and self.token != old:
                return True
        return False

    def _fetch(self, item, part):
        """Uma tentativa. Devolve None quando o `.part` ficou completo; senão levanta."""
        expected = int(item.get("bytes") or 0)
        offset = download_core.resume_offset(os.path.getsize(part) if os.path.exists(part) else 0, expected)
        url = self.url(item["url"])
        extra = dict(item.get("headers") or {})
        if offset:
            extra["Range"] = "bytes={}-".format(offset)
        if item.get("etag"):
            extra["If-None-Match"] = item["etag"]
        with self.opener(url).open(self.build(url, extra=extra), timeout=IMAGE_TIMEOUT) as response, \
                open(part, "ab" if response.status == 206 and offset else "wb") as handle:
            last = 0.0
            while True:
                if self.is_cancelled(item["id"]):
                    raise InterruptedError
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                handle.write(chunk)
                now = time.monotonic()
                if now - last >= PROGRESS_EVERY:
                    last = now
                    self.say(type="progress", id=item["id"], received=handle.tell(),
                             total=expected or int(response.headers.get("Content-Length") or 0))
            item["response_headers"] = dict(response.headers)
        if expected and os.path.getsize(part) < expected:
            raise ConnectionError("conexão cortada antes do fim")      # fim de arquivo sem exceção (prova T004)

    def download(self, item):
        item_id, dest = item["id"], item["dest"]
        part = dest + ".part"
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        attempt, hash_retry, token_retry = 0, False, False
        if not item.get("sha256") and os.path.isfile(dest + ".etag") and os.path.isfile(dest):
            with open(dest + ".etag", encoding="utf-8") as handle:
                item["etag"] = handle.read()
            with open(dest, "rb") as handle:
                if hashlib.sha256(handle.read()).hexdigest() != item["etag"].strip('"'):
                    item.pop("etag", None)
        while True:
            try:
                if self.is_cancelled(item_id):
                    raise InterruptedError
                self._fetch(item, part)
                with open(part, "rb") as handle:
                    digest = hashlib.sha256(handle.read()).hexdigest()
                headers = item.get("response_headers", {})
                etag = headers.get("ETag", "")
                if not download_core.verify(digest, item.get("sha256") or etag.strip('"')):
                    os.remove(part)
                    if hash_retry:
                        return self.say(type="error", id=item_id, code="hash", status=None,
                                        message="Arquivo baixado não confere com o catálogo")
                    hash_retry = True
                    continue
                os.replace(part, dest)
                if etag:
                    with open(dest + ".etag", "w", encoding="utf-8") as handle:
                        handle.write(etag)
                return self.say(type="done", id=item_id, path=dest, headers=headers, etag=etag, sha256=digest)
            except InterruptedError:
                return self.say(type="error", id=item_id, code="cancelled", status=None, message="")
            except urllib.error.HTTPError as exc:
                if exc.code == 304 and item.get("etag") and os.path.isfile(dest):
                    return self.say(type="done", id=item_id, path=dest, headers=dict(exc.headers), etag=item["etag"])
                body = self._json(exc.read())
                if exc.code == 401 and not token_retry:
                    token_retry = True
                    if self.wait_token(item_id, self.token):
                        continue
                if exc.code == 416 and os.path.exists(part):          # `.part` além do arquivo: recomeça
                    os.remove(part)
                    continue
                attempt += 1
                delay = download_core.retry_delay(attempt, exc.code, exc.headers.get("Retry-After"))
                if delay is None:
                    return self.say(type="error", id=item_id, code=body.get("error") or "http", status=exc.code,
                                    message=body.get("message") or "")
                time.sleep(delay)
            except (urllib.error.URLError, OSError, ValueError) as exc:
                attempt += 1
                delay = download_core.retry_delay(attempt, None)
                if delay is None:
                    return self.say(type="error", id=item_id, code="network", status=None, message=str(exc))
                time.sleep(delay)

    # Laço principal ------------------------------------------------------------------------------------------
    def handle(self, message):
        kind = message["type"]
        if kind == "token":
            self.token = str(message.get("value") or "")
            self.token_event.set()
        elif kind == "get":
            with self.state_lock:
                self.cancelled.discard(message["id"])
            threading.Thread(target=self.download, args=(message,), daemon=True).start()
        elif kind == "request":
            threading.Thread(target=self.request, daemon=True,
                             args=(message["rid"], message.get("method", "GET"), message["path"],
                                   message.get("body"), bool(message.get("auth", True)),
                                   message.get("headers"), bool(message.get("form")))).start()
        elif kind == "cancel":
            with self.state_lock:
                self.cancelled.add(message["id"])
        elif kind == "quit":
            return False
        return True

    def run(self, stream):
        for line in stream:
            message = download_core.parse_line(line)
            if message is not None and not self.handle(message):
                break
        with self.state_lock:
            self.cancelled.add("*")
        return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--ua", default="CAFFMobDraw")
    args = parser.parse_args(argv)
    return Worker(args.base, args.ua).run(sys.stdin)


if __name__ == "__main__":
    sys.exit(main())
