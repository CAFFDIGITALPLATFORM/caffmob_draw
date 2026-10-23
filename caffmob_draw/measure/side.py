"""Cotas fixas do item ativo (feature 066, T038; D-10, RN-06, RF-015 a RF-019; BUG-20261023-HYCE). Python puro, sem
`bpy`.

- `fixed_axis`: o eixo lateral é o da parede hospedeira ou, sem parede, o X local do móvel, só na horizontal; a vista
  não muda o que é medido, só a projeção do desenho (RF02 da auditoria de cotas fixas). `lateral_axis` (pela vista)
  fica para quem ainda precisar dela.
- `gaps`: do exterior do corpo ativo até a primeira superfície de cada lado, ao longo do eixo. Só contam obstáculos
  no mesmo corredor: mesma faixa de altura (`cotas._vertical_overlap`, RN-MEASURE-02) e de profundidade. O limite de
  cada lado sai de `cotas.limits`. Lado livre dá None (nunca um 0 fictício); encostar até a tolerância dá 0.
"""

import math
from collections import namedtuple

from . import cotas

Gap = namedtuple('Gap', 'value start end ref', defaults=(None,))   # start → end; ref = índice do obstáculo ou None
Side = namedtuple('Side', 'left right')
Vertical = namedtuple('Vertical', 'below above')

MIN_LENGTH = 0.25        # parte da direita da vista que precisa sobrar no plano para o eixo valer
TOLERANCE = 0.001        # m; encostar (a mesma de `collision/rules.py`)
_FAR = 1.0e6             # margem para `cotas.limits` (que procura entre 0 e o comprimento da parede)
_UP = (0.0, 0.0, 1.0)


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def lateral_axis(view_right, plane_normal=_UP, min_length=MIN_LENGTH):
    """Direção da direita (unitária, horizontal) ou None quando a vista não dá um eixo lateral estável."""
    n = plane_normal
    along = _dot(view_right, n)
    x, y = view_right[0] - n[0] * along, view_right[1] - n[1] * along
    length = math.hypot(x, y)
    if length < min_length:
        return None
    return (x / length, y / length, 0.0)


def fixed_axis(local_x, wall_x=None):
    """Eixo lateral fixo: o X da parede (se houver) ou o X local do móvel, projetado na horizontal e unitário; sem
    componente horizontal (móvel deitado de lado), o X do mundo."""
    for vector in (wall_x, local_x):
        if vector is None:
            continue
        length = math.hypot(vector[0], vector[1])
        if length > 1e-6:
            return (vector[0] / length, vector[1] / length, 0.0)
    return (1.0, 0.0, 0.0)


def _span(points, axis):
    values = [_dot(p, axis) for p in points]
    return min(values), max(values)


def gaps(axis, body, obstacles, tolerance=TOLERANCE):
    """`Side(left, right)` do corpo (cantos no mundo) entre os obstáculos (listas de cantos); None sem eixo."""
    if axis is None or not body:
        return None
    depth_axis = _cross(_UP, axis)
    x0, x1 = _span(body, axis)
    d0, d1 = _span(body, depth_axis)
    z0, z1 = _span(body, _UP)
    lanes, refs = [], []
    for i, points in enumerate(obstacles):
        od0, od1 = _span(points, depth_axis)
        if not cotas._vertical_overlap(d0, d1, od0, od1):
            continue                                     # fora do corredor de profundidade
        ox0, ox1 = _span(points, axis)
        oz0, oz1 = _span(points, _UP)
        lanes.append((ox0 - x0 + _FAR, ox1 - x0 + _FAR, oz0, oz1))
        refs.append(i)
    # O corpo entra encolhido pela tolerância: obstáculo encostado (até 1 mm dentro) ainda é vizinho, com cota 0.
    width = max(0.0, (x1 - x0) - 2.0 * tolerance)
    placement = cotas.Placement(_FAR + tolerance, width, z0, z1 - z0, 0.0)
    left, right = cotas.limits(placement, lanes, 2.0 * _FAR)
    d_mid, z_mid = (d0 + d1) / 2.0, (z0 + z1) / 2.0

    def point(x):
        return tuple(axis[k] * x + depth_axis[k] * d_mid + _UP[k] * z_mid for k in range(3))

    def owner(limit, end):
        for i, lane in enumerate(lanes):
            if abs(lane[end] - limit) < 1e-9:
                return refs[i]
        return None

    out_left = out_right = None
    if left > 0.0:
        surface = left - _FAR + x0
        out_left = Gap(max(0.0, x0 - surface), point(min(surface, x0)), point(x0), owner(left, 1))
    if right < 2.0 * _FAR:
        surface = right - _FAR + x0
        out_right = Gap(max(0.0, surface - x1), point(x1), point(max(surface, x1)), owner(right, 0))
    return Side(out_left, out_right)


def vertical(axis, body, obstacles, floor_z, ceiling_z, tolerance=TOLERANCE):
    """`Vertical(below, above)`: do corpo até o primeiro obstáculo abaixo e acima na mesma pegada (faixa lateral e de
    profundidade); sem obstáculo, o piso (`floor_z`) e o teto (`ceiling_z`, None = sem teto), com `ref` -1 e -2."""
    if axis is None or not body:
        return None
    depth_axis = _cross(_UP, axis)
    x0, x1 = _span(body, axis)
    d0, d1 = _span(body, depth_axis)
    z0, z1 = _span(body, _UP)
    below = (floor_z, -1) if floor_z is not None and floor_z <= z0 + tolerance else (None, None)
    top = (ceiling_z, -2) if ceiling_z is not None and ceiling_z >= z1 - tolerance else (None, None)
    for i, points in enumerate(obstacles):
        ox0, ox1 = _span(points, axis)
        od0, od1 = _span(points, depth_axis)
        if not (cotas._vertical_overlap(x0 + tolerance, x1 - tolerance, ox0, ox1)
                and cotas._vertical_overlap(d0 + tolerance, d1 - tolerance, od0, od1)):
            continue                                     # fora da pegada do corpo
        oz0, oz1 = _span(points, _UP)
        if oz1 <= z0 + tolerance and (below[0] is None or oz1 > below[0]):
            below = (oz1, i)
        elif oz0 >= z1 - tolerance and (top[0] is None or oz0 < top[0]):
            top = (oz0, i)
    x_mid, d_mid = (x0 + x1) / 2.0, (d0 + d1) / 2.0

    def point(z):
        return tuple(axis[k] * x_mid + depth_axis[k] * d_mid + _UP[k] * z for k in range(3))

    out_below = Gap(max(0.0, z0 - below[0]), point(min(below[0], z0)), point(z0), below[1]) \
        if below[0] is not None else None
    out_above = Gap(max(0.0, top[0] - z1), point(z1), point(max(top[0], z1)), top[1]) if top[0] is not None else None
    return Vertical(out_below, out_above)
