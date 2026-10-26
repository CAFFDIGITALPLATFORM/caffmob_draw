"""Adaptador de personalização do módulo paramétrico CAFFMob (`btm`) (feature 003, T040; D-05, D-07 a D-09).

O módulo é uma malha única (`geometry/mesh_gen.py`) com portas filhas (`geometry/door_controller.py`). Um só vão:
o próprio módulo. Gavetas, divisórias e estilos de porta não existem nessa linha e aparecem com o motivo.

Estrutura (feature 006, T013): as cinco chapas são faces da malha, controladas por `btm_cabinet.has_*`, `mode_*` e
`thickness_*`; os três modos de remoção valem em todas (D-08). O vão interno sai de `cabinet_editor/structure.layout`.
"""

from ...data.i18n import N_, tr
from ...geometry import door_controller
from ...geometry.mesh_gen import MAT_BACK, MAT_CARCASS, MAT_SHELF
from .. import spec
from . import common, frameless

LIBRARY = 'BTM'
SWING_TO_FRONT = {'LEFT': 'DOOR_LEFT', 'RIGHT': 'DOOR_RIGHT', 'DOUBLE': 'DOUBLE_DOORS', 'FLIP': 'FLIP_UP',
                  'NONE': 'OPEN'}
FRONT_TO_SWING = {v: k for k, v in SWING_TO_FRONT.items()}
NO_STYLES = N_("O módulo paramétrico não tem estilos de porta")


def capabilities(root):
    return {'FRONTS': None, 'PULLS': None, 'MATERIALS': None, 'INTERIOR': None, 'STYLES': NO_STYLES}


def front_types(root):
    return list(FRONT_TO_SWING) + ['DRAWERS']          # 067 RF-104


def openings(root):
    from ...geometry import subspace_fronts
    return [("module", root)] + [(h[subspace_fronts.PATH_PROP], h) for h in subspace_fronts.holders(root)]


def front_type(root):
    from ...geometry import subspace_fronts
    own = subspace_fronts.front_type(root, "module")         # gavetas do módulo inteiro (067 RF-104)
    if own is not None:
        return own
    return SWING_TO_FRONT.get(root.btm_cabinet.door_swing, 'OPEN'), 0


def space_boxes(context, root):
    """{caminho: (lo, hi)} do módulo inteiro (`module`, o vão interno) e dos subvãos do editor (067 D-23)."""
    out = {}
    inner = inner_spaces(context, root).get("s0")
    if inner is not None:
        out["module"] = (tuple(inner.lo), tuple(inner.hi))
    try:
        from ...cabinet_editor import bridge, divisions as dv
        roots, core, _raw, _names = bridge.division_context(context, root)
        for path, box in dv.resolve(roots, core)[0].items():
            out[path] = (tuple(box.lo), tuple(box.hi))
    except (AttributeError, KeyError, ValueError):
        pass
    return out


def read(root):
    result = spec.Spec(library=LIBRARY)
    item = result.ensure_opening("module")
    item.front, item.drawer_count = front_type(root)
    custom = root.btm_custom
    item.pull_model, item.pull_position, item.front_material = (custom.pull_model, custom.pull_position,
                                                                custom.front_material)
    item.interior = common.interior_of(root) or spec.Interior(shelves=int(root.btm_cabinet.shelves))
    result.group_materials = {i.group: i.material for i in custom.group_materials if i.material}
    from ...geometry import subspace_fronts
    for path, _holder in openings(root)[1:]:                  # frentes por subvão (067 RF-103)
        found = subspace_fronts.front_type(root, path)
        sub = result.ensure_opening(path)
        sub.front, sub.drawer_count = found if found is not None else ('OPEN', 0)
    return result


