"""Reprodução e regressão do lote das cotas de módulo: BUG-20261011-NBKB e BUG-20261011-4ZPJ
(os casos puros de BUG-20261011-3W52 e BUG-20261011-WJHO estão em tests/test_cotas.py).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_NBKB_measure.py

- vizinho sem Geometry Nodes (módulo rápido) conta pela largura real, não como um ponto (questions.md, pergunta 13);
- o getter das cotas no painel não quebra com a parede sem o input Length (measure EC-08).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.measure import scene_cotas  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.ui import object_properties  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def wall_with_module():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.Chain([(0, 0), (4, 0)], [model.Segment()])]))
    env.settle()
    wall = next(o for o in ctx.scene.objects if o.get('IS_WALL_BP'))
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.parent = wall
    base.obj.location = (1.5, 0.0, 0.0)
    env.settle()
    return wall, base.obj


def quick_neighbor():
    wall, balcao = wall_with_module()
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    quick = ctx.object
    quick.parent = wall
    quick.matrix_parent_inverse.identity()
    quick.location = (0.2, 0.0, 0.0)
    env.settle()
    right_edge = 0.2 + quick.btm_cabinet.width
    anterior = scene_cotas.for_object(balcao, ctx.scene).compute().anterior
    check("NBKB: cota anterior mede até a lateral do módulo rápido", abs(anterior - (1.5 - right_edge)) < 1e-4,
          f"anterior={anterior:.4f} esperado={1.5 - right_edge:.4f}")


def broken_wall_getter():
    wall, balcao = wall_with_module()
    wall.home_builder.mod_name = ""                          # GeoNodeWall.get_input('Length') levanta ValueError
    balcao.location.y = -0.01                                # continua do lado da frente (espessura lida vira 0)
    env.settle()
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    balcao.select_set(True)
    ctx.view_layer.objects.active = balcao
    try:
        value = object_properties._cota_getter('anterior')(None)
        ok, detail = value == 0.0, str(value)
    except ValueError as exc:
        ok, detail = False, repr(exc)
    check("4ZPJ: o getter da cota não quebra com a parede sem Length", ok, detail)


for step in (quick_neighbor, broken_wall_getter):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_NBKB_measure: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
