"""T022: adoção preserva geometria e pose; em janela, Desfazer em um passo."""
import hashlib
import math
import os
import sys
import traceback
from pathlib import Path
import bpy
from mathutils import Matrix
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as ae
from caffmob_draw.aggregates import ops_authored as authored
from caffmob_draw.selection import component
from caffmob_draw import identity_migration


def digest(obj):
    return hashlib.sha256(repr((
        [tuple(v.co) for v in obj.data.vertices], [tuple(p.vertices) for p in obj.data.polygons],
        [[tuple(d.uv) for d in layer.data] for layer in obj.data.uv_layers],
        [m.name if m else None for m in obj.data.materials],
        [v for row in obj.matrix_world for v in row])).encode()).hexdigest()


def run():
    ae.env.clean_scene()
    for angle, x in ((0, 0), (90, 3)):
        root = bpy.data.objects.new('Manual' + str(angle), None)
        bpy.context.collection.objects.link(root)
        root.matrix_world = Matrix.Translation((x, 0, 0)) @ Matrix.Rotation(math.radians(angle), 4, 'Z')
        body = ae.cube('Estrutura', (.6, .368, 2.6), (0, 0, 1.3), root)
        body.data.materials.append(bpy.data.materials.new('Acabamento'))
        before = digest(body)
        ae.select([root])
        assert bpy.ops.caffmob_draw.authored_adopt() == {'FINISHED'}
        ae.env.settle()
        assert digest(body) == before
        assert abs(root.btm_authored.size_local[0] - 600) < .01
        assert abs(root.btm_authored.size_local[2] - 2600) < .01
        assert component.component_root(body) == root
        print('OK adoção torre', angle, 'hash igual; medidas', tuple(root.btm_authored.size_local), flush=True)
    # Raiz nova para peças soltas e auditoria de referências externas.
    loose = ae.cube('Solta', (.1, .1, .1), (6, 0, 0))
    ae.select([loose])
    assert bpy.ops.caffmob_draw.authored_adopt(new_root=True) == {'FINISHED'}
    assert loose.btm_member.owner is not None
    root = loose.btm_member.owner
    copy = root.copy()
    bpy.context.collection.objects.link(copy)
    member = loose.copy()
    bpy.context.collection.objects.link(member)
    member.parent = copy
    member.btm_member.owner = copy
    identity_migration.migrate_authored()
    assert root.btm_authored.uid != copy.btm_authored.uid
    assert loose.btm_member.uid != member.btm_member.uid
    assert member.btm_member.owner == copy
    print('OK identidade duplicada renovada sem ligação ao original', flush=True)
    print('blender_066_authored_adopt: OK', flush=True)


def script():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    win.event_simulate('ESC', 'PRESS', x=10, y=10)
    win.event_simulate('ESC', 'RELEASE', x=10, y=10)
    yield .5
    run()
    ae.env.clean_scene()
    root = ae.cube('DesfazerAutor', (.6, .368, 2.6))
    ae.select([root])
    bpy.ops.ed.undo_push(message='Antes da adoção')
    yield .3
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.caffmob_draw.authored_adopt('EXEC_DEFAULT', True)
    yield .4
    assert ctx.scene.objects['DesfazerAutor'].get('IS_AUTHORED_CABINET')
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    yield .4
    root = ctx.scene.objects['DesfazerAutor']
    assert not root.get('IS_AUTHORED_CABINET') and not root.btm_authored.is_authored
    assert not root.btm_member.owner
    print('OK um Desfazer restaura adoção integral', flush=True)


if bpy.app.background:
    run()
else:
    gen = script()

    def tick():
        try:
            return next(gen)
        except StopIteration:
            os._exit(0)
        except Exception:
            traceback.print_exc()
            sys.stdout.flush()
            os._exit(1)
    bpy.app.timers.register(tick, first_interval=2)
