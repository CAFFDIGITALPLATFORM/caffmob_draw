"""Sessão única do aparelho MOBI (063 RF-03, RF-08; D-05, D-06).

Código RFC 8628, renovação e revogação passam por downloads.request. A sessão, com tokens, titular e base,
fica em caffmob/sessao.json (0600); só 400 invalid_grant a invalida na renovação.
"""

import datetime
import json
import os
import time
import platform

import bpy  # type: ignore

from ..data.i18n import N_
from ..caffmob import sessao
from . import auth_core, downloads

CLIENT_ID = "caffmob-draw"
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"
POLL_TICK = 0.5
DENIED = N_("O acesso foi recusado no navegador")
EXPIRED = N_("O código venceu antes da confirmação. Entre de novo")
LOGIN_FAILED = N_("Não foi possível entrar com a conta CAF Mob")

_state = {"session": None, "loaded": False, "access": "", "access_exp": None, "flow": None,
          "on_done": None, "refreshing": [], "entitlements": None, "login_generation": 0}


# Sessão em disco ----------------------------------------------------------------------------------------------------
def session_path():
    return os.path.join(bpy.utils.extension_path_user(downloads.ADDON_PKG, path="caffmob", create=True), "sessao.json")


def _load():
    if _state["loaded"]:
        if _state["session"] and not auth_core.load_session(_state["session"], downloads.server_url()):
            reload()
        else:
            return _state["session"]
    _state["loaded"] = True
    try:
        with open(session_path(), encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        data = None
    _state["session"] = auth_core.load_session(data, downloads.server_url())
    return _state["session"]


def _save(tokens):
    payload = auth_core.session_payload(tokens, downloads.server_url(),
                                        datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
    sessao.save(session_path(), payload)
    _state["session"], _state["loaded"] = payload, True
    _set_access(tokens)


def _set_access(tokens):
    _state["access"] = str(tokens.get("access_token") or "")
    _state["access_exp"] = time.monotonic() + float(tokens.get("expires_in") or 0)
    downloads.send_token(_state["access"])


def _clear():
    _state.update(session=None, loaded=True, access="", access_exp=None, entitlements=None)
    downloads.send_token("")
    from . import catalog
    catalog.invalidate()
    try:
        os.remove(session_path())
    except OSError:
        pass


def reload():
    """Relê a sessão do disco (servidor trocado nas preferências, outro arquivo aberto)."""
    _state.update(session=None, loaded=False, access="", access_exp=None, entitlements=None)
    from . import catalog
    catalog.invalidate()


# Consultas ----------------------------------------------------------------------------------------------------------
def account_email():
    session = _load()
    return str((session or {}).get("titular", {}).get("nome") or "") if session else ""


def signed_in():
    return bool(_load())


def login_state():
    """(estado, código, endereço) do login em andamento, ou (None, "", "")."""
    flow = _state["flow"]
    if flow is None:
        return None, "", ""
    return flow.state, flow.user_code, flow.open_url


def entitlements():
    """Compatibilidade: o MOBI não oferece permissão de download em lote."""
    return _state["entitlements"]


# Token de acesso ----------------------------------------------------------------------------------------------------
def invalidate_access():
    _state["access"], _state["access_exp"] = "", None


def with_access(callback):
    """`callback(token)` com um token válido; "" sem sessão, sem rede ou com a sessão encerrada no servidor."""
    _load()
    if downloads.unavailable_reason():
        callback("")
        return
    if auth_core.access_valid(_state["access_exp"], time.monotonic()) and _state["access"]:
        callback(_state["access"])
        return
    session = _load()
    if session is None or downloads.unavailable_reason():
        callback("")
        return
    _state["refreshing"].append(callback)
    if len(_state["refreshing"]) > 1:
        return

    base = downloads.server_url()
    def done(status, body):
        waiting, _state["refreshing"] = _state["refreshing"], []
        if base != downloads.server_url():
            for cb in waiting:
                cb("")
            return
        outcome, tokens = auth_core.refresh_outcome(status, body)
        if outcome == auth_core.OK:
            _save(tokens)                              # o servidor pode girar o token de renovação
            token = _state["access"]
        else:
            if outcome == auth_core.LOGOUT:
                _clear()
            token = ""
        for cb in waiting:
            cb(token)
    downloads.request("POST", auth_core.TOKEN_PATH, {"client_id": CLIENT_ID, "grant_type": "refresh_token", "refresh_token": session["refresh_token"]},
                      auth=False, callback=done, form=True)


def fetch_entitlements(callback=None):
    """Compatibilidade com a grade: o MOBI não tem permissões de download em lote."""
    if callback:
        callback(None)


# Login por código de dispositivo ------------------------------------------------------------------------------------
def start_login(on_code=None, on_done=None):
    """Começa o login. `on_code(código, endereço)` quando o servidor dá o código; `on_done(ok, mensagem)` no fim."""
    reason = downloads.unavailable_reason()
    if reason:
        if on_done:
            on_done(False, reason)
        return False
    cancel_login()
    _state["on_done"] = on_done
    generation, base = _state["login_generation"], downloads.server_url()

    def started(status, body):
        if generation != _state["login_generation"] or base != downloads.server_url():
            return
        if status != 200 or not body.get("device_code"):
            from ..mobi.respostas import message
            _end(False, message(status, body))
            return
        flow = auth_core.DeviceFlow()
        flow.start(body, time.monotonic())
        flow.base = base
        _state["flow"] = flow
        if on_code:
            on_code(flow.user_code, flow.open_url)
        if not bpy.app.timers.is_registered(_poll):
            bpy.app.timers.register(_poll, first_interval=POLL_TICK, persistent=True)
    downloads.request("POST", auth_core.CODE_PATH, {"client_id": CLIENT_ID, "nome": ("Blender — " + platform.node())[:80],
                                                               "plataforma": "blender"}, auth=False, callback=started, form=True)
    return True


def _poll():
    flow = _state["flow"]
    if flow is None:
        return None
    now = time.monotonic()
    if flow.state == auth_core.EXPIRED:
        _end(False, EXPIRED)
        return None
    if flow.due(now):
        flow.next_poll = now + 3600.0                  # uma consulta por vez; `handle` remarca

        def answered(status, body):
            if _state["flow"] is not flow or flow.base != downloads.server_url():
                return
            result = flow.handle(status, body, time.monotonic())
            if result == auth_core.DONE:
                _save(flow.tokens)
                _end(True, "")
            elif result == auth_core.DENIED:
                from ..mobi.respostas import message
                _end(False, message(status, body))
            elif result == auth_core.EXPIRED:
                from ..mobi.respostas import message
                _end(False, message(status, body))
            elif result == auth_core.ERROR:
                from ..mobi.respostas import message
                _end(False, message(status, body))
        downloads.request("POST", auth_core.TOKEN_PATH, {"client_id": CLIENT_ID, "grant_type": DEVICE_GRANT,
                                                     "device_code": flow.device_code},
                          auth=False, callback=answered, form=True)
    return POLL_TICK if _state["flow"] is flow else None


def _end(ok, message):
    on_done, _state["on_done"] = _state["on_done"], None
    _state["flow"] = None
    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)
    if on_done:
        on_done(ok, message)


def cancel_login():
    _state["login_generation"] += 1
    _state["flow"], _state["on_done"] = None, None
    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)


def logout(callback=None):
    """Revoga pelo token de renovação; sem rede, encerra localmente e avisa."""
    session = _load()
    cancel_login()
    if session and not downloads.unavailable_reason():
        def done(status, body):
            message = "" if status == 200 else sessao.PENDENTE
            if callback:
                callback(message)
        downloads.request("POST", "/api/draw/aparelho/revogar", sessao.revogacao(session),
                          auth=False, callback=done, form=True)
        _clear()
        return
    message = sessao.disconnect(session_path(), None) if session else ""
    _clear()
    if callback:
        callback(message)


def shutdown():
    cancel_login()
    invalidate_access()
    _state["refreshing"] = []


def titular_nome():
    return account_email()
