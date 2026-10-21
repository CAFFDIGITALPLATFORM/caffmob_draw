"""T030: parede 5410 mm, porta/janela, identidade incremental e Desfazer/Refazer reais."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import _cladding_env as a
from caffmob_draw import hb_types
from caffmob_draw.cladding import ops, sync
from caffmob_draw.collision import guard

walls, wall, door, window, root = a.scene()
a.check(abs(hb_types.GeoNodeWall(wall).get_input('Length') - 5.41) < 1e-5, 'parede real de 5410 mm')
items = a.pieces(root)
for obj in items.values():
    edge_counts = {}
    for face in obj.data.polygons:
        for edge in face.edge_keys:
            edge_counts[edge] = edge_counts.get(edge, 0) + 1
    a.check(all(count == 2 for count in edge_counts.values()), 'peça sólida fechada')
a.check(bool(items), 'peças geradas na região avaliada com dois vãos')
for obj in items.values():
    a.check(obj.parent == root and obj.btm_plane.collision_override == 'OFF', 'controlador e exclusão de colisão')
# Um ponto em cada triângulo da frente não pode cair dentro de um vão.
for obj in items.values():
    for polygon in obj.data.polygons:
        c = polygon.center
        if polygon.normal.z > .99:
            for cage in (door, window):
                w, _d, h = __import__('caffmob_draw.openings.sync', fromlist=['_dims'])._dims(cage)
                a.check(not (cage.location.x + .0001 < c.x < cage.location.x + w - .0001 and
                             cage.location.z + .0001 < c.y < cage.location.z + h - .0001), 'vão desobstruído')
manual = bpy.data.objects.new('Peça manual', next(iter(items.values())).data.copy())
bpy.context.collection.objects.link(manual)
manual['btm_cladding_piece'] = dict(owner=root.btm_cladding.uid, key='manual', generated=False)
manual_before = manual.data.as_pointer(), manual.matrix_world.copy()
for _i in range(10):
    plan = sync.sync(root)
    a.check(not (plan.create or plan.update or plan.remove), 'hash igual não faz nada')
a.check(len(a.pieces(root)) == len(items), 'dez sincronizações sem duplicatas')
before = {k:(o.as_pointer(), o.data.as_pointer(), o.get('btm_cladding_signature')) for k,o in items.items()}
with guard.suspended():
    window.location.x += .2
    a.env.settle()
    sync.sync(root)
after = a.pieces(root)
unchanged = [k for k,o in after.items() if k in before and o.get('btm_cladding_signature') == before[k][2]]
a.check(bool(unchanged) and len(unchanged) < len(after), 'mover janela altera um subconjunto das peças')
a.check(all((after[k].as_pointer(), after[k].data.as_pointer()) == before[k][:2] for k in unchanged),
        'peças não afetadas preservam objeto e malha')
a.check(manual.data.as_pointer() == manual_before[0] and manual.matrix_world == manual_before[1], 'manual intacta')
# O Blender suporta undo em background quando se semeia o histórico e se empilha a confirmação Python.
for obj in bpy.context.selected_objects:
    obj.select_set(False)
root.select_set(True)
bpy.context.view_layer.objects.active = root
ops.copy_settings(root.btm_cladding, bpy.context.scene.btm_cladding_settings)
bpy.ops.ed.undo_push(message='Antes do revestimento')
bpy.context.scene.btm_cladding_settings.width_mm = 220
bpy.ops.caffmob.cladding_edit()
bpy.ops.ed.undo_push(message='Confirmação do revestimento')
name = root.name
bpy.ops.ed.undo()
a.check(abs(bpy.data.objects[name].btm_cladding.width_mm - 150) < .01, 'um Desfazer restaura confirmação')
bpy.ops.ed.redo()
a.check(abs(bpy.data.objects[name].btm_cladding.width_mm - 220) < .01, 'Refazer recupera confirmação')
print('T030 OK', flush=True)
