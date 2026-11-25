# (023 RF-02/RF-03; achados A005/A007) Núcleo puro, sem bpy.
import unittest

import _bootstrap  # noqa: F401  (põe a raiz do projeto no sys.path)
from caffmob_draw.armario_v2 import fila, selecao, validar


def peca(nome, papel, box, espessura=18.0, ferragem=None):
    return {'nome': nome, 'papel': papel, 'box': box, 'espessura': espessura, 'ferragem': ferragem}


def caixa(x0, y0, z0, x1, y1, z1):
    return ((x0, y0, z0), (x1, y1, z1))


class SelecaoPorClique023Test(unittest.TestCase):
    def test_ultima_peca_desenhada_vence(self):
        hits = [
            {'nome': 'Fundo', 'rect': (0, 0, 100, 100)},
            {'nome': 'Prateleira', 'rect': (10, 10, 50, 50)},
        ]
        self.assertEqual(selecao.peca_no_ponto(hits, 30, 30)['nome'], 'Prateleira')

    def test_ponto_fora_de_todas_as_pecas(self):
        hits = [{'nome': 'Fundo', 'rect': (0, 0, 100, 100)}]
        self.assertIsNone(selecao.peca_no_ponto(hits, 140, 40))

    def test_borda_conta_como_dentro(self):
        hits = [{'nome': 'Lateral', 'rect': (0, 0, 30, 60)}]
        self.assertEqual(selecao.peca_no_ponto(hits, 0, 60)['nome'], 'Lateral')

    def test_sem_hits(self):
        self.assertIsNone(selecao.peca_no_ponto([], 10, 10))
        self.assertIsNone(selecao.peca_no_ponto(None, 10, 10))

    def test_rotulo_da_barra(self):
        self.assertEqual(selecao.rotulo({'nome': 'Base inferior'}), 'Base inferior')
        self.assertEqual(selecao.rotulo({'papel': 'LATERAL'}), 'LATERAL')
        self.assertEqual(selecao.rotulo(None), '')


class SelecaoMultipla023Test(unittest.TestCase):
    """T020 / RN-06: clique simples, vazio limpa, Shift acumula e alterna."""

    HITS = [
        {'nome': 'Lateral esquerda', 'vista': 'FRONTAL', 'rect': (0, 0, 20, 100)},
        {'nome': 'Prateleira', 'vista': 'FRONTAL', 'rect': (20, 40, 100, 60)},
        {'nome': 'Prateleira', 'vista': 'LATERAL', 'rect': (120, 40, 200, 60)},
    ]

    def test_clique_simples_escolhe_uma(self):
        itens = selecao.aplicar_clique(self.HITS, 30, 50, atuais=[], acumular=False)
        self.assertEqual([i['nome'] for i in itens], ['Prateleira'])
        self.assertEqual(itens[0]['vista'], 'FRONTAL')

    def test_clique_no_vazio_limpa(self):
        atuais = [self.HITS[0]]
        self.assertEqual(selecao.aplicar_clique(self.HITS, 300, 300, atuais, acumular=True), [])

    def test_shift_acumula_pecas_de_vistas_diferentes(self):
        atuais = selecao.aplicar_clique(self.HITS, 5, 5, [], acumular=True)
        atuais = selecao.aplicar_clique(self.HITS, 150, 50, atuais, acumular=True)
        self.assertEqual(len(atuais), 2)
        self.assertEqual({i['vista'] for i in atuais}, {'FRONTAL', 'LATERAL'})

    def test_shift_no_mesmo_item_remove(self):
        atuais = selecao.aplicar_clique(self.HITS, 30, 50, [], acumular=True)
        atuais = selecao.aplicar_clique(self.HITS, 30, 50, atuais, acumular=True)
        self.assertEqual(atuais, [])

    def test_rotulo_do_conjunto(self):
        self.assertEqual(selecao.rotulo_conjunto([]), '')
        self.assertEqual(selecao.rotulo_conjunto([{'nome': 'Base inferior'}]), 'Base inferior')
        self.assertEqual(selecao.rotulo_conjunto([{'nome': 'A'}, {'nome': 'B'}]), '2 peças selecionadas')


class FilaDePedidos023Test(unittest.TestCase):
    """T019 / RN-02: a fila guarda, executa em ordem e isola a falha."""

    def test_executa_em_ordem(self):
        fila_pedidos = []
        feitos = []
        fila.enfileirar(fila_pedidos, lambda: feitos.append(1))
        fila.enfileirar(fila_pedidos, lambda: feitos.append(2))
        self.assertEqual(fila.processar(fila_pedidos, lambda acao: acao()), [])
        self.assertEqual(feitos, [1, 2])
        self.assertEqual(fila_pedidos, [])

    def test_falha_vira_aviso_e_a_proxima_roda(self):
        fila_pedidos = []
        feitos = []

        def quebra():
            raise ValueError('falhou')

        fila.enfileirar(fila_pedidos, quebra)
        fila.enfileirar(fila_pedidos, lambda: feitos.append('depois'))
        avisos = fila.processar(fila_pedidos, lambda acao: acao())
        self.assertEqual(avisos, ['falhou'])
        self.assertEqual(feitos, ['depois'])


class ValidacaoGeometrica023Test(unittest.TestCase):
    LARGURA = 1000.0
    ALTURA = 2400.0

    def test_armario_dentro_do_modulo_nao_tem_violacao(self):
        itens = [
            peca('Lateral esquerda', 'LATERAL', caixa(-500, -500, 0, -482, 0, 2400)),
            peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1000, 482, 0, 1018)),
        ]
        self.assertEqual(validar.violacoes(itens, self.LARGURA, self.ALTURA), [])

    def test_peca_alem_da_largura_e_geo_001(self):
        itens = [peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1000, 502, 0, 1018))]
        erros = validar.violacoes(itens, self.LARGURA, self.ALTURA)
        self.assertEqual([e['codigo'] for e in erros], ['GEO-001'])

    def test_peca_alem_da_altura_e_geo_001(self):
        itens = [peca('Lateral esquerda', 'LATERAL', caixa(-500, -500, 0, -482, 0, 2405))]
        erros = validar.violacoes(itens, self.LARGURA, self.ALTURA)
        self.assertEqual([e['codigo'] for e in erros], ['GEO-001'])

    def test_sobreposicao_de_prateleiras_e_geo_002(self):
        itens = [
            peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1000, 482, 0, 1018)),
            peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1013, 482, 0, 1031)),
        ]
        erros = validar.violacoes(itens, self.LARGURA, self.ALTURA)
        self.assertEqual([e['codigo'] for e in erros], ['GEO-002'])

    def test_sobreposicao_de_meio_milimetro_e_tolerada(self):
        itens = [
            peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1000, 482, 0, 1018)),
            peca('Prateleira', 'PRATELEIRA', caixa(-482, -500, 1017.5, 482, 0, 1035.5)),
        ]
        self.assertEqual(validar.violacoes(itens, self.LARGURA, self.ALTURA), [])

    def test_ferragem_nao_conta_como_chapa(self):
        itens = [peca('Dobradiça', 'FERRAGEM', caixa(-502, -500, 0, 0, 0, 2402), ferragem='dobradica')]
        self.assertEqual(validar.violacoes(itens, self.LARGURA, self.ALTURA), [])


if __name__ == '__main__':
    unittest.main()
