"""Reprodução e regressão do lote de exclusão de parede: BUG-20261011-7DHT, BUG-20261011-TUWO, BUG-20261011-DXOV.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_7DHT_wall_delete.py

Decisões do titular (questions.md, perguntas 2, 4 e 5): X/Delete numa parede usa `ops_wall_extras.remove_wall`
(filhos soltos com a matriz de mundo preservada; portas, janelas e cotas saem com a parede) e os agregados dos
módulos filhos da parede não entram na pergunta "O objeto tem agregados".
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import ops_aggregate  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def room():
    """Sala 4 × 3; devolve a parede mais longe da origem (matriz de mundo deslocada e girada)."""
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    walls = [o for o in ctx.scene.objects if o.get('IS_WALL_BP')]
    return max(walls, key=lambda o: (o.matrix_world.translation.length, o.name))


def child_mesh(wall, name, loc):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    ctx.scene.collection.objects.link(obj)
    obj.parent = wall
    obj.location = loc
    env.settle()
    return obj


def door_on(wall, x):
    door = oe.make_cage('DOOR')
    door.parent = wall
    door.location = (x, 0.0, 0.0)
    dw.cut_wall(wall, door)
    env.settle()
    sync.sync(ctx, door)
    env.settle()
    return door


def cabinet_with_aggregate(wall):
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.parent = wall
    base.obj.location = (2.0, 0.0, 0.0)
    fruteira = bpy.data.objects.new("Fruteira", bpy.data.meshes.new("Fruteira"))
    ctx.scene.collection.objects.link(fruteira)
    fruteira.parent = base.obj
    fruteira.btm_aggregate.is_aggregate = True
    env.settle()
    return base.obj, fruteira


def press_x(wall, with_aggregates=True):
    with ctx.temp_override(selected_objects=[wall], active_object=wall, object=wall):
        poll = bpy.ops.caffmob.delete_with_aggregates.poll()
        result = bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT', with_aggregates=with_aggregates) if poll else None
    env.settle()
    return poll, result


def moved(obj, before):
    return (obj.matrix_world.translation - before).length


def wall_with_door_and_geometry():
    wall = room()
    walls = len([o for o in ctx.scene.objects if o.get('IS_WALL_BP')])
    door = door_on(wall, 1.0)
    door_parts = [door.name] + [o.name for o in door.children_recursive]
    geo = child_mesh(wall, "Geo", (2.5, 0.3, 0.0))
    before = geo.matrix_world.translation.copy()
    poll, result = press_x(wall)
    check("7DHT: X numa parede sem agregado é do plugin", poll and result == {'FINISHED'}, str(result))
    check("7DHT: a geometria filha fica no lugar", moved(geo, before) < 1e-6, f"{moved(geo, before):.3f} m")
    left = [n for n in door_parts if n in bpy.data.objects]
    check("7DHT: a porta sai com a parede (KEEP_WITH_WALL)", not left, str(left))
    remaining = len([o for o in ctx.scene.objects if o.get('IS_WALL_BP')])
    check("7DHT: só a parede escolhida sai", remaining == walls - 1, f"{walls} → {remaining}")


def wall_with_module(with_aggregates):
    wall = room()
    geo = child_mesh(wall, "Geo", (2.5, 0.3, 0.0))
    cabinet, fruteira = cabinet_with_aggregate(wall)
    check("TUWO/DXOV: a pergunta não lista agregados do módulo filho",
          ops_aggregate._children_aggregates(wall) == [], str(ops_aggregate._children_aggregates(wall)))
    before_geo = geo.matrix_world.translation.copy()
    before_cab = cabinet.matrix_world.translation.copy()
    poll, result = press_x(wall, with_aggregates)
    tag = "ligado" if with_aggregates else "desligado"
    check(f"7DHT ({tag}): X apaga a parede", poll and result == {'FINISHED'}, str(result))
    check(f"7DHT ({tag}): geometria e balcão ficam no lugar",
          moved(geo, before_geo) < 1e-6 and moved(cabinet, before_cab) < 1e-6,
          f"geo {moved(geo, before_geo):.3f} m, balcão {moved(cabinet, before_cab):.3f} m")
    check(f"TUWO/DXOV ({tag}): a fruteira continua agregado do balcão",
          fruteira.name in bpy.data.objects and fruteira.btm_aggregate.is_aggregate and fruteira.parent == cabinet,
          f"agregado={fruteira.btm_aggregate.is_aggregate} pai={fruteira.parent.name if fruteira.parent else None}")


try:
    wall_with_door_and_geometry()
    wall_with_module(with_aggregates=False)
    wall_with_module(with_aggregates=True)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_7DHT_wall_delete: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
