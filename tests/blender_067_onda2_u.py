"""U: criar componente a partir da seleção (feature 067, T026; RF-045 a RF-048, CMP-01).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda2_u.py

- 6 chapas com 128 decorações filhas (134 selecionados) viram um armário autoral em ≤ 150 ms pela chamada
  `bpy.ops`, com as matrizes idênticas (erro 0) e a decoração na hierarquia sem cadastro;
- Desfazer e Refazer revertem e refazem;
- o atalho fica só no keymap "Object Mode" (Edit Mode continua com o UV Unwrap; campo de texto não chega ao keymap),
  e o poll falha fora do Object Mode e com menos de 2 chapas (o U passa ao Blender);
- recusas terminam `CANCELLED` com a hierarquia intacta: pai fora da seleção, constraint, animação, membro de outro
  armário e mais de 512 selecionados;
- o componente é reconhecido pelo painel, pelo Mover Sobre, pelas cotas e pelos acabamentos.
"""

import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
import _janela_067 as j  # noqa: E402
from caffmob_draw.aggregates import ops_component_u  # noqa: E402
from caffmob_draw.target import resolver as r  # noqa: E402
from caffmob_draw.target import snapshot, view  # noqa: E402


def sheets_with_decoration(count=6, decorations=128, x0=0.0):
    sheets = []
    for i in range(count):
        sheet = authored_env.cube(f"Chapa {i}", (0.6, 0.018, 0.7), (x0 + 0.02 * i, 0.03 * i, 0.35))
        sheet.rotation_euler.z = 0.1 * i
        sheets.append(sheet)
    decos = []
    for i in range(decorations):
        deco = bpy.data.objects.new(f"Decoração {i}", None)
        bpy.context.collection.objects.link(deco)
        deco.parent = sheets[i % count]
        deco.matrix_parent_inverse = Matrix.Identity(4)
        deco.location = (0.01 * (i % 7), 0.0, 0.01 * (i % 5))
        decos.append(deco)
    env.settle()
    return sheets, decos


def run_u(w, objects, active=None, **kwargs):
    authored_env.select(objects, active)
    bpy.context.view_layer.update()
    try:
        with w.override():
            return bpy.ops.caffmob.component_from_selection('EXEC_DEFAULT', **kwargs)
    except RuntimeError as exc:          # relatório ERROR chamado por script vira exceção; o retorno é CANCELLED
        print(f"recusa: {exc}", flush=True)
        return {'CANCELLED'}


