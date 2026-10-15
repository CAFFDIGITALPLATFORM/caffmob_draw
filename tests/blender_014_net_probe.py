"""Prova D-11 e D-12 (feature 014, T004): conta e download em subprocesso, sem travar o Blender.

Precisa de janela (não roda em --background):
    xvfb-run -a blender --factory-startup --python tests/blender_014_net_probe.py

1. Sobe o servidor falso (`tests/fake_texture_server.py`) com um arquivo de 4 MB e corte no meio do 1º download.
2. Um subprocesso sem `bpy`, rodado com o Python do Blender (`sys.executable`), faz o login por código de dispositivo
   e baixa o arquivo para `.part`, retoma com `Range` depois do corte, confere o sha256 e renomeia. Fala JSON por
   linha no stdout.
3. O thread principal lê o pipe sem bloquear num `bpy.app.timers` e mede o intervalo entre redesenhos da vista
   enquanto o download acontece.
4. Com um segundo subprocesso parado esperando pedidos, fecha o stdin dele (o que acontece quando o Blender sai) e
   confere que ele termina sozinho.
Imprime `PROVA_D11 {...}` e sai com 0 se login, retomada, hash e encerramento funcionarem e nenhum redesenho
passar de 0,25 s.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

import bpy

TESTS = Path(__file__).resolve().parent
SIZE = 4 * 1024 * 1024
REPORT = {}

WORKER = r'''
import hashlib, json, os, sys, time, urllib.request, urllib.error
base, dest, sha, expected = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
def say(**m): sys.stdout.write(json.dumps(m) + "\n"); sys.stdout.flush()
def post(path, body):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read() or b"{}")
st, dev = post("/api/draw/aparelho/codigo", {"client_id": "caffmob-draw"})
say(type="device", user_code=dev["user_code"], url=dev["verification_uri_complete"])
while True:
    time.sleep(dev["interval"])
    st, body = post("/api/draw/aparelho/token", {"client_id": "caffmob-draw", "grant_type": "device_code", "device_code": dev["device_code"]})
    if st == 200: break
    say(type="pending", error=body.get("error"))
token = body["access_token"]; say(type="logged", titular=body["titular"]["nome"])
part = dest + ".part"; attempts = 0
while True:
    offset = os.path.getsize(part) if os.path.exists(part) else 0
    req = urllib.request.Request(base + "/api/draw/v1/texturas/big/imagem?tamanho=trabalho", headers={"Authorization": "Bearer " + token, **({"Range": f"bytes={offset}-"} if offset else {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r, open(part, "ab" if r.status == 206 else "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk: break
                f.write(chunk); say(type="progress", received=f.tell())
        if os.path.getsize(part) < expected: raise ConnectionError("conexão cortada antes do fim")
        h = hashlib.sha256(open(part, "rb").read()).hexdigest()
        if h == sha: os.replace(part, dest); say(type="done", path=dest, resumed_from=offset); break
        say(type="error", code="hash"); break
    except Exception as e:
        attempts += 1; say(type="retry", attempt=attempts, error=type(e).__name__)
        if attempts > 3: say(type="error", code="network"); break
        time.sleep(0.5)
'''

IDLE_WORKER = r'''
import sys
for line in sys.stdin: pass          # sai quando o stdin fecha (Blender saiu)
'''


def start_server(root):
    proc = subprocess.Popen([sys.executable, str(TESTS / "fake_texture_server.py"), "--root", root, "--port", "0",
                             "--cut-after", str(SIZE // 2)], stdout=subprocess.PIPE, text=True)
    line = json.loads(proc.stdout.readline())
    return proc, line["url"]


def make_root():
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, "files"))
    data = os.urandom(SIZE)
    with open(os.path.join(root, "files", "big.jpg"), "wb") as handle:
        handle.write(data)
    sha = hashlib.sha256(data).hexdigest()
    with open(os.path.join(root, "manifest.json"), "w") as handle:
        json.dump({"version": 1, "items": {"big": {"sha256": sha, "bytes": SIZE, "file": "files/big.jpg"}}}, handle)
    return root, sha


def script():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    root, sha = make_root()
    server, url = start_server(root)
    dest = os.path.join(tempfile.mkdtemp(), "big.jpg")
    draws = []

    def on_draw():
        draws.append(time.perf_counter())
    handle = bpy.types.SpaceView3D.draw_handler_add(on_draw, (), 'WINDOW', 'POST_PIXEL')
    worker = subprocess.Popen([sys.executable, "-c", WORKER, url, dest, sha, str(SIZE)], stdout=subprocess.PIPE,
                              stdin=subprocess.PIPE, text=True)
    os.set_blocking(worker.stdout.fileno(), False)
    messages, buffer, t0 = [], "", time.perf_counter()
    try:
        while True:
            try:
                chunk = worker.stdout.read() or ""
            except (BlockingIOError, TypeError):
                chunk = ""
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    messages.append(json.loads(line))
            if worker.poll() is not None:
                os.set_blocking(worker.stdout.fileno(), True)
                for line in (buffer + (worker.stdout.read() or "")).splitlines():
                    if line.strip():
                        messages.append(json.loads(line))
                buffer = ""
                break
            area.tag_redraw()
            if time.perf_counter() - t0 > 60:
                worker.kill()
                break
            yield 0.05
    finally:
        bpy.types.SpaceView3D.draw_handler_remove(handle, 'WINDOW')
    gaps = [b - a for a, b in zip(draws, draws[1:])]
    kinds = [m["type"] for m in messages]
    done = next((m for m in messages if m["type"] == "done"), None)
    REPORT["login"] = "logged" in kinds and "device" in kinds
    REPORT["retomada"] = bool(done) and done.get("resumed_from", 0) > 0 and "retry" in kinds
    REPORT["hash_ok"] = bool(done) and os.path.exists(dest) and not os.path.exists(dest + ".part")
    REPORT["redesenhos"] = len(draws)
    REPORT["maior_intervalo_s"] = round(max(gaps), 3) if gaps else None
    REPORT["tempo_total_s"] = round(time.perf_counter() - t0, 2)
    REPORT["mensagens"] = kinds[:6] + ["…"] + kinds[-2:]

    idle = subprocess.Popen([sys.executable, "-c", IDLE_WORKER], stdin=subprocess.PIPE, text=True)
    yield 0.2
    idle.stdin.close()
    t1 = time.perf_counter()
    while idle.poll() is None and time.perf_counter() - t1 < 3:
        yield 0.05
    REPORT["sai_ao_fechar_stdin"] = idle.poll() is not None
    if idle.poll() is None:
        idle.kill()
    server.terminate()
    server.wait(timeout=5)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        REPORT["erro"] = True
    print("PROVA_D11", REPORT, flush=True)
    ok = (REPORT.get("login") and REPORT.get("retomada") and REPORT.get("hash_ok") and REPORT.get("sai_ao_fechar_stdin")
          and (REPORT.get("maior_intervalo_s") or 9) <= 0.25 and not REPORT.get("erro"))
    os._exit(0 if ok else 1)


bpy.app.timers.register(tick, first_interval=2.0)
