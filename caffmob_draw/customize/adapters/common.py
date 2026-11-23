"""Utilidades comuns aos adaptadores de personalização (feature 003, T019-T040)."""

import bpy  # type: ignore

from ...data.i18n import N_, tr
from ... import compat
from ...cutting import part_roles
from .. import spec

NO_STYLE_REASON = N_("A biblioteca não tem estilos de porta")


def ordered(objs):
    """Ordem estável: da esquerda para a direita, de cima para baixo (posição no mundo)."""
    return sorted(objs, key=lambda o: (round(o.matrix_world.translation.x, 4), -round(o.matrix_world.translation.z, 4),
                                       o.name))


def material(name, warnings):
    """Material por nome (RN-06); ausente → aviso e None."""
    if not name:
        return None
    mat = bpy.data.materials.get(name)
    if mat is None:
        warnings.append(tr("Material '{}' não existe neste arquivo").format(name))
    return mat


def rotated(mat):
    """Variante com o veio girado (convenção do legado: '<nome> ROTATED'), ou o próprio material."""
    if mat is None:
        return None
    return bpy.data.materials.get(mat.name + " ROTATED") or mat


def gn_modifier(obj, base_name):
    for mod in obj.modifiers:
        if mod.type == 'NODES' and mod.node_group and mod.node_group.name.split(".")[0] == base_name:
            return mod
    return None


# Parede, piso e teto (feature 018, T014; RN-14, D-10): o material da parede chega pelos sockets do nó, não pelo
# slot da malha — era a causa do "aplicar textura na parede" não mudar a vista.
SURFACE_SOCKETS = ('Top Surface', 'Bottom Surface', 'Inside Face', 'Outside Face', 'Left Edge', 'Right Edge')
SURFACE_FLAGS = ('IS_WALL_BP', 'IS_FLOOR_BP', 'IS_CEILING_BP')


def is_surface(obj):
    """Parede, piso ou teto pelas marcas do projeto."""
    return obj is not None and any(obj.get(flag) for flag in SURFACE_FLAGS)


def surface_modifier(obj):
    """Modificador com os sockets de superfície (parede); None quando a malha não tem o nó esperado."""
    if obj is None:
        return None
    for mod in obj.modifiers:
        if mod.type != 'NODES' or mod.node_group is None:
            continue
        items = mod.node_group.interface.items_tree
        if any(socket in items for socket in SURFACE_SOCKETS):
            return mod
    return None


def _set_slots(obj, mat):
    """Material em todos os slots da malha (criando o primeiro quando não há)."""
    if obj.type != 'MESH':
        return False
    if not obj.data.materials:
        obj.data.materials.append(mat)
    for i in range(len(obj.data.materials)):
        obj.data.materials[i] = mat
    return True


def set_surface_material(obj, mat):
    """Material da superfície: os seis sockets do nó na parede, os slots no piso e no teto (RN-14).

    Devolve False quando o objeto é superfície e não tem o modificador esperado: o material não cai no slot em
    silêncio, e quem chamou consegue avisar.
    """
    if mat is None or obj is None:
        return False
    mod = surface_modifier(obj)
    if mod is not None:
        escritos = [socket for socket in SURFACE_SOCKETS if compat.try_set_gn_input(mod, socket, mat)]
        return bool(escritos)
    if obj.get('IS_FLOOR_BP') or obj.get('IS_CEILING_BP'):
        return _set_slots(obj, mat)
    return False


def set_cutpart_material(obj, mat):
    """Material de uma peça `GeoNodeCutpart` (as duas faces e os materiais de porta 5 peças); outras malhas: slots."""
    if mat is None:
        return False
    if is_surface(obj) or surface_modifier(obj) is not None:
        return set_surface_material(obj, mat)
    mod = gn_modifier(obj, 'GeoNodeCutpart')
    if mod is None:
        return _set_slots(obj, mat)
    compat.try_set_gn_input(mod, 'Top Surface', mat)
    compat.try_set_gn_input(mod, 'Bottom Surface', mat)
    if not mod.show_viewport and obj.type == 'MESH' and obj.data.materials:
        # porta 5 peças do face frame: malha estática, com o modificador da peça desligado
        for i in range(len(obj.data.materials)):
            obj.data.materials[i] = mat
    for other in obj.modifiers:
        if other.type != 'NODES' or other is mod or other.node_group is None:
            continue
        items = other.node_group.interface.items_tree
        for socket, value in (('Material', mat), ('Stile Material', mat), ('Panel Material', mat),
                              ('Rail Material', rotated(mat))):
            if socket in items:
                compat.try_set_gn_input(other, socket, value)
    return True


