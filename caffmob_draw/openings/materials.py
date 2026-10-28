"""Materiais da porta e da janela reais (feature 010, T015; D-09, D-15), compartilhados por arquivo.

Cada material é criado uma vez e reaproveitado pela marca `btm_opening_material` (chave). A nogueira usa as texturas
do pacote (`assets/nogueira_cor.jpg` e `nogueira_rugosidade.jpg`, da porta realista do projeto), com bump fino, como
o gerador original. Alumínio e vidro seguem os valores do preset da `blender-product-polish` (rugosidade baixa,
camada de verniz, IOR alto).
"""

import os

import bpy  # type: ignore

TAG = 'btm_opening_material'
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

FINISH_KEYS = {
    'madeira': 'WOOD',
    'aluminio': 'ALU',
    'blindex': 'GLASS',
}


def resolve_finish_key(finish):
    """Mapeia acabamento do contrato v2 ('madeira'|'aluminio'|'blindex') para chave de SPECS."""
    if finish in SPECS:
        return finish
    return FINISH_KEYS.get(finish or 'madeira', 'WOOD')

# chave: (nome, cor, metálico, rugosidade, extras)
SPECS = {
    'WOOD': ("Nogueira verniz acetinado", (0.32, 0.18, 0.075), 0.0, 0.35, {'Coat Weight': 0.18, 'Coat Roughness': 0.3}),
    'METAL': ("Aço inox escovado", (0.46, 0.49, 0.51), 1.0, 0.27, {}),
    'RUBBER': ("Borracha EPDM", (0.012, 0.016, 0.014), 0.0, 0.68, {}),
    'SLOT': ("Cavidades das ferragens", (0.019, 0.022, 0.025), 0.6, 0.42, {}),
    'BRASS': ("Latão", (0.48, 0.30, 0.10), 0.85, 0.3, {}),
    'ALU': ("Alumínio anodizado", (0.78, 0.79, 0.80), 1.0, 0.18, {'Coat Weight': 1.0, 'Coat Roughness': 0.05}),
    'GLASS': ("Vidro", (0.86, 0.92, 0.95), 0.0, 0.02, {'Transmission Weight': 1.0, 'IOR': 1.52, 'Alpha': 0.25}),
    'STONE': ("Granito cinza", (0.36, 0.36, 0.37), 0.0, 0.22, {'Coat Weight': 0.4}),
}


def _image(name):
    path = os.path.join(ASSETS, name)
    if not os.path.isfile(path):
        return None
    return bpy.data.images.load(path, check_existing=True)


def _wood_textures(mat, bsdf):
    tree = mat.node_tree
    color, rough = _image("nogueira_cor.jpg"), _image("nogueira_rugosidade.jpg")
    if color is None:
        return
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.image = color
    tex.location = (bsdf.location.x - 400, bsdf.location.y + 120)
    tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.025
    bump.inputs['Distance'].default_value = 0.00022
    bump.location = (bsdf.location.x - 200, bsdf.location.y - 260)
    tree.links.new(tex.outputs['Color'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    if rough is not None:
        rough.colorspace_settings.name = 'Non-Color'
        node = tree.nodes.new('ShaderNodeTexImage')
        node.image = rough
        node.location = (bsdf.location.x - 400, bsdf.location.y - 160)
        tree.links.new(node.outputs['Color'], bsdf.inputs['Roughness'])


def get(key):
    """Material da chave (`door_core`/`window_core`), criado na primeira vez e reaproveitado depois."""
    for mat in bpy.data.materials:
        if mat.get(TAG) == key:
            return mat
    name, color, metallic, roughness, extras = SPECS[key]
    mat = bpy.data.materials.new(name)
    mat[TAG] = key
    mat.diffuse_color = (*color, extras.get('Alpha', 1.0))
    mat.metallic, mat.roughness = metallic, roughness
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is not None:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        for socket, value in extras.items():
            if socket in bsdf.inputs:
                bsdf.inputs[socket].default_value = value
        if key == 'WOOD':
            _wood_textures(mat, bsdf)
    if key == 'GLASS':
        mat.surface_render_method = 'BLENDED'
    return mat
