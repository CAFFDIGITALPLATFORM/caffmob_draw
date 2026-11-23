"""Probe headless do T001 da 018 (Textura por UV, veio e conta-gotas).

Roda no Blender 5.2 em background e imprime JSON entre marcadores:

    blender --background --factory-startup --python tests/blender_018_probe.py

Verificações:
1. O node group GeoNodeCutpart gera UV próprio?
2. Os seis sockets de material existem no node group de parede?
3. ShaderNodeUVMap com layer explícito respeita o layer e muda com a edição de UV?
4. Custo de grain.sync em 40 peças.
"""

import json
import os
import sys
import time
import traceback

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEOMETRY_NODES = os.path.join(ROOT, 'caffmob_draw', 'geometry_nodes')
RESULT = {}
UV_TOKENS = ('UV', 'Uv', 'uv')


def _load_group(blend_name):
    """Carrega os node groups do .blend sem abrir o arquivo inteiro."""
    path = os.path.join(GEOMETRY_NODES, blend_name)
    before = set(bpy.data.node_groups)
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):
        data_to.node_groups = list(data_from.node_groups)
    return [g for g in bpy.data.node_groups if g not in before]


def _sockets(group):
    items = group.interface.items_tree
    out = {'INPUT': [], 'OUTPUT': []}
    for item in items:
        kind = getattr(item, 'in_out', None)
        if kind in out and getattr(item, 'item_type', '') == 'SOCKET':
            out[kind].append(getattr(item, 'name', ''))
    return out


def _uv_evidence(group):
    """Nós e sockets que indicam UV dentro do grafo."""
    evidence = []
    for node in group.nodes:
        label = f'{node.bl_idname}:{node.name}'
        if 'UV' in node.bl_idname or 'UV' in node.name:
            evidence.append(label)
        if node.bl_idname == 'GeometryNodeStoreNamedAttribute':
            name = getattr(node, 'data_type', '')
            attribute = ''
            for item in node.inputs:
                if item.name == 'Name' and getattr(item, 'default_value', None):
                    attribute = item.default_value
            if 'FLOAT2' in name or 'UV' in attribute.upper():
                evidence.append(f'{label}(data_type={name},nome={attribute})')
        if node.bl_idname == 'GeometryNodeInputNamedAttribute':
            for item in node.inputs:
                if item.name == 'Name' and getattr(item, 'default_value', None):
                    if 'UV' in str(item.default_value).upper():
                        evidence.append(f'{label}(lê {item.default_value})')
    return evidence


def check_cutpart():
    groups = _load_group('GeoNodeCutpart.blend')
    out = []
    for group in groups:
        sockets = _sockets(group)
        out.append({
            'grupo': group.name,
            'entradas': sockets['INPUT'],
            'saidas': sockets['OUTPUT'],
            'tem_socket_uv': any('UV' in name.upper() for name in sockets['INPUT'] + sockets['OUTPUT']),
            'evidencia_uv_no_grafo': _uv_evidence(group),
        })
    return out


def check_wall():
    groups = _load_group('GeoNodeWall.blend')
    wanted = ['Top Surface', 'Bottom Surface', 'Inside Face', 'Outside Face', 'Left Edge', 'Right Edge']
    out = []
    for group in groups:
        sockets = _sockets(group)
        inputs = sockets['INPUT']
        out.append({
            'grupo': group.name,
            'total_entradas': len(inputs),
            'materiais_presentes': [w for w in wanted if w in inputs],
            'materiais_ausentes': [w for w in wanted if w not in inputs],
            'entradas_com_material': [n for n in inputs if 'material' in n.lower() or 'surface' in n.lower()
                                      or 'face' in n.lower()],
            'saidas': sockets['OUTPUT'],
        })
    return out


def _make_image():
    image = bpy.data.images.new('probe_uv', 2, 2, alpha=True)
    red = (1.0, 0.0, 0.0, 1.0)
    blue = (0.0, 0.0, 1.0, 1.0)
    pixels = []
    for _row in range(2):
        pixels += list(red) + list(blue)      # coluna 0 vermelha, coluna 1 azul
    image.pixels = pixels
    image.pack()
    return image


def _material_with_uv(layer):
    mat = bpy.data.materials.new(f'probe_uv_{layer}')
    mat.use_nodes = True
    tree = mat.node_tree
    for node in list(tree.nodes):
        if node.type != 'OUTPUT_MATERIAL':
            tree.nodes.remove(node)
    output = next(n for n in tree.nodes if n.type == 'OUTPUT_MATERIAL')
    uv = tree.nodes.new('ShaderNodeUVMap')
    uv.uv_map = layer
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = _make_image()
    tex.interpolation = 'Closest'
    tex.extension = 'EXTEND'
    emission = tree.nodes.new('ShaderNodeEmission')
    tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
    tree.links.new(tex.outputs['Color'], emission.inputs['Color'])
    tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])
    return mat


