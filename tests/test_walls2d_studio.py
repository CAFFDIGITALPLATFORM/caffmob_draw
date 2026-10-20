"""065 T124–T128: documento, interação em mm e máquina de estados sem bpy."""
import copy
import hashlib
import json
import math
from pathlib import Path
import unittest
from types import SimpleNamespace
import _bootstrap  # noqa: F401
from caffmob_draw.walls2d.studio import Prancheta, previa, snap_ponto, cota, pontos, arredondar
from caffmob_draw.walls2d import studio_interacao as interacao
from caffmob_draw.walls2d.studio_aberturas import simbolo, projetar
from caffmob_draw.canvas2d.view import View2D
from caffmob_draw.walls2d.tokens_studio import TOKENS, SHA256
from caffmob_draw.caffmob.v2 import paredes_edicao as pe
from caffmob_draw.caffmob.v2.validacao import validar_documento
from test_paredes_edicao_v2 import casos, executar, maior_diferenca

PASTA = Path(__file__).resolve().parent / 'casos_ouro_v2'


def documento():
    d = copy.deepcopy(casos('editar-retangulo-inicio-interna')[0][1]['entrada'])
    d['paredes'], d['aberturas'], d['modulos'], d['vinculos'] = [], [], [], []
    return d


class PranchetaStudioTest(unittest.TestCase):
    def setUp(self):
        self.d = documento()
        self.v = Prancheta(self.d)

    def test_copia_e_cancelar(self):
        self.v.modelo('retangulo')
        self.assertEqual(self.d, documento())
        self.assertEqual(self.v.original, self.d)
        self.assertFalse(validar_documento(self.v.documento))

    def test_snap_angular_e_linear(self):
        p = previa((0, 0), (1024, 40), 1)
        self.assertEqual(p['angulo'], 0)
        self.assertAlmostEqual(p['comprimento'], 1020)
        self.assertEqual(arredondar(-15, 10), -10)
        self.assertEqual(previa((0, 0), (0, 0), 1)['comprimento'], 10)

    def test_snap_primeiro_tem_prioridade(self):
        p = previa((1000, 0), (5, 4), 1, (0, 0), [(8, 10)])
        self.assertEqual(p['fim'], (0, 0))
        self.assertEqual(p['retorno'], 'Primeiro ponto')
        self.assertNotEqual(previa((1000, 0), (5, 4), 1, (0, 0), comprimento=200)['retorno'], 'Primeiro ponto')

    def test_snap_alinhamento_escala_e_ortogonal(self):
        p = previa((0, 0), (1005, 802), 1, vizinhos=[(1000, 800)])
        self.assertEqual(p['fim'], (1000, 800))
        self.assertEqual(p['retorno'], 'Alinhamento X e Z')
        p = previa((0, 0), (1005, 802), 10, vizinhos=[(1000, 800)])
        self.assertNotEqual(p['fim'], (1000, 800))
        self.assertEqual(previa((0, 0), (1000, 400), 1, ortogonal=True)['angulo'], 0)

    def test_desenhar_digitado_fechar_concluir_continuar(self):
        v = self.v
        v.iniciar((0, 0))
        for comprimento, angulo in ((4000, 0), (3000, 90), (4000, 180)):
            v.direcao = angulo
            self.assertTrue(v.fixar(v.previa((600, 800), 1, comprimento)['fim']))
        self.assertTrue(v.fechar())
        self.assertFalse(v.desenhando)
        self.assertTrue(v.paredes()[0]['fechada'])
        for s, l in zip(v.paredes()[0]['segmentos'], (4000, 3000, 4000, 3000)):
            self.assertAlmostEqual(s['comprimento'], l)
        self.assertFalse(v.continuar())
        v.modelo('L')
        self.assertTrue(v.continuar())
        v.concluir()
        self.assertFalse(v.desenhando)
        self.assertFalse(validar_documento(v.documento))

    def test_meio_ponto_cota_e_divisao(self):
        v = self.v
        v.modelo('retangulo')
        p = v.paredes()[0]
        t = p['segmentos'][0]
        h = v.hit((1200, -70), 0.1)  # Dentro da espessura, longe das bordas.
        self.assertEqual(h['tipo'], 'trecho')
        v.selecionar(h)
        self.assertEqual(v.selecao, t['id'])
        self.assertAlmostEqual(v.divisao, 1200)
        self.assertEqual(v.hit((0, 0), 1)['tipo'], 'ponto')
        self.assertEqual(v.hit(cota(p, 0, 1), 1)['tipo'], 'cota')
        self.assertTrue(v.dividir())
        self.assertEqual(len(v.paredes()[0]['segmentos']), 5)
        v.ponto = (p['id'], 1)
        self.assertTrue(v.excluir())
        self.assertEqual(len(v.paredes()[0]['segmentos']), 4)

    def test_arrasto_aresta_e_vizinhos(self):
        v = self.v
        v.modelo('retangulo')
        p = v.paredes()[0]
        antes = pontos(p)
        r = pe.mover_aresta(v.documento, p['id'], 0, dict(x=0, y=200))
        self.assertTrue(v.tentar(r), r)
        depois = pontos(v.paredes()[0])
        self.assertEqual(depois[0], (0, 200))
        self.assertEqual(depois[1], (4000, 200))
        for a, b in zip(antes[2:], depois[2:]):
            self.assertLess(math.dist(a, b), 1e-8)
        self.assertEqual(snap_ponto(v.paredes()[0], 1, (4003, 203), 1), (4000, 200))

    def test_erro_nao_muda_historico(self):
        v = self.v
        v.modelo('retangulo')
        antes = copy.deepcopy(v.documento)
        self.assertFalse(v.editar(comprimento=-5))
        self.assertEqual(v.documento, antes)
        self.assertFalse(v.checkpoint())
        self.assertTrue(v.historico(-1))
        self.assertEqual(v.documento, self.d)
        self.assertTrue(v.historico(1))
        self.assertEqual(v.documento, antes)
        v.selecao = v.paredes()[0]['segmentos'][0]['id']
        v.editar(comprimento=4500)
        v.checkpoint()
        v.historico(-1)
        v.editar(comprimento=5000)
        v.checkpoint()
        self.assertFalse(v.historico(1))

    def test_porta_janela_arrasto_e_recusa(self):
        v = self.v
        v.modelo('retangulo')
        self.assertTrue(v.abertura_nova('DOOR'))
        porta = v.abertura
        self.assertTrue(v.tentar(pe.editar_abertura(v.documento, porta, dict(posicao=300))))
        self.assertTrue(v.abertura_nova('WINDOW'))
        janela = v.abertura
        self.assertEqual(v.hit((700, 0), 1)['id'], porta)
        self.assertTrue(v.tentar(pe.editar_abertura(v.documento, janela, dict(posicao=2300))))
        antes = copy.deepcopy(v.documento)
        self.assertFalse(v.tentar(pe.editar_abertura(v.documento, janela, dict(posicao=500))))
        self.assertEqual(v.documento, antes)
        v.tentar(pe.ocultar_trecho(v.documento, v.selecao))
        self.assertFalse(v.abertura_nova('DOOR'))
        self.assertEqual(v.erros[0]['codigo'], 'TRECHO_OCULTO')

    def test_materiais_e_pavimento_isolado(self):
        v = self.v
        v.modelo('retangulo')
        rico = json.loads((PASTA / 'referencia-rica.json').read_text())['entrada']
        v.documento['materiais'] = copy.deepcopy(rico['materiais'])
        mid = v.documento['materiais'][0]['id']
        self.assertTrue(v.tentar(pe.material_da_face(v.documento, v.selecao, 'interna', mid)))
        self.assertEqual(v.trecho()[2]['material_interno_id'], mid)
        self.assertTrue(v.tentar(pe.aplicar_espessura_a_todas(v.documento, v.pavimento_id, 180)))
        self.assertTrue(all(s['espessura'] == 180 for p in v.paredes() for s in p['segmentos']))

    def test_casos_ouro_na_copia(self):
        for arquivo, c in casos():
            with self.subTest(caso=arquivo.stem):
                v = Prancheta(c['entrada'])
                r = executar(v.documento, c)
                self.assertLessEqual(maior_diferenca(r, c['esperado']), 0.1)
                self.assertEqual(v.tentar(r), c['esperado']['ok'])
                self.assertEqual(v.original, c['entrada'])
                if not r['ok']:
                    self.assertEqual(v.documento, c['entrada'])

    def test_tokens_gerados(self):
        fonte = Path(__file__).resolve().parents[2] / 'caff-mobi/shared/studio/tokens.json'
        if not fonte.exists():
            self.skipTest('Fontes do MOBI só presentes na entrega da feature.')
        self.assertEqual(SHA256, hashlib.sha256(fonte.read_bytes()).hexdigest())
        self.assertEqual(TOKENS, json.loads(fonte.read_text()))

    def test_modelos_orientados_como_painel_studio(self):
        self.v.espessura = 180
        self.v.modelo('U', 4200, 2700)
        p = self.v.paredes()[0]
        self.assertEqual(p['origem'], dict(x=0, y=2700))
        self.assertEqual([s['comprimento'] for s in p['segmentos']], [2700, 4200, 2700])
        self.assertEqual([s['angulo_absoluto'] for s in p['segmentos']], [270, 0, 90])
        self.assertTrue(all(s['espessura'] == 180 for s in p['segmentos']))

    def test_ambiente_atual_usa_contorno_sem_mudar_original(self):
        d = documento()
        d['pavimentos'][0]['laje']['contorno'] = [dict(x=0, y=0), dict(x=2000, y=0), dict(x=2000, y=1000), dict(x=0, y=1000)]
        v = Prancheta(d)
        r = pe.ambiente_atual_na_prancheta(v.documento, v.original, v.pavimento_id, v.gerar_id)
        self.assertTrue(v.tentar(r), r)
        self.assertEqual([round(s['comprimento']) for s in v.paredes()[0]['segmentos']], [2000, 1000, 2000, 1000])
        self.assertTrue(v.paredes()[0]['fechada'])
        self.assertEqual(d, v.original)
        self.assertFalse(d['paredes'])

    def test_referencias_nao_sao_editaveis(self):
        d = json.loads((PASTA / 'referencia-rica.json').read_text())['entrada']
        for m in d['modulos']:
            m['camada_id'] = None
            m['visivel'] = True
        v = Prancheta(d)
        self.assertTrue(v.referencias())
        q = v.referencias()[0][0]
        self.assertEqual(q, (d['modulos'][0]['posicao']['x'], d['modulos'][0]['posicao']['y']))


