"""Ponte do download das texturas no thread principal (feature 014, T021; RN-12, RN-13, D-11, D-14).

Inicia `downloader.py` com o Python do Blender, manda pedidos por JSON no stdin e lê o stdout sem bloquear num
`bpy.app.timers`. Guarda o progresso em memória (para a grade e o rodapé) e chama de volta, no thread principal,
quem pediu: `fetch(item_id, callback)` → `callback(path, error)`; `request(...)` → `callback(status, body)`.

Nada acessa a rede sem `bpy.app.online_access` (D-14). O token de acesso vem de `auth` (T023), que esta ponte pede
antes de baixar e de novo quando o subprocesso responde 401 (`need_token`).

As imagens ficam em `extension_path_user("textures")/<id>.<ext>`; um arquivo que já está lá nunca é baixado de novo.
"""

import os
import subprocess
import sys

import bpy  # type: ignore

from ..data.i18n import N_
from . import catalog, download_core

ADDON_PKG = __package__.rsplit(".", 1)[0]
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloader.py")
TICK = 0.1
OFFLINE = N_("O acesso à internet do Blender está desligado (Preferências › Sistema › Rede)")
NO_SERVER = N_("Servidor de texturas não configurado nas preferências do CAFFMob Draw")
NOT_ON_SERVER = N_("Textura não disponível no servidor")
NO_ACCOUNT = N_("Entre com a sua conta CAF Mob para baixar texturas")
NETWORK = N_("Sem resposta do servidor de texturas")

_state = {"proc": None, "buffer": "", "rid": 0, "base": "", "server_items": None, "catalog_waiting": [],
          "server_override": None, "token_sent": ""}
_queue = download_core.Queue()
_callbacks = {}                  # id → [callback(path, error)]
_requests = {}                   # rid → callback(status, body)


# Configuração -------------------------------------------------------------------------------------------------------
def _prefs():
    try:
        return bpy.context.preferences.addons[ADDON_PKG].preferences
    except (KeyError, AttributeError):
        return None


def set_server(url):
    """Endereço do servidor fora das preferências (testes); None volta às preferências."""
    _state["server_override"] = url
    shutdown()


def server_url():
    if _state["server_override"] is not None:
        return _state["server_override"].rstrip("/")
    return str(getattr(_prefs(), "textures_server_url", "") or "").strip().rstrip("/")


def online():
    return bool(bpy.app.online_access)


def unavailable_reason():
    """Por que a rede não pode ser usada agora (texto para o usuário), ou ""."""
    if not online():
        return OFFLINE
    if not server_url():
        return NO_SERVER
    return ""


def cache_dir():
    if not _state.get("cache_dir"):
        _state["cache_dir"] = bpy.utils.extension_path_user(ADDON_PKG, path="textures", create=True)
    return _state["cache_dir"]


def cache_path(entry):
    return os.path.join(cache_dir(), *entry["id"].split("/")) + "." + (entry.get("ext") or "jpg")


def cached(item_id, entry=None):
    """Caminho da imagem baixada, ou "" (RN-13: baixada funciona sem internet)."""
    entry = entry or catalog.item(item_id)
    if entry is None:
        return ""
    path = cache_path(entry)
    return path if os.path.isfile(path) else ""


