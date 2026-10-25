"""Papel das frentes do módulo rápido (feature 067, T136; RF-102, RF-141, D-25).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda5_papel_frente.py

Um arquivo "1.8.0" de fixture (as três portas do módulo rápido e o Empty controlador, sem papel, dobradiça nem marca)
abre com:
- as portas como Frente, com `hb_part_role` e `btm_front_hinge` gravados, e o Empty com `btm_door_controller`;
- as portas abrindo para o mesmo lado de antes;
- abrir e fechar a porta sem marcar o plano de corte como desatualizado;
- a inspeção girando as portas (achadas pela marca e pela dobradiça);
- renomear uma porta para "Painel" sem mudar o tipo;
- abrir o arquivo 2× sem regravar nada;
- objeto só com o sufixo do nome, fora de módulo BTM, como Peça (ou objeto), nunca Frente.
"""

import math
import os
import sys
import tempfile
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import caffmob_draw as addon  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def doors(root):
    return sorted((c for c in root.children if c.type == 'MESH'), key=lambda o: o.name)


def angles(root):
    bpy.context.view_layer.update()
    return [tuple(round(math.degrees(v), 2) for v in d.matrix_world.to_euler()) for d in doors(root)]


def strip(obj):
    for key in ('hb_part_role', 'btm_front_hinge', 'btm_door_controller'):
        if key in obj:
            del obj[key]


def fixture(folder):
    env.clean_scene()
    roots = {}
    for i, swing in enumerate(('LEFT', 'RIGHT', 'FLIP')):
        assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing=swing) == {'FINISHED'}
        root = bpy.context.object
        root.location.x = i * 1.0
        roots[swing] = root.name
    env.settle()
    reference = {}
    for swing, name in roots.items():
        root = bpy.data.objects[name]
        root.btm_cabinet.door_open = 1.0
        reference[swing] = angles(root)
        root.btm_cabinet.door_open = 0.0
        for child in root.children:
            strip(child)                      # como era na 1.8.0
    loose = bpy.data.objects.new("Solta_Door_L", bpy.data.meshes.new("Solta"))
    bpy.context.collection.objects.link(loose)
    path = os.path.join(folder, "frentes_1_8_0.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
    return path, roots, reference


def open_file(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    addon.load_file_post(None) if hasattr(addon, 'load_file_post') else None


def run(folder):
    path, roots, reference = fixture(folder)
    open_file(path)
    for swing, name in roots.items():
        root = bpy.data.objects[name]
        found = doors(root)
        check(found and all(classify.classify(d).kind == classify.FRONT for d in found),
              f"{swing}: as portas abrem o arquivo como Frente")
        check(all(d.get('hb_part_role') in ('DOOR', 'TILT_OUT') and d.get('btm_front_hinge') for d in found),
              f"{swing}: papel e dobradiça gravados", str([(d.get('hb_part_role'), d.get('btm_front_hinge'))
                                                         for d in found]))
        controller = [c for c in root.children if c.type == 'EMPTY']
        check(controller and controller[0].get('btm_door_controller'), f"{swing}: o Empty ganhou a marca")
        root.btm_cabinet.door_open = 1.0
        check(angles(root) == reference[swing], f"{swing}: a porta abre para o mesmo lado",
              f"{reference[swing]} × {angles(root)}")
        root.btm_cabinet.door_open = 0.0
    loose = bpy.data.objects["Solta_Door_L"]
    check(classify.classify(loose).kind != classify.FRONT and not loose.get('hb_part_role'),
          "objeto só com o sufixo, fora de módulo BTM, não vira Frente")

    # Plano de corte calculado: abrir e fechar a porta não o marca como desatualizado.
    scene = bpy.context.scene
    scene['btm_nesting_sheets_count'] = 1
    scene.btm_settings.cut_plan_stale = False
    from caffmob_draw.inspection.adapters import btm as inspection_btm
    fronts = inspection_btm.find_fronts(scene)
    check(len(fronts) == 3, "a inspeção acha as três frentes pela marca e pela dobradiça", str(len(fronts)))
    front = fronts[0]
    before = angles(front.module_root)
    front.apply(90.0)
    bpy.context.view_layer.update()
    turned = angles(front.module_root)
    front.apply(0.0)
    bpy.context.view_layer.update()
    check(turned != before, "a inspeção gira as portas")
    check(not scene.btm_settings.cut_plan_stale, "abrir e fechar a porta não desatualiza o plano de corte")

    # Renomear não muda o tipo.
    door = doors(bpy.data.objects[roots['LEFT']])[0]
    door.name = "Painel"
    check(classify.classify(door).kind == classify.FRONT, "renomear a porta para Painel não muda o tipo")

    # Abrir 2× não regrava.
    from caffmob_draw.selection import migration_front_roles
    check(migration_front_roles.run() == 0, "rodar a M-08 de novo não regrava nada")


try:
    with tempfile.TemporaryDirectory(prefix="caffmob_067_frentes_") as tmp:
        run(tmp)
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda5_papel_frente: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
