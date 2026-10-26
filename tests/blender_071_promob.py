"""071, onda A (T042; RF-01 a RF-13): importar o `.promob` sintético no Blender.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_071_promob.py

Sem janela, o timer da importação não dispara: o ensaio chama `importar` (que troca para o arquivo novo) e depois
`_montar`, que é o que o timer faria. O desfazer da importação foi provado em janela pelo protótipo T003.
Só o arquivo sintético (RN-02).
"""
import json
import os
import sys
import tempfile
import time
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _promob_sintetico as ps  # noqa: E402
from caffmob_draw.promob import complemento, ops  # noqa: E402
from caffmob_draw.selection import component_select  # noqa: E402
from caffmob_draw.target import mobi_fields, snapshot  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402

FAILURES = []
PASTA = tempfile.mkdtemp(prefix='caffmob_071_')


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def importar(dados, nome='Cozinha teste.promob', indice=None):
    caminho = ps.gravar(os.path.join(PASTA, nome), dados)
    erro = ops.importar(caminho, indice)
    if erro is None:
        if bpy.app.timers.is_registered(ops._montar):
            bpy.app.timers.unregister(ops._montar)
        ops._montar()
    return erro, caminho


def colecao():
    return next(c for c in bpy.data.collections if c.name.startswith('Promob · '))


def obj(nome):
    return next(o for o in colecao().all_objects if o.name == nome or o.name.startswith(nome + '.'))


def entradas():
    check(hasattr(bpy.types, 'CAFFMOB_FH_promob'), "arrastar .promob para a janela tem FileHandler")
    funcoes = getattr(bpy.types.TOPBAR_MT_file_import.draw, '_draw_funcs', [])
    check(ops.menu_importar in funcoes, "Arquivo › Importar tem o projeto do Promob")


def ambiente():
    bpy.ops.mesh.primitive_cube_add()
    bpy.context.active_object.name = 'Do arquivo anterior'
    erro, caminho = importar(ps.promob())
    check(erro is None, "a importação do sintético não dá erro", str(erro))
    cena = bpy.context.scene
    check('Do arquivo anterior' not in bpy.data.objects, "o projeto abre num arquivo novo")
    d = json.loads(cena['caffmob_ambiente'])
    check(len(d['paredes']) == 1 and len(d['aberturas']) == 2, "documento do MOBI com a parede e as duas aberturas")
    paredes = [o for o in cena.objects if o.get('caffmob_tipo') == 'parede']
    aberturas = [o for o in cena.objects if o.get('caffmob_tipo') == 'abertura']
    check(len(paredes) == 1 and len(aberturas) == 2, "a parede e as aberturas estão na cena")
    trechos = json.loads(paredes[0]['caffmob_parede'])['segmentos']
    check([round(s['comprimento']) for s in trechos] == [3000, 2500] and {s['espessura'] for s in trechos} == {150}
          and {s['pe_direito_inicial'] for s in trechos} == {2700}, "medidas da parede iguais às do arquivo")
    check(cena.unit_settings.length_unit == 'MILLIMETERS', "a cena fica em mm")
    balcao = obj('Balcão 600')
    check(balcao.type == 'EMPTY' and len(balcao.children) == 3, "o balcão é um grupo com as três peças")
    porta = obj('Porta')
    check(tuple(round(v, 4) for v in porta.dimensions) == (0.6, 0.018, 0.7), "a porta do balcão tem as medidas",
          str(tuple(porta.dimensions)))
    lateral = obj('Lateral direita')
    check(tuple(round(v, 4) for v in lateral.matrix_world.translation) == (1.085, 0.62, 0.0),
          "a lateral fica no canto frontal do Promob", str(tuple(lateral.matrix_world.translation)))
    check(obj('Oculto').hide_viewport, "item oculto no Promob entra oculto")
    madeira = next(m for m in bpy.data.materials if m.get('btm_promob_material') == 'madeira')
    imagens = [n.image for n in madeira.node_tree.nodes if n.type == 'TEX_IMAGE']
    check(imagens and imagens[0].packed_file is not None, "a textura do arquivo fica embutida")
    check(obj('Piso').type == 'MESH' and len(obj('Piso').data.vertices) > 8, "a laje com arco é uma malha extrudada")
    externa = obj('EntidadeExterna')
    malhas = [o for o in externa.children if o.type == 'MESH']
    from mathutils import Vector
    cantos = [o.matrix_world @ Vector(c) for o in malhas for c in o.bound_box]
    medidas = tuple(round(max(c[k] for c in cantos) - min(c[k] for c in cantos), 4) for k in range(3)) if cantos else ()
    check(medidas == (0.6, 0.4, 0.2), "a malha vinculada entra ajustada à caixa do item", str(medidas))
    check(not any(o.get('caffmob_tipo') for o in colecao().all_objects), "o complemento não leva caffmob_tipo")
    dados = complemento.lido(bpy.context)
    check(dados['arquivo'] == 'Cozinha teste.promob' and len(dados['sha256']) == 64, "a cena guarda de onde veio")
    check(dados['cliente'] == {'NOMECLIENTE': 'Cliente Fictício'} and 'FICTICIO-0000' not in cena['caffmob_promob'],
          "guarda o cliente e nunca a licença")
    check(dados['relatorio']['caixas'] == 5 and dados['relatorio']['aberturas'] == 2, "relatório da importação")
    return caminho


