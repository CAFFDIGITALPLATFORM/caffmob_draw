# (063 RF-01, RF-03 a RF-11; D-04 a D-11) Testes focados dos operadores, transporte simulado.
import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon
from caffmob_draw.mobi import cena, tarefas, texturas, ops_ambientes, respostas
from caffmob_draw.mobi.ops_biblioteca import EMPTY
from caffmob_draw.data.i18n import tr
from caffmob_draw.texture_library import auth, catalog, downloads, apply, handlers
from caffmob_draw.caffmob import chapas
from caffmob_draw.cutting import part_sources, part_extractor
from caffmob_draw.walls2d import scene_io, model
from caffmob_draw.operators import floor_builder

addon.register()
addon.load_file_post(None)
pending = []

def request(method, path, body=None, auth=True, callback=None, headers=None, form=False, response_headers=False):
    ticket = {'method':method, 'path':path, 'body':copy.deepcopy(body), 'headers':headers or {},
              'callback':callback, 'response_headers':response_headers, 'cancelled':False, 'form':form}
    pending.append(ticket)
    return ticket


def reply(status, body, headers=None):
    ticket = pending.pop(0)
    if not ticket['cancelled'] and ticket['callback']:
        args = (status, copy.deepcopy(body), headers or {}) if ticket['response_headers'] else (status, copy.deepcopy(body))
        ticket['callback'](*args)
    return ticket


def cancel(ticket):
    if ticket:
        ticket['cancelled'] = True


def document():
    path = ROOT / 'tests/casos_ouro/paredes/parede-ambiente-l.json'
    doc = json.loads(path.read_text())['entrada']
    doc['version'] = 7
    return doc


