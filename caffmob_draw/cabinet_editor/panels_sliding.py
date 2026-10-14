"""Aba Deslizantes do Editor de Armário (feature 008, T043; RN-13b, D-18).

Família (Madeira / Alumínio), estilos em grade (inclusive os de puxador integrado), número de folhas, Inserir
invertido e o aviso de profundidade dos trilhos; Remover deslizantes.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import catalog, props, scene_slides
from .panels import _TabPanel, catalog_grid, insert_button, properties_box
from .panels_tabs_common import registrar


class BTM_PT_CabinetEditorSliding(_TabPanel, bpy.types.Panel):
    bl_label = "Deslizantes"
    bl_idname = "BTM_PT_cabinet_editor_sliding"
    bl_order = 1
    bl_options = {'HIDE_HEADER'}
    TAB = 'SLIDING'

    def draw(self, context):
        s = props.session()
        ui = context.window_manager.btm_cabinet_editor
        layout = self.layout
        layout.label(text=tr("Portas deslizantes"), icon='ARROW_LEFTRIGHT')
        # Feature 015 (D-17, clarify Q4): dois modos; "Sobre a caixa" (conjunto Interna/Externa/Embutida) vem depois
        mode = layout.row(align=True)
        mode.label(text=tr("Modo"))
        current = mode.row(align=True)
        current.label(text=tr("No vão"), icon='RADIOBUT_ON')
        later = mode.row(align=True)
        later.enabled = False
        later.label(text=tr("Sobre a caixa"), icon='RADIOBUT_OFF')
        note = layout.row()
        note.active = False
        note.label(text=tr("Sobre a caixa: disponível numa próxima versão"), icon='INFO')
        layout.row().prop(ui, "slide_family", expand=True)
        catalog_grid(layout, context, catalog.items('SLIDING', ui.slide_family))
        row = layout.row(align=True)
        row.prop(ui, "slide_leaves")
        row.prop(ui, "invert")
        root = s.root()
        need = scene_slides.missing_depth(context, root, ui.slide_leaves) if root is not None else None
        if need is not None:
            warn = layout.row()
            warn.alert = True
            warn.label(text=tr("Os trilhos precisam de {:.0f} mm de profundidade").format(need * 1000.0),
                       icon='ERROR')
        insert_button(layout, context, 'SLIDING')
        chosen = catalog.get(ui.catalog_item)
        properties_box(layout, chosen if chosen is not None and chosen.tab == 'SLIDING' else None)
        if root is not None and scene_slides.frame_of(root) is not None:
            op = layout.operator("caffmob.cabinet_editor_remove_item", text=tr("Remover deslizantes"), icon='X')
            op.kind = 'SLIDES'


classes = (BTM_PT_CabinetEditorSliding,)
register, unregister = registrar(classes)
