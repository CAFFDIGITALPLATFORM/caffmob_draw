"""Busca digitada na BIBLIOTECA CAFFMOB maximizada (feature 014, T031; RF-04, D-17).

Clicar no campo de busca liga a digitação: as teclas com texto (`event.unicode`) entram no campo, Backspace apaga,
Ctrl+Backspace limpa, Enter confirma e Esc desfaz a digitação desta vez. A grade filtra ao vivo (`catalog.search`, sem
caixa e sem acento, por fabricante, coleção e nome; na aba Blocos, pelo nome). Um clique fora do campo confirma e
segue para onde foi dado (célula, aba, cena).
"""

import bpy  # type: ignore

from . import draw

MAX_LEN = 60


class BTM_OT_LibrarySearch(bpy.types.Operator):
    """Digitar a busca da biblioteca"""
    bl_idname = "caffmob.library_search"
    bl_label = "Buscar na biblioteca"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        state = getattr(context.window_manager, 'btm_library', None)
        return state is not None and state.mode == 'MAX' and context.area is not None \
            and context.area.type == 'VIEW_3D'

    def invoke(self, context, event):
        self.before = context.window_manager.btm_library.search
        draw._search['active'] = True
        context.window_manager.modal_handler_add(self)
        draw.tag_redraw(context)
        return {'RUNNING_MODAL'}

    def _set(self, context, text):
        state = context.window_manager.btm_library
        state.search, state.scroll = text[:MAX_LEN], 0.0
        draw.tag_redraw(context)

    def _end(self, context, result):
        draw._search['active'] = False
        draw.tag_redraw(context)
        return result

    def modal(self, context, event):
        state = context.window_manager.btm_library
        if state.mode != 'MAX':
            return self._end(context, {'CANCELLED'})
        if event.value != 'PRESS':
            return {'PASS_THROUGH'} if event.type in ('MOUSEMOVE', 'INBETWEEN_MOUSEMOVE') else {'RUNNING_MODAL'}
        if event.type in ('LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE'):
            return self._end(context, {'FINISHED', 'PASS_THROUGH'})
        if event.type in ('WHEELUPMOUSE', 'WHEELDOWNMOUSE'):
            return {'PASS_THROUGH'}
        if event.type == 'ESC':
            self._set(context, self.before)
            return self._end(context, {'CANCELLED'})
        if event.type in ('RET', 'NUMPAD_ENTER'):
            return self._end(context, {'FINISHED'})
        if event.type == 'BACK_SPACE':
            self._set(context, "" if event.ctrl else state.search[:-1])
            return {'RUNNING_MODAL'}
        if event.unicode and event.unicode.isprintable() and not (event.ctrl or event.oskey):
            self._set(context, state.search + event.unicode)
        return {'RUNNING_MODAL'}                         # as outras teclas não vão para a cena enquanto digita


classes = (BTM_OT_LibrarySearch,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    draw._search['active'] = False
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
