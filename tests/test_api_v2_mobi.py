"""065 T112 B01 a B09: transportes falsos, subprocesso real sem abrir rede ou Blender."""
import copy
import importlib.util
import io
import json
import sys
import types
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch
import _bootstrap  # noqa: F401
from caffmob_draw.mobi.api_v2_core import (ClienteV2, Operacao, ACCEPT, SCHEMA_V1, SCHEMA_V2,
                                          confirmar_recibo, Conflito)
from caffmob_draw.mobi.api_v2 import ArmazenamentoCena, PROPRIEDADE, cliente

PASTA_REDE = Path(__file__).parents[1] / 'caffmob_draw/texture_library'
sys.path.insert(0, str(PASTA_REDE))
_spec = importlib.util.spec_from_file_location('worker_v2_ensaio', PASTA_REDE / 'downloader.py')
worker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(worker)
sys.path.remove(str(PASTA_REDE))

DOCUMENTO = json.loads((Path(__file__).parent / 'casos_ouro_v2/referencia-rica.json').read_text())['entrada']
CAPACIDADES = {'versao_api': 2, 'schemas': [SCHEMA_V1, SCHEMA_V2], 'ambientes_v2': True,
               'idempotencia': 'chave-duravel', 'maximo_documento_bytes': 1048576}


class TransporteFalso:
    def __init__(self, respostas=()):
        self.respostas = list(respostas)
        self.chamadas = []
        self.antes = None
        self.callbacks = []

    def __call__(self, metodo, path, corpo=None, headers=None, callback=None):
        if self.antes:
            self.antes()
        self.chamadas.append((metodo, path, copy.deepcopy(corpo), copy.deepcopy(headers)))
        self.callbacks.append(callback)
        if self.respostas:
            callback(*self.respostas.pop(0))
        return {'rid': len(self.chamadas)}


class Resposta:
    def __init__(self, status, body, headers):
        self.status, self.headers = status, headers
        self.raw = json.dumps(body).encode()
    def read(self):
        return self.raw
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class SubprocessoFalso:
    """Executa Worker.request e build reais, trocando apenas I/O e a espera."""
    def __init__(self, respostas):
        self.respostas, self.chamadas, self.esperas = list(respostas), [], []
        self.worker = worker.Worker('https://ensaio.invalid', 'CAFFMobDraw/ensaio')
        self.worker.opener = lambda _: types.SimpleNamespace(open=self.abrir)

    def abrir(self, request, timeout):
        self.chamadas.append((request.get_method(), request.full_url, request.data, dict(request.header_items()), timeout))
        status, body, headers = self.respostas.pop(0)
        if status is None:
            raise urllib.error.URLError('tempo esgotado')
        if status >= 400:
            raise urllib.error.HTTPError(request.full_url, status, 'ensaio', headers, io.BytesIO(json.dumps(body).encode()))
        return Resposta(status, body, headers)

    def __call__(self, metodo, path, corpo=None, headers=None, callback=None):
        self.worker.say = lambda **r: callback(r['status'], r['body'], r['headers'])
        with patch.object(worker.time, 'sleep', side_effect=self.esperas.append):
            self.worker.request('ensaio', metodo, path, corpo, True, headers)
        return {'rid': 'ensaio'}


