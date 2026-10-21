"""Painéis de colisão (feature 004, T042; feature 066, T075/T076, RF-022, RF-024).

- "Colisões" (aba CAFFMob Draw): a chave "Impedir atravessamento" e o botão "Diagnóstico técnico". A lista com "Ir para"
  e "Afastar até encostar" só aparece no popup do diagnóstico, calculada na hora; nada fica na barra nem na viewport.
- "Colisão" (no painel de propriedades do objeto): Herdar / Ativa / Desativada para o item selecionado, sem "Colide
  com" (o bloqueio é silencioso, RF-021).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import props

MAX_ROWS = 12
_LABELS = {key: label for key, label, _desc in props.KIND_ITEMS}


def draw_collisions(layout, context):
    """Lista do diagnóstico técnico (popup de `caffmob.collision_diagnose`), calculada na hora em que abriu."""
    state = context.window_manager.btm_collision
    row = layout.row(align=True)
    row.operator("caffmob.check_collisions", text=tr("Recalcular"), icon='FILE_REFRESH').scope = state.scope
    if state.error:
        box = layout.box()
        box.alert = True
        box.label(text=tr("Não foi possível calcular a colisão: {}").format(state.error), icon='ERROR')
        return
    if not state.items:
        layout.label(text=tr("Sem colisões em {} item(ns).").format(max(0, state.checked)), icon='CHECKMARK')
        return
    col = layout.column(align=True)
    col.alert = True
    col.label(text=tr("{} colisão(ões):").format(len(state.items)), icon='ERROR')
    for index, item in enumerate(state.items[:MAX_ROWS]):
        line = col.row(align=True)                # na coluna em alerta: as linhas também ficam em destaque
        line.label(text="{}: {} × {} ({:.0f} mm)".format(tr(_LABELS.get(item.kind, item.kind)), item.name_a,
                                                        item.name_b, item.depth * 1000.0))
        line.operator("caffmob.collision_goto", text="", icon='VIEWZOOM').index = index
        line.operator("caffmob.collision_push_out", text="", icon='MOD_OFFSET').index = index
    if len(state.items) > MAX_ROWS:
        layout.label(text=tr("… e mais {}").format(len(state.items) - MAX_ROWS))


def draw_tools(layout, context):
    """Barra lateral (feature 066, RF-022/RF-024): a chave do guarda e o diagnóstico, que só abre por botão."""
    settings = getattr(context.scene, 'btm_settings', None)
    if settings is not None:
        row = layout.row(align=True)
        row.prop(settings, "block_penetration", text=tr("Impedir atravessamento"), toggle=True)
        row.prop(settings, "show_side_dimensions", text=tr("Medidas laterais"), toggle=True)
    row = layout.row(align=True)
    row.operator("caffmob.collision_diagnose", text=tr("Diagnóstico técnico"), icon='MOD_PHYSICS').scope = 'ALL'
    row.operator("caffmob.collision_diagnose", text=tr("Selecionado"), icon='RESTRICT_SELECT_OFF').scope = 'SELECTED'


class BTM_PT_Collisions(bpy.types.Panel):
    bl_label = "Colisões"
    bl_idname = "BTM_PT_collisions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        draw_tools(self.layout, context)


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
        self.layout.prop(item.btm_plane, "collision_override", text=tr("Colisão"))


# Desenhados na barra lateral única (feature 005) pelas funções de desenho e pelo proxy; não registrados.
classes = ()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
