"""Teste de fumaça da feature 004, incremento I2 (T057): colisão de corpo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_collision_smoke.py

Cobre: penetração de 20 mm na parede; balcões encostados sem ocorrência; porta de ambiente × parede e agregado × pai
fora da lista; "Colisão: Desativada"; Ir para; Afastar até encostar; 200 itens em até 2 s.

Feature 066 (T013): a lista virou diagnóstico técnico sob pedido. As penetrações do diagnóstico são montadas com
"Impedir atravessamento" desligado (como num projeto antigo); com ele ligado, o mesmo movimento para no contato, sem
ocorrência, aviso ou nota ao salvar. O "desatualizado" e o aviso ao soltar saíram: o diagnóstico recalcula ao abrir.
"""

import sys
import time
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import guard as _guard  # noqa: E402
# Estes cenários movem por código no lugar do G: o guarda só limita G e gizmo (BUG-20261023-TAMR, RF01).
_guard._direct_move_running = lambda: True
from caffmob_draw import hb_types, hb_utils  # noqa: E402
from caffmob_draw.aggregates import convert  # noqa: E402
from caffmob_draw.collision import scan  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.stick import magnet  # noqa: E402
from caffmob_draw.ui import save_feedback  # noqa: E402

ctx = bpy.context
scene = ctx.scene
state = ctx.window_manager.btm_collision
env.clean_scene()
magnet.preferences = lambda: (False, 0.05)      # o ímã não deve grudar os balcões de teste na parede
scene.btm_settings.block_penetration = False    # monta penetrações de projeto antigo para o diagnóstico (066)


def box_mesh(name, lo, hi, location=(0.0, 0.0, 0.0)):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(tuple(lo[i] if v.co[i] < 0 else hi[i] for i in range(3)))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    scene.collection.objects.link(obj)
    return obj


def cabinet(name, location):
    cab = tf.BaseCabinet()
    cab.create(name)
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    cab.obj.location = location
    return cab.obj


def pairs():
    return [(r.kind, r.name_a, r.name_b, round(r.depth, 4)) for r in state.items]


wall = hb_types.GeoNodeWall()
wall.create("Parede")
wall.set_input('Length', 4.0)
wall.set_input('Thickness', 0.15)
wall.set_input('Height', 2.6)

# 1. Balcão 20 mm dentro da parede (o fundo do módulo fica em Y local 0 e o corpo vai para −Y).
balcao = cabinet("Balcao", (0.5, 0.02, 0.0))
env.settle()
assert scan.check_all(ctx) is not None
assert pairs() == [('WALL', 'Balcao', 'Parede', 0.02)], pairs()

# 2. Ir para seleciona os dois; Afastar até encostar tira o balcão de dentro da parede.
assert bpy.ops.caffmob.collision_goto(index=0) == {'FINISHED'}
assert set(o.name for o in ctx.selected_objects) == {'Balcao', 'Parede'}
assert bpy.ops.caffmob.collision_push_out(index=0) == {'FINISHED'}
assert abs(balcao.location.y - 0.0) < 1e-4, balcao.location.y
scan.check_all(ctx)
assert pairs() == [], pairs()

# 3. Dois balcões encostados (0,5 mm de diferença) não colidem; sobrepostos 100 mm colidem.
width = balcao.dimensions.x
vizinho = cabinet("Vizinho", (0.5 + width - 0.0005, 0.0, 0.0))
env.settle()
scan.check_all(ctx)
assert pairs() == [], pairs()
vizinho.location.x = 0.5 + width - 0.1
env.settle()
scan.check_all(ctx)
assert [p[:3] for p in pairs()] == [('ITEM', 'Balcao', 'Vizinho')], pairs()

# 4. "Colisão: Desativada" tira o par da lista.
vizinho.btm_plane.collision_override = 'OFF'
scan.check_all(ctx)
assert pairs() == [], pairs()
vizinho.btm_plane.collision_override = 'INHERIT'

# 5. Porta de ambiente na parede e agregado afundado no pai não são colisão.
porta = box_mesh("Porta", (0.0, -0.05, 0.0), (0.8, 0.2, 2.1), location=(2.5, 0.0, 0.0))
porta['IS_ENTRY_DOOR_BP'] = True
porta.parent = wall.obj
side = bpy.data.objects["Left Side"]
nicho = box_mesh("Nicho", (-0.05, -0.05, -0.005), (0.05, 0.05, 0.02))
nicho.matrix_world = side.matrix_world.copy()
env.settle()
convert.convert(nicho, side, 'POS_Z')
nicho.btm_aggregate.offset = -0.005
env.settle()
scan.check_all(ctx)
names = {(p[1], p[2]) for p in pairs()}
assert ('Porta', 'Parede') not in names and not any('Nicho' in n for n in names), pairs()
assert [p[:3] for p in pairs()] == [('ITEM', 'Balcao', 'Vizinho')], pairs()

# 6. Diagnóstico sob pedido (066, RF-024): sem "desatualizado" nem nota ao salvar; abrir recalcula a cena de agora.
assert not hasattr(save_feedback, '_collision_note')
assert not hasattr(scan, 'check_moved')
balcao.location.z += 0.01
env.settle()
assert bpy.ops.caffmob.collision_diagnose() == {'FINISHED'}
assert [p[:3] for p in pairs()] == [('ITEM', 'Balcao', 'Vizinho')], pairs()
balcao.location.z -= 0.01
env.settle()

# 7. Com "Impedir atravessamento" ligado, o balcão levado 20 mm para dentro da parede para na face, em silêncio
#    (RF-001, RF-021): nenhuma ocorrência nova, nada na barra de status.
shown = []
show = save_feedback.show
save_feedback.show = shown.append
bpy.ops.caffmob.collision_clear()
scene.btm_settings.block_penetration = True
balcao.location.y = 0.02
env.settle()
assert abs(balcao.location.y) < 1e-4, balcao.location.y
assert not state.items and not shown, (pairs(), shown)
save_feedback.show = show

# 8. O antigo "Evitar Sobreposição" desligado não impede o diagnóstico (a chave saiu da interface, D-06).
scene.btm_settings.collision_global = False
assert bpy.ops.caffmob.check_collisions() == {'FINISHED'}
scene.btm_settings.collision_global = True
scene.btm_settings.block_penetration = False

# 9. 200 itens em até 2 s.
env.clean_scene()
for i in range(200):
    x, y = (i % 20) * 0.7, (i // 20) * 0.7
    box_mesh(f"Caixa{i:03d}", (0.0, 0.0, 0.0), (0.6, 0.6, 0.7), location=(x, y, 0.0))
box_mesh("Extra", (0.0, 0.0, 0.0), (0.6, 0.6, 0.7), location=(0.3, 0.3, 0.0))
env.settle()
start = time.perf_counter()
found = scan.check_all(ctx)
elapsed = time.perf_counter() - start
assert len(found) == 4, len(found)          # a caixa extra entra em quatro vizinhas
assert elapsed <= 2.0, elapsed
print(f"200 itens: {elapsed:.3f} s")

print("OK blender_004_collision_smoke")