def _plane(layer_names):
    bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0.0, 0.0, 0.0))
    obj = bpy.context.active_object
    mesh = obj.data
    for index, name in enumerate(layer_names):
        layer = mesh.uv_layers[0] if index == 0 and mesh.uv_layers else mesh.uv_layers.new(name=name)
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                vertex = mesh.vertices[mesh.loops[loop_index].vertex_index]
                layer.data[loop_index].uv = ((vertex.co.x + 1.0) / 2.0, (vertex.co.y + 1.0) / 2.0)
    return obj


def _render(path):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 1
    scene.cycles.use_denoising = False
    scene.render.resolution_x = 8
    scene.render.resolution_y = 8
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    pixels = list(image.pixels)
    width = image.size[0]

    def sample(x, y):
        offset = (y * width + x) * 4
        return [round(v, 2) for v in pixels[offset:offset + 3]]

    left = sample(1, 4)
    right = sample(6, 4)
    bpy.data.images.remove(image)
    return {'esquerda': left, 'direita': right}


def _flip_uv(obj):
    layer = obj.data.uv_layers['UVMap']
    for item in layer.data:
        item.uv = (1.0 - item.uv[0], item.uv[1])


def check_uv_layer():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    out = {'camadas': ['UVMap', 'Outra']}
    obj = _plane(['UVMap', 'Outra'])
    obj.data.materials.append(_material_with_uv('UVMap'))
    # A segunda camada aponta para o lado oposto; se o material ignorasse o nome, o resultado seria o invertido.
    other = obj.data.uv_layers['Outra']
    for item in other.data:
        item.uv = (1.0 - item.uv[0], item.uv[1])
    camera_data = bpy.data.cameras.new('probe_cam')
    camera = bpy.data.objects.new('probe_cam', camera_data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location = (0.0, 0.0, 4.0)
    bpy.context.scene.camera = camera
    light_data = bpy.data.lights.new('probe_light', 'SUN')
    light = bpy.data.objects.new('probe_light', light_data)
    bpy.context.scene.collection.objects.link(light)
    light.location = (0.0, 0.0, 3.0)
    out['antes'] = _render(os.path.join(ROOT, 'probe_uv_antes.png'))
    _flip_uv(obj)
    out['depois_de_editar_uv'] = _render(os.path.join(ROOT, 'probe_uv_depois.png'))
    out['muda_com_edicao_de_uv'] = out['antes']['esquerda'] != out['depois_de_editar_uv']['esquerda']
    return out


def check_grain_cost():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    from caffmob_draw.target import props as target_props
    try:
        target_props.register()
    except Exception as exc:                                  # noqa: BLE001 - relatar, não abortar
        return {'erro': f'registro de target.props: {exc}'}
    from caffmob_draw.object_library import retexture
    from caffmob_draw.texture_library import grain

    image = _make_image()
    path = os.path.join(ROOT, 'probe_textura.png')
    image.filepath_raw = path
    image.file_format = 'PNG'
    image.save()
    mat = retexture.image_material(path, 600.0, texture_id='probe')
    objects = []
    for index in range(40):
        mesh = bpy.data.meshes.new(f'peca_{index}')
        obj = bpy.data.objects.new(f'peca_{index}', mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.data.materials.append(mat)
        objects.append(obj)
    inicio = time.perf_counter()
    for obj in objects:
        grain.sync(obj)
    total = time.perf_counter() - inicio
    return {
        'pecas': len(objects),
        'total_s': round(total, 4),
        'por_peca_ms': round(total * 1000.0 / len(objects), 2),
        'material_tem_grafo': grain.ensure_graph(mat),
        'projecao': grain.projection(mat),
    }


def main():
    RESULT['blender'] = bpy.app.version_string
    for name, function in (('cutpart', check_cutpart), ('parede', check_wall),
                           ('uv_layer', check_uv_layer), ('grain', check_grain_cost)):
        try:
            RESULT[name] = function()
        except Exception as exc:                              # noqa: BLE001 - o probe precisa terminar
            RESULT[name] = {'erro': str(exc), 'trace': traceback.format_exc()}
    print('===PROBE_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, indent=2))
    print('===PROBE_JSON_FIM===')


main()
