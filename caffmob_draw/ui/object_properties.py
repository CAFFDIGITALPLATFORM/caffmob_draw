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

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from ..data.i18n import N_, tr
from ..measure import scene_cotas
from ..selection import classify, editing

ERROR_KEY = 'btm_selection_error'


# (067 D-04) Os campos leem e escrevem no objeto do snapshot do alvo (`target/snapshot.py`), nunca no ativo: o
# snapshot é refeito fora do draw, e o setter confere se o alvo que o painel mostrou ainda é o mesmo e está parado.
_drawn = {'uid': 0}


def remember_drawn(target):
    """O draw anota o alvo que mostrou (dicionário Python, não dado do Blender) para o setter conferir."""
    _drawn['uid'] = target.uid if target is not None else 0


def _target():
    from ..target import snapshot
    return snapshot.current(bpy.context)


def _target_object(target):
    from ..target import snapshot
    return snapshot.object_for(bpy.context, target.uid) if target is not None else None


def _info():
    obj = _target_object(_target())
    return classify.classify(obj) if obj is not None else None


def _edit_target():
    """Alvo para um setter: recusa se a seleção mudou desde que o painel foi desenhado ou se o alvo se moveu."""
    from ..target import snapshot
    target = _target()
    if target is None or (_drawn['uid'] and target.uid != _drawn['uid']):
        raise ValueError(tr("A seleção mudou: confira o painel e digite de novo."))
    if not snapshot.pose_matches(bpy.context, target):
        raise ValueError(tr("O objeto mudou de posição: confira o painel e digite de novo."))
    return target


def _edit_info():
    return classify.classify(_target_object(_edit_target()))


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
        _set_error(tr(str(exc)))            # recusas puras (chapa, banco) chegam com o msgid; as outras já traduzidas


def _guarded_info():
    """`_edit_info()` com a recusa no canal de erro do painel; None quando recusou."""
    try:
        return _edit_info()
    except ValueError as exc:
        _set_error(str(exc))
        return None


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
        info = _guarded_info()
        if info is not None:
            _guard(lambda: editing.set_dimension(bpy.context, info, field, value))
    return set_


# Cotas -----------------------------------------------------------------------------------------------------

def _cota_getter(field):
    def get(_self):
        obj = _target_object(_target())          # timer, salvamento: sem alvo (BUG-20261023-7YO4)
        try:
            mc = scene_cotas.for_object(obj, bpy.context.scene) if obj else None
            value = getattr(mc.compute(), field) if mc is not None else None
        except ValueError:                # parede sem o modificador ou o input Length: o desenho segue (EC-08)
            return 0.0
        return 0.0 if value is None else float(value)
    return get


def _cota_setter(field):
    def set_(_self, value):
        info = _guarded_info()
        obj = info.obj if info is not None else None
        mc = scene_cotas.for_object(obj, bpy.context.scene) if obj else None
        if mc is not None:
            _guard(lambda: mc.apply(field, value))
    return set_


# Cotas fixas (BUG-20261023-HYCE): leem o último cálculo das medidas; editar move o conjunto pela diferença.

def _fixed_getter(name):
    def get(_self):
        from ..overlays import side_cotas
        try:
            record = side_cotas.records(bpy.context, compute=False).get(name)
        except (AttributeError, ReferenceError):
            record = None
        return float(record[0]) if record is not None else 0.0
    return get


def _fixed_setter(name):
    def set_(_self, value):
        from ..overlays import side_cotas
        _guard(lambda: side_cotas.apply_fixed(bpy.context, name, value))
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
        info = _guarded_info()
        if info is not None and info.kind == classify.WALL:
            _guard(lambda: editing.set_wall(info, field, value))
    return set_


def _get_sill(_self):
    info = _info()
    return float(editing.get_sill(info)) if info and info.kind in (classify.WINDOW, classify.ROOM_DOOR) else 0.0


def _set_sill(_self, value):
    info = _guarded_info()
    if info is not None:
        _guard(lambda: editing.set_sill(info, value))


# Chapa (067 D-11, D-12): medidas semânticas do snapshot; editar passa por `target/part_edit`.

_PART_INDEX = {'part_a': 0, 'part_b': 1}


