"""Editor de Paredes sobre a cena v2 do CAFF MOBI: o preenchimento de polígonos (recorte das aberturas).

`mathutils.geometry.tessellate_polygon` devolve trincas de índices, e o `preencher` lia `.x` de cada índice: o desenho
do editor caía a cada quadro, sem paredes, cotas nem painel. Roda em segundo plano, com o lote do GPU capturado:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_studio_preencher.py
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.walls2d import classico_v2 as studio_ui  # noqa: E402

lotes = []
studio_ui.batch_for_shader = lambda sh, tipo, dados: lotes.append((tipo, dados['pos'])) or SimpleNamespace(draw=lambda sh: None)
sh = SimpleNamespace(bind=lambda: None, uniform_float=lambda nome, valor: None)

# Parede em L (côncava) em pixels, como o desenho passa: seis cantos.
contorno = [(0.0, 0.0), (300.0, 0.0), (300.0, 20.0), (20.0, 20.0), (20.0, 200.0), (0.0, 200.0)]
studio_ui.preencher(sh, contorno, (1, 1, 1, 1))
tipo, pos = lotes[-1]
assert tipo == 'TRIS' and len(pos) == 3 * (len(contorno) - 2), (tipo, len(pos))
assert all(tuple(p) in contorno for p in pos), pos
area = sum(abs((b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])) / 2
           for a, b, c in zip(pos[0::3], pos[1::3], pos[2::3]))
assert abs(area - (300 * 20 + 20 * 180)) < 1e-6, area
print("blender_bug_studio_preencher: OK", flush=True)
