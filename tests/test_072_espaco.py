"""072, onda B (T050, T053; D-20, D-23): espaço livre em volta de um ponto, pelas caixas das peças."""
import unittest

import _gavetas_072  # noqa: F401
from caffmob_draw.drawers import espaco_core as ec


def C(lo, hi):
    return ec.Caixa(lo, hi)


# Armário de 600 × 560 × 2000 com laterais de 18, fundo de 6 atrás e duas prateleiras (em 700 e 1400)
PECAS = [C((0, 0, 0), (18, 560, 2000)), C((582, 0, 0), (600, 560, 2000)), C((18, 554, 0), (582, 560, 2000)),
         C((18, 0, 0), (582, 554, 18)), C((18, 0, 1982), (582, 554, 2000)),
         C((18, 0, 700), (582, 540, 718)), C((18, 0, 1400), (582, 540, 1418))]
ENVELOPE = ec.envelope_de(PECAS)


class EspacoTest(unittest.TestCase):
    def test_entre_duas_prateleiras(self):
        caixa = ec.livre(PECAS, (300, 200, 1000), ENVELOPE)
        self.assertEqual((caixa.lo, caixa.hi), ((18, 0, 718), (582, 554, 1400)))
        self.assertEqual(caixa.tamanho(), (564, 554, 682))

    def test_embaixo(self):
        caixa = ec.livre(PECAS, (300, 300, 100), ENVELOPE)
        self.assertEqual((caixa.lo[2], caixa.hi[2]), (18, 700))

    def test_ponto_dentro_de_peca_ou_fora(self):
        self.assertIsNone(ec.livre(PECAS, (5, 200, 1000), ENVELOPE))
        self.assertIsNone(ec.livre(PECAS, (300, 900, 1000), ENVELOPE))


if __name__ == '__main__':
    unittest.main()
