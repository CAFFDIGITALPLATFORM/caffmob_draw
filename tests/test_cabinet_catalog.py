"""Testes do catálogo do Construtor (feature 008, T005): `caffmob_draw/cabinet_editor/catalog.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import catalog as cat


class CatalogTest(unittest.TestCase):
    def test_ids_unicos(self):
        ids = [i.id for i in cat.ITEMS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_divisoes(self):
        # os dois itens da 008 continuam primeiro; as variantes por ambiente da 015 vêm depois (AmbienteTest)
        self.assertEqual([i.label for i in cat.items('DIVISIONS', 'RECESS') if not i.environments][:2],
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


class AmbienteTest(unittest.TestCase):
    """Feature 015 (T011; RN-15 a RN-17, D-13): catálogo das abas filtrado pelo ambiente da estrutura."""

    def ids(self, tab, group, env):
        return {i.id for i in cat.items(tab, group, environment=env)}

    def test_divisoes_do_dormitorio_e_da_cozinha(self):
        dor = self.ids('DIVISIONS', 'RECESS', 'DOR')
        coz = self.ids('DIVISIONS', 'RECESS', 'COZ')
        self.assertTrue({'DIV_MONTANTE', 'SHELF_INVISIBLE', 'SHELF_SLIDE', 'SHELF_WIRE'} <= dor)
        self.assertNotIn('DIV_CORTA_SAR', dor)
        self.assertTrue({'DIV_CORTA_SAR', 'DIV_C_REB', 'DIV_KEEP_BACK'} <= coz)
        self.assertNotIn('SHELF_INVISIBLE', coz)
        self.assertIn('DIVISION_ONLY', dor & coz)                    # vale em todos
        self.assertIn('DIV_NO_RECESS', dor & coz)                    # itens da 008 continuam em todos

    def test_internos_de_roupeiro_so_no_dormitorio(self):
        labels = {i.label for i in cat.items('INTERIOR', 'WARDROBE', environment='DOR')}
        self.assertTrue({"Cabideiro 01", "Cabideiro 02", "Cab Extensível", "Tubo", "Tubo s/ Reforço",
                         "Sapateira", "Porta Cintos/Gravatas"} <= labels)
        self.assertTrue(any(lbl.startswith("Calceiro Madeira") for lbl in labels))
        self.assertTrue(any(lbl.startswith("Calceiro Aramado") for lbl in labels))
        self.assertEqual(cat.items('INTERIOR', 'WARDROBE', environment='COZ'), [])
        self.assertEqual(cat.items('INTERIOR', 'PANELS', environment='DOR'), [])   # eletros só na cozinha

    def test_gavetas_do_dormitorio(self):
        labels = {i.label for i in cat.items('DRAWERS', environment='DOR')}
        self.assertTrue({"Interna p/ trilho", "Sapateira", "Prateleira Corrediça", "Externas"} <= labels)
        self.assertNotIn("Interna p/ trilho", {i.label for i in cat.items('DRAWERS', environment='COZ')})

    def test_sem_ambiente_mostra_tudo(self):
        self.assertIn('SHELF_INVISIBLE', {i.id for i in cat.items('DIVISIONS', 'RECESS')})

    def test_arvore_com_as_pecas_da_estrutura(self):
        keys = [k for k, *_ in cat.TREE]
        for key in ('STRETCHER_FRONT', 'STRETCHER_BACK', 'STRETCHER_FULL', 'TOP_LINEAR', 'TOE_KICK', 'CASTERS'):
            self.assertIn(key, keys)
            self.assertIn(key, cat.STRUCTURE_KEYS)
        self.assertIn('SIDES_EXTENDED', cat.DISABLED)


if __name__ == '__main__':
    unittest.main()
