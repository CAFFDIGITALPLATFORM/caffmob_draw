"""Ímã de face plana (feature 004, T031; RN-10a, D-06).

Com o ímã ligado nas preferências, um módulo ou geometria solto com o fundo (+Y local) a até a distância do ímã de uma
face plana de outro objeto gruda nela ao ser solto. Piso e teto não contam (RN-05).
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore

from ..selection import classify
from . import apply, link

DEFAULT_DISTANCE = 0.05
_MAX_STEPS = 8
_FACING = -0.7          # a face precisa estar de frente para o fundo do item


def preferences():
    """(ligado, distância) das preferências do add-on; padrão quando o add-on não está instalado (testes)."""
    package = __package__.rsplit('.', 1)[0]
    addon = bpy.context.preferences.addons.get(package)
    prefs = getattr(addon, 'preferences', None) if addon is not None else None
    if prefs is None or not hasattr(prefs, 'stick_magnet'):
        return True, DEFAULT_DISTANCE
    return bool(prefs.stick_magnet), float(prefs.stick_magnet_distance)


def _back(item, depsgraph):
    lo, hi = apply.local_box(item, depsgraph)
    center = Vector(((lo[0] + hi[0]) / 2.0, hi[1], (lo[2] + hi[2]) / 2.0))
    direction = (item.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
    return item.matrix_world @ center, direction


def find(item, distance, depsgraph=None):
    """(objeto, ponto, normal, vértices do polígono) da face que o ímã alcança, ou None."""
    depsgraph = depsgraph or bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    origin, direction = _back(item, depsgraph)
    own = {item} | set(item.children_recursive)
    start = origin - direction * 0.001
    for _ in range(_MAX_STEPS):
        hit, location, normal, index, obj, _matrix = scene.ray_cast(depsgraph, start, direction,
                                                                     distance=distance + 0.002)
        if not hit:
            return None
        if obj in own or obj.get('IS_CUTTING_OBJ') or obj.get('IS_2D_ANNOTATION'):
            start = location + direction * 0.0001
            continue
        hit_dist = (location - origin).dot(direction)
        if hit_dist > distance or normal.dot(direction) > _FACING:
            return None
        host = link.host_for(obj)
        kind = classify.classify(host).kind if host is not None else classify.OTHER
        if kind in (classify.FLOOR, classify.CEILING):
            return None
        from . import release_guard_core
        st = getattr(item, 'btm_stick', None)
        released = getattr(st, 'released_host_name', '') if st is not None else ''
        if host is not None and release_guard_core.should_suppress_magnet(released, host.name, hit_dist, distance):
            return None
        return obj, location, normal, _polygon(obj, index, depsgraph)
    return None


def _polygon(obj, index, depsgraph):
    try:
        mesh = obj.evaluated_get(depsgraph).data
        poly = mesh.polygons[index]
    except (AttributeError, IndexError, ReferenceError):
        return None
    return [obj.matrix_world @ mesh.vertices[i].co for i in poly.vertices]


def preview_pose(item, hit_location, hit_normal, depsgraph=None):
    """Prévia do ímã (feature 005, T029; D-15): cantos (mundo) da caixa do item girado para a face e encostado nela,
    **sem alterar o objeto**. Mesma orientação de `link.orient` e mesmo encosto de `link.stick(center=False)`."""
    depsgraph = depsgraph or bpy.context.evaluated_depsgraph_get()
    target = link.oriented_matrix(item.matrix_world, hit_normal)
    inv = target.inverted_safe()
    local = [inv @ Vector(c) for c in apply._corners(item, target, depsgraph)]
    lo = [min(c[i] for c in local) for i in range(3)]
    hi = [max(c[i] for c in local) for i in range(3)]
    # Mesma ordem dos cantos de `Object.bound_box` (o desenho liga as arestas por índice).
    box = [(lo[0], lo[1], lo[2]), (lo[0], lo[1], hi[2]), (lo[0], hi[1], hi[2]), (lo[0], hi[1], lo[2]),
           (hi[0], lo[1], lo[2]), (hi[0], lo[1], hi[2]), (hi[0], hi[1], hi[2]), (hi[0], hi[1], lo[2])]
    corners = [target @ Vector(c) for c in box]
    n = Vector(hit_normal).normalized()
    origin = Vector(hit_location)
    gap = min((c - origin).dot(n) for c in corners)
    return [c - n * gap for c in corners]


def try_stick(item):
    """Aplica o ímã ao item solto; devolve o hospedeiro quando grudou."""
    enabled, distance = preferences()
    if not enabled:
        return None
    found = find(item, distance)
    if found is None:
        return None
    obj, location, normal, polygon = found
    try:
        host, _face = link.stick(item, obj, location, normal, polygon, center=False, rotate=True)
    except ValueError:
        return None
    return host
