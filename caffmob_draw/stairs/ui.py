"""Painel do editor de escadas no grupo "Escadas" da barra lateral (071 D-23, RF-20 a RF-26)."""
import bpy

from ..data.i18n import tr
from . import core


def draw(layout, context):
    state = context.window_manager.btm_stairs
    e = state.escada()
    editando = bool(state.editando) and bpy.data.objects.get(state.editando) is not None
    col = layout.column()
    if editando:
        col.label(text=tr("Editando: {}").format(state.editando), icon='GREASEPENCIL')
    col.label(text=tr("Tipo"))
    col.row(align=True).prop(state, 'tipo', expand=True)
    if e.tipo != 'reta':
        col.row(align=True).prop(state, 'giro', expand=True)
    col.separator()
    col.label(text=tr("Medidas"))
    grade = col.column(align=True)
    grade.prop(state, 'altura')
    grade.prop(state, 'largura')
    if e.tipo != 'reta':
        grade.prop(state, 'largura_total')
    grade.prop(state, 'comprimento')
    grade.prop(state, 'degrau')
    if e.tipo == 'U':
        grade.prop(state, 'vao')
    if not core.medidas_sao_confortaveis(e):
        col.operator('caffmob.escada_confortavel', icon='SHADERFX')
    plano, texto = core.leitura(e)
    leitura = col.column(align=True)
    leitura.alert = not plano.confortavel
    for parte in texto.split(' · '):
        leitura.label(text=parte)
    leitura.label(text=tr("(confortável)") if plano.confortavel else tr("(fora do conforto: 600–660 mm)"))
    col.separator()
    col.label(text=tr("Peças"))
    pecas = col.row(align=True)
    pecas.prop(state, 'espelhos', toggle=True)
    pecas.prop(state, 'laterais', toggle=True)
    pecas.prop(state, 'corrimao', toggle=True)
    col.prop(state, 'material_frente')
    col.prop(state, 'material_corpo')
    col.prop(state, 'previa')
    col.separator()
    botoes = col.row(align=True)
    if editando:
        botoes.operator('caffmob.escada_aplicar', icon='CHECKMARK')
        botoes.operator('caffmob.escada_nova', icon='FILE_NEW')
    else:
        botoes.operator('caffmob.escada_inserir', text=tr("Inserir no ambiente"), icon='ADD')
    col.label(text=tr("Degraus, espelhos e laterais entram no plano de corte; o corrimão, na lista de ferragens."),
              icon='INFO')
