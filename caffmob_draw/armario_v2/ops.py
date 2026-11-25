"""Operadores do construtor de armário v2 (feature 017, T021; RN-18, RF-01, RF-22, D-03).

- `caffmob.cabinet_editor` abre o construtor: confirma que a seleção é a raiz do armário e grava o instantâneo do estado
  atual, que é o ponto de retorno do Cancelar. Sem raiz na cena, cria o armário vazio (RF-01); num móvel da construção
  antiga não cria nada e avisa que a edição exige recriar (RN-23). Sem `UNDO`: abrir o painel não cria passo de desfazer
  (RN-18).
- `caffmob.armario_v2_montar_caixa` é a montagem rápida da janela vazia: liga laterais, bases e fundo e gera (RF-01).
- `caffmob.armario_v2_gerar` lê o spec e as coleções gravadas no armário, confere o contrato de chapas e as medidas e
  chama `build.gerar`. Recusa sem contrato (RN-02) e, com o bloqueio de chapa ligado, recusa a peça que passa da chapa
  (RN-03, RN-16).
- `caffmob.armario_v2_aplicar` grava um passo de desfazer e fixa o estado atual como novo ponto de retorno, sem fechar.
- `caffmob.armario_v2_cancelar` devolve o armário ao instantâneo da abertura e refaz as peças a partir dele (ou apaga as
  peças, se a abertura ainda não tinha gerado nada).
- `caffmob.armario_v2_limpar` apaga as peças geradas e deixa o armário em pé para novo Gerar.

O `bl_idname` `caffmob.cabinet_editor` é o mesmo do editor 2D de propósito (D-03): quando este módulo entrar na cascata
de registro (T030), o editor antigo já terá saído de `cabinet_editor._modules()` (T027), então não há dois operadores com
o mesmo nome. Enquanto T027 não roda, `_MODULES` não carrega este módulo.

O que vai para o Blender é sempre derivado do que está gravado no armário: as coleções de divisórias, gavetas e internos
são lidas de `btm_armario` a cada Gerar, e não guardadas em memória, para o resultado ser o mesmo depois de salvar e
reabrir o arquivo.
"""

import json
from dataclasses import replace

import bpy  # type: ignore

from ..data import dimension_schema as schema
from ..data.i18n import tr
from ..standards import api
from . import build
from . import chapas as chapas_mod
from . import conferencia
from . import gavetas as gavetas_mod
from . import internos as internos_mod
from . import spec as spec_mod
from . import vaos as vaos_mod

CAMPOS_DIVISAO = ('uid', 'eixo', 'vao', 'posicao', 'tipo', 'espessura')
ESPESSURAS = ('6', '15', '18', '25')

# Componente do Padrão de Dimensões de cada papel do contrato de chapas (D-11, RN-02).
COMPONENTES_CONTRATO = {
    'espessura_lateral': 'LAT',
    'espessura_base_inferior': 'BAS',
    'espessura_base_superior': 'BAS',
    'espessura_divisoria': 'DIV',
    'espessura_prateleira': 'PRAT',
    'espessura_fundo': 'FUN_INF',
    'espessura_gaveta': 'FRE_GAV_INT',
    'espessura_porta': 'POR',
}
MONTAGEM_DA_API = {'LATERAL': 'LATERAL_PASSANTE', 'BASE': 'BASE_PASSANTE'}
CAMPOS_GAVETA = ('uid', 'vao', 'indice', 'altura', 'modelo', 'separador_colunas', 'separador_linhas',
                 'afastador_frente', 'afastador_tras', 'afastador_esq', 'afastador_dir', 'corredica_3d')
CAMPOS_INTERNO = ('uid', 'vao', 'tipo', 'altura')
CAMPOS_AJUSTE = ('uid', 'nome', 'papel', 'dx', 'dy', 'dz', 'espelho_x', 'removida')


