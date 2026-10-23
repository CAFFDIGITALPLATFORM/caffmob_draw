"""Reprodução e regressão de BUG-20261023-5O7K (#152): objeto movido por ferramenta assistida (guarda suspenso e
`accept`) tem a caixa atualizada no índice; as medidas do ativo veem a posição nova.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5O7K_vizinho_assistido_atualiza_indice.py
"""

import sys
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


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    env.clean_scene()
    fx.cube("Esquerda", (0.6, 0.6, 0.8), (-1.0, 0.0, 0.4))
    right = fx.cube("Direita", (0.6, 0.6, 0.8), (2.0, 0.0, 0.4))
    item = fx.cube("Item", (0.6, 0.6, 0.8), (0.5, 0.0, 0.4))
    for obj in ctx.scene.objects:
        obj.select_set(obj == item)
    ctx.view_layer.objects.active = item
    fx.settle()
    before = [tuple(s)[2] for s in side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))]
    with guard.suspended():                          # como o Encostar, o ímã e o espelhar
        right.location.x = 1.5
        ctx.view_layer.update()
        guard.accept(right)
    fx.settle()
    after = [tuple(s)[2] for s in side_cotas.specs(ctx, Vector((1.0, 0.0, 0.0)))]
    check("reprodução: a cota da direita vê o vizinho na posição nova", after != before and "400 mm" in after,
          (before, after))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
