"""Soltar textura por domínio (feature 067, T024; RF-040, RF-041).

    xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_067_onda2_soltar.py

Com o catálogo do servidor falso local do MOBI:
- soltar abre o diálogo e nada baixa antes do OK; sem confirmar, o hash de materiais e objetos fica igual;
- soltar numa porta de um módulo de duas portas sugere a Peça selecionada: só aquela porta muda;
- Frentes muda só as frentes; Interno só as faces internas (nem as aparentes nem as bordas);
- item com vários materiais exige o material fonte;
- confirmar aplica num passo de Desfazer.
"""

import hashlib
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402
import _janela_067 as j  # noqa: E402
from _mobi_texture_fixture import TextureServer  # noqa: E402
from caffmob_draw.customize import finish, finish_core as fc  # noqa: E402
from caffmob_draw.geometry import door_controller  # noqa: E402
from caffmob_draw.texture_library import catalog, downloads  # noqa: E402

server = TextureServer()


def scene_hash():
    h = hashlib.sha256()
    for mat in sorted(bpy.data.materials, key=lambda m: m.name):
        h.update(mat.name.encode())
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        h.update(obj.name.encode())
        if obj.type == 'MESH':
            h.update(repr([m.name if m else '' for m in obj.data.materials]).encode())
            h.update(repr([p.material_index for p in obj.data.polygons]).encode())
    return h.hexdigest()


def face_materials(obj, role):
    roles = finish.face_roles(obj)
    mats = obj.data.materials
    names = [m.name if m else '' for m in mats]
    return {names[p.material_index] if p.material_index < len(names) else '' for p, r in zip(obj.data.polygons, roles)
            if r == role}


def door_material(door):
    return door.data.materials[0].name if door.data.materials and door.data.materials[0] else ''


def body(w):
    env.clean_scene()
    server.connect()
    square = next(i["id"] for i in catalog._cache['items'] if i["px"][0] == i["px"][1])
    assert bpy.ops.caffmob.cabinet_builder(width=0.8, door_swing='DOUBLE') == {'FINISHED'}
    module = bpy.context.object
    env.settle()
    doors = door_controller.doors_of(module)
    j.check(len(doors) == 2 and finish.face_roles(module) is not None, "módulo de duas portas com papel por face")

    # Soltar e não confirmar: nada baixa, nada muda.
    calls = []
    real_fetch = downloads.fetch
    downloads.fetch = lambda *a, **k: calls.append(a) or real_fetch(*a, **k)
    try:
        before = scene_hash()
        with w.override():
            result = bpy.ops.caffmob.finish_drop('INVOKE_DEFAULT', key=square, object_name=doors[0].name)
        j.check('RUNNING_MODAL' in result or 'FINISHED' not in result, "soltar abre o diálogo", str(result))
        j.check(not calls, "nada baixa antes do OK", str(calls))
        j.check(scene_hash() == before, "sem confirmar, o hash de materiais e objetos fica igual")
    finally:
        downloads.fetch = real_fetch

    server.download(square)                 # a imagem no cache: o OK aplica na hora
    carcass_before = face_materials(module, fc.FACE_EXTERNAL)
    other_before = door_material(doors[1])
    w.push("Antes de soltar")
    result = bpy.ops.caffmob.finish_drop('EXEC_DEFAULT', key=square, object_name=doors[0].name, fronts=True,
                                         external=False, scope='PART')
    w.push("Soltar textura")                # chamado por script, o operador não grava o passo
    applied = door_material(doors[0])
    j.check(result == {'FINISHED'} and bpy.data.materials[applied].get("btm_texture_id") == square,
            "OK aplica a textura na porta", f"{result} {applied}")
    j.check(door_material(doors[1]) == other_before, "soltar numa porta não muda a outra sem a escolha")
    j.check(face_materials(module, fc.FACE_EXTERNAL) == carcass_before, "Frentes não muda a caixa")
    j.check(doors[0].btm_part.grain == 'V', "a frente nasce com veio vertical", doors[0].btm_part.grain)
    module_name = module.name
    w.undo()
    module = bpy.data.objects[module_name]
    doors = door_controller.doors_of(module)
    j.check(door_material(doors[0]) != applied, "um Desfazer tira a textura da porta", door_material(doors[0]))

    # Interno: só as faces internas.
    external = face_materials(module, fc.FACE_EXTERNAL)
    edges = face_materials(module, fc.FACE_EDGE)
    result = bpy.ops.caffmob.finish_drop('EXEC_DEFAULT', key=square, object_name=module.name, internal=True,
                                         external=False)
    inner = face_materials(module, fc.FACE_INTERNAL)
    j.check(result == {'FINISHED'} and len(inner) == 1 and bpy.data.materials[next(iter(inner))].get(
        "btm_texture_id") == square, "Interno aplica nas faces internas", str(inner))
    j.check(face_materials(module, fc.FACE_EXTERNAL) == external, "Interno não muda as faces aparentes")
    j.check(face_materials(module, fc.FACE_EDGE) == edges, "Interno não muda as bordas (fita)")
    j.check(any(i.domain == fc.INTERNAL and i.source == 'LIBRARY' for i in module.btm_finish),
            "a escolha fica gravada em btm_finish")

    # Item com vários materiais exige o material fonte.
    multi = dict(catalog.item(square), id="multi-067", materials=["Carvalho", "Nogueira"])
    catalog._cache['by_id']["multi-067"] = multi
    try:
        result = bpy.ops.caffmob.finish_drop('EXEC_DEFAULT', key="multi-067", object_name=module.name,
                                             external=True)
        j.check(result == {'CANCELLED'}, "vários materiais sem o material fonte: recusa", str(result))
    finally:
        catalog._cache['by_id'].pop("multi-067", None)

    # Nenhum domínio: recusa, sem passo.
    before = scene_hash()
    result = bpy.ops.caffmob.finish_drop('EXEC_DEFAULT', key=square, object_name=module.name, external=False)
    j.check(result == {'CANCELLED'} and scene_hash() == before, "sem domínio: recusa e nada muda")
    server.close()


j.run("blender_067_onda2_soltar", body)
