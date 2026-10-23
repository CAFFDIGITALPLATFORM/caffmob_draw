"""Reprodução e regressão de BUG-20261022-RQR5 (#137): a janela do Mover Sobre é o "Encostar" do artefato.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_RQR5_janela_encostar.py

A janela roda sem área de tela no modo background; o teste chama os métodos do operador num objeto falso, como o
`blender_bug_CKVJ_move_over_dialog.py`.
"""

import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.move_over import encostar, ops_dialog  # noqa: E402
from caffmob_draw.move_over.scene import MoveOver  # noqa: E402

ctx = bpy.context
FAILURES = []
REGION = types.SimpleNamespace(width=1400, height=900)
CTX = types.SimpleNamespace(area=types.SimpleNamespace(tag_redraw=lambda: None), region=REGION,
                            window_manager=ctx.window_manager, scene=ctx.scene,
                            evaluated_depsgraph_get=ctx.evaluated_depsgraph_get)


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


def cube(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = ctx.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def scene():
    env.clean_scene()
    b = cube("Armario", (1.0, 0.6, 0.8), (0.5, 0.3, 1.6))          # caixa de B: x 0..1, y 0..0,6, z 1,2..2
    a = cube("Coifa", (0.4, 0.5, 0.4), (3.2, 0.05, 1.4))           # à direita de B
    env.settle()
    return a, b


def dialog(a, b):
    methods = {k: v for k, v in vars(ops_dialog.BTM_OT_MoveOverDialog).items() if callable(v)}
    fake = type('Dialog', (), methods)()
    fake.mo = MoveOver(ctx, a, b)
    fake.report = lambda *args: None
    fake._finish = lambda context: None
    fake.state = ctx.window_manager.btm_move_over
    fake.state.glue = False
    fake.state.snap_on = True
    fake._init_encostar(CTX)
    fake._layout(CTX)
    fake._fit_views()
    return fake


def box_a(fake):
    return fake.mo.box_a()


try:
    a, b = scene()
    fake = dialog(a, b)
    check("título é Encostar «A» em «B»", fake._title() == "Encostar “Coifa” em “Armario”", fake._title())
    check("lado inicial pelo maior afastamento (à direita)", fake.side == encostar.RIGHT, fake.side)
    check("seis chips de lado", len(fake.side_chips) == 6 and [s for s, _r in fake.side_chips] == list(encostar.SIDES))
    check("alinhamentos do lado à direita: profundidade e altura",
          sorted(axis for axis, _r in fake.align_rows) == [1, 2], fake.align_rows)
    check("campo Afastamento e caixa Grudar", fake.gap_field is not None and fake.glue_box is not None)

    lo, hi = box_a(fake)
    bb = fake.mo.box_b
    check("abre já encostado à direita, pela base e pelo fundo",
          close(lo[0], bb[1][0]) and close(lo[2], bb[0][2]) and close(hi[1], bb[1][1]), (lo, hi, bb))

    fake._set_side(encostar.LEFT)
    fake._set_gap_typed("100")
    lo, hi = box_a(fake)
    check("à esquerda com 100 mm", close(hi[0], bb[0][0] - 0.1), (hi[0], bb[0][0]))
    check("afastamento fora de 0 a 5000 mm é recusado com aviso",
          not fake._set_gap_typed("6000") and bool(fake.warning) and close(fake.gap, 0.1), (fake.gap, fake.warning))

    fake._set_side(encostar.TOP)
    fake._set_align(0, 'CENTER')
    lo, hi = box_a(fake)
    check("em cima, centralizado na largura", close(lo[2], bb[1][2] + 0.1) and
          close((lo[0] + hi[0]) / 2, (bb[0][0] + bb[1][0]) / 2), (lo, hi))
    check("linha de folga e deslocamento", fake._info_text().startswith("Folga até “Armario”:") and
          "Deslocamento:" in fake._info_text(), fake._info_text())

    # Arrastar o laranja na vista frontal: o ímã puxa para alinhar à direita de B; com Shift, não puxa.
    fake._set_side(encostar.RIGHT)
    fake._set_gap_typed("0")
    view = fake.view_front
    lo = box_a(fake)[0]
    start = view.to_screen((lo[0] + 0.01, lo[2] + 0.01))
    fake._drag_begin('front', start)
    target = view.to_screen((bb[1][0] + 0.003 + 0.01, lo[2] + 0.3 + 0.01))
    fake._drag_move(target, shift=False)
    check("arraste com ímã encosta no lado de B", close(box_a(fake)[0][0], bb[1][0]) and fake.side is None,
          (box_a(fake)[0][0], bb[1][0], fake.side))
    check("arraste mostra a guia do ímã", bool(fake.guides), fake.guides)
    fake._drag_move(target, shift=True)
    check("Shift solta o ímã", not close(box_a(fake)[0][0], bb[1][0], 1e-3), box_a(fake)[0][0])
    fake._drag_end()

    # Clique fora do laranja na planta escolhe o lado.
    plan = fake.view_plan
    front_px = plan.to_screen(((bb[0][0] + bb[1][0]) / 2, bb[0][1] - 2.0))
    fake._drag_begin('plan', front_px)
    fake._drag_end()
    check("clique abaixo de B na planta escolhe Na frente", fake.side == encostar.FRONT, fake.side)

    # Encostar sem Grudar: nada fica grudado; com Grudar, A fica grudado em B na face da frente.
    fake.glue = False
    fake._confirm(ctx)
    check("Encostar sem Grudar não gruda", not a.btm_stick.is_stuck)
    a, b = scene()
    fake = dialog(a, b)
    fake._set_side(encostar.LEFT)
    fake.glue = True
    result = fake._confirm(ctx)
    env.settle()
    check("Encostar com Grudar gruda A em B, na face do lado", result == {'FINISHED'} and a.btm_stick.is_stuck
          and a.btm_stick.host == b and a.btm_stick.face == 'NEG_X',
          (a.btm_stick.is_stuck, a.btm_stick.host, a.btm_stick.face))
    offset = a.matrix_world.translation - b.matrix_world.translation
    b.location.z += 0.5
    env.settle()
    moved = a.matrix_world.translation - b.matrix_world.translation
    check("Grudado: mover B leva A junto", (moved - offset).length < 1e-3, (offset, moved))

    # Regressão: Cancelar devolve A como estava.
    a, b = scene()
    before = a.matrix_world.copy()
    parent = a.parent
    fake = dialog(a, b)
    fake._set_side(encostar.TOP)
    fake.cancel(CTX)
    check("Cancelar devolve A à posição e ao pai", a.matrix_world == before and a.parent == parent)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
