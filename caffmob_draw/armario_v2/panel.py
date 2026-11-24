"""Painel do construtor de armário v2 na vista 3D (feature 017, T023; RN-01, RN-22, RN-23, D-05, D-14, RF-01, RF-02).

Um painel só, em `View3D > CAFFMob Draw`, com as sete abas num `EnumProperty` (`BTM_PG_ArmarioV2.aba`) e as sub-abas de
Divisões e Gavetas num segundo (`subaba_divisoes`/`subaba_gavetas`). Nada de janela 2D: a superfície do construtor é a
própria vista (RN-22, D-05).

- **Cabeçalho** com o tipo de montagem, o vão da peça escolhida na coleção ativa e a chapa máxima do contrato; quando a
  seleção é uma peça animável, o botão de Abrir/Fechar de `anim` aparece aqui com o rótulo da ação oposta.
- **Janela vazia** (RN-01): sem nenhuma das quatro chapas da caixa ligada, o painel mostra o estado vazio com Montar
  Caixa, que liga laterais, bases e fundo e gera (RF-01).
- **Móvel da construção antiga** (RN-23, RF-26): selecionar um móvel do construtor anterior, sem `btm_armario`, mostra
  só o aviso de que a edição exige recriar pelo motor novo. Gerar e Aplicar não aparecem, e nada no móvel é alterado.
- **Ações**: Gerar, Aplicar, Cancelar e Limpar são os operadores de `ops` (T021); Montar Caixa é o operador de montagem
  rápida. Gerar fica desabilitado enquanto o contrato de chapas não permitir (`chapas.pode_gerar`), com os motivos
  escritos abaixo do botão (RN-02).
- **Contrato de chapas** (D-11, RF-03): o contrato é semeado do Padrão de Dimensões ativo ao **abrir** o construtor
  (`ops.semear_contrato`) e pelo botão `Semear do Padrão de Dimensões`, que aparece quando ainda não há contrato. O
  desenho do painel só lê — desenhar não escreve na cena.

As listas de divisórias, gavetas e internos são as coleções gravadas no armário: o painel edita o que existe, campo a
campo, e **insere** pelas ações de D-21 (`Inserir divisória`, `Inserir prateleira`, `Inserir matriz`, `Criar bloco de
gavetas` e `Inserir interno`), que regravam a coleção e geram de novo num único passo de desfazer. Os campos de
variante, matriz e bloco ficam no armário, como as sub-abas, porque o painel só desenha: quem escreve é o operador.
"""

import bpy  # type: ignore

from ..data.i18n import tr
from . import anim
from . import build
from . import chapas as chapas_mod
from . import conferencia
from . import ops
from . import ponte
from . import resumo
from . import spec as spec_mod

CATEGORIA = "CAFFMob Draw"


# Armário da cena -------------------------------------------------------------------------------------------------
def raiz_da_selecao(context):
    """Armário v2 da seleção ativa, subindo a hierarquia; `None` quando a seleção não é de um armário v2."""
    return build.raiz_de(getattr(context, 'active_object', None))


def raiz_da_cena(context):
    """Armário v2 da seleção ativa ou, sem seleção de peça, o primeiro da coleção do construtor."""
    obj = raiz_da_selecao(context)
    if obj is not None:
        return obj
    colecao = bpy.data.collections.get(build.COLECAO)
    if colecao is None:
        return None
    for candidato in colecao.objects:
        if build.e_raiz(candidato):
            return candidato
    return None


def movel_antigo(context):
    """Móvel do construtor anterior na seleção: tem os grupos do editor 2D e não tem `btm_armario` (D-14).

    Módulo de biblioteca fica de fora: desde T026 ele é editável pelo motor novo, pela ponte de `ponte.py` (RN-21).
    """
    obj = getattr(context, 'active_object', None)
    if ponte.modulo_da_selecao(context) is not None:
        return False
    return ops.e_construcao_antiga(obj)


# Estado do armário -----------------------------------------------------------------------------------------------
def _vao_ativo(armario):
    """Vão da peça escolhida na coleção ativa; o mesmo critério da inserção (D-21)."""
    return ops.vao_ativo(armario)


