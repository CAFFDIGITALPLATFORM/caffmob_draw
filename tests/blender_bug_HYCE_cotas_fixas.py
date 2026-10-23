"""Reprodução e regressão de BUG-20261023-HYCE (#151): quatro cotas fixas (esquerda, direita, superior, inferior),
iguais em qualquer vista, com o nome da referência, editáveis no desenho e nas propriedades; editar move o conjunto
pela diferença (RF02 a RF08 da auditoria de cotas fixas).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_HYCE_cotas_fixas.py
"""

import math
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.overlays import side_cotas  # noqa: E402

FAILURES = []
ctx = bpy.context


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def near(a, b, tol=1e-4):
    return a is not None and b is not None and abs(a - b) < tol


def scene():
    env.clean_scene()
    fx.cube("Armário esquerdo", (0.6, 0.6, 0.8), (-1.0, 0.0, 0.5))
    fx.cube("Armário direito", (0.6, 0.6, 0.8), (2.0, 0.0, 0.5))
    fx.cube("Prateleira", (0.6, 0.6, 0.2), (0.5, 0.0, 2.0))
    item = fx.cube("Item", (0.6, 0.6, 0.8), (0.5, 0.0, 0.5))      # x 0,2..0,8; z 0,1..0,9
    handle = fx.cube("Puxador", (0.05, 0.05, 0.2), (0.5, -0.32, 0.5))
    handle.parent = item
    handle.matrix_parent_inverse = item.matrix_world.inverted()
    for obj in ctx.scene.objects:
        obj.select_set(obj == item)
    ctx.view_layer.objects.active = item
    ctx.scene.btm_settings.show_side_dimensions = True
    fx.settle()
    return item, handle


try:
    item, handle = scene()
    views = [Vector((1.0, 0.0, 0.0)), Vector((-1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), Vector((0.3, 0.0, 0.95))]
    labels = [sorted(tuple(s)[2] for s in side_cotas.specs(ctx, v)) for v in views]
    check("reprodução: as mesmas cotas em qualquer vista", all(x == labels[0] for x in labels), labels)
    check("reprodução: quatro cotas", len(labels[0]) == 4, labels[0])
    rec = side_cotas.records(ctx)
    check("esquerda e direita com o nome do vizinho",
          near(rec['LEFT'][0], 0.9) and rec['LEFT'][1] == "Armário esquerdo"
          and near(rec['RIGHT'][0], 0.9) and rec['RIGHT'][1] == "Armário direito", rec)
    check("inferior até o piso e superior até a prateleira",
          near(rec['BOTTOM'][0], 0.1) and near(rec['TOP'][0], 1.0) and rec['TOP'][1] == "Prateleira", rec)

    edit = ctx.scene.btm_selection
    check("propriedades com os mesmos valores", near(edit.cota_esquerda, 0.9) and near(edit.cota_direita, 0.9)
          and near(edit.cota_superior, 1.0) and near(edit.cota_inferior, 0.1),
          (edit.cota_esquerda, edit.cota_direita, edit.cota_superior, edit.cota_inferior))

    size = tuple(item.dimensions)
    child_offset = handle.matrix_world.translation - item.matrix_world.translation
    side_cotas.apply_fixed(ctx, 'LEFT', 0.5)
    fx.settle()
    rec = side_cotas.records(ctx)
    check("editar a esquerda move o conjunto pela diferença", near(rec['LEFT'][0], 0.5) and near(rec['RIGHT'][0], 1.3)
          and near(item.location.x, 0.1), (rec, item.location.x))
    check("sem redimensionar, e o filho acompanha", tuple(item.dimensions) == size
          and (handle.matrix_world.translation - item.matrix_world.translation - child_offset).length < 1e-5)
    edit.cota_superior = 0.5
    fx.settle()
    check("editar a superior pelas propriedades sobe o conjunto", near(side_cotas.records(ctx)['TOP'][0], 0.5)
          and near(item.location.z, 1.0), (side_cotas.records(ctx)['TOP'], item.location.z))
    before = item.matrix_world.copy()
    for bad in (-0.1, math.nan, math.inf):
        try:
            side_cotas.apply_fixed(ctx, 'RIGHT', bad)
            raised = False
        except ValueError:
            raised = True
        check(f"valor inválido ({bad}) não move", raised and item.matrix_world == before)

    # Leitores (desenho e propriedades) só leem o último cálculo.
    real = side_cotas._compute
    side_cotas._compute = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("leitor calculou"))
    try:
        value = edit.cota_esquerda
        drawn = side_cotas.specs(ctx, None, compute=False)
        check("leitores não recalculam", value is not None and len(drawn) == 4)
    except RuntimeError as exc:
        check("leitores não recalculam", False, repr(exc))
    finally:
        side_cotas._compute = real

    # Edição pelo rótulo: o operador confere a identidade e a pose antes de gravar.
    result = bpy.ops.caffmob.fixed_cota_edit('EXEC_DEFAULT', side='RIGHT', value=0.4)
    fx.settle()
    check("rótulo clicado edita o lado certo", result == {'FINISHED'} and near(side_cotas.records(ctx)['RIGHT'][0], 0.4),
          (result, side_cotas.records(ctx)['RIGHT']))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
