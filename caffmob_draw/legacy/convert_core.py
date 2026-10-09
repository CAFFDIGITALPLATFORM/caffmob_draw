"""Tradução de um armário herdado para o módulo CAFFMob (feature 012, T058; D-24, RN-13). Python puro.

Entrada: `LegacyCabinet`, montado pelo `legacy/convert.py` com as medidas (`selection/editing.get_dimension`), o
tipo e a especificação lida pelo adaptador da biblioteca (`customize/adapters/<lib>.read`). Saída: os campos do
`btm_cabinet` e a lista de perdas.

O módulo CAFFMob tem uma frente só (nenhuma, porta à esquerda, à direita, duas portas ou basculante) e prateleiras;
não tem gavetas (feature 013). Tudo o que ele não representa vira perda, com a quantidade.
"""

from collections import namedtuple
from dataclasses import dataclass, field

from ..data.i18n import N_

LegacyOpening = namedtuple('LegacyOpening', 'front drawer_count shelves', defaults=(0, 0))
Loss = namedtuple('Loss', 'key count')


@dataclass
class LegacyCabinet:
    library: str
    cabinet_type: str
    width: float
    height: float
    depth: float
    line: str = ""
    openings: list = field(default_factory=list)
    shelves: int = 0
    other_fronts: list = field(default_factory=list)    # frentes sem equivalente lidas fora da especificação


LINES = ('COZ', 'DOR', 'BAN', 'SAL', 'ESC')
TALL_FROM = 1.2          # m: tipos sem equivalente viram torre a partir desta altura

TYPE_APPROX, DRAWERS, PANEL, SPECIAL_FRONT, EXTRA_DOORS = 'TYPE_APPROX', 'DRAWERS', 'PANEL', 'SPECIAL', 'EXTRA_DOORS'
LOSS_LABELS = {
    TYPE_APPROX: N_("Tipo de armário aproximado"),
    DRAWERS: N_("Gavetas"),
    PANEL: N_("Painéis fixos"),
    SPECIAL_FRONT: N_("Frentes especiais (basculante de puxar, painel embutido, eletrodoméstico)"),
    EXTRA_DOORS: N_("Portas além de duas"),
}
_TYPES = {'BASE': 'BASE', 'UPPER': 'WALL', 'WALL': 'WALL', 'TALL': 'TALL'}
_DOORS = {'DOOR_LEFT': 1, 'DOOR_RIGHT': 1, 'DOUBLE_DOORS': 2}


def _type(cabinet):
    mapped = _TYPES.get((cabinet.cabinet_type or "").upper())
    if mapped:
        return mapped, False
    return ('TALL' if cabinet.height >= TALL_FROM else 'BASE'), True


def _line(cabinet):
    if cabinet.line in LINES:
        return cabinet.line
    return 'DOR' if cabinet.library == 'CLOSETS' else 'COZ'


def translate(cabinet):
    """(campos do `btm_cabinet`, perdas)."""
    losses = {}

    def lose(key, count=1):
        if count > 0:
            losses[key] = losses.get(key, 0) + count

    cabinet_type, approx = _type(cabinet)
    if approx:
        lose(TYPE_APPROX)
    doors, sides, flip = 0, [], False
    shelves = int(cabinet.shelves or 0)
    for opening in cabinet.openings:
        shelves += int(opening.shelves or 0)
        front = opening.front
        if front in _DOORS:
            doors += _DOORS[front]
            sides.append(front)
        elif front == 'FLIP_UP':
            flip = True
        elif front == 'DRAWERS':
            lose(DRAWERS, max(1, int(opening.drawer_count or 0)))
        elif front == 'PANEL':
            lose(PANEL)
        elif front not in ('OPEN', '', None):
            lose(SPECIAL_FRONT)
    for _front in cabinet.other_fronts:
        lose(SPECIAL_FRONT)
    if doors >= 2:
        swing = 'DOUBLE'
        lose(EXTRA_DOORS, doors - 2)
    elif doors == 1:
        swing = 'LEFT' if sides[0] == 'DOOR_LEFT' else 'RIGHT'
    else:
        swing = 'FLIP' if flip else 'NONE'
    if flip and doors:
        lose(SPECIAL_FRONT)
    fields = {
        'cabinet_type': cabinet_type, 'width': cabinet.width, 'height': cabinet.height, 'depth': cabinet.depth,
        'door_swing': swing, 'shelves': shelves, 'line': _line(cabinet), 'assembly': 'LATERAL',
    }
    return fields, [Loss(key, count) for key, count in losses.items()]
