"""Decisão da sincronia do Padrão de Dimensões por uid (feature 067, T149; D-34; RF-034, RF-035). Python puro.

Entradas por uid: o registro local (documento, `versao_remota`, `sujo`, `excluida`) e o item da listagem da nuvem
(`version`, `excluido`). A conta compara conteúdo pelo documento normalizado (`canonical`): JSON com as chaves em
ordem e sem o envelope que o addon muda a cada edição local (`version`, `updated_at`, `source`; auditoria A001).

- conteúdo igual dos dois lados → adota a versão da nuvem, sem conflito (também na primeira sincronia);
- só a nuvem mudou → baixar; só o local mudou → enviar com `If-Match: versao_remota`;
- os dois mudaram → conflito de edição ("Manter a minha" / "Manter a da nuvem");
- um apagou e o outro editou → conflito apagar × editar ("Manter apagado" / "Manter a edição");
- apagado de um lado e intacto do outro → propagar a exclusão (`DELETE` com `If-Match`; um 409 vira conflito).
"""

import hashlib
import json
from dataclasses import dataclass

ENVELOPE = ("version", "updated_at", "source")

# Ações.
NOTHING, DOWNLOAD, UPLOAD, CREATE, DELETE_REMOTE, DELETE_LOCAL, PURGE, ADOPT, COMPARE = (
    'NOTHING', 'DOWNLOAD', 'UPLOAD', 'CREATE', 'DELETE_REMOTE', 'DELETE_LOCAL', 'PURGE', 'ADOPT', 'COMPARE')
EDIT_CONFLICT, DELETE_CONFLICT = 'EDIT_CONFLICT', 'DELETE_CONFLICT'
# Escolhas do usuário (RF-035).
KEEP_MINE, KEEP_CLOUD, KEEP_DELETED, KEEP_EDIT = 'KEEP_MINE', 'KEEP_CLOUD', 'KEEP_DELETED', 'KEEP_EDIT'
CHOICES = {EDIT_CONFLICT: (KEEP_MINE, KEEP_CLOUD), DELETE_CONFLICT: (KEEP_DELETED, KEEP_EDIT)}


@dataclass(frozen=True)
class Local:
    document: dict
    remote_version: object = None       # int ou None (nunca sincronizado)
    dirty: bool = False
    deleted: bool = False


@dataclass(frozen=True)
class Remote:
    version: int
    deleted: bool = False


@dataclass(frozen=True)
class Decision:
    action: str
    if_match: object = None             # versão para o `If-Match` (ou None)
    side: str = ''                      # no conflito apagar × editar: quem apagou ('LOCAL' ou 'CLOUD')


def canonical(document):
    """JSON canônico do conteúdo: chaves em ordem, sem o envelope do addon."""
    content = {k: v for k, v in (document or {}).items() if k not in ENVELOPE}
    return json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def same_content(a, b):
    return canonical(a) == canonical(b)


def digest(document):
    return hashlib.sha256(canonical(document).encode("utf-8")).hexdigest()


def decide(local, remote):
    """Primeira decisão por uid; COMPARE pede o documento da nuvem e segue em `after_compare`."""
    if local is None:
        if remote is None or remote.deleted:
            return Decision(NOTHING)
        return Decision(DOWNLOAD)
    if remote is None:
        if local.deleted:
            return Decision(PURGE)
        return Decision(CREATE)
    if remote.deleted:
        if local.deleted:
            return Decision(PURGE)
        if local.dirty or local.remote_version is None:
            return Decision(DELETE_CONFLICT, side='CLOUD')        # a nuvem apagou, o local editou
        return Decision(DELETE_LOCAL)
    if local.deleted:
        if local.remote_version is not None and remote.version == local.remote_version:
            return Decision(DELETE_REMOTE, if_match=remote.version)
        return Decision(DELETE_CONFLICT, if_match=remote.version, side='LOCAL')   # o local apagou, a nuvem editou
    if local.remote_version is None:
        return Decision(COMPARE)                                 # primeira sincronia com o uid dos dois lados
    if remote.version == local.remote_version:
        return Decision(UPLOAD, if_match=remote.version) if local.dirty else Decision(NOTHING)
    if not local.dirty:
        return Decision(DOWNLOAD)
    return Decision(COMPARE)


def after_compare(local, remote, remote_document):
    """Com o documento da nuvem em mãos: conteúdo igual adota a nuvem; diferente é conflito de edição."""
    if same_content(local.document, remote_document):
        return Decision(ADOPT, if_match=remote.version)
    return Decision(EDIT_CONFLICT, if_match=remote.version)


def on_status(decision, status, local):
    """Resposta da escrita: 409 vira conflito; 404 numa atualização é a nuvem que apagou."""
    if status == 409:
        return Decision(EDIT_CONFLICT if decision.action in (UPLOAD, CREATE) else DELETE_CONFLICT,
                        side='LOCAL' if decision.action == DELETE_REMOTE else '')
    if status == 404 and decision.action in (UPLOAD, DELETE_REMOTE):
        if decision.action == DELETE_REMOTE:
            return Decision(PURGE)
        return Decision(DELETE_CONFLICT, side='CLOUD') if local.dirty else Decision(DELETE_LOCAL)
    return None


def resolve(kind, choice, side='', remote_version=None):
    """O que fazer com a escolha do usuário num conflito; recusa escolha que não é do tipo (RF-035)."""
    if choice not in CHOICES.get(kind, ()):
        raise ValueError(f"escolha {choice} não vale para {kind}")
    if kind == EDIT_CONFLICT:
        return Decision(UPLOAD, if_match=remote_version) if choice == KEEP_MINE else Decision(ADOPT, if_match=remote_version)
    if side == 'CLOUD':                       # a nuvem apagou, o local editou
        return Decision(DELETE_LOCAL) if choice == KEEP_DELETED else Decision(CREATE)
    # o local apagou, a nuvem editou
    return Decision(DELETE_REMOTE, if_match=remote_version) if choice == KEEP_DELETED else Decision(DOWNLOAD)


def changed_fields(a, b):
    """Campos de primeiro nível que diferem (para a lista de conflitos mostrar)."""
    keys = sorted(set(a or {}) | set(b or {}))
    return [k for k in keys if k not in ENVELOPE and json.dumps((a or {}).get(k), sort_keys=True)
            != json.dumps((b or {}).get(k), sort_keys=True)]


# Listagem paginada da nuvem ------------------------------------------------------------------------------------

LIST_PATH = "/padroes-de-dimensao"


def page_path(cursor=None):
    """Caminho da página da listagem; `cursor` é o `proximo` da página anterior."""
    return LIST_PATH if cursor in (None, "") else f"{LIST_PATH}?depois={cursor}"


def read_page(body):
    """(itens como {uid: Remote}, próximo cursor ou None) de uma página da listagem."""
    remotes = {}
    for item in (body or {}).get("itens") or ():
        uid = item.get("uid")
        if isinstance(uid, str) and uid:
            remotes[uid] = Remote(int(item.get("version") or 0), bool(item.get("excluido")))
    return remotes, (body or {}).get("proximo") or None


def plan(locals_by_uid, remotes_by_uid):
    """Decisão de cada uid presente em algum lado, em ordem de uid."""
    uids = sorted(set(locals_by_uid) | set(remotes_by_uid))
    return [(uid, decide(locals_by_uid.get(uid), remotes_by_uid.get(uid))) for uid in uids]
