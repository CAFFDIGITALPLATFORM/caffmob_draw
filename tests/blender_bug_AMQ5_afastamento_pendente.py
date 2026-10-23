"""Reprodução e regressão de BUG-20261023-AMQ5 (#144): clicar Encostar grava o campo em edição.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_AMQ5_afastamento_pendente.py
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.move_over import encostar, ops_dialog  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def scene():
    env.clean_scene()
    b = fx.cube("B", (1.0, 0.6, 0.8), (0.5, 0.3, 0.4))
    a = fx.cube("A", (0.4, 0.5, 0.4), (-2.0, 0.3, 0.2))
    fx.settle()
    return a, b


def click_ok(fake):
    r = fake.button_ok
    return fake.modal(fx.CTX, fx.event('LEFTMOUSE', x=r[0] + r[2] / 2, y=r[1] + r[3] / 2))


try:
    a, b = scene()
    fake = fx.dialog(a, b)
    fake._set_side(encostar.LEFT)
    fake.typing, fake.buffer = ops_dialog.GAP, "300"
    result = click_ok(fake)
    fx.settle()
    gap = (b.location.x - 0.5) - (a.location.x + 0.2)
    check("reprodução: 300 mm pendentes valem ao clicar Encostar", result == {'FINISHED'} and abs(gap - 0.3) < 1e-4,
          (result, round(gap, 4)))

    a, b = scene()
    fake = fx.dialog(a, b)
    fake.typing, fake.buffer = ops_dialog.GAP, "abc"
    result = click_ok(fake)
    check("valor inválido pendente: a janela fica aberta com o aviso", result == {'RUNNING_MODAL'}
          and not fake.finished and bool(fake.warning), (result, fake.warning))

    # Regressão: Enter no campo grava e mantém a janela; Enter de novo encosta.
    fake.typing, fake.buffer = ops_dialog.GAP, "50"
    first = fake.modal(fx.CTX, fx.event('RET'))
    check("regressão: Enter no campo grava sem fechar", first == {'RUNNING_MODAL'} and abs(fake.gap - 0.05) < 1e-9
          and fake.typing is None, (first, fake.gap))
    second = fake.modal(fx.CTX, fx.event('RET'))
    check("regressão: Enter de novo encosta", second == {'FINISHED'}, second)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