def part_group(obj, cabinet_type=None):
    """Grupo de material da peça pelo componente (`part_roles.classify`)."""
    if obj.get('IS_CABINET_FRONT') or obj.get('hb_part_role') in ('DOOR', 'DRAWER_FRONT', 'PULLOUT_FRONT'):
        return 'FRENTES'
    component = part_roles.classify(obj.name, obj.get('hb_part_role'), cabinet_type,
                                    component=obj.get('btm_component'))
    return spec.group_of_component(component)


def is_cutpart(obj):
    return obj.type == 'MESH' and gn_modifier(obj, 'GeoNodeCutpart') is not None


def apply_group_materials(root, warnings, cabinet_type=None, parts=None):
    """Materiais por grupo (no `btm_custom` da raiz) e por peça (no `btm_custom` da peça; vence o grupo)."""
    custom = root.btm_custom
    groups = {item.group: item.material for item in custom.group_materials if item.material}
    for obj in (parts if parts is not None else [o for o in root.children_recursive if is_cutpart(o)]):
        name = obj.btm_custom.material or groups.get(part_group(obj, cabinet_type), "")
        if name:
            set_cutpart_material(obj, material(name, warnings))


def read_materials(root, target, parts):
    target.group_materials = {item.group: item.material for item in root.btm_custom.group_materials if item.material}
    target.part_materials = {obj.name: obj.btm_custom.material for obj in parts if obj.btm_custom.material}


def interior_of(opening):
    return spec.interior_from_json(opening.btm_custom.interior)


def unique(messages):
    """Mensagens sem repetição, na ordem em que apareceram."""
    return list(dict.fromkeys(messages))


def run_operator(context, op, obj, **kwargs):
    """Chama um operador da biblioteca com `obj` como objeto ativo; devolve o conjunto de retorno."""
    with context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        return op(**kwargs)


# Estrutura e divisões (feature 006, T011; D-04, D-07, D-09) --------------------------------------------------
#
# Contrato opcional dos adaptadores (cada função pode faltar; `call` usa a padrão daqui):
# - `inner_spaces(context, root)` → {caminho-raiz: divisions.Box} no referencial da raiz;
# - `structure_parts(root)` → {papel: [objetos]} das chapas da caixa (só papéis que existem);
# - `structure_caps(root)` → {papel: {'remove': motivo|None, 'thickness': motivo|None, 'modes': {modo: motivo|None}}};
# - `remove_part(context, root, role, mode)`, `restore_part(context, root, role, mode)`,
#   `set_part_thickness(context, root, role, value)`, `reaffirm(context, root)` → mensagens.
# Os dados ficam em `root.btm_structure`; `reaffirm` os reaplica depois que a biblioteca reconstrói as peças.

REMOVED_PROP = 'btm_removed'
RAW_MATERIAL_PROP = 'btm_raw_material'
_DRIVER_VAR = 'btm_rm'
NO_LIBRARY_REASON = N_("Esta biblioteca não tem estrutura editável")
NO_NEIGHBOR_REASON = N_("Esta biblioteca não ajusta as chapas vizinhas; use Manter tudo")


def call(adapter, name, *args):
    """Função `name` do adaptador, ou a padrão (`default_<name>`) deste módulo."""
    fn = getattr(adapter, name, None) or globals()['default_' + name]
    return fn(*args)


def keep_only_caps(parts, thickness=None):
    """Capacidades de quem só faz Manter tudo: remover e editar sim, estender e reduzir não."""
    modes = {'KEEP': None, 'EXTEND': tr(NO_NEIGHBOR_REASON), 'SHRINK': tr(NO_NEIGHBOR_REASON)}
    return {role: {'remove': None, 'thickness': thickness, 'modes': dict(modes)} for role in parts}


def default_inner_spaces(context, root):
    return {}


def default_structure_parts(root):
    return {}


def default_structure_caps(root):
    return {}


def default_remove_part(context, root, role, mode):
    return [tr(NO_LIBRARY_REASON)]


def default_restore_part(context, root, role, mode):
    return [tr(NO_LIBRARY_REASON)]


def default_set_part_thickness(context, root, role, value):
    return [tr(NO_LIBRARY_REASON)]


def default_reaffirm(context, root):
    return reaffirm_parts(context, root)


