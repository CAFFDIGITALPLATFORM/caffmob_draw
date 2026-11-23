"""Ponte dos módulos de biblioteca para o motor v2 (feature 017, T026; RN-21, D-13, RF-24).

O motor novo passa a desenhar também os módulos frameless, face frame e closets (e os CAFFMob, `BTM`): o módulo vira
um `spec.Spec` em milímetros e o `Gerar` cria o armário v2 ao lado, com as peças do mesmo cálculo (RN-21).

- **Leitura** (`ler_modulo`): medidas de `editing.get_dimension` (metros) para milímetros, montagem de
  `btm_cabinet.assembly`, presença das chapas de `has_*`, espessuras de `btm_cabinet.thickness` com as sobrescritas da
  estrutura (`btm_structure`), portas de `btm_cabinet.door_swing` e as divisões de `scene_divisions.read`, que gravam
  vão, eixo, posição e variante como o `vaos.Divisao` do motor novo.
- **Sem correspondência completa** (`ler_modulo` devolve avisos, não exceção): módulo sem medidas abre a aba vazia do
  construtor em vez de falhar; prateleiras e gavetas das bibliotecas antigas não são convertidas e o aviso pede que
  sejam refeitas nas abas; divisão fora do vão raiz (`s0`) fica de fora, porque a árvore do motor novo nasce de um vão
  só.
- **Gerar**: cria (ou reaproveita) o armário v2 do módulo, grava o spec e as divisões, semeia o contrato e gera. Só
  quando a geração passa é que o módulo antigo é ocultado e marcado com `btm_cut_exclude` — as duas marcas que
  `cutting/part_sources` já respeita —, e os nomes marcados ficam gravados na raiz para a reversão.
- **Recriar do módulo**: desfaz a conversão — devolve a visibilidade e as marcas do módulo e apaga o armário v2 que
  saiu dele. A raiz guarda `btm_armario.origem` com o nome do módulo, o que também é o que o painel lê para oferecer o
  botão.
"""

import json

import bpy  # type: ignore

from ..cabinet_editor import scene_divisions
from ..data.i18n import tr
from ..selection import classify, editing
from . import build
from . import ops
from . import resumo
from . import spec as spec_mod
from . import vaos as vaos_mod

BIBLIOTECAS = ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM')

# Papel da estrutura da caixa (legado) -> campo de espessura do armário v2.
PAPEL_DA_ESTRUTURA = {
    'TOP': 'espessura_base_superior',
    'BOTTOM': 'espessura_base_inferior',
    'LEFT': 'espessura_lateral',
    'RIGHT': 'espessura_lateral',
    'BACK': 'espessura_fundo',
}
# Chapas do `btm_cabinet` com espessura própria -> campo do armário v2.
ESPESSURA_DO_CABINET = (
    ('espessura_lateral', 'thickness_left'),
    ('espessura_base_inferior', 'thickness_bottom'),
    ('espessura_base_superior', 'thickness_top'),
    ('espessura_fundo', 'thickness_back'),
)
# `door_swing` do legado -> (porta ligada, folhas, dobradiça).
PORTAS = {
    'NONE': (False, 1, 'ESQUERDA'),
    'LEFT': (True, 1, 'ESQUERDA'),
    'RIGHT': (True, 1, 'DIREITA'),
    'DOUBLE': (True, 2, 'ESQUERDA'),
    'FLIP': (True, 1, 'ESQUERDA'),
}
TIPOS_DE_DIVISAO = {'FIXED': vaos_mod.FIXA, 'MOVABLE': vaos_mod.MOVEL, 'SPACER': vaos_mod.ESPACADOR}

PROP_MODULO = 'btm_armario_modulo'      # nome do módulo de origem gravado na raiz do armário v2
PROP_MARCADOS = 'btm_armario_marcados'  # nomes dos objetos que o Gerar ocultou e marcou


# Leitura -----------------------------------------------------------------------------------------------------------
def modulo_da_selecao(context):
    """Raiz do módulo de biblioteca da seleção (subindo a hierarquia), ou `None`."""
    obj = getattr(context, 'active_object', None)
    raiz, biblioteca = classify.module_root(obj) if obj is not None else (None, None)
    if raiz is None or biblioteca not in BIBLIOTECAS:
        return None
    if ops.e_raiz(raiz):
        return None                     # já é armário do motor novo
    return raiz


