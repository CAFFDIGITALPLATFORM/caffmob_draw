"""Biblioteca autoral: pacote fechado, transação e duas instâncias (T024)."""
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _authored_env as a
import bpy
from caffmob_draw.customize import adapters, library_io, manifest
from caffmob_draw.customize.ops_library import BTM_OT_ModuleSave
from caffmob_draw.aggregates import leaf, ops_authored_leaf, ops_members
from caffmob_draw.collision import guard

# A outra sessão (reopen) lê a entrada gravada aqui; fora do repositório.
RELOAD_ENTRY = Path(tempfile.gettempdir()) / 'caffmob_066_reload-entry.json'


def check(value, message):
    assert value, message
    print('OK:', message)


def main():
    a.env.clean_scene()
    root, body = a.tower(angle=90)
    panel = a.cube('Vidro', (.55, .01, 2.4), (0, -.2, 1.3), root)
    ops_members.set_member(panel, root, 'LEAF_PART', reparent=False)
    front = ops_authored_leaf.configure([panel], root, construction='GLASS', closed_pose=True)
    light = bpy.data.objects.new('Luz', bpy.data.lights.new('Área', 'AREA'))
    bpy.context.collection.objects.link(light)
    ops_members.set_member(light, root, 'LIGHT')
    cutter = a.cube('Cortador', (.01, .01, .1), parent=root)
    cutter['IS_CUTTING_OBJ'] = True
    ops_members.set_member(cutter, root, 'CUTTER', reparent=False)
    mod = body.modifiers.new('Rasgo', 'BOOLEAN')
    mod.object = cutter
    ref = light.btm_member.refs.add()
    ref.target, ref.uid = body, body.btm_member.uid
    front.btm_aggregate.open_value = .5
    a.env.settle()
    a.select([panel])
    check(BTM_OT_ModuleSave.poll(bpy.context), 'poll aceita membro AUTHORED')
    from caffmob_draw.library_panel import categories
    check(any(c.name == library_io.AUTHORED_CATEGORY for c in categories.load()[0]),
          'painel da biblioteca oferece categoria de armários autorais')
    # 067 RF-044 (D-18): Materiais vale quando há papéis de acabamento; o resto continua recusado com motivo.
    from caffmob_draw.customize import finish
    caps = adapters.for_root(root).capabilities(root)
    check(all(v for k, v in caps.items() if k != 'MATERIALS') and (caps['MATERIALS'] is None) == finish.has_roles(root),
          'personalização recusada com motivo')
    # A imagem de disco é empacotada temporariamente e sobrevive sem o arquivo de origem.
    texture_path = Path(a.env.USER_DIR) / 'textura_autoral.png'
    generated = bpy.data.images.new('Imagem do ensaio', width=2, height=2)
    generated.filepath_raw = str(texture_path)
    generated.file_format = 'PNG'
    generated.save()
    image = bpy.data.images.load(str(texture_path))
    material = bpy.data.materials.new('Acabamento autoral')
    material.use_nodes = True
    material.node_tree.nodes.new('ShaderNodeTexImage').image = image
    body.data.materials.append(material)
    before = {o: o.matrix_world.copy() for o in [root] + list(root.children_recursive)}
    paths, errors = library_io.save(bpy.context, root, 'Torre ensaio', 'Armários autorais', thumbnail=True)
    check(not errors, 'salvar autoral: ' + str(errors))
    check(all(a.matrix_error(m, o.matrix_world) < 1e-6 for o, m in before.items()), 'salvar aberta restaura a cena')
    check(abs(leaf.current_fraction(front) - .5) < 1e-6, 'fração aberta restaurada')
    block = json.loads(Path(paths['json']).read_text())
    check(block['schema_version'] == '1.2.0' and 'structure' not in block and 'divisions' not in block,
          'manifesto 1.2 sem estrutura nativa')
    check(abs(block['authored']['size_local_mm'][0] - 600) < .01, 'medida no referencial local girado')
    check(os.path.getsize(paths['png']) > 0, 'miniatura gravada')
    check(image.packed_file is None, 'salvar restaura imagem originalmente não empacotada')
    previous = {ext: Path(paths[ext]).read_bytes() for ext in ('blend', 'json')}
    original_replace = os.replace
    
    
    def fail_second(source, target):
        if target == paths['json']:
            raise OSError('falha de gravação simulada')
        return original_replace(source, target)
    
    
    with patch.object(library_io.os, 'replace', fail_second):
        _, errors = library_io.save(bpy.context, root, 'Torre ensaio', 'Armários autorais', thumbnail=False)
    check(errors and all(Path(paths[e]).read_bytes() == previous[e] for e in previous),
          'falha da troca preserva versão anterior')
    check(all(a.matrix_error(m, o.matrix_world) < 1e-6 for o, m in before.items()), 'falha restaura pose aberta')
    external = a.cube('Parede externa', (1, .1, 3), (5, 0, 0))
    mod.object = external
    _, errors = library_io.save(bpy.context, root, 'Inválido', 'Armários autorais', thumbnail=False)
    check(errors and 'Parede externa' in str(errors), 'referência externa recusada com motivo')
    mod.object = cutter
    source_uids = {o.btm_member.uid for o in root.children_recursive} | {root.btm_authored.uid}
    texture_path.unlink()
    a.env.clean_scene()
    entry = dict(paths, has_manifest=True)
    RELOAD_ENTRY.write_text(json.dumps(entry))
    with guard.suspended():
        first, loaded, errors = library_io.load(bpy.context, entry)
    check(first is not None and not errors, 'inserção em cena vazia: ' + str(errors))
    check(any(node.image.packed_file for obj in loaded for slot in obj.material_slots
              if slot.material and slot.material.node_tree for node in slot.material.node_tree.nodes
              if node.type == 'TEX_IMAGE' and node.image), 'imagem viaja sem o arquivo de origem')
    check(any(o.type == 'LIGHT' for o in loaded) and any(o.btm_member.role == 'CUTTER' for o in loaded),
          'luz e cortador viajam no pacote')
    first_uids = {o.btm_member.uid for o in first.children_recursive} | {first.btm_authored.uid}
    with guard.suspended():
        second, loaded2, errors = library_io.load(bpy.context, entry)
    check(second is not None and not errors, 'segunda inserção: ' + str(errors))
    second_uids = {o.btm_member.uid for o in second.children_recursive} | {second.btm_authored.uid}
    check(not first_uids & second_uids and not (first_uids | second_uids) & source_uids, 'uids independentes da origem')
    for instance in (first, second):
        inside = set(instance.children_recursive)
        for obj in inside:
            for ref in obj.btm_member.refs:
                check(ref.target in inside and ref.uid == ref.target.btm_member.uid, 'referência aponta à instância')
            if obj.btm_aggregate.kind == 'LEAF' and obj.btm_aggregate.is_aggregate:
                check(leaf.current_fraction(obj) == 0 and obj.btm_aggregate.open_value == 0, 'folha inserida fechada')
                check(leaf.pivot_of(obj) in inside, 'pivô da própria instância')
        check(instance.btm_authored.asset_uid == block['authored']['uid'] and instance.btm_authored.asset_version == 1,
              'identidade de asset registrada')
    # Manifesto válido com .blend de outra biblioteca: nada inserido e nada existente apagado.
    wrong = json.loads(Path(paths['json']).read_text())
    wrong['authored']['uid'] = 'a' * 32
    bad = Path(paths['json']).with_name('incompativel.json')
    bad.write_text(manifest.dumps(wrong))
    count = len(bpy.data.objects)
    original_ids = set(bpy.data.all_ids)
    with guard.suspended():
        obj, loaded, errors = library_io.load(bpy.context, dict(entry, json=str(bad)))
    check(obj is None and loaded == [] and errors and len(bpy.data.objects) == count,
          'pacote incompatível sem resíduos')
    check(set(bpy.data.all_ids) == original_ids, 'pacote incompatível não deixa datablocks órfãos')
    # Os dois formatos anteriores continuam inseríveis pelo caminho nativo.
    from caffmob_draw import hb_utils
    from caffmob_draw.product_libraries.frameless import types_frameless
    from caffmob_draw.product_libraries.face_frame import types_face_frame
    from caffmob_draw.product_libraries.closets import types_closets
    for library in ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM'):
        for version in ('1.0.0', '1.1.0'):
            a.env.clean_scene()
            if library == 'BTM':
                bpy.ops.caffmob.cabinet_builder(width=.6)
                native_root = bpy.context.object
            elif library == 'CLOSETS':
                cabinet = types_closets.BaseClosetStarter()
                cabinet.create_starter('Nativo', bay_qty=2)
                types_closets.recalculate_closet_starter(cabinet.obj)
                native_root = cabinet.obj
            else:
                cabinet = (types_frameless.BaseCabinet() if library == 'FRAMELESS'
                           else types_face_frame.BaseFaceFrameCabinet())
                cabinet.create('Nativo')
                native_root = cabinet.obj
                hb_utils.run_calc_fix_until_stable(bpy.context, native_root)
            native_paths, errors = library_io.save(bpy.context, native_root, 'Legado', 'Ensaio', thumbnail=False)
            check(not errors, 'gravar nativo ' + library + ' ' + version + ': ' + str(errors))
            native_data = json.loads(Path(native_paths['json']).read_text())
            check(native_data['schema_version'] == '1.1.0', 'nativo continua gravando 1.1.0: ' + library)
            native_data['schema_version'] = version
            Path(native_paths['json']).write_text(manifest.dumps(native_data))
            a.env.clean_scene()
            native, _, errors = library_io.load(bpy.context, dict(native_paths, has_manifest=True))
            check(native is not None and not errors, 'inserir legado ' + library + ' ' + version + ': ' + str(errors))
    print('PASSOU: biblioteca autoral 066')


def reopen():
    entry_path = RELOAD_ENTRY
    entry = json.loads(entry_path.read_text())
    a.env.clean_scene()
    instance, objects, errors = library_io.load(bpy.context, entry)
    check(instance is not None and not errors, 'outra sessão insere o pacote autoral: ' + str(errors))
    check(any(o.type == 'LIGHT' for o in objects), 'outra sessão conserva luzes')
    for obj in objects:
        if obj.btm_aggregate.is_aggregate and obj.btm_aggregate.kind == 'LEAF':
            check(leaf.current_fraction(obj) == 0, 'outra sessão insere fechada')
    print('PASSOU: biblioteca autoral em outra sessão 066')


reopen() if '--reabrir' in sys.argv else main()
