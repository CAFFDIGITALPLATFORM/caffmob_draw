"""Painel "Elemento filho" no painel de propriedades (feature 004, T035; RF-17, D-11).

No item grudado: "Elemento filho de: <hospedeiro> — <face>", posição na face, distância, giro, aviso de item fora da
face e os botões Mover no plano / Desgrudar. Num item solto: o botão Grudar. No hospedeiro: a lista "Elementos filhos".
O estado aparece sempre em texto, não só por cor (RNF de usabilidade).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import apply, link
from .ops_stick import item_of, stickable


class BTM_PT_Stick(bpy.types.Panel):
    bl_label = "Elemento filho"
    bl_idname = "BTM_PT_stick"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"

    @classmethod
    def poll(cls, context):
        return stickable(context.active_object)

    def draw(self, context):
        layout = self.layout
        item = item_of(context.active_object)
        st = item.btm_stick
        if st.is_stuck and st.host is not None:
            box = layout.box()
            box.label(text=tr("Elemento filho de: {}").format(link.face_label(item)), icon='SNAP_FACE')
            col = box.column(align=True)
            col.prop(st, "u")
            col.prop(st, "v")
            col.prop(st, "distance")
            col.prop(st, "spin")
            if st.out_of_face:
                warn = box.box()
                warn.alert = True
                warn.label(text=tr("Item fora da face: {}").format(item.name), icon='ERROR')
            row = box.row(align=True)
            row.operator("caffmob.stick_move", icon='SNAP_FACE')
            row.operator("caffmob.stick_release", icon='UNLINKED')
        else:
            layout.operator("caffmob.stick_to_face", icon='SNAP_FACE')
        children = apply.stuck_items(item)
        if children:
            box = layout.box()
            box.label(text=tr("Elementos filhos: {}").format(len(children)), icon='OUTLINER_OB_GROUP_INSTANCE')
            col = box.column(align=True)
            for child in sorted(children, key=lambda o: o.name):
                col.label(text="{} — {}".format(child.name, link.face_label(child).split(" — ", 1)[-1]))


# Desenhados na barra lateral única (feature 005) pelas funções de desenho e pelo proxy; não registrados.
classes = ()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