def armario_da_selecao(context):
    """Raiz do armário v2 da seleção, subindo a hierarquia (o mesmo critério de `ops._raiz`)."""
    obj = getattr(context, 'active_object', None)
    while obj is not None:
        if ops.e_raiz(obj):
            return obj
        obj = obj.parent
    return None


def _mm_no_enum(valor):
    """Espessura encaixada num dos itens do enum (6, 15, 18 ou 25 mm), como o contrato de chapas."""
    return float(min(spec_mod.THICKNESSES, key=lambda item: abs(item - float(valor))))


def medidas_do_modulo(modulo):
    """(largura, altura, profundidade) em milímetros, ou `None` quando o módulo não tem as três medidas."""
    info = classify.classify(modulo)
    medidas = []
    for campo in ('width', 'height', 'depth'):
        try:
            valor = editing.get_dimension(info, campo)
        except (AttributeError, KeyError, TypeError, ValueError):
            return None
        if not valor or float(valor) <= 0.0:
            return None
        medidas.append(float(valor) * 1000.0)
    return tuple(medidas)


def espessuras_do_modulo(modulo):
    """Espessuras por papel em mm: a do `btm_cabinet` e as sobrescritas da estrutura do módulo."""
    cab = getattr(modulo, 'btm_cabinet', None)
    base = float(getattr(cab, 'thickness', 0.0) or 0.0) * 1000.0 or 15.0
    papeis = {campo: base for campo in spec_mod.THICKNESS_FIELDS}
    if cab is not None:
        for papel, campo in ESPESSURA_DO_CABINET:
            valor = float(getattr(cab, campo, 0.0) or 0.0)
            if valor > 0.0:
                papeis[papel] = valor * 1000.0
    estrutura = getattr(modulo, 'btm_structure', None)
    for entrada in getattr(estrutura, 'components', ()) if estrutura is not None else ():
        papel = PAPEL_DA_ESTRUTURA.get(getattr(entrada, 'role', ''))
        valor = float(getattr(entrada, 'thickness', 0.0) or 0.0)
        if papel is not None and valor > 0.0 and not getattr(entrada, 'removed', False):
            papeis[papel] = valor * 1000.0
    return {papel: _mm_no_enum(valor) for papel, valor in papeis.items()}


def presenca_do_modulo(modulo):
    """Chapas da caixa do módulo: as flags do `btm_cabinet`; nas outras bibliotecas a caixa existe inteira."""
    cab = getattr(modulo, 'btm_cabinet', None)
    if cab is None:
        return {'lateral_esq_ativa': True, 'lateral_dir_ativa': True, 'base_inf_ativa': True,
                'base_sup_ativa': True, 'fundo_ativo': True}
    return {'lateral_esq_ativa': bool(cab.has_left), 'lateral_dir_ativa': bool(cab.has_right),
            'base_inf_ativa': bool(cab.has_bottom), 'base_sup_ativa': bool(cab.has_top),
            'fundo_ativo': bool(cab.has_back)}


def divisoes_do_modulo(modulo, espessuras):
    """(divisões, avisos) do módulo, já no `vaos.Divisao` do motor novo (mm)."""
    saida, fora_do_raiz = [], False
    for item in scene_divisions.read(modulo):
        vao = str(item.get('space') or '')
        if not vao.startswith(vaos_mod.RAIZ):
            fora_do_raiz = True
            continue
        eixo = vaos_mod.VERTICAL if item.get('orientation') == vaos_mod.VERTICAL else vaos_mod.HORIZONTAL
        espessura = float(item.get('thickness') or 0.0) * 1000.0
        if espessura <= 0.0:
            espessura = espessuras['espessura_divisoria' if eixo == vaos_mod.VERTICAL else
                                   'espessura_prateleira']
        saida.append(vaos_mod.Divisao(
            uid=str(item.get('uid') or ''), eixo=eixo, vao=vao, posicao=float(item.get('offset') or 0.0) * 1000.0,
            tipo=TIPOS_DE_DIVISAO.get(item.get('kind'), vaos_mod.FIXA), espessura=espessura,
            recuo_tras=float(item.get('back') or 0.0) * 1000.0 if item.get('use_back') else 0.0,
            recuo_frente=float(item.get('front') or 0.0) * 1000.0 if item.get('use_front') else 0.0))
    avisos = []
    if fora_do_raiz:
        avisos.append(tr("Divisões fora do vão raiz ficam de fora no motor novo"))
    return saida, avisos


