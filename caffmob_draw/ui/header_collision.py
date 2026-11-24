"""Botão global de Ativar / Desativar Colisões no cabeçalho da Viewport 3D (feature 021, T023; RF-04, RN-04)."""

import bpy  # type: ignore

from ..data.i18n import tr


class BTM_OT_ToggleGlobalCollision(bpy.types.Operator):
    """Ativa ou desativa globalmente o sistema de colisões do CAFFMob Draw"""
    bl_idname = "caffmob.toggle_global_collision"
    bl_label = "Colisões"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = getattr(context.scene, 'btm_settings', None)
        if settings is None:
            return {'CANCELLED'}
        new_state = not bool(settings.collision_global)
        settings.collision_global = new_state
        if hasattr(settings, 'block_penetration'):
            settings.block_penetration = new_state
        label = tr("Colisões ativadas") if new_state else tr("Colisões desativadas")
        self.report({'INFO'}, label)
        return {'FINISHED'}


def draw_header_collision(self, context):
    settings = getattr(context.scene, 'btm_settings', None)
    if settings is None:
        return
    enabled = bool(settings.collision_global)
    row = self.layout.row(align=True)
    row.operator(
        "caffmob.toggle_global_collision",
        text=tr("Colisão: ON") if enabled else tr("Colisão: OFF"),
        icon='MOD_PHYSICS' if enabled else 'CANCEL',
        depress=enabled,
    )


classes = (BTM_OT_ToggleGlobalCollision,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_HT_header.append(draw_header_collision)


def unregister():
    try:
        bpy.types.VIEW3D_HT_header.remove(draw_header_collision)
    except ValueError:
        pass
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
