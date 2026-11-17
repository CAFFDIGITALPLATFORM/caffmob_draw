"""Ferramenta Medir entre dois pontos do Editor de Paredes (BUG-20261117-V4I3). Python puro.

O estado é um dicionário `{'inicio': (x, y) | None, 'fim': (x, y) | None}`, em metros do mundo 2D, como as paredes.
O primeiro clique guarda o início, o segundo fecha a medida e o clique seguinte começa outra. O ímã é o mesmo dos
vértices das outras ferramentas: o candidato mais próximo na tela, até `SNAP_PX`. Medir é só leitura: nada vai para o
rascunho nem para o desfazer.
"""

import math

SNAP_PX = 9


def novo():
    return {'inicio': None, 'fim': None}


def ativa(estado):
    return bool(estado and estado['inicio'] is not None)


def fechada(estado):
    return bool(estado and estado['inicio'] is not None and estado['fim'] is not None)


def clicar(estado, ponto):
    """Primeiro clique começa a medida, o segundo fecha; depois de fechada, o clique seguinte começa outra."""
    if ativa(estado) and not fechada(estado):
        return {'inicio': estado['inicio'], 'fim': (float(ponto[0]), float(ponto[1]))}
    return {'inicio': (float(ponto[0]), float(ponto[1])), 'fim': None}


def limpar(_estado=None):
    """Esc: a medição some sem tocar nas paredes."""
    return None


def distancia(estado):
    """Distância em metros entre os dois pontos; None enquanto falta o segundo."""
    if not fechada(estado):
        return None
    return math.hypot(estado['fim'][0] - estado['inicio'][0], estado['fim'][1] - estado['inicio'][1])


def snap(ponto, candidatos, para_pixel, limite=SNAP_PX):
    """(ponto, tipo) do ímã: o candidato mais próximo na tela, ou o próprio cursor livre.

    `para_pixel` converte um ponto do mundo 2D em pixels da vista, então o limite vale na tela, como o dos vértices.
    """
    pixel = para_pixel(ponto)
    melhor = None
    for candidato in candidatos:
        q = para_pixel(candidato)
        d = math.hypot(q[0] - pixel[0], q[1] - pixel[1])
        if d <= limite and (melhor is None or d < melhor[0]):
            melhor = (d, candidato)
    if melhor is None:
        return (ponto[0], ponto[1]), 'free'
    return (melhor[1][0], melhor[1][1]), 'node'