def _part_getter(field):
    def get(_self):
        target = _target()
        measures = target.measures if target is not None else None
        if measures is None:
            return 0.0
        item = measures.face[_PART_INDEX[field]] if field in _PART_INDEX else measures.thickness
        return float(item.value)
    return get


def _part_setter(field):
    def set_(_self, value):
        def apply():
            from ..target import part_edit
            target = _edit_target()
            part_edit.resize(target, _target_object(target), field, value)
        _guard(apply)
    return set_


def _multi_thickness_get(_self):
    target = _target()
    values = [v for v in (target.multi_thickness if target is not None else ()) if v is not None]
    return float(values[0]) if values else 0.0


def _multi_thickness_set(_self, value):
    def apply():
        from ..target import part_edit, snapshot
        target = _edit_target()
        for uid in target.selected_uids:              # um só passo de Desfazer: o da edição do campo (RF-026)
            obj = snapshot.object_for(bpy.context, uid)
            sheet = snapshot.sheet_target(bpy.context, obj) if obj is not None else None
            if sheet is not None and sheet.measures is not None:
                part_edit.resize(sheet, obj, 'part_thickness', value)
    _guard(apply)


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
    cota_esquerda: _length(N_("Esquerda"), _fixed_getter('LEFT'), _fixed_setter('LEFT'),
                           N_("Do lado esquerdo até a referência mais próxima, no eixo da parede ou do móvel"))  # type: ignore
    cota_direita: _length(N_("Direita"), _fixed_getter('RIGHT'), _fixed_setter('RIGHT'),
                          N_("Do lado direito até a referência mais próxima, no eixo da parede ou do móvel"))  # type: ignore
    cota_superior: _length(N_("Superior"), _fixed_getter('TOP'), _fixed_setter('TOP'),
                           N_("Do topo até a referência mais próxima acima, ou o teto"))  # type: ignore
    cota_inferior: _length(N_("Inferior"), _fixed_getter('BOTTOM'), _fixed_setter('BOTTOM'),
                           N_("Da base até a referência mais próxima abaixo, ou o piso"))  # type: ignore
    sill: _length(N_("Peitoril"), _get_sill, _set_sill)  # type: ignore
    wall_length: _length(N_("Comprimento"), _wall_getter('length'), _wall_setter('length'))  # type: ignore
    wall_height: _length(N_("Pé-direito inicial"), _wall_getter('height'), _wall_setter('height'))  # type: ignore
    wall_end_height: _length(N_("Pé-direito final"), _wall_getter('end_height'), _wall_setter('end_height'))  # type: ignore
    wall_thickness: _length(N_("Espessura"), _wall_getter('thickness'), _wall_setter('thickness'))  # type: ignore
    # 067: medidas da própria chapa (rótulos pela orientação, no painel) e a espessura comum da seleção múltipla.
    part_a: _length(N_("Medida A"), _part_getter('part_a'), _part_setter('part_a'))  # type: ignore
    part_b: _length(N_("Medida B"), _part_getter('part_b'), _part_setter('part_b'))  # type: ignore
    part_thickness: _length(N_("Espessura"), _part_getter('part_thickness'), _part_setter('part_thickness'))  # type: ignore
    multi_thickness: _length(N_("Espessura"), _multi_thickness_get, _multi_thickness_set)  # type: ignore


# Painel (067 T087): desenha o ViewModel do alvo (`target/view.py`) ----------------------------------------------

_SECTION_ICONS = {
    'sheet': 'MESH_PLANE', 'dimensions': 'FIXED_SIZE', 'cotas': 'DRIVER_DISTANCE', 'position': 'ORIENTATION_GLOBAL',
    'module': 'MODIFIER', 'geometry': 'MESH_CUBE', 'material': 'MATERIAL', 'wall': 'MOD_BUILD', 'opening': 'MOD_BOOLEAN',
    'leaf': 'MOD_SIMPLEDEFORM', 'member': 'CON_SIZELIMIT', 'front': 'HIDE_OFF', 'cladding': 'MOD_ARRAY',
    'surface': 'MESH_GRID', 'light': 'LIGHT', 'camera': 'CAMERA_DATA', 'multiple': 'OBJECT_DATA', 'limits': 'INFO',
    'fallback': 'QUESTION', 'aggregates': 'LINKED', 'legacy_cotas': 'DRIVER_DISTANCE',
}


