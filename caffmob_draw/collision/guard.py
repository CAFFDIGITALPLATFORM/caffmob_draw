"""Guarda de colisão: o movimento para no primeiro contato, em silêncio (feature 066, T039/T071; D-03, D-04, D-05).

Handler `depsgraph_update_post` (`@persistent`, com trava de reentrada). Limita só o deslocamento direto: G ou gizmo
de translação em andamento, com eixo travado e digitação dentro do G (`_direct_move_running`). Ferramentas assistidas
(Encostar, ímã, espelhar, posicionar), edição dimensional, giro, escala, painel e Python têm o destino respeitado
(BUG-20261023-TAMR, RF01 a RF04 da auditoria de desempenho; substitui RF-001 e RF-003 da 066 nesse ponto).

- Conjunto móvel: os objetos que se moveram sem que um ancestral também se movesse, e que são donos do próprio
  movimento (módulo, geometria, obstáculo, porta/janela, agregado que não é folha, corpo solto). Peças e frentes
  internas se movem com o componente (regenerar, abrir porta) e ficam de fora. Objetos movidos juntos com o mesmo
  deslocamento andam como um conjunto só e não se bloqueiam.
- Corpo efetivo (RF-005): cada malha, curva ou texto visível da hierarquia do móvel, com a caixa dela.
- Obstáculos: o índice de `scan.entry_of` (qualquer corpo físico, D-09), guardado por `session_uid` e refeito só para
  o que o depsgraph diz que mudou (RF-011).
- Translação: varre sempre da última pose válida até a pedida (`rules.first_contact`), então digitar 2 m contra uma
  chapa de 15 mm para antes dela (RF-004). Par com vão (parede, malha solta) é conferido pela malha real com
  `aggregates/sweep.sweep` (RF-006). Parado pela caixa, desliza na tangente do contato, sem sair dos eixos que o
  movimento já usava (eixo travado) e sem empurrar nada (RF-007).
- Esc volta à pose de antes do gesto; Desfazer, Refazer e abrir arquivo recomeçam da cena como está (RF-008).
- Falha segura: qualquer exceção devolve a última pose válida e vai só para o console.
- Silêncio (RF-021): nada é desenhado, escrito na barra de status ou relatado por contato.

Os modais que posicionam por conta própria (posicionar da biblioteca, editor de módulo, janela Mover Sobre) não são
corrigidos; a pose deles é aceita. A edição dimensional (`reconfigure`) não é recusada por sobreposição: erro
restaura e propaga.
"""

import math
import traceback
from contextlib import contextmanager

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Matrix, Vector  # type: ignore
from mathutils.bvhtree import BVHTree  # type: ignore

from ..selection import classify
from . import obb, rules, scan

PROBE_STEP = 0.005           # m: passo da conferência pela malha
PROBE_TOLERANCE = 0.00005     # m: precisão da parada refinada
MAX_PROBES = 400
_SAME = 1e-6                 # diferença de matriz que não conta como movimento
_MANAGED = {'caffmob.move_over_dialog', 'caffmob.cabinet_editor_modal'}
_BOX_TRIS = tuple(tri for a, b, c, d in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4),
                                         (1, 5, 7, 3)) for tri in ((a, b, c), (a, c, d)))

_last = {}           # session_uid → matriz de mundo da última pose válida
_anchor = {}         # session_uid → pose de antes do gesto em andamento (o Esc volta para ela)
_parent = {}         # session_uid → session_uid do pai na última pose (0 = sem pai)
_busy = [False]
_reported = [False]


def enabled(scene):
    settings = getattr(scene, 'btm_settings', None)
    return settings is None or bool(settings.block_penetration)


# Índice dos obstáculos ------------------------------------------------------------------------------------------
def _visible(obj):
    try:
        return obj.visible_get()
    except RuntimeError:
        return False


