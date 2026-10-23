"""Regras do Encostar (BUG-20261022-RQR5, #137): `caffmob_draw/move_over/encostar.py`, iguais às do diálogo
"Encostar" do artefato, no referencial de B (X largura, Y profundidade com a frente em Y mínimo, Z altura)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.move_over import encostar as e

B = ((0.0, 0.0, 0.0), (1.0, 0.6, 0.8))          # largura 1, profundidade 0,6, altura 0,8
A = ((3.0, -0.2, 0.1), (3.4, 0.3, 0.5))         # 0,4 × 0,5 × 0,4, à direita de B


def close(a, b, tol=1e-9):
    return all(abs(x - y) < tol for x, y in zip(a, b))


class LadosTest(unittest.TestCase):
    def test_seis_lados_com_afastamento(self):
        g = 0.1
        no_align = {0: e.KEEP, 1: e.KEEP, 2: e.KEEP}
        expect = {
            e.LEFT: (0.0 - g - 0.4, -0.2, 0.1),
            e.RIGHT: (1.0 + g, -0.2, 0.1),
            e.TOP: (3.0, -0.2, 0.8 + g),
            e.BOTTOM: (3.0, -0.2, 0.0 - g - 0.4),
            e.BACK: (3.0, 0.6 + g, 0.1),
            e.FRONT: (3.0, 0.0 - g - 0.5, 0.1),
        }
        for side, want in expect.items():
            with self.subTest(side=side):
                self.assertTrue(close(e.target_min(A, B, side, g, no_align), want),
                                (side, e.target_min(A, B, side, g, no_align)))

    def test_alinhamento_padrao_do_lado(self):
        self.assertEqual(e.default_align(e.LEFT), {0: e.KEEP, 1: 'BACK', 2: 'BASE'})
        self.assertEqual(e.default_align(e.TOP), {0: 'LEFT', 1: 'BACK', 2: e.KEEP})
        self.assertEqual(e.default_align(e.FRONT), {0: 'LEFT', 1: e.KEEP, 2: 'BASE'})
        self.assertEqual(e.align_axes(e.LEFT), (1, 2))
        self.assertEqual(e.align_axes(e.TOP), (0, 1))
        self.assertEqual(e.align_axes(e.BACK), (0, 2))

    def test_alinhamentos(self):
        at = lambda side, **al: e.target_min(A, B, side, 0.0, {0: al.get('w', e.KEEP), 1: al.get('d', e.KEEP),
                                                                2: al.get('h', e.KEEP)})
        self.assertAlmostEqual(at(e.RIGHT, d='BACK')[1], 0.6 - 0.5)       # fundo de A no fundo de B
        self.assertAlmostEqual(at(e.RIGHT, d='FRONT')[1], 0.0)            # frente de A na frente de B
        self.assertAlmostEqual(at(e.RIGHT, h='BASE')[2], 0.0)
        self.assertAlmostEqual(at(e.RIGHT, h='TOP')[2], 0.8 - 0.4)
        self.assertAlmostEqual(at(e.TOP, w='LEFT')[0], 0.0)
        self.assertAlmostEqual(at(e.TOP, w='RIGHT')[0], 1.0 - 0.4)
        self.assertAlmostEqual(at(e.TOP, w='CENTER')[0], (1.0 - 0.4) / 2)
        self.assertTrue(close(at(None), A[0]))                            # posição livre: nada muda

    def test_lado_inicial_pelo_maior_afastamento(self):
        self.assertEqual(e.initial_side(A, B), e.RIGHT)
        self.assertEqual(e.initial_side(((-2.0, 0.0, 0.0), (-1.0, 0.6, 0.8)), B), e.LEFT)
        self.assertEqual(e.initial_side(((0.0, 0.0, 2.0), (1.0, 0.6, 2.5)), B), e.TOP)
        self.assertEqual(e.initial_side(((0.0, -3.0, 0.0), (1.0, -2.0, 0.8)), B), e.FRONT)
        self.assertEqual(e.initial_side(((0.0, 3.0, 0.0), (1.0, 4.0, 0.8)), B), e.BACK)


class FolgaTest(unittest.TestCase):
    def test_folga_por_eixo_e_sobreposicao(self):
        n = ((1.1, 0.0, 0.0), (1.5, 0.5, 0.4))
        g = e.gaps(n, B)
        self.assertAlmostEqual(g[0], 0.1)
        self.assertLess(g[1], 0)                  # sobrepõe na profundidade
        self.assertEqual(e.derived_side(n, B), e.RIGHT)
        self.assertEqual(e.derived_side(((0.0, 0.0, 1.0), (1.0, 0.6, 1.2)), B), e.TOP)


class ImaTest(unittest.TestCase):
    def test_candidatos_do_eixo(self):
        values = sorted(round(c[0], 6) for c in e.candidates(0, 0.4, B, 0.05))
        for want in (1.05, -0.45, 0.0, 0.6, 0.3, 1.0, -0.4):
            self.assertIn(round(want, 6), values)

    def test_puxa_dentro_da_tolerancia_e_solta_fora(self):
        value, guide = e.snap(1.004, 0, 0.4, B, 0.0, tolerance=0.01)
        self.assertAlmostEqual(value, 1.0)
        self.assertIsNotNone(guide)
        value, guide = e.snap(1.2, 0, 0.4, B, 0.0, tolerance=0.01)
        self.assertAlmostEqual(value, 1.2)
        self.assertIsNone(guide)
        value, guide = e.snap(0.301, 0, 0.4, B, 0.0, tolerance=0.01)
        self.assertAlmostEqual(value, 0.3)                                # centralizado
        self.assertEqual(guide[1], "centralizado")


class CliqueTest(unittest.TestCase):
    def test_lado_pelo_clique_nas_vistas(self):
        self.assertEqual(e.side_from_point('FRONT', -2.0, 0.1), e.LEFT)
        self.assertEqual(e.side_from_point('FRONT', 0.1, 2.0), e.TOP)
        self.assertEqual(e.side_from_point('FRONT', 0.1, -2.0), e.BOTTOM)
        self.assertEqual(e.side_from_point('PLAN', 0.1, 2.0), e.BACK)     # planta: o fundo fica em cima
        self.assertEqual(e.side_from_point('PLAN', 0.1, -2.0), e.FRONT)
        self.assertEqual(e.side_from_point('PLAN', 2.0, 0.1), e.RIGHT)

    def test_afastamento_aceita_de_0_a_5000_mm(self):
        self.assertEqual(e.MAX_GAP, 5.0)


if __name__ == "__main__":
    unittest.main()
