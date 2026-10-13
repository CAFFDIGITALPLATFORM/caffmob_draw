"""Relevo da textura (feature 014, T045; RF-14, Could).

Quando o item do catálogo tem `bump` (o `.bump` do fabricante, um JPEG de altura), a imagem de relevo é baixada como
um item próprio do servidor (`<id>.bump`, mesma fila e mesmo cache) e ligada ao material: Image Texture (Non-Color, a
mesma projeção em caixa e o mesmo mapeamento da cor) → Bump → Normal do Principled. Aparece no modo de vista com
material e no render. Sem a imagem (sem internet, sem conta), o material fica só com a cor, sem aviso.
"""

import bpy  # type: ignore

from . import downloads

NODE_NAME = "CAFFMob Relevo"
STRENGTH = 0.25


def bump_id(item_id):
    return item_id + ".bump"


def bump_entry(item):
    """Entrada do relevo para a fila de download (fora do catálogo do pacote)."""
    return {"id": bump_id(item["id"]), "name": item.get("name", ""), "ext": "jpg", "sha256": "", "bytes": 0}


def attach(mat, path):
    """Liga a imagem de relevo ao material (uma vez); devolve True se ligou agora."""
    tree = mat.node_tree if mat is not None else None
    if tree is None or tree.nodes.get(NODE_NAME) is not None:
        return False
    bsdf = next((n for n in tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    mapping = next((n for n in tree.nodes if n.type == 'MAPPING'), None)
    if bsdf is None or mapping is None:
        return False
    tex = tree.nodes.new('ShaderNodeTexImage')
    tex.name = tex.label = NODE_NAME
    tex.image = bpy.data.images.load(path, check_existing=True)
    tex.image.colorspace_settings.name = 'Non-Color'
    tex.projection, tex.projection_blend = 'BOX', 0.2
    bump = tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = STRENGTH
    tex.location, bump.location = (-450, -320), (-200, -320)
    tree.links.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    tree.links.new(tex.outputs['Color'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return True


def request(mat, item):
    """Liga o relevo agora (imagem no cache) ou depois do download; nada sem `bump` no catálogo ou sem rede."""
    if not item or not item.get("bump") or mat is None:
        return
    entry = bump_entry(item)
    path = downloads.cached(entry["id"], entry=entry)
    if path:
        attach(mat, path)
        return
    if downloads.unavailable_reason():
        return
    name = mat.name

    def done(path, error):
        target = bpy.data.materials.get(name)
        if path and not error and target is not None:
            attach(target, path)
    downloads.fetch(entry["id"], done, entry=entry)
