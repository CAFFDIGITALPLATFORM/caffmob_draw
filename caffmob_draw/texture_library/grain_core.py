"""Conta do veio da textura (feature 067, D-20, D-30; RF-060, RF-061, RF-063). Python puro, sem `bpy`.

O material é um só por textura; o giro é por objeto, no vetor `btm_grain_rot` (Euler XYZ em radianos) que o nó
Attribute (tipo Object) entrega ao Vector Rotate, antes da escala métrica da imagem. Assim a imagem gira sem esticar e
sem mudar o tamanho físico, e uma chapa não muda as irmãs que usam o mesmo material.

A conta: o veio pedido (H ou V) é um eixo da face semântica da chapa (o eixo local de rótulo Largura para H; Altura,
ou Profundidade na chapa deitada, para V). Na projeção BOX, a face de normal `n` usa os outros dois eixos locais como
(u, v) da imagem, na ordem de `BOX_PLANE`; com UV, u e v são os eixos X e Y locais. A calibração diz se o veio da imagem corre em u (H) ou em
v (V). Se o eixo do veio da imagem já é o eixo pedido, não gira; senão, gira 90° em torno da normal da face.
"""

import math

BOX, UV = 'BOX', 'UV'
ZERO = (0.0, 0.0, 0.0)
# Projeção BOX do Blender 5.2: eixos locais (u, v) da imagem na face de normal n, medidos por render no protótipo T008
# (`tests/blender_067_proto_veio_box.py`): face X → (Z, Y), face Y → (X, Z), face Z → (Y, X). Com UV, (X, Y).
BOX_PLANE = {0: (2, 1), 1: (0, 2), 2: (1, 0)}
UV_PLANE = (0, 1)


def grain_axis(grain, fields):
    """Eixo local do veio pedido. `fields` = {eixo: 'WIDTH' | 'HEIGHT' | 'DEPTH'} dos dois eixos da face."""
    if grain == 'H':
        wanted = ('WIDTH',)
    elif grain == 'V':
        wanted = ('HEIGHT', 'DEPTH')
    else:
        return None
    for label in wanted:
        for axis, field in fields.items():
            if field == label:
                return axis
    return None


def rotation(grain, thickness_axis, fields, image_axis='H', projection=BOX):
    """Euler (x, y, z) que leva o veio da imagem ao eixo pedido na face da chapa; ZERO quando não precisa girar."""
    axis = grain_axis(grain, fields)
    if axis is None or thickness_axis is None:
        return ZERO
    normal = 2 if projection == UV else thickness_axis
    u, v = UV_PLANE if projection == UV else BOX_PLANE[normal]
    image = u if image_axis != 'V' else v
    if image == axis or axis == normal:
        return ZERO
    out = [0.0, 0.0, 0.0]
    out[normal] = math.pi / 2.0
    return tuple(out)


def legacy_rotated():
    """A variante `<nome> ROTATED` girava o Mapping 90° em Z (M-05)."""
    return (0.0, 0.0, math.pi / 2.0)


def calibration_from_size(width_px, height_px):
    """Palpite inicial da calibração pela proporção da imagem: em pé, veio V; deitada ou quadrada, H (editável)."""
    try:
        return 'V' if float(height_px) > float(width_px) else 'H'
    except (TypeError, ValueError):
        return 'H'
