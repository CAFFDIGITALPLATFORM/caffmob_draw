"""Fumaça no Blender da 018 (T010, T012): UV em metros do armário e as três fontes de textura.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_018_uv_smoke.py

Verifica:
A. `armario_v2.build._malha` cria `UVMap` em metros (0,6 × 0,4 m na chapa de 600 × 400 mm).
B. Projeção `UV` respeita o layer e reage à edição de UV (render).
C. Projeção `ATTRIBUTE_UV` mostra a textura na peça com `GeoNodeCutpart`, que não tem layer de UV.
D. Projeção `BOX` continua funcionando em malha sem UV.
"""

import json
import os
import sys
import traceback

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUTPART = os.path.join(ROOT, 'caffmob_draw', 'geometry_nodes', 'GeoNodeCutpart.blend')
RESULT = {}


def _image():
    imagem = bpy.data.images.new('smoke_tex', 2, 2, alpha=True)
    vermelho, verde, azul, branco = (1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)
    imagem.pixels = list(vermelho) + list(verde) + list(azul) + list(branco)   # 2×2, linha de baixo primeiro
    caminho = os.path.join(ROOT, 'smoke_018_tex.png')
    imagem.filepath_raw = caminho
    imagem.file_format = 'PNG'
    imagem.save()
    return caminho


def _camera(nome='cam', z=2.0, ortho=None):
    dados = bpy.data.cameras.new(nome)
    if ortho:
        dados.type = 'ORTHO'
        dados.ortho_scale = ortho
    objeto = bpy.data.objects.new(nome, dados)
    bpy.context.scene.collection.objects.link(objeto)
    objeto.location = (0.0, 0.0, z)
    bpy.context.scene.camera = objeto
    return objeto


def _luz():
    dados = bpy.data.lights.new('luz', 'SUN')
    objeto = bpy.data.objects.new('luz', dados)
    bpy.context.scene.collection.objects.link(objeto)
    objeto.location = (0.0, 0.0, 3.0)
    return objeto


