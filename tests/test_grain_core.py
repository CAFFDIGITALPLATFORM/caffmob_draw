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

    def test_veio_em_graus_soma_na_normal_da_face(self):
        # (018, T009) O ângulo livre soma ao giro do enum, na normal da face (D-05).
        self.assertEqual(gc.rotation('H', 1, STANDING, 'H', gc.BOX, 0.0), gc.ZERO)
        self.assertAlmostEqual(gc.rotation('H', 1, STANDING, 'H', gc.BOX, 30.0)[1], math.radians(30.0))
        self.assertAlmostEqual(gc.rotation('V', 1, STANDING, 'H', gc.BOX, 30.0)[1], QUARTER + math.radians(30.0))
        self.assertAlmostEqual(gc.rotation('NONE', 1, STANDING, 'H', gc.BOX, 45.0)[1], math.radians(45.0))
        self.assertAlmostEqual(gc.rotation('VERTICAL', 2, SHELF, 'H', gc.BOX, -20.0)[2], math.radians(-20.0))

    def test_uv_com_angulo_nao_precisa_da_espessura(self):
        # A normal do UV é sempre Z, então o giro livre também entra sem a medida (T009).
        self.assertAlmostEqual(gc.rotation('H', None, {}, 'H', gc.UV, 90.0)[2], QUARTER)
        self.assertEqual(gc.rotation('NONE', None, {}, 'H', gc.BOX, 90.0), gc.ZERO)

    def test_veio_de_corte_pelo_multiplo_de_90(self):
        # (018, T009/T022) 0 e 180 saem horizontais, 90 e 270 verticais; o enum entra na soma.
        self.assertEqual(gc.direction('H', 0.0), 'H')
        self.assertEqual(gc.direction('H', 30.0), 'H')
        self.assertEqual(gc.direction('H', 60.0), 'V')
        self.assertEqual(gc.direction('H', 90.0), 'V')
        self.assertEqual(gc.direction('H', 180.0), 'H')
        self.assertEqual(gc.direction('H', 270.0), 'V')
        self.assertEqual(gc.direction('VERTICAL', 0.0), 'V')
        self.assertEqual(gc.direction('VERTICAL', 30.0), 'V')          # 120 fica mais perto de 90
        self.assertEqual(gc.direction('VERTICAL', 60.0), 'H')          # 150 fica mais perto de 180
        self.assertEqual(gc.direction('VERTICAL', 90.0), 'H')
        self.assertEqual(gc.direction('NONE', 0.0), 'NONE')
        self.assertEqual(gc.direction('NONE', 30.0), 'H')
        self.assertEqual(gc.total_angle('V', -30.0), 60.0)
        self.assertEqual(gc.normalize('VERTICAL'), 'V')
        self.assertIsNone(gc.normalize('NONE'))

    def test_variante_antiga_e_calibracao(self):
        self.assertEqual(gc.legacy_rotated(), (0.0, 0.0, QUARTER))
        self.assertEqual(gc.calibration_from_size(512, 1024), 'V')
        self.assertEqual(gc.calibration_from_size(1024, 512), 'H')
        self.assertEqual(gc.calibration_from_size(None, 'x'), 'H')


if __name__ == '__main__':
    unittest.main()
