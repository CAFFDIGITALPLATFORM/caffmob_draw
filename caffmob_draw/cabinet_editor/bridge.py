"""Ponte do Editor de Armário com a cena (feature 004, T044; D-21, D-22, D-23).

- `read_state(root)`: medidas (`selection/editing`) + personalização da 003 (`adapter.read`) + os valores crus de
  `btm_custom` (vãos, raiz e peças), para que reaplicar um instantâneo devolva exatamente o que havia.
- `apply_state(context, root, target)`: leva o módulo ao instantâneo. Muda só o que difere (medida, frente do vão,
  divisões internas), grava os campos crus de `btm_custom` e reaplica pela biblioteca. Chamado de dentro do modal do
  editor: os operadores das bibliotecas usados pelos adaptadores não criam passos de desfazer próprios (D-22).
- `edit(context, root, action, data)`: as edições do editor (frente, estilo, puxador, material, interior), as mesmas
  dos operadores de `customize/ops_customize.py`, sem passar por operador.
- `parts(root)`: caixas das peças no referencial da raiz, para a vista frontal (`elevation.Part`).
- Feature 006 (T021; D-11): o instantâneo leva também a estrutura (`root.btm_structure`) e as divisões; `edit` ganha
  `ADD_DIVISION`, `EDIT_DIVISION`, `REMOVE_DIVISION`, `EDIT_PART`, `REMOVE_PART` e `RESTORE_PART`. A ordem importa:
  o registro em `btm_structure` muda **antes** do adaptador, porque o recálculo das bibliotecas reafirma o que estiver
  gravado.
"""

from mathutils import Vector  # type: ignore

from ..customize import adapters, reapply, spec
from ..customize.adapters import common
from ..cutting import part_roles
from ..selection import classify, editing
from . import divisions as dv
from . import bays as _bays
from . import catalog, elevation, scene_divisions, scene_extras, scene_interiors, scene_slides
from . import state as _state
from . import structure as st

CUSTOM_FIELDS = ('door_style', 'drawer_style', 'pull_model', 'pull_position', 'front_material', 'interior')
_LIBRARY_HOLDER = {'FACE_FRAME': 'face_frame_cabinet', 'CLOSETS': 'hb_closet_starter', 'BTM': 'btm_cabinet'}
_SKIP_TAGS = ('IS_CUTTING_OBJ', 'IS_2D_ANNOTATION', 'IS_DIMENSION', 'obj_x')


def info_of(root):
    return classify.classify(root)


def adapter_of(root):
    return adapters.for_root(root)


# Leitura ---------------------------------------------------------------------------------------------------
def _raw(root, adapter):
    openings = {}
    for path, opening in adapter.openings(root):
        custom = opening.btm_custom
        openings[path] = {name: getattr(custom, name) for name in CUSTOM_FIELDS}
    custom = root.btm_custom
    groups = {item.group: item.material for item in custom.group_materials}
    parts = {obj.name: obj.btm_custom.material for obj in root.children_recursive
             if getattr(obj, 'btm_custom', None) is not None and obj.btm_custom.material}
    return {"openings": openings, "pull_model": custom.pull_model, "pull_all_fronts": bool(custom.pull_all_fronts),
            "groups": groups, "parts": parts}


def read_state(root):
    info = info_of(root)
    adapter = adapter_of(root)
    dims = tuple(float(editing.get_dimension(info, f) or 0.0) for f in ('width', 'height', 'depth'))
    data = spec.to_dict(adapter.read(root)) if adapter is not None else {}
    if adapter is not None:
        data["_raw"] = _raw(root, adapter)
    holder = getattr(root, 'btm_structure', None)
    structure = holder.to_dict() if holder is not None else {}
    return _state.EditorState(dims, data, structure, scene_divisions.read(root),
                              extras=holder.extras_dict() if holder is not None else {},
                              slides=scene_slides.state_of(root), interiors=scene_interiors.entries(root),
                              backs=holder.backs_dict() if holder is not None else {},
                              assembly=root.btm_cabinet.assembly if is_caffmob_module(root) else "",
                              **_structure_fields(root))


_CARCASS_ROLES = ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT')


def _structure_fields(root):
    """Estrutura de caixa e chapas presentes do módulo CAFFMob, para o instantâneo do editor (feature 015)."""
    if not is_caffmob_module(root):
        return {}
    cab = root.btm_cabinet
    return {'structure_id': cab.structure_id,
            'present': {role: bool(getattr(cab, 'has_' + role.lower())) for role in _CARCASS_ROLES}}


def set_structure(context, root, structure_id, present):
    """Leva o módulo CAFFMob à estrutura `structure_id` com as chapas `present`; refaz malha, divisões e extras."""
    from ..data.properties import suspended_geometry, update_cabinet_geom
    cab = root.btm_cabinet
    with suspended_geometry():
        cab.structure_id = structure_id
        for role, value in (present or {}).items():
            setattr(cab, 'has_' + role.lower(), bool(value))
    update_cabinet_geom(cab, context)
    scene_divisions.reflow(context, root, force=True)
    scene_extras.sync(context, root)
    return []


