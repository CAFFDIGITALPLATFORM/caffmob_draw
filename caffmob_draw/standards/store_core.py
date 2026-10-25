"""Banco local do Padrão de Dimensões (feature 067, D-26; data-delta §6): núcleo puro.

O padrão da marcenaria vive fora do `.blend`, num `padroes.sqlite3`, para não precisar ser configurado de novo a cada
arquivo (RN-15). Python puro com `sqlite3` da biblioteca padrão e caminho injetado; a ligação com o Blender (onde
fica o arquivo) é de `standards/store.py`. Cada definição é guardada como o documento de `io_json.values_to_document`.
As embutidas nunca entram. Toda gravação é uma transação.

Onda 7 (T150; D-34): esquema 2. Cada linha guarda a `Idempotency-Key` da escrita pendente na nuvem
(`operacao_pendente`, reaproveitada na repetição e trocada quando o conteúdo muda) e a tabela `conflito` guarda o que
a sincronia não decide sozinha (RF-035), com o documento remoto, até o usuário escolher. Banco do esquema 1 migra no
próprio banco, ao abrir.
"""

import datetime
import json
import sqlite3
import uuid

from . import builtin
from ..data.i18n import N_

SCHEMA = 2
BUILTIN_UIDS = frozenset(uid for uid, _name, _market in builtin.BUILTINS)

_CONFLICT_DDL = (
    "CREATE TABLE IF NOT EXISTS conflito ("
    " uid TEXT PRIMARY KEY,"
    " tipo TEXT NOT NULL,"
    " lado TEXT NOT NULL DEFAULT '',"
    " versao_remota INTEGER,"
    " documento_remoto TEXT,"
    " detectado_em TEXT NOT NULL)")

