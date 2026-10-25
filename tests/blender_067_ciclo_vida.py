"""Ciclo de vida da 067 (T022; D-31, RF-140, RF-141). Organizado por seção de onda: cada onda acrescenta a sua.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_ciclo_vida.py

Onda 1:
- recarregar o addon 3× não duplica handler, timer nem atalho;
- salvar e reabrir conserva o uid da peça e o veio;
- arquivo antigo com driver ou animação nos campos virtuais (nomes antigos e novos) abre sem eles e sem perder objeto.
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


try:
    with fx.banco_temporario(), tempfile.TemporaryDirectory(prefix="caffmob_067_ciclo_") as folder:
        wave_1(folder)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_ciclo_vida: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
