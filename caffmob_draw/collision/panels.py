"""Painéis de colisão (feature 004, T042; RF-20, RF-21, RF-24, RF-25, D-14, D-18).

- "Colisões" (aba CAFFMob Draw): verificar a cena ou o selecionado e a lista com "Ir para" e "Afastar até encostar".
  Estados: colisão desligada, nunca verificado, erro, desatualizado, sem colisões, lista. Nunca diz "sem colisões"
  com resultado desatualizado ou com erro (RN-14).
- "Colisão" (no painel de propriedades do objeto): Herdar / Ativa / Desativada para o item selecionado.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props, scan

MAX_ROWS = 12
_LABELS = {key: label for key, label, _desc in props.KIND_ITEMS}


def draw_collisions(layout, context):
    scene = context.scene
    state = context.window_manager.btm_collision
    row = layout.row(align=True)
    row.operator("caffmob.check_collisions", text=tr("Verificar colisões"), icon='MOD_PHYSICS').scope = 'ALL'
    row.operator("caffmob.check_collisions", text=tr("Selecionado"), icon='RESTRICT_SELECT_OFF').scope = 'SELECTED'
    if state.items or state.checked >= 0:
        row.operator("caffmob.collision_clear", text="", icon='X')
    if not scan.enabled(scene):
        layout.label(text=tr("Colisão desligada (Evitar Sobreposição)"), icon='INFO')
        layout.label(text=tr("Ligue em Produção/Projeto › Configurações"))
        return
    if state.error:
        box = layout.box()
        box.alert = True
        box.label(text=tr("Não foi possível calcular a colisão: {}").format(state.error), icon='ERROR')
        return
    if state.checked < 0 and not state.items:
        layout.label(text=tr("Ainda não verificado."), icon='INFO')
        return
    if state.stale:
        warn = layout.box()
        warn.alert = True
        warn.label(text=tr("Desatualizado, verifique de novo"), icon='ERROR')
    if not state.items:
        if not state.stale:
            layout.label(text=tr("Sem colisões em {} item(ns).").format(state.checked), icon='CHECKMARK')
        return
    col = layout.column(align=True)
    col.alert = not state.stale
    col.label(text=tr("{} colisão(ões):").format(len(state.items)), icon='ERROR')
    for index, item in enumerate(state.items[:MAX_ROWS]):
        line = col.row(align=True)                # na coluna em alerta: as linhas também ficam em destaque
        line.label(text="{}: {} × {} ({:.0f} mm)".format(tr(_LABELS.get(item.kind, item.kind)), item.name_a,
                                                        item.name_b, item.depth * 1000.0))
        line.operator("caffmob.collision_goto", text="", icon='VIEWZOOM').index = index
        line.operator("caffmob.collision_push_out", text="", icon='MOD_OFFSET').index = index
    if len(state.items) > MAX_ROWS:
        layout.label(text=tr("… e mais {}").format(len(state.items) - MAX_ROWS))


class BTM_PT_Collisions(bpy.types.Panel):
    bl_label = "Colisões"
    bl_idname = "BTM_PT_collisions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        draw_collisions(self.layout, context)


def _item(context):
    obj = context.active_object
    if obj is None:
        return None
    from ..stick.ops_stick import item_of
    return item_of(obj)


class BTM_PT_ItemCollision(bpy.types.Panel):
    bl_label = "Colisão"
    bl_idname = "BTM_PT_item_collision"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_parent_id = "BTM_PT_object_properties"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        item = _item(context)
        return item is not None and getattr(item, 'btm_plane', None) is not None

    def draw(self, context):
        item = _item(context)
        active = context.active_object
        agg = getattr(active, 'btm_aggregate', None)
        if agg is not None and agg.is_aggregate:      # agregado: o override é dele, não do módulo (pergunta 35)
            item = active
        layout = self.layout
        layout.prop(item.btm_plane, "collision_override", text=tr("Colisão"))
        state = context.window_manager.btm_collision
        mine = [r for r in state.items if item.name in (r.name_a, r.name_b)]
        for r in mine[:5]:
            other = r.name_b if r.name_a == item.name else r.name_a
            row = layout.row()
            row.alert = True
            row.label(text=tr("Colide com {}").format(other), icon='ERROR')


# Desenhados na barra lateral única (feature 005) pelas funções de desenho e pelo proxy; não registrados.
classes = ()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
