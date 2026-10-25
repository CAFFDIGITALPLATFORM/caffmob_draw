"""Protótipo da premissa 3 (feature 067, T007; D-12): editar um campo de `Scene.btm_selection` cujo setter muda a
malha de OUTRO objeto (a peça do snapshot) gera um só passo de Desfazer, que restaura a malha, a matriz e o material.

Precisa de janela (o Desfazer do Blender é o da tela):
    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_proto_undo_campo.py

O campo de teste é registrado aqui, no mesmo molde dos campos virtuais (get/set, `options=set()`), e o setter chama
`target/part_edit.resize_authored`, que é o caminho da peça autoral. O passo é empurrado como a interface empurra
depois de editar um campo (`ed.undo_push`).
"""

import os
import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _authored_env as authored_env  # noqa: E402
from caffmob_draw.target import part_edit  # noqa: E402

FAILURES = []
state = {}


def check(ok, label):
    print(("OK   " if ok else "FALHA ") + label, flush=True)
    if not ok:
        FAILURES.append(label)


def _get(_self):
    obj = bpy.data.objects.get(state['name'])
    values = [v.co.x for v in obj.data.vertices]
    return max(values) - min(values)


def _set(_self, value):
    part_edit.resize_authored(bpy.data.objects.get(state['name']), 0, value)


def snapshot(obj):
    return ([tuple(v.co) for v in obj.data.vertices], [tuple(r) for r in obj.matrix_world],
            obj.active_material.name if obj.active_material else None, obj.data.name)


def tick():
    try:
        ctx = bpy.context
        win = ctx.window_manager.windows[0]
        area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        env.clean_scene()
        root, body = authored_env.tower("Torre", x=0)
        material = bpy.data.materials.new("Branco")
        body.data.materials.append(material)
        sibling = bpy.data.objects.new("Irmã", body.data)            # malha compartilhada com uma irmã
        ctx.collection.objects.link(sibling)
        state['name'] = body.name
        bpy.types.Scene.btm_proto_067 = bpy.props.FloatProperty(get=_get, set=_set, options=set())
        env.settle()
        bpy.ops.ed.undo_push(message="Antes do campo")
        before = snapshot(body)
        sibling_before = [tuple(v.co) for v in sibling.data.vertices]
        ctx.scene.btm_proto_067 = 0.9                                # o campo do painel, 600 → 900 mm
        bpy.ops.ed.undo_push(message="Campo da peça")
        body = bpy.data.objects[state['name']]
        check(abs(ctx.scene.btm_proto_067 - 0.9) < 1e-6, "o setter muda a malha da peça")
        check(body.data is not bpy.data.objects["Irmã"].data, "a malha compartilhada virou cópia só da peça")
        check([tuple(v.co) for v in bpy.data.objects["Irmã"].data.vertices] == sibling_before, "a irmã não mudou")
        with ctx.temp_override(window=win, area=area, region=region):
            bpy.ops.ed.undo()
        env.settle()
        body = bpy.data.objects[state['name']]
        check(snapshot(body) == before, "um passo de Desfazer restaura vértices, matriz, material e malha")
        check(abs(ctx.scene.btm_proto_067 - 0.6) < 1e-6, "o campo volta a 600 mm")
    except Exception:
        traceback.print_exc()
        FAILURES.append("exceção")
    print(f"blender_067_proto_undo_campo: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
    os._exit(1 if FAILURES else 0)


bpy.app.timers.register(tick, first_interval=2.0)
