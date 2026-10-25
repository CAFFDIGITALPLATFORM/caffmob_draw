"""Adaptadores de módulo, chapa de módulo e membro autoral (feature 067, T045; RF-006 a RF-010, RF-015, RF-016)."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Action, Field, Note, Section
from . import cotas_section, finish_section, position_section

KINDS = (r.MODULE, r.PART, r.MEMBER)
GRAIN_NOTE = N_("Veio guardado na peça e enviado ao corte; o visual é aplicado na onda 3.")


def library_reason(target):
    return N_("Esta peça é gerada pelo módulo: {}").format(target.owner_name) if target.owner_name else \
        N_("Esta peça é gerada pelo módulo.")


def sheet_section(target, read_only_reason='', essential=True, grain=True):
    """As medidas da própria chapa: duas da face e a espessura, com os rótulos da orientação instalada."""
    labels = {'WIDTH': N_("Largura"), 'HEIGHT': N_("Altura"), 'DEPTH': N_("Profundidade")}
    items = []
    if target.measure_error:
        items.append(Note(target.measure_error, 'ERROR'))
    face = target.measures.face if target.measures is not None else ()
    names = ('part_a', 'part_b')
    for i, prop in enumerate(names):
        label = labels.get(face[i].field, '') if i < len(face) else ''
        items.append(Field('selection', prop, label, bool(read_only_reason), read_only_reason, essential))
    items.append(Field('selection', 'part_thickness', N_("Espessura"), bool(read_only_reason), read_only_reason,
                       essential))
    if read_only_reason:
        items.append(Note(read_only_reason, 'LOCKED'))
        items.append(Action('caffmob_draw.authored_adopt', N_("Adotar como autoral"), True, '', essential))
    if grain:
        items.append(Field('part', 'grain', N_("Veio"), essential=essential))
        items.append(Note(GRAIN_NOTE, 'INFO', False))
    return Section('sheet', N_("Chapa"), tuple(items), True)


def sections(target):
    if target.kind == r.MODULE:
        dims = Section('dimensions', N_("Dimensões"), (
            Field('selection', 'width', N_("Largura"), essential=True),
            Field('selection', 'height', N_("Altura"), essential=True),
            Field('selection', 'depth', N_("Profundidade"), essential=True)), True)
        # Cotas antigas (afastamento da parede e Mover na Parede) como ação na Completa (RF-030, T094).
        legacy = Section('legacy_cotas', N_("Cotas antigas"), (
            Field('target', 'legacy_cotas'), Field('selection', 'afastamento'), Field('selection', 'anterior'),
            Field('selection', 'posterior'), Field('selection', 'inferior'), Field('selection', 'superior'),
            Action('caffmob.move_on_wall', N_("Mover na Parede"))), False)
        return [dims, finish_section(target), cotas_section(target), position_section(target), legacy]
    if target.kind == r.MEMBER:
        rule = Section('member', N_("Regra do membro"), (
            Field('member', 'rule', N_("Regra dimensional"), essential=True),
            Field('member', 'role', N_("Papel")), Field('member', 'axis'), Field('member', 'offset_mm')), True)
        return [sheet_section(target), rule, finish_section(target), cotas_section(target), position_section(target)]
    # Chapa de módulo: autoral edita a própria chapa; de biblioteca é somente leitura com o motivo (D-06).
    reason = '' if target.detail == 'AUTHORED' else library_reason(target)
    return [sheet_section(target, reason), finish_section(target), cotas_section(target),
            position_section(target, read_only_reason=reason or '', essential=False)]
