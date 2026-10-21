"""Testes do primeiro contato entre caixas orientadas (feature 066, T006): `obb.sweep_toi`.

RF-004 (não atravessar entre atualizações), RF-006 (caixa girada e escala negativa) e RF-007 (vários obstáculos).
"""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.collision import obb, rules

AXES = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
TOL = rules.TOLERANCE


def box(lo, hi, axes=AXES, origin=(0.0, 0.0, 0.0)):
    return obb.from_box(origin, axes, lo, hi)


def moved(b, delta, t):
    return obb.OBB(tuple(b.center[k] + delta[k] * t for k in range(3)), b.axes, b.half)


CUBO = box((-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))                       # face direita em x = 0,5
CHAPA = box((1.0, -1.0, -1.0), (1.015, 1.0, 1.0))                    # chapa de 15 mm em x = 1,0


class SweepToiTest(unittest.TestCase):
    def test_digitar_2_m_contra_chapa_de_15_mm_para_antes(self):
        delta = (2.0, 0.0, 0.0)                                        # o destino já está do outro lado da chapa
        self.assertIsNone(obb.overlap(moved(CUBO, delta, 1.0), CHAPA))
        hit = obb.sweep_toi(CUBO, delta, CHAPA, TOL)
        self.assertIsNotNone(hit)
        self.assertAlmostEqual(hit.t_touch, 0.25, places=9)            # 0,5 m até encostar, de 2 m
        self.assertGreater(hit.t_enter, hit.t_touch)
        self.assertLess(hit.t_enter, 1.0)
        self.assertAlmostEqual(hit.normal[0], -1.0, places=9)          # a normal aponta da chapa para o cubo
        stop = moved(CUBO, delta, hit.t_touch)
        self.assertAlmostEqual(stop.center[0] + stop.half[0], 1.0, places=9)

    def test_contato_de_1_mm_nao_bloqueia(self):
        delta = (0.5 + TOL * 0.9, 0.0, 0.0)                            # termina 0,9 mm dentro da chapa
        hit = obb.sweep_toi(CUBO, delta, CHAPA, TOL)
        self.assertTrue(hit is None or hit.t_enter >= 1.0, hit)

    def test_deslizar_encostado_nao_bloqueia(self):
        encostado = box((0.0, -0.5, -0.5), (1.0, 0.5, 0.5))           # face direita na face da chapa
        hit = obb.sweep_toi(encostado, (0.0, 0.3, 0.0), CHAPA, TOL)
        self.assertIsNone(hit)

    def test_ja_penetrado_comeca_dentro(self):
        dentro = box((0.0, -0.5, -0.5), (1.01, 0.5, 0.5))
        hit = obb.sweep_toi(dentro, (-0.5, 0.0, 0.0), CHAPA, TOL)
        self.assertIsNotNone(hit)
        self.assertLessEqual(hit.t_enter, 0.0)                         # quem chama trata como já penetrado

    def test_afastando_nao_bloqueia(self):
        self.assertIsNone(obb.sweep_toi(CUBO, (-2.0, 0.0, 0.0), CHAPA, TOL))

    def test_caixa_girada(self):
        c, s = math.cos(math.radians(45)), math.sin(math.radians(45))
        girado = obb.from_box((0.0, 0.0, 0.0), ((c, s, 0.0), (-s, c, 0.0), (0.0, 0.0, 1.0)),
                              (-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))
        hit = obb.sweep_toi(girado, (2.0, 0.0, 0.0), CHAPA, TOL)
        self.assertIsNotNone(hit)
        reach = math.sqrt(2.0) / 2.0                                   # a quina do cubo girado vai na frente
        self.assertAlmostEqual(hit.t_touch, (1.0 - reach) / 2.0, places=9)

    def test_escala_negativa_nao_inventa_bloqueio(self):
        # Escala −1 em X (eixos da mão esquerda) com a mesma caixa: o resultado é o da caixa comum.
        espelhado = obb.from_box((0.0, 0.0, 0.0), ((-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
                                 (-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))
        hit = obb.sweep_toi(espelhado, (2.0, 0.0, 0.0), CHAPA, TOL)
        self.assertAlmostEqual(hit.t_touch, 0.25, places=9)
        self.assertIsNone(obb.sweep_toi(espelhado, (0.0, 2.0, 0.0), CHAPA, TOL))

    def test_dois_obstaculos_da_o_menor_t(self):
        perto = box((0.8, -1.0, -1.0), (0.815, 1.0, 1.0))
        longe = CHAPA
        a = obb.sweep_toi(CUBO, (2.0, 0.0, 0.0), perto, TOL)
        b = obb.sweep_toi(CUBO, (2.0, 0.0, 0.0), longe, TOL)
        self.assertLess(a.t_touch, b.t_touch)
        self.assertAlmostEqual(a.t_touch, 0.15, places=9)

    def test_sem_movimento(self):
        self.assertIsNone(obb.sweep_toi(CUBO, (0.0, 0.0, 0.0), CHAPA, TOL))


if __name__ == "__main__":
    unittest.main()
