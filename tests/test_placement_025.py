"""Núcleo puro do posicionamento do armário v2 (feature 025), sem Blender."""

import math
import unittest
from types import SimpleNamespace

import _bootstrap  # noqa: F401  (stub de bpy para o núcleo puro)
from caffmob_draw.armario_v2 import placement


class PosicionamentoTest(unittest.TestCase):
    def test_setas_apontam_para_as_quatro_direcoes(self):
        self.assertAlmostEqual(placement.seta_para_yaw('UP_ARROW'), 0.0)
        self.assertAlmostEqual(placement.seta_para_yaw('RIGHT_ARROW'), math.pi / 2)
        self.assertAlmostEqual(placement.seta_para_yaw('DOWN_ARROW'), math.pi)
        self.assertAlmostEqual(placement.seta_para_yaw('LEFT_ARROW'), 3 * math.pi / 2)

    def test_seta_desconhecida_nao_gira(self):
        self.assertAlmostEqual(placement.seta_para_yaw('SPACE'), 0.0)

    def test_yaw_para_seta_mais_proxima(self):
        self.assertEqual(placement.yaw_para_seta(0.0), 'UP_ARROW')
        self.assertEqual(placement.yaw_para_seta(math.pi / 2), 'RIGHT_ARROW')
        self.assertEqual(placement.yaw_para_seta(math.radians(179)), 'DOWN_ARROW')
        self.assertEqual(placement.yaw_para_seta(math.radians(271)), 'LEFT_ARROW')

    def test_girar_normaliza_em_uma_volta(self):
        self.assertAlmostEqual(placement.girar(math.radians(270)), 0.0)
        self.assertAlmostEqual(placement.girar(0.0, -90), 3 * math.pi / 2)

    def test_caixa_do_spec_em_metros(self):
        spec = SimpleNamespace(largura=1000.0, altura=2400.0, profundidade=510.0)
        self.assertEqual(placement.caixa(spec), (1.0, 0.51, 2.4))


if __name__ == '__main__':
    unittest.main()