def panel_mode(context):
    """Essencial ou Completa, das preferências do usuário (fora da cena e do Desfazer, D-05)."""
    addon = context.preferences.addons.get(__package__.rsplit('.', 1)[0])
    prefs = getattr(addon, 'preferences', None)
    return getattr(prefs, 'panel_mode', 'ESSENTIAL')


def _data(context, obj, key):
    wm = context.window_manager
    if key == 'selection':
        return context.scene.btm_selection
    if key in ('move_over', 'target', 'cladding', 'finish_draft'):
        return getattr(wm, {'move_over': 'btm_move_over', 'target': 'btm_target', 'cladding': 'btm_cladding_draft',
                            'finish_draft': 'btm_finish_draft'}[key], None)
    if obj is None:
        return None
    if key == 'object':
        return obj
    if key in ('light', 'camera'):
        return obj.data
    return getattr(obj, {'part': 'btm_part', 'geometry': 'btm_geometry', 'aggregate': 'btm_aggregate',
                         'member': 'btm_member', 'cladding': 'btm_cladding', 'door': 'btm_opening_real',
                         'wall': 'btm_wall', 'btm_opening': 'btm_opening', 'insertion': 'btm_plane',
                         'edgeband': 'btm_edgeband'}.get(key, key),
                   None)


def _edgeband_arg(obj, arg):
    """Valores da fita visual para as notas do painel (onda 4, RF-084)."""
    from ..edgeband import core
    data = getattr(obj, 'btm_edgeband', None)
    if data is None:
        return "—"
    if arg == 'edgeband.edges':
        return str(len(core.loads(data.edge_keys)))
    if arg == 'edgeband.owner':
        return data.owner.name if data.owner is not None else tr("sem componente")
    return tr({'GENERATED': "gerada", 'EXISTING': "existente"}.get(data.state, data.state or "gerada"))


def _note_args(context, target, obj, args):
    from ..target import resolver, snapshot
    values = []
    for arg in args:
        if arg == 'target.move_name':
            moving = snapshot.object_for(context, target.move_uid)
            values.append(moving.name if moving is not None else "—")
        elif arg == 'target.kind_label':
            values.append(tr(resolver.KIND_LABELS.get(target.kind, "")))
        elif arg == 'cladding.diagnostic':
            values.append(getattr(getattr(obj, 'btm_cladding', None), 'diagnostic', "") or tr("sem avisos"))
        elif arg.startswith('edgeband.'):
            values.append(_edgeband_arg(obj, arg))
        else:
            values.append(tr(arg))
    return values


def _draw_field(layout, context, target, obj, field):
    data = _data(context, obj, field.data)
    if data is None or field.prop not in data.bl_rna.properties:
        return
    row = layout.row(align=True)
    row.enabled = not field.read_only
    kwargs = {}
    if field.label:
        kwargs['text'] = tr(field.label)
    if field.index >= 0:
        kwargs['index'] = field.index
    row.prop(data, field.prop, **kwargs)
    if field.mixed and len({round(v, 6) for v in target.multi_thickness if v is not None}) > 1:
        row.label(text=tr("Múltiplos"), icon='DOCUMENTS')


def _draw_action(layout, action):
    row = layout.row()
    row.enabled = action.enabled
    op = row.operator(action.operator, text=tr(action.label)) if action.label else row.operator(action.operator)
    for name, value in action.args:
        setattr(op, name, value)


def _draw_note(layout, context, target, obj, note):
    text = tr(note.text)
    if note.args:
        text = text.format(*_note_args(context, target, obj, note.args))
    layout.label(text=text, icon=note.icon)


def _draw_items(layout, context, target, obj, items):
    from ..target import view
    col = layout.column(align=True)
    for item in items:
        if isinstance(item, view.Field):
            _draw_field(col, context, target, obj, item)
        elif isinstance(item, view.Action):
            _draw_action(col, item)
        else:
            _draw_note(col, context, target, obj, item)


