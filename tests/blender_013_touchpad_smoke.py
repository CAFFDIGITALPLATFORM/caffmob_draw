"""Teste de fumaça da feature 013 (T015; RF-01 a RF-07, RF-10, RF-11): touchpad e lupa no Editor de Paredes.

Roda em segundo plano, acionando os tratadores do modal com eventos falsos, como a fumaça da 009:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_013_touchpad_smoke.py

- pinça (`TRACKPADZOOM`): afastar aproxima e juntar afasta, com o ponto sob o cursor parado (≤ 1 px); ida e volta
  devolvem a escala (≤ 0,1%); o fator cresce com o gesto e não é o passo de 15% da roda;
- arraste com dois dedos (`TRACKPADPAN`): move 100 px (± 1 px) sem mudar a escala;
- roda e Ctrl + roda: 1,15 ancorado; com a preferência "inverter zoom pela roda", a roda para cima afasta e a pinça não
  muda;
- os gestos não mexem no rascunho: com "2.4" digitado no lápis e com a pergunta de fechamento aberta, a escala muda e
  o texto, a pergunta e o número de passos de desfazer continuam iguais; o evento de navegação pula o encaixe da mira;
- um evento com o mouse sobre o painel lateral devolve `PASS_THROUGH` (nada muda na planta);
- lupa com quadrado: clique na lupa liga o modo, marcar um retângulo enquadra centrado, Esc cancela sem mexer na vista
  nem no desenho, retângulo de 3 px não muda a vista, e nada entra no histórico.
"""

import math
import sys
import traceback
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.canvas2d import gestures  # noqa: E402
from caffmob_draw.canvas2d.view import View2D  # noqa: E402
from caffmob_draw.walls2d import model, ops_editor, props, window  # noqa: E402

ctx = bpy.context
FAILURES = []
W, H = 1000, 800


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def event(kind, value='PRESS', px=(0, 0), dx=0, dy=0, ctrl=False, char=''):
    """Evento como o Blender entrega: nos gestos de touchpad o delta vem em `mouse_prev_*` (prova D-02)."""
    x, y = int(px[0]), int(px[1])
    return types.SimpleNamespace(type=kind, value=value, unicode=char, shift=False, ctrl=ctrl, oskey=False,
                                 mouse_x=x, mouse_y=y, mouse_prev_x=x - dx, mouse_prev_y=y - dy)


def pinch(delta):
    """Pinça com `delta` > 0 = afastar os dedos, na convenção do Blender (`compat.pinch_delta`): prev_x > x."""
    return event('TRACKPADZOOM', 'NOTHING', px=PX, dx=-delta)


def room():
    return model.Chain([(0.0, 0.0), (3.9, 0.0), (3.9, 2.7), (0.0, 2.7)], [model.Segment() for _ in range(4)], True,
                       'RIGHT')


def setup(tool='SELECT'):
    env.clean_scene()
    s = props.start(model.WallPlan([room()]), ctx.scene.name)
    s.view = View2D((0, 0, W, H - ops_editor.toolbar_height()))
    s.view.fit(s.plan.bounds(), margin=0.15)
    window.editor_area = lambda c: (None, None, types.SimpleNamespace(width=W, height=H, x=0, y=0))
    op = types.SimpleNamespace(dragging=None, panning=None, shift=False)
    for name in ('_handle', '_handle_click', '_handle_draw', '_append', '_finish_drawing', '_handle_prompt',
                 '_handle_typing', '_answer_no', '_update_snap', '_is_navigation', '_local'):
        setattr(op, name, getattr(ops_editor.BTM_OT_WallEditorModal, name).__get__(op))
    state = ctx.window_manager.btm_wall_editor
    state.tool, state.magnetic = tool, False
    return s, op


def send(s, op, ev):
    """Como o modal: cursor e encaixe antes do tratador, passo de desfazer depois."""
    s.cursor = s.view.to_world((ev.mouse_x, ev.mouse_y))
    if not op._is_navigation(ev):
        op._update_snap(ctx, s, s.view)
    handled = op._handle(ctx, ev, s, s.view, (float(ev.mouse_x), float(ev.mouse_y)))
    if handled and op.dragging is None:
        s.checkpoint()
    return handled


