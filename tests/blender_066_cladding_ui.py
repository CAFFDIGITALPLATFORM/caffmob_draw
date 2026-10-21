"""T084/RF-089/RF-090: modal real, Esc e Desfazer/Refazer em janela, sem artefatos no repositório.

xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_066_cladding_ui.py
"""
import math
import os
import sys
import traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Quaternion, Vector
from bpy_extras import view3d_utils
import _blender_env as env
from caffmob_draw.cladding import ops, sync
from caffmob_draw.collision import guard


def check(value, label):
    assert value, label
    print('OK:',label,flush=True)


def key(win, kind, x, y):
    win.event_simulate(kind,'PRESS',x=x,y=y)
    win.event_simulate(kind,'RELEASE',x=x,y=y)


def script():
    ctx=bpy.context
    win=ctx.window_manager.windows[0]
    area=next(a for a in win.screen.areas if a.type=='VIEW_3D')
    region=next(r for r in area.regions if r.type=='WINDOW')
    key(win,'ESC',10,10)
    yield .5
    with guard.suspended():
        env.clean_scene()
        mesh=bpy.data.meshes.new('Face de ensaio')
        mesh.from_pydata([(0,0,0),(5.41,0,0),(5.41,0,2.6),(0,0,2.6)],[],[(0,1,2,3)])
        host=bpy.data.objects.new('Parede de ensaio',mesh)
        ctx.collection.objects.link(host)
        host.select_set(True)
        ctx.view_layer.objects.active=host
        env.settle()
    rv3d=area.spaces.active.region_3d
    rv3d.view_rotation=Quaternion((1,0,0),math.pi/2)
    rv3d.view_location=(2.7,0,1.3)
    rv3d.view_distance=8
    rv3d.view_perspective='ORTHO'
    yield .5
    point=view3d_utils.location_3d_to_region_2d(region,rv3d,Vector((1,0,1)))
    x,y=round(region.x+point.x),round(region.y+point.y)
    bpy.ops.ed.undo_push(message='Antes do revestimento')
    initial=set(bpy.data.objects.keys())
    with ctx.temp_override(window=win,area=area,region=region):
        result=bpy.ops.caffmob.cladding_face('INVOKE_DEFAULT')
    check(result=={'RUNNING_MODAL'},'modal real inicia em janela')
    yield .3
    win.event_simulate('MOUSEMOVE','NOTHING',x=x,y=y)
    yield .5
    check(bool(ops._live) and bool(next(iter(ops._live))._lines),'raycast escolhe a face e desenha prévia')
    key(win,'ESC',x,y)
    yield .5
    check(not ops._live and set(bpy.data.objects.keys())==initial,'Esc remove desenho e preserva a cena')
    with ctx.temp_override(window=win,area=area,region=region):
        bpy.ops.caffmob.cladding_face('INVOKE_DEFAULT')
    yield .3
    win.event_simulate('MOUSEMOVE','NOTHING',x=x,y=y)
    yield .5
    key(win,'LEFTMOUSE',x,y)
    yield .3
    key(win,'RET',x,y)
    yield 1
    roots=sync.controllers()
    check(len(roots)==1 and not ops._live,'confirmar gera um controlador e encerra o modal')
    uid=roots[0].btm_cladding.uid
    with ctx.temp_override(window=win,area=area,region=region):
        bpy.ops.ed.undo()
    yield .5
    check(not sync.controllers(),'um Desfazer da confirmação remove controlador e peças')
    with ctx.temp_override(window=win,area=area,region=region):
        bpy.ops.ed.redo()
    yield .5
    check(len(sync.controllers())==1 and sync.controllers()[0].btm_cladding.uid==uid,
          'Refazer recupera revestimento e identidade')
    print('T084 JANELADO OK',flush=True)


generator=script()


def tick():
    try:
        return next(generator)
    except StopIteration:
        os._exit(0)
    except Exception:
        traceback.print_exc()
        os._exit(1)


if bpy.app.background:
    print('blender_066_cladding_ui: precisa de janela; nada testado em --background',flush=True)
else:
    bpy.app.timers.register(tick,first_interval=2)