def migrate_structure(context, root):
    """Módulo CAFFMob de antes da 015 passa para a estrutura equivalente (RN-22, D-06); devolve o id ou None."""
    from . import structures_core
    if not is_caffmob_module(root) or root.btm_cabinet.structure_id:
        return None
    cab = root.btm_cabinet
    structure_id = structures_core.load().legacy_structure(cab.line, cab.cabinet_type)
    recipe = structures_core.get(structure_id)
    if recipe is None:
        return None
    set_structure(context, root, recipe.id, {role: recipe.has(role) for role in _CARCASS_ROLES})
    return recipe.id


def library_limits(root, library):
    holder = getattr(root, _LIBRARY_HOLDER.get(library, ''), None)
    out = {}
    if holder is None:
        return out
    for field in ('width', 'height', 'depth'):
        prop = holder.bl_rna.properties.get(field)
        if prop is not None:
            out[field] = (max(prop.hard_min, 0.0), prop.hard_max)
    return out


# Escrita ---------------------------------------------------------------------------------------------------
def set_dimension(context, root, field, value):
    editing.set_dimension(context, info_of(root), field, value)


def _openings(root, adapter):
    return dict(adapter.openings(root))


def apply_state(context, root, target):
    """Leva o módulo ao instantâneo `target`; devolve os avisos da biblioteca."""
    adapter = adapter_of(root)
    messages = []
    current = read_state(root)
    for index, field in enumerate(('width', 'height', 'depth')):
        if abs(current.dimensions[index] - target.dimensions[index]) > 1e-7:
            set_dimension(context, root, field, target.dimensions[index])
    if target.assembly and target.assembly != current.assembly:
        messages += set_assembly(context, root, {'assembly': target.assembly})
    if is_caffmob_module(root) and (target.structure_id, target.present) != (current.structure_id, current.present):
        messages += set_structure(context, root, target.structure_id, target.present)   # feature 015
    if adapter is None:
        return messages
    migrate_paths(context, root, adapter, target.spec)
    wanted = spec.from_dict(target.spec)
    now = spec.from_dict(current.spec)
    openings = _openings(root, adapter)
    for item in wanted.openings:
        opening = openings.get(item.path)
        cur = now.opening(item.path)
        if opening is None or cur is None:
            continue
        if item.front and (item.front, item.drawer_count) != (cur.front, cur.drawer_count):
            messages += adapter.set_front(context, root, opening, item.front, item.drawer_count or 1)
            openings = _openings(root, adapter)
            opening = openings.get(item.path, opening)
        if item.interior is not None and item.interior != cur.interior:
            messages += adapter.set_interior(context, root, opening, item.interior)
    raw = target.spec.get("_raw", {})
    openings = _openings(root, adapter)
    for path, fields in raw.get("openings", {}).items():
        opening = openings.get(path)
        if opening is None:
            continue
        for name, value in fields.items():
            if getattr(opening.btm_custom, name) != value:
                setattr(opening.btm_custom, name, value)
    custom = root.btm_custom
    custom.pull_model = raw.get("pull_model", custom.pull_model)
    custom.pull_all_fronts = raw.get("pull_all_fronts", custom.pull_all_fronts)
    groups = raw.get("groups", {})
    for group in spec.GROUPS:
        if custom.group_material(group) != groups.get(group, ""):
            custom.set_group_material(group, groups.get(group, ""))
    parts = raw.get("parts", {})
    for obj in root.children_recursive:
        if getattr(obj, 'btm_custom', None) is not None and obj.btm_custom.material != parts.get(obj.name, ""):
            obj.btm_custom.material = parts.get(obj.name, "")
    messages += reapply.reapply(context, root)
    messages += _apply_structure(context, root, current.structure, target.structure)
    if target.backs != current.backs:
        messages += set_back(context, root, dict(target.backs or {'mode': 'FULL', 'setback': 0.02, 'auto': True}))
    if target.divisions != scene_divisions.read(root):
        scene_divisions.apply(context, root, target.divisions)
    else:
        scene_divisions.reflow(context, root, force=True)
    # Internos, extras e deslizantes só são refeitos quando a parte deles ou a geometria mudou (DT-09).
    geometry = (target.dimensions != current.dimensions or target.structure != current.structure
                or target.divisions != current.divisions or target.backs != current.backs)
    if target.extras != current.extras:
        root.btm_structure.extras_from_dict(target.extras)
    if geometry or target.extras != current.extras:
        scene_extras.sync(context, root)
        if target.extras != current.extras and is_caffmob_module(root) and root.btm_cabinet.structure_id:
            from ..data.properties import update_cabinet_geom         # peças da estrutura na árvore (015)
            update_cabinet_geom(root.btm_cabinet, context)
    if geometry or target.interiors != current.interiors:
        scene_interiors.apply(context, root, target.interiors)
    if _slides_key(target.slides) != _slides_key(current.slides) or (geometry and target.slides):
        scene_slides.apply(context, root, target.slides)
    return messages


