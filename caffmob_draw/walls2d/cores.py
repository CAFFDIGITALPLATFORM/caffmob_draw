"""Cor de cada tipo de parede no editor (BUG-20261117-AKYJ).

O NORMAL mantém o cinza que o editor já usa em `ops_editor.COLORS['wall']`. DIVISORIA e MURETA ganham cores próprias,
escolhidas pelo titular em 2026-11-17 como subconjunto do padrão CTB da prancha impressa: azul para a estrutura leve e
amarelo para a meia-altura. No tema claro (BUG-20261117-6OXN) as três ganham variantes escuras, legíveis sobre branco.
Python puro, para as cores serem provadas sem o Blender.
"""

CINZA = (0.85, 0.85, 0.88, 1.0)
AZUL_DIVISORIA = (0.36, 0.62, 0.98, 1.0)
AMARELO_MURETA = (0.95, 0.78, 0.28, 1.0)

CINZA_CLARO = (0.18, 0.18, 0.20, 1.0)
AZUL_CLARO = (0.05, 0.30, 0.75, 1.0)
AMARELO_CLARO = (0.60, 0.40, 0.0, 1.0)

POR_TIPO = {'NORMAL': CINZA, 'DIVISORIA': AZUL_DIVISORIA, 'MURETA': AMARELO_MURETA}
POR_TIPO_CLARO = {'NORMAL': CINZA_CLARO, 'DIVISORIA': AZUL_CLARO, 'MURETA': AMARELO_CLARO}


def cor(wall_type, claro=False):
    """Cor RGBA do tipo de parede; um tipo desconhecido cai no cinza do NORMAL. `claro` usa as variantes do tema claro."""
    if claro:
        return POR_TIPO_CLARO.get(wall_type, CINZA_CLARO)
    return POR_TIPO.get(wall_type, CINZA)
