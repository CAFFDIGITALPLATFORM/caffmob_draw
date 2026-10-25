"""065 T128 e T133: seleção múltipla na prancheta e painel da parede desenhado como o Studio, sem bpy.

Os casos 1 a 11 de `feature/selecao-multipla.md` passam aqui pelo mesmo despacho de eventos do modal.
"""
import copy
import json
from pathlib import Path
import unittest
from types import SimpleNamespace
import _bootstrap  # noqa: F401
from caffmob_draw.walls2d.studio import Prancheta, pontos
from caffmob_draw.walls2d import studio_interacao as interacao
from caffmob_draw.walls2d import studio_painel as sp
from caffmob_draw.canvas2d.view import View2D
from caffmob_draw.caffmob.v2.validacao import validar_documento
from test_walls2d_studio import documento
from test_paredes_edicao_v2 import casos

PASTA = Path(__file__).resolve().parent / 'casos_ouro_v2'


def medir(texto, tamanho, peso=400):
    return len(texto) * tamanho * 0.55


class Sessao(SimpleNamespace):
    def undo(self):
        return self.v2.historico(-1)

    def redo(self):
        return self.v2.historico(1)


class Base(unittest.TestCase):
    def preparar(self, d=None, pavimento=None):
        self.v = Prancheta(d or documento(), pavimento)
        self.view = View2D((0, 0, 1000, 800), scale=100)
        self.s = Sessao(v2=self.v, cursor=(0, 0), error='', request=None, view=self.view)
        self.op = SimpleNamespace(dragging=None)

    def evento(self, tipo, alvo=(0, 0), valor='PRESS', texto='', **mods):
        self.s.cursor = tuple(q / 1000 for q in alvo)
        pixel = self.view.to_screen(self.s.cursor)
        e = SimpleNamespace(type=tipo, value=valor, unicode=texto, ctrl=mods.get('ctrl', False),
                            shift=mods.get('shift', False), is_tablet=mods.get('toque', False))
        r = interacao.tratar(self.op, e, self.s, self.view, pixel)
        if self.op.dragging is None:
            self.v.checkpoint()
        return r

    def arrastar(self, a, b, **mods):
        self.evento('LEFTMOUSE', a, **mods)
        meio = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        self.evento('MOUSEMOVE', meio, **mods)
        self.evento('MOUSEMOVE', b, **mods)
        self.evento('LEFTMOUSE', b, 'RELEASE', **mods)

    def ids(self):
        return [s['id'] for p in self.v.paredes() for s in p['segmentos']]


