"""T025/T082: grupo heterogêneo, membro, corpo, Mover Sobre e cotas."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as ae
from caffmob_draw.aggregates import group, ops_members
from caffmob_draw.collision import guard, scan
from caffmob_draw.move_over import scene
from caffmob_draw.overlays import side_cotas
from caffmob_draw.selection.component import component_root


def run():
    ae.env.clean_scene()
    solid = ae.cube('Corpo', (.6, .368, 2.6), (0, 0, 1.3))
    light = bpy.data.objects.new('Luz distante', bpy.data.lights.new('Área', 'AREA'))
    empty = bpy.data.objects.new('Controle distante', None)
    curve_data = bpy.data.curves.new('Perfil', 'CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = .005
    spline = curve_data.splines.new('POLY')
    spline.points.add(1)
    spline.points[0].co = (-.1, 0, .1, 1)
    spline.points[1].co = (.1, 0, .1, 1)
    curve = bpy.data.objects.new('Perfil curvo', curve_data)
    for obj in (light, empty, curve):
        bpy.context.collection.objects.link(obj)
    light.location = empty.location = (100, 100, 100)
    cutter = ae.cube('Cortador distante', (10, 10, 10), (50, 50, 50))
    cutter['IS_CUTTING_OBJ'] = True
    ae.env.settle()
    objects = [solid, light, empty, curve, cutter]
    before = {o: o.matrix_world.copy() for o in objects}
    root = group.create_group(objects)
    ae.env.settle()
    assert all(ae.matrix_error(o.matrix_world, before[o]) < 1e-5 for o in objects)
    lo, hi = group.group_box(root)
    assert abs(hi.x - lo.x - .6) < 1e-5 and abs(hi.z - lo.z - 2.6) < 1e-5
    root.location.x += 1
    ae.env.settle()
    for obj in objects:
        assert abs(obj.matrix_world.translation.x - before[obj].translation.x - 1) < 1e-5
    assert len(group.members(root)) == 5
    nested = ae.cube('Peça do controle', (.1, .1, .1), (0, 0, 0), empty)
    hierarchy = group.create_group([empty, nested])
    ae.env.settle()
    assert nested.parent == empty and empty.parent == hierarchy
    assert group.create_group([light, empty]) is not None
    # Volta às peças e adota explicitamente a montagem heterogênea.
    ae.env.clean_scene()
    root, body = ae.tower()
    light = bpy.data.objects.new('Luz', bpy.data.lights.new('LED', 'AREA'))
    empty = bpy.data.objects.new('Controle', None)
    for obj in (light, empty):
        bpy.context.collection.objects.link(obj)
        obj.location = (100, 100, 100)
        ops_members.set_member(obj, root, 'LIGHT' if obj.type == 'LIGHT' else 'HARDWARE')
    cutter = ae.cube('Cortador', (10, 10, 10), (50, 50, 50))
    ops_members.set_member(cutter, root, 'CUTTER')
    ae.env.settle()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    assert len(guard._body(root, depsgraph)) == 1
    assert scan.entry_of(light, depsgraph) is None
    assert scan.entry_of(empty, depsgraph) is None
    assert scan.entry_of(cutter, depsgraph) is None
    corners = scene.tree_corners(root, depsgraph)
    assert max(c.x for c in corners) < 1
    assert component_root(light) == root
    # Contato externo + ausência de autocolisão; corpo não inclui luz ou cortador.
    obstacle = ae.cube('Parede solta', (.015, 5, 3), (1, 0, 1.5))
    ae.env.settle()
    start = root.matrix_world.copy()
    proposed = start.copy()
    proposed.translation.x += 2
    allowed = guard.clamp(root, start, proposed)
    assert abs(allowed.translation.x - .6925) < .002
    ae.select([light])
    lateral = {k for k in side_cotas.records(bpy.context) if k in ('LEFT', 'RIGHT')}   # cotas fixas (HYCE)
    assert len(lateral) == 1, lateral
    print('OK seleção, Mover Sobre, corpo efetivo, contato e cota lateral do autoral', flush=True)
    # Transferir/remover: pose e dono mudam sem agregado por face.
    other, _ = ae.tower('Destino', x=4)
    mover = scene.MoveOver(bpy.context, body, other)
    assert mover.a == root and mover.b == other
    mover.nudge((0, .2, 0))
    ae.env.settle()
    assert abs(root.matrix_world.translation.y - .2) < 1e-5
    mover.restore()
    ae.env.settle()
    pose = light.matrix_world.copy()
    ops_members.set_member(light, other, 'LIGHT')
    ae.env.settle()
    assert light.btm_member.owner == other and not light.btm_aggregate.is_aggregate
    assert ae.matrix_error(light.matrix_world, pose) < 1e-5
    ops_members.remove_member(light)
    ae.env.settle()
    assert light.parent is None and light.btm_member.owner is None
    assert ae.matrix_error(light.matrix_world, pose) < 1e-5
    print('blender_066_hetero_group: OK', flush=True)


run()
