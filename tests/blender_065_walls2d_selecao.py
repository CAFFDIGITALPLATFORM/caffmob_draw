"""065 T133 no Blender sem interface: seleção múltipla pelo modal real, no editor clássico sobre a cena v2.

Os eventos passam por `BTM_OT_WallEditorModal._handle`, o mesmo caminho do modal (perguntas, navegação e prancheta).
Casos 1 a 11 de `feature/selecao-multipla.md`; o lote vai pelo painel nativo e a exclusão em lote pela pergunta do
clássico; o desenho troca só as primitivas GPU.
"""
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import bpy

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = 'bl_ext.ensaio_065s.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
from importlib import import_module
cena = import_module(PACKAGE + '.mobi.cena_v2')
scene_v2 = import_module(PACKAGE + '.walls2d.scene_v2')
props = import_module(PACKAGE + '.walls2d.props')
editor = import_module(PACKAGE + '.walls2d.ops_editor')
ui = import_module(PACKAGE + '.walls2d.studio_ui')
sp = import_module(PACKAGE + '.walls2d.studio_painel')
classico = import_module(PACKAGE + '.walls2d.classico_v2')
interacao = import_module(PACKAGE + '.walls2d.studio_interacao')
studio = import_module(PACKAGE + '.walls2d.studio')
validar = import_module(PACKAGE + '.caffmob.v2.validacao').validar_documento
serializar = import_module(PACKAGE + '.caffmob.v2.serializacao').serializar
addon.register()
addon.load_file_post(None)
assert not bpy.app.online_access
context = bpy.context
PASTA = ROOT / 'tests/casos_ouro_v2'
verificacoes = []
tr = import_module(PACKAGE + '.data.i18n').tr
notas = {}


def conferir(ok, texto):
    assert ok, texto
    verificacoes.append(texto)
    print('OK ' + texto, flush=True)


class Layout:
    """UILayout de mentira: grava rótulos, propriedades e botões do N-panel."""
    def __init__(self, registro):
        self.r = registro
        self.enabled = self.alert = True
        self.scale_y = 1

    def label(self, text='', icon='NONE'):
        self.r.append(('label', text))

    def prop(self, dono, nome, **kw):
        self.r.append(('prop', nome, kw.get('placeholder')))

    def operator(self, idname, text='', **kw):
        op = SimpleNamespace()
        self.r.append(('op', text, kw.get('depress', False)))
        return op

    def row(self, **kw):
        return Layout(self.r)

    box = column = row

    def separator(self):
        pass