def _render(nome='smoke.png', tamanho=16):
    cena = bpy.context.scene
    cena.render.engine = 'CYCLES'
    cena.cycles.device = 'CPU'
    cena.cycles.samples = 1
    cena.cycles.use_denoising = False
    cena.render.resolution_x = cena.render.resolution_y = tamanho
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = 'PNG'
    caminho = os.path.join(ROOT, nome)
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    imagem = bpy.data.images.load(caminho)
    largura, altura = imagem.size
    pixels = list(imagem.pixels)

    def amostra(x, y):
        base = (y * largura + x) * 4
        return tuple(round(v, 2) for v in pixels[base:base + 3])

    grade = [amostra(x, y) for x in range(1, largura, max(1, largura // 4))
             for y in range(1, altura, max(1, altura // 4))]
    bpy.data.images.remove(imagem)
    return {'esquerda': amostra(int(largura * 0.3), altura // 2),
            'direita': amostra(int(largura * 0.7), altura // 2),
            'cores': len(set(grade)), 'grade': grade}


def _plano(largura, altura, com_uv=True):
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    objeto = bpy.context.active_object
    objeto.scale = (largura, altura, 1.0)
    if com_uv:
        camada = objeto.data.uv_layers[0] if objeto.data.uv_layers else objeto.data.uv_layers.new(name='UVMap')
        camada.name = 'UVMap'
    return objeto


def _material(projecao, tamanho_mm, caminho):
    from caffmob_draw.object_library import retexture
    return retexture.image_material(caminho, tamanho_mm, projection=projecao)


def check_build_uv():
    from caffmob_draw.armario_v2 import build
    malha = build._malha('smoke_chapa', ((0.0, 0.0, 0.0), (600.0, 400.0, 18.0)))
    camadas = [layer.name for layer in malha.uv_layers]
    us = [item.uv[0] for item in malha.uv_layers.active.data]
    vs = [item.uv[1] for item in malha.uv_layers.active.data]
    return {'camadas': camadas, 'u_min': round(min(us), 4), 'u_max': round(max(us), 4),
            'v_min': round(min(vs), 4), 'v_max': round(max(vs), 4),
            'ok': camadas == ['UVMap'] and abs(max(us) - 0.6) < 1e-4 and abs(max(vs) - 0.4) < 1e-4}


def check_uv_projection(caminho):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objeto = _plano(0.6, 0.4)
    material = _material('UV', 600.0, caminho)
    objeto.data.materials.append(material)
    _camera(ortho=0.8)
    _luz()
    antes = _render('smoke_uv_antes.png')
    camada = objeto.data.uv_layers['UVMap']
    for item in camada.data:
        item.uv = (1.0 - item.uv[0], item.uv[1])
    depois = _render('smoke_uv_depois.png')
    nos = [node.type for node in material.node_tree.nodes]
    return {'no_uvmap': 'UVMAP' in nos, 'projecao_material': material.get('btm_texture_projection'),
            'antes': antes, 'depois': depois,
            'ok': 'UVMAP' in nos and antes['esquerda'] != depois['esquerda']}


def check_attribute_projection(caminho):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from caffmob_draw import compat
    antes = set(bpy.data.node_groups)
    with bpy.data.libraries.load(CUTPART, link=False) as (origem, destino):
        destino.node_groups = list(origem.node_groups)
    grupos = [g for g in bpy.data.node_groups if g not in antes]
    grupo = next(g for g in grupos if g.name.split('.')[0] == 'GeoNodeCutpart')

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    objeto = bpy.context.active_object
    while objeto.data.uv_layers:                        # caso real: peça de biblioteca sem layer
        objeto.data.uv_layers.remove(objeto.data.uv_layers[0])
    modificador = objeto.modifiers.new('Cutpart', 'NODES')
    modificador.node_group = grupo
    for nome, valor in (('Length', 1.0), ('Width', 0.6), ('Thickness', 0.018)):
        compat.try_set_gn_input(modificador, nome, valor)
    material = _material('ATTRIBUTE_UV', 1000.0, caminho)
    objeto.data.materials.append(material)
    bpy.context.view_layer.update()

    avaliado = objeto.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    sem_layer = len(avaliado.uv_layers) == 0
    objeto.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()

    _camera(ortho=1.2)
    _luz()
    render = _render('smoke_attr.png', 24)
    nos = [node.type for node in material.node_tree.nodes]
    atributo = next((node for node in material.node_tree.nodes if node.type == 'ATTRIBUTE'), None)
    return {'sem_layer_de_uv': sem_layer, 'no_attribute': 'ATTRIBUTE' in nos,
            'atributo': getattr(atributo, 'attribute_name', ''),
            'projecao_material': material.get('btm_texture_projection'),
            'cores': render['cores'], 'ok': sem_layer and 'ATTRIBUTE' in nos and render['cores'] >= 2}


def check_box_projection(caminho):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    objeto = _plano(0.6, 0.4, com_uv=False)
    material = _material('BOX', 600.0, caminho)
    objeto.data.materials.append(material)
    _camera(ortho=1.0)
    _luz()
    render = _render('smoke_box.png')
    nos = [node.type for node in material.node_tree.nodes]
    return {'no_texcoord': 'TEX_COORD' in nos, 'projecao_material': material.get('btm_texture_projection'),
            'cores': render['cores'], 'ok': 'TEX_COORD' in nos and render['cores'] >= 2}


def main():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    caminho = _image()
    RESULT['blender'] = bpy.app.version_string
    for nome, funcao in (('build_uv', lambda: check_build_uv()),
                         ('uv', lambda: check_uv_projection(caminho)),
                         ('attribute_uv', lambda: check_attribute_projection(caminho)),
                         ('box', lambda: check_box_projection(caminho))):
        try:
            RESULT[nome] = funcao()
        except Exception as exc:                        # noqa: BLE001 - a fumaça precisa terminar
            RESULT[nome] = {'erro': str(exc), 'trace': traceback.format_exc()}
    print('===SMOKE_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, indent=2))
    print('===SMOKE_JSON_FIM===')
    for nome in ('smoke_uv_antes.png', 'smoke_uv_depois.png', 'smoke_attr.png', 'smoke_box.png', 'smoke_018_tex.png'):
        arquivo = os.path.join(ROOT, nome)
        if os.path.exists(arquivo):
            os.remove(arquivo)
    print('OK' if all(v.get('ok', True) for v in RESULT.values() if isinstance(v, dict)) else 'FALHOU')


main()
