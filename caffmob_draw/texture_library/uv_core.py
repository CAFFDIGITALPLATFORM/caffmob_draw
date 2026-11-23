"""Núcleo puro de UV e projeção de textura (feature 018, T007; RN-08, RN-09, RN-10, D-01, D-03, D-14).

Sem `bpy`: escala, repetição, chave de material e escolha de projeção são regra, não cena.

- **UV em metros**: o UV gravado na chapa tem 1 unidade por metro. A escala real da textura fica no `Mapping` do
  material (`1 / tamanho em metros`), então trocar a textura não exige refazer o UV. `repetir`/`escala_uv` existem
  para quem quiser a conta em repetições (testes e relatórios), não para gravar na malha.
- **Três fontes de coordenada** (D-03): `UV` lê o layer `UVMap`; `ATTRIBUTE_UV` lê o atributo `uv_map` que o
  `GeoNodeCutpart` grava (a peça de biblioteca não tem layer de UV, T001); `BOX` projeta em caixa sobre coordenadas
  de objeto, para malha sem UV nenhum.
- **Veio**: `angulo_para_veio` arredonda para o múltiplo de 90 mais próximo, porque o plano de corte só entende
  H/V/NONE (`cutting/part_roles`).
- **Partes do conta-gotas** (T019): Porta, Exterior e Interior são os domínios de `customize/finish_core`
  (`FRONTS`, `EXTERNAL`, `INTERNAL`), sem um segundo vocabulário de partes (RN-11, D-08).
"""

from ..customize import finish_core

MM = 1000.0

UV, ATTRIBUTE_UV, BOX = 'UV', 'ATTRIBUTE_UV', 'BOX'
PROJECTIONS = (UV, ATTRIBUTE_UV, BOX)

LAYER_UV = 'UVMap'
ATRIBUTO_UV = 'uv_map'
PRECISAO_ANGULO = 1e-6

# Partes do conta-gotas → domínios de acabamento (RN-11, D-08). Fita (`EDGE`) e cota não são partes.
PORTA, EXTERIOR, INTERIOR = 'PORTA', 'EXTERIOR', 'INTERIOR'
PARTES = (PORTA, EXTERIOR, INTERIOR)
DOMINIO_DA_PARTE = {PORTA: finish_core.FRONTS, EXTERIOR: finish_core.EXTERNAL, INTERIOR: finish_core.INTERNAL}


def repetir(medida_mm, tamanho_mm):
    """Quantas repetições da textura cabem em `medida_mm`, com o tamanho real do catálogo."""
    if tamanho_mm <= 0:
        raise ValueError("O tamanho da textura precisa ser maior que zero")
    return float(medida_mm) / float(tamanho_mm)


def escala_uv(largura_mm, altura_mm, tamanho_mm, altura_textura_mm=None):
    """(repetições em U, repetições em V) de uma chapa; textura retangular usa cada eixo pelo seu lado."""
    altura_textura = tamanho_mm if altura_textura_mm is None else altura_textura_mm
    return repetir(largura_mm, tamanho_mm), repetir(altura_mm, altura_textura)


def chave_de_material(path, size_mm, projection=BOX, rotated=False):
    """Chave estável de reaproveitamento: mesmo arquivo, mesmo tamanho, mesma projeção e mesma variante girada."""
    return (str(path or ''), round(float(size_mm), 6), str(projection or BOX), bool(rotated))


def angulo_para_veio(angulo):
    """'H' ou 'V' pelo múltiplo de 90 mais próximo; ângulo intermediário não vira veio de corte próprio."""
    from . import grain_core
    return grain_core.direction('H', angulo)


def girar_uv(uv, angulo, centro=0.5):
    """Gira um par de UV em graus em torno de `centro` (mesma convenção do `grain_core`)."""
    import math
    radianos = math.radians(float(angulo))
    x, y = float(uv[0]) - centro, float(uv[1]) - centro
    cos, sen = math.cos(radianos), math.sin(radianos)
    return (cos * x - sen * y + centro, sen * x + cos * y + centro)


def partes_para_dominios(partes):
    """Domínios das marcas escolhidas, na ordem de `PARTES` e sem repetição (RN-11, D-08).

    Aceita uma marca só (`PORTA`) ou uma coleção delas; marca desconhecida (fita, cota) não vira domínio nenhum.
    """
    if isinstance(partes, str):
        marcas = {partes.strip().upper()}
    else:
        marcas = {str(parte or '').strip().upper() for parte in (partes or ())}
    return tuple(DOMINIO_DA_PARTE[parte] for parte in PARTES if parte in marcas)


def dominios_do_alvo(papel, finish_role, excluido=False):
    """Domínios de parte que cobrem uma peça: o que o destaque do conta-gotas e a aplicação consultam (RN-11).

    Fica fora: a fita visual (`excluido`), a cota e qualquer malha sem papel (`btm_armario_parte.papel` vazio), e
    a peça sem papel de acabamento (`finish_role` UNKNOWN). O que sobra é só Porta/Exterior/Interior, nunca `EDGE`.
    """
    if excluido or not str(papel or '').strip():
        return ()
    dominios = DOMINIO_DA_PARTE.values()
    return tuple(d for d in finish_core.domains_for_piece(finish_role) if d in dominios)


def parte_de_dominios(dominios):
    """A parte mais específica que cobre estes domínios: Porta vence Exterior, que vence Interior (RN-11).

    A frente pertence a `EXTERNAL` e a `FRONTS`; mostrar as duas seria ruído.
    """
    for parte in PARTES:
        if DOMINIO_DA_PARTE[parte] in dominios:
            return parte
    return ''


def parte_do_alvo(papel, finish_role, excluido=False):
    """A parte que o destaque do conta-gotas mostra para a peça (T019, RN-11)."""
    return parte_de_dominios(dominios_do_alvo(papel, finish_role, excluido))


def alvos_unicos(nomes):
    """Nomes de alvo sem repetição, na ordem dada: o mesmo alvo não recebe a textura duas vezes (RN-11)."""
    vistos, unicos = set(), []
    for nome in nomes or ():
        if nome and nome not in vistos:
            vistos.add(nome)
            unicos.append(nome)
    return unicos


def projecao_do_alvo(tem_cutpart, tem_layer_uv):
    """Projeção que o alvo aceita: cutpart pelo atributo, malha com layer pelo UV, resto em caixa (D-14)."""
    if tem_cutpart:
        return ATTRIBUTE_UV
    if tem_layer_uv:
        return UV
    return BOX
