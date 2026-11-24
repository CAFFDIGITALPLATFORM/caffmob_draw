"""Teste de fumaça da porta e da janela reais (feature 010, T029; RF-01 a RF-07, RF-13).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_openings_smoke.py

Paredes de verdade (editor de paredes, sala 4 × 3 com 150 mm) e a caixa de porta montada como o modal de colocação
monta (`_openings_env.make_cage`), presa à parede e cortando-a:
- porta 80 × 210: 4 malhas, caixa em arame, texto escondido, furo de 898 × 2159 mm, folha abrindo 90°;
- a folha para num armário no caminho;
- largura 90 refaz a folha com 900 mm sem mudar as ferragens; espessura 200 mm pelo editor de paredes;
- porta dupla, vão aberto e janela de correr (cada folha corre 535 mm);
- "Atualizar portas e janelas" monta uma caixa antiga; medidas padrão 80/160 × 210.
"""

import math
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _openings_env as oe  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_types  # noqa: E402
from caffmob_draw.aggregates import group  # noqa: E402
from caffmob_draw.openings import door_core, sync  # noqa: E402
from caffmob_draw.operators import doors_windows as dw  # noqa: E402
from caffmob_draw.walls2d import apply, model, scene_io  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def walls():
    return sorted((o for o in ctx.scene.objects if o.get('IS_WALL_BP')), key=lambda o: o.name)


def on_wall(cage, wall, x=1.0, z=0.0):
    cage.parent = wall
    cage.location = (x, 0.0, z)
    dw.cut_wall(wall, cage)
    env.settle()


def meshes(cage):
    return [o for o in cage.btm_opening_real.assembly.children_recursive if o.type == 'MESH']


def leaves(cage):
    return [o for o in cage.btm_opening_real.assembly.children_recursive
            if o.btm_aggregate.is_aggregate and o.btm_aggregate.kind == 'LEAF']


def part(cage, label):
    return next(o for o in meshes(cage) if label in o.name)


def box(objs):
    lo, hi = group.world_box(objs)
    return lo, hi