class SelecaoMultiplaTest(Base):
    """Retângulo 4000 × 3000 a partir da origem: 0 embaixo, 1 à direita, 2 em cima, 3 à esquerda."""

    def setUp(self):
        self.preparar()
        self.v.modelo('retangulo')
        self.evento('ESC')

    def test_01_retangulo_dentro(self):
        self.arrastar((-300, -300), (4300, 200))
        self.assertEqual(self.v.selecionadas, [self.ids()[0]])
        self.assertIsNone(self.v.retangulo)

    def test_02_retangulo_que_toca(self):
        self.arrastar((2000, 600), (1000, -100))
        self.assertEqual(self.v.selecionadas, [self.ids()[0]])
        self.arrastar((4300, 3300), (3900, -300))
        self.assertEqual(set(self.v.selecionadas), set(self.ids()[:3]))

    def test_03_shift_retangulo_soma(self):
        self.arrastar((-300, -300), (4300, 200))
        self.arrastar((4300, 1600), (3900, 1400), shift=True)
        self.assertEqual(self.v.selecionadas, self.ids()[:2])
        self.arrastar((-300, 2800), (4300, 3300))
        self.assertEqual(self.v.selecionadas, [self.ids()[2]])

    def test_04_shift_e_ctrl_clique_alternam(self):
        self.evento('LEFTMOUSE', (2000, -70), shift=True)
        self.evento('LEFTMOUSE', (4070, 1500), ctrl=True)
        self.assertEqual(self.v.selecionadas, self.ids()[:2])
        self.evento('LEFTMOUSE', (4070, 1500), shift=True)
        self.assertEqual(self.v.selecionadas, [self.ids()[0]])

    def test_05_todas_e_A_so_no_pavimento_atual(self):
        d = copy.deepcopy(casos('fundir-dois-pavimentos-relacoes')[0][1]['entrada'])
        cima = max(d['pavimentos'], key=lambda p: p['ordem'])['id']
        self.preparar(d, cima)
        self.evento('A')
        proprios = [s['id'] for p in d['paredes'] if p['pavimento_id'] == cima for s in p['segmentos']]
        self.assertEqual(self.v.selecionadas, proprios)
        self.evento('ESC')
        sp.executar(self.s, 'todas')
        self.assertEqual(self.v.selecionadas, proprios)
        self.assertEqual(self.v.anuncio, f'{len(proprios)} paredes selecionadas')

    def test_06_esc_e_clique_no_vazio_limpam(self):
        self.evento('A')
        self.evento('ESC')
        self.assertEqual(self.v.selecionadas, [])
        self.evento('A')
        self.evento('LEFTMOUSE', (2000, 1500))
        self.evento('LEFTMOUSE', (2002, 1500), 'RELEASE')
        self.assertEqual(self.v.selecionadas, [])

    def test_07_vista_pelo_meio_e_espaco_e_nao_pelo_esquerdo(self):
        centro = tuple(self.view.center)
        self.arrastar((2000, 1500), (2500, 1800))
        self.assertEqual(tuple(self.view.center), centro)
        self.evento('MIDDLEMOUSE', (2000, 1500))
        self.evento('MOUSEMOVE', (2500, 1500))
        self.evento('MIDDLEMOUSE', (2500, 1500), 'RELEASE')
        self.assertNotEqual(tuple(self.view.center), centro)
        centro = tuple(self.view.center)
        self.evento('SPACE')
        self.evento('LEFTMOUSE', (2000, 1500))
        self.evento('MOUSEMOVE', (2000, 2000))
        self.evento('LEFTMOUSE', (2000, 2000), 'RELEASE')
        self.evento('SPACE', valor='RELEASE')
        self.assertNotEqual(tuple(self.view.center), centro)
        self.assertEqual(self.v.selecionadas, [])

    def test_08_espessura_em_lote_e_um_desfazer(self):
        self.evento('A')
        p = sp.painel_de(self.v)
        p.controles(self.v)
        p.lote['espessura'] = '200'
        passos = len(self.v._historico)
        sp.executar(self.s, 'lote_aplicar')
        self.assertTrue(all(s['espessura'] == 200 for q in self.v.paredes() for s in q['segmentos']))
        self.assertEqual(len(self.v._historico), passos + 1)
        self.assertTrue(self.s.undo())
        self.assertTrue(all(s['espessura'] == 150 for q in self.v.paredes() for s in q['segmentos']))

    def test_09_material_externo_em_lote(self):
        rico = json.loads((PASTA / 'referencia-rica.json').read_text())['entrada']
        self.v.documento['materiais'] = copy.deepcopy(rico['materiais'])
        self.v.checkpoint()
        mid = self.v.documento['materiais'][1]['id']
        self.arrastar((-300, -300), (4300, 3300))
        self.assertEqual(len(self.v.selecionadas), 4)
        p = sp.painel_de(self.v)
        c = next(c for c in p.controles(self.v) if c['id'] == 'lote.material_externo_id')
        self.assertEqual(c['valor'], '')
        self.assertEqual(c['opcoes'][0][1], 'vários')
        p.escolher(self.v, c, mid)
        self.assertTrue(p.aplicar_lote(self.v))
        self.assertTrue(all(s.get('material_externo_id') == mid for q in self.v.paredes() for s in q['segmentos']))
        self.assertTrue(all(s.get('material_interno_id') is None for q in self.v.paredes() for s in q['segmentos']))

    def test_10_excluir_tres_com_confirmacao(self):
        for x, y in ((2000, -70), (4070, 1500), (2000, 3070)):
            self.evento('LEFTMOUSE', (x, y), shift=True)
        self.evento('DEL')
        self.assertEqual(self.v.confirmacao['quantidade'], 3)
        self.assertEqual(len(self.ids()), 4)
        self.evento('ESC')
        self.assertIsNone(self.v.confirmacao)
        self.assertEqual(len(self.ids()), 4)
        self.evento('DEL')
        sp.executar(self.s, 'confirmar_exclusao')
        self.assertEqual(len(self.ids()), 1)
        self.assertEqual(self.v.selecionadas, [])
        self.assertFalse(validar_documento(self.v.documento))

    def test_11_arrastar_conjunto_mantem_ligadas(self):
        self.evento('LEFTMOUSE', (2000, -70), shift=True)
        self.evento('LEFTMOUSE', (4070, 1500), shift=True)
        passos = len(self.v._historico)
        self.evento('LEFTMOUSE', (2000, -70))
        self.assertEqual(len(self.v.selecionadas), 2)
        self.evento('MOUSEMOVE', (2300, -270))
        self.evento('MOUSEMOVE', (2500, -570))
        self.evento('LEFTMOUSE', (2500, -570), 'RELEASE')
        self.assertEqual(len(self.v._historico), passos + 1)
        p = self.v.paredes()[0]
        self.assertTrue(p['fechada'])
        ps = pontos(p)
        self.assertEqual([tuple(round(c) for c in q) for q in ps], [(500, -500), (4500, -500), (4500, 2500), (0, 3000)])
        self.assertFalse(validar_documento(self.v.documento))
        self.assertEqual(len(self.v.selecionadas), 2)

    def test_toque_segurar_corpo_liga_e_pronto_desliga(self):
        self.evento('LEFTMOUSE', (2000, -70), toque=True)
        self.assertFalse(self.v.multipla_toque)
        self.op.studio_espera['tempo'] -= 1
        self.assertTrue(interacao.segurar(self.op, self.v))
        self.assertTrue(self.v.multipla_toque)
        self.evento('LEFTMOUSE', (2000, -70), 'RELEASE', toque=True)
        self.evento('LEFTMOUSE', (4070, 1500), toque=True)
        self.evento('LEFTMOUSE', (4070, 1500), 'RELEASE', toque=True)
        self.assertEqual(self.v.selecionadas, self.ids()[:2])
        self.evento('LEFTMOUSE', (4070, 1500), toque=True)
        self.evento('LEFTMOUSE', (4070, 1500), 'RELEASE', toque=True)
        self.assertEqual(self.v.selecionadas, self.ids()[:1])
        barra = sp.barra_toque(self.v, self.view.rect, medir)
        self.assertEqual([n for n, _ in barra], ['barra', 'todas', 'pronto'])
        sp.executar(self.s, 'pronto')
        self.assertFalse(self.v.multipla_toque)
        self.assertEqual(sp.barra_toque(self.v, self.view.rect, medir), [])

    def test_toque_segurar_aresta_prende_e_um_dedo_move_a_vista(self):
        self.evento('LEFTMOUSE', (0, 0), toque=True)
        self.op.studio_espera['tempo'] -= 1
        interacao.segurar(self.op, self.v)
        self.assertTrue(self.v.aresta_presa)
        self.assertFalse(self.v.multipla_toque)
        self.evento('LEFTMOUSE', (0, 0), 'RELEASE', toque=True)
        centro = tuple(self.view.center)
        self.evento('LEFTMOUSE', (2000, 1500), toque=True)
        self.evento('MOUSEMOVE', (2500, 1500), toque=True)
        self.evento('LEFTMOUSE', (2500, 1500), 'RELEASE', toque=True)
        self.assertNotEqual(tuple(self.view.center), centro)

    def test_selecao_some_com_parede_apagada_e_desfazer(self):
        self.evento('A')
        self.evento('DEL')
        sp.executar(self.s, 'confirmar_exclusao')
        self.assertEqual(self.ids(), [])
        self.assertTrue(self.s.undo())
        self.assertEqual(len(self.ids()), 4)
        self.assertLessEqual(len(self.v.selecionadas), 1)

    def test_espaco_digitado_na_medida_continua_texto(self):
        self.evento('LEFTMOUSE', (2000, -70))
        self.evento('TEXTINPUT', texto='1')
        self.evento('SPACE', texto=' ')
        self.assertEqual(self.v.texto, '1 ')
        self.assertFalse(getattr(self.op, 'studio_espaco', False))


