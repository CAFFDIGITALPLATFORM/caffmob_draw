"""Testes do layout do painel BIBLIOTECA CAFFMOB (feature 012, T008; D-14, D-30)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import layout_core as lc


def width(text):
    return 7.0 * len(text)


ITEMS = [('CREATE_CABINET', "Criar armário"), ('CAT:Cozinha', "Cozinha"), ('CAT:Banheiro', "Banheiro"),
         ('CREATE_CATEGORY', "Criar categoria")]


class LayoutTest(unittest.TestCase):
    def test_fechado_no_canto(self):
        lay = lc.panel_layout(0, 600, 1.0, None, False, ITEMS, width)
        x, y, w, h = lay.label
        self.assertEqual(x, lc.MARGIN_X)
        self.assertEqual(y + h, 600 - lc.MARGIN_Y)
        self.assertEqual(lay.items, [])
        self.assertEqual(lc.hit(lay, x + 1, y + 1), 'LABEL')
        self.assertIsNone(lc.hit(lay, 500, 300))

    def test_com_hud_fica_depois_do_botao(self):
        lay = lc.panel_layout(0, 600, 1.0, 120.0, False, ITEMS, width)
        self.assertEqual(lay.label[0], 120.0 + lc.GAP)

    def test_aberto_em_ordem(self):
        lay = lc.panel_layout(0, 600, 1.0, None, True, ITEMS, width)
        self.assertEqual([key for key, _rect in lay.items], [k for k, _l in ITEMS])
        tops = [rect[1] for _key, rect in lay.items]
        self.assertEqual(tops, sorted(tops, reverse=True))          # de cima para baixo
        key, rect = lay.items[2]
        self.assertEqual(lc.hit(lay, rect[0] + 2, rect[1] + 2), key)
        widths = {rect[2] for _key, rect in lay.items}
        self.assertEqual(len(widths), 1)                            # coluna com largura única

    def test_escala(self):
        small = lc.panel_layout(0, 600, 1.0, None, True, ITEMS, width)
        big = lc.panel_layout(0, 600, 2.0, None, True, ITEMS, width)
        self.assertEqual(big.label[3], 2 * small.label[3])

    def test_itens(self):
        items = lc.menu_items(["Cozinha", "Lavanderia"], offer_groups=True)
        self.assertEqual([k for k, _l in items],
                         ['CONVERT_GROUPS', 'CREATE_CABINET', 'CAT:Cozinha', 'CAT:Lavanderia', 'CREATE_CATEGORY'])
        self.assertEqual(lc.menu_items(["Cozinha"], offer_groups=False)[0][0], 'CREATE_CABINET')


if __name__ == "__main__":
    unittest.main()
