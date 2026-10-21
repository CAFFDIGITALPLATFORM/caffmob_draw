"""Testes das cotas laterais pela vista (feature 066, T008): `measure/side.py`.

RF-015 (lados pela vista), RF-016 (superfície a superfície), RF-019 (contato, sem limite e vista degenerada) e
RN-MEASURE-02 (só obstáculos na mesma faixa).
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.measure import side


def corners(lo, hi):
    return [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


CORPO = corners((1.0, 0.0, 0.0), (1.6, 0.6, 0.8))
ESQUERDA = corners((0.0, 0.0, 0.0), (0.7, 0.6, 2.0))        # 300 mm à esquerda (no X do mundo)
DIREITA = corners((2.1, 0.0, 0.0), (2.5, 0.6, 0.9))         # 500 mm à direita
VISTA_FRENTE = (1.0, 0.0, 0.0)                               # direita da vista = +X


class LateralAxisTest(unittest.TestCase):
    def test_eixo_horizontal_da_vista(self):
        axis = side.lateral_axis((0.6, 0.0, 0.8))               # vista inclinada: só a parte horizontal conta
        self.assertAlmostEqual(axis[0], 1.0)
        self.assertAlmostEqual(axis[2], 0.0)

    def test_vista_degenerada_nao_da_eixo(self):
        self.assertIsNone(side.lateral_axis((0.05, 0.0, 0.998)))

    def test_plano_da_parede(self):
        # Parede ao longo de X (normal Y): a vista olhando ao longo da parede é degenerada.
        self.assertIsNone(side.lateral_axis((0.0, 1.0, 0.0), plane_normal=(0.0, 1.0, 0.0)))
        axis = side.lateral_axis((0.7, 0.7, 0.0), plane_normal=(0.0, 1.0, 0.0))
        self.assertAlmostEqual(axis[0], 1.0)
        self.assertAlmostEqual(axis[1], 0.0)


class GapsTest(unittest.TestCase):
    def test_superficie_a_superficie(self):
        result = side.gaps(VISTA_FRENTE, CORPO, [ESQUERDA, DIREITA])
        self.assertAlmostEqual(result.left.value, 0.3)
        self.assertAlmostEqual(result.right.value, 0.5)
        self.assertAlmostEqual(result.left.start[0], 0.7)       # do obstáculo …
        self.assertAlmostEqual(result.left.end[0], 1.0)         # … até a superfície do corpo, nunca a origem

    def test_girar_a_vista_180_troca_os_lados(self):
        result = side.gaps((-1.0, 0.0, 0.0), CORPO, [ESQUERDA, DIREITA])
        self.assertAlmostEqual(result.left.value, 0.5)
        self.assertAlmostEqual(result.right.value, 0.3)

    def test_lado_livre_e_none(self):
        result = side.gaps(VISTA_FRENTE, CORPO, [ESQUERDA])
        self.assertAlmostEqual(result.left.value, 0.3)
        self.assertIsNone(result.right)

    def test_contato_da_zero(self):
        encostado = corners((1.6, 0.0, 0.0), (2.0, 0.6, 0.8))
        result = side.gaps(VISTA_FRENTE, CORPO, [encostado])
        self.assertEqual(result.right.value, 0.0)
        quase = corners((1.5995, 0.0, 0.0), (2.0, 0.6, 0.8))     # 0,5 mm dentro: contato, não penetração
        self.assertEqual(side.gaps(VISTA_FRENTE, CORPO, [quase]).right.value, 0.0)

    def test_fora_da_faixa_de_altura_e_ignorado(self):
        aereo = corners((1.7, 0.0, 1.5), (2.3, 0.6, 2.2))
        result = side.gaps(VISTA_FRENTE, CORPO, [aereo, DIREITA])
        self.assertAlmostEqual(result.right.value, 0.5)

    def test_fora_do_corredor_de_profundidade_e_ignorado(self):
        atras = corners((1.8, 2.0, 0.0), (2.0, 2.6, 0.8))
        self.assertIsNone(side.gaps(VISTA_FRENTE, CORPO, [atras]).right)

    def test_obstaculo_sobreposto_nao_vira_limite(self):
        sobreposto = corners((1.2, 0.0, 0.0), (1.4, 0.6, 0.8))
        result = side.gaps(VISTA_FRENTE, CORPO, [sobreposto, DIREITA])
        self.assertAlmostEqual(result.right.value, 0.5)

    def test_sem_eixo_sem_cota(self):
        self.assertIsNone(side.gaps(None, CORPO, [ESQUERDA, DIREITA]))


if __name__ == "__main__":
    unittest.main()
