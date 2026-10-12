"""Reprodução e regressão do lote dos modais interrompidos: BUG-20261011-TLCT, BUG-20261011-3T7M e BUG-20261011-JDYP.

Precisa de janela (não roda em --background), numa instância própria (encerra com o código do resultado):
    blender --factory-startup --enable-event-simulate --python tests/blender_bug_TLCT_modal_cancel.py

Cada modal é aberto numa janela nova, que depois é fechada: o Blender interrompe o modal e chama `cancel()`.
- Criar Geometria não deixa a peça provisória (geometry_free EC-01);
- Inserir objeto da biblioteca não deixa os objetos carregados (object_library DT-03);
- Mover na Parede devolve o módulo ao lugar (questions.md, pergunta 17); Plano de inserção sai sem erro.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401  (registra o addon e a pasta de usuário da extensão)
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.geometry_free import ops_create  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

FAILURES = []
VASE = "B:DECOR:vaso-com-planta"


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def new_window(ctx):
    before = set(w.as_pointer() for w in ctx.window_manager.windows)
    main = ctx.window_manager.windows[0]
    with ctx.temp_override(window=main):
        bpy.ops.wm.window_new()
    win = next(w for w in ctx.window_manager.windows if w.as_pointer() not in before)
    area = max(win.screen.areas, key=lambda a: a.width * a.height)
    area.type = 'VIEW_3D'
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def close(ctx, win):
    with ctx.temp_override(window=win):
        bpy.ops.wm.window_close()


def script():
    ctx = bpy.context
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    yield 0.5

    # Criar Geometria
    win, area, region = new_window(ctx)
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.geometry_create('INVOKE_DEFAULT', kind='PLACA')
    yield 0.3
    drafts = [o for o in ctx.scene.objects if o.get(ops_create.DRAW_FLAG)]
    check("TLCT: o modal criou a peça provisória", len(drafts) == 1)
    close(ctx, win)
    yield 0.5
    left = [o.name for o in ctx.scene.objects if o.get(ops_create.DRAW_FLAG)]
    check("TLCT: interrompido, não fica peça provisória", not left, str(left))

    # Inserir objeto da biblioteca
    before = set(o.name for o in ctx.scene.objects)
    win, area, region = new_window(ctx)
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.object_insert('INVOKE_DEFAULT', key=VASE)
    yield 0.3
    check("JDYP: o modal carregou o vaso", len(set(o.name for o in ctx.scene.objects) - before) > 0)
    close(ctx, win)
    yield 0.5
    extra = sorted(set(o.name for o in ctx.scene.objects) - before)
    check("JDYP: interrompido, não ficam objetos carregados", not extra, str(extra))

    # Mover na Parede
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    wall = sorted((o for o in ctx.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)[0]
    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    base.obj.parent = wall
    base.obj.location = (1.0, 0.0, 0.0)
    ctx.view_layer.update()
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    base.obj.select_set(True)
    ctx.view_layer.objects.active = base.obj
    where = base.obj.location.copy()
    win, area, region = new_window(ctx)
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region, active_object=base.obj):
        started = bpy.ops.caffmob.move_on_wall.poll()
        if started:
            win.event_simulate('MOUSEMOVE', 'NOTHING', x=region.x + region.width // 2, y=region.y + region.height // 2)
            bpy.ops.caffmob.move_on_wall('INVOKE_DEFAULT')
    yield 0.3
    base.obj.location.x += 0.7                                   # o arraste em curso muda a posição
    close(ctx, win)
    yield 0.5
    check("3T7M: Mover na Parede interrompido devolve o módulo", started and (base.obj.location - where).length < 1e-6,
          f"poll={started} {tuple(round(v, 3) for v in base.obj.location)}")

    # Plano de inserção
    win, area, region = new_window(ctx)
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.set_insertion_plane('INVOKE_DEFAULT')
    yield 0.3
    close(ctx, win)
    yield 0.5
    check("3T7M: Plano de inserção interrompido não deixa o plano ativo",
          not ctx.window_manager.btm_insertion_plane.active)


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_bug_TLCT_modal_cancel: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