_DDL = (
    "CREATE TABLE IF NOT EXISTS definicao ("
    " uid TEXT PRIMARY KEY,"
    " documento TEXT NOT NULL,"
    " atualizado_em TEXT NOT NULL,"
    " versao_remota INTEGER,"
    " sujo INTEGER NOT NULL DEFAULT 1,"
    " excluida INTEGER NOT NULL DEFAULT 0,"
    " operacao_pendente TEXT)",
    "CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT)",
    _CONFLICT_DDL,
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


def _migrate(db):
    """Esquema 1 → 2: a coluna da chave pendente (a tabela `conflito` já veio do `_DDL`)."""
    columns = {row[1] for row in db.execute("PRAGMA table_info(definicao)")}
    if 'operacao_pendente' not in columns:
        db.execute("ALTER TABLE definicao ADD COLUMN operacao_pendente TEXT")
    db.execute("INSERT INTO meta (chave, valor) VALUES ('esquema', ?) "
               "ON CONFLICT(chave) DO UPDATE SET valor = excluded.valor", (str(SCHEMA),))


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
        with self._transaction() as db:
            existed = db.execute("SELECT 1 FROM sqlite_master WHERE name = 'definicao'").fetchone() is not None
            for statement in _DDL:
                db.execute(statement)
            if existed:
                _migrate(db)
            db.execute("INSERT OR IGNORE INTO meta (chave, valor) VALUES ('esquema', ?)", (str(SCHEMA),))

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
            "sujo = 1, excluida = 0, operacao_pendente = NULL",
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
                db.execute("UPDATE definicao SET excluida = 1, sujo = 1, operacao_pendente = NULL, atualizado_em = ? "
                           "WHERE uid = ?",
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

    def mark_synced(self, uid, remote_version, dirty=False):
        """A nuvem aceitou ou entregou esta versão (onda 7): limpa `sujo` e guarda a versão remota. Com `dirty`, só
        guarda a versão (o conteúdo mudou enquanto o pedido estava no ar e ainda precisa subir)."""
        with self._transaction() as db:
            db.execute("UPDATE definicao SET sujo = ?, versao_remota = ?, operacao_pendente = NULL WHERE uid = ?",
                       (1 if dirty else 0, int(remote_version), uid))

    # Sincronia com a nuvem (onda 7) -------------------------------------------------------------------------

    def rows(self):
        """Todas as linhas, inclusive as excluídas à espera da nuvem: (uid, documento, estado)."""
        rows = self._db.execute("SELECT uid, documento, versao_remota, sujo, excluida FROM definicao ORDER BY uid")
        return [(r[0], json.loads(r[1]), {'versao_remota': r[2], 'sujo': bool(r[3]), 'excluida': bool(r[4])})
                for r in rows.fetchall()]

    def pending_key(self, uid):
        """`Idempotency-Key` da escrita pendente: a mesma até a nuvem confirmar ou o conteúdo mudar."""
        with self._transaction() as db:
            row = db.execute("SELECT operacao_pendente FROM definicao WHERE uid = ?", (uid,)).fetchone()
            if row is None:
                raise StoreError(N_("Definição não encontrada no banco."))
            if row[0]:
                return row[0]
            key = str(uuid.uuid4())
            db.execute("UPDATE definicao SET operacao_pendente = ? WHERE uid = ?", (key, uid))
            return key

    def drop_pending_key(self, uid):
        """A nuvem recusou a chave (`CHAVE_REUTILIZADA`): a próxima tentativa gera outra."""
        with self._transaction() as db:
            db.execute("UPDATE definicao SET operacao_pendente = NULL WHERE uid = ?", (uid,))

    def apply_remote(self, document, remote_version):
        """Grava o documento que veio da nuvem, já sincronizado (não fica `sujo`)."""
        uid = _uid_of(document)
        with self._transaction() as db:
            db.execute(
                "INSERT INTO definicao (uid, documento, atualizado_em, versao_remota, sujo, excluida) "
                "VALUES (?, ?, ?, ?, 0, 0) ON CONFLICT(uid) DO UPDATE SET documento = excluded.documento, "
                "atualizado_em = excluded.atualizado_em, versao_remota = excluded.versao_remota, sujo = 0, "
                "excluida = 0, operacao_pendente = NULL",
                (uid, json.dumps(document, ensure_ascii=False, sort_keys=True), now_utc(), int(remote_version)))
            db.execute("DELETE FROM conflito WHERE uid = ?", (uid,))

    def purge(self, uid):
        """Tira a linha de vez (a exclusão chegou aos dois lados)."""
        with self._transaction() as db:
            db.execute("DELETE FROM definicao WHERE uid = ?", (uid,))
            db.execute("DELETE FROM conflito WHERE uid = ?", (uid,))
            if self.meta('ultima_ativa') == uid:
                db.execute("DELETE FROM meta WHERE chave = 'ultima_ativa'")

    def add_conflict(self, uid, kind, side='', remote_version=None, remote_document=None):
        """Registra (ou atualiza) o conflito do uid; nada muda na definição até o usuário escolher (RF-035)."""
        remote = None if remote_document is None else json.dumps(remote_document, ensure_ascii=False, sort_keys=True)
        with self._transaction() as db:
            db.execute(
                "INSERT INTO conflito (uid, tipo, lado, versao_remota, documento_remoto, detectado_em) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(uid) DO UPDATE SET tipo = excluded.tipo, lado = excluded.lado, "
                "versao_remota = excluded.versao_remota, documento_remoto = excluded.documento_remoto, "
                "detectado_em = excluded.detectado_em",
                (uid, str(kind), str(side or ''), remote_version, remote, now_utc()))

    def conflicts(self):
        rows = self._db.execute("SELECT uid, tipo, lado, versao_remota, documento_remoto, detectado_em "
                                "FROM conflito ORDER BY uid").fetchall()
        return [_conflict(row) for row in rows]

    def conflict(self, uid):
        row = self._db.execute("SELECT uid, tipo, lado, versao_remota, documento_remoto, detectado_em "
                               "FROM conflito WHERE uid = ?", (uid,)).fetchone()
        return _conflict(row) if row else None

    def local_document(self, uid):
        """Documento local, inclusive o da linha excluída (o conflito mostra as duas versões)."""
        row = self._db.execute("SELECT documento FROM definicao WHERE uid = ?", (uid,)).fetchone()
        return json.loads(row[0]) if row else None

    def remove_conflict(self, uid):
        with self._transaction() as db:
            db.execute("DELETE FROM conflito WHERE uid = ?", (uid,))

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


def _conflict(row):
    return {'uid': row[0], 'tipo': row[1], 'lado': row[2], 'versao_remota': row[3],
            'documento_remoto': json.loads(row[4]) if row[4] else None, 'detectado_em': row[5]}


def same_content(a, b):
    """Mesmo conteúdo, ignorando o carimbo local de versão e data."""
    def strip(document):
        return {k: v for k, v in document.items() if k not in ('version', 'updated_at')}
    return json.dumps(strip(a), sort_keys=True) == json.dumps(strip(b), sort_keys=True)