# Spec e coleções -------------------------------------------------------------------------------------------------
def _dados(root):
    """Medidas e enums do armário como dicionário; as espessuras saem dos enums em mm (float)."""
    armario = root.btm_armario
    dados = {}
    for campo in spec_mod.Spec.__dataclass_fields__:
        if not hasattr(armario, campo):
            continue
        valor = getattr(armario, campo)
        dados[campo] = float(valor) if campo in spec_mod.THICKNESS_FIELDS else valor
    return dados


def spec_de_dados(dados):
    """Spec a partir do dicionário de medidas do armário (ou de um instantâneo), em milímetros."""
    campos = {}
    for campo in spec_mod.Spec.__dataclass_fields__:
        if campo not in dados:
            continue
        valor = dados[campo]
        campos[campo] = float(valor) if campo in spec_mod.THICKNESS_FIELDS else valor
    return spec_mod.Spec(**campos)


def spec_do_armario(root):
    return spec_de_dados(_dados(root))


def _itens(colecao, campos):
    return [{campo: getattr(item, campo) for campo in campos} for item in colecao]


def divisoes_do_armario(armario):
    """`vaos.Divisao` de cada divisória gravada no armário.

    Os recuos ficam em zero: o modelo de dados (§2.1) grava eixo, vão, posição, tipo e espessura, sem os recuos do
    mockup. Quando o Painel (T023) editar a divisória, o recuo volta a ser proposto pela variante escolhida.
    """
    return [vaos_mod.Divisao(uid=item['uid'], eixo=item['eixo'], vao=item['vao'], posicao=item['posicao'],
                             tipo=item['tipo'], espessura=float(item['espessura']))
            for item in _itens(armario.divisoes, CAMPOS_DIVISAO)]


def gavetas_do_armario(armario):
    """`gavetas.Gaveta` de cada gaveta gravada, com o separador, os afastadores e a corrediça 3D."""
    return [gavetas_mod.Gaveta(**item) for item in _itens(armario.gavetas, CAMPOS_GAVETA)]


def internos_do_armario(armario):
    """`internos.Interno` de cada interno gravado, com o vão e a altura."""
    return [internos_mod.Interno(**item) for item in _itens(armario.internos, CAMPOS_INTERNO)]


def contrato_da_cena(scene):
    """Contrato de chapas da cena; sem o PropertyGroup, um contrato vazio — e o Gerar recusa."""
    dados = getattr(scene, 'btm_armario_contrato', None)
    if dados is None:
        return chapas_mod.contrato_vazio()
    return chapas_mod.Contrato(
        comprimento_max=dados.comprimento_max,
        largura_max=dados.largura_max,
        espessuras={papel: float(getattr(dados, papel)) for papel in chapas_mod.PAPEIS},
        montagem_padrao=dados.montagem_padrao,
        orientacao_frente_padrao=dados.orientacao_frente_padrao,
        orientacao_tras_padrao=dados.orientacao_tras_padrao,
        configurado=dados.configurado)


# Contrato de chapas ----------------------------------------------------------------------------------------------
def _espessura_do_enum(valor):
    """Espessura do Padrão de Dimensões encaixada num item do enum (6, 15, 18 ou 25 mm)."""
    return min(ESPESSURAS, key=lambda item: abs(float(item) - float(valor)))


def semear_contrato(scene, forcar=False):
    """Semeia `Scene.btm_armario_contrato` do Padrão de Dimensões ativo (D-11, RF-03).

    `True` quando escreveu. Roda na abertura do construtor e no botão do painel, nunca no desenho: o contrato é dado
    do arquivo e desenhar painel não pode alterar a cena. Sem definição ativa, os valores são os padrões do esquema BR,
    o mesmo fallback do corte.
    """
    dados = getattr(scene, 'btm_armario_contrato', None)
    if dados is None or (dados.configurado and not forcar):
        return False
    valores = {papel: float(api.get_value(scene, schema.sheet_key('COZ', componente, 'thickness')))
               for papel, componente in COMPONENTES_CONTRATO.items()}
    # O Padrão guarda a chapa em `GLOBAL.max.sheet_*`, com os eixos trocados em relação ao contrato
    # (`sheet_width_max` é o lado maior do fornecedor): o contrato recebe maior com maior.
    limites = sorted((float(api.get_value(scene, schema.max_key('sheet_length_max'))),
                      float(api.get_value(scene, schema.max_key('sheet_width_max')))))
    contrato = chapas_mod.apply_host_contract(limites[1], limites[0], valores)
    dados.comprimento_max = contrato.comprimento_max
    dados.largura_max = contrato.largura_max
    for papel in chapas_mod.PAPEIS:
        setattr(dados, papel, _espessura_do_enum(contrato.espessuras[papel]))
    dados.montagem_padrao = MONTAGEM_DA_API.get(api.active_assembly(scene), 'LATERAL_PASSANTE')
    dados.configurado = True
    return True


