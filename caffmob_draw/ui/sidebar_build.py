"""Seção Construir (feature 005, T012; RF-02, RN-07, D-05).

Primeiro a ação principal (Editor de Paredes); depois os grupos por finalidade (067 RF-013): Ambiente (Paredes,
Aberturas, Piso e teto, Obstáculos, Escadas, Imagem de referência), Móveis (aponta para Inserir), Chapas e peças (a
Chapa do Padrão de Dimensões e as Geometrias) e Iluminação (Luzes). O conteúdo vem dos painéis do Room Layout,
desenhados pelo proxy. Sem nenhuma parede, Aberturas e Piso e teto ficam desabilitados com o motivo (R-01 da UI).
"""

from ..data.i18n import N_, tr
from . import sidebar_proxy, view3d_sidebar
from .sidebar import empty_state, group_scope

NO_WALL = N_("Desenhe uma parede primeiro")


def has_walls(scene):
    from ..operators.floor_builder import scene_walls
    hb, layer = scene_walls(scene)
    return bool(hb or layer)


def draw_view_mode(layout, context):
    """Modo de vista (feature 010, D-06): Sólido · Textura e o interruptor Linhas, com o estado escrito."""
    from . import view_mode_core
    scene = context.scene
    if not hasattr(scene, 'btm_view_mode'):
        return
    row = layout.row(align=True)
    row.prop(scene, "btm_view_mode", expand=True)
    row.prop(scene, "btm_view_lines", text="", icon='MOD_WIREFRAME', toggle=True)
    hint = layout.row()
    hint.active = False
    hint.label(text=tr("Vista: {}").format(view_mode_core.label(scene.btm_view_mode, scene.btm_view_lines)))


def draw_wall_region(layout, context):
    """Região na parede (feature 011, T020): marcar antes de escolher a porta ou a janela, que entra com as medidas
    exatas dela; marcada, mostra as medidas (editáveis) e "Limpar região"."""
    from .. import units
    region = getattr(context.window_manager, 'btm_wall_region', None)
    if region is None:
        return
    box = layout.box()
    row = box.row(align=True)
    row.operator("caffmob.wall_region", text=N_("Marcar região"), icon='SELECT_SET')
    if not region.active:
        hint = box.row()
        hint.active = False
        hint.label(text=tr("Opcional: a porta ou janela entra no tamanho exato da região"))
        return
    row.operator("caffmob.wall_region_clear", text="", icon='X')
    unit = context.scene.unit_settings
    box.label(text=tr("Região em {}: {} × {}").format(
        region.wall, units.unit_to_string(unit, region.x1 - region.x0), units.unit_to_string(unit, region.z1 - region.z0)),
        icon='CHECKMARK')
    grid = box.grid_flow(columns=2, align=True)
    grid.prop(region, "x0", text=tr("Esquerda"))
    grid.prop(region, "x1", text=tr("Direita"))
    grid.prop(region, "z0", text=tr("Base"))
    grid.prop(region, "z1", text=tr("Topo"))


