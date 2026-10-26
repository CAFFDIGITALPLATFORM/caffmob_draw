"""072 (T011; RN-02 a RN-05): peças da caixa da gaveta com os números dos guias do titular."""
import unittest

import _gavetas_072 as fx
from caffmob_draw.drawers import core


def peca(c, papel, i=0):
    return [p for p in c.pecas if p['papel'] == papel][i]


class CaixaTest(unittest.TestCase):
    def test_telescopica_no_vao_de_564(self):
        c = core.caixa(fx.VAO, core.Gaveta(corredica='telescopica_soft'), fx.corredica('telescopica_soft'), 220)
        self.assertEqual(c.largura, 538)                                   # 564 − 26
        self.assertEqual(c.comprimento, 500)                               # maior nominal em 530 − 10
        self.assertEqual(c.deslocamento_x, 13)
        laterais = [p for p in c.pecas if p['papel'] == 'lateral']
        self.assertEqual(len(laterais), 2)
        self.assertEqual(laterais[0]['tam'], (15, 500, 220 - 40))
        self.assertEqual(peca(c, 'contra_frente')['tam'][0], 508)         # 564 − 26 − 30
        self.assertEqual(peca(c, 'traseira')['tam'][0], 508)
        fundo = peca(c, 'fundo')
        self.assertEqual(fundo['tam'], (508 + 8, 500 - 30 + 8, 6))         # canal de 4 mm nos quatro lados
        self.assertEqual(fundo['pos'][2], 10 + 8)                           # a 8 mm da borda inferior
        self.assertEqual(peca(c, 'traseira')['furos'], [])

    def test_oculta(self):
        c = core.caixa(fx.VAO, core.Gaveta(corredica='oculta_soft'), fx.corredica('oculta_soft'), 220)
        self.assertEqual(c.largura, 554)                                   # 564 − 10: 16 mm mais larga
        self.assertEqual(peca(c, 'contra_frente')['tam'][0], 524)
        self.assertEqual(peca(c, 'fundo')['pos'][2], 10 + 12)               # fundo recuado 12 mm
        furo, = peca(c, 'traseira')['furos']
        self.assertEqual(furo['diametro'], 6)

    def test_lateral_metalica(self):
        c = core.caixa(fx.VAO, core.Gaveta(corredica='lateral_metalica'), fx.corredica('lateral_metalica'), 220)
        self.assertEqual(sorted({p['papel'] for p in c.pecas}), ['fundo', 'traseira'])
        self.assertEqual(peca(c, 'fundo')['tam'][2], 16)

    def test_gavetao_com_fundo_parafusado(self):
        g = core.Gaveta(corredica='oculta_soft', fundo=15, fundo_tipo='parafusado')
        c = core.caixa(fx.VAO, g, fx.corredica('oculta_soft'), 300)
        fundo = peca(c, 'fundo')
        self.assertEqual(fundo['tam'], (524, 500 - 30, 15))
        self.assertEqual(fundo['pos'][2], 10 + 12)

    def test_toque_recua_a_caixa(self):
        c = core.caixa(fx.VAO, core.Gaveta(corredica='telescopica_toque', puxador='sem'),
                       fx.corredica('telescopica_toque'), 220)
        self.assertEqual(c.recuo, 4)
        self.assertEqual(peca(c, 'lateral')['pos'][1], 4)

    def test_registros_para_o_corte(self):
        c = core.caixa(fx.VAO, core.Gaveta(corredica='oculta_soft'), fx.corredica('oculta_soft'), 220)
        regs = core.registros(c, 'g1')
        self.assertTrue(all(r['comprimento'] >= r['largura'] >= r['espessura'] for r in regs))
        traseira = next(r for r in regs if r['papel'] == 'traseira')
        self.assertEqual((traseira['comprimento'], traseira['espessura'], len(traseira['furos'])), (524, 15, 1))


if __name__ == '__main__':
    unittest.main()
