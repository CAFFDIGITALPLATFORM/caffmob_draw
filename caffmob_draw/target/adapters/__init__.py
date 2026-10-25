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


def finish_section(target, essential=False):
    """Acabamentos (MAT-03, RF-043): Interno, Externo, Frentes e Fita com o material efetivo ("Múltiplos" com a
    inspeção por peça), e o rascunho para aplicar: material, escala, veio e escopo."""
    from ..view import Action, Field, Note, Section
    from ...customize import finish_core as fc
    from ...data.i18n import N_
    labels = {fc.INTERNAL: N_("Interno"), fc.EXTERNAL: N_("Externo"), fc.FRONTS: N_("Frentes"), fc.EDGE: N_("Fita")}
    items = []
    for domain, material, rows in target.finish:
        shown = N_("Múltiplos") if material == fc.MULTIPLE else (material or N_("sem material"))
        items.append(Note(N_("{}: {}"), 'MATERIAL', True, (labels[domain], shown)))
        if material == fc.MULTIPLE:
            items += [Note(N_("  {}: {}"), 'DOT', False, (piece, value or N_("sem material"))) for piece, value in rows]
    if not target.finish_roles or not target.finish:
        items.append(Note(N_("Sem papéis de acabamento: classifique as peças (Object Mode) ou as faces (Edit Mode)."),
                          'INFO', True))
        items.append(Action('caffmob.finish_classify', N_("Classificar peças"), True, '', True))
        items.append(Action('caffmob.finish_classify_preview', N_("Prévia dos papéis"), True, '', False))
        return Section('finish', N_("Acabamentos"), tuple(items), essential)
    items += [Field('finish_draft', 'domain', N_("Aplicar em"), essential=True),
              Field('finish_draft', 'material', N_("Material"), essential=True),
              Field('finish_draft', 'scale_mm'), Field('finish_draft', 'grain', N_("Veio das frentes"))]
    if target.finish_scope_part:
        items.append(Field('finish_draft', 'scope', N_("Escopo"), essential=True))
    items += [Action('caffmob.finish_apply_draft', N_("Aplicar acabamento"), True, '', True),
              Action('caffmob.finish_classify_preview', N_("Prévia dos papéis"), True, '', False)]
    return Section('finish', N_("Acabamentos"), tuple(items), essential)


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
