"""Adaptadores por tipo (feature 067, T021; RF-011, RF-014, RF-017 a RF-026).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda1_tipos.py

Geometria livre girada, frente BTM com a própria largura, folha, porta BTM DOOR como Porta, revestimento sem
refazer ao digitar, piso e teto, luz, câmera, anotação, objeto livre e seleção múltipla com "Múltiplos" num passo de
Desfazer.
"""

import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw.cladding import sync as cladding_sync  # noqa: E402
from caffmob_draw.geometry_free import mesh as geometry_mesh  # noqa: E402
from caffmob_draw.selection import classify  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402
from caffmob_draw.target import view  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402


def target_of(objs, active=None):
    fx.select(objs, active)
    return j.refresh()


def section_ids(target, mode=view.COMPLETE):
    return {s.id for s in view.build(target, mode).sections}


def props(target):
    return {(f.data, f.prop) for f in view.fields(view.build(target, view.COMPLETE))}


def body(w):
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False

    # Geometria livre deitada e girada 90° em X: passa a mostrar Largura e Altura (RF-011).
    plate = geometry_mesh.create_object(bpy.context, 'PLACA')
    plate.btm_geometry.plane, plate.btm_geometry.width, plate.btm_geometry.depth = 'XY', 0.8, 0.4
    geometry_mesh.update(plate)
    plate.rotation_euler.x = math.radians(90)
    env.settle()
    t = target_of([plate])
    j.check([m.field for m in t.measures.face] == ['WIDTH', 'HEIGHT'], "placa deitada girada 90° em X: Largura e Altura",
            str([m.field for m in t.measures.face]))
    j.check(not any(f.label and "biblioteca" in f.label for f in view.fields(view.build(t, view.COMPLETE))),
            "geometria sem o texto de limites de biblioteca")

    # Frente BTM: a largura dela, não a do módulo (RF-014).
    front = next((o for o in s.btm_module.children_recursive if classify.classify(o).kind == classify.FRONT
                  and o.type == 'MESH'), None)
    if front is not None:
        t = target_of([front])
        width = next(m.value for m in t.measures.face if m.field == 'WIDTH')
        j.check(t.kind == r.FRONT and abs(width - s.btm_module.btm_cabinet.width) > 1e-3,
                "frente BTM mostra a própria largura", f"{width} × {s.btm_module.btm_cabinet.width}")
    else:
        j.check(False, "módulo rápido sem frente para conferir")

    # Folha: seção própria e cabeçalho "Folha" (RF-017).
    t = target_of([s.leaf])
    j.check('leaf' in section_ids(t, view.ESSENTIAL) and view.build(t).header.kind_label == "Folha",
            "folha com seção própria no Essencial")

    # Porta BTM DOOR aparece como Porta; sem folha gerada, o painel diz isso (RF-019).
    data = bpy.data.meshes.new("Abertura")
    opening = bpy.data.objects.new("Abertura", data)
    bpy.context.collection.objects.link(opening)
    opening.btm_plane.object_kind = 'OPENING'
    opening.btm_opening.opening_type = 'DOOR'
    t = target_of([opening])
    model = view.build(t, view.COMPLETE)
    notes = [i.text for sec in model.sections for i in sec.items if isinstance(i, view.Note)]
    j.check(model.header.kind_label == "Porta", "abertura BTM DOOR é Porta", model.header.kind_label)
    j.check(any("sem folha" in n for n in notes), "porta sem folha gerada diz isso")

    # Revestimento: os valores do selecionado; digitar não refaz; "Aplicar" refaz (RF-020).
    calls = []
    original = cladding_sync.sync
    cladding_sync.sync = lambda root, *a, **k: calls.append(root) or original(root, *a, **k)
    t = target_of([s.cladding])
    j.check(('cladding', 'width_mm') in props(t), "revestimento mostra os parâmetros dele")
    draft = bpy.context.window_manager.btm_cladding_draft
    j.check(abs(draft.width_mm - s.cladding.btm_cladding.width_mm) < 1e-6, "o rascunho traz os valores do selecionado")
    signature = s.cladding.btm_cladding.params_hash
    draft.width_mm = 120.0
    env.settle()
    # O handler do revestimento roda a cada atualização (e não refaz se o hash não mudou): o que vale é o revestimento.
    j.check(abs(s.cladding.btm_cladding.width_mm - 120.0) > 1e-6 and s.cladding.btm_cladding.params_hash == signature,
            "digitar não refaz o revestimento")
    with w.override():
        result = bpy.ops.caffmob.target_cladding_apply()
    j.check(result == {'FINISHED'} and abs(s.cladding.btm_cladding.width_mm - 120.0) < 1e-6
            and s.cladding.btm_cladding.params_hash != signature,
            "Aplicar leva o valor ao revestimento e o refaz", f"{result} {len(calls)}")
    cladding_sync.sync = original

    # Piso, teto, luz, câmera, anotação e objeto livre.
    for name, wanted in (('floor', 'surface'), ('ceiling', 'surface'), ('light', 'light'), ('camera', 'camera')):
        t = target_of([getattr(s, name)])
        j.check(wanted in section_ids(t), f"{name}: seção {wanted}")
    t = target_of([s.light])
    j.check(('light', 'size') in props(t) and ('light', 'shadow_soft_size') not in props(t), "luz de área: tamanho")
    s.light.data.type = 'POINT'
    t = target_of([s.light])
    j.check(('light', 'shadow_soft_size') in props(t) and ('light', 'size') not in props(t), "luz pontual: raio")
    t = target_of([s.camera])
    j.check({('camera', 'lens'), ('camera', 'clip_start'), ('camera', 'type')} <= props(t), "câmera: lente e clipping")
    t = target_of([s.annotation])
    j.check(not any(p[0] == 'move_over' for p in props(t)), "anotação sem Mover Sobre")
    t = target_of([s.free])
    j.check(('object', 'scale') in props(t) and t.move_uid == s.free.session_uid, "objeto livre: transformação completa")

    # Seleção múltipla: 15/15/18 mostra "Múltiplos"; digitar 18 muda as três num passo de Desfazer (RF-026).
    sheets = []
    for i, thickness in enumerate((0.015, 0.015, 0.018)):
        g = geometry_mesh.create_object(bpy.context, 'PLACA')
        g.btm_geometry.plane, g.btm_geometry.thickness = 'XZ', thickness
        geometry_mesh.update(g)
        g.location = (5.0 + i, 5.0, 0.0)
        sheets.append(g)
    env.settle()
    t = target_of(sheets, sheets[0])
    op.remember_drawn(t)
    j.check(t.kind == r.MULTIPLE and len({round(v, 6) for v in t.multi_thickness}) > 1, "15/15/18 mostra Múltiplos")
    w.push("Antes da espessura comum")
    bpy.context.scene.btm_selection.multi_thickness = 0.018
    w.push("Espessura comum")
    names = [g.name for g in sheets]
    j.check(all(abs(bpy.data.objects[n].btm_geometry.thickness - 0.018) < 1e-6 for n in names),
            "digitar 18 muda as três")
    w.undo()
    j.check([round(bpy.data.objects[n].btm_geometry.thickness, 6) for n in names] == [0.015, 0.015, 0.018],
            "um Desfazer volta as três")


j.run("blender_067_onda1_tipos", body)
