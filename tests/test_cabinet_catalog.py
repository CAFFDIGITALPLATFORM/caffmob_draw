"""Testes do catálogo do Construtor (feature 008, T005): `caffmob_draw/cabinet_editor/catalog.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import catalog as cat


class CatalogTest(unittest.TestCase):
    def test_ids_unicos(self):
        ids = [i.id for i in cat.ITEMS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_divisoes(self):
        self.assertEqual([i.label for i in cat.items('DIVISIONS', 'RECESS')],
                         ["Interna s/ Recuo — Tras 15mm", "Interna c/ Recuo — Tras 15mm"])
        spacers = cat.items('DIVISIONS', 'SPACER')
        self.assertEqual([i.label for i in spacers],
                         ["Distanciador 15mm", "Distanciador Duplo 30mm", "Distanciador p/ Divisão 15mm"])
        self.assertEqual([i.param('thickness') for i in spacers], [15.0, 30.0, 15.0])

    def test_gavetas(self):
        self.assertEqual(cat.get('DRAWER_CF').description, "Caixa Gaveta c/ Contra Frente")
        self.assertEqual(cat.get('FRONT_RETA').label, "Reta")
        self.assertEqual({i.group for i in cat.items('DRAWERS')}, {'DRAWERS', 'TALL', 'INTERNAL', 'BLUM', 'FRONTS'})

    def test_internos_das_capturas(self):
        external = [i.label for i in cat.items('INTERIOR', 'PANELS', filter_='EXTERNAL')]
        for label in ("Painel Forno/Micro Externo", "Painel Forno Externo", "Painel Micro Externo",
                      "Painel Cafeteira Externo", "Frontal Externo", "Forno", "Microondas", "Cafeteira", "Respiro"):
            self.assertIn(label, external)
        self.assertTrue(cat.items('INTERIOR', 'PANELS', filter_='BUILT_IN'))
        self.assertEqual(cat.get('OVEN').size_mm, (595.0, 595.0, 560.0))
        self.assertTrue(cat.items('INTERIOR', 'SUPPORTS'))
        self.assertTrue(cat.items('INTERIOR', 'PISTONS'))

    def test_deslizantes(self):
        wood = [i.label for i in cat.items('SLIDING', 'WOOD')]
        self.assertEqual(len(wood), 18)
        for label in ("Lisa", "Gola Vertical 2L", "Perfil Y Vertical 2L", "Obispa — Pux Integrados",
                      "Altero — Pux Integrados"):
            self.assertIn(label, wood)
        self.assertTrue(cat.items('SLIDING', 'ALUMINIUM'))
        self.assertTrue(cat.get('SLIDE_GOLA_VERTICAL_2L').groove)
        self.assertFalse(cat.get('SLIDE_LISA').groove)

    def test_fundos_e_invertido(self):
        self.assertEqual([i.group for i in cat.items('BACKS')], ['FULL', 'RECESSED'])
        self.assertFalse(cat.get('BACK_FULL').invertible)
        self.assertTrue(cat.get('SLIDE_LISA').invertible)

    def test_cabe(self):
        oven = cat.get('PANEL_OVEN_EXT')
        self.assertIsNone(oven.too_small((700.0, 700.0, 560.0)))
        self.assertEqual(oven.too_small((700.0, 340.0, 560.0)), (615.0, 615.0, 560.0))
        self.assertEqual(oven.too_small((700.0, 700.0, 350.0)), (615.0, 615.0, 560.0))   # profundidade (EC-15)


if __name__ == '__main__':
    unittest.main()