# Coleções gravadas ------------------------------------------------------------------------------------------------
def vao_ativo(armario):
    """Vão da peça escolhida na coleção ativa; sem escolha, o vão raiz (D-21).

    O `data-delta` §2 não tem campo de vão ativo: a escolha é o `active_index` das três coleções, lido na ordem em
    que o painel as desenha. A inserção usa o mesmo critério do cabeçalho, para a peça nascer onde o vão anunciado diz.
    """
    for colecao in (armario.divisoes, armario.gavetas, armario.internos):
        indice = getattr(colecao, 'active_index', -1)
        if 0 <= indice < len(colecao):
            return colecao[indice].vao or vaos_mod.RAIZ
    return vaos_mod.RAIZ


def _regiao_do_vao(root, armario, vao):
    """(largura, altura) livres do vão, pela árvore das divisórias gravadas."""
    regioes = vaos_mod.regioes(divisoes_do_armario(armario), spec_do_armario(root))
    if vao not in regioes:
        raise ValueError(tr("Vão desconhecido: {}").format(vao))
    _x, _z, largura, altura = regioes[vao]
    return largura, altura


def gravar_divisoes(armario, divisoes):
    """Regrava a coleção de divisórias a partir das `vaos.Divisao` (Duplicar e Excluir do menu).

    A espessura volta como texto do enum ("15"), não como float: o item do `EnumProperty` é textual.
    """
    _repovoar(armario.divisoes, [
        {'uid': divisao.uid, 'eixo': divisao.eixo, 'vao': divisao.vao, 'posicao': divisao.posicao,
         'tipo': divisao.tipo, 'espessura': str(int(round(divisao.espessura)))} for divisao in divisoes])


def gravar_gavetas(armario, lista_gavetas):
    """Regrava a coleção de gavetas a partir das `gavetas.Gaveta` (bloco novo, D-21)."""
    _repovoar(armario.gavetas, [
        {'uid': gaveta.uid, 'vao': gaveta.vao, 'indice': gaveta.indice, 'altura': gaveta.altura,
         'modelo': gaveta.modelo, 'separador_colunas': gaveta.separador_colunas,
         'separador_linhas': gaveta.separador_linhas, 'afastador_frente': gaveta.afastador_frente,
         'afastador_tras': gaveta.afastador_tras, 'afastador_esq': gaveta.afastador_esq,
         'afastador_dir': gaveta.afastador_dir, 'corredica_3d': gaveta.corredica_3d}
        for gaveta in lista_gavetas])


def gravar_internos(armario, lista_internos):
    """Regrava a coleção de internos a partir dos `internos.Interno` (inserção do painel, D-21)."""
    _repovoar(armario.internos, [
        {'uid': interno.uid, 'vao': interno.vao, 'tipo': interno.tipo, 'altura': interno.altura}
        for interno in lista_internos])


# Instantâneo (o ponto de retorno do Cancelar) ---------------------------------------------------------------------
def snapshot_de(root):
    """JSON do estado do armário — spec, coleções, se gerou e se o construtor está aberto."""
    armario = root.btm_armario
    estado = {
        'spec': _dados(root),
        'gerado': bool(armario.gerado),
        'aberto': bool(armario.aberto),
        'divisoes': _itens(armario.divisoes, CAMPOS_DIVISAO),
        'gavetas': _itens(armario.gavetas, CAMPOS_GAVETA),
        'internos': _itens(armario.internos, CAMPOS_INTERNO),
        'ajustes': _itens(armario.ajustes, CAMPOS_AJUSTE),
    }
    return json.dumps(estado, sort_keys=True)


