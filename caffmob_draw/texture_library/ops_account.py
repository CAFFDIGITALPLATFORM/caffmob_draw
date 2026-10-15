"""Conta e cancelamento das texturas (063 RN-02, RN-12; D-05, D-08).

A grade usa a mesma sessão de aparelho do MOBI. Não há download do catálogo inteiro.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import auth, catalog, downloads

CODE_HINT = N_("Código {}: confirme no navegador que abriu")
CONNECTED = N_("Conta CAF Mob conectada: {}")
SIGNED_OUT = N_("Você saiu da conta CAF Mob")


def _notify(text):
    from ..ui import save_feedback
    save_feedback.show(text)
    _redraw()


def _redraw():
    wm = bpy.context.window_manager
    for window in (wm.windows if wm else []):
        for area in window.screen.areas:
            if area.type in ('VIEW_3D', 'PREFERENCES'):
                area.tag_redraw()


class BTM_OT_TextureLogin(bpy.types.Operator):
    """Entrar com a conta CAF Mob (abre o navegador; a senha não passa pelo Blender)"""
    bl_idname = "caffmob.texture_login"
    bl_label = "Entrar com a conta CAF Mob"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        reason = downloads.unavailable_reason()
        if reason:
            self.report({'WARNING'}, tr(reason))
            return {'CANCELLED'}

        def on_code(code, link):
            try:
                bpy.ops.wm.url_open(url=link)
            except RuntimeError:
                pass
            _notify(tr(CODE_HINT).format(code))

        def on_done(ok, message):
            _notify(tr(CONNECTED).format(auth.account_email()) if ok else tr(message))
        auth.start_login(on_code, on_done)
        return {'FINISHED'}


class BTM_OT_TextureLogout(bpy.types.Operator):
    """Sair da conta CAF Mob neste computador (apaga a sessão guardada)"""
    bl_idname = "caffmob.texture_logout"
    bl_label = "Sair da conta CAF Mob"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return auth.signed_in()

    def execute(self, context):
        downloads.cancel_all()
        auth.logout(lambda message: _notify(tr(message)) if message else None)
        self.report({'INFO'}, tr(SIGNED_OUT))
        _redraw()
        return {'FINISHED'}


class BTM_OT_TextureDownloadCancel(bpy.types.Operator):
    """Cancela os downloads de textura em andamento (o que já baixou fica)"""
    bl_idname = "caffmob.texture_download_cancel"
    bl_label = "Cancelar downloads"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        downloads.cancel_all()
        _redraw()
        return {'FINISHED'}


def draw_account(layout):
    """Linhas da conta (menu do chip e preferências)."""
    reason = downloads.unavailable_reason()
    if reason:
        layout.label(text=tr(reason), icon='ERROR')
    state, code, _link = auth.login_state()
    email = auth.account_email()
    if state == 'WAITING':
        layout.label(text=tr(CODE_HINT).format(code), icon='TIME')
    if email:
        layout.label(text=tr(CONNECTED).format(email), icon='CHECKMARK')
        layout.operator(BTM_OT_TextureLogout.bl_idname, icon='X')
    else:
        row = layout.row()
        row.enabled = not reason
        row.operator(BTM_OT_TextureLogin.bl_idname, icon='USER')
    if downloads.summary() is not None:
        layout.operator(BTM_OT_TextureDownloadCancel.bl_idname, icon='CANCEL')


class BTM_OT_TextureAccountMenu(bpy.types.Operator):
    """Conta CAF Mob e downloads de textura"""
    bl_idname = "caffmob.texture_account_menu"
    bl_label = "Conta CAF Mob"
    bl_options = {'INTERNAL'}

    def invoke(self, context, event):
        if not auth.signed_in() and auth.login_state()[0] is None and not downloads.unavailable_reason():
            return bpy.ops.caffmob.texture_login()
        context.window_manager.popup_menu(lambda menu, _ctx: draw_account(menu.layout), title=tr("Conta CAF Mob"),
                                          icon='USER')
        return {'FINISHED'}


classes = (BTM_OT_TextureLogin, BTM_OT_TextureLogout, BTM_OT_TextureDownloadCancel,
           BTM_OT_TextureAccountMenu)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
