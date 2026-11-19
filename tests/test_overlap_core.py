"""Testes do núcleo do seletor de sobreposição (feature 016, T003): `caffmob_draw/selection/overlap_core.py`.

Puros, sem Blender: ordenação, estado do seletor e geometria do painel.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.selection import overlap_core as core


class Obj:
    """Objeto simulado: só o nome importa para a lista."""

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Obj({self.name})"


A, B, C, D = (Obj(name) for name in ("A", "B", "C", "D"))


class RankTest(unittest.TestCase):
    def test_ordena_do_mais_proximo_ao_mais_distante(self):
        self.assertEqual(core.rank([(2.0, C), (0.5, A), (1.0, B)]), [A, B, C])

    def test_nao_repete_o_mesmo_objeto(self):
        self.assertEqual(core.rank([(1.0, A), (0.2, A), (0.5, B)]), [A, B])

    def test_lista_vazia(self):
        self.assertEqual(core.rank([]), [])


class PickerTest(unittest.TestCase):
    def test_inicia_no_primeiro_sem_marcados(self):
        picker = core.Picker([A, B, C])
        self.assertEqual((picker.focus, picker.scroll), (0, 0))
        self.assertEqual(picker.staged, set())
        self.assertIs(picker.focused, A)

    def test_toggle_marca_e_desmarca(self):
        picker = core.Picker([A, B, C])
        picker.toggle(1)
        self.assertEqual(picker.staged, {B})
        picker.toggle(1)
        self.assertEqual(picker.staged, set())
        picker.toggle(9)
        self.assertEqual(picker.staged, set())

    def test_mark_all_e_invert(self):
        picker = core.Picker([A, B, C])
        picker.mark_all()
        self.assertEqual(picker.staged, {A, B, C})
        picker.invert()
        self.assertEqual(picker.staged, set())
        picker.toggle(2)
        picker.invert()
        self.assertEqual(picker.staged, {A, B})

    def test_add_e_remove_no_foco(self):
        picker = core.Picker([A, B, C])
        picker.add(0)
        picker.move(1)
        picker.add(picker.focus)
        self.assertEqual(picker.staged, {A, B})
        picker.remove(1)
        self.assertEqual(picker.staged, {A})

    def test_move_respeita_as_pontas(self):
        picker = core.Picker([A, B, C])
        picker.move(99)
        self.assertEqual(picker.focus, 2)
        picker.move(-99)
        self.assertEqual(picker.focus, 0)

    def test_foco_continua_visivel_na_rolagem(self):
        hits = [Obj(f"O{i:02d}") for i in range(20)]
        picker = core.Picker(hits)
        picker.move(15)
        self.assertEqual(picker.focus, 15)
        self.assertEqual(picker.scroll, 15 - core.MAX_VISIBLE + 1)
        picker.move(0)
        self.assertTrue(picker.scroll <= picker.focus < picker.scroll + core.MAX_VISIBLE)

    def test_scroll_para_nos_limites_da_lista(self):
        picker = core.Picker([Obj(f"O{i:02d}") for i in range(20)])
        picker.scroll_by(99)
        self.assertEqual(picker.scroll, 20 - core.MAX_VISIBLE)
        picker.scroll_by(-99)
        self.assertEqual(picker.scroll, 0)

    def test_scroll_nao_mexe_foco_nem_marcados(self):
        picker = core.Picker([Obj(f"O{i:02d}") for i in range(20)])
        picker.toggle(0)
        picker.scroll_by(3)
        self.assertEqual((picker.focus, picker.staged), (0, {picker.hits[0]}))

    def test_visible_e_uma_janela_de_doze(self):
        hits = [Obj(f"O{i:02d}") for i in range(20)]
        picker = core.Picker(hits)
        self.assertEqual(picker.visible(), hits[:core.MAX_VISIBLE])
        picker.scroll_by(2)
        self.assertEqual(picker.visible(), hits[2:2 + core.MAX_VISIBLE])

    def test_lista_vazia_nao_quebra(self):
        picker = core.Picker([])
        picker.move(1)
        picker.scroll_by(1)
        self.assertEqual((picker.focus, picker.scroll, picker.focused), (-1, 0, None))


class ConfirmTest(unittest.TestCase):
    """RF-10 e RF-12: o `Enter` aplica o marcado e preserva o que já estava selecionado fora da lista."""

    def test_sem_selecao_previa_aplica_os_marcados(self):
        selection, active = core.confirm_selection([A, B, C], {A, C}, [], None, C)
        self.assertEqual(selection, [A, C])
        self.assertIs(active, C)

    def test_soma_a_selecao_anterior(self):
        selection, active = core.confirm_selection([A, B, C], {B}, [D], D, B)
        self.assertEqual(selection, [D, B])
        self.assertIs(active, B)

    def test_desmarcar_tira_o_que_ja_estava_selecionado(self):
        selection, active = core.confirm_selection([A, B], {A}, [A, D], D, A)
        self.assertEqual(selection, [D, A])
        self.assertIs(active, A)
        selection, active = core.confirm_selection([A, B], {B}, [A], A, B)
        self.assertEqual(selection, [B])
        self.assertIs(active, B)

    def test_foco_desmarcado_nao_vira_ativo(self):
        selection, active = core.confirm_selection([A, B], {A}, [A], None, B)
        self.assertEqual(selection, [A])
        self.assertIs(active, A)

    def test_sem_marcado_nem_selecao_anterior(self):
        selection, active = core.confirm_selection([A], set(), [], None, A)
        self.assertEqual((selection, active), ([], None))


class PanelTest(unittest.TestCase):
    def test_tamanho_do_painel(self):
        rect = core.panel_rect((100, 100), (800, 600), 3)
        self.assertEqual(rect[2:], (core.WIDTH, core.HEADER + 3 * core.ROW_H + core.FOOTER))

    def test_no_maximo_doze_linhas(self):
        rect = core.panel_rect((100, 100), (800, 600), 20)
        self.assertEqual(rect[3], core.HEADER + core.MAX_VISIBLE * core.ROW_H + core.FOOTER)

    def test_preso_a_regiao(self):
        self.assertEqual(core.panel_rect((100, 100), (800, 600), 3)[:2], (118, 8))
        rect = core.panel_rect((795, 590), (800, 600), 3)
        self.assertLessEqual(rect[0] + rect[2], 800 - 8)
        self.assertLessEqual(rect[1] + rect[3], 600 - 8)

    def test_vira_para_o_outro_lado_perto_da_borda(self):
        rect = core.panel_rect((700, 300), (800, 600), 3)
        self.assertEqual(rect[0], 700 - 18 - core.WIDTH)

    def test_row_at_conta_a_rolagem(self):
        rect = core.panel_rect((100, 100), (800, 600), 3)
        rows = core.rows_rect(rect)
        top = rows[1] + rows[3]
        self.assertEqual(core.row_at((rows[0] + 5, top - 5), rect, 0, 3), 0)
        self.assertEqual(core.row_at((rows[0] + 5, rows[1] + 5), rect, 0, 3), 2)
        self.assertEqual(core.row_at((rows[0] + 5, top - 5), rect, 2, 3), 2)

    def test_row_at_fora_das_linhas(self):
        rect = core.panel_rect((100, 100), (800, 600), 3)
        rows = core.rows_rect(rect)
        self.assertIsNone(core.row_at((rows[0] + 5, rows[1] - 2), rect, 0, 3))
        self.assertIsNone(core.row_at((rect[0] - 2, rows[1] + 5), rect, 0, 3))
        self.assertIsNone(core.row_at((rows[0] + 5, rows[1] + 5), rect, 1, 3))

    def test_action_at(self):
        rect = core.panel_rect((100, 100), (800, 600), 3)
        rows = core.rows_rect(rect)
        top = rows[1] + rows[3]
        self.assertEqual(core.action_at((rows[0] + 5, top - 5), rect, 0, 3), (core.ROW, 0))
        self.assertEqual(core.action_at((rows[0] + 5, rect[1] + 5), rect, 0, 3), (core.FOOTER_HIT, None))
        self.assertEqual(core.action_at((rows[0] + 5, top + 5), rect, 0, 3), (core.HEADER_HIT, None))
        self.assertEqual(core.action_at((rect[0] - 5, top + 5), rect, 0, 3), (core.OUTSIDE, None))


if __name__ == "__main__":
    unittest.main()
