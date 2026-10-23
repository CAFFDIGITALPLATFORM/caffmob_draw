"""Regras da janela "Encostar" do Mover Sobre (BUG-20261022-RQR5). Python puro, sem `bpy`.

Mesmas regras do diálogo "Encostar" do artefato (`openSnap`, `snapTarget`, `snapCandidates`, `derivedSide`),
traduzidas para o referencial de B usado pelo Mover Sobre, em metros:
- X: largura; Y: profundidade, com a **frente em Y mínimo** e o fundo em Y máximo; Z: altura.

Caixas são `((xmin, ymin, zmin), (xmax, ymax, zmax))`. A posição é sempre o canto mínimo de A.
"""

from ..data.i18n import N_

LEFT, RIGHT, TOP, BOTTOM, BACK, FRONT = 'LEFT', 'RIGHT', 'TOP', 'BOTTOM', 'BACK', 'FRONT'
SIDES = (LEFT, RIGHT, TOP, BOTTOM, BACK, FRONT)
SIDE_LABELS = {LEFT: N_("À esquerda"), RIGHT: N_("À direita"), TOP: N_("Em cima"), BOTTOM: N_("Embaixo"),
               BACK: N_("Atrás"), FRONT: N_("Na frente")}
SIDE_PHRASES = {LEFT: N_("à esquerda de"), RIGHT: N_("à direita de"), TOP: N_("em cima de"),
                BOTTOM: N_("embaixo de"), BACK: N_("atrás de"), FRONT: N_("na frente de")}
SIDE_AXIS = {LEFT: 0, RIGHT: 0, TOP: 2, BOTTOM: 2, BACK: 1, FRONT: 1}
SIDE_FACE = {LEFT: 'NEG_X', RIGHT: 'POS_X', TOP: 'POS_Z', BOTTOM: 'NEG_Z', BACK: 'POS_Y', FRONT: 'NEG_Y'}

WIDTH, DEPTH, HEIGHT = 0, 1, 2
KEEP = 'KEEP'
ALIGN_TITLES = {WIDTH: N_("Alinhar na largura"), HEIGHT: N_("Alinhar na altura"), DEPTH: N_("Alinhar na profund.")}
ALIGN_OPTIONS = {
    WIDTH: (('LEFT', N_("Pela esquerda")), ('RIGHT', N_("Pela direita")), ('CENTER', N_("Centralizado")),
            (KEEP, N_("Manter"))),
    HEIGHT: (('BASE', N_("Pela base")), ('TOP', N_("Pelo topo")), (KEEP, N_("Manter"))),
    DEPTH: (('BACK', N_("Pelo fundo")), ('FRONT', N_("Pela frente")), (KEEP, N_("Manter"))),
}
ALIGN_ORDER = (WIDTH, HEIGHT, DEPTH)        # ordem em que a janela mostra os alinhamentos

MAX_GAP = 5.0                               # m (5000 mm, como no artefato)
SNAP_PX = 8.0                               # alcance do ímã, em pixels da vista


def size(box):
    return tuple(box[1][i] - box[0][i] for i in range(3))


def align_axes(side):
    """Eixos que a janela deixa alinhar para o lado: os dois que não são o eixo do lado."""
    return tuple(i for i in range(3) if i != SIDE_AXIS[side])


def default_align(side):
    """Como o artefato ao escolher um lado: pela esquerda, pela base e pelo fundo nos eixos livres."""
    axis = SIDE_AXIS[side]
    return {WIDTH: 'LEFT' if axis != WIDTH else KEEP,
            DEPTH: 'BACK' if axis != DEPTH else KEEP,
            HEIGHT: 'BASE' if axis != HEIGHT else KEEP}


def initial_side(box_a, box_b):
    """Lado em que A já está: o eixo de maior afastamento entre os centros, relativo ao tamanho de B."""
    sep = [((box_a[0][i] + box_a[1][i]) - (box_b[0][i] + box_b[1][i])) / max(1e-6, box_b[1][i] - box_b[0][i])
           for i in range(3)]
    axis = max((WIDTH, HEIGHT, DEPTH), key=lambda i: abs(sep[i]))
    if axis == WIDTH:
        return LEFT if sep[0] < 0 else RIGHT
    if axis == HEIGHT:
        return BOTTOM if sep[2] < 0 else TOP
    return FRONT if sep[1] < 0 else BACK


