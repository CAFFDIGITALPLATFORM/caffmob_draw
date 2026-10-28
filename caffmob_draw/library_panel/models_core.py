"""Modelos prontos CAFFMob (feature 012, T057; feature 078, T020; D-10, D-16, RN-15). Python puro.

O catálogo é dado (`data/library_models.json`), para crescer sem mudar código (princípio III):
- `models`: os 5 modelos clássicos da linha;
- `presets`: balcões adicionais, gaveteiros (`drawers > 0`) e armários de canto (`corner_kind` `'L'` ou `'OBLIQUE'`,
  `right_width_mm`);
- `openings`: os 30 modelos paramétricos de portas (`DOOR`, 5 giro + 5 correr) e janelas (`WINDOW`, 20 modelos nas 4
  famílias de folha).
"""

import json
from collections import namedtuple
from pathlib import Path

from ..caffmob.v2 import contrato as v2_contrato
from ..data.i18n import tr

Model = namedtuple(
    'Model',
    'id label cabinet_type width_mm door_swing shelves structure_id '
    'drawers corner_kind right_width_mm kind opening_model default_material height_mm sill_mm category',
    defaults=("", 0, 'NONE', 0, 'MODULE', "", "", 0, 0, ""),
)
CABINET_TYPES = ('BASE', 'WALL', 'TALL')
DOOR_SWINGS = ('NONE', 'LEFT', 'RIGHT', 'DOUBLE', 'FLIP')
CORNER_KINDS = ('NONE', 'L', 'OBLIQUE')
OPENING_KINDS = ('DOOR', 'WINDOW')
OPENING_CATEGORIES = (
    'portas_giro',
    'portas_correr',
    'janelas_correr',
    'janelas_abrir',
    'janelas_basculantes',
    'janelas_fixas',
)
CATALOG = Path(__file__).resolve().parents[1] / "data" / "library_models.json"


def _parse_cabinet_item(item, warnings):
    if not isinstance(item, dict) or not item.get('id'):
        warnings.append(tr("Modelo sem identificador ignorado"))
        return None
    if item.get('cabinet_type') not in CABINET_TYPES:
        warnings.append(tr("Modelo {}: tipo desconhecido").format(item['id']))
        return None
    swing = item.get('door_swing') or 'NONE'          # null = ausente (F-06)
    if swing not in DOOR_SWINGS:
        warnings.append(tr("Modelo {}: frente desconhecida").format(item['id']))
        return None
    corner_kind = str(item.get('corner_kind') or 'NONE')
    if corner_kind not in CORNER_KINDS:
        warnings.append(tr("Modelo {}: canto desconhecido").format(item['id']))
        return None
    width = _count(item, 'width_mm', warnings)
    shelves = _count(item, 'shelves', warnings)
    drawers = _count(item, 'drawers', warnings)
    right_width = _count(item, 'right_width_mm', warnings)
    structure_id = str(item.get('structure_id') or "")      # feature 015 (D-16): vazio = equivalência
    if structure_id and not _known_structure(structure_id):
        warnings.append(tr("Modelo {}: estrutura desconhecida").format(item['id']))
        return None
    return Model(
        str(item['id']),
        str(item.get('label') or item['id']),
        item['cabinet_type'],
        width,
        swing,
        shelves,
        structure_id,
        drawers,
        corner_kind,
        right_width,
        'MODULE',
        "",
        "",
        0,
        0,
        "",
    )


