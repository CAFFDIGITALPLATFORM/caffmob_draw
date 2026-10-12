"""Reprodução e regressão de BUG-20261011-W2DP: inserido pela barra lateral, o objeto segue o mouse (RN-14, DT-01).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_bug_W2DP_object_insert.py
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401  (registra a extensão)

from caffmob_draw.object_library import item_io, ops  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def script():
    ctx = bpy.context
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    area.spaces.active.show_region_ui = True
    yield 0.5
    window = next(r for r in area.regions if r.type == 'WINDOW')
    sidebar = next(r for r in area.regions if r.type == 'UI')
    items, _w = item_io.all_items()
    key = ops.item_key(items[0])
    ctx.scene.cursor.location = (0.0, 0.0, 0.0)
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=sidebar.x + 20, y=sidebar.y + 40)   # aquecimento
    yield 0.2
    with ctx.temp_override(window=win, area=area, region=sidebar):
        result = bpy.ops.caffmob.object_insert('INVOKE_DEFAULT', key=key)
    check("modal aberto pela barra lateral", result == {'RUNNING_MODAL'}, str(result))
    root = ctx.view_layer.objects.active
    yield 0.2
    for dx in (0, 40, 80):
        win.event_simulate('MOUSEMOVE', 'NOTHING', x=window.x + window.width // 4 + dx, y=window.y + window.height // 4)
        yield 0.1
    moved = root.location.copy()
    check("W2DP: o objeto segue o mouse", moved.length > 0.05, str(tuple(round(v, 3) for v in moved)))
    win.event_simulate('ESC', 'PRESS', x=window.x + 10, y=window.y + 10)
    win.event_simulate('ESC', 'RELEASE', x=window.x + 10, y=window.y + 10)
    yield 0.3


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_bug_W2DP_object_insert: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
