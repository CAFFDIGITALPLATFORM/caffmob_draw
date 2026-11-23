"""Escala de UV da 018 (T003; RN-08, RF-07), sem `bpy`.

A chapa tem 1 unidade de UV por metro. A repetição real é a medida da peça dividida pelo tamanho da textura: chapa
de 600 × 400 com textura de 600 mm mostra 1,0 repetição na largura e 2/3 na altura. Textura retangular usa cada eixo
pelo seu lado (1830 × 2750 mm).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import _bootstrap  # noqa: E402,F401  (carrega o pacote sem `bpy`)
from caffmob_draw.texture_library import uv_core  # noqa: E402


class TestRepetir(unittest.TestCase):
    def test_textura_quadrada(self):
        self.assertAlmostEqual(uv_core.repetir(600, 600), 1.0)
        self.assertAlmostEqual(uv_core.repetir(400, 600), 2.0 / 3.0)

    def test_tamanho_invalido(self):
        for tamanho in (0, -600):
            with self.assertRaises(ValueError):
                uv_core.repetir(600, tamanho)


class TestEscalaUv(unittest.TestCase):
    def test_chapa_600_por_400_com_textura_600(self):
        u, v = uv_core.escala_uv(600, 400, 600)
        self.assertAlmostEqual(u, 1.0)
        self.assertAlmostEqual(v, 2.0 / 3.0)

    def test_textura_retangular_usa_cada_eixo_pelo_seu_lado(self):
        u, v = uv_core.escala_uv(600, 400, 1830, 2750)
        self.assertAlmostEqual(u, 600 / 1830)
        self.assertAlmostEqual(v, 400 / 2750)

    def test_sem_altura_usa_a_largura_nos_dois_eixos(self):
        u, v = uv_core.escala_uv(600, 400, 1830)
        self.assertAlmostEqual(u, 600 / 1830)
        self.assertAlmostEqual(v, 400 / 1830)

    def test_tamanho_zero_e_negativo(self):
        for largura, altura in ((0, 600), (-600, 600), (600, 0), (600, -300)):
            with self.assertRaises(ValueError):
                uv_core.escala_uv(600, 400, largura, altura)


class TestGirarUv(unittest.TestCase):
    def test_90_graus_troca_os_eixos(self):
        u, v = uv_core.girar_uv((1.0, 0.5), 90)
        self.assertAlmostEqual(u, 0.5)
        self.assertAlmostEqual(v, 1.0)

    def test_centro_permanece(self):
        self.assertEqual(uv_core.girar_uv((0.5, 0.5), 90), (0.5, 0.5))

    def test_180_graus_espelha(self):
        u, v = uv_core.girar_uv((1.0, 0.25), 180)
        self.assertAlmostEqual(u, 0.0)
        self.assertAlmostEqual(v, 0.75)


if __name__ == "__main__":
    unittest.main()