def _parse_opening_item(item, warnings):
    if not isinstance(item, dict) or not item.get('id'):
        warnings.append(tr("Modelo sem identificador ignorado"))
        return None
    kind = item.get('kind')
    if kind not in OPENING_KINDS:
        warnings.append(tr("Modelo {}: tipo desconhecido").format(item['id']))
        return None
    opening_model = str(item.get('opening_model') or item['id'])
    valid_models = v2_contrato.MODELOS_DE_PORTA if kind == 'DOOR' else v2_contrato.MODELOS_DE_JANELA
    if opening_model not in valid_models:
        warnings.append(tr("Modelo {}: modelo de abertura desconhecido").format(item['id']))
        return None
    default_mat = str(item.get('default_material') or v2_contrato.PADRAO_ABERTURA[kind]['material'])
    if default_mat not in v2_contrato.MATERIAIS_DE_ABERTURA:
        warnings.append(tr("Modelo {}: material desconhecido").format(item['id']))
        return None
    width = _count(item, 'width_mm', warnings) or (800 if kind == 'DOOR' else 1200)
    height = _count(item, 'height_mm', warnings) or (2100 if kind == 'DOOR' else 1200)
    sill = _count(item, 'sill_mm', warnings)
    category = str(item.get('category') or ('portas_giro' if kind == 'DOOR' else 'janelas_correr'))
    return Model(
        str(item['id']),
        str(item.get('label') or item['id']),
        'BASE',
        width,
        'NONE',
        0,
        "",
        0,
        'NONE',
        0,
        kind,
        opening_model,
        default_mat,
        height,
        sill,
        category,
    )


def parse(text):
    """(modelos válidos, avisos). Item inválido é pulado com aviso."""
    try:
        data = json.loads(text)
    except ValueError:
        return [], [tr("Catálogo de modelos inválido")]
    models, warnings = [], []
    for item in data.get('models', []) if isinstance(data, dict) else []:
        if isinstance(item, dict) and item.get('kind') in OPENING_KINDS:
            parsed = _parse_opening_item(item, warnings)
        else:
            parsed = _parse_cabinet_item(item, warnings)
        if parsed is not None:
            models.append(parsed)
    return models, warnings


def parse_all(text):
    """(móveis, aberturas, avisos) lendo `models`, `presets` e `openings` do catálogo."""
    try:
        data = json.loads(text)
    except ValueError:
        return [], [], [tr("Catálogo de modelos inválido")]
    if not isinstance(data, dict):
        return [], [], [tr("Catálogo de modelos inválido")]
    cabinets, openings, warnings = [], [], []
    for key in ('models', 'presets'):
        for item in data.get(key, []):
            if isinstance(item, dict) and item.get('kind') in OPENING_KINDS:
                parsed = _parse_opening_item(item, warnings)
                if parsed is not None:
                    openings.append(parsed)
            else:
                parsed = _parse_cabinet_item(item, warnings)
                if parsed is not None:
                    cabinets.append(parsed)
    for item in data.get('openings', []):
        parsed = _parse_opening_item(item, warnings)
        if parsed is not None:
            openings.append(parsed)
    return cabinets, openings, warnings


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


