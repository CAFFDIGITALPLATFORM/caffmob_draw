"""Reprodução e regressão de BUG-20261022-7KFP (#136): o "Mover Sobre" aceita o objeto solto (torneira importada,
tampo de pedra feito à mão) como objeto movido e como referência, e diz o motivo quando o clique cai no que não se
move.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_7KFP_mover_sobre_objeto_livre.py
"""

import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import group  # noqa: E402
from caffmob_draw.move_over import ops_drag  # noqa: E402
from caffmob_draw.move_over.scene import MoveOver  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


def box_mesh(name, size, location):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = ctx.active_object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


def cabinet(name, x):
    cab = tf.BaseCabinet()
    cab.create(name)
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    cab.obj.location.x = x
    return cab.obj


def opens(a, b):
    try:
        MoveOver(ctx, a, b)
        return True, ""
    except ValueError as exc:
        return False, str(exc)


def drag_report(hit):
    """Roda o `invoke` do arraste com o raio apontando para `hit`; devolve (resultado, relatórios)."""
    reports = []
    fake = types.SimpleNamespace(report=lambda kind, msg: reports.append((set(kind), msg)))
    event = types.SimpleNamespace(mouse_region_x=10, mouse_region_y=10)
    saved = ops_drag.raycast
    ops_drag.raycast = lambda _context, _coord: hit
    try:
        result = ops_drag.BTM_OT_MoveOverDrag.invoke(fake, ctx, event)
    finally:
        ops_drag.raycast = saved
    return result, reports


try:
    env.clean_scene()
    balcao = cabinet("Balcao", 0.0)
    balcao2 = cabinet("Balcao2", 3.0)
    torneira = box_mesh("Kitchen Faucet", (0.06, 0.20, 0.30), (5.0, 0.0, 1.2))
    pedra = box_mesh("Cubo.004", (1.2, 0.6, 0.03), (5.0, 0.0, 0.9))
    env.settle()

    # Reprodução: as combinações do relato.
    for rotulo, a, b in (("torneira sobre a pedra", torneira, pedra),
                         ("torneira sobre o módulo", torneira, balcao),
                         ("módulo sobre a pedra", balcao, pedra)):
        ok, motivo = opens(a, b)
        check(f"reprodução: {rotulo} abre o Mover Sobre", ok, motivo)

    check("o objeto solto move a si mesmo", classify.movable_root(torneira) == torneira,
          getattr(classify.movable_root(torneira), 'name', None))
    check("o objeto solto serve de referência", classify.reference_root(pedra) == pedra,
          getattr(classify.reference_root(pedra), 'name', None))

    # A torneira vai para cima do tampo, sozinha.
    pedra_antes = pedra.matrix_world.copy()
    mo = MoveOver(ctx, torneira, pedra)
    mo.set_gap(2, mo.box_b[1][2] - mo.box_b[0][2])
    env.settle()
    check("a torneira fica apoiada no tampo", close(mo.box_a()[0][2], mo.box_b[1][2]),
          (mo.box_a()[0][2], mo.box_b[1][2]))
    check("o tampo não se move", pedra.matrix_world == pedra_antes)
    mo.restore()

    # Regressão: o que já funcionava continua igual.
    ok, motivo = opens(balcao2, balcao)
    check("regressão: módulo sobre módulo abre", ok, motivo)
    porta = next(o for o in balcao.children_recursive if o.type == 'MESH')
    check("regressão: peça do módulo move o módulo inteiro", classify.movable_root(porta) == balcao,
          getattr(classify.movable_root(porta), 'name', None))
    folha = box_mesh("Folha", (0.75, 0.035, 2.0), (8.0, 0.0, 1.0))
    env.settle()
    grupo = group.create_group([folha], 'PLAIN', "Porta SKP")
    env.settle()
    check("regressão: malha do grupo do SketchUp move o grupo", classify.movable_root(folha) == grupo,
          getattr(classify.movable_root(folha), 'name', None))

    bpy.ops.object.camera_add(location=(0.0, -6.0, 1.5))
    camera = ctx.active_object
    bpy.ops.object.light_add(type='POINT', location=(0.0, 0.0, 3.0))
    luz = ctx.active_object
    check("câmera não se move no Mover Sobre", classify.movable_root(camera) is None)
    check("luz não se move no Mover Sobre", classify.movable_root(luz) is None)

    # O clique no que não se move diz o motivo; o clique no vazio continua silencioso.
    for rotulo, alvo in (("câmera", camera), ("luz", luz)):
        result, reports = drag_report(alvo)
        check(f"clique na {rotulo} encerra com motivo", result == {'FINISHED'} and len(reports) == 1
              and reports[0][0] == {'INFO'} and "Mover Sobre" in reports[0][1], reports)
    result, reports = drag_report(None)
    check("clique no vazio continua silencioso", result == {'FINISHED'} and reports == [], reports)
    check("motivo da torneira é nenhum", classify.move_over_denial(torneira) is None)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
