"""Probe 2 do T001 da 018: o UV que o GeoNodeCutpart entrega e o custo de grain.sync.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_018_probe2.py
"""

import json
import os
import sys
import time
import traceback

import bpy  # type: ignore

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND = os.path.join(ROOT, 'caffmob_draw', 'geometry_nodes', 'GeoNodeCutpart.blend')
RESULT = {}


def _group():
    before = set(bpy.data.node_groups)
    with bpy.data.libraries.load(BLEND, link=False) as (data_from, data_to):
        data_to.node_groups = list(data_from.node_groups)
    new = [g for g in bpy.data.node_groups if g not in before]
    return next(g for g in new if g.name.split('.')[0] == 'GeoNodeCutpart')


def _store_nodes(group):
    out = []
    for node in group.nodes:
        if node.bl_idname == 'GeometryNodeStoreNamedAttribute':
            name = ''
            for item in node.inputs:
                if item.name == 'Name':
                    name = getattr(item, 'default_value', '')
            out.append({
                'no': node.name,
                'data_type': getattr(node, 'data_type', ''),
                'domain': getattr(node, 'domain', ''),
                'nome': name,
                'entradas': [item.name for item in node.inputs],
                'ligado_a': [link.from_node.bl_idname for link in group.links if link.to_node == node],
            })
    return out


def _identifiers(group, wanted):
    found = {}
    for item in group.interface.items_tree:
        if getattr(item, 'item_type', '') == 'SOCKET' and getattr(item, 'in_out', '') == 'INPUT':
            if item.name in wanted:
                found[item.name] = item.identifier
    return found


def check_evaluated_uv():
    group = _group()
    out = {'stores': _store_nodes(group)}

    bpy.ops.mesh.primitive_cube_add(size=1.0)
    obj = bpy.context.active_object
    obj.name = 'probe_chapa'
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name='UVMap')
    else:
        mesh.uv_layers[0].name = 'UVMap'
    out['base_uv_layers'] = [layer.name for layer in mesh.uv_layers]

    modifier = obj.modifiers.new('ProbeCutpart', 'NODES')
    modifier.node_group = group
    ids = _identifiers(group, {'Length', 'Width', 'Thickness', 'Top Surface', 'Bottom Surface'})
    out['identificadores'] = ids
    from caffmob_draw import compat
    out['escritas'] = {}
    for name, value in (('Length', 1.0), ('Width', 0.6), ('Thickness', 0.018)):
        out['escritas'][name] = compat.try_set_gn_input(modifier, name, value)
    obj.update_tag()
    bpy.context.view_layer.update()

    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    out['avaliado_uv_layers'] = [layer.name for layer in evaluated_mesh.uv_layers]
    attributes = []
    for attribute in evaluated_mesh.attributes:
        attributes.append({'nome': attribute.name, 'dominio': attribute.domain,
                           'tipo': attribute.data_type})
    out['atributos'] = attributes
    out['tem_atributo_uv_map'] = any(a['nome'].lower() in ('uv_map', 'uvmap') for a in attributes)
    out['tem_camada_uv'] = bool(evaluated_mesh.uv_layers)
    out['faces'] = len(evaluated_mesh.polygons)
    evaluated.to_mesh_clear()
    return out


def check_grain_cost():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    import caffmob_draw
    try:
        caffmob_draw.register()
    except Exception as exc:                                  # noqa: BLE001
        return {'registro_addon': f'falhou: {exc}', 'trace': traceback.format_exc()[-800:]}

    from caffmob_draw.texture_library import grain
    from caffmob_draw.object_library import retexture

    image = bpy.data.images.new('probe_tex', 4, 4)
    image.pixels = [0.5] * (4 * 4 * 4)
    path = os.path.join(ROOT, 'probe_textura.png')
    image.filepath_raw = path
    image.file_format = 'PNG'
    image.save()
    mat = retexture.image_material(path, 600.0, texture_id='probe')

    objects = []
    for index in range(40):
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        obj = bpy.context.active_object
        obj.name = f'probe_peca_{index}'
        obj.data.materials.append(mat)
        objects.append(obj)

    inicio = time.perf_counter()
    for obj in objects:
        grain.sync(obj)
    total = time.perf_counter() - inicio
    return {
        'registro_addon': 'ok',
        'pecas': len(objects),
        'total_s': round(total, 4),
        'por_peca_ms': round(total * 1000.0 / len(objects), 2),
        'projecao': grain.projection(mat),
        'grafo_ok': grain.ensure_graph(mat),
        'veio_gravado': objects[0].get('btm_grain_rot', None),
    }


def main():
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    RESULT['blender'] = bpy.app.version_string
    for name, function in (('uv_avaliado', check_evaluated_uv), ('grain', check_grain_cost)):
        try:
            RESULT[name] = function()
        except Exception as exc:                              # noqa: BLE001
            RESULT[name] = {'erro': str(exc), 'trace': traceback.format_exc()}
    print('===PROBE2_JSON_INICIO===')
    print(json.dumps(RESULT, ensure_ascii=False, indent=2, default=str))
    print('===PROBE2_JSON_FIM===')


main()
