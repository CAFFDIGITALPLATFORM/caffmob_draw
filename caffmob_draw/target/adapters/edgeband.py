"""Adaptador da fita de borda selecionada (feature 067, T105; RF-084).

Selecionar a faixa abre as propriedades dela: material ou cor lisa (a cor lisa não destrói a imagem do material),
espessura, largura aparente, bordas atendidas, comprimento, vínculo (o componente) e estado. A fita não se move
sozinha: acompanha o componente.
"""

from ...data.i18n import N_
from .. import resolver as r
from ..view import Action, Field, Note, Section
from . import unavailable_cotas

KINDS = (r.EDGEBAND,)


def sections(target):
    items = (Field('edgeband', 'use_color', N_("Cor lisa"), essential=True),
             Field('edgeband', 'material', N_("Material"), essential=True),
             Field('edgeband', 'color', N_("Cor")),
             Field('edgeband', 'thickness', N_("Espessura"), essential=True),
             Field('edgeband', 'coverage_width', N_("Largura aparente"), True, N_("Medida das chapas cobertas")),
             Field('edgeband', 'length', N_("Comprimento"), True, N_("Medida das chapas cobertas")),
             Note(N_("Bordas atendidas: {}"), 'MOD_EDGESPLIT', True, ('edgeband.edges',)),
             Note(N_("Vínculo: {}"), 'LINKED', True, ('edgeband.owner',)),
             Note(N_("Estado: {}"), 'INFO', False, ('edgeband.state',)),
             Action('caffmob.edgeband_apply', N_("Mudar cor da fita"), True, '', False))
    return [Section('edgeband', N_("Fita de borda"), items, True),
            unavailable_cotas(N_("fita de borda (acompanha o componente)"))]
