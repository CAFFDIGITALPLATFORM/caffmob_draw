"""Seleção de várias paredes no editor do projeto do addon (067 onda 8, T194; D-39, D-40; RF-162, RF-163).

Sem Blender: a seleção é uma lista ordenada de `(cadeia, trecho)`, e o polígono de cada trecho são as faces interna e
externa de `model.Chain`, em metros do mundo 2D. O retângulo reaproveita a geometria do Studio
(`studio_selecao.poligono_no_retangulo`).
"""
from .studio_selecao import poligono_no_retangulo

MULTIPLOS = object()          # sentinela: os trechos selecionados têm valores diferentes
CAMPOS_DO_LOTE = ('thickness', 'height', 'end_height', 'wall_type')


def todos(plan):
    return [(ci, si) for ci, chain in enumerate(plan.chains) for si in range(chain.segment_count())]


def validos(plan, selecao):
    """Descarta os trechos que não existem mais (desfazer, remoção), conservando a ordem."""
    existentes = set(todos(plan))
    return [t for t in dict.fromkeys(selecao) if t in existentes]


def alternar(selecao, trecho):
    return [t for t in selecao if t != trecho] if trecho in selecao else [*selecao, trecho]


def poligono(chain, i):
    return [*chain.inner_line(i), *reversed(chain.outer_line(i))]


def no_retangulo(plan, a, b, toca=True):
    """Trechos que o retângulo `a`–`b` (cantos em metros) toca, ou contém inteiros com `toca=False`."""
    return [(ci, si) for ci, si in todos(plan)
            if poligono_no_retangulo([tuple(p) for p in poligono(plan.chains[ci], si)], a, b, toca)]


def valor_comum(plan, selecao, campo):
    valores = {getattr(plan.chains[ci].segments[si], campo) for ci, si in selecao}
    valores = {round(v, 6) if isinstance(v, float) else v for v in valores}
    if len(valores) != 1:
        return MULTIPLOS
    return next(iter(valores))


def aplicar(plan, selecao, campo, valor):
    """Grava `campo` em todos os trechos; um valor recusado pelo modelo não muda nenhum (ValueError)."""
    if campo not in CAMPOS_DO_LOTE:
        raise ValueError(campo)
    antes = [(plan.chains[ci].segments[si], dict(vars(plan.chains[ci].segments[si]))) for ci, si in selecao]
    try:
        for ci, si in selecao:
            plan.chains[ci].set_segment_value(si, campo, valor)
    except ValueError:
        for segmento, valores in antes:
            vars(segmento).update(valores)
        raise
