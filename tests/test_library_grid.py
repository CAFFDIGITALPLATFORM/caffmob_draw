"""Testes do núcleo da grade e do retângulo maximizado da biblioteca (feature 014, T010; RN-08, RN-09, D-06, D-11)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import grid_core as gc


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


class GridTest(unittest.TestCase):
    def test_colunas_pela_largura(self):
        """RF-09: maximizado numa tela de 1.920 px cabem pelo menos 4 colunas."""
        rect = gc.initial_rect((0, 0, 1920, 1000), scale=1.0)
        area = gc.grid_area(rect, scale=1.0)
        self.assertGreaterEqual(gc.columns(area[2], scale=1.0), 4)
        self.assertEqual(gc.columns(10, scale=1.0), 1)          # nunca zero

    def test_celulas_visiveis_e_rolagem(self):
        area = (0, 0, 400, 300)
        cells = gc.visible_cells(area, count=100, scale=1.0, scroll=0.0)
        self.assertEqual(cells[0][0], 0)
        top = area[1] + area[3]
        self.assertTrue(all(c[1][1] < top and c[1][1] + c[1][3] > area[1] for c in cells))
        rolled = gc.visible_cells(area, count=100, scale=1.0, scroll=500.0)
        self.assertGreater(rolled[0][0], 0)
        self.assertLess(len(cells), 100)

    def test_rolagem_limitada(self):
        area = (0, 0, 400, 300)
        content = gc.content_height(area[2], count=100, scale=1.0)
        self.assertEqual(gc.clamp_scroll(-50, content, area[3]), 0.0)
        self.assertEqual(gc.clamp_scroll(10 ** 6, content, area[3]), content - area[3])
        self.assertEqual(gc.clamp_scroll(30, 100, 300), 0.0)       # conteúdo menor que a área: sem rolagem

    def test_acerto_de_celula(self):
        area = (0, 0, 400, 300)
        cells = gc.visible_cells(area, count=10, scale=1.0, scroll=0.0)
        index, (x, y, w, h) = cells[2]
        self.assertEqual(gc.hit_cell(cells, x + w / 2, y + h / 2), 2)
        self.assertIsNone(gc.hit_cell(cells, -5, -5))

    def test_limites_e_hud(self):
        """RN-09, RF-16: o retângulo fica dentro da região visível e fora dos retângulos do HUD."""
        bounds = (0, 0, 1600, 900)
        hud = [(0, 820, 400, 80), (1500, 0, 100, 900)]
        for rect in [(-100, 700, 800, 500), (1400, 100, 600, 400), (100, 750, 500, 300)]:
            fixed = gc.clamp_rect(rect, bounds, hud, scale=1.0)
            x, y, w, h = fixed
            self.assertTrue(x >= 0 and y >= 0 and x + w <= 1600 and y + h <= 900, fixed)
            self.assertFalse(any(overlap(fixed, f) for f in hud), fixed)
            self.assertGreaterEqual(w, gc.MIN_W)
            self.assertGreaterEqual(h, gc.MIN_H)

    def test_mover_e_redimensionar(self):
        bounds = (0, 0, 1600, 900)
        rect = (200, 200, 800, 500)
        moved = gc.move(rect, 50, -30, bounds, [], scale=1.0)
        self.assertEqual(moved[:2], (250, 170))
        grown = gc.resize(rect, 'RIGHT', 100, 0, bounds, [], scale=1.0)
        self.assertEqual(grown[2], 900)
        tiny = gc.resize(rect, 'RIGHT', -10 ** 4, 0, bounds, [], scale=1.0)
        self.assertEqual(tiny[2], gc.MIN_W)
        top = gc.resize(rect, 'TOP', 0, 40, bounds, [], scale=1.0)
        self.assertEqual((top[1], top[3]), (200, 540))
        bottom = gc.resize(rect, 'BOTTOM', 0, -40, bounds, [], scale=1.0)
        self.assertEqual((bottom[1], bottom[3]), (160, 540))

    def test_estados(self):
        """RN-09: minimizado, aberto e maximizado; fixo não fecha com clique fora; solto fecha."""
        self.assertEqual(gc.next_mode('MIN', 'LABEL', pinned=False), 'OPEN')
        self.assertEqual(gc.next_mode('OPEN', 'LABEL', pinned=False), 'MIN')
        self.assertEqual(gc.next_mode('OPEN', 'MAXIMIZE', pinned=False), 'MAX')
        self.assertEqual(gc.next_mode('MAX', 'MINIMIZE', pinned=True), 'MIN')
        self.assertEqual(gc.next_mode('MAX', 'OUTSIDE', pinned=True), 'MAX')
        self.assertEqual(gc.next_mode('MAX', 'OUTSIDE', pinned=False), 'MIN')
        self.assertEqual(gc.next_mode('MAX', 'ESC', pinned=False), 'MIN')
        self.assertEqual(gc.next_mode('MAX', 'ESC', pinned=True), 'MAX')
        self.assertEqual(gc.next_mode('OPEN', 'OUTSIDE', pinned=False), 'MIN')

    def test_regioes_do_retangulo(self):
        """Cabeçalho move, borda redimensiona, área da grade não é borda."""
        rect = (100, 100, 800, 500)
        self.assertEqual(gc.region_at(rect, 500, 590, scale=1.0), 'HEADER')
        self.assertEqual(gc.region_at(rect, 899, 300, scale=1.0), 'RIGHT')
        self.assertEqual(gc.region_at(rect, 101, 300, scale=1.0), 'LEFT')
        self.assertEqual(gc.region_at(rect, 500, 101, scale=1.0), 'BOTTOM')
        self.assertEqual(gc.region_at(rect, 500, 300, scale=1.0), 'BODY')
        self.assertIsNone(gc.region_at(rect, 50, 50, scale=1.0))


if __name__ == "__main__":
    unittest.main()
