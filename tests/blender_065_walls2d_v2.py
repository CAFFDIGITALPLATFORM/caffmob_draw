"""065 T124–T128: sessão real, despacho do modal e montagem v2 offline no Blender."""
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
PACKAGE = 'bl_ext.ensaio_065.caffmob_draw'
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
studio = import_module(PACKAGE + '.walls2d.studio')
pe = import_module(PACKAGE + '.caffmob.v2.paredes_edicao')
validar = import_module(PACKAGE + '.caffmob.v2.validacao').validar_documento
serializar = import_module(PACKAGE + '.caffmob.v2.serializacao').serializar
View2D = import_module(PACKAGE + '.canvas2d.view').View2D
addon.register()
addon.load_file_post(None)
assert not bpy.app.online_access
context = bpy.context
PASTA = ROOT / 'tests/casos_ouro_v2'
verificacoes = []


def conferir(ok, texto):
    assert ok, texto
    verificacoes.append(texto)
    print('OK ' + texto, flush=True)


def event(tipo, value='PRESS', char=''):
    return SimpleNamespace(type=tipo, value=value, unicode=char, ctrl=False, shift=False, oskey=False)


def abrir_parede(d):
    root = cena.construir_cena(context, d)
    obj = next(o for o in root.all_objects if o.get('caffmob_tipo') == 'parede')
    context.view_layer.objects.active = obj
    s = scene_v2.abrir(context)
    conferir(s.v2.selecao == json.loads(obj['caffmob_parede'])['segmentos'][0]['id'], 'Abre a parede v2 ativa')
    return s


