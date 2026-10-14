import os, sys, tempfile, traceback
import bpy, numpy as np
sys.path.insert(0, "/home/theleoinfo/www/BlenderToMob/tests")
import _blender_env  # noqa
from caffmob_draw.library_panel import draw, grid_core

def capture(win, area):
    path = os.path.join(tempfile.mkdtemp(), "s.png")
    with bpy.context.temp_override(window=win, area=area):
        bpy.ops.screen.screenshot_area(filepath=path)
    img = bpy.data.images.load(path); w, h = img.size
    px = np.empty(w*h*4, dtype=np.float32); img.pixels.foreach_get(px); bpy.data.images.remove(img)
    return px.reshape(h, w, 4)

def script():
    ctx = bpy.context; win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    ox, oy = region.x - area.x, region.y - area.y
    win.event_simulate('ESC', 'PRESS', x=region.x+10, y=region.y+10); win.event_simulate('ESC', 'RELEASE', x=region.x+10, y=region.y+10)
    for o in list(ctx.scene.objects): bpy.data.objects.remove(o, do_unlink=True)
    st = ctx.window_manager.btm_library
    st.mode, st.tab, st.category, st.search, st.scroll = 'MAX', 'BLOCKS', 'Cozinha', '', 0.0
    st.rect = (8.0, 8.0, region.width - 16.0, region.height - 16.0)
    for _ in range(6): area.tag_redraw(); yield 0.1
    img = capture(win, area)
    with ctx.temp_override(window=win, area=area, region=region):
        lay = draw.max_layout(ctx, area)
    entries = draw.grid_entries(st); s = ctx.preferences.system.ui_scale
    cells = dict(grid_core.visible_cells(lay.grid, len(entries), s, 0.0))
    side = int(140*s); crops = {}
    for i, e in enumerate(entries):
        if e["kind"] != 'MODEL' or i not in cells: continue
        x, y, w, h = cells[i]; ty = int(y + h - side)
        crops[e["id"]] = img[int(oy+ty)+4:int(oy+ty)+side-4, int(ox+x)+4:int(ox+x)+side-4, :3]
    ids = list(crops); same = [(a, b) for k, a in enumerate(ids) for b in ids[k+1:] if np.allclose(crops[a], crops[b], atol=0.02)]
    print("REPRO modelos", ids, flush=True)
    print("REPRO pares_iguais", len(same), "de", len(ids)*(len(ids)-1)//2, same[:3], flush=True)

g = script()
def tick():
    try: return next(g)
    except StopIteration: pass
    except Exception: traceback.print_exc()
    os._exit(0)
bpy.app.timers.register(tick, first_interval=1.5)
