"""Fumaça no Blender da 018 (T025): a textura por UV, o veio por parte e a malha sem UV.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_018_textura_smoke.py

A parede (seis sockets e render, A–D) e o conta-gotas em três armários (G) já têm fumaça própria em
`tests/blender_018_parede_smoke.py`: repetir as duas aqui daria duas provas da mesma coisa, então este arquivo fica
com o que nenhum outro prova.

Verifica:
A. Armário com UV: a repetição que o material aplica ao UV da chapa aparece na vista — a textura de 2 repetições
   mostra células com metade da largura das de 1 repetição, e o contador lido do `Mapping` bate com o UV medido.
B. Veio 90° por parte: girar o veio de uma peça gira só ela; a outra peça fica intacta e o veio de corte de cada uma
   segue a própria intenção.
C. Malha sem UV: a textura cai na projeção de caixa e o addon avisa uma vez; na chapa com UV, não avisa.
"""

import json
import math
import os
import sys
import traceback
from pathlib import Path

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402

from caffmob_draw.armario_v2 import build, spec as spec_mod  # noqa: E402
from caffmob_draw.cutting import part_roles, part_sources  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.object_library import retexture  # noqa: E402
from caffmob_draw.texture_library import apply, grain, uv_core  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = {}
FALHAS = []


def check(nome, ok, detalhe=""):
    print(("OK   " if ok else "FALHA ") + nome, detalhe, flush=True)
    if not ok:
        FALHAS.append(nome)


