"""Teste de fumaça da seleção e da exclusão por componente (feature 011, T023; RF-01 a RF-07, RF-12).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_011_component_smoke.py

Sala 4 × 3 de paredes de 150 mm com uma porta real (010), um balcão frameless e um OBJ de 5 malhas importado:
- peça → raiz pelo normalizador (maçaneta → porta, pé → grupo do OBJ, frente → balcão no modo Cabinets);
- várias peças → raízes sem repetir; agregado continua dele; modo Parts não sobe;
- interruptor desligado não sobe e fica salvo no arquivo; peça do Alt + clique (isenta) fica;
- excluir a porta pelo X (`caffmob.delete_with_aggregates`) e pelo menu (`delete_door_window`) não deixa peça nem furo.
O disparo do handler pelo clique de verdade, o arraste e a seleção por caixa estão na `blender_011_drag_probe.py`.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.aggregates import group  # noqa: E402
from caffmob_draw.openings import sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import component_select as cs  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def select_only(*objs):
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    for obj in objs:
        obj.select_set(True)
    ctx.view_layer.objects.active = objs[0] if objs else None


def normalized():
    cs.forget()
    cs.on_depsgraph_update(ctx.scene)
    return sorted(o.name for o in ctx.view_layer.objects if o.select_get())


def door_on(wall, x):
    door = oe.make_cage('DOOR')
    door.parent = wall
    door.location = (x, 0.0, 0.0)
    dw.cut_wall(wall, door)
    env.settle()
    sync.sync(ctx, door)
    env.settle()
    return door


def import_chair():
    for name, loc in (("Assento", (0, 0, 0.45)), ("Pe1", (-0.2, -0.2, 0.2)), ("Pe2", (0.2, -0.2, 0.2)),
                      ("Pe3", (-0.2, 0.2, 0.2)), ("Pe4", (0.2, 0.2, 0.2))):
        bpy.ops.mesh.primitive_cube_add(size=0.1, location=loc)
        ctx.active_object.name = name
    for obj in ctx.scene.objects:
        obj.select_set(obj.name in ("Assento", "Pe1", "Pe2", "Pe3", "Pe4"))
    path = os.path.join(tempfile.mkdtemp(), "cadeira.obj")
    assert bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, export_materials=False) == {'FINISHED'}
    for name in ("Assento", "Pe1", "Pe2", "Pe3", "Pe4"):
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    assert bpy.ops.caffmob.import_model(filepath=path, unit='M') == {'FINISHED'}
    return ctx.view_layer.objects.active


def main():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    wall = sorted((o for o in ctx.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)[0]
    door = door_on(wall, 1.0)
    parts = [o for o in door.btm_opening_real.assembly.children_recursive if o.type == 'MESH']
    knob = next((o for o in parts if 'Ferragens da folha' in o.name), parts[-1])

    chair = import_chair()
    members = group.members(chair) if chair is not None else []
    check("OBJ de 5 malhas entra como 1 grupo", group.is_group(chair) and len(members) == 5,
          f"{chair.name if chair else None} {len(members)}")

    base = tf.BaseCabinet()
    base.create("Balcao")
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    cabinet_part = next(o for o in base.obj.children_recursive if o.type == 'MESH')
    fruteira = bpy.data.objects.new("Fruteira", bpy.data.meshes.new("Fruteira"))
    ctx.scene.collection.objects.link(fruteira)
    fruteira.parent = base.obj
    fruteira.btm_aggregate.is_aggregate = True
    env.settle()

    # Peça → raiz.
    select_only(knob)
    check("maçaneta seleciona a porta", normalized() == [door.name], knob.name)
    check("a porta vira a ativa", ctx.view_layer.objects.active == door)
    select_only(members[1])
    check("pé seleciona o grupo do OBJ", normalized() == [chair.name])
    select_only(knob, parts[0], members[2])
    check("várias peças → raízes sem repetir", normalized() == sorted([door.name, chair.name]))
    select_only(fruteira)
    check("agregado continua dele", normalized() == ["Fruteira"])

    # Armário pelo modo de seleção.
    hb_frameless = ctx.scene.hb_frameless
    hb_frameless.frameless_selection_mode = 'Cabinets'
    select_only(cabinet_part)
    check("modo Cabinets: peça seleciona o balcão", normalized() == [base.obj.name], cabinet_part.name)
    # Feature 012: os modos de seleção herdados só existem no modo de suporte (show_legacy_libraries).
    from caffmob_draw.legacy import gate
    original_gate, gate.legacy_ui = gate.legacy_ui, (lambda context=None: True)
    try:
        hb_frameless.frameless_selection_mode = 'Parts'
        select_only(cabinet_part)
        check("modo Parts (suporte): peça fica", normalized() == [cabinet_part.name])
        hb_frameless.frameless_selection_mode = 'Cabinets'
    finally:
        gate.legacy_ui = original_gate

    # Alt + clique (isenção) e interruptor.
    select_only(knob)
    cs.set_exempt(ctx, {knob.name})
    check("peça isenta (Alt + clique) fica", normalized() == [knob.name])
    cs.set_exempt(ctx, set())
    ctx.scene.btm_component_select = False
    select_only(knob)
    check("interruptor desligado: peça fica", normalized() == [knob.name])
    path = os.path.join(tempfile.mkdtemp(), "componente.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    bpy.ops.wm.open_mainfile(filepath=path)
    check("interruptor desligado fica salvo", bpy.context.scene.btm_component_select is False)
    bpy.context.scene.btm_component_select = True
    return path


def delete_part():
    scene = bpy.context.scene
    wall = sorted((o for o in scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)[0]
    door = next(o for o in scene.objects if o.get('IS_ENTRY_DOOR_BP'))
    names = [door.name] + [o.name for o in door.children_recursive]
    check("porta real com peças em vários níveis", len(names) > 6, str(len(names)))
    with bpy.context.temp_override(selected_objects=[door], active_object=door, object=door):
        result = bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT')
    left = [n for n in names if n in bpy.data.objects]
    check("X apaga a porta inteira", result == {'FINISHED'} and not left, str(left))
    check("e o furo da parede", not any(m.type == 'BOOLEAN' for m in wall.modifiers),
          str([m.name for m in wall.modifiers]))

    other = door_on(wall, 2.4)
    names = [other.name] + [o.name for o in other.children_recursive]
    with bpy.context.temp_override(selected_objects=[other], active_object=other, object=other):
        result = bpy.ops.caffmob_doors_windows.delete_door_window('EXEC_DEFAULT')
    left = [n for n in names if n in bpy.data.objects]
    check("Delete Door/Window também apaga em profundidade", result == {'FINISHED'} and not left, str(left))
    check("a parede fica sem booleano de porta", not any(m.type == 'BOOLEAN' for m in wall.modifiers),
          str([m.name for m in wall.modifiers]))

    # BUG-20261011-7DHT (pergunta 5): X numa parede é do plugin e usa remove_wall; o que está nela fica no lugar.
    cabinet = next(o for o in scene.objects if o.get('IS_FRAMELESS_CABINET_CAGE'))
    where = cabinet.matrix_world.translation.copy()
    with bpy.context.temp_override(selected_objects=[wall], active_object=wall, object=wall):
        poll = bpy.ops.caffmob.delete_with_aggregates.poll()
        result = bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT') if poll else None
    check("X numa parede usa o caminho do plugin", poll and result == {'FINISHED'}, str(result))
    check("e o balcão fica onde estava", cabinet.name in bpy.data.objects
          and (cabinet.matrix_world.translation - where).length < 1e-6)


try:
    main()
    delete_part()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_011_component_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
