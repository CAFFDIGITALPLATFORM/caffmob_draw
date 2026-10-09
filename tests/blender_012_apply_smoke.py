"""Fumaça de aplicar o Padrão de Dimensões com as duas perguntas (feature 012, T039; RF-08 a RF-10, RN-10, RN-11).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_apply_smoke.py

Sem janela, as perguntas são respondidas pelo `EXEC` do `caffmob.standards_apply_scene` (`apply_differ` = Sim na 2ª):
- 5 balcões CAFFMob, 1 com base passante própria; um OBJ importado e um frameless não convertido;
- Não (não chamar) → nada muda; Sim + Não → 4 mudam; Sim + Sim → os 5;
- balcão de Banheiro recebe as chapas de BAN; 50 módulos em menos de 5 s; M-03 grava a origem num módulo antigo.
"""

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.standards import api, migration, sync  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def balcao(line='COZ'):
    assert bpy.ops.caffmob.cabinet_builder(cabinet_type='BASE', width=0.6, line=line) == {'FINISHED'}
    return ctx.view_layer.objects.active


def new_standard(lat_mm):
    """Cópia do padrão ativo com outra espessura de lateral em todas as linhas; vira a ativa."""
    previous = api.active_definition(ctx.scene)
    copy = api.duplicate_definition(ctx.scene, previous, name=f"Padrão {lat_mm}")
    for line in ('COZ', 'BAN'):
        api.set_value(copy, f"{line}.sheets.LAT.thickness", lat_mm)
    return previous.uid, copy


def main():
    env.clean_scene()
    mods = [balcao() for _ in range(5)]
    own = mods[4]
    own.btm_cabinet.assembly = 'BASE'                      # padrão próprio
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=(3, 0, 0))
    cube = ctx.active_object
    from caffmob_draw.aggregates import group
    obj_group = group.create_group([cube], 'PLAIN', "Cadeira OBJ")
    legacy = tf.BaseCabinet()
    legacy.create("Antigo")
    hb_utils.run_calc_fix_until_stable(ctx, legacy.obj)
    env.settle()

    previous_uid, copy = new_standard(25.0)
    the_plan, _objects = sync.plan_for(ctx.scene, previous_uid)
    check("plano: 4 seguem, 1 difere", len(the_plan.follow) == 4 and the_plan.differ == [own.name],
          f"{the_plan.follow} {the_plan.differ}")
    check("não aplicáveis: OBJ e frameless", set(the_plan.not_applicable) == {obj_group.name, legacy.obj.name}
          and the_plan.legacy == [legacy.obj.name], str(the_plan.not_applicable))

    check("Não: nada muda", all(abs(m.btm_cabinet.thickness - 0.015) < 1e-6 for m in mods),
          str([round(m.btm_cabinet.thickness, 4) for m in mods]))
    assert bpy.ops.caffmob.standards_apply_scene('EXEC_DEFAULT', previous_uid=previous_uid) == {'FINISHED'}
    check("Sim + Não: os 4 que seguem mudam", all(abs(m.btm_cabinet.thickness - 0.025) < 1e-6 for m in mods[:4])
          and abs(own.btm_cabinet.thickness - 0.015) < 1e-6 and own.btm_cabinet.assembly == 'BASE')
    check("origem dos 4 = padrão novo", all(m.get('btm_standard_uid') == copy.uid for m in mods[:4]))

    previous_uid, copy2 = new_standard(18.0)
    assert bpy.ops.caffmob.standards_apply_scene('EXEC_DEFAULT', previous_uid=previous_uid,
                                                 apply_differ=True) == {'FINISHED'}
    check("Sim + Sim: os 5 mudam e o próprio volta ao padrão",
          all(abs(m.btm_cabinet.thickness - 0.018) < 1e-6 for m in mods) and own.btm_cabinet.assembly == 'LATERAL')
    check("OBJ e frameless não mudam", cube.name in bpy.data.objects and legacy.obj.name in bpy.data.objects)

    bath = balcao('BAN')
    api.set_value(copy2, "BAN.sheets.LAT.thickness", 12.0)
    assert bpy.ops.caffmob.standards_apply_scene('EXEC_DEFAULT', previous_uid=copy2.uid) == {'FINISHED'}
    check("balcão de Banheiro com as chapas de BAN", abs(bath.btm_cabinet.thickness - 0.012) < 1e-6,
          f"{bath.btm_cabinet.thickness:.4f}")

    env.clean_scene()
    many = [balcao() for _ in range(50)]
    previous_uid, _copy3 = new_standard(19.0)
    start = time.perf_counter()
    bpy.ops.caffmob.standards_apply_scene('EXEC_DEFAULT', previous_uid=previous_uid)
    elapsed = time.perf_counter() - start
    check("50 módulos em menos de 5 s", elapsed < 5.0 and all(abs(m.btm_cabinet.thickness - 0.019) < 1e-6
                                                              for m in many), f"{elapsed:.2f} s")

    old = many[0]
    del old['btm_standard_uid']
    migration.stamp_standard_uid(ctx.scene)
    check("M-03 grava a origem num módulo antigo", old.get('btm_standard_uid') == api.active_definition(ctx.scene).uid)


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_012_apply_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
