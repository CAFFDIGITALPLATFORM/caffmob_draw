"""Fumaça da frente do objeto no Mover Sobre (feature 022) no Blender 5.2, em `--background`.

Cobre: decisão por parede atrás (sem pergunta), ausência de evidência (pergunta), propriedade gravada vencendo,
`yaw = 0` idêntico ao comportamento anterior e o operador `caffmob.move_over_front` gravando e apagando a escolha.
"""

import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))
if not hasattr(bpy.types.Scene, "btm_settings"):
    import _blender_env  # noqa: F401,E402

from caffmob_draw.move_over import frente_core  # noqa: E402
from caffmob_draw.move_over.scene import MoveOver  # noqa: E402

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name if ok else f"{name} :: {detail}")


def clean():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def box(name, location, size, wall=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.dimensions = size
    bpy.context.view_layer.update()
    if wall:
        obj["IS_WALL_BP"] = True
    return obj


def main():
    clean()
    a = box("A_022", (3.0, 0.0, 1.0), (0.8, 0.55, 2.0))
    b = box("B_022", (0.0, 0.0, 1.0), (0.8, 0.55, 2.0))
    wall = box("Parede_022", (0.0, 0.4, 1.35), (4.0, 0.15, 2.7), wall=True)
    bpy.context.view_layer.update()

    mo = MoveOver(bpy.context, a, b)
    check("parede atrás decide a frente", (mo.front_origem, mo.front_ambiguo) == (frente_core.PAREDE, False),
          (mo.front_origem, mo.front_ambiguo))
    check("parede atrás mantém yaw 0", abs(mo.front_yaw) < 1e-6, mo.front_yaw)
    check("yaw 0 devolve o referencial de B", (mo.b_frame.to_euler().z) < 1e-6, mo.b_frame.to_euler().z)
    target = mo._target_matrix()
    check("yaw 0 não move A com delta 0",
          (target.translation - mo.original_matrix.translation).length < 1e-6,
          (target.translation, mo.original_matrix.translation))

    bpy.data.objects.remove(wall, do_unlink=True)
    bpy.context.view_layer.update()
    mo = MoveOver(bpy.context, a, b)
    check("sem parede e sem módulo pergunta", mo.front_ambiguo is True and mo.front_origem == frente_core.EIXO,
          (mo.front_origem, mo.front_ambiguo))

    b["btm_front_yaw"] = 90.0
    mo = MoveOver(bpy.context, a, b)
    check("propriedade gravada vence", mo.front_origem == frente_core.PROPRIEDADE and not mo.front_ambiguo,
          (mo.front_origem, mo.front_ambiguo))
    check("yaw 90 gira o referencial",
          abs(mo.b_frame.to_euler().z - 1.5707963267948966) < 1e-6, mo.b_frame.to_euler().z)
    box_b_size = tuple(mo.box_b[1][i] - mo.box_b[0][i] for i in range(3))
    check("a caixa de B na vista troca largura por profundidade",
          abs(box_b_size[0] - 0.55) < 1e-3 and abs(box_b_size[1] - 0.8) < 1e-3, box_b_size)

    del b["btm_front_yaw"]
    result = bpy.ops.caffmob.move_over_front(b_name=b.name, side='POS_X')
    check("operador grava 90°", result == {'FINISHED'} and abs(b.get("btm_front_yaw", -1) - 90.0) < 1e-6,
          (result, b.get("btm_front_yaw")))
    result = bpy.ops.caffmob.move_over_front(b_name=b.name, side='AXIS')
    check("operador apaga a escolha", result == {'FINISHED'} and "btm_front_yaw" not in b, b.get("btm_front_yaw"))

    clean()
    print(json.dumps({"pass": len(PASS), "fail": len(FAIL), "failures": FAIL}, ensure_ascii=False))
    return 0 if not FAIL else 1


raise SystemExit(main())
