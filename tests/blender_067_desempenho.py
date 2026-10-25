"""Desempenho da troca de seleção (feature 067, T005; RNF p95 ≤ 50 ms).

Cena de 461 objetos; cada amostra troca o ativo e mede até o painel "Selecionado" desenhado (camada falsa). Grava ou
confere `tests/data/067_desempenho.json`, que guarda a linha de base da 1.8.0 e a medida de cada onda.

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_desempenho.py -- --rotulo 1.8.0
    blender ... --python tests/blender_067_desempenho.py -- --rotulo onda1 --limite 50
"""

import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _desempenho_067 as perf  # noqa: E402

DATA = Path(__file__).resolve().parent / "data" / "067_desempenho.json"


def _arg(name, default=None):
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    return argv[argv.index(name) + 1] if name in argv else default


label = _arg('--rotulo')
limit = _arg('--limite')
targets = perf.build_scene()
perf.measure(targets, rounds=2)                  # aquecimento: caches de nós e de desenho
result = perf.percentiles(perf.measure(targets))
result['objetos'] = len(bpy.context.scene.objects)
result['blender'] = bpy.app.version_string
print("DESEMPENHO_067", json.dumps(result), flush=True)
if label:
    data = json.loads(DATA.read_text(encoding='utf-8')) if DATA.exists() else {}
    data[label] = result
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')
if limit is not None:
    assert result['p95'] <= float(limit), f"p95 {result['p95']} ms acima de {limit} ms"
print("DESEMPENHO_067_OK", flush=True)
