"""Fumaça com janela do arraste da BIBLIOTECA CAFFMOB (feature 014, T043; RN-10, D-07).

Precisa de janela:
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_014_drag_smoke.py

Com uma textura baixada do servidor falso local do MOBI e um armário CAFFMob no meio da vista:
- textura sobre a porta: só a frente muda; sobre o tampo da caixa: só a caixa muda;
- no vazio: aviso, nada muda; Esc no meio do arraste: nada muda; voltar para o painel: nada muda;
- modelo pronto (aba Blocos) até o piso: insere um módulo e um Ctrl+Z o remove.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras import view3d_utils
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _blender_env  # noqa: E402,F401
from caffmob_draw.library_panel import draw, grid_core, ops_drag  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402
from caffmob_draw.texture_library import catalog, downloads  # noqa: E402

FAILURES = []
from fake_texture_server import IDS
from _mobi_texture_fixture import TextureServer
TID = IDS[0]


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def mats(obj):
    return tuple(m.name if m else "" for m in obj.data.materials)


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    rv3d = area.spaces.active.region_3d
    state = ctx.window_manager.btm_library
    ox, oy = region.x, region.y

    def ev(kind, value, x, y, **kw):
        win.event_simulate(kind, value, x=int(ox + x), y=int(oy + y), **kw)

    def drag(x0, y0, x1, y1, release=True):
        ev('MOUSEMOVE', 'NOTHING', x0, y0)
        yield 0.05
        ev('LEFTMOUSE', 'PRESS', x0, y0)
        yield 0.05
        for i in range(1, 9):
            ev('MOUSEMOVE', 'NOTHING', x0 + (x1 - x0) * i / 8, y0 + (y1 - y0) * i / 8)
            yield 0.03
        if release:
            ev('LEFTMOUSE', 'RELEASE', x1, y1)
        yield 0.4

    def screen(point):
        p = view3d_utils.location_3d_to_region_2d(region, rv3d, point)
        return (p.x, p.y)

    yield 0.5
    ev('ESC', 'PRESS', region.width / 2, 20)
    ev('ESC', 'RELEASE', region.width / 2, 20)
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    server = TextureServer()
    server.connect()
    server.download(TID)

    from mathutils import Euler
    import math
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.cabinet_builder(cabinet_type='BASE', width=0.6, line='COZ')
        root = ctx.view_layer.objects.active
        rv3d.view_perspective = 'PERSP'
        rv3d.view_rotation = Euler((math.radians(62), 0.0, math.radians(20))).to_quaternion()
        rv3d.view_location = (-0.2, 0.0, 0.4)              # o armário fica à direita, longe do painel
        rv3d.view_distance = 2.4
        bpy.ops.ed.undo_push(message="cena do teste")
    yield 0.4
    door = next(o for o in root.children_recursive if classify.classify(o).kind == classify.FRONT)

    # Painel no canto, aba Texturas, filtrado até a textura
    state.mode, state.pinned, state.tab = 'MAX', True, 'TEXTURES'
    state.manufacturer, state.collection, state.search, state.scroll = "arauco", "colecao-realce", "anis", 0.0
    state.rect = (8.0, region.height - 340.0, 560.0, 300.0)
    yield 0.3

    def cell_center():
        with ctx.temp_override(window=win, area=area, region=region):
            lay = draw.max_layout(ctx, area)
        entries = draw.grid_entries(state)
        cells = grid_core.visible_cells(lay.grid, len(entries), ctx.preferences.system.ui_scale, 0.0)
        index = next(i for i, e in enumerate(entries) if draw.entry_key(e) == TID)
        x, y, w, h = dict(cells)[index]
        return x + w / 2, y + h - w / 2

    def find_point(target, want_top=False):
        """Ponto da região cujo ray-cast acerta `target` (no tampo, se pedido), fora do painel."""
        panel = draw.max_rect(ctx, area)
        corners = [screen(target.matrix_world @ Vector(c)) for c in target.bound_box]
        xs, ys = [c[0] for c in corners], [c[1] for c in corners]
        top = max((target.matrix_world @ Vector(c)).z for c in target.bound_box)
        hits = []
        for i in range(1, 16):
            for j in range(1, 16):
                x = int(min(xs) + (max(xs) - min(xs)) * i / 16)
                y = int(min(ys) + (max(ys) - min(ys)) * j / 16)
                if ops_drag._inside(panel, x, y):
                    continue
                with ctx.temp_override(window=win, area=area, region=region):
                    obj, loc = ops_drag.ray_hit(ctx, x, y)
                if obj is target and (not want_top or loc.z > top - 0.003):
                    hits.append((x, y))
        if not hits:
            raise AssertionError(f"nenhum ponto acerta {target.name}")
        return hits[len(hits) // 2]                         # longe das bordas

    def door_point():
        return find_point(door)

    def top_point():
        return find_point(root, want_top=True)

    door_before, root_before = mats(door), mats(root)
    cx, cy = cell_center()
    yield from drag(cx, cy, *door_point())
    check("textura sobre a porta: a porta muda", mats(door) != door_before and any("anis" in m for m in mats(door)),
          str(mats(door)))
    check("textura sobre a porta: a caixa não muda", mats(root) == root_before, str(mats(root)))

    door_now = mats(door)
    yield from drag(cx, cy, *top_point())
    check("textura sobre o tampo: a caixa muda", any("anis" in m for m in mats(root)), str(mats(root)))
    check("textura sobre o tampo: a porta não muda", mats(door) == door_now)

    snapshot = (mats(door), mats(root))
    yield from drag(cx, cy, region.width - 20, 20)
    check("no vazio: nada muda", (mats(door), mats(root)) == snapshot)

    yield from drag(cx, cy, *door_point(), release=False)
    ev('ESC', 'PRESS', *door_point())
    ev('ESC', 'RELEASE', *door_point())
    yield 0.1
    ev('LEFTMOUSE', 'RELEASE', *door_point())
    yield 0.3
    check("Esc no meio do arraste: nada muda", (mats(door), mats(root)) == snapshot)

    yield from drag(cx, cy, cx + 40, cy - 30)
    check("solto de volta no painel: nada muda", (mats(door), mats(root)) == snapshot)
    check("o painel fixo continua aberto", state.mode == 'MAX')

    # Bloco: modelo pronto até o piso
    state.tab, state.category, state.search = 'BLOCKS', "Cozinha", ""
    yield 0.3
    entries = draw.grid_entries(state)
    model = next(e for e in entries if e["kind"] == 'MODEL')
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.max_layout(ctx, area)
    cells = grid_core.visible_cells(lay.grid, len(entries), ctx.preferences.system.ui_scale, 0.0)
    x, y, w, h = dict(cells)[entries.index(model)]
    modules = lambda: [o for o in ctx.scene.objects if o.get('btm_plane') is not None or  # noqa: E731
                       classify.module_library(o)]
    before = len(modules())
    floor_point = screen(Vector((1.2, 0.0, 0.0)))
    yield from drag(x + w / 2, y + h - w / 2, *floor_point)
    added = [o for o in modules() if o is not root]
    check("modelo pronto até o piso: insere um módulo", len(modules()) == before + 1, f"{before} → {len(modules())}")
    if added:
        spot = added[-1].location
        check("inserido no ponto sob o mouse", abs(spot.x - 1.2) < 0.15 and abs(spot.y) < 0.15 and abs(spot.z) < 1e-6,
              str(tuple(round(v, 3) for v in spot)))
    ev('Z', 'PRESS', region.width / 2, region.height / 2, ctrl=True)
    ev('Z', 'RELEASE', region.width / 2, region.height / 2, ctrl=True)
    yield 0.6
    check("um Ctrl+Z remove a inserção", len(modules()) == before, f"{len(modules())}")
    state.mode, state.pinned = 'MIN', False
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
    print(f"blender_014_drag_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=1.5)
