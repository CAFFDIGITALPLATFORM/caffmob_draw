"""Folha de porta convertida de uma malha (feature 003, T049, T052; RN-11, RN-11a, D-17 a D-19).

Mesmo padrão das portas de ambiente (`inspection/room_door_leaf.py`): um Empty de pivô ("<folha> - Eixo"), filho do
pai, com a malha como filha dele. Giro: eixo na aresta esquerda/direita (vertical) ou de cima/de baixo (horizontal) da
caixa da folha, na face da frente (−Y do pai, a frente dos módulos); correr: o pivô desliza em ±X do pai.
A pose fechada fica guardada (`btm_leaf_rest`, espaço do pai) e abrir nunca altera a malha.
`open_value` é a fração da abertura (0 a 1): graus = fração × ângulo máximo; metros = fração × curso.

Feature 007:
- a folha pode ser um **grupo de peças** (Empty com `btm_group`): a caixa é a união das peças (T015);
- numa **esquadria** (pai = grupo FRAME), abrir para na esquadria e fechar para no primeiro de três batentes: a pose
  do arquivo, o montante da outra folha (`slide_limits.close_stop`) e o contato com a esquadria (T018, D-10);
- folha de correr na esquadria: sentido padrão para o próprio lado e curso = distância livre (T019, D-08, D-09).
"""

import math

import bpy  # type: ignore
from mathutils import Matrix, Vector  # type: ignore

from . import apply, group, slide_limits, sweep

PIVOT_SUFFIX = " - Eixo"
REST_KEY = 'btm_leaf_rest'
FREE_CONTACT_KEY = 'btm_free_contact'      # peça da esquadria no fim do curso livre (feature 007)
OPEN_KEY = 'btm_open_fraction'
# Sinal do ângulo para abrir "para fora" (para −Y do pai); "para dentro" inverte.
OUT_SIGN = {'LEFT': -1.0, 'RIGHT': 1.0, 'TOP': -1.0, 'BOTTOM': 1.0}


def _matrix(values):
    return Matrix([list(values[i * 4:(i + 1) * 4]) for i in range(4)])


def rest_matrix(obj):
    return _matrix(obj[REST_KEY]) if REST_KEY in obj else None


def local_corners(obj):
    """Os 8 cantos da caixa da folha no espaço dela: da malha avaliada ou, num grupo, da união das peças."""
    if group.is_group(obj):
        box = group.group_box(obj)
        return group.box_corners(*box) if box is not None else [Vector()] * 8
    depsgraph = bpy.context.evaluated_depsgraph_get()
    return [Vector(c) for c in obj.evaluated_get(depsgraph).bound_box]


def leaf_box(obj):
    """Caixa da folha fechada no espaço do pai."""
    rest = rest_matrix(obj)
    corners = [rest @ c for c in local_corners(obj)]
    return Vector([min(c[i] for c in corners) for i in range(3)]), Vector([max(c[i] for c in corners) for i in range(3)])


# Esquadria (feature 007) -------------------------------------------------------------------------------------
def frame_of(obj):
    """Grupo FRAME pai da folha, ou None."""
    parent = obj.btm_aggregate.parent_ref
    return parent if group.is_group(parent) and parent.btm_group.kind == 'FRAME' else None


