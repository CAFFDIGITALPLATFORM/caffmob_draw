"""Peça sob o cursor e partes do conta-gotas (feature 018, T016/T019; RF-10, RN-11).

A assinatura da textura copiada vive em `WindowManager.btm_texture_pick` (T015, D-09). Aqui ficam só o que o cursor
aponta — estado de vista, não de sessão —, a regra que transforma a peça em parte e a projeção do destaque.

Nada aqui toca a cena: apontar não aplica textura nem grava passo de desfazer.
"""

import bpy  # type: ignore
from mathutils import Vector  # type: ignore
from bpy_extras.view3d_utils import (  # type: ignore
    location_3d_to_region_2d,
    region_2d_to_origin_3d,
    region_2d_to_vector_3d,
)

from ..customize import finish_core
from ..data.i18n import N_, tr
from . import uv_core

GRUPO = 'btm_texture_pick'
ROTULOS = {uv_core.PORTA: N_("Porta"), uv_core.EXTERIOR: N_("Exterior"), uv_core.INTERIOR: N_("Interior")}
PAPEIS_DE_FRENTE = ('PORTA', 'FOLHA', 'FRENTE_GAVETA')
_ARESTAS = ((0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7))

_apontado = {'alvo': '', 'parte': ''}


# Assinatura da sessão (T015) -------------------------------------------------------------------------------------

def estado(context=None):
    """Grupo da sessão do conta-gotas, ou None sem a extensão registrada."""
    return getattr((context or bpy.context).window_manager, GRUPO, None)


def ativo(context=None):
    grupo = estado(context)
    return bool(grupo is not None and grupo.ativo)


def alvos(context=None):
    """Nomes congelados quando o conta-gotas abriu; a seleção pode mudar durante o gesto (RN-11)."""
    grupo = estado(context)
    return [nome for nome in (grupo.alvos.split('\n') if grupo is not None else ()) if nome]


def iniciar(context, alvos=()):
    """Abre a sessão: limpa a assinatura anterior e congela os alvos na seleção atual."""
    grupo = estado(context)
    if grupo is None:
        return None
    grupo.ativo = True
    grupo.path = grupo.nome = grupo.texture_id = grupo.origem = ''
    grupo.size_mm = grupo.height_mm = grupo.angle = 0.0
    grupo.alvos = '\n'.join(uv_core.alvos_unicos([obj.name if obj is not None else "" for obj in alvos]))
    apontar(None)
    return grupo


def encerrar(context=None):
    """Fecha o modo de apontar; a assinatura e os alvos ficam para a aplicação por partes (T017)."""
    grupo = estado(context)
    if grupo is not None:
        grupo.ativo = False
    apontar(None)


def angulo_da_peca(obj):
    """Giro do veio em graus gravado na peça (T020); 0 quando a peça não tem o campo."""
    for dono in (getattr(obj, 'btm_armario_parte', None), getattr(obj, 'btm_part', None)):
        valor = getattr(dono, 'grain_angle', None)
        if valor is not None:
            return float(valor)
    return 0.0


# Peça sob o cursor e parte ---------------------------------------------------------------------------------------

def _papeis(obj):
    """(papel gravado, papel de acabamento): o armário v2 deriva do componente; a biblioteca, do assistente."""
    grupo = getattr(obj, 'btm_armario_parte', None)
    papel = str(getattr(grupo, 'papel', '') or '')
    if papel:
        return papel, finish_core.piece_role_of_component(str(getattr(grupo, 'componente', '') or ''),
                                                          is_front=papel in PAPEIS_DE_FRENTE)
    return papel, str(getattr(getattr(obj, 'btm_part', None), 'finish_role', '') or finish_core.PIECE_UNKNOWN)


def dominios_do_objeto(obj):
    """Domínios de parte que a peça cobre; () quando ela não recebe textura (fita, cota, sem papel)."""
    if obj is None or obj.type != 'MESH':
        return ()
    papel, acabamento = _papeis(obj)
    return uv_core.dominios_do_alvo(papel, acabamento, excluido=bool(obj.get('btm_cut_exclude', False)))


def parte_do_objeto(obj):
    """Porta, Exterior, Interior ou '' — a parte mais específica que a peça cobre."""
    return uv_core.parte_de_dominios(dominios_do_objeto(obj))


def alvo():
    return bpy.data.objects.get(_apontado['alvo']) if _apontado['alvo'] else None


def parte():
    return _apontado['parte']


def rotulo(valor=None):
    """Nome da parte traduzido: "Porta", "Exterior", "Interior"."""
    chave = valor or _apontado['parte']
    return tr(ROTULOS[chave]) if chave in ROTULOS else ''


def apontar(obj):
    """Grava a peça sob o cursor e a parte dela."""
    _apontado['alvo'] = obj.name if obj is not None else ''
    _apontado['parte'] = parte_do_objeto(obj)


def atualizar(context, region, x, y):
    """Aponta a peça sob o cursor por raio na cena; devolve o objeto (None fora de malha)."""
    obj = None
    if region is not None and region.type == 'WINDOW' and context.region_data is not None:
        depsgraph = context.evaluated_depsgraph_get()
        origem = region_2d_to_origin_3d(region, context.region_data, (x, y))
        direcao = region_2d_to_vector_3d(region, context.region_data, (x, y))
        achou, _local, _normal, _indice, encontrado, _matriz = context.scene.ray_cast(depsgraph, origem, direcao)
        obj = encontrado if achou and encontrado is not None and encontrado.type == 'MESH' else None
    apontar(obj)
    return obj


# Desenho --------------------------------------------------------------------------------------------------------

def pontos_do_destaque(obj, region, rv3d):
    """([(x1, y1, x2, y2), ...], (x, y) do rótulo) em pixels da região, ou ([], None) sem vista 3D."""
    if obj is None or region is None or rv3d is None or obj.type != 'MESH':
        return [], None
    cantos = [obj.matrix_world @ Vector(canto) for canto in obj.bound_box]
    pontos = [location_3d_to_region_2d(region, rv3d, canto) for canto in cantos]
    if any(ponto is None for ponto in pontos):
        return [], None
    segmentos = [(pontos[a].x, pontos[a].y, pontos[b].x, pontos[b].y) for a, b in _ARESTAS]
    alto = max(pontos, key=lambda ponto: ponto.y)
    return segmentos, (alto.x, alto.y)
