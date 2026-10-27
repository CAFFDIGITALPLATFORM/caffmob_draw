"""Mapas PBR de uma textura do pacote no material (073, T017; D-09, RN-08).

`attach(mat, entry, vector=None)` liga ao Principled os mapas que a entrada tem no disco (`local_path`): normal
(NormalGL → Normal Map → Normal), rugosidade (→ Roughness) e metálico (→ Metallic), em Non-Color, no mesmo vetor da
cor. Sem `vector`, usa a entrada Vector do nó de imagem da cor. Os dois construtores de material do addon
(`object_library.retexture.image_material`, projeção em caixa, e `mobi.materiais_v2._aplicar_imagem`, UV em mm)
chamam esta função, então os dois saem iguais. Idempotente: os nós têm nome e a marca `btm_texture_pbr` evita
ligar duas vezes.
"""

import bpy  # type: ignore

MARK = "btm_texture_pbr"
NORMAL, ROUGHNESS, METALLIC = "CAFFMob PBR Normal", "CAFFMob PBR Rugosidade", "CAFFMob PBR Metálico"


def _color_node(tree):
    bsdf = next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        return None, None
    links = [lk for lk in tree.links if lk.to_node == bsdf and lk.to_socket.name == 'Base Color']
    node = links[0].from_node if links else None
    return bsdf, node if node is not None and node.type == 'TEX_IMAGE' else None


def _image_node(tree, name, path, color, location):
    node = tree.nodes.new('ShaderNodeTexImage')
    node.name = node.label = name
    node.image = bpy.data.images.load(path, check_existing=True)
    node.image.colorspace_settings.name = 'Non-Color'
    node.location = location
    node.projection, node.projection_blend = color.projection, color.projection_blend
    node.extension = color.extension
    return node


def attach(mat, entry, vector=None):
    """Liga os mapas PBR; devolve True se ligou agora (False sem entrada PBR, sem nós ou já ligado)."""
    if mat is None or not entry or not entry.get('pbr') or mat.get(MARK) == entry['id']:
        return False
    tree = mat.node_tree
    if tree is None:
        return False
    bsdf, color = _color_node(tree)
    if bsdf is None or color is None:
        return False
    if vector is None:
        links = color.inputs['Vector'].links
        vector = links[0].from_socket if links else None
    for name in (NORMAL, ROUGHNESS, METALLIC):
        old = tree.nodes.get(name)
        if old is not None:
            tree.nodes.remove(old)
    old_map = tree.nodes.get(NORMAL + " Mapa")
    if old_map is not None:
        tree.nodes.remove(old_map)
    paths = entry.get('local_path') or {}
    x, y = color.location
    plugs = []
    if paths.get('normal'):
        tex = _image_node(tree, NORMAL, paths['normal'], color, (x, y - 300))
        normal_map = tree.nodes.new('ShaderNodeNormalMap')
        normal_map.name = normal_map.label = NORMAL + " Mapa"
        normal_map.location = (x + 280, y - 300)
        tree.links.new(tex.outputs['Color'], normal_map.inputs['Color'])
        tree.links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
        plugs.append(tex)
    if paths.get('rugosidade'):
        tex = _image_node(tree, ROUGHNESS, paths['rugosidade'], color, (x, y - 600))
        tree.links.new(tex.outputs['Color'], bsdf.inputs['Roughness'])
        plugs.append(tex)
    if paths.get('metalico'):
        tex = _image_node(tree, METALLIC, paths['metalico'], color, (x, y - 900))
        tree.links.new(tex.outputs['Color'], bsdf.inputs['Metallic'])
        plugs.append(tex)
    if vector is not None:
        for tex in plugs:
            tree.links.new(vector, tex.inputs['Vector'])
    mat[MARK] = entry['id']
    return bool(plugs)
