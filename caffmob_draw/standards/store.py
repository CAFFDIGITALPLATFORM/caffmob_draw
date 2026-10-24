"""Banco local do Padrão de Dimensões ligado ao Blender (feature 067, D-26, D-35).

O arquivo `padroes.sqlite3` fica em `extension_path_user(<pacote>, path="standards")`, a mesma pasta de
`io_json.user_folder`. Abre só quando alguém pede (`get()`), nunca no draw. O caminho troca por `override_path`
(ensaios Blender, `tests/_fixtures_067.banco_temporario`) ou pela variável `CAFFMOB_DRAW_STANDARDS_DB` (portão).
O `sqlite3` acompanha o Blender 5.2.2 nas três plataformas (investigation §1, T127); se faltar, `get()` recusa
com `StoreError` e o padrão continua só no arquivo, como antes da 067.
"""

import os

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
        raise StoreError("O banco do Padrão de Dimensões não está disponível neste Blender.") from exc
    directory = os.path.dirname(os.path.abspath(wanted))
    os.makedirs(directory, exist_ok=True)
    _store = StandardsStore(wanted)
    return _store


def close():
    global _store
    if _store is not None:
        _store.close()
        _store = None


def register():
    pass


def unregister():
    close()
