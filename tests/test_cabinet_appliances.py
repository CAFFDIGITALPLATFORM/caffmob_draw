"""Testes dos internos (feature 008, T009): `caffmob_draw/cabinet_editor/appliances.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import appliances as ap
from caffmob_draw.cabinet_editor import divisions as dv

SPACE = dv.Box((0.015, 0.0, 1.0), (0.785, 0.535, 1.8))       # 770 × 800
T = 0.018


class AppliancesTest(unittest.TestCase):
    def test_painel_com_recorte_centrado(self):
        lay = ap.layout(SPACE, 'PANEL_OVEN_EXT', T)
        self.assertAlmostEqual(lay.panel.box[1][1], 0.0)               # externo: na frente
        cut = lay.cutout
        self.assertAlmostEqual(cut[1][0] - cut[0][0], 0.595)
        self.assertAlmostEqual((cut[0][0] + cut[1][0]) / 2, 0.4)
        self.assertAlmostEqual((cut[0][2] + cut[1][2]) / 2, 1.4)
        self.assertEqual(len(lay.appliances), 1)

    def test_embutido_recuado(self):
        lay = ap.layout(SPACE, 'PANEL_OVEN_BI', T)
        self.assertAlmostEqual(lay.panel.box[0][1], T)

    def test_forno_e_micro(self):
        lay = ap.layout(SPACE.__class__((0.015, 0.0, 0.5), (0.785, 0.535, 1.6)), 'PANEL_OVEN_MICRO_EXT', T)
        self.assertEqual(len(lay.appliances), 2)
        self.assertAlmostEqual(lay.cutout[1][2] - lay.cutout[0][2], 0.985)
        # BUG-20261011-HVYM (F-12): forno embaixo, micro em cima.
        (low, low_box), (high, high_box) = lay.appliances
        self.assertEqual((low, high), ('OVEN', 'MICRO'))
        self.assertLess(low_box[0][2], high_box[0][2])

    def test_nao_cabe(self):
        small = dv.Box((0.0, 0.0, 0.0), (0.77, 0.535, 0.34))
        self.assertEqual(ap.missing(small, 'PANEL_OVEN_EXT'), (615.0, 615.0, 560.0))
        deep = dv.Box((0.015, 0.0, 1.0), (0.785, 0.58, 1.8))
        self.assertIsNone(ap.missing(deep, 'PANEL_OVEN_EXT'))
        # BUG-20261011-TFC7 (EC-15): forno de 560 mm num vão de 535 mm de profundidade não cabe.
        self.assertEqual(ap.missing(SPACE, 'PANEL_OVEN_EXT')[2], 560.0)

    def test_apoio_abaixo_do_eletro(self):
        lay = ap.layout(SPACE, 'PANEL_OVEN_EXT', T)
        offset = ap.support_offset(SPACE, lay, T)
        self.assertAlmostEqual(SPACE.lo[2] + offset + T, lay.cutout[0][2])


if __name__ == '__main__':
    unittest.main()
