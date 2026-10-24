"""Banco local do Padrão de Dimensões (feature 067, D-26; data-delta §6): núcleo puro.

O padrão da marcenaria vive fora do `.blend`, num `padroes.sqlite3`, para não precisar ser configurado de novo a cada
arquivo (RN-15). Python puro com `sqlite3` da biblioteca padrão e caminho injetado; a ligação com o Blender (onde
fica o arquivo) é de `standards/store.py`. Cada definição é guardada como o documento de `io_json.values_to_document`.
As embutidas nunca entram. Toda gravação é uma transação.
"""

import datetime
import json
import sqlite3

from . import builtin
from ..data.i18n import N_

SCHEMA = 1
BUILTIN_UIDS = frozenset(uid for uid, _name, _market in builtin.BUILTINS)

_DDL = (
    "CREATE TABLE IF NOT EXISTS definicao ("
    " uid TEXT PRIMARY KEY,"
    " documento TEXT NOT NULL,"
    " atualizado_em TEXT NOT NULL,"
    " versao_remota INTEGER,"
    " sujo INTEGER NOT NULL DEFAULT 1,"
    " excluida INTEGER NOT NULL DEFAULT 0)",
    "CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT)",
)


class StoreError(Exception):
    """Uso inválido do banco (mensagem pronta para o usuário)."""


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def _uid_of(document):
    uid = document.get("uid") if isinstance(document, dict) else None
    if not isinstance(uid, str) or not uid:
        raise StoreError(N_("Definição sem identificador."))
    if uid in BUILTIN_UIDS:
        raise StoreError(N_("As definições embutidas não são gravadas no banco."))
    return uid


def _version(document):
    try:
        return int(document.get("version") or 1)
    except (TypeError, ValueError):
        return 1


