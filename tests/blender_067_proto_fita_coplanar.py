"""Protótipo da premissa 6 (feature 067, T010; D-21): bordas coplanares de chapas empilhadas, com tolerância de
0,1 mm, no referencial do componente girado.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_proto_fita_coplanar.py

Três chapas de 15 mm empilhadas viram um armário autoral; o componente é girado 37° e 90° e escalado. As caixas das
peças levadas ao referencial do dono (`edgeband/pieces.boxes`) dão uma faixa de 45 mm na frente em todos os casos, e
uma chapa deslocada 0,5 mm vira faixa própria (fora da tolerância).
"""

import math
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
from caffmob_draw.aggregates import ops_authored  # noqa: E402
from caffmob_draw.edgeband import core, pieces  # noqa: E402

FAILURES = []
T = 0.015


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def component(shift=0.0):
    root = bpy.data.objects.new("Engrossado", None)
    bpy.context.collection.objects.link(root)
    plates = [authored_env.cube(f"Chapa {i}", (0.6, 0.4, T), (0, (shift if i == 1 else 0.0), T / 2 + i * T), root)
              for i in range(3)]
    env.settle()
    ops_authored.adopt(root, [root] + plates)
    return root, plates


def front_bands(root):
    found = pieces.boxes(root, create_uids=True)
    bands = core.merge(core.exposed([box for box, _obj in found]))
    return [b for b in bands if b.axis == 1 and b.sign < 0]


def run():
    env.clean_scene()
    root, _plates = component()
    for label, matrix in (("parado", Matrix.Identity(4)),
                          ("girado 37°", Matrix.Rotation(math.radians(37), 4, 'Z')),
                          ("girado 90° em X", Matrix.Rotation(math.radians(90), 4, 'X')),
                          ("escalado 2×", Matrix.Diagonal((2.0, 2.0, 2.0, 1.0)))):
        root.matrix_world = Matrix.Translation((1.0, 2.0, 0.0)) @ matrix
        bpy.context.view_layer.update()
        bands = front_bands(root)
        widths = [round(b.size()[1], 6) for b in bands]
        check(len(bands) == 1 and abs(bands[0].size()[1] - 0.045) < 1e-6, f"{label}: uma faixa de 45 mm na frente",
              str(widths))
    env.clean_scene()
    root, _plates = component(shift=0.0005)
    bpy.context.view_layer.update()
    check(len(front_bands(root)) == 3, "chapa deslocada 0,5 mm fica fora da tolerância")
    env.clean_scene()
    root, _plates = component(shift=0.00008)
    bpy.context.view_layer.update()
    check(len(front_bands(root)) == 1, "0,08 mm fica dentro da tolerância (uma faixa)")


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_proto_fita_coplanar: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
