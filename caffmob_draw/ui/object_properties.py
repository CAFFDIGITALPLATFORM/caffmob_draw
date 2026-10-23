"""Janela de propriedades por tipo de objeto (T023; D-10, RN-01 a RN-04, M-08).

A seção Selecionado da barra lateral (`draw_selected`, feature 005; antes o painel `BTM_PT_ObjectProperties`) mostra o
objeto ATIVO e só os grupos do tipo dele, no máximo 4 abertos:
- linha de estado: tipo, nome, L × A × P e rotação;
- Dimensões: largura, altura, profundidade (módulos; largura e altura de portas e janelas de ambiente);
- Cotas: afastamento da parede, anterior, posterior, inferior e superior (módulos), editáveis;
- Abrir: frentes do módulo (inspeção da 001);
- Parede: comprimento, pé-direito inicial e final, espessura;
- Outras: biblioteca e coleções;
- Ações: o menu do botão direito do objeto (`MENU_ID`).

Os campos editáveis são propriedades virtuais em `Scene.btm_selection` (com `get`/`set`): a cena tem desfazer, então
cada edição vira um passo de Ctrl+Z (RN-03). Valor inválido não é aplicado e a mensagem aparece no painel.
"""

import math

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from ..data import units
from ..data.i18n import N_, tr
from ..measure import cotas as cotas_mod
from ..measure import scene_cotas
from ..selection import classify, editing

ERROR_KEY = 'btm_selection_error'


def _info():
    return classify.classify(bpy.context.active_object)


def _set_error(message):
    wm = bpy.context.window_manager
    if wm is not None:
        wm[ERROR_KEY] = message


def _clear_error():
    wm = bpy.context.window_manager
    if wm is not None and ERROR_KEY in wm:
        del wm[ERROR_KEY]


def _guard(apply):
    try:
        apply()
        _clear_error()
    except ValueError as exc:
        _set_error(str(exc))


# Dimensões -------------------------------------------------------------------------------------------------

def _dim_getter(field):
    def get(_self):
        info = _info()
        if info is None or not editing.has_dimensions(info) and info.kind not in (classify.FRONT, classify.PART):
            return 0.0
        try:
            return float(editing.get_dimension(info, field))
        except Exception:
            return 0.0
    return get


def _dim_setter(field):
    def set_(_self, value):
        info = _info()
        if info is not None:
            _guard(lambda: editing.set_dimension(bpy.context, info, field, value))
    return set_


# Cotas -----------------------------------------------------------------------------------------------------

def _cota_getter(field):
    def get(_self):
        obj = getattr(bpy.context, 'active_object', None)    # timer, salvamento: sem objeto ativo (BUG-20261023-7YO4)
        try:
            mc = scene_cotas.for_object(obj, bpy.context.scene) if obj else None
            value = getattr(mc.compute(), field) if mc is not None else None
        except ValueError:                # parede sem o modificador ou o input Length: o desenho segue (EC-08)
            return 0.0
        return 0.0 if value is None else float(value)
    return get


def _cota_setter(field):
    def set_(_self, value):
        obj = getattr(bpy.context, 'active_object', None)
        mc = scene_cotas.for_object(obj, bpy.context.scene) if obj else None
        if mc is not None:
            _guard(lambda: mc.apply(field, value))
    return set_


# Parede e peitoril -----------------------------------------------------------------------------------------

def _wall_getter(field):
    def get(_self):
        info = _info()
        if info is None or info.kind != classify.WALL or info.library != 'HB':
            return 0.0
        try:
            return float(editing.get_wall(info, field))
        except Exception:
            return 0.0
    return get


def _wall_setter(field):
    def set_(_self, value):
        info = _info()
        if info is not None and info.kind == classify.WALL:
            _guard(lambda: editing.set_wall(info, field, value))
    return set_


def _get_sill(_self):
    info = _info()
    return float(editing.get_sill(info)) if info and info.kind in (classify.WINDOW, classify.ROOM_DOOR) else 0.0


def _set_sill(_self, value):
    info = _info()
    if info is not None:
        _guard(lambda: editing.set_sill(info, value))


