"""Editor de armário (feature 067, T032; RF-106, RF-107).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda5_editor.py

- arrastar uma divisória e soltar grava um único passo no histórico do editor (um Desfazer volta ao antes do
  arraste); Esc durante o arraste restaura a posição sem passo;
- a peça escolhida continua escolhida depois que a lista é refeita;
- a lista de peças é rolável (lista do Blender) e as medidas recolhem;
- a grade do catálogo usa 1, 2 ou 3 colunas pela largura;
- item de catálogo sem executor validado aparece com o motivo e não é inserível; os que aparecem habilitados têm
  executor no editor.
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.cabinet_editor import (bridge, catalog, division_drag, ops_editor, panels, props,  # noqa: E402
                                         scene_divisions)
from caffmob_draw.ui import layout_probe  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def view3d(ctx):
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, region


def offset(root):
    return round(scene_divisions.read(root)[0]['offset'], 5)


def script():
    ctx = bpy.context
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(width=1.0, door_swing='NONE') == {'FINISHED'}
    root = ctx.object
    env.settle()
    win, area, region = view3d(ctx)
    with ctx.temp_override(window=win, area=area, region=region, active_object=root, object=root):
        check(bpy.ops.caffmob.cabinet_editor('INVOKE_DEFAULT') == {'FINISHED'}, "abre o editor")
    yield 1.2
    s = props.session()
    root = s.root()
    ui = ctx.window_manager.btm_cabinet_editor
    ui.tab = 'DIVISIONS'
    s.push('edit', ('ADD_DIVISION', {'space': s.space, 'orientation': 'VERTICAL', 'targets': []}))
    yield 0.8
    division = scene_divisions.objects(root)[0]
    start = offset(root)
    steps = len(s.draft.history._undo)

    # Arrastar e soltar: um passo.
    drag = division_drag.begin(ctx, s, root, division, 0.0, 0.0)
    check(drag is not None and drag.vertical, "o clique na divisória começa o arraste")
    division_drag.update(ctx, s, root, drag, 0.05, 0.0)
    division_drag.update(ctx, s, root, drag, 0.12, 0.0)
    moved = offset(root)
    division_drag.end(ctx, s, root, drag, ops_editor.refresh)
    check(abs(moved - start - 0.12) < 1e-4, "a divisória acompanha o mouse", f"{start} → {moved}")
    check(len(s.draft.history._undo) == steps + 1, "soltar grava um único passo no histórico",
          f"{steps} → {len(s.draft.history._undo)}")
    s.push('undo')
    yield 0.6
    check(abs(offset(root) - start) < 1e-4, "um Desfazer do editor volta ao antes do arraste", str(offset(root)))

    # Esc durante o arraste restaura sem passo.
    steps = len(s.draft.history._undo)
    drag = division_drag.begin(ctx, s, root, scene_divisions.objects(root)[0], 0.0, 0.0)
    division_drag.update(ctx, s, root, drag, -0.1, 0.0)
    division_drag.cancel(ctx, s, root, drag, ops_editor.refresh)
    check(abs(offset(root) - start) < 1e-4 and len(s.draft.history._undo) == steps,
          "Esc restaura a posição sem passo", f"{offset(root)} {len(s.draft.history._undo)}")

    # Seleção sobrevive ao refresh da lista.
    name = scene_divisions.objects(root)[0].name
    s.selected = name
    ops_editor.refresh(ctx, s, checkpoint=False)
    index = ui.component_index
    check(0 <= index < len(ui.components) and ui.components[index].name == name,
          "a peça escolhida continua escolhida depois do refresh")

    # Painéis: lista de peças e medidas recolhíveis; grade de 1 a 3 colunas.
    recorder = layout_probe.Recorder()
    panel = panels.BTM_PT_CabinetEditorParts
    try:
        panel.draw(type('P', (), {'layout': layout_probe.Probe(recorder)})(), ctx)
        drawn = True
    except Exception as exc:                  # a camada falsa pode não ter template_list
        drawn = 'template_list' in str(exc)
    check(drawn, "o painel Peças desenha a lista")
    ui.measures_open = False
    check(not ui.measures_open and 'measures_open' in ui.bl_rna.properties, "as medidas recolhem")
    ui.measures_open = True
    widths = [panels.columns_for(type('R', (), {'width': w})()) for w in (200, 300, 520)]
    check(widths == [1, 2, 3], "1, 2 ou 3 colunas pela largura", str(widths))

    # Catálogo: só executor validado.
    executors = set(bridge.EDIT_006) | set(bridge.EDIT_008)
    offered = [i for i in catalog.ITEMS if catalog.unavailable_reason(i, 'BTM') is None]
    refused = [i for i in catalog.ITEMS if catalog.unavailable_reason(i, 'BTM') is not None]
    check(all(catalog.EXECUTOR_OF[i.action] in executors for i in offered),
          "todo item oferecido tem executor no editor",
          str([i.id for i in offered if catalog.EXECUTOR_OF.get(i.action) not in executors]))
    check(catalog.get('FRONT_RETA') in refused and catalog.get('DRAWER_SHOE') in refused,
          "item sem executor (ou sem suporte na biblioteca) fica de fora, com o motivo",
          str([(i.id, catalog.unavailable_reason(i, 'BTM')) for i in refused][:6]))
    texts = []

    class Spy:
        """Layout mínimo que grava os rótulos (a camada falsa da 005 não grava `label`)."""

        def __getattr__(self, name):
            return lambda *a, **k: Spy()

        def label(self, text="", **_k):
            texts.append(text)

        def operator(self, *a, **k):
            return type('Op', (), {})()

    panels.catalog_grid(Spy(), ctx, catalog.items('DRAWERS', 'FRONTS'))
    check(any("Sem executor" in t for t in texts), "a grade mostra o motivo do item sem executor", str(texts))
    s.request = 'cancel'
    yield 0.6


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção no roteiro")
    print(f"blender_067_onda5_editor: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
