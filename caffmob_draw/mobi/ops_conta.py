# (063 RF-07, RF-08; D-05) Autorização do aparelho pelo subprocesso existente.
import bpy  # type: ignore
from ..data.i18n import N_, tr
from ..texture_library import auth, downloads, catalog
from . import tarefas

CONNECTED = N_('Conectado ao titular {}')
DISCONNECTED = N_('Blender desconectado do MOBI')
CODE = N_('Código {}: confirme a conexão no navegador')


class MOBI_OT_Conectar(bpy.types.Operator):
    """Conectar o Blender ao MOBI pelo código do aparelho"""
    bl_idname = 'caffmob.mobi_conectar'
    bl_label = 'Conectar ao MOBI'

    def execute(self, context):
        reason = downloads.unavailable_reason()
        if reason:
            self.report({'WARNING'}, tr(reason))
            return {'CANCELLED'}
        def code(value, url):
            state = bpy.context.window_manager.btm_caffmob
            state.codigo, state.endereco = value, url
            state.situacao = tr(CODE).format(value)
            if not bpy.app.background:
                bpy.ops.wm.url_open(url=url)
        def done(ok, message):
            state = bpy.context.window_manager.btm_caffmob
            state.codigo = ''
            state.situacao = tr(CONNECTED).format(auth.titular_nome()) if ok else tr(message)
            if ok:
                catalog.invalidate()
        auth.start_login(code, done)
        return {'FINISHED'}


class MOBI_OT_Desconectar(bpy.types.Operator):
    """Revogar o aparelho e encerrar a sessão local"""
    bl_idname = 'caffmob.mobi_desconectar'
    bl_label = 'Desconectar do MOBI'

    def execute(self, context):
        tarefas.cancel_all()
        downloads.cancel_all()
        catalog.invalidate()
        def done(message):
            state = bpy.context.window_manager.btm_caffmob
            state.ocupado = False
            state.situacao = tr(message or DISCONNECTED)
        auth.logout(done)
        return {'FINISHED'}


classes = (MOBI_OT_Conectar, MOBI_OT_Desconectar)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    auth.cancel_login()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
