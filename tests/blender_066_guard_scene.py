"""Ensaio do guarda de colisão pelos caminhos sem janela (feature 066, T010 complementar; RF-002, RF-005 a RF-007,
RF-011, RF-012).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_066_guard_scene.py

O G de verdade fica em `blender_066_guard_translate.py` (precisa de janela). Aqui o movimento vem do Python e dos
campos, que o guarda pega do mesmo jeito (`depsgraph_update_post`):
- vão real: cabe pelo portal aberto, não cabe para na face (RF-006);
- canto com dois obstáculos: para na última pose válida, desliza sem empurrar e não vibra (RF-007);
- conjunto móvel: dois itens movidos juntos não se bloqueiam; o puxador saliente do módulo toca primeiro (RF-005);
- índice acompanha a cena: obstáculo novo bloqueia; apagado ou movido não usa caixa vencida (RF-011);
- escala que penetra volta à anterior (RF-012, pela matriz).
"""

import sys
import traceback
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import guard as _guard  # noqa: E402
# Estes cenários movem por código no lugar do G: o guarda só limita G e gizmo (BUG-20261023-TAMR, RF01).
_guard._direct_move_running = lambda: True

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cube(name, loc, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = ctx.object
    obj.name, obj.scale = name, scale
    env.settle()
    return obj


def portal(name, x, width, height=2.2, thickness=0.15, total=4.0):
    """Parede com um vão de `width` × `height` no meio, uma malha só (sem cadastro)."""
    bm = bmesh.new()
    half = total / 2.0
    for x0, x1, z0, z1 in ((-half, -width / 2, 0.0, 2.6), (width / 2, half, 0.0, 2.6),
                           (-width / 2, width / 2, height, 2.6)):
        verts = [bm.verts.new((x + (x0 if i & 1 == 0 else x1), (0.0 if i & 2 == 0 else thickness),
                               (z0 if i & 4 == 0 else z1))) for i in range(8)]
        for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            bm.faces.new([verts[i] for i in f])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    ctx.scene.collection.objects.link(obj)
    env.settle()
    return obj


def move(obj, loc):
    obj.location = loc
    env.settle()
    return tuple(round(v, 4) for v in obj.location)


def doorway():
    env.clean_scene()
    portal("Portal", 0.0, 1.0)
    small = cube("Pequeno", (0.0, -1.0, 0.5), (0.6, 0.6, 0.6))
    final = move(small, (0.0, 1.5, 0.5))
    check("RF-006: o que cabe passa pelo portal aberto", final == (0.0, 1.5, 0.5), str(final))
    wide = cube("Largo", (0.0, -1.0, 0.5), (1.4, 0.6, 0.6))
    final = move(wide, (0.0, 1.5, 0.5))
    check("RF-006: o que não cabe para na face da parede", abs(final[1] + 0.3) < 1e-3, str(final))


def corner():
    env.clean_scene()
    cube("Parede X", (1.0075, 0.0, 0.5), (0.015, 4.0, 2.0))
    cube("Parede Y", (-0.55, 1.0075, 0.5), (2.9, 0.015, 2.0))     # não cruza a parede X
    mover = cube("Movel", (-1.0, -1.0, 0.5))
    final = move(mover, (2.0, 0.0, 0.5))
    check("RF-007: desliza na tangente e para na parede X", final == (0.5, 0.0, 0.5), str(final))
    final = move(mover, (2.0, 2.0, 0.5))
    check("RF-007: no canto, para nas duas faces", final == (0.5, 0.5, 0.5), str(final))
    again = move(mover, (2.0, 2.0, 0.5))
    check("RF-007: pedir de novo não vibra", again == final, str(again))
    walls = [tuple(round(v, 4) for v in bpy.data.objects[n].location) for n in ("Parede X", "Parede Y")]
    check("RF-007: não empurra o obstáculo", walls == [(1.0075, 0.0, 0.5), (-0.55, 1.0075, 0.5)], str(walls))


def moving_set():
    env.clean_scene()
    a = cube("A", (0.0, 0.0, 0.5))
    b = cube("B", (1.0, 0.0, 0.5))                      # encostado em A
    cube("Chapa", (3.0075, 0.0, 0.5), (0.015, 2.0, 2.0))
    a.location.x += 0.5
    b.location.x += 0.5
    env.settle()
    check("RF-005: movidos juntos não se bloqueiam", abs(a.location.x - 0.5) < 1e-6 and abs(b.location.x - 1.5)
          < 1e-6, f"{a.location.x:.4f} {b.location.x:.4f}")
    a.location.x += 3.0
    b.location.x += 3.0
    env.settle()
    check("RF-005: o conjunto para junto no contato", abs(b.location.x - 2.5) < 1e-4 and abs(a.location.x - 1.5)
          < 1e-4, f"{a.location.x:.4f} {b.location.x:.4f}")


def module_handle():
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    module = ctx.view_layer.objects.active
    env.settle()
    depsgraph = ctx.evaluated_depsgraph_get()

    def front():
        return min((o.matrix_world @ Vector(c)).y for o in [module] + list(module.children_recursive)
                   if o.type == 'MESH' and o.visible_get() and o.display_type not in {'WIRE', 'BOUNDS'}
                   for c in o.evaluated_get(depsgraph).bound_box)
    reach = front()
    plate = cube("Chapa", (0.3, reach - 0.5075, 0.4), (2.0, 0.015, 2.0))      # face em y = frente − 0,5
    face = plate.location.y + 0.0075
    module.location.y -= 2.0
    env.settle()
    depsgraph = ctx.evaluated_depsgraph_get()
    check("RF-005: a peça mais saliente do módulo toca primeiro, sem autocolisão", abs(front() - face) < 1e-3,
          f"frente={front():.4f} face={face:.4f}")


def index_follows_scene():
    env.clean_scene()
    mover = cube("Movel", (0.0, 0.0, 0.5))
    wall = cube("Novo", (1.0075, 0.0, 0.5), (0.015, 2.0, 2.0))
    final = move(mover, (2.0, 0.0, 0.5))
    check("RF-011: objeto novo bloqueia", final[0] == 0.5, str(final))
    move(mover, (0.0, 0.0, 0.5))
    wall.location.x = 3.0
    env.settle()
    final = move(mover, (2.0, 0.0, 0.5))
    check("RF-011: obstáculo movido não usa a caixa velha", final[0] == 2.0, str(final))
    move(mover, (0.0, 0.0, 0.5))
    bpy.data.objects.remove(wall, do_unlink=True)
    env.settle()
    final = move(mover, (5.0, 0.0, 0.5))
    check("RF-011: obstáculo apagado não bloqueia", final[0] == 5.0, str(final))
    hidden = cube("Oculto", (6.5075, 0.0, 0.5), (0.015, 2.0, 2.0))
    hidden.hide_set(True)
    env.settle()
    final = move(mover, (8.0, 0.0, 0.5))
    check("D-09: obstáculo oculto não bloqueia", final[0] == 8.0, str(final))


def scale_back():
    env.clean_scene()
    mover = cube("Movel", (0.0, 0.0, 0.5))
    cube("Vizinho", (1.2, 0.0, 0.5))
    mover.scale = (2.0, 1.0, 1.0)
    env.settle()
    check("RF-012: escala que penetra volta à anterior", tuple(round(s, 4) for s in mover.scale) == (1.0, 1.0, 1.0),
          str(tuple(mover.scale)))
    mover.scale = (1.3, 1.0, 1.0)
    env.settle()
    check("RF-012: escala livre fica", abs(mover.scale.x - 1.3) < 1e-6, str(tuple(mover.scale)))


def portal_from_inside():
    env.clean_scene()
    portal("Portal", 0.0, 1.0)
    mover = cube("Dentro do vão", (0.0, 0.075, 0.5), (0.2, 0.2, 0.2))
    final = move(mover, (1.5, 0.075, 0.5))
    check("RF-006: começar dentro da caixa do portal não libera a ombreira", abs(final[0] - 0.4) < 0.001,
          str(final))


def clamp_crossing():
    from caffmob_draw.collision import guard
    from mathutils import Matrix
    env.clean_scene()
    mover = cube("Movel", (0.0, 0.0, 0.5))
    cube("Chapa", (1.0075, 0.0, 0.5), (0.015, 2.0, 2.0))
    start = mover.matrix_world.copy()
    target = Matrix.Translation((2.0, 0.0, 0.5))
    allowed = guard.clamp(mover, start, target)
    check("RF-003/004: clamp não salta a chapa com destino livre", abs(allowed.translation.x - 0.5) < 1e-4,
          str(tuple(allowed.translation)))


def parameter_resize():
    from caffmob_draw.selection import classify, editing
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    module = ctx.view_layer.objects.active
    env.settle()
    cube("Vizinho", (1.4, -0.3, 0.5))
    info = classify.classify(module)
    old = editing.get_dimension(info, 'width')
    editing.set_dimension(ctx, info, 'width', 2.2)
    env.settle()
    # BUG-20261023-TAMR (RF03): medida não é deslocamento; a largura que sobrepõe vale.
    check("RF03: largura paramétrica que sobrepõe vale", abs(editing.get_dimension(info, 'width') - 2.2) < 1e-6)
    editing.set_dimension(ctx, info, 'width', 0.7)
    env.settle()
    check("RF-012: largura paramétrica livre fica", abs(editing.get_dimension(info, 'width') - 0.7) < 1e-6)
    from caffmob_draw.overlays import element_toast
    for other in ctx.selected_objects:
        other.select_set(False)
    module.select_set(True)
    ctx.view_layer.objects.active = module
    shown = []
    real = element_toast.show
    element_toast.show = lambda *args, **kwargs: shown.append(args)
    try:
        result = bpy.ops.caffmob.resize_width(width=2.2)
        env.settle()
        check("RF03: Redimensionar que sobrepõe vale", result == {'FINISHED'}
              and abs(editing.get_dimension(info, 'width') - 2.2) < 1e-6, (result, editing.get_dimension(info, 'width')))
    finally:
        element_toast.show = real
    env.clean_scene()
    from caffmob_draw.geometry_free import mesh
    obj = mesh.create_object(ctx, kind='CAIXA')
    env.settle()
    cube("Vizinho", (1.4, 0.2, 0.2))
    old = obj.btm_geometry.width
    obj.btm_geometry.width = 1.5
    env.settle()
    check("RF03: dimensão da geometria livre que sobrepõe vale",
          abs(obj.btm_geometry.width - 1.5) < 1e-6 and abs(obj.dimensions.x - 1.5) < 1e-6,
          (old, obj.btm_geometry.width, obj.dimensions.x))


def broad_obstacles():
    from caffmob_draw.collision import scan
    for kind in ('MESH', 'CURVE', 'FONT', 'META'):
        env.clean_scene()
        if kind == 'MESH':
            obstacle = cube("Obstáculo", (1.5, 0.0, 0.5))
        else:
            if kind == 'META':
                bpy.ops.object.metaball_add(type='BALL', location=(1.5, 0, 0))
                obstacle = ctx.object
                obstacle.scale = (0.3, 0.3, 0.3)
                data = None
            else:
                data = bpy.data.curves.new("Corpo", kind)
                if kind == 'FONT':
                    data.body = "I"
                    data.extrude = 0.1
                else:
                    data.dimensions = '3D'
                    data.bevel_depth = 0.15
                    line = data.splines.new('POLY')
                    line.points.add(1)
                    line.points[0].co, line.points[1].co = (0, -0.5, 0, 1), (0, 0.5, 0, 1)
            if data is not None:
                obstacle = bpy.data.objects.new("Obstáculo", data)
                ctx.scene.collection.objects.link(obstacle)
                obstacle.location.x = 1.5
            env.settle()
        box = scan.box_of(obstacle, ctx.evaluated_depsgraph_get())
        lo, hi = box.aabb()
        mover = cube("Movel", (0, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2), (0.1, 0.1, 0.1))
        final = move(mover, (hi[0] + 2.0, mover.location.y, mover.location.z))
        check(f"RF-002: {kind} sem cadastro bloqueia", final[0] <= lo[0] - 0.05 + 0.001,
              f"x={final[0]} face={lo[0]}")
        obstacle.btm_plane.collision_override = 'OFF'
        env.settle()
        final = move(mover, (hi[0] + 2.0, mover.location.y, mover.location.z))
        check(f"RF-002: {kind} com override OFF libera", abs(final[0] - (hi[0] + 2.0)) < 0.001)


def thin_inside_mesh_bounds():
    env.clean_scene()
    ctx.scene.btm_settings.block_penetration = False
    parts = [cube("Filete", (1.0025, 0, 0.5), (0.003, 1, 1)),
             cube("Extremo A", (-0.5, 3, 0.5)), cube("Extremo B", (2.5, 3, 0.5))]
    for obj in ctx.selected_objects:
        obj.select_set(False)
    for obj in parts:
        obj.select_set(True)
    ctx.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    env.settle()
    ctx.scene.btm_settings.block_penetration = True
    mover = cube("Corpo fino", (0, 0, 0.5), (0.003, 0.003, 0.003))
    final = move(mover, (2, 0, 0.5))
    check("RF-004/006: filete entre amostras do BVH não é atravessado", abs(final[0] - 0.9995) < 0.0002,
          str(final))


def collection_failure():
    from caffmob_draw.collision import guard
    env.clean_scene()
    mover = cube("Movel", (0.0, 0.0, 0.5))
    real = guard._index.refresh

    def broken(*_args, **_kwargs):
        raise RuntimeError("falha forçada na coleta")
    guard._index.refresh = broken
    try:
        final = move(mover, (2.0, 0.0, 0.5))
        check("Falha segura também antes do cálculo (índice)", final == (0.0, 0.0, 0.5), str(final))
    finally:
        guard._index.refresh = real


for step in (doorway, corner, moving_set, module_handle, index_follows_scene, scale_back, portal_from_inside,
             clamp_crossing, parameter_resize,
             broad_obstacles, thin_inside_mesh_bounds, collection_failure):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_066_guard_scene: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