def set_front(context, root, opening, front, drawer_count=1, gaveta=None):
    """067 (D-23; RF-103, RF-104): gavetas reais no módulo inteiro e frentes por subvão (`subspace_fronts`).

    072 (D-05, M-04): `gaveta` é o spec do construtor de gavetas; vai gravado no pedido do vão."""
    from ...geometry import subspace_fronts
    if front not in subspace_fronts.SUPPORTED:
        return [tr("O módulo paramétrico não tem a frente '{}'").format(spec.FRONT_LABELS.get(front, front))]
    if opening is not root:
        path = opening.get(subspace_fronts.PATH_PROP, "")
        box = space_boxes(context, root).get(path)
        if box is None:
            return [tr("O vão {} não existe mais").format(path)]
        return subspace_fronts.build(root, path, box, front, drawer_count, gaveta)
    if front == 'DRAWERS':
        box = space_boxes(context, root).get("module")
        if box is None:
            return [tr("O módulo não tem vão interno para gavetas")]
        if root.btm_cabinet.door_swing != 'NONE':
            root.btm_cabinet.door_swing = 'NONE'              # as portas do construtor saem
        return subspace_fronts.build(root, "module", box, 'DRAWERS', drawer_count, gaveta)
    if subspace_fronts.front_type(root, "module") is not None:
        subspace_fronts.build(root, "module", ((0, 0, 0), (0, 0, 0)), 'OPEN')
    if front not in FRONT_TO_SWING:
        return [tr("O módulo paramétrico não tem a frente '{}'").format(spec.FRONT_LABELS.get(front, front))]
    root.btm_cabinet.door_swing = FRONT_TO_SWING[front]      # o update refaz malha, portas e reaplica
    return []


def set_interior(context, root, opening, interior):
    messages = spec.validate_interior(interior)
    if messages:
        return messages
    root.btm_custom.interior = spec.interior_to_json(interior)
    root.btm_cabinet.shelves = int(interior.shelves)
    if interior.dividers or interior.drawers:
        messages.append(tr("O módulo paramétrico só tem prateleiras; divisórias e gavetas internas foram ignoradas"))
    if interior.heights:
        messages.append(tr("O módulo paramétrico distribui as prateleiras por igual; as alturas foram ignoradas"))
    return messages


def style_names():
    return []


def pull_items():
    return frameless.pull_items()       # mesmos arquivos de puxador da biblioteca frameless


def _carcass_materials(root, warnings):
    groups = {i.group: i.material for i in root.btm_custom.group_materials if i.material}
    if not groups:
        return
    carcass = common.material(groups.get('CAIXA'), warnings)
    slots = {MAT_CARCASS: carcass,
             MAT_SHELF: common.material(groups.get('INTERNO'), warnings) or carcass,
             MAT_BACK: common.material(groups.get('FUNDO'), warnings) or carcass}
    materials = root.data.materials
    while len(materials) < 3:
        materials.append(None)
    for index, mat in slots.items():
        if mat is not None:
            materials[index] = mat


def reapply(context, root):
    warnings = []
    from ...geometry import subspace_fronts
    if subspace_fronts.specs(root):                          # vãos que mudaram de tamanho refazem as frentes
        warnings += subspace_fronts.rebuild_all(root, space_boxes(context, root))
    custom = root.btm_custom
    _carcass_materials(root, warnings)
    groups = {i.group: i.material for i in custom.group_materials if i.material}
    front_mat = common.material(custom.front_material or groups.get('FRENTES', ""), warnings)
    pull_source = None
    if custom.pull_model and custom.pull_model != spec.NO_PULL:
        pull_source = frameless._pull_object(custom.pull_model, warnings)
    for door in door_controller.doors_of(root):
        if custom.pull_model == spec.NO_PULL or pull_source is not None:
            length = pull_source.dimensions.x if pull_source is not None else 0.1
            door_controller.set_door_pull(root, door, pull_source, custom.pull_position, length)
        door_controller.set_door_material(door, front_mat)
    return common.unique(warnings)


# Estrutura e divisões (feature 006) ---------------------------------------------------------------------------
def _layout(cab, full=False):
    from ...cabinet_editor import structure as st
    from ...data.properties import back_setback_of, structure_of
    data = structure_of(cab)
    thick = {role: data[role][2] for role in st.ROLES}
    states = {} if full else {role: st.RoleState(removed=not present, mode=mode)
                              for role, (present, mode, _t) in data.items() if not present}
    return st.layout(cab.width, cab.height, cab.depth, thick, states, back_setback_of(cab.id_data)), thick


