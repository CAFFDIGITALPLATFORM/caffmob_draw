"""Aviso ao salvar o projeto (feature 003, T065; RF-32, D-27).

Depois de salvar, a barra de status mostra "Projeto salvo: <arquivo>" por alguns segundos. Se a gravação falhar,
mostra "Falha ao salvar" e registra no console o caminho (o Blender continua mostrando o próprio erro), para ajudar a
investigar falhas como a do bug #4 (erro ao salvar no Windows).
"""

import os

import bpy  # type: ignore
from bpy.app.handlers import persistent  # type: ignore

from ..data.i18n import tr

SHOW_SECONDS = 4.0


def _clear():
    try:
        for window in bpy.context.window_manager.windows:
            window.workspace.status_text_set(None)
    except (AttributeError, ReferenceError, RuntimeError):
        pass
    return None


def _show(text):
    try:
        windows = bpy.context.window_manager.windows
    except AttributeError:
        return
    for window in windows:
        try:
            window.workspace.status_text_set(text)
        except (AttributeError, RuntimeError):
            pass
    if bpy.app.timers.is_registered(_clear):
        bpy.app.timers.unregister(_clear)
    bpy.app.timers.register(_clear, first_interval=SHOW_SECONDS)


def show(text):
    """Mostra um aviso na barra de status por alguns segundos (usado também pelos handlers da feature 004, que não
    podem chamar `self.report`) e o registra no console."""
    print(f"CAFFMob Draw: {text}")
    _show(text)


@persistent
def on_save_post(filepath, *_args):
    if filepath:
        _show(tr("Projeto salvo: {}").format(os.path.basename(filepath)))     # sem nota de colisão (066, D-07)


@persistent
def on_save_fail(filepath, *_args):
    print(f"CAFFMob Draw: falha ao salvar '{filepath or '(arquivo de inicialização)'}'. "
          "Confira permissão de escrita, espaço em disco e se o arquivo está aberto em outro programa.")
    _show(tr("Falha ao salvar: veja a mensagem do Blender e o console"))


_HANDLERS = ((bpy.app.handlers.save_post, on_save_post), (bpy.app.handlers.save_post_fail, on_save_fail))


def register():
    for handlers, func in _HANDLERS:
        if func not in handlers:
            handlers.append(func)


def unregister():
    for handlers, func in _HANDLERS:
        if func in handlers:
            handlers.remove(func)
    if bpy.app.timers.is_registered(_clear):
        bpy.app.timers.unregister(_clear)
