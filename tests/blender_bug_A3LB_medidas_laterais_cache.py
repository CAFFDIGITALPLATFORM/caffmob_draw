"""Reprodução e regressão de BUG-20261023-A3LB (#148): as Medidas laterais só recalculam quando a cena muda.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_A3LB_medidas_laterais_cache.py
"""

import sys
import time
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.collision import guard  # noqa: E402
from caffmob_draw.overlays import side_cotas  # noqa: E402

FAILURES = []
ctx = bpy.context
RIGHT = Vector((1.0, 0.0, 0.0))


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def values(items):
    return [(tuple(round(v, 6) for v in s.start), tuple(round(v, 6) for v in s.end), tuple(s)[2]) for s in items]


try:
    env.clean_scene()
    for i in range(12):                       # uma "cozinha" de 12 × 12 caixas
        for j in range(12):
            fx.cube(f"O{i}_{j}", (0.5, 0.5, 0.5), (i * 1.2 + 3.0, j * 1.2 + 3.0, 0.25))
    left = fx.cube("Esquerda", (0.6, 0.6, 0.8), (-1.0, 0.0, 0.4))
    right = fx.cube("Direita", (0.6, 0.6, 0.8), (2.0, 0.0, 0.4))
    item = fx.cube("Item", (0.6, 0.6, 0.8), (0.5, 0.0, 0.4))
    for obj in ctx.scene.objects:
        obj.select_set(obj == item)
    ctx.view_layer.objects.active = item
    fx.settle()

    calls = [0]
    real_refresh = guard._index.refresh

    def counting(*args, **kwargs):
        calls[0] += 1
        return real_refresh(*args, **kwargs)
    guard._index.refresh = counting
    first = side_cotas.specs(ctx, RIGHT)
    before = calls[0]
    t0 = time.perf_counter()
    for _ in range(20):
        again = side_cotas.specs(ctx, RIGHT)
    per_draw = (time.perf_counter() - t0) / 20 * 1000
    guard._index.refresh = real_refresh
    print(f"MEDIDA: {per_draw:.3f} ms por desenho repetido, {len(ctx.scene.objects)} objetos", flush=True)
    check("cotas calculadas dos dois lados", len(first) == 2, values(first))
    check("reprodução: desenhar de novo sem mudança não recalcula", calls[0] == before, (before, calls[0]))
    check("o resultado repetido é igual", values(again) == values(first))

    right.location.x = 1.6
    fx.settle()
    moved = side_cotas.specs(ctx, RIGHT)
    check("mover um obstáculo atualiza as cotas", values(moved) != values(first), values(moved))
    item.location.x = 0.3
    fx.settle()
    check("mover o ativo atualiza as cotas", values(side_cotas.specs(ctx, RIGHT)) != values(moved))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
