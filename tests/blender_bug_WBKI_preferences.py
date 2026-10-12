"""Reprodução e regressão de BUG-20261012-WBKI: sem o add-on em `preferences.addons` (pacote registrado direto, como nos
testes), `get_user_preferences` devolve os padrões em vez de levantar `KeyError`.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_WBKI_preferences.py
"""

import sys
import traceback
from pathlib import Path

import bpy  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import caffmob_draw as addon  # noqa: E402

addon.register()                      # como a blender_inspection_smoke: registrado sem estar habilitado
from caffmob_draw.product_libraries.frameless.operators import ops_placement  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    check("o pacote não está em preferences.addons (cenário do teste)", ctx.preferences.addons.get('caffmob_draw') is None)
    try:
        prefs = ctx.window_manager.home_builder.get_user_preferences(ctx)
        color = tuple(round(v, 3) for v in prefs.cabinet_color)
    except Exception as exc:
        color = repr(exc)
    check("WBKI: a cor dos armários vem do padrão", color == (0.0, 0.5, 0.7, 0.3), str(color))
    bpy.ops.mesh.primitive_cube_add()
    cube = ctx.active_object
    try:
        ops_placement.toggle_cabinet_color(cube, True, dont_show_parent=False)
        ok, detail = tuple(round(v, 3) for v in cube.color) == (0.0, 0.5, 0.7, 0.3), str(tuple(cube.color))
    except Exception as exc:
        ok, detail = False, repr(exc)
    check("WBKI: o destaque do armário funciona sem o add-on habilitado", ok, detail)


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_WBKI_preferences: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
