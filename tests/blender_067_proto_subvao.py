"""Protótipo (feature 067, T011; D-23): a frente gerada pelo caminho do subvão, com dois subvãos do módulo rápido
convivendo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_proto_subvao.py

Uma divisória vertical parte o módulo em dois subvãos. `bridge.library_opening` devolve o próprio caminho de cada
subvão (não o vão que contém o centro), e a frente vai no retângulo dele: porta à esquerda num, quatro gavetas no
outro. Trocar a frente de um não mexe no outro. O vão-raiz continua sendo o módulo inteiro.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.cabinet_editor import bridge  # noqa: E402
from caffmob_draw.customize.adapters import btm  # noqa: E402
from caffmob_draw.geometry import subspace_fronts  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def split_module():
    assert bpy.ops.caffmob.cabinet_builder(width=1.0, door_swing='NONE') == {'FINISHED'}
    root = bpy.context.object
    env.settle()
    ctx = bpy.context
    roots = bridge.division_context(ctx, root)[0]
    root_path = next(iter(roots))
    bridge.add_division(ctx, root, {'space': root_path, 'orientation': 'VERTICAL'})
    boxes = btm.space_boxes(ctx, root)
    subs = sorted(p for p in boxes if p not in ('module', root_path))
    return root, root_path, subs, boxes


def run():
    env.clean_scene()
    ctx = bpy.context
    root, root_path, subs, boxes = split_module()
    print("SUBVAOS", root_path, subs, flush=True)
    check(len(subs) == 2, "a divisória cria dois subvãos", str(subs))
    check(bridge.library_opening(ctx, root, root_path) == "module", "o vão-raiz é o módulo inteiro")
    left, right = subs
    check(bridge.library_opening(ctx, root, left) == left and bridge.library_opening(ctx, root, right) == right,
          "cada subvão é o próprio vão da biblioteca (não o que contém o centro)")
    check(bridge.edit(ctx, root, 'FRONT', {'path': left, 'front': 'DOOR_LEFT'}) == [], "porta no subvão")
    bridge.edit(ctx, root, 'FRONT', {'path': right, 'front': 'DRAWERS', 'drawer_count': 4})
    door = subspace_fronts.fronts_of(root, left)
    drawers = [o for o in subspace_fronts.fronts_of(root, right) if o.get('hb_part_role') == 'DRAWER_FRONT']
    check(len([o for o in door if o.get('hb_part_role') == 'DOOR']) == 1, "um subvão com porta", str(len(door)))
    check(len(drawers) == 4, "o outro com quatro gavetas", str(len(drawers)))
    bpy.context.view_layer.update()
    lbox = boxes[left]
    door_obj = next(o for o in door if o.get('hb_part_role') == 'DOOR')
    x = door_obj.matrix_world.translation.x
    check(lbox[0][0] - 0.01 <= x <= lbox[1][0], "a porta fica no retângulo do subvão esquerdo", f"{x} {lbox}")
    names = sorted(o.name for o in subspace_fronts.fronts_of(root, right))
    bridge.edit(ctx, root, 'FRONT', {'path': left, 'front': 'DOUBLE_DOORS'})
    check(sorted(o.name for o in subspace_fronts.fronts_of(root, right)) == names,
          "trocar a frente de um subvão não mexe no outro")
    read = btm.read(root)
    check((read.opening(left).front, read.opening(right).front, read.opening(right).drawer_count)
          == ('DOUBLE_DOORS', 'DRAWERS', 4), "o Spec lê a frente de cada subvão pelo caminho",
          str([(o.path, o.front, o.drawer_count) for o in read.openings]))


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_proto_subvao: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