def _preencher(alvo, dados):
    for campo, valor in dados.items():
        if hasattr(alvo, campo):
            setattr(alvo, campo, valor)


def _repovoar(colecao, itens):
    while len(colecao):
        colecao.remove(0)
    for item in itens or ():
        if isinstance(item, dict):
            _preencher(colecao.add(), item)


def aplicar_snapshot(root, texto):
    """Devolve o armário ao estado do instantâneo; levanta `ValueError` se o texto não servir."""
    try:
        estado = json.loads(texto)
    except (TypeError, ValueError) as erro:
        raise ValueError(tr("Instantâneo inválido: {}").format(erro)) from erro
    if not isinstance(estado, dict) or not isinstance(estado.get('spec'), dict):
        raise ValueError(tr("Instantâneo inválido: falta o spec do armário"))
    armario = root.btm_armario
    for campo, valor in estado['spec'].items():
        if not hasattr(armario, campo):
            continue
        # Os enums de espessura guardam texto: 15.0 volta como "15" (o item do enum), não como "15.0".
        setattr(armario, campo, str(int(valor)) if campo in spec_mod.THICKNESS_FIELDS else valor)
    _repovoar(armario.divisoes, estado.get('divisoes'))
    _repovoar(armario.gavetas, estado.get('gavetas'))
    _repovoar(armario.internos, estado.get('internos'))
    if 'ajustes' in estado:                       # instantâneos antigos não têm ajustes: não mexe nos atuais
        _repovoar(armario.ajustes, estado.get('ajustes'))
    armario.gerado = bool(estado.get('gerado'))
    armario.aberto = bool(estado.get('aberto', False))
    return estado


# Geração -----------------------------------------------------------------------------------------------------------
def _raiz(context):
    """Raiz do armário a partir da seleção: o próprio objeto ativo ou um pai dele."""
    return build.raiz_de(getattr(context, 'active_object', None))


def e_raiz(obj):
    """O objeto é a raiz vazia do armário v2 (o critério de `build.e_raiz`)."""
    return build.e_raiz(obj)


def e_construcao_antiga(obj):
    """Móvel do construtor anterior: módulo de biblioteca/`btm` sem armário v2 na hierarquia (RN-23).

    Não dá para testar `btm_cabinet`/`btm_structure`: os grupos existem em todo `Object`, com valores padrão. O que
    identifica o móvel é a marca de módulo, a mesma que `cutting.part_sources.iter_modules` usa.
    """
    if build.raiz_de(obj) is not None:
        return False
    while obj is not None:
        if _e_modulo(obj):
            return True
        obj = obj.parent
    return False


def _e_modulo(obj):
    if obj.get('caffmob_modulo') or obj.get('IS_FRAMELESS_CABINET_CAGE') or obj.get('IS_CLOSET_STARTER_CAGE'):
        return True
    plano = getattr(obj, 'btm_plane', None)
    return plano is not None and getattr(plano, 'object_kind', '') == 'MODULE'


def gerar_armario(root, context):
    """Confere o contrato e as medidas e refaz as chapas; devolve (gerou, avisos)."""
    spec = spec_do_armario(root)
    contrato = contrato_da_cena(context.scene)
    motivos = chapas_mod.pode_gerar(contrato)
    if motivos:
        return False, tuple(motivos)
    problemas = spec_mod.validate(spec)
    if problemas:
        return False, tuple(problemas)
    armario = root.btm_armario
    divisoes = divisoes_do_armario(armario)
    lista_gavetas = gavetas_do_armario(armario)
    lista_internos = internos_do_armario(armario)
    lista = [conferencia.Peca(item['papel'], item['nome'], *build.medidas_de_corte(item), item['espessura'])
             for item in build.pecas(spec, divisoes, lista_gavetas, lista_internos)]
    decisao = conferencia.decidir(lista, contrato, spec.bloquear_chapa)
    if not decisao.gera:
        return False, tuple(decisao.avisos)
    build.gerar(root, spec, divisoes, lista_gavetas, lista_internos)
    return True, tuple(decisao.avisos)


