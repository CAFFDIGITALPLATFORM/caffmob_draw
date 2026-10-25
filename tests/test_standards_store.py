"""Banco local do Padrão de Dimensões (feature 067, T129; RF-032, RF-033, D-26, D-28).

Todo banco aqui nasce num diretório temporário passado por parâmetro (D-35): nenhum teste abre o banco real.
"""

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.standards import io_json, store
from caffmob_draw.standards.store_core import StandardsStore, StoreError, same_content


def _document(uid, name="Marcenaria X", lateral=15.0, version=1):
    values = {'COZ.sheets.LAT.thickness': lateral, 'COZ.sheets.LAT.material': 'MDF'}
    return io_json.values_to_document(name, uid, 'BR', 'USER', version, "2026-10-24T12:00:00-03:00", values)


class StoreTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / "padroes.sqlite3"
        self.store = StandardsStore(self.path)

    def tearDown(self):
        self.store.close()
        self._dir.cleanup()

    def test_gravar_ler_renomear_e_apagar(self):
        self.store.put(_document("u1"))
        self.assertEqual(self.store.get("u1")["name"], "Marcenaria X")
        self.store.rename("u1", "Marcenaria Y")
        self.assertEqual(self.store.get("u1")["name"], "Marcenaria Y")
        self.store.delete("u1")
        self.assertIsNone(self.store.get("u1"))
        self.assertIsNone(self.store.state("u1"))           # nunca foi à nuvem: sai do banco já

    def test_sobrevive_a_outra_conexao(self):
        self.store.put(_document("u1", lateral=18.0))
        self.store.set_last_active("u1")
        self.store.close()
        with StandardsStore(self.path) as other:
            self.assertEqual(other.get("u1")["lines"]["COZ"]["sheets"]["LAT"]["thickness"], 18.0)
            self.assertEqual(other.last_active, "u1")
            self.assertEqual(other.schema(), 1)
        self.store = StandardsStore(self.path)

    def test_documento_continua_valido_para_o_io_json(self):
        self.store.put(_document("u1", lateral=18.0))
        values, warnings = io_json.document_to_values(self.store.get("u1"))
        self.assertEqual(values['COZ.sheets.LAT.thickness'], 18.0)
        self.assertEqual(warnings, [])

    def test_embutidas_nunca_entram(self):
        for uid in ("builtin-br", "builtin-us"):
            with self.assertRaises(StoreError):
                self.store.put(_document(uid))
        self.assertEqual(self.store.documents(), [])
        self.store.set_last_active("builtin-br")           # a ativa pode ser uma embutida
        self.assertEqual(self.store.last_active, "builtin-br")

    def test_ultima_ativa(self):
        self.assertIsNone(self.store.last_active)
        with self.assertRaises(StoreError):
            self.store.set_last_active("inexistente")
        self.store.put(_document("u1"))
        self.store.set_last_active("u1")
        self.assertEqual(self.store.last_active, "u1")
        self.store.delete("u1")
        self.assertIsNone(self.store.last_active)

    def test_sujo_e_versao_remota(self):
        self.store.put(_document("u1"))
        self.assertEqual(self.store.state("u1")["sujo"], True)
        self.assertIsNone(self.store.state("u1")["versao_remota"])
        self.store.mark_synced("u1", 3)
        self.assertEqual(self.store.state("u1")["sujo"], False)
        self.assertEqual(self.store.state("u1")["versao_remota"], 3)
        self.store.put(_document("u1", lateral=18.0))
        self.assertEqual(self.store.state("u1")["sujo"], True)
        self.assertEqual(self.store.state("u1")["versao_remota"], 3)
        self.store.delete("u1")                             # já foi à nuvem: fica marcada até a sincronia
        self.assertIsNone(self.store.get("u1"))
        self.assertEqual(self.store.state("u1")["excluida"], True)

    def test_gravacao_e_transacao(self):
        self.store.put(_document("u1"))
        bad = _document("u2")
        bad["lines"] = object()                             # json.dumps falha no meio da gravação
        with self.assertRaises(TypeError):
            self.store.import_documents([_document("u3"), bad])
        self.assertIsNone(self.store.get("u3"))             # nada do lote entrou
        self.assertIsNotNone(self.store.get("u1"))

    def test_versao_mais_antiga_que_a_do_banco(self):
        self.store.put(_document("u1", version=4))
        self.assertTrue(self.store.is_older_than_stored(_document("u1", version=2)))
        self.assertFalse(self.store.is_older_than_stored(_document("u1", version=4)))
        self.assertFalse(self.store.is_older_than_stored(_document("u9", version=1)))

    def test_importar_uid_existente_sem_confirmar_nao_muda_nada(self):
        self.store.put(_document("u1", lateral=15.0))
        before = sqlite3.connect(self.path).execute("SELECT documento, atualizado_em FROM definicao").fetchall()
        report = self.store.import_documents([_document("u1", lateral=18.0)])
        self.assertEqual(report['pending'], ["u1"])
        after = sqlite3.connect(self.path).execute("SELECT documento, atualizado_em FROM definicao").fetchall()
        self.assertEqual(before, after)
        report = self.store.import_documents([_document("u1", lateral=18.0), _document("u2")], replace={"u1"})
        self.assertEqual((report['replaced'], report['added']), (["u1"], ["u2"]))
        self.assertEqual(self.store.get("u1")["lines"]["COZ"]["sheets"]["LAT"]["thickness"], 18.0)

    def test_conteudo_igual_ignora_versao_e_data(self):
        a, b = _document("u1", version=1), _document("u1", version=7)
        b["updated_at"] = "2027-01-01T00:00:00Z"
        self.assertTrue(same_content(a, b))
        self.store.put(a)
        self.assertEqual(self.store.import_documents([b])['unchanged'], ["u1"])


