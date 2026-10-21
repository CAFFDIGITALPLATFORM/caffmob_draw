"""Cena sintética autoral compartilhada pelos ensaios 066."""
import math
import bpy
from mathutils import Matrix
import _blender_env as env
from caffmob_draw.aggregates import ops_authored
from caffmob_draw.collision import guard


@guard.suspended()
def cube(name, size, location=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name = name
    # Geometria em metros, sem escala para tornar os erros de eixo visíveis.
    for vertex in obj.data.vertices:
        for i in range(3):
            vertex.co[i] *= size[i]
    obj.parent = parent
    obj.location = location
    env.settle()
    guard.accept(obj)
    return obj


def tower(name='Torre', angle=0, x=0, axis='NEG_Y'):
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.matrix_world = Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(angle), 4, 'Z')
    body = cube(name + ' corpo', (.6, .368, 2.6), (0, 0, 1.3), root)
    env.settle()
    ops_authored.adopt(root, [root, body], axis)
    return root, body


def select(objects, active=None):
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active or objects[0]


def matrix_error(a, b):
    return max(abs(a[r][c] - b[r][c]) for r in range(4) for c in range(4))
