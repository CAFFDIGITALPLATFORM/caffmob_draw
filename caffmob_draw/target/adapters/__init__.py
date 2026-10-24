"""Adaptadores por tipo (feature 067, D-02): as seções de campos e notas do painel para cada tipo de alvo.

Cada módulo expõe `sections(target)` para os tipos que atende (`KINDS`); o tipo sem adaptador cai no fallback
rotulado de `other.fallback` (RN-04). Python puro: só lê o `Target`.
"""

from .. import resolver as r


def _registry():
    from . import environment, front, geometry, module, other, room
    table = {}
    for adapter in (module, geometry, front, room, environment, other):
        for kind in adapter.KINDS:
            table[kind] = adapter.sections
    return table


def sections_for(target):
    sections = _registry().get(target.kind)
    if sections is None or target.adapter == 'FALLBACK':
        from . import other
        return other.fallback(target)
    return sections(target)


def position_section(target, *, read_only_reason='', move_over=True, essential=True, rotation_index=2,
                     scale=False):
    """Posição e vínculo: a posição do próprio alvo e, se ele se move, o Mover Sobre (RF-009, RF-024)."""
    from ..view import Field, Section
    from ...data.i18n import N_
    read_only = bool(read_only_reason)
    items = [Field('object', 'location', N_("Posição"), read_only, read_only_reason, essential),
             Field('object', 'rotation_euler', N_("Rotação Z") if rotation_index == 2 else N_("Rotação"),
                   read_only, read_only_reason, False, rotation_index)]
    if scale:
        items.append(Field('object', 'scale', N_("Escala")))
    if move_over and target.move_uid:
        items += [Field('move_over', 'enabled', N_("Mover Sobre (botão direito + arraste)"), essential=essential),
                  Field('move_over', 'step'), Field('move_over', 'show_relative', N_("Relativa"))]
    from ..commands import S_POSITION, SECTION_LABELS
    return Section(S_POSITION, SECTION_LABELS[S_POSITION], tuple(items), essential)


def unavailable_cotas(reason):
    """Nota de cotas indisponíveis, com o motivo (RF-018, RF-021 a RF-023)."""
    from ..view import Note, Section
    from ...data.i18n import N_
    return Section('cotas', N_("Cotas"), (Note(N_("Cotas: indisponível para {}."), 'INFO', True, (reason,)),), True)


def cotas_section(target):
    """Cotas fixas do alvo móvel, no escopo de `btm_target.cota_scope` (D-07)."""
    from ..view import Field, Section
    from ...data.i18n import N_
    items = (Field('target', 'cota_scope', N_("Mover"), essential=True),
             Field('selection', 'cota_esquerda', essential=True), Field('selection', 'cota_direita', essential=True),
             Field('selection', 'cota_superior', essential=True), Field('selection', 'cota_inferior', essential=True))
    return Section('cotas', N_("Cotas"), items, True)
