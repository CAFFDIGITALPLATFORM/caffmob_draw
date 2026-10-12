"""Internos do armário: painel p/ eletro, eletros de referência, apoio e respiro (feature 008, T017; RN-13a, D-17).
Python puro, sem `bpy`.

O painel ocupa a frente do vão (largura e altura do vão): **externo** fica no plano da frente, para fora (Y de
−espessura a 0); **embutido** fica recuado pela espessura de uma frente (Y de espessura a 2 × espessura). O recorte tem a medida do eletro (ou dos
eletros empilhados, forno e micro) e fica centrado. O eletro de referência é uma caixa atrás do painel, fora do
corte. O apoio é uma prateleira logo abaixo do recorte.
"""

from dataclasses import dataclass

from . import catalog

MM = 0.001
VENT_SIZE = (0.440, 0.030)


@dataclass(frozen=True)
class Piece:
    box: tuple


@dataclass(frozen=True)
class Layout:
    panel: Piece
    cutout: tuple                  # ((x0, y0, z0), (x1, y1, z1)) ou None
    appliances: tuple              # ((código, Box-tuple), …)


def _space_mm(space):
    return (space.size(0) / MM, space.size(2) / MM, space.size(1) / MM)


def missing(space, item_id):
    """None se o item cabe no vão; senão a medida mínima (mm)."""
    item = catalog.get(item_id)
    return item.too_small(_space_mm(space)) if item is not None else None


def layout(space, item_id, thickness):
    item = catalog.get(item_id)
    (x0, y0, z0), (x1, _y1, z1) = space.lo, space.hi
    built_in = item.filter == 'BUILT_IN'
    py0, py1 = (y0 + thickness, y0 + 2 * thickness) if built_in else (y0 - thickness, y0)
    panel = Piece(((x0, py0, z0), (x1, py1, z1)))
    codes = item.param('appliances') or ()
    cutout, appliances = None, []
    cx, cz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    if codes or item.id == 'VENT':
        if item.id == 'VENT':
            w, h = VENT_SIZE
        else:
            w = max(catalog.APPLIANCE_SIZE_MM[c][0] for c in codes) * MM
            h = sum(catalog.APPLIANCE_SIZE_MM[c][1] for c in codes) * MM
        cutout = ((cx - w / 2.0, py0, cz - h / 2.0), (cx + w / 2.0, py1, cz + h / 2.0))
        bottom = cz - h / 2.0
        for code in codes:                               # de baixo para cima na ordem da tupla: forno embaixo (F-12)
            aw, ah, ad = (v * MM for v in catalog.APPLIANCE_SIZE_MM[code])
            appliances.append((code, ((cx - aw / 2.0, py1, bottom), (cx + aw / 2.0, py1 + ad, bottom + ah))))
            bottom += ah
    elif item.id in catalog.APPLIANCE_SIZE_MM:           # eletro solto, sem painel
        aw, ah, ad = (v * MM for v in catalog.APPLIANCE_SIZE_MM[item.id])
        appliances.append((item.id, ((cx - aw / 2.0, y0, z0), (cx + aw / 2.0, y0 + ad, z0 + ah))))
        panel = None
    return Layout(panel, cutout, tuple(appliances))


def support_offset(space, lay, thickness):
    """Posição (a partir da face de baixo do vão) da prateleira de apoio logo abaixo do recorte."""
    if lay.cutout is None:
        return 0.0
    return max(0.0, lay.cutout[0][2] - space.lo[2] - thickness)
