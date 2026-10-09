"""Prova do arraste da seleção por componente (feature 011, T011; roadmap D-03).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_011_drag_probe.py

Uma "cadeira" de 5 malhas agrupada (`btm_group`); clicar num pé e arrastar, sem nada selecionado antes, tem que mover
as 5 juntas: o normalizador (`depsgraph_update_post`) precisa promover o pé ao grupo antes de o arraste começar.
Também confere o clique simples, o Alt + clique (só a peça) e o clique sem Alt que volta ao componente.
Sai com código 0 (tudo certo) ou 1 (falhas listadas no console).
"""

import os
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401  (registra a extensão)

from caffmob_draw.aggregates import group  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def ev(win, kind, value='PRESS', x=0, y=0, alt=False):
    win.event_simulate(kind, value, x=int(x), y=int(y), alt=alt)


def view3d(win):
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    return area, next(r for r in area.regions if r.type == 'WINDOW'), area.spaces.active.region_3d


def click(win, x, y, alt=False):
    ev(win, 'MOUSEMOVE', 'NOTHING', x, y)
    yield 0.05
    ev(win, 'LEFTMOUSE', 'PRESS', x, y, alt=alt)
    ev(win, 'LEFTMOUSE', 'RELEASE', x, y, alt=alt)
    yield 0.3


def selected_names(ctx):
    return sorted(o.name for o in ctx.view_layer.objects if o.select_get())


