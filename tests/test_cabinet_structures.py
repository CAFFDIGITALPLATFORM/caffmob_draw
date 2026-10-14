"""Testes do catálogo de estruturas de caixa (feature 015, T007): `caffmob_draw/cabinet_editor/structures_core.py`."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import structures_core as sc

BASE = {
    "schema-version": 1,
    "environments": [{"id": "COZ", "label_pt": "Cozinhas", "label_en": "Kitchens", "line": "COZ"}],
    "structures": [],
    "legacy_map": [],
}


def item(sid="a", **over):
    data = {"id": sid, "environment": "COZ", "group": "INFERIOR", "label_pt": "A", "label_en": "A",
            "assembly": "LATERAL", "sides_to_floor": False, "bays": 1,
            "size_mm": {"width": 500, "height": None, "depth": None},
            "components": {"LEFT": True, "RIGHT": True}, "division_variants": [], "order": 1}
    data.update(over)
    return data


def catalog(structures, legacy=()):
    doc = dict(BASE, structures=list(structures), legacy_map=list(legacy))
    return sc.parse(json.dumps(doc))


class CatalogoRealTest(unittest.TestCase):
    def test_carrega_as_17_estruturas_sem_aviso(self):
        cat = sc.load(sc.CATALOG)
        self.assertEqual(cat.warnings, ())
        self.assertEqual(len(cat.structures), 17)
        self.assertEqual([e.id for e in cat.environments], ['COZ', 'DOR'])
        self.assertEqual(len(cat.by_environment('COZ')), 12)
        self.assertEqual(len(cat.by_environment('DOR')), 5)

    def test_balcao_sem_base_superior_e_com_sarrafos(self):
        s = sc.load(sc.CATALOG).by_id('coz_inferior_divisoria')
        self.assertFalse(s.has('TOP'))
        self.assertTrue(s.has('STRETCHER_FRONT'))
        self.assertTrue(s.has('STRETCHER_BACK'))
        self.assertFalse(s.has('TOP_LINEAR'))
        self.assertEqual(s.cabinet_type, 'BASE')
        self.assertEqual(s.width_mm, 500.0)
        self.assertEqual(s.height_mm, 0.0)               # do Padrão de Dimensões (D-19)

    def test_divisoria_sobre_base_sem_base_inferior(self):
        s = sc.load(sc.CATALOG).by_id('dor_divisoria_sobre_base')
        self.assertFalse(s.has('BOTTOM'))
        self.assertTrue(s.has('TOE_KICK'))

    def test_equivalencia_dos_modulos_antigos(self):
        cat = sc.load(sc.CATALOG)
        self.assertEqual(cat.legacy_structure('COZ', 'BASE'), 'coz_inferior_divisoria')
        self.assertEqual(cat.legacy_structure('DOR', 'TALL'), 'dor_armario')
        self.assertEqual(cat.legacy_structure('SAL', 'WALL'), 'coz_superior_divisoria')   # reserva "*"


class ValidacaoTest(unittest.TestCase):
    def test_versao_desconhecida_recusa_tudo(self):
        cat = sc.parse(json.dumps(dict(BASE, **{"schema-version": 2}, structures=[item()])))
        self.assertEqual(cat.structures, ())
        self.assertIn("versão desconhecida", cat.warnings[0])

    def test_json_invalido(self):
        cat = sc.parse("{")
        self.assertEqual(cat.structures, ())
        self.assertTrue(cat.warnings)

    def test_id_repetido_pula_so_a_segunda(self):
        cat = catalog([item("a"), item("a")])
        self.assertEqual([s.id for s in cat.structures], ["a"])
        self.assertIn("Estrutura a: identificador repetido", cat.warnings)

    def test_ambiente_e_grupo_desconhecidos(self):
        cat = catalog([item("a", environment="XX"), item("b", group="CANTO"), item("c")])
        self.assertEqual([s.id for s in cat.structures], ["c"])
        self.assertIn("Estrutura a: ambiente desconhecido", cat.warnings)
        self.assertIn("Estrutura b: grupo desconhecido", cat.warnings)

    def test_peca_desconhecida(self):
        cat = catalog([item("a", components={"LEFT": True, "PORTA_MAGICA": True})])
        self.assertEqual(cat.structures, ())
        self.assertIn("Estrutura a: peça desconhecida (PORTA_MAGICA)", cat.warnings)

    def test_medida_nao_numerica(self):
        cat = catalog([item("a", size_mm={"width": "500", "height": None, "depth": None})])
        self.assertEqual(cat.structures, ())
        self.assertIn("Estrutura a: largura inválido", cat.warnings)

    def test_vaos_fora_da_faixa(self):
        cat = catalog([item("a", bays=0), item("b", bays=11)])
        self.assertEqual(cat.structures, ())

    def test_equivalencia_para_estrutura_inexistente_e_pulada(self):
        cat = catalog([item("a")], legacy=[{"line": "COZ", "cabinet_type": "BASE", "structure": "zz"},
                                           {"line": "*", "cabinet_type": "BASE", "structure": "a"}])
        self.assertEqual(cat.legacy, (("*", "BASE", "a"),))
        self.assertEqual(cat.legacy_structure('COZ', 'BASE'), "a")
        self.assertTrue(any("zz" in w for w in cat.warnings))

    def test_ordem_na_aba(self):
        cat = catalog([item("b", order=20), item("a", order=10)])
        self.assertEqual([s.id for s in cat.by_environment("COZ")], ["a", "b"])


if __name__ == '__main__':
    unittest.main()
