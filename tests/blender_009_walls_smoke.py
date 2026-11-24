"""Teste de fumaça do editor de paredes da feature 009 (T037; RF-01 a RF-05, RN-01 a RN-07).

Roda em segundo plano, acionando os tratadores do modal como a fumaça da 002 (a janela e o desenho da mira ficam com
`blender_002_ui_events.py`, que abre o editor de verdade):
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_walls_smoke.py

- mira: o cursor a 3 mm da altura de um canto trava na altura dele, e o ponto clicado sai pareado; com Shift não trava;
- sequência 100, 285, 2*8, 200/2, 2000 com o mouse parado em qualquer lugar: 5 trechos a 0° que somam 2501 mm;
- mover o mouse sem clicar mantém a direção; a seta para cima troca; o clique troca para a direção do trecho;
- "10/0" mostra "Valor Inválido" e não cria parede;
- no OK (aplicar o plano), os trechos colineares continuam separados (RN-07).
"""

import math
import sys
import types
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.canvas2d.view import View2D  # noqa: E402
from caffmob_draw.data.i18n import tr  # noqa: E402
from caffmob_draw.walls2d import apply, model, ops_editor, props, scene_io, window  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=1e-6):
    return all(abs(p - q) <= tol for p, q in zip(a, b))


def event(kind, value='PRESS', char='', shift=False):
    return types.SimpleNamespace(type=kind, value=value, unicode=char, shift=shift)


def setup():
    env.clean_scene()
    s = props.start(model.WallPlan([model.Chain([(3.0, 2.0), (3.0, 4.0)], [model.Segment()], False, 'RIGHT')]),
                    ctx.scene.name)
    s.view = View2D((0, 0, 1000, 800))
    s.view.fit(((-1, -1), (6, 5)), margin=0.1)
    window.editor_area = lambda c: (None, None, types.SimpleNamespace(width=1000, height=800, x=0, y=0))
    op = types.SimpleNamespace(dragging=None, panning=None, shift=False)
    for name in ('_handle', '_handle_click', '_handle_draw', '_append', '_finish_drawing', '_handle_prompt',
                 '_handle_typing', '_answer_no', '_update_snap', '_handle_menu'):
        setattr(op, name, getattr(ops_editor.BTM_OT_WallEditorModal, name).__get__(op))
    state = ctx.window_manager.btm_wall_editor
    state.tool, state.magnetic = 'DRAW', False
    return s, op


def move(s, op, world, shift=False):
    """Como o modal: cursor, Shift e trava da mira antes de tratar o evento."""
    s.cursor, op.shift = world, shift
    op._update_snap(ctx, s, s.view)


def press(s, op, ev):
    return op._handle(ctx, ev, s, s.view, s.view.to_screen(s.cursor))


def type_text(s, op, text):
    for ch in text:
        press(s, op, event('A', char=ch))
    press(s, op, event('RET'))


def main():
    s, op = setup()
    mm = 1 / 1000.0
    # Mira: começa em (0, 0); o canto (3, 2) está do outro lado da planta
    move(s, op, (0.0, 0.0))
    press(s, op, event('LEFTMOUSE'))
    move(s, op, (0.4, 2.0 + 3 * mm))
    check("mira trava na altura do canto (8 px)", s.lock_y is not None and s.lock_y[1] == (3.0, 2.0)
          and s.snap_point[0][1] == 2.0, str(s.lock_y))
    move(s, op, (0.4, 2.0 + 3 * mm), shift=True)
    check("com Shift o alinhamento não trava", s.lock_y is None and abs(s.snap_point[0][1] - 2.003) < 1e-9,
          str(s.snap_point))
    move(s, op, (0.4, 2.0 + 3 * mm))
    press(s, op, event('LEFTMOUSE'))
    check("o ponto clicado sai pareado (Y = 2000 mm exato)", s.drawing.nodes[-1][1] == 2.0, str(s.drawing.nodes))
    props.end()

    # Sequência na direção atual, com o mouse em qualquer lugar
    s, op = setup()
    move(s, op, (0.0, 0.0))
    press(s, op, event('LEFTMOUSE'))
    move(s, op, (0.9, 0.02))
    for text, mouse in (("100", (0.9, 0.02)), ("285", (-3.0, 1.0)), ("2*8", (0.0, -4.0)), ("200/2", (2.0, 3.0)),
                        ("2000", (-1.0, -1.0))):
        move(s, op, mouse)
        if text == "2*8":
            for ch in text:
                press(s, op, event('A', char=ch))
            check("a conta mostra o resultado ao lado", s.typed_preview == "= 16 mm", s.typed_preview)
            press(s, op, event('RET'))
        else:
            type_text(s, op, text)
    nodes = s.drawing.nodes
    lengths = [round(math.dist(nodes[i], nodes[i + 1]) * 1000, 3) for i in range(len(nodes) - 1)]
    check("5 trechos na direção 0° com 100, 285, 16, 100 e 2000 mm", lengths == [100, 285, 16, 100, 2000]
          and close(nodes[-1], (2.501, 0.0)), f"{lengths} {nodes[-1]}")
    move(s, op, (2.501, 3.0))                         # mouse para cima, sem clicar
    type_text(s, op, "300")
    check("mover o mouse sem clicar mantém a direção", close(s.drawing.nodes[-1], (2.801, 0.0)), str(nodes[-1]))
    press(s, op, event('UP_ARROW'))
    type_text(s, op, "1200")
    check("a seta para cima troca a direção", close(s.drawing.nodes[-1], (2.801, 1.2)), str(s.drawing.nodes[-1]))
    move(s, op, (1.0, 1.2))
    press(s, op, event('LEFTMOUSE'))
    type_text(s, op, "500")
    check("o clique troca a direção para a do trecho", close(s.drawing.nodes[-1], (0.5, 1.2)),
          str(s.drawing.nodes[-1]))
    count = len(s.drawing.nodes)
    for ch in "10/0":
        press(s, op, event('A', char=ch))
    check("10/0 mostra Valor Inválido ao lado", s.typed_preview == tr("Valor Inválido"), s.typed_preview)
    press(s, op, event('RET'))
    check("10/0 não cria parede", len(s.drawing.nodes) == count and s.error.startswith(tr("Valor Inválido")),
          s.error)
    press(s, op, event('ESC'))
    plan = s.plan
    props.end()
    report = apply.apply_plan(ctx, plan)
    reread = scene_io.read_plan(ctx.scene)
    counts = sorted(c.segment_count() for c in reread.chains)
    check("no OK os trechos colineares continuam separados", counts == [1, 9], f"{counts} {len(report['created'])}")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_009_walls_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
