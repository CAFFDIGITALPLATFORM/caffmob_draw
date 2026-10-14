"""Testes dos internos de roupeiro (feature 015, T023): `caffmob_draw/cabinet_editor/wardrobe.py`.

Subvão de 976 × 550 × 2384 (X, Y, Z), frente em Y = 0.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import wardrobe as wd

SPACE = ((0.0, 0.0, 0.098), (0.976, 0.55, 2.482))


class WardrobeTest(unittest.TestCase):
    def test_tubo_70_abaixo_da_prateleira_de_cima(self):
        rod, = wd.layout('HANGER_ROD', SPACE, rod_drop=0.07)
        self.assertEqual(rod.hardware, 'TUBO_CABIDEIRO')
        self.assertIsNone(rod.component)
        center = (rod.box[0][2] + rod.box[1][2]) / 2.0
        self.assertAlmostEqual(center, 2.482 - 0.07)
        self.assertAlmostEqual(rod.box[1][0] - rod.box[0][0], 0.976 - 2 * wd.ROD_CLEARANCE)

    def test_calceiro_madeira_e_chapa_aramado_e_ferragem(self):
        wood, = wd.layout('PANTS_RACK', SPACE, material='WOOD')
        wire, = wd.layout('PANTS_RACK', SPACE, material='WIRE')
        self.assertEqual((wood.component, wood.hardware), ('ESP', None))
        self.assertEqual((wire.component, wire.hardware), (None, 'CALCEIRO_ARAMADO'))

    def test_sapateira_no_fundo_do_vao(self):
        shoe, = wd.layout('SHOE_RACK', SPACE)
        self.assertEqual(shoe.component, 'ESP')
        self.assertAlmostEqual(shoe.box[0][2], 0.098)

    def test_porta_cintos_e_ferragem(self):
        belt, = wd.layout('BELT_RACK', SPACE)
        self.assertEqual(belt.hardware, 'PORTA_CINTOS')

    def test_vao_estreito_recusa(self):
        narrow = ((0.0, 0.0, 0.0), (0.15, 0.55, 1.0))
        self.assertEqual(wd.too_small('HANGER_ROD', narrow), (0.20, 0.0, 0.0))
        self.assertIsNone(wd.too_small('HANGER_ROD', SPACE))


if __name__ == '__main__':
    unittest.main()