class ApiV2(unittest.TestCase):
    def setUp(self):
        self.scene = {}
        self.storage = ArmazenamentoCena(self.scene)
        self.session = {'capacidades': copy.deepcopy(CAPACIDADES)}
        self.retorno = []

    def novo(self, transporte, online=lambda: True, v1=None):
        return ClienteV2(transporte, self.storage, self.session, online, v1)

    def recibo(self, version=2):
        return {'id': DOCUMENTO['id'], 'version': version, 'atualizado_em': '2026-10-20T10:00:00.000Z'}

    def test_B01_online_desligado_zero_chamadas(self):
        t = TransporteFalso()
        c = self.novo(t, online=lambda: False)
        c.descobrir(self.retorno.append)
        c.enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        c.ler(DOCUMENTO['id'], lambda *a: None)
        c.listar(lambda *a: None)
        self.assertEqual(t.chamadas, [])
        self.assertNotIn(PROPRIEDADE, self.scene)
        # O adaptador consulta bpy.app.online_access a cada pedido.
        bpy = types.SimpleNamespace(app=types.SimpleNamespace(online_access=False, translations=types.SimpleNamespace(pgettext_iface=lambda s, *a: s)))
        with patch.dict(sys.modules, {'bpy': bpy}):
            cliente(types.SimpleNamespace(scene=self.scene), types.SimpleNamespace(request=t), self.session).descobrir(self.retorno.append)
        self.assertEqual(t.chamadas, [])

    def test_B02_descoberta_404_delega_v1_e_recusa_v2(self):
        self.session.clear()
        t, v1 = TransporteFalso([(404, {}, {})]), []
        c = self.novo(t, v1=lambda *a: v1.append(a))
        c.descobrir(self.retorno.append)
        self.assertEqual(self.session['capacidades']['versao_api'], 1)
        d = dict(DOCUMENTO, schema=SCHEMA_V1)
        c.enviar(d, 'PUT', 1, self.retorno.append)
        self.assertEqual(v1[0][0], d)
        self.assertEqual(c.rota(SCHEMA_V1), '/api/draw/v1')
        with self.assertRaises(ValueError):
            c.enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        self.assertEqual(len(t.chamadas), 1)
        self.assertNotIn(PROPRIEDADE, self.scene)

    def test_descoberta_erro_nao_faz_fallback(self):
        self.session.clear()
        for status in (None, 401, 502):
            t = TransporteFalso([(status, {}, {})])
            c = self.novo(t)
            c.descobrir(self.retorno.append)
            with self.assertRaises(ValueError):
                c.enviar(DOCUMENTO, 'POST', None, self.retorno.append)
            self.assertEqual(len(t.chamadas), 1)
        self.assertNotIn('capacidades', self.session)

    def test_capacidades_guardadas_com_campos_aditivos(self):
        caps = dict(CAPACIDADES, novo_campo='futuro')
        t = TransporteFalso([(200, caps, {})])
        self.novo(t).descobrir(self.retorno.append)
        self.assertEqual(self.session['capacidades'], caps)
        self.assertEqual(t.chamadas[0][1], '/api/draw/v2/capacidades')

    def test_B03_put_resposta_perdida_reenvia_chave_e_revisao_recebe_recibo_antigo(self):
        t = SubprocessoFalso([(None, {}, {}), (200, self.recibo(), {'Idempotency-Replayed': 'true'}),
                             (200, dict(DOCUMENTO, version=7), {'ETag': '"7"'})])
        self.novo(t).enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        self.assertEqual(t.esperas, [2])
        self.assertEqual(t.chamadas[0][2:4], t.chamadas[1][2:4])
        self.assertEqual(t.chamadas[0][3]['If-match'], '"1"')
        self.assertNotIn(PROPRIEDADE, self.scene)
        r = self.retorno[0]
        self.assertTrue(r.replay)
        self.assertEqual(r.corpo['version'], 2)
        self.assertEqual(r.atual['version'], 7)
        self.assertEqual([a[0] for a in t.chamadas], ['PUT', 'PUT', 'GET'])

    def test_post_resposta_perdida_uuid_estavel(self):
        t = SubprocessoFalso([(None, {}, {}), (201, self.recibo(1), {'Idempotency-Replayed': 'true'}),
                             (200, DOCUMENTO, {})])
        self.novo(t).enviar(DOCUMENTO, 'POST', None, self.retorno.append)
        self.assertEqual(t.chamadas[0][2:4], t.chamadas[1][2:4])
        self.assertNotIn(PROPRIEDADE, self.scene)

    def test_B04_5xx_2_4_8_e_tentar_novamente_mesma_chave(self):
        t = SubprocessoFalso([(502, {}, {})] * 4)
        c = self.novo(t)
        c.enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        self.assertEqual(t.esperas, [2, 4, 8])
        self.assertEqual(len(t.chamadas), 4)
        self.assertEqual(len({a[3]['Idempotency-key'] for a in t.chamadas}), 1)
        chave = self.storage.ler().chave
        self.assertEqual(self.retorno[-1].mensagem, 'Tentar novamente')
        t.respostas = [(200, self.recibo(), {})]
        c.reenviar(self.retorno.append)
        self.assertEqual(t.chamadas[-1][3]['Idempotency-key'], chave)
        self.assertNotIn(PROPRIEDADE, self.scene)

    def test_B05_429_retry_after_ate_seis_vezes(self):
        t = SubprocessoFalso([(429, {}, {'Retry-After': '17'})] * 7)
        self.novo(t).enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        self.assertEqual(t.esperas, [17] * 6)
        self.assertEqual(len(t.chamadas), 7)
        self.assertEqual(len({a[3]['Idempotency-key'] for a in t.chamadas}), 1)
        self.assertIsNotNone(self.storage.ler())
        self.assertEqual(self.retorno[-1].mensagem, 'Tentar novamente')

    def test_B06_conflito_conserva_duas_versoes_e_tres_escolhas(self):
        remota = dict(DOCUMENTO, version=8, nome='Remota')
        t = TransporteFalso([(409, {'erro': 'VERSAO_DIVERGENTE', 'versao_atual': 8, 'documento_atual': remota}, {})])
        self.novo(t).enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        conflito = self.retorno[0].conflito
        self.assertEqual(conflito.local, DOCUMENTO)
        self.assertEqual(conflito.remota, remota)
        self.assertEqual(conflito.escolhas, ('remota', 'local', 'copia'))
        self.assertEqual(len(conflito.rotulos()), 3)
        self.assertEqual(conflito.escolher('remota'), remota)
        local = conflito.escolher('local')
        self.assertEqual(local.revisao_base, 8)
        self.assertEqual(local.documento, DOCUMENTO)
        self.assertNotEqual(local.chave, self.storage.ler().chave)
        copia = conflito.escolher('copia')
        self.assertEqual(copia.metodo, 'POST')
        self.assertNotEqual(copia.ambiente_id, DOCUMENTO['id'])
        self.assertNotEqual(copia.chave, local.chave)
        self.assertIsNone(copia.revisao_base)
        self.assertEqual(len(t.chamadas), 1)

    def test_B07_propriedade_antes_do_envio_reabre_e_so_confirma_a_chave_certa(self):
        t = TransporteFalso()
        t.antes = lambda: self.assertIsNotNone(self.storage.ler())
        self.novo(t).enviar(DOCUMENTO, 'POST', None, self.retorno.append)
        cena_reaberta = json.loads(json.dumps(self.scene))
        storage = ArmazenamentoCena(cena_reaberta)
        self.assertEqual(storage.ler(), self.storage.ler())
        storage.confirmar('outra-chave')
        self.assertIsNotNone(storage.ler())
        t2 = TransporteFalso([(201, self.recibo(1), {})])
        ClienteV2(t2, storage, self.session).reenviar(self.retorno.append)
        self.assertEqual(t2.chamadas[0][3]['Idempotency-Key'], self.storage.ler().chave)
        self.assertNotIn(PROPRIEDADE, cena_reaberta)

    def test_B08_cancelar_job_real_preserva_operacao_ate_recibo(self):
        import caffmob_draw.texture_library as biblioteca
        class Cena(dict):
            name = 'Ensaio'
        self.scene = Cena()
        self.storage = ArmazenamentoCena(self.scene)
        estado = types.SimpleNamespace(ocupado=False, progresso=0, situacao='')
        context = types.SimpleNamespace(scene=self.scene, window_manager=types.SimpleNamespace(btm_caffmob=estado))
        handlers = types.ModuleType('bpy.app.handlers')
        handlers.persistent = lambda f: f
        bpy = types.SimpleNamespace(context=context,
            app=types.SimpleNamespace(online_access=True, translations=types.SimpleNamespace(pgettext_iface=lambda s, *a: s)),
            types=types.SimpleNamespace(Operator=object), props=types.SimpleNamespace(StringProperty=lambda: None))
        callbacks, cancelados = [], []
        bridge = types.SimpleNamespace(request=lambda *a, **k: callbacks.append(k['callback']) or {'rid': 1},
                                       cancel_request=cancelados.append)
        spec = importlib.util.spec_from_file_location('caffmob_draw.mobi.tarefas_ensaio',
            Path(__file__).parents[1] / 'caffmob_draw/mobi/tarefas.py')
        tarefas = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'bpy': bpy, 'bpy.app.handlers': handlers}), patch.object(biblioteca, 'downloads', bridge, create=True):
            spec.loader.exec_module(tarefas)
            job = tarefas.Job(context, 'Ensaio')
            cliente(context, job, self.session).enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
            antes = copy.deepcopy(self.scene)
            job.cancel()
            callbacks[0](200, self.recibo(), {})
            self.assertEqual(cancelados, [{'rid': 1}])
            self.assertEqual(self.retorno, [])
            self.assertEqual(self.scene, antes)
        t2 = TransporteFalso([(200, self.recibo(), {'Idempotency-Replayed': 'true'}), (404, {'erro': 'NAO_ENCONTRADO'}, {})])
        self.novo(t2).reenviar(self.retorno.append)
        self.assertNotIn(PROPRIEDADE, self.scene)
        self.assertEqual(self.retorno[-1].status_atual, 404)
        self.assertEqual([c[0] for c in t2.chamadas], ['PUT', 'GET'])

    def test_B09_accept_nas_chamadas(self):
        t = TransporteFalso([(200, CAPACIDADES, {})])
        c = self.novo(t)
        c.descobrir(self.retorno.append)
        c.listar(lambda *a: None)
        c.ler(DOCUMENTO['id'], lambda *a: None)
        c.enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
        self.assertTrue(all(a[3]['Accept'] == ACCEPT for a in t.chamadas))
        self.assertEqual(t.chamadas[-1][3]['Content-Type'], 'application/json; charset=utf-8')

    def test_pedido_congelado_nao_usa_edicao_posterior(self):
        t = TransporteFalso()
        c = self.novo(t)
        d = copy.deepcopy(DOCUMENTO)
        c.enviar(d, 'PUT', 1, self.retorno.append)
        d['nome'] = 'Outra intenção'
        with self.assertRaises(ValueError):
            c.enviar(d, 'PUT', 1, self.retorno.append)
        c.reenviar(self.retorno.append)
        self.assertEqual(t.chamadas[0], t.chamadas[1])

    def test_erros_nao_confirmam_chave_nem_fazem_fallback(self):
        for status, corpo in [(404, {}), (406, {}), (409, {'erro': 'CHAVE_REUTILIZADA'}),
                              (413, {}), (422, {}), (428, {}), (200, {})]:
            self.scene.clear()
            t = TransporteFalso([(status, corpo, {})])
            self.novo(t).enviar(DOCUMENTO, 'PUT', 1, self.retorno.append)
            self.assertIsNotNone(self.storage.ler())
            self.assertEqual(len(t.chamadas), 1)
            self.assertTrue(t.chamadas[0][1].startswith('/api/draw/v2/'))

    def test_adapter_usa_job_request(self):
        t = TransporteFalso([(200, CAPACIDADES, {})])
        with patch.dict(sys.modules, {'bpy': types.SimpleNamespace(app=types.SimpleNamespace(online_access=True))}):
            c = cliente(types.SimpleNamespace(scene=self.scene), types.SimpleNamespace(request=t), self.session)
            c.descobrir(self.retorno.append)
        self.assertEqual(len(t.chamadas), 1)

    def test_documento_invalido_nao_inicia_envio(self):
        t = TransporteFalso()
        d = dict(DOCUMENTO, preco=999)
        with self.assertRaises(ValueError):
            self.novo(t).enviar(d, 'POST', None, self.retorno.append)
        self.assertEqual(t.chamadas, [])
        self.assertEqual(self.scene, {})

    def test_recibo_confere_id_metodo_e_revisao(self):
        operacao = Operacao.criar(DOCUMENTO, 'PUT', 7)
        self.assertTrue(confirmar_recibo(operacao, 200, self.recibo(8)))
        for status, corpo in ((201, self.recibo(8)), (200, self.recibo(9)),
                              (200, dict(self.recibo(8), id='outro')), (200, {})):
            self.assertFalse(confirmar_recibo(operacao, status, corpo))
