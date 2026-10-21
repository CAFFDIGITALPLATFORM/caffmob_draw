"""T023: folha composta, referencial, pivô único, contato e fechamento sem deriva."""
import math
import os
import sys
import tempfile
import traceback
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as ae
from caffmob_draw.aggregates import leaf, ops_authored_leaf as authored
from caffmob_draw.aggregates.ops_members import set_member
from caffmob_draw.inspection import fronts
from caffmob_draw.inspection.adapters.aggregate_leaf import AggregateLeafFront
from caffmob_draw import identity_migration
from caffmob_draw.selection import component_select


def make_parts(root, shift=0):
    # Folha à frente da carcaça, com puxador e quatro perfis.
    parts = [ae.cube('Vidro', (.26, .006, 2.4), (shift, -.205, 1.3), root)]
    for x in (-.13, .13):
        parts.append(ae.cube('Montante', (.015, .02, 2.4), (shift + x, -.205, 1.3), root))
    for z in (.1, 2.5):
        parts.append(ae.cube('Travessa', (.26, .02, .015), (shift, -.205, z), root))
    parts.append(ae.cube('Puxador', (.02, .04, .2), (shift + .1, -.24, 1.3), root))
    for obj in parts:
        set_member(obj, root, 'LEAF_PART')
    return parts


