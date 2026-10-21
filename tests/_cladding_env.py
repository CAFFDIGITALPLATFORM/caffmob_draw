"""Cenas reais para revestimentos; artefatos dos ensaios ficam em tempfile."""
import bpy
import _blender_env as env
import _openings_env as oe
from caffmob_draw import hb_types
from caffmob_draw.cladding import ops_adopt, sync
from caffmob_draw.collision import guard
from caffmob_draw.openings import sync as opening_sync
from caffmob_draw.operators import doors_windows as dw
from caffmob_draw.walls2d import apply, model


def check(value, label):
    assert value, label
    print('OK:', label, flush=True)


def pieces(root):
    return {o['btm_cladding_piece']['key']: o for o in bpy.context.scene.objects
            if o.get('btm_cladding_piece') and o['btm_cladding_piece'].get('owner') == root.btm_cladding.uid
            and o['btm_cladding_piece'].get('generated')}


@guard.suspended()
def scene():
    env.clean_scene()
    apply.apply_plan(bpy.context, model.WallPlan([model.rectangle(5.41, 4)]))
    env.settle()
    walls = sorted((o for o in bpy.context.scene.objects if o.get('IS_WALL_BP')), key=lambda o:o.name)
    wall = next(o for o in walls if abs(hb_types.GeoNodeWall(o).get_input('Length') - 5.41) < .001)
    door = oe.make_cage()
    door.parent, door.location = wall, (0.5, 0, 0)
    dw.cut_wall(wall, door)
    window = oe.make_cage(kind='WINDOW')
    window.parent, window.location = wall, (3, 0, 1)
    dw.cut_wall(wall, window)
    env.settle()
    opening_sync.sync(bpy.context, door)
    opening_sync.sync(bpy.context, window)
    env.settle()
    root = ops_adopt.create(wall)
    sync.sync(root)
    env.settle()
    return walls, wall, door, window, root
