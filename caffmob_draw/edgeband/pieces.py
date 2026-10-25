"""As peças de um componente como caixas no referencial do dono (feature 067, onda 4; D-21, RF-082).

- módulo BTM: as chapas são caixas de 8 vértices consecutivos da malha (é assim que `geometry/mesh_gen` monta cada
  chapa), mais as portas filhas;
- bibliotecas HB e armário autoral: cada peça (`customize/finish.pieces_of`) pela caixa dela, levada ao dono;
- objeto solto ou geometria livre: ele mesmo, no próprio referencial.

O uid da peça é o `btm_uid` do objeto (`cutting/part_sources.ensure_module_uid`); a chapa da malha BTM usa o do dono
com o índice da chapa. Fita visual nunca entra como peça.
"""

from mathutils import Vector  # type: ignore

from . import core


def _uid(obj, create):
    from ..cutting import part_sources
    if create:
        return part_sources.ensure_module_uid(obj)
    return str(obj.get(part_sources.UID_PROP) or obj.name)


def _box_in(owner_inv, obj, uid):
    corners = [owner_inv @ (obj.matrix_world @ Vector(c)) for c in obj.bound_box]
    lo = tuple(min(c[i] for c in corners) for i in range(3))
    hi = tuple(max(c[i] for c in corners) for i in range(3))
    return core.Box(uid, lo, hi)


def _mesh_boxes(owner, uid):
    verts = owner.data.vertices
    if not verts or len(verts) % 8:
        return []
    out = []
    for index in range(len(verts) // 8):
        group = [verts[index * 8 + k].co for k in range(8)]
        lo = tuple(min(v[i] for v in group) for i in range(3))
        hi = tuple(max(v[i] for v in group) for i in range(3))
        out.append(core.Box(f"{uid}:{index}", lo, hi))
    return out


def boxes(owner, create_uids=False):
    """[(Box, objeto)] das peças do componente, no referencial do dono."""
    from ..customize import finish
    if owner is None:
        return []
    inverse = owner.matrix_world.inverted_safe()
    out = []
    library = finish._library(owner)
    for obj in finish.pieces_of(owner):
        if getattr(obj, 'btm_cut_exclude', False) or obj.type != 'MESH':
            continue
        uid = _uid(obj, create_uids)
        if library == 'BTM' and obj is owner:
            out += [(box, obj) for box in _mesh_boxes(obj, uid)]
        else:
            out.append((_box_in(inverse, obj, uid), obj))
    return out


def owner_for(obj):
    """Dono da fita: o da faixa selecionada, ou o dono do acabamento do objeto."""
    band = getattr(obj, 'btm_edgeband', None)
    if band is not None and band.visual:
        return band.owner
    from ..customize import finish
    return finish.owner_of(obj)


def bands_of(owner):
    """As faixas de fita visual do componente (filhas do dono)."""
    if owner is None:
        return []
    return [o for o in owner.children if getattr(o, 'btm_edgeband', None) is not None and o.btm_edgeband.visual]