def sibling_leaves(obj):
    frame = frame_of(obj)
    if frame is None:
        return []
    return [o for o in bpy.data.objects if o is not obj and getattr(o, 'btm_aggregate', None) is not None
            and o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF' and o.btm_aggregate.parent_ref == frame]


def _span_x(box):
    return (box[0].x, box[1].x)


def frame_span(frame):
    box = group.group_box(frame)
    return _span_x(box) if box is not None else None


def displacement(obj):
    """Deslocamento atual da folha de correr em X do pai (m, com sinal)."""
    agg = obj.btm_aggregate
    if agg.motion != 'SLIDE':
        return 0.0
    return slide_limits.sign(agg.slide_dir) * agg.travel * current_fraction(obj)


def base_point(box, motion, hinge):
    lo, hi = box
    if motion == 'SLIDE':
        return Vector(lo)
    if hinge == 'LEFT':
        return Vector((lo.x, lo.y, lo.z))
    if hinge == 'RIGHT':
        return Vector((hi.x, lo.y, lo.z))
    if hinge == 'TOP':
        return Vector((lo.x, lo.y, hi.z))
    return Vector((lo.x, lo.y, lo.z))         # BOTTOM


def swing_angle(agg, fraction):
    sign = OUT_SIGN[agg.hinge] * (1.0 if agg.swing_sign == 'OUT' else -1.0)
    return sign * math.radians(max(0.0, min(1.0, fraction)) * agg.max_angle)


def pose_matrix(agg, base, fraction):
    """Matriz do pivô no espaço do pai para a abertura `fraction`."""
    if agg.motion == 'SLIDE':
        direction = Vector((1.0 if agg.slide_dir == 'POS_X' else -1.0, 0.0, 0.0))
        return Matrix.Translation(base + direction * agg.travel * max(0.0, min(1.0, fraction)))
    axis = 'Z' if agg.hinge in ('LEFT', 'RIGHT') else 'X'
    return Matrix.Translation(base) @ Matrix.Rotation(swing_angle(agg, fraction), 4, axis)


def pivot_of(obj):
    pivot = obj.btm_aggregate.pivot
    try:
        return pivot if pivot is not None and pivot.name in bpy.data.objects else None
    except ReferenceError:
        return None


def _base(obj):
    pivot = pivot_of(obj)
    return Vector(pivot['btm_leaf_base']) if pivot is not None and 'btm_leaf_base' in pivot else None


def apply_fraction(obj, fraction):
    """Só a pose (sem testar contato): usada na verificação de interferência e no salvar fechado."""
    pivot = pivot_of(obj)
    if pivot is None:
        return
    pivot.matrix_basis = pose_matrix(obj.btm_aggregate, _base(obj), fraction)
    pivot[OPEN_KEY] = float(fraction)


def current_fraction(obj):
    pivot = pivot_of(obj)
    return float(pivot.get(OPEN_KEY, 0.0)) if pivot is not None else 0.0


def rebuild_pivot(obj):
    """Cria ou refaz o pivô a partir da pose fechada e das opções de giro/correr."""
    agg = obj.btm_aggregate
    parent = agg.parent_ref
    if agg.kind != 'LEAF' or parent is None or REST_KEY not in obj:
        return None
    base = base_point(leaf_box(obj), agg.motion, agg.hinge)
    pivot = pivot_of(obj)
    if pivot is None:
        pivot = bpy.data.objects.new(obj.name + PIVOT_SUFFIX, None)
        pivot.empty_display_size = 0.1
        for collection in obj.users_collection or parent.users_collection:
            collection.objects.link(pivot)
        agg.pivot = pivot
    pivot.empty_display_type = 'SINGLE_ARROW' if agg.motion == 'SWING' else 'PLAIN_AXES'   # segue o movimento (RN-11)
    pivot['btm_leaf'] = obj.name
    pivot['btm_leaf_base'] = list(base)
    pivot.parent = parent
    pivot.matrix_parent_inverse = Matrix.Identity(4)
    obj.parent = pivot
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_basis = Matrix.Translation(-base) @ rest_matrix(obj)
    apply_fraction(obj, 0.0)
    if agg.motion == 'SLIDE' and frame_of(obj) is not None:
        measure_free_travel(obj)
    update_open(obj, bpy.context)
    return pivot


def default_slide_dir(obj):
    """Sentido padrão na esquadria: para o próprio lado (RN-07a)."""
    span = frame_span(frame_of(obj))
    return slide_limits.default_direction(_span_x(leaf_box(obj)), span) if span else 'POS_X'


def measure_free_travel(obj):
    """Curso livre até a esquadria no sentido atual; vira o curso e o teto dele (RN-07, D-09)."""
    from . import collision
    span = frame_span(frame_of(obj))
    if span is None or pivot_of(obj) is None:
        return 0.0
    probe = span[1] - span[0]
    apply._write(obj, 'free_travel', 0.0)
    apply._write(obj, 'travel', probe)
    collision.invalidate(obj)
    tester = collision.Tester(obj)
    reached, contact = sweep.sweep(0.0, probe, lambda v: tester.hit(v / probe), sweep.SLIDE_STEP,
                                   sweep.SLIDE_TOLERANCE)
    free = max(0.0, reached)
    obj[FREE_CONTACT_KEY] = contact.name if contact is not None and hasattr(contact, 'name') else ""
    apply._write(obj, 'free_travel', free)
    apply._write(obj, 'travel', max(free, 0.001))
    apply_fraction(obj, 0.0)
    return free


def low_travel(obj):
    """Pouco curso para o sentido escolhido (aviso do painel, D-08)."""
    agg = obj.btm_aggregate
    if agg.motion != 'SLIDE' or frame_of(obj) is None or agg.free_travel <= 0.0:
        return False
    lo, hi = leaf_box(obj)
    return slide_limits.low_travel(agg.free_travel, hi.x - lo.x)


def make_leaf(obj, parent, motion='SWING', hinge='LEFT', swing_sign='OUT', max_angle=90.0, slide_dir='POS_X',
              travel=0.5):
    """Converte `obj` em folha de porta de `parent` (sem mexer na malha)."""
    agg = obj.btm_aggregate
    if not agg.is_aggregate:
        agg.orig_parent = obj.parent
        agg.orig_matrix = [v for row in obj.matrix_world for v in row]
    obj[REST_KEY] = [v for row in (parent.matrix_world.inverted() @ obj.matrix_world) for v in row]
    for name, value in (('kind', 'LEAF'), ('motion', motion), ('hinge', hinge), ('swing_sign', swing_sign),
                        ('max_angle', max_angle), ('slide_dir', slide_dir), ('travel', travel), ('open_value', 0.0)):
        apply._write(obj, name, value)
    agg.parent_ref = parent
    agg.is_aggregate = True
    agg.contact_name = ""
    agg.contact_kind = 'NONE'
    for other in sibling_leaves(obj):            # sobreposição dos montantes no arquivo, nas duas folhas (D-10)
        if REST_KEY in other:
            overlap = slide_limits.rest_overlap(_span_x(leaf_box(obj)), _span_x(leaf_box(other)))
            apply._write(obj, 'rest_overlap', overlap)
            apply._write(other, 'rest_overlap', overlap)
    return rebuild_pivot(obj)


def remove_pivot(obj):
    """Volta a folha à pose fechada, filha direta do pai, e apaga o pivô."""
    pivot = pivot_of(obj)
    parent = obj.btm_aggregate.parent_ref
    rest = rest_matrix(obj)
    if parent is not None and rest is not None:
        obj.parent = parent
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = rest
    if pivot is not None:
        bpy.data.objects.remove(pivot, do_unlink=True)
    obj.btm_aggregate.pivot = None
    if REST_KEY in obj:
        del obj[REST_KEY]


def update_open(obj, context):
    """Leva a folha até `open_value`, parando no primeiro contato ao abrir (RN-11a)."""
    agg = obj.btm_aggregate
    if agg.kind != 'LEAF' or pivot_of(obj) is None:
        return
    from . import collision
    target = max(0.0, min(1.0, agg.open_value))
    current = current_fraction(obj)
    if agg.motion == 'SLIDE':
        scale, step, tolerance = agg.travel, sweep.SLIDE_STEP, sweep.SLIDE_TOLERANCE
    else:
        scale, step, tolerance = agg.max_angle, sweep.SWING_STEP, sweep.SWING_TOLERANCE
    if scale <= 0.0:
        return
    tester = collision.Tester(obj)
    closing = target < current
    if frame_of(obj) is None:
        reached, contact = sweep.sweep(current * scale, target * scale, lambda v: tester.hit(v / scale), step,
                                       tolerance)
    else:                                         # esquadria: batentes nos dois sentidos (RN-08, RN-09)
        floor, floor_contact = _close_floor(obj, scale)
        reached, contact = sweep.sweep(current * scale, target * scale, lambda v: tester.hit(v / scale), step,
                                       tolerance, close=True, floor=floor, floor_contact=floor_contact)
    fraction = reached / scale
    apply_fraction(obj, fraction)
    agg.contact_name = contact.name if contact is not None and hasattr(contact, 'name') else ""
    if (not agg.contact_name and not closing and agg.motion == 'SLIDE' and agg.free_travel > 0.0
            and reached >= agg.free_travel - tolerance):
        agg.contact_name = obj.get(FREE_CONTACT_KEY, "")      # o curso acaba encostado na esquadria (RN-08)
    agg.contact_kind = ('CLOSE' if closing else 'OPEN') if agg.contact_name else 'NONE'
    if abs(fraction - agg.open_value) > 1e-6:
        apply._write(obj, 'open_value', fraction)
    if context is not None and context.screen is not None:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()


def _close_floor(obj, scale):
    """(abertura mínima ao fechar, na unidade da varredura; folha que a impõe ou None) (D-10)."""
    agg = obj.btm_aggregate
    if agg.motion != 'SLIDE':
        return 0.0, None
    best, who = 0.0, None
    for other in sibling_leaves(obj):
        stop = slide_limits.close_stop(slide_limits.sign(agg.slide_dir), displacement(other))
        if stop > best:
            best, who = stop, other
    return min(best, scale), who

