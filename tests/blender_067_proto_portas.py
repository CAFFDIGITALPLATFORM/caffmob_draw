"""Protótipo da premissa dos drivers de porta (feature 067, T128; D-25).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_proto_portas.py

Para as três portas do módulo rápido (esquerda, direita e basculante): troca o nome da porta, grava o papel à mão e
abre o módulo. A porta gira para o mesmo lado que antes: o giro vem dos drivers, que apontam para o
Empty pelo objeto, não pelo nome. O nome só é lido pelo construtor (que acha, apaga e recria o que ele criou) e pelo
puxador da basculante; os leitores de fora (classificador, aviso de corte e inspeção) passam aos campos gravados.
"""

import math
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def module(swing):
    assert bpy.ops.caffmob.cabinet_builder(width=0.8, door_swing=swing) == {'FINISHED'}
    root = bpy.context.object
    env.settle()
    return root


def doors(root):
    return [c for c in root.children if c.type == 'MESH']


def angles(root):
    bpy.context.view_layer.update()
    return {d.name: tuple(round(math.degrees(v), 2) for v in d.matrix_world.to_euler()) for d in doors(root)}


def run():
    env.clean_scene()
    for swing in ('LEFT', 'RIGHT', 'DOUBLE', 'FLIP'):
        root = module(swing)
        root.btm_cabinet.door_open = 1.0
        reference = sorted(angles(root).values())
        root.btm_cabinet.door_open = 0.0
        for index, door in enumerate(doors(root)):
            door.name = f"Painel {swing} {index}"
            door['hb_part_role'] = 'TILT_OUT' if swing == 'FLIP' else 'DOOR'
        root.btm_cabinet.door_open = 1.0
        renamed = sorted(angles(root).values())
        check(renamed == reference and any(any(abs(v) > 1 for v in a) for a in renamed),
              f"{swing}: com outro nome a porta gira para o mesmo lado", f"{reference} × {renamed}")
        root.btm_cabinet.door_open = 0.0
        check(all(all(abs(v) < 0.01 or abs(abs(v) - 180) < 0.01 for v in a) for a in angles(root).values()),
              f"{swing}: e fecha", str(angles(root)))
        root.location.x += 1.5


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_proto_portas: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
