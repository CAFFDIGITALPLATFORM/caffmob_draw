"""Reprodução e regressão de BUG-20261023-EI4W (#155): o cabeçalho da BIBLIOTECA CAFFMOB tem uma faixa própria para
arrastar a janela e nenhum controle sobreposto nas larguras 560, 780 e 1000 px (RF03 da auditoria da biblioteca)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import layout_core as lc

TABS = [('BLOCKS', "Blocos"), ('TEXTURES', "Texturas")]
ACCOUNT = "leonardo.lima@caff.digital"


def width(text):
    return 7.5 * len(text)          # Sora 12-13 px, um pouco acima da média para não esconder sobreposição


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


class CabecalhoTest(unittest.TestCase):
    def layouts(self):
        for w in (560.0, 780.0, 1000.0):
            yield w, lc.max_layout((0.0, 0.0, w, 600.0), 1.0, width, TABS, ACCOUNT, footer=False)

    def test_controles_sem_sobreposicao(self):
        for w, lay in self.layouts():
            parts = [('title', lay.title)] + [(k, r) for k, r in lay.tabs] + [('search', lay.search),
                     ('account', lay.account)] + [(k, r) for k, r in lay.buttons]
            for i, (ka, a) in enumerate(parts):
                for kb, b in parts[i + 1:]:
                    self.assertFalse(overlap(a, b), (w, ka, a, kb, b))
                self.assertTrue(a[2] >= 0 and a[0] >= 0 and a[0] + a[2] <= w + 1e-6, (w, ka, a))

    def test_faixa_de_arrastar(self):
        """Uma faixa do cabeçalho sem controle, com pelo menos 120 px livres, que o clique trata como arrastar."""
        for w, lay in self.layouts():
            hx, hy, hw, hh = lay.header
            controls = [r for _k, r in lay.tabs] + [lay.search, lay.account] + [r for _k, r in lay.buttons]
            best = (0.0, None)
            for y in range(int(hy) + 8, int(hy + hh) - 8, 2):          # longe das bordas de redimensionar
                xs = sorted((r[0], r[0] + r[2]) for r in controls if r[1] <= y <= r[1] + r[3])
                edge = hx + 8
                for x0, x1 in xs + [(hx + hw - 8, hx + hw - 8)]:
                    if x0 - edge > best[0]:
                        best = (x0 - edge, ((edge + x0) / 2, y))
                    edge = max(edge, x1)
            free, point = best
            self.assertGreaterEqual(free, 120.0, (w, free))
            self.assertEqual(lc.hit_max(lay, point[0], point[1], 1.0), 'HEADER', (w, point))

    def test_busca_cabe_inteira(self):
        for w, lay in self.layouts():
            self.assertGreaterEqual(lay.search[2], 110.0, (w, lay.search))


if __name__ == "__main__":
    unittest.main()
