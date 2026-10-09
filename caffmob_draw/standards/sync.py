"""Sincronização Padrão de Dimensões → módulos do projeto (T019; D-05, D-06, D-16a; RN-23).

Grava os valores da definição nas propriedades de cena consumidas pelo frameless (`Scene.hb_frameless`) e pelo
closets (`Scene.hb_closets`), conforme `legacy_targets` do esquema, para os arquivos antigos abrirem coerentes.

Feature 012 (T031; D-20, D-21, RN-10, RN-11): quem é atualizado são os **módulos CAFFMob**, cada um na sua linha
(espessuras por papel, montagem, altura e profundidade do tipo; a largura fica). `scene_modules` classifica a cena
para as duas perguntas (`apply_core`): segue, difere (padrão próprio ou outro padrão de origem) e não aplicável
(armário herdado não convertido, item importado). Os armários herdados só são atualizados no modo de suporte
(`legacy/gate.py`), como antes.
"""

import json

import bpy

from ..data import dimension_schema as schema

OVERRIDES_PROP = 'btm_overrides'
LINE_PROP = 'btm_line'

FRAMELESS_TAG = 'IS_FRAMELESS_CABINET_CAGE'
CLOSET_TAG = 'IS_CLOSET_STARTER_CAGE'

# Profundidade de sincronização em andamento: escritas feitas pela sincronização não viram medida manual.
_SYNC_DEPTH = [0]


def is_syncing():
    return _SYNC_DEPTH[0] > 0


# ----------------------------------------------------------------------------------------------------------------
# Medidas editadas à mão (btm_overrides)
# ----------------------------------------------------------------------------------------------------------------

def module_root(obj):
    """Objeto raiz do módulo (gabinete frameless ou starter de closets) que contém `obj`."""
    current = obj
    while current is not None:
        if current.get(FRAMELESS_TAG) or current.get(CLOSET_TAG):
            return current
        current = current.parent
    return None


def get_overrides(obj):
    raw = obj.get(OVERRIDES_PROP)
    if not raw:
        return set()
    try:
        return set(json.loads(raw))
    except (TypeError, ValueError):
        return set()


def add_override(obj, name):
    """Marca `name` como medida editada à mão no módulo de `obj` (usado pelos diálogos de prompts)."""
    root = module_root(obj) or obj
    overrides = get_overrides(root)
    if name not in overrides:
        overrides.add(name)
        root[OVERRIDES_PROP] = json.dumps(sorted(overrides))


def clear_overrides(obj):
    root = module_root(obj) or obj
    if OVERRIDES_PROP in root:
        del root[OVERRIDES_PROP]


def make_skip(include_manual, skipped):
    """Função `skip(obj, nome)` para as rotinas de atualização; conta as medidas puladas em `skipped`."""
    def skip(obj, name):
        if include_manual:
            return False
        root = module_root(obj) or obj
        if name in get_overrides(root):
            skipped.append((root.name, name))
            return True
        return False
    return skip


# ----------------------------------------------------------------------------------------------------------------
# Contagem e escrita
# ----------------------------------------------------------------------------------------------------------------

def affected_modules(scene):
    """Módulos que a aplicação de uma definição pode alterar (para a confirmação "N módulos" — D-16a).
    Feature 012: os módulos CAFFMob (os herdados só no modo de suporte)."""
    from ..legacy import gate
    found = [obj for obj in scene.objects if is_caffmob_module(obj)]
    if gate.legacy_ui():
        found += [obj for obj in scene.objects if obj.get(FRAMELESS_TAG) or obj.get(CLOSET_TAG)]
    return found


def _scenes_for(scene):
    from . import api
    main = api.main_scene(scene)
    scenes = [main] if main else []
    if scene is not None and scene not in scenes:
        scenes.append(scene)
    return scenes


