"""Medidas semânticas da chapa (feature 067, D-11; RF-006, RF-008, RF-011): Python puro.

A caixa da malha em coordenadas locais vezes a escala acumulada dos ancestrais (as colunas de `matrix_world`),
nunca o AABB da tela nem `obj.dimensions` (que ignora a escala do pai). A espessura é o menor eixo. Os outros dois
recebem o nome pela direção no referencial dado (o do módulo dono, ou o mundo para a geometria livre): o eixo mais
vertical é a Altura; dos horizontais, o mais alinhado a X é a Largura e o mais alinhado a Y é a Profundidade.
Assim um painel em pé mostra Altura e uma prateleira mostra Largura × Profundidade.

As matrizes são lidas por índice `m[linha][coluna]`, o que serve tanto para `mathutils.Matrix` quanto para listas.
"""

import math
from dataclasses import dataclass

WIDTH, HEIGHT, DEPTH, THICKNESS = 'WIDTH', 'HEIGHT', 'DEPTH', 'THICKNESS'
_EPS_SCALE = 1e-9
_SHEAR_TOL = 1e-5


class PartGeometryError(Exception):
    """Medida recusada (mensagem pronta para o usuário)."""


@dataclass(frozen=True)
class AxisMeasure:
    field: str          # WIDTH, HEIGHT, DEPTH ou THICKNESS
    axis: int           # eixo local da malha (0 = X, 1 = Y, 2 = Z)
    value: float        # comprimento real, em unidades da cena


@dataclass(frozen=True)
class PartMeasures:
    face: tuple         # dois AxisMeasure, na ordem Largura, Altura, Profundidade
    thickness: AxisMeasure
    normal: tuple       # direção da espessura no referencial, unitária

    def by_field(self, field):
        for item in self.face + (self.thickness,):
            if item.field == field:
                return item
        return None


def _finite(*values):
    return all(math.isfinite(v) for v in values)


def _column(matrix, index):
    return tuple(float(matrix[row][index]) for row in range(3))


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _length(a):
    return math.sqrt(_dot(a, a))


def _to_reference(direction, reference):
    if reference is None:
        return direction
    # `reference` é uma rotação (colunas = eixos do referencial no mundo): coordenadas = transposta × direção.
    return tuple(_dot(_column(reference, i), direction) for i in range(3))


def scale_axes(matrix_world):
    """Direções unitárias e escalas dos três eixos locais no mundo. Recusa escala zero, shear e não finito."""
    columns = [_column(matrix_world, i) for i in range(3)]
    if not _finite(*(v for c in columns for v in c)):
        raise PartGeometryError("A transformação da peça tem valor não finito.")
    scales = [_length(c) for c in columns]
    if min(scales) < _EPS_SCALE:
        raise PartGeometryError("A peça tem escala zero num eixo: aplique a escala antes de editar.")
    units = [tuple(v / s for v in c) for c, s in zip(columns, scales)]
    for i, j in ((0, 1), (0, 2), (1, 2)):
        if abs(_dot(units[i], units[j])) > _SHEAR_TOL:
            raise PartGeometryError("A peça está distorcida (shear): aplique a transformação antes de editar.")
    return units, scales


def measure(local_min, local_max, matrix_world, reference=None):
    """Medidas da chapa a partir da caixa local da malha e da matriz mundial (com a escala dos ancestrais)."""
    if not _finite(*local_min, *local_max):
        raise PartGeometryError("A malha da peça tem coordenada não finita.")
    units, scales = scale_axes(matrix_world)
    lengths = [abs(float(local_max[i]) - float(local_min[i])) * scales[i] for i in range(3)]
    thickness_axis = min(range(3), key=lambda i: (lengths[i], i))
    face_axes = [i for i in range(3) if i != thickness_axis]
    directions = {i: _to_reference(units[i], reference) for i in range(3)}

    height_axis = max(face_axes, key=lambda i: (abs(directions[i][2]), -i))
    other = next(i for i in face_axes if i != height_axis)
    if abs(directions[height_axis][2]) < abs(directions[thickness_axis][2]):
        # A espessura é o eixo mais vertical: peça deitada, a face é Largura × Profundidade.
        first, second = sorted(face_axes, key=lambda i: (-abs(directions[i][0]), i))
        face = (AxisMeasure(WIDTH, first, lengths[first]), AxisMeasure(DEPTH, second, lengths[second]))
    elif abs(directions[other][0]) >= abs(directions[other][1]):
        face = (AxisMeasure(WIDTH, other, lengths[other]), AxisMeasure(HEIGHT, height_axis, lengths[height_axis]))
    else:
        face = (AxisMeasure(HEIGHT, height_axis, lengths[height_axis]), AxisMeasure(DEPTH, other, lengths[other]))
    normal = directions[thickness_axis]
    return PartMeasures(face, AxisMeasure(THICKNESS, thickness_axis, lengths[thickness_axis]), normal)


def validate_length(value):
    """Valor digitado para uma medida da chapa: positivo e finito."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise PartGeometryError("Medida inválida.") from None
    if not math.isfinite(number):
        raise PartGeometryError("Medida não finita.")
    if number <= 0.0:
        raise PartGeometryError("A medida precisa ser maior que zero.")
    return number
