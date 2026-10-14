"""Aba Internos do Editor de Armário (feature 008, T041; RN-13a, D-17, D-21).

Subabas Painel p/ Eletros (filtros Externos / Embutidos), Biblioteca (módulos salvos da 003), Apoios e Pistões;
catálogo em grade, com o que não cabe no vão apagado; lista do que já foi inserido, com remover.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import appliances, catalog, props, scene_interiors
from .panels import _TabPanel, catalog_grid, insert_button, properties_box, target_box
from .panels_tabs_common import registrar


class BTM_PT_CabinetEditorInterior(_TabPanel, bpy.types.Panel):
    bl_label = "Internos"
    bl_idname = "BTM_PT_cabinet_editor_interior"
    bl_order = 1
    bl_options = {'HIDE_HEADER'}
    TAB = 'INTERIOR'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        target_box(layout, context, 'INTERIOR')
        env = props.environment()                       # feature 015 (D-13): catálogo pelo ambiente
        grid = layout.grid_flow(columns=2, align=True)
        keys = ('WARDROBE', 'LIBRARY', 'PISTONS') if env == 'DOR' else ('PANELS', 'LIBRARY', 'SUPPORTS', 'PISTONS')
        for key in keys:
            grid.prop_enum(ui, "interior_group", key)
        if ui.interior_group == 'LIBRARY':
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Os módulos salvos ficam em Inserir › Meus módulos"), icon='INFO')
            return
        if ui.interior_group == 'PANELS':
            layout.row().prop(ui, "interior_filter", expand=True)
            items = catalog.items('INTERIOR', 'PANELS', filter_=ui.interior_filter, environment=env)
        else:
            items = catalog.items('INTERIOR', ui.interior_group, environment=env)
        box = s.spaces.get(s.space)
        catalog_grid(layout, context, items, appliances._space_mm(box) if box is not None else None)
        if not items:
            hint = layout.row()
            hint.active = False
            hint.label(text=tr("Nada desta subaba neste ambiente"), icon='INFO')
        insert_button(layout, context, 'INTERIOR')
        chosen = catalog.get(ui.catalog_item)
        properties_box(layout, chosen if chosen is not None and chosen.tab == 'INTERIOR' else None)
        root = s.root()
        inserted = scene_interiors.entries(root) if root is not None else []
        if inserted:
            box = layout.box()
            box.label(text=tr("Inseridos"))
            for entry in inserted:
                item = catalog.get(entry["catalog_id"])
                row = box.row(align=True)
                row.label(text="{} · {}".format(tr(item.label) if item else entry["catalog_id"],
                                                 s.space_labels.get(entry["space"], entry["space"])))
                op = row.operator("caffmob.cabinet_editor_remove_item", text="", icon='X')
                op.kind, op.slot = 'INTERIOR', entry["slot"]


classes = (BTM_PT_CabinetEditorInterior,)
register, unregister = registrar(classes)
