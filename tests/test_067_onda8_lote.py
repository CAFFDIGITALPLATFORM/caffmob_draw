"""Onda 8 da 067 (T183; RF-162, RF-163, D-39, D-40): várias paredes no editor do projeto do addon."""
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import model
from caffmob_draw.walls2d import selecao_classica as sc


def plano():
    sala = model.rectangle(4.0, 3.0, thickness=0.14, height=2.6)
    sala.segments[2].thickness = 0.19
    corredor = model.Chain([(10.0, 0.0), (14.0, 0.0)], [model.Segment(0.14, 2.6)])
    return model.WallPlan([sala, corredor])


class SelecaoTest(unittest.TestCase):
    def test_todos(self):
        self.assertEqual(sc.todos(plano()), [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)])

    def test_somar_tirar(self):
        self.assertEqual(sc.alternar([(0, 0)], (0, 1)), [(0, 0), (0, 1)])
        self.assertEqual(sc.alternar([(0, 0), (0, 1)], (0, 0)), [(0, 1)])

    def test_retangulo_toca(self):
        p = plano()
        self.assertEqual(sc.no_retangulo(p, (9.0, -1.0), (15.0, 1.0)), [(1, 0)])
        self.assertEqual(set(sc.no_retangulo(p, (-1.0, -1.0), (15.0, 4.0))), set(sc.todos(p)))
        self.assertEqual(sc.no_retangulo(p, (6.0, 5.0), (8.0, 6.0)), [])

    def test_valor_comum_ou_multiplos(self):
        p = plano()
        self.assertIs(sc.valor_comum(p, sc.todos(p), 'thickness'), sc.MULTIPLOS)
        self.assertAlmostEqual(sc.valor_comum(p, [(0, 0), (0, 1)], 'thickness'), 0.14)
        self.assertAlmostEqual(sc.valor_comum(p, sc.todos(p), 'height'), 2.6)

    def test_aplicar_a_todos(self):
        p = plano()
        sc.aplicar(p, sc.todos(p), 'thickness', 0.15)
        self.assertEqual({round(sg.thickness, 6) for ch in p.chains for sg in ch.segments}, {0.15})
        sc.aplicar(p, [(0, 0), (1, 0)], 'height', 2.8)
        self.assertEqual((p.chains[0].segments[0].end_height, p.chains[0].segments[1].height), (2.8, 2.6))

    def test_valor_invalido_nao_aplica_em_nenhum(self):
        p = plano()
        with self.assertRaises(ValueError):
            sc.aplicar(p, sc.todos(p), 'thickness', 5.0)
        self.assertEqual(p.chains[0].segments[0].thickness, 0.14)

    def test_limpa_os_que_sumiram(self):
        p = plano()
        self.assertEqual(sc.validos(p, [(0, 0), (3, 1), (1, 4)]), [(0, 0)])


if __name__ == '__main__':
    unittest.main()
