"""Verificação de colisão de corpo na cena (feature 004, T036, T037; D-13, D-14, D-16, RN-11 a RN-14).

`collect` monta a lista de itens para o núcleo puro (`rules.py`):
- itens: módulos (raiz), geometrias, eletrodomésticos, agregados, portas e janelas de ambiente e malhas soltas;
- estáticos: paredes (as duas camadas), obstáculos, piso e teto.
Peças e frentes de módulo não entram sozinhas: a caixa da raiz cobre o módulo. Ficam de fora cortadores, anotações,
cotas e objetos ocultos.

Cada item leva a caixa orientada da caixa local avaliada. Quando o par envolve parede, obstáculo, abertura ou malha
solta, a sobreposição é confirmada pela malha real (`BVHTree.overlap`), o que respeita o vão de uma porta na parede.

`check_all` grava o resultado em `WindowManager.btm_collision`; `check_moved` refaz só os pares de quem acabou de se
mover (assentar do grudar) e avisa "Colide com <outro>" sem mover nada (RF-23).
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import obb, rules

_SKIP_TAGS = ('IS_CUTTING_OBJ', 'IS_2D_ANNOTATION', 'IS_DIMENSION', 'obj_x')
_FINE_KINDS = {rules.WALL, rules.OBSTACLE}


class _Entry:
    __slots__ = ('item', 'obj', 'fine')

    def __init__(self, item, obj, fine):
        self.item, self.obj, self.fine = item, obj, fine


def _skip(obj):
    if any(obj.get(tag) for tag in _SKIP_TAGS):
        return True
    try:
        return obj.hide_viewport or not obj.visible_get()
    except RuntimeError:
        return True


def box_of(obj, depsgraph):
    """Caixa orientada (mundo) da caixa local avaliada do objeto."""
    from ..stick import apply as stick_apply
    lo, hi = stick_apply.local_box(obj, depsgraph)
    loc, rot, scale = obj.matrix_world.decompose()
    axes = tuple(tuple(c) for c in rot.to_matrix().col)
    lo = tuple(lo[i] * scale[i] for i in range(3))
    hi = tuple(hi[i] * scale[i] for i in range(3))
    lo, hi = tuple(min(lo[i], hi[i]) for i in range(3)), tuple(max(lo[i], hi[i]) for i in range(3))
    return obb.from_box(tuple(loc), axes, lo, hi)


def _override(obj):
    plane = getattr(obj, 'btm_plane', None)
    return plane.collision_override if plane is not None else 'INHERIT'


def _root_name(obj):
    if obj is None:
        return ''
    root = classify.movable_root(obj) or classify.reference_root(obj)
    return root.name if root is not None else obj.name


def _links(obj):
    names = set()
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate and agg.parent_ref is not None:
        names.update({agg.parent_ref.name, _root_name(agg.parent_ref)})
    st = getattr(obj, 'btm_stick', None)
    if st is not None and st.is_stuck and st.host is not None:
        names.update({st.host.name, _root_name(st.host)})
    parent = obj.parent
    if parent is not None and (parent.get('IS_WALL_BP') or parent.get('btm_wall_segments')):
        if obj.get('IS_ENTRY_DOOR_BP') or obj.get('IS_WINDOW_BP') or classify.classify(obj).kind == classify.WINDOW:
            names.add(parent.name)
    return frozenset(names)


def _kind_of(obj):
    """(tipo para as regras, raiz, confirmar pela malha) ou None quando o objeto não entra sozinho."""
    if obj.get('btm_wall_segments') and obj.type == 'MESH':
        return rules.WALL, obj.name, True
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return rules.ITEM, '', True
    if obj.get('IS_APPLIANCE'):
        return rules.ITEM, obj.name, False
    info = classify.classify(obj)
    if info is None or info.obj is not obj:
        return None
    kind = info.kind
    if kind == classify.MODULE:
        return rules.ITEM, obj.name, False
    if kind == classify.GEOMETRY:
        return rules.ITEM, obj.name, False
    if kind in (classify.ROOM_DOOR, classify.WINDOW):
        return rules.ITEM, obj.name, True
    if kind == classify.WALL:
        return rules.WALL, obj.name, True
    if kind == classify.OBSTACLE:
        return rules.OBSTACLE, obj.name, True
    if kind == classify.FLOOR:
        return rules.FLOOR, obj.name, False
    if kind == classify.CEILING:
        return rules.CEILING, obj.name, False
    if kind == classify.OTHER and obj.type == 'MESH' and obj.parent is None and obj.display_type not in {'WIRE', 'BOUNDS'}:
        return rules.ITEM, obj.name, True
    return None


def collect(scene, depsgraph):
    entries = []
    for obj in scene.objects:
        if _skip(obj):
            continue
        found = _kind_of(obj)
        if found is None:
            continue
        kind, root, fine = found
        item = rules.Item(obj.name, box_of(obj, depsgraph), kind=kind, root=root, linked=_links(obj),
                          override=_override(obj))
        entries.append(_Entry(item, obj, fine or kind in _FINE_KINDS))
    return entries


class _Meshes:
    """BVH das malhas avaliadas no mundo, sob demanda (mesmo cálculo de `inspection/interference._Targets`)."""

    def __init__(self, depsgraph):
        self.depsgraph = depsgraph
        self._trees = {}

    def tree(self, entry):
        key = entry.obj.as_pointer()
        if key not in self._trees:
            self._trees[key] = self._build(entry)
        return self._trees[key]

    def _build(self, entry):
        obj = entry.obj
        if obj.type == 'MESH':
            evaluated = obj.evaluated_get(self.depsgraph)
            try:
                mesh = evaluated.to_mesh()
            except RuntimeError:
                mesh = None
            if mesh is not None:
                try:
                    matrix = evaluated.matrix_world
                    verts = [matrix @ v.co for v in mesh.vertices]
                    polys = [tuple(p.vertices) for p in mesh.polygons]
                finally:
                    evaluated.to_mesh_clear()
                if verts and polys:
                    return BVHTree.FromPolygons(verts, polys)
        corners = [Vector(c) for c in entry.item.box.corners()]
        faces = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))
        return BVHTree.FromPolygons(corners, faces)


def _confirm(by_name, meshes):
    def confirm(a, b):
        ea, eb = by_name[a.name], by_name[b.name]
        if not (ea.fine or eb.fine):
            return True
        ta, tb = meshes.tree(ea), meshes.tree(eb)
        return bool(ta.overlap(tb)) if ta is not None and tb is not None else True
    return confirm


def enabled(scene):
    settings = getattr(scene, 'btm_settings', None)
    return settings is None or settings.collision_global


def find(context, only=None):
    """(ocorrências, itens verificados) da cena; `only` restringe aos pares que envolvem esses nomes."""
    depsgraph = context.evaluated_depsgraph_get()
    entries = collect(context.scene, depsgraph)
    by_name = {e.item.name: e for e in entries}
    found = rules.conflicts([e.item for e in entries], confirm=_confirm(by_name, _Meshes(depsgraph)), only=only)
    return found, entries


def _store(state, found, names, scope):
    state.items.clear()
    for c in found:
        row = state.items.add()
        row.kind, row.name_a, row.name_b = c.kind, c.name_a, c.name_b
        row.depth, row.push, row.location = c.depth, c.push, c.location
    state.index = 0
    state.checked = len(names)
    state.checked_names = "\n".join(sorted(names))
    state.scope = scope
    state.stale = False
    state.error = ""
    from . import stale
    stale.reset()


def selected_names(context):
    names = set()
    for obj in context.selected_objects:
        root = classify.movable_root(obj) or obj
        names.add(root.name)
    return names


def check_all(context, scope='ALL'):
    """Verifica a cena inteira (`ALL`) ou só o selecionado e o que ele toca (`SELECTED`); grava no estado."""
    state = context.window_manager.btm_collision
    try:
        only = selected_names(context) if scope == 'SELECTED' else None
        found, entries = find(context, only)
    except Exception as exc:          # RF-25: falha vira erro visível, nunca "sem colisões"
        state.items.clear()
        state.error = str(exc) or exc.__class__.__name__
        state.stale = False
        return None
    names = only if only is not None else {e.item.name for e in entries}
    _store(state, found, names, scope)
    _redraw(context)
    return found


def check_moved(objs):
    """Depois de um movimento: refaz os pares de quem se moveu; colidindo, avisa e destaca (RF-23, D-16)."""
    context = bpy.context
    if not enabled(context.scene):
        return []
    names = {o.name for o in objs if o.name in bpy.data.objects}
    if not names:
        return []
    roots = set(names)
    for obj in objs:                      # o que se move junto (agregados, itens grudados) também é verificado
        names.update(c.name for c in obj.children_recursive)
    try:
        found, _entries = find(context, names)
    except Exception:
        return []
    state = context.window_manager.btm_collision
    keep = [(r.kind, r.name_a, r.name_b, r.depth, tuple(r.push), tuple(r.location)) for r in state.items
            if r.name_a not in names and r.name_b not in names]
    state.items.clear()
    for kind, a, b, depth, push, location in keep:
        row = state.items.add()
        row.kind, row.name_a, row.name_b, row.depth, row.push, row.location = kind, a, b, depth, push, location
    for c in found:
        row = state.items.add()
        row.kind, row.name_a, row.name_b = c.kind, c.name_a, c.name_b
        row.depth, row.push, row.location = c.depth, c.push, c.location
    if state.checked < 0:                  # sem "Verificar" antes: estes itens passam a ser os verificados (EC-04)
        state.checked = len(roots)
        state.checked_names = "\n".join(sorted(roots))
    from . import stale
    stale.rechecked(names)
    if found:
        from ..ui import save_feedback
        for c in found:
            moved, other = (c.name_a, c.name_b) if c.name_a in names else (c.name_b, c.name_a)
            save_feedback.show(tr("{} colide com {}").format(moved, other))
    _redraw(context)
    return found


def _redraw(context):
    try:
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type in {'VIEW_3D', 'PROPERTIES'}:
                    area.tag_redraw()
    except AttributeError:
        pass
