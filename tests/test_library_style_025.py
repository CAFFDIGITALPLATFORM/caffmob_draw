"""A paleta da janela da Biblioteca segue o mockup de 2026-11-26 (feature 025)."""

import unittest

import _bootstrap  # noqa: F401  (stub de bpy para os tokens puros)
from caffmob_draw.library_panel import detail_core, style
from caffmob_draw.library_panel.style import hex_rgba


class PaletaBibliotecaTest(unittest.TestCase):
    def test_tokens_light_do_mockup(self):
        self.assertEqual(style.SURFACE, hex_rgba("#FFFBF5", 0.98))
        self.assertEqual(style.SURFACE_RAISED, hex_rgba("#FFF8EC", 0.99))
        self.assertEqual(style.SURFACE_HOVER, hex_rgba("#FFF0DF"))
        self.assertEqual(style.SURFACE_SUNKEN, hex_rgba("#F5EFE3"))
        self.assertEqual(style.BORDER, hex_rgba("#EADDCB"))
        self.assertEqual(style.BORDER_STRONG, hex_rgba("#DECBB0"))
        self.assertEqual(style.TEXT, hex_rgba("#2B1A0E"))
        self.assertEqual(style.TEXT_MUTED, hex_rgba("#7A6A5A"))
        self.assertEqual(style.ACCENT, hex_rgba("#B45309"))
        self.assertEqual(style.SUCCESS, hex_rgba("#0E7C74"))

    def test_card_branco_com_tinta_cafe(self):
        self.assertEqual(detail_core.FUNDO, (1.0, 1.0, 1.0, 0.98))
        self.assertEqual(detail_core.TINTA, (0.169, 0.102, 0.055, 1.0))
        self.assertEqual(detail_core.CAMPO, (0.961, 0.937, 0.890, 1.0))


if __name__ == '__main__':
    unittest.main()
