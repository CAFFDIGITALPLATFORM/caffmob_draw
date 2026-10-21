"""Malha da placa e da caixa (T021; D-18) e as chapas que as formam (lista de peças, data-delta §5).

Python puro nas funções de medida (`size`, `sheets`); só `update`/`create_object` tocam o Blender.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from ..data.i18n import N_

GEOMETRY_FLAG = 'IS_BTM_GEOMETRY'
_parameters = {}      # session_uid → parâmetros da última malha construída


def size(kind, plane, width, depth, height, thickness):
    """(x, y, z) da peça: na placa, o eixo da espessura recebe `thickness`."""
    if kind == 'PLACA':
        if plane == 'XY':
            return width, depth, thickness
        if plane == 'XZ':
            return width, thickness, height
        return thickness, depth, height
    return width, depth, height


def sheets(kind, plane, width, depth, height, thickness):
    """[(nome, comprimento, largura, espessura)] em metros.

    Placa: uma chapa com espessura `thickness` e comprimento e largura pelas duas medidas do plano, maior primeiro
    (questions.md, pergunta 66). Caixa: fundo e tampo inteiros; laterais entre eles; frente e trás entre as laterais.
    """
    if kind == 'PLACA':
        a, b = sorted(_plane_sides(plane, width, depth, height), reverse=True)
        return [(N_("Placa"), a, b, thickness)]
    t = thickness
    inner_h = max(0.001, height - 2 * t)
    inner_w = max(0.001, width - 2 * t)
    return [
        (N_("Fundo"), width, depth, t), (N_("Tampo"), width, depth, t),
        (N_("Lateral esquerda"), inner_h, depth, t), (N_("Lateral direita"), inner_h, depth, t),
        (N_("Frente"), inner_w, inner_h, t), (N_("Trás"), inner_w, inner_h, t),
    ]


def _plane_sides(plane, width, depth, height):
    return {'XY': (width, depth), 'XZ': (width, height)}.get(plane, (depth, height))


def thinner_than_thickness(kind, plane, width, depth, height, thickness):
    """Placa com uma medida do plano menor que a espessura (aviso no painel, pergunta 66)."""
    return kind == 'PLACA' and min(_plane_sides(plane, width, depth, height)) < thickness


def _props(obj):
    g = obj.btm_geometry
    return g.kind, g.plane, g.width, g.depth, g.height, g.thickness


def update(obj):
    """Refaz a malha (caixa com origem no canto mínimo) a partir de `btm_geometry`."""
    x, y, z = size(*_props(obj))
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * x
        v.co.y = (v.co.y + 0.5) * y
        v.co.z = (v.co.z + 0.5) * z
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    _parameters[obj.session_uid] = _props(obj)


def create_object(context, kind='PLACA', name=None):
    """Cria a geometria na coleção ativa, marcada como `GEOMETRY`."""
    label = name or ("Placa" if kind == 'PLACA' else "Caixa")
    data = bpy.data.meshes.new(label)
    obj = bpy.data.objects.new(label, data)
    context.collection.objects.link(obj)
    obj[GEOMETRY_FLAG] = True
    obj.btm_plane.object_kind = 'GEOMETRY'
    obj.btm_geometry.kind = kind
    update(obj)
    return obj


def is_geometry(obj):
    return obj is not None and obj.type == 'MESH' and getattr(obj, 'btm_plane', None) is not None \
        and obj.btm_plane.object_kind == 'GEOMETRY' and getattr(obj, 'btm_geometry', None) is not None
