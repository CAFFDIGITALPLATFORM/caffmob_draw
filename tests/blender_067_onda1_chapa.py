"""Chapa pelo painel (feature 067, T019; RF-007 a RF-009, RF-016, D-06, D-12).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda1_chapa.py

- peça de módulo de biblioteca: campos somente leitura com o motivo, e digitar nela não muda nada;
- peça autoral (membro): mudar a medida muda só ela, nunca irmãos nem o envelope do armário, e um Desfazer restaura
  vértices, matriz, material e papel;
- malha compartilhada vira cópia própria antes da edição; dado linked é recusado;
- `aggregates/stretch.resize` nunca é chamado pela edição da chapa.
"""

import os
import sys
import tempfile
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _fixtures_067 as fx  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw.aggregates import stretch  # noqa: E402
from caffmob_draw.target import part_edit, view  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402


def mesh_state(obj):
    return ([tuple(round(c, 6) for c in v.co) for v in obj.data.vertices], [tuple(r) for r in obj.matrix_world],
            obj.active_material.name if obj.active_material else None, obj.btm_member.role)


def body(w):
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False
    calls = []
    original_resize = stretch.resize
    stretch.resize = lambda *a, **k: calls.append(a) or original_resize(*a, **k)

    # Peça de biblioteca: somente leitura com o motivo.
    fx.select([s.part])
    part = j.refresh()
    sheet = next(sec for sec in view.build(part, view.COMPLETE).sections if sec.id == 'sheet')
    fields = [f for f in sheet.items if isinstance(f, view.Field) and f.prop.startswith('part_')]
    j.check(fields and all(f.read_only and f.reason for f in fields), "peça de biblioteca: somente leitura com motivo")
    op.remember_drawn(part)
    before = [tuple(v.co) for v in s.part.data.vertices]
    bpy.context.scene.btm_selection.part_thickness = 0.03
    j.check(bool(bpy.context.window_manager.get(op.ERROR_KEY)), "digitar na peça de biblioteca diz o motivo")
    j.check([tuple(v.co) for v in s.part.data.vertices] == before, "e não muda a peça")

    # Peça autoral: só ela muda; o armário e a irmã ficam; um Desfazer restaura tudo.
    material = bpy.data.materials.new("Carvalho")
    s.member.data.materials.append(material)
    sibling = bpy.data.objects.new("Irmã", s.member.data)           # malha compartilhada
    bpy.context.collection.objects.link(sibling)
    sibling.parent = s.authored
    env.settle()
    fx.select([s.member])
    member = j.refresh()
    op.remember_drawn(member)
    size_before = tuple(s.authored.btm_authored.size_local)
    state_before = mesh_state(s.member)
    sibling_before = [tuple(v.co) for v in sibling.data.vertices]
    w.push("Antes da medida")
    field = 'part_a' if member.measures.face[0].field == 'WIDTH' else 'part_b'
    old_value = getattr(bpy.context.scene.btm_selection, field)
    setattr(bpy.context.scene.btm_selection, field, old_value + 0.3)
    w.push("Medida da peça")
    member_obj = bpy.data.objects[s.member.name]
    j.check(mesh_state(member_obj)[0] != state_before[0], "a peça autoral mudou de medida")
    j.check(member_obj.data is not bpy.data.objects["Irmã"].data, "a malha compartilhada virou cópia só da peça")
    j.check([tuple(v.co) for v in bpy.data.objects["Irmã"].data.vertices] == sibling_before, "a irmã não mudou")
    j.check(tuple(bpy.data.objects[s.authored.name].btm_authored.size_local) == size_before,
            "o envelope do armário não esticou")
    j.check(not calls, "stretch.resize nunca é chamado", str(len(calls)))
    member_name = member_obj.name
    w.undo()
    j.check(mesh_state(bpy.data.objects[member_name]) == state_before,
            "um Desfazer restaura vértices, matriz, material e papel")

    # Dado linked é recusado.
    folder = tempfile.mkdtemp(prefix="caffmob_067_linked_")
    source = os.path.join(folder, "biblioteca.blend")
    mesh = bpy.data.meshes.new("Ligada")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 0.02, 0), (0, 0.02, 0), (0, 0, 1), (1, 0, 1), (1, 0.02, 1), (0, 0.02, 1)],
                     [], [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    obj = bpy.data.objects.new("Ligada", mesh)
    bpy.data.libraries.write(source, {obj}, fake_user=True)
    bpy.data.objects.remove(obj)
    with bpy.data.libraries.load(source, link=True) as (data_from, data_to):
        data_to.objects = ["Ligada"]
    linked = data_to.objects[0]
    bpy.context.collection.objects.link(linked)
    try:
        part_edit.resize_authored(linked, 0, 0.5)
        refused = False
    except part_edit.PartEditError:
        refused = True
    j.check(refused, "dado linked é recusado")
    stretch.resize = original_resize


j.run("blender_067_onda1_chapa", body)
