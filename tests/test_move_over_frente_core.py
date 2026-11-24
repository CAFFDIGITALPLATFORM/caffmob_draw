"""Decisão da frente do objeto no Mover Sobre (feature 022, RN-01 a RN-06). Sem Blender.

Casos: propriedade vence, parede atrás (perto e longe, sem limite), parede na frente, eixo para módulo,
ambiguidade por ausência de evidência e por desacordo, e a referência que é a própria parede.
"""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.move_over import frente_core as fc  # noqa: E402

B = ((0.0, 0.0, 0.0), (0.8, 0.55, 2.0))                       # armário de 800 × 550, fundo em Y = 0
WALL_BEHIND = ((-0.2, 0.6, 0.0), (4.0, 0.75, 2.7), 0.0)       # parede atrás (Y +), espessura no Y local
WALL_FAR = ((-0.2, 30.0, 0.0), (4.0, 30.15, 2.7), 0.0)        # parede atrás, muito longe (sem limite de distância)
WALL_IN_FRONT = ((-0.2, -0.75, 0.0), (4.0, -0.6, 2.7), 0.0)   # parede do lado −Y: a frente vira +Y
WALL_SIDE = ((1.0, -0.2, 0.0), (1.15, 2.0, 2.7), 0.0)         # parede ao lado (+X), fora do pé de B em Y


def wall_for(front_yaw, distance=2.0):
    """Parede atrás de B que dá exatamente `front_yaw`: centro a `distance` atrás, girada no mesmo yaw."""
    cx, cy = fc.plan_center(B)
    fx, fy = fc.normal_of(front_yaw, sign=-1.0)          # direção da frente: Rz(yaw) @ (0, −1)
    wx, wy = cx - fx * distance, cy - fy * distance
    return ((wx - 2.0, wy - 0.075, 0.0), (wx + 2.0, wy + 0.075, 2.7), front_yaw)


class DegreesTest(unittest.TestCase):
    def test_normal_para_yaw(self):
        self.assertEqual(fc.yaw_from_normal(0.0, -1.0), 0.0)      # −Y é a convenção do objeto
        self.assertEqual(fc.yaw_from_normal(1.0, 0.0), 90.0)
        self.assertEqual(fc.yaw_from_normal(0.0, 1.0), 180.0)
        self.assertEqual(fc.yaw_from_normal(-1.0, 0.0), 270.0)

    def test_distancia_angular(self):
        self.assertEqual(fc.angular_distance(350.0, 10.0), 20.0)
        self.assertEqual(fc.angular_distance(0.0, 180.0), 180.0)

    def test_face_da_vista_vira_face_do_objeto(self):
        self.assertEqual(fc.face_of('NEG_Y', 0.0), 'NEG_Y')
        self.assertEqual(fc.face_of('NEG_Y', 90.0), 'NEG_X')
        self.assertEqual(fc.face_of('NEG_Y', 180.0), 'POS_Y')
        self.assertEqual(fc.face_of('NEG_X', 270.0), 'NEG_Y')

    def test_eixo_da_espessura_acompanha_o_yaw(self):
        self.assertAlmostEqual(fc.normal_of(0.0)[1], 1.0)
        nx, ny = fc.normal_of(90.0)
        self.assertAlmostEqual(nx, -1.0)
        self.assertAlmostEqual(ny, 0.0, places=6)


class DecideTest(unittest.TestCase):
    def test_propriedade_vence_parede_e_eixo(self):
        yaw, origem, ambiguo = fc.decide(B, [WALL_BEHIND], 90.0, True)
        self.assertEqual((yaw, origem, ambiguo), (90.0, fc.PROPRIEDADE, False))

    def test_parede_atras_define_a_frente_sem_pergunta(self):
        yaw, origem, ambiguo = fc.decide(B, [WALL_BEHIND], None, True)
        self.assertEqual((yaw, origem, ambiguo), (0.0, fc.PAREDE, False))

    def test_parede_sem_limite_de_distancia(self):
        yaw, origem, _ambiguo = fc.decide(B, [WALL_FAR], None, True)
        self.assertEqual((yaw, origem), (0.0, fc.PAREDE))

    def test_parede_do_outro_lado_inverte_a_frente(self):
        yaw, origem, ambiguo = fc.decide(B, [WALL_IN_FRONT], None, True)
        self.assertEqual((yaw, origem), (180.0, fc.PAREDE))
        self.assertTrue(ambiguo, "180° de desacordo com o eixo precisa perguntar")

    def test_parede_que_nao_cobre_o_pe_de_b_e_ignorada(self):
        yaw, origem, ambiguo = fc.decide(B, [WALL_SIDE], None, True)
        self.assertEqual((yaw, origem, ambiguo), (0.0, fc.EIXO, False))

    def test_sem_parede_modulo_de_biblioteca_usa_o_eixo(self):
        self.assertEqual(fc.decide(B, [], None, True), (0.0, fc.EIXO, False))

    def test_sem_parede_objeto_solto_pergunta(self):
        yaw, origem, ambiguo = fc.decide(B, [], None, False)
        self.assertEqual((yaw, origem), (0.0, fc.EIXO))
        self.assertTrue(ambiguo)

    def test_desacordo_dentro_da_tolerancia_nao_pergunta(self):
        yaw, origem, ambiguo = fc.decide(B, [wall_for(44.0)], None, True)
        self.assertEqual(origem, fc.PAREDE)
        self.assertAlmostEqual(yaw, 44.0, places=4)
        self.assertFalse(ambiguo, "abaixo de 45° não pergunta")

    def test_desacordo_acima_da_tolerancia_pergunta(self):
        _yaw, origem, ambiguo = fc.decide(B, [wall_for(46.0)], None, True)
        self.assertEqual(origem, fc.PAREDE)
        self.assertTrue(ambiguo)

    def test_parede_mais_proxima_vence(self):
        yaw, _origem, _ambiguo = fc.decide(B, [WALL_FAR, WALL_IN_FRONT], None, True)
        self.assertEqual(yaw, 180.0)


class WallAsReferenceTest(unittest.TestCase):
    WALL = ((-2.0, 0.0, 0.0), (2.0, 0.15, 2.7), 0.0)          # parede em X, espessura em Y

    def test_sem_arraste_pergunta(self):
        yaw, origem, ambiguo = fc.decide_for_wall(self.WALL, ((0.0, 0.5, 0.0), (0.8, 1.05, 2.0)), False, None)
        self.assertEqual((yaw, origem, ambiguo), (0.0, fc.EIXO, True))

    def test_arraste_define_o_lado_de_onde_a_chegou(self):
        yaw, origem, ambiguo = fc.decide_for_wall(self.WALL, ((0.0, 0.5, 0.0), (0.8, 1.05, 2.0)), True, None)
        self.assertEqual((origem, ambiguo), (fc.PAREDE, False))
        self.assertEqual(yaw, 180.0, "A está em +Y da parede: a frente olha para +Y")

    def test_a_sobre_a_parede_pergunta(self):
        _yaw, _origem, ambiguo = fc.decide_for_wall(self.WALL, ((-0.5, 0.02, 0.0), (0.3, 0.1, 2.0)), True, None)
        self.assertTrue(ambiguo)


if __name__ == "__main__":
    unittest.main()
