"""Caixas orientadas e sobreposição entre elas (feature 004, T004; D-12, D-19). Python puro, sem `bpy`.

Uma caixa orientada (`OBB`) tem centro, três eixos unitários (no mundo) e meias medidas. A sobreposição usa o teste dos
eixos separadores (as três faces de cada caixa e os nove produtos vetoriais): se algum eixo separa as caixas, não há
sobreposição. Quando há, a profundidade é a menor sobreposição entre os eixos testados, e `push` é o deslocamento de A
que acaba com ela pelo caminho mais curto (usado pelo "Afastar até encostar").
"""

import math
from collections import namedtuple
from dataclasses import dataclass

_EPS = 1e-9


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


@dataclass(frozen=True)
class OBB:
    center: tuple
    axes: tuple      # três vetores unitários
    half: tuple      # meias medidas ao longo de cada eixo

    def corners(self):
        out = []
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                for sz in (-1.0, 1.0):
                    s = (sx, sy, sz)
                    out.append(tuple(self.center[k] + sum(self.axes[i][k] * self.half[i] * s[i] for i in range(3))
                                     for k in range(3)))
        return out

    def aabb(self):
        ext = tuple(sum(abs(self.axes[i][k]) * self.half[i] for i in range(3)) for k in range(3))
        return (tuple(self.center[k] - ext[k] for k in range(3)), tuple(self.center[k] + ext[k] for k in range(3)))


def from_box(origin, axes, lo, hi):
    """Caixa local `(lo, hi)` (já com a escala) de um objeto com origem e eixos unitários no mundo."""
    mid = tuple((lo[i] + hi[i]) / 2.0 for i in range(3))
    center = tuple(origin[k] + sum(axes[i][k] * mid[i] for i in range(3)) for k in range(3))
    return OBB(center, tuple(tuple(a) for a in axes), tuple(abs(hi[i] - lo[i]) / 2.0 for i in range(3)))


def _radius(box, axis):
    return sum(box.half[i] * abs(_dot(box.axes[i], axis)) for i in range(3))


def _sat_axes(a, b):
    """Os 15 eixos do teste de separação (3 de A, 3 de B e os 9 produtos vetoriais), unitários; os degenerados saem."""
    axes = list(a.axes) + list(b.axes)
    for i in range(3):
        for j in range(3):
            axes.append(_cross(a.axes[i], b.axes[j]))
    out = []
    for axis in axes:
        length = math.sqrt(_dot(axis, axis))
        if length >= 1e-6:
            out.append((axis[0] / length, axis[1] / length, axis[2] / length))
    return out


def overlap(a, b):
    """None se as caixas não se sobrepõem; senão {'depth', 'push', 'axis'} (axis: 0-2 eixos de A, 3-5 de B, 6+)."""
    t = _sub(b.center, a.center)
    axes = list(a.axes) + list(b.axes)
    for i in range(3):
        for j in range(3):
            axes.append(_cross(a.axes[i], b.axes[j]))
    best = None
    for index, axis in enumerate(axes):
        length = math.sqrt(_dot(axis, axis))
        if length < 1e-6:
            continue
        axis = (axis[0] / length, axis[1] / length, axis[2] / length)
        dist = _dot(t, axis)
        amount = _radius(a, axis) + _radius(b, axis) - abs(dist)
        if amount < -_EPS:
            return None
        if best is None or amount < best[0] - _EPS:
            sign = -1.0 if dist > 0 else 1.0
            best = (max(0.0, amount), tuple(axis[k] * sign * max(0.0, amount) for k in range(3)), index)
    if best is None:
        return None
    return {'depth': best[0], 'push': best[1], 'axis': best[2]}


def aabb_overlap(a, b, margin=0.0):
    (alo, ahi), (blo, bhi) = a, b
    return all(alo[i] - margin <= bhi[i] and blo[i] - margin <= ahi[i] for i in range(3))


# Feature 066 (T034, D-04): primeiro contato de A andando `delta` contra B parado.
Sweep = namedtuple('Sweep', 't_enter t_exit t_touch normal')


def _interval(c, v, r):
    """Trecho de t em que |c − v·t| < r num eixo; (None, None) quando nunca, (−inf, inf) quando sempre."""
    if abs(v) < 1e-12:
        return (-math.inf, math.inf) if abs(c) < r else (None, None)
    t0, t1 = (c - r) / v, (c + r) / v
    return (t0, t1) if t0 <= t1 else (t1, t0)


def sweep_toi(a, delta, b, tolerance=0.0):
    """A anda `delta` (t de 0 a 1) e B fica parado; exato nos 15 eixos do SAT.

    Devolve None quando, de t = 0 a t = 1, A não penetra B além de `tolerance` (encostar ou passar raspando não
    conta). Senão
    `Sweep(t_enter, t_exit, t_touch, normal)`:
    - `t_enter`/`t_exit`: trecho em que a sobreposição passa de `tolerance` (pode começar antes de 0: já penetrado);
    - `t_touch`: quando as caixas começam a se tocar (≤ `t_enter`), a posição de parada sem penetrar;
    - `normal`: eixo do contato, unitário, de B para A (para onde A teria de recuar).
    """
    t = _sub(b.center, a.center)
    enter, leave = -math.inf, math.inf
    touch, normal = -math.inf, None
    for axis in _sat_axes(a, b):
        c, v = _dot(t, axis), _dot(delta, axis)
        r = _radius(a, axis) + _radius(b, axis)
        lo, hi = _interval(c, v, r - tolerance)
        if lo is None:
            return None
        enter, leave = max(enter, lo), min(leave, hi)
        if enter >= leave:
            return None
        lo_touch, _hi = _interval(c, v, r)
        if lo_touch is not None and lo_touch > touch:
            touch = lo_touch
            side = c - v * lo_touch                  # B − A no eixo, no instante do toque
            sign = -1.0 if side > 0 else 1.0
            normal = (axis[0] * sign, axis[1] * sign, axis[2] * sign)
    if leave <= 0.0 or enter >= 1.0:
        return None
    return Sweep(enter, leave, min(touch, enter), normal)
