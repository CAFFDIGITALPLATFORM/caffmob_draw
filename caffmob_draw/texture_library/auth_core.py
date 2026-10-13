"""Regras da conta CAF Mob (feature 014, T022; RN-11, D-12, D-13). Python puro, sem `bpy`.

Login por código de dispositivo (OAuth 2.0 Device Authorization Grant, RFC 8628): o servidor dá um código, o plugin
abre o navegador e consulta `/auth/token` no intervalo pedido até a confirmação. A senha nunca passa pelo Blender.

A sessão gravada em disco (`session_payload`) guarda só o token de renovação, a conta e o servidor; o token de acesso
fica em memória e é renovado 30 s antes de vencer (`access_valid`).
"""

SCHEMA_VERSION = 1
SLOW_DOWN_STEP = 5                      # RFC 8628 §3.5
ACCESS_MARGIN = 30.0                    # renova o token de acesso este tanto antes de vencer

WAITING, DONE, DENIED, EXPIRED, ERROR = 'WAITING', 'DONE', 'DENIED', 'EXPIRED', 'ERROR'
OK, LOGOUT, RETRY = 'OK', 'LOGOUT', 'RETRY'
TOKEN_FIELDS = ("access_token", "refresh_token")


class DeviceFlow:
    def __init__(self):
        self.state = None
        self.device_code = self.user_code = self.open_url = ""
        self.interval = SLOW_DOWN_STEP
        self.expires_at = self.next_poll = 0.0
        self.tokens = None

    def start(self, response, now):
        """`response` = corpo de `POST /v1/auth/device`."""
        self.state = WAITING
        self.device_code = str(response["device_code"])
        self.user_code = str(response["user_code"])
        self.open_url = str(response.get("verification_uri_complete") or response["verification_uri"])
        self.interval = int(response.get("interval") or SLOW_DOWN_STEP)
        self.expires_at = now + float(response.get("expires_in") or 600)
        self.next_poll = now + self.interval
        self.tokens = None

    def due(self, now):
        """Hora de consultar `/auth/token`? Vencido o código, o estado vira EXPIRED."""
        if self.state != WAITING:
            return False
        if now >= self.expires_at:
            self.state = EXPIRED
            return False
        return now >= self.next_poll

    def handle(self, status, body, now):
        """Estado depois da resposta de `/auth/token` (`status` None = sem rede)."""
        body = body if isinstance(body, dict) else {}
        if status == 200 and all(body.get(f) for f in TOKEN_FIELDS):
            self.state, self.tokens = DONE, body
            return self.state
        error = body.get("error")
        if status is None or (status >= 500) or error == "authorization_pending":
            self.state = WAITING
        elif error == "slow_down":
            self.interval += SLOW_DOWN_STEP
            self.state = WAITING
        elif error == "access_denied":
            self.state = DENIED
        elif error == "expired_token":
            self.state = EXPIRED
        else:
            self.state = ERROR
        self.next_poll = now + self.interval
        return self.state


def session_payload(tokens, server, saved_at):
    """Conteúdo de `auth/session.json`: sem token de acesso e sem senha."""
    return {"schema-version": SCHEMA_VERSION, "refresh_token": str(tokens["refresh_token"]),
            "account": dict(tokens.get("account") or {}), "server": str(server), "saved-at": str(saved_at)}


def load_session(data, server):
    """Sessão válida para este servidor, ou None (arquivo de outra versão, incompleto ou de outro servidor)."""
    if not isinstance(data, dict) or data.get("schema-version") != SCHEMA_VERSION:
        return None
    if not data.get("refresh_token") or data.get("server") != server:
        return None
    return data


def refresh_outcome(status, body):
    """(OK, tokens), (LOGOUT, None) ou (RETRY, None) para a resposta de `/auth/refresh`."""
    if status is None or status == 429 or (isinstance(status, int) and status >= 500):
        return RETRY, None
    if status == 200 and isinstance(body, dict) and all(body.get(f) for f in TOKEN_FIELDS):
        return OK, body
    return LOGOUT, None


def access_valid(expires_at, now, margin=ACCESS_MARGIN):
    return expires_at is not None and now < expires_at - margin
