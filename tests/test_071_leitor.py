"""071 (T010; RN-01, RN-03, RN-05, D-01, D-04): leitura do `.promob` sintético."""
import unittest
import zipfile
from unittest import mock

import _promob_sintetico as ps
from caffmob_draw.promob import leitor


class LeitorTest(unittest.TestCase):
    def setUp(self):
        self.pacote = leitor.abrir(ps.promob())

    def test_separador_e_bom(self):
        nomes = self.pacote.nomes()
        self.assertIn('solucao/container1/document1/document1.ambient3d', nomes)
        self.assertTrue(all('\\' not in n for n in nomes))

    def test_ambientes_e_o_maior_pre_escolhido(self):
        ambientes = self.pacote.ambientes()
        self.assertEqual([a.nome for a in ambientes], ['Cozinha teste', 'Ambiente 2'])
        self.assertGreater(ambientes[0].contagem, ambientes[1].contagem)
        self.assertEqual(self.pacote.maior_ambiente(), 0)
        self.assertEqual(self.pacote.projeto().ambiente.indice, 0)
        self.assertEqual(self.pacote.projeto(1).ambiente.nome, 'Ambiente 2')
        with self.assertRaises(leitor.PromobErro):
            self.pacote.projeto(5)

    def test_arvore_de_itens(self):
        itens = self.pacote.projeto().itens
        parede = next(i for i in itens if i.tipo == 'WALL')
        self.assertEqual(parede.alinhamento, 'Direita')
        self.assertEqual([p[:2] for p in parede.pontos], [(0, 0), (3000, 0), (3000, 2500)])
        self.assertEqual(parede.altura, 2700)
        janela = next(h for h in parede.filhos if h.id == 'Janela_07')
        self.assertEqual((janela.rotacao, janela.base), (90, (2850, 700, 1000)))
        balcao = next(i for i in itens if i.id == 'bal_600')
        self.assertEqual((balcao.largura, balcao.altura, balcao.profundidade), (600, 850, 580))
        self.assertEqual(balcao.material, None)                      # o material é só dos filhos diretos
        self.assertEqual([f.material for f in balcao.filhos], ['cin_cor_000', 'cin_cor_000', 'madeira'])
        self.assertTrue(all(f.rotacao == 0 for f in balcao.filhos))  # rotação herdada quando falta
        self.assertFalse(next(i for i in itens if i.id == 'oculto').visivel)
        externa = next(i for i in itens if i.tipo == 'ENTIDADEEXTERNA')
        self.assertTrue(externa.arquivo_3d.endswith(ps.OBJ_GUID + '.obj'))

    def test_materiais_e_cliente(self):
        materiais = self.pacote.materiais()
        self.assertEqual(materiais['reboco'].cor, (232, 226, 214))
        self.assertEqual(materiais['madeira'].textura, 'solucao/materials/MyTextures/madeira.png')
        self.assertEqual(materiais['madeira'].escala, (800, 400))
        self.assertIsNone(materiais['marmore'].textura)
        self.assertIn('marmore.jpg', materiais['marmore'].textura_do_sistema)
        self.assertEqual(self.pacote.cliente(), {'NOMECLIENTE': 'Cliente Fictício'})

    def test_licenca_nunca_e_lida(self):
        lidos = []
        original = zipfile.ZipFile.read

        def espiao(zf, nome, *args, **kwargs):
            lidos.append(getattr(nome, 'filename', nome))
            return original(zf, nome, *args, **kwargs)
        with mock.patch.object(zipfile.ZipFile, 'read', espiao):
            p = leitor.abrir(ps.promob())
            p.projeto()
            p.materiais()
            p.cliente()
        self.assertTrue(lidos)
        self.assertFalse([n for n in lidos if n.lower().endswith('promob.info')])
        with self.assertRaises(leitor.PromobErro):
            p.ler('promob.info')


if __name__ == '__main__':
    unittest.main()