# Subprocesso --------------------------------------------------------------------------------------------------------
def _user_agent():
    version = "?"
    manifest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "blender_manifest.toml")
    try:
        with open(manifest, encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("version"):
                    version = line.split("=", 1)[1].strip().strip('"')
                    break
    except OSError:
        pass
    return "CAFFMobDraw/{} Blender/{}".format(version, bpy.app.version_string)


def _running():
    proc = _state["proc"]
    return proc is not None and proc.poll() is None


def _ensure_process():
    if _running():
        return True
    if unavailable_reason():
        return False
    ua = _user_agent()
    _state["base"] = server_url() + "/v1"
    _state["proc"] = subprocess.Popen([sys.executable, "-I", WORKER, "--base", _state["base"], "--ua", ua],
                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      text=True, encoding="utf-8", bufsize=1)
    os.set_blocking(_state["proc"].stdout.fileno(), False)
    _state["buffer"], _state["token_sent"] = "", ""
    if not bpy.app.timers.is_registered(_tick):
        bpy.app.timers.register(_tick, first_interval=TICK, persistent=True)
    return True


def _send(message):
    proc = _state["proc"]
    if proc is None or proc.poll() is not None:
        return False
    try:
        proc.stdin.write(download_core.encode(message))
        proc.stdin.flush()
        return True
    except (BrokenPipeError, OSError, ValueError):
        return False


def send_token(token):
    if token and token != _state["token_sent"] and _send({"type": "token", "value": token}):
        _state["token_sent"] = token


def request(method, path, body=None, auth=True, callback=None):
    """Chamada JSON ao servidor pelo subprocesso; `callback(status, body)` no thread principal (status None = sem
    rede). Sem rede liberada, chama de volta na hora com None."""
    if not _ensure_process():
        if callback:
            callback(None, {"error": "offline", "message": unavailable_reason()})
        return
    _state["rid"] += 1
    rid = _state["rid"]
    if callback:
        _requests[rid] = callback
    _send({"type": "request", "rid": rid, "method": method, "path": path, "body": body, "auth": auth})


def _read_lines():
    proc = _state["proc"]
    try:
        chunk = proc.stdout.read() or ""
    except (BlockingIOError, TypeError, ValueError):
        chunk = ""
    if proc.poll() is not None:                       # terminou: lê o resto do pipe (achado da prova T004)
        try:
            os.set_blocking(proc.stdout.fileno(), True)
            chunk += proc.stdout.read() or ""
        except (OSError, ValueError):
            pass
    _state["buffer"] += chunk
    lines = _state["buffer"].split("\n")
    _state["buffer"] = lines.pop()
    return [m for m in (download_core.parse_line(line) for line in lines) if m is not None]


def _finish(item_id, path, error):
    for callback in _callbacks.pop(item_id, []):
        try:
            callback(path, error)
        except Exception as exc:                      # um chamador com defeito não derruba a fila
            print("CAFFMob texturas:", repr(exc))


def _dispatch(message):
    kind = message["type"]
    if kind == "progress":
        _queue.progress(message["id"], message.get("received", 0))
    elif kind == "done":
        _queue.finish(message["id"], True)
        _finish(message["id"], message.get("path", ""), None)
    elif kind == "error":
        if message.get("code") == "cancelled":
            _finish(message["id"], None, {"code": "cancelled", "message": ""})
            return
        _queue.finish(message["id"], False, message)
        _finish(message["id"], None, message)
    elif kind == "need_token":
        from . import auth
        auth.invalidate_access()
        auth.with_access(lambda token: send_token(token) if token else None)
    elif kind == "reply":
        callback = _requests.pop(message.get("rid"), None)
        if callback:
            try:
                callback(message.get("status"), message.get("body") or {})
            except Exception as exc:
                print("CAFFMob texturas:", repr(exc))


def _start_batch():
    if not _state["token_sent"]:
        return
    for item_id in _queue.next_batch():
        entry = _queue.items[item_id]
        _send({"type": "get", "id": item_id, "url": entry["url"], "dest": entry["dest"], "sha256": entry["sha256"],
               "bytes": entry["bytes"]})


def _tick():
    if _state["proc"] is None:
        return None
    for message in _read_lines():
        _dispatch(message)
    if not _running():                                # caiu ou saiu: o que estava ativo falhou
        for item_id, entry in list(_queue.items.items()):
            if entry["state"] in (download_core.PENDING, download_core.ACTIVE):
                _queue.finish(item_id, False, {"code": "network", "message": NETWORK})
                _finish(item_id, None, {"code": "network", "message": NETWORK})
        for callback in list(_requests.values()):
            callback(None, {"error": "network", "message": NETWORK})
        _requests.clear()
        _state["proc"] = None
        return None
    _start_batch()
    _redraw()
    return TICK


def _redraw():
    wm = bpy.context.window_manager
    if not _queue.idle() or _queue.items:
        for window in (wm.windows if wm else []):
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()


# Catálogo do servidor -----------------------------------------------------------------------------------------------
def _with_server_items(callback):
    """`callback(items ou None, erro)` com o catálogo do servidor (sha256, bytes, url), pedido uma vez."""
    if _state["server_items"] is not None:
        callback(_state["server_items"], None)
        return
    _state["catalog_waiting"].append(callback)
    if len(_state["catalog_waiting"]) > 1:
        return

    def done(status, body):
        waiting, _state["catalog_waiting"] = _state["catalog_waiting"], []
        if status == 200 and isinstance(body.get("items"), dict):
            _state["server_items"] = body["items"]
            for cb in waiting:
                cb(body["items"], None)
            return
        error = {"code": body.get("error") or "network", "status": status,
                 "message": body.get("message") or NETWORK}
        for cb in waiting:
            cb(None, error)
    version = catalog.load()[0].get("catalog-version", 1)
    request("GET", "/v1/textures/catalog?version={}".format(version), callback=done)


# API ----------------------------------------------------------------------------------------------------------------
def fetch(item_id, callback=None, entry=None):
    """Garante a imagem no cache: já baixada chama de volta na hora; senão entra na fila (RN-12, sob demanda).
    `entry` serve para o que não está no catálogo do pacote (o relevo, `bump.bump_entry`)."""
    entry = entry or catalog.item(item_id)
    if callback:
        _callbacks.setdefault(item_id, []).append(callback)
    if entry is None:
        _finish(item_id, None, {"code": "not_found", "message": NOT_ON_SERVER})
        return
    path = cache_path(entry)
    if os.path.isfile(path):
        _finish(item_id, path, None)
        return
    reason = unavailable_reason()
    if reason:
        _finish(item_id, None, {"code": "offline", "message": reason})
        return
    if _queue.state(item_id) in (download_core.PENDING, download_core.ACTIVE):
        return
    from . import auth

    def with_token(token):
        if not token:
            _finish(item_id, None, {"code": "no_account", "message": NO_ACCOUNT})
            return
        send_token(token)

        def with_items(items, error):
            if error:
                _finish(item_id, None, error)
                return
            remote = items.get(item_id)
            if remote is None:
                _finish(item_id, None, {"code": "not_found", "message": NOT_ON_SERVER})
                return
            _queue.items.pop(item_id, None)            # falha ou cancelamento anterior: tenta de novo
            _queue.add({"id": item_id, "url": remote.get("url") or "/v1/textures/{}/file".format(item_id),
                        "dest": path, "sha256": remote.get("sha256") or entry.get("sha256"),
                        "bytes": int(remote.get("bytes") or entry.get("bytes") or 0)})
            _start_batch()
        _with_server_items(with_items)
    auth.with_access(with_token)


def state(item_id):
    """'DONE' se baixada; senão o estado na fila (PENDING, ACTIVE, FAILED, CANCELLED) ou None."""
    if cached(item_id):
        return download_core.DONE
    return _queue.state(item_id)


def progress(item_id):
    """Fração de 0 a 1 do download em andamento, ou None."""
    entry = _queue.items.get(item_id)
    if entry is None or entry["state"] != download_core.ACTIVE or not entry.get("bytes"):
        return None
    return min(1.0, entry["received"] / float(entry["bytes"]))


def error(item_id):
    entry = _queue.items.get(item_id)
    return entry["error"] if entry is not None and entry["state"] == download_core.FAILED else None


def summary():
    """(concluídos, total, MB recebidos, MB total) com download em andamento; senão None (rodapé da grade)."""
    if _queue.idle():
        return None
    done, total, received, expected = _queue.totals()
    return done, total, received / 1048576.0, expected / 1048576.0


def cancel(item_id):
    _queue.cancel(item_id)
    _send({"type": "cancel", "id": item_id})
    _finish(item_id, None, {"code": "cancelled", "message": ""})


def cancel_all():
    for item_id, entry in list(_queue.items.items()):
        if entry["state"] in (download_core.PENDING, download_core.ACTIVE):
            cancel(item_id)


def clear_finished():
    """Esquece os concluídos e os falhos (o rodapé volta a contar do zero no próximo lote)."""
    for item_id in [i for i, e in _queue.items.items() if e["state"] not in (download_core.PENDING,
                                                                            download_core.ACTIVE)]:
        _queue.items.pop(item_id, None)
        if item_id in _queue.order:
            _queue.order.remove(item_id)


def shutdown():
    """Encerra o subprocesso (fecha o stdin; mata se não sair) e esquece a fila. Chamado no unregister e no
    load_pre (princípio VII)."""
    proc = _state["proc"]
    _state["proc"] = None
    if proc is not None:
        try:
            if proc.poll() is None:
                proc.stdin.write(download_core.encode({"type": "quit"}))
                proc.stdin.close()
                proc.wait(timeout=2)
        except (BrokenPipeError, OSError, ValueError, subprocess.TimeoutExpired):
            proc.kill()
        for stream in (proc.stdin, proc.stdout):
            try:
                stream.close()
            except (OSError, ValueError):
                pass
    if bpy.app.timers.is_registered(_tick):
        bpy.app.timers.unregister(_tick)
    _queue.items.clear()
    _queue.order.clear()
    _callbacks.clear()
    _requests.clear()
    _state.update(buffer="", server_items=None, catalog_waiting=[], token_sent="")


def process_alive():
    return _running()
