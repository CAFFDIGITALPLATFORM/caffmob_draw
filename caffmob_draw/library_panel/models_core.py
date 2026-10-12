"""Modelos prontos CAFFMob (feature 012, T057; D-16, RN-15). Python puro.

O catálogo é dado (`data/library_models.json`), para crescer sem mudar código (princípio III): cada modelo diz o tipo,
a largura (0 = a do padrão), a frente e as prateleiras. Altura, profundidade, chapas e montagem vêm do Padrão de
Dimensões, na linha da categoria. O balcão gaveteiro entra quando o módulo CAFFMob tiver gavetas (feature 013).
"""

import json
from collections import namedtuple
from pathlib import Path

from ..data.i18n import tr

Model = namedtuple('Model', 'id label cabinet_type width_mm door_swing shelves')
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
        models.append(Model(str(item['id']), str(item.get('label') or item['id']), item['cabinet_type'],
                            width, swing, shelves))
    return models, warnings


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
