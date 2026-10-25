"""Decisão da sincronia do Padrão de Dimensões (feature 067, T139; RF-034, RF-035, D-34, auditoria A001)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.standards import sync_core as sc


def doc(name="Marcenaria X", thickness=15, **envelope):
    base = {"schema": "caffmob_draw.dimension-standard", "schema_version": 1, "uid": "u1", "name": name,
            "market": "BR", "unit": "mm", "lines": {"COZ": {"sheets": {"LAT": {"thickness": thickness}}}},
            "version": 1, "updated_at": "2026-10-25T10:00:00Z", "source": "USER"}
    base.update(envelope)
    return base


class CanonicalTest(unittest.TestCase):
    def test_envelope_fica_fora(self):
        self.assertTrue(sc.same_content(doc(version=1), doc(version=9, updated_at="2030", source="LIBRARY")))
        self.assertFalse(sc.same_content(doc(), doc(thickness=18)))
        self.assertEqual(sc.digest(doc(version=2)), sc.digest(doc(version=3)))

    def test_ordem_das_chaves_nao_importa(self):
        a = doc()
        b = dict(reversed(list(a.items())))
        self.assertEqual(sc.canonical(a), sc.canonical(b))


class DecideTest(unittest.TestCase):
    def test_conteudo_igual_adota_a_nuvem_sem_conflito(self):
        local = sc.Local(doc(version=4), remote_version=None, dirty=True)
        self.assertEqual(sc.decide(local, sc.Remote(3)).action, sc.COMPARE)       # primeira sincronia
        self.assertEqual(sc.after_compare(local, sc.Remote(3), doc(version=1)).action, sc.ADOPT)

    def test_so_a_nuvem_mudou(self):
        self.assertEqual(sc.decide(sc.Local(doc(), 2), sc.Remote(3)).action, sc.DOWNLOAD)
        self.assertEqual(sc.decide(None, sc.Remote(1)).action, sc.DOWNLOAD)

    def test_so_o_local_mudou(self):
        d = sc.decide(sc.Local(doc(), 2, dirty=True), sc.Remote(2))
        self.assertEqual((d.action, d.if_match), (sc.UPLOAD, 2))
        self.assertEqual(sc.decide(sc.Local(doc()), None).action, sc.CREATE)

    def test_os_dois_mudaram(self):
        local = sc.Local(doc(thickness=18), 2, dirty=True)
        self.assertEqual(sc.decide(local, sc.Remote(3)).action, sc.COMPARE)
        d = sc.after_compare(local, sc.Remote(3), doc(thickness=25))
        self.assertEqual((d.action, d.if_match), (sc.EDIT_CONFLICT, 3))
        self.assertEqual(sc.after_compare(local, sc.Remote(3), doc(thickness=18)).action, sc.ADOPT)

    def test_apagar_x_editar_e_conflito(self):
        d = sc.decide(sc.Local(doc(), 2, dirty=True), sc.Remote(3, deleted=True))
        self.assertEqual((d.action, d.side), (sc.DELETE_CONFLICT, 'CLOUD'))
        d = sc.decide(sc.Local(doc(), 2, deleted=True), sc.Remote(3))
        self.assertEqual((d.action, d.side), (sc.DELETE_CONFLICT, 'LOCAL'))

    def test_exclusao_propaga(self):
        d = sc.decide(sc.Local(doc(), 2, deleted=True), sc.Remote(2))
        self.assertEqual((d.action, d.if_match), (sc.DELETE_REMOTE, 2))
        self.assertEqual(sc.decide(sc.Local(doc(), 2), sc.Remote(3, deleted=True)).action, sc.DELETE_LOCAL)
        self.assertEqual(sc.decide(sc.Local(doc(), 2, deleted=True), sc.Remote(3, deleted=True)).action, sc.PURGE)
        self.assertEqual(sc.decide(None, sc.Remote(3, deleted=True)).action, sc.NOTHING)

    def test_nada_a_fazer(self):
        self.assertEqual(sc.decide(sc.Local(doc(), 2), sc.Remote(2)).action, sc.NOTHING)


class StatusTest(unittest.TestCase):
    def test_409_vira_conflito(self):
        up = sc.Decision(sc.UPLOAD, 2)
        self.assertEqual(sc.on_status(up, 409, sc.Local(doc(), 2, True)).action, sc.EDIT_CONFLICT)
        delete = sc.Decision(sc.DELETE_REMOTE, 2)
        self.assertEqual(sc.on_status(delete, 409, sc.Local(doc(), 2, deleted=True)).action, sc.DELETE_CONFLICT)

    def test_404_na_atualizacao(self):
        up = sc.Decision(sc.UPLOAD, 2)
        self.assertEqual(sc.on_status(up, 404, sc.Local(doc(), 2, True)).action, sc.DELETE_CONFLICT)
        self.assertEqual(sc.on_status(up, 404, sc.Local(doc(), 2, False)).action, sc.DELETE_LOCAL)
        self.assertIsNone(sc.on_status(up, 200, sc.Local(doc(), 2, True)))


class ResolveTest(unittest.TestCase):
    def test_escolhas_de_edicao(self):
        self.assertEqual(sc.resolve(sc.EDIT_CONFLICT, sc.KEEP_MINE, remote_version=5),
                         sc.Decision(sc.UPLOAD, 5))
        self.assertEqual(sc.resolve(sc.EDIT_CONFLICT, sc.KEEP_CLOUD, remote_version=5).action, sc.ADOPT)

    def test_escolhas_de_apagar_x_editar(self):
        self.assertEqual(sc.resolve(sc.DELETE_CONFLICT, sc.KEEP_DELETED, 'CLOUD').action, sc.DELETE_LOCAL)
        self.assertEqual(sc.resolve(sc.DELETE_CONFLICT, sc.KEEP_EDIT, 'CLOUD').action, sc.CREATE)
        self.assertEqual(sc.resolve(sc.DELETE_CONFLICT, sc.KEEP_DELETED, 'LOCAL', 7), sc.Decision(sc.DELETE_REMOTE, 7))
        self.assertEqual(sc.resolve(sc.DELETE_CONFLICT, sc.KEEP_EDIT, 'LOCAL').action, sc.DOWNLOAD)

    def test_escolha_errada_recusa(self):
        with self.assertRaises(ValueError):
            sc.resolve(sc.EDIT_CONFLICT, sc.KEEP_DELETED)

    def test_campos_que_diferem(self):
        self.assertEqual(sc.changed_fields(doc(), doc(name="Y", version=9)), ["name"])


class PagesTest(unittest.TestCase):
    def test_paginas_e_plano(self):
        self.assertEqual(sc.page_path(), "/padroes-de-dimensao")
        self.assertEqual(sc.page_path("50"), "/padroes-de-dimensao?depois=50")
        remotes, cursor = sc.read_page({"itens": [{"uid": "b", "version": 2, "excluido": True}], "proximo": "50"})
        self.assertEqual((remotes, cursor), ({"b": sc.Remote(2, True)}, "50"))
        self.assertIsNone(sc.read_page({"itens": [], "proximo": None})[1])
        plano = sc.plan({"a": sc.Local(doc())}, remotes)
        self.assertEqual([(u, d.action) for u, d in plano], [("a", sc.CREATE), ("b", sc.NOTHING)])


if __name__ == '__main__':
    unittest.main()
