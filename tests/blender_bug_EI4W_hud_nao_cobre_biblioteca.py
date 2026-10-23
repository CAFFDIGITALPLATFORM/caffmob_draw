"""Reprodução e regressão de BUG-20261023-EI4W (#155): numa vista estreita, a fileira de botões do HUD (Abrir Portas e
Gavetas, Mover Sobre, Seleção por componente) não fica embaixo do rótulo BIBLIOTECA CAFFMOB; numa vista larga, continua
centralizada.

Precisa de janela (xvfb-run). Roda duas vezes, com a janela estreita e com a larga:
    xvfb-run -a -s "-screen 0 900x700x24" blender --factory-startup --enable-event-simulate --window-geometry 0 0 900 700 --python tests/blender_bug_EI4W_hud_nao_cobre_biblioteca.py
Em --background não há janela: o roteiro avisa e sai sem testar.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.hb_gpu_draw import get_visible_window_bounds  # noqa: E402
from caffmob_draw.library_panel import draw as library  # noqa: E402
from caffmob_draw.operators import viewport_hud as hud  # noqa: E402

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
    win.event_simulate('ESC', 'PRESS', x=region.x + 10, y=region.y + 10)
    win.event_simulate('ESC', 'RELEASE', x=region.x + 10, y=region.y + 10)
    yield 0.3
    hud._hud_enabled = lambda: True                 # a preferência do HUD ligada, como no Blender do titular
    ctx.window_manager.btm_library.mode = 'MIN'
    with ctx.temp_override(window=win, area=area, region=region):
        rows = [(type(w).__name__, r) for w, r in hud.compute_layout(ctx, area)]
        label = library.layout(ctx, area, region).label
    print("REGIÃO", region.width, "RÓTULO", tuple(round(v) for v in label), flush=True)
    bad = [(name, tuple(round(v) for v in r)) for name, r in rows if overlap(r, label)]
    check("reprodução: nenhum botão do HUD embaixo do rótulo da Biblioteca", not bad, bad)
    x_min, x_max, _y0, _y1 = get_visible_window_bounds(area)
    centered = [r for name, r in rows if name != '_NavButton']
    if centered and x_max - x_min > 1400:
        first = [r for r in centered if r[1] == centered[0][1]]
        mid = (min(r[0] for r in first) + max(r[0] + r[2] for r in first)) / 2
        check("regressão: na vista larga a fileira continua centralizada", abs(mid - (x_min + x_max) / 2) < 2,
              (mid, (x_min + x_max) / 2))
    inside = all(r[0] + r[2] <= x_max + 1 for _n, r in rows)
    check("os botões não saem da vista", inside, [(n, tuple(round(v) for v in r)) for n, r in rows])


if bpy.app.background:
    print("blender_bug_EI4W: precisa de janela (xvfb-run); nada testado em --background", flush=True)
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
