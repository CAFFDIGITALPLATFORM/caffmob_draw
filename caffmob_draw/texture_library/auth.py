"""Conta CAF Mob no plugin (feature 014, T023; RN-11, D-12, D-13, D-14).

Todas as chamadas passam pelo subprocesso de rede (`downloads.request`), sem bloquear a interface:
- `start_login(on_code, on_done)`: pede o código de dispositivo, devolve o código e o endereço para abrir no navegador
  e consulta `/auth/token` num timer até a confirmação (`auth_core.DeviceFlow`);
- `with_access(callback)`: dá um token de acesso válido (renova pela sessão gravada quando preciso) ou "";
- `logout()`: avisa o servidor e apaga a sessão.

A sessão fica em `extension_path_user("auth")/session.json` com permissão 0600: token de renovação, conta e servidor,
nunca a senha. O token de acesso fica só em memória. Sem `bpy.app.online_access`, nada é chamado.
"""

import datetime
import json
import os
import time

import bpy  # type: ignore

from ..data.i18n import N_
from . import auth_core, downloads

CLIENT_ID = "caffmob-draw"
DEVICE_GRANT = "urn:ietf:params:oauth:grant-type:device_code"
POLL_TICK = 0.5
DENIED = N_("O acesso foi recusado no navegador")
EXPIRED = N_("O código venceu antes da confirmação. Entre de novo")
LOGIN_FAILED = N_("Não foi possível entrar com a conta CAF Mob")

_state = {"session": None, "loaded": False, "access": "", "access_exp": None, "flow": None,
          "on_done": None, "refreshing": [], "entitlements": None}


# Sessão em disco ----------------------------------------------------------------------------------------------------
def session_path():
    return os.path.join(bpy.utils.extension_path_user(downloads.ADDON_PKG, path="auth", create=True), "session.json")


def _load():
    if _state["loaded"]:
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
    path = session_path()
    tmp = path + ".tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)
    _state["session"], _state["loaded"] = payload, True
    _set_access(tokens)


def _set_access(tokens):
    _state["access"] = str(tokens.get("access_token") or "")
    _state["access_exp"] = time.monotonic() + float(tokens.get("expires_in") or 0)
    downloads.send_token(_state["access"])


def _clear():
    _state.update(session=None, loaded=True, access="", access_exp=None, entitlements=None)
    try:
        os.remove(session_path())
    except OSError:
        pass


def reload():
    """Relê a sessão do disco (servidor trocado nas preferências, outro arquivo aberto)."""
    _state.update(session=None, loaded=False, access="", access_exp=None, entitlements=None)


# Consultas ----------------------------------------------------------------------------------------------------------
def account_email():
    session = _load()
    return str((session or {}).get("account", {}).get("email") or "") if session else ""


def signed_in():
    return bool(_load())


def login_state():
    """(estado, código, endereço) do login em andamento, ou (None, "", "")."""
    flow = _state["flow"]
    if flow is None:
        return None, "", ""
    return flow.state, flow.user_code, flow.open_url


def entitlements():
    """Permissões da conta já consultadas (`GET /v1/me/entitlements`), ou None."""
    return _state["entitlements"]


# Token de acesso ----------------------------------------------------------------------------------------------------
def invalidate_access():
    _state["access"], _state["access_exp"] = "", None


def with_access(callback):
    """`callback(token)` com um token válido; "" sem sessão, sem rede ou com a sessão encerrada no servidor."""
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

    def done(status, body):
        waiting, _state["refreshing"] = _state["refreshing"], []
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
    downloads.request("POST", "/v1/auth/refresh", {"client_id": CLIENT_ID, "refresh_token": session["refresh_token"]},
                      auth=False, callback=done)


def fetch_entitlements(callback=None):
    """Consulta as permissões da conta; `callback(entitlements ou None)`."""
    def with_token(token):
        if not token:
            if callback:
                callback(None)
            return

        def done(status, body):
            _state["entitlements"] = body if status == 200 else None
            if callback:
                callback(_state["entitlements"])
        downloads.request("GET", "/v1/me/entitlements", callback=done)
    with_access(with_token)


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

    def started(status, body):
        if status != 200 or not body.get("device_code"):
            _end(False, body.get("message") or LOGIN_FAILED)
            return
        flow = auth_core.DeviceFlow()
        flow.start(body, time.monotonic())
        _state["flow"] = flow
        if on_code:
            on_code(flow.user_code, flow.open_url)
        if not bpy.app.timers.is_registered(_poll):
            bpy.app.timers.register(_poll, first_interval=POLL_TICK, persistent=True)
    downloads.request("POST", "/v1/auth/device", {"client_id": CLIENT_ID}, auth=False, callback=started)
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
            if _state["flow"] is not flow:
                return
            result = flow.handle(status, body, time.monotonic())
            if result == auth_core.DONE:
                _save(flow.tokens)
                _end(True, "")
            elif result == auth_core.DENIED:
                _end(False, DENIED)
            elif result == auth_core.EXPIRED:
                _end(False, EXPIRED)
            elif result == auth_core.ERROR:
                _end(False, body.get("message") or LOGIN_FAILED)
        downloads.request("POST", "/v1/auth/token", {"client_id": CLIENT_ID, "grant_type": DEVICE_GRANT,
                                                     "device_code": flow.device_code},
                          auth=False, callback=answered)
    return POLL_TICK if _state["flow"] is flow else None


def _end(ok, message):
    on_done, _state["on_done"] = _state["on_done"], None
    _state["flow"] = None
    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)
    if on_done:
        on_done(ok, message)


def cancel_login():
    _state["flow"], _state["on_done"] = None, None
    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)


def logout():
    """Sai: avisa o servidor (se der) e apaga a sessão. Funciona sem internet (só apaga)."""
    session = _load()
    if session and not downloads.unavailable_reason():
        downloads.request("POST", "/v1/auth/logout", {"refresh_token": session["refresh_token"]}, auth=False)
    _clear()


def shutdown():
    cancel_login()
    invalidate_access()
    _state["refreshing"] = []