class _ArmarioOperator:
    """Base dos operadores do armário: exigem a raiz do armário na seleção."""

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if _raiz(context) is None:
            cls.poll_message_set(tr("Selecione o armário v2"))
            return False
        return True

    def _avisar(self, avisos):
        for aviso in avisos:
            self.report({'WARNING'}, aviso)


class BTM_OT_ArmarioV2Abrir(_ArmarioOperator, bpy.types.Operator):
    """Abre o construtor do armário e guarda o estado atual para o Cancelar"""
    bl_idname = "caffmob.cabinet_editor"
    bl_label = "Abrir armário v2"
    bl_options = {'REGISTER'}          # abrir não cria passo de desfazer (RN-18)

    @classmethod
    def poll(cls, context):
        """Abrir serve também para começar: sem armário v2 ele cria a raiz (RF-01).

        A herança de `_ArmarioOperator` exigiria a raiz na seleção e o construtor nunca abriria num projeto limpo
        (provado na fumaça de T033); o móvel da construção antiga continua recusado, agora com o motivo no `poll`.
        """
        if _raiz(context) is not None:
            return True
        if e_construcao_antiga(getattr(context, 'active_object', None)):
            cls.poll_message_set(tr("Este móvel é da construção antiga: recrie pelo construtor novo para editar"))
            return False
        return True

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            if e_construcao_antiga(getattr(context, 'active_object', None)):
                self.report({'WARNING'},
                            tr("Este móvel é da construção antiga: recrie pelo construtor novo para editar"))
                return {'CANCELLED'}
            # Construtor vazio (RF-01): sem armário v2 na cena, abrir cria a raiz e deixa a janela vazia.
            root = build.criar_raiz(context.scene)
            if getattr(context, 'view_layer', None) is not None:
                context.view_layer.objects.active = root
            root.select_set(True)
        semear_contrato(context.scene)
        armario = root.btm_armario
        armario.snapshot = snapshot_de(root)
        armario.aberto = False
        return {'FINISHED'}


