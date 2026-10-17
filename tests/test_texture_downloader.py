"""Subprocesso de rede das texturas contra o servidor falso (feature 014, T020; D-11, interfaces/servidor-texturas.md).

Sem Blender: roda `caffmob_draw/texture_library/downloader.py` com este Python e conversa por JSON no stdin/stdout.
"""

import hashlib
import json
import os
import select
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import fake_texture_server as fake  # noqa: E402

WORKER = ROOT / "caffmob_draw" / "texture_library" / "downloader.py"
SIZE = 300 * 1024


def make_root():
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "files"))
    data = os.urandom(SIZE)
    with open(os.path.join(root, "files", "big.jpg"), "wb") as handle:
        handle.write(data)
    manifest = {"version": 1, "items": {"big": {"sha256": hashlib.sha256(data).hexdigest(), "bytes": SIZE,
                                                "file": "files/big.jpg"}}}
    with open(os.path.join(root, "manifest.json"), "w") as handle:
        json.dump(manifest, handle)
    return root, manifest["items"]["big"]


class Server:
    def __init__(self, *flags):
        self.root, self.big = make_root()
        self.httpd = fake.make_server(fake.parse_args(["--root", self.root, "--port", "0", *flags]))
        host, port = self.httpd.server_address[:2]
        self.base = f"http://{host}:{port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class Worker:
    def __init__(self, base):
        # select observa o pipe; sem leitura adiantada, nenhuma resposta fica retida no TextIOWrapper.
        self.proc = subprocess.Popen([sys.executable, str(WORKER), "--base", base, "--ua", "CAFFMobDraw/teste"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
        self.rid = 0

    def send(self, **message):
        self.proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))
        self.proc.stdin.flush()

    def wait(self, predicate, timeout=20.0):
        deadline = time.monotonic() + timeout
        seen = []
        while time.monotonic() < deadline:
            ready, _w, _x = select.select([self.proc.stdout], [], [], 0.2)
            if not ready:
                continue
            line = self.proc.stdout.readline()
            if not line:
                break
            message = json.loads(line)
            seen.append(message)
            if predicate(message):
                return message
        raise AssertionError(f"mensagem esperada não chegou; recebidas: {[m.get('type') for m in seen]}")

    def call(self, method, path, body=None, auth=True):
        self.rid += 1
        rid = self.rid
        self.send(type="request", rid=rid, method=method, path=path, body=body, auth=auth, form=not auth and method == "POST")
        reply = self.wait(lambda m: m["type"] == "reply" and m["rid"] == rid)
        return reply["status"], reply["body"]

    def login(self):
        _st, device = self.call("POST", "/api/draw/aparelho/codigo", {"client_id": "caffmob-draw"}, auth=False)
        status, tokens = self.call("POST", "/api/draw/aparelho/token", {"client_id": "caffmob-draw", "grant_type": "urn:ietf:params:oauth:grant-type:device_code", "device_code":
                                                             device["device_code"]}, auth=False)
        assert status == 200, tokens
        self.send(type="token", value=tokens["access_token"])
        return tokens

    def get(self, item_id, dest, sha, size, url=None):
        self.send(type="get", id=item_id, url=url or f"/api/draw/v1/texturas/{item_id}/imagem?tamanho=trabalho", dest=dest, sha256=sha,
                  bytes=size)
        return self.wait(lambda m: m["type"] in ("done", "error") and m.get("id") == item_id, timeout=30)

    def close(self):
        if not self.proc.stdin.closed:
            self.proc.stdin.close()
        self.proc.wait(timeout=5)
        self.proc.stdout.close()


