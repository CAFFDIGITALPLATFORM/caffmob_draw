"""Sonda em janela real da 071, onda B: editor de escadas, prévia, inserção por clique, painel e desfazer.

    OUT=/pasta xvfb-run -a -s "-screen 0 1600x1000x24" blender --factory-startup --enable-event-simulate \
        --python tests/sonda_071_escadas.py

Capturas em $OUT (scrot). Sai com 0 se tudo passou.
"""
import os
import subprocess
import sys
import traceback

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blender_env  # noqa: E402,F401
from caffmob_draw.stairs import scene  # noqa: E402

OUT = os.environ.get('OUT', '/tmp')
FALHAS = []


def check(ok, texto, detalhe=''):
    print(('OK   ' if ok else 'FALHA ') + texto + (f' ({detalhe})' if detalhe and not ok else ''), flush=True)
    if not ok:
        FALHAS.append(texto)


def foto(nome):
    subprocess.run(['scrot', '-o', os.path.join(OUT, f'escadas_{nome}.png')], check=False)


def area_3d():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def script():
    ctx = bpy.context
    for o in list(ctx.scene.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.ed.undo_push(message='vazio')
    win, area, region = area_3d()
    space = area.spaces.active
    space.show_region_ui = True
    win.event_simulate(type='ESC', value='PRESS', x=region.x + 20, y=region.y + 20)
    win.event_simulate(type='ESC', value='RELEASE', x=region.x + 20, y=region.y + 20)
    st = ctx.window_manager.btm_sidebar
    st.open_build, st.open_group_stairs, st.open_selected = True, True, True
    editor = ctx.window_manager.btm_stairs
    editor.inicial()
    editor.tipo = 'L'
    editor.altura = '2800'
    rv3d = space.region_3d
    rv3d.view_location = Vector((1.5, 2.0, 1.0))
    rv3d.view_distance = 9.0
    for a in win.screen.areas:
        a.tag_redraw()
    yield 1.5
    foto('1_editor_e_previa')

    # Inserir por clique no piso (modal real)
    alvo = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector((0.0, 0.0, 0.0)))
    x, y = region.x + int(alvo.x), region.y + int(alvo.y)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.escada_inserir('INVOKE_DEFAULT')
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
    yield 0.5
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 2, y=y + 2)
    yield 0.5
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=x + 2, y=y + 2)
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x + 2, y=y + 2)
    yield 1.0
    raizes = scene.roots(ctx.scene)
    check(len(raizes) == 1, 'um clique no piso insere uma escada', len(raizes))
    raiz = raizes[0] if raizes else None
    if raiz is not None:
        degraus = [c for c in raiz.children if 'degrau' in (c.get(scene.PART_PROP) or '')]
        check(len(degraus) == 14, 'escada em L com 14 degraus', len(degraus))
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 60, y=y + 60)
    yield 1.5
    foto('2_escada_inserida_e_painel')

    # Desfazer a inserção
    cx, cy = region.x + region.width // 2, region.y + region.height // 2
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=cx, y=cy)
    win.event_simulate(type='Z', value='PRESS', x=cx, y=cy, ctrl=True)
    win.event_simulate(type='Z', value='RELEASE', x=cx, y=cy, ctrl=True)
    yield 1.5
    check(not scene.roots(bpy.context.scene), 'um Ctrl+Z desfaz a inserção inteira', len(scene.roots(bpy.context.scene)))
    print('RESULTADO', 'VERDE' if not FALHAS else 'VERMELHO', flush=True)
    os._exit(1 if FALHAS else 0)


_gerador = script()


def passo():
    try:
        return next(_gerador)
    except StopIteration:
        return None
    except Exception:
        traceback.print_exc()
        os._exit(1)


bpy.app.timers.register(passo, first_interval=2.0)