class PainelStudioTest(Base):
    def setUp(self):
        self.preparar()
        self.v.modelo('retangulo')
        self.p = sp.painel_de(self.v)
        self.area = (1000, 0, 330, 900)

    def tecla(self, tipo, texto='', **mods):
        e = SimpleNamespace(type=tipo, value='PRESS', unicode=texto, ctrl=mods.get('ctrl', False), shift=mods.get('shift', False))
        return self.p.tecla(self.v, e)

    def centro(self, id, parte=None):
        it = next(it for it in self.p.compor(self.v, self.area, medir) if it['c']['id'] == id)
        r = dict(it['partes']).get(parte, it['r']) if parte is not None else it['r']
        return (r[0] + r[2] / 2, r[1] + r[3] / 2)

    def test_modelo_um_e_varios(self):
        ids = [c['id'] for c in self.p.controles(self.v)]
        for id in ('comprimento', 'espessura', 'angulo', 'pad', 'lado', 'ancora', 'material_interno_id', 'material_externo_id'):
            self.assertIn(id, ids)
        self.v.editar(espessura=200)
        self.v.selecionar_todas()
        cs = {c['id']: c for c in self.p.controles(self.v)}
        self.assertEqual(cs['titulo.{} paredes selecionadas']['args'], (4,))
        self.assertEqual(cs['lote.espessura']['valor'], '')
        self.assertEqual(cs['lote.espessura']['placeholder'], 'vários')
        self.assertEqual(cs['lote.altura']['valor'], self.v.paredes()[0]['segmentos'][0]['pe_direito_inicial'])
        self.assertNotIn('comprimento', cs)

    def test_composicao_cabe_no_painel_e_usa_tokens(self):
        itens = self.p.compor(self.v, self.area, medir)
        self.assertTrue(itens)
        for it in itens:
            r = it['r']
            self.assertGreaterEqual(r[0], self.area[0] + 16)
            self.assertLessEqual(r[0] + r[2], self.area[0] + self.area[2] - 16 + 0.01)
            self.assertGreaterEqual(r[1], 0)
        campo = next(it for it in itens if it['c']['id'] == 'espessura')
        self.assertEqual(campo['r'][3], 32)
        self.assertEqual(campo['partes'][0][1][0], campo['r'][0] + 120 + 8)
        grande = next(it for it in itens if it['c']['id'] == 'comprimento')
        self.assertEqual(grande['r'][3], 44)
        pad = next(it for it in itens if it['c']['id'] == 'pad')
        self.assertEqual(len(pad['partes']), 9)
        self.assertEqual(pad['partes'][0][1][3], 34)

    def test_clique_digitacao_enter_e_tab(self):
        self.p.compor(self.v, self.area, medir)
        self.assertTrue(self.p.clicar(self.s, self.centro('espessura')))
        self.assertEqual(self.p.foco, 'espessura')
        self.assertTrue(self.p.marcado)
        for letra in '220':
            self.tecla('NUMPAD_' + letra, letra)
        self.assertEqual(self.p.texto, '220')
        self.tecla('RET')
        self.assertIsNone(self.p.foco)
        self.assertEqual(self.v.trecho()[2]['espessura'], 220)
        self.tecla('TAB')
        primeiro = self.p.foco
        self.tecla('TAB')
        self.assertNotEqual(self.p.foco, primeiro)
        self.tecla('TAB', shift=True)
        self.assertEqual(self.p.foco, primeiro)
        self.tecla('ESC')
        self.assertIsNone(self.p.foco)

    def test_valor_recusado_fica_no_campo_com_erro(self):
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('espessura'))
        self.tecla('ZERO', '0')
        self.tecla('RET')
        self.assertEqual(self.p.foco, 'espessura')
        self.assertTrue(self.p.erro)
        self.assertEqual(self.v.trecho()[2]['espessura'], 150)

    def test_clique_fora_grava_como_blur(self):
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('comprimento'))
        self.tecla('BACK_SPACE')
        for letra in '3500':
            self.tecla('X', letra)
        self.p.clicar(self.s, (1005, 450))
        self.assertIsNone(self.p.foco)
        self.assertAlmostEqual(self.v.trecho()[2]['comprimento'], 3500)

    def test_segmentado_pad_e_lista(self):
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('lado', 'eixo'))
        self.assertEqual(self.v.lado, 'eixo')
        self.p.clicar(self.s, self.centro('pad', 90))
        self.assertEqual(round(self.v.trecho()[2]['angulo_absoluto']), 90)
        rico = json.loads((PASTA / 'referencia-rica.json').read_text())['entrada']
        self.v.documento['materiais'] = copy.deepcopy(rico['materiais'])
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('material_interno_id'))
        self.assertEqual(self.p.menu['id'], 'material_interno_id')
        self.p.compor(self.v, self.area, medir)
        valor, _, r = self.p.menu_rects[1]
        self.p.clicar(self.s, (r[0] + 4, r[1] + 4))
        self.assertEqual(self.v.trecho()[2]['material_interno_id'], valor)
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('material_interno_id'))
        self.tecla('DOWN_ARROW')
        self.assertEqual(self.v.trecho()[2]['material_interno_id'], self.v.documento['materiais'][1]['id'])

    def test_botoes_rodape_e_desabilitado(self):
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('todas'))
        self.assertEqual(len(self.v.selecionadas), 4)
        self.p.compor(self.v, self.area, medir)
        self.p.clicar(self.s, self.centro('excluir'))
        self.assertEqual(self.v.confirmacao['quantidade'], 4)
        sp.executar(self.s, 'cancelar_exclusao')
        _, r = self.p.rodape_rects[1]
        self.p.clicar(self.s, (r[0] + 2, r[1] + 2))
        self.assertEqual(self.s.request, 'cancel')
        self.v.iniciar()
        todas = next(c for c in self.p.controles(self.v) if c['id'] == 'todas')
        self.assertTrue(todas['desabilitado'])

    def test_lote_vazio_nao_muda_e_recusa_negativo(self):
        self.v.selecionar_todas()
        self.p.compor(self.v, self.area, medir)
        antes = copy.deepcopy(self.v.documento)
        self.assertTrue(self.p.aplicar_lote(self.v))
        self.assertEqual(self.v.documento, antes)
        self.p.clicar(self.s, self.centro('lote.espessura'))
        self.tecla('MINUS', '-')
        self.tecla('ONE', '1')
        self.tecla('RET')
        self.assertTrue(self.p.erro)
        self.assertEqual(self.p.lote['espessura'], 150)

    def test_rolagem_limita(self):
        self.p.mais = True
        self.p.rolar(10000)
        self.p.compor(self.v, (1000, 0, 330, 300), medir)
        self.assertLessEqual(self.p.scroll, self.p.altura_conteudo)
        self.p.rolar(-20000)
        self.p.compor(self.v, (1000, 0, 330, 300), medir)
        self.assertEqual(self.p.scroll, 0)

    def test_dialogo_e_barra_dentro_da_prancheta(self):
        d = sp.dialogo((0, 0, 1000, 800))
        for nome in ('cancelar', 'confirmar_exclusao'):
            r = d[nome]
            c = d['cartao']
            self.assertTrue(c[0] <= r[0] and r[0] + r[2] <= c[0] + c[2] and c[1] <= r[1] and r[1] + r[3] <= c[1] + c[3])

    def test_nucleo_sem_bpy(self):
        for modulo in (sp, interacao):
            self.assertNotRegex(Path(modulo.__file__).read_text(), r'(?m)^\s*(import|from)\s+(bpy|mathutils|blf|gpu)\b')


if __name__ == '__main__':
    unittest.main()
