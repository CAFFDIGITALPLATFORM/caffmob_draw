"""Adaptadores de objeto livre, anotação e seleção múltipla, e o fallback rotulado (feature 067, T050; RF-024 a
RF-026, RN-04)."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Field, Note, Section
from . import cotas_section, position_section, unavailable_cotas

KINDS = (r.OTHER, r.ANNOTATION, r.MULTIPLE)


def sections(target):
    if target.kind == r.OTHER:
        if not target.move_uid:
            return [position_section(target, rotation_index=-1, scale=True),
                    Section('limits', N_("Limites"), (Note(N_("Objeto sem corpo: não se move no Mover Sobre.")),),
                            True), unavailable_cotas(N_("objeto sem corpo"))]
        moving = Note(N_("Mover e cotas atuam em: {}"), 'INFO', True, ('target.move_name',))
        position = position_section(target, rotation_index=-1, scale=True)
        position = Section(position.id, position.label, (moving,) + position.items, True)
        return [position, cotas_section(target)]
    if target.kind == r.ANNOTATION:
        # Adaptador mínimo: sem colisão, limites nem Mover Sobre (RF-025).
        return [position_section(target, move_over=False, rotation_index=-1),
                unavailable_cotas(N_("cota e anotação"))]
    common = Section('multiple', N_("Comuns aos selecionados"), (
        Field('selection', 'multi_thickness', N_("Espessura"), essential=True, mixed=True),
        Note(N_("Campos com valores diferentes mostram \"Múltiplos\"; editar aplica a todos num passo de Desfazer."),
             'INFO', False)), True)
    return [common, cotas_section(target)]


def fallback(target):
    """Tipo sem adaptador: o painel diz o que é e o que não sabe editar, sem fingir capacidade (RN-04)."""
    cotas = cotas_section(target) if target.move_uid else unavailable_cotas(N_("este tipo"))
    note = Note(N_("Tipo sem painel próprio: {}. Só a posição pode ser editada aqui."), 'INFO', True,
                ('target.kind_label',))
    return [Section('fallback', N_("Objeto"), (note,), True), cotas, position_section(target, rotation_index=-1)]
