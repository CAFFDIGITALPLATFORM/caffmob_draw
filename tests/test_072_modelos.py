"""072, onda B (T052; RN-10, D-24): modelos de gaveta com a corrediça recomendada pela matriz do guia."""
import tempfile
import unittest

import _gavetas_072  # noqa: F401
from caffmob_draw.drawers import catalogo, core, modelos


class ModelosTest(unittest.TestCase):
    def test_seis_modelos_com_a_corredica_da_matriz(self):
        esperado = {'talheres': 'telescopica_soft', 'panelas': 'oculta_soft', 'joias': 'oculta_toque',
                    'interna': 'telescopica', 'secreta': 'oculta_toque', 'pasta': 'telescopica'}
        self.assertEqual({m.id: m.gaveta['corredica'] for m in modelos.FABRICA}, esperado)
        for m in modelos.FABRICA:
            self.assertIsNotNone(catalogo.por_id(m.gaveta['corredica']))
        secreta = modelos.por_id('secreta')
        self.assertEqual(secreta.gaveta['puxador'], 'sem')
        panelas = modelos.por_id('panelas')
        self.assertEqual((panelas.gaveta['fundo'], panelas.gaveta['fundo_tipo']), (15, 'parafusado'))
        self.assertEqual(modelos.por_id('interna').gaveta['frente_espessura'], 15)

    def test_modelos_cabem_no_balcao(self):
        import _gavetas_072 as fx
        for m in modelos.FABRICA:
            g = core.Gaveta.de_dict(m.gaveta)
            self.assertEqual(core.motivos(fx.VAO, g, catalogo.por_id(g.corredica), 220), [], m.id)

    def test_salvar_e_reler(self):
        pasta = tempfile.mkdtemp()
        m = modelos.salvar(pasta, "Minha gaveta Hettich", core.Gaveta(corredica='oculta_soft', lateral=16), 2)
        self.assertEqual(m.id, 'usuario:minha_gaveta_hettich')
        relido = modelos.por_id(m.id, pasta)
        self.assertEqual((relido.quantidade, relido.gaveta['lateral']), (2, 16))
        modelos.salvar(pasta, "Minha gaveta Hettich", core.Gaveta(), 1)
        self.assertEqual(len(modelos.ler_usuario(pasta)), 1)
        self.assertEqual(len(modelos.todos(pasta)), 7)


if __name__ == '__main__':
    unittest.main()
