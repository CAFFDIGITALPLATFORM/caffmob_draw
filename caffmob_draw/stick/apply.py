"""Manter o item grudado na face do hospedeiro (feature 004, T023-T025; D-04, D-10, RN-07, RN-08, RN-08a).

- `update_position(item)`: leva o item a `u`/`v`/`distance` no referencial da face (`frame.py`), sem limite de contorno.
- Handler `depsgraph_update_post`: quando a caixa avaliada de um hospedeiro muda (espessura da parede, largura do
  painel), reposiciona na hora os itens grudados nele. Quando um objeto se mexe, só anota o nome.
- Temporizador de assentar: quando nenhum movimento modal está rodando (G nativo, posicionamento do plugin), trata uma
  vez o que foi anotado (`settle.py`): projeta o item grudado de volta no plano, vincula módulo novo na parede, ímã e
  verificação de colisão. Assim o projeto não briga com o arraste do usuário.
- Vínculo perdido (hospedeiro apagado, pai trocado): o item fica onde estava no mundo, sem vínculo, e a barra de
  status avisa. Item que saiu da face: `out_of_face` e aviso (RN-08a).
"""

import time

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import tr
from . import frame, props

SETTLE_SECONDS = 0.2
QUIET_SECONDS = 0.6      # depois de desfazer, refazer ou abrir: o que se mexe não é gesto do usuário


# Caixas ----------------------------------------------------------------------------------------------------
def _depsgraph():
    return bpy.context.evaluated_depsgraph_get()


def local_box(obj, depsgraph=None):
    """Caixa do objeto avaliado no espaço local dele (com modificadores); sem geometria, a dos filhos."""
    depsgraph = depsgraph or _depsgraph()
    corners = _corners(obj, Matrix.Identity(4), depsgraph)
    return (tuple(min(c[i] for c in corners) for i in range(3)), tuple(max(c[i] for c in corners) for i in range(3)))


def _own_corners(obj, to_ref, depsgraph):
    if obj.type not in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'META'}:
        return []
    evaluated = obj.evaluated_get(depsgraph)
    corners = [Vector(c) for c in evaluated.bound_box]
    if all(c.length < 1e-9 for c in corners):
        return []
    return [to_ref @ c for c in corners]


def _corners(obj, to_ref, depsgraph):
    """Cantos da caixa do objeto no referencial `to_ref` (matriz do espaço local do objeto para o referencial)."""
    own = _own_corners(obj, to_ref, depsgraph)
    if own:
        return own
    out = []
    inv_world = obj.matrix_world.inverted_safe()
    for child in obj.children_recursive:
        if child.get('IS_CUTTING_OBJ') or child.get('IS_2D_ANNOTATION') or child.get('obj_x'):
            continue
        out.extend(_own_corners(child, to_ref @ inv_world @ child.matrix_world, depsgraph))
    return out or [to_ref @ Vector((0.0, 0.0, 0.0))]


def item_corners(item, host, depsgraph=None):
    """Cantos da caixa do item no referencial local do hospedeiro."""
    depsgraph = depsgraph or _depsgraph()
    to_host = host.matrix_world.inverted_safe() @ item.matrix_world
    return [tuple(c) for c in _corners(item, to_host, depsgraph)]


def host_box(host, depsgraph=None):
    lo, hi = local_box(host, depsgraph)
    return tuple(lo), tuple(hi)


def face_of(item, depsgraph=None):
    """(referencial, extensão da face ou None) do vínculo atual."""
    st = item.btm_stick
    box = host_box(st.host, depsgraph)
    fr = frame.frame_for(box, st.face_kind, st.face, tuple(st.plane))
    extent = frame.face_extent(box, st.face) if st.face_kind == frame.BOX_SIDE else None
    return fr, extent


# Escrita sem disparar os `update` ---------------------------------------------------------------------------
def write(item, name, value):
    key = (item.name, name)
    props._guard.add(key)
    try:
        setattr(item.btm_stick, name, value)
    finally:
        props._guard.discard(key)


def _store_world(item):
    write(item, 'last_world', [v for row in item.matrix_world for v in row])


def _translate_local(item, host, delta):
    """Desloca o item por `delta` (referencial local do hospedeiro), qualquer que seja o `matrix_parent_inverse`."""
    world_delta = host.matrix_world.to_3x3() @ Vector(delta)
    if world_delta.length <= 1e-9:
        return False
    item.matrix_world = Matrix.Translation(world_delta) @ item.matrix_world
    return True


# Posição -----------------------------------------------------------------------------------------------------
def linked(item):
    st = getattr(item, 'btm_stick', None)
    return st is not None and st.is_stuck and st.host is not None and item.parent == st.host