def migrate_paths(context, root, adapter, data):
    """M-06 (067 T107): vão do instantâneo sem caminho (ou com caminho que não existe mais) é lido pelo vão atual e
    regravado com o caminho. No módulo rápido o vão atual de um pedido antigo é o módulo inteiro; nas bibliotecas,
    o vão que contém o centro do subvão gravado (`space`), quando houver. Devolve quantos vãos foram regravados."""
    known = {path for path, _o in adapter.openings(root)}
    count = 0
    for item in data.get('openings', []):
        path = item.get('path', '')
        if path in known:
            continue
        found = library_opening(context, root, item.get('space', '')) if item.get('space') else None
        if found is None and getattr(adapter, 'LIBRARY', '') == 'BTM':
            found = "module"
        if found is not None and found != path:
            item['path'] = found
            count += 1
    return count


def _slides_key(state):
    return {k: v for k, v in (state or {}).items() if k != 'opens'}


def reflow_all(context, root):
    """Depois de mudar medidas, estrutura ou divisões: divisões, extras, internos e deslizantes no lugar novo."""
    scene_divisions.reflow(context, root, force=True)
    scene_extras.sync(context, root)
    scene_interiors.reflow(context, root)
    scene_slides.reflow(context, root)


def edit(context, root, action, data):
    """Uma edição do editor sobre o vão `data['path']`; devolve os avisos da biblioteca."""
    if action in EDIT_006:
        return EDIT_006[action](context, root, data)
    if action in EDIT_008:
        return EDIT_008[action](context, root, data)
    adapter = adapter_of(root)
    if adapter is None:
        return []
    opening = _openings(root, adapter).get(data.get('path', ''))
    if action == 'FRONT':
        if opening is None:
            return []
        if data.get('gaveta') and adapter.LIBRARY == 'BTM':       # 072 (D-06): construtor de gavetas
            return adapter.set_front(context, root, opening, data['front'], data.get('drawer_count', 1),
                                     data['gaveta']) + reapply.reapply(context, root)
        current = adapter.read(root).opening(data.get('path', ''))
        if current is not None and (current.front, current.drawer_count or 0) == (
                data['front'], data.get('drawer_count', 1) if data['front'] == 'DRAWERS' else 0):
            return []                      # mesma frente: nada a refazer (o face frame reconstruiria o vão)
        return adapter.set_front(context, root, opening, data['front'], data.get('drawer_count', 1)) + \
            reapply.reapply(context, root)
    if action == 'STYLE':
        if opening is None:
            return []
        setattr(opening.btm_custom, 'door_style' if data.get('kind', 'DOOR') == 'DOOR' else 'drawer_style',
                data.get('style', ""))
    elif action == 'PULL':
        root.btm_custom.pull_all_fronts = bool(data.get('all_fronts'))
        if data.get('all_fronts'):
            root.btm_custom.pull_model = data.get('model', "")
            for _path, other in adapter.openings(root):
                other.btm_custom.pull_position = data.get('position', 'DEFAULT')
        elif opening is not None:
            opening.btm_custom.pull_model = data.get('model', "")
            opening.btm_custom.pull_position = data.get('position', 'DEFAULT')
    elif action == 'MATERIAL':
        target = data.get('target', 'GROUP')
        if target == 'GROUP':
            root.btm_custom.set_group_material(data['group'], data.get('material', ""))
        elif target == 'FRONTS' and opening is not None:
            opening.btm_custom.front_material = data.get('material', "")
    elif action == 'INTERIOR':
        if opening is None:
            return []
        inner = spec.Interior(int(data.get('shelves', 0)), int(data.get('dividers', 0)), int(data.get('drawers', 0)),
                              list(data.get('heights', [])))
        messages = adapter.set_interior(context, root, opening, inner)
        return messages or reapply.reapply(context, root)
    return reapply.reapply(context, root)


# Vista frontal ---------------------------------------------------------------------------------------------
def _own_corners(obj, to_root, depsgraph):
    if obj.type != 'MESH':
        return []
    evaluated = obj.evaluated_get(depsgraph)
    corners = [Vector(c) for c in evaluated.bound_box]
    if all(c.length < 1e-9 for c in corners):
        return []
    return [to_root @ c for c in corners]


def _kind(obj, opening_names):
    if obj.name in opening_names:
        return elevation.OPENING
    agg = getattr(obj, 'btm_aggregate', None)
    if agg is not None and agg.is_aggregate:
        return elevation.AGGREGATE
    if classify.classify(obj).kind == classify.FRONT or obj.get('IS_CABINET_FRONT'):
        return elevation.FRONT
    code = part_roles.classify(obj.name, obj.get('hb_part_role'), component=obj.get(scene_divisions.COMPONENT_PROP))
    return elevation.kind_from_role(code)


