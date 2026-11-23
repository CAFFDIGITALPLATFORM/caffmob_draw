"""Bloco de gavetas do armário v2 (feature 017, T016; RN-06, RN-07, RN-09).

Python puro, em milímetros. O bloco distribui a altura disponível entre as gavetas com folga de 3 mm nas pontas e
entre elas, cada gaveta leva um dos dez modelos de frente do mockup (ou um modelo único para o bloco) e a caixa recebe
separadores de 6 mm por colunas e linhas e os quatro afastadores independentes.

Os afastadores são tiras presas à frente/traseira e às laterais da caixa para afastar a frente do corpo; a largura de
60 mm é a do mockup do anexo e fica num único lugar (`AFASTADOR_LARGURA`).
"""

from dataclasses import dataclass, replace
from uuid import uuid4

FOLGA = 3.0
ESPESSURA_SEPARADOR = 6.0
AFASTADOR_LARGURA = 60.0

MODELOS = (
    's_cf_reta',
    's_cf_normal',
    's_cf_vidro',
    's_cf_gola',
    's_cf_cava',
    'c_cf_reta',
    'c_cf_normal',
    'c_cf_vidro',
    'c_cf_gola',
    'c_cf_cava',
)

MODELO_PADRAO = 's_cf_reta'


@dataclass(frozen=True)
class Gaveta:
    """Uma gaveta do bloco: o vão que a contém, o índice, a altura, o modelo e o separador/afastadores."""

    uid: str
    vao: str
    indice: int
    altura: float
    modelo: str
    separador_colunas: int = 1
    separador_linhas: int = 1
    afastador_frente: bool = True
    afastador_tras: bool = True
    afastador_esq: bool = True
    afastador_dir: bool = True
    corredica_3d: bool = True


def alturas(altura_bloco, quantidade):
    """Altura de cada gaveta: (bloco − (n + 1) × folga) / n, todas iguais (RN-07)."""
    quantidade = int(quantidade)
    if quantidade <= 0:
        raise ValueError("O bloco precisa de pelo menos uma gaveta")
    livre = float(altura_bloco) - (quantidade + 1) * FOLGA
    if livre <= 0.0:
        raise ValueError(f"Bloco de {float(altura_bloco):g} mm não comporta {quantidade} gavetas com folga de "
                         f"{FOLGA:g} mm")
    return [livre / quantidade] * quantidade


def bloco(altura_bloco, quantidade, modelo=None, modelos=None, vao='', uid=None):
    """Gavetas do bloco: `modelo` único vale para todas; `modelos` dá um por gaveta (RN-07, RF-09)."""
    alturas_ = alturas(altura_bloco, quantidade)
    if modelos is not None:
        modelos = list(modelos)
        if len(modelos) != len(alturas_):
            raise ValueError(f"Informe um modelo por gaveta: {len(alturas_)} esperados, {len(modelos)} recebidos")
    else:
        modelos = [modelo or MODELO_PADRAO] * len(alturas_)
    for nome in modelos:
        if nome not in MODELOS:
            raise ValueError(f"Modelo de frente desconhecido: {nome}")
    prefixo = uid or uuid4().hex[:8]
    return [Gaveta(f"{prefixo}/{indice}", vao, indice, altura, modelos[indice])
            for indice, altura in enumerate(alturas_)]


def _separadores(gaveta, largura_caixa, profundidade_caixa):
    """Separadores de 6 mm por colunas (verticais) e linhas (horizontais), dentro da caixa."""
    pecas = []
    verticais = max(0, int(gaveta.separador_colunas) - 1)
    horizontais = max(0, int(gaveta.separador_linhas) - 1)
    for indice in range(verticais):
        pecas.append({'papel': 'SEPARADOR', 'nome': f"Separador vertical {indice + 1}", 'lado': '',
                      'comprimento': max(0.0, gaveta.altura - 2.0 * FOLGA),
                      'largura': float(profundidade_caixa), 'espessura': ESPESSURA_SEPARADOR})
    for indice in range(horizontais):
        pecas.append({'papel': 'SEPARADOR', 'nome': f"Separador horizontal {indice + 1}", 'lado': '',
                      'comprimento': float(largura_caixa), 'largura': float(profundidade_caixa),
                      'espessura': ESPESSURA_SEPARADOR})
    return pecas


def _afastadores(gaveta, largura_caixa, profundidade_caixa, espessura):
    """Os quatro afastadores, cada um independente (RN-09, RF-11)."""
    lados = (
        ('frente', gaveta.afastador_frente, largura_caixa),
        ('tras', gaveta.afastador_tras, largura_caixa),
        ('esq', gaveta.afastador_esq, profundidade_caixa),
        ('dir', gaveta.afastador_dir, profundidade_caixa),
    )
    return [{'papel': 'AFASTADOR', 'nome': f"Afastador {lado}", 'lado': lado,
             'comprimento': float(comprimento), 'largura': AFASTADOR_LARGURA, 'espessura': float(espessura)}
            for lado, ativo, comprimento in lados if ativo]


def chapas(gaveta, largura_caixa, profundidade_caixa, espessura):
    """Peças da caixa da gaveta: separadores e afastadores, em milímetros (RN-09)."""
    pecas = _separadores(gaveta, largura_caixa, profundidade_caixa)
    pecas.extend(_afastadores(gaveta, largura_caixa, profundidade_caixa, espessura))
    return pecas


def com_separador(gaveta, colunas=None, linhas=None):
    """Cópia da gaveta com o separador trocado, para o painel editar sem refazer o bloco."""
    return replace(gaveta, separador_colunas=colunas if colunas is not None else gaveta.separador_colunas,
                   separador_linhas=linhas if linhas is not None else gaveta.separador_linhas)
