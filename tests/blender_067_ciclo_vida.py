"""Ciclo de vida da 067 (T022; D-31, RF-140, RF-141). Organizado por seção de onda: cada onda acrescenta a sua.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_ciclo_vida.py

Onda 1:
- recarregar o addon 3× não duplica handler, timer nem atalho;
- salvar e reabrir conserva o uid da peça e o veio;
- arquivo antigo com driver ou animação nos campos virtuais (nomes antigos e novos) abre sem eles e sem perder objeto.

Onda 2:
- salvar e reabrir conserva `btm_finish`, `btm_part.finish_role` e o atributo `btm_face_role`;
- recarregar o addon 3× deixa um único atalho U.

Onda 3:
- salvar e reabrir conserva `btm_grain_rot`, `btm_part.grain` e a calibração do material.

Onda 4:
- salvar e reabrir conserva `btm_edgeband` e `btm_cut_exclude`;
- recarregar o addon 3× não duplica o handler da sincronia da fita.

Onda 5:
- salvar e reabrir conserva o papel e a dobradiça das frentes, o caminho do subvão e os mecanismos.

Onda 6:
- salvar e reabrir conserva as posições salvas com `pivot`, `anchor` e `orientation`.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
import caffmob_draw as addon  # noqa: E402
from caffmob_draw.cutting import part_sources  # noqa: E402
from caffmob_draw.geometry_free import mesh as geometry_mesh  # noqa: E402

FAILURES = []
HANDLERS = ('depsgraph_update_post', 'load_post', 'undo_post', 'redo_post', 'save_pre', 'save_post')


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def census():
    handlers = {name: len(getattr(bpy.app.handlers, name)) for name in HANDLERS}
    kc = bpy.context.window_manager.keyconfigs.addon
    keymaps = sum(len(km.keymap_items) for km in kc.keymaps) if kc is not None else 0
    from caffmob_draw.overlays import side_cotas
    return handlers, keymaps, bpy.app.timers.is_registered(side_cotas._tick)


def wave_1(folder):
    first = census()
    for _ in range(3):
        addon.unregister()
        addon.register()
    check(census() == first, "recarregar 3× não duplica handler, atalho nem timer", f"{first} → {census()}")

    env.clean_scene()
    plate = geometry_mesh.create_object(bpy.context, 'PLACA')
    plate.btm_part.grain = 'V'
    uid = part_sources.ensure_module_uid(plate)
    name = plate.name
    scene = bpy.context.scene
    anim = scene.animation_data_create()
    # Os campos não são animáveis (`driver_add` recusa); um arquivo antigo traz a curva gravada: cria direto.
    for path in ('btm_selection.width', 'btm_selection.part_a', 'btm_selection.multi_thickness'):
        anim.drivers.new(path).driver.expression = "1.0"
    count = len(bpy.data.objects)
    path = os.path.join(folder, "ciclo.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    plate = bpy.data.objects.get(name)
    check(plate is not None and plate.btm_part.grain == 'V', "salvar e reabrir conserva o veio")
    check(plate is not None and plate.get(part_sources.UID_PROP) == uid, "salvar e reabrir conserva o uid")
    anim = bpy.context.scene.animation_data
    left = [fc.data_path for fc in (anim.drivers if anim else ()) if fc.data_path.startswith('btm_selection.')]
    check(not left, "drivers nos campos virtuais (nomes antigos e novos) saem na abertura", str(left))
    check(len(bpy.data.objects) == count, "nenhum objeto se perde")


def u_keymaps():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc is None:
        return None
    return sum(1 for km in kc.keymaps for i in km.keymap_items if i.idname == 'caffmob.component_from_selection')


def wave_2(folder):
    for _ in range(3):
        addon.unregister()
        addon.register()
    count = u_keymaps()
    check(count in (None, 1), "recarregar 3× deixa um único atalho U", str(count))

    env.clean_scene()
    from caffmob_draw.customize import finish, finish_core as fc
    assert bpy.ops.caffmob.cabinet_builder(width=0.6) == {'FINISHED'}
    module = bpy.context.object
    env.settle()
    oak = bpy.data.materials.new("Carvalho 067")
    finish.apply(module, (fc.EXTERNAL,), oak)
    bpy.ops.mesh.primitive_cube_add(size=0.3, location=(2, 0, 0))
    cube = bpy.context.object
    cube.btm_part.finish_role = 'INTERNAL'
    names = (module.name, cube.name)
    path = os.path.join(folder, "ciclo_onda2.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    module, cube = (bpy.data.objects.get(n) for n in names)
    entries = [(i.domain, i.material.name if i.material else '', i.source) for i in module.btm_finish] if module else []
    check(entries == [(fc.EXTERNAL, "Carvalho 067", 'USER')], "salvar e reabrir conserva btm_finish", str(entries))
    check(cube is not None and cube.btm_part.finish_role == 'INTERNAL', "salvar e reabrir conserva finish_role")
    check(module is not None and finish.face_roles(module) is not None, "salvar e reabrir conserva btm_face_role")


def wave_3(folder):
    env.clean_scene()
    from caffmob_draw.texture_library import grain
    mat = bpy.data.materials.new("Textura 067")
    img_path = os.path.join(folder, "veio.png")
    img = bpy.data.images.new("veio", 8, 16)
    img.filepath_raw, img.file_format = img_path, 'PNG'
    img.save()
    from caffmob_draw.object_library import retexture
    mat = retexture.image_material(img_path, 300, 600)
    check(mat.get(grain.CALIBRATION) == 'V', "imagem em pé nasce calibrada V", str(mat.get(grain.CALIBRATION)))
    grain.calibrate(mat, 'H')
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    plate = bpy.context.object
    plate.data.transform(__import__('mathutils').Matrix.Diagonal((0.4, 0.018, 0.7, 1.0)))
    plate.data.materials.append(mat)
    bpy.context.view_layer.update()                 # a caixa da malha só vale depois do update
    plate.btm_part.grain = 'V'
    value = tuple(plate.get(grain.ATTR))
    names = (plate.name, mat.name)
    path = os.path.join(folder, "ciclo_onda3.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    plate, mat = bpy.data.objects.get(names[0]), bpy.data.materials.get(names[1])
    check(plate is not None and plate.btm_part.grain == 'V', "salvar e reabrir conserva btm_part.grain")
    check(plate is not None and tuple(plate.get(grain.ATTR, ())) == value and any(value),
          "salvar e reabrir conserva btm_grain_rot", str(value))
    check(mat is not None and mat.get(grain.CALIBRATION) == 'H', "salvar e reabrir conserva a calibração")


def wave_4(folder):
    from caffmob_draw.edgeband import sync as band_sync
    for _ in range(3):
        addon.unregister()
        addon.register()
    count = sum(1 for h in bpy.app.handlers.depsgraph_update_post if h.__name__ == band_sync.on_update.__name__
                and h.__module__ == band_sync.on_update.__module__)
    check(count == 1, "recarregar 3× deixa uma única sincronia da fita", str(count))
    env.clean_scene()
    import _authored_env as authored_env
    from caffmob_draw.aggregates import ops_authored
    from caffmob_draw.edgeband import core, pieces
    root = bpy.data.objects.new("Componente fita", None)
    bpy.context.collection.objects.link(root)
    plates = [authored_env.cube(f"Chapa fita {i}", (0.6, 0.4, 0.015), (0, 0, 0.0075 + i * 0.015), root)
              for i in range(2)]
    env.settle()
    ops_authored.adopt(root, [root] + plates)
    authored_env.select([root])
    bpy.context.view_layer.update()
    mat = bpy.data.materials.new("Fita ciclo")
    assert bpy.ops.caffmob.edgeband_apply('EXEC_DEFAULT', material=mat.name) == {'FINISHED'}
    before = sorted((o.btm_edgeband.uid, o.btm_edgeband.edge_keys, round(o.btm_edgeband.coverage_width, 6))
                    for o in pieces.bands_of(root))
    path = os.path.join(folder, "ciclo_onda4.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    root = bpy.data.objects.get("Componente fita")
    bands = pieces.bands_of(root)
    after = sorted((o.btm_edgeband.uid, o.btm_edgeband.edge_keys, round(o.btm_edgeband.coverage_width, 6))
                   for o in bands)
    check(after == before and len(after) == 4, "salvar e reabrir conserva btm_edgeband")
    check(all(o.btm_cut_exclude and o.btm_edgeband.owner == root for o in bands),
          "salvar e reabrir conserva btm_cut_exclude e o vínculo")
    check(all(core.loads(o.btm_edgeband.edge_keys) for o in bands), "as chaves das bordas voltam")


def wave_5(folder):
    env.clean_scene()
    from caffmob_draw import mechanisms
    from caffmob_draw.cabinet_editor import bridge
    from caffmob_draw.customize.adapters import btm
    from caffmob_draw.geometry import subspace_fronts
    ctx = bpy.context
    assert bpy.ops.caffmob.cabinet_builder(width=1.0, door_swing='DOUBLE') == {'FINISHED'}
    quick = ctx.object
    assert bpy.ops.caffmob.cabinet_builder(width=1.0, door_swing='NONE') == {'FINISHED'}
    split = ctx.object
    split.location.x = 2.0
    env.settle()
    root_path = next(iter(bridge.division_context(ctx, split)[0]))
    bridge.add_division(ctx, split, {'space': root_path, 'orientation': 'VERTICAL'})
    left = sorted(p for p in btm.space_boxes(ctx, split) if p not in ('module', root_path))[0]
    bridge.edit(ctx, split, 'FRONT', {'path': bridge.library_opening(ctx, split, left), 'front': 'DRAWERS',
                                      'drawer_count': 3})
    hinges = sorted(d.get('btm_front_hinge') for d in quick.children if d.type == 'MESH')
    names = (quick.name, split.name)
    path = os.path.join(folder, "ciclo_onda5.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    quick, split = (bpy.data.objects.get(n) for n in names)
    check(sorted(d.get('btm_front_hinge') for d in quick.children if d.type == 'MESH') == hinges == ['L', 'R']
          and all(d.get('hb_part_role') == 'DOOR' for d in quick.children if d.type == 'MESH'),
          "salvar e reabrir conserva papel e dobradiça das portas")
    drawers = [o for o in subspace_fronts.fronts_of(split, left) if o.get('hb_part_role') == 'DRAWER_FRONT']
    check(len(drawers) == 3 and subspace_fronts.front_type(split, left) == ('DRAWERS', 3)
          and subspace_fronts.holder(split, left, create=False) is not None,
          "salvar e reabrir conserva o caminho do subvão e as gavetas")
    check(all(mechanisms.of(d) is not None and mechanisms.of(d).kind == mechanisms.DRAWER for d in drawers),
          "salvar e reabrir conserva os mecanismos")


def wave_6(folder):
    env.clean_scene()
    from caffmob_draw.move_over import rotation as rot
    item = bpy.context.scene.btm_saved_positions.add()
    item.name, item.rotation, item.b_side = "Posição com giro", 30.0, 'RIGHT'
    item.pivot, item.anchor = 'C100', 'C011'
    item.orientation = rot.axis_angle(rot.AXES['Y'], 30.0)
    expected = (item.pivot, item.anchor, tuple(round(v, 6) for v in item.orientation))
    path = os.path.join(folder, "ciclo_onda6.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    bpy.ops.wm.open_mainfile(filepath=path)
    found = [(i.pivot, i.anchor, tuple(round(v, 6) for v in i.orientation))
             for i in bpy.context.scene.btm_saved_positions if i.name == "Posição com giro"]
    check(found == [expected], "salvar e reabrir conserva pivô, âncora e orientação da posição salva", str(found))


try:
    with fx.banco_temporario(), tempfile.TemporaryDirectory(prefix="caffmob_067_ciclo_") as folder:
        wave_1(folder)
        wave_2(folder)
        wave_3(folder)
        wave_4(folder)
        wave_5(folder)
        wave_6(folder)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_ciclo_vida: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
