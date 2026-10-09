"""Testes da porta e janela na região marcada (feature 011, T005): `caffmob_draw/openings/region_core.py` (D-11)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.openings import region_core as r

PAREDE = dict(wall_length=4.0, wall_height=2.7)


class FitTest(unittest.TestCase):
    def test_porta_exata_a_partir_do_piso(self):
        fit = r.fit(1.0, 1.82, 0.0, 2.12, kind='DOOR', **PAREDE)
        self.assertTrue(fit.ok)
        self.assertAlmostEqual(fit.x, 1.0, places=9)
        self.assertAlmostEqual(fit.width, 0.82, places=9)      # nem um milímetro a mais
        self.assertAlmostEqual(fit.height, 2.12, places=9)
        self.assertEqual(fit.sill, 0.0)

    def test_porta_com_regiao_acima_do_piso_vai_do_piso(self):
        fit = r.fit(1.0, 1.8, 0.3, 2.1, kind='DOUBLE_DOOR', **PAREDE)
        self.assertTrue(fit.ok)
        self.assertEqual(fit.sill, 0.0)
        self.assertAlmostEqual(fit.height, 2.1, places=9)

    def test_janela_usa_o_peitoril(self):
        fit = r.fit(0.5, 1.7, 1.1, 2.1, kind='WINDOW', **PAREDE)
        self.assertTrue(fit.ok)
        self.assertAlmostEqual(fit.sill, 1.1, places=9)
        self.assertAlmostEqual(fit.width, 1.2, places=9)
        self.assertAlmostEqual(fit.height, 1.0, places=9)

    def test_cantos_invertidos(self):
        a = r.fit(1.0, 1.82, 0.0, 2.12, kind='DOOR', **PAREDE)
        b = r.fit(1.82, 1.0, 2.12, 0.0, kind='DOOR', **PAREDE)
        self.assertEqual(a, b)

    def test_clique_um_pouco_abaixo_do_piso_conta_como_piso(self):
        fit = r.fit(0.5, 1.7, -0.004, 1.0, kind='WINDOW', **PAREDE)
        self.assertTrue(fit.ok)
        self.assertEqual(fit.sill, 0.0)
        self.assertAlmostEqual(fit.height, 1.0, places=9)

    def test_recusas(self):
        self.assertEqual(r.fit(3.0, 5.0, 0.0, 2.1, kind='DOOR', **PAREDE).reason, r.OUTSIDE)
        self.assertEqual(r.fit(-0.2, 0.6, 0.0, 2.1, kind='DOOR', **PAREDE).reason, r.OUTSIDE)
        self.assertEqual(r.fit(1.0, 1.8, 0.0, 3.0, kind='DOOR', **PAREDE).reason, r.TOO_TALL)
        self.assertEqual(r.fit(1.0, 1.0, 0.0, 2.1, kind='DOOR', **PAREDE).reason, r.EMPTY)
        self.assertEqual(r.fit(1.0, 1.8, 1.0, 1.0, kind='WINDOW', **PAREDE).reason, r.EMPTY)
        outra = [(1.5, 2.3, 0.0, 2.1)]
        self.assertEqual(r.fit(1.0, 1.8, 0.0, 2.1, kind='DOOR', others=outra, **PAREDE).reason, r.OVERLAP)
        recusa = r.fit(3.0, 5.0, 0.0, 2.1, kind='DOOR', **PAREDE)
        self.assertFalse(recusa.ok)

    def test_vizinha_que_so_encosta_ou_fica_acima_nao_bloqueia(self):
        encosta = [(1.8, 2.6, 0.0, 2.1)]
        self.assertTrue(r.fit(1.0, 1.8, 0.0, 2.1, kind='DOOR', others=encosta, **PAREDE).ok)
        acima = [(1.0, 1.8, 2.3, 2.6)]                       # janela alta sobre a região
        self.assertTrue(r.fit(1.0, 1.8, 0.0, 2.1, kind='DOOR', others=acima, **PAREDE).ok)


if __name__ == "__main__":
    unittest.main()