def root_box(root, depsgraph):
    from ..stick import apply as stick_apply
    return stick_apply.local_box(root, depsgraph)


def parts(context, root):
    """Peças visíveis do módulo como `elevation.Part`, com a origem no canto mínimo da caixa da raiz."""
    depsgraph = context.evaluated_depsgraph_get()
    adapter = adapter_of(root)
    opening_names = {o.name for _p, o in adapter.openings(root)} if adapter is not None else set()
    lo_root, _hi = root_box(root, depsgraph)
    shift = Vector(lo_root)
    to_root_world = root.matrix_world.inverted_safe()
    out = []
    for obj in root.children_recursive:
        if obj.name not in opening_names and (any(obj.get(tag) for tag in _SKIP_TAGS) or obj.hide_viewport
                                              or not obj.visible_get() or obj.display_type in {'WIRE', 'BOUNDS'}):
            continue                       # gaiolas em arame e auxiliares não são peças; os vãos entram tracejados
        corners = _own_corners(obj, to_root_world @ obj.matrix_world, depsgraph)
        if not corners:
            continue
        lo = tuple(min(c[i] for c in corners) - shift[i] for i in range(3))
        hi = tuple(max(c[i] for c in corners) - shift[i] for i in range(3))
        out.append(elevation.Part(obj.name, _kind(obj, opening_names), lo, hi))
    if adapter is not None:              # chapas que não são objetos (malha única do `btm`, feature 006)
        for name, _role, lo, hi in common.call(adapter, 'elevation_parts', context, root):
            out.append(elevation.Part(name, elevation.STRUCTURE, tuple(lo[i] - shift[i] for i in range(3)),
                                      tuple(hi[i] - shift[i] for i in range(3))))
    return out


def view_shift(context, root):
    """Origem da vista frontal no referencial da raiz (canto mínimo da caixa do módulo)."""
    lo, _hi = root_box(root, context.evaluated_depsgraph_get())
    return tuple(lo)


def root_size(context, root):
    lo, hi = root_box(root, context.evaluated_depsgraph_get())
    return tuple(hi[i] - lo[i] for i in range(3))


def opening_of(root, name):
    """Caminho do vão que contém o componente `name` (o próprio vão, uma frente ou peça dentro dele)."""
    adapter = adapter_of(root)
    if adapter is None or not name:
        return None
    import bpy  # type: ignore
    obj = bpy.data.objects.get(name)
    best = None
    for path, opening in adapter.openings(root):
        node = obj
        while node is not None:
            if node == opening:
                if best is None or len(opening.children_recursive) < len(best[1].children_recursive):
                    best = (path, opening)
                break
            node = node.parent
    return best[0] if best else None


# Estrutura e divisões (feature 006, T021) -----------------------------------------------------------------------
def structure_rows(context, root):
    """[(papel, info, capacidades, estado)] na ordem de `structure.ROLES`, só dos papéis que o módulo tem."""
    adapter = adapter_of(root)
    if adapter is None:
        return []
    info = common.call(adapter, 'structure_info', context, root)
    caps = common.call(adapter, 'structure_caps', root)
    states = st.state_from_dict(root.btm_structure.to_dict())
    return [(role, info[role], caps.get(role, {}), states.get(role, st.RoleState()))
            for role in st.ROLES if role in info]


def configured_part(context, root, role):
    """(material, espessura em m) do componente do Configurador para o papel, na linha do módulo."""
    from ..data import dimension_schema as schema
    from ..standards import api
    line = scene_divisions.line_of(root)
    component = st.ROLE_COMPONENT[role]
    material = api.get_value(context.scene, schema.sheet_key(line, component, 'material')) or 'MDF'
    thickness = api.get_value_m(context.scene, schema.sheet_key(line, component, 'thickness')) or 0.0
    return str(material), float(thickness)


# Montagem e padrão próprio (feature 012, T028; D-09, D-12) ---------------------------------------------------
def is_caffmob_module(root):
    from ..selection import classify
    return root is not None and classify.btm_kind(root) == 'MODULE' and getattr(root, 'btm_cabinet', None) is not None


def origin_definition(context, root):
    """Padrão global de origem do módulo (`btm_standard_uid`), ou o ativo se não houver."""
    from ..standards import api
    uid = root.get('btm_standard_uid', "")
    return (api.find_definition(context.scene, uid=uid) if uid else None) or api.active_definition(context.scene)


def is_own_standard(context, root):
    """O módulo CAFFMob tem padrão próprio (montagem, espessura por papel ou valores à mão diferentes do padrão)?"""
    from ..standards import apply_core, sync
    if not is_caffmob_module(root):
        return False
    origin = origin_definition(context, root)
    origin_assembly = getattr(origin, 'assembly', 'LATERAL') if origin is not None else 'LATERAL'
    thickness = [entry.thickness for entry in root.btm_structure.components] if hasattr(root, 'btm_structure') else []
    return apply_core.is_own(sync.get_overrides(root), root.btm_cabinet.assembly, origin_assembly, thickness)


