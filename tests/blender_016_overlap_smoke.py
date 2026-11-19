"""Teste de fumaça do seletor de objetos sobrepostos (feature 016, T014; RN-02 a RN-05, RN-10).

Roda em segundo plano:
    blender --background --factory-startup --python-exit-code 1 --python tests/blender_016_overlap_smoke.py

A cena tem três cubos empilhados na frente do raio, uma curva, um texto, um vazio, uma malha com Geometry Nodes, um
cubo oculto e um cubo com **Desabilitar seleção** ligado:
- o raio pega só os três cubos, do mais próximo ao mais distante; curva, texto, vazio, GN, oculto e não selecionável
  ficam de fora (o filtro `MESH` vem antes do `ray_cast`, que já derrubou o Blender numa curva);
- `Picker` marca, isola e restaura a visibilidade, inclusive a de um objeto que já estava oculto;
- a seleção aplicada é exatamente a marcada, com o objeto em foco como ativo, e o cancelar devolve a seleção anterior;
- o operador não empilha desfazer (`{'INTERNAL'}`) e está registrado.

O painel, o desenho e as teclas do modal precisam de janela: aqui o `poll` falha por não haver área `VIEW_3D`, então
esta fumaça cobre o caminho de dados, e a interface fica na conferência manual do `onboarding.md`.
"""

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from caffmob_draw.selection import overlap_core as core  # noqa: E402
from caffmob_draw.selection import overlap_select as sel  # noqa: E402

ctx = bpy.context
FAILURES = []
ORIGIN = Vector((0.0, -6.0, 1.0))
DIRECTION = Vector((0.0, 1.0, 0.0))


def check(name, ok, detail=""):
    print(("OK   " if ok else "FALHA ") + name, detail, flush=True)
    if not ok:
        FAILURES.append(name)


def cube(name, location, size=0.4):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = ctx.active_object
    obj.name = name
    return obj


def gn_instanced(name, location, template):
    """Malha cujo avaliado só tem instâncias (0 vértices), como o caso da sonda: o raio não a pega."""
    group = bpy.data.node_groups.new("SondaGN016", 'GeometryNodeTree')
    group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    output = group.nodes.new('NodeGroupOutput')
    info = group.nodes.new('GeometryNodeObjectInfo')
    info.inputs['Object'].default_value = template
    instance = group.nodes.new('GeometryNodeGeometryToInstance')
    group.links.new(info.outputs['Geometry'], instance.inputs['Geometry'])
    group.links.new(instance.outputs['Instances'], output.inputs['Geometry'])
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    ctx.scene.collection.objects.link(obj)
    obj.location = location
    obj.modifiers.new("GN", 'NODES').node_group = group
    return obj


def build_scene():
    env.clean_scene()
    front = cube("Cubo Frente", (0.0, 0.0, 1.0))
    middle = cube("Cubo Meio", (0.0, 0.3, 1.0))
    back = cube("Cubo Fundo", (0.0, 0.6, 1.0))
    bpy.ops.curve.primitive_bezier_curve_add(location=(0.0, 0.15, 1.0))
    ctx.active_object.name = "Curva"
    bpy.ops.object.text_add(location=(0.0, 0.45, 1.0))
    ctx.active_object.name = "Texto"
    bpy.ops.object.empty_add(location=(0.0, 0.75, 1.0))
    ctx.active_object.name = "Vazio"
    try:
        gn = gn_instanced("Malha GN", (0.0, 0.9, 1.0), front)
    except Exception:                                    # noqa: BLE001 - sem o nó, a malha sem vértices cobre o caso
        traceback.print_exc()
        gn = cube("Malha GN", (0.0, 0.9, 1.0))
    hidden = cube("Cubo Oculto", (0.0, 1.05, 1.0))
    hidden.hide_set(True)
    locked = cube("Cubo Nao Selecionavel", (0.0, 1.2, 1.0))
    locked.hide_select = True
    env.settle()
    return [front, middle, back], gn


