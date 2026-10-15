"""Desenho dos três estados da BIBLIOTECA CAFFMOB (feature 014, T028; RN-08, RN-09, design-direction.md).

Precisa de janela (contexto de GPU):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_014_library_draw.py

Para cada estado, captura a área da vista 3D (`screen.screenshot_area`) e confere pelos pixels:
- MIN: o rótulo tem a cor Noite (`style.SURFACE`) e nenhum retângulo grande aparece;
- OPEN: a coluna aparece abaixo do rótulo;
- MAX: placa Noite no meio do retângulo, cabeçalho `SURFACE_RAISED`, miniaturas reais desenhadas (pixels com cor de
  madeira), recorte da grade (o respiro abaixo da grade fica com a cor da placa, sem miniatura vazando) e nenhuma
  exceção no desenho;
- o desenho não grava no estado (o retângulo continua zerado).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401

from caffmob_draw.library_panel import draw, style, thumbs_gpu  # noqa: E402
from caffmob_draw.texture_library import catalog
from _mobi_texture_fixture import TextureServer

FAILURES = []
ERRORS = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


_original = {"max": draw._draw_max, "col": draw._draw_column}


def _guard(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:                      # o desenho engole a exceção no console; o teste registra
            ERRORS.append(repr(exc))
            traceback.print_exc()
            raise
    return wrapper


draw._draw_max = _guard(_original["max"])
draw._draw_column = _guard(_original["col"])


def capture(win, area):
    path = os.path.join(tempfile.mkdtemp(), "shot.png")
    with bpy.context.temp_override(window=win, area=area):
        bpy.ops.screen.screenshot_area(filepath=path)
    image = bpy.data.images.load(path)
    w, h = image.size
    pixels = np.empty(w * h * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    bpy.data.images.remove(image)
    return pixels.reshape(h, w, 4)


def near(px, color, tol=0.06):
    return all(abs(float(px[i]) - color[i]) <= tol for i in range(3))


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    ox, oy = region.x - area.x, region.y - area.y          # região → pixel da captura da área
    try:                                                    # fecha a tela de abertura (só com --enable-event-simulate)
        win.event_simulate('ESC', 'PRESS', x=region.x + 10, y=region.y + 10)
        win.event_simulate('ESC', 'RELEASE', x=region.x + 10, y=region.y + 10)
    except (RuntimeError, ValueError):
        pass
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    server = TextureServer()
    entries = server.connect()
    for entry in entries:
        thumb = catalog.thumb_entry(entry)
        server.download(thumb['id'], thumb)
    state = ctx.window_manager.btm_library

    def at(img, x, y):
        return img[int(oy + y), int(ox + x)]

    # MIN
    state.mode = 'MIN'
    area.tag_redraw()
    yield 0.5
    img = capture(win, area)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.layout(ctx, area, region)
    lx, ly, lw, lh = lay.label
    check("MIN: rótulo com a cor Noite", near(at(img, lx + lw - 8, ly + lh / 2), style.SURFACE),
          str(at(img, lx + lw - 8, ly + lh / 2)[:3]))
    check("MIN: sem coluna", not lay.items)

    # OPEN
    state.mode = 'OPEN'
    area.tag_redraw()
    yield 0.4
    img = capture(win, area)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.layout(ctx, area, region)
    rx, ry, rw, rh = lay.items[-1][1]
    check("OPEN: coluna desenhada abaixo do rótulo", len(lay.items) >= 3 and near(at(img, rx + rw - 6, ry + 4),
                                                                                    style.SURFACE),
          str(at(img, rx + rw - 6, ry + 4)[:3]))

    # MAX
    state.mode, state.manufacturer, state.collection, state.tab = 'MAX', "Fábrica de teste", "", 'TEXTURES'
    area.tag_redraw()
    for _ in range(80):                                     # o timer converte as miniaturas visíveis
        area.tag_redraw()
        yield 0.05
        if not thumbs_gpu.pending():
            break
    yield 0.3
    img = capture(win, area)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.max_layout(ctx, area)
    x, y, w, h = lay.rect
    hx, hy, hw, hh = lay.header
    check("MAX: cabeçalho com SURFACE_RAISED", near(at(img, hx + hw / 2 + 40, hy + 4), style.SURFACE_RAISED),
          str(at(img, hx + hw / 2 + 40, hy + 4)[:3]))
    sx, sy, sw, sh = lay.sidebar
    check("MAX: coluna de filtros com SURFACE_RAISED", near(at(img, sx + sw - 6, sy + 10), style.SURFACE_RAISED),
          str(at(img, sx + sw - 6, sy + 10)[:3]))
    gx, gy, gw, gh = lay.grid
    thumb = at(img, gx + 60, gy + gh - 60)                  # meio da primeira miniatura
    check("MAX: miniatura real desenhada (não é a cor da placa nem do fundo vazio)",
          not near(thumb, style.SURFACE) and not near(thumb, style.SURFACE_SUNKEN), str(thumb[:3]))
    below = at(img, gx + 60, gy - 4)                       # respiro abaixo da grade
    check("MAX: recorte da grade (nada vaza abaixo da área)", near(below, style.SURFACE), str(below[:3]))
    outside = [at(img, gx + 60 + dx, y - 6) for dx in range(0, 300, 20)]     # logo abaixo do painel: a cena
    check("MAX: nada da grade aparece abaixo do painel", not any(near(px, style.TEXT, 0.15) for px in outside),
          str([tuple(round(float(c), 2) for c in px[:3]) for px in outside[:3]]))
    check("MAX: retângulo dentro da região", x >= 0 and y >= 0 and x + w <= region.width and y + h <= region.height,
          str(lay.rect))
    check("o desenho não grava no estado", tuple(state.rect) == (0.0, 0.0, 0.0, 0.0), str(tuple(state.rect)))
    check("nenhuma exceção no desenho", not ERRORS, str(ERRORS[:2]))
    out = os.environ.get("BTM_SHOT_DIR")
    if out:
        os.makedirs(out, exist_ok=True)
        with ctx.temp_override(window=win, area=area):
            bpy.ops.screen.screenshot_area(filepath=os.path.join(out, "max.png"))
    state.mode = 'MIN'
    server.close()


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_014_library_draw: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.5)