try:
    d = json.loads((PASTA / 'obra/referencia-obra.json').read_text())['entrada']
    d.update(paredes=[], aberturas=[], modulos=[], vinculos=[])
    baixo, cima = sorted(d['pavimentos'], key=lambda p: p['ordem'])
    cena.construir_cena(context, d)
    context.scene['caffmob_pavimento_ativo'] = baixo['id']
    s = scene_v2.abrir(context)
    v = s.v2
    v.pavimento_id = cima['id']
    v.modelo('L')
    v.pavimento_id = baixo['id']
    v.modelo('retangulo')
    v.selecionar_ids([])
    s.checkpoint()
    conferir([len(p['segmentos']) for p in v.paredes()] == [4] and
             any(p['pavimento_id'] == cima['id'] for p in v.documento['paredes']), 'Prancheta com retângulo embaixo e L em cima')
    ids = [t['id'] for p in v.paredes() for t in p['segmentos']]
    acima = [t['id'] for p in v.documento['paredes'] if p['pavimento_id'] == cima['id'] for t in p['segmentos']]

    # Vista com a mesma conta do modal: no clássico, os painéis são nativos e a prancheta ocupa a região toda.
    region = SimpleNamespace(width=1430, height=860)
    s.view = None
    view = editor.ensure_view(region)
    conferir(view.rect[2] == 1430 and not getattr(s, 'studio_painel_area', None),
             'Prancheta com a largura toda da região, como no editor clássico')
    op = SimpleNamespace(dragging=None, panning=None, shift=False)
    modal = editor.BTM_OT_WallEditorModal._handle

    def ev(tipo, pixel, value='PRESS', char='', **m):
        e = SimpleNamespace(type=tipo, value=value, unicode=char, ctrl=m.get('ctrl', False), shift=m.get('shift', False),
                            oskey=False, alt=False, is_tablet=m.get('toque', False))
        s.cursor = view.to_world(pixel)
        r = modal(op, context, e, s, view, pixel)
        if r and op.dragging is None:
            s.checkpoint()
        return r

    def px(q):
        pixel = view.to_screen((q[0] / 1000, q[1] / 1000))
        assert view.contains(pixel), ('fora da prancheta', q, pixel)
        return pixel

    def arrastar(a, b, **m):
        ev('LEFTMOUSE', px(a), **m)
        ev('MOUSEMOVE', px(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)), **m)
        ev('MOUSEMOVE', px(b), **m)
        ev('LEFTMOUSE', px(b), 'RELEASE', **m)

    def meio(t):
        p = next(p for p in v.paredes() if any(x['id'] == t for x in p['segmentos']))
        i = [x['id'] for x in p['segmentos']].index(t)
        g = studio.geometria_da_parede(p)[i]
        a, b = g['linha'][0], g['linha'][-1]
        c, f = g['face'][0], g['face'][-1]
        return ((a[0] + b[0] + c[0] + f[0]) / 4, (a[1] + b[1] + c[1] + f[1]) / 4)

    # 1 e 2: dentro e que toca.
    arrastar((-600, -600), (4600, 600))
    conferir(v.selecionadas == [ids[0]], 'Caso 1: retângulo da esquerda para a direita pega só a parede inteira dentro')
    arrastar((2000, 900), (1000, -600))
    conferir(v.selecionadas == [ids[0]], 'Caso 2: retângulo da direita para a esquerda pega a que ele toca')
    arrastar((4450, 3450), (3800, -450))
    conferir(set(v.selecionadas) == set(ids[:3]), 'Caso 2: tocar o canto pega as três paredes cruzadas')
    # 3: Shift soma.
    arrastar((-600, -600), (4600, 600))
    arrastar((4500, 1700), (3800, 1300), shift=True)
    conferir(v.selecionadas == ids[:2], 'Caso 3: Shift+retângulo soma à seleção existente')
    # 4: Shift+clique tira.
    ev('LEFTMOUSE', px(meio(ids[1])), shift=True)
    ev('LEFTMOUSE', px(meio(ids[1])), 'RELEASE', shift=True)
    conferir(v.selecionadas == [ids[0]], 'Caso 4: Shift+clique tira uma parede da seleção')
    ev('LEFTMOUSE', px(meio(ids[3])), ctrl=True)
    ev('LEFTMOUSE', px(meio(ids[3])), 'RELEASE', ctrl=True)
    conferir(v.selecionadas == [ids[0], ids[3]], 'Caso 4: Ctrl+clique soma uma parede')
    # 5: A e "Selecionar todas" só no pavimento atual.
    ev('A', px((2000, 1500)))
    conferir(v.selecionadas == ids and not set(acima) & set(v.selecionadas), 'Caso 5: A seleciona o pavimento atual e não o de cima')
    # 6: Esc limpa.
    ev('ESC', px((2000, 1500)))
    conferir(v.selecionadas == [], 'Caso 6: Esc limpa a seleção')
    bpy.ops.caffmob.wall_studio_action(acao='todas')
    conferir(v.selecionadas == ids, 'Caso 5: botão "Selecionar todas" do N-panel faz o mesmo')
    ev('LEFTMOUSE', px((2000, 1500)))
    ev('LEFTMOUSE', px((2000, 1500)), 'RELEASE')
    conferir(v.selecionadas == [], 'Caso 6: clique simples no vazio limpa a seleção')
    # 7: vista.
    centro = tuple(view.center)
    arrastar((1500, 1000), (2500, 2000))
    conferir(tuple(view.center) == centro, 'Caso 7: arrasto esquerdo no vazio não move a vista')
    ev('MIDDLEMOUSE', px((2000, 1500)))
    ev('MOUSEMOVE', (px((2000, 1500))[0] + 60, px((2000, 1500))[1]))
    ev('MIDDLEMOUSE', px((2000, 1500)), 'RELEASE')
    conferir(tuple(view.center) != centro, 'Caso 7: botão do meio move a vista')
    centro = tuple(view.center)
    a = px((2000, 1500))
    ev('SPACE', a)
    ev('LEFTMOUSE', a)
    ev('MOUSEMOVE', (a[0], a[1] + 50))
    ev('LEFTMOUSE', (a[0], a[1] + 50), 'RELEASE')
    ev('SPACE', a, 'RELEASE')
    conferir(tuple(view.center) != centro and v.selecionadas == [], 'Caso 7: Espaço + arrasto move a vista sem selecionar')
    view.fit(v.bounds(), margin=0.15)

    # 8: espessura em lote pelo painel nativo.
    ev('A', px((2000, 1500)))
    p = sp.painel_de(v)
    campos = context.window_manager.btm_wall_studio
    passos = v._indice
    campos.lote_espessura = '200'
    bpy.ops.caffmob.wall_studio_action(acao='lote_aplicar')
    conferir(all(t['espessura'] == 200 for q in v.paredes() for t in q['segmentos']), 'Caso 8: espessura em lote aplicada')
    conferir(v._indice == passos + 1, 'Caso 8: uma entrada só no histórico')
    conferir(s.undo() and all(t['espessura'] == 150 for q in v.paredes() for t in q['segmentos']), 'Caso 8: um Ctrl+Z desfaz todas juntas')
    conferir(s.redo() and s.undo(), 'Caso 8: refazer e desfazer de novo')
    v.selecionar_todas()
    # 9: material da face externa em lote, pelo N-panel nativo.
    mid = v.documento['materiais'][-1]['id']
    campos = context.window_manager.btm_wall_studio
    conferir(campos.lote_espessura == '150', 'N-panel lê o valor comum das selecionadas')
    v.tentar(studio.pe.editar_trecho(v.documento, ids[0], dict(ancora='inicio', lado_medida='interna', espessura=180)))
    s.checkpoint()
    v.selecionar_todas()
    conferir(campos.lote_espessura == '' and next(c for c in p.controles(v) if c['id'] == 'lote.espessura')['placeholder'] == 'vários',
             'Valores diferentes ficam vazios com a dica "vários"')
    campos.lote_material_externo = mid
    bpy.ops.caffmob.wall_studio_action(acao='lote_aplicar')
    conferir(all(t.get('material_externo_id') == mid for q in v.paredes() for t in q['segmentos']), 'Caso 9: material da face externa em lote')
    conferir([t['espessura'] for q in v.paredes() for t in q['segmentos']][:2] == [180, 150], 'Caso 9: campo vazio não muda a espessura')
    registro = []
    classico.painel_trecho(Layout(registro), context, s)
    textos = [r[1] for r in registro]
    conferir(tr('{} paredes selecionadas').format(4) in textos and ('prop', 'lote_espessura', tr('vários')) in registro,
             'Painel do trecho mostra "N paredes" e os campos do lote')
    notas['placeholder_nativo'] = 'placeholder' in bpy.types.UILayout.bl_rna.functions['prop'].parameters.keys()
    # 10: excluir três com confirmação.
    ev('ESC', px((2000, 1500)))
    for t in ids[:3]:
        ev('LEFTMOUSE', px(meio(t)), shift=True)
        ev('LEFTMOUSE', px(meio(t)), 'RELEASE', shift=True)
    ev('DEL', px((2000, 1500)))
    conferir(v.confirmacao and v.confirmacao['quantidade'] == 3 and len(v.paredes()[0]['segmentos']) == 4,
             'Caso 10: Delete pede confirmação dizendo quantas são')
    _caixa, sim, nao = editor._prompt_rects(SimpleNamespace(width=view.rect[2], height=view.rect[3] + editor.toolbar_height()))
    ev('LEFTMOUSE', (nao[0] + 5, nao[1] + 5))
    conferir(v.confirmacao is None and len(v.paredes()[0]['segmentos']) == 4, 'Caso 10: "Não" na pergunta não exclui')
    ev('DEL', px((2000, 1500)))
    ev('LEFTMOUSE', (sim[0] + 5, sim[1] + 5))
    conferir(sum(len(q['segmentos']) for q in v.paredes()) == 1 and not validar(v.documento), 'Caso 10: "Sim" na pergunta apaga as três')
    s.undo()
    conferir(sum(len(q['segmentos']) for q in v.paredes()) == 4, 'Caso 10: desfazer devolve as três')
    # Esc sem nada selecionado, com alterações: pergunta antes de descartar, como o clássico.
    v.selecionar_ids([])
    ev('ESC', px((2000, 1500)))
    conferir(s.prompt == 'discard' and s.request is None, 'Esc sem seleção pergunta antes de descartar as alterações')
    ev('LEFTMOUSE', (nao[0] + 5, nao[1] + 5))
    conferir(s.prompt is None and s.request is None, '"Não" mantém o editor aberto')
    # 11: arrastar o conjunto.
    for t in ids[:2]:
        ev('LEFTMOUSE', px(meio(t)), shift=True)
        ev('LEFTMOUSE', px(meio(t)), 'RELEASE', shift=True)
    passos = v._indice
    inicio = meio(ids[0])
    ev('LEFTMOUSE', px(inicio))
    ev('MOUSEMOVE', px((inicio[0] + 250, inicio[1] - 250)))
    ev('MOUSEMOVE', px((inicio[0] + 500, inicio[1] - 500)))
    ev('LEFTMOUSE', px((inicio[0] + 500, inicio[1] - 500)), 'RELEASE')
    q = v.paredes()[0]
    ps = [tuple(round(c) for c in x) for x in studio.pontos(q)]
    conferir(q['fechada'] and ps[3] == (0, 3000) and ps[0][0] > 0 and ps[2][0] > 4000, 'Caso 11: o conjunto se move e as paredes de fora seguem ligadas')
    conferir(v._indice == passos + 1 and not validar(v.documento), 'Caso 11: arrasto do conjunto é um passo e o contrato é válido')

    # Toque/caneta: segurar no corpo liga a seleção múltipla; o temporizador do modal dispara.
    v.selecionar_ids([])
    ev('LEFTMOUSE', px(meio(ids[2])), toque=True)
    op.studio_espera['tempo'] -= 1
    conferir(interacao.segurar(op, v) and v.multipla_toque and v.selecionadas == [ids[2]], 'Toque: segurar no corpo liga a seleção múltipla')
    ev('LEFTMOUSE', px(meio(ids[2])), 'RELEASE', toque=True)
    ev('LEFTMOUSE', px(meio(ids[3])), toque=True)
    ev('LEFTMOUSE', px(meio(ids[3])), 'RELEASE', toque=True)
    conferir(v.selecionadas == [ids[2], ids[3]], 'Toque: com a seleção ligada, cada toque soma')
    bpy.ops.caffmob.wall_studio_action(acao='pronto')
    conferir(not v.multipla_toque, 'Toque: "Pronto" desliga a seleção múltipla')

    # Desenho clássico: primitivas GPU trocadas.
    v.selecionar_todas()
    v.retangulo = dict(inicio=(0, 0), fim=(1000, 1000), pixel=(500, 500), fim_pixel=(400, 400), somar=False, base=[], moveu=True, toque=False)
    tela = SimpleNamespace(region=region, window_manager=context.window_manager)

    def desenhar():
        with patch.object(classico, 'preencher'), patch.object(classico.draw, 'begin', return_value=None), \
             patch.object(classico.draw, 'end'), patch.object(classico.draw, 'outline'), patch.object(classico.draw, 'button') as botoes, \
             patch.object(classico.draw, 'lines') as linhas, patch.object(classico.draw, 'rect') as rets, \
             patch.object(classico.draw, 'text') as textos_padrao, patch.object(classico.draw, 'text_width', return_value=50):
            classico.desenhar(tela, s, view)
        return linhas, rets, [c.args[2] for c in textos_padrao.call_args_list], [c.args[2] for c in botoes.call_args_list]

    linhas, rets, escritos, botoes = desenhar()
    conferir(rets.call_args_list[0].args[2] == editor.COLORS['background'], 'Fundo escuro do editor clássico')
    conferir(classico.DICAS['SELECT'] in escritos, 'Dica da ferramenta Selecionar/Mover')
    conferir(any(c.args[2] == editor.COLORS['selected'] for c in linhas.call_args_list), 'Selecionadas e retângulo na cor de seleção do clássico')
    conferir(sum(len(c.args[1]) for c in linhas.call_args_list) > 60, 'Paredes, seleção e barra desenhadas')
    v.retangulo = None
    v.confirmacao = dict(ids=ids[:2], quantidade=2)
    linhas, rets, escritos, botoes = desenhar()
    conferir(any(t and tr(sp.CONFIRMAR_LOTE).format(2).startswith(t) for t in escritos) and 'Sim' in botoes and 'Não' in botoes,
             'Pergunta de exclusão em lote com a contagem, Sim e Não')
    v.confirmacao = None

    # Aplicar leva o resultado à cena.
    root = scene_v2.aplicar(context, s)
    conferir(context.scene['caffmob_ambiente'] == serializar(v.documento) and not validar(v.documento), 'Aplicar grava o contrato com as edições em lote')
    props.end()
finally:
    destino = os.environ.get('CAFFMOB_RESULTADO') or (ROOT.parent / 'feature/blender-065-walls2d-selecao-r22.json'
                                                      if (ROOT.parent / 'feature').is_dir() else None)
    if destino:
        Path(destino).write_text(json.dumps(dict(verificacoes=verificacoes, notas=notas), ensure_ascii=False, indent=2) + '\n')
