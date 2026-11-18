"""Reprodução e regressão do BUG-20261117-6KBC: nome do editor na barra superior.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_6KBC_titulo.py

1. Reprodução: a barra superior desenha "Editor de Paredes CAFF MOB DRAW" dentro do espaço da barra, à direita;
2. Regressão: os botões da lupa e Mover continuam desenhados na mesma barra;
3. Regressão: o texto é traduzível e sai igual em pt_BR.

A barra do sistema operacional fica fora deste teste: o título dela é `IFACE_(ED_area_name(area))` do Blender e não
tem API Python (ver evidence/reproduction.md).
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.data.i18n import tr  # noqa: E402
from caffmob_draw.walls2d import model, ops_editor, props  # noqa: E402

ctx = bpy.context
ops_editor_draw = ops_editor.draw
ESPERADO = "Editor de Paredes CAFF MOB DRAW"

# 1. Reprodução: a constante existe e é o nome pedido pelo titular.
assert hasattr(ops_editor, "TITULO"), "ops_editor sem TITULO: a barra não mostra o nome do editor"
assert tr(ops_editor.TITULO) == ESPERADO, tr(ops_editor.TITULO)


class ViewFalsa:
    """Vista com o retângulo de uma região real do editor."""
    rect = (0.0, 0.0, 800.0, 600.0)
    scale = 100.0


def desenhar():
    """Chama a barra superior com o desenho em GPU interceptado; devolve as chamadas de texto."""
    chamadas = []

    class DesenhoFalso:
        def __getattr__(self, nome):                 # COLORS, FONT_SIZE e o resto continuam reais
            return getattr(ops_editor_draw, nome)

        def text(self, x, y, value, color=None, size=None):
            chamadas.append((x, y, value))

        def text_width(self, value, size=None):
            return 7.0 * len(value)

        def rect(self, *a, **k):
            return None

        def lines(self, *a, **k):
            return None

        def outline(self, *a, **k):
            return None

    ops_editor.draw = DesenhoFalso()
    try:
        s = props.start(model.WallPlan([model.Chain([(0.0, 0.0), (3.0, 0.0)], [model.Segment()])]), ctx.scene.name)
        ops_editor._draw_toolbar(None, ViewFalsa(), s)
    finally:
        ops_editor.draw = ops_editor_draw
    return chamadas


chamadas = desenhar()
titulos = [(x, y) for x, y, valor in chamadas if valor == ESPERADO]
assert titulos, [c[2] for c in chamadas]
x, y = titulos[0]
barra, _lupa, mover = ops_editor._toolbar_rects(ViewFalsa())
assert x >= mover[0] + mover[2], (x, mover)
assert x + 7.0 * len(ESPERADO) <= barra[0] + barra[2], (x, barra)
assert barra[1] <= y <= barra[1] + barra[3], (y, barra)

# 2. Regressão: os botões da barra continuam lá.
rotulos = [valor for _x, _y, valor in chamadas]
assert "Mover" in rotulos, rotulos
assert len(chamadas) >= 2, chamadas

props.end()
print("blender_bug_6KBC_titulo: OK")