def script():
    ctx = bpy.context
    scene = ctx.scene
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    win = ctx.window_manager.windows[0]
    area, region, rv3d = view3d(win)
    yield 0.5

    parts = []
    for name, loc, size in (("Assento", (0, 0, 0.45), (0.5, 0.5, 0.05)), ("Pé 1", (-0.2, -0.2, 0.2), (0.05, 0.05, 0.4)),
                            ("Pé 2", (0.2, -0.2, 0.2), (0.05, 0.05, 0.4)), ("Pé 3", (-0.2, 0.2, 0.2), (0.05, 0.05, 0.4)),
                            ("Pé 4", (0.2, 0.2, 0.2), (0.05, 0.05, 0.4))):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
        obj = ctx.active_object
        obj.name = name
        obj.scale = size
        parts.append(obj)
    chair = group.create_group(parts, 'PLAIN', "Cadeira")
    for obj in list(ctx.selected_objects):
        obj.select_set(False)
    ctx.view_layer.update()
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type='TOP')
        bpy.ops.view3d.view_all()
    yield 0.5

    def to_win(co):
        p = view3d_utils.location_3d_to_region_2d(region, rv3d, Vector(co))
        return region.x + p.x, region.y + p.y

    leg = to_win((0.2, -0.2, 0.45))         # vista de cima: canto do assento sobre o Pé 2, clicar fora do assento
    seat_edge = to_win((0.0, -0.24, 0.47))
    empty = (region.x + 15, region.y + 15)
    yield from click(win, *empty)            # aquecimento: o 1º evento simulado se perde numa janela nova

    # 1. Clique simples numa peça seleciona a cadeira.
    yield from click(win, *seat_edge)
    check("clique numa peça seleciona o grupo", selected_names(ctx) == ["Cadeira"], str(selected_names(ctx)))

    # 2. Alt + clique seleciona só a peça; clique sem Alt volta ao grupo.
    yield from click(win, *seat_edge, alt=True)
    check("Alt + clique seleciona só a peça", selected_names(ctx) == ["Assento"],
          f"{selected_names(ctx)} isentas={ctx.window_manager.btm_component_exempt!r}")
    yield from click(win, *seat_edge)
    check("clique sem Alt volta ao componente", selected_names(ctx) == ["Cadeira"], str(selected_names(ctx)))

    # 3. Arrastar um pé, sem nada selecionado, move a cadeira inteira. Arrastar move com a ferramenta Tweak; a de
    # fábrica (Select Box) faz seleção por caixa, conferida no passo 4.
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
    yield from click(win, *empty)
    before = {o.name: o.matrix_world.translation.copy() for o in parts + [chair]}
    start = seat_edge
    ev(win, 'MOUSEMOVE', 'NOTHING', *start)
    yield 0.05
    ev(win, 'LEFTMOUSE', 'PRESS', *start)
    yield 0.1
    for k in range(1, 12):
        ev(win, 'MOUSEMOVE', 'NOTHING', start[0] + 6 * k, start[1])
        yield 0.04
    ev(win, 'LEFTMOUSE', 'RELEASE', start[0] + 66, start[1])
    yield 0.4
    moved = {name: (o.matrix_world.translation - before[name]).length
             for name, o in [(p.name, p) for p in parts + [chair]]}
    together = all(d > 0.01 for d in moved.values()) and max(moved.values()) - min(moved.values()) < 1e-4
    check("arrastar uma peça move o componente inteiro (D-03)", together,
          ", ".join(f"{k}={v:.3f}" for k, v in moved.items()))
    del leg

    # 4. Seleção por caixa (Select Box) que pega só peças seleciona o grupo, sem repetir.
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
    yield from click(win, *empty)
    center = chair.matrix_world.translation
    lo, hi = to_win(center + Vector((-0.25, -0.25, 0.0))), to_win(center + Vector((0.25, 0.25, 0.0)))
    corner_a, corner_b = (lo[0] - 20, lo[1] - 20), (hi[0] + 20, hi[1] + 20)
    ev(win, 'MOUSEMOVE', 'NOTHING', *corner_a)
    yield 0.05
    ev(win, 'LEFTMOUSE', 'PRESS', *corner_a)
    for k in range(1, 11):
        ev(win, 'MOUSEMOVE', 'NOTHING', corner_a[0] + (corner_b[0] - corner_a[0]) * k / 10,
           corner_a[1] + (corner_b[1] - corner_a[1]) * k / 10)
        yield 0.04
    ev(win, 'LEFTMOUSE', 'RELEASE', *corner_b)
    yield 0.4
    check("seleção por caixa sobe para o grupo", selected_names(ctx) == ["Cadeira"], str(selected_names(ctx)))

    # 5. Região na parede (T024): dois cliques marcam 800 × 2100, a porta escolhida entra com Enter, exata.
    from caffmob_draw import hb_types
    from caffmob_draw.walls2d import apply, model
    for obj in list(scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    ctx.view_layer.update()
    wall = max((o for o in scene.objects if o.get('IS_WALL_BP')),
               key=lambda o: hb_types.GeoNodeWall(o).get_input('Length'))
    for other in scene.objects:                     # a parede oposta ficaria entre a vista e a parede alvo
        if other.get('IS_WALL_BP') and other is not wall:
            other.hide_viewport = True
    m = wall.matrix_world
    facing = (m.to_3x3() @ Vector((0.0, -1.0, 0.0))).normalized()          # olhar para a face da frente (y = 0)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type='FRONT')
    rv3d.view_rotation = facing.to_track_quat('Z', 'Y')
    rv3d.view_location = m @ Vector((2.0, 0.0, 1.2))
    rv3d.view_distance = 6.0
    rv3d.view_perspective = 'ORTHO'
    yield 0.4
    p0 = to_win(m @ Vector((1.003, 0.0, 2.098)))         # 1º canto em cima (raycast na parede)
    p1 = to_win(m @ Vector((1.797, 0.0, -0.003)))        # canto oposto no plano da face, rente ao piso
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_region('INVOKE_DEFAULT')
    yield 0.2
    yield from click(win, *p0)
    for k in range(1, 6):
        ev(win, 'MOUSEMOVE', 'NOTHING', p0[0] + (p1[0] - p0[0]) * k / 5, p0[1] + (p1[1] - p0[1]) * k / 5)
        yield 0.04
    yield from click(win, *p1)
    reg = ctx.window_manager.btm_wall_region
    w, h = reg.x1 - reg.x0, reg.z1 - reg.z0

    def on_grid(v):
        return abs(v / 0.01 - round(v / 0.01)) < 1e-4      # propriedade em float32

    # Com este zoom 1 pixel ≈ 10 mm: o canto fica na grade e perto do alvo; a exigência é a porta igual à região.
    check("dois cliques marcam ~800 × 2100 na grade, a partir do piso", reg.active and reg.wall == wall.name
          and abs(w - 0.8) <= 0.0101 and abs(h - 2.1) <= 0.0101 and abs(reg.z0) < 1e-9
          and all(on_grid(v) for v in (reg.x0, reg.x1, reg.z1)), f"{w:.4f} × {h:.4f} x0={reg.x0:.4f} {reg.side}")
    expected = (round(w, 6), round(h, 6), round(reg.x0, 6))
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob_doors_windows.place_door('INVOKE_DEFAULT')
    yield 0.3
    ev(win, 'RET', 'PRESS', *p1)
    ev(win, 'RET', 'RELEASE', *p1)
    yield 0.6
    doors = [o for o in scene.objects if o.get('IS_ENTRY_DOOR_BP')]
    got = [(round(hb_types.GeoNodeCage(d).get_input('Dim X'), 6), round(hb_types.GeoNodeCage(d).get_input('Dim Z'), 6),
            round(d.location.x, 6)) for d in doors]
    check("Enter põe a porta exata na região (nem um milímetro a mais)", got == [expected] and not reg.active,
          f"{got} região={expected}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_011_drag_probe: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
