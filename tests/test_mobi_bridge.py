# (063 RF-03, RF-08, RF-10; D-04 a D-07) Ponte sem rede e sem Blender.
import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import _bootstrap
from test_catalogo_mobi import ITEM


class Ponte(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        timers = types.SimpleNamespace(is_registered=lambda f: False, register=lambda *a, **k: None, unregister=lambda f: None)
        self.bpy = types.SimpleNamespace(app=types.SimpleNamespace(online_access=True, timers=timers, version_string='5.2.2'),
            utils=types.SimpleNamespace(extension_path_user=lambda *a, **k: self.tmp.name),
            context=types.SimpleNamespace(preferences=types.SimpleNamespace(addons={})))
        self.stub = patch.dict(sys.modules, {'bpy': self.bpy})
        self.stub.start()
        self.dl = importlib.import_module('caffmob_draw.texture_library.downloads')
        self.auth = importlib.import_module('caffmob_draw.texture_library.auth')
        self.catalog = importlib.import_module('caffmob_draw.texture_library.catalog')
        self.dl._state.update(proc=None, token_sent='', cache_dir=self.tmp.name, server_override='http://127.0.0.1:1234')
        self.auth.reload()
        self.catalog._cache.update(query=None, busy=False, ticket=None, items=[], by_id={})
        self.auth._save({'access_token': 'mobd_x', 'refresh_token': 'mobr_x', 'expires_in':3600, 'titular':{'nome':'Oficina'}})

    def tearDown(self):
        self.dl._requests.clear()
        self.dl._callbacks.clear()
        self.dl._queue.items.clear()
        self.dl._queue.order.clear()
        self.auth.reload()
        self.stub.stop()
        self.tmp.cleanup()

    def test_offline_nunca_inicia_processo_mesmo_com_token(self):
        self.bpy.app.online_access = False
        result = []
        with patch.object(self.dl, '_ensure_process') as start:
            self.dl.request('GET', '/api/draw/v1/ambientes', callback=lambda s,b:result.append(s))
        start.assert_not_called()
        self.assertEqual(result, [None])

    def test_401_renova_uma_vez_e_preserva_cabecalhos(self):
        sent, results = [], []
        with patch.object(self.dl, '_ensure_process', return_value=True), patch.object(self.dl, '_send', side_effect=lambda m:sent.append(m) or True):
            self.dl.request('PUT', '/api/draw/v1/ambientes/id', {}, headers={'If-Match':'"7"'}, callback=lambda s,b,h:results.append((s,h)), response_headers=True)
            req = [m for m in sent if m['type']=='request'][-1]
            self.dl._dispatch({'type':'reply','rid':req['rid'],'status':401})
            renewal = [m for m in sent if m['type']=='request'][-1]
            self.assertEqual(renewal['path'], '/api/draw/aparelho/token')
            self.assertTrue(renewal['form'])
            self.dl._dispatch({'type':'reply','rid':renewal['rid'],'status':200,'body':{'access_token':'mobd_y','refresh_token':'mobr_y','expires_in':3600,'titular':{'nome':'Oficina'},'pessoa':{'nome':'Ana'}}})
            again = [m for m in sent if m['type']=='request'][-1]
            self.assertEqual(again['headers'], {'If-Match':'"7"'})
            self.dl._dispatch({'type':'reply','rid':again['rid'],'status':401,'headers':{'ETag':'"8"'}})
        self.assertEqual(self.auth.pessoa_nome(), 'Ana')
        self.auth.reload()
        self.assertEqual(self.auth.pessoa_nome(), 'Ana')
        self.assertEqual(self.auth.titular_nome(), 'Oficina')
        self.assertEqual(results, [(401, {'ETag':'"8"'})])
        self.assertEqual(len([m for m in sent if m.get('path')=='/api/draw/aparelho/token']), 1)

    def test_desconectar_monta_formulario_e_apaga_sessao(self):
        calls, results = [], []
        def request(*args, **kwargs):
            calls.append((args, kwargs))
            kwargs['callback'](200, {})
        with patch.object(self.dl, 'request', side_effect=request):
            self.auth.logout(results.append)
        self.assertEqual(calls[0][0][1], '/api/draw/aparelho/revogar')
        self.assertEqual(calls[0][0][2], {'client_id':'caffmob-draw','token':'mobr_x'})
        self.assertTrue(calls[0][1]['form'])
        self.assertFalse(Path(self.auth.session_path()).exists())
        self.assertEqual(results, [''])

    def test_catalogo_pagina_cursor_etag_e_cancelamento(self):
        calls = []
        def request(*args, **kwargs):
            calls.append((args, kwargs)); return {'rid':len(calls)}
        with patch.object(self.dl,'request',side_effect=request), patch.object(self.dl,'cancel_request'):
            self.catalog.refresh('madeira', 'Berneck', 'Linha')
            self.assertIn('busca=madeira', calls[-1][0][1])
            calls[-1][1]['callback'](200, {'itens':[ITEM], 'proximo':'p2'}, {'ETag':'"primeira"'})
            self.catalog.refresh('madeira', 'Berneck', 'Linha', more=True)
            self.assertIn('cursor=p2', calls[-1][0][1])
            self.catalog.cancel()
            calls[-1][1]['callback'](200, {'itens':[dict(ITEM,id='outro')], 'proximo':None}, {})
            self.assertEqual([i['id'] for i in self.catalog._cache['items']], ['uuid'])
            self.catalog._cache['query'] = None
            self.catalog.refresh('madeira', 'Berneck', 'Linha')
            self.assertEqual(calls[-1][1]['headers'], {'If-None-Match':'"primeira"'})
            calls[-1][1]['callback'](304, {}, {})
            self.assertEqual(self.catalog._cache['items'][0]['id'], 'uuid')

    def test_cache_de_imagem_com_etag_fraco_e_forte(self):
        import hashlib
        for prefix in ('W/', ''):
            with self.subTest(prefix=prefix):
                digest = hashlib.sha256(b'imagem').hexdigest()
                etag = prefix + '"' + digest + '"'
                item_id = 'imagem-' + prefix
                url = '/api/draw/v1/modelos/teste/imagem'
                path = Path(self.tmp.name) / 'temporario.png'
                path.write_bytes(b'imagem')
                self.dl._queue.add({'id':item_id, 'url':url, 'ext':'png'})
                result = []
                self.dl._callbacks[item_id] = [lambda p,e:result.append((p,e))]
                self.dl._dispatch({'type':'done', 'id':item_id, 'path':str(path), 'etag':etag})
                final = Path(self.tmp.name) / (digest + '.png')
                self.assertEqual(result, [(str(final), None)])
                self.assertEqual(final.read_bytes(), b'imagem')
                self.assertEqual(Path(str(final) + '.etag').read_text(), etag)
                metadata = Path(self.tmp.name) / (hashlib.sha256(url.encode()).hexdigest() + '.json')
                self.assertEqual(json.loads(metadata.read_text()), {'file':final.name, 'etag':etag})

    def test_catalogo_304_preserva_etag_fraco_opaco(self):
        calls = []
        with patch.object(self.dl, 'request', side_effect=lambda *a, **k:calls.append(k)):
            self.catalog.refresh('fraco')
            calls[-1]['callback'](200, {'itens':[ITEM], 'proximo':None}, {'etag':'W/"pagina"'})
            self.catalog._cache['query'] = None
            self.catalog.refresh('fraco')
            self.assertEqual(calls[-1]['headers'], {'If-None-Match':'W/"pagina"'})
            calls[-1]['callback'](304, {}, {})
            self.assertEqual(self.catalog._cache['items'][0]['id'], ITEM['id'])

    def test_cancelar_pedido_suprime_resposta(self):
        seen = []
        with patch.object(self.dl, '_ensure_process', return_value=True), patch.object(self.dl, '_send', return_value=True):
            ticket = self.dl.request('GET', '/api/draw/v1/ambientes', callback=lambda *a:seen.append(a))
            self.dl.cancel_request(ticket)
            self.dl._dispatch({'type':'reply', 'rid':ticket['rid'], 'status':200})
        self.assertEqual(seen, [])

    def test_user_agent_e_download_sob_demanda_pelo_sha(self):
        entry = self.catalog.remember(ITEM)
        self.assertTrue(self.dl._user_agent().startswith('CAFFMobDraw/'))
        self.assertIn('Blender/5.2.2', self.dl._user_agent())
        sent, result = [], []
        with patch.object(self.dl, '_ensure_process', return_value=True), patch.object(self.dl, '_send', side_effect=lambda m:sent.append(m) or True):
            self.dl.fetch(entry['id'], lambda p,e:result.append((p,e)), entry)
            get = next(m for m in sent if m['type']=='get')
            self.assertEqual(get['url'], '/api/draw/v1/texturas/uuid/imagem?tamanho=trabalho')
            self.assertTrue(get['dest'].endswith('a'*64 + '.jpg'))
            self.assertEqual(get['sha256'], 'a'*64)
            self.assertFalse(result)
            Path(get['dest']).write_bytes(b'arquivo')
            self.dl._dispatch({'type':'done','id':entry['id'],'path':get['dest']})
            count = len(sent)
            self.dl.fetch(entry['id'], lambda p,e:result.append((p,e)), entry)
            self.assertEqual(len(sent), count)
            self.assertEqual(len(result), 2)

    def test_resposta_de_login_cancelado_nao_reabre_o_fluxo(self):
        callbacks = []
        def request(*args, **kwargs):
            callbacks.append(kwargs['callback'])
        with patch.object(self.dl, 'request', side_effect=request):
            self.auth.start_login()
            self.auth.cancel_login()
            callbacks[0](200, {'device_code':'codigo','user_code':'BCDF-GHJK','verification_uri':'http://127.0.0.1'})
        self.assertIsNone(self.auth._state['flow'])

    def test_mudanca_de_servidor_durante_renovacao_nao_salva_tokens(self):
        callbacks, returned = [], []
        self.auth.invalidate_access()
        with patch.object(self.dl, 'request', side_effect=lambda *a, **k:callbacks.append(k['callback'])):
            self.auth.with_access(returned.append)
            self.dl._state['server_override'] = 'http://127.0.0.1:9876'
            callbacks[0](200, {'access_token':'novo','refresh_token':'novo'})
        self.assertEqual(returned, [''])
        self.assertEqual(json.loads(Path(self.auth.session_path()).read_text())['server'], 'http://127.0.0.1:1234')

    def test_renovacao_preserva_arquivo_e_so_invalid_grant_apaga(self):
        for status, body in [(502,{}),(429,{}),(None,{})]:
            self.auth.invalidate_access()
            callbacks = []
            with patch.object(self.dl, 'request', side_effect=lambda *a, **k:callbacks.append(k['callback'])):
                self.auth.with_access(lambda token:None)
                callbacks[0](status,body)
            self.assertTrue(Path(self.auth.session_path()).exists())
            self.assertTrue(self.auth.signed_in())
        callbacks = []
        with patch.object(self.dl, 'request', side_effect=lambda *a, **k:callbacks.append(k['callback'])):
            self.auth.with_access(lambda token:None)
            callbacks[0](400,{'error':'invalid_grant'})
        self.assertFalse(Path(self.auth.session_path()).exists())
        self.assertFalse(self.auth.signed_in())

    def test_logout_sem_rede_remove_e_avisa(self):
        result = []
        self.bpy.app.online_access = False
        with patch.object(self.dl,'request') as request:
            self.auth.logout(result.append)
        request.assert_not_called()
        self.assertFalse(Path(self.auth.session_path()).exists())
        self.assertIn('Aparelhos conectados',result[0])

    def test_troca_do_codigo_guarda_pessoa_e_sessao_antiga_mostra_so_titular(self):
        self.assertEqual(self.auth.pessoa_nome(), '')
        self.assertEqual(self.auth.titular_nome(), 'Oficina')
        with patch.object(self.dl, 'request') as request:
            self.auth.start_login()
            request.call_args.kwargs['callback'](200, {'device_code':'codigo', 'user_code':'BCDF-GHJK',
                'verification_uri':'http://127.0.0.1', 'expires_in':600, 'interval':5})
            self.auth._state['flow'].next_poll = 0
            self.auth._poll()
            request.call_args.kwargs['callback'](200, {'access_token':'mobd_novo', 'refresh_token':'mobr_novo',
                'expires_in':3600, 'titular':{'nome':'Oficina'}, 'pessoa':{'nome':'Ana'}})
        self.auth.reload()
        self.assertEqual(self.auth.pessoa_nome(), 'Ana')
        self.assertEqual(json.loads(Path(self.auth.session_path()).read_text())['pessoa'], {'nome':'Ana'})
