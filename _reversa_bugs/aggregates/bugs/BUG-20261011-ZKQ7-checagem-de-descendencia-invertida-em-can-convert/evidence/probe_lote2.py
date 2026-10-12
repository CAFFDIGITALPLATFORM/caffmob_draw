import sys
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env as env  # noqa
import bpy  # noqa
from caffmob_draw.aggregates import convert  # noqa
from caffmob_draw.stick import link  # noqa

def mesh(name, parent=None, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, bpy.data.meshes.new(name)); bpy.context.scene.collection.objects.link(o)
    o.parent = parent; o.location = loc; return o

env.clean_scene()
caixa = mesh("Caixa"); peca = mesh("Peca", caixa, (1, 0, 0))
print("can_convert(peca filha da caixa, caixa):", repr(convert.can_convert(peca, caixa)))
obj = mesh("Obj"); filho = mesh("Filho", obj, (0, 1, 0))
print("can_convert(obj, pai=filho do obj):", repr(convert.can_convert(obj, filho)))
# ciclo no Blender 5.2?
a = mesh("A"); b = mesh("B", a); a.parent = b; bpy.context.view_layer.update()
print("Blender aceita ciclo A<->B:", a.parent == b and b.parent == a)
# stick release com orig_parent descendente do item
env.clean_scene()
item = mesh("Item", None, (2, 0, 0)); desc = mesh("Desc", item, (0, 0, 1))
item.btm_stick.is_stuck = True; item.btm_stick.orig_parent = desc
bpy.context.view_layer.update()
link.release(item); bpy.context.view_layer.update()
print("release: item.parent =", item.parent.name if item.parent else None, "| desc.parent =", desc.parent.name if desc.parent else None,
      "| ciclo:", item.parent == desc and desc.parent == item)
print("release: item world =", tuple(round(v, 3) for v in item.matrix_world.translation), "(era (2, 0, 0))")
env.clean_scene()
obj = mesh("Obj", None, (3, 0, 0)); filho = mesh("Filho", obj, (0, 1, 0))
bpy.context.view_layer.update()
try:
    r = convert.convert(obj, filho)
    bpy.context.view_layer.update()
    print("convert(obj, filho):", r, "| obj.parent =", obj.parent.name if obj.parent else None,
          "| is_aggregate =", obj.btm_aggregate.is_aggregate, "| parent_ref =", obj.btm_aggregate.parent_ref.name if obj.btm_aggregate.parent_ref else None)
except Exception as e:
    print("convert(obj, filho) exceção:", type(e).__name__, e)
