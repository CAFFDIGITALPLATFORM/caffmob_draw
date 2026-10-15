# (063 RF-12; T059) Ensaio HTTP real, somente no MOBI descartável em 127.0.0.1.
# Não integra tools/portao.sh. Comando e saída nas notas da rodada 4.
import copy
import importlib.util
import json
import os
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import patch

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
base = os.environ.get('CAFFMOB_BASE', '')
assert urlsplit(base).hostname == '127.0.0.1' and urlsplit(base).scheme == 'http', base
assert bpy.app.online_access, 'Use --online-mode'
# O clone é carregado como extensão para usar extension_path_user de verdade.
PACKAGE = 'bl_ext.ensaio_mobi_063.caffmob_draw'
spec = importlib.util.spec_from_file_location(PACKAGE, ROOT / 'caffmob_draw/__init__.py',
                                            submodule_search_locations=[str(ROOT / 'caffmob_draw')])
addon = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = addon
spec.loader.exec_module(addon)
from importlib import import_module
chapas = import_module(PACKAGE + '.caffmob.chapas')
sem_envelope_do_servidor = import_module(PACKAGE + '.caffmob.contrato').sem_envelope_do_servidor
cena, ops_biblioteca, ops_ambientes = [import_module(PACKAGE + '.mobi.' + name)
                                    for name in ('cena', 'ops_biblioteca', 'ops_ambientes')]
auth, catalog, downloads, apply = [import_module(PACKAGE + '.texture_library.' + name)
                                  for name in ('auth', 'catalog', 'downloads', 'apply')]


def wait(predicate, label, timeout=90):
    # --python bloqueia o event loop: bombeia os callbacks reais do addon.
    end = time.monotonic() + timeout
    while True:
        downloads._tick()
        auth._poll()
        if predicate():
            return
        assert time.monotonic() < end, ('Tempo esgotado: ' + label, state.situacao)
        time.sleep(0.05)


def request(method, path, body=None, headers=None, authenticated=True):
    result = []
    downloads.request(method, path, body, headers=headers, auth=authenticated,
                      callback=lambda s, b, h: result.append((s, b, h)), response_headers=True)
    wait(lambda: bool(result), method + ' ' + path)
    return result[0]


def operate(operator, **kwargs):
    original = downloads.request
    def observed(method, path, body=None, **options):
        callback = options.get('callback')
        if callback and path.startswith('/api/draw/v1/'):
            def received(status, data, incoming):
                if status and status >= 400:
                    print('Resposta do MOBI:', method, path, status, data, flush=True)
                callback(status, data, incoming)
            options['callback'] = received
        return original(method, path, body, **options)
    with patch.object(downloads, 'request', side_effect=observed):
        assert operator(**kwargs) == {'FINISHED'}
        wait(lambda: not state.ocupado, operator.idname())


def fixture(name):
    return json.loads((ROOT / 'tests/casos_ouro' / name).read_text())['entrada']


