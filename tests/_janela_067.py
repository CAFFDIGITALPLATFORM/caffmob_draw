"""Apoio dos ensaios da 067 que precisam de janela (Desfazer da tela): roda `body(ctx_janela)` num timer, conta as
conferências e encerra o Blender com o código certo.

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/<ensaio>.py
"""

import os
import traceback

import bpy

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


class Window:
    """A janela real e a área 3D, para `ed.undo` e operadores que pedem área."""

    def __init__(self):
        ctx = bpy.context
        self.window = ctx.window_manager.windows[0]
        self.area = next(a for a in self.window.screen.areas if a.type == 'VIEW_3D')
        self.region = next(r for r in self.area.regions if r.type == 'WINDOW')

    def override(self):
        return bpy.context.temp_override(window=self.window, area=self.area, region=self.region)

    def undo(self):
        with self.override():
            bpy.ops.ed.undo()

    def push(self, message):
        with self.override():
            bpy.ops.ed.undo_push(message=message)


def run(name, body):
    def tick():
        try:
            body(Window())
        except Exception:
            traceback.print_exc()
            FAILURES.append("exceção")
        print(f"{name}: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
        os._exit(1 if FAILURES else 0)
    bpy.app.timers.register(tick, first_interval=2.0)


def refresh():
    """Atualiza o depsgraph: os handlers refazem o snapshot do alvo, como na interface."""
    bpy.context.view_layer.update()
    from caffmob_draw.target import snapshot
    return snapshot.ensure(bpy.context)