def _draw_cotas(layout, context, target, section):
    """Cotas fixas do alvo móvel com o nome da referência; lado sem referência diz isso, nunca 0 (RF-028)."""
    from ..overlays import side_cotas
    from ..target import view
    notes = [i for i in section.items if isinstance(i, view.Note)]
    if notes:
        _draw_items(layout, context, target, None, notes)
        return
    edit = context.scene.btm_selection
    layout.prop(context.window_manager.btm_target, 'cota_scope', expand=True)
    moving = _target_object(target)
    from ..target import snapshot
    moving = snapshot.object_for(context, target.move_uid) or moving
    layout.label(text=tr("Mover: {}").format(moving.name if moving is not None else "—"), icon='ORIENTATION_VIEW')
    try:
        found = side_cotas.records(context, compute=False)
    except (AttributeError, ReferenceError):
        found = {}
    col = layout.column(align=True)
    for name, field in (('TOP', 'cota_superior'), ('LEFT', 'cota_esquerda'), ('RIGHT', 'cota_direita'),
                        ('BOTTOM', 'cota_inferior')):
        row = col.row(align=True)
        if name in found:
            row.prop(edit, field)
            row.label(text=tr("até {}").format(found[name][1]))
        else:
            row.label(text=tr("{}: sem referência").format(tr(side_cotas.tr_label(name, ""))))


def _draw_module(layout, context, target, section):
    """Ações do módulo dono (escopo Conjunto numa peça): editor, Personalizar e abrir frentes, como na 1.8.0."""
    from . import sidebar_proxy
    from ..customize import panels as customize_panels
    enabled = {a.operator for a in section.items if getattr(a, 'enabled', False)}
    if 'caffmob.cabinet_editor' in enabled:
        layout.operator("caffmob.cabinet_editor", text=tr("Abrir editor de armário"), icon='MOD_BUILD')
    if sidebar_proxy.visible(customize_panels.BTM_PT_CustomizeModule, context):
        sidebar_proxy.draw_panel(customize_panels.BTM_PT_CustomizeModule, layout, context)
    elif 'caffmob.module_save' in enabled:
        layout.operator("caffmob.module_save")
    if 'caffmob.fronts_set_open' in enabled and target.kind == 'MODULE':
        row = layout.row(align=True)
        for label, mode in (("Abrir 90°", 'OPEN_90'), ("45°", 'OPEN_45'), ("Fechar", 'CLOSE')):
            op = row.operator("caffmob.fronts_set_open", text=tr(label))
            op.scope, op.mode = 'ACTIVE_MODULE', mode


def _draw_position(layout, context, target, obj, section):
    from ..target import view
    from ..stick import panels as stick_panels
    from ..collision import panels as collision_panels
    from . import sidebar_proxy
    operators = {a.operator for a in section.items if isinstance(a, view.Action) and a.enabled}
    collision_panel = ('caffmob.check_collisions' in operators
                       and sidebar_proxy.visible(collision_panels.BTM_PT_ItemCollision, context))
    # O painel de colisão já mostra a colisão do objeto; sem ele, o campo aparece aqui.
    fields = [i for i in section.items if not isinstance(i, view.Action)
              and not (collision_panel and getattr(i, 'data', '') == 'insertion')]
    _draw_items(layout, context, target, obj, fields)
    if 'caffmob.stick_to_face' in operators:
        sidebar_proxy.draw_panel(stick_panels.BTM_PT_Stick, layout, context)
    if 'caffmob.set_insertion_plane' in operators:
        plane = context.window_manager.btm_insertion_plane
        row = layout.row(align=True)
        row.operator_context = 'INVOKE_DEFAULT'
        row.operator("caffmob.set_insertion_plane", text=tr("Plano de inserção"), icon='SNAP_FACE')
        if plane.active:
            row.operator("caffmob.clear_insertion_plane", text="", icon='X')
            layout.label(text=tr("Plano ativo: face de {}").format(plane.source_name), icon='INFO')
    for operator in ('caffmob.move_over_toggle', 'caffmob.resize_width'):
        if operator in operators:
            layout.operator(operator)
    if collision_panel:
        sidebar_proxy.draw_panel(collision_panels.BTM_PT_ItemCollision, layout, context)
    elif 'caffmob.check_collisions' in operators:
        layout.operator('caffmob.check_collisions')