def update_position(item, depsgraph=None):
    """Leva o item a `u`/`v`/`distance` (D-04); devolve True quando moveu."""
    if not linked(item):
        return False
    st = item.btm_stick
    depsgraph = depsgraph or _depsgraph()
    fr, extent = face_of(item, depsgraph)
    corners = item_corners(item, st.host, depsgraph)
    moved = _translate_local(item, st.host, frame.shift(fr, corners, st.u, st.v, st.distance))
    if moved:
        corners = item_corners(item, st.host, depsgraph)
    _check_face(item, fr, corners, extent)
    _store_world(item)
    return moved


def project(item, depsgraph=None):
    """Item movido livremente (G nativo, campos de posição): volta ao plano da face na posição em que foi solto."""
    if not linked(item):
        return False
    st = item.btm_stick
    depsgraph = depsgraph or _depsgraph()
    flipped = _flip_if_across(item, depsgraph)
    fr, _extent = face_of(item, depsgraph)
    if not flipped:                       # trocar de lado (parede invertida) não é giro livre: a pose fica
        _restore_orientation(item, fr)
    u, v, _d = frame.params(fr, item_corners(item, st.host, depsgraph))
    if abs(u - st.u) > 1e-9:
        write(item, 'u', u)
    if abs(v - st.v) > 1e-9:
        write(item, 'v', v)
    moved = update_position(item, depsgraph)
    if abs(st.spin - st.applied_spin) > 1e-9:
        update_spin(item)
    return moved


def _restore_orientation(item, fr):
    """Depois de um giro livre, o item volta a encostar na face; em face de pé o giro em torno da normal volta ao
    `spin` gravado (questions.md, pergunta 82)."""
    from .link import oriented_matrix
    normal = (item.btm_stick.host.matrix_world.to_3x3() @ Vector(fr[3])).normalized()
    target = oriented_matrix(item.matrix_world, normal)
    if frame.contact_axis(tuple(normal)) == 'BACK':
        write(item, 'applied_spin', 0.0)       # update_spin reaplica o spin a partir da pose sem giro
    item.matrix_world = target


_OPPOSITE = {'POS_X': 'NEG_X', 'NEG_X': 'POS_X', 'POS_Y': 'NEG_Y', 'NEG_Y': 'POS_Y', 'POS_Z': 'NEG_Z', 'NEG_Z': 'POS_Z'}


def _flip_if_across(item, depsgraph):
    """O item foi parar do outro lado do hospedeiro (ex.: o editor de paredes inverteu a direção da parede e devolveu
    os filhos ao lugar no mundo): o vínculo passa para a face oposta em vez de puxar o item através dele."""
    st = item.btm_stick
    if st.face_kind != frame.BOX_SIDE:
        return False
    box = host_box(st.host, depsgraph)
    corners = item_corners(item, st.host, depsgraph)
    thickness = frame.limits.thickness(box, st.face)
    d = frame.params(frame.box_frame(box, st.face), corners)[2]
    if d >= -thickness - frame.OUT_TOLERANCE:
        return False
    other = _OPPOSITE[st.face]
    d_other = frame.params(frame.box_frame(box, other), corners)[2]
    if d_other < -frame.OUT_TOLERANCE:
        return False
    write(item, 'face', other)
    write(item, 'distance', d_other)
    return True


