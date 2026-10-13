"""Aplicar textura do catálogo (feature 014, T025; RN-05, RN-06, RN-13).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_014_apply.py

Com a imagem "baixada" (a miniatura do pacote copiada para o cache do usuário):
- peça: material de imagem do catálogo (`btm_texture_id`) e gravado na personalização da peça;
- imagem em pé numa peça: variante `ROTATED` (veio); objeto solto não gira;
- frente: todas as malhas da frente; módulo: todas as peças; mesma textura de novo reaproveita o material;
- sem alvo válido e sem internet com a imagem fora do cache: aviso, nada muda.
"""

import os
import shutil
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from caffmob_draw.customize.adapters import common  # noqa: E402
from caffmob_draw.product_libraries.frameless import types_frameless as tf  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402
from caffmob_draw.texture_library import apply, catalog, downloads  # noqa: E402

ctx = bpy.context
FAILURES = []


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def fake_download(item_id):
    entry = catalog.item(item_id)
    dest = downloads.cache_path(entry)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(catalog.thumb_path(entry), dest)
    return dest


def item_where(pred):
    for item in catalog.catalog_core.iter_items(catalog.load()[0]):
        if pred(item):
            return item["id"]
    raise AssertionError("nenhum item do catálogo atende")


def mats(obj):
    mod = common.gn_modifier(obj, 'GeoNodeCutpart')
    if mod is not None:
        from caffmob_draw import compat
        return {getattr(compat.get_gn_input(mod, 'Top Surface'), "name", None)}
    return {m.name for m in obj.data.materials if m}


def main():
    env.clean_scene()
    square = item_where(lambda i: i["px"][0] == i["px"][1])
    tall = item_where(lambda i: i["px"][1] > i["px"][0])
    for tid in (square, tall):
        fake_download(tid)

    # Armário CAFFMob: caixa e frentes pela personalização
    assert bpy.ops.caffmob.cabinet_builder(cabinet_type='BASE', width=0.6, line='COZ') == {'FINISHED'}
    root = ctx.view_layer.objects.active
    env.settle()
    door = next(o for o in root.children_recursive if classify.classify(o).kind == classify.FRONT)
    status, n = apply.apply(apply.targets(root), square)
    names = mats(root)
    mat = bpy.data.materials.get(next(iter(names))) if names else None
    check("módulo CAFFMob: caixa com o material de imagem", status == apply.APPLIED and mat is not None
          and mat.get("btm_texture_id") == square, f"{status} {names}")
    caixa = {i.group: i.material for i in root.btm_custom.group_materials}.get('CAIXA')
    check("módulo CAFFMob: gravado no grupo CAIXA", caixa == (mat.name if mat else "?"), str(caixa))
    check("módulo CAFFMob: a porta não muda", mats(door) != names, str(mats(door)))
    status, n = apply.apply(apply.targets(door), tall)
    check("frente CAFFMob: portas com a textura e front_material gravado",
          status == apply.APPLIED and root.btm_custom.front_material in mats(door) and mats(root) == names,
          f"{root.btm_custom.front_material} {mats(door)}")
    count = len(bpy.data.materials)
    apply.apply(apply.targets(door), tall)
    check("mesma textura de novo reaproveita o material", len(bpy.data.materials) == count)

    # Peça GeoNodeCutpart (biblioteca herdada): personalização da peça e veio
    legacy = tf.BaseCabinet()
    legacy.create("Frameless")
    env.settle()
    parts = [o for o in legacy.obj.children_recursive if common.is_cutpart(o)]
    part = next((p for p in parts if classify.classify(p).kind == classify.PART), None)
    if part is None:
        check("frameless com peça GeoNodeCutpart", False, str([p.name for p in parts][:5]))
    else:
        status, n = apply.apply([part], square)
        names = mats(part)
        check("peça: aplicada e gravada na personalização (vence grupo e vão)", status == apply.APPLIED
              and part.btm_custom.material in names and not part.btm_custom.material.endswith("ROTATED"),
              f"{part.btm_custom.material} {names}")
        apply.apply([part], tall)
        check("imagem em pé numa peça usa a variante ROTATED (RN-06)", any(n.endswith("ROTATED") for n in mats(part)),
              str(mats(part)))

    bpy.ops.mesh.primitive_cube_add()
    cube = ctx.active_object
    apply.apply(apply.targets(cube), tall)
    check("objeto solto: material sem girar", mats(cube) and all(not n.endswith("ROTATED") for n in mats(cube)),
          str(mats(cube)))

    # T046: aplicar à seleção e mudar o tamanho real
    for obj in ctx.selected_objects:
        obj.select_set(False)
    cube.select_set(True)
    ctx.view_layer.objects.active = cube
    assert bpy.ops.caffmob.texture_apply(item_id=square) == {'FINISHED'}
    check("operador aplica à seleção", any("anis" in n for n in mats(cube)), str(mats(cube)))
    result = bpy.ops.caffmob.texture_size('EXEC_DEFAULT', width_mm=1200.0, height_mm=900.0, keep_ratio=False)
    names = mats(cube)
    mat = bpy.data.materials.get(next(iter(names)))
    mapping = next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')
    scale = tuple(round(v, 4) for v in mapping.inputs['Scale'].default_value)
    check("tamanho real muda para 1200 × 900 mm", result == {'FINISHED'} and "1200 × 900 mm" in mat.name
          and scale[:2] == (round(1 / 1.2, 4), round(1 / 0.9, 4)) and mat.get("btm_texture_id") == square,
          f"{mat.name} {scale}")

    # T045: relevo do fabricante ligado ao material quando a imagem está no cache
    from caffmob_draw.texture_library import bump
    bumpy = item_where(lambda i: bool(i.get("bump")))
    fake_download(bumpy)
    relief = bump.bump_entry(catalog.item(bumpy))
    relief_path = downloads.cache_path(relief)
    shutil.copy(catalog.thumb_path(catalog.item(bumpy)), relief_path)
    bpy.ops.mesh.primitive_cube_add()
    plate = ctx.active_object
    apply.apply([plate], bumpy)
    mat = bpy.data.materials.get(next(iter(mats(plate))))
    node = mat.node_tree.nodes.get(bump.NODE_NAME)
    bsdf = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    check("relevo ligado à Normal do material (RF-14)", node is not None and bsdf.inputs['Normal'].is_linked
          and node.image.colorspace_settings.name == 'Non-Color', mat.name)
    check("textura sem relevo não ganha o nó", bump.NODE_NAME not in
          bpy.data.materials.get(next(iter(mats(cube)))).node_tree.nodes)

    status, msg = apply.apply([], square)
    check("sem alvo: aviso", status == apply.ERROR and msg, msg)

    original = downloads.online
    downloads.online = lambda: False
    missing = item_where(lambda i: i["id"] not in (square, tall))
    before = mats(cube)
    status, msg = apply.apply([cube], missing)
    downloads.online = original
    check("sem internet e fora do cache: aviso claro, nada muda", status == apply.ERROR and "internet" in msg
          and mats(cube) == before, msg)


try:
    main()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_014_apply: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
