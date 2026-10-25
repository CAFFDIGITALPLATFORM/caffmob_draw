"""Conta do veio (feature 067, onda 3; RF-060, RF-061, RF-063, M-05)."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.texture_library import grain_core as gc

# Chapa em pé de frente (normal Y): largura em X, altura em Z.
STANDING = {0: 'WIDTH', 2: 'HEIGHT'}
# Lateral (normal X): profundidade em Y, altura em Z.
SIDE = {1: 'DEPTH', 2: 'HEIGHT'}
# Prateleira deitada (normal Z): largura em X, profundidade em Y.
SHELF = {0: 'WIDTH', 1: 'DEPTH'}
QUARTER = math.pi / 2.0


class GrainTest(unittest.TestCase):
    def test_eixo_do_veio(self):
        self.assertEqual(gc.grain_axis('H', STANDING), 0)
        self.assertEqual(gc.grain_axis('V', STANDING), 2)
        self.assertEqual(gc.grain_axis('V', SHELF), 1)          # deitada: V corre na profundidade
        self.assertIsNone(gc.grain_axis('NONE', STANDING))

    def test_frente_em_pe_com_imagem_horizontal(self):
        self.assertEqual(gc.rotation('H', 1, STANDING, 'H'), gc.ZERO)
        self.assertEqual(gc.rotation('V', 1, STANDING, 'H'), (0.0, QUARTER, 0.0))   # gira na normal da face

    def test_imagem_calibrada_vertical_produz_h_correto(self):
        # RF-061: H não supõe imagem horizontal.
        self.assertEqual(gc.rotation('V', 1, STANDING, 'V'), gc.ZERO)
        self.assertEqual(gc.rotation('H', 1, STANDING, 'V'), (0.0, QUARTER, 0.0))

    def test_lateral_e_prateleira(self):
        # Face X: u = Z (a altura); face Z: u = Y (a profundidade), pelo render do protótipo T008.
        self.assertEqual(gc.rotation('V', 0, SIDE, 'H'), gc.ZERO)
        self.assertEqual(gc.rotation('V', 0, SIDE, 'V'), (QUARTER, 0.0, 0.0))
        self.assertEqual(gc.rotation('V', 2, SHELF, 'H'), gc.ZERO)
        self.assertEqual(gc.rotation('H', 2, SHELF, 'H'), (0.0, 0.0, QUARTER))

    def test_uv_gira_em_z(self):
        self.assertEqual(gc.rotation('V', 1, {0: 'WIDTH', 1: 'HEIGHT'}, 'H', gc.UV), (0.0, 0.0, QUARTER))

    def test_sem_veio_ou_sem_medida_nao_gira(self):
        self.assertEqual(gc.rotation('NONE', 1, STANDING), gc.ZERO)
        self.assertEqual(gc.rotation('V', None, STANDING), gc.ZERO)
        self.assertEqual(gc.rotation('V', 1, {}), gc.ZERO)

    def test_variante_antiga_e_calibracao(self):
        self.assertEqual(gc.legacy_rotated(), (0.0, 0.0, QUARTER))
        self.assertEqual(gc.calibration_from_size(512, 1024), 'V')
        self.assertEqual(gc.calibration_from_size(1024, 512), 'H')
        self.assertEqual(gc.calibration_from_size(None, 'x'), 'H')


if __name__ == '__main__':
    unittest.main()
