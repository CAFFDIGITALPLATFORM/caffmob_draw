"""Modelos prontos CAFFMob (feature 012, T057; D-16, RN-15). Python puro.

O catálogo é dado (`data/library_models.json`), para crescer sem mudar código (princípio III): cada modelo diz o tipo,
a largura (0 = a do padrão), a frente e as prateleiras. Altura, profundidade, chapas e montagem vêm do Padrão de
Dimensões, na linha da categoria. O balcão gaveteiro entra quando o módulo CAFFMob tiver gavetas (feature 013).
"""

import json
from collections import namedtuple
from pathlib import Path

from ..data.i18n import tr

Model = namedtuple('Model', 'id label cabinet_type width_mm door_swing shelves structure_id', defaults=("",))
CABINET_TYPES = ('BASE', 'WALL', 'TALL')
DOOR_SWINGS = ('NONE', 'LEFT', 'RIGHT', 'DOUBLE', 'FLIP')
CATALOG = Path(__file__).resolve().parents[1] / "data" / "library_models.json"


def parse(text):
    """(modelos válidos, avisos). Item inválido é pulado com aviso."""
    try:
        data = json.loads(text)
    except ValueError:
        return [], [tr("Catálogo de modelos inválido")]
    models, warnings = [], []
    for item in data.get('models', []) if isinstance(data, dict) else []:
        if not isinstance(item, dict) or not item.get('id'):
            warnings.append(tr("Modelo sem identificador ignorado"))
            continue
        if item.get('cabinet_type') not in CABINET_TYPES:
            warnings.append(tr("Modelo {}: tipo desconhecido").format(item['id']))
            continue
        swing = item.get('door_swing') or 'NONE'          # null = ausente (F-06)
        if swing not in DOOR_SWINGS:
            warnings.append(tr("Modelo {}: frente desconhecida").format(item['id']))
            continue
        width, shelves = _count(item, 'width_mm', warnings), _count(item, 'shelves', warnings)
        structure_id = str(item.get('structure_id') or "")      # feature 015 (D-16): vazio = equivalência
        if structure_id and not _known_structure(structure_id):
            warnings.append(tr("Modelo {}: estrutura desconhecida").format(item['id']))
            continue
        models.append(Model(str(item['id']), str(item.get('label') or item['id']), item['cabinet_type'],
                            width, swing, shelves, structure_id))
    return models, warnings


def _known_structure(structure_id):
    from ..cabinet_editor import structures_core
    return structures_core.get(structure_id) is not None


def model_structure(model, line):
    """Estrutura de caixa do modelo: a do catálogo ou, sem ela, a equivalente pela linha e pelo tipo (RN-22)."""
    if model.structure_id:
        return model.structure_id
    from ..cabinet_editor import structures_core
    return structures_core.load().legacy_structure(line, model.cabinet_type) or ""


def _count(item, key, warnings):
    """Inteiro ≥ 0; valor não numérico vale 0, com aviso, e o catálogo continua (EC-07)."""
    try:
        return max(0, int(item.get(key) or 0))
    except (TypeError, ValueError):
        warnings.append(tr("Modelo {}: {} não numérico ignorado").format(item['id'], key))
        return 0


def load_default():
    try:
        return parse(CATALOG.read_text(encoding='utf-8'))
    except OSError:
        return [], [tr("Catálogo de modelos não encontrado")]


def find(models, model_id):
    return next((m for m in models if m.id == model_id), None)


# Miniatura do modelo pronto na grade (BUG-20261014-RWU2) -----------------------------------------------------------
THUMB_REF_MM = 2400.0                 # altura de referência: todos os modelos na mesma escala
THUMB_PAD = 0.08                      # respiro da caixa, em fração do lado
PLINTH_MM, DOOR_GAP_MM = 100.0, 12.0
DOOR_COUNT = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2, 'FLIP': 1}


def thumb_shapes(cabinet_type, width_mm, height_mm, z_mm, door_swing, shelves, box):
    """Frente do módulo desenhada na caixa `box` (x, y, w, h; y para cima), em escala comum.

    Devolve dict com `scale` (px por mm), `floor` (x0, y, x1), `plinth` (retângulo ou None), `carcass`, `doors`
    (retângulos), `handles` ((x, y) de cada puxador) e `shelves` (y das prateleiras). Balcão e torre ficam no piso com
    rodapé; o aéreo, na altura de instalação `z_mm`. Frente desconhecida desenha o módulo aberto.
    """
    bx, by, bw, bh = box
    pad = min(bw, bh) * THUMB_PAD
    width, height, z = max(1.0, float(width_mm)), max(1.0, float(height_mm)), max(0.0, float(z_mm))
    scale = (bh - 2 * pad) / max(THUMB_REF_MM, z + height)
    scale = min(scale, (bw - 2 * pad) / width)                 # largo demais: encolhe para caber
    floor_y = by + pad
    cw, ch = width * scale, height * scale
    cx = bx + (bw - cw) / 2.0
    cy = floor_y + (z * scale if cabinet_type == 'WALL' else 0.0)
    carcass = (cx, cy, cw, ch)
    plinth = None
    front_y = cy
    if cabinet_type != 'WALL':
        ph = min(PLINTH_MM * scale, ch * 0.2)
        inset = cw * 0.04
        plinth = (cx + inset, cy, cw - 2 * inset, ph)
        front_y = cy + ph
    front_h = cy + ch - front_y
    count = DOOR_COUNT.get(door_swing, 0)
    gap = DOOR_GAP_MM * scale
    doors, handles = [], []
    if count:
        dw = (cw - gap * (count + 1)) / count
        for i in range(count):
            doors.append((cx + gap + i * (dw + gap), front_y + gap, dw, front_h - 2 * gap))
        hy = {'BASE': front_y + front_h * 0.82, 'WALL': front_y + front_h * 0.18}.get(cabinet_type,
                                                                                   front_y + front_h * 0.5)
        if door_swing == 'FLIP':
            handles.append((cx + cw / 2.0, front_y + gap * 2))
        elif door_swing == 'LEFT':
            handles.append((doors[0][0] + doors[0][2] * 0.85, hy))
        elif door_swing == 'RIGHT':
            handles.append((doors[0][0] + doors[0][2] * 0.15, hy))
        else:
            handles += [(doors[0][0] + doors[0][2] * 0.85, hy), (doors[1][0] + doors[1][2] * 0.15, hy)]
    rows = max(0, int(shelves))
    shelf_ys = [front_y + front_h * (i + 1) / (rows + 1) for i in range(rows)]
    return {"scale": scale, "floor": (bx + pad * 0.5, floor_y, bx + bw - pad * 0.5), "plinth": plinth,
            "carcass": carcass, "doors": doors, "handles": handles, "shelves": shelf_ys}
