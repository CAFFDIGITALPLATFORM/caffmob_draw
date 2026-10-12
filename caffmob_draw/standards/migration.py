"""Migrações do Padrão de Dimensões em `load_post` (T028; data-delta §5).

- M-01: valores alterados em `btm_settings.dimension_settings` e `btm_settings.config_*` (grupos obsoletos) viram a
  definição "Migrada" (origem MIGRATED), que passa a ser a ativa.
- M-02: projeto sem definição recebe as embutidas; a ativa é "Padrão EUA (HB5)" se já houver gabinetes legados
  (para não mudar medidas de projetos do Home Builder) e "Padrão Brasil" nos demais casos.
- M-03 (feature 012, T004): raiz de módulo sem `btm_standard_uid` recebe o uid do padrão ativo, sem refazer nada.
  Roda a cada abertura (idempotente). `line` e `assembly` dos módulos CAFFMob antigos já leem os padrões das
  propriedades (COZ, lateral passante).

As migrações rodam uma vez por arquivo (marca `btm_standards_migrated` na cena principal), a partir do
`load_file_post` do add-on (handler `@persistent` já existente) e, na abertura sem arquivo, de um timer.
"""

import bpy

from ..data import dimension_schema as schema
from . import api, builtin, sync

MIGRATED_FLAG = 'btm_standards_migrated'
STANDARD_UID_PROP = 'btm_standard_uid'
MIGRATED_NAME = "Migrada"

# config_* (obsoleto) → componentes do padrão (linha Cozinha)
CONFIG_COMPONENTS = {
    'config_lateral': ("LAT",),
    'config_divisoria': ("DIV",),
    'config_base': ("BAS",),
    'config_fundo': ("FUN_INF", "FUN_SUP", "FUN_ALT"),
    'config_prateleira': ("PRAT",),
    'config_porta': ("POR",),
}
CONFIG_FIELDS = ('material', 'max_width', 'max_length', 'thickness', 'edge_1', 'edge_2', 'edge_3', 'edge_4')

# dimension_settings (obsoleto) → chaves do padrão (m → mm)
DIMENSION_SETTINGS_KEYS = {
    'carcass_thickness': ("COZ.sheets.LAT.thickness", "COZ.sheets.DIV.thickness", "COZ.sheets.BAS.thickness"),
    'back_thickness': ("COZ.sheets.FUN_INF.thickness", "COZ.sheets.FUN_SUP.thickness", "COZ.sheets.FUN_ALT.thickness"),
    'door_thickness': ("COZ.sheets.POR.thickness",),
    'shelf_thickness': ("COZ.sheets.PRAT.thickness",),
    'height_default': ("COZ.external.base_height",),
    'depth_default': ("COZ.external.base_depth",),
    'base_height': ("COZ.external.toe_kick_height",),
}


def _is_set(group, prop):
    try:
        return group.is_property_set(prop)
    except (TypeError, AttributeError):
        return False


def legacy_values(settings):
    """Valores (chave → mm ou texto) alterados pelo usuário nos grupos obsoletos; vazio se nada foi alterado."""
    values = {}
    dim = getattr(settings, 'dimension_settings', None)
    if dim is not None:
        for prop, keys in DIMENSION_SETTINGS_KEYS.items():
            if _is_set(dim, prop):
                for key in keys:
                    values[key] = getattr(dim, prop) * 1000.0
    for group_name, components in CONFIG_COMPONENTS.items():
        group = getattr(settings, group_name, None)
        if group is None:
            continue
        for fname in CONFIG_FIELDS:
            if not _is_set(group, fname):
                continue
            raw = getattr(group, fname)
            for component in components:
                key = schema.sheet_key("COZ", component, fname)
                values[key] = raw if fname == 'material' else raw * 1000.0
    valid = {}
    for key, value in values.items():
        param = schema.get_param(key)
        if param is not None and schema.validate(param, value)[0]:
            valid[key] = value
    return valid


LEGACY_TAGS = (sync.FRAMELESS_TAG, sync.CLOSET_TAG, 'IS_FACE_FRAME_CABINET_CAGE')   # face frame também (pergunta 52)


def _has_legacy_cabinets(scene):
    return any(o.get(tag) for o in scene.objects for tag in LEGACY_TAGS)


def migrate_scene(scene):
    """Executa M-01/M-02 na cena principal. Devolve a lista das migrações aplicadas."""
    data = api.standards(scene)
    if data is None or scene.get(MIGRATED_FLAG):
        return []
    applied = []
    had_definitions = len(data.definitions) > 0
    api.ensure_ready(scene)
    if not had_definitions:
        uid = builtin.BUILTIN_US_UID if _has_legacy_cabinets(scene) else builtin.BUILTIN_BR_UID
        api.set_active(scene, api.find_definition(scene, uid=uid))
        applied.append('M-02')
    settings = getattr(scene, 'btm_settings', None)
    values = legacy_values(settings) if settings is not None else {}
    if values and api.find_definition(scene, name=MIGRATED_NAME) is None:
        base = api.find_definition(scene, uid=builtin.BUILTIN_BR_UID)
        definition = api.duplicate_definition(scene, base, name=MIGRATED_NAME)
        definition.source = 'MIGRATED'
        api.set_values(definition, values)
        api.set_active(scene, definition)
        applied.append('M-01')
    scene[MIGRATED_FLAG] = 1
    return applied


def stamp_standard_uid(scene):
    """M-03: grava o padrão de origem nas raízes de módulo que ainda não o têm. Devolve quantas foram marcadas."""
    from ..selection import classify
    definition = api.active_definition(scene)
    if definition is None:
        return 0
    count = 0
    for obj in scene.objects:
        if classify.module_library(obj) and not obj.get(STANDARD_UID_PROP):
            obj[STANDARD_UID_PROP] = definition.uid
            count += 1
    return count


def run(scene=None):
    """Chamado pelo `load_file_post` do add-on depois de garantir a cena principal."""
    scene = api.main_scene(scene or bpy.context.scene)
    if scene is None:
        return []
    try:
        applied = migrate_scene(scene)
        if stamp_standard_uid(scene):
            applied.append('M-03')
        return applied
    except api.StandardsError as exc:
        print(f"CAFFMob Draw: migração do Padrão de Dimensões não aplicada: {exc}")
        return []
    except Exception:                       # o resto do load_file_post precisa continuar (EC-14)
        import traceback
        print("CAFFMob Draw: falha inesperada na migração do Padrão de Dimensões")
        traceback.print_exc()
        return []


def _startup_timer():
    """Abertura do Blender sem carregar arquivo: `load_post` não dispara, então a migração roda uma vez aqui."""
    if bpy.context.scene is not None:
        run(bpy.context.scene)
    return None


def register():
    if not bpy.app.timers.is_registered(_startup_timer):
        bpy.app.timers.register(_startup_timer, first_interval=0.5)


def unregister():
    if bpy.app.timers.is_registered(_startup_timer):
        bpy.app.timers.unregister(_startup_timer)