try:
    d = json.loads((PASTA / 'obra/referencia-obra.json').read_text())['entrada']
    s = abrir_parede(d)
    antes = context.scene['caffmob_ambiente']
    s.v2.modelo('L')
    props.end()
    conferir(context.scene['caffmob_ambiente'] == antes, 'Cancelar descarta a cópia e conserva a cena')
    s = scene_v2.abrir(context)
    v = s.v2
    s.view = View2D((0, 0, 1100, 800), scale=150)
    op = SimpleNamespace(dragging=None, panning=None)

    def despachar(tipo, alvo=(0, 0), value='PRESS', char=''):
        s.cursor = (alvo[0] / 1000, alvo[1] / 1000)
        pixel = s.view.to_screen(s.cursor)
        ui.tratar(op, context, event(tipo, value, char), s, s.view, pixel)
        if op.dragging is None:
            s.checkpoint()

    v.iniciar((15000, 15000))
    for medida, seta in (('4000', 'RIGHT_ARROW'), ('3000', 'UP_ARROW'), ('4000', 'LEFT_ARROW')):
        despachar(seta)
        for char in medida:
            despachar('TEXTINPUT', char=char)
        despachar('RET')
    conferir(v.fechar(), 'Desenha com medidas digitadas e fecha exatamente no primeiro ponto')
    nova = v.paredes()[-1]
    conferir([round(t['comprimento'], 6) for t in nova['segmentos']] == [4000, 3000, 4000, 3000], 'Medidas digitadas em mm')
    # Meio da espessura, fora das linhas de borda e da cota.
    despachar('LEFTMOUSE', (17000, 14930))
    despachar('LEFTMOUSE', (17000, 14930), 'RELEASE')
    conferir(v.selecao == nova['segmentos'][0]['id'] and abs(v.divisao - 2000) < 0.001, 'Meio da parede seleciona e marca o ponto de divisão')
    context.window_manager.btm_wall_studio.comprimento = 4500
    conferir(v.trecho()[2]['comprimento'] == 4500, 'Campo do painel muda imediatamente o contrato de trabalho')
    # Arraste pelo modal; só um passo de histórico ao soltar.
    op.studio_clique = None
    delta_arrasto = max(200, 20 / s.view.scale * 1000)
    despachar('LEFTMOUSE', (17000, 14930))
    despachar('MOUSEMOVE', (17000, 14930 + delta_arrasto))
    despachar('LEFTMOUSE', (17000, 14930 + delta_arrasto), 'RELEASE')
    conferir(abs(v.paredes()[-1]['origem']['y'] - (15000 + delta_arrasto)) < 0.01, 'Arrasta aresta sem deslocar os demais cantos')
    v.divisao = 2000
    conferir(v.dividir(), 'Divide no ponto clicado')
    v.ponto = (nova['id'], 1)
    conferir(v.excluir(), 'Exclui ponto unindo os trechos')
    v.ponto = None
    v.selecao = v.paredes()[-1]['segmentos'][0]['id']
    conferir(v.abertura_nova('DOOR'), 'Insere porta pelo painel da parede')
    porta = v.abertura
    conferir(v.tentar(pe.editar_abertura(v.documento, porta, dict(posicao=300))), 'Move porta ao longo da parede')
    conferir(v.abertura_nova('WINDOW'), 'Insere janela pelo painel da parede')
    janela = v.abertura
    conferir(v.tentar(pe.editar_abertura(v.documento, janela, dict(posicao=2500))), 'Move janela ao longo da parede')
    campos = context.window_manager.btm_wall_studio
    campos.altura = 2800
    campos.altura_final = 2750
    campos.afastamento = 100
    campos.material_interno = v.documento['materiais'][0]['id']
    campos.material_externo = v.documento['materiais'][-1]['id']
    conferir(v.trecho()[2]['material_interno_id'] == v.documento['materiais'][0]['id'], 'Painel aplica material por face no contrato')
    conferir(v.trecho()[2]['afastamento'] == 100 and v.trecho()[2]['pe_direito_inicial'] == 2800, 'Painel aplica alturas e afastamento em mm')
    bpy.ops.caffmob.wall_studio_action(acao='ocultar')
    conferir(v.trecho()[2]['estado'] == 'oculto', 'Ocultar mantém o trecho e seus vãos')
    bpy.ops.caffmob.wall_studio_action(acao='ocultar')
    campos.arco = 150
    conferir(v.trecho()[2]['flecha'] == 150, 'Arco editável sem conversão para Home Builder')
    s.checkpoint()
    final = copy.deepcopy(v.documento)
    conferir(s.undo() and s.redo() and v.documento == final, 'Desfaz e refaz o documento integral')
    conferir(context.scene['caffmob_ambiente'] == antes, 'Nada chega à cena antes de Aplicar')
    # Desenho GPU é ensaiado pelo mesmo apresentador, substituindo só as primitivas GPU.
    classico = import_module(PACKAGE + '.walls2d.classico_v2')
    with patch.object(classico, 'preencher'), patch.object(classico.draw, 'begin', return_value=None), patch.object(classico.draw, 'end'), \
         patch.object(classico.draw, 'outline'), patch.object(classico.draw, 'lines') as linhas, patch.object(classico.draw, 'rect'), \
         patch.object(classico.draw, 'text'), patch.object(classico.draw, 'text_width', return_value=50):
        classico.desenhar(SimpleNamespace(region=SimpleNamespace(width=1100, height=800), window_manager=context.window_manager), s, s.view)
        pontos_desenhados = sum(len(c.args[1]) for c in linhas.call_args_list)
        cor_do_vao = editor.COLORS['node']
        conferir(pontos_desenhados > 80 and any(c.args[2] == cor_do_vao for c in linhas.call_args_list),
                 'Editor clássico desenha paredes, vãos, folha e arco da porta')
    root = scene_v2.aplicar(context, s)
    conferir(not validar(v.documento), 'Contrato final passa pela validação v2')
    conferir(context.scene['caffmob_ambiente'] == serializar(v.documento), 'Aplicar grava o contrato atualizado na cena')
    obj = next(o for o in root.all_objects if o.get('caffmob_id') == nova['id'])
    conferir(json.loads(obj['caffmob_parede']) == json.loads(serializar(v.paredes()[-1])), 'Objeto guarda a parede atualizada')
    conferir(obj.type == 'MESH' and len(obj.data.vertices) > 20, 'Montagem v2 regenera malha com os vãos')
    conferir(not any(o.get('IS_WALL_BP') for o in context.scene.objects), 'Nenhuma parede Home Builder criada')
    props.end()
    # Oráculos reais TS: usa a sessão para aceitar ou recusar, conferindo o resultado completo.
    sys.path.insert(0, str(ROOT / 'tests'))
    # Os imports do helper puro usam o pacote sem prefixo; redireciona apenas o núcleo.
    for nome in ('caffmob_draw', 'caffmob_draw.caffmob', 'caffmob_draw.caffmob.v2', 'caffmob_draw.caffmob.v2.paredes_edicao'):
        sys.modules[nome] = sys.modules[PACKAGE + nome[len('caffmob_draw'):]]
    from test_paredes_edicao_v2 import casos, executar, maior_diferenca
    for arquivo, c in casos():
        r = executar(copy.deepcopy(c['entrada']), c)
        conferir(maior_diferenca(r, c['esperado']) <= 0.1, 'Caso TS ' + arquivo.stem)
    # Falha de montagem mantém a cena anterior; edição concorrente também é recusada.
    s = scene_v2.abrir(context)
    antes = context.scene['caffmob_ambiente']
    with patch.object(cena, '_obra', side_effect=RuntimeError('falha deliberada')):
        try:
            scene_v2.aplicar(context, s)
            raise AssertionError('Montagem deveria falhar')
        except RuntimeError:
            pass
    conferir(context.scene['caffmob_ambiente'] == antes, 'Erro de montagem conserva a cena e o contrato anteriores')
    props.end()
    vazio = copy.deepcopy(d)
    vazio.update(paredes=[], aberturas=[], modulos=[], vinculos=[])
    cena.construir_cena(context, vazio)
    context.scene['caffmob_pavimento_ativo'] = vazio['pavimentos'][1]['id']
    s = scene_v2.abrir(context)
    conferir(not s.v2.paredes() and s.v2.pavimento_id == vazio['pavimentos'][1]['id'], 'Cena v2 sem parede abre prancheta vazia no pavimento ativo')
    s.v2.modelo('L')
    conferir(s.v2.paredes()[0]['pavimento_id'] == vazio['pavimentos'][1]['id'], 'Parede nova pertence ao pavimento ativo')
    props.end()
    del context.scene['caffmob_ambiente']
    conferir(scene_v2.abrir(context) is None, 'Projeto não MOBI mantém entrada do editor Home Builder')
    antigo = props.start(editor.model.WallPlan(), context.scene.name)
    conferir(antigo.v2 is None, 'Sessão legada não é convertida para v2')
    props.end()
finally:
    destino = os.environ.get('CAFFMOB_RESULTADO') or (ROOT.parent / 'feature/blender-065-walls2d-v2-r21.json'
                                                      if (ROOT.parent / 'feature').is_dir() else None)
    if destino:
        Path(destino).write_text(json.dumps(dict(verificacoes=verificacoes), ensure_ascii=False, indent=2) + '\n')
