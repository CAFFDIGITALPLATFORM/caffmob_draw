"""Ensaio real da onda 2. Em janela também prova Esc e Desfazer/Refazer em um passo."""

import math
import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
from caffmob_draw import hb_types, identity_migration  # noqa: E402
from caffmob_draw.aggregates import collision, leaf  # noqa: E402
from caffmob_draw.openings import ops_transfer as move, sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.walls2d import apply, model  # noqa: E402

ctx = bpy.context
FAILURES = []
OUT = Path(__file__).resolve().parents[1] / 'test-results'
OUT.mkdir(exist_ok=True)


def check(label, ok, detail=''):
    print(('OK ' if ok else 'FALHA ') + label, detail, flush=True)
    if not ok:
        FAILURES.append(label)


def active(obj):
    for o in ctx.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    ctx.view_layer.objects.active = obj


def scene():
    env.clean_scene()
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4, 3)]))
    env.settle()
    walls = sorted((o for o in ctx.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)
    source = walls[0]
    target = next(w for w in walls if abs(math.cos(w.rotation_euler.z - source.rotation_euler.z)) < 0.01)
    door = oe.make_cage(leaf_w=0.88)
    door.name = 'Portal de ensaio'
    door.parent = source
    door.location = (1, 0, 0)
    dw.cut_wall(source, door)
    env.settle()
    sync.sync(ctx, door)
    env.settle()
    active(door)
    door.btm_opening_real.angle = 90
    env.settle()
    return door, source, target


def booleans(door):
    return [(o, m) for o in ctx.scene.objects for m in o.modifiers if m.type == 'BOOLEAN' and m.object == door]


def run():
    door, source, target = scene()
    check('folha aberta a 90° antes de transferir', abs(door.btm_opening_real.angle - 90) < 0.1)
    before = sync._dims(door)
    hb_types.GeoNodeWall(target).set_input('Thickness', 0.23)
    finish = bpy.data.materials.new('Acabamento autoral do ensaio')
    body = next(o for o in door.children_recursive if o.type == 'MESH' and o.get('btm_opening_role') == 'LEAF')
    body.data.materials[0] = finish
    env.settle()
    handle = next(o for o in door.children_recursive if o.type == 'MESH' and 'Ferragens da folha' in o.name)
    active(handle)
    check('operador encontra porta pela maçaneta', bpy.ops.caffmob.door_move_to_wall.poll())
    result = bpy.ops.caffmob.door_move_to_wall(target=target.name, distance=1200)
    env.settle()
    check('transferência para parede perpendicular', result == {'FINISHED'} and door.parent == target)
    cuts = booleans(door)
    check('um Boolean só e na parede nova', len(cuts) == 1 and cuts[0][0] == target)
    check('recorte usa uid', cuts[0][1].name == 'Boolean_' + door.btm_opening_real.uid[:8])
    check('medidas e 90° preservados', max(abs(before[i]-sync._dims(door)[i]) for i in (0, 2)) < 0.0001
          and abs(door.btm_opening_real.angle - 90) < 0.1)
    check('espessura adaptada à nova parede', abs(sync._dims(door)[1] - 0.23) < 1e-6)
    check('acabamento mantido ao reconstruir por espessura', any(finish in list(o.data.materials)
          for o in door.children_recursive if o.type == 'MESH'))
    # Uma falha de reconstrução não deixa a porta sem o recorte de origem.
    real_sync = sync.sync
    calls = []

    def fail_once(*args, **kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError('falha de montagem simulada')
        return real_sync(*args, **kwargs)

    sync.sync = fail_once
    try:
        active(door)
        result = bpy.ops.caffmob.door_move_to_wall(target=source.name, distance=1200)
        check('falha na confirmação restaura vínculo, ângulo e recorte', result == {'CANCELLED'}
              and door.parent == target and len(booleans(door)) == 1 and booleans(door)[0][0] == target
              and abs(door.btm_opening_real.angle - 90) < 0.1)
    finally:
        sync.sync = real_sync
    # A folha centralizada na parede de 230 mm encosta nela aos 117,25°; o ensaio de 120° usa a de 150 mm.
    active(door)
    check('retorno à parede de 150 mm preserva abertura',
          bpy.ops.caffmob.door_move_to_wall(target=source.name, distance=1200) == {'FINISHED'}
          and abs(door.btm_opening_real.angle - 90) < 0.1)
    source, target = target, source
    door.btm_opening_real.swing_limit = 120
    env.settle()
    check('mudar limite preserva graus', abs(door.btm_opening_real.angle - 90) < 0.1)
    active(door)
    check('120° aceito', bpy.ops.caffmob.door_set_angle(degrees=120) == {'FINISHED'}
          and abs(door.btm_opening_real.angle - 120) < 0.1, str((door.btm_opening_real.angle,
              [(o.name,o.btm_aggregate.contact_name) for o in sync.door_leaves(door)])))
    check('130° recusado', bpy.ops.caffmob.door_set_angle(degrees=130) == {'CANCELLED'}
          and abs(door.btm_opening_real.angle - 120) < 0.1)
    door.btm_opening_real.angle = 130
    check('digitação RNA também recusa 130°', abs(door.btm_opening_real.angle - 120) < 0.1)
    door.btm_opening_real.angle = 90
    uid = door.btm_opening_real.uid
    door.name, target.name = 'Portal renomeado', 'Parede renomeada'
    for i, obj in enumerate(door.children_recursive):
        obj.name = 'Peça renomeada ' + str(i)
    for operator, axis in ((bpy.ops.caffmob_doors_windows.flip_door_hand, 1),
                           (bpy.ops.caffmob_doors_windows.flip_door_swing, 2)):
        before_swing = sync._swing(door)
        active(next(o for o in door.children_recursive if o.type == 'MESH'))
        result = operator()
        after_swing = sync._swing(door)
        check('flip distinto por qualquer peça e símbolo renomeado ' + str(axis),
              result == {'FINISHED'} and after_swing[axis] != before_swing[axis]
              and all(after_swing[i] == before_swing[i] for i in (1, 2) if i != axis))
        operator()
    dw.cut_wall(target, door)
    check('renomear e recortar não duplica Boolean', len(booleans(door)) == 1)
    sync.sync(ctx, door, force=True)
    env.settle()
    check('refazer após renomear mantém abertura por índice', abs(door.btm_opening_real.angle - 90) < 0.1)
    identity_migration.migrate()
    identity_migration.migrate()
    check('migração idempotente', uid == door.btm_opening_real.uid and len(booleans(door)) == 1)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / 'onda2-porta.blend'))
    bpy.ops.wm.open_mainfile(filepath=str(OUT / 'onda2-porta.blend'))
    door = bpy.data.objects['Portal renomeado']
    check('reabrir mantém vínculo e abertura', door.btm_opening_real.host_wall == door.parent
          and door.btm_opening_real.uid == uid and abs(door.btm_opening_real.angle - 90) < 0.1)
    # Duplicata em dados, equivalente ao uid copiado por Shift+D; a migração mantém o mais antigo.
    copy = door.copy()
    ctx.scene.collection.objects.link(copy)
    identity_migration.migrate()
    check('uid duplicado renovado no dono mais recente', copy.btm_opening_real.uid != uid
          and door.btm_opening_real.uid == uid)
    bpy.data.objects.remove(copy, do_unlink=True)
    active(door)
    # Uma caixa física no destino bloqueia a implantação inteira, inclusive folha aberta.
    source = next(o for o in ctx.scene.objects if o.get('IS_WALL_BP') and o != door.parent)
    fit, _ = move.implantation(door, source, 'START', 1000)
    bpy.ops.mesh.primitive_cube_add(size=1, location=source.matrix_world @ __import__('mathutils').Vector((1.4, 0, 1)))
    obstacle = ctx.object
    obstacle.name = 'Obstáculo do destino'
    env.settle()
    active(door)
    parent = door.parent
    check('destino penetrado bloqueia sem mudar recortes',
          bpy.ops.caffmob.door_move_to_wall(target=source.name, distance=1000) == {'CANCELLED'}
          and door.parent == parent and len(booleans(door)) == 1)
    bpy.data.objects.remove(obstacle, do_unlink=True)
    # Colisão da folha continua ativa depois da transferência.
    sash = sync.door_leaves(door)[0]
    door.btm_opening_real.angle = 0
    env.settle()
    tester = collision.Tester(sash)
    center = sum(tester.corners_at(0.5), __import__('mathutils').Vector()) / 8
    bpy.ops.mesh.primitive_cube_add(size=0.25, location=center)
    env.settle()
    collision.invalidate()
    door.btm_opening_real.angle = 120
    env.settle()
    check('folha transferida para no contato', 0 < door.btm_opening_real.angle < 120,
          str(door.btm_opening_real.angle))


