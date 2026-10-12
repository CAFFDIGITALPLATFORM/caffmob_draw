"""Reprodução e regressão do lote do gizmo de inspeção: BUG-20261011-5EX7, BUG-20261011-GBPG e BUG-20261011-PGMI.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5EX7_gizmo.py

- folha de correr convertida tem curso (`travel`) e o gizmo não quebra (questions.md, pergunta 61);
- o dial vai até o máximo da folha (pergunta 62);
- trocar de ativo logo depois de soltar o gizmo grava o valor na frente certa (inspection EC-18).
"""

import math
import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
from caffmob_draw.inspection import gizmo  # noqa: E402
from caffmob_draw.inspection.adapters import aggregate_leaf  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402

ctx = bpy.context
FAILURES = []
GROUP = gizmo.BTM_GGT_front_open


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def leaves(kind):
    env.clean_scene()
    cage = oe.make_cage(kind)
    sync.sync(ctx, cage)
    env.settle()
    return [aggregate_leaf.AggregateLeafFront(o) for o in cage.btm_opening_real.assembly.children_recursive
            if aggregate_leaf.is_leaf(o)]


def reset():
    gizmo._state.update(front=None, pending=None, pointer=0)
    gizmo._state['pending_front'] = None


def slide_travel():
    reset()
    front = leaves('WINDOW')[0]
    try:
        travel = front.travel()
        gizmo._state['front'] = front
        GROUP._arrow_get(types.SimpleNamespace())
        ok, detail = travel > 0.0, f"curso {travel:.3f} m"
    except AttributeError as exc:
        ok, detail = False, repr(exc)
    check("5EX7: folha de correr convertida tem curso e o gizmo lê", ok, detail)


def dial_max():
    reset()
    front = leaves('DOOR')[0]
    front.obj.btm_aggregate.max_angle = 110.0
    gizmo._state['front'] = front
    GROUP._dial_set(types.SimpleNamespace(), math.radians(105.0))
    check("GBPG: o dial vai até o máximo da folha", abs(front.get() - 105.0) < 0.5, f"{front.get():.1f}°")
    gizmo._commit_pending()


def commit_on_switch():
    reset()
    front = leaves('DOOR')[0]
    gizmo._state['front'] = front
    gizmo._state['pointer'] = front.obj.as_pointer()
    GROUP._dial_set(types.SimpleNamespace(), math.radians(60.0))
    other = bpy.data.objects.new("Outro", bpy.data.meshes.new("Outro"))
    ctx.scene.collection.objects.link(other)
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    other.select_set(True)
    ctx.view_layer.objects.active = other
    gizmo._active_front(ctx)                                 # o ativo novo não é frente
    gizmo._commit_pending()                                  # o timer roda depois
    value = front.obj.btm_aggregate.open_value * front.obj.btm_aggregate.max_angle
    check("PGMI: o valor pendente é gravado na frente de antes", abs(value - 60.0) < 0.5, f"{value:.1f}°")


for step in (slide_travel, dial_max, commit_on_switch):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_5EX7_gizmo: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
