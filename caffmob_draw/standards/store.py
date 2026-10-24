"""Banco local do Padrão de Dimensões ligado ao Blender (feature 067, D-26, D-35).

O arquivo `padroes.sqlite3` fica em `extension_path_user(<pacote>, path="standards")`, a mesma pasta de
`io_json.user_folder`. Abre só quando alguém pede (`get()`), nunca no draw. O caminho troca por `override_path`
(ensaios Blender, `tests/_fixtures_067.banco_temporario`) ou pela variável `CAFFMOB_DRAW_STANDARDS_DB` (portão).
O `sqlite3` acompanha o Blender 5.2.2 nas três plataformas (investigation §1, T127); se faltar, `get()` recusa
com `StoreError` e o padrão continua só no arquivo, como antes da 067.
"""

import os
from ..data.i18n import N_

ENV_PATH = 'CAFFMOB_DRAW_STANDARDS_DB'
FILENAME = 'padroes.sqlite3'

override_path = None
_store = None


class StoreError(Exception):
    """Banco indisponível (mensagem pronta para o usuário)."""


def path():
    """Caminho do banco: `override_path`, depois a variável de ambiente, depois a pasta do usuário."""
    if override_path:
        return str(override_path)
    env = os.environ.get(ENV_PATH)
    if env:
        return env
    from . import io_json
    return os.path.join(io_json.user_folder(), FILENAME)


def get():
    """Conexão aberta com o banco do caminho atual; reabre se o caminho mudou."""
    global _store
    wanted = path()
    if _store is not None and _store.path == wanted:
        return _store
    close()
    try:
        from .store_core import StandardsStore
    except ImportError as exc:                  # Python do Blender sem `_sqlite3`
        raise StoreError(N_("O banco do Padrão de Dimensões não está disponível neste Blender.")) from exc
    directory = os.path.dirname(os.path.abspath(wanted))
    os.makedirs(directory, exist_ok=True)
    _store = StandardsStore(wanted)
    return _store


def close():
    global _store
    if _store is not None:
        _store.close()
        _store = None


# Ligação com as definições da cena (D-26, D-27) ---------------------------------------------------------------

SEEDED = 'semeado'


def _print_unavailable(exc):
    print(f"CAFFMob Draw: banco do Padrão de Dimensões indisponível: {exc}")


def persist(scene, definition, confirmed=False):
    """Grava a definição do arquivo no banco, numa transação. Devolve 'SAVED', 'BUILTIN', 'OLDER' (o banco tem uma
    versão mais nova: quem chama pergunta e grava de novo com `confirmed=True`, R11) ou 'UNAVAILABLE'."""
    from . import io_json
    if definition is None or definition.builtin:
        return 'BUILTIN'
    try:
        db = get()
        seed(scene, db)
        document = io_json.definition_document(definition)
        if not confirmed and db.is_older_than_stored(document):
            return 'OLDER'
        db.put(document)
    except (StoreError, OSError) as exc:
        _print_unavailable(exc)
        return 'UNAVAILABLE'
    return 'SAVED'


def seed(scene, db=None):
    """M-09: a primeira gravação leva ao banco as definições não embutidas do arquivo (sem sobrescrever o que já há)."""
    from . import io_json
    db = db or get()
    if db.meta(SEEDED):
        return 0
    data = getattr(scene, 'btm_standards', None)
    documents = [io_json.definition_document(d) for d in (data.definitions if data is not None else ()) if not d.builtin]
    report = db.import_documents(documents)
    db.set_meta(SEEDED, 1)
    return len(report['added'])


def remember_active(uid):
    """Guarda a definição ativa como `ultima_ativa` (arquivo novo abre com ela)."""
    try:
        db = get()
        from .store_core import BUILTIN_UIDS
        if uid in BUILTIN_UIDS or db.get(uid) is not None:
            db.set_last_active(uid)
    except (StoreError, OSError) as exc:
        _print_unavailable(exc)


def forget(uid):
    try:
        get().delete(uid)
    except (StoreError, OSError) as exc:
        _print_unavailable(exc)


def load_into(scene):
    """Abertura do arquivo (D-27): arquivo novo (só as embutidas) recebe todas as definições do banco e a última ativa;
    arquivo existente recebe só os uids que não tem, sem mudar a ativa nem os módulos. Abrir nunca grava no banco.
    Devolve quantas definições entraram."""
    from . import api, io_json
    try:
        db = get()
        documents = db.documents()
        last = db.last_active
    except (StoreError, OSError) as exc:
        _print_unavailable(exc)
        return 0
    data = api.ensure_ready(scene)
    fresh = all(d.builtin for d in data.definitions)
    known = {d.uid for d in data.definitions}
    added = 0
    for document in documents:
        if document.get("uid") in known:
            continue                         # uid igual: vale a do arquivo, dentro do arquivo
        try:
            io_json.definition_from_document(scene, document)
            added += 1
        except io_json.StandardFileError as exc:
            print(f"CAFFMob Draw: definição do banco ignorada ({document.get('name')}): {exc}")
    if fresh and last:
        definition = api.find_definition(scene, uid=last)
        if definition is not None:
            api.set_active(scene, definition)
    return added


def register():
    pass


def unregister():
    close()