class BTM_OT_ArmarioV2Gerar(_ArmarioOperator, bpy.types.Operator):
    """Gera as chapas do armário a partir do spec, das divisórias, das gavetas e dos internos"""
    bl_idname = "caffmob.armario_v2_gerar"
    bl_label = "Gerar armário"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        gerou, avisos = gerar_armario(root, context)
        self._avisar(avisos)
        if not gerou:
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_ArmarioV2Aplicar(_ArmarioOperator, bpy.types.Operator):
    """Grava um passo de desfazer e fixa o estado atual como ponto de retorno, sem fechar"""
    bl_idname = "caffmob.armario_v2_aplicar"
    bl_label = "Aplicar"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        bpy.ops.ed.undo_push(message=tr("Armário: Aplicar"))
        root.btm_armario.snapshot = snapshot_de(root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2Cancelar(_ArmarioOperator, bpy.types.Operator):
    """Devolve o armário ao estado da abertura e apaga as peças geradas"""
    bl_idname = "caffmob.armario_v2_cancelar"
    bl_label = "Cancelar"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        if not armario.snapshot:
            self.report({'WARNING'}, tr("Sem estado guardado: nada para cancelar"))
            return {'CANCELLED'}
        try:
            aplicar_snapshot(root, armario.snapshot)
        except ValueError as erro:
            self.report({'WARNING'}, str(erro))
            return {'CANCELLED'}
        if armario.gerado:
            gerou, avisos = gerar_armario(root, context)
            self._avisar(avisos)
            if not gerou:
                return {'CANCELLED'}
        else:
            build.limpar(root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2SemearContrato(bpy.types.Operator):
    """Semeia o contrato de chapas do Padrão de Dimensões ativo"""

    bl_idname = "caffmob.armario_v2_semear_contrato"
    bl_label = "Semear do Padrão de Dimensões"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not semear_contrato(context.scene, forcar=True):
            self.report({'WARNING'}, tr("Sem contrato de chapas na cena"))
            return {'CANCELLED'}
        return {'FINISHED'}


class BTM_OT_ArmarioV2MontarCaixa(_ArmarioOperator, bpy.types.Operator):
    """Liga laterais, base inferior, base superior e fundo e gera o armário"""

    bl_idname = "caffmob.armario_v2_montar_caixa"
    bl_label = "Montar Caixa"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        armario.lateral_esq_ativa = True
        armario.lateral_dir_ativa = True
        armario.base_inf_ativa = True
        armario.base_sup_ativa = True
        armario.fundo_ativo = True
        gerou, avisos = gerar_armario(root, context)
        self._avisar(avisos)
        if not gerou:
            return {'CANCELLED'}
        return {'FINISHED'}


class _InserirOperator(_ArmarioOperator):
    """Base das inserções do painel (D-21): escreve a coleção e gera de novo só quando o armário já existe."""

    def _regerar(self, context, root):
        if not root.btm_armario.gerado:
            return
        _gerou, avisos = gerar_armario(root, context)
        self._avisar(avisos)

    def _gravar(self, montar):
        """Executa a operação do núcleo e devolve `(resultado, None)` ou `(None, erro)`."""
        try:
            return montar(), None
        except ValueError as erro:
            self.report({'WARNING'}, str(erro))
            return None, erro


class BTM_OT_ArmarioV2InserirDivisoria(_InserirOperator, bpy.types.Operator):
    """Insere uma divisória vertical no vão ativo, com a variante gravada no armário"""
    bl_idname = "caffmob.armario_v2_inserir_divisoria"
    bl_label = "Inserir divisória"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        vao = vao_ativo(armario)
        resultado, erro = self._gravar(lambda: vaos_mod.inserir_vertical(
            divisoes_do_armario(armario), spec_do_armario(root), vao, armario.variante_divisoria))
        if erro is not None:
            return {'CANCELLED'}
        gravar_divisoes(armario, resultado[0])
        self._regerar(context, root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2InserirPrateleira(_InserirOperator, bpy.types.Operator):
    """Insere uma prateleira horizontal no vão ativo, com a variante gravada no armário"""
    bl_idname = "caffmob.armario_v2_inserir_prateleira"
    bl_label = "Inserir prateleira"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        vao = vao_ativo(armario)
        resultado, erro = self._gravar(lambda: vaos_mod.inserir_horizontal(
            divisoes_do_armario(armario), spec_do_armario(root), vao, armario.variante_prateleira))
        if erro is not None:
            return {'CANCELLED'}
        gravar_divisoes(armario, resultado[0])
        self._regerar(context, root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2InserirMatriz(_InserirOperator, bpy.types.Operator):
    """Insere a matriz de divisórias e prateleiras no vão ativo"""
    bl_idname = "caffmob.armario_v2_inserir_matriz"
    bl_label = "Inserir matriz"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        vao = vao_ativo(armario)
        prioridade = vaos_mod.HORIZONTAL if armario.matriz_prioridade == 'HORIZONTAL' else vaos_mod.VERTICAL
        resultado, erro = self._gravar(lambda: vaos_mod.matriz(
            divisoes_do_armario(armario), spec_do_armario(root), vao,
            armario.matriz_linhas, armario.matriz_colunas, prioridade))
        if erro is not None:
            return {'CANCELLED'}
        gravar_divisoes(armario, resultado)
        self._regerar(context, root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2CriarBlocoGavetas(_InserirOperator, bpy.types.Operator):
    """Cria o bloco de gavetas no vão ativo, com quantidade, altura e modelo gravados no armário"""
    bl_idname = "caffmob.armario_v2_criar_bloco_gavetas"
    bl_label = "Criar bloco de gavetas"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        vao = vao_ativo(armario)

        def montar():
            _largura, altura_vao = _regiao_do_vao(root, armario, vao)
            if armario.bloco_altura > altura_vao + 1e-9:
                raise ValueError(tr("Bloco de {} mm não cabe no vão de {} mm").format(
                    f"{armario.bloco_altura:g}", f"{altura_vao:g}"))
            lista = gavetas_do_armario(armario)
            novas = gavetas_mod.bloco(armario.bloco_altura, armario.bloco_quantidade,
                                      modelo=armario.bloco_modelo, vao=vao)
            base = len([item for item in lista if item.vao == vao])
            novas = [replace(item, indice=item.indice + base) for item in novas]
            return lista + novas

        resultado, erro = self._gravar(montar)
        if erro is not None:
            return {'CANCELLED'}
        gravar_gavetas(armario, resultado)
        self._regerar(context, root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2InserirInterno(_InserirOperator, bpy.types.Operator):
    """Insere o interno do tipo gravado no armário, no vão ativo"""
    bl_idname = "caffmob.armario_v2_inserir_interno"
    bl_label = "Inserir interno"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        armario = root.btm_armario
        vao = vao_ativo(armario)
        spec = spec_do_armario(root)

        def montar():
            _largura, altura_vao = _regiao_do_vao(root, armario, vao)
            return internos_mod.inserir(internos_do_armario(armario), vao, armario.interno_tipo,
                                        altura_vao, spec.espessura_prateleira)[0]

        resultado, erro = self._gravar(montar)
        if erro is not None:
            return {'CANCELLED'}
        gravar_internos(armario, resultado)
        self._regerar(context, root)
        return {'FINISHED'}


class BTM_OT_ArmarioV2Limpar(_ArmarioOperator, bpy.types.Operator):
    """Apaga as chapas geradas do armário, sem tocar no resto da cena"""
    bl_idname = "caffmob.armario_v2_limpar"
    bl_label = "Limpar armário"

    def execute(self, context):
        root = _raiz(context)
        if root is None:
            return {'CANCELLED'}
        build.limpar(root)
        root.btm_armario.gerado = False
        return {'FINISHED'}


classes = (BTM_OT_ArmarioV2Abrir, BTM_OT_ArmarioV2Gerar, BTM_OT_ArmarioV2Aplicar, BTM_OT_ArmarioV2Cancelar,
           BTM_OT_ArmarioV2MontarCaixa, BTM_OT_ArmarioV2SemearContrato, BTM_OT_ArmarioV2Limpar,
           BTM_OT_ArmarioV2InserirDivisoria, BTM_OT_ArmarioV2InserirPrateleira, BTM_OT_ArmarioV2InserirMatriz,
           BTM_OT_ArmarioV2CriarBlocoGavetas, BTM_OT_ArmarioV2InserirInterno)


def _outro_no_idname(idname):
    """Classe de operador registrada que responde por `idname`, ou `None`.

    `hasattr(bpy.ops.caffmob, 'cabinet_editor')` não serve: o atributo existe mesmo sem operador registrado, e a guarda
    nunca deixava o `Abrir` entrar (provado na fumaça de T033). O registro de verdade está nas classes de `bpy.types`.
    """
    for nome in dir(bpy.types):
        classe = getattr(bpy.types, nome, None)
        if isinstance(classe, type) and issubclass(classe, bpy.types.Operator) \
                and getattr(classe, 'bl_idname', '') == idname:
            return classe
    return None


def _dividido(cls):
    """O editor 2D antigo ainda ocupa `caffmob.cabinet_editor`: a classe do armário espera a vez (D-03).

    `Abrir` reusa o `bl_idname` do editor antigo de propósito, e T027 tira a interface antiga do registro. Enquanto ela
    estiver lá, registrar as duas deixaria dois operadores com o mesmo id; a guarda some sozinha quando o antigo sair.
    """
    return cls is BTM_OT_ArmarioV2Abrir and not cls.is_registered \
        and _outro_no_idname(BTM_OT_ArmarioV2Abrir.bl_idname) is not None


def register():
    for cls in classes:
        if not _dividido(cls):
            bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
