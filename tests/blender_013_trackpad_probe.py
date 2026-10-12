"""Prova da feature 013 (T001; D-02): como o delta da pinça e do arraste com dois dedos chega ao modal.

Precisa de janela (não roda em --background):
    /opt/blender/blender --factory-startup --enable-event-simulate --python tests/blender_013_trackpad_probe.py

O corpus da API 5.2 confirma os tipos `TRACKPADZOOM`/`TRACKPADPAN` e os campos `mouse_x/y` e `mouse_prev_x/y`
(`docs/rag/blender-api/corpus/bpy.types.Event.md`), mas não diz em que eixo, com que sinal e em que unidade o delta do
gesto vem. Esta prova:
1. abre o Editor de Paredes de verdade, embrulha o `modal` para imprimir cada evento `TRACKPAD*`/`WHEEL*` recebido
   (`type`, `value`, `mouse_x/y`, `mouse_prev_x/y`, `ctrl`) e a escala da vista antes e depois;
2. envia gestos por `Window.event_simulate` com deltas conhecidos (x = +40, y = +40, ...);
3. se a simulação não reproduzir o delta (o Blender pode gerar o evento sem o deslocamento), deixa a janela aberta com
   o `print` ligado por `CAFFMOB_PROBE_MANUAL=1`, para a prova à mão num notebook com touchpad: faça a pinça e o arraste
   e leia o console. Encerre com Esc no editor.

O resultado vai para `_reversa_forward/013-touchpad-editor-parede/investigation.md` §6 (T002).
"""

import os
import sys
import traceback
import types
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon  # noqa: E402

addon.register()
type(bpy.context.window_manager.home_builder).get_user_preferences = \
    lambda self, c: types.SimpleNamespace(wall_color=(0.5, 0.5, 0.5, 1.0), door_window_color=(0.3, 0.3, 0.3, 1.0))

from caffmob_draw.walls2d import ops_editor, props  # noqa: E402
from caffmob_draw.walls2d import window as w2d  # noqa: E402

MANUAL = os.environ.get("CAFFMOB_PROBE_MANUAL") == "1"
WATCH = {'TRACKPADZOOM', 'TRACKPADPAN', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'MOUSEZOOM', 'MOUSEPAN', 'MOUSESMARTZOOM'}
SEEN = []


def log(label, event, before, after):
    row = (label, event.type, event.value, event.mouse_x, event.mouse_y, event.mouse_prev_x, event.mouse_prev_y,
           event.ctrl, round(before, 3), round(after, 3))
    SEEN.append(row)
    print("PROVA  label={} type={} value={} xy=({}, {}) prev=({}, {}) dxy=({}, {}) ctrl={} escala {} -> {}".format(
        label, event.type, event.value, event.mouse_x, event.mouse_y, event.mouse_prev_x, event.mouse_prev_y,
        event.mouse_x - event.mouse_prev_x, event.mouse_y - event.mouse_prev_y, event.ctrl, round(before, 3),
        round(after, 3)), flush=True)


_original_modal = ops_editor.BTM_OT_WallEditorModal.modal
LABEL = ['inicio']


def _probe_modal(self, context, event):
    s = props.session()
    before = s.view.scale if s is not None and s.view is not None else 0.0
    result = _original_modal(self, context, event)
    if event.type in WATCH:
        s = props.session()
        after = s.view.scale if s is not None and s.view is not None else 0.0
        log(LABEL[0], event, before, after)
    return result


ops_editor.BTM_OT_WallEditorModal.modal = _probe_modal


def ev(win, kind, value='NOTHING', x=0, y=0, ctrl=False):
    win.event_simulate(kind, value, x=int(x), y=int(y), ctrl=ctrl)


def script():
    ctx = bpy.context
    for obj in list(ctx.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.wall_editor('INVOKE_DEFAULT')
    yield 1.5
    ewin, earea, ereg = w2d.editor_area(ctx)
    cx, cy = ereg.x + ereg.width * 0.4, ereg.y + ereg.height * 0.5
    ev(ewin, 'MOUSEMOVE', 'NOTHING', cx, cy)
    yield 0.2
    # Gestos simulados com delta conhecido: o Blender guarda a posição anterior no próprio evento.
    for label, kind, dx, dy, ctrl in (("zoom x+40", 'TRACKPADZOOM', 40, 0, False),
                                      ("zoom x-40", 'TRACKPADZOOM', -40, 0, False),
                                      ("zoom y+40", 'TRACKPADZOOM', 0, 40, False),
                                      ("zoom y-40", 'TRACKPADZOOM', 0, -40, False),
                                      ("pan x+60", 'TRACKPADPAN', 60, 0, False),
                                      ("pan y+60", 'TRACKPADPAN', 0, 60, False),
                                      ("roda cima", 'WHEELUPMOUSE', 0, 0, False),
                                      ("ctrl+roda cima", 'WHEELUPMOUSE', 0, 0, True)):
        LABEL[0] = label
        ev(ewin, 'MOUSEMOVE', 'NOTHING', cx, cy)
        yield 0.1
        if kind.startswith('WHEEL'):
            ev(ewin, kind, 'PRESS', cx, cy, ctrl=ctrl)
        else:
            ev(ewin, kind, 'NOTHING', cx + dx, cy + dy, ctrl=ctrl)
        yield 0.25
    simulated = [r for r in SEEN if r[1] in {'TRACKPADZOOM', 'TRACKPADPAN'}]
    with_delta = [r for r in simulated if (r[3] - r[5], r[4] - r[6]) != (0, 0)]
    print(f"PROVA  eventos de touchpad recebidos: {len(simulated)}, com delta: {len(with_delta)}", flush=True)
    if MANUAL or not with_delta:
        LABEL[0] = 'manual'
        print("PROVA  faça a pinça (afastar, depois juntar) e o arraste com dois dedos sobre a planta; "
              "Esc no editor encerra.", flush=True)
        while props.session() is not None:
            yield 0.5
    else:
        s = props.session()
        if s is not None:
            s.request = 'cancel'
        yield 0.5


_gen = script()


def tick():
    try:
        return next(_gen)
    except StopIteration:
        pass
    except Exception:
        traceback.print_exc()
    print("PROVA  fim: {} evento(s) registrado(s)".format(len(SEEN)), flush=True)
    os._exit(0)


bpy.app.timers.register(tick, first_interval=2.0)