def _length(name, getter, setter, description=""):
    # Sem 'ANIMATABLE': o campo escreve no objeto ativo; um driver nele move o ativo a cada avaliação e derruba o
    # Blender (BUG-20261023-GAVK).
    return bpy.props.FloatProperty(name=name, description=description, subtype='DISTANCE', unit='LENGTH',
                                   precision=1, get=getter, set=setter, options=set())


class BTM_PG_SelectionEdit(bpy.types.PropertyGroup):
    """Campos virtuais da janela de propriedades (não guardam valor: leem e escrevem no objeto ativo)."""
    width: _length(N_("Largura"), _dim_getter('width'), _dim_setter('width'))  # type: ignore
    height: _length(N_("Altura"), _dim_getter('height'), _dim_setter('height'))  # type: ignore
    depth: _length(N_("Profundidade"), _dim_getter('depth'), _dim_setter('depth'))  # type: ignore
    afastamento: _length(N_("Afastamento da parede"), _cota_getter('afastamento'), _cota_setter('afastamento'),
                         N_("Do fundo do módulo até a face da parede"))  # type: ignore
    anterior: _length(N_("Cota anterior"), _cota_getter('anterior'), _cota_setter('anterior'),
                      N_("Da lateral esquerda até o item ou o fim de parede mais próximo"))  # type: ignore
    posterior: _length(N_("Cota posterior"), _cota_getter('posterior'), _cota_setter('posterior'),
                       N_("Da lateral direita até o item ou o fim de parede mais próximo"))  # type: ignore
    inferior: _length(N_("Cota inferior"), _cota_getter('inferior'), _cota_setter('inferior'),
                      N_("Do piso até a base do módulo"))  # type: ignore
    superior: _length(N_("Cota superior"), _cota_getter('superior'), _cota_setter('superior'),
                      N_("Do topo do módulo até o teto"))  # type: ignore
    sill: _length(N_("Peitoril"), _get_sill, _set_sill)  # type: ignore
    wall_length: _length(N_("Comprimento"), _wall_getter('length'), _wall_setter('length'))  # type: ignore
    wall_height: _length(N_("Pé-direito inicial"), _wall_getter('height'), _wall_setter('height'))  # type: ignore
    wall_end_height: _length(N_("Pé-direito final"), _wall_getter('end_height'), _wall_setter('end_height'))  # type: ignore
    wall_thickness: _length(N_("Espessura"), _wall_getter('thickness'), _wall_setter('thickness'))  # type: ignore


# Painel ----------------------------------------------------------------------------------------------------

def _status_line(info):
    obj = info.obj
    if info.kind in (classify.MODULE, classify.FRONT, classify.PART):
        try:
            module = classify.classify(info.root)
            dims = [editing.get_dimension(module, f) for f in ('width', 'height', 'depth')]
        except Exception:
            dims = [obj.dimensions.x, obj.dimensions.z, obj.dimensions.y]
    else:
        dims = [obj.dimensions.x, obj.dimensions.z, obj.dimensions.y]
    size = " × ".join(units.format_value(d) for d in dims)
    rotation = math.degrees(obj.matrix_world.to_euler().z) % 360.0
    return tr("{}: {} ({}) — rotação {:.0f}°").format(tr(classify.KIND_LABELS[info.kind]), obj.name, size, rotation)


def _draw_dimensions(layout, edit, info):
    fields = editing.editable_dimensions(info)
    box = layout.box()
    box.label(text="Dimensões", icon='FIXED_SIZE')
    col = box.column(align=True)
    if fields:
        for field in fields:
            col.prop(edit, field)
    else:
        d = info.obj.dimensions
        col.label(text=f"{units.format_value(d.x)} × {units.format_value(d.z)} × {units.format_value(d.y)}")
    if info.kind == classify.WINDOW and info.library == 'HB':
        col.prop(edit, 'sill')
    if (info.kind in (classify.MODULE, classify.FRONT, classify.PART)
            and bpy.types.Operator.bl_rna_get_subclass_py('CAFFMOB_OT_cabinet_editor') is not None):
        box.operator("caffmob.cabinet_editor", text="Abrir editor de armário", icon='MOD_BUILD')   # feature 004


