"""Reprodução e regressão do lote dos resultados desatualizados: BUG-20261011-TIPN (colisão) e BUG-20261011-FVQI
(interferência).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TIPN_stale_results.py

- colisão: objeto novo, apagado ou renomeado depois de verificar deixa o resultado desatualizado; o aviso ao soltar
  sem verificação prévia marca os itens como verificados (questions.md, pergunta 34);
- interferência: malha que se move depois da verificação deixa o resultado desatualizado (pergunta 93).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw.collision import scan  # noqa: E402
from caffmob_draw.inspection import interference  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def module(x):
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    obj = ctx.object
    obj.location.x = x
    env.settle()
    return obj


def fresh_check():
    env.clean_scene()
    bpy.ops.caffmob.collision_clear()
    a, b = module(0.0), module(2.0)
    assert bpy.ops.caffmob.check_collisions(scope='ALL') == {'FINISHED'}
    env.settle()
    state = ctx.window_manager.btm_collision
    return state, a, b


def collision_stale():
    state, _a, _b = fresh_check()
    check("TIPN: logo depois de verificar, em dia", not state.stale)
    module(4.0)
    env.settle()
    check("TIPN: módulo novo deixa desatualizado", state.stale)

    state, a, _b = fresh_check()
    a.name = "Balcão renomeado"
    env.settle()
    check("TIPN: renomear deixa desatualizado", state.stale)

    state, a, _b = fresh_check()
    bpy.data.objects.remove(a, do_unlink=True)
    env.settle()
    check("TIPN: apagar deixa desatualizado", state.stale)


def moved_without_check():
    env.clean_scene()
    bpy.ops.caffmob.collision_clear()
    a, _b = module(0.0), module(0.3)                 # os dois se sobrepõem
    state = ctx.window_manager.btm_collision
    scan.check_moved([a])
    check("TIPN: aviso ao soltar sem verificar marca os itens verificados", state.checked >= 0 and bool(state.items),
          f"checked={state.checked} linhas={len(state.items)}")
    a.location.x = 1.5
    env.settle()
    check("TIPN: e esse resultado também fica desatualizado", state.stale)


def interference_stale():
    env.clean_scene()
    obj = module(0.0)
    interference.store_results(ctx.window_manager, [], 3)
    env.settle()
    state = ctx.window_manager.btm_inspection
    fresh = not state.stale
    obj.location.x = 1.0
    env.settle()
    check("FVQI: mover depois de verificar deixa a interferência desatualizada", fresh and state.stale,
          f"em dia={fresh} desatualizado={state.stale}")


for step in (collision_stale, moved_without_check, interference_stale):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_TIPN_stale_results: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