def set_assembly(context, root, data):
    """Troca a montagem do módulo CAFFMob; a malha e a lista de corte seguem (propriedade com `update`)."""
    if not is_caffmob_module(root):
        return [common.tr("Só armários CAFFMob têm montagem")]
    if root.btm_cabinet.assembly != data['assembly']:
        root.btm_cabinet.assembly = data['assembly']
        scene_divisions.reflow(context, root, force=True)
    return []


def _item(root, role):
    return root.btm_structure.item(role, create=True)


def _tidy(root, role):
    """Tira o registro do papel quando ele voltou ao padrão (nada removido nem sobrescrito)."""
    components = root.btm_structure.components
    for index, entry in enumerate(components):
        if entry.role == role and not entry.removed and not entry.thickness and not entry.material:
            components.remove(index)
            return


def remove_part(context, root, data):
    role, mode = data['role'], data.get('mode', st.KEEP)
    adapter = adapter_of(root)
    caps = common.call(adapter, 'structure_caps', root).get(role)
    if not caps or caps.get('remove'):
        return [caps.get('remove') if caps else common.tr(common.NO_LIBRARY_REASON)]
    mode, reason = st.allowed_mode(mode, caps.get('modes', {}))
    entry = _item(root, role)
    if entry.removed:
        return []
    entry.removed, entry.mode = True, mode
    messages = [reason] if reason else []
    messages += common.call(adapter, 'remove_part', context, root, role, mode)
    scene_divisions.reflow(context, root, force=True)
    return messages


def restore_part(context, root, data):
    role = data['role']
    entry = root.btm_structure.item(role)
    if entry is None or not entry.removed:
        return []
    mode = entry.mode
    entry.removed, entry.mode = False, st.KEEP
    messages = common.call(adapter_of(root), 'restore_part', context, root, role, mode)
    _tidy(root, role)
    scene_divisions.reflow(context, root, force=True)
    return messages


def edit_part(context, root, data):
    role = data['role']
    adapter = adapter_of(root)
    entry = _item(root, role)
    messages = []
    if 'thickness' in data:
        value = float(data['thickness'] or 0.0)
        caps = common.call(adapter, 'structure_caps', root).get(role, {})
        if caps.get('thickness'):
            return [caps['thickness']]
        if abs(entry.thickness - value) > 1e-9:
            entry.thickness = value
            messages += common.call(adapter, 'set_part_thickness', context, root, role, value)
    if 'material' in data:
        entry.material = data['material'] or ""
    messages += common.call(adapter, 'reaffirm', context, root)
    _tidy(root, role)
    scene_divisions.reflow(context, root, force=True)
    return messages


def _apply_structure(context, root, current, target):
    """Leva a estrutura do módulo de `current` a `target` (dicionários de `BTM_PG_Structure.to_dict`)."""
    messages = []
    now = st.state_from_dict(current)
    wanted = st.state_from_dict(target)
    for role in st.ROLES:
        a, b = now.get(role, st.RoleState()), wanted.get(role, st.RoleState())
        if a == b:
            continue
        if a.removed and (not b.removed or a.mode != b.mode):
            messages += restore_part(context, root, {'role': role})
        if (a.thickness, a.material) != (b.thickness, b.material):
            messages += edit_part(context, root, {'role': role, 'thickness': b.thickness, 'material': b.material})
        if b.removed and not (a.removed and a.mode == b.mode):
            messages += remove_part(context, root, {'role': role, 'mode': b.mode})
    return messages


def division_context(context, root):
    """(vãos-raiz, divisões como `divisions.Division`, dicionários crus, nomes {uid: objeto})."""
    raw = scene_divisions.read(root)
    return (scene_divisions.roots(context, root), scene_divisions.core(context.scene, root, raw), raw,
            scene_divisions.names(root))


def _raw_entry(division, own_thickness=False):
    """Dicionário cru (006) da divisão: espessura 0 = do Configurador, salvo distanciador (espessura própria)."""
    return dict(dv.to_dict(division), thickness=division.thickness if own_thickness else 0.0, material="")


def add_division(context, root, data):
    roots, core, raw, _names = division_context(context, root)
    _material, thickness = scene_divisions.configured(context.scene, root)
    kind = data.get('kind', dv.FIXED)
    own = float(data.get('thickness') or 0.0)
    space = data['space']
    follow = ""
    if data.get('follow'):                           # distanciador p/ divisão: logo depois da divisória do vão
        parent = space.rsplit(".", 1)[0] if "." in space else ""
        followed = next((d for d in core if d.space == parent and d.kind != dv.SPACER), None)
        if followed is None:
            raise ValueError(common.tr("Escolha o vão logo à direita (ou acima) de uma divisória"))
        follow = followed.uid
    added = dv.add(roots, core, space, data['orientation'], own or thickness,
                   use_front=data.get('use_front', False), front=data.get('front', dv.DEFAULT_SETBACK),
                   use_back=data.get('use_back', False), back=data.get('back', dv.DEFAULT_SETBACK),
                   kind=kind, follow=follow, variant=data.get('variant', ""))[-1]
    scene_divisions.apply(context, root, raw + [_raw_entry(added, own_thickness=bool(own))])
    reflow_all(context, root)
    return []


