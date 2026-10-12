"""Reprodução e regressão do lote da conversão das bibliotecas herdadas: BUG-20261011-5NLX, BUG-20261011-NTM3,
BUG-20261011-HUWF e BUG-20261011-ORRG.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_5NLX_legacy.py

- falha no meio do lote: os módulos já criados saem, ERROR com o nome do armário e CANCELLED (questions.md, 54);
- frente especial do face frame conta uma vez só (pergunta 55);
- falha do leitor da biblioteca vira a perda "Frentes não lidas", nunca "sem perdas" (pergunta 56);
- grupo homônimo em outra pasta não some da lista de grupos a converter (legacy RN-19).
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import adapters  # noqa: E402
from caffmob_draw.legacy import convert, convert_core, gate, groups  # noqa: E402
from caffmob_draw.product_libraries.face_frame import types_face_frame as tff  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.product_libraries.frameless.operators import ops_library  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def frameless(name, x):
    cab = tf.BaseCabinet()
    cab.create(name)
    cab.obj.location = (x, 0.0, 0.0)
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    return cab.obj


def rollback():
    env.clean_scene()
    frameless("Balcao A", 0.0)
    frameless("Balcao B", 1.2)
    env.settle()
    before = {o.name for o in bpy.data.objects}
    original, calls = convert._build, []

    def failing(context, reading):
        calls.append(reading.name)
        result = original(context, reading)          # o segundo módulo nasce e só então falha
        if len(calls) == 2:
            raise ValueError("falha simulada")
        return result
    convert._build = failing
    message = ""
    try:
        with ctx.temp_override(selected_objects=[], active_object=None):
            result = bpy.ops.caffmob.legacy_convert('EXEC_DEFAULT')
        message = str(result)
    except RuntimeError as exc:                       # report ERROR em segundo plano vira RuntimeError
        message = str(exc)
    finally:
        convert._build = original
    left = sorted({o.name for o in bpy.data.objects} - before)
    check("5NLX: nada criado fica na cena", not left, str(left))
    check("5NLX: ERROR com o nome do armário", "Não foi possível converter Balcao B" in message, message[-160:])
    check("5NLX: os herdados continuam", len(gate.legacy_roots(ctx.scene)) == 2)


def face_frame_counts_once():
    env.clean_scene()
    ff = tff.BaseFaceFrameCabinet()
    ff.create("FaceFrame")
    env.settle()
    opening = next(o for o in ff.obj.children_recursive if o.get(tff.TAG_OPENING_CAGE)
                   and not any(c.get(tff.TAG_OPENING_CAGE) for c in o.children_recursive))
    opening.face_frame_opening.front_type = 'PULLOUT'
    cabinet, _box = convert.read_cabinet(ff.obj)
    _fields, losses = convert_core.translate(cabinet)
    found = {loss.key: loss.count for loss in losses}
    check("NTM3: o basculante de puxar conta uma vez", convert_core.SPECIAL_FRONT not in found
          and found.get(convert_core.DRAWERS) == 1, str(found))
    return ff.obj


def unread_is_loss():
    env.clean_scene()
    root = frameless("Balcao C", 0.0)
    env.settle()
    _root, adapter = adapters.for_object(root)
    original = adapter.read

    def broken(obj):
        raise KeyError("dado inesperado")
    adapter.read = broken
    try:
        cabinet, _box = convert.read_cabinet(root)
    finally:
        adapter.read = original
    _fields, losses = convert_core.translate(cabinet)
    lines = convert.report_lines([convert.Result(root.name, cabinet.library, "Módulo", losses)])
    check("HUWF: falha do leitor aparece como perda", "Frentes não lidas" in lines[0] and "sem perdas" not in lines[0],
          lines[0])


def homonymous_groups():
    base = tempfile.mkdtemp()
    os.makedirs(os.path.join(base, "Cozinha"))
    for path in (os.path.join(base, "Torre.blend"), os.path.join(base, "Cozinha", "Torre.blend")):
        open(path, "wb").close()
    original = ops_library.get_all_cabinet_group_paths
    ops_library.get_all_cabinet_group_paths = lambda: [base]
    try:
        items = groups.group_items()
    finally:
        ops_library.get_all_cabinet_group_paths = original
    check("ORRG: o homônimo de outra pasta entra na lista", len(items) == 2 and len({p for _n, p in items}) == 2,
          str(items))


def main():
    rollback()
    face_frame_counts_once()
    unread_is_loss()
    homonymous_groups()


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_5NLX_legacy: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