def peca_da_selecao(context):
    """Peça do armário v2 na seleção ativa, ou `None`.

    O grupo `btm_armario_parte` existe em **todo** `Object`, vazio por padrão, então testar se ele está preenchido
    aceitava qualquer objeto da cena. A peça é o objeto com papel gravado e a raiz v2 acima (`build.raiz_de`), o mesmo
    critério de root do resto do pacote (T033/T034).
    """
    obj = getattr(context, 'active_object', None)
    parte = getattr(obj, 'btm_armario_parte', None) if obj is not None else None
    if parte is None or not parte.papel:
        return None
    return obj if build.raiz_de(obj) is not None else None


def _peca_escolhida(context):
    obj = peca_da_selecao(context)
    return obj.name if obj is not None else ''


def _violacoes(raiz, spec, contrato):
    """Peças que passam da chapa, para a linha de estado (RN-03, RN-16); vazio sem contrato configurado."""
    if chapas_mod.pode_gerar(contrato):
        return ()
    armario = raiz.btm_armario
    itens = build.pecas(spec, ops.divisoes_do_armario(armario), ops.gavetas_do_armario(armario),
                        ops.internos_do_armario(armario))
    pecas = [conferencia.Peca(item['papel'], item['nome'], *build.medidas_de_corte(item), item['espessura'])
             for item in itens]
    return tuple(conferencia.conferir(pecas, contrato))


def _caixa_ligada(armario):
    return any((armario.lateral_esq_ativa, armario.lateral_dir_ativa, armario.base_inf_ativa, armario.base_sup_ativa))


# Sub-abas -------------------------------------------------------------------------------------------------------
def _divisoes_da_subaba(armario, subaba):
    """Divisórias da sub-aba: Vertical e Horizontal filtram o eixo; Múltipla mostra os dois."""
    if subaba == 'VERTICAL':
        return [item for item in armario.divisoes if item.eixo == 'VERTICAL']
    if subaba == 'HORIZONTAL':
        return [item for item in armario.divisoes if item.eixo == 'HORIZONTAL']
    return list(armario.divisoes)


def _gavetas_da_subaba(armario, subaba):
    """Gavetas da sub-aba.

    O modelo da gaveta não tem coluna de tipo: interna e externa saem do próprio modelo (s/ e c/ contra-frente, como o
    mockup), a sapateira é uma gaveta qualquer e `Prat. c/ Corrediça` pede a corrediça 3D ligada.
    """
    itens = list(armario.gavetas)
    if subaba == 'INTERNAS':
        return [item for item in itens if item.modelo.startswith('s_cf_')]
    if subaba == 'EXTERNAS':
        return [item for item in itens if item.modelo.startswith('c_cf_')]
    if subaba == 'PRAT_CORREDICA':
        return [item for item in itens if item.corredica_3d]
    return itens


# Desenho ---------------------------------------------------------------------------------------------------------
def _cabecalho(layout, context, raiz, spec, contrato):
    armario = raiz.btm_armario
    violacoes = _violacoes(raiz, spec, contrato)

    # Barra de título estilo mockup (título + status de chapa + acesso rápido ao Plano de Corte)
    topo = layout.box()
    linha = topo.row(align=True)
    linha.label(text=tr("Construtor de Armários"), icon='MESH_CUBE')
    linha.operator("caffmob.opcut_generate", text=tr("Plano de Corte"), icon='MOD_ARRAY')

    # Badge de status de chapa + dimensões + montagem
    status = topo.row(align=True)
    if contrato.configurado:
        status_txt = tr("Chapa OK ({}×{})").format(f"{contrato.comprimento_max:g}", f"{contrato.largura_max:g}")
        status.label(text=tr("Fora da chapa ({})").format(len(violacoes)) if violacoes else status_txt,
                     icon='ERROR' if violacoes else 'CHECKMARK')
    else:
        status.label(text=tr("Contrato de chapas pendente"), icon='INFO')

    # Barra de ferramentas superior estilo mockup (Montar Caixa | Limpar | Abrir/Fechar)
    tb = layout.row(align=True)
    tb.operator("caffmob.armario_v2_montar_caixa", text=tr("Montar Caixa"), icon='CUBE')
    tb.operator("caffmob.armario_v2_limpar", text=tr("Limpar"), icon='TRASH')
    alvo = anim.alvo_de(context)
    if alvo is not None:
        tb.operator("caffmob.armario_v2_alternar", text=anim.rotulo(alvo),
                    icon='TRIA_DOWN' if anim.estado(alvo) else 'TRIA_RIGHT')