def edit_division(context, root, data):
    raw = scene_divisions.read(root)
    changes = {k: v for k, v in data.items() if k != 'uid'}
    scene_divisions.apply(context, root, [dict(d, **changes) if d['uid'] == data['uid'] else d for d in raw])
    return []


def remove_division(context, root, data):
    _roots, core, raw, _names = division_context(context, root)
    _rest, removed = dv.remove(core, data['uid'])
    scene_divisions.apply(context, root, [d for d in raw if d['uid'] not in removed])
    reflow_all(context, root)
    return []


# Feature 008 (T028, T029, T056) --------------------------------------------------------------------------------
def toggle_extra(context, root, data):
    """Caixa da árvore da Estrutura (extras): liga/desliga e valor (D-07). Base Superior Recuada troca o tampo."""
    key = data['key']
    entry = root.btm_structure.extra(key, create=True)
    if 'value' in data:
        entry.value = float(data['value'])
    messages = []
    if 'enabled' in data and bool(data['enabled']) != entry.enabled:
        entry.enabled = bool(data['enabled'])
        if key == 'BASE_TOP_RECESSED':
            action = remove_part if entry.enabled else restore_part
            messages += action(context, root, {'role': 'TOP', 'mode': st.KEEP})
    scene_extras.sync(context, root)
    if key in catalog.STRUCTURE_KEYS and is_caffmob_module(root) and root.btm_cabinet.structure_id:
        from ..data.properties import update_cabinet_geom             # sarrafos, tampo, rodapé (feature 015)
        update_cabinet_geom(root.btm_cabinet, context)
        scene_divisions.reflow(context, root, force=True)
    return messages


def set_bays(context, root, data):
    roots, core, raw, _names = division_context(context, root)
    if int(data['count']) != _bays.count(core) and any(d.space == _bays.ROOT and not d.bay for d in core):
        # s0 já cortado por divisória comum: recusa em vez de quebrar o layout (questions.md, pergunta 44)
        raise ValueError(common.tr("Tire a divisória que corta o vão inteiro antes de mudar o Número de vãos"))
    _material, thickness = scene_divisions.configured(context.scene, root)
    new = _bays.apply(roots, core, int(data['count']), thickness)
    by_uid = {d['uid']: d for d in raw}
    out = []
    for division in new:
        base = by_uid.get(division.uid)
        out.append(dict(base, space=division.space, offset=division.offset) if base is not None
                   else _raw_entry(division))
    scene_divisions.apply(context, root, out)
    reflow_all(context, root)
    removed = _bays.removed(core, new)
    return [common.tr("{} divisória(s) de vão removida(s)").format(len(removed))] if removed else []


def set_bay_width(context, root, data):
    """Largura digitada de um vão (feature 015, RN-14, D-15): grava na divisória de vão à direita dele e refaz os
    vãos; os livres dividem o que sobra. O último vão é sempre calculado; largura que não cabe é recusada."""
    roots, core, raw, _names = division_context(context, root)
    total = _bays.count(core)
    index = int(data['index'])
    if index >= total - 1:
        raise ValueError(common.tr("O último vão é calculado: digite a largura de outro vão"))
    _material, thickness = scene_divisions.configured(context.scene, root)
    dividers = sorted((d for d in core if d.bay), key=lambda d: dv.depth_of(d.space))
    typed = [d.bay_width for d in dividers]
    typed[index] = max(0.0, float(data['width']))
    found, short = _bays.widths(roots[_bays.ROOT].size(0), total, thickness, typed)
    if found is None:
        raise ValueError(common.tr("A largura não cabe: os outros vãos ficariam com {:.0f} mm").format(short * 1000.0))
    target = dividers[index].uid
    raw = [dict(d, bay_width=typed[index]) if d['uid'] == target else d for d in raw]
    core = [dv.replace(d, bay_width=typed[index]) if d.uid == target else d for d in core]
    new = _bays.apply(roots, core, total, thickness)
    by_uid = {d['uid']: d for d in raw}
    out = []
    for division in new:
        base = by_uid.get(division.uid)
        out.append(dict(base, space=division.space, offset=division.offset) if base is not None
                   else _raw_entry(division))
    scene_divisions.apply(context, root, out)
    reflow_all(context, root)
    return []