def painel_da_porta():
    folha = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'abertura'
                 and json.loads(o['caffmob_abertura'])['tipo'] == 'DOOR')
    for o in bpy.context.selected_objects:
        o.select_set(False)
    folha.select_set(True)
    bpy.context.view_layer.objects.active = folha
    component_select.forget()
    bpy.context.view_layer.update()
    component_select.normalize(bpy.context, bpy.context.scene)
    alvo = snapshot.ensure(bpy.context)
    check(alvo is not None and alvo.kind == r.OPENING and alvo.library == 'MOBI' and alvo.detail == 'DOOR'
          and alvo.owner_name.endswith('· trecho 1'), "a porta importada aparece no painel da 067",
          str(alvo and (alvo.kind, alvo.library, alvo.owner_name)))


def remontar_preserva_o_complemento():
    antes = len(colecao().all_objects)
    parede = next(o for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'parede')
    for o in bpy.context.selected_objects:
        o.select_set(False)
    parede.select_set(True)
    bpy.context.view_layer.objects.active = parede
    component_select.forget()
    snapshot.ensure(bpy.context)
    bpy.context.window_manager.btm_mobi.parede_altura = '2800'
    mobi_fields._tick()
    d = json.loads(bpy.context.scene['caffmob_ambiente'])
    check({s['pe_direito_inicial'] for s in d['paredes'][0]['segmentos']} == {2800}, "editar a altura da parede grava")
    check(len(colecao().all_objects) == antes, "a remontagem preserva os móveis importados")
    madeira = next(m for m in bpy.data.materials if m.get('btm_promob_material') == 'madeira')
    check(any(n.type == 'TEX_IMAGE' and n.image for n in madeira.node_tree.nodes), "e as texturas")


def salvar_e_reabrir():
    destino = os.path.join(PASTA, 'Cozinha teste.blend')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=destino, check_existing=False)
    n = len(colecao().all_objects)
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.wm.open_mainfile(filepath=destino)
    check(len(colecao().all_objects) == n and 'caffmob_ambiente' in bpy.context.scene and complemento.lido(bpy.context),
          "o .blend reabre com o ambiente, o complemento e a origem")
    imagens = [i for i in bpy.data.images if i.source == 'FILE']
    check(imagens and all(i.packed_file is not None for i in imagens), "com as texturas embutidas")


def arquivo_invalido():
    n = len(bpy.data.objects)
    mapa = {k: v for k, v in ps.entradas().items() if not k.endswith('.ambient3d')}
    erro, caminho = importar(ps.zip_de(mapa), 'sem ambiente.promob')
    check(erro == 'O arquivo não tem ambiente 3D.' and len(bpy.data.objects) == n,
          "sem ambiente: a mensagem e nenhum objeto criado", str(erro))
    try:
        bpy.ops.caffmob.promob_importar(filepath=caminho)
        motivo = ''
    except RuntimeError as exc:
        motivo = str(exc)
    check('não tem ambiente 3D' in motivo, "o operador recusa com a mesma mensagem", motivo)


def desempenho():
    inicio = time.perf_counter()
    erro, _ = importar(ps.promob_grande(300), 'grande.promob')
    duracao = time.perf_counter() - inicio
    print(f"INFO importação de 300 módulos: {duracao:.1f} s", flush=True)
    check(erro is None and duracao <= 10, "300 módulos importam em até 10 s", f"{duracao:.1f} s")


try:
    entradas()
    ambiente()
    painel_da_porta()
    remontar_preserva_o_complemento()
    salvar_e_reabrir()
    arquivo_invalido()
    desempenho()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_071_promob: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
