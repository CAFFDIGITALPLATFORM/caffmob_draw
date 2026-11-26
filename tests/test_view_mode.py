"""Testes do modo de vista (feature 010, T008; RN-06, D-05; 027, RF-03): `caffmob_draw/ui/view_mode_core.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.ui import view_mode_core as vm


class ViewModeTest(unittest.TestCase):
    def test_textura_com_linha(self):
        s = vm.settings('TEXTURE', True, 'MATERIAL')
        self.assertEqual((s['shading_type'], s['color_type'], s['show_wireframes']), ('SOLID', 'TEXTURE', False))
        self.assertTrue(s['edges'])          # quem desenha as arestas pretas é `overlays/arestas.py`

    def test_textura_sem_linha(self):
        s = vm.settings('TEXTURE', False, 'MATERIAL')
        self.assertEqual((s['color_type'], s['show_wireframes'], s['edges']), ('TEXTURE', False, False))

    def test_solido_devolve_a_cor_anterior(self):
        self.assertEqual(vm.settings('SOLID', False, 'OBJECT')['color_type'], 'OBJECT')
        self.assertEqual(vm.settings('SOLID', False, '')['color_type'], 'MATERIAL')
        self.assertEqual(vm.settings('SOLID', False, 'TEXTURE')['color_type'], 'MATERIAL')

    def test_linhas_tambem_no_solido(self):
        self.assertTrue(vm.settings('SOLID', True, 'OBJECT')['edges'])

    def test_rotulo(self):
        self.assertEqual(vm.label('TEXTURE', True), "Textura com linha")
        self.assertEqual(vm.label('SOLID', False), "Sólido")


if __name__ == '__main__':
    unittest.main()
