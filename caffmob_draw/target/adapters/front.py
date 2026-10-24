"""Adaptadores de frente e folha (feature 067, T047; RF-014, RF-017): medidas próprias, movimento atual somente leitura
até a onda 5, presets Abrir e Fechar, e a folha com seção própria."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Action, Field, Note, Section
from . import cotas_section, position_section
from .module import sheet_section

KINDS = (r.FRONT, r.LEAF)
MOTION_NOTE = N_("O movimento desta frente é editado no módulo; aqui ele só é mostrado.")
# `caffmob.fronts_set_open` no escopo da peça selecionada (Peça) e do módulo dono (Todas as frentes).
_PRESETS = ((N_("Abrir 90°"), 'OPEN_90', 'SELECTED'), (N_("Abrir 45°"), 'OPEN_45', 'SELECTED'),
            (N_("Fechar"), 'CLOSE', 'SELECTED'), (N_("Abrir todas as frentes do módulo"), 'OPEN_90', 'ACTIVE_MODULE'),
            (N_("Fechar todas as frentes do módulo"), 'CLOSE', 'ACTIVE_MODULE'))


def _presets(essential):
    return tuple(Action('caffmob.fronts_set_open', label, True, '', essential and scope == 'SELECTED',
                        (('scope', scope), ('mode', mode)))
                 for label, mode, scope in _PRESETS)


def sections(target):
    reason = N_("Medida da frente gerada pelo módulo: {}").format(target.owner_name)
    sheet = sheet_section(target, reason, grain=target.kind == r.LEAF)
    if target.kind == r.FRONT:
        motion = Section('front', N_("Frente"), (Note(MOTION_NOTE, 'INFO', False),) + _presets(True), True,
                         N_("Peça"))
        return [sheet, motion, cotas_section(target),
                position_section(target, read_only_reason=reason, essential=False)]
    leaf = Section('leaf', N_("Folha"), (
        Field('aggregate', 'motion', N_("Movimento"), essential=True), Field('aggregate', 'hinge', essential=True),
        Field('aggregate', 'swing_sign'), Field('aggregate', 'max_angle'),
        Field('aggregate', 'open_value', N_("Abertura"), essential=True)), True, N_("Folha"))
    return [leaf, sheet, cotas_section(target), position_section(target, read_only_reason=reason, essential=False)]