def local_box(root, obj, depsgraph):
    """Caixa (lo, hi) do objeto avaliado no referencial da raiz, ou None."""
    from mathutils import Vector  # type: ignore
    evaluated = obj.evaluated_get(depsgraph)
    corners = [Vector(c) for c in evaluated.bound_box]
    if all(c.length < 1e-9 for c in corners):
        return None
    to_root = root.matrix_world.inverted_safe() @ obj.matrix_world
    pts = [to_root @ c for c in corners]
    return (tuple(min(p[i] for p in pts) for i in range(3)), tuple(max(p[i] for p in pts) for i in range(3)))


def clip_space(box, part_boxes):
    """Recorta o vão pelas faces internas das chapas da caixa presentes (a espessura sobrescrita cresce para dentro).

    `part_boxes` = {papel: [(lo, hi)]}; só corta quem cruza o vão nos outros dois eixos.
    """
    from ...cabinet_editor.divisions import Box
    lo, hi = list(box.lo), list(box.hi)

    def crosses(b, axes):
        return all(b[0][a] < hi[a] - 1e-6 and b[1][a] > lo[a] + 1e-6 for a in axes)

    for b in part_boxes.get('LEFT', ()):
        if crosses(b, (1, 2)) and b[1][0] > lo[0]:
            lo[0] = min(max(lo[0], b[1][0]), hi[0])
    for b in part_boxes.get('RIGHT', ()):
        if crosses(b, (1, 2)) and b[0][0] < hi[0]:
            hi[0] = max(min(hi[0], b[0][0]), lo[0])
    for b in part_boxes.get('BOTTOM', ()):
        if crosses(b, (0, 1)) and b[1][2] > lo[2]:
            lo[2] = min(max(lo[2], b[1][2]), hi[2])
    for b in part_boxes.get('TOP', ()):
        if crosses(b, (0, 1)) and b[0][2] < hi[2]:
            hi[2] = max(min(hi[2], b[0][2]), lo[2])
    for b in part_boxes.get('BACK', ()):
        if crosses(b, (0, 2)) and b[0][1] < hi[1]:
            hi[1] = max(min(hi[1], b[0][1]), lo[1])
    return Box(tuple(lo), tuple(hi))


def cage_spaces(context, root, adapter, tag):
    """Vãos-raiz a partir das jaulas `tag` (bay/abertura) da biblioteca, da esquerda para a direita."""
    from ...cabinet_editor.divisions import Box
    depsgraph = context.evaluated_depsgraph_get()
    cages = [o for o in root.children_recursive if o.get(tag)]
    boxes = [b for b in (local_box(root, c, depsgraph) for c in cages) if b is not None]
    boxes.sort(key=lambda b: (round(b[0][0], 4), round(b[0][2], 4)))
    parts = {}
    removed = removed_roles(root)
    for role, objs in call(adapter, 'structure_parts', root).items():
        if role in removed:
            continue
        parts[role] = [b for b in (local_box(root, o, depsgraph) for o in objs if not o.hide_viewport)
                       if b is not None]
    return {f"s{i}": clip_space(Box(lo, hi), parts) for i, (lo, hi) in enumerate(boxes)}


def removed_roles(root):
    structure = getattr(root, 'btm_structure', None)
    return {e.role for e in structure.components if e.removed} if structure is not None else set()


def _fcurve(obj, path):
    data = obj.animation_data
    if data is None:
        return None
    return next((fc for fc in data.drivers if fc.data_path == path), None)


def set_removed(obj, removed):
    """Esconde (ou mostra) a peça por driver, somando-se ao esconder que a biblioteca já dirige (D-07)."""
    obj[REMOVED_PROP] = bool(removed)
    for path in ('hide_viewport', 'hide_render'):
        fc = _fcurve(obj, path)
        if fc is None:
            if not removed:
                continue
            fc = obj.driver_add(path)
            fc.driver.expression = _DRIVER_VAR
        driver = fc.driver
        if _DRIVER_VAR not in [v.name for v in driver.variables]:
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = _DRIVER_VAR
            var.targets[0].id = obj
            var.targets[0].data_path = f'["{REMOVED_PROP}"]'
            if driver.expression != _DRIVER_VAR:
                driver.expression = f"({driver.expression}) or {_DRIVER_VAR}"
        if not removed and driver.expression == _DRIVER_VAR:
            obj.driver_remove(path)            # driver só nosso: some e a biblioteca volta a mandar
    if not removed:
        if _fcurve(obj, 'hide_viewport') is None:
            obj.hide_viewport = False
        if _fcurve(obj, 'hide_render') is None:
            obj.hide_render = False
    obj.update_tag()


