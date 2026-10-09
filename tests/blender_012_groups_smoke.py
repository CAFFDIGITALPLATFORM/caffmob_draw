"""Fumaça da conversão dos grupos salvos das bibliotecas herdadas (feature 012, T069; RF-16, RN-16; D-29, D-30).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_groups_smoke.py

Dois grupos frameless gravados em `cabinet_groups/` (um com 2 gavetas): a conversão cria 2 módulos em "Geral" com os
mesmos nomes, lista as gavetas perdidas, deixa os `.blend` originais na pasta e não suja o arquivo aberto (mesma
contagem de objetos, malhas e materiais antes e depois). Depois disso, a oferta não volta.
"""

import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw import hb_utils  # noqa: E402
from caffmob_draw.customize import library_io  # noqa: E402
from caffmob_draw.legacy import groups  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.product_libraries.frameless.operators import ops_library  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def save_group(name, exterior):
    cab = tf.BaseCabinet()
    cab.default_exterior = exterior
    cab.create(name)
    hb_utils.run_calc_fix_until_stable(ctx, cab.obj)
    tree = {cab.obj, *cab.obj.children_recursive}
    path = os.path.join(ops_library.get_user_library_path(), f"{name}.blend")
    bpy.data.libraries.write(path, tree, fake_user=True)
    for obj in sorted(tree, key=lambda o: len(o.children_recursive)):
        bpy.data.objects.remove(obj, do_unlink=True)
    return path


def counts():
    return len(bpy.data.objects), len(bpy.data.meshes), len(bpy.data.materials), len(bpy.data.collections)


def main():
    env.clean_scene()
    paths = [save_group("Grupo Portas", 'Doors'), save_group("Grupo Gavetas", '2 Drawers')]
    groups.invalidate()
    check("2 grupos pendentes e oferta ligada", sorted(groups.pending_files()) == sorted(paths) and groups.should_offer())
    before = counts()
    saved, lines = groups.convert_pending(ctx)
    after = counts()
    check("2 módulos salvos com os mesmos nomes", sorted(saved) == ["Grupo Gavetas", "Grupo Portas"], str(saved))
    entries = [e for e in library_io.list_modules() if e["category"] == groups.TARGET_CATEGORY]
    check("módulos em Geral, com miniatura", sorted(e["name"] for e in entries) == ["Grupo Gavetas", "Grupo Portas"]
          and all(os.path.exists(e["png"]) for e in entries), str([(e["name"], os.path.exists(e["png"]))
                                                                 for e in entries]))
    check("relatório lista as gavetas", any("Gavetas" in line and "2" in line for line in lines), str(lines))
    check("originais continuam na pasta", all(os.path.exists(p) for p in paths))
    check("arquivo aberto sem dados soltos", before == after, f"{before} → {after}")
    check("a oferta não volta", not groups.should_offer() and not groups.pending_files())
    with ctx.temp_override(selected_objects=[]):
        result = bpy.ops.caffmob.module_insert(filepath=entries[0]["blend"])
    inserted = [o for o in ctx.scene.objects if o.btm_plane.object_kind == 'MODULE']
    check("módulo convertido insere como CAFFMob", 'FINISHED' in result and len(inserted) == 1, str(result))


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_012_groups_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