def main():
    env.clean_scene()
    hb = ctx.scene.home_builder
    check("medidas padrão 80 / 160 × 210", (round(hb.door_single_width, 3), round(hb.door_double_width, 3),
                                            round(hb.door_height, 3)) == (0.8, 1.6, 2.1))
    apply.apply_plan(ctx, model.WallPlan([model.rectangle(4.0, 3.0)]))
    env.settle()
    wall = walls()[0]
    door = oe.make_cage('DOOR')
    on_wall(door, wall)
    sync.sync(ctx, door)
    env.settle()
    geo = hb_types.GeoNodeCage(door)
    check("porta: 4 malhas reais", len(meshes(door)) == 4, str([o.name for o in meshes(door)]))
    text = next(c for c in door.children if 'Text' in c.name)
    check("caixa em arame e sem o texto DOOR na vista", door.display_type == 'WIRE' and text.hide_viewport)
    check("furo de 898 × 2159 mm cortando a parede",
          (round(geo.get_input('Dim X'), 3), round(geo.get_input('Dim Z'), 3)) == (0.898, 2.159)
          and any(m.type == 'BOOLEAN' and m.object == door for m in wall.modifiers))
    leaf_mesh = part(door, "Folha 1")
    lo, hi = box([leaf_mesh])
    check("folha de 800 mm", abs((hi - lo).length - (hi - lo).length) < 1e-9 and
          abs(max(hi.x - lo.x, hi.y - lo.y) - 0.80) < 0.002, f"{hi - lo}")
    sash = leaves(door)[0]
    closed = leaf_mesh.matrix_world.to_euler().z
    sash.btm_aggregate.open_value = 1.0
    env.settle()
    angle = abs(math.degrees(leaf_mesh.matrix_world.to_euler().z - closed))
    check("a folha abre até 90°", abs(angle - 90.0) < 1.0, f"{angle:.1f}°")
    open_lo, open_hi = box([leaf_mesh])
    sash.btm_aggregate.open_value = 0.0
    env.settle()
    mid = (open_lo + open_hi) / 2
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(mid.x, mid.y, 0.6))
    cabinet = ctx.active_object
    cabinet.name = "Armario"
    env.settle()
    from caffmob_draw.aggregates import collision
    collision._cache.clear()
    sash.btm_aggregate.open_value = 1.0
    env.settle()
    stopped = abs(math.degrees(leaf_mesh.matrix_world.to_euler().z - closed))
    check("a folha para no armário", stopped < 85.0 and "Armario" in sash.btm_aggregate.contact_name,
          f"{stopped:.1f}° {sash.btm_aggregate.contact_name!r}")
    bpy.data.objects.remove(cabinet, do_unlink=True)
    sash.btm_aggregate.open_value = 0.0
    collision._cache.clear()

    hw_faces = len(part(door, "Ferragens da folha").data.polygons)
    geo.set_input('Dim X', door_core.hole_size(0.90, 2.10)[0])
    sync.sync(ctx, door)
    env.settle()
    lo, hi = box([part(door, "Folha 1")])
    check("largura 90 refaz a folha sem mudar as ferragens",
          abs(max(hi.x - lo.x, hi.y - lo.y) - 0.90) < 0.002 and
          len(part(door, "Ferragens da folha").data.polygons) == hw_faces, f"{hi - lo}")

    plan = scene_io.read_plan(ctx.scene)
    for chain in plan.chains:
        for seg in chain.segments:
            seg.thickness = 0.20
    report = apply.apply_plan(ctx, plan)
    env.settle()
    lo, hi = box([part(door, "Marco")])
    depth = min(hi.x - lo.x, hi.y - lo.y)
    check("o marco acompanha a parede de 200 mm", abs(hb_types.GeoNodeCage(door).get_input('Dim Y') - 0.20) < 1e-6
          and abs(depth - (0.20 + 0.045)) < 0.003 and report.get('openings', 0) >= 1, f"{depth:.3f}")

    double = oe.make_cage('DOUBLE_DOOR')
    on_wall(double, walls()[1])
    sync.sync(ctx, double)
    opening = oe.make_cage('OPEN_DOOR')
    on_wall(opening, walls()[2])
    sync.sync(ctx, opening)
    window = oe.make_cage('WINDOW')
    on_wall(window, walls()[3], x=1.0, z=1.0)
    sync.sync(ctx, window)
    env.settle()
    check("porta dupla com 2 folhas e vão aberto sem folha", len(leaves(double)) == 2 and not leaves(opening))
    angles = []
    for sash in leaves(double):                 # outra parede, girada: a montagem segue os eixos da caixa
        mesh = next(o for o in sash.children_recursive if o.type == 'MESH' and "Folha" in o.name)
        before = mesh.matrix_world.to_euler().z
        sash.btm_aggregate.open_value = 1.0
        env.settle()
        angles.append(round(abs(math.degrees(mesh.matrix_world.to_euler().z - before)) % 360))
        sash.btm_aggregate.open_value = 0.0
    check("as 2 folhas da dupla abrem 90° numa parede girada", angles == [90, 90], str(angles))
    moved = []
    for sash in leaves(window):
        mesh = next(o for o in sash.children_recursive if o.type == 'MESH')
        before = box([mesh])[0].copy()
        sash.btm_aggregate.open_value = 1.0
        env.settle()
        moved.append(round((box([mesh])[0] - before).length, 3))
        sash.btm_aggregate.open_value = 0.0
    check("janela: 2 folhas de correr até o batente (535 mm)", moved == [0.535, 0.535], str(moved))

    legacy = oe.make_cage('DOOR')
    legacy.btm_opening_real.kind = 'NONE'
    on_wall(legacy, walls()[0], x=2.5)
    check("caixa antiga aparece para atualizar", legacy in sync.outdated(ctx.scene))
    result = bpy.ops.caffmob.openings_update()
    check("Atualizar portas e janelas monta a caixa antiga", result == {'FINISHED'}
          and legacy.btm_opening_real.assembly is not None and not sync.outdated(ctx.scene))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_010_openings_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
