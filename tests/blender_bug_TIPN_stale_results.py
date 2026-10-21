"""Reprodução e regressão do lote dos resultados desatualizados: BUG-20261011-TIPN (colisão) e BUG-20261011-FVQI
(interferência).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_TIPN_stale_results.py

- colisão (reescrito na feature 066, T013): o "desatualizado" saiu com o diagnóstico sob pedido. Abrir o diagnóstico
  depois de criar, renomear ou apagar um objeto mostra a cena de agora, sem resultado vencido; mover não grava
  nada na lista nem avisa (o guarda bloqueia em silêncio);
- interferência: malha que se move depois da verificação deixa o resultado desatualizado (pergunta 93).
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
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


def overlapping_pair():
    env.clean_scene()
    bpy.ops.caffmob.collision_clear()
    ctx.scene.btm_settings.block_penetration = False         # par sobreposto de projeto antigo
    a, b = module(0.0), module(0.3)
    ctx.scene.btm_settings.block_penetration = True
    return a, b


def names():
    return {(r.name_a, r.name_b) for r in ctx.window_manager.btm_collision.items}


def diagnosis_is_current():
    a, b = overlapping_pair()
    assert bpy.ops.caffmob.collision_diagnose() == {'FINISHED'}
    check("TIPN: o diagnóstico mostra o par sobreposto", len(names()) == 1, str(names()))
    ctx.scene.btm_settings.block_penetration = False
    c = module(0.15)
    ctx.scene.btm_settings.block_penetration = True
    bpy.ops.caffmob.collision_diagnose()
    check("TIPN: módulo novo entra no diagnóstico seguinte", any(c.name in p for p in names()), str(names()))
    a.name = "Balcão renomeado"
    env.settle()
    bpy.ops.caffmob.collision_diagnose()
    check("TIPN: renomear aparece com o nome novo", any("Balcão renomeado" in p for p in names()), str(names()))
    for root in (c, b):                       # o módulo inteiro, com as peças
        for obj in [root] + list(root.children_recursive):
            bpy.data.objects.remove(obj, do_unlink=True)
    env.settle()
    bpy.ops.caffmob.collision_diagnose()
    check("TIPN: apagar tira do diagnóstico, sem Limpar", not names(), str(names()))


def moving_is_silent():
    _a, b = overlapping_pair()
    state = ctx.window_manager.btm_collision
    b.location.x = 1.5
    env.settle()
    check("TIPN: mover não grava ocorrência nem marca verificado", not state.items and state.checked < 0,
          f"checked={state.checked} linhas={len(state.items)}")


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


for step in (diagnosis_is_current, moving_is_silent, interference_stale):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_TIPN_stale_results: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
