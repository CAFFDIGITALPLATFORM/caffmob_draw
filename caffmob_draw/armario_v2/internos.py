"""Internos do vão: cabideiro, calceiro, sapateira e maleiro (feature 017, T018; RN-13).

Python puro, em milímetros. Calceiro e sapateira nascem a 480 mm do piso do vão; o maleiro, 420 mm abaixo do topo;
o cabideiro, no piso. A posição vertical é editável dentro de `[0, altura do vão − espessura do interno]`.

Dois internos na mesma altura é premissa 🟡 do roadmap §4: o último vence e o outro sobe 50 mm. A regra fica isolada
aqui (`PASSO_DESEMPATE`), para ser corrigida sem tocar nas abas do painel.
"""

from dataclasses import dataclass, replace
from uuid import uuid4

ALTURA_BAIXA = 480.0
MALEIRO_ABAIXO_TOPO = 420.0
PASSO_DESEMPATE = 50.0
TIPOS = ('CABIDEIRO', 'CALCEIRO', 'SAPATEIRA', 'MALEIRO')


@dataclass(frozen=True)
class Interno:
    """Um interno preso a um vão, na altura medida do piso do vão em milímetros."""

    uid: str
    vao: str
    tipo: str
    altura: float


def altura_inicial(tipo, altura_vao):
    """Altura de nascimento do interno, pela posição do mockup (RF-12)."""
    if tipo in ('CALCEIRO', 'SAPATEIRA'):
        return ALTURA_BAIXA
    if tipo == 'MALEIRO':
        return max(0.0, float(altura_vao) - MALEIRO_ABAIXO_TOPO)
    return 0.0


def faixa(altura_vao, espessura):
    """Limites da posição vertical: do piso do vão até o topo menos a espessura do interno."""
    return 0.0, max(0.0, float(altura_vao) - float(espessura))


def _limitar(altura, altura_vao, espessura):
    baixo, alto = faixa(altura_vao, espessura)
    return min(max(float(altura), baixo), alto)


def inserir(internos, vao, tipo, altura_vao, espessura, altura=None, uid=None):
    """(lista nova, interno criado). Sem `altura`, usa a posição inicial do tipo, sempre dentro da faixa."""
    if tipo not in TIPOS:
        raise ValueError(f"Interno desconhecido: {tipo}")
    valor = altura_inicial(tipo, altura_vao) if altura is None else altura
    novo = Interno(uid or uuid4().hex[:8], vao, tipo, _limitar(valor, altura_vao, espessura))
    return list(internos) + [novo], novo


def resolver(internos, altura_vao, espessura):
    """Reposiciona internos na mesma altura: o último vence e os demais sobem 50 mm (idempotente)."""
    baixo, alto = faixa(altura_vao, espessura)
    resultado = [None] * len(internos)
    ocupadas = set()
    for indice in range(len(internos) - 1, -1, -1):
        item = internos[indice]
        altura = min(max(item.altura, baixo), alto)
        chave = round(altura, 3)
        while chave in ocupadas and altura + PASSO_DESEMPATE <= alto + 1e-9:
            altura += PASSO_DESEMPATE
            chave = round(altura, 3)
        ocupadas.add(chave)
        resultado[indice] = replace(item, altura=altura)
    return resultado