def _draw_cotas(layout, edit, context):
    mc = scene_cotas.for_object(context.active_object, context.scene)
    if mc is None:
        return
    box = layout.box()
    box.label(text="Cotas", icon='DRIVER_DISTANCE')
    col = box.column(align=True)
    if mc.on_wall:
        for field in cotas_mod.FIELDS:
            col.prop(edit, field)
        box.operator("caffmob.move_on_wall", text="Mover na Parede", icon='ARROW_LEFTRIGHT')
    else:
        col.label(text="Módulo livre (sem parede): só cotas verticais.", icon='INFO')
        col.prop(edit, 'inferior')
        col.prop(edit, 'superior')


def _draw_open(layout, context, info):
    from ..openings.ops import door_of
    if door_of(context.active_object) is not None:
        from .menus import draw_door_controls
        draw_door_controls(layout, context)
        return
    from ..inspection import fronts
    module = info.root
    module_fronts = fronts.fronts_of(module, context.scene)
    if not module_fronts:
        return
    box = layout.box()
    box.label(text="Abrir", icon='HIDE_OFF')
    if info.kind == classify.FRONT:
        box.label(text=tr("Módulo: {}").format(module.name))
        scope = 'SELECTED'
    else:
        scope = 'ACTIVE_MODULE'
    row = box.row(align=True)
    for label, mode in (("Abrir 90°", 'OPEN_90'), ("45°", 'OPEN_45'), ("Fechar", 'CLOSE')):
        op = row.operator("caffmob.fronts_set_open", text=label)
        op.scope, op.mode = scope, mode


def _draw_wall(layout, edit, info):
    box = layout.box()
    box.label(text="Parede", icon='MOD_BUILD')
    col = box.column(align=True)
    if info.library == 'HB':
        for field in ('wall_length', 'wall_height', 'wall_end_height', 'wall_thickness'):
            col.prop(edit, field)
    else:
        wall = info.obj.btm_wall
        for field in ('length', 'thickness', 'height_start', 'height_end', 'offset'):
            col.prop(wall, field)
    if info.library == 'HB':
        row = box.row(align=True)
        lowered = bool(info.obj.get('btm_wall_lowered'))
        row.operator("caffmob.wall_lower", text="Restaurar Altura" if lowered else "Rebaixar", icon='TRIA_DOWN_BAR')
        row.operator_menu_enum("caffmob.wall_visibility", "mode", text="Visibilidade", icon='HIDE_OFF')
        row = box.row()
        row.alert = True
        row.operator("caffmob.wall_remove", text="Remover Parede…", icon='TRASH')


def _draw_geometry(layout, info):
    g = getattr(info.obj, 'btm_geometry', None)
    if g is None:
        _draw_dimensions(layout, None, info)
        return
    box = layout.box()
    box.label(text="Geometria", icon='MESH_CUBE')
    col = box.column(align=True)
    col.prop(g, 'kind')
    if g.kind == 'PLACA':
        col.prop(g, 'plane')
    for field in ('width', 'depth', 'height'):
        if g.kind == 'PLACA' and {'XY': 'height', 'XZ': 'depth', 'YZ': 'width'}[g.plane] == field:
            continue
        col.prop(g, field)
    col.prop(g, 'thickness')
    from ..geometry_free import mesh
    if mesh.thinner_than_thickness(g.kind, g.plane, g.width, g.depth, g.height, g.thickness):
        col.label(text="Uma medida da placa é menor que a espessura", icon='ERROR')
    col.prop(info.obj, 'location', text="Posição")
    fab = layout.box()
    fab.prop(g, 'fabrication')
    sub = fab.column(align=True)
    sub.enabled = g.fabrication
    for field in ('component', 'material', 'finish'):
        sub.prop(g, field)
    row = layout.row(align=True)
    row.operator("caffmob.geometry_duplicate", text="Duplicar", icon='DUPLICATE')
    row.operator("caffmob.geometry_mirror", text="Espelhar", icon='MOD_MIRROR')
    row.operator("caffmob.geometry_delete", text="Excluir", icon='TRASH')


def _draw_btm_opening(layout, info):
    opening = getattr(info.obj, 'btm_opening', None)
    if opening is None:
        return
    box = layout.box()
    box.label(text="Abertura", icon='MOD_BOOLEAN')
    col = box.column(align=True)
    for field in ('opening_type', 'width', 'height', 'sill_height'):
        col.prop(opening, field)
    row = box.row()
    row.alert = True
    row.operator("caffmob.remove_opening", text="Remover Abertura", icon='TRASH')


