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


# Estrutura de caixa (feature 015, T015 a T018; RN-01, RN-04 a RN-10, D-02 a D-04, D-09) ----------------------------
#
# `carcass_parts` monta as peças da caixa de um módulo `btm` que tem estrutura (`btm_cabinet.structure_id`) a partir da
# receita do catálogo (`structures_core.Structure`). A malha (`geometry/mesh_gen.py`) e o plano de corte
# (`cutting/part_sources.synthetic_records`) chamam esta função: o 3D e o corte saem da mesma conta.
#
# Sem unidade própria: medidas, espessuras e `params` na mesma unidade (m na malha, mm no corte). Referencial do
# `layout`: X centrado na largura, Y de −profundidade (frente) a 0 (trás), Z de 0 a altura.
#
# Diferenças em relação ao `layout` (que continua valendo para os módulos sem estrutura):
# - papel ausente na receita (balcão sem Base Superior, armário sem lateral) não reserva espaço no vão;
# - rodapé da estrutura: a caixa sobe `toe_kick_height` e a altura total fica igual (RN-05, D-04);
# - "até Piso": as laterais descem ao piso e a base inferior fica entre elas, na altura do rodapé (RN-06);
# - balcão: Sarrafo Frontal e Sarrafo Traseiro no alto em vez da Base Superior (RN-04); Sarrafo Inteiro e Tampo
#   Linear opcionais. O Tampo Linear fica sobre a caixa (a altura do padrão é "sem tampo");
# - fundo pelo tipo do grupo (D-09): ENCAIXADO e REBAIXADO (a mesma caixa; o corte soma `back_allowance` nas duas
#   medidas, como o "+16" de antes; 🟡 a diferença de rebaixo ainda não é modelada), PREGADO (sobre a face traseira,
#   nas medidas externas; as outras chapas encurtam a espessura do fundo) e TRAVESSAS (duas travessas traseiras e o
#   fundo à frente delas).

ENCAIXADO, REBAIXADO, PREGADO, TRAVESSAS = 'ENCAIXADO', 'REBAIXADO', 'PREGADO', 'TRAVESSAS'
HORIZONTAL, VERTICAL = 'HORIZONTAL', 'VERTICAL'
BACK_COMPONENT = {'INFERIOR': 'FUN_INF', 'SUPERIOR': 'FUN_SUP', 'DESPENSEIRO': 'FUN_ALT'}
# Valores de reserva em mm, usados só quando o padrão não dá o parâmetro (princípio III: num lugar só).
PARAM_FALLBACK_MM = {'stretcher_width': 100.0, 'toe_kick_height': 100.0, 'toe_kick_setback': 50.0,
                     'top_overhang': 20.0, 'back_allowance': 16.0, 'rail_width': 100.0, 'shelf_setback': 20.0,
                     'hanger_rod_drop': 70.0}
EDGE_FRONT = (True, False, False, False)
EDGE_NONE = (False, False, False, False)
# Papel → (nome da peça no corte, componente do Configurador, fitas)
PART_INFO = {
    'LEFT': ("Lateral esquerda", 'LAT', EDGE_FRONT),
    'RIGHT': ("Lateral direita", 'LAT', EDGE_FRONT),
    'BOTTOM': ("Base inferior", 'BAS', EDGE_FRONT),
    'TOP': ("Base superior", 'BAS', EDGE_FRONT),
    'STRETCHER_FRONT': ("Sarrafo frontal", 'SAR', EDGE_FRONT),
    'STRETCHER_BACK': ("Sarrafo traseiro", 'SAR', EDGE_NONE),
    'STRETCHER_FULL': ("Sarrafo inteiro", 'SAR', EDGE_FRONT),
    'TOP_LINEAR': ("Tampo linear", 'TAMP', EDGE_FRONT),
    'TOE_KICK': ("Rodapé frontal", 'ROD', EDGE_FRONT),
    'BACK': ("Fundo", 'FUN_INF', EDGE_NONE),
    'RAIL_LOW': ("Travessa traseira inferior", 'TRA', EDGE_NONE),
    'RAIL_HIGH': ("Travessa traseira superior", 'TRA', EDGE_NONE),
}
STRUCTURE_ROLE_KEYS = ('STRETCHER_FRONT', 'STRETCHER_BACK', 'STRETCHER_FULL', 'TOP_LINEAR', 'TOE_KICK')


