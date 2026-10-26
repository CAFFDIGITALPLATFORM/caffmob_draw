"""072 (T012; RN-06 a RN-09): comprimento, divisão da altura, recusas e regras de frente."""
import unittest

import _gavetas_072 as fx
from caffmob_draw.drawers import core


class RegrasTest(unittest.TestCase):
    def test_maior_comprimento_que_cabe(self):
        t = fx.corredica('telescopica')
        self.assertEqual(core.comprimento_que_cabe(530, t), 500)
        self.assertEqual(core.comprimento_que_cabe(460, t), 450)
        self.assertIsNone(core.comprimento_que_cabe(280, t))

    def test_tres_frentes_iguais(self):
        self.assertEqual(core.dividir_altura(684, 3, 2), [(684 - 4) / 3] * 3)
        gavetas = core.gavetas(fx.VAO, core.Gaveta(), fx.corredica('telescopica'), 3, 2)
        self.assertEqual(len(gavetas), 3)
        self.assertTrue(all(c.largura == 538 for _h, c in gavetas))

    def test_recusas_com_motivo(self):
        motivos = core.motivos(fx.NICHO_RASO, core.Gaveta(), fx.corredica('telescopica'))
        self.assertIn("Profundidade livre de 280 mm é menor que a menor corrediça (300 mm).", motivos)
        grossa = core.Gaveta(corredica='oculta_soft', lateral=18)
        self.assertTrue(any('até 16 mm' in m and '15 mm' in m for m in core.motivos(fx.VAO, grossa,
                                                                                fx.corredica('oculta_soft'))))
        estreito = core.Espaco(largura=110, altura=200, profundidade=500)
        self.assertTrue(core.motivos(estreito, core.Gaveta(), fx.corredica('telescopica')))
        with self.assertRaises(ValueError):
            core.caixa(fx.NICHO_RASO, core.Gaveta(), fx.corredica('telescopica'), 200)
        fixo = core.Gaveta(comprimento=550)
        self.assertTrue(any('550' in m for m in core.motivos(fx.VAO, fixo, fx.corredica('telescopica'))))

    def test_regras_de_frente(self):
        cava = core.Gaveta(puxador='cava', frente_espessura=15)
        self.assertTrue(any('cava' in m for m in core.motivos(fx.VAO, cava, fx.corredica('telescopica'))))
        self.assertEqual(core.motivos(fx.VAO, core.Gaveta(puxador='cava', frente_espessura=18),
                                      fx.corredica('telescopica')), [])
        toque = core.Gaveta(corredica='telescopica_toque', recuo_toque=8)
        self.assertTrue(any('3 a 5' in m for m in core.motivos(fx.VAO, toque, fx.corredica('telescopica_toque'))))

    def test_troca_de_corredica(self):
        g = core.Gaveta(corredica='telescopica_soft', comprimento=450)
        nova = core.trocar_corredica(fx.VAO, g, fx.corredica('oculta_soft'), 220)
        self.assertEqual((nova.corredica, nova.comprimento), ('oculta_soft', 0))
        with self.assertRaises(ValueError):
            core.trocar_corredica(fx.VAO, core.Gaveta(lateral=18), fx.corredica('oculta_soft'), 220)
        self.assertEqual(core.Gaveta.de_dict(nova.para_dict()), nova)


if __name__ == '__main__':
    unittest.main()