def is_removed(obj):
    return bool(obj.get(REMOVED_PROP))


def cutpart_thickness(obj):
    mod = gn_modifier(obj, 'GeoNodeCutpart')
    return float(compat.try_get_gn_input(mod, 'Thickness', 0.0) or 0.0) if mod is not None else 0.0


def set_cutpart_thickness(obj, value, drop_driver=False):
    """Grava a espessura da peça; com `drop_driver`, tira antes o driver da biblioteca (frameless)."""
    mod = gn_modifier(obj, 'GeoNodeCutpart')
    if mod is None:
        return False
    if drop_driver:
        path = compat.gn_input_data_path(mod, 'Thickness')
        if _fcurve(obj, path) is not None:
            obj.driver_remove(path)
    compat.try_set_gn_input(mod, 'Thickness', float(value))
    obj.update_tag()
    return True


def reaffirm_parts(context, root, adapter=None, drop_driver=False):
    """Reaplica remoções, espessuras e material da chapa gravados em `root.btm_structure` (após reconstruções)."""
    structure = getattr(root, 'btm_structure', None)
    if structure is None or not structure.components:
        return []
    from . import for_root
    parts = call(adapter or for_root(root), 'structure_parts', root)
    for entry in structure.components:
        for obj in parts.get(entry.role, ()):
            if entry.removed != is_removed(obj):
                set_removed(obj, entry.removed)
            if entry.thickness > 0.0 and abs(cutpart_thickness(obj) - entry.thickness) > 1e-7:
                set_cutpart_thickness(obj, entry.thickness, drop_driver)
            if entry.material:
                obj[RAW_MATERIAL_PROP] = entry.material
            elif RAW_MATERIAL_PROP in obj:
                del obj[RAW_MATERIAL_PROP]
    return []


def parts_by_name(root, names):
    """{papel: [filhos diretos]} pelo nome sem sufixo (frameless): `names` = {nome: papel}."""
    out = {}
    for obj in root.children:
        role = names.get(part_roles.base_name(obj.name))
        if role is not None and is_cutpart(obj):
            out.setdefault(role, []).append(obj)
    return out


def default_structure_info(context, root):
    """{papel: {'size': (comprimento, largura), 'thickness', 'removed'}} a partir da primeira peça de cada papel."""
    from . import for_root
    out = {}
    for role, objs in call(for_root(root), 'structure_parts', root).items():
        mod = gn_modifier(objs[0], 'GeoNodeCutpart')
        length = abs(float(compat.try_get_gn_input(mod, 'Length', 0.0) or 0.0)) if mod is not None else 0.0
        width = abs(float(compat.try_get_gn_input(mod, 'Width', 0.0) or 0.0)) if mod is not None else 0.0
        out[role] = {'size': (max(length, width), min(length, width)), 'thickness': cutpart_thickness(objs[0]),
                     'removed': all(is_removed(o) for o in objs)}
    return out


def default_elevation_parts(context, root):
    return []


# Feature 008 (T021, T063; D-05, D-11) --------------------------------------------------------------------------
def default_opening_boxes(context, root):
    """{caminho do vão da biblioteca: divisions.Box} no referencial da raiz (o módulo inteiro = o vão interno)."""
    from ...cabinet_editor.divisions import Box
    from . import for_root
    adapter = for_root(root)
    depsgraph = context.evaluated_depsgraph_get()
    out = {}
    for path, opening in adapter.openings(root):
        if opening == root:
            spaces = call(adapter, 'inner_spaces', context, root)
            if spaces:
                out[path] = spaces[min(spaces)]
            continue
        box = local_box(root, opening, depsgraph)
        if box is not None:
            out[path] = Box(*box)
    return out


def set_back_recess(context, root, adapter, setback):
    """Fundo recuado nas bibliotecas de peças: a peça do fundo anda `setback` para dentro (para a frente, −Y da
    raiz) pelo `delta_location`, que drivers e recálculos das bibliotecas não sobrescrevem."""
    from mathutils import Vector  # type: ignore
    for obj in call(adapter, 'structure_parts', root).get('BACK', ()):
        to_parent = obj.parent.matrix_world.inverted_safe() if obj.parent is not None else None
        world_dir = root.matrix_world.to_3x3() @ Vector((0.0, -1.0, 0.0))
        local_dir = (to_parent.to_3x3() @ world_dir) if to_parent is not None else world_dir
        if local_dir.length > 1e-9:
            local_dir.normalize()
        obj.delta_location = local_dir * float(setback)
        obj.update_tag()
    return []