def write_legacy_targets(scene, values):
    """Grava em `Scene.hb_frameless` / `Scene.hb_closets` (metros). Devolve a lista de destinos escritos."""
    written = []
    for key, param in schema.PARAMS.items():
        if not param.legacy_targets or key not in values:
            continue
        meters = float(values[key]) / 1000.0
        for target in param.legacy_targets:
            group_name, prop = target.split('.', 1)
            for sc in _scenes_for(scene):
                group = getattr(sc, group_name, None)
                if group is None or not hasattr(group, prop):
                    continue
                if abs(getattr(group, prop) - meters) > 1e-9:
                    setattr(group, prop, meters)
                written.append(target)
    return sorted(set(written))


def _update_frameless(context, skip):
    from ..product_libraries.frameless.operators import ops_defaults
    touched = 0
    touched += ops_defaults.update_material_thickness_prompts(context, skip)
    touched += ops_defaults.update_toe_kick_prompts(context, skip)
    touched += ops_defaults.update_cabinet_sizes(context, skip)
    return touched


def _update_closets(scene, skip):
    from ..product_libraries.closets import types_closets
    props = scene.hb_closets
    heights = {'BASE': props.base_panel_height, 'TALL': props.tall_panel_height}
    count = 0
    for root in [obj for obj in scene.objects if obj.get(CLOSET_TAG)]:
        starter = getattr(root, 'hb_closet_starter', None)
        if starter is None:
            continue
        targets = {
            'toe_kick_height': props.toe_kick_height,
            'toe_kick_setback': props.toe_kick_setback,
            'depth': props.default_panel_depth,
        }
        if starter.closet_type in heights:
            targets['height'] = heights[starter.closet_type]
        for name, value in targets.items():
            if not skip(root, name) and abs(getattr(starter, name) - value) > 1e-9:
                setattr(starter, name, value)
        # A espessura de painel/prateleira é lida da cena no recálculo.
        types_closets.recalculate_closet_starter(root)
        count += 1
    return count


def _tag_lines(scene):
    for obj in scene.objects:
        if obj.get(FRAMELESS_TAG) and not obj.get(LINE_PROP):
            obj[LINE_PROP] = 'COZ'
        elif obj.get(CLOSET_TAG) and not obj.get(LINE_PROP):
            obj[LINE_PROP] = 'DOR'


def apply_definition(scene, definition, include_manual=False, changed_keys=None, modules=None):
    """Aplica a definição ao projeto. `modules` = objetos CAFFMob escolhidos pelas perguntas (None = todos os que
    seguem o padrão). Devolve o relatório da sincronização."""
    _SYNC_DEPTH[0] += 1
    try:
        return _apply_definition(scene, definition, include_manual, changed_keys, modules)
    finally:
        _SYNC_DEPTH[0] -= 1


# ----------------------------------------------------------------------------------------------------------------
# Módulos CAFFMob (feature 012)
# ----------------------------------------------------------------------------------------------------------------

STANDARD_UID_PROP = 'btm_standard_uid'


def is_caffmob_module(obj):
    from ..selection import classify
    return obj.type == 'MESH' and classify.btm_kind(obj) == 'MODULE' and getattr(obj, 'btm_cabinet', None) is not None


def _other_roots(scene, taken):
    """Componentes não paramétricos de topo: grupos de peças (SketchUp, OBJ) e itens da biblioteca de objetos."""
    from ..selection import classify
    found = []
    for obj in scene.objects:
        if obj.name in taken or classify.module_root(obj)[0] is not None:
            continue
        group = getattr(obj, 'btm_group', None)
        item = getattr(obj, 'btm_object_item', None)
        is_root = (group is not None and group.is_group) or (item is not None and item.is_item)
        if is_root and classify.free_group(obj) in (None, obj):
            found.append(obj)
    return found


