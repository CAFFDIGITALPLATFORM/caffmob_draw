"""Estado da barra lateral (feature 005, T002; data-delta §1.1, D-02).

Fica em `WindowManager.btm_sidebar` e não é salvo no arquivo: abrir ou recolher uma seção não marca o projeto como
alterado nem entra no desfazer. Cada seção e cada grupo interno é um `layout.panel_prop` sobre um destes booleanos;
`open_selected` é ligado pelo `msgbus` quando o objeto ativo muda (D-03).
"""

import bpy  # type: ignore

# Grupos internos recolhíveis: (id, aberto por padrão).
GROUPS = (
    # Construir
    ('walls', False), ('openings', False), ('floor', False), ('obstacles', False), ('lights', False),
    ('stairs', False), ('reference', False), ('geometry', False),
    # Construir por finalidade (067 RF-013): os grupos acima ficam dentro destes, com os mesmos ids
    ('build_room', True), ('build_furniture', False), ('build_sheets', True), ('build_lighting', False),
    # Inserir
    ('my_modules', False), ('objects', False),
    # Selecionado (módulo: 4 abertos)
    ('sel_dimensions', True), ('sel_customize', True), ('sel_position', True), ('sel_open', True),
    ('sel_aggregates', False), ('sel_collision', False), ('sel_arrangement', False), ('sel_actions', False),
    ('sel_library', False), ('sel_retexture', False),
    # Selecionado da 067 (seções do ViewModel; os detalhes técnicos começam recolhidos)
    ('sel_sheet', True), ('sel_cotas', True), ('sel_module', False), ('sel_geometry', True), ('sel_material', True),
    ('sel_wall', True), ('sel_opening', True), ('sel_leaf', True), ('sel_member', True), ('sel_front', True),
    ('sel_cladding', True), ('sel_surface', True), ('sel_light', True), ('sel_camera', True), ('sel_multiple', True),
    ('sel_limits', True), ('sel_fallback', True), ('sel_legacy_cotas', False), ('sel_stair', True), ('sel_drawer', True),
    # Verificar
    ('check_fronts', True), ('check_collisions', True),
    # Produção/Projeto
    ('mobi', False), ('cut_plan', True), ('rooms', False), ('settings', False), ('project_info', False), ('drawings_2d', False),
)


def _annotations():
    ann = {
        'open_build': bpy.props.BoolProperty(name="Construir", default=True),
        'open_insert': bpy.props.BoolProperty(name="Inserir", default=False),
        'open_selected': bpy.props.BoolProperty(name="Selecionado", default=False),
        'open_check': bpy.props.BoolProperty(name="Verificar", default=False),
        'open_project': bpy.props.BoolProperty(name="Produção/Projeto", default=False),
        'my_modules_filter': bpy.props.EnumProperty(
            name="Origem",
            items=[('ALL', "Todas", "Todos os módulos do usuário"),
                   ('MODULES', "Módulos salvos", "Módulos salvos pelo Personalizar módulo"),
                   ('FRAMELESS', "Grupos frameless", "Grupos de gabinetes frameless do usuário"),
                   ('FACE_FRAME', "Grupos face frame", "Grupos de gabinetes face frame do usuário")],
            default='ALL'),
        'last_active': bpy.props.StringProperty(),
    }
    for group, default in GROUPS:
        ann[f'open_group_{group}'] = bpy.props.BoolProperty(default=default)
    return ann


BTM_PG_SidebarState = type('BTM_PG_SidebarState', (bpy.types.PropertyGroup,), {'__annotations__': _annotations()})

classes = (BTM_PG_SidebarState,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.btm_sidebar = bpy.props.PointerProperty(type=BTM_PG_SidebarState)


def unregister():
    if hasattr(bpy.types.WindowManager, 'btm_sidebar'):
        del bpy.types.WindowManager.btm_sidebar
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