class PackTest(unittest.TestCase):
    def test_pacote_ida_e_volta_valor_a_valor(self):
        documents = [_document("u1", lateral=15.0), _document("u2", "Marcenaria Z", lateral=18.0)]
        pack = io_json.pack_documents(documents, "2026-10-24T12:00:00Z")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ("tudo" + io_json.PACK_EXTENSION)
            io_json.write_document(path, pack)
            back = io_json.unpack_documents(io_json.read_document(path))
        self.assertEqual(back, documents)
        for original, read in zip(documents, back):
            self.assertEqual(io_json.document_to_values(original), io_json.document_to_values(read))

    def test_aceita_btmdim_solto_e_recusa_versao_nova(self):
        self.assertEqual(io_json.unpack_documents(_document("u1")), [_document("u1")])
        pack = io_json.pack_documents([], "x")
        pack["schema_version"] = 2
        with self.assertRaises(io_json.StandardFileError):
            io_json.unpack_documents(pack)
        broken = io_json.pack_documents([{"schema": "outro"}], "x")
        with self.assertRaises(io_json.StandardFileError):
            io_json.unpack_documents(broken)


class StorePathTest(unittest.TestCase):
    """O caminho do banco troca por `override_path` e por `CAFFMOB_DRAW_STANDARDS_DB` (D-35)."""

    def setUp(self):
        self._env = os.environ.pop(store.ENV_PATH, None)
        self._dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        store.close()
        store.override_path = None
        os.environ.pop(store.ENV_PATH, None)
        if self._env is not None:
            os.environ[store.ENV_PATH] = self._env
        self._dir.cleanup()

    def test_override_vence_a_variavel(self):
        os.environ[store.ENV_PATH] = str(Path(self._dir.name) / "env.sqlite3")
        self.assertEqual(store.path(), os.environ[store.ENV_PATH])
        store.override_path = Path(self._dir.name) / "sub" / "teste.sqlite3"
        self.assertEqual(store.path(), str(store.override_path))
        first = store.get()
        first.put(_document("u1"))
        self.assertIs(store.get(), first)                  # mesma conexão enquanto o caminho não muda
        store.override_path = None
        self.assertIsNot(store.get(), first)               # caminho mudou: reabre no da variável
        self.assertIsNone(store.get().get("u1"))


if __name__ == '__main__':
    unittest.main()
