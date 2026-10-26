"""Adaptadores de frente e folha (feature 067, T047; RF-014, RF-017): medidas próprias, presets Abrir e Fechar, e a
folha com seção própria. Onda 5 (T108, RF-100): a frente do módulo rápido edita a abertura pelo editor animado
(`mechanisms`); a frente das bibliotecas HB continua pelos presets do módulo."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Action, Field, Note, Section
from . import cotas_section, finish_section, position_section
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


def _drawer_section(target):
    """072 (D-09, RF-06, RF-12): corrediça da gaveta, trocada com um botão; a gaveta antiga converte ao trocar."""
    if target.detail not in ('DRAWER', 'DRAWER_OLD'):
        return None
    items = [Field('drawer', 'corredica', N_("Corrediça"), essential=True)]
    if target.detail == 'DRAWER':
        items.append(Field('drawer', 'comprimento', N_("Comprimento da corrediça"), True,
                           N_("O maior que cabe na profundidade do vão")))
    else:
        items.append(Note(N_("Gaveta anterior à 1.20.0: escolher a corrediça refaz a caixa pelo construtor."), 'INFO',
                          True))
    return Section('drawer', N_("Gaveta"), tuple(items), True, N_("Gaveta"))


def sections(target):
    reason = N_("Medida da frente gerada pelo módulo: {}").format(target.owner_name)
    sheet = sheet_section(target, reason)          # o veio é de cada frente (RF-041), editável aqui
    if target.kind == r.FRONT:
        if target.library == 'BTM':
            editor = (Field('front_cabinet', 'door_open', N_("Abertura"), essential=True),
                      Field('front_cabinet', 'door_swing', N_("Tipo de abertura")))
        else:
            editor = (Note(MOTION_NOTE, 'INFO', False),)
        motion = Section('front', N_("Frente"), editor + _presets(True), True, N_("Peça"))
        drawer = _drawer_section(target)
        if drawer is not None:
            return [drawer, sheet, motion, finish_section(target), cotas_section(target),
                    position_section(target, read_only_reason=reason, essential=False)]
        return [sheet, motion, finish_section(target), cotas_section(target),
                position_section(target, read_only_reason=reason, essential=False)]
    leaf = Section('leaf', N_("Folha"), (
        Field('aggregate', 'motion', N_("Movimento"), essential=True), Field('aggregate', 'hinge', essential=True),
        Field('aggregate', 'swing_sign'), Field('aggregate', 'max_angle'),
        Field('aggregate', 'open_value', N_("Abertura"), essential=True)), True, N_("Folha"))
    drawer = _drawer_section(target)
    return ([drawer] if drawer is not None else []) + [leaf, sheet, finish_section(target), cotas_section(target),
                                                       position_section(target, read_only_reason=reason,
                                                                        essential=False)]