def _imagem(nome, largura, pixels):
    imagem = bpy.data.images.new(nome, largura, len(pixels) // largura, alpha=True)
    imagem.pixels = [valor for cor in pixels for valor in cor]
    caminho = os.path.join(ROOT, nome + '.png')
    imagem.filepath_raw = caminho
    imagem.file_format = 'PNG'
    imagem.save()
    return caminho


def _vermelha():
    """2 × 2 vermelho: basta para provar que o material chega à face."""
    return _imagem('smoke_018_textura_vermelha', 2, [(1.0, 0.0, 0.0, 1.0)] * 4)


def _listrada():
    """2 × 1: metade vermelha, metade azul. Constante em V, então a vista mostra só a repetição em U."""
    return _imagem('smoke_018_textura_listrada', 2, [(1.0, 0.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0)])


def _armario():
    env.clean_scene()
    spec = spec_mod.Spec(lateral_esq_ativa=True, lateral_dir_ativa=True, base_inf_ativa=True, porta_ativa=True)
    pecas = build.gerar(build.criar_raiz(bpy.context.scene), spec)
    return next(o for o in pecas if o.btm_armario_parte.papel == 'PORTA'), \
        next(o for o in pecas if o.btm_armario_parte.papel == 'LATERAL')


def _camera(objeto, cena):
    """Câmera ortográfica de frente para a face maior da peça (a vista que mostra a textura)."""
    cantos = [objeto.matrix_world @ Vector(canto) for canto in objeto.bound_box]
    minimo = Vector([min(p[i] for p in cantos) for i in range(3)])
    maximo = Vector([max(p[i] for p in cantos) for i in range(3)])
    centro = (minimo + maximo) / 2.0
    tamanho = maximo - minimo
    fino = min(range(3), key=lambda i: tamanho[i])
    direcao = Vector((0.0, 0.0, 0.0))
    direcao[fino] = 1.0
    dados = bpy.data.cameras.new('smoke_textura_cam')
    dados.type = 'ORTHO'
    dados.ortho_scale = max(tamanho) * 1.05
    camera = bpy.data.objects.new('smoke_textura_cam', dados)
    cena.collection.objects.link(camera)
    camera.location = centro + direcao * (max(tamanho) * 2.0 + 0.5)
    camera.rotation_euler = (centro - camera.location).to_track_quat('-Z', 'Y').to_euler()
    cena.camera = camera
    luz_dados = bpy.data.lights.new('smoke_textura_sun', 'SUN')
    luz_dados.energy = 3.0
    luz = bpy.data.objects.new('smoke_textura_sun', luz_dados)
    cena.collection.objects.link(luz)
    luz.rotation_euler = camera.rotation_euler
    mundo = cena.world or bpy.data.worlds.new('smoke_textura_world')
    cena.world = mundo
    if mundo.node_tree is None:
        mundo.use_nodes = True
    fundo = mundo.node_tree.nodes.get('Background')
    if fundo is not None:
        fundo.inputs['Strength'].default_value = 0.1


def _faixa_render(cena, tamanho=128):
    """Letra da cor dominante (R ou B) por pixel na linha central, entre 20% e 80% da largura."""
    cena.render.engine = 'CYCLES'
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 4
    cena.cycles.use_denoising = False
    cena.render.resolution_x = cena.render.resolution_y = tamanho
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = 'PNG'
    cena.view_settings.view_transform = 'Standard'
    caminho = os.path.join(ROOT, 'smoke_018_textura_vista.png')
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    imagem = bpy.data.images.load(caminho)
    largura, altura = imagem.size
    pixels = list(imagem.pixels)
    linha = altura // 2
    faixa = []
    for x in range(int(largura * 0.2), int(largura * 0.8)):
        base = (linha * largura + x) * 4
        faixa.append('R' if pixels[base] > pixels[base + 2] else 'B')
    bpy.data.images.remove(imagem)
    if os.path.exists(caminho):
        os.remove(caminho)
    return faixa


def _celula(faixa, minimo=4):
    """Largura média entre as emendas de cor, em pixels: metade da repetição não depende de onde a emenda cai."""
    bordas = [i for i in range(1, len(faixa)) if faixa[i] != faixa[i - 1]
              and all(cor == faixa[i] for cor in faixa[i:i + minimo])]
    if len(bordas) < 2:
        return 0.0
    return round((bordas[-1] - bordas[0]) / (len(bordas) - 1), 2)


def _repeticao(material, us):
    """Repetições em U que o `Mapping` do material aplica ao UV medido da chapa."""
    no = next(n for n in material.node_tree.nodes if n.type == 'MAPPING')
    return round((max(us) - min(us)) * no.inputs['Scale'].default_value[0], 3)


def check_repeticao(caminho):
    """A. Uma repetição × duas repetições: a vista dobra as células e o `Mapping` bate com o UV."""
    porta, _lateral = _armario()
    us = [item.uv[0] for item in porta.data.uv_layers.active.data]
    largura_mm = round((max(us) - min(us)) * 1000.0, 3)
    uma = retexture.image_material(caminho, largura_mm, projection=uv_core.UV)
    duas = retexture.image_material(caminho, largura_mm / 2.0, projection=uv_core.UV)
    cena = bpy.context.scene
    common.set_cutpart_material(porta, uma)
    grain.sync(porta)
    for obj in cena.objects:
        obj.hide_render = obj is not porta and obj.type == 'MESH'
    _camera(porta, cena)
    bpy.context.view_layer.update()
    faixa_uma = _faixa_render(cena)
    common.set_cutpart_material(porta, duas)
    grain.sync(porta)
    env.settle()
    faixa_duas = _faixa_render(cena)
    celula_uma, celula_duas = _celula(faixa_uma), _celula(faixa_duas)
    razao = round(celula_uma / celula_duas, 2) if celula_duas else 0.0
    projecao = porta.data.materials[0].get(retexture.PROJECTION_PROP)
    return {'camadas_uv': [layer.name for layer in porta.data.uv_layers], 'largura_mm': largura_mm,
            'celula_px': {'uma': celula_uma, 'duas': celula_duas, 'razao': razao},
            'repeticao': {'uma': _repeticao(uma, us), 'duas': _repeticao(duas, us)},
            'projecao': projecao,
            'ok': [layer.name for layer in porta.data.uv_layers] == [uv_core.LAYER_UV]
            and celula_uma > 0 and abs(razao - 2.0) <= 0.2
            and _repeticao(uma, us) == 1.0 and _repeticao(duas, us) == 2.0 and projecao == uv_core.UV}


def check_veio_por_parte(caminho):
    """B. Gira o veio de uma peça em 90°: só ela gira, e o veio de corte das duas segue a própria intenção."""
    porta, lateral = _armario()
    material = retexture.image_material(caminho, 600.0, projection=uv_core.UV)
    for obj in (porta, lateral):
        obj.btm_armario_parte.veio = 'HORIZONTAL'       # a mesma textura e o mesmo veio nas duas peças
        common.set_cutpart_material(obj, material)
        grain.sync(obj)
    antes_porta = tuple(round(v, 6) for v in porta[grain.ATTR])
    antes_lateral = tuple(round(v, 6) for v in lateral[grain.ATTR])
    porta.btm_armario_parte.grain_angle = 90.0            # o `update` do ângulo chama `grain.sync`
    depois_porta = tuple(round(v, 6) for v in porta[grain.ATTR])
    depois_lateral = tuple(round(v, 6) for v in lateral[grain.ATTR])
    deltas = [round(b - a, 6) for a, b in zip(antes_porta, depois_porta)]
    eixo = max(range(3), key=lambda i: abs(deltas[i]))
    girou = abs(deltas[eixo] - math.radians(90.0)) < 1e-4 and all(
        abs(deltas[i]) < 1e-6 for i in range(3) if i != eixo)
    registros = {r.key: r.grain for r in part_sources.armario_v2_records(bpy.context.scene)}
    corte = {nome: part_roles.grain_direction(obj.btm_armario_parte.veio, obj.btm_armario_parte.grain_angle)
             for nome, obj in (('porta', porta), ('lateral', lateral))}
    return {'giro': {'antes': antes_porta, 'depois': depois_porta, 'eixo': eixo, 'deltas': deltas},
            'lateral_intacta': depois_lateral == antes_lateral,
            'corte': corte, 'corte_no_registro': {'porta': registros.get(porta.name),
                                                  'lateral': registros.get(lateral.name)},
            'ok': girou and depois_lateral == antes_lateral
            and corte == {'porta': 'VERTICAL', 'lateral': 'HORIZONTAL'}
            and registros.get(porta.name) == 'VERTICAL' and registros.get(lateral.name) == 'HORIZONTAL'}


def _aviso():
    """O texto do aviso, como o catálogo o entrega (T002)."""
    from caffmob_draw.data import i18n
    return i18n.load_catalog()["A malha não tem UV: a textura entra em projeção de caixa"]["pt_BR"]


def check_sem_uv(caminho):
    """C. Malha sem UV: projeção de caixa e aviso uma vez; chapa com UV não avisa."""
    from caffmob_draw.ui import save_feedback
    env.clean_scene()
    bpy.ops.mesh.primitive_plane_add(size=0.6)
    plano = bpy.context.active_object
    while plano.data.uv_layers:
        plano.data.uv_layers.remove(plano.data.uv_layers[0])
    projecao = retexture.projection_for(plano)
    avisos = []
    original = save_feedback.show
    save_feedback.show = avisos.append
    try:
        mudou = apply.apply_cached([plano], '', caminho, (600.0, 600.0))
    finally:
        save_feedback.show = original
    material = plano.data.materials[0] if plano.data.materials else None
    nos = [no.type for no in material.node_tree.nodes] if material is not None else []
    caixa = material.get(retexture.PROJECTION_PROP) if material is not None else None

    porta, _lateral = _armario()
    avisos_uv = []
    save_feedback.show = avisos_uv.append
    try:
        mudou_uv = apply.apply_cached([porta], '', caminho, (600.0, 600.0))
    finally:
        save_feedback.show = original
    return {'projecao_do_alvo': projecao, 'mudou': mudou, 'projecao_do_material': caixa, 'nos': nos,
            'avisos': avisos, 'texto': _aviso(),
            'chapa': {'projecao': retexture.projection_for(porta), 'mudou': mudou_uv, 'avisos': avisos_uv},
            'ok': projecao == uv_core.BOX and mudou == 1 and caixa == uv_core.BOX and 'TEX_COORD' in nos
            and avisos == [_aviso()] and mudou_uv == 1 and avisos_uv == []
            and retexture.projection_for(porta) == uv_core.UV}


def main():
    vermelho = _vermelha()
    listrada = _listrada()
    RESULT['blender'] = bpy.app.version_string
    for nome, funcao in (('A_repeticao_na_vista', lambda: check_repeticao(listrada)),
                         ('B_veio_por_parte', lambda: check_veio_por_parte(vermelho)),
                         ('C_sem_uv', lambda: check_sem_uv(vermelho))):
        try:
            RESULT[nome] = funcao()
        except Exception as exc:                     # noqa: BLE001 - a fumaça precisa terminar
            RESULT[nome] = {'erro': str(exc), 'trace': traceback.format_exc()}
        check(nome, bool(RESULT[nome].get('ok')), json.dumps(RESULT[nome], ensure_ascii=False, default=str))
    print('===SMOKE_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, default=str))
    print('===SMOKE_JSON_FIM===')
    for nome in ('smoke_018_textura_vermelha', 'smoke_018_textura_listrada', 'smoke_018_textura_vista'):
        caminho = os.path.join(ROOT, nome + '.png')
        if os.path.exists(caminho):
            os.remove(caminho)
    print('OK' if not FALHAS else 'FALHOU: ' + ', '.join(FALHAS))


main()
