"""Gaveteiro novo (072 RN-12, D-22), sem bpy: as medidas da caixaria pelos dois métodos do guia do titular.

- Lateral passante: base e tampo entre as laterais; largura deles = largura total − 2 × lateral.
- Base passante: base e tampo na largura total; laterais com altura total − base − tampo.
Os tipos do guia §1 sugerem as espessuras (fixo 18, volante 18 com tampo 25 e rodízios, suspenso 18, oculto 18 com
frente de 15). Medidas em mm.
"""
from dataclasses import dataclass

METODOS = ('LATERAL', 'BASE')
TIPOS = {
    'fixo': dict(lateral=18, base=18, tampo=18, rodizios=False, frente=18),
    'volante': dict(lateral=18, base=18, tampo=25, rodizios=True, frente=18),
    'suspenso': dict(lateral=18, base=18, tampo=18, rodizios=False, frente=18),
    'oculto': dict(lateral=18, base=18, tampo=18, rodizios=False, frente=15),
}


@dataclass
class Gaveteiro:
    largura: float = 450
    altura: float = 600
    profundidade: float = 500
    metodo: str = 'BASE'
    tipo: str = 'volante'
    gavetas: int = 3

    def espessuras(self):
        return TIPOS.get(self.tipo, TIPOS['fixo'])


def pecas(g):
    """Laterais, base e tampo: {papel: (largura, altura ou profundidade, espessura)} em mm."""
    e = g.espessuras()
    if g.metodo == 'LATERAL':
        interna = g.largura - 2 * e['lateral']
        return dict(lateral=(g.profundidade, g.altura, e['lateral']), base=(interna, g.profundidade, e['base']),
                    tampo=(interna, g.profundidade, e['tampo']))
    return dict(lateral=(g.profundidade, g.altura - e['base'] - e['tampo'], e['lateral']),
                base=(g.largura, g.profundidade, e['base']), tampo=(g.largura, g.profundidade, e['tampo']))


def vao(g):
    """Espaço livre das gavetas dentro da caixaria (largura, altura) em mm."""
    e = g.espessuras()
    return g.largura - 2 * e['lateral'], g.altura - e['base'] - e['tampo']
