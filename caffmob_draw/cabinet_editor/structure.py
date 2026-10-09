"""Componentes externos do armário e os modos de remoção (feature 006, T010; RN-03 a RN-07, D-07 a D-09).
Python puro, sem `bpy`.

Papéis: tampo (`TOP`), base (`BOTTOM`), fundo (`BACK`), lateral esquerda (`LEFT`) e lateral direita (`RIGHT`).

Modos de remoção (RN-06):
- `KEEP` (Manter tudo, padrão): a chapa sai; medidas, demais chapas e vão interno ficam onde estão.
- `EXTEND` (Estender as vizinhas): as vizinhas avançam até a borda; o vão interno cresce pela espessura retirada.
- `SHRINK` (Reduzir o armário): as medidas externas diminuem pela espessura; o vão interno fica igual. É o `EXTEND`
  com a medida externa reduzida e a raiz deslocada para as outras chapas não saírem do lugar.

`layout` monta a caixa do módulo `btm` (malha gerada por código) no referencial dele: X centrado na largura, Y de
−profundidade (frente) a 0 (trás), Z de 0 a altura.

Códigos: `STR-001` modo que a biblioteca não faz (aviso, cai em `KEEP`); `STR-002` espessura fora da faixa (erro).
"""

from dataclasses import dataclass

from ..data import units
from ..data.i18n import N_, tr
from .validate import ERROR, WARNING, Message

ROLES = ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT')
ROLE_LABELS = {'TOP': N_("Tampo"), 'BOTTOM': N_("Base"), 'BACK': N_("Fundo"), 'LEFT': N_("Lateral esquerda"),
               'RIGHT': N_("Lateral direita")}
KEEP, EXTEND, SHRINK = 'KEEP', 'EXTEND', 'SHRINK'
MODES = (KEEP, EXTEND, SHRINK)
MODE_LABELS = {KEEP: N_("Manter tudo"), EXTEND: N_("Estender as vizinhas"), SHRINK: N_("Reduzir o armário")}
THICKNESS_RANGE = (0.003, 0.06)     # m: a faixa da espessura no Configurador (3 a 60 mm)

# Componente do Configurador de Dimensões de cada papel (o tampo da caixa sai como "Base superior" na produção,
# como já faz o legado: `cutting/part_roles.py` e `cutting/part_sources.synthetic_records`).
ROLE_COMPONENT = {'TOP': 'BAS', 'BOTTOM': 'BAS', 'LEFT': 'LAT', 'RIGHT': 'LAT', 'BACK': 'FUN_INF'}


@dataclass(frozen=True)
class RoleState:
    removed: bool = False
    mode: str = KEEP
    thickness: float = 0.0      # 0 = segue o Configurador / a biblioteca
    material: str = ""          # "" = segue o Configurador

    @property
    def changed(self):
        return bool(self.thickness or self.material)


def state_from_dict(data):
    return {role: RoleState(bool(v.get("removed", False)), v.get("mode", KEEP) or KEEP,
                            float(v.get("thickness", 0.0) or 0.0), str(v.get("material", "") or ""))
            for role, v in (data or {}).items() if role in ROLES}


def state_to_dict(states):
    return {role: {"removed": s.removed, "mode": s.mode, "thickness": s.thickness, "material": s.material}
            for role, s in sorted(states.items()) if s != RoleState()}


def allowed_mode(mode, caps):
    """(modo efetivo, mensagem ou None). `caps` = {modo: None (pode) ou motivo}."""
    if caps.get(mode, tr("Modo desconhecido")) is None:
        return mode, None
    return KEEP, caps.get(mode)


def check_thickness(role, value, unit='MM'):
    lo, hi = THICKNESS_RANGE
    if value == 0.0 or lo - 1e-9 <= value <= hi + 1e-9:
        return []
    span = "{} – {}".format(units.format_length(lo, unit), units.format_length(hi, unit))
    return [Message('STR-002', ERROR, tr(ROLE_LABELS[role]), 'thickness', units.format_length(value, unit), span,
                    tr("Use uma espessura dentro da faixa"))]


