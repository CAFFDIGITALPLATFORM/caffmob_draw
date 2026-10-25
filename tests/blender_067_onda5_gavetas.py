"""Gavetas do módulo rápido e frentes por subvão (feature 067, T030; RF-103, RF-104).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda5_gavetas.py

- DRAWERS no módulo gera 4 caixas reais (frente e caixa) e `Spec.front == DRAWERS` com a contagem 4;
- pedido não suportado (painel fixo, 9 gavetas) termina em recusa, sem mudar a frente; o operador devolve CANCELLED;
- dois subvãos, um com porta e outro com quatro gavetas, convivem; trocar um não altera o outro;
- a gaveta corre em profundidade (mecanismo DRAWER), não em X;
- M-06: instantâneo antigo sem o caminho do vão é lido pelo vão atual e regravado com o caminho.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
from caffmob_draw import mechanisms  # noqa: E402
from caffmob_draw.cabinet_editor import bridge  # noqa: E402
from caffmob_draw.customize.adapters import btm  # noqa: E402
from caffmob_draw.geometry import subspace_fronts  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def drawers(root, path="module"):
    return [o for o in subspace_fronts.fronts_of(root, path) if o.get('hb_part_role') == 'DRAWER_FRONT']


def run():
    env.clean_scene()
    ctx = bpy.context
    assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='LEFT') == {'FINISHED'}
    root = ctx.object
    env.settle()
    check(btm.set_front(ctx, root, root, 'DRAWERS', 4) == [], "DRAWERS aceito no módulo")
    fronts = drawers(root)
    boxes = [c for f in fronts for c in f.children if c.get('hb_part_role') == 'CLOSET_DRAWER_BOX']
    check(len(fronts) == 4 and len(boxes) == 4 and all(len(b.data.polygons) == 24 for b in boxes),
          "4 gavetas com caixa real (fundo, laterais e traseira)", f"{len(fronts)} {len(boxes)}")
    item = btm.read(root).opening("module")
    check((item.front, item.drawer_count) == ('DRAWERS', 4), "Spec.front == DRAWERS com a contagem 4",
          f"{item.front} {item.drawer_count}")
    check(root.btm_cabinet.door_swing == 'NONE', "as portas do construtor saem")

    for front, count in (('PANEL', 1), ('DRAWERS', 9)):
        refused = btm.set_front(ctx, root, root, front, count)
        item = btm.read(root).opening("module")
        check(refused and (item.front, item.drawer_count) == ('DRAWERS', 4),
              f"{front} × {count}: recusa e a frente fica", str(refused))
    authored_env.select([root])
    with ctx.temp_override(active_object=root, object=root):
        try:
            result = bpy.ops.caffmob.customize_set_front('EXEC_DEFAULT', path="module", front='DRAWERS',
                                                         drawer_count=4)
        except (TypeError, RuntimeError) as exc:
            result = {'EXC', str(exc)}
    check(result == {'FINISHED'}, "o operador Personalizar aceita as gavetas", str(result))

    fronts = drawers(root)                         # o operador refez as gavetas
    boxes = [c for f in fronts for c in f.children if c.get('hb_part_role') == 'CLOSET_DRAWER_BOX']
    mech = mechanisms.of(fronts[0])
    check(mech is not None and mech.kind == mechanisms.DRAWER, "a gaveta tem o mecanismo DRAWER")
    bpy.context.view_layer.update()
    before = fronts[0].matrix_world.translation.copy()
    mech.set_fraction(1.0)
    bpy.context.view_layer.update()
    after = fronts[0].matrix_world.translation.copy()
    moved = after - before
    check(moved.y < -0.1 and abs(moved.x) < 1e-4, "a gaveta corre em profundidade, não em X", str(tuple(moved)))
    box_moved = boxes[0].matrix_world.translation.y
    mech.set_fraction(0.0)

    # Dois subvãos: porta e gavetas convivem.
    assert bpy.ops.caffmob.cabinet_builder(width=1.0, door_swing='NONE') == {'FINISHED'}
    split = ctx.object
    split.location.x = 2.0
    env.settle()
    root_path = next(iter(bridge.division_context(ctx, split)[0]))
    bridge.add_division(ctx, split, {'space': root_path, 'orientation': 'VERTICAL'})
    left, right = sorted(p for p in btm.space_boxes(ctx, split) if p not in ('module', root_path))
    for path, front, count in ((left, 'DOOR_LEFT', 1), (right, 'DRAWERS', 4)):
        target = bridge.library_opening(ctx, split, path)
        bridge.edit(ctx, split, 'FRONT', {'path': target, 'front': front, 'drawer_count': count})
    check(len(drawers(split, right)) == 4 and len(subspace_fronts.fronts_of(split, left)) >= 1,
          "dois subvãos: porta e quatro gavetas convivem")
    names = sorted(o.name for o in subspace_fronts.fronts_of(split, left))
    bridge.edit(ctx, split, 'FRONT', {'path': right, 'front': 'DRAWERS', 'drawer_count': 2})
    check(len(drawers(split, right)) == 2 and sorted(o.name for o in subspace_fronts.fronts_of(split, left)) == names,
          "trocar as gavetas não altera a porta do outro subvão")
    _ = box_moved

    # M-06: instantâneo do editor sem caminho de vão.
    old = {'openings': [{'path': '', 'front': 'DRAWERS', 'drawer_count': 2}, {'path': 's9.z', 'front': 'OPEN'}]}
    count = bridge.migrate_paths(ctx, root, btm, old)
    check(count == 2 and [o['path'] for o in old['openings']] == ['module', 'module'],
          "M-06: vão sem caminho (ou que não existe mais) regravado com o vão atual", str(old))
    check(bridge.migrate_paths(ctx, root, btm, old) == 0, "M-06 de novo não regrava")


try:
    run()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda5_gavetas: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
