"""Cotas laterais pela vista do usuário (feature 066, T038; D-10, RN-06, RF-015 a RF-019). Python puro, sem `bpy`.

- `lateral_axis`: a direita da vista, projetada no plano de trabalho (piso, ou a face da parede) e só na horizontal.
  Sem uma direção estável (vista ao longo da parede, vista com giro forte), não há eixo e não há cota.
- `gaps`: do exterior do corpo ativo até a primeira superfície de cada lado, ao longo do eixo. Só contam obstáculos
  no mesmo corredor: mesma faixa de altura (`cotas._vertical_overlap`, RN-MEASURE-02) e de profundidade. O limite de
  cada lado sai de `cotas.limits`. Lado livre dá None (nunca um 0 fictício); encostar até a tolerância dá 0.
"""

import math
from collections import namedtuple

from . import cotas

Gap = namedtuple('Gap', 'value start end')     # start → end ao longo do eixo, da esquerda para a direita
Side = namedtuple('Side', 'left right')

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
    lanes = []
    for points in obstacles:
        od0, od1 = _span(points, depth_axis)
        if not cotas._vertical_overlap(d0, d1, od0, od1):
            continue                                     # fora do corredor de profundidade
        ox0, ox1 = _span(points, axis)
        oz0, oz1 = _span(points, _UP)
        lanes.append((ox0 - x0 + _FAR, ox1 - x0 + _FAR, oz0, oz1))
    # O corpo entra encolhido pela tolerância: obstáculo encostado (até 1 mm dentro) ainda é vizinho, com cota 0.
    width = max(0.0, (x1 - x0) - 2.0 * tolerance)
    placement = cotas.Placement(_FAR + tolerance, width, z0, z1 - z0, 0.0)
    left, right = cotas.limits(placement, lanes, 2.0 * _FAR)
    d_mid, z_mid = (d0 + d1) / 2.0, (z0 + z1) / 2.0

    def point(x):
        return tuple(axis[k] * x + depth_axis[k] * d_mid + _UP[k] * z_mid for k in range(3))

    out_left = out_right = None
    if left > 0.0:
        surface = left - _FAR + x0
        out_left = Gap(max(0.0, x0 - surface), point(min(surface, x0)), point(x0))
    if right < 2.0 * _FAR:
        surface = right - _FAR + x0
        out_right = Gap(max(0.0, surface - x1), point(x1), point(max(surface, x1)))
    return Side(out_left, out_right)
