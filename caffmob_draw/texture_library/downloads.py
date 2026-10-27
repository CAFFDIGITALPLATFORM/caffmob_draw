"""Ponte do download das texturas no thread principal (feature 014, T021; RN-12, RN-13, D-11, D-14).

Inicia `downloader.py` com o Python do Blender, manda pedidos por JSON no stdin e lê o stdout sem bloquear num
`bpy.app.timers`. Guarda o progresso em memória (para a grade e o rodapé) e chama de volta, no thread principal,
quem pediu: `fetch(item_id, callback)` → `callback(path, error)`; `request(...)` → `callback(status, body)`.

Nada acessa a rede sem `bpy.app.online_access` (D-14). O token de acesso vem de `auth` (T023), que esta ponte pede
antes de baixar e de novo quando o subprocesso responde 401 (`need_token`).

As imagens ficam em `extension_path_user("textures")/<sha256>.<ext>` (063 D-07). Mapas sem sha no catálogo
são conferidos e revalidados pelo ETag; os pedidos também aceitam formulário e cabeçalhos.
"""

import os
import hashlib
import json
from urllib.parse import urlsplit
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
    return str(os.environ.get("CAFFMOB_BASE") or getattr(_prefs(), "mobi_url", "https://mobi.caff.digital")).strip().rstrip("/")


def online():
    return bool(bpy.app.online_access)


def unavailable_reason():
    """Por que a rede não pode ser usada agora (texto para o usuário), ou ""."""
    if not online():
        return OFFLINE
    url = urlsplit(server_url())
    if url.username or url.password or url.query or url.fragment or url.path not in ('', '/'):
        return NO_SERVER
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname == '127.0.0.1'):
        return NO_SERVER
    return ""


def cache_dir():
    if not _state.get("cache_dir"):
        _state["cache_dir"] = bpy.utils.extension_path_user(ADDON_PKG, path="textures", create=True)
    return _state["cache_dir"]


def cache_path(entry):
    sha = entry.get("sha256")
    ext = entry.get("ext") or "jpg"
    if sha:
        return os.path.join(cache_dir(), sha + "." + ext)
    key = hashlib.sha256(entry.get("url", entry["id"]).encode()).hexdigest()
    index = os.path.join(cache_dir(), key + ".json")
    try:
        with open(index, encoding="utf-8") as handle:
            return os.path.join(cache_dir(), json.load(handle)["file"])
    except (OSError, ValueError, KeyError):
        return os.path.join(cache_dir(), key + ".part-cache")


def cached(item_id, entry=None):
    """Caminho da imagem baixada, ou "" (RN-13: baixada funciona sem internet)."""
    entry = entry or catalog.item(item_id)
    if entry is None:
        return ""
    if entry.get('local_path'):                       # 073: textura PBR do pacote, sem cache nem rede (RN-07)
        path = entry['local_path'].get('cor', '')
        return path if os.path.isfile(path) else ""
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
    if unavailable_reason():
        return False
    if _running() and _state["base"] != server_url():
        shutdown()
    if _running():
        return True
    ua = _user_agent()
    _state["base"] = server_url()
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
    if token != _state["token_sent"] and _send({"type": "token", "value": token}):
        _state["token_sent"] = token


