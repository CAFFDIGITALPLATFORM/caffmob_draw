"""Regras do download das texturas (feature 014, T019; RN-12, D-11). Python puro, sem `bpy`.

Usado pelos dois lados do subprocesso de rede:
- `Queue`: fila sem duplicar id, até `MAX_PARALLEL` ao mesmo tempo, progresso e cancelamento (thread principal);
- `resume_offset`, `verify`, `retry_delay`, `same_origin`: retomada por `Range`, conferência por sha256, recuo
  para 429/5xx e o cuidado de não mandar `Authorization` a outro domínio (`downloader.py`);
- `encode`/`parse_line`: protocolo de uma mensagem JSON por linha entre o Blender e o subprocesso.

(063 RF-10; D-04): request aceita form e headers; reply devolve headers e etag.

Mensagens para o subprocesso: `get` (id, url, dest, sha256, bytes), `token` (value), `cancel` (id), `quit`.
Mensagens do subprocesso: `progress` (id, received, total), `done` (id, path), `error` (id, code, status, message),
`need_token` (id).
"""

import json
from urllib.parse import urlsplit

MAX_PARALLEL = 4
RETRY_5XX = (2, 4, 8)                    # segundos entre tentativas (5xx e erro de rede)
RETRY_429_MAX_ATTEMPTS = 6
RETRY_429_CAP = 60

PENDING, ACTIVE, DONE, FAILED, CANCELLED = 'PENDING', 'ACTIVE', 'DONE', 'FAILED', 'CANCELLED'


class Queue:
    def __init__(self, max_parallel=MAX_PARALLEL):
        self.max_parallel = max_parallel
        self.items = {}                   # id → dict(item, state, received, error)
        self.order = []

    def add(self, item):
        """Põe na fila; False se o id já está pendente, ativo ou concluído."""
        current = self.items.get(item["id"])
        if current is not None and current["state"] in (PENDING, ACTIVE, DONE):
            return False
        self.items[item["id"]] = dict(item, state=PENDING, received=0, error=None)
        if item["id"] in self.order:
            self.order.remove(item["id"])
        self.order.append(item["id"])
        return True

    def state(self, item_id):
        entry = self.items.get(item_id)
        return entry["state"] if entry else None

    def next_batch(self):
        """Ids que podem começar agora (passam a ativos), respeitando o limite de paralelos."""
        active = sum(1 for e in self.items.values() if e["state"] == ACTIVE)
        started = []
        for item_id in self.order:
            if active >= self.max_parallel:
                break
            entry = self.items[item_id]
            if entry["state"] == PENDING:
                entry["state"] = ACTIVE
                started.append(item_id)
                active += 1
        return started

    def progress(self, item_id, received):
        entry = self.items.get(item_id)
        if entry is not None and entry["state"] == ACTIVE:
            entry["received"] = int(received)

    def finish(self, item_id, ok, error=None):
        entry = self.items.get(item_id)
        if entry is None or entry["state"] not in (PENDING, ACTIVE):
            return
        entry["state"] = DONE if ok else FAILED
        entry["error"] = error
        if ok and entry.get("bytes"):
            entry["received"] = int(entry["bytes"])

    def cancel(self, item_id):
        entry = self.items.get(item_id)
        if entry is not None and entry["state"] in (PENDING, ACTIVE):
            entry["state"] = CANCELLED

    def cancel_all(self):
        for item_id in list(self.items):
            self.cancel(item_id)

    def idle(self):
        return not any(e["state"] in (PENDING, ACTIVE) for e in self.items.values())

    def totals(self):
        """(concluídos, total sem cancelados, bytes recebidos, bytes esperados)."""
        live = [e for e in self.items.values() if e["state"] != CANCELLED]
        return (sum(1 for e in live if e["state"] == DONE), len(live), sum(e["received"] for e in live),
                sum(int(e.get("bytes") or 0) for e in live))


def resume_offset(part_size, expected):
    """De onde retomar um `.part`: só quando há tamanho esperado e o parcial é menor que ele."""
    if not expected or part_size <= 0 or part_size >= expected:
        return 0
    return int(part_size)


def etag_value(etag):
    """Valor para leitura/comparação; preserve o ETag original nos pedidos condicionais."""
    value = str(etag or '').strip()
    if value.startswith('W/'):
        value = value[2:]
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    return value


def response_version(body, headers, default=0):
    """A versão do documento prevalece sobre o validador HTTP da borda."""
    if body.get('version') is not None:
        return int(body['version'])
    etag = next((v for k, v in headers.items() if k.lower() == 'etag'), '')
    return int(etag_value(etag) or default)


def verify(actual_sha, expected_sha):
    return bool(expected_sha) and str(actual_sha).lower() == str(expected_sha).lower()


def retry_delay(attempt, status, retry_after=None):
    """Segundos até a próxima tentativa (`attempt` = 1 na primeira repetição) ou None para desistir."""
    if status == 429:
        if attempt > RETRY_429_MAX_ATTEMPTS:
            return None
        if retry_after is not None:
            try:
                return min(RETRY_429_CAP, max(0, int(float(retry_after))))
            except (TypeError, ValueError):
                pass
        return min(RETRY_429_CAP, 2 ** attempt)
    if status is None or 500 <= int(status) < 600:
        return RETRY_5XX[attempt - 1] if 1 <= attempt <= len(RETRY_5XX) else None
    return None


def same_origin(a, b):
    pa, pb = urlsplit(a), urlsplit(b)
    return (pa.scheme, pa.hostname, pa.port) == (pb.scheme, pb.hostname, pb.port)


def encode(message):
    return json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n"


def parse_line(line):
    """Mensagem do protocolo ou None (linha vazia, inválida ou sem `type`)."""
    try:
        data = json.loads(line)
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("type"), str):
        return None
    return data