def unsupported_mode(role, mode, reason):
    return Message('STR-001', WARNING, tr(ROLE_LABELS[role]), 'mode', tr(MODE_LABELS.get(mode, mode)), '', reason)


# Módulo `btm` ------------------------------------------------------------------------------------------------
def _neighbor_thickness(role, thick, states):
    """Espessura que as vizinhas e o vão respeitam: 0 quando a chapa saiu em EXTEND/SHRINK."""
    state = states.get(role, RoleState())
    if state.removed and state.mode in (EXTEND, SHRINK):
        return 0.0
    return thick[role]


LATERAL, BASE = 'LATERAL', 'BASE'          # montagem (feature 012, D-09)


def layout(width, height, depth, thick, states, back_setback=0.0, assembly=LATERAL):
    """(chapas {papel: (lo, hi)} só das presentes, vão interno (lo, hi)) do módulo `btm`.

    `back_setback` (feature 008, D-11): fundo "Inteiro Recuado"; o fundo anda para dentro e o vão termina nele.
    `assembly` (feature 012, D-09): `LATERAL` (laterais do piso ao topo, base e tampo entre elas) ou `BASE` (a base
    ocupa a largura toda e as laterais ficam em cima dela; o tampo continua entre as laterais).
    """
    w2 = width / 2.0
    t = {role: _neighbor_thickness(role, thick, states) for role in ROLES}
    x0, x1 = -w2 + t['LEFT'], w2 - t['RIGHT']
    z0, z1 = t['BOTTOM'], height - t['TOP']
    side_z = t['BOTTOM'] if assembly == BASE else 0.0
    bottom_x = (-w2, w2) if assembly == BASE else (x0, x1)
    boxes = {
        'LEFT': ((-w2, -depth, side_z), (-w2 + thick['LEFT'], 0.0, height)),
        'RIGHT': ((w2 - thick['RIGHT'], -depth, side_z), (w2, 0.0, height)),
        'BOTTOM': ((bottom_x[0], -depth, 0.0), (bottom_x[1], 0.0, thick['BOTTOM'])),
        'TOP': ((x0, -depth, height - thick['TOP']), (x1, 0.0, height)),
        'BACK': ((x0, -thick['BACK'] - back_setback, z0), (x1, -back_setback, z1)),
    }
    present = {role: box for role, box in boxes.items() if not states.get(role, RoleState()).removed}
    inner = ((x0, -depth, z0), (x1, -t['BACK'] - (back_setback if t['BACK'] > 0.0 else 0.0), z1))
    return present, inner


def carcass_lengths(width, height, left, right, bottom, assembly=LATERAL):
    """Comprimento de cada chapa da caixa pela montagem (mesma unidade da entrada; feature 012, D-09).

    `left`, `right`, `bottom` = espessura que as vizinhas respeitam (0 quando a chapa saiu em EXTEND/SHRINK).
    Laterais e base no sentido da altura e da largura; o tampo fica sempre entre as laterais.
    """
    inner = width - left - right
    if assembly == BASE:
        return {'LEFT': height - bottom, 'RIGHT': height - bottom, 'BOTTOM': width, 'TOP': inner}
    return {'LEFT': height, 'RIGHT': height, 'BOTTOM': inner, 'TOP': inner}


def shrink_change(role, thickness):
    """Ajuste da raiz ao remover (`sign`=+1) ou restaurar (−1) em SHRINK: ({medida: delta}, deslocamento local).

    As chapas que ficam não saem do lugar: o módulo `btm` é centrado em X e começa em Z = 0, então reduzir a largura
    ou a altura pede deslocar a raiz; reduzir a profundidade mantém a frente e puxa o fundo.
    """
    if role == 'LEFT':
        return {'width': -thickness}, (thickness / 2.0, 0.0, 0.0)
    if role == 'RIGHT':
        return {'width': -thickness}, (-thickness / 2.0, 0.0, 0.0)
    if role == 'BOTTOM':
        return {'height': -thickness}, (0.0, 0.0, thickness)
    if role == 'TOP':
        return {'height': -thickness}, (0.0, 0.0, 0.0)
    return {'depth': -thickness}, (0.0, -thickness, 0.0)
