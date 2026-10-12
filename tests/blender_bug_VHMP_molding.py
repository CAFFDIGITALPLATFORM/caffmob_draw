"""Reprodução e regressão do lote das molduras (`molding/ops.py`): BUG-20261011-VHMP, BUG-20261011-XP5E,
BUG-20261011-QT2G, BUG-20261011-MWN5 e BUG-20261011-ARCH.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_VHMP_molding.py

- sweep convertido em malha não aborta a reconstrução (EC-11, EC-04);
- apagar pelo X o 1º armário da corrida deixa a moldura no lugar;
- falha no meio da reconstrução mantém as molduras de antes (sem cena parcial);
- sweep descartado não deixa dado de curva órfão (EC-03);
- perfil de um sweep apagado à mão não acumula (EC-12).
"""

import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.molding import ops  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def sweeps():
    return [o for o in ctx.scene.objects if o.get(ops.MOLDING_TAG)]


def profiles():
    return [o for o in ctx.scene.objects if o.get('IS_HB_MOLDING_PROFILE')]


def run(count=2):
    env.clean_scene()
    ctx.scene.home_builder.molding_base_package = 'NONE'
    cabinets = []
    for i in range(count):
        base = tf.BaseCabinet()
        base.create(f"Balcao{i}")
        hb_utils.run_calc_fix_until_stable(ctx, base.obj)
        base.obj.location = (1.0 + i * base.obj.dimensions.x, 2.0, 0.0)
        cabinets.append(base.obj)
    env.settle()
    ctx.scene.home_builder.molding_base_package = 'SIMPLE'
    env.settle()
    return cabinets


def converted_sweep():
    run()
    mesh = bpy.data.objects.new("Rodapé convertido", bpy.data.meshes.new("Rodapé convertido"))
    ctx.scene.collection.objects.link(mesh)
    mesh[ops.MOLDING_TAG] = True                       # Object › Convert mantém as idprops
    try:
        ops.apply_scene_packages(ctx.scene)
        ok, detail = len(sweeps()) == 1 and "Rodapé convertido" not in bpy.data.objects, str([s.name for s in sweeps()])
    except TypeError as exc:
        ok, detail = False, repr(exc)
    check("VHMP: sweep convertido em malha não aborta a reconstrução", ok, detail)


def delete_first_cabinet():
    run()
    sweep = sweeps()[0]
    first = sweep.parent
    where = sweep.matrix_world.translation.copy()
    with ctx.temp_override(selected_objects=[first], active_object=first, object=first):
        bpy.ops.caffmob.delete_with_aggregates('EXEC_DEFAULT')
    env.settle()
    try:
        alive = sweep.name in bpy.data.objects
    except ReferenceError:
        alive = False
    check("XP5E: apagar o 1º armário deixa a moldura", alive)
    if alive:
        check("XP5E: no mesmo lugar", (sweep.matrix_world.translation - where).length < 1e-6,
              f"{(sweep.matrix_world.translation - where).length:.3f} m")


def failure_midway():
    run()
    before = sorted(s.as_pointer() for s in sweeps())        # os mesmos objetos, não só o mesmo nome
    original = ops._apply_type

    def flaky(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("falha simulada depois de montar")

    ops._apply_type = flaky
    try:
        try:
            ops.apply_scene_packages(ctx.scene)
        except RuntimeError:
            pass
    finally:
        ops._apply_type = original
    after = sorted(s.as_pointer() for s in sweeps())
    check("QT2G: falha no meio mantém as molduras de antes", after == before, f"{len(before)} → {len(after)}, mesmos: "
          f"{after == before}")
    check("QT2G: sem perfil a mais", len(profiles()) == len(sweeps()), f"{len(profiles())} perfis")


def discarded_sweep():
    cabinets = run()
    orphan = len([c for c in bpy.data.curves if c.users == 0])
    tiny = [(([Vector((0.0, 0.0, 0.0)), Vector((0.00001, 0.0, 0.0))]), False)]
    made = ops._spawn_sweep(ctx.scene, 'BASE', cabinets, tiny, "Base Molding/x", 'base_simple', 0.0, {},
                            {'cap_offset': 0.0})
    after = len([c for c in bpy.data.curves if c.users == 0])
    check("MWN5: sweep descartado não deixa curva órfã", made is None and after == orphan, f"{orphan} → {after}")


def hand_deleted_sweep():
    run()
    bpy.data.objects.remove(sweeps()[0], do_unlink=True)
    ops.apply_scene_packages(ctx.scene)
    check("ARCH: perfil do sweep apagado à mão não acumula", len(profiles()) == len(sweeps()) == 1,
          f"{len(profiles())} perfis, {len(sweeps())} sweeps")


for step in (converted_sweep, delete_first_cabinet, failure_midway, discarded_sweep, hand_deleted_sweep):
    try:
        step()
    except Exception:
        traceback.print_exc()
        FAILURES.append(f"exceção em {step.__name__}")
print(f"blender_bug_VHMP_molding: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
