"""071 (T012; RN-04, RN-10, D-06 a D-10, D-30): do `.promob` ao documento do CAFF MOBI v2."""
import unittest

import _promob_sintetico as ps
from caffmob_draw.caffmob import geometria
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.promob import leitor, para_v2


def converter(indice=None, extras=()):
    return para_v2.converter(leitor.abrir(ps.promob(extras)).projeto(indice))


class DocumentoTest(unittest.TestCase):
    def setUp(self):
        self.r = converter()
        self.d = self.r['documento']

    def test_documento_valido(self):
        self.assertEqual(self.r['erros'], [])
        self.assertEqual(validar_documento(self.d), [])
        self.assertEqual((self.d['origem'], self.d['unidade'], self.d['eixos']), ('blender', 'mm', 'Z_UP'))
        self.assertEqual(self.d['nome'], 'Cozinha teste')
        self.assertEqual([p['nome'] for p in self.d['pavimentos']], ['Térreo'])
        self.assertEqual(self.d['pavimentos'][0]['pe_direito'], 2700)
        # D-30: os móveis não vão para o documento (limite de 300 entidades do contrato)
        self.assertEqual((self.d['modulos'], self.d['primitivas'], self.d['itens_externos']), ([], [], []))

    def test_parede_em_l(self):
        parede, = self.d['paredes']
        self.assertEqual(parede['origem'], dict(x=0, y=0))
        self.assertFalse(parede['fechada'])
        medidas = [(s['comprimento'], s['angulo_absoluto'], s['espessura'], s['pe_direito_inicial'])
                   for s in parede['segmentos']]
        self.assertEqual(medidas, [(3000, 0, 150, 2700), (2500, 90, 150, 2700)])
        self.assertEqual([s['angulo_relativo'] for s in parede['segmentos']], [0, 90])

    def test_lado_da_espessura_pelo_alinhamento(self):
        """Teste de ouro (D-06): "Direita" põe a espessura à esquerda do percurso, como nos projetos do titular."""
        parede, = self.d['paredes']
        self.assertEqual({s['sentido'] for s in parede['segmentos']}, {'LEFT'})
        trecho = geometria.geometria_da_parede(parede)[0]
        self.assertEqual(trecho['linha'][0], (0, 0))
        self.assertGreater(trecho['face'][0][1], 0)          # a face externa fica em +Y: à esquerda de +X
        fechada = converter(1)['documento']['paredes'][0]
        self.assertTrue(fechada['fechada'])
        self.assertEqual(len(fechada['segmentos']), 4)
        self.assertEqual({s['sentido'] for s in fechada['segmentos']}, {'RIGHT'})   # "Esquerda"

    def test_aberturas(self):
        porta, janela = sorted(self.d['aberturas'], key=lambda a: a['tipo'])
        trechos = [s['id'] for s in self.d['paredes'][0]['segmentos']]
        self.assertEqual((porta['tipo'], porta['segmento_id'], porta['posicao'], porta['largura'], porta['altura'],
                          porta['peitoril']), ('DOOR', trechos[0], 1000, 800, 2100, 0))
        self.assertEqual((janela['tipo'], janela['segmento_id'], janela['posicao'], janela['largura'],
                          janela['altura'], janela['peitoril']), ('WINDOW', trechos[1], 700, 1200, 1000, 1000))

    def test_abertura_sem_parede_vira_caixa(self):
        solta = ps._item('MODULO', 'Porta_99', base=(9000, 9000, 0), dim=(800, 2100, 150), nome='Porta longe',
                         camada='Decore-Aberturas')
        mapa = ps.entradas()
        chave = 'solucao\\container1\\document1\\document1.ambient3d'
        mapa[chave] = mapa[chave].replace('</INFORMACOESCOLECAO></INFORMACOES><INFORMACOES ID="bal_600"',
                                          solta + '</INFORMACOESCOLECAO></INFORMACOES><INFORMACOES ID="bal_600"', 1)
        r = para_v2.converter(leitor.abrir(ps.zip_de(mapa)).projeto())
        self.assertEqual(len(r['documento']['aberturas']), 2)
        motivos = [i['motivo'] for i in r['relatorio']['ignorados'] if i['item'] == 'Porta longe']
        self.assertEqual(len(motivos), 1)
        self.assertIn('entrou como caixa', motivos[0])
        self.assertIn('Porta longe', [n['nome'] for n in r['complemento']['moveis']])

    def test_porta_que_virou_abertura_nao_desenha_caixa(self):
        nomes = []

        def todos(nos):
            for n in nos:
                nomes.append(n['nome'])
                todos(n['filhos'])
        todos(self.r['complemento']['moveis'])
        self.assertNotIn('Porta Externa', nomes)
        self.assertNotIn('Folha', nomes)
        self.assertIn('Revestimento', nomes)          # hospedado que não é abertura fica como móvel

    def test_materiais_de_cor(self):
        parede, = self.d['paredes']
        material, = self.d['materiais']
        self.assertEqual(parede['material_id'], material['id'])
        self.assertEqual((material['tipo'], material['cor'], material['nome']), ('cor', '#e8e2d6', 'Reboco'))

    def test_limites_do_contrato(self):
        r = converter(extras=[ps._item('MODULO', 'nome_longo', base=(0, 3000, 0), dim=(100, 100, 100),
                                       nome='x' * 400)])
        nomes = [n['nome'] for n in r['complemento']['moveis']]
        self.assertTrue(any(len(n) == 160 for n in nomes))
        alta = ps._parede([(0, 0, 150), (1000, 0, 150), (1010, 0, 150), (2000, 0, 150)], 9000, id_='ALTA')
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([alta])
        r = para_v2.converter(leitor.abrir(ps.zip_de(mapa)).projeto(1))
        self.assertEqual(r['erros'], [])
        segmentos = r['documento']['paredes'][0]['segmentos']
        self.assertEqual({s['pe_direito_inicial'] for s in segmentos}, {6000})
        self.assertTrue(all(s['comprimento'] >= 50 for s in segmentos))
        self.assertTrue(r['relatorio']['avisos'])

    def test_relatorio(self):
        rel = self.r['relatorio']
        self.assertEqual((rel['paredes'], rel['aberturas'], rel['lajes'], rel['malhas']), (1, 2, 1, 1))
        motivos = {i['item']: i['motivo'] for i in rel['ignorados']}
        self.assertEqual(motivos['Sem medida'], 'sem dimensões')
        self.assertEqual(motivos['luz'], 'luz')
        self.assertEqual(motivos['teto'], 'forro')
        self.assertEqual(self.r['cliente'], {'NOMECLIENTE': 'Cliente Fictício'})


class MacrosTest(unittest.TestCase):
    def test_macros_de_medida(self):
        item = leitor.Item('MODULO', 'x', 'Balcão $W$ x $H$ #COR# fim', '', True, (0, 0, 0), 0, 600, 850, 580)
        self.assertEqual(para_v2.resolver_macros(item.nome, item), 'Balcão 600 x 850 fim')


if __name__ == '__main__':
    unittest.main()
