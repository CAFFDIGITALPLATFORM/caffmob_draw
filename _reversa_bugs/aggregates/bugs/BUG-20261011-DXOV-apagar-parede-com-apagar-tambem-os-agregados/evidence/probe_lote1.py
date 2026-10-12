"""Sonda do lote 1: exclusão de parede (#12 7DHT, #13 TUWO, #14 DXOV)."""
import sys
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context


def room():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    walls = [o for o in ctx.scene.objects if o.get('IS_WALL_BP')]
    # parede com matriz não trivial (deslocada e girada)
    return max(walls, key=lambda o: (o.matrix_world.translation.length, o.name))


def child_mesh(wall, name, loc):
    obj = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    ctx.scene.collection.objects.link(obj)
    obj.parent = wall
    obj.location = loc
    env.settle()
    return obj


def cabinet_with_aggregate(wall):
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.parent = wall
    base.obj.location = (2.0, 0.0, 0.0)
    fr = bpy.data.objects.new("Fruteira", bpy.data.meshes.new("Fruteira"))
    ctx.scene.collection.objects.link(fr)
    fr.parent = base.obj
    fr.btm_aggregate.is_aggregate = True
    env.settle()
    return base.obj, fr


def run_delete(wall, with_aggregates):
    with ctx.temp_override(selected_objects=[wall], active_object=wall, object=wall):
        poll = bpy.ops.caffmob.delete_with_aggregates.poll()
        if poll:
            res = bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT', with_aggregates=with_aggregates)
        else:
            res = bpy.ops.object.delete()
    env.settle()
    return poll, res


print("=== #12 filhos não grudados (sem agregados): Delete nativo ou do plugin")
wall = room()
door = oe.make_cage('DOOR'); door.parent = wall; door.location = (1.0, 0, 0); dw.cut_wall(wall, door); env.settle()
sync.sync(ctx, door); env.settle()
geo = child_mesh(wall, "Geo", (2.5, 0.3, 0.0))
before = geo.matrix_world.translation.copy()
door_name = door.name
poll, res = run_delete(wall, True)
print("poll plugin:", poll, res)
print("Geo antes", tuple(round(v, 3) for v in before), "depois", tuple(round(v, 3) for v in geo.matrix_world.translation))
print("porta ainda existe:", door_name in bpy.data.objects)

print("=== #12/#13 com módulo e agregado, with_aggregates=False")
wall = room()
geo = child_mesh(wall, "Geo", (2.5, 0.3, 0.0))
cab, fr = cabinet_with_aggregate(wall)
before_geo = geo.matrix_world.translation.copy()
before_cab = cab.matrix_world.translation.copy()
poll, res = run_delete(wall, False)
print("poll plugin:", poll, res)
print("Geo salto:", round((geo.matrix_world.translation - before_geo).length, 3),
      "Balcao salto:", round((cab.matrix_world.translation - before_cab).length, 3))
print("Fruteira continua agregado:", fr.btm_aggregate.is_aggregate, "pai:", fr.parent.name if fr.parent else None)

print("=== #14 com módulo e agregado, with_aggregates=True")
wall = room()
cab, fr = cabinet_with_aggregate(wall)
fr_name = fr.name
poll, res = run_delete(wall, True)
print("poll plugin:", poll, res, "Fruteira existe:", fr_name in bpy.data.objects,
      "agregado:", bpy.data.objects[fr_name].btm_aggregate.is_aggregate if fr_name in bpy.data.objects else None)