def body(w):
    env.clean_scene()
    bpy.context.scene.btm_component_select = False
    sheets, decos = sheets_with_decoration()
    selected = sheets + decos
    j.check(len(selected) == 134, "fixture de 134 objetos", str(len(selected)))
    worlds = {o.name: o.matrix_world.copy() for o in selected}
    w.push("Antes do U")
    authored_env.select(selected, sheets[0])
    bpy.context.view_layer.update()
    start = time.perf_counter()
    with w.override():
        result = bpy.ops.caffmob.component_from_selection('EXEC_DEFAULT', name="Gaveteiro")
    elapsed = (time.perf_counter() - start) * 1000.0
    w.push("U")
    root = bpy.context.view_layer.objects.active
    print(f"U: {elapsed:.1f} ms para 134 objetos", flush=True)
    j.check(result == {'FINISHED'} and root is not None and root.get('IS_AUTHORED_CABINET'),
            "U cria um armário autoral", str(result))
    j.check(elapsed <= 150.0, "134 objetos em ≤ 150 ms", f"{elapsed:.1f} ms")
    error = max(authored_env.matrix_error(worlds[o.name], o.matrix_world) for o in selected)
    j.check(error < 1e-6, "malhas e matrizes idênticas (erro 0)", f"{error:.2e}")
    j.check(all(s.parent == root and s.btm_member.owner == root for s in sheets), "as chapas viram membros")
    j.check(all(d.parent in sheets and d.btm_member.owner is None for d in decos),
            "a decoração fica na hierarquia, sem cadastro")
    root_name = root.name
    sheet_names = [s.name for s in sheets]

    # Reconhecido pelo painel, pelo Mover Sobre, pelas cotas e pelos acabamentos.
    authored_env.select([root])
    bpy.context.view_layer.update()
    target = snapshot.ensure(bpy.context)
    ids = {s.id for s in view.build(target, view.COMPLETE).sections}
    j.check(target.kind == r.MODULE and target.library == 'AUTHORED' and target.move_uid,
            "o painel vê o componente como módulo autoral que se move", f"{target.kind} {target.library}")
    j.check({'cotas', 'finish'} <= ids, "o componente tem cotas e acabamentos", str(ids))

    w.undo()
    j.check(bpy.data.objects.get(root_name) is None, "um Desfazer tira o componente")
    j.check(all(bpy.data.objects[n].parent is None for n in sheet_names), "as chapas voltam sem pai")
    with w.override():
        bpy.ops.ed.redo()
    j.check(bpy.data.objects.get(root_name) is not None, "Refazer devolve o componente")

    # Atalho e poll.
    kc = bpy.context.window_manager.keyconfigs.addon
    places = [km.name for km in kc.keymaps for i in km.keymap_items
              if i.idname == ops_component_u.BTM_OT_ComponentFromSelection.bl_idname]
    j.check(places == ['Object Mode'], "um único U, no keymap Object Mode", str(places))
    env.clean_scene()
    a = authored_env.cube("A", (0.5, 0.018, 0.5), (0, 0, 0.25))
    b = authored_env.cube("B", (0.5, 0.018, 0.5), (0, 0.2, 0.25))
    authored_env.select([a])
    bpy.context.view_layer.update()
    snapshot.ensure(bpy.context)
    with w.override():
        j.check(not bpy.ops.caffmob.component_from_selection.poll(), "uma chapa só: o U passa ao Blender")
    authored_env.select([a, b])
    bpy.context.view_layer.update()
    snapshot.ensure(bpy.context)
    with w.override():
        bpy.ops.object.mode_set(mode='EDIT')
        j.check(not bpy.ops.caffmob.component_from_selection.poll(), "Edit Mode: o U fica com o UV Unwrap")
        bpy.ops.object.mode_set(mode='OBJECT')

    # Recusas: CANCELLED e hierarquia intacta.
    holder = authored_env.cube("Suporte", (0.1, 0.1, 0.1), (2, 0, 0))
    a.parent = holder
    state = [(o.name, o.parent) for o in (a, b, holder)]
    j.check(run_u(w, [a, b]) == {'CANCELLED'} and [(o.name, o.parent) for o in (a, b, holder)] == state,
            "pai fora da seleção: recusa")
    a.parent = None
    b.constraints.new('COPY_LOCATION')
    j.check(run_u(w, [a, b]) == {'CANCELLED'} and b.parent is None, "constraint: recusa")
    b.constraints.clear()
    b.keyframe_insert('location')
    j.check(run_u(w, [a, b]) == {'CANCELLED'}, "animação: recusa")
    b.animation_data_clear()
    tower, body_obj = authored_env.tower("Torre", x=4.0)
    j.check(run_u(w, [a, body_obj], a) == {'CANCELLED'} and body_obj.btm_member.owner == tower,
            "membro de outro armário: recusa")
    many = [authored_env.cube(f"M{i}", (0.01, 0.01, 0.01), (0, 0, i * 0.02)) for i in range(513)]
    j.check(run_u(w, many) == {'CANCELLED'} and all(m.parent is None for m in many), "mais de 512: recusa")

    # Componente existente: agregar ao ativo.
    result = run_u(w, [tower, a, b], tower, mode='AGGREGATE')
    j.check(result == {'FINISHED'} and a.btm_member.owner == tower and b.btm_member.owner == tower,
            "com armário ativo, agregar ao ativo", str(result))


j.run("blender_067_onda2_u", body)
