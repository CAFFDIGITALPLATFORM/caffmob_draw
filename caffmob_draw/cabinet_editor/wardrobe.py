"""Internos de roupeiro (feature 015, T023; RN-16, D-14). Python puro, sem `bpy`.

A partir do subvão escolhido (no referencial da raiz: X largura, Y profundidade com a frente no menor Y, Z altura),
devolve as peças do item da aba Internos › Cabideiros e Calceiros, no formato de `extras.Piece`:

- Cabideiro e tubo (`HANGER_ROD`): tubo de 25 mm a `rod_drop` abaixo do topo do subvão (a prateleira de cima), no
  meio da profundidade, na largura do vão menos a folga dos suportes. Ferragem `TUBO_CABIDEIRO`.
- Calceiro (`PANTS_RACK`): quadro de largura do vão, logo abaixo do topo do subvão. De madeira é chapa (`ESP`); o
  aramado é ferragem (`CALCEIRO_ARAMADO`). O lado (esquerdo, central, direito) só muda o nome.
- Sapateira (`SHOE_RACK`): chapa (`ESP`) no fundo do subvão; a inclinação não é modelada (🟡).
- Porta-cintos (`BELT_RACK`): ferragem (`PORTA_CINTOS`) presa na lateral esquerda do subvão.

Subvão menor que o item recusa a inserção com a medida mínima (`too_small`).
"""

from .extras import Piece

ROD_DIAMETER = 0.025
ROD_CLEARANCE = 0.002          # folga de cada lado, para os suportes
RACK_HEIGHT = 0.10             # altura do quadro do calceiro
RACK_SETBACK = 0.05            # recuo da frente do calceiro e da sapateira
SHEET = 0.018                  # espessura de reserva da chapa do calceiro e da sapateira
BELT_SIZE = (0.03, 0.40, 0.08)
MIN_SIZE = {'HANGER_ROD': (0.20, 0.0, 0.0), 'PANTS_RACK': (0.30, 0.0, 0.0), 'SHOE_RACK': (0.30, 0.0, 0.0),
            'BELT_RACK': (0.0, 0.0, 0.40)}


def too_small(kind, space):
    """None se o item cabe no subvão; senão a medida mínima (largura, altura, profundidade) em m."""
    (x0, y0, z0), (x1, y1, z1) = space
    need = MIN_SIZE.get(kind, (0.0, 0.0, 0.0))
    if x1 - x0 + 1e-9 >= need[0] and z1 - z0 + 1e-9 >= need[1] and y1 - y0 + 1e-9 >= need[2]:
        return None
    return need


def layout(kind, space, *, rod_drop=0.07, material='WOOD', sheet=SHEET):
    """[Piece] do item `kind` no subvão `space`."""
    (x0, y0, z0), (x1, y1, z1) = space
    if kind == 'HANGER_ROD':
        r = ROD_DIAMETER / 2.0
        cy = (y0 + y1) / 2.0
        cz = max(z0 + r, z1 - rod_drop)
        return [Piece('HANGER_ROD', ((x0 + ROD_CLEARANCE, cy - r, cz - r), (x1 - ROD_CLEARANCE, cy + r, cz + r)),
                      hardware='TUBO_CABIDEIRO')]
    if kind == 'PANTS_RACK':
        box = ((x0, y0 + RACK_SETBACK, z1 - RACK_HEIGHT), (x1, y1, z1))
        if material == 'WIRE':
            return [Piece('PANTS_RACK', box, hardware='CALCEIRO_ARAMADO')]
        return [Piece('PANTS_RACK', ((x0, y0 + RACK_SETBACK, z1 - RACK_HEIGHT), (x1, y1, z1 - RACK_HEIGHT + sheet)),
                      'ESP')]
    if kind == 'SHOE_RACK':
        return [Piece('SHOE_RACK', ((x0, y0 + RACK_SETBACK, z0), (x1, y1, z0 + sheet)), 'ESP')]
    if kind == 'BELT_RACK':
        w, d, h = BELT_SIZE
        cz = (z0 + z1) / 2.0
        return [Piece('BELT_RACK', ((x0, y0 + RACK_SETBACK, cz - h / 2.0), (x0 + w, y0 + RACK_SETBACK + d, cz + h / 2.0)),
                      hardware='PORTA_CINTOS')]
    return []
