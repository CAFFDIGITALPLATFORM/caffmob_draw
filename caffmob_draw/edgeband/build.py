"""Malha da faixa de fita (feature 067, T070; D-21; RF-081, RF-084).

Uma faixa é uma caixa fina fora da face estreita, afastada `OFFSET` contra z-fighting, com a espessura da fita, e
dentro do retângulo da própria face: não cobre a face larga, não passa da quina (sem sobrepor a faixa vizinha) e não
entra no vão. A malha é filha do dono, no referencial dele, então acompanha o movimento do componente. Normais para
fora; seis faces por faixa.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from . import core

OFFSET = 0.0002                 # 0,2 mm entre a chapa e a fita
SOLID_PREFIX = "Fita lisa "


def _write(obj, band, thickness):
    lo, hi = core.band_box(band, thickness, OFFSET)
    bm = bmesh.new()
    verts = [bm.verts.new(co) for co in ((lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]), (hi[0], hi[1], lo[2]),
                                          (lo[0], hi[1], lo[2]), (lo[0], lo[1], hi[2]), (hi[0], lo[1], hi[2]),
                                          (hi[0], hi[1], hi[2]), (lo[0], hi[1], hi[2]))]
    for a, b, c, d in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        bm.faces.new((verts[a], verts[b], verts[c], verts[d]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()


def solid_material(color):
    """Material liso da cor (reaproveitado pela cor): a cor lisa não toca a imagem do material fonte (RF-084)."""
    key = "#%02X%02X%02X" % tuple(int(round(max(0.0, min(1.0, c)) * 255)) for c in color[:3])
    name = SOLID_PREFIX + key
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = tuple(color[:3]) + (1.0,)
        bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.node_tree else None
        if bsdf is not None:
            bsdf.inputs['Base Color'].default_value = tuple(color[:3]) + (1.0,)
        mat['btm_edgeband_solid'] = True
    return mat


def apply_material(obj):
    data = obj.btm_edgeband
    mat = solid_material(data.color) if data.use_color else data.material
    materials = obj.data.materials
    if not materials:
        materials.append(mat)
    else:
        materials[0] = mat


def update(obj, band, thickness=None):
    """Grava a geometria e os metadados da faixa; devolve True se a malha foi refeita."""
    data = obj.btm_edgeband
    if thickness is not None:
        data.thickness = thickness if abs(data.thickness - thickness) > 1e-9 else data.thickness
    digest = core.params_hash(band, data.thickness, OFFSET)
    rebuilt = digest != data.params_hash
    if rebuilt:
        _write(obj, band, data.thickness)
        data.params_hash = digest
    keys = core.dumps(band.keys)
    if data.edge_keys != keys:
        data.edge_keys = keys
        data.part_uids = core.dumps(sorted({k.split('|')[0] for k in band.keys}))
    length, width = band.size()
    if abs(data.length - length) > 1e-9:
        data.length = length
    if abs(data.coverage_width - width) > 1e-9:
        data.coverage_width = width
    return rebuilt


def create(owner, band, thickness, material=None, color=None):
    """Malha nova da faixa, filha do dono, fora do corte e da colisão."""
    from ..cutting import part_sources
    mesh = bpy.data.meshes.new("Fita de borda")
    obj = bpy.data.objects.new("Fita de borda", mesh)
    for collection in owner.users_collection or (bpy.context.collection,):
        collection.objects.link(obj)
        break
    obj.parent = owner
    obj.matrix_parent_inverse.identity()
    obj.matrix_basis.identity()
    data = obj.btm_edgeband
    data.visual = True
    data.uid = band.uid
    data.owner = owner
    data.owner_uid = part_sources.ensure_module_uid(owner)
    data.thickness = thickness
    data.state = 'GENERATED'
    obj.btm_cut_exclude = True
    plane = getattr(obj, 'btm_plane', None)
    if plane is not None:
        plane.collision_override = 'OFF'
    if material is not None:
        data.material = material
    if color is not None:
        data.color = color
    update(obj, band)
    apply_material(obj)
    return obj