class _Index:
    def __init__(self):
        self.entries = {}       # session_uid → scan._Entry
        self.aabbs = {}         # session_uid → caixa alinhada ao mundo
        self.trees = {}         # session_uid → BVHTree da malha avaliada no mundo
        self.pending = {}       # session_uid → objeto que mudou e ainda não foi recalculado
        self.signature = None
        self.depsgraph = None

    def reset(self):
        self.entries.clear()
        self.aabbs.clear()
        self.trees.clear()
        self.pending.clear()
        self.signature = None

    def _put(self, uid, obj, depsgraph):
        self.trees.pop(uid, None)
        try:
            entry = scan.entry_of(obj, depsgraph)
        except ReferenceError:
            entry = None
        if entry is None:
            self.entries.pop(uid, None)
            self.aabbs.pop(uid, None)
        else:
            self.entries[uid] = entry
            self.aabbs[uid] = entry.item.box.aabb()

    def refresh(self, scene, depsgraph, dirty, full=False):
        """Marca o que mudou para recalcular sob demanda; o que se move junto com o conjunto nunca é calculado
        enquanto ele anda (é pulado como obstáculo)."""
        self.depsgraph = depsgraph
        # Objeto novo, apagado, renomeado, ocultado ou reexibido refaz tudo (ocultar não chega como update do objeto).
        objects = scene.objects
        signature = tuple((o.session_uid, o.name, _visible(o), scan._override(o), o.display_type) for o in objects)
        if full or signature != self.signature:
            self.reset()
            self.signature = signature
            self.depsgraph = depsgraph
            for obj in objects:
                self._put(obj.session_uid, obj, depsgraph)
            return
        for uid, obj in dirty.items():
            self.entries.pop(uid, None)
            self.aabbs.pop(uid, None)
            self.trees.pop(uid, None)
            self.pending[uid] = obj

    def near(self, box, skip):
        """Entradas cuja caixa toca `box` (alinhada ao mundo), fora as de `skip` (session_uid)."""
        for uid in [u for u in self.pending if u not in skip]:
            self._put(uid, self.pending.pop(uid), self.depsgraph)
        return [entry for uid, entry in self.entries.items()
                if uid not in skip and obb.aabb_overlap(box, self.aabbs[uid], rules.TOLERANCE)]

    def entry(self, uid):
        if uid in self.pending:
            self._put(uid, self.pending.pop(uid), self.depsgraph)
        return self.entries.get(uid)

    def tree(self, entry, depsgraph):
        uid = entry.obj.session_uid
        if uid not in self.trees:
            self.trees[uid] = scan._Meshes(depsgraph)._build(entry)
        return self.trees[uid]


_index = _Index()


# Conjunto móvel -------------------------------------------------------------------------------------------------
def _eligible(obj):
    """O objeto é dono do próprio movimento (o guarda limita) ou se move com outro (o guarda não mexe)?"""
    if scan._skip(obj):
        return False
    member = getattr(obj, 'btm_member', None)
    if getattr(member, 'owner', None) is not None:
        return False
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return agg.kind != 'LEAF'          # abrir folha é da onda 3 (RF-074)
    if obj.get('IS_APPLIANCE'):
        return True
    info = classify.classify(obj)
    if info is None or info.obj is not obj:
        return False
    return info.kind in (classify.MODULE, classify.GEOMETRY, classify.OBSTACLE, classify.ROOM_DOOR,
                         classify.WINDOW, classify.OTHER)


def _physical(obj):
    return (obj.type in scan.BODY_TYPES and obj.display_type not in {'WIRE', 'BOUNDS'} and not scan._skip(obj))


def _profile(obj):
    """(tipo, raiz, ligados, colisão) do conjunto: os do item do próprio objeto, ou os de um corpo solto."""
    entry = _index.entry(obj.session_uid)
    if entry is not None:
        item = entry.item
        return item.kind, item.group, item.linked, item.override
    root = obj.name if obj.get('IS_AUTHORED_CABINET') else scan._top_name(obj)
    return rules.ITEM, root, scan._links(obj), scan._override(obj)


def _body(obj, depsgraph):
    """Peças com corpo da hierarquia do móvel, na pose atual (RF-005)."""
    kind, root, linked, override = _profile(obj)
    items = []
    for piece in [obj] + _descendants(obj):
        if _physical(piece):
            items.append(rules.Item(piece.name, scan.box_of(piece, depsgraph), kind=kind, root=root,
                                    linked=linked, override=override))
    return items