def set_back_recess(context, root, setback):
    """Fundo recuado (feature 008, T023): o valor já está em `btm_structure`; basta refazer a malha."""
    from ...data.properties import update_cabinet_geom
    update_cabinet_geom(root.btm_cabinet, context)
    return []


def inner_spaces(context, root):
    from ...cabinet_editor.divisions import Box
    from ...cabinet_editor import structure_inputs
    found = structure_inputs.carcass_parts_for(root)      # feature 015: vão da estrutura (rodapé, sarrafos)
    if found is not None:
        return {"s0": Box(*found[1])}
    (_panels, inner), _thick = _layout(root.btm_cabinet)
    return {"s0": Box(*inner)}


def structure_parts(root):
    return {}                   # as chapas não são objetos: `structure_info` e `elevation_parts` cobrem a malha


def structure_info(context, root):
    (panels, _inner), thick = _layout(root.btm_cabinet, full=True)
    out = {}
    for role, (lo, hi) in panels.items():
        sizes = sorted((hi[i] - lo[i] for i in range(3)), reverse=True)
        out[role] = {'size': (sizes[0], sizes[1]), 'thickness': thick[role],
                     'removed': not getattr(root.btm_cabinet, 'has_' + role.lower())}
    return out


def elevation_parts(context, root):
    """Chapas presentes da malha como peças da vista frontal: [(nome, papel, lo, hi)] no referencial da raiz."""
    from ...cabinet_editor import structure as st
    from ...cabinet_editor import structure_inputs
    found = structure_inputs.carcass_parts_for(root)      # feature 015: as peças da estrutura de caixa
    if found is not None:
        return [(tr(st.ROLE_LABELS[p.role]) if p.role in st.ROLE_LABELS else tr(p.name), p.role, p.box[0], p.box[1])
                for p in found[0]]
    (panels, _inner), _thick = _layout(root.btm_cabinet)
    return [(tr(st.ROLE_LABELS[role]), role, lo, hi) for role, (lo, hi) in panels.items()]


def structure_caps(root):
    modes = {'KEEP': None, 'EXTEND': None, 'SHRINK': None}
    return {role: {'remove': None, 'thickness': None, 'modes': dict(modes)}
            for role in ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT')}


def _shrink(root, role, sign):
    from mathutils import Vector  # type: ignore
    from ...cabinet_editor import structure as st
    cab = root.btm_cabinet
    thickness = float(getattr(cab, 'thickness_' + role.lower())) or float(cab.thickness)
    delta, shift = st.shrink_change(role, thickness)
    for field, value in delta.items():
        setattr(cab, field, getattr(cab, field) + sign * value)
    root.location += root.matrix_basis.to_3x3() @ (Vector(shift) * sign)


def remove_part(context, root, role, mode):
    cab = root.btm_cabinet
    if not getattr(cab, 'has_' + role.lower()):
        return []
    setattr(cab, 'mode_' + role.lower(), mode)
    setattr(cab, 'has_' + role.lower(), False)
    if mode == 'SHRINK':
        _shrink(root, role, +1)
    return []


def restore_part(context, root, role, mode):
    cab = root.btm_cabinet
    if getattr(cab, 'has_' + role.lower()):
        return []
    if getattr(cab, 'mode_' + role.lower()) == 'SHRINK':
        _shrink(root, role, -1)
    setattr(cab, 'has_' + role.lower(), True)
    setattr(cab, 'mode_' + role.lower(), 'KEEP')
    return []


def set_part_thickness(context, root, role, value):
    setattr(root.btm_cabinet, 'thickness_' + role.lower(), float(value))
    return []


def reaffirm(context, root):
    return []                   # tudo vive em `btm_cabinet`: a malha refeita já sai certa

