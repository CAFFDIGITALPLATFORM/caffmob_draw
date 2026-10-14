"""Componentes extras da Estrutura (feature 008, T014; RN-07a, D-12 a D-14). Python puro, sem `bpy`.

A partir da caixa da carcaça (no referencial da raiz: X largura, Y profundidade com a frente no menor Y, Z altura) e
da espessura das chapas, devolve as peças de cada item marcado na árvore. Valores padrão das capturas do Promob:
pés 150, fechamentos 50, vistas 150. Pés e rodapés ficam **abaixo** da caixa (o módulo não é levantado).

Geometria (premissas 🟡 do roadmap §4):
- Base Superior Recuada: tampo entre as laterais, recuado `RECESS` na frente;
- Pés plásticos: cilindros (caixa envolvente) nos 4 cantos, a `FOOT_INSET` das bordas (posições 01 a 04: frente
  esquerda, frente direita, trás esquerda, trás direita);
- Rodapés: frontal recuado `KICK_SETBACK`, laterais rente às faces; altura = pés;
- Fechamentos: tiras frontais de largura `value` dos dois lados, por fora;
- Vistas: faixa frontal de largura `value` à esquerda, à direita ou em cima; vistas altas sobem até o teto.

`settings` = {chave da árvore: {'enabled': bool, 'value': m}} (`btm_structure.extras`).

Feature 015 (T022; D-04): num módulo com estrutura de caixa (`structure=True`) os rodapés vêm da própria caixa
(`structure.carcass_parts`), então as chaves de Rodapés daqui não geram peça; os Rodízios são ferragem (`RODIZIO`)
nos 4 cantos, como os pés. O recuo do rodapé vem do Padrão de Dimensões (`kick_setback`); `KICK_SETBACK` é a reserva.
"""

from dataclasses import dataclass

FOOT_RADIUS = 0.02
FOOT_INSET = 0.05
KICK_SETBACK = 0.05
RECESS = 0.02
CEILING = 2.70
DEFAULTS = {'FEET': 0.15, 'CASTERS': 0.10, 'CLOSURE': 0.05, 'VIEW_FRONT': 0.15, 'VIEW_LEFT': 0.15, 'VIEW_RIGHT': 0.15,
            'VIEW_TALL_FRONT': 0.15, 'VIEW_TALL_LEFT': 0.15, 'VIEW_TALL_RIGHT': 0.15}
FOOT_SLOTS = ('FOOT_1', 'FOOT_2', 'FOOT_3', 'FOOT_4')


@dataclass(frozen=True)
class Piece:
    kind: str
    box: tuple                  # ((x0, y0, z0), (x1, y1, z1))
    component: str = None       # componente do Configurador (chapa); None = não é chapa
    hardware: str = None        # código de ferragem
    material: str = ""          # material da chapa sobrescrito (rodapé granito)
    slot: int = 0


def _on(settings, key):
    return bool(settings.get(key, {}).get('enabled'))


def _value(settings, key):
    value = settings.get(key, {}).get('value')
    return float(value) if value else DEFAULTS.get(key, 0.0)


def _box(x0, y0, z0, x1, y1, z1):
    return ((x0, y0, z0), (x1, y1, z1))


def _corners(x0, y0, x1, y1):
    return ((x0 + FOOT_INSET, y0 + FOOT_INSET), (x1 - FOOT_INSET, y0 + FOOT_INSET),
            (x0 + FOOT_INSET, y1 - FOOT_INSET), (x1 - FOOT_INSET, y1 - FOOT_INSET))


def layout(box, t, settings, ceiling=CEILING, structure=False, kick_setback=None):
    """[Piece] das peças extras ligadas, na ordem da árvore."""
    (x0, y0, z0), (x1, y1, z1) = box
    setback = KICK_SETBACK if kick_setback is None else kick_setback
    out = []
    if _on(settings, 'BASE_TOP_RECESSED'):
        out.append(Piece('BASE_TOP_RECESSED', _box(x0 + t, y0 + RECESS, z1 - t, x1 - t, y1, z1), 'BAS'))
    feet = _value(settings, 'FEET')
    if _on(settings, 'FEET'):
        corners = ((x0 + FOOT_INSET, y0 + FOOT_INSET), (x1 - FOOT_INSET, y0 + FOOT_INSET),
                   (x0 + FOOT_INSET, y1 - FOOT_INSET), (x1 - FOOT_INSET, y1 - FOOT_INSET))
        for index, (cx, cy) in enumerate(corners, start=1):
            slot = settings.get(FOOT_SLOTS[index - 1])
            if slot is not None and not slot.get('enabled', True):
                continue
            out.append(Piece('FOOT', _box(cx - FOOT_RADIUS, cy - FOOT_RADIUS, z0 - feet,
                                          cx + FOOT_RADIUS, cy + FOOT_RADIUS, z0), hardware='PE_PLASTICO',
                             slot=index))
    if _on(settings, 'CASTERS'):
        height = _value(settings, 'CASTERS')
        for index, (cx, cy) in enumerate(_corners(x0, y0, x1, y1), start=1):
            out.append(Piece('CASTER', _box(cx - FOOT_RADIUS, cy - FOOT_RADIUS, z0 - height,
                                            cx + FOOT_RADIUS, cy + FOOT_RADIUS, z0), hardware='RODIZIO', slot=index))
    kick_h = feet if feet > 0 else DEFAULTS['FEET']
    if structure:
        settings = {k: v for k, v in settings.items() if k not in ('KICK_FRONT', 'KICK_LEFT', 'KICK_RIGHT')}
    if _on(settings, 'KICK_FRONT') or _on(settings, 'KICK_GRANITE'):
        front = _box(x0, y0 + setback, z0 - kick_h, x1, y0 + setback + t, z0)
        if _on(settings, 'KICK_FRONT'):
            out.append(Piece('KICK_FRONT', front, 'ROD'))
        if _on(settings, 'KICK_GRANITE'):
            out.append(Piece('KICK_GRANITE', front, 'ROD', material='GRANITO'))
    if _on(settings, 'KICK_LEFT'):
        out.append(Piece('KICK_LEFT', _box(x0, y0 + setback, z0 - kick_h, x0 + t, y1, z0), 'ROD'))
    if _on(settings, 'KICK_RIGHT'):
        out.append(Piece('KICK_RIGHT', _box(x1 - t, y0 + setback, z0 - kick_h, x1, y1, z0), 'ROD'))
    if _on(settings, 'CLOSURE'):
        w = _value(settings, 'CLOSURE')
        out.append(Piece('CLOSURE', _box(x0 - w, y0, z0, x0, y0 + t, z1), 'TAMPON', slot=1))
        out.append(Piece('CLOSURE', _box(x1, y0, z0, x1 + w, y0 + t, z1), 'TAMPON', slot=2))
    for key, tall in (('VIEW_LEFT', False), ('VIEW_RIGHT', False), ('VIEW_FRONT', False),
                      ('VIEW_TALL_LEFT', True), ('VIEW_TALL_RIGHT', True), ('VIEW_TALL_FRONT', True)):
        if not _on(settings, key):
            continue
        w = _value(settings, key)
        top = max(ceiling, z1) if tall else z1
        if key.endswith('FRONT'):
            out.append(Piece(key, _box(x0, y0, z1, x1, y0 + t, top if tall else z1 + w), 'ESP'))
        elif key.endswith('LEFT'):
            out.append(Piece(key, _box(x0 - w, y0, z0, x0, y0 + t, top), 'ESP'))
        else:
            out.append(Piece(key, _box(x1, y0, z0, x1 + w, y0 + t, top), 'ESP'))
    return out