def undo_steps(s):
    return len(s.history._undo)


PX = (650.0, 300.0)       # cursor sobre a planta, longe do centro


def main():
    inverted_pref = ctx.preferences.inputs.invert_zoom_wheel
    ctx.preferences.inputs.invert_zoom_wheel = False

    # Pinça: sentido, âncora, ida e volta, proporcional
    s, op = setup()
    scale0, anchor_world = s.view.scale, s.view.to_world(PX)
    send(s, op, pinch(45))
    after = s.view.to_screen(anchor_world)
    check("afastar os dedos aproxima", s.view.scale > scale0, f"{scale0} -> {s.view.scale}")
    check("o ponto sob o cursor fica parado (≤ 1 px)", math.dist(after, PX) <= 1.0, str(after))
    scale1 = s.view.scale
    send(s, op, pinch(-45))
    check("juntar os dedos afasta", s.view.scale < scale1)
    check("ida e volta devolvem a escala (≤ 0,1%)", abs(s.view.scale - scale0) / scale0 <= 0.001,
          f"{scale0} -> {s.view.scale}")
    send(s, op, pinch(20))
    small = s.view.scale / scale0
    s.view.scale = scale0
    send(s, op, pinch(40))
    big = s.view.scale / scale0
    check("o fator cresce com o gesto e não é o passo da roda", big > small and abs(small - 1.15) > 1e-6
          and abs(big - 1.15) > 1e-6, f"{small} {big}")
    check("delta zero não muda nada", (send(s, op, pinch(0)) and s.view.scale == scale0 * big))

    # Arraste com dois dedos
    s, op = setup()
    scale0, p_world = s.view.scale, s.view.to_world((300.0, 300.0))
    send(s, op, event('TRACKPADPAN', 'NOTHING', px=PX, dx=100))
    moved = s.view.to_screen(p_world)
    check("arraste com dois dedos move 100 px para a direita", abs(moved[0] - 400.0) <= 1.0 and abs(moved[1] - 300.0)
          <= 1.0, str(moved))
    check("o arraste não muda a escala", s.view.scale == scale0)

    # Roda, Ctrl + roda e preferência de inverter
    s, op = setup()
    scale0 = s.view.scale
    send(s, op, event('WHEELUPMOUSE', px=PX))
    check("roda para cima aproxima 15%", abs(s.view.scale / scale0 - 1.15) < 1e-9)
    send(s, op, event('WHEELUPMOUSE', px=PX, ctrl=True))
    check("Ctrl + roda para cima aproxima 15%", abs(s.view.scale / scale0 - 1.15 ** 2) < 1e-9)
    ctx.preferences.inputs.invert_zoom_wheel = True
    scale1 = s.view.scale
    send(s, op, event('WHEELUPMOUSE', px=PX))
    check("com a preferência invertida, roda para cima afasta", abs(s.view.scale * 1.15 - scale1) < 1e-9)
    send(s, op, pinch(30))
    check("a pinça não muda com a preferência", s.view.scale > scale1 / 1.15)
    ctx.preferences.inputs.invert_zoom_wheel = False

    # Navegar não mexe no rascunho: lápis com digitação e pergunta aberta
    s, op = setup('DRAW')
    send(s, op, event('LEFTMOUSE', px=(200.0, 200.0)))
    send(s, op, event('A', px=(400.0, 200.0), char='2'))
    send(s, op, event('A', px=(400.0, 200.0), char='.'))
    send(s, op, event('A', px=(400.0, 200.0), char='4'))
    typed, nodes, steps, scale0 = s.typed, len(s.drawing.nodes), undo_steps(s), s.view.scale
    send(s, op, pinch(40))
    send(s, op, event('TRACKPADPAN', 'NOTHING', px=PX, dx=30, dy=-20))
    check("com '2.4' digitado, a pinça muda a escala", s.view.scale != scale0)
    check("o texto digitado e o trecho em curso não mudam", s.typed == typed == "2.4" and len(s.drawing.nodes) == nodes
          and s.drawing is not None, f"{s.typed} {len(s.drawing.nodes)}")
    check("navegar não grava passo de desfazer", undo_steps(s) == steps, f"{steps} -> {undo_steps(s)}")
    check("o evento de navegação pula o encaixe", op._is_navigation(pinch(1)) and not op._is_navigation(
        event('MOUSEMOVE', 'NOTHING')))
    s.prompt = 'close'
    scale0 = s.view.scale
    send(s, op, pinch(-25))
    check("com a pergunta aberta, a pinça muda a escala e a pergunta fica", s.view.scale < scale0 and s.prompt == 'close')

    # Sobre o painel lateral o evento passa direto
    s, op = setup()
    window.over_side_panel = lambda area, x, y: True
    region, pixel = op._local(ctx, event('TRACKPADZOOM', 'NOTHING', px=PX, dx=-40))
    check("gesto sobre o painel lateral passa direto (PASS_THROUGH)", region is None and pixel is None)
    window.over_side_panel = lambda area, x, y: False

    # Lupa com quadrado
    s, op = setup()
    bar, lupa = ops_editor._toolbar_rects(s.view)
    check("a barra fica no topo, acima da vista", bar[1] == s.view.rect[3] and bar[1] + bar[3] == H, str(bar))
    center_btn = (lupa[0] + lupa[2] / 2, lupa[1] + lupa[3] / 2)
    scale0, steps = s.view.scale, undo_steps(s)
    send(s, op, event('LEFTMOUSE', px=center_btn))
    check("clicar na lupa liga o modo", s.zoom_window == 'ARMED')
    send(s, op, event('A', px=PX, char='5'))
    check("com a lupa ligada a digitação não chega às ferramentas", s.typed == "")
    p0, p1 = (300.0, 200.0), (500.0, 330.0)
    send(s, op, event('LEFTMOUSE', px=p0))
    target = s.view.to_world(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2))
    send(s, op, event('MOUSEMOVE', 'NOTHING', px=(420.0, 300.0)))
    check("o retângulo elástico acompanha o mouse", s.zoom_box_end == (420.0, 300.0), str(s.zoom_box_end))
    send(s, op, event('LEFTMOUSE', 'RELEASE', px=p1))
    centered = s.view.to_screen(target)
    vx, vy = s.view.rect[2] / 2, s.view.rect[3] / 2
    check("soltar enquadra o retângulo centrado (± 2 px)", abs(centered[0] - vx) <= 2 and abs(centered[1] - vy) <= 2
          and s.view.scale > scale0, f"{centered} escala {scale0} -> {s.view.scale}")
    check("o modo desliga depois de enquadrar", s.zoom_window is None and s.zoom_box_end is None)
    check("a lupa não mexe no rascunho nem no histórico", len(s.plan.chains) == 1 and s.selected is None
          and undo_steps(s) == steps)
    scale1, center1 = s.view.scale, s.view.center
    send(s, op, event('LEFTMOUSE', px=center_btn))
    send(s, op, event('ESC', px=PX))
    check("Esc cancela a lupa sem mexer na vista", s.zoom_window is None and s.view.scale == scale1
          and s.view.center == center1 and s.request is None)
    send(s, op, event('LEFTMOUSE', px=center_btn))
    send(s, op, event('LEFTMOUSE', px=(300.0, 300.0)))
    send(s, op, event('LEFTMOUSE', 'RELEASE', px=(303.0, 303.0)))
    check("retângulo de 3 px não muda a vista", s.zoom_window is None and s.view.scale == scale1
          and s.view.center == center1)
    send(s, op, event('LEFTMOUSE', px=center_btn))
    send(s, op, event('LEFTMOUSE', px=center_btn))
    check("segundo clique na lupa cancela o modo", s.zoom_window is None)
    check("a vista desconta a barra", s.view.rect[3] == H - ops_editor.toolbar_height()
          and gestures.ZOOM_WINDOW_MIN_PX == 5)
    props.end()
    ctx.preferences.inputs.invert_zoom_wheel = inverted_pref


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_013_touchpad_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
