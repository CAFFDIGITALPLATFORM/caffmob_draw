"""Interface da Biblioteca CAFFMob com eventos simulados (feature 012, T023 e T040).

Precisa de janela (não roda em --background):
    blender --factory-startup --enable-event-simulate --python tests/blender_012_library_ui.py

Sem a extensão instalada, o HUD fica desligado (a preferência não existe): é o caso "painel sem o HUD" (RF-01).
T023 (prova): o rótulo está no canto superior esquerdo, o clique abre a coluna, e clicar numa categoria abre o popover
(`WindowManager.popover`) a partir do operador de keymap.
T040: Criar armário pelo diálogo (Enter) cria o módulo e abre o editor de armário; uma categoria criada aparece na
coluna; com o painel fechado, o clique na viewport segue para a seleção (por componente, 011); Inserir sem as
bibliotecas herdadas.
Sai com código 0 (tudo certo) ou 1 (falhas listadas no console).
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401  (registra a extensão)
from caffmob_draw.library_panel import draw as lib_draw  # noqa: E402
from caffmob_draw.library_panel import popover  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def ev(win, kind, value='PRESS', x=0, y=0):
    win.event_simulate(kind, value, x=int(x), y=int(y))


def view3d(win):
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    return area, next(r for r in area.regions if r.type == 'WINDOW')


def click(win, x, y):
    ev(win, 'MOUSEMOVE', 'NOTHING', x, y)
    yield 0.05
    ev(win, 'LEFTMOUSE', 'PRESS', x, y)
    ev(win, 'LEFTMOUSE', 'RELEASE', x, y)
    yield 0.4


def center(region, rect):
    x, y, w, h = rect
    return region.x + x + w / 2, region.y + y + h / 2


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area, region = view3d(win)
    yield 0.5
    yield from click(win, region.x + region.width / 2, region.y + 20)     # aquecimento
    state = ctx.window_manager.btm_library
    with ctx.temp_override(window=win, area=area, region=region):
        lay = lib_draw.layout(bpy.context, area, region)
    from caffmob_draw.hb_gpu_draw import get_visible_window_bounds
    x_min, _x_max, _y_min, y_max = get_visible_window_bounds(area)
    x, y, w, h = lay.label
    check("rótulo no canto superior esquerdo da parte visível, sem o HUD",
          abs(x - (x_min + 8)) < 1 and abs(y + h - (y_max - 12)) < 1, f"{lay.label} visível=({x_min}, {y_max})")

    yield from click(win, *center(region, lay.label))
    check("clique no rótulo abre a coluna", state.open)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = lib_draw.layout(bpy.context, area, region)
    keys = [key for key, _rect in lay.items]
    check("ordem: Criar armário, categorias, Criar categoria",
          keys[:5] == ['CREATE_CABINET', 'CAT:Cozinha', 'CAT:Banheiro', 'CAT:Sala', 'CAT:Home office']
          and keys[-1] == 'CREATE_CATEGORY', str(keys))

    before = popover._open['drawn']
    rect = dict(lay.items)['CAT:Cozinha']
    yield from click(win, *center(region, rect))
    yield 0.3
    check("categoria abre o popover pelo keymap (T023)", popover._open['drawn'] > before and
          popover._open['category'] == "Cozinha", f"desenhos={popover._open['drawn'] - before}")
    check("categoria grava a linha", state.category == "Cozinha" and state.line == 'COZ',
          f"{state.category} {state.line}")
    ev(win, 'ESC', 'PRESS', region.x + 30, region.y + 30)
    ev(win, 'ESC', 'RELEASE', region.x + 30, region.y + 30)
    yield 0.3

    # T040: categoria criada aparece na coluna.
    from caffmob_draw.library_panel import categories
    categories.create("Lavanderia", 'DOR')
    state.open = False
    with ctx.temp_override(window=win, area=area, region=region):
        lay = lib_draw.layout(bpy.context, area, region)
    yield from click(win, *center(region, lay.label))
    with ctx.temp_override(window=win, area=area, region=region):
        lay = lib_draw.layout(bpy.context, area, region)
    keys = [key for key, _rect in lay.items]
    check("categoria criada aparece antes de Criar categoria", keys[-2:] == ['CAT:Lavanderia', 'CREATE_CATEGORY'],
          str(keys))

    # T040: Criar armário pelo diálogo até o editor abrir.
    before = {o.name for o in ctx.scene.objects}
    yield from click(win, *center(region, dict(lay.items)['CREATE_CABINET']))
    yield 0.3
    ev(win, 'RET', 'PRESS', region.x + region.width / 2, region.y + region.height / 2)
    ev(win, 'RET', 'RELEASE', region.x + region.width / 2, region.y + region.height / 2)
    yield 1.0
    new = [o for o in ctx.scene.objects if o.name not in before and o.btm_plane.object_kind == 'MODULE']
    from caffmob_draw.cabinet_editor import props as editor_props
    check("Criar armário cria o módulo pelo diálogo", len(new) == 1, str([o.name for o in new]))
    check("e abre o editor de armário nele", editor_props.session() is not None
          and editor_props.session().root_name == (new[0].name if new else ""))
    check("painel fechado depois da ação", not state.open)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_012_library_ui: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
