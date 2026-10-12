"""Perfurar o pai e furo real no plano de corte (feature 003, T043-T044; RN-10, D-13, D-14).

- 3D: caixa cortadora do volume afundado (não a malha do agregado, que pode ser pesada ou aberta), oculta e marcada
  `IS_CUTTING_OBJ`, e um modificador `BOOLEAN` DIFFERENCE `EXACT` no pai, depois do Geometry Nodes.
- Furo real: com o pai `GeoNodeCutpart` e o agregado afundando pela face da espessura (±Z), um `CPM_CUTOUT`
  "Agregado: <nome>" no pai, que o plano de corte exporta em `machining`.
Desligar remove tudo; a malha do pai nunca é alterada de forma destrutiva.
"""

import bmesh  # type: ignore
import bpy  # type: ignore

from ..data.i18n import tr
from .. import compat, hb_types
from ..cutting import machining
from . import apply, limits

BOOL_PREFIX = "Agregado (furo): "
CUTTER_SUFFIX = " - Recorte"
BOOL_KEY, CUTOUT_KEY = 'btm_perforate_bool', 'btm_perforate_cutout'    # nome com que cada modificador foi criado
EPSILON = 0.001       # o cortador passa 1 mm além da face, para não ficar coplanar


def _cutpart_mod(obj):
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and mod.node_group.name.split('.')[0] == 'GeoNodeCutpart':
            return mod
    return None


def real_hole_reason(obj):
    """Motivo de o furo real não ser possível, ou None."""
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    if parent is None or _cutpart_mod(parent) is None:
        return tr("O pai não é uma peça do plano de corte")
    if agg.face not in ('POS_Z', 'NEG_Z'):
        return tr("O furo real só vale quando o agregado entra pela face da chapa (topo ou base da peça)")
    return None


def _box_mesh(mesh, lo, hi):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = [lo[i] + (v.co[i] + 0.5) * (hi[i] - lo[i]) for i in range(3)]
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def _expanded(sunk, parent_box, face):
    """Volume afundado, passando `EPSILON` além da face de entrada e (se atravessa) da face oposta."""
    lo, hi = list(sunk[0]), list(sunk[1])
    n, sign, _u, _v = limits.face_axes(face)
    if sign > 0:
        hi[n] += EPSILON
        if lo[n] <= parent_box[0][n] + 1e-9:
            lo[n] -= EPSILON
    else:
        lo[n] -= EPSILON
        if hi[n] >= parent_box[1][n] - 1e-9:
            hi[n] += EPSILON
    return tuple(lo), tuple(hi)