def run():
    ae.env.clean_scene()
    root, body = ae.tower()
    parts = make_parts(root)
    original = {o: o.matrix_world.copy() for o in parts}
    obj = authored.configure(parts, root, construction='GLASS_FRAMED', closed_pose=True)
    ae.env.settle()
    assert all(ae.matrix_error(o.matrix_world, original[o]) < 1e-6 for o in parts)
    assert len(obj.children) == 6
    pivot = leaf.pivot_of(obj)
    pivot.name = 'Controle renomeado'
    obj.name = 'Folha renomeada'
    key = AggregateLeafFront(obj).key
    obj.name = 'Outra folha'
    assert AggregateLeafFront(obj).key == key
    assert fronts.front_for_object(pivot, bpy.context.scene).obj == obj
    for cycle in range(50):
        obj.btm_aggregate.open_value = 1
        ae.env.settle()
        assert abs(leaf.current_fraction(obj) - 1) < 1e-6
        assert abs(AggregateLeafFront(obj).get() - 95) < 1e-5
        obj.btm_aggregate.open_value = 0
        ae.env.settle()
    linear = max((o.matrix_world.translation - original[o].translation).length for o in parts)
    angular = max(o.matrix_world.to_quaternion().rotation_difference(original[o].to_quaternion()).angle for o in parts)
    assert linear <= .0001 and angular <= math.radians(.1)
    print('OK 50 ciclos: desvio mm/°', linear * 1000, math.degrees(angular), flush=True)
    for hinge, kind in [('TOP', 'FLIP_UP'), ('BOTTOM', 'FLIP_DOWN'), ('LEFT', 'DOOR'), ('RIGHT', 'DOOR')]:
        authored.configure(parts, root, hinge=hinge, closed_pose=True)
        assert leaf.pivot_of(obj) == pivot
        assert AggregateLeafFront(obj).kind == kind
        leaf.apply_fraction(obj, 1)
        ae.env.settle()
        assert abs(pivot.matrix_basis.to_quaternion().angle - math.radians(95)) < 1e-5
        leaf.apply_fraction(obj, 0)
        ae.env.settle()
    authored.configure(parts, root, motion='SLIDE', travel_mm=330, closed_pose=True)
    assert AggregateLeafFront(obj).kind == 'SLIDING'
    start = pivot.matrix_world.translation.copy()
    leaf.apply_fraction(obj, 1)
    ae.env.settle()
    assert abs((pivot.matrix_world.translation - start).length - .33) < 1e-5
    try:
        authored.configure(parts, root, closed_pose=True)
        raise AssertionError('configurou aberta')
    except ValueError:
        pass
    leaf.apply_fraction(obj, 0)
    ae.env.settle()
    # Cancelamento da prévia restaura parâmetros, pais e poses, inclusive objetos criados.
    snapshot = authored.Snapshot()
    count = len(bpy.data.objects)
    authored.configure(parts, root, hinge='TOP', max_angle=120, closed_pose=True)
    leaf.apply_fraction(obj, .7)
    snapshot.restore()
    assert len(bpy.data.objects) == count and obj.btm_aggregate.motion == 'SLIDE'
    assert leaf.current_fraction(obj) == 0
    assert all(ae.matrix_error(o.matrix_world, original[o]) < 1e-5 for o in parts)
    print('OK prévia/cancelar restaura mecanismo e pose', flush=True)
    # Pivô manual: usa a origem existente, uma única vez, sem salto.
    other_root, _ = ae.tower('Outra torre', x=3)
    other_parts = make_parts(other_root)
    manual = bpy.data.objects.new('Eixo manual', None)
    bpy.context.collection.objects.link(manual)
    manual.parent = other_root
    manual.location = (-.14, -.215, .1)
    set_member(manual, other_root, 'HARDWARE', reparent=False)
    ae.env.settle()
    before = {o: o.matrix_world.copy() for o in other_parts}
    other = authored.configure(other_parts, other_root, pivot=manual, closed_pose=True)
    ae.env.settle()
    assert leaf.pivot_of(other) == manual
    assert all(ae.matrix_error(o.matrix_world, before[o]) < 1e-5 for o in other_parts)
    authored.configure(other_parts, other_root, closed_pose=True)
    assert leaf.pivot_of(other) == manual
    # Comando duplo por dono: uma terceira folha em outro armário permanece fechada.
    second_parts = make_parts(root, shift=.8)
    second = authored.configure(second_parts, root, hinge='RIGHT', closed_pose=True)
    ae.select([parts[0]])
    bpy.ops.caffmob_draw.authored_leaves_open(opening=.3)
    assert leaf.current_fraction(other) == 0
    assert leaf.current_fraction(obj) > 0 and leaf.current_fraction(second) > 0
    bpy.ops.caffmob_draw.authored_leaves_open(opening=0)
    # Frente fixa não integra a inspeção.
    fixed = ae.cube('Frente fixa', (.1, .01, .1), (0, -.2, 2.7), root)
    set_member(fixed, root)
    authored.configure([fixed], root, construction='FIXED', closed_pose=True)
    assert fronts.front_for_object(fixed, bpy.context.scene) is None
    assert not fixed.btm_aggregate.is_aggregate
    # Migração não consulta o nome, e é idempotente.
    pivot['btm_leaf'] = 'nome que não existe'
    identity_migration.migrate()
    identity_migration.migrate()
    assert 'btm_leaf' not in pivot and obj.parent == pivot
    print('OK TOP/BOTTOM, correr, fixa, dupla isolada, pivô manual e migração', flush=True)
    # Frente em +X, armário girado no mundo: a translação local segue +Y canônico rotacionado.
    axis_root, _ = ae.tower('Eixo X', angle=90, x=7, axis='POS_X')
    axis_part = ae.cube('Correr X', (.02, .3, .7), (.205, 0, 1), axis_root)
    set_member(axis_part, axis_root)
    axis_leaf = authored.configure([axis_part], axis_root, motion='SLIDE', travel_mm=250, closed_pose=True)
    ae.env.settle()
    start = axis_part.matrix_world.translation.copy()
    leaf.apply_fraction(axis_leaf, 1)
    ae.env.settle()
    expected = axis_root.matrix_world.to_3x3() @ Vector((0, .25, 0))
    assert (axis_part.matrix_world.translation - start - expected).length < 1e-5
    leaf.apply_fraction(axis_leaf, 0)
    # Contato real: chapa no percurso de correr, sem as peças móveis bloquearem umas às outras.
    obj.btm_aggregate.open_value = 0
    obstacle = ae.cube('Obstáculo externo', (.02, .2, 3), (.3, -.24, 1.3))
    obj.btm_aggregate.open_value = 1
    ae.env.settle()
    print('contato medido', leaf.current_fraction(obj), obj.btm_aggregate.contact_name,
          tuple(obstacle.matrix_world.translation), flush=True)
    assert 0 < leaf.current_fraction(obj) < 1
    assert obj.btm_aggregate.contact_name == obstacle.name
    print('OK front_axis +X girado e contato silencioso', flush=True)
    # Shift+D real remapeia os ponteiros internos; salvar/reabrir preserva a identidade operacional.
    obj.btm_aggregate.open_value = 0
    ae.env.settle()
    ref = other_parts[0].btm_member.refs.add()
    ref.target = other_parts[1]
    ref.uid = other_parts[1].btm_member.uid
    other_parts[0].btm_member.rule = 'ANCHORED'
    ae.select([other_root] + list(other_root.children_recursive), other_root)
    with component_select.suspended():
        bpy.ops.object.duplicate(linked=False)
    copied_root = next(o for o in bpy.context.selected_objects if o.get('IS_AUTHORED_CABINET'))
    assert copied_root != other_root
    identity_migration.migrate()
    copied_leaf = next(o for o in copied_root.children_recursive
                       if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF')
    assert copied_leaf.btm_member.owner == copied_root
    assert copied_leaf.btm_aggregate.parent_ref == copied_root
    assert leaf.pivot_of(copied_leaf) != manual
    assert copied_root.btm_authored.uid != other_root.btm_authored.uid
    assert copied_leaf.btm_member.uid != other.btm_member.uid
    copied_ref = next(o.btm_member.refs[0] for o in copied_leaf.children_recursive if o.btm_member.refs)
    assert copied_ref.target not in other_parts
    assert copied_ref.target.btm_member.owner == copied_root
    assert copied_ref.uid == copied_ref.target.btm_member.uid
    uid = copied_leaf.btm_member.uid
    copied_leaf.name = 'Cópia renomeada'
    ae.env.settle()
    # A cópia pode ocupar o mesmo lugar: o ensaio aplica a pose sem pedir varredura de contato.
    leaf.apply_fraction(copied_leaf, .5)
    assert leaf.current_fraction(other) == 0
    leaf.apply_fraction(copied_leaf, 0)
    output = Path(__file__).resolve().parents[1] / 'test-results' / 'onda3ab'
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output) as folder:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(folder) / 'identidade.blend'))
        bpy.ops.wm.open_mainfile(filepath=str(Path(folder) / 'identidade.blend'))
        copied_leaf = next(o for o in bpy.data.objects if o.btm_member.uid == uid)
        assert AggregateLeafFront(copied_leaf).key == 'LEAF:' + uid
        assert leaf.pivot_of(copied_leaf) == copied_leaf.parent
        leaf.apply_fraction(copied_leaf, 1)
        leaf.apply_fraction(copied_leaf, 0)
        assert leaf.current_fraction(copied_leaf) == 0
    print('OK Shift+D, renomear e reabrir preservam vínculos independentes', flush=True)
    print('blender_066_composite_leaf: OK', flush=True)


