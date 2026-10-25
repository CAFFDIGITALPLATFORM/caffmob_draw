"""Painel de acabamentos (feature 067, T025; RF-042 a RF-044, MAT-03).

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_067_onda2_acabamentos.py

- duas frentes com materiais diferentes: o módulo mostra Frentes = "Múltiplos", com a inspeção por peça;
- editar uma frente não troca a outra;
- armário autoral sem papéis: Materiais recusado com o motivo, aplicar recusa e o soltar abre o assistente;
- com papéis cadastrados pelo assistente, aplicar Externo funciona e o motivo deixa de bloquear;
- em Edit Mode o assistente marca o papel das faces selecionadas, e a face desconhecida fica fora da prévia;
- o draw da seção Acabamentos não falha (camada falsa);
- M-03: grupos antigos viram `btm_finish` MIGRATED sem mudar material nenhum, e rodar de novo não duplica;
- M-04: módulo sem `btm_face_role` usa o slot antigo como papel e ganha o atributo na primeira aplicação, com a
  caixa igual.
"""

import sys
import traceback
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as authored_env  # noqa: E402
import _blender_env as env  # noqa: E402
import _desempenho_067 as perf  # noqa: E402
from caffmob_draw.customize import finish, finish_core as fc, ops_finish_classify  # noqa: E402
from caffmob_draw.customize.adapters import authored as authored_adapter  # noqa: E402
from caffmob_draw.geometry import door_controller  # noqa: E402
from caffmob_draw.target import snapshot, view  # noqa: E402
from caffmob_draw.ui import layout_probe  # noqa: E402
from caffmob_draw.ui import object_properties as op  # noqa: E402

FAILURES = []


def check(ok, label, detail=""):
    print(("OK   " if ok else "FALHA ") + label + (f" ({detail})" if detail and not ok else ""), flush=True)
    if not ok:
        FAILURES.append(label)