def set_back(context, root, data):
    """Aba Fundos: inteiro/recuado, recuo, inserir automaticamente; "insert" devolve o fundo removido (D-11)."""
    adapter = adapter_of(root)
    if adapter is not None and adapter.LIBRARY != 'BTM' and not common.call(adapter, 'structure_parts', root).get('BACK'):
        return [common.tr("Este armário não tem fundo")]
    holder = root.btm_structure
    holder.backs_from_dict(dict(holder.backs_dict(), **{k: v for k, v in data.items()
                                                        if k in ('mode', 'setback', 'auto')}))
    messages = []
    entry = holder.item('BACK')
    if data.get('insert') and entry is not None and entry.removed:
        messages += restore_part(context, root, {'role': 'BACK'})
    setback = holder.back_setback if holder.back_mode == 'RECESSED' else 0.0
    messages += common.call(adapter_of(root), 'set_back_recess', context, root, setback)
    reflow_all(context, root)
    return messages


def add_many(context, root, data):
    roots, core, raw, _names = division_context(context, root)
    _material, thickness = scene_divisions.configured(context.scene, root)
    new = dv.add_many(roots, core, data['space'], data['orientation'], int(data['count']), thickness,
                      use_front=data.get('use_front', False), front=data.get('front', dv.DEFAULT_SETBACK),
                      use_back=data.get('use_back', False), back=data.get('back', dv.DEFAULT_SETBACK),
                      kind=data.get('kind', dv.FIXED))
    known = {d['uid'] for d in raw}
    scene_divisions.apply(context, root, raw + [_raw_entry(d) for d in new if d.uid not in known])
    reflow_all(context, root)
    return []


def remove_in_space(context, root, data):
    """Sem Divisória: tira a divisória que criou o vão alvo (e as de dentro dela)."""
    _roots, core, raw, _names = division_context(context, root)
    _rest, removed = dv.remove_in_space(core, data['space'])
    if not removed:
        return [common.tr("Este vão não tem divisória para remover")]
    if any(d.bay for d in core if d.uid in removed):      # divisória de vão: só pelo Número de vãos (EC-20)
        return [common.tr("Esta divisória separa os vãos do armário: mude o Número de vãos")]
    scene_divisions.apply(context, root, [d for d in raw if d['uid'] not in removed])
    reflow_all(context, root)
    return []


def library_opening(context, root, space_path):
    """Caminho do vão da biblioteca que contém o centro do subvão `space_path` (D-05), ou None.

    067 (D-23; RF-103): no módulo rápido a frente vai no próprio subvão, pelo caminho dele (o vão da biblioteca é o
    vazio do subvão, criado aqui); o vão-raiz, sem divisão, é o módulo inteiro.
    """
    adapter = adapter_of(root)
    if adapter is None or not space_path:
        return None
    if getattr(adapter, 'LIBRARY', '') == 'BTM':
        if space_path in division_context(context, root)[0]:
            return "module"
        from ..geometry import subspace_fronts
        if space_path not in adapter.space_boxes(context, root):
            return None
        subspace_fronts.holder(root, space_path)
        return space_path
    roots, core, _raw, _names = division_context(context, root)
    box = dv.resolve(roots, core)[0].get(space_path)
    if box is None:
        return None
    center = [(box.lo[i] + box.hi[i]) / 2.0 for i in range(3)]
    inside = [(path, b) for path, b in common.call(adapter, 'opening_boxes', context, root).items()
              if all(b.lo[i] - 1e-4 <= center[i] <= b.hi[i] + 1e-4 for i in range(3))]
    if not inside:
        return None
    return min(inside, key=lambda item: item[1].size(0) * item[1].size(2))[0]


DOOR_FRONTS = {('BOTH', False): 'DOUBLE_DOORS', ('BOTH', True): 'DOUBLE_DOORS',
               ('WHOLE', False): 'DOOR_LEFT', ('WHOLE', True): 'DOOR_RIGHT',
               ('LEFT', False): 'DOOR_LEFT', ('LEFT', True): 'DOOR_RIGHT',
               ('RIGHT', False): 'DOOR_RIGHT', ('RIGHT', True): 'DOOR_LEFT'}


def _front_steps(context, root, path, front, count, kind, style, pull, gaveta=None):
    messages = edit(context, root, 'FRONT', {'path': path, 'front': front, 'drawer_count': count, 'gaveta': gaveta})
    if style:
        messages += edit(context, root, 'STYLE', {'path': path, 'kind': kind, 'style': style})
    if pull:
        messages += edit(context, root, 'PULL', {'path': path, 'model': pull, 'position': 'DEFAULT',
                                                 'all_fronts': False})
    return messages


def insert_doors(context, root, data):
    path = library_opening(context, root, data['space'])
    if path is None:
        return [common.tr("Este vão não pertence a um vão da biblioteca")]
    if data.get('scope') == 'FLIP' or data.get('region') == 'FLIP':
        front = 'FLIP_UP'
    else:
        front = DOOR_FRONTS[(data.get('scope', 'BOTH'), bool(data.get('invert')))]
    return _front_steps(context, root, path, front, 1, 'DOOR', data.get('style', ""), data.get('pull', ""))


