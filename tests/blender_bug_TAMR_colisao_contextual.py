"""Reprodução e regressão de BUG-20261023-TAMR (#147): o guarda de colisão protege só o deslocamento direto
(G e gizmo); Encostar, ímã, espelhar e redimensionar têm o destino respeitado (requirements.md RF01 a RF04 da
auditoria de desempenho de 2026-10-23).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TAMR_colisao_contextual.py
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.collision import guard  # noqa: E402
from caffmob_draw.move_over import encostar  # noqa: E402

FAILURES = []
ctx = fx.ctx


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def scene():
    env.clean_scene()
    b = fx.cube("B", (1.0, 0.6, 0.8), (0.5, 0.3, 0.4))           # x 0..1
    c = fx.cube("C", (0.4, 0.6, 0.8), (1.3, 0.3, 0.4))           # x 1,1..1,5: ocupa o lado direito de B
    a = fx.cube("A", (0.4, 0.5, 0.4), (-2.0, 0.3, 0.2))
    fx.settle()
    guard.seed()
    return a, b, c


try:
    # RF02: Encostar grava o destino pedido mesmo sobrepondo C.
    a, b, c = scene()
    fake = fx.dialog(a, b)
    fake._set_side(encostar.RIGHT)
    result = fake._confirm(ctx)
    fx.settle()
    check("reprodução: Encostar grava o destino mesmo sobrepondo", result == {'FINISHED'}
          and abs(a.location.x - 1.2) < 1e-4, (result, round(a.location.x, 4), fake.warning))

    # RF03: redimensionar que sobrepõe não é desfeito.
    a, b, c = scene()
    size = {}

    def grow():
        b.dimensions = (1.6, 0.6, 0.8)
        size['now'] = 1.6

    def shrink():
        b.dimensions = (1.0, 0.6, 0.8)
        size['now'] = 1.0
    ok = guard.reconfigure(b, grow, shrink)
    fx.settle()
    check("reprodução: redimensionar que sobrepõe vale", ok and abs(b.dimensions.x - 1.6) < 1e-4,
          (ok, round(b.dimensions.x, 4)))

    # RF04: erro na edição dimensional restaura e propaga.
    a, b, c = scene()

    def broken():
        b.dimensions = (1.3, 0.6, 0.8)
        raise RuntimeError("falha de teste")
    raised = False
    try:
        guard.reconfigure(b, broken, shrink)
    except RuntimeError:
        raised = True
    check("erro na edição dimensional restaura e propaga", raised and abs(b.dimensions.x - 1.0) < 1e-4,
          (raised, round(b.dimensions.x, 4)))

    # RF01: sem G/gizmo, mudar a posição por código ou pelo painel não é corrigido.
    a, b, c = scene()
    a.location.x = 1.3
    fx.settle()
    check("reprodução: fora de G/gizmo a posição pedida vale", abs(a.location.x - 1.3) < 1e-4, a.location.x)

    # Regressão RF01: com G/gizmo, o movimento para no primeiro contato (chapa fina incluída).
    a, b, c = scene()
    real = guard._direct_move_running
    guard._direct_move_running = lambda: True
    try:
        a.location.x = 3.0
        fx.settle()
    finally:
        guard._direct_move_running = real
    check("regressão: com G o movimento para no primeiro contato", abs(a.location.x - (-0.2)) < 1e-3,
          a.location.x)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