def _remove_boolean(obj):
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    if parent is not None:
        mod = parent.modifiers.get(BOOL_PREFIX + obj.name)
        if mod is not None:
            parent.modifiers.remove(mod)
    cutter = agg.cutter
    if cutter is not None:
        mesh = cutter.data
        bpy.data.objects.remove(cutter, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        agg.cutter = None


def _remove_cutout(obj):
    parent = obj.btm_aggregate.parent_ref
    if parent is None:
        return
    mod = parent.modifiers.get(machining.AGGREGATE_PREFIX + obj.name)
    if mod is not None:
        parent.modifiers.remove(mod)


def _sync_boolean(obj, sunk, parent_box):
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    lo, hi = _expanded(sunk, parent_box, agg.face)
    cutter = agg.cutter
    if cutter is None:
        mesh = bpy.data.meshes.new(obj.name + CUTTER_SUFFIX)
        cutter = bpy.data.objects.new(obj.name + CUTTER_SUFFIX, mesh)
        for collection in parent.users_collection:
            collection.objects.link(cutter)
        cutter.parent = parent
        cutter['IS_CUTTING_OBJ'] = True
        cutter.display_type = 'WIRE'
        cutter.hide_render = True
        cutter.hide_set(True)
        agg.cutter = cutter
    key = [round(v, 6) for v in lo + hi]
    if list(cutter.get('btm_box', [])) != key:          # só refaz quando muda (evita laço com o depsgraph)
        _box_mesh(cutter.data, lo, hi)
        cutter['btm_box'] = key
    name = BOOL_PREFIX + obj.name
    mod = parent.modifiers.get(name)
    if mod is None:
        mod = parent.modifiers.new(name=name, type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
    mod.object = cutter


def _sync_cutout(obj, sunk):
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    mod_cut = _cutpart_mod(parent)
    mirror_y = bool(compat.try_get_gn_input(mod_cut, 'Mirror Y', False))
    mirror_z = bool(compat.try_get_gn_input(mod_cut, 'Mirror Z', False))
    thickness = compat.try_get_gn_input(mod_cut, 'Thickness', 0.0) or 0.0
    (x0, y0, _z0), (x1, y1, _z1) = sunk
    if mirror_y:
        y0, y1 = -y1, -y0
    depth = min(limits.size(sunk)[2], thickness)
    name = machining.AGGREGATE_PREFIX + obj.name
    mod = parent.modifiers.get(name)
    if mod is None:
        cpm = hb_types.GeoNodeCutpart(parent).add_part_modifier('CPM_CUTOUT', name)
        mod = cpm.mod
    for socket, value in (('X', x0), ('End X', x1), ('Y', y0), ('End Y', y1), ('Route Depth', depth),
                          ('Flip Z', (agg.face == 'NEG_Z') != mirror_z)):
        current = compat.try_get_gn_input(mod, socket)
        if current is None or (abs(float(current) - float(value)) > 1e-7):
            compat.try_set_gn_input(mod, socket, value)
    if not (mod.show_viewport and mod.show_render):
        mod.show_viewport = mod.show_render = True


def _old_boolean(obj, parent):
    old = parent.modifiers.get(obj.get(BOOL_KEY, ""))
    if old is None and obj.btm_aggregate.cutter is not None:      # arquivo antigo: o modificador do mesmo cortador
        old = next((m for m in parent.modifiers if m.type == 'BOOLEAN' and m.name.startswith(BOOL_PREFIX)
                    and m.object == obj.btm_aggregate.cutter), None)
    return old


def _old_cutout(obj, parent):
    old = parent.modifiers.get(obj.get(CUTOUT_KEY, ""))
    if old is None:                       # arquivo antigo: o único recorte de agregado cujo nome não é de objeto algum
        orphans = [m for m in parent.modifiers if m.name.startswith(machining.AGGREGATE_PREFIX)
                   and m.name[len(machining.AGGREGATE_PREFIX):] not in bpy.data.objects]
        old = orphans[0] if len(orphans) == 1 else None
    return old


def _follow_rename(obj, parent):
    """Agregado renomeado: os modificadores do furo passam a ter o nome novo, em vez de nascer outros e o antigo
    continuar no pai e na usinagem (EC-09)."""
    for find, prefix, key in ((_old_boolean, BOOL_PREFIX, BOOL_KEY), (_old_cutout, machining.AGGREGATE_PREFIX,
                                                                      CUTOUT_KEY)):
        new = prefix + obj.name
        old = find(obj, parent)
        if old is not None and old.name != new and parent.modifiers.get(new) is None:
            old.name = new
        if parent.modifiers.get(new) is not None:
            obj[key] = new
    cutter = obj.btm_aggregate.cutter
    if cutter is not None and cutter.name != obj.name + CUTTER_SUFFIX:
        cutter.name = obj.name + CUTTER_SUFFIX


def sync(obj):
    """Deixa recorte 3D e furo real de acordo com `perforate`/`real_hole` e a posição atual."""
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    if parent is None:
        return
    _follow_rename(obj, parent)
    parent_box = apply.local_box(parent)
    sunk = limits.sunk_box(parent_box, apply.current_box(obj), agg.face) if agg.perforate else None
    if sunk is None:
        _remove_boolean(obj)
        _remove_cutout(obj)
        return
    _sync_boolean(obj, sunk, parent_box)
    if agg.real_hole and real_hole_reason(obj) is None:
        _sync_cutout(obj, sunk)
    else:
        _remove_cutout(obj)
