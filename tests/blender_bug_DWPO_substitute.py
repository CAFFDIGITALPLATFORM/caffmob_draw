"""Reprodução e regressão de BUG-20261012-DWPO: o Substituir ignora as peças vazias do módulo antigo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_DWPO_substitute.py

- a caixa do Substituir para um balcão frameless em x = 5 fica em 5,0 a 5,914 (sem `Top`/`Sink Apron` vazios na origem);
- o módulo novo encosta no mesmo canto do antigo em relação a B (move_over RN-19).
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import library_io  # noqa: E402
from caffmob_draw.move_over import ops_substitute  # noqa: E402
from caffmob_draw.move_over.scene import _frame  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cabinet(cls, name, x):
    item = cls()
    item.create(name)
    item.obj.location.x = x
    hb_utils.run_calc_fix_until_stable(ctx, item.obj)
    return item.obj


def main():
    env.clean_scene()
    b = cabinet(tf.BaseCabinet, "Balcao", 5.0)
    a = cabinet(tf.BaseCabinet, "Antigo", 7.0)
    env.settle()
    lo, hi = ops_substitute._tree_box(Matrix.Identity(4), b)
    check("DWPO: a caixa do balcão não vai até a origem", abs(lo[0] - 5.0) < 1e-3 and abs(hi[0] - 5.914) < 1e-3,
          f"x {lo[0]:.3f} a {hi[0]:.3f}")
    saved = cabinet(tf.UpperCabinet, "Aereo DWPO", 12.0)
    env.settle()
    ctx.view_layer.objects.active = saved
    with ctx.temp_override(active_object=saved, object=saved):
        assert bpy.ops.caffmob.module_save(module_name="Aéreo DWPO", category="Testes", thumbnail=False) == {'FINISHED'}
    entry = next(e for e in library_io.list_modules() if e["name"] == "Aéreo DWPO")
    frame_inv = _frame(b).inverted()
    left_a = ops_substitute._tree_box(frame_inv, a)[0][0]
    new, _warnings = ops_substitute.substitute(ctx, a, b, entry)
    env.settle()
    left_new = ops_substitute._tree_box(frame_inv, new)[0][0]
    check("DWPO: o módulo novo encosta no mesmo canto do antigo", abs(left_new - left_a) < 1e-3,
          f"antigo {left_a:.3f} novo {left_new:.3f}")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_DWPO_substitute: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