def _moved_box(box, matrix):
    """Caixa levada por uma transformação afim (giro, escala nos eixos, translação)."""
    m3 = matrix.to_3x3()
    center = tuple(matrix @ Vector(box.center))
    axes, half = [], []
    for axis, h in zip(box.axes, box.half):
        v = m3 @ Vector(axis)
        length = v.length
        axes.append(tuple(v / length) if length > 1e-12 else axis)
        half.append(h * length)
    return obb.OBB(center, tuple(axes), tuple(half))


def _shift(items, delta):
    out = []
    for it in items:
        box = obb.OBB(tuple(it.box.center[k] + delta[k] for k in range(3)), it.box.axes, it.box.half)
        out.append(rules.Item(it.name, box, it.kind, it.root, it.linked, it.override))
    return out


def _carry(items, matrix):
    return [rules.Item(it.name, _moved_box(it.box, matrix), it.kind, it.root, it.linked, it.override)
            for it in items]


def _bounds(item_lists, grow=0.0):
    boxes = [it.box.aabb() for items in item_lists for it in items]
    lo = tuple(min(b[0][k] for b in boxes) - grow for k in range(3))
    hi = tuple(max(b[1][k] for b in boxes) + grow for k in range(3))
    return lo, hi


# Conferência pela malha -----------------------------------------------------------------------------------------
def _inside_box(box, point):
    d = tuple(point[k] - box.center[k] for k in range(3))
    return all(abs(sum(d[k] * box.axes[i][k] for k in range(3))) <= box.half[i] for i in range(3))


def _mesh_blocks(box, tree, other):
    """A caixa (encolhida pela tolerância: encostar não conta) entra na malha do obstáculo?"""
    shrunk = obb.OBB(box.center, box.axes, tuple(max(h - rules.TOLERANCE, 1e-6) for h in box.half))
    corners = [Vector(c) for c in shrunk.corners()]
    if BVHTree.FromPolygons(corners, _BOX_TRIS).overlap(tree):
        return True
    if scan._inside(tree, shrunk.center):
        return True
    return all(_inside_box(shrunk, c) for c in other.box.corners())


def _refiner(by_item, depsgraph, delta):
    """`refine` de `rules.first_contact`: par sem vão fica com a caixa; par com vão anda em passos pela malha."""
    length = math.sqrt(sum(d * d for d in delta))

    def refine(mover, obstacle, hit):
        entry = by_item.get(id(obstacle))
        if entry is None or not entry.fine:
            return True
        tree = _index.tree(entry, depsgraph)
        if tree is None:
            return True

        def at(t):
            return obb.OBB(tuple(mover.box.center[k] + delta[k] * t for k in range(3)), mover.box.axes,
                           mover.box.half)

        if _mesh_blocks(at(0.0), tree, obstacle):
            return None                                 # já penetrado pela malha: dá para sair
        start, end = max(0.0, hit.t_touch), min(1.0, hit.t_exit)
        if end <= start:
            return None
        count = max(1, math.ceil(length * (end - start) / PROBE_STEP))
        if count > MAX_PROBES:
            return max(0.0, hit.t_touch)     # orçamento esgotado: conserva a caixa, nunca alarga o passo
        from ..aggregates import sweep
        per_m = 1.0 / max(length, 1e-9)
        free = [start]

        def swept_probe(t):
            # Testa o volume inteiro entre amostras: uma peça fina não pode cair entre dois pontos livres.
            a = at(free[0])
            segment = tuple(delta[k] * (t - free[0]) for k in range(3))
            center = tuple(a.center[k] + segment[k] / 2 for k in range(3))
            half = tuple(a.half[i] + abs(sum(segment[k] * a.axes[i][k] for k in range(3))) / 2
                         for i in range(3))
            blocked = _mesh_blocks(obb.OBB(center, a.axes, half), tree, obstacle)
            if not blocked:
                free[0] = t
            return blocked

        reached, contact = sweep.sweep(start, end, swept_probe,
                                       (end - start) / count, PROBE_TOLERANCE * per_m)
        if not contact:
            return None                                 # passa pelo vão
        # A malha é conferida com a caixa encolhida pela tolerância: recua essa folga para parar no contato.
        stop = max(start, reached - rules.TOLERANCE * per_m)
        if stop - start <= (2.0 * rules.TOLERANCE + PROBE_TOLERANCE) * per_m:
            return True                                 # a malha toca onde a caixa toca: vale a caixa (e desliza)
        return stop

    return refine


