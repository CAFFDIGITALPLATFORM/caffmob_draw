"""Espaço livre em volta de um ponto (072 D-20, D-23, RN-01), sem bpy.

Recebe as caixas das peças (alinhadas aos eixos, no referencial do móvel: x largura, y profundidade com a frente no
menor y, z altura), o envelope do móvel e um ponto dentro do vão. Devolve a caixa livre: entre a peça mais próxima à
esquerda e à direita, embaixo e em cima, e da frente do móvel até a peça mais próxima atrás. Serve ao armário autoral
(066), que não tem vãos que o addon conheça. Medidas na mesma unidade das caixas.
"""
from dataclasses import dataclass

EPS = 1e-6


@dataclass(frozen=True)
class Caixa:
    lo: tuple
    hi: tuple

    def contem(self, p, eps=EPS):
        return all(self.lo[k] - eps <= p[k] <= self.hi[k] + eps for k in range(3))

    def tamanho(self):
        return tuple(self.hi[k] - self.lo[k] for k in range(3))


def _cruza(a0, a1, b0, b1):
    return a0 < b1 - EPS and b0 < a1 - EPS


def livre(caixas, ponto, envelope):
    """Caixa livre em volta de `ponto`, ou None se o ponto está dentro de uma peça ou fora do envelope."""
    if not envelope.contem(ponto) or any(c.contem(ponto, -EPS) for c in caixas):
        return None
    x, y, z = ponto
    na_linha = [c for c in caixas if c.lo[1] - EPS <= y <= c.hi[1] + EPS and c.lo[2] - EPS <= z <= c.hi[2] + EPS]
    esquerda = max([c.hi[0] for c in na_linha if c.hi[0] <= x + EPS] + [envelope.lo[0]])
    direita = min([c.lo[0] for c in na_linha if c.lo[0] >= x - EPS] + [envelope.hi[0]])
    na_coluna = [c for c in caixas if _cruza(c.lo[0], c.hi[0], esquerda, direita) and c.lo[1] - EPS <= y <= c.hi[1] + EPS]
    baixo = max([c.hi[2] for c in na_coluna if c.hi[2] <= z + EPS] + [envelope.lo[2]])
    cima = min([c.lo[2] for c in na_coluna if c.lo[2] >= z - EPS] + [envelope.hi[2]])
    atras = [c for c in caixas if _cruza(c.lo[0], c.hi[0], esquerda, direita) and _cruza(c.lo[2], c.hi[2], baixo, cima)
             and c.lo[1] >= y - EPS]
    fundo = min([c.lo[1] for c in atras] + [envelope.hi[1]])
    return Caixa((esquerda, envelope.lo[1], baixo), (direita, fundo, cima))


def envelope_de(caixas):
    return Caixa(tuple(min(c.lo[k] for c in caixas) for k in range(3)),
                 tuple(max(c.hi[k] for c in caixas) for k in range(3)))