def ler_modulo(modulo):
    """(spec, divisões, avisos) do módulo de biblioteca; spec `None` quando faltam as medidas."""
    medidas = medidas_do_modulo(modulo)
    if medidas is None:
        return None, [], [tr("O módulo não tem medidas para o motor novo")]
    largura, altura, profundidade = medidas
    espessuras = espessuras_do_modulo(modulo)
    divisoes, avisos = divisoes_do_modulo(modulo, espessuras)
    cab = getattr(modulo, 'btm_cabinet', None)
    montagem = (spec_mod.BASE_PASSANTE if getattr(cab, 'assembly', 'LATERAL') == 'BASE'
                else spec_mod.LATERAL_PASSANTE)
    porta_ativa, folhas, dobradica = PORTAS.get(getattr(cab, 'door_swing', 'NONE'), PORTAS['NONE'])
    spec = spec_mod.Spec(largura=largura, altura=altura, profundidade=profundidade, tipo_montagem=montagem,
                         **espessuras, **presenca_do_modulo(modulo), porta_ativa=porta_ativa,
                         porta_folhas=folhas, porta_dobradica=dobradica)
    if getattr(cab, 'shelves', 0):
        avisos.append(tr("Prateleiras do módulo não são convertidas: refaça na aba Divisões"))
    return spec, divisoes, avisos


# Aplicação na cena -------------------------------------------------------------------------------------------------
def _gravar_spec(armario, spec):
    """Grava o spec no armário v2; espessura é enum textual, o resto é número ou booleano."""
    for campo in spec_mod.Spec.__dataclass_fields__:
        if not hasattr(armario, campo):
            continue
        valor = getattr(spec, campo)
        setattr(armario, campo, str(int(valor)) if campo in spec_mod.THICKNESS_FIELDS else valor)


def raiz_do_modulo(modulo):
    """Armário v2 já criado a partir do módulo (pelo nome gravado em `btm_armario.origem`)."""
    if modulo is None:
        return None
    for obj in bpy.data.objects:
        if getattr(obj, 'btm_armario', None) is not None and obj.btm_armario.origem == modulo.name:
            return obj
    return None


def _marcar_modulo(modulo):
    """Oculta o módulo e marca o corte; devolve os nomes que já não estavam marcados."""
    marcados = []
    alvos = [modulo] + [obj for obj in modulo.children_recursive if obj.type == 'MESH']
    for obj in alvos:
        if not getattr(obj, 'btm_cut_exclude', False):
            obj.btm_cut_exclude = True
            marcados.append(obj.name)
        obj.hide_viewport = True
    return marcados


def gerar_do_modulo(context, modulo):
    """Cria (ou reaproveita) o armário v2 do módulo e gera; oculta o módulo só quando a geração passa."""
    spec, divisoes, avisos = ler_modulo(modulo)
    if spec is None:
        return None, avisos
    raiz = raiz_do_modulo(modulo)
    if raiz is None:
        raiz = build.criar_raiz(context.scene, nome=f"{modulo.name} (v2)")
        raiz.location = modulo.matrix_world.to_translation()
    armario = raiz.btm_armario
    armario.origem = modulo.name
    _gravar_spec(armario, spec)
    ops.gravar_divisoes(armario, divisoes)
    ops.semear_contrato(context.scene)
    gerou, avisos_geracao = ops.gerar_armario(raiz, context)
    avisos = avisos + list(avisos_geracao)
    if not gerou:
        avisos.append(tr("A geração recusou o módulo: o módulo antigo continua visível"))
        return raiz, avisos
    raiz[PROP_MODULO] = modulo.name
    raiz[PROP_MARCADOS] = json.dumps(_marcar_modulo(modulo))
    armario.snapshot = ops.snapshot_de(raiz)
    return raiz, avisos


