"""Seção Produção/Projeto (feature 005, T019; RF-06, RF-07, RN-06, D-09).

Plano de corte, Ambientes, Configurações, Projeto e, recolhido, Desenhos 2D (vistas de layout, detalhes e anotações,
que somem com a preferência "Ocultar Painéis 2D"). Os conteúdos legados vêm pelo proxy; cada um aparece uma vez.
"""

from ..data.i18n import N_, tr
from . import sidebar_proxy, view3d_sidebar
from .sidebar import group_scope

_DRAWINGS = (
    ('HOME_BUILDER_PT_layout_views', ('HOME_BUILDER_PT_layout_views_create', 'HOME_BUILDER_PT_layout_views_settings',
                                      'HOME_BUILDER_PT_layout_views_details')),
    ('HOME_BUILDER_PT_2d_details', ()),
    ('HOME_BUILDER_PT_annotations', ('HOME_BUILDER_PT_annotations_drawing', 'HOME_BUILDER_PT_molding_library',
                                     'HOME_BUILDER_PT_annotations_edit', 'HOME_BUILDER_PT_annotations_plan_view_tools',
                                     'HOME_BUILDER_PT_annotations_settings')),
)


def _cls(name):
    return getattr(view3d_sidebar, name)


def _hide_2d(context):
    addon = context.preferences.addons.get(__package__.rsplit('.', 1)[0])
    prefs = getattr(addon, 'preferences', None)
    return bool(getattr(prefs, 'hide_2d_drawing_panels', False))


LEGACY_CHILDREN = ('HOME_BUILDER_PT_molding_library',)    # feature 012 (T064, D-28): usa operadores do frameless


def draw_drawings(layout, context):
    from ..legacy import gate
    legacy = gate.legacy_ui(context)
    for parent_name, children in _DRAWINGS:
        children = tuple(c for c in children if legacy or c not in LEGACY_CHILDREN)
        parent = _cls(parent_name)
        if not sidebar_proxy.visible(parent, context):
            continue
        box = layout.box()
        box.label(text=sidebar_proxy.label_of(parent))
        sidebar_proxy.draw_panel(parent, box, context)
        for child_name in children:
            child = _cls(child_name)
            if not sidebar_proxy.visible(child, context):
                continue
            sub = box.box()
            sub.label(text=sidebar_proxy.label_of(child))
            sidebar_proxy.draw_panel(child, sub, context)


def draw_hardware(layout, context):
    """Ferragens do projeto (feature 008, T062; D-24): nome, quantidade e módulo; varre a cena só se aberta."""
    header, body = layout.panel('btm_hardware_list', default_closed=True)
    header.label(text=tr("Ferragens"), icon='TOOL_SETTINGS')
    if body is None:
        return
    from ..cutting import hardware, part_sources
    rows = hardware.collect(context.scene, ensure_uid=False)
    if not rows:
        hint = body.row()
        hint.active = False
        hint.label(text=tr("Nenhuma ferragem no projeto"))
        return
    names = {m.uid: m.name for m in part_sources.iter_modules(context.scene, ensure_uid=False)}
    col = body.column(align=True)
    for row in rows:
        line = col.row(align=True)
        line.label(text=row["name"])
        line.label(text="× {}".format(row["quantity"]))
        line.label(text=names.get(row["module_uid"], tr("Sem módulo")))


def draw_mobi_account(layout):
    """Conta única do aparelho, compartilhada com as preferências."""
    from ..texture_library import auth, downloads
    from ..mobi.ops_conta import CONNECTED, CODE
    reason = downloads.unavailable_reason()
    if reason:
        layout.label(text=tr(reason), icon='ERROR')
    state, code, _url = auth.login_state()
    if auth.signed_in():
        layout.label(text=tr(CONNECTED).format(auth.titular_nome()), icon='CHECKMARK')
    else:
        layout.label(text=tr("Blender desconectado do MOBI"), icon='USER')
    if state == 'WAITING':
        layout.label(text=tr(CODE).format(code), icon='TIME')
    row = layout.row(align=True)
    connect = row.row(align=True)
    connect.enabled = not reason and state != 'WAITING' and not auth.signed_in()
    connect.operator('caffmob.mobi_conectar', text=tr("Conectar"), icon='LINKED')
    disconnect = row.row(align=True)
    disconnect.enabled = auth.signed_in() or state == 'WAITING'
    disconnect.operator('caffmob.mobi_desconectar', text=tr("Desconectar"), icon='UNLINKED')


