"""Testes do núcleo da galeria de estruturas de caixa (feature 015, T009; RN-11, RN-21, RF-11, RF-21, D-10, D-11)."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import gallery_core as gc
from caffmob_draw.cabinet_editor import structures_core as sc
from caffmob_draw.library_panel import grid_core


def measure(text):
    return 7.0 * len(text)


def center(r):
    return (r[0] + r[2] / 2, r[1] + r[3] / 2)


def structure(sid, env, order, label=None, group='INFERIOR', **extra):
    item = {"id": sid, "environment": env, "group": group, "order": order, "label_pt": label or sid,
            "size_mm": {"width": 500, "height": None, "depth": None},
            "components": {"LEFT": True, "RIGHT": True, "BOTTOM": True, "TOP": False, "BACK": True,
                           "STRETCHER_FRONT": True, "STRETCHER_BACK": True}}
    item.update(extra)
    return item


def catalog(structures, environments=None):
    envs = environments or [{"id": "DOR", "label_pt": "Dormitórios", "line": "DOR"},
                            {"id": "COZ", "label_pt": "Cozinhas", "line": "COZ"}]
    return sc.parse(json.dumps({"schema-version": 1, "environments": envs, "structures": structures}))


class TabsTest(unittest.TestCase):
    def setUp(self):
        self.cat = catalog([structure("c_b", "COZ", 20, "B"), structure("c_a", "COZ", 10, "A"),
                            structure("d_a", "DOR", 5, "Armário", group='DESPENSEIRO')])

    def test_abas_na_ordem_do_catalogo(self):
        self.assertEqual([t[0] for t in gc.tabs(self.cat)], ["DOR", "COZ"])
        self.assertEqual(gc.tab_index(self.cat, ""), 0)
        self.assertEqual(gc.tab_index(self.cat, "COZ"), 1)
        self.assertEqual(gc.tab_index(self.cat, "XYZ"), 0)

    def test_estruturas_ordenadas_por_order(self):
        state = gc.GalleryState(self.cat, "COZ")
        self.assertEqual([s.id for s in state.items], ["c_a", "c_b"])
        self.assertEqual(state.selected.id, "c_a")             # a primeira já vem escolhida
        state.set_tab(0)
        self.assertEqual([s.id for s in state.items], ["d_a"])
        self.assertEqual(state.scroll, 0.0)

    def test_catalogo_real_abre_cozinhas(self):
        real = sc.load()
        self.assertEqual(gc.tabs(real)[0][0], "COZ")
        state = gc.GalleryState(real, "DOR")
        self.assertTrue(state.items and all(s.environment == "DOR" for s in state.items))

    def test_texto_de_estado(self):
        state = gc.GalleryState(self.cat, "COZ")
        self.assertEqual(state.status(), "Selecionado: A")
        self.assertEqual(gc.status_text(None), "Nenhuma estrutura selecionada")


class GridTest(unittest.TestCase):
    def test_colunas_pela_largura_da_regiao(self):
        wide = gc.layout(1920, 1080, 1.0, ["Cozinhas"], measure)
        narrow = gc.layout(500, 800, 1.0, ["Cozinhas"], measure)
        self.assertGreaterEqual(grid_core.columns(wide.grid[2], 1.0), 5)
        self.assertLess(grid_core.columns(narrow.grid[2], 1.0), grid_core.columns(wide.grid[2], 1.0))
        x, y, w, h = narrow.rect
        self.assertTrue(x >= 0 and y >= 0 and x + w <= 500 and y + h <= 800)

    def test_quadro_e_abas_dentro(self):
        lay = gc.layout(1600, 900, 1.0, ["Cozinhas", "Dormitórios"], measure)
        x, y, w, h = lay.rect
        for _i, (tx, ty, tw, th) in lay.tabs:
            self.assertTrue(x <= tx and tx + tw <= x + w and y <= ty and ty + th <= y + h)
        self.assertLess(lay.tabs[0][1][0], lay.tabs[1][1][0])
        self.assertLess(lay.ok[0], lay.cancel[0])              # OK antes de Cancelar

    def test_acerto_de_celula_com_rolagem(self):
        lay = gc.layout(1000, 700, 1.0, ["Cozinhas"], measure)
        count = 30
        cells = gc.visible_cells(lay, count, 1.0, 0.0)
        index, (cx, cy, cw, ch) = cells[1]
        self.assertEqual(gc.hit(lay, cells, cx + cw / 2, cy + ch / 2), ('CELL', index))
        scroll = gc.scroll_by(0.0, 400.0, lay, count, 1.0)
        rolled = gc.visible_cells(lay, count, 1.0, scroll)
        self.assertGreater(rolled[0][0], 0)
        index, (cx, cy, cw, ch) = rolled[0]
        # a célula de cima pode estar cortada: o acerto só vale na parte dentro da grade
        gy = lay.grid[1] + lay.grid[3]
        self.assertEqual(gc.hit(lay, rolled, cx + cw / 2, min(cy + ch, gy) - 2), ('CELL', index))
        self.assertEqual(gc.hit(lay, rolled, cx + cw / 2, gy + 3)[0] != 'CELL', True)
        self.assertEqual(gc.scroll_by(0.0, 10 ** 6, lay, count, 1.0),
                         gc.content_height(lay, count, 1.0) - lay.grid[3])

    def test_botoes_abas_e_fora(self):
        lay = gc.layout(1000, 700, 1.0, ["Cozinhas", "Dormitórios"], measure)
        self.assertEqual(gc.hit(lay, [], *center(lay.ok)), ('OK',))
        self.assertEqual(gc.hit(lay, [], *center(lay.cancel)), ('CANCEL',))
        self.assertEqual(gc.hit(lay, [], *center(lay.tabs[1][1])), ('TAB', 1))
        self.assertEqual(gc.hit(lay, [], *center(lay.title)), ('INSIDE',))
        self.assertIsNone(gc.hit(lay, [], 1, 1))


class KeyboardTest(unittest.TestCase):
    def test_setas(self):
        self.assertEqual(gc.key_action('RIGHT_ARROW', 0, 7, 3), (1, None))
        self.assertEqual(gc.key_action('LEFT_ARROW', 0, 7, 3), (0, None))
        self.assertEqual(gc.key_action('DOWN_ARROW', 1, 7, 3), (4, None))
        self.assertEqual(gc.key_action('DOWN_ARROW', 4, 7, 3), (6, None))     # última linha incompleta
        self.assertEqual(gc.key_action('DOWN_ARROW', 6, 7, 3), (6, None))
        self.assertEqual(gc.key_action('UP_ARROW', 4, 7, 3), (1, None))
        self.assertEqual(gc.key_action('UP_ARROW', 1, 7, 3), (1, None))

    def test_enter_escolhe_e_esc_cancela(self):
        self.assertEqual(gc.key_action('RET', 2, 7, 3), (2, 'OK'))
        self.assertEqual(gc.key_action('NUMPAD_ENTER', 2, 7, 3), (2, 'OK'))
        self.assertEqual(gc.key_action('RET', -1, 0, 3), (-1, None))          # sem seleção, Enter não cria
        self.assertEqual(gc.key_action('ESC', 2, 7, 3)[1], 'CANCEL')

    def test_teclado_rola_ate_a_selecao(self):
        cat = catalog([structure("s{:02d}".format(i), "COZ", i) for i in range(30)])
        state = gc.GalleryState(cat, "COZ")
        lay = gc.layout(1000, 700, 1.0, ["Dormitórios", "Cozinhas"], measure)
        for _ in range(8):
            self.assertIsNone(state.key('DOWN_ARROW', lay, 1.0))
        cells = gc.visible_cells(lay, len(state.items), 1.0, state.scroll)
        rect = dict(cells)[state.index]
        self.assertGreaterEqual(rect[1], lay.grid[1] - 1e-6)                  # inteira à vista
        self.assertEqual(state.key('RET', lay, 1.0), 'OK')
        self.assertEqual(state.key('ESC', lay, 1.0), 'CANCEL')


class EmptyTest(unittest.TestCase):
    def test_catalogo_vazio_mostra_aviso(self):
        empty = sc.parse("não é json")
        state = gc.GalleryState(empty)
        self.assertTrue(state.empty)
        self.assertIsNone(state.selected)
        title, hint = gc.empty_state(empty)
        self.assertEqual(title, "Nenhuma estrutura de caixa no catálogo")
        self.assertEqual(hint, "Catálogo de estruturas inválido")
        lay = gc.layout(1000, 700, 1.0, [], measure)
        self.assertEqual(state.key('RET', lay, 1.0), None)
        self.assertEqual(state.status(), "Nenhuma estrutura selecionada")


class ThumbTest(unittest.TestCase):
    def test_elevacao_do_balcao(self):
        recipe = sc.load().by_id("coz_inferior_divisoria")
        shapes = gc.thumb_shapes(recipe)
        x0, z0, x1, z1 = shapes['bounds']
        self.assertAlmostEqual(x1 - x0, 500.0)
        self.assertAlmostEqual(z1 - z0, 720.0)
        self.assertEqual(len(shapes['parts']), 4)            # laterais, base inferior, sarrafo frontal (fundo atrás)
        fitted = gc.fit_shapes(shapes, (100, 100, 140, 140))
        ix, iy, iw, ih = fitted['inner']
        self.assertTrue(100 < ix and ix + iw < 240 and 100 < iy and iy + ih < 240)

    def test_divisorias_pelos_vaos(self):
        recipe = sc.load().by_id("dor_divisoria_sobre_base")
        self.assertEqual(len(gc.thumb_shapes(recipe)['dividers']), recipe.bays - 1)


if __name__ == "__main__":
    unittest.main()
