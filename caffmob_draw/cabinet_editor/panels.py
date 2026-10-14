"""Painéis do Editor de Armário (feature 004, T048; RF-02, RF-03, RF-04, RF-06, RF-07, RF-09, RF-10).

Na região lateral do Image Editor, aba "Editor de Armário". Feature 008 (T037; D-02, D-03, brief `_reversa_forward/008-editor-armario-construtor/design/construtor-abas.md`):
cabeçalho com tipo, estado do rascunho, as 7 abas do Construtor só com ícone e o nome da aba ativa; Definições
(Número de vãos e medidas) na Estrutura; blocos comuns às abas de inserção (Alvo, catálogo em grade, propriedades com
"Não há propriedades disponíveis", Inserir); rodapé com mensagens, ajustes, Desfazer/Refazer e OK / Cancelar /
Aplicar. A aba Acabamento da 006 saiu: Materiais foi para a Estrutura e o Interior da biblioteca para Divisões.
Cada aba tem o seu arquivo (`panels_structure`, `panels_divisions`, `panels_drawers`, `panels_interior`,
`panels_doors`, `panels_sliding`, `panels_backs`).
"""

import bpy  # type: ignore

from ..data import units
from ..data.i18n import N_, tr
from ..selection import classify
from . import bridge, props, window
from .ops_actions import selected_path

_SEVERITY_ICON = {'ERROR': 'ERROR', 'WARNING': 'INFO', 'INFO': 'INFO'}
_CHANGE_LABEL = {'MOVED': "moveu", 'RESIZED': "mudou de medida", 'ADDED': "entrou", 'REMOVED': "saiu"}


class _EditorPanel:
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = props.EDITOR_CATEGORY

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context)


class _TabPanel(_EditorPanel):
    """Painel que só aparece numa aba (`TAB`)."""
    TAB = 'STRUCTURE'

    @classmethod
    def poll(cls, context):
        return window.is_editor_area(context) and context.window_manager.btm_cabinet_editor.tab == cls.TAB


TAB_NAMES = {key: label for key, label, _d, _i, _n in props.TAB_ITEMS}
_TYPE_LABELS = {'BASE': N_("Balcão"), 'UPPER': N_("Aéreo"), 'TALL': N_("Alto"), 'CORNER': N_("Canto"),
                'WALL': N_("Aéreo")}


def cabinet_type(root, library):
    """Tipo do armário pela biblioteca (D-25); sem tipo conhecido, o nome da biblioteca."""
    code = root.get('CABINET_TYPE') if root is not None else None
    if library == 'CLOSETS' and getattr(root, 'hb_closet_starter', None) is not None:
        return str(root.hb_closet_starter.closet_type).title()
    if library == 'BTM' and getattr(root, 'btm_cabinet', None) is not None:
        from . import structures_core
        recipe = structures_core.get(root.btm_cabinet.structure_id)   # feature 015: o nome da estrutura
        if recipe is not None:
            return tr(recipe.label_pt)
        prop = root.btm_cabinet.bl_rna.properties['cabinet_type']
        return tr(prop.enum_items[root.btm_cabinet.cabinet_type].name)
    if code and str(code).upper() in _TYPE_LABELS:
        return tr(_TYPE_LABELS[str(code).upper()])
    return tr(classify.LIBRARY_LABELS.get(library, library or ""))


# Blocos comuns às abas de inserção (brief `design/construtor-abas.md`) --------------------------------------------
def target_box(layout, context, tab):
    """Bloco "Alvo": em qual vão a aba vai inserir; sem vão, a dica de como escolher (D-21)."""
    s = props.session()
    col = layout.column(align=True)
    if s.space and s.space in s.spaces:
        col.label(text=tr("Vão: {}").format(s.space_labels.get(s.space, s.space)), icon='RESTRICT_SELECT_OFF')
    else:
        row = col.row()
        row.active = False
        row.label(text=tr("Clique num vão na vista"), icon='RESTRICT_SELECT_ON')
    if tab in ('DRAWERS', 'DOORS'):
        row = col.row()
        row.active = bool(s.library_path)
        row.label(text=tr("Vão da biblioteca: {}").format(s.library_path) if s.library_path
                  else tr("Este vão não pertence a um vão da biblioteca"), icon='MOD_WIREFRAME')


