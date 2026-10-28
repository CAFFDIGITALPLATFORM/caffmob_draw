"""Montagem da porta e da janela reais em poucas malhas (feature 010, T014 e T016; D-08).

As peças de `door_core`/`window_core` são juntadas por papel, numa malha cada: Marco, Ferragens do marco e, por
folha, Folha N e Ferragens da folha N (na janela, perfil, vidro e puxador ficam na malha da folha). Cerca de 5 a 6
objetos por porta no lugar das 157 peças do gerador original, com os materiais por slot, a UV de caixa com o veio
orientado por peça (como o gerador) e Bevel por ângulo + Weighted Normal para os cantos chanfrados.

Os objetos saem no referencial da caixa (sem pai); quem monta (`openings/sync.py`) os põe no lugar.
"""

import math

import bmesh  # type: ignore
import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from . import door_core as dc
from . import materials

BEVEL = 0.001
_AXIS = {'CYL_X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'CYL_Y': Matrix.Rotation(math.pi / 2, 4, 'X'),
         'CYL_Z': Matrix.Identity(4)}


def group_key(part):
    if part.role in (dc.FRAME, dc.FRAME_HW):
        return part.role, None
    return (dc.LEAF if part.role == dc.LEAF or part.material in ('ALU', 'GLASS') else dc.LEAF_HW), (part.leaf or 0)


def group_name(key):
    role, leaf = key
    if role == dc.FRAME:
        return "Marco"
    if role == dc.FRAME_HW:
        return "Ferragens do marco"
    if role == dc.LEAF:
        return f"Folha {leaf + 1}"
    return f"Ferragens da folha {leaf + 1}"


def _add_part(bm, part, slot, uv_layer):
    if part.shape == 'BOX':
        geom = bmesh.ops.create_cube(bm, size=1.0)['verts']
        bmesh.ops.scale(bm, vec=part.size, verts=geom)
    else:
        d, _d, h = part.size
        geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=d / 2, radius2=d / 2, depth=h)['verts']
        bmesh.ops.transform(bm, matrix=_AXIS[part.shape], verts=geom)
    bmesh.ops.translate(bm, vec=part.center, verts=geom)
    faces = {f for v in geom for f in v.link_faces}
    offset = (sum(ord(c) for c in part.name) % 97) / 97
    for face in faces:
        face.material_index = slot
        face.smooth = part.shape != 'BOX'
        n = face.normal
        for loop in face.loops:
            co = loop.vert.co
            if abs(n.y) > 0.5:
                a, b = (co.z, co.x) if part.horizontal else (co.x, co.z)
            elif abs(n.x) > 0.5:
                a, b = co.y, co.z
            else:
                a, b = co.x, co.y
            loop[uv_layer].uv = (a / 0.45 + offset, b / 2.3 + offset * 0.3)


def build(parts, collection, window=False):
    """{chave do grupo: objeto} com as malhas montadas, ligadas a `collection`."""
    groups = {}
    for part in parts:
        groups.setdefault(group_key(part), []).append(part)
    out = {}
    for key, items in groups.items():
        name = group_name(key)
        keys = sorted({p.material for p in items})
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new("UVMap")
        for part in items:
            _add_part(bm, part, keys.index(part.material), uv_layer)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        for material in keys:
            mesh.materials.append(materials.get(material))
        obj = bpy.data.objects.new(name, mesh)
        collection.objects.link(obj)
        if any(p.bevel for p in items):
            bevel = obj.modifiers.new("Chanfro", 'BEVEL')
            bevel.width, bevel.segments, bevel.limit_method = BEVEL, 2, 'ANGLE'
            weighted = obj.modifiers.new("Normais ponderadas", 'WEIGHTED_NORMAL')
            weighted.keep_sharp = True
        out[key] = obj
    return out