def _deep(mover, entry, depsgraph):
    """Penetração além da tolerância, conferida pela malha quando o obstáculo tem vão."""
    found = obb.overlap(mover.box, entry.item.box)
    if found is None or found['depth'] <= rules.TOLERANCE + 1e-9:
        return False
    if not entry.fine:
        return True
    tree = _index.tree(entry, depsgraph)
    return tree is None or _mesh_blocks(mover.box, tree, entry.item)


def _new_penetration(now, before, entries, depsgraph):
    for entry in entries:
        for item_now, item_before in zip(now, before):
            if rules.excluded(item_now, entry.item):
                continue
            if _deep(item_now, entry, depsgraph) and not _deep(item_before, entry, depsgraph):
                return True
    return False


# Cálculo ---------------------------------------------------------------------------------------------------------
def _sweep(body, delta, entries, depsgraph, slide=True):
    """Deslocamento permitido (Vector) do corpo, da pose de `body`, pedindo `delta`."""
    by_item = {id(e.item): e for e in entries}
    obstacles = [e.item for e in entries]
    delta = Vector(delta)
    contact = rules.first_contact(body, tuple(delta), obstacles, _refiner(by_item, depsgraph, tuple(delta)))
    if contact is None:
        return delta
    applied = delta * contact.t
    if not slide or contact.normal is None:
        return applied
    normal = Vector(contact.normal)
    rest = delta * (1.0 - contact.t)
    tangent = rest - normal * rest.dot(normal)
    for k in range(3):                       # eixo travado: não ganha componente que o movimento não tinha
        if abs(delta[k]) < 1e-9:
            tangent[k] = 0.0
    if tangent.length < 1e-6:
        return applied
    moved = _shift(body, tuple(applied))
    second = rules.first_contact(moved, tuple(tangent), obstacles, _refiner(by_item, depsgraph, tuple(tangent)))
    return applied + tangent * (second.t if second is not None else 1.0)


def _translation_only(a, b):
    return all(abs(a[r][c] - b[r][c]) <= _SAME for r in range(3) for c in range(3))


def _same(a, b):
    return all(abs(a[r][c] - b[r][c]) <= _SAME for r in range(4) for c in range(4))


def _subtree_uids(objs):
    uids = set()
    for obj in objs:
        uids.add(obj.session_uid)
        uids.update(c.session_uid for c in _descendants(obj))
    return uids


def _resolve_translation(movers, depsgraph, moving):
    current = {o.session_uid: o.matrix_world.copy() for o in movers}
    first = movers[0]
    delta = current[first.session_uid].translation - _last[first.session_uid].translation
    body = []
    for obj in movers:
        body += _body(obj, depsgraph)
    if not body:
        return {}
    start = _shift(body, tuple(-delta))
    entries = _index.near(_bounds([start, body], grow=delta.length), moving)
    allowed = _sweep(start, delta, entries, depsgraph)
    if (allowed - delta).length <= _SAME:
        return {}
    out = {}
    for obj in movers:
        uid = obj.session_uid
        target = current[uid].copy()
        target.translation = _last[uid].translation + allowed
        out[uid] = target
    return out


def _resolve_pose(obj, depsgraph, moving):
    uid = obj.session_uid
    body = _body(obj, depsgraph)
    if not body:
        return {}
    before = _carry(body, _last[uid] @ obj.matrix_world.inverted_safe())
    entries = _index.near(_bounds([before, body]), moving)
    if _new_penetration(body, before, entries, depsgraph):
        return {uid: _last[uid].copy()}
    return {}


def _groups(movers):
    """Conjuntos que andam juntos: mesma translação e nada além dela; giro e escala vão um a um."""
    groups, poses = {}, []
    for obj in movers:
        uid = obj.session_uid
        cur, last = obj.matrix_world, _last[uid]
        if _translation_only(cur, last):
            key = tuple(round(cur.translation[k] - last.translation[k], 7) for k in range(3))
            groups.setdefault(key, []).append(obj)
        else:
            poses.append(obj)
    return list(groups.values()), poses


