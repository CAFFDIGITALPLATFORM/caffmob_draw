"""Converter e desconverter agregado (feature 003, T041; RN-07, RN-12, D-12).

O objeto vira filho Blender do pai (mover, girar e apagar o pai o levam junto), preso à face do pai mais próxima.
O pai e a matriz originais ficam guardados para desconverter sem perda.

Feature 007 (T016): um grupo de peças (Empty com `btm_group`) também pode virar agregado ou folha, e uma esquadria
(grupo FRAME) pode ser o pai.
"""

import bpy  # type: ignore
from mathutils import Matrix  # type: ignore

from ..data.i18n import tr
from . import apply, limits


def can_convert(obj, parent):
    from . import group
    if obj is None or (obj.type != 'MESH' and not group.is_group(obj)):      # grupo de peças: feature 007, D-05
        return tr("Selecione um objeto de malha para converter")
    if parent is None:
        return tr("Selecione também o elemento pai (por último, como ativo)")
    if parent == obj or parent in obj.children_recursive:
        return tr("O pai não pode ser o próprio objeto nem um filho dele")
    stick = getattr(obj, 'btm_stick', None)
    if stick is not None and stick.is_stuck:
        return tr("O objeto está grudado numa face: desgrude antes")       # feature 004, data-delta §5
    if getattr(parent, 'btm_aggregate', None) is not None and parent.btm_aggregate.kind == 'LEAF':
        return tr("Uma folha de porta não pode receber agregados")
    return None


def convert(obj, parent, face=None):
    """Converte `obj` em agregado de `parent`; devolve a face escolhida."""
    agg = obj.btm_aggregate
    if not agg.is_aggregate:
        agg.orig_parent = obj.parent
        agg.orig_matrix = [v for row in obj.matrix_world for v in row]
    world = obj.matrix_world.copy()
    obj.parent = parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = parent.matrix_world.inverted() @ world
    bpy.context.view_layer.update()
    box_p = apply.local_box(parent)
    box_a = apply.box_in_parent(obj, parent)
    center = tuple((box_a[0][i] + box_a[1][i]) / 2.0 for i in range(3))
    face = face or limits.nearest_face(box_p, center)
    agg.size = limits.size(box_a)
    agg.rest_offset = tuple(box_a[0][i] - obj.location[i] for i in range(3))
    u, v, offset = limits.params_from_box(box_p, box_a, face)
    for name, value in (('face', face), ('u', u), ('v', v), ('offset', offset)):
        apply._write(obj, name, value)
    agg.parent_ref = parent
    agg.is_aggregate = True
    apply.update_position(obj)
    return face


def unconvert(obj):
    """Desfaz a conversão: remove recortes, folha e devolve pai e posição originais (RN-12)."""
    agg = obj.btm_aggregate
    if not agg.is_aggregate:
        return False
    from . import perforate
    agg_perforate = agg.perforate
    if agg_perforate or agg.cutter is not None:
        apply._write(obj, 'perforate', False)
        apply._write(obj, 'real_hole', False)
        perforate.sync(obj)
    if agg.kind == 'LEAF':
        from . import leaf
        leaf.remove_pivot(obj)
    if agg.production_part:
        apply._write(obj, 'production_part', False)
        from . import production
        production.sync(obj)
    world = Matrix([agg.orig_matrix[i * 4:(i + 1) * 4] for i in range(4)])
    obj.parent = agg.orig_parent
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = world
    agg.is_aggregate = False
    agg.kind = 'AGGREGATE'
    agg.parent_ref = None
    return True
