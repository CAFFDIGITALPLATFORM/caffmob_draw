"""Testes do layout do retângulo maximizado da BIBLIOTECA CAFFMOB (feature 014, T018; RN-08, RN-09, D-18).

O layout segue a direção visual (`_reversa_forward/014-texturas-fabricantes-grade/design-direction.md`): cabeçalho de
36 px (ícone, título, abas, busca, conta e botões fixar/minimizar/fechar), coluna de filtros de 180 px, grade e
rodapé de download opcional; o rótulo do estado aberto ganha o botão de maximizar.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import grid_core as gc
from caffmob_draw.library_panel import layout_core as lc
from caffmob_draw.library_panel import style


def width(text):
    return 6.0 * len(text)


ITEMS = [('CREATE_CABINET', "Criar armário"), ('CAT:Cozinha', "Cozinha"), ('CREATE_CATEGORY', "Criar categoria")]
RECT = (150.0, 70.0, 1040.0, 770.0)
TABS = [('BLOCKS', "Blocos"), ('TEXTURES', "Texturas")]
TREE = [('arauco', "Arauco", 107, []), ('duratex', "Duratex", 106, [('design', "Design", 13), ('essencial', "Essencial", 17)]),
        ('eucatex', "Eucatex", 106, [('a', "A", 1)])]


def inside(inner, outer):
    return (inner[0] >= outer[0] - 1e-6 and inner[1] >= outer[1] - 1e-6
            and inner[0] + inner[2] <= outer[0] + outer[2] + 1e-6 and inner[1] + inner[3] <= outer[1] + outer[3] + 1e-6)


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


class TokensTest(unittest.TestCase):
    def test_tokens_da_direcao(self):
        self.assertEqual(style.HEADER_H, gc.HEADER_H)
        self.assertEqual(style.SIDEBAR_W, gc.SIDEBAR_W)
        self.assertEqual((style.CELL_W, style.CELL_H), (gc.CELL_W, gc.CELL_H))
        self.assertEqual(len(style.SURFACE), 4)
        self.assertAlmostEqual(style.SURFACE[3], 0.96)
        self.assertEqual(style.hex_rgba("#F07A2A")[:3], style.ACCENT[:3])


class OpenLabelTest(unittest.TestCase):
    def test_coluna_aberta_sem_mudanca(self):
        """A coluna do estado aberto continua igual à da 012 (mesmos itens, ordem e largura única)."""
        old = lc.panel_layout(0, 600, 1.0, None, True, ITEMS, width)
        self.assertEqual([k for k, _r in old.items], [k for k, _l in ITEMS])

    def test_rotulo_com_maximizar(self):
        """Aberto, o rótulo reserva espaço para o botão de maximizar, sem cobrir o texto."""
        lay = lc.panel_layout(0, 600, 1.0, None, True, ITEMS, width, with_maximize=True)
        plain = lc.panel_layout(0, 600, 1.0, None, True, ITEMS, width)
        self.assertGreater(lay.label[2], plain.label[2] - 1e-6)
        button = lc.maximize_button(lay, 1.0)
        self.assertTrue(inside(button, lay.label))
        x, y, w, h = button
        self.assertEqual(lc.hit(lay, x + w / 2, y + h / 2, maximize_scale=1.0), 'MAXIMIZE')
        self.assertGreaterEqual(x, lay.label[0] + lc.PAD_X + width(lc.TITLE))     # depois do texto


class MaxLayoutTest(unittest.TestCase):
    def setUp(self):
        self.lay = lc.max_layout(RECT, 1.0, width, TABS, "leo@caff.digital", footer=True)

    def test_regioes_dentro_do_retangulo(self):
        lay = self.lay
        for part in (lay.header, lay.sidebar, lay.grid, lay.footer, lay.search, lay.account):
            self.assertTrue(inside(part, RECT), part)
        self.assertEqual(lay.header[3], style.HEADER_H)
        self.assertEqual(lay.header[1] + lay.header[3], RECT[1] + RECT[3])
        self.assertEqual(lay.sidebar[2], style.SIDEBAR_W)
        self.assertEqual(lay.footer[3], style.FOOTER_H)
        self.assertFalse(overlap(lay.grid, lay.sidebar))
        self.assertFalse(overlap(lay.grid, lay.header))
        self.assertFalse(overlap(lay.grid, lay.footer))

    def test_sem_rodape(self):
        lay = lc.max_layout(RECT, 1.0, width, TABS, "leo@caff.digital", footer=False)
        self.assertIsNone(lay.footer)
        self.assertLess(lay.grid[1], self.lay.grid[1])          # a grade desce até o fim

    def test_cabecalho_em_ordem(self):
        """Ícone e título à esquerda, abas, e da direita para a esquerda: fechar, minimizar, fixar, conta, busca."""
        lay = self.lay
        keys = [k for k, _r in lay.buttons]
        self.assertEqual(keys, ['CLOSE', 'MINIMIZE', 'PIN'])
        xs = [r[0] for _k, r in lay.buttons]
        self.assertEqual(xs, sorted(xs, reverse=True))
        self.assertLess(lay.account[0] + lay.account[2], min(xs))
        self.assertLess(lay.search[0] + lay.search[2], lay.account[0])
        self.assertLess(lay.title[0], lay.tabs[0][1][0])
        self.assertLess(lay.tabs[-1][1][0] + lay.tabs[-1][1][2], lay.search[0])
        self.assertEqual([k for k, _r in lay.tabs], ['BLOCKS', 'TEXTURES'])

    def test_acerto(self):
        lay = self.lay

        def center(r):
            return r[0] + r[2] / 2, r[1] + r[3] / 2
        for key, r in lay.buttons:
            self.assertEqual(lc.hit_max(lay, *center(r), scale=1.0), key)
        self.assertEqual(lc.hit_max(lay, *center(lay.tabs[1][1]), scale=1.0), 'TAB:TEXTURES')
        self.assertEqual(lc.hit_max(lay, *center(lay.search), scale=1.0), 'SEARCH')
        self.assertEqual(lc.hit_max(lay, *center(lay.account), scale=1.0), 'ACCOUNT')
        self.assertEqual(lc.hit_max(lay, *center(lay.grid), scale=1.0), 'GRID')
        self.assertEqual(lc.hit_max(lay, *center(lay.sidebar), scale=1.0), 'SIDEBAR')
        self.assertEqual(lc.hit_max(lay, lay.header[0] + 300, lay.header[1] + 18, scale=1.0), 'HEADER')
        self.assertEqual(lc.hit_max(lay, RECT[0] + RECT[2] - 1, RECT[1] + 300, scale=1.0), 'RIGHT')
        self.assertEqual(lc.hit_max(lay, RECT[0] + 1, RECT[1] + 300, scale=1.0), 'LEFT')
        self.assertEqual(lc.hit_max(lay, RECT[0] + 500, RECT[1] + 1, scale=1.0), 'BOTTOM')
        self.assertIsNone(lc.hit_max(lay, 10, 10, scale=1.0))

    def test_escala(self):
        big = lc.max_layout((0, 0, 2080, 1540), 2.0, width, TABS, "x", footer=False)
        self.assertEqual(big.header[3], 2 * style.HEADER_H)
        self.assertEqual(big.sidebar[2], 2 * style.SIDEBAR_W)


class NarrowHeaderTest(unittest.TestCase):
    def test_cabecalho_estreito_sem_sobreposicao(self):
        """Na largura mínima, abas, busca, conta e botões não se cobrem; a conta vira só o ponto de estado."""
        rect = (0.0, 0.0, gc.MIN_W, 500.0)
        lay = lc.max_layout(rect, 1.0, width, TABS, "Entrar com a conta CAFF Mob", footer=False)
        parts = [r for _k, r in lay.tabs] + [lay.search, lay.account] + [r for _k, r in lay.buttons]
        for i, a in enumerate(parts):
            for b in parts[i + 1:]:
                self.assertFalse(overlap(a, b), (a, b))
        self.assertTrue(lay.compact)
        self.assertEqual(lay.account[2], style.CHIP_PAD)
        self.assertGreaterEqual(lay.search[2], style.SEARCH_MIN)

    def test_cabecalho_largo_mostra_a_conta(self):
        lay = lc.max_layout(RECT, 1.0, width, TABS, "Entrar com a conta CAFF Mob", footer=False)
        self.assertFalse(lay.compact)
        self.assertEqual(lay.account[2], width("Entrar com a conta CAFF Mob") + style.CHIP_PAD)


class SidebarTest(unittest.TestCase):
    def test_linhas_da_coluna(self):
        """Fabricantes em ordem; só o aberto mostra as coleções, recuadas; rótulo 'Fabricantes' no topo."""
        lay = lc.max_layout(RECT, 1.0, width, TABS, "x", footer=False)
        rows = lc.sidebar_rows(lay.sidebar, TREE, open_id='duratex', scale=1.0)
        keys = [k for k, _r, _d in rows]
        self.assertEqual(keys, ['MAN:arauco', 'MAN:duratex', 'COL:duratex/design', 'COL:duratex/essencial',
                                'MAN:eucatex'])
        depths = [d for _k, _r, d in rows]
        self.assertEqual(depths, [0, 0, 1, 1, 0])
        tops = [r[1] for _k, r, _d in rows]
        self.assertEqual(tops, sorted(tops, reverse=True))
        self.assertTrue(all(r[3] == style.ROW_H for _k, r, _d in rows))
        self.assertLess(rows[0][1][1] + rows[0][1][3], lay.sidebar[1] + lay.sidebar[3] - style.CAPTION_H + 1e-6)
        key, rect, _d = rows[2]
        self.assertEqual(lc.hit_rows(rows, rect[0] + 5, rect[1] + 5), key)

    def test_coluna_cortada_no_fundo(self):
        """Linhas que passariam do fundo da coluna não entram (a coluna rola na T030)."""
        tree = [(f"m{i}", f"M{i}", 1, []) for i in range(80)]
        lay = lc.max_layout(RECT, 1.0, width, TABS, "x", footer=False)
        rows = lc.sidebar_rows(lay.sidebar, tree, open_id='', scale=1.0)
        self.assertLess(len(rows), 80)
        self.assertTrue(all(r[1] >= lay.sidebar[1] for _k, r, _d in rows))


if __name__ == "__main__":
    unittest.main()
