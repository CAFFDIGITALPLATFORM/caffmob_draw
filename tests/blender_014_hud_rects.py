"""Áreas ocupadas pelo plugin que a BIBLIOTECA CAFFMOB não cobre (feature 014, T029; RN-09, RF-16).

Precisa de janela (regiões da vista 3D):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_014_hud_rects.py

Confere `viewport_hud.occupied_rects` e o efeito em `draw.max_rect`:
- HUD ligado: os botões do HUD entram, e o retângulo maximizado posto em cima deles sai de cima;
- navegador de cenas fixado: o painel dele entra;
- aviso de medidas visível: o retângulo do aviso entra, e o maximizado posto sobre ele sai de cima;
- HUD desligado e sem aviso: nada é reservado.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401

from caffmob_draw.library_panel import draw  # noqa: E402
from caffmob_draw.operators import scene_navigator, viewport_hud  # noqa: E402
from caffmob_draw.overlays import element_toast  # noqa: E402

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
    yield 0.3

    def rects():
        with ctx.temp_override(window=win, area=area, region=region):
            return viewport_hud.occupied_rects(ctx, area)

    def maximized(at):
        state.rect = at
        with ctx.temp_override(window=win, area=area, region=region):
            return draw.max_rect(ctx, area, state)

    # HUD desligado, sem aviso
    original = viewport_hud._hud_enabled
    viewport_hud._hud_enabled = lambda: False
    bpy.ops.object.select_all(action='DESELECT')
    check("HUD desligado e sem aviso: nada reservado", rects() == [], str(rects()))

    # HUD ligado: botões
    viewport_hud._hud_enabled = lambda: True
    hud = rects()
    check("HUD ligado: os botões entram", len(hud) >= 1, str(hud))
    if hud:
        bx, by, bw, bh = hud[0]
        got = maximized((bx - 20, by - 300, 640, 360))           # em cima do primeiro botão
        check("MAX posto sobre o HUD sai de cima de todos os botões", not any(overlap(got, r) for r in hud),
              f"{got} x {hud}")

    # navegador fixado
    scene_navigator.set_pinned(True)
    try:
        pinned = rects()
        check("navegador fixado: o painel entra", len(pinned) == len(hud) + 1, f"{len(pinned)} x {len(hud)}")
    finally:
        scene_navigator.set_pinned(False)

    # aviso de medidas (a caixa do aviso só aparece com um elemento que tem medida)
    viewport_hud._hud_enabled = lambda: False
    bpy.ops.mesh.primitive_cube_add()
    obj = ctx.active_object
    obj.select_set(True)
    element_toast.show(obj)
    if element_toast.message(obj):
        toast = rects()
        check("aviso visível: o retângulo do aviso entra", len(toast) == 1, str(toast))
        if toast:
            tx, ty, tw, th = toast[0]
            got = maximized((tx, 0, 640, 360))
            check("MAX posto sobre o aviso sai de cima dele", not overlap(got, toast[0]), f"{got} x {toast[0]}")
    else:
        print("aviso sem medida para um cubo comum: caso do retângulo pulado", flush=True)
        check("sem aviso: nada reservado", rects() == [], str(rects()))
    element_toast._state['shown_at'] = 0.0
    check("aviso vencido: some da lista", rects() == [], str(rects()))
    viewport_hud._hud_enabled = original
    state.rect = (0.0, 0.0, 0.0, 0.0)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_014_hud_rects: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.5)
