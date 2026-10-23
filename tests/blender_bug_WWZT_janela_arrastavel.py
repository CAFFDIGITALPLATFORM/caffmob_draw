"""Reprodução e regressão de BUG-20261023-WWZT (#145): a janela Encostar se arrasta pelo título, sem sair da vista.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_WWZT_janela_arrastavel.py
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    env.clean_scene()
    b = fx.cube("B", (1.0, 0.6, 0.8), (0.5, 0.3, 0.4))
    a = fx.cube("A", (0.4, 0.5, 0.4), (-2.0, 0.3, 0.2))
    fx.settle()
    fake = fx.dialog(a, b)
    before, close_before, matrix = fake.panel, fake.button_close, a.matrix_world.copy()
    t = fake.title_bar
    px, py = t[0] + 60, t[1] + t[3] / 2
    fake.modal(fx.CTX, fx.event('LEFTMOUSE', 'PRESS', px, py))
    fake.modal(fx.CTX, fx.event('MOUSEMOVE', 'NOTHING', px + 100, py - 60))
    fake.modal(fx.CTX, fx.event('LEFTMOUSE', 'RELEASE', px + 100, py - 60))
    moved = fake.panel
    check("reprodução: arrastar o título move a janela", abs(moved[0] - before[0] - 100) < 1e-6
          and abs(moved[1] - before[1] + 60) < 1e-6, (before, moved))
    check("as áreas de clique vão junto", abs(fake.button_close[0] - close_before[0] - 100) < 1e-6)
    check("arrastar a janela não mexe no móvel", a.matrix_world == matrix)

    fake._click(fx.CTX, (fake.button_more[0] + 5, fake.button_more[1] + 5))
    check("Mais opções preserva a posição da janela", fake.more and abs(fake.panel[0] - moved[0]) < 1e-6,
          (moved, fake.panel))

    t = fake.title_bar
    px, py = t[0] + 60, t[1] + t[3] / 2
    fake.modal(fx.CTX, fx.event('LEFTMOUSE', 'PRESS', px, py))
    fake.modal(fx.CTX, fx.event('MOUSEMOVE', 'NOTHING', px + 5000, py + 5000))
    x, y, w, h = fake.panel
    check("a janela não sai da vista", x + w <= fx.REGION.width and y + h <= fx.REGION.height, fake.panel)
    fake.modal(fx.CTX, fx.event('ESC'))
    check("Esc durante o arraste devolve a janela", abs(fake.panel[0] - moved[0]) < 1e-6, fake.panel)
    check("Esc no arraste da janela não cancela o Encostar", not fake.finished)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
