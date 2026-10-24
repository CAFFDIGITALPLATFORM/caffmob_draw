"""Adaptadores de parede, porta e janela e revestimento (feature 067, T048; RF-018 a RF-020)."""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Action, Field, Note, Section
from . import position_section, unavailable_cotas

KINDS = (r.WALL, r.OPENING, r.CLADDING)
CLADDING_FIELDS = ('kind', 'width_mm', 'thickness_mm', 'joint_mm', 'min_gap_mm', 'orientation', 'angle', 'band',
                   'band_from', 'band_mm', 'backing', 'backing_material', 'material', 'material_kind',
                   'texture_size_mm', 'grain_angle', 'sheet_w_mm', 'sheet_h_mm', 'sheet_t_mm')
_ESSENTIAL_CLADDING = {'kind', 'width_mm', 'thickness_mm', 'orientation', 'material'}


def sections(target):
    if target.kind == r.WALL:
        if target.library == 'BTM':
            fields = (Field('wall', 'length', essential=True), Field('wall', 'thickness', essential=True),
                      Field('wall', 'height_start', essential=True), Field('wall', 'height_end'), Field('wall', 'offset'))
        else:
            fields = (Field('selection', 'wall_length', essential=True),
                      Field('selection', 'wall_height', essential=True), Field('selection', 'wall_end_height'),
                      Field('selection', 'wall_thickness', essential=True))
        geometry = Section('wall', N_("Parede"), fields + (
            Note(N_("Aberturas e revestimentos desta parede aparecem ao selecioná-los."), 'INFO', False),), True)
        return [geometry, unavailable_cotas(N_("parede: ela não se move no Mover Sobre"))]
    if target.kind == r.OPENING:
        is_door = target.detail == 'DOOR'
        if target.library == 'BTM':
            items = [Field('btm_opening', 'opening_type', essential=True), Field('btm_opening', 'width', essential=True),
                     Field('btm_opening', 'height', essential=True), Field('btm_opening', 'sill_height')]
        else:
            items = [Field('selection', 'width', N_("Largura"), essential=True),
                     Field('selection', 'height', N_("Altura"), essential=True)]
        if not is_door and target.library != 'BTM':
            items.append(Field('selection', 'sill', N_("Peitoril"), essential=True))
        if is_door and target.library == 'HB':
            items.append(Field('door', 'angle', N_("Abertura"), essential=True))
        if is_door and not target.has_leaf:
            items.append(Note(N_("Porta sem folha gerada."), 'INFO'))
        label = N_("Porta") if is_door else N_("Janela")
        return [Section('opening', label, tuple(items), True),
                unavailable_cotas(N_("porta e janela: elas andam com a parede, não no Mover Sobre")),
                position_section(target, move_over=False, essential=False)]
    # Revestimento: os valores do revestimento selecionado; digitar não refaz nada, "Aplicar" refaz (RF-020).
    items = tuple(Field('cladding', name, essential=name in _ESSENTIAL_CLADDING) for name in CLADDING_FIELDS)
    apply = Action('caffmob.target_cladding_apply', N_("Aplicar"), True, '', True)
    diagnostic = Note(N_("Diagnóstico: {}"), 'INFO', False, ('cladding.diagnostic',))
    return [Section('cladding', N_("Revestimento"), items + (apply, diagnostic), True),
            unavailable_cotas(N_("revestimento: ele segue a parede")),
            position_section(target, move_over=False, essential=False)]