def _draw_wall_actions(layout, obj):
    row = layout.row(align=True)
    lowered = bool(obj.get('btm_wall_lowered'))
    row.operator("caffmob.wall_lower", text=tr("Restaurar Altura") if lowered else tr("Rebaixar"), icon='TRIA_DOWN_BAR')
    row.operator_menu_enum("caffmob.wall_visibility", "mode", text=tr("Visibilidade"), icon='HIDE_OFF')
    row = layout.row()
    row.alert = True
    row.operator("caffmob.wall_remove", text=tr("Remover Parede…"), icon='TRASH')


def _draw_section(layout, context, target, obj, section):
    from ..target import view
    from .sidebar import group_scope
    with group_scope(layout, context, f"sel_{section.id}", section.label, _SECTION_ICONS.get(section.id, 'DOT')) \
            as body:
        if body is None:
            return
        if section.scope:
            body.label(text=tr("Escopo: {}").format(tr(section.scope)), icon='GROUP')
        if section.id == 'cotas':
            _draw_cotas(body, context, target, section)
        elif section.id == 'module':
            _draw_module(body, context, target, section)
        elif section.id == 'position':
            _draw_position(body, context, target, obj, section)
        elif section.id == 'aggregates':
            from ..aggregates import panels as aggregate_panels
            aggregate_panels.draw_aggregate(body, context, include_import=False)
        elif section.id == 'wall':
            _draw_items(body, context, target, obj, [i for i in section.items if not isinstance(i, view.Action)])
            if obj is not None and any(isinstance(i, view.Action) and i.enabled for i in section.items):
                _draw_wall_actions(body, obj)
        elif section.id == 'opening' and target.detail == 'DOOR' and target.has_leaf:
            _draw_items(body, context, target, obj, [i for i in section.items if not isinstance(i, view.Action)])
            from .menus import draw_door_controls
            draw_door_controls(body, context)
        else:
            _draw_items(body, context, target, obj, section.items)


def _draw_header(layout, context, header):
    col = layout.column(align=True)
    kind = tr(header.kind_label)
    if len(header.path) >= 2:
        col.label(text=tr("{} · {} · em {}").format(kind, header.name, header.path[0]), icon='OBJECT_DATA')
    else:
        col.label(text=tr("{} · {}").format(kind, header.name), icon='OBJECT_DATA')
    scope = tr(header.scope_label).format(*header.scope_args) if header.scope_args else tr(header.scope_label)
    col.label(text=tr("Escopo: {}").format(scope))
    if header.select_owner is not None:
        col.operator(header.select_owner.operator, text=tr("Selecionar conjunto"), icon='RESTRICT_SELECT_OFF')
    error = context.window_manager.get(ERROR_KEY)
    if error:
        row = layout.row()
        row.alert = True
        row.label(text=error, icon='ERROR')


def _draw_other(layout, obj):
    info = classify.classify(obj)
    col = layout.column(align=True)
    library = classify.LIBRARY_LABELS.get(info.library, "")
    if library:
        col.label(text=tr("Linha: {}").format(library))
    col.label(text=tr("Coleção: {}").format(', '.join(c.name for c in obj.users_collection) or '—'))
    menu_id = info.root.get('MENU_ID') or obj.get('MENU_ID')
    if menu_id and (getattr(bpy.types, menu_id, None) is not None
                    or bpy.types.Menu.bl_rna_get_subclass_py(menu_id) is not None):
        layout.menu_contents(menu_id)


def draw_selected(layout, context):
    """Seção Selecionado da barra lateral: o ViewModel do alvo do snapshot (067 T087; RF-003, RF-004).

    O draw só lê o snapshot (`target/snapshot.current`); sem snapshot válido, diz "Calculando…" e não calcula nada.
    """
    from ..target import snapshot, view
    from .sidebar import group_scope
    target = snapshot.current(context)
    remember_drawn(target)
    view_layer = context.view_layer
    has_selection = view_layer is not None and view_layer.objects.active is not None
    mode = panel_mode(context)
    model = view.build(target, mode, calculating=target is None and has_selection)
    if model.header is None:
        layout.label(text=tr(model.empty), icon='INFO')
        return
    obj = _target_object(target)
    _draw_header(layout, context, model.header)
    for section in model.sections:
        _draw_section(layout, context, target, obj, section)
    if mode == view.COMPLETE and obj is not None:
        with group_scope(layout, context, 'sel_actions', N_("Outras e ações"), 'TOOL_SETTINGS') as body:
            if body is not None:
                _draw_other(body, obj)


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
