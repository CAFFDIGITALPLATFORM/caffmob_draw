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
# (018, T009) O veio aparece em duas grafias: H/V nas peças das bibliotecas, HORIZONTAL/VERTICAL no armário v2.
HV = {'H': 'H', 'HORIZONTAL': 'H', 'V': 'V', 'VERTICAL': 'V'}
# Projeção BOX do Blender 5.2: eixos locais (u, v) da imagem na face de normal n, medidos por render no protótipo T008
# (`tests/blender_067_proto_veio_box.py`): face X → (Z, Y), face Y → (X, Z), face Z → (Y, X). Com UV, (X, Y).
BOX_PLANE = {0: (2, 1), 1: (0, 2), 2: (1, 0)}
UV_PLANE = (0, 1)


def normalize(grain):
    """'H' ou 'V' do veio, aceitando as duas grafias do projeto; None quando a peça não tem veio."""
    return HV.get(str(grain or '').upper())


def grain_axis(grain, fields):
    """Eixo local do veio pedido. `fields` = {eixo: 'WIDTH' | 'HEIGHT' | 'DEPTH'} dos dois eixos da face."""
    axis = normalize(grain)
    if axis is None:
        return None
    for label in (('WIDTH',) if axis == 'H' else ('HEIGHT', 'DEPTH')):
        for eixo, field in fields.items():
            if field == label:
                return eixo
    return None


def total_angle(grain, angle=0.0):
    """Ângulo visual do veio em graus: 0 no horizontal, 90 no vertical, mais o ângulo livre da peça (D-05)."""
    return (90.0 if normalize(grain) == 'V' else 0.0) + float(angle or 0.0)


def direction(grain, angle=0.0):
    """'H' ou 'V' do corte pelo múltiplo de 90 mais próximo do veio visual; 'NONE' sem enum e sem ângulo (RN-10)."""
    if normalize(grain) is None and not angle:
        return 'NONE'
    total = total_angle(grain, angle) % 180.0
    return 'H' if total < 45.0 or total >= 135.0 else 'V'


def rotation(grain, thickness_axis, fields, image_axis='H', projection=BOX, angle=0.0):
    """Euler (x, y, z) do veio na face da chapa: a conta do enum mais o ângulo livre, na normal da face.

    `angle` é em graus e soma ao giro do enum (D-05), então o veio visual acompanha o de corte; sem a espessura
    medida não há normal, e aí não há giro.
    """
    normal = 2 if projection == UV else thickness_axis
    if normal is None:
        return ZERO
    giro = 0.0
    axis = grain_axis(grain, fields)
    if axis is not None and thickness_axis is not None:
        u, v = UV_PLANE if projection == UV else BOX_PLANE[normal]
        image = u if image_axis != 'V' else v
        if image != axis and axis != normal:
            giro = math.pi / 2.0
    out = [0.0, 0.0, 0.0]
    out[normal] = giro + math.radians(float(angle or 0.0))
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