def draw(layout, context):
    walls = has_walls(context.scene)
    row = layout.row(align=True)
    row.scale_y = 1.3
    row.operator("caffmob.wall_editor", text=N_("Editor de Paredes"), icon='MESH_GRID')
    draw_view_mode(layout, context)
    from ..legacy import gate                               # feature 012 (T061): armários de bibliotecas antigas
    legacy = gate.legacy_roots(context.scene) if not gate.legacy_ui(context) else []
    if legacy:
        box = layout.box()
        box.label(text=tr("{} armário(s) de bibliotecas antigas").format(len(legacy)), icon='INFO')
        box.operator("caffmob.legacy_convert", text=tr("Converter para CAFFMob"), icon='FILE_REFRESH')
    from ..openings import sync as openings_sync           # feature 010: caixas antigas de portas e janelas
    old = openings_sync.outdated(context.scene)
    if old:
        box = layout.box()
        box.label(text=tr("{} porta(s) ou janela(s) em caixa").format(len(old)), icon='INFO')
        box.operator("caffmob.openings_update", icon='FILE_REFRESH')

    vs = view3d_sidebar
    if not sidebar_proxy.visible(vs.HOME_BUILDER_PT_room_layout, context):
        empty_state(layout, N_("Em vistas de layout e de detalhe, volte a um ambiente para construir"))
        return
    # (067 RF-013) Por finalidade. Os grupos de antes ficam dentro dela com os mesmos ids, então o estado aberto ou
    # fechado de cada um continua o mesmo (M-01: nenhum id antigo muda).
    with group_scope(layout, context, 'build_room', N_("Ambiente"), 'HOME') as room:
        if room is not None:
            _draw_room(room, context, walls)
    with group_scope(layout, context, 'build_furniture', N_("Móveis"), 'OUTLINER_OB_MESH') as furniture:
        if furniture is not None:
            hint = furniture.row()
            hint.active = False
            hint.label(text=tr("Módulos, armários e modelos entram por Inserir"), icon='INFO')
            furniture.prop(context.window_manager.btm_sidebar, "open_insert", text=tr("Abrir Inserir"), toggle=True)
    with group_scope(layout, context, 'build_sheets', N_("Chapas e peças"), 'MESH_PLANE') as sheets:
        if sheets is not None:
            row = sheets.row(align=True)
            row.scale_y = 1.2
            row.operator("caffmob.geometry_sheet", text=N_("Chapa"), icon='MESH_PLANE')
            with group_scope(sheets, context, 'geometry', N_("Geometrias"), 'MESH_CUBE') as body:
                if body is not None:
                    row = body.row(align=True)
                    row.operator("caffmob.geometry_create", text=N_("Placa"), icon='MESH_PLANE').kind = 'PLACA'
                    row.operator("caffmob.geometry_create", text=N_("Caixa"), icon='MESH_CUBE').kind = 'CAIXA'
    with group_scope(layout, context, 'build_lighting', N_("Iluminação"), 'LIGHT') as lighting:
        if lighting is not None:
            with group_scope(lighting, context, 'lights', N_("Luzes"), 'LIGHT') as body:
                if body is not None:
                    sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_lighting, body, context)


def _draw_room(layout, context, walls):
    vs = view3d_sidebar
    with group_scope(layout, context, 'walls', N_("Paredes"), 'GREASEPENCIL') as body:
        if body is not None:
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_walls, body, context)
    with group_scope(layout, context, 'openings', N_("Aberturas"), 'MOD_BOOLEAN') as body:
        if body is not None:
            if not walls:
                empty_state(body, NO_WALL)
            col = body.column()
            col.enabled = walls
            draw_wall_region(col, context)
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_doors_windows, col, context)
    with group_scope(layout, context, 'floor', N_("Piso e teto"), 'MESH_PLANE') as body:
        if body is not None:
            if not walls:
                empty_state(body, NO_WALL)
            col = body.column()
            col.enabled = walls
            row = col.row(align=True)
            row.operator("caffmob.adjust_floor", text=N_("Ajustar Piso"), icon='MESH_GRID')
            row.operator("caffmob.floor_builder", text=N_("Piso Manual"), icon='MESH_PLANE')
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_floor, col, context)
    with group_scope(layout, context, 'obstacles', N_("Obstáculos"), 'ERROR') as body:
        if body is not None:
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_obstacles, body, context)
    with group_scope(layout, context, 'stairs', N_("Escadas"), 'IPO_CONSTANT') as body:
        if body is not None:
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_stairs, body, context)
    with group_scope(layout, context, 'reference', N_("Imagem de referência"), 'IMAGE_REFERENCE') as body:
        if body is not None:
            sidebar_proxy.draw_panel(vs.HOME_BUILDER_PT_room_layout_reference_image, body, context)
