"""Ensaio do guarda de colisão no G de verdade (feature 066, T010; a partir do protótipo T003; RF-001 a RF-008).

Precisa de janela (em --background sai sem testar nada):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_066_guard_translate.py

Com o add-on registrado (`_blender_env`), o guarda real (`collision/guard.py`) limita o G modal (G, eixo, digitar,
Enter/Esc), sem nenhum handler de teste:
- digitar 2 m contra uma chapa de 15 mm para encostado nela, mesmo com o destino do outro lado (RF-001, RF-004);
- cubo novo, sem cadastro nenhum, bloqueia (RF-002);
- Desfazer volta à origem; Refazer volta à pose limitada; Esc volta à pose de antes do gesto (RF-008);
- falha segura: com o cálculo quebrado à força, a pose fica na última válida;
- silêncio: nenhuma ocorrência gravada e nada na barra de status (RF-021).
"""
import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import guard  # noqa: E402
from caffmob_draw.ui import save_feedback  # noqa: E402

WALL_X = 1.0          # face esquerda da chapa
HALF = 0.5            # meia aresta do cubo móvel
FAILURES = []
_status = []
_TEXT = {'TWO': '2', 'ONE': '1', 'MINUS': '-'}


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def _scene():
    env.clean_scene()
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
    mover = bpy.context.object
    mover.name = 'Movel'
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(WALL_X + 0.0075, 0.0, 0.0))
    wall = bpy.context.object
    wall.name = 'Chapa'
    wall.scale = (0.015, 2.0, 2.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 1.6, 0.0))      # cubo novo, sem cadastro
    bpy.context.object.name = 'Cubo novo'
    bpy.ops.object.select_all(action='DESELECT')
    mover.select_set(True)
    bpy.context.view_layer.objects.active = mover


def _loc():
    return bpy.context.scene.objects['Movel'].location


def _key(win, key, x, y):
    text = _TEXT.get(key)
    if text:
        win.event_simulate(key, 'PRESS', x=x, y=y, unicode=text)
    else:
        win.event_simulate(key, 'PRESS', x=x, y=y)
    win.event_simulate(key, 'RELEASE', x=x, y=y)


def _gesture(win, x, y, keys):
    """G e as teclas seguintes, com uma pausa entre elas para o modal do transform consumi-las."""
    win.event_simulate('MOUSEMOVE', 'NOTHING', x=x, y=y)
    yield 0.2
    for key in ('G',) + tuple(keys):
        _key(win, key, x, y)
        yield 0.3
    yield 1.0


def _spy_status():
    show = save_feedback.show

    def spy(text):
        _status.append(text)
        show(text)
    save_feedback.show = spy


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    _key(win, 'ESC', 10, 10)       # fecha a tela de boas-vindas
    yield 0.3
    _spy_status()
    _scene()
    bpy.ops.ed.undo_push(message="cena pronta")
    yield 0.5
    cx, cy = region.x + region.width // 2, region.y + region.height // 2
    yield from _gesture(win, cx, cy, ('X', 'TWO', 'RET'))
    check("RF-004: G X 2 Enter para encostado na chapa de 15 mm", abs(_loc().x - (WALL_X - HALF)) < 1e-4,
          f"x={_loc().x:.4f}")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield 0.8
    check("RF-008: Desfazer volta à origem", abs(_loc().x) < 1e-6, f"x={_loc().x:.4f}")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.redo()
    yield 0.8
    check("RF-008: Refazer volta à pose sem penetração", abs(_loc().x - (WALL_X - HALF)) < 1e-4, f"x={_loc().x:.4f}")
    yield from _gesture(win, cx, cy, ('X', 'MINUS', 'ONE', 'ESC'))
    check("RF-008: Esc volta à pose de antes do gesto", abs(_loc().x - (WALL_X - HALF)) < 1e-4, f"x={_loc().x:.4f}")
    yield from _gesture(win, cx, cy, ('Y', 'TWO', 'RET'))
    # O cubo novo (centro y = 1,6) tem a face em y = 1,1: o móvel para com a face dele ali (y = 0,6).
    check("RF-002: cubo novo sem cadastro bloqueia", abs(_loc().y - 0.6) < 1e-4, f"y={_loc().y:.4f}")
    real = guard._resolve_translation

    def broken(*_args, **_kwargs):
        raise RuntimeError("falha forçada pelo ensaio")
    guard._resolve_translation = broken
    before = _loc().copy()
    yield from _gesture(win, cx, cy, ('Z', 'ONE', 'RET'))
    guard._resolve_translation = real
    check("Falha segura: erro no cálculo mantém a última pose válida", (_loc() - before).length < 1e-6,
          f"{tuple(round(v, 4) for v in _loc())}")
    drawing = [p.name for p in (Path(__file__).resolve().parents[1] / "caffmob_draw" / "collision").glob("*.py")
               if 'draw_handler_add' in p.read_text()]
    check("RF-021: zero handler de desenho de colisão", not drawing, str(drawing))
    state = ctx.window_manager.btm_collision
    check("RF-021: nenhuma ocorrência gravada e nada na barra de status", not state.items and not _status,
          f"ocorrências={len(state.items)} status={_status}")


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_066_guard_translate: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


if bpy.app.background:
    print("blender_066_guard_translate: precisa de janela (xvfb-run); nada testado em --background")
else:
    bpy.app.timers.register(tick, first_interval=2.0)