def _fail(movers):
    if not _reported[0]:
        _reported[0] = True
        print("CAFFMob Draw: falha no guarda de colisão; a última posição válida foi mantida")
        traceback.print_exc()
    return {o.session_uid: _last[o.session_uid].copy() for o in movers}


def _limit(movers, depsgraph):
    moving = _subtree_uids(movers)
    out = {}
    translations, poses = _groups(movers)
    for group in translations:
        try:
            out.update(_resolve_translation(group, depsgraph, moving))
        except Exception:                 # falha segura: nunca libera o atravessamento
            out.update(_fail(group))
    for obj in poses:
        try:
            out.update(_resolve_pose(obj, depsgraph, moving))
        except Exception:
            out.update(_fail([obj]))
    return out


def _write(obj, target):
    """Leva o objeto à pose `target` (mundo). Só translação: mexe em `location`, sem tocar giro e escala."""
    current = obj.matrix_world
    if _translation_only(current, target):
        world = target.translation - current.translation
        if world.length <= _SAME:
            return
        parent = Matrix.Identity(4)
        if obj.parent is not None:
            parent = obj.parent.matrix_world @ obj.matrix_parent_inverse
        obj.location = obj.location + parent.to_3x3().inverted_safe() @ world
    else:
        obj.matrix_world = target


# Modais ----------------------------------------------------------------------------------------------------------
def _self_managed():
    from .. import hb_placement
    from ..stick import settle
    try:
        windows = bpy.context.window_manager.windows
    except AttributeError:
        return False
    for window in windows:
        for op in getattr(window, 'modal_operators', ()):
            if settle._idname(op) in _MANAGED or isinstance(op, hb_placement.PlacementMixin):
                return True
    return False


def _gesture_running():
    from ..stick import apply
    return apply.modal_running()


def _direct_move_running():
    """G ou gizmo de translação em andamento: o único movimento que o guarda geral limita. Ferramentas assistidas
    (Encostar, ímã, espelhar, posicionar) e a edição dimensional têm o destino respeitado (BUG-20261023-TAMR)."""
    from ..stick import settle
    try:
        windows = bpy.context.window_manager.windows
    except AttributeError:
        return False
    for window in windows:
        for op in getattr(window, 'modal_operators', ()):
            name = settle._idname(op)
            if name == 'transform.translate' or (name == 'transform.transform'
                                                 and getattr(op.properties, 'mode', '') == 'TRANSLATION'):
                return True
    return False


# Handler ---------------------------------------------------------------------------------------------------------
def _parent_uid(obj):
    return obj.parent.session_uid if obj.parent is not None else 0


_kids = [None]       # pai (session_uid) → filhos, montado uma vez por chamada (`Object.children` varre tudo)


def _children_map():
    kids = {}
    for obj in bpy.data.objects:
        if obj.parent is not None:
            kids.setdefault(obj.parent.session_uid, []).append(obj)
    return kids


def _descendants(obj):
    """Hierarquia abaixo do objeto."""
    kids = _kids[0] if _kids[0] is not None else _children_map()
    out, stack = [], list(kids.get(obj.session_uid, ()))
    while stack:
        node = stack.pop()
        out.append(node)
        stack.extend(kids.get(node.session_uid, ()))
    return out


def _ancestor_in(obj, uids):
    node = obj.parent
    while node is not None:
        if node.session_uid in uids:
            return True
        node = node.parent
    return False