def _draw_other(layout, info):
    box = layout.box()
    box.label(text="Outras", icon='INFO')
    col = box.column(align=True)
    library = classify.LIBRARY_LABELS.get(info.library, "")
    if library:
        col.label(text=tr("Linha: {}").format(library))
    col.label(text=tr("Coleção: {}").format(', '.join(c.name for c in info.obj.users_collection) or '—'))


def _draw_actions(layout, info):
    menu_id = info.root.get('MENU_ID') or info.obj.get('MENU_ID')
    if not menu_id or getattr(bpy.types, menu_id, None) is None and bpy.types.Menu.bl_rna_get_subclass_py(menu_id) is None:
        return
    box = layout.box()
    box.label(text="Ações", icon='TOOL_SETTINGS')
    box.menu_contents(menu_id)


def _status(layout, context, info):
    selected = len(context.selected_objects)
    status = layout.column(align=True)
    status.label(text=_status_line(info), icon='OBJECT_DATA')
    if selected > 1:
        status.label(text=tr("{} objetos selecionados — editando o ativo.").format(selected))
    error = context.window_manager.get(ERROR_KEY)
    if error:
        row = layout.row()
        row.alert = True
        row.label(text=error, icon='ERROR')


def _main_groups(layout, context, info, edit):
    """Os grupos abertos por padrão (no máximo 4, RN-05 da feature 005)."""
    from . import sidebar_proxy
    from .sidebar import group_scope
    kind = info.kind
    if kind in (classify.MODULE, classify.FRONT, classify.PART):
        module = classify.classify(info.root)
        with group_scope(layout, context, 'sel_dimensions', N_("Medidas e cotas"), 'FIXED_SIZE') as body:
            if body is not None:
                _draw_dimensions(body, edit, module)
                _draw_cotas(body, edit, context)
                sidebar_proxy.draw_panel(BTM_PT_ObjectLimits, body, context)
        from ..customize import panels as customize_panels
        if sidebar_proxy.visible(customize_panels.BTM_PT_CustomizeModule, context):
            with group_scope(layout, context, 'sel_customize', N_("Personalizar"), 'MODIFIER') as body:
                if body is not None:
                    sidebar_proxy.draw_panel(customize_panels.BTM_PT_CustomizeModule, body, context)
        _position_group(layout, context)
        with group_scope(layout, context, 'sel_open', N_("Abrir"), 'HIDE_OFF') as body:
            if body is not None:
                _draw_open(body, context, info)
        return
    with group_scope(layout, context, 'sel_dimensions', _GROUP_TITLE.get(kind, N_("Medidas")), 'FIXED_SIZE') as body:
        if body is not None:
            if kind in (classify.ROOM_DOOR, classify.WINDOW):
                if info.library == 'BTM':
                    _draw_btm_opening(body, info)
                else:
                    _draw_dimensions(body, edit, info)
            elif kind == classify.WALL:
                _draw_wall(body, edit, info)
            elif kind == classify.GEOMETRY:
                _draw_geometry(body, info)
            elif kind in (classify.OBSTACLE, classify.FLOOR, classify.CEILING):
                _draw_dimensions(body, edit, info)
            else:
                d = info.obj.dimensions
                body.label(text=f"{units.format_value(d.x)} × {units.format_value(d.z)} × {units.format_value(d.y)}")
            sidebar_proxy.draw_panel(BTM_PT_ObjectLimits, body, context)
    if kind not in (classify.WALL, classify.FLOOR, classify.CEILING):
        _position_group(layout, context)
    if kind == classify.ROOM_DOOR:
        with group_scope(layout, context, 'sel_open', N_("Abrir"), 'HIDE_OFF') as body:
            if body is not None:
                _draw_open(body, context, info)       # folha 3D criada no primeiro "Abrir" (D-20 da 002)


_GROUP_TITLE = {classify.WALL: N_("Parede"), classify.GEOMETRY: N_("Geometria"), classify.ROOM_DOOR: N_("Abertura"),
                classify.WINDOW: N_("Abertura"), classify.OBSTACLE: N_("Obstáculo"), classify.FLOOR: N_("Piso"),
                classify.CEILING: N_("Teto")}


