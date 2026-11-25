"""Gerador puro e determinístico da textura padrão MDF claro (feature 024, T004; RN-01, D-01).

Sem `bpy` e sem rede: a imagem é bytes RGBA calculados aqui, com semente fixa, para o mesmo pedido devolver sempre a
mesma textura. O `textura_padrao` leva esses bytes para uma `bpy.data.images` empacotada (T005).

Aparência: MDF claro (bege quente), grão fino de baixa amplitude e uma fibra mais escura a cada 37 linhas — o
suficiente para o Solid mostrar material em vez de uma cor chapada, sem chamar atenção no render.
"""

TAMANHO = 512
SEMENTE = 20261125
BASE = (222, 205, 183)          # bege claro do MDF, em RGB
VARIACAO = 7                    # ±7 níveis por pixel: grão fino
FIBRA = 6                       # escurecimento da linha de fibra
PASSO_FIBRA = 37

_MULT = 1103515245
_INC = 12345
_MASK = 0x7FFFFFFF


def _proximo(estado):
    """Passo do LCG (estado, valor 15 bits): determinístico e sem dependência externa."""
    estado = (estado * _MULT + _INC) & _MASK
    return estado, (estado >> 16) & 0x7FFF


def _canal(valor):
    return 0 if valor < 0 else (255 if valor > 255 else valor)


def gerar(tamanho=TAMANHO, semente=SEMENTE):
    """Bytes RGBA (`tamanho × tamanho × 4`) da textura padrão; mesma semente, mesmos bytes."""
    if tamanho <= 0:
        raise ValueError("O tamanho da textura precisa ser maior que zero")
    estado = semente & _MASK
    dados = bytearray(tamanho * tamanho * 4)
    for y in range(tamanho):
        fibra = -FIBRA if y % PASSO_FIBRA == 0 else 0
        linha = y * tamanho * 4
        for x in range(tamanho):
            estado, ruido = _proximo(estado)
            tom = (ruido % (2 * VARIACAO + 1)) - VARIACAO + fibra
            indice = linha + x * 4
            dados[indice] = _canal(BASE[0] + tom)
            dados[indice + 1] = _canal(BASE[1] + tom)
            dados[indice + 2] = _canal(BASE[2] + tom)
            dados[indice + 3] = 255
    return bytes(dados)
