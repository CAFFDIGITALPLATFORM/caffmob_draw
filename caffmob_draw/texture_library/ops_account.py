"""Operadores da conta CAF Mob e do "Baixar tudo" (feature 014, T035; RN-11, RN-12, D-12, D-15).

- `caffmob.texture_login`: pede o código, abre o navegador na página da CAF Mob e acompanha até a confirmação;
- `caffmob.texture_logout`: avisa o servidor e apaga a sessão;
- `caffmob.texture_download_all`: só com `download_all` na conta; baixa todas as imagens que faltam pela fila, com
  progresso total no rodapé da biblioteca e cancelamento (`caffmob.texture_download_cancel`);
- `caffmob.texture_account_menu`: menu do chip da conta na biblioteca maximizada.
"""

import bpy  # type: ignore

from ..data.i18n import N_, tr
from . import auth, catalog, downloads

CODE_HINT = N_("Código {}: confirme no navegador que abriu")
CONNECTED = N_("Conta CAF Mob conectada: {}")
SIGNED_OUT = N_("Você saiu da conta CAF Mob")
NOT_ENTITLED = N_("Sua conta não tem permissão para baixar todas as texturas")
ALL_DONE = N_("Todas as texturas baixadas")
DOWNLOAD_ALL_START = N_("Baixando {} texturas ({:.0f} MB)")
CONFIRM_ALL = N_("Baixar todas as texturas que faltam (cerca de {:.0f} MB)?")


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


def missing_items():
    """Itens do catálogo cuja imagem ainda não está no cache."""
    data, _warnings = catalog.load()
    return [item for item in catalog.catalog_core.iter_items(data) if not downloads.cached(item["id"])]


def start_download_all(on_done=None):
    """Enfileira tudo o que falta, se a conta permitir. `on_done(ok, mensagem)` ao decidir (não ao terminar)."""
    def decide(ent):
        if not ent or not ent.get("download_all"):
            message = tr(NOT_ENTITLED) if ent is not None else tr(downloads.NO_ACCOUNT)
            if on_done:
                on_done(False, message)
            return
        items = missing_items()
        if not items:
            if on_done:
                on_done(True, tr(ALL_DONE))
            return
        downloads.clear_finished()
        for item in items:
            downloads.fetch(item["id"])
        size = sum(int(i.get("bytes") or 0) for i in items) / 1048576.0
        if on_done:
            on_done(True, tr(DOWNLOAD_ALL_START).format(len(items), size))
    auth.fetch_entitlements(decide)


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
        auth.logout()
        self.report({'INFO'}, tr(SIGNED_OUT))
        _redraw()
        return {'FINISHED'}


class BTM_OT_TextureDownloadAll(bpy.types.Operator):
    """Baixa todas as texturas para usar sem internet (só para contas com essa permissão)"""
    bl_idname = "caffmob.texture_download_all"
    bl_label = "Baixar todas as texturas"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return auth.signed_in()

    def invoke(self, context, event):
        size = sum(int(i.get("bytes") or 0) for i in missing_items()) / 1048576.0
        return context.window_manager.invoke_confirm(self, event, title=tr(CONFIRM_ALL).format(size),
                                                     confirm_text=tr("Baixar"), icon='IMPORT')

    def execute(self, context):
        reason = downloads.unavailable_reason()
        if reason:
            self.report({'WARNING'}, tr(reason))
            return {'CANCELLED'}
        start_download_all(lambda ok, message: _notify(message))
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
        layout.operator(BTM_OT_TextureDownloadAll.bl_idname, icon='IMPORT')
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


classes = (BTM_OT_TextureLogin, BTM_OT_TextureLogout, BTM_OT_TextureDownloadAll, BTM_OT_TextureDownloadCancel,
           BTM_OT_TextureAccountMenu)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