def _position_group(layout, context):
    from . import sidebar_proxy
    from .sidebar import group_scope
    from ..stick import panels as stick_panels
    with group_scope(layout, context, 'sel_position', N_("Posição e vínculo"), 'ORIENTATION_GLOBAL') as body:
        if body is not None:
            sidebar_proxy.draw_panel(BTM_PT_ObjectMovement, body, context)
            sidebar_proxy.draw_panel(stick_panels.BTM_PT_Stick, body, context)


def _folded_groups(layout, context, info):
    """Grupos recolhidos por padrão: agregados, colisão do item, arranjo, outras e ações, opções do face frame."""
    from . import sidebar_proxy
    from .sidebar import group_scope
    from ..aggregates import panels as aggregate_panels
    from ..collision import panels as collision_panels
    with group_scope(layout, context, 'sel_aggregates', N_("Agregados e folhas"), 'LINKED') as body:
        if body is not None:
            aggregate_panels.draw_aggregate(body, context, include_import=False)
    if sidebar_proxy.visible(collision_panels.BTM_PT_ItemCollision, context):
        with group_scope(layout, context, 'sel_collision', N_("Colisão"), 'MOD_PHYSICS') as body:
            if body is not None:
                sidebar_proxy.draw_panel(collision_panels.BTM_PT_ItemCollision, body, context)
    with group_scope(layout, context, 'sel_arrangement', N_("Arranjo"), 'OUTLINER') as body:
        if body is not None:
            sidebar_proxy.draw_panel(BTM_PT_ObjectArrangement, body, context)
    with group_scope(layout, context, 'sel_actions', N_("Outras e ações"), 'TOOL_SETTINGS') as body:
        if body is not None:
            _draw_other(body, info)
            _draw_actions(body, info)


def draw_selected(layout, context):
    """Seção Selecionado da barra lateral (feature 005, T016; RN-05, D-07): só o que vale para o tipo do objeto ativo,
    com no máximo 4 grupos abertos; o resto fica recolhido."""
    info = classify.classify(context.active_object)
    if info is None:
        layout.label(text=tr("Selecione um objeto na viewport"), icon='INFO')
        return
    _status(layout, context, info)
    edit = context.scene.btm_selection
    _main_groups(layout, context, info, edit)
    _folded_groups(layout, context, info)


# Seções Arranjo / Movimentação / Limites (feature 003, T061; RF-29, RF-30, D-25). "Modelos" é o painel
# "Personalizar módulo" (`customize/panels.py`) e "Agregados e folhas" fica em `aggregates/panels.py`.

class _ChildPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None


class BTM_PT_ObjectArrangement(_ChildPanel, bpy.types.Panel):
    bl_label = "Arranjo"
    bl_idname = "BTM_PT_object_arrangement"

    def draw(self, context):
        layout = self.layout
        info = classify.classify(context.active_object)
        root = info.root if info is not None else context.active_object
        col = layout.column(align=True)
        col.label(text=tr("Objeto: {}").format(root.name), icon='OBJECT_DATA')
        col.label(text=tr("Pai: {}").format(root.parent.name if root.parent else '—'), icon='LINKED')
        children = [c for c in root.children if not c.hide_get()]
        col.label(text=tr("Filhos: {}").format(len(children)), icon='OUTLINER')
        aggregates = [c for c in root.children_recursive if getattr(c, 'btm_aggregate', None) is not None
                      and c.btm_aggregate.is_aggregate]
        if aggregates:
            box = layout.box()
            box.label(text=tr("Agregados ({})").format(len(aggregates)), icon='LINKED')
            for obj in aggregates[:12]:
                kind = "folha" if obj.btm_aggregate.kind == 'LEAF' else "agregado"
                box.label(text=f"{obj.name} ({kind})")


