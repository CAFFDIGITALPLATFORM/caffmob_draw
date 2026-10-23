"""Regressão: o "Mover Sobre" aceita o modelo importado do SketchUp (grupo de peças `btm_group`, Empty com malhas e
subgrupos, como `aggregates/skp_build` monta) e o move para o lado e para cima/baixo de um módulo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_skp_mover_sobre.py
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import group  # noqa: E402
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


try:
    env.clean_scene()
    cabinet = tf.BaseCabinet()
    cabinet.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, cabinet.obj)
    b = cabinet.obj

    # Porta do SketchUp: folha (grupo) com uma ferragem (subgrupo), dentro de um contêiner sem malha.
    leaf = box_mesh("Folha", (0.75, 0.035, 2.0), (3.0, 0.0, 1.0))
    knob = box_mesh("Macaneta", (0.05, 0.10, 0.05), (3.3, -0.05, 1.0))
    env.settle()
    knob_group = group.create_group([knob], 'PLAIN', "Ferragem")
    leaf_group = group.create_group([leaf], 'PLAIN', "Porta")
    knob_group.parent = leaf_group
    knob_group.matrix_parent_inverse = leaf_group.matrix_world.inverted()
    env.settle()

    check("clique na ferragem acha o grupo de topo", classify.movable_root(knob) == leaf_group,
          getattr(classify.movable_root(knob), 'name', None))
    check("clique na folha acha o grupo de topo", classify.movable_root(leaf) == leaf_group)
    solto = box_mesh("Solto", (1, 1, 1), (9, 9, 0))
    check("objeto solto move a si mesmo (BUG-20261022-7KFP)", classify.movable_root(solto) == solto)

    mo = MoveOver(ctx, knob, b)
    lo, hi = mo.a_local_box
    size = [round(hi[i] - lo[i], 3) for i in range(3)]
    check("caixa do grupo = malhas dentro dele", size[0] >= 0.75 and size[2] >= 2.0, size)

    mo.set_gap(0, 0.10)             # ao lado (à direita) do balcão, com 10 cm
    env.settle()
    check("lado: 10 cm à direita do balcão", close(mo.gaps()[0], 0.10), mo.gaps())
    box_a, box_b = mo.box_a(), mo.box_b
    check("lado: à direita", box_a[0][0] >= box_b[1][0] - 1e-4)

    mo.set_gap(2, box_b[1][2] - box_b[0][2])     # em cima do balcão
    env.settle()
    check("cima: base do grupo no topo do balcão", close(mo.box_a()[0][2], mo.box_b[1][2]),
          (mo.box_a()[0][2], mo.box_b[1][2]))
    world_leaf_z = min((leaf.matrix_world @ v.co).z for v in leaf.data.vertices)
    world_top = max((b.matrix_world @ __import__('mathutils').Vector(c)).z for c in b.bound_box)
    check("cima: a malha da folha subiu junto", close(world_leaf_z, world_top, 2e-3), (world_leaf_z, world_top))

    mo.set_gap(2, -2.5)              # abaixo
    env.settle()
    check("baixo: topo do grupo abaixo do balcão", mo.box_a()[1][2] <= mo.box_b[0][2] + 1e-4)

    mo.restore()
    env.settle()
    check("cancelar devolve a posição", close(leaf_group.matrix_world.translation.x, 3.0, 1e-3))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHOU " + ", ".join(FAILURES) if FAILURES else "TUDO OK", flush=True)
sys.exit(1 if FAILURES else 0)