def recriar_do_modulo(context, raiz):
    """Desfaz a conversão: devolve o módulo à cena e apaga o armário v2 que saiu dele."""
    nome = raiz.get(PROP_MODULO) or raiz.btm_armario.origem
    modulo = bpy.data.objects.get(nome) if nome else None
    if modulo is None:
        return [tr("O módulo de origem não está mais na cena")]
    for nome_obj in json.loads(raiz.get(PROP_MARCADOS) or '[]'):
        obj = bpy.data.objects.get(nome_obj)
        if obj is not None:
            obj.btm_cut_exclude = False
            obj.hide_viewport = False
    modulo.hide_viewport = False
    build.limpar(raiz)
    bpy.data.objects.remove(raiz, do_unlink=True)
    return []


# Painel ------------------------------------------------------------------------------------------------------------
def desenhar_modulo(layout, context, modulo):
    """Aba do construtor para o módulo de biblioteca ainda não convertido (D-13)."""
    spec, _divisoes, avisos = ler_modulo(modulo)
    caixa = layout.box()
    biblioteca = classify.module_library(modulo) or ''
    caixa.label(text=tr("Módulo de biblioteca: {}").format(tr(classify.LIBRARY_LABELS.get(biblioteca, biblioteca))),
                icon='LIBRARY_DATA_DIRECT')
    caixa.label(text=modulo.name, icon='OBJECT_DATA')
    if spec is not None:
        caixa.label(text=tr("{} × {} × {} mm").format(f"{spec.largura:g}", f"{spec.altura:g}",
                                                      f"{spec.profundidade:g}"))
        caixa.label(text=tr("Montagem: {}").format(tr(resumo.MONTAGENS.get(spec.tipo_montagem,
                                                                          spec.tipo_montagem))))
    for aviso in avisos:
        caixa.label(text=aviso, icon='ERROR')
    caixa.operator("caffmob.armario_v2_gerar_do_modulo", text=tr("Gerar pelo motor novo"), icon='FILE_REFRESH')


# Operadores --------------------------------------------------------------------------------------------------------
class BTM_OT_ArmarioV2GerarDoModulo(bpy.types.Operator):
    """Gera o armário novo a partir do módulo de biblioteca escolhido e oculta o módulo antigo"""

    bl_idname = "caffmob.armario_v2_gerar_do_modulo"
    bl_label = "Gerar pelo motor novo"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if modulo_da_selecao(context) is None:
            cls.poll_message_set(tr("Selecione um módulo de biblioteca"))
            return False
        return True

    def execute(self, context):
        modulo = modulo_da_selecao(context)
        if modulo is None:
            return {'CANCELLED'}
        raiz, avisos = gerar_do_modulo(context, modulo)
        for aviso in avisos:
            self.report({'WARNING'}, aviso)
        if raiz is None or not raiz.btm_armario.gerado:
            return {'CANCELLED'}
        if getattr(context, 'view_layer', None) is not None:
            context.view_layer.objects.active = raiz
        return {'FINISHED'}


class BTM_OT_ArmarioV2RecriarDoModulo(bpy.types.Operator):
    """Devolve o módulo de biblioteca à cena e apaga o armário novo que saiu dele"""

    bl_idname = "caffmob.armario_v2_recriar_do_modulo"
    bl_label = "Recriar do módulo"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        raiz = armario_da_selecao(context)
        if raiz is None or not raiz.btm_armario.origem:
            cls.poll_message_set(tr("Selecione um armário criado a partir de um módulo"))
            return False
        return True

    def execute(self, context):
        raiz = armario_da_selecao(context)
        if raiz is None:
            return {'CANCELLED'}
        avisos = recriar_do_modulo(context, raiz)
        for aviso in avisos:
            self.report({'WARNING'}, aviso)
        if avisos:
            return {'CANCELLED'}
        return {'FINISHED'}


classes = (BTM_OT_ArmarioV2GerarDoModulo, BTM_OT_ArmarioV2RecriarDoModulo)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls.is_registered:
            bpy.utils.unregister_class(cls)