def insert_drawers(context, root, data):
    """Gavetas, Gavetões, Internas e Blum no vão da biblioteca do alvo (D-23)."""
    path = library_opening(context, root, data['space'])
    if path is None:
        return [common.tr("Este vão não pertence a um vão da biblioteca")]
    variant = data.get('variant', 'DRAWERS')
    count = int(data.get('count', 4))
    if variant == 'TALL':
        count = max(2, min(4, count))
    adapter = adapter_of(root)
    opening = _openings(root, adapter).get(path)
    if variant == 'INTERNAL':
        if adapter.LIBRARY != 'FRAMELESS':
            return [common.tr("Gaveta interna só existe no frameless")]
        messages = adapter.set_interior(context, root, opening, spec.Interior(drawers=count))
        return messages + reapply.reapply(context, root)
    if opening is not None:
        opening.btm_custom.slide_kind = 'BLUM' if variant == 'BLUM' else ""
    return _front_steps(context, root, path, 'DRAWERS', count, 'DRAWER', data.get('style', ""), data.get('pull', ""),
                        data.get('gaveta'))


def insert_interior(context, root, data):
    item = catalog.get(data['catalog_id'])
    roots, core, _raw, _names = division_context(context, root)
    box = dv.resolve(roots, core)[0].get(data['space'])
    if item is None or box is None:
        return [common.tr("Escolha um vão livre")]
    from . import appliances, wardrobe
    if item.action == 'INSERT_WARDROBE':                 # roupeiro (feature 015): medida mínima do vão
        small = wardrobe.too_small(item.param('kind'), (box.lo, box.hi))
        if small is not None:
            return [common.tr("{} precisa de um vão de {:.0f} mm de largura").format(
                common.tr(item.label), small[0] * 1000.0)]
    need = appliances.missing(box, item.id)
    if need is not None and need[2] > 0:
        return [common.tr("{} precisa de um vão de {:.0f} × {:.0f} mm e {:.0f} mm de profundidade").format(
            item.label, need[0], need[1], need[2])]
    if need is not None:
        return [common.tr("{} precisa de um vão de {:.0f} × {:.0f} mm").format(item.label, need[0], need[1])]
    current = scene_interiors.entries(root)
    slot = 1 + max([e["slot"] for e in current] or [0])
    scene_interiors.apply(context, root, current + [{"catalog_id": item.id, "space": data['space'], "slot": slot}])
    return []


def remove_interior(context, root, data):
    rest = [e for e in scene_interiors.entries(root) if e["slot"] != data.get('slot')]
    scene_interiors.apply(context, root, rest)
    return []


def insert_slides(context, root, data):
    _roots, core, _raw, _names = division_context(context, root)
    if _bays.count(core) > 1:                      # ocupariam o 1º vão-raiz inteiro (questions.md, pergunta 45)
        return [common.tr("Deslizantes não vão em armário com mais de um vão: deixe o Número de vãos em 1")]
    warnings = scene_slides.apply(context, root, {"item": data['item'], "leaves": int(data.get('leaves', 2)),
                                                  "invert": bool(data.get('invert'))})
    out = []
    for warning in warnings:
        kind = warning[0] if isinstance(warning, tuple) else None
        if kind == 'BLOCKED':
            out.append(common.tr("{} não corre: esbarra em {}").format(warning[1], warning[2] or "—"))
        elif kind == 'NO_SPACE':                       # não é falta de profundidade (EC-09)
            out.append(common.tr("Sem vão interno para os deslizantes"))
        elif kind == 'DEPTH':
            from ..data import units
            depth = units.format_length(warning[1], units.get_scene_length_unit(context.scene))
            out.append(common.tr("Os trilhos precisam de mais profundidade ({})").format(depth))
        else:
            out.append(common.tr("Os trilhos precisam de mais profundidade ({})").format(warning))
    return out


def remove_slides(context, root, data):
    scene_slides.apply(context, root, {})
    return []


EDIT_008 = {'TOGGLE_EXTRA': toggle_extra, 'SET_BAYS': set_bays, 'SET_BACK': set_back, 'ADD_MANY': add_many,
            'REMOVE_IN_SPACE': remove_in_space, 'INSERT_DOORS': insert_doors, 'INSERT_DRAWERS': insert_drawers,
            'INSERT_INTERIOR': insert_interior, 'REMOVE_INTERIOR': remove_interior, 'INSERT_SLIDES': insert_slides,
            'REMOVE_SLIDES': remove_slides, 'SET_BAY_WIDTH': set_bay_width}


EDIT_006 = {'ADD_DIVISION': add_division, 'EDIT_DIVISION': edit_division, 'REMOVE_DIVISION': remove_division,
            'EDIT_PART': edit_part, 'REMOVE_PART': remove_part, 'RESTORE_PART': restore_part,
            'SET_ASSEMBLY': set_assembly}
