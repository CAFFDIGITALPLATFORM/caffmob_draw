"""Verificação de colisão de corpo na cena (feature 004, T036, T037; D-13, D-14, D-16, RN-11 a RN-14).

`collect` monta a lista de itens para o núcleo puro (`rules.py`):
- itens: módulos (raiz), geometrias, eletrodomésticos, agregados, portas e janelas de ambiente e malhas soltas;
- estáticos: paredes (as duas camadas), obstáculos, piso e teto.
Peças e frentes de módulo não entram sozinhas: a caixa da raiz cobre o módulo. Ficam de fora cortadores, anotações,
cotas e objetos ocultos.

Cada item leva a caixa orientada da caixa local avaliada. Quando o par envolve parede, obstáculo, abertura ou malha
solta, a sobreposição é confirmada pela malha real (`BVHTree.overlap`), o que respeita o vão de uma porta na parede.

`check_all` grava o resultado em `WindowManager.btm_collision`, só para o diagnóstico técnico aberto por botão
(feature 066, RF-024). O aviso depois do movimento (`check_moved`, RF-23 da 004) saiu: quem impede a penetração é o
guarda (`guard.py`), em silêncio.

Feature 066 (D-09): qualquer malha, curva, texto ou metaball visível com corpo é obstáculo, com ou sem pai.
"""

from mathutils import Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

from ..selection import classify
from . import obb, rules

_SKIP_TAGS = ('IS_CUTTING_OBJ', 'IS_2D_ANNOTATION', 'IS_DIMENSION', 'IS_SNAP_LINE', 'obj_x')
BODY_TYPES = {'MESH', 'CURVE', 'FONT', 'META'}
_FINE_KINDS = {rules.WALL, rules.OBSTACLE}


class _Entry:
    __slots__ = ('item', 'obj', 'fine')

    def __init__(self, item, obj, fine):
        self.item, self.obj, self.fine = item, obj, fine


def _skip(obj):
    if getattr(getattr(obj, 'btm_member', None), 'role', '') == 'CUTTER':
        return True
    if any(obj.get(tag) for tag in _SKIP_TAGS):
        return True
    try:
        return obj.hide_viewport or not obj.visible_get()
    except RuntimeError:
        return True


def _local_body_box(obj, depsgraph):
    # 066 RF-002: no 5.2 a caixa avaliada da curva pode incluir uma expansão que a malha não tem.
    # Usa a conversão temporária, também para texto e metaball, sem aplicar modificadores no original.
    if obj.type in {'CURVE', 'FONT', 'META'}:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            if mesh is not None and mesh.vertices:
                return (tuple(min(v.co[k] for v in mesh.vertices) for k in range(3)),
                        tuple(max(v.co[k] for v in mesh.vertices) for k in range(3)))
            return (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)
        finally:
            evaluated.to_mesh_clear()
    from ..stick import apply as stick_apply
    return stick_apply.local_box(obj, depsgraph)


def box_of(obj, depsgraph):
    """Caixa orientada (mundo) da caixa local avaliada do objeto."""
    lo, hi = _local_body_box(obj, depsgraph)
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
    if agg is not None and agg.is_aggregate and agg.kind == 'LEAF':
        for node in classify._ancestors(obj):     # folha de porta/janela: a caixa e a parede dela (questions.md, 68)
            if node.get('IS_ENTRY_DOOR_BP') or node.get('IS_WINDOW_BP'):
                names.add(node.name)
                if node.parent is not None:
                    names.add(node.parent.name)
                break
    st = getattr(obj, 'btm_stick', None)
    if st is not None and st.is_stuck and st.host is not None:
        names.update({st.host.name, _root_name(st.host)})
    parent = obj.parent
    if parent is not None and (parent.get('IS_WALL_BP') or parent.get('btm_wall_segments')):
        if obj.get('IS_ENTRY_DOOR_BP') or obj.get('IS_WINDOW_BP') or classify.classify(obj).kind == classify.WINDOW:
            names.add(parent.name)
    return frozenset(names)


def _top_name(obj):
    """Nome do ancestral mais alto: peças de uma mesma hierarquia solta não se bloqueiam (RF-005)."""
    while obj.parent is not None:
        obj = obj.parent
    return obj.name