def catalog_grid(layout, context, items, space_mm=None):
    """Grade de 2 colunas com miniatura e nome; o item escolhido fica pressionado; o que não cabe, apagado."""
    from . import previews
    ui = context.window_manager.btm_cabinet_editor
    if not items:
        row = layout.row()
        row.active = False
        row.label(text=tr("Nenhum item nesta categoria"))
        return
    grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, align=False)
    for item in items:
        cell = grid.column(align=True)
        need = item.too_small(space_mm) if space_mm is not None else None
        cell.enabled = need is None
        cell.scale_y = 2.6
        icon = previews.icon_id(item.thumb)
        kwargs = {'icon_value': icon} if icon else {'icon': 'MESH_PLANE'}
        cell.operator("caffmob.cabinet_editor_pick", text=tr(item.label), depress=ui.catalog_item == item.id,
                      **kwargs).item = item.id


def properties_box(layout, item):
    """Área de propriedades do item escolhido; sem propriedade, o estado vazio do Construtor (RN-06)."""
    box = layout.box()
    rows = []
    if item is not None:
        if item.description:
            rows.append(tr(item.description))
        if item.size_mm:
            rows.append(tr("Medidas: {:.0f} × {:.0f} mm").format(item.size_mm[0], item.size_mm[1]))
        for name, value in item.params:
            if isinstance(value, float) and value:
                rows.append("{}: {:.0f} mm".format(tr(name), value))
    if not rows:
        row = box.row()
        row.active = False
        row.alignment = 'CENTER'
        row.label(text=tr("Não há propriedades disponíveis"))
        return
    for text in rows:
        box.label(text=text)


def insert_button(layout, context, tab):
    """Inserir largo, no mesmo lugar em todas as abas; apagado com o motivo (D-21)."""
    from .ops_actions import insert_reason
    s = props.session()
    reason = insert_reason(context, tab)
    row = layout.row()
    row.scale_y = 1.5
    row.enabled = reason is None
    label = tr("Inserir em {}").format(s.space_labels.get(s.space, "")) if reason is None and s.space else tr("Inserir")
    row.operator("caffmob.cabinet_editor_insert", text=label, icon='ADD').tab = tab
    if reason:
        hint = layout.row()
        hint.active = False
        hint.label(text=reason, icon='INFO')


def draw_materials(layout, context):
    """Materiais por grupo e das frentes do vão (da 003), agora na Estrutura (D-03)."""
    col = layout.column(align=True)
    _edit(col, 'MATERIAL', tr("Material de um grupo…"), 'MATERIAL', target='GROUP')
    sub = col.row(align=True)
    sub.enabled = bool(selected_path())
    _edit(sub, 'MATERIAL', tr("Material das frentes do vão…"), 'MATERIAL', target='FRONTS')


def draw_library_interior(layout, context):
    """Divisões internas da biblioteca por quantidade (da 003), agora em Divisões (D-03)."""
    s = props.session()
    root = s.root()
    adapter = bridge.adapter_of(root) if root is not None else None
    reason = adapter.capabilities(root).get('INTERIOR') if adapter is not None else tr("Sem biblioteca")
    row = layout.row()
    row.enabled = reason is None and bool(selected_path())
    _edit(row, 'INTERIOR', tr("Interior da biblioteca…"), 'MOD_LATTICE')
    if reason:
        layout.label(text=reason, icon='CANCEL')


class BTM_PT_CabinetEditorTabs(_EditorPanel, bpy.types.Panel):
    bl_label = "Editor de Armário"
    bl_idname = "BTM_PT_cabinet_editor_tabs"
    bl_order = 0
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        col = layout.column(align=True)
        root = s.root()
        library = tr(classify.LIBRARY_LABELS.get(s.library, s.library or ""))
        col.label(text=tr("Tipo: {}").format(cabinet_type(root, s.library)) + "  ·  " + library, icon='MOD_BUILD')
        status = col.row()
        status.active = False
        if s.draft.dirty():
            status.label(text=tr("Rascunho alterado"))
        else:
            status.label(text=tr("Aplicado") if s.applied else tr("Sem alterações"))
        layout.row().prop_tabs_enum(ui, "tab", icon_only=True)
        layout.label(text=tr(TAB_NAMES.get(ui.tab, ui.tab)))
        if s.error:
            box = layout.box()
            box.alert = True
            box.label(text=tr(s.error), icon='ERROR')