def window_script():
    win = ctx.window_manager.windows[0]
    win.event_simulate('ESC', 'PRESS', x=10, y=10)
    win.event_simulate('ESC', 'RELEASE', x=10, y=10)
    yield 0.5
    door, source, target = scene()
    door_name, source_name, target_name = door.name, source.name, target.name
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    bpy.ops.ed.undo_push(message='Antes da transferência')
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.door_move_to_wall('EXEC_DEFAULT', True, target=target.name, distance=700)
    yield 0.5
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield 0.5
    door = bpy.data.objects[door_name]
    check('um Desfazer restaura parede e recorte antigos', door.parent.name == source_name
          and len(booleans(door)) == 1 and booleans(door)[0][0].name == source_name)
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.redo()
    yield 0.5
    door = bpy.data.objects[door_name]
    check('Refazer restaura destino e abertura', door.parent.name == target_name
          and abs(door.btm_opening_real.angle - 90) < 0.1)
    active(door)
    counts = (len(bpy.data.objects), len(bpy.data.materials), len(booleans(door)))
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob.door_move_to_wall('INVOKE_DEFAULT')
    yield 0.5
    win.event_simulate('ESC', 'PRESS', x=region.x+100, y=region.y+100)
    win.event_simulate('ESC', 'RELEASE', x=region.x+100, y=region.y+100)
    yield 0.5
    check('Esc não deixa objeto, material ou modificador', counts ==
          (len(bpy.data.objects), len(bpy.data.materials), len(booleans(door))) and not move._live)


def finish():
    print('blender_066_door_transfer: ' + ('OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)), flush=True)


if bpy.app.background:
    try:
        run()
    except Exception:
        traceback.print_exc()
        FAILURES.append('exceção')
    finish()
    sys.exit(bool(FAILURES))
else:
    gen = window_script()

    def tick():
        try:
            return next(gen)
        except StopIteration:
            pass
        except Exception:
            traceback.print_exc()
            FAILURES.append('exceção janelada')
        finish()
        os._exit(bool(FAILURES))

    bpy.app.timers.register(tick, first_interval=2)