def _process(scene, depsgraph):
    updated, moved, full = {}, {}, False
    geometry_ids = set()
    for update in depsgraph.updates:
        data = update.id
        if isinstance(data, bpy.types.Object):
            obj = data.original
            updated[obj.session_uid] = obj
            if update.is_updated_transform:
                moved[obj.session_uid] = obj
        elif update.is_updated_geometry:
            geometry_ids.add(data.original.session_uid)
        elif isinstance(data, bpy.types.Collection):
            full = True
    if geometry_ids:
        for obj in scene.objects:
            if obj.data is not None and obj.data.session_uid in geometry_ids:
                updated[obj.session_uid] = obj
    if not updated and not full:
        return
    if moved and getattr(scene.btm_settings, 'show_side_dimensions', False):
        from ..overlays import side_cotas
        side_cotas.bind(bpy.context)
    dirty = dict(updated)
    for obj in updated.values():
        if obj.parent is not None and obj.parent.session_uid in updated:
            continue                          # os filhos dele já vêm pelo ancestral
        for child in _descendants(obj):
            dirty[child.session_uid] = child
    for obj in updated.values():
        node = obj.parent
        while node is not None:
            dirty[node.session_uid] = node       # a caixa do conjunto muda quando uma peça muda
            node = node.parent
    live = {o.session_uid for o in scene.objects}
    for uid in set(_last) - live:
        _last.pop(uid, None)
        _parent.pop(uid, None)
        _anchor.pop(uid, None)
    _index.refresh(scene, depsgraph, dirty, full)
    corrected = {}
    if enabled(scene) and moved and not _self_managed() and _direct_move_running():
        movers = []
        for uid, obj in moved.items():
            last = _last.get(uid)
            if last is None or _same(obj.matrix_world, last) or _ancestor_in(obj, moved):
                continue
            if _parent.get(uid, 0) != _parent_uid(obj):
                continue                     # trocar de pai é estrutura (agrupar, desfazer grupo), não movimento
            anchor = _anchor.get(uid)
            if anchor is not None and _same(obj.matrix_world, anchor):
                continue                     # Esc: volta à pose de antes do gesto
            if _eligible(obj):
                movers.append(obj)
        if movers and _gesture_running():
            for obj in movers:
                _anchor.setdefault(obj.session_uid, _last[obj.session_uid].copy())
        if movers:
            corrected = _limit(movers, depsgraph)
            for uid, target in corrected.items():
                _write(moved[uid], target)
    if not _gesture_running():
        _anchor.clear()
    for uid, obj in dirty.items():
        try:
            _last[uid] = corrected[uid] if uid in corrected else obj.matrix_world.copy()
            _parent[uid] = _parent_uid(obj)
        except ReferenceError:
            _last.pop(uid, None)
            _parent.pop(uid, None)


@persistent
def on_depsgraph_update(scene, depsgraph):
    if _busy[0]:
        return
    if not any(isinstance(u.id, (bpy.types.Object, bpy.types.Collection)) or u.is_updated_geometry
               for u in depsgraph.updates):
        return                            # nada que mova ou mude um corpo: sem varrer o arquivo (BUG-20261023-TU4V)
    _busy[0] = True
    try:
        _kids[0] = _children_map()
        _process(scene, depsgraph)
    except Exception:
        if not _direct_move_running():
            _index.reset()
            return
        # Inclui falha na coleta ou no índice, antes de `_limit`: nenhum G/gizmo fica sem proteção.
        movers = [o for o in scene.objects if o.session_uid in _last and _eligible(o)
                  and not _same(o.matrix_world, _last[o.session_uid])]
        for obj in movers:
            _write(obj, _fail([obj])[obj.session_uid])
        _index.reset()
    finally:
        _kids[0] = None
        _busy[0] = False


# API para quem move por conta própria ---------------------------------------------------------------------------
@contextmanager
def suspended():
    """O guarda não corrige nada dentro do bloco; quem move confere e chama `accept` (ímã do assentar)."""
    previous = _busy[0]
    _busy[0] = True
    try:
        yield
    finally:
        _busy[0] = previous


def accept(obj, matrix=None):
    """A pose atual (ou `matrix`) passa a ser a última válida do objeto e da hierarquia dele."""
    _last[obj.session_uid] = (matrix if matrix is not None else obj.matrix_world).copy()
    _parent[obj.session_uid] = _parent_uid(obj)
    for child in _descendants(obj):
        _last[child.session_uid] = child.matrix_world.copy()
        _parent[child.session_uid] = _parent_uid(child)


def _check_context(obj):
    context = bpy.context
    depsgraph = context.evaluated_depsgraph_get()
    _index.refresh(context.scene, depsgraph, {obj.session_uid: obj})
    return context.scene, depsgraph