def main():
    expected, _gn = build_scene()
    hits = sel.hits_along(ctx, ORIGIN, DIRECTION)
    names = [obj.name for obj in hits]
    check("raio acha exatamente os três cubos, em ordem", names == [obj.name for obj in expected], str(names))
    check("curva, texto, vazio, GN, oculto e não selecionável ficam de fora",
          not {"Curva", "Texto", "Vazio", "Malha GN", "Cubo Oculto", "Cubo Nao Selecionavel"} & set(names), str(names))

    picker = core.Picker(hits)
    check("a lista começa no mais próximo, com o comprimento certo", len(picker) == 3 and picker.focused is hits[0])
    picker.toggle(0)
    picker.toggle(2)
    check("clique nas linhas marca", picker.staged == {hits[0], hits[2]}, str(picker.staged))
    picker.invert()
    check("Ctrl+/ inverte", picker.staged == {hits[1]}, str(picker.staged))
    picker.mark_all()
    check("Ctrl+A marca tudo", picker.staged == set(hits))

    # Isolamento: só o foco visível, e tudo volta, inclusive o que já estava oculto.
    state = sel.snapshot_state(ctx)
    sel.isolate(ctx, state['hidden'], hits[1])
    visible = [obj.name for obj in ctx.view_layer.objects if obj.visible_get()]
    check("I isola só o objeto em foco", visible == [hits[1].name], str(visible))
    sel.isolate(ctx, state['hidden'], hits[2])
    check("isolar acompanha o foco", hits[2].visible_get() and not hits[1].visible_get())
    sel.restore_visibility(ctx, state['hidden'])
    check("restaurar devolve a visibilidade de todos",
          all(obj.visible_get() for obj in hits) and not bpy.data.objects["Cubo Oculto"].visible_get())

    # Seleção: aplicar exatamente os marcados, com o foco ativo; cancelar devolve o que era.
    curve = bpy.data.objects["Curva"]
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    curve.select_set(True)
    ctx.view_layer.objects.active = curve
    state = sel.snapshot_state(ctx)
    selection, active = core.confirm_selection(hits, [hits[0], hits[2]], state['selection'], state['active'],
                                               hits[2])
    sel.apply_selection(ctx, selection, active)
    selected = sorted(obj.name for obj in ctx.view_layer.objects if obj.select_get())
    check("Enter soma os marcados à seleção anterior (RF-12)",
          selected == sorted([curve.name, hits[0].name, hits[2].name]), str(selected))
    check("o item em foco vira o ativo", ctx.view_layer.objects.active is hits[2])
    sel.restore_state(ctx, state)
    selected = [obj.name for obj in ctx.view_layer.objects if obj.select_get()]
    check("Esc devolve a seleção e o ativo", selected == ["Curva"] and ctx.view_layer.objects.active is curve,
          str(selected))

    check("o seletor não empilha desfazer", 'UNDO' not in sel.BTM_OT_OverlapSelect.bl_options,
          str(sel.BTM_OT_OverlapSelect.bl_options))
    registered = sel.BTM_OT_OverlapSelect.is_registered
    try:
        poll = bpy.ops.caffmob.overlap_select.poll()
    except Exception as exc:                             # noqa: BLE001 - a fumaça mostra o erro do poll
        poll = f"exceção: {exc!r}"
    check("o operador está registrado e o poll dispensa a falta de janela", registered and poll is False, str(poll))
    wm = ctx.window_manager
    kc = wm.keyconfigs.addon if wm else None
    if kc is not None:
        km = kc.keymaps.get('3D View')
        found = [item for item in getattr(km, 'keymap_items', []) if item.idname == "caffmob.overlap_select"]
        check("atalho Ctrl + Alt + clique no mapa 3D View", len(found) == 1
              and (found[0].ctrl, found[0].alt, found[0].type, found[0].value) == (True, True, 'LEFTMOUSE', 'CLICK'),
              str([(i.ctrl, i.alt, i.type, i.value) for i in found]))
    else:
        print("SEM JANELA: keymap não conferido (keyconfigs.addon ausente)", flush=True)
    sel.cancel_active()
    check("cancel_active sem seletor aberto não quebra", True)


try:
    main()
except Exception:                                        # noqa: BLE001 - a fumaça precisa mostrar o erro e sair 1
    traceback.print_exc()
    FAILURES.append("exceção no roteiro")
print(f"blender_016_overlap_smoke: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}")
sys.exit(1 if FAILURES else 0)
