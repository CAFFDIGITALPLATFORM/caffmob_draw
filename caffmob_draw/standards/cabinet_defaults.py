"""Medidas de um armário CAFFMob pelo Padrão de Dimensões (feature 012, T017; D-07, RN-06, RN-07). Python puro.

`defaults(values, line, cabinet_type)` lê os valores do padrão (chave → mm, como `api.definition_values`) e devolve,
em metros:
- largura padrão do tipo (o padrão não tem largura de módulo: vem de `FALLBACK`);
- altura, profundidade e Z de instalação pelas medidas externas da linha (balcão, aéreo, torre);
- espessura por papel da caixa (`structure.ROLE_COMPONENT`) pelas chapas da linha.

Sem padrão, ou com uma linha que o padrão não tem, usa `FALLBACK` (valores nomeados, num lugar só; princípio III) e
devolve o aviso.
"""

from collections import namedtuple

from ..cabinet_editor.structure import ROLE_COMPONENT
from ..data.i18n import tr

Defaults = namedtuple('Defaults', 'width height depth z thickness carcass warning')

LINES = ('COZ', 'DOR', 'BAN', 'SAL', 'ESC')
# tipo → (largura, altura, profundidade, Z) em metros, usados só sem padrão
FALLBACK = {
    'BASE': (0.8, 0.72, 0.55, 0.0),
    'WALL': (0.8, 0.70, 0.35, 1.5),
    'TALL': (0.6, 2.2, 0.55, 0.0),
}
FALLBACK_SHEET = 0.018
FALLBACK_BACK = 0.006
EXTERNAL = {          # tipo → (altura, profundidade, Z) nas medidas externas da linha
    'BASE': ('base_height', 'base_depth', None),
    'WALL': ('upper_mid_height', 'upper_depth', 'install_height_upper'),
    'TALL': ('tall_height', 'tall_depth', None),
}


def _fallback(cabinet_type, warning):
    width, height, depth, z = FALLBACK.get(cabinet_type, FALLBACK['BASE'])
    thickness = {role: (FALLBACK_BACK if role == 'BACK' else FALLBACK_SHEET) for role in ROLE_COMPONENT}
    return Defaults(width, height, depth, z, thickness, FALLBACK_SHEET, warning)


def defaults(values, line, cabinet_type):
    cabinet_type = cabinet_type if cabinet_type in EXTERNAL else 'BASE'
    if not values:
        return _fallback(cabinet_type, tr("Sem Padrão de Dimensões ativo: medidas de fábrica"))
    if line not in LINES or f"{line}.external.base_height" not in values:
        return _fallback(cabinet_type, tr("O padrão não tem a linha {}: medidas de fábrica").format(line))

    def meters(key, default):
        try:
            return float(values[key]) / 1000.0
        except (KeyError, TypeError, ValueError):
            return default

    width, height, depth, z = FALLBACK[cabinet_type]
    h_key, d_key, z_key = EXTERNAL[cabinet_type]
    height = meters(f"{line}.external.{h_key}", height)
    depth = meters(f"{line}.external.{d_key}", depth)
    z = meters(f"{line}.external.{z_key}", z) if z_key else 0.0
    thickness = {}
    for role, component in ROLE_COMPONENT.items():
        fallback = FALLBACK_BACK if role == 'BACK' else FALLBACK_SHEET
        thickness[role] = meters(f"{line}.sheets.{component}.thickness", fallback)
    return Defaults(width, height, depth, z, thickness, thickness['LEFT'], None)