def _desenhar_abas(layout, armario):
    """Grade de 7 abas em 2 linhas (4 + 3) com ícones, fiel ao mockup sem truncar texto no painel estreito."""
    abas_l1 = (
        ('ESTRUTURA', "Estrutura", 'CUBE'),
        ('DIVISOES', "Divisões", 'GRID'),
        ('GAVETAS', "Gavetas", 'MOD_ARRAY'),
        ('INTERNOS', "Internos", 'MOD_BEVEL'),
    )
    abas_l2 = (
        ('PORTAS', "Portas", 'MESH_PLANE'),
        ('DESLIZANTES', "Deslizantes", 'ARROW_LEFTRIGHT'),
        ('FUNDOS', "Fundos", 'MOD_SOLIDIFY'),
    )
    for grupo in (abas_l1, abas_l2):
        row = layout.row(align=True)
        for chave, rotulo, icone in grupo:
            row.prop_enum(armario, 'aba', chave, text=tr(rotulo), icon=icone)


def _subcabecalho(layout, raiz, spec):
    armario = raiz.btm_armario
    sub = layout.box()
    r1 = sub.row(align=True)
    r1.label(text=tr("Armário: {} × {} × {} mm").format(
        f"{spec.largura:g}", f"{spec.altura:g}", f"{spec.profundidade:g}"
    ), icon='FULLSCREEN_ENTER')
    r2 = sub.row(align=True)
    r2.label(text=tr("Montagem: {}").format(tr(resumo.MONTAGENS.get(armario.tipo_montagem, armario.tipo_montagem))))
    r2.label(text=tr("Vão ativo: {}").format(_vao_ativo(armario)))


def _janela_vazia(layout, armario):
    if _caixa_ligada(armario):
        return
    caixa = layout.box()
    caixa.label(text=tr("Janela de armário vazia"), icon='INFO')
    caixa.label(text=tr("Ative as laterais, a base inferior e a base superior, ou use Montar Caixa"))


def _estrutura(layout, context, raiz):
    armario = raiz.btm_armario
    contrato = context.scene.btm_armario_contrato

    caixa = layout.box()
    caixa.label(text=tr("Contrato de chapas"), icon='MESH_PLANE')
    linha = caixa.row(align=True)
    linha.prop(contrato, 'comprimento_max')
    linha.prop(contrato, 'largura_max')
    grade = caixa.grid_flow(columns=2, even_columns=True, align=True)
    for papel in chapas_mod.PAPEIS:
        grade.prop(contrato, papel)
    if not contrato.configurado:
        caixa.operator("caffmob.armario_v2_semear_contrato", text=tr("Semear do Padrão de Dimensões"),
                       icon='IMPORT')

    caixa = layout.box()
    caixa.label(text=tr("Dimensões do armário"), icon='FULLSCREEN_ENTER')
    for campo in ('largura', 'altura', 'profundidade'):
        caixa.prop(armario, campo)

    caixa = layout.box()
    caixa.label(text=tr("Montagem e orientações"), icon='MOD_BUILD')
    caixa.prop(armario, 'tipo_montagem')
    linha = caixa.row(align=True)
    linha.prop(armario, 'orientacao_frente')
    linha.prop(armario, 'orientacao_tras')

    caixa = layout.box()
    caixa.label(text=tr("Travessas"), icon='MOD_LENGTHWISE')
    linha = caixa.row(align=True)
    linha.prop(armario, 'contra_frente_ativa', text=tr("Contra-frente"))
    linha.prop(armario, 'peca_tras_ativa', text=tr("Peça de trás"))

    caixa = layout.box()
    caixa.label(text=tr("Espessuras do armário"), icon='MOD_SOLIDIFY')
    grade = caixa.grid_flow(columns=2, even_columns=True, align=True)
    for campo in spec_mod.THICKNESS_FIELDS:
        grade.prop(armario, campo)
    caixa.prop(armario, 'bloquear_chapa', text=tr("Bloquear peça fora da chapa"))

    caixa = layout.box()
    caixa.label(text=tr("Caixa do armário"), icon='CUBE')
    linha = caixa.row(align=True)
    linha.prop(armario, 'lateral_esq_ativa')
    linha.prop(armario, 'lateral_dir_ativa')
    linha = caixa.row(align=True)
    linha.prop(armario, 'base_inf_ativa')
    linha.prop(armario, 'base_sup_ativa')
    caixa.prop(armario, 'acabamento')