class BTM_PT_CabinetEditorDimensions(_TabPanel, bpy.types.Panel):
    bl_label = "Definições"
    bl_idname = "BTM_PT_cabinet_editor_dimensions"
    bl_order = 1
    TAB = 'STRUCTURE'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        unit = units.get_scene_length_unit(context.scene)
        layout.prop(ui, "bays")
        if ui.bays > 1:                                   # feature 015 (RN-14): largura do vão selecionado
            row = layout.row(align=True)
            row.enabled = props._bay_of_selection() is not None
            row.prop(ui, "bay_width")
            if not row.enabled:
                hint = layout.row()
                hint.active = False
                hint.label(text=tr("Selecione um vão na vista para digitar a largura"))
        col = layout.column(align=True)
        for field in ('width', 'height', 'depth'):
            row = col.row(align=True)
            row.alert = bool(s.dim_messages.get(field))
            row.prop(ui, field)
            lo, hi = s.limits[field]
            hint = col.row()
            hint.active = False
            hint.label(text=tr("faixa: {} – {}").format(units.format_length(lo, unit), units.format_length(hi, unit)))


def _edit(layout, action, text, icon, **values):
    op = layout.operator("caffmob.cabinet_editor_edit", text=text, icon=icon)
    op.action = action
    for name, value in values.items():
        setattr(op, name, value)
    return op


class BTM_PT_CabinetEditorMessages(_EditorPanel, bpy.types.Panel):
    bl_label = "Mensagens"
    bl_idname = "BTM_PT_cabinet_editor_messages"
    bl_order = 90

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.messages:
            layout.label(text=tr("Sem erros nem avisos"), icon='CHECKMARK')
            return
        for m in ui.messages:
            box = layout.box()
            box.alert = m.blocks
            head = m.code
            if m.component:
                head += " — " + m.component
            if m.parameter:
                head += " — " + tr(m.parameter)
            box.label(text=head, icon=_SEVERITY_ICON.get(m.severity, 'INFO'))
            if m.value or m.range:
                box.label(text=tr("valor: {}  faixa: {}").format(m.value or "-", m.range or "-"))
            if m.action:
                box.label(text=m.action)


class BTM_PT_CabinetEditorAdjustments(_EditorPanel, bpy.types.Panel):
    bl_label = "Ajustes automáticos"
    bl_idname = "BTM_PT_cabinet_editor_adjustments"
    bl_order = 91
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.adjustments:
            layout.label(text=tr("Nenhum ajuste automático"))
            return
        col = layout.column(align=True)
        for row in ui.adjustments[:30]:
            col.label(text="{}: {}".format(row.component, tr(_CHANGE_LABEL.get(row.change, row.change))))
        if len(ui.adjustments) > 30:
            col.label(text=tr("… e mais {}").format(len(ui.adjustments) - 30))


class BTM_PT_CabinetEditorConfirm(_EditorPanel, bpy.types.Panel):
    bl_label = "Confirmar"
    bl_idname = "BTM_PT_cabinet_editor_confirm"
    bl_order = 99
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        s = props.session()
        layout = self.layout
        row = layout.row(align=True)
        row.operator("caffmob.cabinet_editor_history", text=tr("Desfazer"), icon='LOOP_BACK').redo = False
        row.operator("caffmob.cabinet_editor_history", text=tr("Refazer"), icon='LOOP_FORWARDS').redo = True
        if s.blocking():
            box = layout.box()
            box.alert = True
            box.label(text=tr("Corrija os erros para confirmar"), icon='ERROR')
        row = layout.row(align=True)
        row.scale_y = 1.3
        ok = row.row(align=True)
        ok.scale_x = 1.4
        ok.operator("caffmob.cabinet_editor_confirm", text=tr("OK"), icon='CHECKMARK')
        row.operator("caffmob.cabinet_editor_cancel", text=tr("Cancelar"), icon='X')
        row.operator("caffmob.cabinet_editor_apply", text=tr("Aplicar"), icon='FILE_REFRESH')
        row = layout.row(align=True)
        row.operator("caffmob.cabinet_editor_close", text=tr("Fechar"), icon='PANEL_CLOSE')
        row.operator("caffmob.cabinet_editor_save_module", text=tr("Salvar como módulo"), icon='FILE_TICK')


classes = (BTM_PT_CabinetEditorTabs, BTM_PT_CabinetEditorDimensions, BTM_PT_CabinetEditorMessages,
           BTM_PT_CabinetEditorAdjustments, BTM_PT_CabinetEditorConfirm)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