class DespachoStudioTest(unittest.TestCase):
    def setUp(self):
        self.v = Prancheta(documento())
        self.s = SimpleNamespace(v2=self.v, cursor=(0, 0), error='', request=None)
        self.view = View2D((0, 0, 1000, 800), scale=100)
        self.op = SimpleNamespace(dragging=None)

    def evento(self, tipo, alvo=(0, 0), valor='PRESS', texto=''):
        self.s.cursor = tuple(q / 1000 for q in alvo)
        pixel = self.view.to_screen(self.s.cursor)
        e = SimpleNamespace(type=tipo, value=valor, unicode=texto, ctrl=False)
        r = interacao.tratar(self.op, e, self.s, self.view, pixel)
        if self.op.dragging is None:
            self.v.checkpoint()
        return r

    def test_mouse_direcao_digitacao_e_fechamento_automatico(self):
        self.v.iniciar()
        self.evento('MOUSEMOVE', (0, 1000))
        self.assertEqual(self.v.direcao, 90)
        self.evento('TEXTINPUT', texto='1')
        self.evento('TEXTINPUT', texto='0')
        self.evento('TEXTINPUT', texto='0')
        self.evento('TEXTINPUT', texto='0')
        self.evento('RET')
        self.assertAlmostEqual(self.v.inicio[1], 1000)
        for medida, seta in ((2000, 'RIGHT_ARROW'), (1000, 'DOWN_ARROW'), (2000, 'LEFT_ARROW')):
            self.evento(seta)
            self.v.texto = str(medida)
            self.evento('RET')
        self.assertFalse(self.v.desenhando)
        self.assertTrue(self.v.paredes()[0]['fechada'])

    def test_duplo_clique_divide_e_nao_arrasta(self):
        self.v.modelo('retangulo')
        self.evento('LEFTMOUSE', (1300, -70))
        self.evento('LEFTMOUSE', (1300, -70), 'RELEASE')
        self.evento('LEFTMOUSE', (1300, -70), 'DOUBLE_CLICK')
        self.assertEqual(len(self.v.paredes()[0]['segmentos']), 5)
        self.assertIsNone(self.op.dragging)
        self.assertAlmostEqual(self.v.paredes()[0]['segmentos'][0]['comprimento'], 1300)

    def test_arrasto_ponto_gera_um_passo_e_delete(self):
        self.v.modelo('retangulo')
        self.evento('LEFTMOUSE', (0, 0))
        self.evento('MOUSEMOVE', (-300, -100))
        self.evento('MOUSEMOVE', (-400, -200))
        self.assertEqual(len(self.v._historico), 2)
        self.evento('LEFTMOUSE', (-400, -200), 'RELEASE')
        self.assertEqual(len(self.v._historico), 3)
        self.evento('DEL')
        self.assertEqual(len(self.v.paredes()[0]['segmentos']), 3)

    def test_esc_conclui_depois_limpa_selecao(self):
        self.v.iniciar()
        self.v.fixar((1000, 0))
        self.evento('ESC')
        self.assertFalse(self.v.desenhando)
        self.assertIsNotNone(self.v.selecao)
        self.evento('ESC')
        self.assertIsNone(self.v.selecao)
        self.assertIsNone(self.s.request)

    def test_simbolos_do_studio(self):
        vao = dict(inicio=(0, 0), fim=(800, 0))
        porta = dict(tipo='DOOR', largura=800)
        direita = simbolo(porta, vao, 150, 'RIGHT')
        esquerda = simbolo(porta, vao, 150, 'LEFT')
        self.assertEqual(direita['linhas'][0][1], (0, 800))
        self.assertEqual(esquerda['linhas'][0][1], (0, -800))
        self.assertAlmostEqual(direita['arco'][-1][0], 800)
        janela = simbolo(dict(tipo='WINDOW'), vao, 150, 'RIGHT')
        self.assertEqual(len(janela['linhas']), 5)
        self.assertEqual(janela['linhas'][0], ((0, -37.5), (800, -37.5)))

    def test_nucleo_sem_bpy(self):
        for modulo in (interacao,):
            self.assertNotRegex(Path(modulo.__file__).read_text(), r'(?m)^\s*(import|from)\s+(bpy|mathutils)\b')

    def test_alca_ancora_e_divisao(self):
        self.v.modelo('retangulo')
        alcas = self.v.alcas(self.view.scale / 1000)
        self.evento('LEFTMOUSE', alcas['ancora'])
        self.assertEqual(self.v.ancora, 'fim')
        self.v.divisao = 2000
        self.evento('LEFTMOUSE', alcas['dividir'])
        self.assertEqual(len(self.v.paredes()[0]['segmentos']), 5)
        self.assertEqual(self.v.ponto[1], 1)

    def test_arrasto_invalido_e_escape_conservam_base(self):
        self.v.modelo('retangulo')
        antes = copy.deepcopy(self.v.documento)
        self.evento('LEFTMOUSE', (0, 0))
        self.evento('MOUSEMOVE', (-500, 0))
        self.assertNotEqual(self.v.documento, antes)
        self.evento('MOUSEMOVE', (4000, 0))  # Colapsa a primeira aresta.
        self.assertEqual(self.v.documento, antes)
        self.evento('LEFTMOUSE', (4000, 0), 'RELEASE')
        self.assertEqual(len(self.v._historico), 2)
        self.evento('LEFTMOUSE', (0, 0))
        self.evento('MOUSEMOVE', (-500, 0))
        self.evento('ESC')
        self.assertIsNone(self.op.dragging)
        self.assertEqual(self.v.documento, antes)

    def test_projecao_curva_e_abertura_snap_10mm(self):
        from caffmob_draw.caffmob.geometria import geometria_da_parede, ponto_no_arco
        self.v.modelo('retangulo')
        self.v.editar(flecha=400)
        p, i, _ = self.v.trecho()
        g = geometria_da_parede(p)[i]
        q = ponto_no_arco(g['arco'], 1234)
        self.assertAlmostEqual(projetar(g, q), 1234)
        self.v.editar(flecha=0)
        self.assertTrue(self.v.abertura_nova('DOOR'))
        a = self.v.documento['aberturas'][-1]
        self.evento('LEFTMOUSE', (a['posicao'] + 200, 0))
        self.evento('MOUSEMOVE', (a['posicao'] + 537, 0))
        self.evento('LEFTMOUSE', (a['posicao'] + 537, 0), 'RELEASE')
        self.assertEqual(self.v.documento['aberturas'][-1]['posicao'], a['posicao'] + 340)
