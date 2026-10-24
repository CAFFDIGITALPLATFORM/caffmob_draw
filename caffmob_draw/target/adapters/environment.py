"""Adaptadores de piso e teto, luz e câmera (feature 067, T049; RF-021 a RF-023): só os campos que valem para o tipo,
com cotas indisponíveis e o motivo."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Field, Note, Section
from . import position_section, unavailable_cotas

KINDS = (r.FLOOR, r.CEILING, r.LIGHT, r.CAMERA)


def _light(target):
    items = [Field('light', 'type', N_("Tipo"), essential=True), Field('light', 'color', essential=True),
             Field('light', 'energy', N_("Potência"), essential=True)]
    if target.detail == 'AREA':
        items += [Field('light', 'shape'), Field('light', 'size', N_("Tamanho"), essential=True)]
    elif target.detail in ('POINT', 'SPOT'):
        items.append(Field('light', 'shadow_soft_size', N_("Raio"), essential=True))
        if target.detail == 'SPOT':
            items += [Field('light', 'spot_size'), Field('light', 'spot_blend')]
    elif target.detail == 'SUN':
        items.append(Field('light', 'angle'))
    return Section('light', N_("Luz"), tuple(items), True)


def _camera():
    return Section('camera', N_("Câmera"), (
        Field('camera', 'type', N_("Projeção"), essential=True), Field('camera', 'lens', N_("Lente"), essential=True),
        Field('camera', 'ortho_scale'), Field('camera', 'clip_start', essential=True),
        Field('camera', 'clip_end', essential=True), Field('camera', 'shift_x'), Field('camera', 'shift_y'),
        Field('camera', 'sensor_width')), True)


def sections(target):
    if target.kind == r.LIGHT:
        return [_light(target), unavailable_cotas(N_("luz: ela não se move no Mover Sobre")),
                position_section(target, move_over=False, rotation_index=-1)]
    if target.kind == r.CAMERA:
        return [_camera(), unavailable_cotas(N_("câmera")),
                position_section(target, move_over=False, rotation_index=-1)]
    label = N_("Piso") if target.kind == r.FLOOR else N_("Teto")
    surface = Section('surface', label, (
        Field('object', 'dimensions', N_("Medidas"), True, N_("As medidas seguem o contorno das paredes."), True),
        Field('object', 'active_material', N_("Material"), essential=True),
        Note(N_("O contorno segue as paredes do ambiente."), 'INFO', False)), True)
    return [surface, unavailable_cotas(N_("piso e teto"))]
