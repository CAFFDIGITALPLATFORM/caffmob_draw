"""Painel de 7 abas da janela própria do construtor de armário v2 (feature 023, T006/T007/T011/T022; RN-01, RN-07).

Desenha na região lateral (N) do Image Editor da janela própria, no estilo **híbrido** decidido em 2026-11-25: o chrome
funcional do Blender (painéis, ícones, espaçamento de 1 unidade) com a paleta, os rótulos e a organização do mockup —
barra de título com as dimensões, barra de abas em duas linhas, barra de ferramentas, barra de seleção com as ações em
lote, a aba ativa (só ela aberta), a lista de peças e os botões OK/Aplicar/Cancelar.

O que o Blender não dá (titlebar própria do sistema, abas horizontais com pintura própria) fica de fora por decisão da
RN-01; não é pendência.

A aba ativa vem de `window.sessao().aba` e é persistida **por cena** (RN-07). Os botões de comando não escrevem na cena:
enfileiram um pedido (`caffmob.armario_v2_window_pedido`) que o modal processa (RN-02).
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import build
from . import ops as ops_v2
from . import selecao
from . import validar
from . import window as win_mod

CATEGORIA = "Construtor Armário"
PAPEIS_PORTA = ('PORTA', 'FOLHA')

ABAS = (
    ('ESTRUTURA', "Estrutura", 'CUBE'),
    ('DIVISOES', "Divisões", 'GRID'),
    ('GAVETAS', "Gavetas", 'MOD_ARRAY'),
    ('INTERNOS', "Internos", 'MOD_BEVEL'),
    ('PORTAS', "Portas", 'MESH_PLANE'),
    ('DESLIZANTES', "Deslizantes", 'ARROW_LEFTRIGHT'),
    ('FUNDOS', "Fundos", 'MOD_SOLIDIFY'),
)


def _armario(context):
    """Armário v2 da sessão ativa, ou o primeiro da cena (fallback)."""
    s = win_mod.sessao()
    if s is not None and s.armario_root is not None:
        return s.armario_root
    raiz = build.raiz_de(getattr(context, 'active_object', None))
    if raiz is not None:
        return raiz
    colecao = bpy.data.collections.get(build.COLECAO)
    if colecao is not None:
        for candidato in colecao.objects:
            if build.e_raiz(candidato):
                return candidato
    return None


def _tem_estrutura(armario):
    return (armario.lateral_esq_ativa or armario.lateral_dir_ativa or
            armario.base_inf_ativa or armario.base_sup_ativa or armario.fundo_ativo)


def _erros(raiz):
    """Violações GEO-001/GEO-002 do armário (lista vazia quando está tudo dentro)."""
    return validar.violacoes_da_raiz(raiz) if raiz is not None else []


def _aba_atual():
    s = win_mod.sessao()
    return s.aba if s is not None else win_mod.ABA_PADRAO


def _selecionados():
    s = win_mod.sessao()
    return list(s.selecionados) if s is not None else []


class _AbaPainel:
    """Painel de aba: só aparece quando é a aba ativa da janela (RN-07)."""

    ABA = ''

    @classmethod
    def poll(cls, context):
        s = win_mod.sessao()
        return s is None or s.aba == cls.ABA


# Cabeçalho / abas / empty state ------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowHeader(bpy.types.Panel):
    """Cabeçalho da janela: título com dimensões, abas, seleção e empty state."""
    bl_idname = "BTM_PT_ArmarioV2WindowHeader"
    bl_label = "Construtor de Armários"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            layout.label(text="Nenhum armário v2 na cena")
            return
        armario = raiz.btm_armario

        # Barra de título do mockup, com o chrome do Blender.
        topo = layout.box()
        linha = topo.row(align=True)
        linha.label(text=tr("Construtor de Armários"), icon="MESH_CUBE")
        linha.label(text=tr("{} × {} × {} mm").format(f"{armario.largura:.0f}", f"{armario.altura:.0f}",
                                                       f"{armario.profundidade:.0f}"),
                    icon="FULLSCREEN_ENTER")
        acoes = topo.row(align=True)
        acoes.operator("caffmob.armario_v2_window_aba", text="Contrato", icon="FILE_TEXT").alvo = 'ESTRUTURA'
        acoes.operator("caffmob.armario_v2_window_export_json", text="Exportar JSON", icon="EXPORT")
        acoes.operator("caffmob.armario_v2_window_tema", text="", icon="COLOR")

        # Barra de abas horizontal única, com a aba ativa deprimida.
        ativa = _aba_atual()
        linha = topo.row(align=True)
        for chave, rotulo, icone in ABAS:
            linha.operator("caffmob.armario_v2_window_aba", text="", icon=icone,
                           depress=(chave == ativa)).alvo = chave
        rotulo_ativo = dict((c, r) for c, r, _i in ABAS).get(ativa, ativa)
        topo.label(text=tr("Aba: {}").format(tr(rotulo_ativo)), icon="INFO")

        # Barra "Selecionado: …" (uma peça ou o conjunto).
        itens = _selecionados()
        rotulo = selecao.rotulo_conjunto(itens)
        caixa = layout.box()
        caixa.label(text=tr("Selecionado: {}").format(rotulo) if rotulo
                    else tr("Selecionado: nenhuma peça (clique numa peça do preview)"),
                    icon="RESTRICT_SELECT_OFF")
        if itens:
            lote = caixa.row(align=True)
            for acao, texto, icone in (('MOVER_ESQ', "←", 'TRIA_LEFT'), ('MOVER_DIR', "→", 'TRIA_RIGHT'),
                                       ('MOVER_CIMA', "↑", 'TRIA_UP'), ('MOVER_BAIXO', "↓", 'TRIA_DOWN')):
                lote.operator("caffmob.armario_v2_window_lote", text=texto, icon=icone).acao = acao
            lote.operator("caffmob.armario_v2_window_lote", text="Espelhar", icon="MOD_MIRROR").acao = 'ESPELHAR'
            lote.operator("caffmob.armario_v2_window_duplicar", text="", icon="DUPLICATE")
            lote.operator("caffmob.armario_v2_window_medida", text="Medida", icon="DRIVER_DISTANCE")
            lote.operator("caffmob.armario_v2_window_lote", text="Apagar", icon="TRASH").acao = 'APAGAR'

        erros = _erros(raiz)
        for erro in erros[:3]:
            layout.label(text=f"{erro['codigo']}: {erro['nome']} {erro['detalhe']}", icon="ERROR")

        # Empty state: sem nenhuma chapa da caixa ligada.
        if not _tem_estrutura(armario):
            box = layout.box()
            box.label(text="Janela de Armário Vazia", icon="INFO")
            box.label(text="Ative as chapas ou use a montagem rápida.")
            row = box.row(align=True)
            row.scale_y = 1.3
            row.operator("caffmob.armario_v2_window_pedido", text="Montar Caixa", icon="CUBE").acao = 'MONTAR_CAIXA'
            row.operator("caffmob.armario_v2_window_apenas_laterais", text="Apenas Laterais",
                         icon="MOD_SOLIDIFY").criar = True


# Barra de ferramentas ---------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowToolbar(bpy.types.Panel):
    """Barra de ferramentas do mockup: montagem, limpeza, plano de corte e alternadores do preview."""
    bl_idname = "BTM_PT_ArmarioV2WindowToolbar"
    bl_label = "Ferramentas"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        linha = layout.row(align=True)
        linha.operator("caffmob.armario_v2_window_pedido", text="Montar Caixa", icon="CUBE").acao = 'MONTAR_CAIXA'
        linha.operator("caffmob.armario_v2_window_pedido", text="Limpar", icon="TRASH").acao = 'LIMPAR'
        linha.operator("caffmob.armario_v2_window_abrir_tudo", text="Abrir/Fechar Tudo", icon="ARROW_LEFTRIGHT")

        s = win_mod.sessao()
        vista = getattr(s, 'vista', 'SPLIT') if s is not None else 'SPLIT'
        linha = layout.row(align=True)
        for chave, rotulo in (('SPLIT', "Dividida"), ('FRONTAL', "Frontal"), ('LATERAL', "Lateral")):
            linha.operator("caffmob.armario_v2_window_vista", text=tr(rotulo),
                           depress=(vista == chave)).vista = chave

        cotas = s.mostrar_cotas if s is not None else True
        portas = s.mostrar_portas if s is not None else True
        layout.separator()
        linha = layout.row(align=True)
        linha.operator("caffmob.armario_v2_window_toggle",
                       text=tr("Cotas: {}").format("On" if cotas else "Off"),
                       icon="DRIVER_DISTANCE", depress=cotas).alvo = 'COTAS'
        linha.operator("caffmob.armario_v2_window_toggle",
                       text=tr("Portas: {}").format("On" if portas else "Off"),
                       icon="MESH_PLANE", depress=portas).alvo = 'PORTAS'
        linha.operator("caffmob.armario_v2_window_apenas_laterais", text="", icon="MOD_SOLIDIFY",
                       depress=getattr(s, 'apenas_laterais', False)).criar = False

        linha = layout.row(align=True)
        linha.operator("caffmob.armario_v2_window_pedido", text="Plano de Corte",
                       icon="MOD_ARRAY").acao = 'PLANO_CORTE'
        linha.operator("caffmob.armario_v2_window_export_json", text="Exportar JSON", icon="EXPORT")
        linha.operator("caffmob.armario_v2_window_tema", text="Tema", icon="COLOR")
        linha.operator("caffmob.armario_v2_window_painel", text="", icon="WINDOW")


# Estrutura --------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowEstrutura(_AbaPainel, bpy.types.Panel):
    """Aba Estrutura: dimensões e presença das chapas da caixa (aberta quando não há aba gravada)."""
    ABA = 'ESTRUTURA'
    bl_idname = "BTM_PT_ArmarioV2WindowEstrutura"
    bl_label = "▣ Estrutura"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario

        box = layout.box()
        box.label(text="Dimensões (mm)", icon="MESH_GRID")
        col = box.column(align=True)
        col.prop(armario, "largura")
        col.prop(armario, "altura")
        col.prop(armario, "profundidade")
        col.prop(armario, "tipo_montagem")

        box = layout.box()
        box.label(text="Chapas da caixa", icon="FILE_3D")
        col = box.column(align=True)
        col.prop(armario, "lateral_esq_ativa", text="Lateral Esquerda")
        col.prop(armario, "lateral_dir_ativa", text="Lateral Direita")
        col.prop(armario, "base_inf_ativa", text="Base Inferior")
        col.prop(armario, "base_sup_ativa", text="Base Superior")
        col.prop(armario, "fundo_ativo", text="Fundo")

        row = box.row()
        row.scale_y = 1.3
        row.operator("caffmob.armario_v2_window_pedido", text="Montar Caixa", icon="CUBE").acao = 'MONTAR_CAIXA'

        box = layout.box()
        box.label(text="Espessuras", icon="MATERIAL")
        col = box.column(align=True)
        col.prop(armario, "espessura_lateral", text="Lateral")
        col.prop(armario, "espessura_base_inferior", text="Base Inf.")
        col.prop(armario, "espessura_base_superior", text="Base Sup.")
        col.prop(armario, "espessura_fundo", text="Fundo")

        contrato = getattr(context.scene, 'btm_armario_contrato', None)
        if contrato is not None:
            box = layout.box()
            box.label(text="Contrato de chapas", icon="FILE_TEXT")
            col = box.column(align=True)
            col.prop(contrato, "comprimento_max")
            col.prop(contrato, "largura_max")


# Divisões ---------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowDivisoes(_AbaPainel, bpy.types.Panel):
    """Aba Divisões: divisórias verticais e horizontais."""
    ABA = 'DIVISOES'
    bl_idname = "BTM_PT_ArmarioV2WindowDivisoes"
    bl_label = "⊞ Divisões"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.label(text=tr("Divisórias: {}").format(len(armario.divisoes)))
        layout.prop(armario, "variante_divisoria", text="Variante")
        linha = layout.row(align=True)
        linha.operator("caffmob.armario_v2_window_pedido", text="Inserir divisória",
                       icon="MOD_ARRAY").acao = 'DIVISORIA'
        linha.operator("caffmob.armario_v2_window_pedido", text="Inserir prateleira",
                       icon="ADD").acao = 'PRATELEIRA'


# Gavetas ----------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowGavetas(_AbaPainel, bpy.types.Panel):
    """Aba Gavetas: blocos e gavetas individuais."""
    ABA = 'GAVETAS'
    bl_idname = "BTM_PT_ArmarioV2WindowGavetas"
    bl_label = "▤ Gavetas"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.label(text=tr("Gavetas: {}").format(len(armario.gavetas)))
        col = layout.column(align=True)
        col.prop(armario, "bloco_quantidade", text="Quantidade")
        col.prop(armario, "bloco_altura", text="Altura do bloco (mm)")
        col.prop(armario, "bloco_modelo", text="Modelo")
        layout.operator("caffmob.armario_v2_window_pedido", text="Criar bloco de gavetas",
                        icon="OUTLINER_OB_EMPTY").acao = 'BLOCO_GAVETAS'


# Internos ---------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowInternos(_AbaPainel, bpy.types.Panel):
    """Aba Internos: cabideiro, calceiro, sapateira, maleiro."""
    ABA = 'INTERNOS'
    bl_idname = "BTM_PT_ArmarioV2WindowInternos"
    bl_label = "◫ Internos"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.label(text=tr("Internos: {}").format(len(armario.internos)))
        col = layout.column(align=True)
        col.prop(armario, "interno_tipo", text="Tipo")
        col.prop(armario, "matriz_linhas", text="Linhas")
        col.prop(armario, "matriz_colunas", text="Colunas")
        layout.operator("caffmob.armario_v2_window_pedido", text="Inserir interno",
                        icon="OUTLINER_OB_EMPTY").acao = 'INTERNO'


# Portas -----------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowPortas(_AbaPainel, bpy.types.Panel):
    """Aba Portas: portas de abrir."""
    ABA = 'PORTAS'
    bl_idname = "BTM_PT_ArmarioV2WindowPortas"
    bl_label = "▯ Portas"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.prop(armario, "porta_ativa", text="Porta de abrir")
        layout.prop(armario, "porta_folhas", text="Folhas")
        layout.prop(armario, "porta_dobradica", text="Dobradiça")


# Deslizantes ------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowDeslizantes(_AbaPainel, bpy.types.Panel):
    """Aba Deslizantes: portas deslizantes."""
    ABA = 'DESLIZANTES'
    bl_idname = "BTM_PT_ArmarioV2WindowDeslizantes"
    bl_label = "⇆ Deslizantes"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.prop(armario, "deslizante_ativa", text="Porta deslizante")
        layout.prop(armario, "deslizante_folhas", text="Folhas")
        layout.prop(armario, "deslizante_material", text="Material")
        layout.prop(armario, "deslizante_base", text="Posição da base")
        layout.prop(armario, "deslizante_sobreposicao", text="Sobreposição (mm)")
        layout.prop(armario, "trilho_profundidade", text="Profundidade trilho (mm)")


# Fundos -----------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowFundos(_AbaPainel, bpy.types.Panel):
    """Aba Fundos: fixação e recuo do fundo."""
    ABA = 'FUNDOS'
    bl_idname = "BTM_PT_ArmarioV2WindowFundos"
    bl_label = "▧ Fundos"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        armario = raiz.btm_armario
        layout.prop(armario, "fundo_ativo", text="Fundo ativo")
        layout.prop(armario, "fundo_fixacao", text="Fixação")
        layout.prop(armario, "fundo_recuo", text="Recuo (mm)")


# Lista de peças / plano de corte ----------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowPecas(bpy.types.Panel):
    """Lista de peças do armário com as medidas de corte (o modal do mockup, em painel do Blender)."""
    bl_idname = "BTM_PT_ArmarioV2WindowPecas"
    bl_label = "▤ Lista de Peças & Plano de Corte"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return
        spec, itens = validar.pecas_da_raiz(raiz)
        if spec is None:
            return
        layout.label(text=tr("{} peça(s)").format(len(itens)))
        layout.operator("caffmob.armario_v2_window_export_json", text="Exportar cutlist JSON", icon="EXPORT")
        col = layout.column(align=True)
        for item in itens[:24]:
            (x0, _y0, z0), (x1, _y1, z1) = item['box']
            largura, altura = x1 - x0, z1 - z0
            col.label(text=tr("{}: {} × {} × {} mm").format(item['nome'], f"{largura:.0f}", f"{altura:.0f}",
                                                               f"{item.get('espessura', 0):.0f}"))
        if len(itens) > 24:
            layout.label(text=tr("… e mais {} peça(s)").format(len(itens) - 24))
        layout.operator("caffmob.armario_v2_window_pedido", text="Gerar Plano de Corte",
                        icon="MOD_ARRAY").acao = 'PLANO_CORTE'


# Rodapé -----------------------------------------------------------------------------------------------------------

class BTM_PT_ArmarioV2WindowFooter(bpy.types.Panel):
    """Rodapé: OK / Aplicar / Cancelar, com o OK bloqueado por erro geométrico."""
    bl_idname = "BTM_PT_ArmarioV2WindowFooter"
    bl_label = "Ações"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'
    bl_category = CATEGORIA
    bl_parent_id = "BTM_PT_ArmarioV2WindowHeader"

    def draw(self, context):
        layout = self.layout
        raiz = _armario(context)
        if raiz is None:
            return

        s = win_mod.sessao()
        suja = s is not None and s.suja
        bloqueado = bool(_erros(raiz))
        ajustes = len(raiz.btm_armario.ajustes)

        if ajustes:
            linha = layout.row(align=True)
            linha.label(text=tr("Ajustes manuais: {}").format(ajustes), icon="MOD_MIRROR")
            linha.operator("caffmob.armario_v2_window_limpar_ajustes", text="Limpar Ajustes",
                           icon="TRASH")

        col = layout.column(align=True)
        col.scale_y = 1.3

        row = col.row()
        row.enabled = not bloqueado
        row.operator("caffmob.armario_v2_window_aplicar", text="Aplicar", icon="FILE_TICK")

        row = col.row()
        row.scale_y = 1.3
        row.enabled = not bloqueado
        row.operator("caffmob.armario_v2_window_ok", text="OK", icon="CHECKMARK")

        row = col.row()
        if suja:
            row.alert = True
        row.operator("caffmob.armario_v2_window_cancelar", text="Cancelar", icon="CANCEL")

        if bloqueado:
            layout.label(text="Corrija os erros GEO antes de confirmar", icon="ERROR")


classes = (
    BTM_PT_ArmarioV2WindowHeader,
    BTM_PT_ArmarioV2WindowToolbar,
    BTM_PT_ArmarioV2WindowEstrutura,
    BTM_PT_ArmarioV2WindowDivisoes,
    BTM_PT_ArmarioV2WindowGavetas,
    BTM_PT_ArmarioV2WindowInternos,
    BTM_PT_ArmarioV2WindowPortas,
    BTM_PT_ArmarioV2WindowDeslizantes,
    BTM_PT_ArmarioV2WindowFundos,
    BTM_PT_ArmarioV2WindowPecas,
    BTM_PT_ArmarioV2WindowFooter,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
