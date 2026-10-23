"""Conta e cancelamento das texturas (063 RN-02, RN-12; D-05, D-08).

A grade usa a mesma sessão de aparelho do MOBI. Baixar uma categoria inteira (ou todas) só por pedido, na seção
Offline, com confirmação (BUG-20261023-AFC5, `offline.py`).
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import auth, catalog, downloads

CODE_HINT = N_("Código {}: confirme no navegador que abriu")
CONNECTED = N_("Conta CAF Mob conectada: {}")
SIGNED_OUT = N_("Você saiu da conta CAF Mob")
OFFLINE_TITLE = N_("Preparar texturas offline")
OFFLINE_CONFIRM = N_("Baixar {} texturas para usar sem rede? O tamanho total não é informado pelo servidor.")
OFFLINE_PICK = N_("Escolha um fabricante (e, se quiser, uma coleção) na Biblioteca antes.")
OFFLINE_PROGRESS = N_("Offline: {} de {} prontas, {} com falha")


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
    if email:
        draw_offline(layout)


class BTM_OT_TextureOfflinePrepare(bpy.types.Operator):
    """Baixa as texturas para usar sem rede (a categoria escolhida na Biblioteca ou todas)"""
    bl_idname = "caffmob.texture_offline_prepare"
    bl_label = "Preparar texturas offline"
    bl_options = {'INTERNAL'}

    scope: bpy.props.EnumProperty(items=[('SELECTED', "Categoria escolhida", ""), ('ALL', "Todas as categorias", "")],
                                  options={'SKIP_SAVE'})  # type: ignore

    @classmethod
    def poll(cls, context):
        return auth.signed_in() and not downloads.unavailable_reason()

    def _filter(self, context):
        state = getattr(context.window_manager, 'btm_library', None)
        if self.scope == 'ALL' or state is None:
            return '', ''
        return state.manufacturer, state.collection

    def invoke(self, context, event):
        from . import offline
        man, col = self._filter(context)
        if self.scope == 'SELECTED' and not man:
            self.report({'WARNING'}, tr(OFFLINE_PICK))
            return {'CANCELLED'}
        self._count = offline.count(man, col)
        return context.window_manager.invoke_confirm(self, event, title=tr(OFFLINE_TITLE),
                                                     message=tr(OFFLINE_CONFIRM).format(self._count))

    def execute(self, context):
        from . import offline
        man, col = self._filter(context)
        offline.start(offline.slugs(man, col))
        _redraw()
        return {'FINISHED'}


class BTM_OT_TextureOfflineCancel(bpy.types.Operator):
    """Para de agendar as próximas texturas do lote offline (o que já baixou fica)"""
    bl_idname = "caffmob.texture_offline_cancel"
    bl_label = "Parar o lote offline"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        from . import offline
        offline.cancel()
        _redraw()
        return {'FINISHED'}


def draw_offline(layout):
    """Seção Offline do menu da conta: preparar a categoria ou todas, e o progresso do lote."""
    from . import offline
    layout.separator()
    layout.label(text=tr("Offline"), icon='DISK_DRIVE')
    status = offline.status()
    if status['running']:
        layout.label(text=tr(OFFLINE_PROGRESS).format(status['done'], status['total'], status['failed']), icon='TIME')
        layout.operator(BTM_OT_TextureOfflineCancel.bl_idname, icon='CANCEL')
        return
    if status['total']:
        layout.label(text=tr(OFFLINE_PROGRESS).format(status['done'], status['total'], status['failed']),
                     icon='CHECKMARK' if not status['failed'] else 'ERROR')
    layout.operator(BTM_OT_TextureOfflinePrepare.bl_idname, text=tr("Baixar a categoria escolhida")).scope = 'SELECTED'
    layout.operator(BTM_OT_TextureOfflinePrepare.bl_idname, text=tr("Baixar todas as categorias")).scope = 'ALL'


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
           BTM_OT_TextureOfflinePrepare, BTM_OT_TextureOfflineCancel, BTM_OT_TextureAccountMenu)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    from . import offline
    offline.shutdown()
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