def reconfigure(obj, apply, restore):
    """Mudança dimensional atômica. Sobrepor não é recusado: medida não é deslocamento (BUG-20261023-TAMR, RF03);
    erro restaura o estado anterior e é propagado (RF04)."""
    with suspended():
        try:
            apply()
            bpy.context.view_layer.update()
        except Exception:
            restore()
            bpy.context.view_layer.update()
            raise
        finally:
            _index.reset()
            accept(obj)
    return True


def penetrates(obj, start):
    """A pose atual do objeto cria penetração que não existia na pose `start` (matriz de mundo)?"""
    try:
        scene, depsgraph = _check_context(obj)
        if not enabled(scene):
            return False
        body = _body(obj, depsgraph)
        if not body:
            return False
        before = _carry(body, start @ obj.matrix_world.inverted_safe())
        entries = _index.near(_bounds([before, body]), _subtree_uids([obj]))
        return _new_penetration(body, before, entries, depsgraph)
    except Exception:
        _fail([])
        return True


def overlapping(obj, matrix):
    """Objetos que o corpo de `obj`, na pose `matrix` (mundo), penetra além da tolerância."""
    scene, depsgraph = _check_context(obj)
    body = _carry(_body(obj, depsgraph), matrix @ obj.matrix_world.inverted_safe())
    if not body:
        return []
    found = []
    for entry in _index.near(_bounds([body]), _subtree_uids([obj])):
        if any(not rules.excluded(it, entry.item) and _deep(it, entry, depsgraph) for it in body):
            found.append(entry.obj)
    return sorted(found, key=lambda o: o.name)


def clamp(obj, start, target):
    """Pose permitida ao levar `obj` de `start` até `target` (matrizes de mundo; a pose atual do objeto pode ser
    qualquer uma). Toda translação varre o caminho, inclusive com destino livre do outro lado de uma chapa;
    giro ou escala que penetra fica em `start`. Falha devolve `start`."""
    try:
        scene, depsgraph = _check_context(obj)
        if not enabled(scene):
            return target.copy()
        body = _body(obj, depsgraph)
        if not body:
            return target.copy()
        inverse = obj.matrix_world.inverted_safe()
        at_start, at_target = _carry(body, start @ inverse), _carry(body, target @ inverse)
        skip = _subtree_uids([obj])
        entries = _index.near(_bounds([at_start, at_target]), skip)
        if not _translation_only(start, target):
            return start.copy() if _new_penetration(at_target, at_start, entries, depsgraph) else target.copy()
        delta = target.translation - start.translation
        entries = _index.near(_bounds([at_start, at_target], grow=delta.length), skip)
        allowed = _sweep(at_start, delta, entries, depsgraph, slide=False)
        out = target.copy()
        out.translation = start.translation + allowed
        return out
    except Exception:
        _fail([])
        return start.copy()


# Ciclo ------------------------------------------------------------------------------------------------------------
def reset():
    _last.clear()
    _anchor.clear()
    _parent.clear()
    _index.reset()


def seed():
    """Toda pose atual vale como última pose válida (abrir, desfazer, refazer, ligar o add-on)."""
    reset()
    try:
        objects = bpy.data.objects
    except AttributeError:
        return None
    from ..geometry_free import mesh as geometry_mesh
    geometry_mesh._parameters.clear()
    for obj in objects:
        if geometry_mesh.is_geometry(obj):
            geometry_mesh._parameters[obj.session_uid] = geometry_mesh._props(obj)
        _last[obj.session_uid] = obj.matrix_world.copy()
        _parent[obj.session_uid] = _parent_uid(obj)
    return None


@persistent
def on_load_or_undo(*_args):
    seed()


_HANDLERS = ((bpy.app.handlers.depsgraph_update_post, on_depsgraph_update),
             (bpy.app.handlers.load_post, on_load_or_undo),
             (bpy.app.handlers.undo_post, on_load_or_undo),
             (bpy.app.handlers.redo_post, on_load_or_undo))


def register():
    for handlers, func in _HANDLERS:
        if func not in handlers:
            handlers.append(func)
    seed()
    if not bpy.app.timers.is_registered(seed):
        bpy.app.timers.register(seed, first_interval=0.0)


def unregister():
    for handlers, func in _HANDLERS:
        if func in handlers:
            handlers.remove(func)
    if bpy.app.timers.is_registered(seed):
        bpy.app.timers.unregister(seed)
    reset()
