"""Reprodução e regressão de BUG-20261012-YUDY: a cópia nativa (Shift+D) de um módulo ganha um `btm_uid` novo.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_YUDY_module_uid.py

- os dois módulos saem de `iter_modules` com uids diferentes, e o original mantém o dele (geometry_free EC-12);
- as peças dos dois módulos não repetem uid na lista de peças.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.cutting import part_extractor, part_sources  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def main():
    env.clean_scene()
    assert bpy.ops.caffmob.cabinet_builder(cabinet_type='BASE', width=0.6) == {'FINISHED'}
    original = ctx.view_layer.objects.active
    uid = part_sources.iter_modules(ctx.scene)[0].uid
    for obj in ctx.selected_objects:
        obj.select_set(False)
    original.select_set(True)
    ctx.view_layer.objects.active = original
    bpy.ops.object.duplicate()
    copy = ctx.view_layer.objects.active
    env.settle()
    uids = {m.name: m.uid for m in part_sources.iter_modules(ctx.scene)}
    check("YUDY: os dois módulos têm uids diferentes", len(set(uids.values())) == 2, str(uids))
    check("YUDY: o original mantém o uid", uids.get(original.name) == uid and copy.get('btm_uid') != uid,
          f"{uid} → {uids}")
    parts = [p.uid for p in part_extractor.extract_production_parts(ctx)[0]]
    check("YUDY: nenhuma peça repete uid", bool(parts) and len(parts) == len(set(parts)),
          f"{len(parts)} peças, {len(set(parts))} uids")


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_bug_YUDY_module_uid: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
