"""Inventário do painel por tipo (feature 067, T004).

    blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_inventario.py -- --gravar
grava `tests/data/067_inventario_1_8_0.json` (rodado na árvore da 1.8.0, `cb577967`). Sem `--gravar`, só imprime.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _inventario_067 as inventory  # noqa: E402

DATA = Path(__file__).resolve().parent / "data" / "067_inventario_1_8_0.json"
result, errors = inventory.capture()
for name, entry in result.items():
    print("INVENTARIO", name, len(entry['operators']), len(entry['props']), flush=True)
assert not errors, errors
if '--gravar' in sys.argv:
    DATA.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding='utf-8')
print("INVENTARIO_OK", flush=True)