mod = json.loads((ROOT / 'tests/casos_ouro/pecas-addon/pecas-addon-base-double.json').read_text())['entrada']
doc = document()
from caffmob_draw.mobi.ops_biblioteca import instance
doc['modulos'] = [instance(mod, mod['id'])]
state = bpy.context.window_manager.btm_caffmob
assert state is not None
with tempfile.TemporaryDirectory() as directory, patch.object(downloads, 'request', side_effect=request), patch.object(downloads, 'cancel_request', side_effect=cancel), patch.object(downloads, 'cache_dir', side_effect=lambda:directory), patch.object(auth, 'session_path', return_value=directory + '/sessao.json'):
    auth.reload()
    # T038: código RFC 8628 e revogação, sem navegador nem rede reais.
    with patch.object(downloads, 'unavailable_reason', return_value=''):
        assert bpy.ops.caffmob.mobi_conectar() == {'FINISHED'}
        assert pending[0]['path'] == '/api/draw/aparelho/codigo'
        assert pending[0]['form']
        reply(200, {'device_code':'mobc_teste', 'user_code':'BCDF-GHJK', 'verification_uri_complete':'http://127.0.0.1/conectar',
                    'verification_uri':'http://127.0.0.1/conectar','expires_in':600,'interval':5})
        assert state.codigo == 'BCDF-GHJK'
        auth._state['flow'].next_poll = 0
        auth._poll()
        assert pending[0]['path'] == '/api/draw/aparelho/token'
        reply(200, {'access_token':'mobd_teste', 'refresh_token':'mobr_teste', 'expires_in':3600,
                    'titular':{'nome':'Oficina'}, 'pessoa':{'nome':'Ana'}})
        assert auth.pessoa_nome() == 'Ana'
        from caffmob_draw.mobi.ops_conta import CONNECTED, CONNECTED_PERSON
        from caffmob_draw.ui.sidebar_project import draw_mobi_account
        label = tr(CONNECTED_PERSON).format('Ana', 'Oficina')
        assert state.situacao == label
        # Mesmo texto no grupo CAFF MOBI e no quadro das preferências.
        layout = MagicMock()
        draw_mobi_account(layout)
        layout.label.assert_any_call(text=label, icon='CHECKMARK')
        prefs = MagicMock()
        addon.BTM_AddonPreferences.draw(prefs, bpy.context)
        prefs.layout.box.return_value.column.return_value.label.assert_any_call(text=label, icon='CHECKMARK')
        # Sessão 1.1.0 sem pessoa: só titular, até a renovação preencher.
        old = json.loads(Path(auth.session_path()).read_text())
        old.pop('pessoa')
        old['tokens'].pop('pessoa')
        Path(auth.session_path()).write_text(json.dumps(old))
        auth.reload()
        layout = MagicMock()
        draw_mobi_account(layout)
        layout.label.assert_any_call(text=tr(CONNECTED).format('Oficina'), icon='CHECKMARK')
        auth.with_access(lambda token: None)
        reply(200, {'access_token':'mobd_renovado', 'refresh_token':'mobr_renovado', 'expires_in':3600,
                    'titular':{'nome':'Oficina'}, 'pessoa':{'nome':'Beatriz'}})
        assert auth.pessoa_nome() == 'Beatriz'
        layout = MagicMock()
        draw_mobi_account(layout)
        layout.label.assert_any_call(text=tr(CONNECTED_PERSON).format('Beatriz', 'Oficina'), icon='CHECKMARK')
    # T039: cancelar antes da resposta deixa a cena idêntica.
    before = set(o.name for o in bpy.context.scene.objects)
    assert bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id']) == {'FINISHED'}
    assert state.ocupado
    assert bpy.ops.caffmob.mobi_cancelar() == {'FINISHED'}
    reply(200, doc)
    assert set(o.name for o in bpy.context.scene.objects) == before
    # T033/T034: baixar só aplica depois de preparar; módulo não ganha filhos nem dados da 015.
    bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id'])
    reply(200, doc)
    assert not state.ocupado, state.situacao
    root = next(o for o in bpy.context.scene.objects if o.get('caffmob_modulo'))
    assert len(root.children) == 0
    assert not root.btm_cabinet.structure_id
    assert root.btm_plane.object_kind == 'MODULE'
    actual = cena.documento_da_cena(bpy.context)
    assert ops_ambientes.same_document(actual, doc)
    # T035/T036: fonte de peças própria, piso único e sem conversão da parede de contrato.
    source = next(m for m in part_sources.iter_modules(bpy.context.scene) if m.obj is root)
    assert source.library == 'caffmob'
    expected = chapas.pecas_do_modulo(mod)
    parts = part_extractor.extract_parts_from_scene(bpy.context)
    assert {p.id for p in parts} == {p['id'] for p in expected}
    for part in parts:
        e = next(p for p in expected if p['id'] == part.id)
        assert (part.width, part.height, part.thickness, part.quantity, part.material, part.module_ref) == (e['width'],e['height'],e['thickness'],e['quantity'],e['material'],e['module_ref'])
    wall = next(o for o in bpy.context.scene.objects if o.get('caffmob_parede'))
    assert not scene_io.is_other_layer_wall(wall)
    plan = model.WallPlan()
    assert scene_io.convert_into(plan, [wall], bpy.context.scene) == [wall.name]
    assert not plan.chains and not plan.converted_sources
    assert floor_builder.scene_walls(bpy.context.scene) == ([], [])
    floors = [o.name for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'piso']
    assert len(floors) == 1
    assert bpy.ops.caffmob.adjust_floor() == {'FINISHED'}
    assert [o.name for o in bpy.context.scene.objects if o.get('caffmob_tipo') == 'piso'] == floors
    # T030/T037: material pelo sha; acabamento no contrato e preservação do slug antigo.
    image = bpy.data.images.new('Teste 063', width=2, height=2)
    image.filepath_raw = directory + '/image.png'
    image.file_format = 'PNG'
    image.save()
    sha = hashlib.sha256(Path(image.filepath_raw).read_bytes()).hexdigest()
    raw = {'id':'8f0d0210-1111-4111-8111-111111111111','fabricante':'Berneck','linha':'Linha','nome':'Madeira',
           'largura':2400,'altura':1200,'formato':'png','sha256_trabalho':sha,'sha256_miniatura':sha,'mapas':[]}
    entry = catalog.remember(raw)
    assert apply.apply_cached([root], raw['id'], image.filepath_raw) == 1
    assert chapas.texturas_do_modulo(cena._modulo_do_objeto(root)) == [raw['id']]
    mat = root.data.materials[0]
    assert mat['btm_texture_sha256'] == sha
    assert mat['btm_texture_formato'] == 'png'
    mapping = next(n for n in mat.node_tree.nodes if n.type == 'MAPPING')
    assert abs(mapping.inputs['Scale'].default_value[0] - 1/(entry['size-mm'][0]/1000)) < 1e-5
    cached = directory + '/' + sha + '.png'
    Path(cached).write_bytes(Path(image.filepath_raw).read_bytes())
    old = bpy.data.materials.new('014 antigo'); old['btm_texture_id']='slug/antigo'; old['btm_texture_path']='/original.jpg'
    with patch.object(downloads, 'cache_dir', return_value=directory):
        assert handlers.relink([mat,old])[0] == 1
    assert mat['btm_texture_path'] == cached
    assert old['btm_texture_path'] == '/original.jpg'
    # T040: envio por If-Match e conflito com duas versões; pedido cancelado não altera versão.
    bpy.ops.caffmob.mobi_enviar_ambiente()
    local = copy.deepcopy(pending[0]['body'])
    assert pending[0]['headers']['If-Match'] == '"7"'
    remote = dict(local, nome='Mudou no MOBI', version=9)
    reply(409, {'versao_atual':9, 'documento_atual':remote})
    assert json.loads(state.conflito_local)['nome'] == local['nome']
    assert json.loads(state.conflito_mobi)['nome'] == 'Mudou no MOBI'
    bpy.ops.caffmob.mobi_resolver_conflito(escolha='BLENDER')
    assert pending[0]['headers']['If-Match'] == '"9"'
    reply(200, {'version':10})
    assert bpy.context.scene['caffmob_versao'] == 10
    # T040: editar segmento mantém aberturas, muda só pelo contrato.
    bpy.context.view_layer.objects.active = wall
    s = json.loads(wall['caffmob_parede'])['segmentos'][0]
    result = bpy.ops.caffmob.mobi_editar_segmento(indice=0, comprimento=s['comprimento'], espessura=s['espessura']+1,
        pe_direito_inicial=s['pe_direito_inicial'], pe_direito_final=s['pe_direito_final'],
        afastamento=s['afastamento'], flecha=s['flecha'], sentido=s['sentido'], tipo=s['tipo'])
    assert result == {'FINISHED'}
    assert json.loads(wall['caffmob_parede'])['segmentos'][0]['espessura'] == s['espessura']+1
    # T041: biblioteca vazia, atual e versão escolhida; o modelo entra como cópia.
    bpy.ops.caffmob.mobi_listar_modelos()
    reply(200, {'itens':[]}); reply(200, {'itens':[]})
    assert state.situacao == tr(EMPTY), state.situacao
    for version in (0, 3):
        bpy.ops.caffmob.mobi_baixar_modelo(modelo_id=mod['id'], versao=version, escopo='titular')
        assert pending[0]['path'].endswith('/versoes/3') if version else pending[0]['path'].endswith(mod['id'])
        reply(200, mod, {'ETag':'"4"'})
        inserted = bpy.context.object
        assert inserted.get('caffmob_modelo_versao') == (version or 4)
        assert json.loads(inserted['caffmob_modulo'])['modelo'] == {'id': mod['id'], 'version': version or 4, 'escopo': 'titular'}
        assert cena._modulo_do_objeto(inserted)['id'] != mod['id']
        assert not inserted.children
    # T042: PUT e POST; 015 não emite pedido.
    bpy.ops.caffmob.mobi_enviar_modelo()
    assert pending[0]['method']=='PUT' and pending[0]['headers']['If-Match']=='"3"'
    reply(200, {'version':4})
    bpy.ops.caffmob.mobi_enviar_modelo(novo=True, nome='Modelo novo', escopo='pessoal')
    assert pending[0]['method']=='POST' and pending[0]['body']['escopo']=='pessoal'
    reply(201, {'id':mod['id'],'version':1})
    bpy.ops.caffmob.cabinet_builder(structure_id='coz_inferior_divisoria')
    before = len(pending)
    assert bpy.ops.caffmob.mobi_enviar_modelo() == {'CANCELLED'}
    assert bpy.ops.caffmob.mobi_enviar_ambiente() == {'CANCELLED'}
    assert len(pending) == before
    # Contrato incompatível nunca troca a cena.
    before = set(o.name for o in bpy.context.scene.objects)
    bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id'])
    reply(200, doc, {'X-Caffmob-Contrato':'ambiente/v2, modulo/v1'})
    assert set(o.name for o in bpy.context.scene.objects) == before
    assert state.situacao == respostas.message(200, doc, {'X-Caffmob-Contrato':'ambiente/v2, modulo/v1'})
    # T031: timer faz busca remota e miniatura visível, sem buscar a imagem de trabalho.
    from caffmob_draw.library_panel import draw, ops_click
    library = bpy.context.window_manager.btm_library
    library.mode, library.tab, library.search = 'MAX', 'TEXTURES', 'madeira'
    library.manufacturer, library.collection = 'Berneck', 'Linha'
    entry['sha256_miniatura'] = 'b'*64
    catalog._cache.update(items=[entry], next='p2', available=True)
    with patch.object(auth,'signed_in',return_value=True), patch.object(downloads,'unavailable_reason',return_value=''), \
         patch.object(catalog,'refresh') as refresh, patch.object(downloads,'fetch') as fetch, \
         patch.object(catalog,'refresh_manufacturers'), patch.object(draw.time,'monotonic') as clock, \
         patch.object(draw.grid_core,'visible_cells',return_value=[(0,(0,0,100,100))]):
        clock.return_value = 10.0
        draw._remote_tick()
        clock.return_value = 10.5
        draw._remote_tick()
        refresh.assert_called_with('madeira','Berneck','Linha',force=True)
        assert fetch.call_args.kwargs['entry']['url'].endswith('tamanho=miniatura')
        assert draw.texture_items(library)[-1]['id'] == draw._more_id
        from types import SimpleNamespace
        with patch.object(ops_click.grid_core,'hit_cell',return_value=1):
            assert ops_click.cell_at(bpy.context,SimpleNamespace(grid=(0,0,300,300)),1,1) == ''
        assert refresh.call_args.kwargs['more'] is True
    library.mode = 'MIN'
    # T041: as duas bibliotecas trazem miniaturas; cancelar o modelo conserva a cena.
    def preview(item_id, callback=None, entry=None):
        assert '/modelos/' in entry['url'] and entry['url'].endswith('/imagem')
        callback(cached, None)
    with patch.object(downloads,'fetch',side_effect=preview):
        bpy.ops.caffmob.mobi_listar_modelos()
        reply(200, {'itens':[{'id':mod['id'],'nome':'Titular','version':1,'categoria':'Cozinha','escopo':'titular'}]})
        reply(200, {'itens':[{'id':'outro','nome':'Pessoal','version':2,'categoria':'Quarto','escopo':'pessoal'}]})
    assert {i.escopo for i in state.modelos} == {'titular','pessoal'}
    assert all(i.imagem == cached for i in state.modelos)
    # Sem escopo, vale o da lista; sem lista que o conheça, o operador recusa sem pedido (063 T059).
    try:
        bpy.ops.caffmob.mobi_baixar_modelo(modelo_id='sem-lista')
        raise AssertionError('inserir sem escopo devia ser recusado')
    except RuntimeError as recusa:
        assert 'Liste os modelos' in str(recusa) or 'List the models' in str(recusa), recusa
    before = set(o.name for o in bpy.context.scene.objects)
    bpy.ops.caffmob.mobi_baixar_modelo(modelo_id=mod['id'])
    bpy.ops.caffmob.mobi_cancelar()
    reply(200, mod)
    assert set(o.name for o in bpy.context.scene.objects) == before
    # T039: cancelamento enquanto a textura está pendente também preserva a cena.
    textured = copy.deepcopy(doc)
    textured['modulos'][0] = chapas.aplicar_textura(textured['modulos'][0], 'TODAS', raw['id'])
    image_callbacks = []
    with patch.object(downloads,'fetch',side_effect=lambda tid, callback=None, entry=None:image_callbacks.append(callback)):
        bpy.ops.caffmob.mobi_baixar_ambiente(ambiente_id=doc['id'])
        reply(200, textured)
        reply(200, raw)
        assert state.ocupado
        bpy.ops.caffmob.mobi_cancelar()
        image_callbacks[0](cached,None)
    assert set(o.name for o in bpy.context.scene.objects) == before
    # T039: paginação explícita, sem perder a lista anterior ao cancelar.
    bpy.ops.caffmob.mobi_listar_ambientes()
    reply(200, {'itens':[{'id':doc['id'],'nome':doc['nome'],'version':7}], 'proximo':'p2'})
    assert state.ambientes[0].id == doc['id']
    bpy.ops.caffmob.mobi_listar_ambientes(mais=True)
    assert 'depois=p2' in pending[0]['path']
    bpy.ops.caffmob.mobi_cancelar()
    reply(200, {'itens':[], 'proximo':None})
    assert len(state.ambientes) == 1
    # T042: 409 de modelo e escolha do documento remoto.
    bpy.context.view_layer.objects.active = inserted
    bpy.ops.caffmob.mobi_enviar_modelo()
    remote_model = dict(pending[0]['body'], nome='Modelo remoto', version=11)
    reply(409, {'versao_atual':11, 'documento_atual':remote_model})
    assert state.conflito_tipo == 'modelo'
    bpy.ops.caffmob.mobi_resolver_conflito(escolha='MOBI')
    assert pending[0]['headers']['If-Match'] == '"11"'
    reply(200, {'version':12})
    assert inserted['caffmob_modelo_versao'] == 12
    assert cena._modulo_do_objeto(inserted)['nome'] == 'Modelo remoto'
    assert not inserted.children
    # T032: o registro não inclui mais o download em lote.
    assert bpy.types.Operator.bl_rna_get_subclass_py('BTM_OT_TextureDownloadAll') is None
addon.unregister()
assert not hasattr(bpy.types.WindowManager, 'btm_caffmob')
assert not tarefas._jobs
print('BLENDER_MOBI_OPERADORES_OK', flush=True)