@dataclass(frozen=True)
class Part:
    role: str
    box: tuple              # ((x0, y0, z0), (x1, y1, z1))
    component: str
    name: str
    length: float           # medidas de corte, na unidade da entrada
    width: float
    thickness: float
    edges: tuple


def default_params(scale=1.0):
    """`params` de reserva na unidade pedida: `scale` = 1 para mm, 0,001 para m."""
    return {key: value * scale for key, value in PARAM_FALLBACK_MM.items()}


def structure_present(recipe, settings, key):
    """Papel novo da estrutura ligado? O que o projetista marcou na árvore vale sobre a receita (D-03)."""
    entry = (settings or {}).get(key)
    if entry is not None and 'enabled' in entry:
        return bool(entry['enabled'])
    return recipe.has(key)


def _setting_value(settings, key, default):
    entry = (settings or {}).get(key) or {}
    value = entry.get('value')
    return float(value) if value else default


def carcass_parts(recipe, width, height, depth, thick, *, settings=None, params=None, present=None,
                  back_setback=0.0, assembly=LATERAL, back_kind=ENCAIXADO, rear_stretcher=HORIZONTAL,
                  stretcher_cuts=()):
    """([Part] da caixa, vão interno (lo, hi)) de um módulo com estrutura.

    `thick` = {papel: espessura} para LEFT, RIGHT, BOTTOM, TOP, BACK e os componentes 'SAR', 'ROD', 'TAMP', 'TRA'
    (ausentes = a da lateral). `present` = {papel: bool} para LEFT, RIGHT, BOTTOM, TOP e BACK (o `has_*` do
    módulo); ausente = o da receita. `settings` = árvore de extras do módulo (`btm_structure.extras_dict()`).
    `stretcher_cuts` = [(x0, x1)] das divisórias "Corta Sar" (`divisions.stretcher_cuts`): os sarrafos saem em
    pedaços, numerados da esquerda para a direita.
    """
    p = dict(default_params())
    p.update(params or {})
    present = dict(present or {})

    def on(role):
        return bool(present[role]) if role in present else recipe.has(role)

    def t(key, fallback='LEFT'):
        return float(thick.get(key) or thick.get(fallback) or 0.0)

    hw = width / 2.0
    t_left, t_right, t_bottom, t_top, t_back = (t(r) for r in ('LEFT', 'RIGHT', 'BOTTOM', 'TOP', 'BACK'))
    t_sar, t_rod, t_tamp, t_tra = t('SAR'), t('ROD'), t('TAMP'), t('TRA')
    has_left, has_right, has_bottom, has_top, has_back = (on(r) for r in ('LEFT', 'RIGHT', 'BOTTOM', 'TOP', 'BACK'))
    s_front, s_back, s_full, top_linear, toe_kick = (structure_present(recipe, settings, k)
                                                     for k in STRUCTURE_ROLE_KEYS)
    if has_top or s_full:                         # Base Superior ou Sarrafo Inteiro tomam o lugar dos sarrafos
        s_front = s_back = False
    stretcher_w = _setting_value(settings, 'STRETCHER_FRONT', p['stretcher_width'])
    toe_h = _setting_value(settings, 'TOE_KICK', p['toe_kick_height'])
    floor = bool(recipe.sides_to_floor)
    zb = toe_h if (toe_kick or floor) else 0.0
    pregado = has_back and back_kind == PREGADO
    rails = has_back and back_kind == TRAVESSAS
    y_front = -depth
    y_rear = -t_back if pregado else 0.0          # as chapas da caixa param antes do fundo pregado

    x0 = -hw + (t_left if has_left else 0.0)
    x1 = hw - (t_right if has_right else 0.0)
    z_inner_bottom = zb + (t_bottom if has_bottom else 0.0)
    if has_top:
        z_top = height - t_top
    elif s_full or s_front or (s_back and rear_stretcher == HORIZONTAL):
        z_top = height - t_sar
    elif s_back:
        z_top = height - stretcher_w
    else:
        z_top = height
    if s_back and rear_stretcher == VERTICAL and not has_top:
        back_top = height - stretcher_w
    else:
        back_top = z_top

    parts = []

    def add(role, lo, hi, length, part_width, thickness, component=None):
        name, comp, edges = PART_INFO[role]
        parts.append(Part(role, (lo, hi), component or comp, name, length, part_width, thickness, edges))

    side_z = 0.0 if floor else (zb + t_bottom if (assembly == BASE and has_bottom) else zb)
    side_depth = y_rear - y_front
    if has_left:
        add('LEFT', (-hw, y_front, side_z), (-hw + t_left, y_rear, height), height - side_z, side_depth, t_left)
    if has_right:
        add('RIGHT', (hw - t_right, y_front, side_z), (hw, y_rear, height), height - side_z, side_depth, t_right)
    if has_bottom:
        bx = (-hw, hw) if (assembly == BASE and not floor) else (x0, x1)
        add('BOTTOM', (bx[0], y_front, zb), (bx[1], y_rear, zb + t_bottom), bx[1] - bx[0], side_depth, t_bottom)
    if has_top:
        add('TOP', (x0, y_front, height - t_top), (x1, y_rear, height), x1 - x0, side_depth, t_top)
    if s_full:
        add('STRETCHER_FULL', (x0, y_front, height - t_sar), (x1, y_rear, height), x1 - x0, side_depth, t_sar)
    if s_front:
        add('STRETCHER_FRONT', (x0, y_front, height - t_sar), (x1, y_front + stretcher_w, height), x1 - x0,
            stretcher_w, t_sar)
    if s_back:
        if rear_stretcher == VERTICAL:
            add('STRETCHER_BACK', (x0, y_rear - t_sar, height - stretcher_w), (x1, y_rear, height), x1 - x0,
                stretcher_w, t_sar)
        else:
            add('STRETCHER_BACK', (x0, y_rear - stretcher_w, height - t_sar), (x1, y_rear, height), x1 - x0,
                stretcher_w, t_sar)
    if top_linear:
        overhang = p['top_overhang']
        add('TOP_LINEAR', (-hw, y_front - overhang, height), (hw, 0.0, height + t_tamp), width,
            depth + overhang, t_tamp)
    if toe_kick and zb > 0.0:
        kx = (x0, x1) if floor else (-hw, hw)
        ky = y_front + p['toe_kick_setback']
        add('TOE_KICK', (kx[0], ky, 0.0), (kx[1], ky + t_rod, zb), kx[1] - kx[0], zb, t_rod)

    back_front = y_rear
    if has_back:
        component = BACK_COMPONENT.get(recipe.group, 'FUN_INF')
        if pregado:
            add('BACK', (-hw, -t_back, zb), (hw, 0.0, height), height - zb, width, t_back, component)
            back_front = -t_back
        elif rails:
            rail = p['rail_width']
            add('RAIL_LOW', (x0, -t_tra, z_inner_bottom), (x1, 0.0, z_inner_bottom + rail), x1 - x0, rail, t_tra)
            add('RAIL_HIGH', (x0, -t_tra, back_top - rail), (x1, 0.0, back_top), x1 - x0, rail, t_tra)
            add('BACK', (x0, -t_tra - t_back, z_inner_bottom), (x1, -t_tra, back_top), back_top - z_inner_bottom,
                x1 - x0, t_back, component)
            back_front = -t_tra - t_back
        else:
            allowance = p['back_allowance']
            add('BACK', (x0, -t_back - back_setback, z_inner_bottom), (x1, -back_setback, back_top),
                back_top - z_inner_bottom + allowance, x1 - x0 + allowance, t_back, component)
            back_front = -t_back - back_setback
    inner = ((x0, y_front, z_inner_bottom), (x1, back_front, z_top))
    if stretcher_cuts:
        parts = _split_stretchers(parts, stretcher_cuts)
    return parts, inner


def _split_stretchers(parts, cuts):
    """Sarrafos cortados pelas faixas `cuts`; pedaço menor que 1e-6 some."""
    out = []
    for part in parts:
        if part.role not in ('STRETCHER_FRONT', 'STRETCHER_BACK', 'STRETCHER_FULL'):
            out.append(part)
            continue
        (px0, py0, pz0), (px1, py1, pz1) = part.box
        pieces, start = [], px0
        for cx0, cx1 in sorted(cuts):
            if cx1 <= start or cx0 >= px1:
                continue
            if cx0 - start > 1e-6:
                pieces.append((start, cx0))
            start = max(start, cx1)
        if px1 - start > 1e-6:
            pieces.append((start, px1))
        if len(pieces) == 1 and pieces[0] == (px0, px1):
            out.append(part)
            continue
        for index, (a, b) in enumerate(pieces, start=1):
            out.append(Part(part.role, ((a, py0, pz0), (b, py1, pz1)), part.component, f"{part.name} {index}",
                            b - a, part.width, part.thickness, part.edges))
    return out