def material(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


def refresh(objects, active=None):
    authored_env.select(objects, active)
    bpy.context.view_layer.update()
    return snapshot.ensure(bpy.context)


def door_material(door):
    return door.data.materials[0].name if door.data.materials and door.data.materials[0] else ''


def notes(model, section_id):
    section = next((s for s in model.sections if s.id == section_id), None)
    return [] if section is None else [i for i in section.items if isinstance(i, view.Note)]


def run():
    env.clean_scene()
    bpy.context.scene.btm_component_select = False
    oak, walnut, white = material("Carvalho", (0.6, 0.4, 0.2, 1)), material("Nogueira", (0.3, 0.2, 0.1, 1)), \
        material("Branco", (1, 1, 1, 1))
    assert bpy.ops.caffmob.cabinet_builder(width=0.8, door_swing='DOUBLE') == {'FINISHED'}
    module = bpy.context.object
    env.settle()
    left, right = door_controller.doors_of(module)

    for door, mat in ((left, oak), (right, walnut)):
        refresh([door])
        result = bpy.ops.caffmob.finish_apply(domains={fc.FRONTS}, material=mat.name, scope='PART')
        check(result == {'FINISHED'}, f"Frentes em {door.name} com {mat.name}", str(result))
    check(door_material(left) == "Carvalho" and door_material(right) == "Nogueira",
          "editar uma frente não troca a outra", f"{door_material(left)} {door_material(right)}")
    target = refresh([module])
    fronts = {d: (m, rows) for d, m, rows in target.finish}.get(fc.FRONTS)
    check(fronts is not None and fronts[0] == fc.MULTIPLE and len(fronts[1]) == 2,
          "o módulo mostra Frentes = Múltiplos com as duas peças", str(fronts))
    model = view.build(target, view.COMPLETE)
    texts = [n.args for n in notes(model, 'finish')]
    check(any(fc.MULTIPLE not in a and "Múltiplos" in a for a in texts), "a seção diz \"Múltiplos\"", str(texts))
    check(sum(1 for a in texts if "Carvalho" in a or "Nogueira" in a) >= 2, "inspeção por peça na seção",
          str(texts))
    recorder = layout_probe.Recorder()
    op.panel_mode = lambda _c: 'COMPLETE'
    op.draw_selected(layout_probe.Probe(recorder), perf.CTX)
    check(True, "o draw da seção Acabamentos não falha")

    # Componente inteiro: Externo pega a caixa aparente e as frentes, não as faces internas.
    inner_before = {p.material_index for p, r in zip(module.data.polygons, finish.face_roles(module))
                    if r == fc.FACE_INTERNAL}
    refresh([module])
    result = bpy.ops.caffmob.finish_apply(domains={fc.EXTERNAL}, material=white.name, scope='COMPONENT')
    roles = finish.face_roles(module)
    ext = {module.data.materials[p.material_index].name for p, r in zip(module.data.polygons, roles)
           if r == fc.FACE_EXTERNAL}
    inner_after = {p.material_index for p, r in zip(module.data.polygons, roles) if r == fc.FACE_INTERNAL}
    check(result == {'FINISHED'} and ext == {"Branco"} and door_material(left) == "Branco",
          "Externo aplica nas faces aparentes e nas frentes", f"{ext} {door_material(left)}")
    check(inner_after == inner_before, "Externo não muda as faces internas")

    # Armário autoral sem papéis.
    root, body = authored_env.tower("Torre", x=3.0)
    shelf = authored_env.cube("Prateleira", (.56, .33, .018), (0, 0, 1.0), root)
    from caffmob_draw.aggregates.ops_members import set_member
    set_member(shelf, root, 'CARCASS', reparent=False)
    caps = authored_adapter.capabilities(root)
    check(caps['MATERIALS'] == authored_adapter.NO_ROLES, "autoral sem papéis: Materiais recusado com o motivo",
          str(caps['MATERIALS']))
    refresh([body])
    result = bpy.ops.caffmob.finish_apply(domains={fc.EXTERNAL}, material=oak.name)
    check(result == {'CANCELLED'}, "autoral sem papéis: aplicar recusa", str(result))
    target = refresh([body])
    model = view.build(target, view.COMPLETE)
    actions = [a.operator for s in model.sections if s.id == 'finish' for a in s.items if isinstance(a, view.Action)]
    check('caffmob.finish_classify' in actions, "sem papéis, a seção oferece o assistente", str(actions))
    ops_finish_classify._preview['owner'] = ''
    result = bpy.ops.caffmob.finish_drop('INVOKE_DEFAULT', key="qualquer", object_name=body.name)
    check(result == {'CANCELLED'} and ops_finish_classify._preview['owner'] == root.name,
          "sem papéis, o soltar abre o assistente em vez de aplicar", str(result))

    # Assistente em Object Mode: corpo externo, prateleira interna.
    refresh([body])
    check(bpy.ops.caffmob.finish_classify(role=fc.PIECE_EXTERNAL) == {'FINISHED'}, "assistente marca o corpo")
    refresh([shelf])
    check(bpy.ops.caffmob.finish_classify(role=fc.PIECE_INTERNAL) == {'FINISHED'}, "assistente marca a prateleira")
    caps = authored_adapter.capabilities(root)
    check(caps['MATERIALS'] is None and caps['FRONTS'] == authored_adapter.REASON,
          "com papéis, Materiais habilitado; Frentes continua recusado", str(caps))
    refresh([body])
    result = bpy.ops.caffmob.finish_apply(domains={fc.EXTERNAL}, material=walnut.name, scope='COMPONENT')
    check(result == {'FINISHED'} and body.data.materials[0].name == "Nogueira", "autoral com papéis aplica Externo",
          f"{result} {[m.name for m in body.data.materials if m]}")
    check(not shelf.data.materials or shelf.data.materials[0] is None or shelf.data.materials[0].name != "Nogueira",
          "Externo não muda a peça interna")

    # Assistente em Edit Mode: só as faces selecionadas; a desconhecida fica fora da prévia.
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(6, 0, 0.25))
    cube = bpy.context.object
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    cube.data.polygons[0].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    result = bpy.ops.caffmob.finish_classify(role=fc.PIECE_INTERNAL)
    bpy.ops.object.mode_set(mode='OBJECT')
    roles = finish.face_roles(cube)
    check(result == {'FINISHED'} and roles is not None and roles[0] == fc.FACE_INTERNAL
          and roles.count(fc.FACE_UNKNOWN) == 5, "Edit Mode marca só a face selecionada", str(roles))
    tris = ops_finish_classify.build_preview(cube)
    check(set(tris) == {fc.FACE_INTERNAL} and len(tris[fc.FACE_INTERNAL]) == 6,
          "a prévia pinta só a face com papel", str({k: len(v) for k, v in tris.items()}))


