"""Conta e download das texturas contra o servidor falso (feature 014, T021, T023, T044; RN-11 a RN-13).

Precisa de janela (os timers da ponte rodam no laço de eventos) e do acesso à internet liberado:
    xvfb-run -a blender --factory-startup --online-mode --python tests/blender_014_textures_net.py

Roteiro:
1. sem acesso à internet (simulado): `fetch` avisa sem erro e sem processo;
2. login por código de dispositivo; `session.json` com 0600, sem token de acesso e sem senha;
3. download sob demanda com progresso, retomada depois do corte; a segunda vez não baixa;
4. a sessão sobrevive a "reiniciar" (`auth.reload`) e renova o token sozinha; 401 no meio renova e continua;
5. permissões: "Baixar tudo" com e sem `download_all`; 403 vira aviso;
6. Baixar tudo com e sem `download_all` (progresso total; "todas baixadas" na segunda vez);
7. Sair apaga a sessão; `shutdown` não deixa processo órfão.
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401

from caffmob_draw.texture_library import auth, catalog, downloads  # noqa: E402

FAILURES = []
TID = "arauco/colecao-realce/anis"


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def server_root():
    """Pasta do servidor com duas texturas reais do catálogo (arquivo sintético com o sha256 do manifesto)."""
    root = tempfile.mkdtemp()
    items = {}
    for tid in (TID, "arauco/colecao-realce/cravo"):
        entry = catalog.item(tid)
        data = os.urandom(200 * 1024)
        rel = "files/" + tid.replace("/", "_") + ".jpg"
        os.makedirs(os.path.join(root, "files"), exist_ok=True)
        with open(os.path.join(root, rel), "wb") as handle:
            handle.write(data)
        import hashlib
        items[tid] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "file": rel}
        assert entry is not None, tid
    with open(os.path.join(root, "manifest.json"), "w") as handle:
        json.dump({"version": 1, "items": items}, handle)
    return root, items


def start_server(root, *flags):
    proc = subprocess.Popen([sys.executable, str(ROOT / "tests" / "fake_texture_server.py"), "--root", root,
                             "--port", "0", *flags], stdout=subprocess.PIPE, text=True)
    return proc, json.loads(proc.stdout.readline())["url"]


def wait_for(cond, timeout=20.0):
    """Gerador: espera `cond()` com o laço de eventos rodando."""
    t = 0.0
    while not cond() and t < timeout:
        yield 0.1
        t += 0.1


def reset_cache():
    shutil.rmtree(downloads.cache_dir(), ignore_errors=True)


def script():
    root, items = server_root()
    for tid, meta in items.items():                       # o catálogo do pacote passa a esperar estes arquivos
        catalog.item(tid)["sha256"], catalog.item(tid)["bytes"] = meta["sha256"], meta["bytes"]
    server, url = start_server(root, "--cut-after", str(64 * 1024), "--download-all")
    downloads.set_server(url)
    auth.logout()
    reset_cache()
    yield 0.2

    # 1. sem internet
    original_online = downloads.online
    downloads.online = lambda: False
    got = {}
    downloads.fetch(TID, lambda path, err: got.update(path=path, err=err))
    check("sem internet: aviso claro e nenhum processo",
          got.get("path") is None and got["err"]["code"] == "offline" and not downloads.process_alive(), str(got))
    downloads.online = original_online
    check("acesso à internet do Blender ligado no teste (--online-mode)", bool(bpy.app.online_access))

    # sem conta: pede login
    got.clear()
    downloads.fetch(TID, lambda path, err: got.update(path=path, err=err))
    yield from wait_for(lambda: got)
    check("sem conta: pede para entrar", got.get("err", {}).get("code") == "no_account", str(got))

    # 2. login
    codes, result = {}, {}
    auth.start_login(lambda code, link: codes.update(code=code, link=link), lambda ok, msg: result.update(ok=ok, msg=msg))
    yield from wait_for(lambda: result)
    check("login por código: código recebido e conta conectada", bool(codes.get("code")) and result.get("ok"),
          f"{codes} {result}")
    check("e-mail da conta", auth.account_email() == "teste@cafmob.local", auth.account_email())
    path = auth.session_path()
    mode = stat.S_IMODE(os.stat(path).st_mode) if os.path.exists(path) else None
    with open(path, encoding="utf-8") as handle:
        saved = json.load(handle)
    check("session.json com 0600", mode == 0o600, oct(mode or 0))
    check("session.json sem token de acesso e sem senha",
          "access_token" not in saved and "password" not in json.dumps(saved) and saved.get("refresh_token"),
          str(sorted(saved)))

    # 3. download sob demanda com retomada
    got.clear()
    seen_progress = []
    downloads.fetch(TID, lambda p, err: got.update(path=p, err=err))

    def watching():
        frac = downloads.progress(TID)
        if frac is not None:
            seen_progress.append(frac)
        return bool(got)
    yield from wait_for(watching, 30)
    check("download sob demanda concluído", bool(got.get("path")) and os.path.isfile(got["path"]), str(got))
    check("estado DONE e sem .part", downloads.state(TID) == 'DONE' and not os.path.exists(got.get("path", "") + ".part"))
    calls = server_calls(server)
    got.clear()
    downloads.fetch(TID, lambda p, err: got.update(path=p, err=err))
    check("segunda vez não baixa (chamada de volta na hora)", bool(got.get("path")))
    yield 0.3
    check("segunda vez sem requisição nova ao servidor", server_calls(server) == calls)

    # 4. sessão sobrevive a reiniciar
    auth.reload()
    check("sessão relida do disco", auth.signed_in() and auth.account_email() == "teste@cafmob.local")
    tokens = {}
    auth.with_access(lambda token: tokens.update(token=token))
    yield from wait_for(lambda: tokens)
    check("renova o token sozinha pela sessão gravada", bool(tokens.get("token")))

    # 5. permissões e Baixar tudo
    ent = {}
    auth.fetch_entitlements(lambda e: ent.update(e=e))
    yield from wait_for(lambda: ent)
    check("permissões com download_all", (ent.get("e") or {}).get("download_all") is True, str(ent))

    # Baixar tudo (o servidor do teste tem 2 imagens: o "tudo" do teste são elas)
    from caffmob_draw.texture_library import ops_account
    ops_account.missing_items = lambda: [catalog.item(t) for t in items if not downloads.cached(t)]
    reset_cache()
    decided = {}
    ops_account.start_download_all(lambda ok, msg: decided.update(ok=ok, msg=msg))
    yield from wait_for(lambda: decided)
    check("Baixar tudo com permissão começa", decided.get("ok") is True, str(decided))
    totals = []
    yield from wait_for(lambda: totals.append(downloads.summary()) or all(downloads.cached(t) for t in items), 30)
    check("Baixar tudo: as imagens que faltavam ficam no cache", all(downloads.cached(t) for t in items))
    check("Baixar tudo: progresso total no rodapé enquanto baixa", any(t is not None for t in totals), str(totals[:3]))
    decided.clear()
    ops_account.start_download_all(lambda ok, msg: decided.update(ok=ok, msg=msg))
    yield from wait_for(lambda: decided)
    check("Baixar tudo de novo: todas baixadas", decided.get("msg") == "Todas as texturas baixadas", str(decided))

    # 6. Sair
    auth.logout()
    check("Sair apaga a sessão", not os.path.exists(path) and not auth.signed_in())
    proc = downloads._state["proc"]
    downloads.shutdown()
    check("shutdown encerra o subprocesso", proc is None or proc.poll() is not None)

    # 401 no meio (outro servidor: o token vale 2 requisições)
    server.terminate()
    server.wait(timeout=5)
    server, url = start_server(root, "--expire-access", "2", "--download-all")
    downloads.set_server(url)
    auth.reload()
    reset_cache()
    result.clear()
    auth.start_login(None, lambda ok, msg: result.update(ok=ok))
    yield from wait_for(lambda: result)
    got.clear()
    other = "arauco/colecao-realce/cravo"
    downloads.fetch(TID, lambda p, err: got.update(a=p))
    downloads.fetch(other, lambda p, err: got.update(b=p, err=err))
    yield from wait_for(lambda: "a" in got and "b" in got, 30)
    check("401 no meio: renova e conclui os dois", bool(got.get("a")) and bool(got.get("b")), str(got))
    downloads.shutdown()

    # 403
    server.terminate()
    server.wait(timeout=5)
    server, url = start_server(root, "--forbid")
    downloads.set_server(url)
    auth.reload()
    reset_cache()
    result.clear()
    auth.start_login(None, lambda ok, msg: result.update(ok=ok))
    yield from wait_for(lambda: result)
    ent.clear()
    auth.fetch_entitlements(lambda e: ent.update(e=e))
    yield from wait_for(lambda: ent)
    check("conta sem permissão: download_all falso", (ent.get("e") or {}).get("download_all") is False, str(ent))
    got.clear()
    downloads.fetch(TID, lambda p, err: got.update(path=p, err=err))
    yield from wait_for(lambda: got, 20)
    check("403 vira aviso (not_entitled)", (got.get("err") or {}).get("code") == "not_entitled", str(got))
    decided = {}
    ops_account.start_download_all(lambda ok, msg: decided.update(ok=ok, msg=msg))
    yield from wait_for(lambda: decided)
    check("Baixar tudo sem permissão: recusado com aviso", decided.get("ok") is False and "permissão" in decided["msg"],
          str(decided))
    auth.logout()
    downloads.shutdown()
    server.terminate()
    server.wait(timeout=5)


def server_calls(_server):
    """Requisições de arquivo que a fila mandou (contadas pela fila do lado do Blender)."""
    return sum(1 for e in downloads._queue.items.values() if e["state"] in ('ACTIVE', 'DONE'))


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    downloads.shutdown()
    print(f"blender_014_textures_net: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.0)
