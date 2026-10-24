"""Construir → Chapa (feature 067, T131; D-29, RF-012).

Precisa de janela (o Desfazer do Blender é o da tela):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda1_chapa_nova.py

Com o "Padrão Brasil" a chapa nasce com 15 mm e tipo MDF; com a Lateral do padrão ativo em 18 mm, a próxima nasce com
18 mm e a anterior não muda; 600 × 400 mm em pé, com a base no cursor 3D; o material "MDF Branco" é criado na
primeira chapa e reaproveitado; um Desfazer remove a chapa. O Padrão de Dimensões roda num banco temporário (D-35).
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
from caffmob_draw.geometry_free import materials  # noqa: E402
from caffmob_draw.standards import api  # noqa: E402

FAILURES = []


def check(ok, label):
    print(("OK   " if ok else "FALHA ") + label, flush=True)
    if not ok:
        FAILURES.append(label)


def close(a, b, tol=1e-5):
    return abs(a - b) < tol


def marked():
    return [m for m in bpy.data.materials if m.get(materials.MARK) == materials.MDF_BRANCO]


def sheet():
    assert bpy.ops.caffmob.geometry_sheet() == {'FINISHED'}
    return bpy.context.object


def tick():
    try:
        with fx.banco_temporario():
            run()
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"blender_067_onda1_chapa_nova: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


def run():
    ctx = bpy.context
    win = ctx.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    env.clean_scene()
    scene = ctx.scene
    api.ensure_ready(scene)
    api.set_active(scene, api.find_definition(scene, uid='builtin-br'))
    scene.cursor.location = (1.0, 2.0, 0.5)

    first = sheet()
    g = first.btm_geometry
    check(close(g.thickness, 0.015) and g.material == 'MDF', "Padrão Brasil: 15 mm e tipo MDF")
    env.settle()
    dims = first.dimensions
    check(close(dims.x, 0.6) and close(dims.z, 0.4) and close(dims.y, 0.015), "600 × 400 mm em pé (face para −Y)")
    low = [first.matrix_world @ v.co for v in first.data.vertices]
    check(close(min(p.z for p in low), 0.5) and close((min(p.x for p in low) + max(p.x for p in low)) / 2, 1.0),
          "base no cursor 3D")
    check(first.active_material is not None and first.active_material.get(materials.MARK) == materials.MDF_BRANCO,
          "cor pelo material \"MDF Branco\"")
    check(first.btm_part.grain == 'NONE', "veio Nenhum")
    second = sheet()
    check(len(marked()) == 1 and second.active_material == first.active_material, "a segunda chapa reaproveita o material")

    own = api.duplicate_definition(scene, api.find_definition(scene, uid='builtin-br'), "Marcenaria X")
    api.set_value(own, 'COZ.sheets.LAT.thickness', 18.0)
    api.set_active(scene, own)
    third = sheet()
    check(close(third.btm_geometry.thickness, 0.018), "Lateral do padrão em 18 mm: a próxima nasce com 18 mm")
    check(close(first.btm_geometry.thickness, 0.015), "a chapa já criada não muda")

    count = len(scene.objects)
    bpy.ops.ed.undo_push(message="Antes da chapa")
    with ctx.temp_override(window=win, area=area, region=region):
        assert bpy.ops.caffmob.geometry_sheet() == {'FINISHED'}
        bpy.ops.ed.undo_push(message="Chapa")      # a interface grava o passo do operador; por script, não grava
    check(len(scene.objects) == count + 1, "a chapa foi criada")
    with ctx.temp_override(window=win, area=area, region=region):
        bpy.ops.ed.undo()
    check(len(bpy.context.scene.objects) == count, "um Desfazer remove a chapa")


bpy.app.timers.register(tick, first_interval=2.0)
