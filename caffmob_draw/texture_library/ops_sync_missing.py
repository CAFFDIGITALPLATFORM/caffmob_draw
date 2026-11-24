"""Operador e painel de Sincronização de Texturas Perdidas do addon (feature 021, T022; RF-03, RN-03)."""

import bpy  # type: ignore

from ..data.i18n import tr
from . import sync_missing


class BTM_OT_SyncMissingTextures(bpy.types.Operator):
    """Detecta texturas do addon ausentes no disco, baixa novamente e reconecta os materiais da cena"""
    bl_idname = "caffmob.sync_missing_textures"
    bl_label = "Sincronizar Texturas Perdidas"
    bl_options = {'REGISTER'}

    def execute(self, context):
        if sync_missing._active_sync['running']:
            self.report({'INFO'}, tr("Sincronização de texturas já está em andamento."))
            return {'CANCELLED'}

        def _done(summary):
            try:
                from ..ui import save_feedback
                save_feedback.show(summary['message'])
            except Exception:
                pass

        res = sync_missing.sync_missing_textures(on_complete=_done)
        if res.get('running'):
            self.report({'INFO'}, tr("Baixando {} textura(s) perdida(s)...").format(res['total']))
        else:
            self.report({'INFO'}, tr(res.get('message', "Todas as texturas do addon já estão presentes localmente.")))
        return {'FINISHED'}


class BTM_OT_CancelSyncMissingTextures(bpy.types.Operator):
    """Cancela a sincronização de texturas perdidas em andamento"""
    bl_idname = "caffmob.cancel_sync_missing_textures"
    bl_label = "Cancelar Sincronização"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        sync_missing.cancel_sync()
        self.report({'INFO'}, tr("Sincronização de texturas cancelada."))
        return {'FINISHED'}


class BTM_PT_SyncMissingTextures(bpy.types.Panel):
    """Acesso rápido no painel de Texturas/Materiais para recuperar texturas perdidas do addon"""
    bl_label = "Texturas / Materiais"
    bl_idname = "BTM_PT_SyncMissingTextures"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "CAFFMob Draw"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        if sync_missing._active_sync['running']:
            row = layout.row(align=True)
            row.label(text=tr("Sincronizando texturas..."), icon='TIME')
            row.operator("caffmob.cancel_sync_missing_textures", text="", icon='CANCEL')
        else:
            layout.operator("caffmob.sync_missing_textures", text=tr("Sincronizar Texturas Perdidas"), icon='FILE_REFRESH')


classes = (
    BTM_OT_SyncMissingTextures,
    BTM_OT_CancelSyncMissingTextures,
    BTM_PT_SyncMissingTextures,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    sync_missing.cancel_sync()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