def scene_modules(scene, context=None):
    """[(objeto, apply_core.ModuleInfo)] da cena: CAFFMob, herdados (raízes) e outros componentes de topo."""
    from ..cabinet_editor import bridge
    from ..legacy import gate
    from . import apply_core
    context = context or bpy.context
    out = []
    for obj in scene.objects:
        if is_caffmob_module(obj):
            own = bridge.is_own_standard(context, obj)
            out.append((obj, apply_core.ModuleInfo(obj.name, apply_core.CAFFMOB, obj.get(STANDARD_UID_PROP, ""), own)))
    for obj in gate.legacy_roots(scene):
        out.append((obj, apply_core.ModuleInfo(obj.name, apply_core.LEGACY, obj.get(STANDARD_UID_PROP, ""), False)))
    taken = {obj.name for obj, _info in out}
    for obj in _other_roots(scene, taken):
        out.append((obj, apply_core.ModuleInfo(obj.name, apply_core.OTHER, "", False)))
    return out


def plan_for(scene, previous_uid, context=None):
    from . import apply_core
    modules = scene_modules(scene, context)
    return apply_core.plan([info for _obj, info in modules], previous_uid), {obj.name: obj for obj, _i in modules}


def apply_to_module(context, obj, definition, values):
    """Leva o módulo CAFFMob ao padrão: chapas e medidas da linha dele, montagem do padrão; a largura fica."""
    from ..data.properties import suspended_geometry, update_cabinet_geom
    from . import cabinet_defaults
    cab = obj.btm_cabinet
    found = cabinet_defaults.defaults(values, cab.line, cab.cabinet_type)
    with suspended_geometry():
        cab.height, cab.depth, cab.thickness = found.height, found.depth, found.carcass
        for role in ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT'):
            value = found.thickness.get(role, found.carcass)
            setattr(cab, 'thickness_' + role.lower(), 0.0 if abs(value - found.carcass) < 1e-9 else value)
        cab.assembly = getattr(definition, 'assembly', 'LATERAL')
    structure = getattr(obj, 'btm_structure', None)
    if structure is not None:
        for entry in structure.components:
            entry.thickness = 0.0                       # sai o padrão próprio de espessura
    clear_overrides(obj)
    obj[STANDARD_UID_PROP] = definition.uid
    obj[LINE_PROP] = cab.line
    update_cabinet_geom(cab, context)


def _apply_definition(scene, definition, include_manual, changed_keys, modules=None):
    from ..legacy import gate
    from . import api
    context = bpy.context
    scene = scene or context.scene
    values = api.definition_values(definition)
    targets = write_legacy_targets(scene, values)
    skipped = []
    skip = make_skip(include_manual, skipped)
    _tag_lines(scene)
    if modules is None:          # sem as perguntas (scripts): todos os CAFFMob, e os de padrão próprio com include_manual
        modules = [obj for obj, info in scene_modules(scene, context)
                   if info.kind == 'CAFFMOB' and (include_manual or not info.own)]
    caffmob_count = 0
    for obj in modules:
        if obj.name in bpy.data.objects and is_caffmob_module(obj):
            apply_to_module(context, obj, definition, values)
            caffmob_count += 1
    frameless_count = closets_count = 0
    if gate.legacy_ui(context):  # modo de suporte: sincronização herdada, como antes da 012
        frameless_count = len([o for o in scene.objects if o.get(FRAMELESS_TAG)])
        if frameless_count and hasattr(scene, 'hb_frameless'):
            _update_frameless(context, skip)
        closets_count = _update_closets(scene, skip) if hasattr(scene, 'hb_closets') else 0
    settings = getattr(scene, 'btm_settings', None)
    if settings is not None and hasattr(settings, 'cut_plan_stale'):
        settings.cut_plan_stale = True
    keys = changed_keys if changed_keys is not None else []
    without_target = [k for k in keys if k in schema.PARAMS and not schema.PARAMS[k].legacy_targets]
    return {
        'definition': definition.name,
        'modules_updated': caffmob_count + frameless_count + closets_count,
        'caffmob': caffmob_count,
        'frameless': frameless_count,
        'closets': closets_count,
        'targets_written': targets,
        'skipped_manual': skipped,
        'without_target': without_target,
    }
