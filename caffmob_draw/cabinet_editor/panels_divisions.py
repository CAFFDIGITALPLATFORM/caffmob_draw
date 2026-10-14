"""Aba Divisões do Editor de Armário (feature 006, T028; feature 008, T039; RN-09 a RN-10a, D-10, D-21, D-22).

Feature 008: modos Vertical / Horizontal / Inserção múltipla; tipos Móveis / Fixas / Distanciador / Sem Divisória;
catálogo em grade (com/sem recuo frontal, distanciadores); bloco Alvo e Inserir desabilitado sem vão; propriedades do
item; lista de divisões; Interior da biblioteca (quantidade, da 003).

Texto da 006:

Nova divisão: chapa do Configurador (material e espessura), vão escolhido (lista ou clique na vista), orientação,
recuos da frente e de trás com as medidas e Adicionar. Divisões: uma linha por chapa, com Editar e Remover.
Brief: `_reversa_forward/006-editor-armario-abas/design/editor-abas.md`.
"""

import bpy  # type: ignore

from ..data import units
from ..data.i18n import tr
from . import props, scene_divisions
from . import catalog
from .panels import _TabPanel, catalog_grid, draw_library_interior, insert_button, properties_box, target_box
from .panels_structure import face_frame_note


class BTM_PT_CabinetEditorDivisionNew(_TabPanel, bpy.types.Panel):
    bl_label = "Inserir divisão"
    bl_idname = "BTM_PT_cabinet_editor_division_new"
    bl_order = 1
    TAB = 'DIVISIONS'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        root = s.root()
        target_box(layout, context, 'DIVISIONS')
        if root is not None:
            material, thickness = scene_divisions.configured(context.scene, root)
            info = layout.row()
            info.active = False
            info.label(text=tr("Chapa: {} {} (Configurador › {})").format(
                material, units.format_length(thickness, units.get_scene_length_unit(context.scene)),
                scene_divisions.line_of(root)), icon='MOD_SOLIDIFY')
        face_frame_note(layout)
        layout.row().prop(ui, "div_mode", expand=True)
        grid = layout.grid_flow(columns=2, align=True)
        grid.prop_enum(ui, "div_kind", 'MOVABLE')
        grid.prop_enum(ui, "div_kind", 'FIXED')
        grid.prop_enum(ui, "div_kind", 'SPACER')
        grid.prop_enum(ui, "div_kind", 'NONE')
        if ui.div_mode == 'MULTIPLE':
            row = layout.row(align=True)
            row.prop(ui, "new_orientation", expand=True)
            layout.prop(ui, "div_count")
        if ui.div_kind == 'NONE':
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Remove a divisória do vão escolhido e junta os vãos"), icon='INFO')
        elif ui.div_kind == 'SPACER':
            catalog_grid(layout, context, catalog.items('DIVISIONS', 'SPACER', environment=props.environment()))
        else:
            catalog_grid(layout, context, catalog.items('DIVISIONS', 'RECESS', environment=props.environment()))
            col = layout.column()
            for use, value in (("new_use_front", "new_front"), ("new_use_back", "new_back")):
                row = col.row(align=True)
                row.prop(ui, use)
                sub = row.row(align=True)
                sub.active = getattr(ui, use)
                sub.prop(ui, value, text="")
        insert_button(layout, context, 'DIVISIONS')
        properties_box(layout, catalog.get(ui.catalog_item) if catalog.get(ui.catalog_item) is not None
                       and catalog.get(ui.catalog_item).tab == 'DIVISIONS' else None)


class BTM_PT_CabinetEditorDivisionList(_TabPanel, bpy.types.Panel):
    bl_label = "Divisões"
    bl_idname = "BTM_PT_cabinet_editor_division_list"
    bl_order = 2
    TAB = 'DIVISIONS'

    def draw(self, context):
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        if not ui.divisions:
            row = layout.row()
            row.active = False
            row.label(text=tr("Nenhuma divisão. Escolha um vão e clique em Adicionar."))
            return
        col = layout.column(align=True)
        for item in ui.divisions:
            box = col.box()
            box.alert = item.flagged
            head = box.row(align=True)
            head.label(text=item.label, icon='ERROR' if item.flagged else 'MOD_LATTICE')
            head.operator("caffmob.cabinet_editor_division_edit", text="", icon='GREASEPENCIL').uid = item.uid
            head.operator("caffmob.cabinet_editor_division_remove", text="", icon='X').uid = item.uid
            detail = box.row()
            detail.active = False
            detail.label(text=item.detail)


class BTM_PT_CabinetEditorLibraryInterior(_TabPanel, bpy.types.Panel):
    bl_label = "Interior da biblioteca"
    bl_idname = "BTM_PT_cabinet_editor_library_interior"
    bl_order = 3
    bl_options = {'DEFAULT_CLOSED'}
    TAB = 'DIVISIONS'

    def draw(self, context):
        draw_library_interior(self.layout, context)


classes = (BTM_PT_CabinetEditorDivisionNew, BTM_PT_CabinetEditorDivisionList, BTM_PT_CabinetEditorLibraryInterior)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
