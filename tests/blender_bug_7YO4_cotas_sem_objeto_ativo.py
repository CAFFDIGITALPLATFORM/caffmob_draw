"""Reprodução e regressão de BUG-20261023-7YO4 (#146): os campos de cota do painel não quebram sem objeto ativo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_7YO4_cotas_sem_objeto_ativo.py
"""

import sys
import traceback
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env  # noqa: E402,F401
from caffmob_draw.ui import object_properties as op  # noqa: E402

FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


real = op.bpy
try:
    # Contexto de timer, MCP ou salvamento: tem a cena, mas não `active_object`.
    op.bpy = types.SimpleNamespace(context=types.SimpleNamespace(scene=bpy.context.scene))
    try:
        value = op._cota_getter('afastamento')(None)
        check("reprodução: getter sem objeto ativo devolve 0", value == 0.0, value)
    except AttributeError as exc:
        check("reprodução: getter sem objeto ativo devolve 0", False, repr(exc))
    try:
        op._cota_setter('afastamento')(None, 0.5)
        check("setter sem objeto ativo não faz nada", True)
    except AttributeError as exc:
        check("setter sem objeto ativo não faz nada", False, repr(exc))
finally:
    op.bpy = real

try:
    bpy.ops.mesh.primitive_cube_add()
    check("regressão: com objeto ativo o getter responde", isinstance(op._cota_getter('afastamento')(None), float))
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")

print("RESULTADO:", "FALHAS " + ", ".join(FAILURES) if FAILURES else "OK", flush=True)
sys.exit(1 if FAILURES else 0)
