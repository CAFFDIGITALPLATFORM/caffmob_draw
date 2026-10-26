"""Sonda em janela real da 072: destaque do espaço livre sob o mouse e inserção por clique, e o grupo "Gavetas".

    OUT=/pasta xvfb-run -a -s "-screen 0 1600x1000x24" blender --factory-startup --enable-event-simulate \
        --python tests/sonda_072_gavetas.py

Capturas em $OUT (scrot). Sai com 0 se tudo passou.
"""
import os
import subprocess
import sys
import traceback

import bpy
from bpy_extras import view3d_utils
from mathutils import Euler, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401
from caffmob_draw.customize.adapters import btm  # noqa: E402
from caffmob_draw.drawers import construtor, scene  # noqa: E402

OUT = os.environ.get('OUT', '/tmp')
FALHAS = []


def check(ok, texto, detalhe=''):
    print(('OK   ' if ok else 'FALHA ') + texto + (f' ({detalhe})' if detalhe and not ok else ''), flush=True)
    if not ok:
        FALHAS.append(texto)


def foto(nome):
    subprocess.run(['scrot', '-o', os.path.join(OUT, f'gavetas_{nome}.png')], check=False)


def script():
    ctx = bpy.context
    for o in list(ctx.scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='NONE')
    raiz = ctx.view_layer.objects.active
    bpy.ops.ed.undo_push(message='modulo')
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    space = area.spaces.active
    space.show_region_ui = True
    win.event_simulate(type='ESC', value='PRESS', x=region.x + 20, y=region.y + 20)
    win.event_simulate(type='ESC', value='RELEASE', x=region.x + 20, y=region.y + 20)
    st = ctx.window_manager.btm_sidebar
    st.open_build, st.open_group_drawers = True, True
    b = ctx.window_manager.btm_drawer_builder
    b.modelo, b.corredica, b.quantidade = 'NENHUM', 'telescopica_soft', 3
    lo, hi = btm.space_boxes(ctx, raiz)["module"]
    centro = raiz.matrix_world @ Vector(((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2))
    r3d = space.region_3d
    r3d.view_perspective = 'PERSP'
    r3d.view_location = centro
    r3d.view_rotation = Euler((1.25, 0, -0.45)).to_quaternion()
    r3d.view_distance = 2.2
    yield 1.5

    p = view3d_utils.location_3d_to_region_2d(region, r3d, centro)
    x, y = region.x + int(p.x), region.y + int(p.y)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.gaveta_espaco('INVOKE_DEFAULT')
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    yield 0.7
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 3, y=y + 3)
    yield 1.0
    alvo = construtor._destaque['alvo']
    check(alvo is not None and alvo['caminho'] == 'module', 'o espaço sob o mouse é o vão do módulo', str(alvo))
    foto('1_destaque')
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=x + 3, y=y + 3)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x + 3, y=y + 3)
    yield 1.5
    gavetas = [o for o in raiz.children_recursive if scene.is_drawer(o)]
    check(len(gavetas) == 3, 'o clique insere 3 gavetas', len(gavetas))
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 80, y=y + 80)
    yield 1.0
    foto('2_gavetas_inseridas')
    cx, cy = region.x + region.width // 2, region.y + region.height // 2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='Z', value='PRESS', x=cx, y=cy, ctrl=True)
    win.event_simulate(type='Z', value='RELEASE', x=cx, y=cy, ctrl=True)
    yield 1.5
    raiz = bpy.data.objects.get('BTM_Cabinet') or next(iter(bpy.context.scene.objects))
    restantes = [o for o in bpy.context.scene.objects if scene.is_drawer(o)]
    check(not restantes, 'um Ctrl+Z desfaz a inserção', len(restantes))
    print('RESULTADO', 'VERDE' if not FALHAS else 'VERMELHO', flush=True)
    os._exit(1 if FALHAS else 0)


_g = script()


def passo():
    try:
        return next(_g)
    except StopIteration:
        return None
    except Exception:
        traceback.print_exc()
        os._exit(1)


bpy.app.timers.register(passo, first_interval=2.0)
