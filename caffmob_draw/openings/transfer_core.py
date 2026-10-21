"""Implantação pura: canto físico no mundo e distância em mm, sem depender do sentido da parede."""

from math import dist

from . import region_core


def reference_corner(start, end, reference='START', chosen=None):
    """START/END são as pontas ordenadas no mundo; EDGE escolhe a ponta mais próxima do ponto indicado."""
    a, b = sorted((tuple(start), tuple(end)))
    if reference == 'EDGE' and chosen is not None:
        return min((a, b), key=lambda p: dist(p, chosen))
    return b if reference == 'END' else a


def local_x(start, end, corner, distance_mm, width):
    """Distância entre o canto e a borda mais próxima do portal (m)."""
    offset = distance_mm / 1000.0
    return offset if dist(start, corner) <= dist(end, corner) else dist(start, end) - offset - width


def distance_mm(start, end, corner, x, width):
    return 1000.0 * (x if dist(start, corner) <= dist(end, corner) else dist(start, end) - x - width)


def destination(start, end, wall_height, width, height, reference='START', distance=0.0, others=(), chosen=None,
                end_height=None):
    corner = reference_corner(start, end, reference, chosen)
    x = local_x(start, end, corner, distance, width)
    length = dist(start, end)
    if end_height is not None and length > 0:
        # Portal retangular: a menor altura do topo sobre as duas bordas é o teto permitido.
        slope = (end_height - wall_height) / length
        wall_height = min(wall_height + slope * x, wall_height + slope * (x + width))
    return region_core.fit(x, x + width, 0.0, height, length, wall_height, 'DOOR', others)
