"""Reprodução e regressão do lote da biblioteca própria (`customize/library_io.py`): BUG-20261011-J2NY,
BUG-20261011-MRZC e BUG-20261011-OJBL.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_J2NY_library_io.py

- `.blend` sem `.json` (grupo antigo) entra sem personalização, sem `UnboundLocalError` (EC-01, RN-CUSTOMIZE-13);
- estilo válido do closets não aparece como ausente; ausente de verdade continua avisado (EC-02);
- falha entre os dois `os.replace` não deixa `.blend` novo com `.json` antigo (RN-15).
"""

import hashlib
import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import library_io  # noqa: E402
from caffmob_draw.product_libraries.closets import types_closets as tc  # noqa: E402
from caffmob_draw.customize.adapters import closets as ca  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cabinet(name):
    base = tf.BaseCabinet()
    base.create(name)
    hb_utils.run_calc_fix_until_stable(ctx, base.obj)
    return base.obj


def entry_of(name):
    return next(e for e in library_io.list_modules() if e['name'] == name)


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha1(handle.read()).hexdigest()


def blend_without_json():
    env.clean_scene()
    paths, errors = library_io.save(ctx, cabinet("Antigo"), "Antigo", "Testes", thumbnail=False)
    check("J2NY: módulo gravado", paths is not None and not errors, str(errors))
    os.remove(paths["json"])
    entry = entry_of("Antigo")
    env.clean_scene()
    try:
        root, loaded, warnings = library_io.load(ctx, entry)
        check("J2NY: .blend sem .json entra sem exceção", root is not None, f"raiz={root} avisos={warnings}")
    except UnboundLocalError as exc:
        check("J2NY: .blend sem .json entra sem exceção", False, repr(exc))
    env.clean_scene()
    try:
        result = bpy.ops.caffmob.module_insert(filepath=entry['blend'], place=False)
    except RuntimeError as exc:
        result = repr(exc)
    check("J2NY: Inserir módulo aceita o grupo antigo", result == {'FINISHED'}, str(result))


def closets_styles():
    check("MRZC: estilo válido do closets não é ausente; inválido é",
          library_io._missing_styles({"library": "CLOSETS", "styles": {"door_styles": ["WIDE_SHAKER", "XYZ"]}})
          == ["XYZ"], str(library_io._missing_styles({"library": "CLOSETS",
                                                       "styles": {"door_styles": ["WIDE_SHAKER", "XYZ"]}})))
    env.clean_scene()
    starter = tc.BaseClosetStarter()
    starter.create_starter("Roupeiro", bay_qty=2)
    tc.recalculate_closet_starter(starter.obj)
    ca.openings(starter.obj)[0][1].btm_custom.door_style = 'WIDE_SHAKER'
    tc.recalculate_closet_starter(starter.obj)
    paths, errors = library_io.save(ctx, starter.obj, "Roupeiro", "Testes", thumbnail=False)
    check("MRZC: roupeiro gravado", paths is not None and not errors, str(errors))
    env.clean_scene()
    root, _loaded, warnings = library_io.load(ctx, entry_of("Roupeiro"))
    check("MRZC: inserir o roupeiro não acusa estilo ausente", root is not None and not any(
        "WIDE_SHAKER" in w for w in warnings), str(warnings))


def atomic_save():
    env.clean_scene()
    root = cabinet("Atomico")
    paths, errors = library_io.save(ctx, root, "Atomico", "Testes", thumbnail=False)
    check("OJBL: módulo gravado", paths is not None and not errors, str(errors))
    before = (digest(paths["blend"]), digest(paths["json"]))
    root.location.x = 1.0
    root.name = "Atomico mudado"
    original = os.replace

    def flaky(src, dst, *args, **kwargs):
        if str(dst).endswith(".json"):
            raise OSError("falha simulada no segundo os.replace")
        return original(src, dst, *args, **kwargs)

    os.replace = flaky
    try:
        _paths, errors = library_io.save(ctx, root, "Atomico", "Testes", thumbnail=False)
    finally:
        os.replace = original
    check("OJBL: a falha é avisada", bool(errors), str(errors))
    after = (digest(paths["blend"]), digest(paths["json"]))
    check("OJBL: .blend e .json continuam o par anterior", after == before, f"{before} → {after}")
    leftovers = sorted(n for n in os.listdir(os.path.dirname(paths["blend"])) if n.startswith("tmp"))
    check("OJBL: sem temporários na pasta", not leftovers, str(leftovers))


try:
    blend_without_json()
    closets_styles()
    atomic_save()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_J2NY_library_io: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