class BTM_PT_ObjectMovement(_ChildPanel, bpy.types.Panel):
    bl_label = "Movimentação"
    bl_idname = "BTM_PT_object_movement"

    def draw(self, context):
        layout = self.layout
        info = classify.classify(context.active_object)
        root = info.root if info is not None else context.active_object
        col = layout.column(align=True)
        col.prop(root, "location", text="Posição")
        col.prop(root, "rotation_euler", index=2, text="Rotação Z")
        state = context.window_manager.btm_move_over
        layout.prop(state, "enabled", text="Mover Sobre (botão direito + arraste)", toggle=True, icon='ORIENTATION_VIEW')
        row = layout.row(align=True)
        row.prop(state, "step")
        row.prop(state, "show_relative", text="Relativa")
        plane = context.window_manager.btm_insertion_plane
        row = layout.row(align=True)
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("caffmob.set_insertion_plane", text="Plano de inserção", icon='SNAP_FACE')
        if plane.active:
            row.operator("caffmob.clear_insertion_plane", text="", icon='X')
            layout.label(text=tr("Plano ativo: face de {}").format(plane.source_name), icon='INFO')


def _range(owner, name):
    prop = owner.bl_rna.properties[name]
    return prop.hard_min, prop.hard_max


class BTM_PT_ObjectLimits(_ChildPanel, bpy.types.Panel):
    bl_label = "Dimensões e limites"
    bl_idname = "BTM_PT_object_limits"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        scene = context.scene
        info = classify.classify(obj)
        root = info.root if info is not None else obj
        col = layout.column(align=True)
        cabinet = getattr(root, 'btm_cabinet', None)
        if info is not None and info.library == 'BTM' and cabinet is not None:
            for name, label in (('width', "Largura"), ('height', "Altura"), ('depth', "Profundidade")):
                lo, hi = _range(cabinet, name)
                col.label(text=tr("{}: {}  (mín. {}, máx. {})").format(label, units.format_value(getattr(cabinet, name), scene), units.format_value(lo, scene), units.format_value(hi, scene)))
        else:
            dims = root.dimensions
            col.label(text=f"L × A × P: {units.format_value(dims.x, scene)} × {units.format_value(dims.z, scene)} × "
                           f"{units.format_value(dims.y, scene)}")
            col.label(text="Limites: definidos pela biblioteca do módulo", icon='INFO')
        agg = getattr(obj, 'btm_aggregate', None)
        if agg is not None and agg.is_aggregate and agg.kind == 'AGGREGATE':
            from ..aggregates import apply, limits
            box_p = apply.parent_box(obj)
            if box_p is not None:
                lim = limits.limits(box_p, tuple(agg.size), agg.face)
                col.label(text=tr("Agregado: horizontal até {}, vertical até {}, afunda até {}").format(units.format_value(lim['u'][1], scene), units.format_value(lim['v'][1], scene), units.format_value(-lim['offset'][0], scene)))
        space = context.space_data
        overlay = getattr(space, 'overlay', None)
        if overlay is not None:
            col.label(text=tr("Grade: {}").format(units.format_value(overlay.grid_scale, scene)))


@persistent
def quarantine_virtual_drivers(*_args):
    """Tira drivers e keyframes gravados por versões antigas nos campos virtuais (`btm_selection.*`), anotando no
    console o que foi removido; os dos móveis ficam (BUG-20261023-GAVK)."""
    for scene in bpy.data.scenes:
        anim = scene.animation_data
        if anim is None:
            continue
        for fc in [fc for fc in anim.drivers if fc.data_path.startswith('btm_selection.')]:
            variables = [(v.name, v.type) for v in fc.driver.variables]
            print(f"CAFFMob Draw: driver removido de {scene.name}.{fc.data_path} "
                  f"(expressão {fc.driver.expression!r}, variáveis {variables})")
            anim.drivers.remove(fc)
        curves = getattr(anim.action, 'fcurves', None) if anim.action is not None else None
        for fc in [fc for fc in (curves or ()) if fc.data_path.startswith('btm_selection.')]:
            print(f"CAFFMob Draw: animação removida de {scene.name}.{fc.data_path}")
            curves.remove(fc)


# Os painéis `_ChildPanel` são desenhados como grupos de Selecionado (feature 005, `ui/sidebar_selected.py`).
classes = (BTM_PG_SelectionEdit,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.btm_selection = bpy.props.PointerProperty(type=BTM_PG_SelectionEdit)
    if quarantine_virtual_drivers not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(quarantine_virtual_drivers)


def unregister():
    if quarantine_virtual_drivers in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(quarantine_virtual_drivers)
    if hasattr(bpy.types.Scene, 'btm_selection'):
        del bpy.types.Scene.btm_selection
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
