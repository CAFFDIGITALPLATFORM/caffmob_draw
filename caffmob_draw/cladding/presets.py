"""Presets de revestimento independentes de standards/ e JSON local versionado (RN-13)."""

from dataclasses import asdict
import json
from pathlib import Path

from .core import Params

FORMAT = 'caffmob_draw.cladding-preset'
VERSION = 1
COMPANY = {
    'tabuas_castanhas': {'name': 'Tábuas castanhas', 'material_kind': 'SOLID_WOOD',
                        'params': asdict(Params()), 'texture_size_mm': 1000.0, 'grain_angle': 0.0, 'texture': '',
                        'finish': {'name': 'Castanho', 'color': [.18, .065, .025, 1]}},
    'ripado_mdf': {'name': 'Ripado com MDF', 'material_kind': 'MDF',
                   'params': asdict(Params(kind='SLATS', width_mm=30, joint_mm=18, backing=True)),
                   'texture_size_mm': 1000.0, 'grain_angle': 90.0, 'texture': '',
                   'finish': {'name': 'Castanho', 'color': [.18, .065, .025, 1]},
                   'backing_finish': {'name': 'MDF do fundo', 'color': [.12, .08, .04, 1]}},
    'painel_horizontal': {'name': 'Painel de veio horizontal', 'material_kind': 'MDF',
                          'params': asdict(Params(kind='PANEL')), 'texture_size_mm': 1000.0,
                          'grain_angle': 0.0, 'texture': ''},
}


def validate(preset):
    """Não completa materiais com regras de MDF: cada JSON traz suas medidas e seus limites explícitos."""
    if preset.get('material_kind') not in {'MDF', 'SOLID_WOOD', 'CERAMIC'}:
        raise ValueError('Material do preset inválido')
    if set(preset['params']) != set(asdict(Params())):
        raise ValueError('Preset deve declarar todas as medidas sem herança implícita')
    Params(**preset['params']).validate()
    size = preset.get('texture_size_mm', 1000)
    import math
    if not math.isfinite(size) or size <= 0 or not math.isfinite(preset.get('grain_angle', 0)):
        raise ValueError('Escala física inválida')
    for key in ('finish', 'backing_finish'):
        finish = preset.get(key)
        if finish is not None:
            color = finish.get('color', [])
            if not finish.get('name') or len(color) != 4 or any(not math.isfinite(v) or not 0 <= v <= 1
                                                               for v in color):
                raise ValueError('Acabamento do preset inválido')
    if not str(preset.get('name', '')).strip():
        raise ValueError('Informe o nome do preset')
    return preset


def dumps(preset):
    return json.dumps({'format': FORMAT, 'version': VERSION, 'preset': validate(preset)},
                      ensure_ascii=False, indent=2, allow_nan=False)


def loads(text):
    document = json.loads(text)
    if document.get('format') != FORMAT or document.get('version') != VERSION:
        raise ValueError('Formato de preset incompatível')
    return validate(document['preset'])


def save(path, preset):
    """Valida antes da escrita; substituição atômica no mesmo diretório."""
    import os
    import tempfile
    text = dumps(preset)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False) as stream:
            temporary = stream.name
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


def load(path):
    return loads(Path(path).read_text(encoding='utf-8'))
