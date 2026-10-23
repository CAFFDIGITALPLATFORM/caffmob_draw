"""Reprodução e regressão de BUG-20261023-NS3U (#154): clique, clique direito, botão do meio e roda sobre o painel
BIBLIOTECA CAFFMOB (retângulo MAX) não chegam à cena em Object Mode; fora do painel, a cena responde como sempre.

Precisa de janela (eventos simulados):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_bug_NS3U_biblioteca_nao_vaza_cliques.py
Em --background não há janela: o roteiro avisa e sai sem testar.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    rv3d = area.spaces.active.region_3d
    win.event_simulate('ESC', 'PRESS', x=region.x + 10, y=region.y + 10)
    win.event_simulate('ESC', 'RELEASE', x=region.x + 10, y=region.y + 10)
    yield 0.3
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 0.0))
    behind = ctx.active_object
    behind.name = "Atrás do painel"
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(6.0, 0.0, 0.0))
    outside = ctx.active_object
    outside.name = "Fora do painel"
    for obj in ctx.scene.objects:
        obj.select_set(False)
    ctx.view_layer.objects.active = None
    yield 0.3
    p = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector((0.0, 0.0, 0.0)))
    q = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector((6.0, 0.0, 0.0)))
    state = ctx.window_manager.btm_library
    state.mode, state.tab = 'MAX', 'BLOCKS'
    state.rect = (p.x - 200, p.y - 160, 420, 360)
    area.tag_redraw()
    yield 0.4
    with ctx.temp_override(window=win, area=area, region=region):
        rect = draw.max_rect(ctx, area)
        lay = draw.max_layout(ctx, area)
    x, y, w, h = rect
    gx, gy, gw, gh = lay.grid
    point = (gx + gw - 30, gy + 30)                 # canto da grade, sem célula
    check("o cubo de trás fica sob o painel", x <= p.x <= x + w and y <= p.y <= y + h, (tuple(p), rect))
    check("o cubo de fora fica fora do painel", not (x <= q.x <= x + w and y <= q.y <= y + h), (tuple(q), rect))
    wx, wy = region.x + int(point[0]), region.y + int(point[1])

    def click(button, px, py):                     # o Blender precisa processar cada evento simulado
        win.event_simulate('MOUSEMOVE', 'NOTHING', x=px, y=py)
        yield 0.1
        win.event_simulate(button, 'PRESS', x=px, y=py)
        yield 0.1
        win.event_simulate(button, 'RELEASE', x=px, y=py)
        yield 0.3

    # Clique esquerdo num ponto vazio do painel, com o cubo atrás: nada é selecionado.
    behind_px = (region.x + int(p.x), region.y + int(p.y))
    if not (x <= p.x <= x + w and y <= p.y <= y + h):
        behind_px = (wx, wy)
    yield from click('LEFTMOUSE', wx, wy)
    yield from click('LEFTMOUSE', *behind_px)
    check("reprodução: clique no painel não seleciona o que está atrás", not behind.select_get())
    # Botão do meio arrastado sobre o painel: a vista não gira.
    before = rv3d.view_rotation.copy()
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=wx, y=wy)
    yield 0.1
    win.event_simulate('MIDDLEMOUSE', 'PRESS', x=wx, y=wy)
    yield 0.1
    for k in range(1, 6):
        win.event_simulate('MOUSEMOVE', 'NOTHING', x=wx + 15 * k, y=wy)
        yield 0.05
    win.event_simulate('MIDDLEMOUSE', 'RELEASE', x=wx + 75, y=wy)
    yield 0.3
    check("reprodução: botão do meio sobre o painel não gira a vista",
          rv3d.view_rotation.rotation_difference(before).angle < 1e-4)
    # Atalhos nos mapas de modo (processados antes do 3D View).
    kc = ctx.window_manager.keyconfigs.addon
    km = kc.keymaps.get('Object Mode')
    events = {(i.idname, i.type) for i in km.keymap_items} if km else set()
    check("reprodução: clique direito e do meio do painel também no mapa Object Mode",
          any(t == 'RIGHTMOUSE' and n.startswith('caffmob.library') for n, t in events)
          and any(t == 'MIDDLEMOUSE' and n.startswith('caffmob.library') for n, t in events), sorted(events))
    # Regressão: fora do painel, a cena responde.
    state.pinned = True                              # fixo: clicar fora não fecha o painel
    rv3d.view_rotation = before                      # se a vista girou, volta para o cubo de fora ficar no lugar
    yield 0.2
    q = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector((6.0, 0.0, 0.0)))
    yield from click('LEFTMOUSE', region.x + int(q.x), region.y + int(q.y))
    check("regressão: fora do painel o clique seleciona", outside.select_get())
    state.mode, state.pinned = 'MIN', False


if bpy.app.background:
    print("blender_bug_NS3U: precisa de janela (xvfb-run); nada testado em --background", flush=True)
    sys.exit(0)

_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.5)
