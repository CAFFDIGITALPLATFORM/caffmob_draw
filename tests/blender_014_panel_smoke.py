"""Fumaça com janela da BIBLIOTECA CAFFMOB maximizada (feature 014, T042; RN-09, RF-04, RF-09, RF-10, RF-15, RF-16).

Precisa de janela:
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_014_panel_smoke.py

Com eventos simulados pelo keymap da extensão:
- rótulo abre a coluna, o botão de maximizar abre o retângulo; solto, clique fora fecha;
- fixo, clique fora e Esc não fecham; arrastar o cabeçalho move, arrastar a borda redimensiona;
- com o HUD ligado, o retângulo gravado não cobre nenhum botão;
- ≥ 4 colunas numa região de 1.920 px; a roda rola a grade; abas, fabricantes e busca digitada filtram;
- fechar solta e minimiza.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw, grid_core, layout_core  # noqa: E402
from caffmob_draw.operators import viewport_hud  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def overlap(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    state = ctx.window_manager.btm_library
    ox, oy = region.x, region.y

    def ev(kind, value, x, y, **kw):
        win.event_simulate(kind, value, x=int(ox + x), y=int(oy + y), **kw)

    def click(x, y):
        ev('MOUSEMOVE', 'NOTHING', x, y)
        yield 0.05
        ev('LEFTMOUSE', 'PRESS', x, y)
        ev('LEFTMOUSE', 'RELEASE', x, y)
        yield 0.25

    def drag(x, y, dx, dy):
        ev('MOUSEMOVE', 'NOTHING', x, y)
        yield 0.05
        ev('LEFTMOUSE', 'PRESS', x, y)
        yield 0.05
        for i in range(1, 5):
            ev('MOUSEMOVE', 'NOTHING', x + dx * i / 4, y + dy * i / 4)
            yield 0.03
        ev('LEFTMOUSE', 'RELEASE', x + dx, y + dy)
        yield 0.25

    def mid(rect):
        return rect[0] + rect[2] / 2.0, rect[1] + rect[3] / 2.0

    def lay_max():
        with ctx.temp_override(window=win, area=area, region=region):
            return draw.max_layout(ctx, area)

    s = ctx.preferences.system.ui_scale
    yield 0.5
    ev('ESC', 'PRESS', region.width / 2, 20)                 # tela de abertura
    ev('ESC', 'RELEASE', region.width / 2, 20)
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    yield 0.3

    # MIN → OPEN → MAX
    state.mode, state.pinned, state.rect = 'MIN', False, (0, 0, 0, 0)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.layout(ctx, area, region)
    yield from click(*mid(lay.label))
    check("rótulo abre a coluna", state.mode == 'OPEN', state.mode)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.layout(ctx, area, region)
    yield from click(*mid(layout_core.maximize_button(lay, s)))
    check("botão de maximizar abre o retângulo", state.mode == 'MAX', state.mode)

    # solto: clique fora fecha
    rect = draw.max_rect(ctx, area)
    yield from click(min(region.width - 10, rect[0] + rect[2] + 40), max(10, rect[1] - 40))
    check("solto: clique fora fecha", state.mode == 'MIN', state.mode)

    # fixo
    state.mode = 'MAX'
    yield 0.2
    lay = lay_max()
    yield from click(*mid(dict(lay.buttons)['PIN']))
    check("botão fixar liga o painel fixo", state.pinned)
    yield from click(min(region.width - 10, lay.rect[0] + lay.rect[2] + 40), max(10, lay.rect[1] - 40))
    check("fixo: clique fora segue para a cena e não fecha", state.mode == 'MAX', state.mode)
    ev('ESC', 'PRESS', *mid(lay.grid))
    ev('ESC', 'RELEASE', *mid(lay.grid))
    yield 0.2
    check("fixo: Esc não fecha", state.mode == 'MAX', state.mode)

    # mover e redimensionar
    lay = lay_max()
    before = tuple(lay.rect)
    tx, ty = mid(lay.title)
    yield from drag(tx, ty, 60, -40)
    after = tuple(state.rect)
    check("arrastar o cabeçalho move", abs(after[0] - before[0] - 60) < 2 and abs(after[1] - before[1] + 40) < 2,
          f"{before} → {after}")
    x, y, w, h = after
    yield from drag(x + w - 2 * s, y + h / 2, 50, 0)
    resized = tuple(state.rect)
    check("arrastar a borda direita redimensiona", abs(resized[2] - (w + 50)) < 2 and abs(resized[0] - x) < 1,
          f"{after} → {resized}")
    yield from drag(x + w + 50 - 2 * s, y + h / 2, -400, 0)
    check("não estreita além do mínimo", abs(state.rect[2] - grid_core.MIN_W * s) < 1, str(tuple(state.rect)))

    # HUD ligado: o retângulo não cobre botão do HUD
    original = viewport_hud._hud_enabled
    viewport_hud._hud_enabled = lambda: True
    try:
        with ctx.temp_override(window=win, area=area, region=region):
            hud = viewport_hud.occupied_rects(ctx, area)
        lay = lay_max()
        tx, ty = mid(lay.title)
        yield from drag(tx, ty, 0, 400)                      # empurra para cima, em direção ao HUD
        stored = tuple(state.rect)
        drawn = draw.max_rect(ctx, area)
        check("com o HUD, nenhum botão coberto (gravado e desenhado)", hud and not any(overlap(stored, r) for r in hud)
              and not any(overlap(drawn, r) for r in hud), f"{stored} x {hud[:2]}")
    finally:
        viewport_hud._hud_enabled = original

    # colunas numa região de 1.920 px
    bounds = (0.0, 0.0, 1920.0, 1000.0)
    grid = grid_core.grid_area(grid_core.initial_rect(bounds, 1.0), 1.0)
    check("≥ 4 colunas numa região de 1.920 px (RF-09)", grid_core.columns(grid[2], 1.0) >= 4,
          str(grid_core.columns(grid[2], 1.0)))

    # rolagem
    state.manufacturer, state.collection, state.search, state.tab, state.scroll = "", "", "", 'TEXTURES', 0.0
    yield 0.2
    lay = lay_max()
    gx, gy = mid(lay.grid)
    ev('MOUSEMOVE', 'NOTHING', gx, gy)
    yield 0.05
    ev('WHEELDOWNMOUSE', 'PRESS', gx, gy)
    yield 0.2
    check("roda rola a grade", state.scroll > 0, str(state.scroll))
    ev('WHEELUPMOUSE', 'PRESS', gx, gy)
    yield 0.2
    check("roda para cima volta", state.scroll == 0.0, str(state.scroll))

    # fabricantes
    rows = layout_core.sidebar_rows(lay.sidebar, draw.texture_tree(), state.manufacturer, s)
    key, rect, _depth = rows[1]
    yield from click(*mid(rect))
    check("fabricante filtra a grade", state.manufacturer == key[4:], f"{state.manufacturer} {key}")
    count_man = len(draw.texture_items(state))

    # busca digitada
    lay = lay_max()
    yield from click(*mid(lay.search))
    for letter in "branco":
        ev(letter.upper(), 'PRESS', *mid(lay.grid), unicode=letter)
        ev(letter.upper(), 'RELEASE', *mid(lay.grid))
        yield 0.02
    yield 0.1
    check("busca digitada filtra ao vivo", state.search == "branco" and len(draw.texture_items(state)) < count_man,
          f"'{state.search}' {len(draw.texture_items(state))}/{count_man}")
    ev('BACK_SPACE', 'PRESS', *mid(lay.grid))
    ev('BACK_SPACE', 'RELEASE', *mid(lay.grid))
    yield 0.05
    check("Backspace apaga", state.search == "branc", state.search)
    ev('ESC', 'PRESS', *mid(lay.grid))
    ev('ESC', 'RELEASE', *mid(lay.grid))
    yield 0.1
    check("Esc desfaz a digitação desta vez", state.search == "" and not draw._search['active'], state.search)

    # abas
    lay = lay_max()
    yield from click(*mid(dict(lay.tabs)['BLOCKS']))
    check("aba Blocos", state.tab == 'BLOCKS', state.tab)
    lay = lay_max()
    yield from click(*mid(dict(lay.tabs)['TEXTURES']))

    # fechar
    lay = lay_max()
    yield from click(*mid(dict(lay.buttons)['CLOSE']))
    check("fechar minimiza e solta", state.mode == 'MIN' and not state.pinned, f"{state.mode} {state.pinned}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_014_panel_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.5)
