"""Grudar e desgrudar um item numa face plana (feature 004, T026; D-02, D-03, D-05, D-07, RN-05, RN-06, RN-09).

- O hospedeiro é a raiz do que foi clicado (módulo para peça ou frente, a própria parede, a geometria); um objeto não
  reconhecido é o próprio hospedeiro. Assim o vínculo sobrevive às bibliotecas que recriam as peças no recálculo.
- Grudar gira o item para a normal (em face de pé, o fundo do item, +Y local, encosta; em face deitada, a base), vira
  filho do hospedeiro com inversa identidade e grava o vínculo (`props.BTM_PG_Stick`).
- Desgrudar devolve o pai anterior e mantém o item onde está no mundo.
"""

from mathutils import Matrix, Vector  # type: ignore

from ..data.i18n import tr
from ..selection import classify
from . import apply, frame

UP = Vector((0.0, 0.0, 1.0))


def host_for(obj):
    """Hospedeiro do vínculo a partir do objeto clicado."""
    if obj is None:
        return None
    info = classify.classify(obj)
    if info is not None and info.kind not in (classify.OTHER, classify.ANNOTATION) and info.root is not None:
        return info.root
    return obj


def can_stick(item, host):
    if item is None:
        return tr("Selecione o item a grudar")
    if host is None:
        return tr("Clique numa face plana de outro objeto")
    if host == item or host in item.children_recursive:
        return tr("O item não pode ser grudado nele mesmo nem num filho dele")
    agg = getattr(item, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return tr("O item é um agregado: desconverta antes de grudar")
    return None


def _to_host(host, point, normal):
    world = host.matrix_world
    p = world.inverted_safe() @ Vector(point)
    n = (world.to_3x3().transposed() @ Vector(normal)).normalized()
    return p, n


def oriented_matrix(world, normal_world):
    """Matriz de mundo do item girado para a face (sem alterar nada): em pé, −Y do item = normal (o fundo encosta);
    deitada, Z do item = ±normal."""
    n = Vector(normal_world).normalized()
    loc, rot, scale = world.decompose()
    current = rot.to_matrix()
    if frame.contact_axis(tuple(n)) == 'BACK':
        y = -n
        z = UP - n * UP.dot(n)
        if z.length < 1e-6:
            z = current.col[2] - n * current.col[2].dot(n)
        z.normalize()
        x = y.cross(z).normalized()
    else:
        z = n if n.dot(UP) > 0 else -n
        y = current.col[1] - z * current.col[1].dot(z)
        if y.length < 1e-6:
            y = current.col[0].cross(z)
        y.normalize()
        x = y.cross(z).normalized()
    basis = Matrix((x, y, z)).transposed()
    return Matrix.LocRotScale(loc, basis.to_quaternion(), scale)


def orient(item, normal_world):
    """Gira o item para a face (ver `oriented_matrix`)."""
    item.matrix_world = oriented_matrix(item.matrix_world, normal_world)


def _attach(item, host):
    st = item.btm_stick
    if not st.is_stuck:
        apply.write(item, 'orig_parent', item.parent)
    world = item.matrix_world.copy()
    item.parent = host
    item.matrix_parent_inverse = Matrix.Identity(4)
    item.matrix_basis = host.matrix_world.inverted_safe() @ world


def _record(item, host, kind, face, plane_values, u, v, distance):
    for name, value in (('host', host), ('face_kind', kind), ('face', face or 'NEG_Y'), ('plane', plane_values),
                        ('u', u), ('v', v), ('distance', distance), ('spin', 0.0), ('applied_spin', 0.0),
                        ('out_of_face', False), ('is_stuck', True)):
        apply.write(item, name, value)
    apply.invalidate()


def stick(item, hit_obj, point_world, normal_world, polygon_world=None, center=True, rotate=True):
    """Gruda `item` na face de `hit_obj` em `point_world`; devolve (hospedeiro, face) ou levanta ValueError."""
    host = host_for(hit_obj)
    reason = can_stick(item, host)
    if reason:
        raise ValueError(reason)
    if polygon_world:
        points = [tuple(host.matrix_world.inverted_safe() @ Vector(p)) for p in polygon_world]
        _p, n_local = _to_host(host, point_world, normal_world)
        if not frame.is_planar(points, tuple(n_local)):
            raise ValueError(tr("A face não é plana"))
    if rotate:
        orient(item, normal_world)
    _attach(item, host)
    depsgraph = apply._depsgraph()
    box = apply.host_box(host, depsgraph)
    p, n = _to_host(host, point_world, normal_world)
    kind, face = frame.choose_face(box, tuple(p), tuple(n))
    if kind == frame.BOX_SIDE:
        fr = frame.box_frame(box, face)
        plane_values = tuple(apply.props.IDENTITY)
    else:
        fr = frame.plane_frame(tuple(p), tuple(n))
        plane_values = frame.frame_to_matrix(fr)
    corners = apply.item_corners(item, host, depsgraph)
    u, v, _d = frame.params(fr, corners)
    if center:
        lo, hi = frame.footprint(fr, corners)
        hu, hv, _hn = frame.to_frame(fr, tuple(p))
        u, v = hu - (hi[0] - lo[0]) / 2.0, hv - (hi[1] - lo[1]) / 2.0
    _record(item, host, kind, face, plane_values, u, v, 0.0)
    apply.update_position(item, depsgraph)
    return host, face


def link_in_place(item, host, face):
    """Grava o vínculo com a posição que o item já tem (migração e módulos postos na parede, D-08); não move."""
    if item.parent != host:
        _attach(item, host)
    apply.write(item, 'orig_parent', host)
    depsgraph = apply._depsgraph()
    fr = frame.box_frame(apply.host_box(host, depsgraph), face)
    u, v, d = frame.params(fr, apply.item_corners(item, host, depsgraph))
    _record(item, host, frame.BOX_SIDE, face, tuple(apply.props.IDENTITY), u, v, d)
    apply.write(item, 'last_world', [x for row in item.matrix_world for x in row])


def release(item):
    """Desgruda: pai anterior, mesma posição no mundo, sem vínculo (RN-09)."""
    st = item.btm_stick
    if not st.is_stuck:
        return False
    world = item.matrix_world.copy()
    parent = st.orig_parent
    if parent is not None and parent not in item.children_recursive and parent != item:
        item.parent = parent
        item.matrix_parent_inverse = Matrix.Identity(4)
        item.matrix_basis = parent.matrix_world.inverted_safe() @ world
    else:
        item.parent = None
        item.matrix_world = world
    for name, value in (('is_stuck', False), ('host', None), ('orig_parent', None), ('out_of_face', False)):
        apply.write(item, name, value)
    apply.invalidate()
    return True


def face_label(item):
    """"<hospedeiro> — <face>" para o painel (D-11); paredes usam frente/trás."""
    st = item.btm_stick
    if st.host is None:
        return ""
    if st.face_kind == frame.PLANE:
        side = tr("plano")
    elif classify.classify(st.host).kind == classify.WALL and st.face in ('NEG_Y', 'POS_Y'):
        side = tr("frente") if st.face == 'NEG_Y' else tr("trás")
    else:
        from ..aggregates import limits
        side = tr(limits.FACE_LABELS[st.face])
    return "{} — {}".format(st.host.name, side)
