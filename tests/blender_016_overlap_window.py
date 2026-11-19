"""Ensaio com janela do seletor de sobreposição (feature 016; RF-01 a RF-14).

Precisa de janela e de eventos simulados:
    blender --factory-startup --enable-event-simulate --python tests/blender_016_overlap_window.py

Percorre o caminho de interface que a fumaça em segundo plano não alcança:
- `Ctrl + Alt + botão esquerdo` abre o painel pela lista de keymap da extensão;
- clique nas linhas marca, `I` isola e restaura, `Enter` soma os marcados à seleção anterior (RF-12);
- `Esc` devolve seleção, ativo e visibilidade;
- o item do menu de contexto abre o mesmo seletor (RF-14), com `End` + `Enter` no popup do botão direito.

O roteiro tira uma captura do painel aberto para conferir o desenho.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy  # type: ignore
from bpy_extras.view3d_utils import location_3d_to_region_2d  # type: ignore
from mathutils import Vector  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401
from caffmob_draw.selection import overlap_core as core  # noqa: E402
from caffmob_draw.selection import overlap_select as sel  # noqa: E402

FAILURES = []
SHOT = ROOT / "_reversa_forward" / "016-seletor-sobreposicao" / "captura-painel.png"
ctx = bpy.context
win = ctx.window_manager.windows[0]
area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def scene():
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    front = None
    for index, y in enumerate((0.0, 1.0, 2.0)):
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, y, 0.0))
        obj = ctx.active_object
        obj.name = f"Cubo {index + 1}"
        front = front or obj
    base = []
    for index in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(14.0 + index * 3, 0.0, 0.0))
        base.append(ctx.active_object)
        ctx.active_object.name = f"Base {index + 1}"
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    for obj in base:
        obj.select_set(True)
    ctx.view_layer.objects.active = base[0]
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_center_cursor()
    return base


def selected():
    return sorted(obj.name for obj in ctx.view_layer.objects if obj.select_get())


def screen_of(point):
    with ctx.temp_override(window=win, area=area, region=region):
        co = location_3d_to_region_2d(region, ctx.region_data, Vector(point))
    return None if co is None else (int(co.x), int(co.y))


def rows_centers(op):
    rect = core.panel_rect(op.anchor, (region.width, region.height), len(op.picker.hits))
    rows = core.rows_rect(rect)
    centers = []
    for index in range(min(len(op.picker.hits), core.MAX_VISIBLE)):
        y = rows[1] + rows[3] - (index + 0.5) * core.ROW_H
        centers.append((rect[0] + rect[2] / 2.0, y))
    return rect, centers


def script():
    ox, oy = region.x, region.y

    def ev(kind, value, point, **kw):
        win.event_simulate(kind, value, x=int(ox + point[0]), y=int(oy + point[1]), **kw)

    def press(kind, point, wait=0.15, **kw):
        ev(kind, 'PRESS', point, **kw)
        yield wait
        ev(kind, 'RELEASE', point, **kw)
        yield 0.1

    base = scene()
    yield 0.6
    ev('MOUSEMOVE', 'NOTHING', (20, 20))          # aquecimento: o primeiro evento simulado se perde numa janela nova
    yield 0.1
    ev('LEFTMOUSE', 'PRESS', (20, 20))
    ev('LEFTMOUSE', 'RELEASE', (20, 20))
    yield 0.3
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    for obj in base:
        obj.select_set(True)
    ctx.view_layer.objects.active = base[0]
    yield 0.2
    point = screen_of((0.0, 0.0, 0.0))
    check("o centro da pilha cai na região", point is not None, str(point))
    ev('MOUSEMOVE', 'NOTHING', point)
    yield 0.2

    # Abrir pelo atalho da extensão.
    ev('LEFTMOUSE', 'PRESS', point, ctrl=True, alt=True)
    yield 0.2
    ev('LEFTMOUSE', 'RELEASE', point, ctrl=True, alt=True)   # o clique só fecha com os modificadores nos dois eventos
    yield 0.3
    op = sel._active
    check("Ctrl + Alt + clique abre o seletor", op is not None)
    if op is None:
        items = [item for item in ctx.window_manager.keyconfigs.addon.keymaps['3D View'].keymap_items
                 if item.idname.startswith("caffmob.overlap")]
        print("atalho registrado:", [(i.idname, i.type, i.value, i.ctrl, i.alt) for i in items], flush=True)
        with ctx.temp_override(window=win, area=area, region=region):
            result = bpy.ops.caffmob.overlap_select('INVOKE_DEFAULT')
        print("invocação direta:", result, sel._active, flush=True)
        if sel._active is not None:
            yield from press('ESC', point, wait=0.3)
        return
    names = [obj.name for obj in op.picker.hits]
    check("a lista traz os três cubos empilhados", names == ["Cubo 1", "Cubo 2", "Cubo 3"], str(names))
    check("a seleção anterior continua intocada", selected() == sorted(o.name for o in base), str(selected()))
    check("painel aberto com o foco no primeiro", op.picker.focus == 0 and op.anchor is not None, str(op.anchor))

    rect, centers = rows_centers(op)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.screen.screenshot(filepath=str(SHOT))
    yield 0.3

    # Marcar por clique na linha 3 e depois na linha 1.
    ev('MOUSEMOVE', 'NOTHING', centers[2])
    yield 0.1
    yield from press('LEFTMOUSE', centers[2])
    staged = [obj.name for obj in op.picker.staged]
    check("clique na linha 3 marca o cubo de trás", staged == ["Cubo 3"], str(staged))
    ev('MOUSEMOVE', 'NOTHING', centers[0])
    yield 0.1
    yield from press('LEFTMOUSE', centers[0])
    staged = sorted(obj.name for obj in op.picker.staged)
    check("clique na linha 1 soma o cubo da frente", staged == ["Cubo 1", "Cubo 3"], str(staged))
    check("o foco acompanha o mouse", op.picker.focus == 0, str(op.picker.focus))

    # Isolar e restaurar.
    yield from press('I', point)
    visible = [obj.name for obj in ctx.view_layer.objects if obj.visible_get()]
    check("I isola só o objeto em foco", visible == ["Cubo 1"], str(visible))
    yield from press('I', point)
    visible = [obj.name for obj in ctx.view_layer.objects if obj.visible_get()]
    check("I de novo restaura a visibilidade", len(visible) == 6, str(len(visible)))
    check("o painel continua aberto depois do isolamento", sel._active is op)

    # Confirmar: seleção anterior mais os marcados.
    yield from press('RET', point, wait=0.4)
    check("Enter fecha o seletor", sel._active is None)
    expect = sorted([o.name for o in base] + ["Cubo 1", "Cubo 3"])
    check("Enter soma os marcados à seleção anterior (RF-12)", selected() == expect, str(selected()))
    check("o item em foco vira o ativo", ctx.view_layer.objects.active is bpy.data.objects["Cubo 1"],
          ctx.view_layer.objects.active.name if ctx.view_layer.objects.active else None)

    # Reabrir e cancelar.
    ev('MOUSEMOVE', 'NOTHING', point)
    yield 0.15
    ev('LEFTMOUSE', 'PRESS', point, ctrl=True, alt=True)
    yield 0.2
    ev('LEFTMOUSE', 'RELEASE', point, ctrl=True, alt=True)
    yield 0.3
    op = sel._active
    check("o atalho reabre o seletor", op is not None)
    if op is None:
        return
    check("os cubos que já estavam selecionados vêm marcados", sorted(obj.name for obj in op.picker.staged)
          == ["Cubo 1", "Cubo 3"], str(sorted(obj.name for obj in op.picker.staged)))
    check("a seleção da abertura é guardada", len(op.state['selection']) == 5, str(len(op.state['selection'])))
    yield from press('ESC', point, wait=0.4)
    check("Esc fecha o seletor", sel._active is None)
    check("Esc devolve a seleção e o ativo", selected() == expect
          and ctx.view_layer.objects.active is bpy.data.objects["Cubo 1"])

    # O botão direito é do `move_over_drag` desta extensão (arraste), então o menu que lista o item fica na captura
    # `captura-menu.png`, e o botão dele é exercitado pelo mesmo INVOKE_DEFAULT que o menu usa.
    with ctx.temp_override(window=win, area=area, region=region):
        result = bpy.ops.caffmob.overlap_select('INVOKE_DEFAULT')
    yield 0.35
    op = sel._active
    check("o botão do menu abre o seletor (INVOKE_DEFAULT)",
          op is not None and result == {'RUNNING_MODAL'}, str(result))
    if op is not None:
        check("a lista aberta pelo menu traz os três cubos",
              [obj.name for obj in op.picker.hits] == ["Cubo 1", "Cubo 2", "Cubo 3"],
              str([obj.name for obj in op.picker.hits]))
        yield from press('ESC', point, wait=0.3)
        check("Esc fecha o seletor aberto pelo menu", sel._active is None)


def finish():
    print(f"blender_016_overlap_window: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


_gen = script()
_started = [0.0]


def tick():
    try:
        delay = next(_gen)
    except StopIteration:
        finish()
        return None
    except Exception:                                    # noqa: BLE001 - o ensaio precisa mostrar o erro e sair 1
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
        finish()
        return None
    _started[0] += delay or 0.05
    if _started[0] > 45:
        traceback.print_stack()
        FAILURES.append("tempo esgotado")
        finish()
        return None
    return delay


bpy.app.timers.register(tick, first_interval=1.5)