def update_spin(item):
    """Gira o item em torno da normal da face, pelo centro da pegada, até `spin`."""
    if not linked(item):
        return
    st = item.btm_stick
    delta = st.spin - st.applied_spin
    if abs(delta) > 1e-9:
        depsgraph = _depsgraph()
        fr, _extent = face_of(item, depsgraph)
        lo, hi = frame.footprint(fr, item_corners(item, st.host, depsgraph))
        center = frame.from_frame(fr, ((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0, lo[2]))
        world_center = st.host.matrix_world @ Vector(center)
        axis = (st.host.matrix_world.to_3x3() @ Vector(fr[3])).normalized()
        rot = (Matrix.Translation(world_center) @ Matrix.Rotation(delta, 4, axis)
               @ Matrix.Translation(-world_center))
        item.matrix_world = rot @ item.matrix_world
        write(item, 'applied_spin', st.spin)
    update_position(item)


def _check_face(item, fr, corners, extent):
    out = frame.out_of_face(fr, corners, extent)
    st = item.btm_stick
    if out != st.out_of_face:
        write(item, 'out_of_face', out)
        if out:
            _warn(tr("Item fora da face: {}").format(item.name))


def _warn(text):
    from ..ui import save_feedback
    save_feedback.show(text)


def lose_link(item, warn=True):
    """RN-08: o item fica onde estava no mundo, sem vínculo."""
    st = item.btm_stick
    world = Matrix([tuple(st.last_world[r * 4:(r + 1) * 4]) for r in range(4)])
    if item.parent is None and any(abs(world[r][c] - (1.0 if r == c else 0.0)) > 1e-12
                                   for r in range(4) for c in range(4)):
        item.matrix_world = world
    for name, value in (('is_stuck', False), ('host', None), ('out_of_face', False)):
        write(item, name, value)
    invalidate()
    if warn:
        _warn(tr("Vínculo perdido: {}").format(item.name))


# Índice hospedeiro → itens -----------------------------------------------------------------------------------
_index = {}
_index_ok = [False]


def invalidate():
    _index_ok[0] = False


def _host_key(host):
    return host.as_pointer() if host is not None else ''


def index():
    """Hospedeiro (pelo ponteiro, que sobrevive a renomear) → nomes dos itens; refeito quando um item some, é
    renomeado ou perde o hospedeiro (questions.md, pergunta 37)."""
    if _index_ok[0] and not _index_valid():
        _index_ok[0] = False
    if not _index_ok[0]:
        _index.clear()
        for obj in bpy.data.objects:
            st = getattr(obj, 'btm_stick', None)
            if st is not None and st.is_stuck:
                _index.setdefault(_host_key(st.host), []).append(obj.name)
        _index_ok[0] = True
    return _index


def _index_valid():
    for key, names in _index.items():
        for name in names:
            item = bpy.data.objects.get(name)
            if item is None or not item.btm_stick.is_stuck or _host_key(item.btm_stick.host) != key:
                return False
    return True


def stuck_items(host):
    return [bpy.data.objects[n] for n in index().get(_host_key(host), ()) if n in bpy.data.objects]


# Handler e temporizador --------------------------------------------------------------------------------------
_busy = [False]
_last_box = {}
_pending = set()
_quiet_until = [0.0]


@persistent
def on_depsgraph_update(scene, depsgraph):
    if _busy[0]:
        return
    _busy[0] = True
    try:
        idx = index()
        for update in depsgraph.updates:
            if not isinstance(update.id, bpy.types.Object):
                continue
            obj = update.id.original
            name = obj.name
            if update.is_updated_geometry and obj.as_pointer() in idx:
                box = host_box(obj, depsgraph)
                if _last_box.get(name) != box:
                    _last_box[name] = box
                    for item in stuck_items(obj):
                        update_position(item, depsgraph)
            if update.is_updated_transform and time.monotonic() >= _quiet_until[0]:
                _pending.add(name)
        for name in idx.get('', ()):
            item = bpy.data.objects.get(name)
            if item is not None:
                lose_link(item)
        for key, names in list(idx.items()):     # pai trocado fora do plugin (Ctrl+P): vínculo perdido (pergunta 36)
            for name in list(names):
                item = bpy.data.objects.get(name)
                if item is not None and key != '' and item.parent != item.btm_stick.host:
                    lose_link(item)
        if _pending and not bpy.app.timers.is_registered(_settle_timer):
            bpy.app.timers.register(_settle_timer, first_interval=SETTLE_SECONDS)
    except ReferenceError:
        pass
    finally:
        _busy[0] = False


def modal_running():
    """Algum movimento modal em andamento (G nativo, posicionamento, mover do plugin)?"""
    from . import settle
    try:
        windows = bpy.context.window_manager.windows
    except AttributeError:
        return False
    for window in windows:
        for op in getattr(window, 'modal_operators', ()):
            if settle.is_move_operator(op):
                return True
    return False


def _settle_timer():
    if modal_running():
        return SETTLE_SECONDS
    names = list(_pending)
    _pending.clear()
    _busy[0] = True
    try:
        from . import settle
        settle.run(names)
    except ReferenceError:
        pass
    except Exception:                     # erro inesperado vai para o log, com os itens do lote (EC-15)
        import traceback
        print(f"CAFFMob Draw: assentar dos itens grudados falhou para {sorted(names)}")
        traceback.print_exc()
    finally:
        _busy[0] = False
    return None


@persistent
def on_load_or_undo(*_args):
    _quiet_until[0] = time.monotonic() + QUIET_SECONDS
    invalidate()
    _last_box.clear()
    _pending.clear()


_HANDLERS = ((bpy.app.handlers.depsgraph_update_post, on_depsgraph_update),
             (bpy.app.handlers.load_post, on_load_or_undo),
             (bpy.app.handlers.undo_post, on_load_or_undo),
             (bpy.app.handlers.redo_post, on_load_or_undo))


def register():
    for handlers, func in _HANDLERS:
        if func not in handlers:
            handlers.append(func)


def unregister():
    for handlers, func in _HANDLERS:
        if func in handlers:
            handlers.remove(func)
    if bpy.app.timers.is_registered(_settle_timer):
        bpy.app.timers.unregister(_settle_timer)
    on_load_or_undo()
