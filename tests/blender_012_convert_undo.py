"""Ctrl+Z da conversão para CAFFMob, com janela (feature 012, T070; RF-14; roadmap D-31).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_012_convert_undo.py

Três armários frameless; a conversão (`caffmob.legacy_convert`, com etapa de desfazer) os troca por módulos CAFFMob;
uma etapa de desfazer (`ed.undo` com a janela, o mesmo sistema de memória do Ctrl+Z) volta os três originais e tira os
módulos; `ed.redo` refaz. Neste ambiente de teste a tecla Ctrl+Z simulada não chega ao `ed.undo` da tela (nem com o
Ctrl apertado), por isso o desfazer é chamado pelo operador, com a janela real.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401  (registra a extensão)
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def state():
    scene = bpy.context.scene
    legacy = sorted(o.name for o in scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE'))
    modules = sorted(o.name for o in scene.objects if o.btm_plane.object_kind == 'MODULE' and o.type == 'MESH'
                     and getattr(o, 'btm_cabinet', None) is not None and o.get('btm_line'))
    return legacy, modules


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for i, name in enumerate(("A", "B", "C")):
        cab = tf.BaseCabinet()
        cab.create(name)
        cab.obj.location.x = i * 1.2
        hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    bpy.ops.ed.undo_push(message="Três armários frameless")
    yield 0.5
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=win.width // 2, y=win.height // 2)
    yield 0.2
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.legacy_convert('EXEC_DEFAULT', True)
    yield 0.5
    legacy, modules = state()
    check("converte os 3", legacy == [] and modules == ["A", "B", "C"], f"{legacy} {modules}")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield 0.8
    legacy, modules = state()
    check("uma etapa de desfazer volta os 3 originais e tira os módulos", legacy == ["A", "B", "C"] and modules == [],
          f"{legacy} {modules}")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.redo()
    yield 0.8
    legacy, modules = state()
    check("refazer volta a conversão", legacy == [] and modules == ["A", "B", "C"], f"{legacy} {modules}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_012_convert_undo: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