addon.register()
addon.load_file_post(None)
state = bpy.context.window_manager.btm_caffmob
try:
    # Sessão anterior do ensaio é revogada antes de criar outro aparelho.
    if auth.signed_in():
        bpy.ops.caffmob.mobi_desconectar()
        wait(lambda: not downloads._requests, 'revogação anterior')
    assert bpy.ops.caffmob.mobi_conectar() == {'FINISHED'}
    wait(auth.signed_in, 'aprovação automática do aparelho')
    assert not state.codigo
    print('1. Conectar e aprovação: OK', flush=True)

    doc = sem_envelope_do_servidor(fixture('paredes/parede-ambiente-l.json'))
    mod = sem_envelope_do_servidor(fixture('pecas-addon/pecas-addon-base-double.json'))
    doc.update(id=str(uuid.uuid4()), nome='TESTE 063 ensaio ambiente')
    mod.update(id=str(uuid.uuid4()), nome='TESTE 063 ensaio modelo')
    doc['modulos'] = [ops_biblioteca.instance(mod, str(uuid.uuid4()))]
    status, created, _ = request('POST', '/api/draw/v1/ambientes', doc)
    assert status == 201, (status, created)
    doc['id'] = created['id']
    status, model, _ = request('POST', '/api/draw/v1/modelos', {
        'escopo': 'titular', 'nome': mod['nome'], 'categoria': 'TESTE 063', 'documento': mod})
    assert status == 201, (status, model)
    print('2. POST ambiente e modelo dos casos-ouro: 201 / 201', flush=True)

    operate(bpy.ops.caffmob.mobi_listar_ambientes)
    assert doc['id'] in {i.id for i in state.ambientes}, state.situacao
    operate(bpy.ops.caffmob.mobi_baixar_ambiente, ambiente_id=doc['id'])
    assert bpy.context.scene.get('caffmob_ambiente_id') == doc['id'] or json.loads(bpy.context.scene['caffmob_ambiente'])['id'] == doc['id']
    root = next(o for o in bpy.context.scene.objects if o.get('caffmob_modulo'))
    assert not root.children
    print('3. Listar e baixar ambiente: OK', flush=True)

    result = []
    catalog.refresh_manufacturers(lambda s, b: result.append((s, b)))
    wait(lambda: bool(result), 'fabricantes')
    assert result[0][0] in (200, 304), result
    result.clear()
    catalog.refresh(callback=lambda s, b: result.append((s, b)))
    wait(lambda: bool(result), 'catálogo')
    assert result[0][0] in (200, 304) and catalog.search(), result
    entry = catalog.search()[0]
    result.clear()
    catalog.refresh(text=entry['nome'][:80], callback=lambda s, b: result.append((s, b)))
    wait(lambda: bool(result), 'busca de textura')
    assert result[0][0] in (200, 304) and entry['id'] in {e['id'] for e in catalog.search()}
    fetched = []
    downloads.fetch(entry['id'], lambda path, error: fetched.append((path, error)), entry=entry)
    wait(lambda: bool(fetched), 'imagem de trabalho')
    assert fetched[0][0] and not fetched[0][1], fetched
    assert apply.apply_cached([root], entry['id'], fetched[0][0]) == 1
    assert entry['id'] in chapas.texturas_do_modulo(cena._modulo_do_objeto(root))
    assert root.data.materials[0]['btm_texture_sha256'] == entry['sha256']
    print('4. Buscar, baixar e aplicar textura: OK', flush=True)

    operate(bpy.ops.caffmob.mobi_baixar_modelo, modelo_id=model['id'], escopo='titular')
    inserted = bpy.context.object
    assert inserted['caffmob_modelo_id'] == model['id'] and not inserted.children
    assert len([o for o in bpy.context.scene.objects if o.get('caffmob_modulo')]) == 2
    print('5. Inserir modelo: OK', flush=True)

    inserted.location.x += 0.05
    old_version = bpy.context.scene['caffmob_versao']
    operate(bpy.ops.caffmob.mobi_enviar_ambiente)
    assert bpy.context.scene['caffmob_versao'] == old_version + 1, state.situacao
    status, saved, _ = request('GET', '/api/draw/v1/ambientes/' + doc['id'])
    assert status == 200 and len(saved['modulos']) == 2
    assert any(entry['id'] in chapas.texturas_do_modulo(m) for m in saved['modulos'])
    print('6. Enviar alteração e conferir no servidor: OK', flush=True)

    remote = copy.deepcopy(saved)
    remote['nome'] = 'TESTE 063 alteração concorrente'
    status, updated, _ = request('PUT', '/api/draw/v1/ambientes/' + doc['id'], remote,
                               {'If-Match': '"{}"'.format(old_version + 1)})
    assert status == 200, (status, updated)
    inserted.location.x += 0.05
    operate(bpy.ops.caffmob.mobi_enviar_ambiente)
    assert state.conflito_local and state.conflito_mobi and '409' in state.situacao, state.situacao
    assert state.conflito_versao == updated['version']
    chosen = json.loads(state.conflito_local)
    operate(bpy.ops.caffmob.mobi_resolver_conflito, escolha='BLENDER')
    assert not state.conflito_local and not state.conflito_mobi
    status, resolved, _ = request('GET', '/api/draw/v1/ambientes/' + doc['id'])
    assert status == 200 and resolved['version'] == updated['version'] + 1
    assert ops_ambientes.same_document(chosen, resolved)
    print('7. HTTP 409 real e resolução BLENDER conferida: OK', flush=True)

    assert bpy.ops.caffmob.cabinet_builder(structure_id='coz_inferior_divisoria') == {'FINISHED'}
    assert bpy.context.object.btm_cabinet.structure_id
    with patch.object(downloads, 'request', wraps=downloads.request) as observed:
        assert bpy.ops.caffmob.mobi_enviar_modelo() == {'CANCELLED'}
        assert bpy.ops.caffmob.mobi_enviar_ambiente() == {'CANCELLED'}
        observed.assert_not_called()
    print('8. Armário da 015 recusado sem pedido (modelo e ambiente): OK', flush=True)

    tokens = []
    auth.with_access(tokens.append)
    wait(lambda: bool(tokens), 'token antes de revogar')
    assert tokens[0]
    assert bpy.ops.caffmob.mobi_desconectar() == {'FINISHED'}
    wait(lambda: not downloads._requests, 'revogação')
    assert not auth.signed_in() and not Path(auth.session_path()).exists()
    assert 'pendente' not in state.situacao.lower(), state.situacao
    status, _, _ = request('GET', '/api/draw/v1/ambientes',
                           headers={'Authorization': 'Bearer ' + tokens[0]}, authenticated=False)
    assert status == 401, status
    print('9. Desconectar revoga; token antigo: HTTP 401', flush=True)
finally:
    # Mesmo uma asserção falha não deixa uma vaga de aparelho ocupada no ensaio.
    try:
        if auth.signed_in():
            bpy.ops.caffmob.mobi_desconectar()
            wait(lambda: not downloads._requests, 'revogação na limpeza')
            print('Limpeza: sessão local encerrada e revogação concluída', flush=True)
    finally:
        addon.unregister()
print('BLENDER_ENSAIO_MOBI_OK', flush=True)
