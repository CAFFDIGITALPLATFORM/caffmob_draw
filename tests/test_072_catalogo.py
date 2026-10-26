"""072 (T010; D-02, D-10, M-01): catálogo de corrediças."""
import tempfile
import unittest

import _gavetas_072  # noqa: F401
from caffmob_draw.drawers import catalogo


class CatalogoTest(unittest.TestCase):
    def test_seis_tipos_de_fabrica(self):
        ids = [c.id for c in catalogo.FABRICA]
        self.assertEqual(ids, ['telescopica', 'telescopica_soft', 'telescopica_toque', 'oculta_soft', 'oculta_toque',
                               'lateral_metalica'])
        for c in catalogo.FABRICA[:3]:
            self.assertEqual((c.folga_total, c.recuo_fundo, c.laterais_mdf), (26, 0, True))
        oculta = catalogo.por_id('oculta_soft')
        self.assertEqual((oculta.folga_total, oculta.recuo_fundo, oculta.furo_traseira, oculta.lateral_max),
                         (10, 12, 6, 16))
        self.assertFalse(catalogo.por_id('lateral_metalica').laterais_mdf)
        self.assertTrue(catalogo.por_id('telescopica_toque').toque and catalogo.por_id('oculta_toque').toque)
        self.assertEqual(catalogo.COMPRIMENTOS, (300, 350, 400, 450, 500, 550))

    def test_codigo_e_nome_de_ferragem(self):
        c = catalogo.por_id('telescopica_soft')
        self.assertEqual(c.codigo_de_ferragem(500), 'CORREDICA_TELESCOPICA_SOFT_500')
        self.assertEqual(c.nome_de_ferragem(500), 'Corrediça telescópica soft 500 mm (par)')

    def test_corredica_da_pessoa(self):
        pasta = tempfile.mkdtemp()
        minha = catalogo.Corredica('usuario:hettich_x', 'Hettich X', 'oculta', 9, recuo_fundo=13, furo_traseira=6,
                                   lateral_max=16, codigo='HETTICH_X', comprimentos=(270, 470))
        intrusa = catalogo.Corredica('telescopica', 'Falsa', 'telescopica', 1, codigo='X')
        catalogo.gravar_usuario(pasta, [minha, intrusa])
        lidas = catalogo.ler_usuario(pasta)
        self.assertEqual([c.id for c in lidas], ['usuario:hettich_x'])
        self.assertEqual(lidas[0].comprimentos, (270, 470))
        self.assertEqual(catalogo.por_id('telescopica', pasta).folga_total, 26)      # a de fábrica não é trocada
        self.assertEqual(len(catalogo.todas(pasta)), 7)
        self.assertEqual(catalogo.ler_usuario(tempfile.mkdtemp()), ())


if __name__ == '__main__':
    unittest.main()