def request(method, path, body=None, auth=True, callback=None, headers=None, form=False, response_headers=False):
    """(063 RF-10; D-04) JSON/formulário pelo subprocesso. Devolve um pedido cancelável."""
    ticket = {"rid": None, "cancelled": False}

    def deliver(status, payload, received):
        if ticket["cancelled"] or callback is None:
            return
        if response_headers:
            callback(status, payload, received)
        else:
            callback(status, payload)

    def send(token="", retry=False):
        if ticket["cancelled"]:
            return
        if not _ensure_process():
            deliver(None, {"error": "offline", "message": unavailable_reason()}, {})
            return
        if auth and not token:
            deliver(401, {"error": "disconnected"}, {})
            return
        if token:
            send_token(token)
        _state["rid"] += 1
        rid = _state["rid"]
        ticket["rid"] = rid

        def answered(status, payload, received):
            if ticket["cancelled"]:
                return
            if status == 401 and auth and not retry:
                from . import auth as account
                account.invalidate_access()
                account.with_access(lambda fresh: send(fresh, True))
                return
            from ..mobi import respostas
            if auth and not respostas.compatible(received):
                deliver(426, {"error": "contract", "message": respostas.message(status, payload, received)}, received)
                return
            deliver(status, payload, received)
        _requests[rid] = answered
        if not _send({"type": "request", "rid": rid, "method": method, "path": path, "body": body,
                      "auth": auth, "headers": headers or {}, "form": form}):
            _requests.pop(rid, None)
            deliver(None, {"error": "network", "message": NETWORK}, {})
    if auth:
        from . import auth as account
        if unavailable_reason():
            deliver(None, {"error": "offline", "message": unavailable_reason()}, {})
        else:
            account.with_access(send)
    else:
        send()
    return ticket


def cancel_request(ticket):
    if not ticket:
        return
    ticket["cancelled"] = True
    rid = ticket.get("rid")
    _requests.pop(rid, None)
    if rid is not None:
        _send({"type": "cancel", "id": rid})


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
            catalog.warn("callback")
            print("CAFFMob texturas:", repr(exc))


def _dispatch(message):
    kind = message["type"]
    if kind == "progress":
        _queue.progress(message["id"], message.get("received", 0))
        if message.get("total") and message["id"] in _queue.items:
            _queue.items[message["id"]]["bytes"] = message["total"]
    elif kind == "done":
        entry = _queue.items.get(message["id"], {})
        path = message.get("path", "")
        if path and not entry.get("sha256") and message.get("etag"):
            sha = download_core.etag_value(message["etag"])
            final = os.path.join(cache_dir(), sha + "." + entry.get("ext", "jpg"))
            if path != final:
                os.replace(path, final)
            key = hashlib.sha256(entry.get("url", entry.get("id", "")).encode()).hexdigest()
            with open(os.path.join(cache_dir(), key + ".json"), "w", encoding="utf-8") as handle:
                json.dump({"file": os.path.basename(final), "etag": message["etag"]}, handle)
            if message.get("etag"):
                with open(final + ".etag", "w", encoding="utf-8") as handle:
                    handle.write(message["etag"])
            path = final
        _queue.finish(message["id"], True)
        _finish(message["id"], path, None)
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
                callback(message.get("status"), message.get("body") or {}, message.get("headers") or {})
            except Exception as exc:
                catalog.warn("callback")
                print("CAFFMob texturas:", repr(exc))


def _start_batch():
    if unavailable_reason():
        return
    if not _state["token_sent"]:
        return
    for item_id in _queue.next_batch():
        entry = _queue.items[item_id]
        _send({"type": "get", "id": item_id, "url": entry["url"], "dest": entry["dest"], "sha256": entry["sha256"],
               "bytes": entry["bytes"], "headers": entry.get("headers", {}), "etag": entry.get("etag")})


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
            callback(None, {"error": "network", "message": NETWORK}, {})
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
    if os.path.isfile(path) and (entry.get("sha256") or unavailable_reason()):
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

        if not _ensure_process():
            _finish(item_id, None, {"code": "offline", "message": unavailable_reason()})
            return
        send_token(token)
        _queue.items.pop(item_id, None)
        _queue.add({"id": item_id, "url": entry.get("url") or "/api/draw/v1/texturas/{}/imagem?tamanho=trabalho".format(item_id),
                    "dest": path, "sha256": entry.get("sha256"), "ext": entry.get("ext", "jpg"),
                    "headers": entry.get("headers", {}), "bytes": int(entry.get("bytes") or 0)})
        _start_batch()
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
