"""Reprodução e regressão de BUG-20261023-5ATK (#143): o Encostar é um salto, não um arraste. Destino livre vale
mesmo com B no caminho; destino que atravessa mantém a janela aberta e diz com quem colidiria.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5ATK_encostar_colisao.py
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.move_over import encostar  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def scene():
    env.clean_scene()
    b = fx.cube("B", (1.0, 0.6, 0.8), (0.5, 0.3, 0.4))        # x 0..1
    a = fx.cube("A", (0.4, 0.5, 0.4), (-2.0, 0.3, 0.2))       # à esquerda de B
    fx.settle()
    return a, b


try:
    # Reprodução: à direita de B, com B no caminho reto.
    a, b = scene()
    fake = fx.dialog(a, b)
    fake._set_side(encostar.RIGHT)
    result = fake._confirm(fx.ctx)
    fx.settle()
    check("reprodução: B no caminho não impede encostar à direita", abs(a.location.x - 1.2) < 1e-4,
          f"A.x={a.location.x:.4f} (esperado 1,2)")
    check("encostar à direita fecha com a mensagem do lado pedido", result == {'FINISHED'} and fake.finished
          and "à direita" in fake.reports[-1], (result, fake.reports))

    # Destino que atravessa: C ocupa o lugar à direita de B.
    a, b = scene()
    c = fx.cube("C", (0.4, 0.6, 0.8), (1.3, 0.3, 0.4))
    fx.settle()
    origin = a.matrix_world.copy()
    fake = fx.dialog(a, b)
    fake._set_side(encostar.RIGHT)
    result = fake._confirm(fx.ctx)
    check("destino que atravessa: a janela continua aberta", result == {'RUNNING_MODAL'} and not fake.finished,
          (result, fake.finished))
    check("destino que atravessa: o aviso diz com quem", "C" in fake.warning and bool(fake.warning), fake.warning)
    check("destino que atravessa: nada é anunciado como posicionado", not fake.reports, fake.reports)
    fake.cancel(fx.CTX)
    fx.settle()
    check("Cancelar depois do aviso devolve A à origem", a.matrix_world == origin)

    # Regressão: destino livre sem nada no caminho continua igual; com o guarda desligado, grava o destino.
    a, b = scene()
    fake = fx.dialog(a, b)
    fake._set_side(encostar.LEFT)
    fake._confirm(fx.ctx)
    fx.settle()
    check("regressão: à esquerda, caminho livre", abs(a.location.x - (-0.2)) < 1e-4, a.location.x)
    a, b = scene()
    c = fx.cube("C", (0.4, 0.6, 0.8), (1.3, 0.3, 0.4))
    fx.settle()
    fx.ctx.scene.btm_settings.block_penetration = False
    fake = fx.dialog(a, b)
    fake._set_side(encostar.RIGHT)
    result = fake._confirm(fx.ctx)
    fx.settle()
    check("Impedir atravessamento desligado: grava o destino", result == {'FINISHED'} and abs(a.location.x - 1.2) < 1e-4,
          (result, a.location.x))
    fx.ctx.scene.btm_settings.block_penetration = True
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
