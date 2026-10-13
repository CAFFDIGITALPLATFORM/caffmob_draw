"""Prova D-07 (feature 014, T002): arrastar de um retângulo desenhado para a cena.

Precisa de janela (não roda em --background):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_014_drag_probe.py

Dois casos com eventos simulados (`Window.event_simulate`):
1. **Textura:** um modal começa no PRESS dentro do retângulo, segue o MOUSEMOVE e, no RELEASE sobre um cubo, faz o
   ray-cast e "aplica" (troca a cor do objeto). Confere a sequência de eventos e o objeto atingido.
2. **Bloco:** o mesmo modal, ao sair do retângulo com o botão ainda apertado, chama um segundo operador modal em
   `INVOKE_DEFAULT` (no papel da inserção que segue o mouse) e termina. Confere se o segundo modal recebe os
   MOUSEMOVE seguintes e o RELEASE do mesmo botão.
Imprime `PROVA_D07 {...}` e sai com 0 se os dois casos funcionarem.
"""

import os
import traceback

import bpy
from bpy_extras import view3d_utils

RECT = (40, 40, 160, 120)                  # x, y, largura, altura em px da região
REPORT = {"textura": {}, "bloco": {}}
EVENTS = {"drag": [], "insert": []}


def inside(x, y):
    rx, ry, rw, rh = RECT
    return rx <= x <= rx + rw and ry <= y <= ry + rh


class PROBE_OT_insert(bpy.types.Operator):
    """No papel da inserção existente: segue o mouse e confirma no RELEASE."""
    bl_idname = "probe014.insert"
    bl_label = "Prova inserção"

    def invoke(self, context, event):
        EVENTS["insert"].append(("INVOKE", event.type, event.value))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'MOUSEMOVE', 'LEFTMOUSE', 'ESC'}:
            EVENTS["insert"].append((event.type, event.value, event.mouse_region_x, event.mouse_region_y))
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return {'FINISHED'}
        if event.type == 'ESC':
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


class PROBE_OT_drag(bpy.types.Operator):
    """Arraste que nasce no retângulo."""
    bl_idname = "probe014.drag"
    bl_label = "Prova arraste"
    kind: bpy.props.StringProperty(default='TEXTURE')  # type: ignore

    def invoke(self, context, event):
        EVENTS["drag"].append(("INVOKE", event.type, event.value, event.mouse_region_x, event.mouse_region_y))
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type in {'MOUSEMOVE', 'LEFTMOUSE'}:
            EVENTS["drag"].append((event.type, event.value, event.mouse_region_x, event.mouse_region_y))
        if self.kind == 'BLOCK' and event.type == 'MOUSEMOVE' and not inside(event.mouse_region_x, event.mouse_region_y):
            bpy.ops.probe014.insert('INVOKE_DEFAULT')
            return {'FINISHED'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            region, rv3d = context.region, context.region_data
            coord = (event.mouse_region_x, event.mouse_region_y)
            origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)
            direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
            hit, _loc, _n, _i, obj, _m = context.scene.ray_cast(context.evaluated_depsgraph_get(), origin, direction)
            REPORT["textura"]["atingido"] = obj.name if hit else None
            if hit:
                obj.color = (1.0, 0.0, 0.0, 1.0)
            return {'FINISHED'}
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            return {'CANCELLED'}
        return {'RUNNING_MODAL'}


def ev(win, kind, value, x, y):
    win.event_simulate(kind, value, x=int(x), y=int(y))


def script():
    ctx = bpy.context
    for cls in (PROBE_OT_insert, PROBE_OT_drag):
        bpy.utils.register_class(cls)
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    rv3d = area.spaces.active.region_3d
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    cube = ctx.active_object
    cube.color = (1, 1, 1, 1)
    rv3d.view_location = (0, 0, 0)
    rv3d.view_distance = 6.0
    yield 0.5
    center = view3d_utils.location_3d_to_region_2d(region, rv3d, (0, 0, 0))
    start = (region.x + RECT[0] + 20, region.y + RECT[1] + 20)
    ev(win, 'MOUSEMOVE', 'NOTHING', *start)                       # aquecimento
    yield 0.2

    # Caso 1: textura
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.probe014.drag('INVOKE_DEFAULT', kind='TEXTURE')
    yield 0.1
    target = (region.x + center.x, region.y + center.y)
    for i in range(1, 6):
        ev(win, 'MOUSEMOVE', 'NOTHING', start[0] + (target[0] - start[0]) * i / 5, start[1] + (target[1] - start[1]) * i / 5)
        yield 0.05
    ev(win, 'LEFTMOUSE', 'RELEASE', *target)
    yield 0.3
    REPORT["textura"]["eventos"] = len(EVENTS["drag"])
    REPORT["textura"]["release_recebido"] = any(e[0] == 'LEFTMOUSE' and e[1] == 'RELEASE' for e in EVENTS["drag"])
    REPORT["textura"]["cor_aplicada"] = tuple(round(c, 2) for c in cube.color) == (1.0, 0.0, 0.0, 1.0)

    # Caso 2: bloco
    EVENTS["drag"].clear()
    ev(win, 'MOUSEMOVE', 'NOTHING', *start)
    yield 0.1
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.probe014.drag('INVOKE_DEFAULT', kind='BLOCK')
    yield 0.1
    for i in range(1, 6):
        ev(win, 'MOUSEMOVE', 'NOTHING', start[0] + 60 * i, start[1] + 40 * i)
        yield 0.05
    ev(win, 'LEFTMOUSE', 'RELEASE', start[0] + 300, start[1] + 200)
    yield 0.3
    moves = [e for e in EVENTS["insert"] if e[0] == 'MOUSEMOVE']
    REPORT["bloco"]["insert_invocado"] = bool(EVENTS["insert"]) and EVENTS["insert"][0][0] == 'INVOKE'
    REPORT["bloco"]["mousemove_no_insert"] = len(moves)
    REPORT["bloco"]["release_no_insert"] = any(e[0] == 'LEFTMOUSE' and e[1] == 'RELEASE' for e in EVENTS["insert"])
    REPORT["bloco"]["eventos_insert"] = EVENTS["insert"][:3]


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        REPORT["erro"] = True
    print("PROVA_D07", REPORT, flush=True)
    ok = (REPORT["textura"].get("cor_aplicada") and REPORT["bloco"].get("release_no_insert")
          and REPORT["bloco"].get("mousemove_no_insert", 0) > 0 and not REPORT.get("erro"))
    os._exit(0 if ok else 1)


bpy.app.timers.register(tick, first_interval=2.0)
