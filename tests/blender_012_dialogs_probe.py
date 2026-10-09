"""Prova: um diálogo que abre outro diálogo no `execute` (feature 012, T032; roadmap D-22, P5).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_012_dialogs_probe.py

O operador A (`invoke_props_dialog`) chama, no `execute`, o operador B com `INVOKE_DEFAULT`, que abre o próprio
diálogo. Enter confirma cada um; as duas respostas têm de chegar. Também confere que Esc no segundo cancela só ele.
"""

import os
import traceback

import bpy

FAILURES = []
ANSWERS = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


class PROBE_OT_First(bpy.types.Operator):
    bl_idname = "probe.first"
    bl_label = "Pergunta 1"
    flag: bpy.props.BoolProperty(default=True)  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Pergunta 1")

    def execute(self, context):
        ANSWERS.append(('first', self.flag))
        bpy.ops.probe.second('INVOKE_DEFAULT')
        return {'FINISHED'}


class PROBE_OT_Second(bpy.types.Operator):
    bl_idname = "probe.second"
    bl_label = "Pergunta 2"
    flag: bpy.props.BoolProperty(default=True)  # type: ignore

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, title="Pergunta 2")

    def execute(self, context):
        ANSWERS.append(('second', self.flag))
        return {'FINISHED'}


bpy.utils.register_class(PROBE_OT_First)
bpy.utils.register_class(PROBE_OT_Second)


def key(win, kind):
    x, y = win.width // 2, win.height // 2
    win.event_simulate(kind, 'PRESS', x=x, y=y)
    win.event_simulate(kind, 'RELEASE', x=x, y=y)


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    yield 0.5
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=win.width // 2, y=win.height // 2)
    yield 0.2
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.probe.first('INVOKE_DEFAULT')
    yield 0.4
    key(win, 'RET')
    yield 0.5
    key(win, 'RET')
    yield 0.5
    check("as duas respostas chegam", ANSWERS == [('first', True), ('second', True)], str(ANSWERS))
    ANSWERS.clear()
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.probe.first('INVOKE_DEFAULT')
    yield 0.4
    key(win, 'RET')
    yield 0.5
    key(win, 'ESC')
    yield 0.5
    check("Esc no segundo cancela só ele", ANSWERS == [('first', True)], str(ANSWERS))


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_012_dialogs_probe: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