def slots(obj):
    return [m.name if m else '' for m in obj.data.materials], [p.material_index for p in obj.data.polygons]


def migrations():
    from caffmob_draw.customize import finish_migration
    env.clean_scene()
    oak, white = material("Carvalho", (0.6, 0.4, 0.2, 1)), material("Branco", (1, 1, 1, 1))
    assert bpy.ops.caffmob.cabinet_builder(width=0.6, door_swing='LEFT') == {'FINISHED'}
    module = bpy.context.object
    env.settle()
    module.btm_custom.set_group_material('CAIXA', oak.name)
    module.btm_custom.front_material = white.name
    from caffmob_draw.customize import reapply
    reapply.reapply(bpy.context, module)
    before = slots(module)
    doors = [door_material(d) for d in door_controller.doors_of(module)]
    count = finish_migration.run()
    entries = sorted((i.domain, i.material.name, i.source) for i in module.btm_finish)
    check(count == 3 and entries == [(fc.EXTERNAL, "Carvalho", 'MIGRATED'), (fc.FRONTS, "Branco", 'MIGRATED'),
                                     (fc.INTERNAL, "Carvalho", 'MIGRATED')], "M-03 grava btm_finish MIGRATED",
          str(entries))
    check(slots(module) == before and [door_material(d) for d in door_controller.doors_of(module)] == doors,
          "M-03 não muda material nenhum")
    check(finish_migration.run() == 0 and len(module.btm_finish) == 3, "M-03 de novo não duplica")
    reapply.reapply(bpy.context, module)
    check(slots(module) == before, "rebuild com entradas migradas: a aparência não muda")

    # M-04: arquivo antigo sem o atributo.
    module.data.attributes.remove(module.data.attributes[finish.FACE_ATTR])
    check(finish.face_roles(module) is None, "fixture M-04 sem btm_face_role")
    summary = finish.summary(module)
    check((module.name, "Carvalho") in summary[fc.EXTERNAL][1], "M-04: o slot antigo dá o papel até o rebuild",
          str(summary[fc.EXTERNAL]))
    walnut = material("Nogueira", (0.3, 0.2, 0.1, 1))
    authored_env.select([module])
    bpy.context.view_layer.update()
    result = bpy.ops.caffmob.finish_apply(domains={fc.INTERNAL}, material=walnut.name)
    roles = finish.face_roles(module)
    ext = {module.data.materials[p.material_index].name for p, r in zip(module.data.polygons, roles or ())
           if r == fc.FACE_EXTERNAL}
    check(result == {'FINISHED'} and roles is not None, "M-04: o módulo ganha o atributo na aplicação")
    check(ext == {"Carvalho"}, "M-04: a caixa aparente continua igual", str(ext))


try:
    run()
    migrations()
except Exception:
    traceback.print_exc()
    FAILURES.append("exceção")
print(f"blender_067_onda2_acabamentos: {'OK' if not FAILURES else 'FALHAS: ' + ', '.join(FAILURES)}", flush=True)
sys.exit(1 if FAILURES else 0)