class StandardsStore:
    """Uma conexão com o banco. Use como gerenciador de contexto ou chame `close()`."""

    def __init__(self, path):
        self.path = str(path)
        self._db = sqlite3.connect(self.path, isolation_level=None)
        with self._transaction():
            for statement in _DDL:
                self._db.execute(statement)
            self._db.execute("INSERT OR IGNORE INTO meta (chave, valor) VALUES ('esquema', ?)", (str(SCHEMA),))

    def close(self):
        if self._db is not None:
            self._db.close()
            self._db = None

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def _transaction(self):
        db = self._db

        class _Tx:
            def __enter__(self):
                db.execute("BEGIN IMMEDIATE")
                return db

            def __exit__(self, exc_type, _exc, _tb):
                db.execute("ROLLBACK" if exc_type else "COMMIT")
                return False
        return _Tx()

    # Leitura ------------------------------------------------------------------------------------------------

    def get(self, uid):
        row = self._db.execute("SELECT documento FROM definicao WHERE uid = ? AND excluida = 0", (uid,)).fetchone()
        return json.loads(row[0]) if row else None

    def documents(self):
        rows = self._db.execute("SELECT documento FROM definicao WHERE excluida = 0 ORDER BY uid").fetchall()
        return [json.loads(row[0]) for row in rows]

    def state(self, uid):
        """Estado de sincronia da linha (inclusive a excluída): dict com `sujo`, `versao_remota`, `excluida`."""
        row = self._db.execute("SELECT atualizado_em, versao_remota, sujo, excluida FROM definicao WHERE uid = ?",
                               (uid,)).fetchone()
        if row is None:
            return None
        return {'atualizado_em': row[0], 'versao_remota': row[1], 'sujo': bool(row[2]), 'excluida': bool(row[3])}

    def schema(self):
        return int(self.meta('esquema') or 0)

    def meta(self, key):
        row = self._db.execute("SELECT valor FROM meta WHERE chave = ?", (key,)).fetchone()
        return row[0] if row else None

    @property
    def last_active(self):
        return self.meta('ultima_ativa')

    def is_older_than_stored(self, document):
        """Verdadeiro quando o banco já tem esta definição numa versão mais nova (R11: pedir confirmação)."""
        stored = self.get(_uid_of(document))
        return stored is not None and _version(stored) > _version(document)

    # Gravação -----------------------------------------------------------------------------------------------

    def put(self, document):
        """Grava (ou substitui) a definição e a marca como mudada localmente."""
        uid = _uid_of(document)
        with self._transaction() as db:
            self._put(db, uid, document)

    def _put(self, db, uid, document):
        db.execute(
            "INSERT INTO definicao (uid, documento, atualizado_em, sujo, excluida) VALUES (?, ?, ?, 1, 0) "
            "ON CONFLICT(uid) DO UPDATE SET documento = excluded.documento, atualizado_em = excluded.atualizado_em, "
            "sujo = 1, excluida = 0",
            (uid, json.dumps(document, ensure_ascii=False, sort_keys=True), now_utc()))

    def rename(self, uid, name):
        with self._transaction() as db:
            document = self.get(uid)
            if document is None:
                raise StoreError(N_("Definição não encontrada no banco."))
            document["name"] = str(name)
            self._put(db, uid, document)

    def delete(self, uid):
        """Apaga. Linha que nunca foi à nuvem sai já; a sincronizada fica marcada até a nuvem confirmar."""
        with self._transaction() as db:
            row = db.execute("SELECT versao_remota FROM definicao WHERE uid = ?", (uid,)).fetchone()
            if row is None:
                return
            if row[0] is None:
                db.execute("DELETE FROM definicao WHERE uid = ?", (uid,))
            else:
                db.execute("UPDATE definicao SET excluida = 1, sujo = 1, atualizado_em = ? WHERE uid = ?",
                           (now_utc(), uid))
            if self.meta('ultima_ativa') == uid:
                db.execute("DELETE FROM meta WHERE chave = 'ultima_ativa'")

    def set_meta(self, key, value):
        with self._transaction() as db:
            db.execute("INSERT INTO meta (chave, valor) VALUES (?, ?) "
                       "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor", (key, str(value)))

    def set_last_active(self, uid):
        """Guarda a definição ativa (uid do banco ou de uma embutida); `None` apaga."""
        if uid is not None and uid not in BUILTIN_UIDS and self.get(uid) is None:
            raise StoreError(N_("Definição não encontrada no banco."))
        with self._transaction() as db:
            if uid is None:
                db.execute("DELETE FROM meta WHERE chave = 'ultima_ativa'")
            else:
                db.execute("INSERT INTO meta (chave, valor) VALUES ('ultima_ativa', ?) "
                           "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor", (uid,))

    def mark_synced(self, uid, remote_version):
        """A nuvem aceitou ou entregou esta versão (onda 7): limpa `sujo` e guarda a versão remota."""
        with self._transaction() as db:
            db.execute("UPDATE definicao SET sujo = 0, versao_remota = ? WHERE uid = ?", (int(remote_version), uid))

    def import_documents(self, documents, replace=()):
        """Importa numa transação. Uid novo entra; igual não muda; uid existente com conteúdo diferente só é
        substituído se estiver em `replace` (o usuário marcou no diálogo). Devolve as listas de uids por destino."""
        replace = set(replace)
        report = {'added': [], 'replaced': [], 'unchanged': [], 'pending': [], 'refused': []}
        with self._transaction() as db:
            for document in documents:
                try:
                    uid = _uid_of(document)
                except StoreError:
                    report['refused'].append(document.get("uid") if isinstance(document, dict) else None)
                    continue
                stored = self.get(uid)
                if stored is None:
                    self._put(db, uid, document)
                    report['added'].append(uid)
                elif same_content(stored, document):
                    report['unchanged'].append(uid)
                elif uid in replace:
                    self._put(db, uid, document)
                    report['replaced'].append(uid)
                else:
                    report['pending'].append(uid)
        return report


def same_content(a, b):
    """Mesmo conteúdo, ignorando o carimbo local de versão e data."""
    def strip(document):
        return {k: v for k, v in document.items() if k not in ('version', 'updated_at')}
    return json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)
