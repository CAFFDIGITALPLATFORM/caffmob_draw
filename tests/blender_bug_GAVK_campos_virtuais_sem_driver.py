"""Reprodução e regressão de BUG-20261023-GAVK (#150): os campos virtuais do painel (`Scene.btm_selection`) não
aceitam driver nem keyframe, e o driver legado nesses campos é removido ao abrir o arquivo, sem tocar nos drivers
dos móveis.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_GAVK_campos_virtuais_sem_driver.py
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _encostar_fixture as fx  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

FAILURES = []
ctx = bpy.context


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


try:
    env.clean_scene()
    cube = fx.cube("Cubo", (0.5, 0.5, 0.5), (0.0, 0.0, 0.25))
    ctx.view_layer.objects.active = cube
    cube.select_set(True)
    fx.settle()
    animatable = [name for name, prop in ctx.scene.btm_selection.bl_rna.properties.items()
                  if name != 'rna_type' and prop.is_animatable]
    check("reprodução: nenhum campo virtual é animável", not animatable, animatable)
    try:
        ctx.scene.driver_add('btm_selection.inferior')
        added = True
    except (TypeError, RuntimeError):
        added = False
    check("reprodução: o painel não deixa pôr driver na cota", not added)

    # Arquivo antigo: o driver já existe (gravado pela versão anterior) num campo virtual e num móvel.
    anim = ctx.scene.animation_data_create()
    for fc in list(anim.drivers):
        anim.drivers.remove(fc)
    legacy = anim.drivers.new('btm_selection.inferior')
    legacy.driver.expression = "1.45"
    keep = cube.driver_add('location', 2)
    keep.driver.expression = "0.25"
    op.quarantine_virtual_drivers()
    paths = [fc.data_path for fc in ctx.scene.animation_data.drivers]
    check("driver legado no campo virtual é removido", 'btm_selection.inferior' not in paths, paths)
    check("driver do móvel fica", any(fc.data_path == 'location' for fc in cube.animation_data.drivers))
    check("a quarentena está ligada ao abrir arquivo", op.quarantine_virtual_drivers in bpy.app.handlers.load_post
          or any(getattr(h, '__name__', '') == 'quarantine_virtual_drivers' for h in bpy.app.handlers.load_post))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
