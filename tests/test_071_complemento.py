"""071 (T013; D-11, D-30): descritor do complemento local (móveis, lajes livres, malhas e materiais)."""
import math
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2


class ComplementoTest(unittest.TestCase):
    def setUp(self):
        self.r = para_v2.converter(leitor.abrir(ps.promob()).projeto())
        self.moveis = {n['nome']: n for n in self.r['complemento']['moveis']}

    def test_caixa_pelo_canto_frontal(self):
        balcao = self.moveis['Balcão 600']
        self.assertEqual(balcao['tipo'], 'grupo')
        # base (500, 1200) é o canto traseiro; profundidade 580 → frente em y = 620 (RN-03)
        self.assertEqual(tuple(round(v) for v in balcao['origem']), (500, 620, 0))
        self.assertEqual(balcao['dimensoes'], (600, 580, 850))
        porta = next(f for f in balcao['filhos'] if f['nome'] == 'Porta')
        self.assertEqual((porta['tipo'], porta['material']), ('caixa', 'madeira'))

    def test_rotacao_na_origem(self):
        janela = leitor.Item('MODULO', 'j', 'j', '', True, (2850, 700, 1000), 90, 1200, 1000, 150)
        x, y, z = para_v2.origem_da_caixa(janela)
        self.assertAlmostEqual(x, 3000)
        self.assertAlmostEqual(y, 700)

    def test_laje_com_arco(self):
        laje = self.moveis['Piso']
        self.assertEqual((laje['tipo'], laje['altura'], laje['material']), ('laje', 20, 'reboco'))
        xs = [p[0] for p in laje['contorno']]
        self.assertGreater(len(laje['contorno']), 4)               # o arco de 90° virou vários pontos
        self.assertAlmostEqual(max(xs), 3000, delta=1e-6)
        # a corda vai de (2000, 0) a (3000, 1000), na reta x − y = 2000; o arco de 90° passa por fora dela, até ~414 mm
        self.assertTrue(any(p[0] - p[1] > 2400 for p in laje['contorno']))

    def test_malha_vinculada(self):
        malha = self.moveis['EntidadeExterna']
        self.assertEqual(malha['tipo'], 'malha')
        self.assertTrue(malha['entrada'].endswith(f'LinkedFiles/{ps.OBJ_GUID}.obj'))
        self.assertEqual(malha['dimensoes'], (600, 400, 200))

    def test_materiais_e_texturas(self):
        materiais = self.r['complemento']['materiais']
        self.assertEqual(materiais['madeira']['textura'], 'solucao/materials/MyTextures/madeira.png')
        self.assertEqual(materiais['madeira']['escala'], (800, 400))
        self.assertEqual(materiais['cin_cor_000']['nome'], 'Acabamento do modelo (não resolvido)')
        self.assertEqual(materiais['reboco']['cor'], '#e8e2d6')

    def test_visibilidade(self):
        self.assertFalse(self.moveis['Oculto']['visivel'])
        self.assertTrue(self.moveis['Balcão 600']['visivel'])

    def test_contorno_reto_inalterado(self):
        quadrado = [(0, 0, 0), (100, 0, 0), (100, 100, 0), (0, 100, 0)]
        self.assertEqual(para_v2.contorno_com_arcos(quadrado), [(0, 0), (100, 0), (100, 100), (0, 100)])
        arco = para_v2.contorno_com_arcos([(0, 0, 180), (100, 0, 0), (100, -50, 0)])
        meio = arco[len(arco) // 2] if len(arco) > 4 else arco[1]
        self.assertTrue(math.isfinite(meio[0]))


if __name__ == '__main__':
    unittest.main()