if bpy.app.background:
    run()
else:
    def script():
        ctx = bpy.context
        win = ctx.window_manager.windows[0]
        area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        win.event_simulate('ESC', 'PRESS', x=10, y=10)
        win.event_simulate('ESC', 'RELEASE', x=10, y=10)
        yield .4
        run()
        yield .5
        win = ctx.window_manager.windows[0]
        area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        ae.env.clean_scene()
        root, _ = ae.tower()
        parts = make_parts(root)
        names = [o.name for o in parts]
        original = {o.name: o.matrix_world.copy() for o in parts}
        count = len(bpy.data.objects)
        component_select.set_exempt(ctx, set(names))
        ae.select(parts)
        # Prévia real do diálogo, seguida de Esc.
        with ctx.temp_override(window=win, area=area, region=region):
            bpy.ops.caffmob_draw.authored_leaf('INVOKE_DEFAULT', closed_pose=True)
        yield .3
        op = next(iter(authored._live.values()))
        op.preview = .5
        yield .3
        print('objetos na prévia', len(bpy.data.objects), count, flush=True)
        assert len(bpy.data.objects) == count + 2
        win.event_simulate('ESC', 'PRESS', x=region.x + 100, y=region.y + 100)
        win.event_simulate('ESC', 'RELEASE', x=region.x + 100, y=region.y + 100)
        yield .5
        assert not authored._live and len(bpy.data.objects) == count
        assert all(ae.matrix_error(bpy.data.objects[n].matrix_world, original[n]) < 1e-5 for n in names)
        print('OK prévia real e Esc restauram composição e pose', flush=True)
        ae.select([bpy.data.objects[name] for name in names])
        bpy.ops.ed.undo_push(message='Antes da folha composta')
        yield .3
        # A seleção pode subir à raiz entre eventos: o operador recebe novamente as peças explícitas.
        ae.select([bpy.data.objects[name] for name in names])
        with ctx.temp_override(window=win, area=area, region=region):
            result = bpy.ops.caffmob_draw.authored_leaf('EXEC_DEFAULT', True, closed_pose=True,
                                                       construction='GLASS_FRAMED')
        assert result == {'FINISHED'}
        yield .4
        assert len(bpy.data.objects) == count + 2
        with ctx.temp_override(window=win, area=area, region=region):
            bpy.ops.ed.undo()
        yield .4
        assert len(bpy.data.objects) == count
        assert all(ae.matrix_error(bpy.data.objects[n].matrix_world, original[n]) < 1e-5 for n in names)
        print('OK um Desfazer restaura folha composta sem pivô órfão', flush=True)

    gen = script()

    def tick():
        try:
            return next(gen)
        except StopIteration:
            sys.stdout.flush()
            os._exit(0)
        except Exception:
            traceback.print_exc()
            sys.stdout.flush()
            os._exit(1)
    bpy.app.timers.register(tick, first_interval=2, persistent=True)
