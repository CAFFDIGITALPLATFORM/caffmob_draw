"""Testes do gerador da textura MDF claro (feature 024, T004; RN-01, D-01).

Determinístico (mesma semente, mesmos bytes), RGBA de 512², claro e bege — o suficiente para o Solid mostrar material.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.armario_v2 import mdf_core


class MdfCoreTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dados = mdf_core.gerar()

    def test_tamanho_rgba(self):
        self.assertEqual(len(self.dados), mdf_core.TAMANHO * mdf_core.TAMANHO * 4)

    def test_deterministico(self):
        self.assertEqual(self.dados, mdf_core.gerar())

    def test_opaco(self):
        self.assertTrue(all(self.dados[i] == 255 for i in range(3, len(self.dados), 4)))

    def test_claro_e_bege(self):
        amostra = [self.dados[i] for i in range(0, len(self.dados), 4 * 97)]
        media = sum(amostra) / len(amostra)
        self.assertGreater(media, 190.0)
        self.assertLess(media, 235.0)
        r, g, b = (self.dados[i] for i in (0, 1, 2))
        self.assertGreaterEqual(r, g)       # bege quente: vermelho >= verde >= azul
        self.assertGreaterEqual(g, b)

    def test_semente_muda_a_textura(self):
        self.assertNotEqual(mdf_core.gerar(semente=7), self.dados)


if __name__ == '__main__':
    unittest.main()