def draw_mobi(layout, context):
    from ..texture_library import auth, downloads
    state = context.window_manager.btm_caffmob
    draw_mobi_account(layout)
    content = layout.column()
    content.enabled = auth.signed_in() and not state.ocupado and not downloads.unavailable_reason()
    content.separator()
    content.label(text=tr("Ambientes"), icon='HOME')
    content.operator('caffmob.mobi_listar_ambientes', text=tr("Listar ambientes"), icon='FILE_REFRESH')
    for item in state.ambientes:
        row = content.row(align=True)
        row.label(text=item.nome)
        row.operator('caffmob.mobi_baixar_ambiente', text=tr("Baixar"), icon='IMPORT').ambiente_id = item.id
    if state.proximo_ambiente:
        content.operator('caffmob.mobi_listar_ambientes', text=tr("Carregar mais ambientes")).mais = True
    content.operator('caffmob.mobi_enviar_ambiente', text=tr("Enviar ambiente"), icon='EXPORT')
    content.operator('caffmob.mobi_editar_segmento', text=tr("Editar segmento"), icon='EDITMODE_HLT')
    content.separator()
    content.label(text=tr("Biblioteca do MOBI"), icon='ASSET_MANAGER')
    content.prop(state, 'biblioteca', expand=True)
    content.operator('caffmob.mobi_listar_modelos', text=tr("Listar modelos"), icon='FILE_REFRESH')
    for item in state.modelos:
        if item.escopo != state.biblioteca:
            continue
        row = content.row(align=True)
        row.label(text=item.nome)
        op = row.operator('caffmob.mobi_baixar_modelo', text=tr("Inserir"), icon='ADD')
        op.modelo_id = item.id
    content.operator('caffmob.mobi_enviar_modelo', text=tr("Enviar versão do modelo"), icon='EXPORT')
    op = content.operator('caffmob.mobi_enviar_modelo', text=tr("Enviar como modelo novo"), icon='ADD')
    op.novo, op.escopo = True, state.biblioteca
    if state.conflito_local:
        content.operator('caffmob.mobi_resolver_conflito', icon='ERROR')
    layout.separator()
    layout.label(text=tr("Situação"), icon='INFO')
    if state.situacao:
        layout.label(text=state.situacao)
    waiting = auth.login_state()[0] == 'WAITING'
    if state.ocupado:
        layout.progress(factor=state.progresso, type='BAR', text=tr("Progresso"))
    if state.ocupado or waiting:
        layout.operator('caffmob.mobi_cancelar', text=tr("Cancelar"), icon='CANCEL')


def draw(layout, context):
    from . import panels
    with group_scope(layout, context, 'mobi', N_("CAFF MOBI"), 'URL') as body:
        if body is not None:
            draw_mobi(body, context)
    with group_scope(layout, context, 'cut_plan', N_("Plano de corte"), 'ALIGN_JUSTIFY') as body:
        if body is not None:
            panels.draw_cut_plan(body, context)
            draw_hardware(body, context)
    project_panel = view3d_sidebar.HOME_BUILDER_PT_project
    in_room = sidebar_proxy.visible(project_panel, context)     # fora de vistas de layout e de detalhe
    with group_scope(layout, context, 'rooms', N_("Ambientes"), 'HOME') as body:
        if body is not None and in_room:
            sidebar_proxy.draw_panel(view3d_sidebar.HOME_BUILDER_PT_project_rooms, body, context)
    with group_scope(layout, context, 'settings', N_("Configurações"), 'PREFERENCES') as body:
        if body is not None:
            panels.draw_settings(body, context)
    with group_scope(layout, context, 'project_info', N_("Projeto"), 'INFO') as body:
        if body is not None and in_room:
            sidebar_proxy.draw_panel(project_panel, body, context)
            sidebar_proxy.draw_panel(view3d_sidebar.HOME_BUILDER_PT_project_info, body, context)
    if not _hide_2d(context):
        with group_scope(layout, context, 'drawings_2d', N_("Desenhos 2D"), 'VIEW_ORTHO') as body:
            if body is not None:
                draw_drawings(body, context)
