"""072, onda B (T051; RN-12): medidas do gaveteiro pelos dois métodos do guia."""
import unittest

import _gavetas_072  # noqa: F401
from caffmob_draw.drawers import gaveteiro_core as gc


class GaveteiroTest(unittest.TestCase):
    def test_volante_base_passante(self):
        g = gc.Gaveteiro(450, 600, 500, 'BASE', 'volante', 3)
        p = gc.pecas(g)
        self.assertEqual(p['lateral'], (500, 600 - 18 - 25, 18))           # 557
        self.assertEqual((p['base'][0], p['tampo'][0], p['tampo'][2]), (450, 450, 25))
        self.assertTrue(g.espessuras()['rodizios'])
        self.assertEqual(gc.vao(g), (414, 557))

    def test_lateral_passante(self):
        g = gc.Gaveteiro(600, 720, 560, 'LATERAL', 'fixo', 4)
        p = gc.pecas(g)
        self.assertEqual(p['lateral'][1], 720)
        self.assertEqual(p['base'][0], 600 - 36)
        self.assertEqual(p['tampo'][0], 564)

    def test_tipos_do_guia(self):
        self.assertEqual(sorted(gc.TIPOS), ['fixo', 'oculto', 'suspenso', 'volante'])
        self.assertEqual(gc.TIPOS['oculto']['frente'], 15)


if __name__ == '__main__':
    unittest.main()