class DownloaderTest(unittest.TestCase):
    def setUp(self):
        self.servers, self.workers = [], []
        self.dest_dir = tempfile.mkdtemp()

    def tearDown(self):
        for worker in self.workers:
            try:
                worker.close()
            except (subprocess.TimeoutExpired, BrokenPipeError):
                worker.proc.kill()
            worker.proc.stdout.close()
        for server in self.servers:
            server.close()
            self.assertTrue(all(not line.split(' ', 1)[-1].startswith('/v1/')
                                for line in server.httpd.RequestHandlerClass.store.log))

    def start(self, *flags):
        server = Server(*flags)
        worker = Worker(server.base)
        self.servers.append(server)
        self.workers.append(worker)
        return server, worker

    def dest(self, name="big.jpg"):
        return os.path.join(self.dest_dir, "sub", name)

    def test_login_e_retomada_depois_do_corte(self):
        server, worker = self.start("--cut-after", str(SIZE // 3))
        worker.login()
        result = worker.get("big", self.dest(), server.big["sha256"], SIZE)
        self.assertEqual(result["type"], "done", result)
        with open(self.dest(), "rb") as handle:
            self.assertEqual(hashlib.sha256(handle.read()).hexdigest(), server.big["sha256"])
        self.assertFalse(os.path.exists(self.dest() + ".part"))
        ranged = [line for line in server.httpd.RequestHandlerClass.store.log if "/imagem" in line]
        self.assertGreaterEqual(len(ranged), 2, "deveria ter retomado numa segunda requisição")

    def test_redirecionamento_e_429(self):
        server, worker = self.start("--redirect", "--rate-limit-once")
        worker.login()
        result = worker.get("big", self.dest(), server.big["sha256"], SIZE)
        self.assertEqual(result["type"], "done", result)

    def test_401_pede_token_novo(self):
        server, worker = self.start("--expire-access", "1")
        tokens = worker.login()
        status, _body = worker.call("GET", "/api/draw/v1/texturas/fabricantes")
        self.assertEqual(status, 200)
        worker.send(type="get", id="big", url="/api/draw/v1/texturas/big/imagem?tamanho=trabalho", dest=self.dest(),
                    sha256=server.big["sha256"], bytes=SIZE)
        worker.wait(lambda m: m["type"] == "need_token" and m["id"] == "big")
        status, fresh = worker.call("POST", "/api/draw/aparelho/token", {"client_id": "caffmob-draw",
                                                                 "grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]},
                                    auth=False)
        self.assertEqual(status, 200)
        worker.send(type="token", value=fresh["access_token"])
        result = worker.wait(lambda m: m["type"] in ("done", "error") and m.get("id") == "big")
        self.assertEqual(result["type"], "done", result)

    def test_404_e_403(self):
        server, worker = self.start()
        worker.login()
        missing = worker.get("nada", self.dest("nada.jpg"), "a" * 64, 10)
        self.assertEqual((missing["type"], missing["code"], missing["status"]), ("error", "not_found", 404))
        server2, worker2 = self.start("--forbid")
        worker2.login()
        denied = worker2.get("big", self.dest("big2.jpg"), server2.big["sha256"], SIZE)
        self.assertEqual((denied["code"], denied["status"]), ("not_entitled", 403))

    def test_hash_errado_descarta(self):
        _server, worker = self.start()
        worker.login()
        result = worker.get("big", self.dest(), "0" * 64, SIZE)
        self.assertEqual((result["type"], result["code"]), ("error", "hash"))
        self.assertFalse(os.path.exists(self.dest()))
        self.assertFalse(os.path.exists(self.dest() + ".part"))

    def test_sem_rede(self):
        worker = Worker("http://127.0.0.1:9")
        self.workers.append(worker)
        status, body = worker.call("GET", "/api/draw/v1/texturas/fabricantes")
        self.assertIsNone(status)
        self.assertEqual(body["error"], "network")

    def test_sai_quando_o_stdin_fecha(self):
        _server, worker = self.start()
        worker.proc.stdin.close()
        self.assertEqual(worker.proc.wait(timeout=5), 0)


if __name__ == "__main__":
    unittest.main()
