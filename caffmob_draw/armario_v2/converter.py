"""Conversão de peças soltas em armário v2, peça por peça (feature 020; RN-01 a RN-03).

Python puro, em milímetros: recebe as caixas de mundo das peças que o usuário apontou e devolve as medidas e as flags
de presença do `spec.Spec`. A conversão **não gera** nada: as peças de origem ficam preservadas (ocultas e fora do
corte) e o armário nasce com o spec gravado, para o usuário abrir o construtor e só gerar quando quiser — é o que
evita a peça que "muda de posição" ao converter (RN-02).

Papéis: as quatro chapas da caixa (`lateral_esq`, `lateral_dir`, `base_inf`, `base_sup`), o `fundo` e a `porta`. Papel
não apontado é peça inexistente, com a mesma flag de presença da 017.
"""

from . import spec as spec_mod

PAPEIS = ('lateral_esq', 'lateral_dir', 'base_inf', 'base_sup', 'fundo', 'porta')

# Papel -> flag de presença do `Spec` (o fundo e a porta usam o nome sem o sufixo `_ativa`).
FLAGS = {
    'lateral_esq': 'lateral_esq_ativa',
    'lateral_dir': 'lateral_dir_ativa',
    'base_inf': 'base_inf_ativa',
    'base_sup': 'base_sup_ativa',
    'fundo': 'fundo_ativo',
    'porta': 'porta_ativa',
}

# Papel -> campo de espessura do `Spec`.
ESPESSURA_DO_PAPEL = {
    'lateral_esq': 'espessura_lateral',
    'lateral_dir': 'espessura_lateral',
    'base_inf': 'espessura_base_inferior',
    'base_sup': 'espessura_base_superior',
    'fundo': 'espessura_fundo',
    'porta': 'espessura_porta',
}


def limites(caixas):
    """Caixa que envolve todas as caixas recebidas: `((x0, y0, z0), (x1, y1, z1))`, ou `None` sem nenhuma."""
    caixas = [caixa for caixa in caixas if caixa is not None]
    if not caixas:
        return None
    minimo = tuple(min(caixa[0][i] for caixa in caixas) for i in range(3))
    maximo = tuple(max(caixa[1][i] for caixa in caixas) for i in range(3))
    return minimo, maximo


def espessura_da_caixa(caixa):
    """Espessura da peça: o menor dos três lados da caixa, em milímetros."""
    (x0, y0, z0), (x1, y1, z1) = caixa
    return min(x1 - x0, y1 - y0, z1 - z0)


def mm_no_enum(valor):
    """Espessura encaixada num dos itens do contrato de chapas (6, 15, 18 ou 25 mm)."""
    return float(min(spec_mod.THICKNESSES, key=lambda item: abs(item - float(valor))))


def spec_das_pecas(caixas):
    """Campos do `Spec` a partir de `{papel: caixa}`; a porta fica de fora das medidas externas.

    A largura, a altura e a profundidade saem da caixa que envolve as peças estruturais (sem a porta, que fica à
    frente do armário e inflaria a profundidade). Sem nenhuma peça estrutural, a porta vira a referência.
    """
    estruturais = [caixas[papel] for papel in PAPEIS if papel != 'porta' and caixas.get(papel) is not None]
    if not estruturais:
        estruturais = [caixa for caixa in caixas.values() if caixa is not None]
    limite = limites(estruturais)
    if limite is None:
        return None
    (x0, y0, z0), (x1, y1, z1) = limite
    campos = {'largura': round(x1 - x0, 1), 'altura': round(z1 - z0, 1), 'profundidade': round(y1 - y0, 1)}
    for papel, flag in FLAGS.items():
        campos[flag] = caixas.get(papel) is not None
    for papel, campo in ESPESSURA_DO_PAPEL.items():
        caixa = caixas.get(papel)
        if caixa is not None:
            campos[campo] = mm_no_enum(espessura_da_caixa(caixa))
    if campos['porta_ativa']:
        campos['porta_folhas'] = 1
        campos['porta_dobradica'] = 'ESQUERDA'
    return campos
