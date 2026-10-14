"""Aba Gavetas do Editor de Armário (feature 008, T040; RN-11, RN-12, D-08, D-21, D-23).

Subabas Gavetas / Gavetões / Internas / Blum, "Opções de gavetas" (o item do catálogo), "Opções de frentes" (estilo da
biblioteca), puxador e número de gavetas; Inserir no vão da biblioteca do vão alvo.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import bridge, catalog, props
from .panels import catalog_grid, _TabPanel, insert_button, properties_box, target_box
from .panels_tabs_common import registrar


class BTM_PT_CabinetEditorDrawers(_TabPanel, bpy.types.Panel):
    bl_label = "Gavetas"
    bl_idname = "BTM_PT_cabinet_editor_drawers"
    bl_order = 1
    bl_options = {'HIDE_HEADER'}
    TAB = 'DRAWERS'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        target_box(layout, context, 'DRAWERS')
        layout.row().prop(ui, "drawer_tab", expand=True)
        root = s.root()
        adapter = bridge.adapter_of(root) if root is not None else None
        allowed = adapter.front_types(root) if adapter is not None else []
        if 'DRAWERS' not in allowed:
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Esta biblioteca não tem gavetas"), icon='CANCEL')
        if ui.drawer_tab == 'INTERNAL' and getattr(adapter, 'LIBRARY', '') != 'FRAMELESS':
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Gaveta interna só existe no frameless"), icon='CANCEL')
        options = catalog.items('DRAWERS', ui.drawer_tab, environment=props.environment())   # feature 015
        chosen = catalog.get(ui.catalog_item)
        item = chosen if chosen in options else options[0]
        if len(options) > 1:
            catalog_grid(layout, context, options)
        box = layout.box()
        box.label(text=tr("Opções de gavetas"))
        row = box.row()
        row.label(text=tr(item.label), icon='NLA_PUSHDOWN')
        sub = box.row()
        sub.active = False
        sub.label(text=tr(item.description))
        box = layout.box()
        box.label(text=tr("Opções de frentes"))
        box.prop(ui, "drawer_style", text="")
        if ui.drawer_tab != 'INTERNAL':
            box.prop(ui, "drawer_pull")
        box = layout.box()
        box.label(text=tr("Opções de inserção"))
        box.prop(ui, "drawer_count")
        if ui.drawer_tab == 'TALL':
            hint = box.row()
            hint.active = False
            hint.label(text=tr("Gavetões: de 2 a 4 por vão"))
        insert_button(layout, context, 'DRAWERS')
        properties_box(layout, item)


classes = (BTM_PT_CabinetEditorDrawers,)
register, unregister = registrar(classes)