def _has_body(obj, depsgraph=None):
    """Malha comum, curva ou texto com corpo (feature 066, D-09): caixa avaliada com volume; plano sem espessura
    (fundo fotográfico, curva sem extrusão) não é obstáculo."""
    if obj.type not in BODY_TYPES or obj.display_type in {'WIRE', 'BOUNDS'}:
        return False
    try:
        if depsgraph is not None and obj.type in {'CURVE', 'FONT', 'META'}:
            corners = _local_body_box(obj, depsgraph)
        else:
            corners = [tuple(c) for c in obj.bound_box]
    except (AttributeError, ReferenceError):
        return False
    size = [max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3)]
    return min(abs(size[i] * obj.scale[i]) for i in range(3)) > 1e-6


def _kind_of(obj, depsgraph=None):
    """(tipo para as regras, raiz, confirmar pela malha) ou None quando o objeto não entra sozinho."""
    owner = getattr(getattr(obj, 'btm_member', None), 'owner', None)
    if owner is not None or obj.get('IS_AUTHORED_CABINET'):
        root = owner if owner is not None else obj
        return (rules.ITEM, root.name, True) if _has_body(obj, depsgraph) else None
    if obj.get('btm_wall_segments') and obj.type == 'MESH':
        return rules.WALL, obj.name, True
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return rules.ITEM, '', True
    if obj.get('IS_APPLIANCE'):
        return rules.ITEM, obj.name, False
    if obj.type == 'EMPTY' and classify.free_group(obj) is obj:
        return rules.ITEM, _top_name(obj), True     # grupo solto (SketchUp, biblioteca de objetos; pergunta 35)
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
    if kind == classify.OTHER and _has_body(obj, depsgraph):
        return rules.ITEM, _top_name(obj), True     # qualquer corpo físico, com ou sem pai (066, RF-002, RN-05)
    return None


def entry_of(obj, depsgraph):
    """Item de colisão do objeto (com a caixa avaliada no mundo), ou None quando ele não entra sozinho."""
    if _skip(obj):
        return None
    found = _kind_of(obj, depsgraph)
    if found is None:
        return None
    kind, root, fine = found
    item = rules.Item(obj.name, box_of(obj, depsgraph), kind=kind, root=root, linked=_links(obj),
                      override=_override(obj))
    return _Entry(item, obj, fine or kind in _FINE_KINDS)


def collect(scene, depsgraph):
    entries = []
    for obj in scene.objects:
        entry = entry_of(obj, depsgraph)
        if entry is not None:
            entries.append(entry)
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
        if obj.type in BODY_TYPES:
            evaluated = obj.evaluated_get(self.depsgraph)
            try:
                mesh = evaluated.to_mesh()
            except RuntimeError:
                mesh = None
            if mesh is not None:
                try:
                    matrix = evaluated.matrix_world
                    verts = [matrix @ v.co for v in mesh.vertices]
                    mesh.calc_loop_triangles()     # triângulos: com quads, faces coplanares sobrepostas escapam
                    polys = [tuple(t.vertices) for t in mesh.loop_triangles]
                finally:
                    evaluated.to_mesh_clear()
                if verts and polys:
                    return BVHTree.FromPolygons(verts, polys)
        corners = [Vector(c) for c in entry.item.box.corners()]
        quads = ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3))
        faces = [tri for a, b, c, d in quads for tri in ((a, b, c), (a, c, d))]
        return BVHTree.FromPolygons(corners, faces)


def _inside(tree, point):
    """O ponto está dentro da malha fechada? Paridade dos cruzamentos de um raio em +X."""
    direction, origin, hits = Vector((1.0, 0.0, 0.0)), Vector(point), 0
    for _ in range(256):
        location, _normal, _index, _distance = tree.ray_cast(origin, direction)
        if location is None:
            break
        hits += 1
        origin = location + direction * 1e-5
    return hits % 2 == 1


def _confirm(by_name, meshes):
    def confirm(a, b):
        ea, eb = by_name[a.name], by_name[b.name]
        if not (ea.fine or eb.fine):
            return True
        ta, tb = meshes.tree(ea), meshes.tree(eb)
        if ta is None or tb is None:
            return True
        if ta.overlap(tb):
            return True
        # Sem cruzamento de faces: um pode estar inteiro dentro do outro (contenção total, pergunta 33).
        return _inside(tb, a.box.center) or _inside(ta, b.box.center)
    return confirm


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


def _redraw(context):
    try:
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type in {'VIEW_3D', 'PROPERTIES'}:
                    area.tag_redraw()
    except AttributeError:
        pass
