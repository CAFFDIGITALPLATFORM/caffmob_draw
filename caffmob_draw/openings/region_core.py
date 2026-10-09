"""Porta e janela na região marcada na parede (feature 011, T007; roadmap D-11, RN-11, RN-12).

`fit(x0, x1, z0, z1, wall_length, wall_height, kind, others)` recebe a região no espaço local da parede (X ao longo
dela, Z a partir do piso; os cantos podem vir em qualquer ordem) e devolve onde fica o vão:

- porta (`DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`): encosta no piso (peitoril 0, R-08) e vai até a borda de cima;
- janela (`WINDOW`): a borda de baixo vira o peitoril.

Largura e altura são exatamente as da região, sem grade e sem folga. A recusa diz o motivo; `others` são as outras
aberturas da parede, como `(x0, x1, z0, z1)`.
"""

from collections import namedtuple

from ..data.i18n import N_

Fit = namedtuple('Fit', 'ok x width height sill reason')

EMPTY, OUTSIDE, TOO_TALL, OVERLAP = 'EMPTY', 'OUTSIDE', 'TOO_TALL', 'OVERLAP'
MIN_SIZE = 0.001        # 1 mm: abaixo disso a região é um clique só
TOLERANCE = 0.005       # 5 mm: clique um pouco fora da parede ou abaixo do piso conta como a borda

REASONS = {
    EMPTY: N_("A região está vazia: clique em dois cantos opostos"),
    OUTSIDE: N_("A região passa da ponta da parede"),
    TOO_TALL: N_("A região é mais alta que a parede"),
    OVERLAP: N_("A região encosta em outra porta ou janela"),
}


def _refuse(reason):
    return Fit(False, 0.0, 0.0, 0.0, 0.0, reason)


def fit(x0, x1, z0, z1, wall_length, wall_height, kind, others=()):
    x0, x1 = min(x0, x1), max(x0, x1)
    z0, z1 = min(z0, z1), max(z0, z1)
    if z0 < 0.0 and z0 > -TOLERANCE:
        z0 = 0.0
    if x1 - x0 < MIN_SIZE or z1 - z0 < MIN_SIZE:
        return _refuse(EMPTY)
    if x0 < -TOLERANCE or x1 > wall_length + TOLERANCE or z0 < 0.0:
        return _refuse(OUTSIDE)
    if z1 > wall_height + TOLERANCE:
        return _refuse(TOO_TALL)
    sill = z0 if kind == 'WINDOW' else 0.0
    for ox0, ox1, oz0, oz1 in others:
        if x0 < ox1 - MIN_SIZE and ox0 < x1 - MIN_SIZE and sill < oz1 - MIN_SIZE and oz0 < z1 - MIN_SIZE:
            return _refuse(OVERLAP)
    return Fit(True, x0, x1 - x0, z1 - sill, sill, '')