def target_min(box_a, box_b, side, gap, align, base=None):
    """Canto mínimo de A depois de encostar no `side` de B com `gap` e os alinhamentos `align` (eixo → opção).

    `base` é o canto mínimo de partida (a posição arrastada); sem lado (`side` None), A fica nela."""
    w, d, h = size(box_a)
    (bx0, by0, bz0), (bx1, by1, bz1) = box_b
    x, y, z = base if base is not None else box_a[0]
    if side is None:
        return (x, y, z)
    if side == LEFT:
        x = bx0 - gap - w
    elif side == RIGHT:
        x = bx1 + gap
    elif side == TOP:
        z = bz1 + gap
    elif side == BOTTOM:
        z = bz0 - gap - h
    elif side == BACK:
        y = by1 + gap
    elif side == FRONT:
        y = by0 - gap - d
    axis = SIDE_AXIS[side]
    if axis != WIDTH:
        x = {'LEFT': bx0, 'RIGHT': bx1 - w, 'CENTER': (bx0 + bx1 - w) / 2.0}.get(align.get(WIDTH), x)
    if axis != HEIGHT:
        z = {'BASE': bz0, 'TOP': bz1 - h}.get(align.get(HEIGHT), z)
    if axis != DEPTH:
        y = {'BACK': by1 - d, 'FRONT': by0}.get(align.get(DEPTH), y)
    return (x, y, z)


def gaps(box_n, box_b):
    """Folga de A até B em cada eixo; negativa quando sobrepõe."""
    return tuple(max(box_b[0][i] - box_n[1][i], box_n[0][i] - box_b[1][i]) for i in range(3))


def derived_side(box_n, box_b):
    """Lado de uma posição livre (arrastada): o eixo de maior folga e o sentido do centro."""
    g = gaps(box_n, box_b)
    axis = max((WIDTH, HEIGHT, DEPTH), key=lambda i: g[i])
    c = (box_n[0][axis] + box_n[1][axis]) - (box_b[0][axis] + box_b[1][axis])
    if axis == WIDTH:
        return LEFT if c < 0 else RIGHT
    if axis == HEIGHT:
        return BOTTOM if c < 0 else TOP
    return FRONT if c < 0 else BACK


def candidates(axis, length, box_b, gap):
    """Posições do ímã num eixo (canto mínimo de A), com a linha-guia e o rótulo: encostar dos dois lados com o
    afastamento, alinhar as bordas, centralizar e encostar sem afastamento. O rótulo com afastamento tem `{}` para
    os milímetros."""
    b0, b1 = box_b[0][axis], box_b[1][axis]
    touch = N_("encostado")
    with_gap = N_("encostado + {} mm") if gap else touch
    return [
        (b1 + gap, b1, with_gap), (b0 - gap - length, b0, with_gap),
        (b0, b0, N_("alinhado")), (b1 - length, b1, N_("alinhado")),
        ((b0 + b1 - length) / 2.0, (b0 + b1) / 2.0, N_("centralizado")),
        (b1, b1, touch), (b0 - length, b0, touch),
    ]


def snap(value, axis, length, box_b, gap, tolerance):
    """(valor, guia): o candidato mais próximo até `tolerance`; guia = (linha, rótulo), ou None se nada puxou."""
    best = None
    for candidate, edge, label in candidates(axis, length, box_b, gap):
        dist = abs(candidate - value)
        if dist <= tolerance and (best is None or dist < best[0]):
            best = (dist, candidate, edge, label)
    if best is None:
        return value, None
    return best[1], (best[2], best[3])


def side_from_point(view, dh, dv):
    """Lado escolhido por um clique fora de A: `dh`, `dv` = posição relativa ao centro de B, em meias-medidas de B
    (`dv` cresce para cima na tela). Frontal: em cima/embaixo; planta: o fundo fica em cima, a frente embaixo."""
    if abs(dh) >= abs(dv):
        return LEFT if dh < 0 else RIGHT
    if view == 'FRONT':
        return TOP if dv > 0 else BOTTOM
    return BACK if dv > 0 else FRONT
