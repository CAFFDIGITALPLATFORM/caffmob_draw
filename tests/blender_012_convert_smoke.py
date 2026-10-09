"""Fumaça de Converter para CAFFMob (feature 012, T062; RF-13, RF-14, RN-12, RN-13).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_convert_smoke.py

Arquivo com 3 frameless (um com 3 gavetas), 1 face frame e 1 closet:
- 5 raízes herdadas; converter deixa 5 módulos CAFFMob na mesma caixa (posição, rotação e medidas externas);
- o relatório lista as gavetas perdidas;
- os objetos herdados (raízes e peças) saem; um item grudado não é apagado;
- 50 armários em menos de 5 s.
O Ctrl+Z da conversão é provado com janela em `blender_012_convert_undo.py` (D-31).
"""

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.legacy import convert, gate  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def world_box(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.evaluated_get(ctx.evaluated_depsgraph_get()).bound_box]
    return tuple(round(min(p[i] for p in pts), 3) for i in range(3)) + \
        tuple(round(max(p[i] for p in pts), 3) for i in range(3))


def frameless(name, x, exterior='Doors', rotate=0.0):
    cab = tf.BaseCabinet()
    cab.default_exterior = exterior
    cab.create(name)
    cab.obj.location = (x, 0.0, 0.0)
    cab.obj.rotation_euler.z = rotate
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    return cab.obj


def build_scene():
    env.clean_scene()
    roots = [frameless("Balcao A", 0.0), frameless("Balcao B", 1.2, rotate=1.5708),
             frameless("Gaveteiro", 2.4, exterior='3 Drawers')]
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    ff.obj.location.x = 4.0
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    starter.obj.location.x = 6.0
    tc.recalculate_closet_starter(starter.obj)
    roots += [ff.obj, starter.obj]
    env.settle()
    return roots


def main():
    roots = build_scene()
    names = sorted(r.name for r in roots)
    check("5 armários herdados", sorted(o.name for o in gate.legacy_roots(ctx.scene)) == names,
          str([o.name for o in gate.legacy_roots(ctx.scene)]))
    boxes = {r.name: world_box(r) for r in roots}
    legacy_objects = {o.name for r in roots for o in [r] + list(r.children_recursive)}
    with ctx.temp_override(selected_objects=[], active_object=None):
        assert bpy.ops.caffmob.legacy_convert('EXEC_DEFAULT') == {'FINISHED'}
    env.settle()
    check("nenhum herdado sobra", not gate.legacy_roots(ctx.scene))
    modules = {name: bpy.data.objects.get(name) for name in names}
    check("5 módulos CAFFMob com os mesmos nomes",
          all(m is not None and m.btm_plane.object_kind == 'MODULE' for m in modules.values()), str(modules))
    for name, module in modules.items():
        if module is None:
            continue
        got = world_box(module)
        same = all(abs(a - b) < 0.002 for a, b in zip(got, boxes[name]))
        check(f"{name}: mesma caixa no mundo", same, f"{got} × {boxes[name]}")
    leftovers = [n for n in legacy_objects if n in bpy.data.objects and n not in names]
    check("peças herdadas saem", not leftovers, str(leftovers[:5]))
    drawers = modules["Gaveteiro"]
    check("closet vira linha DOR", modules["Roupeiro"].btm_cabinet.line == 'DOR')
    check("gaveteiro sem portas", drawers.btm_cabinet.door_swing == 'NONE')

    # Relatório (o operador grava em ops_standards._LAST_REPORT).
    from caffmob_draw.operators import ops_standards
    lines = ops_standards._LAST_REPORT['lines']
    check("relatório lista as gavetas perdidas", any("Gaveteiro" in line and "3" in line for line in lines),
          str(lines))

    # Desempenho.
    env.clean_scene()
    many = [frameless(f"B{i}", i * 0.7) for i in range(50)]
    env.settle()
    start = time.perf_counter()
    results = convert.convert_scene(ctx, many)
    elapsed = time.perf_counter() - start
    check("50 armários em menos de 5 s", len(results) == 50 and elapsed < 5.0, f"{elapsed:.2f} s")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_012_convert_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