def _divisoes(layout, _context, raiz):
    armario = raiz.btm_armario
    layout.prop(armario, 'subaba_divisoes', expand=True)
    if armario.subaba_divisoes in ('VERTICAL', 'MULTIPLA'):
        layout.prop(armario, 'variante_divisoria')
        layout.operator("caffmob.armario_v2_inserir_divisoria", text=tr("Inserir divisória"), icon='ADD')
    if armario.subaba_divisoes in ('HORIZONTAL', 'MULTIPLA'):
        layout.prop(armario, 'variante_prateleira')
        layout.operator("caffmob.armario_v2_inserir_prateleira", text=tr("Inserir prateleira"), icon='ADD')
    if armario.subaba_divisoes == 'MULTIPLA':
        caixa = layout.box()
        caixa.label(text=tr("Inserção múltipla"), icon='GRID')
        linha = caixa.row(align=True)
        linha.prop(armario, 'matriz_linhas')
        linha.prop(armario, 'matriz_colunas')
        caixa.prop(armario, 'matriz_prioridade', expand=True)
        caixa.operator("caffmob.armario_v2_inserir_matriz", text=tr("Inserir matriz"), icon='ADD')
    itens = _divisoes_da_subaba(armario, armario.subaba_divisoes)
    if not itens:
        layout.label(text=tr("Sem divisórias neste vão"), icon='INFO')
        return
    for item in itens:
        caixa = layout.box()
        linha = caixa.row(align=True)
        linha.prop(item, 'vao')
        linha.prop(item, 'posicao')
        linha = caixa.row(align=True)
        linha.prop(item, 'tipo')
        linha.prop(item, 'espessura')


def _gavetas(layout, _context, raiz):
    armario = raiz.btm_armario
    layout.prop(armario, 'subaba_gavetas', expand=True)
    caixa = layout.box()
    caixa.label(text=tr("Bloco de gavetas"), icon='MOD_BEVEL')
    linha = caixa.row(align=True)
    linha.prop(armario, 'bloco_quantidade')
    linha.prop(armario, 'bloco_altura')
    caixa.prop(armario, 'bloco_modelo')
    caixa.operator("caffmob.armario_v2_criar_bloco_gavetas", text=tr("Criar bloco de gavetas"), icon='ADD')
    itens = _gavetas_da_subaba(armario, armario.subaba_gavetas)
    if not itens:
        layout.label(text=tr("Sem gavetas nesta sub-aba"), icon='INFO')
        return
    for item in itens:
        caixa = layout.box()
        linha = caixa.row(align=True)
        linha.prop(item, 'vao')
        linha.prop(item, 'altura')
        caixa.prop(item, 'modelo')
        caixa.prop(item, 'corredica_3d')
        linha = caixa.row(align=True)
        linha.prop(item, 'separador_colunas')
        linha.prop(item, 'separador_linhas')
        linha = caixa.row(align=True)
        linha.prop(item, 'afastador_frente')
        linha.prop(item, 'afastador_tras')
        linha = caixa.row(align=True)
        linha.prop(item, 'afastador_esq')
        linha.prop(item, 'afastador_dir')


def _internos(layout, _context, raiz):
    armario = raiz.btm_armario
    caixa = layout.box()
    caixa.label(text=tr("Interno a inserir"), icon='MOD_BEVEL')
    caixa.prop(armario, 'interno_tipo', expand=True)
    caixa.operator("caffmob.armario_v2_inserir_interno", text=tr("Inserir interno"), icon='ADD')
    if not len(armario.internos):
        layout.label(text=tr("Sem internos neste vão"), icon='INFO')
        return
    for item in armario.internos:
        caixa = layout.box()
        linha = caixa.row(align=True)
        linha.prop(item, 'vao')
        linha.prop(item, 'altura')
        caixa.prop(item, 'tipo')


def _portas(layout, _context, raiz):
    armario = raiz.btm_armario
    caixa = layout.box()
    caixa.prop(armario, 'porta_ativa')
    if armario.porta_ativa:
        caixa.prop(armario, 'porta_folhas')
        caixa.prop(armario, 'porta_dobradica')


def _deslizantes(layout, _context, raiz):
    armario = raiz.btm_armario
    caixa = layout.box()
    caixa.prop(armario, 'deslizante_ativa')
    if armario.deslizante_ativa:
        caixa.prop(armario, 'deslizante_folhas')
        caixa.prop(armario, 'deslizante_sobreposicao')
        caixa.prop(armario, 'deslizante_material')
        caixa.prop(armario, 'deslizante_base')
        caixa.prop(armario, 'trilho_profundidade')


