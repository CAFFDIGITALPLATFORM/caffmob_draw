"""Reprodução e regressão do lote do editor de paredes: BUG-20261011-YAVM, BUG-20261011-LT3C, BUG-20261011-624G,
BUG-20261011-XMZM, BUG-20261011-PJJU e BUG-20261011-Z2BL.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_YAVM_wall_editor.py

- trocar a Direção pelo painel é um passo de desfazer (EC-10);
- o "Não" de fechar a sala sobrevive ao OK (questions.md, pergunta 8);
- soltar o mouse na barra conclui a lupa e o arraste de vértice (pergunta 9);
- o rascunho mudado depois do 1º aviso refaz os avisos no OK (pergunta 10);
- com a trava, os campos de ângulo ficam desabilitados (pergunta 11);
- pé-direito do projeto fora da faixa não é gravado nas paredes (EC-13).
"""

import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.canvas2d.view import View2D  # noqa: E402
from caffmob_draw.walls2d import apply, model, ops_editor, panels, props  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def walls():
    return [o for o in ctx.scene.objects if o.get('IS_WALL_BP')]


def session(plan):
    props.end()
    s = props.start(plan, ctx.scene.name)
    s.selected = (0, 0)
    return s


def direction_undo():
    s = session(model.WallPlan([model.rectangle(4.0, 3.0)]))
    before = s.plan.chains[0].side
    other = 'LEFT' if before == 'RIGHT' else 'RIGHT'
    ctx.window_manager.btm_wall_editor.direction = other
    side = s.plan.chains[0].side
    undone = s.undo()
    check("YAVM: Ctrl+Z desfaz a troca de Direção", side == other and undone and s.plan.chains[0].side == before,
          f"depois da troca={side} desfez={undone} agora={s.plan.chains[0].side}")
    s.redo()
    check("YAVM: e refaz", s.plan.chains[0].side == other)


def answer_no_survives_ok():
    env.clean_scene()
    u = model.Chain([(0, 0), (4, 0), (4, 3), (0, 3), (0, 0.004)], [model.Segment() for _ in range(4)])
    s = session(model.WallPlan([u]))
    s.prompt, s.prompt_chain = 'close_existing', 0
    ops_editor.BTM_OT_WallEditorModal._answer_no(types.SimpleNamespace(), ctx, s)
    report = apply.apply_plan(ctx, s.plan)
    check("LT3C: o 'Não' de fechar a sala sobrevive ao OK", report['closed'] == 0 and len(walls()) == 4,
          f"fechadas={report['closed']} paredes={len(walls())}")


def release_on_bar():
    view = View2D((0, 0, 800, 600), scale=100.0)
    bar, _lupa = ops_editor._toolbar_rects(view)
    on_bar = (bar[0] + bar[2] / 2, bar[1] + bar[3] / 2)
    release = types.SimpleNamespace(type='LEFTMOUSE', value='RELEASE')
    s = types.SimpleNamespace(zoom_window=(100.0, 100.0), zoom_box_end=(300.0, 400.0))
    scale = view.scale
    ops_editor.handle_zoom_window(release, s, view, on_bar)
    check("624G: soltar na barra conclui a lupa", s.zoom_window is None and view.scale != scale,
          f"zoom_window={s.zoom_window} escala {scale} → {view.scale}")
    s = types.SimpleNamespace(zoom_window=None, zoom_box_end=None)
    consumed = ops_editor.handle_zoom_window(release, s, view, on_bar)
    check("624G: soltar na barra durante o arraste de vértice chega ao editor", not consumed)


def ok_rewarns_after_change():
    env.clean_scene()
    s = session(model.WallPlan([model.rectangle(4.0, 3.0)]))
    s.project_height, s.equalize_height = 3.0, False         # 2,6 m ≠ 3,0 m: aviso de pé-direito
    first = bpy.ops.caffmob.wall_editor_ok()
    s.plan.chains[0].set_length(0, 4.5)                       # muda o rascunho depois do aviso
    second = bpy.ops.caffmob.wall_editor_ok()
    check("XMZM: o 2º OK refaz os avisos se o rascunho mudou", first == {'CANCELLED'} and second == {'CANCELLED'}
          and s.request != 'ok', f"1º={first} 2º={second}")
    third = bpy.ops.caffmob.wall_editor_ok()
    check("XMZM: sem mudança, o OK seguinte aplica", third == {'FINISHED'} and s.request == 'ok', str(third))


class Layout:
    """Layout falso: registra se cada campo foi desenhado habilitado."""

    def __init__(self, record, enabled=True):
        self.record, self.enabled = record, enabled
        self.use_property_split = self.use_property_decorate = False

    def _child(self, *args, **kwargs):
        child = Layout(self.record)
        child.parent = self
        return child

    row = column = box = split = _child

    def prop(self, _data, name, **kwargs):
        on, node = True, self
        while node is not None:
            on = on and node.enabled
            node = getattr(node, 'parent', None)
        self.record[name] = on

    def label(self, *args, **kwargs):
        pass

    operator = separator = label


def lock_disables_angles():
    s = session(model.WallPlan([model.rectangle(4.0, 3.0)]))
    s.plan.chains[0].segments[0].lock_angle = True
    record = {}
    panels.BTM_PT_WallEditorSegment.draw(types.SimpleNamespace(layout=Layout(record)), ctx)
    check("PJJU: com a trava, os ângulos ficam desabilitados", record.get('angle_abs') is False
          and record.get('angle_rel') is False and record.get('lock_angle') is True, str(record))


def invalid_project_height():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    try:
        apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]), project_height=12.0)
        refused = False
    except ValueError:
        refused = True
    tall = [o.name for o in walls() if o.get('IS_WALL_BP') and
            abs(__import__('caffmob_draw.hb_types', fromlist=['x']).GeoNodeWall(o).get_input('Height') - 12.0) < 1e-6]
    check("Z2BL: pé-direito de 12 m é recusado", refused and not tall, f"recusou={refused} paredes com 12 m={tall}")


for step in (direction_undo, answer_no_survives_ok, release_on_bar, ok_rewarns_after_change, lock_disables_angles,
             invalid_project_height):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
props.end()
print(f"blender_bug_YAVM_wall_editor: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
