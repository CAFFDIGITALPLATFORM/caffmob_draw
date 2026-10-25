"""Adaptador de geometria livre (feature 067, T046; RF-009, RF-011): rótulos pela orientação no mundo, material real,
posição uma vez só e nenhum texto de limites de biblioteca."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Field, Section
from . import cotas_section, position_section
from .module import sheet_section

KINDS = (r.GEOMETRY,)


def sections(target):
    material = Section('material', N_("Material"), (
        Field('geometry', 'material', N_("Material"), essential=True), Field('geometry', 'finish'),
        Field('geometry', 'fabrication'), Field('geometry', 'component'), Field('geometry', 'kind'),
        Field('geometry', 'plane')), True)
    return [sheet_section(target), material, cotas_section(target), position_section(target)]
