"""Card branco de detalhe do módulo na Biblioteca (2026-11-26).

Testa em Python puro o que o desenho, o clique e o operador de digitação usam: layout dentro da grade, acerto de
clique (campo, ambiente, inserir, cancelar), formatação/leitura das medidas e a validação contra o Padrão de
Dimensões (máximos do módulo, chapa máxima e espessura da lateral). As dimensões são em milímetros.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import detail_core as dc

GRID = (100.0, 100.0, 900.0, 700.0)
CHAPA = (1810.0, 2730.0)
MODULO = (1200.0, 2700.0, 900.0)


class LayoutTest(unittest.TestCase):
    def test_card_cabe_na_grade(self):
        lay = dc.layout(GRID, 1.0)
        x, y, w, h = lay.card
        self.assertGreaterEqual(x, GRID[0])
        self.assertGreaterEqual(y, GRID[1])
        self.assertLessEqual(x + w, GRID[0] + GRID[2] + 1e-6)
        self.assertLessEqual(y + h, GRID[1] + GRID[3] + 1e-6)

    def test_partes_ficam_dentro_do_card(self):
        lay = dc.layout(GRID, 1.0)
        x, y, w, h = lay.card
        for _key, rect in list(lay.campos) + list(lay.chips):
            self.assertGreaterEqual(rect[0], x - 1e-6)
            self.assertGreaterEqual(rect[1], y - 1e-6)
            self.assertLessEqual(rect[0] + rect[2], x + w + 1e-6)
            self.assertLessEqual(rect[1] + rect[3], y + h + 1e-6)
        for rect in (lay.ok, lay.cancelar):
            self.assertLessEqual(rect[0] + rect[2], x + w + 1e-6)
            self.assertLessEqual(rect[1] + rect[3], y + h + 1e-6)

    def test_cinco_ambientes(self):
        self.assertEqual([code for code, _label in dc.AMBIENTES], ['COZ', 'DOR', 'BAN', 'SAL', 'ESC'])
        self.assertEqual(len(dc.layout(GRID, 1.0).chips), 5)


class HitTest(unittest.TestCase):
    def setUp(self):
        self.lay = dc.layout(GRID, 1.0)

    def _center(self, rect):
        return rect[0] + rect[2] / 2.0, rect[1] + rect[3] / 2.0

    def test_campo(self):
        for key, rect in self.lay.campos:
            self.assertEqual(dc.hit(self.lay, *self._center(rect)), 'FIELD:' + key)

    def test_ambiente(self):
        for code, rect in self.lay.chips:
            self.assertEqual(dc.hit(self.lay, *self._center(rect)), 'LINE:' + code)

    def test_botoes(self):
        self.assertEqual(dc.hit(self.lay, *self._center(self.lay.ok)), 'OK')
        self.assertEqual(dc.hit(self.lay, *self._center(self.lay.cancelar)), 'CANCEL')

    def test_fora_do_card(self):
        self.assertIsNone(dc.hit(self.lay, -50.0, -50.0))


class MedidaTest(unittest.TestCase):
    def test_fmt(self):
        self.assertEqual(dc.fmt(800.0), '800')
        self.assertEqual(dc.fmt(720.5), '720.5')

    def test_parse_aceita_virgula(self):
        self.assertEqual(dc.parse_mm('800'), 800.0)
        self.assertEqual(dc.parse_mm('720,5'), 720.5)

    def test_parse_recusa_texto(self):
        self.assertIsNone(dc.parse_mm('abc'))
        self.assertIsNone(dc.parse_mm(''))


class InsertPropsTest(unittest.TestCase):
    """Props levadas ao inserir: o arraste usa as do card; sem card, só o ambiente do catálogo."""

    def test_medidas_e_ambiente_do_card(self):
        props = dc.insert_props(900.0, 800.0, 500.0, 'DOR', 'COZ')
        self.assertEqual(props, {'line': 'DOR', 'width_mm': 900.0, 'height_mm': 800.0, 'depth_mm': 500.0})

    def test_sem_medidas_mantem_o_arraste_atual(self):
        props = dc.insert_props(0.0, 0.0, 0.0, '', 'COZ')
        self.assertEqual(props, {'line': 'COZ'})

    def test_ambiente_invalido_cai_no_catalogo(self):
        self.assertEqual(dc.insert_props(0.0, 0.0, 0.0, 'XYZ', 'BAN')['line'], 'BAN')


class ValidateTest(unittest.TestCase):
    def test_aceita_medida_valida(self):
        self.assertEqual(dc.validate(900.0, 800.0, 550.0, CHAPA, MODULO, 15.0), (True, ""))

    def test_recusa_acima_do_modulo(self):
        ok, mensagem = dc.validate(1300.0, 800.0, 550.0, CHAPA, MODULO, 15.0)
        self.assertFalse(ok)
        self.assertIn("1200", mensagem)

    def test_recusa_acima_da_chapa(self):
        ok, mensagem = dc.validate(1200.0, 2700.0, 900.0, (600.0, 1000.0), MODULO, 15.0)
        self.assertFalse(ok)
        self.assertIn("chapa", mensagem.lower())

    def test_recusa_medida_zero(self):
        ok, _ = dc.validate(0.0, 800.0, 550.0, CHAPA, MODULO, 15.0)
        self.assertFalse(ok)

    def test_recusa_espessura_que_nao_cabe(self):
        ok, mensagem = dc.validate(20.0, 20.0, 20.0, CHAPA, MODULO, 15.0)
        self.assertFalse(ok)
        self.assertIn("espessura", mensagem.lower())


if __name__ == '__main__':
    unittest.main()
