"""Sonda de desempenho da abertura do seletor de sobreposição (feature 016, T001).

Mede uma passada completa do algoritmo de D-03 na cena sintética mais hostil que o roadmap previu: 2.000 malhas
empilhadas na frente do raio. Roda em segundo plano:

    blender --background --factory-startup --python-exit-code 1 --python <este arquivo>
"""

import time

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

COUNT = 2000
ORIGIN = Vector((0.0, -6.0, 1.6))
TARGET = Vector((0.0, 0.0, 1.2))
ROUNDS = 5
CORNER = 0.1


def _mesh():
    verts = [(x * CORNER, y * CORNER, z * CORNER) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    mesh = bpy.data.meshes.new("Sonda016")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def build():
    mesh = _mesh()
    scene = bpy.context.scene
    for i in range(COUNT):
        obj = bpy.data.objects.new(f"Cubo{i:04d}", mesh)
        scene.collection.objects.link(obj)
        obj.location = ((i % 20) * 0.02 - 0.2, 0.0, (i % 7) * 0.02 + 1.0)
    bpy.context.view_layer.update()


def sweep(depsgraph):
    """Uma passada do raio por objeto, como o operador vai fazer (D-03)."""
    direction = (TARGET - ORIGIN).normalized()
    candidates = hits = 0
    for obj in bpy.context.view_layer.objects:
        if obj.type != 'MESH' or not obj.visible_get() or obj.hide_select:
            continue
        candidates += 1
        evaluated = obj.evaluated_get(depsgraph)
        inverse = evaluated.matrix_world.inverted()
        ok, _location, _normal, _index = evaluated.ray_cast(inverse @ ORIGIN, inverse.to_3x3() @ direction)
        if ok:
            hits += 1
    return candidates, hits


def main():
    build()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    sweep(depsgraph)                                   # aquece o depsgraph antes de medir
    times = []
    for _ in range(ROUNDS):
        start = time.perf_counter()
        candidates, hits = sweep(depsgraph)
        times.append(time.perf_counter() - start)
    times.sort()
    print(f"objetos na cena: {COUNT}")
    print(f"candidatos por passada: {candidates}, com impacto: {hits}")
    print(f"passadas (s): {[round(t, 3) for t in times]}")
    print(f"mediana: {times[len(times) // 2]:.3f} s | pior: {times[-1]:.3f} s")


try:
    main()
except Exception:                                       # noqa: BLE001 - a sonda precisa mostrar o erro e sair 1
    import traceback
    traceback.print_exc()
    raise SystemExit(1)