def _fundos(layout, _context, raiz):
    armario = raiz.btm_armario
    caixa = layout.box()
    caixa.prop(armario, 'fundo_ativo')
    if armario.fundo_ativo:
        caixa.prop(armario, 'fundo_fixacao')
        caixa.prop(armario, 'fundo_recuo')


ABAS = {'ESTRUTURA': _estrutura, 'DIVISOES': _divisoes, 'GAVETAS': _gavetas, 'INTERNOS': _internos,
        'PORTAS': _portas, 'DESLIZANTES': _deslizantes, 'FUNDOS': _fundos}


def _estado(layout, context, raiz, spec, contrato):
    violacoes = _violacoes(raiz, spec, contrato)
    escolhida = _peca_escolhida(context)
    caixa = layout.box()
    caixa.label(text=tr("Peça escolhida: {}").format(escolhida) if escolhida else tr("Nenhuma peça escolhida"),
                icon='RESTRICT_SELECT_OFF')
    caixa.label(text=resumo.linha_estado(spec, vao=_vao_ativo(raiz.btm_armario), peca=escolhida,
                                        violacoes=violacoes),
                icon='ERROR' if violacoes else 'CHECKMARK')


def _acoes(layout, context, raiz):
    linha = layout.row(align=True)
    linha.operator("caffmob.armario_v2_montar_caixa", text=tr("Montar Caixa"), icon='CUBE')
    linha.operator("caffmob.armario_v2_limpar", text=tr("Limpar"), icon='TRASH')

    contrato = ops.contrato_da_cena(context.scene)
    motivos = chapas_mod.pode_gerar(contrato)
    coluna = layout.column()
    coluna.scale_y = 1.4
    coluna.enabled = not motivos
    coluna.operator("caffmob.armario_v2_gerar", text=tr("Gerar"), icon='FILE_REFRESH')

    linha = layout.row(align=True)
    linha.operator("caffmob.armario_v2_aplicar", text=tr("Aplicar"), icon='CHECKMARK')
    linha.operator("caffmob.armario_v2_cancelar", text=tr("Cancelar"), icon='CANCEL')
    if raiz.btm_armario.origem:
        layout.operator("caffmob.armario_v2_recriar_do_modulo", text=tr("Recriar do módulo"), icon='LOOP_BACK')
    if motivos:
        for motivo in motivos:
            layout.label(text=motivo, icon='ERROR')


def draw_painel(layout, context):
    """Corpo do painel, separado da classe para a fumaça poder desenhar com um layout falso.

    A seleção vence o recuo para a coleção: com um módulo de biblioteca escolhido, a aba do módulo aparece mesmo que
    haja outro armário v2 na cena (RN-21, D-13).
    """
    raiz = raiz_da_selecao(context)
    modulo = ponte.modulo_da_selecao(context)
    if raiz is None and modulo is not None:
        ponte.desenhar_modulo(layout, context, modulo)
        return
    raiz = raiz_da_cena(context)
    if movel_antigo(context) and raiz is None:
        caixa = layout.box()
        caixa.label(text=tr("Este móvel é da construção antiga: recrie pelo construtor novo para editar"),
                    icon='ERROR')
        return
    if raiz is None:
        return
    armario = raiz.btm_armario
    spec = ops.spec_do_armario(raiz)
    contrato = ops.contrato_da_cena(context.scene)
    _cabecalho(layout, context, raiz, spec, contrato)
    _janela_vazia(layout, armario)
    _desenhar_abas(layout, armario)
    _subcabecalho(layout, raiz, spec)
    ABAS.get(armario.aba, _estrutura)(layout, context, raiz)
    layout.separator()
    _estado(layout, context, raiz, spec, contrato)
    _acoes(layout, context, raiz)


class BTM_PT_ArmarioV2(bpy.types.Panel):
    """Construtor do armário v2: sete abas, estado da montagem e os comandos do armário"""

    bl_label = "Construtor de Armário v2"
    bl_idname = "BTM_PT_armario_v2"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = CATEGORIA

    @classmethod
    def poll(cls, context):
        return (ponte.modulo_da_selecao(context) is not None or raiz_da_cena(context) is not None
                or movel_antigo(context))

    def draw(self, context):
        draw_painel(self.layout, context)


classes = (BTM_PT_ArmarioV2,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
