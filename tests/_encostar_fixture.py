"""Fixture comum dos testes da janela Encostar no Blender: cubos e o operador num objeto falso, sem área de tela."""

import types

import bpy

import _blender_env as env
from caffmob_draw.move_over import ops_dialog
from caffmob_draw.move_over.scene import MoveOver

ctx = bpy.context
REGION = types.SimpleNamespace(width=1400, height=900)
CTX = types.SimpleNamespace(area=types.SimpleNamespace(tag_redraw=lambda: None), region=REGION,
                            window_manager=ctx.window_manager, scene=ctx.scene, view_layer=ctx.view_layer,
                            evaluated_depsgraph_get=ctx.evaluated_depsgraph_get)


def cube(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = ctx.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def dialog(a, b):
    methods = {k: v for k, v in vars(ops_dialog.BTM_OT_MoveOverDialog).items() if callable(v)}
    fake = type('Dialog', (), methods)()
    fake.mo = MoveOver(ctx, a, b)
    fake.reports = []
    fake.report = lambda _kind, message: fake.reports.append(message)
    fake.finished = []
    fake._finish = lambda _context: fake.finished.append(True)
    fake.state = ctx.window_manager.btm_move_over
    fake.state.glue = False
    fake.state.snap_on = True
    fake._init_encostar(CTX)
    fake._layout(CTX)
    fake._fit_views()
    return fake


def event(kind, value='PRESS', x=-1, y=-1, unicode="", shift=False):
    return types.SimpleNamespace(type=kind, value=value, mouse_region_x=x, mouse_region_y=y, unicode=unicode,
                                 shift=shift)


def settle():
    env.settle()
