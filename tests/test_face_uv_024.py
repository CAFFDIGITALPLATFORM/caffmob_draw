"""Testes do UV por face da chapa (feature 024, T003; RN-03, D-03).

Caixa de 600 × 18 × 720 mm em metros (a malha do `build` usa metros): espessura no eixo Y, então +Y é a face de fora,
−Y a de dentro e as quatro faces restantes são fita.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.armario_v2 import face_uv_core as uv

CAIXA = ((0.0, 0.0, 0.0), (0.6, 0.018, 0.72))


class FaceUvTest(unittest.TestCase):
    def test_face_de_fora_e_de_dentro(self):
        self.assertEqual(uv.tipo_da_face(CAIXA, (0.0, 1.0, 0.0)), uv.EXTERNA)
        self.assertEqual(uv.tipo_da_face(CAIXA, (0.0, -1.0, 0.0)), uv.INTERNA)

    def test_quatro_arestas_sao_fita(self):
        for normal in ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)):
            self.assertEqual(uv.tipo_da_face(CAIXA, normal), uv.FITA, normal)

    def test_uv_em_metros_com_u_no_comprimento(self):
        inicio = uv.uv_metros(CAIXA, (0.0, 1.0, 0.0), (0.0, 0.018, 0.0))
        fim = uv.uv_metros(CAIXA, (0.0, 1.0, 0.0), (0.6, 0.018, 0.72))
        self.assertAlmostEqual(abs(fim[0] - inicio[0]), 0.72)      # U no eixo mais comprido (Z)
        self.assertAlmostEqual(abs(fim[1] - inicio[1]), 0.6)       # V no outro eixo do plano (X)

    def test_interna_espelha_o_u(self):
        fora = uv.uv_metros(CAIXA, (0.0, 1.0, 0.0), (0.6, 0.018, 0.72))
        dentro = uv.uv_metros(CAIXA, (0.0, -1.0, 0.0), (0.6, 0.0, 0.72))
        self.assertAlmostEqual(fora[0], 0.72)
        self.assertAlmostEqual(dentro[0], 0.018)                    # canto oposto + uma espessura de avanço
        self.assertAlmostEqual(fora[1], dentro[1])

    def test_fita_tem_v_na_espessura(self):
        u, v = uv.uv_metros(CAIXA, (1.0, 0.0, 0.0), (0.6, 0.01, 0.5))
        self.assertAlmostEqual(u, 0.5)                             # comprimento da aresta
        self.assertAlmostEqual(v, 0.01)                            # espessura da chapa

    def test_retangulo_cobre_a_face(self):
        (u0, v0), (u1, v1) = uv.retangulo(CAIXA, (0.0, 1.0, 0.0))
        self.assertAlmostEqual(u1 - u0, 0.72)
        self.assertAlmostEqual(v1 - v0, 0.6)
        fora = uv.retangulo(CAIXA, (0.0, 1.0, 0.0))
        dentro = uv.retangulo(CAIXA, (0.0, -1.0, 0.0))
        self.assertNotEqual(fora, dentro)                          # fora e dentro não dividem o retângulo

    def test_layer_uv_reaproveitado(self):
        self.assertEqual(uv.LAYER_UV, 'UVMap')


if __name__ == '__main__':
    unittest.main()