def load_presets():
    """(presets de armários adicionais: balcões, gaveteiros e cantos, avisos)."""
    try:
        data = json.loads(CATALOG.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return [], [tr("Catálogo de modelos não encontrado")]
    presets, warnings = [], []
    for item in data.get('presets', []) if isinstance(data, dict) else []:
        parsed = _parse_cabinet_item(item, warnings)
        if parsed is not None:
            presets.append(parsed)
    return presets, warnings


def load_all_cabinets():
    """Todos os modelos de armário (`models` + `presets`)."""
    models, w1 = load_default()
    presets, w2 = load_presets()
    return models + presets, w1 + w2


def load_openings(kind=None, category=None):
    """(modelos de aberturas, avisos), opcionalmente filtrados por `kind` ('DOOR'|'WINDOW') ou `category`."""
    try:
        _cabs, openings, warnings = parse_all(CATALOG.read_text(encoding='utf-8'))
    except OSError:
        return [], [tr("Catálogo de modelos não encontrado")]
    if kind is not None:
        openings = [o for o in openings if o.kind == kind]
    if category is not None:
        openings = [o for o in openings if o.category == category]
    return openings, warnings


def load_all():
    """(todos os modelos de móveis e aberturas, avisos)."""
    try:
        cabs, openings, warnings = parse_all(CATALOG.read_text(encoding='utf-8'))
        return cabs + openings, warnings
    except OSError:
        return [], [tr("Catálogo de modelos não encontrado")]


def find(models, model_id):
    return next((m for m in models if m.id == model_id), None)


def find_any(model_id):
    """Busca `model_id` entre todos os móveis (`models` + `presets`) e aberturas (`openings`)."""
    all_items, _warnings = load_all()
    return find(all_items, model_id)


# Miniatura do modelo pronto na grade (BUG-20261014-RWU2 + feature 078) ----------------------------------------------
THUMB_REF_MM = 2400.0                 # altura de referência: todos os modelos na mesma escala
THUMB_PAD = 0.08                      # respiro da caixa, em fração do lado
PLINTH_MM, DOOR_GAP_MM = 100.0, 12.0
DOOR_COUNT = {'LEFT': 1, 'RIGHT': 1, 'DOUBLE': 2, 'FLIP': 1}


def opening_thumb_shapes(opening_model, width_mm, height_mm, sill_mm, box):
    """Frente vetorial de uma porta ou janela na caixa `box` (x, y, w, h; y para cima), em escala comum."""
    bx, by, bw, bh = box
    pad = min(bw, bh) * THUMB_PAD
    width = max(1.0, float(width_mm))
    height = max(1.0, float(height_mm))
    sill = max(0.0, float(sill_mm))
    scale = (bh - 2 * pad) / max(THUMB_REF_MM, sill + height)
    scale = min(scale, (bw - 2 * pad) / width)
    floor_y = by + pad
    cw, ch = width * scale, height * scale
    cx = bx + (bw - cw) / 2.0
    cy = floor_y + sill * scale
    carcass = (cx, cy, cw, ch)
    gap = max(1.5, 25.0 * scale)
    ix, iy, iw, ih = cx + gap, cy + gap, max(2.0, cw - 2 * gap), max(2.0, ih_raw := ch - 2 * gap)

    doors = []
    handles = []
    shelves = []
    model = str(opening_model or "")

    # Bandeira superior (transom)
    if "bandeira" in model:
        bh_band = ih * 0.24
        doors.append((ix, iy + ih - bh_band, iw, bh_band))
        shelves.append(iy + ih - bh_band)
        ih = ih - bh_band - gap * 0.5
    elif "maximar_fixo" in model:
        bh_fix = ih * 0.32
        doors.append((ix, iy, iw, bh_fix))
        shelves.append(iy + bh_fix)
        iy = iy + bh_fix + gap * 0.5
        ih = ih - bh_fix - gap * 0.5

    # Número de folhas / colunas
    if any(k in model for k in ("_4f",)):
        cols = 4
    elif any(k in model for k in ("_3f", "_bay")):
        cols = 3
    elif any(k in model for k in ("_2f", "_dupla", "_panoramica", "_camarao", "abrir_veneziana", "correr_veneziana", "abrir_bandeira", "correr_bandeira")):
        cols = 2
    else:
        cols = 1

    leaf_gap = max(1.0, gap * 0.45)
    lw = (iw - leaf_gap * (cols - 1)) / cols
    for i in range(cols):
        lx = ix + i * (lw + leaf_gap)
        doors.append((lx, iy, lw, ih))

    # Detalhes internos por modelo (frisos, almofadas, visor, veneziana, vitrô, maxim-ar 2m)
    if "frisada" in model:
        for r in range(1, 5):
            shelves.append(iy + ih * r / 5.0)
    elif "almofadada" in model:
        pad_x, pad_y = lw * 0.18, ih * 0.10
        doors.append((ix + pad_x, iy + pad_y, lw - 2 * pad_x, ih * 0.34))
        doors.append((ix + pad_x, iy + ih * 0.54, lw - 2 * pad_x, ih * 0.34))
    elif "visor" in model:
        vw = lw * 0.28
        doors.append((ix + lw * 0.58, iy + ih * 0.16, vw, ih * 0.68))
    elif "veneziana" in model:
        for r in range(1, 7):
            shelves.append(iy + ih * r / 7.0)
    elif "vitro" in model:
        for r in range(1, 4):
            shelves.append(iy + ih * r / 4.0)
        doors.append((ix + iw / 2.0 - leaf_gap * 0.5, iy, leaf_gap, ih))
    elif "maximar_2m" in model:
        shelves.append(iy + ih * 0.5)
    elif "basculante" in model:
        for r in range(1, 4):
            shelves.append(iy + ih * r / 4.0)
    elif "aparente" in model:
        # Trilho superior aparente
        shelves.append(cy + ch + max(2.0, 40.0 * scale))

    # Puxadores / maçanetas
    hy = iy + ih * 0.48
    if model.startswith("porta_"):
        if cols == 1:
            handles.append((ix + lw * 0.84, hy))
        else:
            handles.append((ix + lw * 0.88, hy))
            handles.append((ix + lw + leaf_gap + lw * 0.12, hy))
    else:
        handles.append((ix + iw * 0.5, iy + ih * (0.15 if "maximar" in model else 0.5)))

    return {
        "scale": scale,
        "floor": (bx + pad * 0.5, floor_y, bx + bw - pad * 0.5),
        "plinth": None,
        "carcass": carcass,
        "doors": doors,
        "handles": handles,
        "shelves": shelves,
    }


def thumb_shapes(cabinet_type, width_mm, height_mm, z_mm, door_swing, shelves, box,
                 *, drawers=0, corner_kind='NONE', right_width_mm=0, kind='MODULE', opening_model=""):
    """Frente do módulo (ou abertura) desenhada na caixa `box` (x, y, w, h; y para cima), em escala comum.

    Devolve dict com `scale` (px por mm), `floor` (x0, y, x1), `plinth` (retângulo ou None), `carcass`, `doors`
    (retângulos), `handles` ((x, y) de cada puxador) e `shelves` (y das prateleiras). Quando `drawers=0`,
    `corner_kind='NONE'` e `kind='MODULE'`, o retorno é idêntico ao da feature 014 (BUG-20261014-RWU2).
    """
    if kind in OPENING_KINDS or opening_model:
        return opening_thumb_shapes(opening_model or kind, width_mm, height_mm, z_mm, box)

    bx, by, bw, bh = box
    pad = min(bw, bh) * THUMB_PAD
    eff_width = float(width_mm) + (float(right_width_mm) * 0.35 if corner_kind in ('L', 'OBLIQUE') else 0.0)
    width, height, z = max(1.0, eff_width), max(1.0, float(height_mm)), max(0.0, float(z_mm))
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
    gap = DOOR_GAP_MM * scale
    doors, handles = [], []

    drawer_count = max(0, int(drawers))
    if drawer_count > 0:
        dh = (front_h - gap * (drawer_count + 1)) / drawer_count
        dw = cw - 2 * gap
        for i in range(drawer_count):
            dy = front_y + gap + i * (dh + gap)
            doors.append((cx + gap, dy, dw, dh))
            handles.append((cx + cw / 2.0, dy + dh * 0.55))
    else:
        count = DOOR_COUNT.get(door_swing, 0)
        if count:
            dw = (cw - gap * (count + 1)) / count
            for i in range(count):
                doors.append((cx + gap + i * (dw + gap), front_y + gap, dw, front_h - 2 * gap))
            hy = {'BASE': front_y + front_h * 0.82, 'WALL': front_y + front_h * 0.18}.get(
                cabinet_type, front_y + front_h * 0.5
            )
            if door_swing == 'FLIP':
                handles.append((cx + cw / 2.0, front_y + gap * 2))
            elif door_swing == 'LEFT':
                handles.append((doors[0][0] + doors[0][2] * 0.85, hy))
            elif door_swing == 'RIGHT':
                handles.append((doors[0][0] + doors[0][2] * 0.15, hy))
            else:
                handles += [(doors[0][0] + doors[0][2] * 0.85, hy), (doors[1][0] + doors[1][2] * 0.15, hy)]

    if corner_kind == 'L':
        # Marca vertical da quina interna em L
        fold_x = cx + cw * 0.52
        doors.append((fold_x - max(1.0, gap * 0.4), front_y + gap, max(2.0, gap * 0.8), front_h - 2 * gap))
    elif corner_kind == 'OBLIQUE':
        # Chanfro central do canto oblíquo
        chamfer_w = cw * 0.46
        doors.append((cx + (cw - chamfer_w) / 2.0, front_y + gap * 1.5, chamfer_w, front_h - 3 * gap))

    rows = max(0, int(shelves))
    shelf_ys = [front_y + front_h * (i + 1) / (rows + 1) for i in range(rows)]
    return {"scale": scale, "floor": (bx + pad * 0.5, floor_y, bx + bw - pad * 0.5), "plinth": plinth,
            "carcass": carcass, "doors": doors, "handles": handles, "shelves": shelf_ys}
