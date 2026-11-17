"""Caixa de contexto da parede no Editor de Paredes (BUG-20261117-AKYJ).

Python puro: o layout, o alvo do clique e a regra de abertura são provados sem o Blender. A caixa abre no ponto do
clique com o botão direito, no modo Selecionar, e traz Linha/Direção, inverter o sentido de todas as paredes ativas e
o tipo de parede com cor (decisões do titular em 2026-11-17).
"""

from ..data.i18n import tr
from . import cores

LINHA, DIRECAO, INVERTER, TIPO = 'linha', 'direcao', 'inverter', 'tipo'
LARGURA = 236
ALTURA_ITEM = 24
PAD = 6
MARGEM = 4


def abre_menu(tool, event_type, event_value):
    """O botão direito abre a caixa no modo Selecionar; no Desenhar ele continua encerrando o lápis."""
    return event_type == 'RIGHTMOUSE' and event_value == 'PRESS' and tool == 'SELECT'


def tipo_da_chave(chave):
    """`'tipo:DIVISORIA'` devolve `'DIVISORIA'`; qualquer outra linha devolve None."""
    return chave[len(TIPO) + 1:] if chave.startswith(TIPO + ':') else None


def itens(linha, direcao, tipo):
    """Linhas da caixa, na ordem pedida: Linha, Direção, inverter e os três tipos com cor e marca do atual.

    `linha` em `('INNER', 'OUTER')`; `direcao` em `('LEFT', 'RIGHT')` e `tipo` em `model.WALL_TYPES`; None quando as
    paredes ativas divergem (a caixa mostra "Múltiplas" e nenhum tipo marcado).
    """
    linhas = [
        dict(id=LINHA, rotulo=tr("Linha"), valor=tr("Externa") if linha == 'OUTER' else tr("Interna")),
        dict(id=DIRECAO, rotulo=tr("Direção"),
             valor=tr("Esquerda") if direcao == 'LEFT' else tr("Direita") if direcao == 'RIGHT' else tr("Múltiplas")),
        dict(id=INVERTER, rotulo=tr("Inverter sentido"), valor=""),
    ]
    for nome, rotulo in (('NORMAL', tr("Normal")), ('DIVISORIA', tr("Divisória")), ('MURETA', tr("Mureta"))):
        linhas.append(dict(id=TIPO + ':' + nome, rotulo=rotulo, valor="", cor=cores.cor(nome), marcado=nome == tipo))
    return linhas


def layout(pixel, itens, regiao):
    """Caixa com o canto superior esquerdo no clique e as linhas para baixo, presa dentro de `regiao`.

    `regiao` é `(x, y, largura, altura)` em pixels da área do editor; devolve `x`, `y`, `largura`, `altura` e
    `itens` como `(chave, retângulo)`.
    """
    x0, y0, largura_regiao, altura_regiao = regiao
    altura = PAD * 2 + len(itens) * ALTURA_ITEM
    x = min(max(pixel[0], x0 + MARGEM), x0 + largura_regiao - LARGURA - MARGEM)
    y = min(max(pixel[1] - altura, y0 + MARGEM), y0 + altura_regiao - altura - MARGEM)
    x, y = max(x, x0), max(y, y0)
    caixa = dict(x=x, y=y, largura=LARGURA, altura=altura, itens=[], linhas=list(itens))
    for k, item in enumerate(itens):
        topo = y + altura - PAD - (k + 1) * ALTURA_ITEM
        caixa['itens'].append((item['id'], (x + MARGEM, topo, LARGURA - 2 * MARGEM, ALTURA_ITEM)))
    return caixa


def alvo(caixa, pixel):
    """Chave da linha sob o pixel, ou None quando o clique cai fora da caixa."""
    x, y, largura, altura = caixa['x'], caixa['y'], caixa['largura'], caixa['altura']
    if not (x <= pixel[0] <= x + largura and y <= pixel[1] <= y + altura):
        return None
    for chave, r in caixa['itens']:
        if r[0] <= pixel[0] <= r[0] + r[2] and r[1] <= pixel[1] <= r[1] + r[3]:
            return chave
    return None


def estado(trechos, plano):
    """(linha, direção, tipo) para os valores já aparecerem na caixa a partir dos trechos ativos."""
    lados = {plano.chains[ci].side for ci, _si in trechos}
    tipos = {plano.chains[ci].segments[si].wall_type for ci, si in trechos}
    return (next(iter(lados)) if len(lados) == 1 else None,
            next(iter(tipos)) if len(tipos) == 1 else None)
