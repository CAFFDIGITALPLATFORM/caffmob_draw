"""Seleção relacional (feature 067, T018; RF-001, RF-003, RF-004).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda1_selecao.py

- o cabeçalho diz o tipo e o escopo certos para os 15 tipos;
- o setter recusa, com motivo, quando a seleção troca depois de o painel ser desenhado (popup aberto) e não grava no
  objeto novo;
- "Selecionar conjunto" seleciona o dono num passo de Desfazer;
- o modo Essencial/Completa mora nas preferências, fora da cena e do Desfazer.
"""

import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
import _fixtures_067 as fx  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw import BTM_AddonPreferences  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402
from caffmob_draw.target import view  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

EXPECTED = {
    'btm_module': (r.MODULE, r.SCOPE_ASSEMBLY), 'hb_module': (r.MODULE, r.SCOPE_ASSEMBLY),
    'authored': (r.MODULE, r.SCOPE_ASSEMBLY), 'member': (r.MEMBER, r.SCOPE_PART), 'part': (r.PART, r.SCOPE_PART),
    'geometry': (r.GEOMETRY, r.SCOPE_OBJECT), 'front': (r.FRONT, r.SCOPE_PART), 'leaf': (r.LEAF, r.SCOPE_LEAF),
    'wall': (r.WALL, r.SCOPE_OBJECT), 'room_door': (r.OPENING, r.SCOPE_OBJECT), 'window': (r.OPENING, r.SCOPE_OBJECT),
    'cladding': (r.CLADDING, r.SCOPE_OBJECT), 'floor': (r.FLOOR, r.SCOPE_OBJECT), 'ceiling': (r.CEILING, r.SCOPE_OBJECT),
    'light': (r.LIGHT, r.SCOPE_OBJECT), 'camera': (r.CAMERA, r.SCOPE_OBJECT),
    'annotation': (r.ANNOTATION, r.SCOPE_OBJECT), 'free': (r.OTHER, r.SCOPE_OBJECT),
}


def body(w):
    s = fx.scene_15()
    bpy.context.scene.btm_component_select = False
    for name, (kind, scope) in EXPECTED.items():
        fx.select([getattr(s, name)])
        target = j.refresh()
        header = view.build(target).header
        label = ("Porta" if target.detail == 'DOOR' else "Janela") if kind == r.OPENING else r.KIND_LABELS[kind]
        j.check(target.kind == kind and target.scope == scope and header.kind_label == label,
                f"cabeçalho de {name}: {kind} · {scope}", f"{target.kind} · {target.scope}")
    fx.select([s.member])
    member = j.refresh()
    j.check(view.build(member).header.path == (s.authored.name, s.member.name), "caminho do dono no cabeçalho")

    # Popup aberto para a peça autoral; a seleção troca para a geometria; o valor digitado não pode ir para ela.
    op.remember_drawn(member)
    thickness = s.geometry.btm_geometry.thickness
    member_verts = [tuple(v.co) for v in s.member.data.vertices]
    fx.select([s.geometry])
    j.refresh()
    bpy.context.scene.btm_selection.part_thickness = 0.05
    error = bpy.context.window_manager.get(op.ERROR_KEY)
    j.check(bool(error), "o setter recusa com motivo quando a seleção trocou", str(error))
    j.check(abs(s.geometry.btm_geometry.thickness - thickness) < 1e-9, "o objeto novo não recebe o valor")
    j.check([tuple(v.co) for v in s.member.data.vertices] == member_verts, "o objeto antigo também não muda")

    # Selecionar conjunto: um passo de Desfazer.
    fx.select([s.member])
    op.remember_drawn(j.refresh())
    member_name = s.member.name
    w.push("Antes de selecionar o conjunto")
    with w.override():
        result = bpy.ops.caffmob.target_select_owner()
    w.push("Selecionar conjunto")          # a interface grava o passo do operador; chamado por script, não grava
    j.check(result == {'FINISHED'} and bpy.context.view_layer.objects.active == s.authored,
            "Selecionar conjunto seleciona o dono")
    w.undo()
    active = bpy.context.view_layer.objects.active
    j.check(active is not None and active.name == member_name, "um Desfazer volta a seleção da peça")

    # O modo é preferência do usuário: fora da cena (não vai ao arquivo nem ao Desfazer).
    j.check('panel_mode' in BTM_AddonPreferences.bl_rna.properties and
            'panel_mode' not in bpy.types.Scene.bl_rna.properties, "Essencial/Completa nas preferências, fora da cena")


j.run("blender_067_onda1_selecao", body)
