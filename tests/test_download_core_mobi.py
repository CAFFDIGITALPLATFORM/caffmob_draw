# (063 RF-10; D-04) Protocolo de rede contra HTTP local.
import hashlib
import importlib.util
import json
import tempfile
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
import _bootstrap
from caffmob_draw.texture_library import download_core

spec = importlib.util.spec_from_file_location('mobi_worker', _bootstrap.PACKAGE / 'texture_library/downloader.py')
worker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(worker)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        self.server.seen.append((self.path, dict(self.headers), self.rfile.read(int(self.headers.get('Content-Length', 0)))))
        status = self.server.statuses.pop(0) if self.server.statuses else 200
        self.send_response(status)
        self.send_header('ETag', '"pagina"')
        self.send_header('Retry-After', '90')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        self.server.seen.append((self.path, dict(self.headers), b''))
        self.send_response(304 if self.headers.get('If-None-Match') else 200)
        self.send_header('ETag', '"' + ('0'*64 if getattr(self.server, 'bad_etag', False) else hashlib.sha256(b'imagem').hexdigest()) + '"')
        self.end_headers()
        if not self.headers.get('If-None-Match'):
            self.wfile.write(b'imagem')


class Protocolo(unittest.TestCase):
    def setUp(self):
        self.http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.http.seen, self.http.statuses = [], []
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.w = worker.Worker('http://127.0.0.1:' + str(self.http.server_port), 'CAFFMobDraw/test Blender/test')
        self.messages = []
        self.w.say = lambda **m: self.messages.append(m)

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join()

    def test_formulario_e_cabecalhos_nas_duas_direcoes(self):
        self.w.request(1, 'POST', '/codigo', {'nome': 'Blender estúdio'}, False,
                       {'If-Match': '"7"', 'If-None-Match': '"6"'}, True)
        _, headers, body = self.http.seen[0]
        self.assertEqual(body.decode(), 'nome=Blender+est%C3%BAdio')
        self.assertEqual(headers['Content-Type'], 'application/x-www-form-urlencoded')
        self.assertEqual(headers['If-Match'], '"7"')
        self.assertEqual(headers['If-None-Match'], '"6"')
        self.assertEqual(self.messages[-1]['etag'], '"pagina"')
        self.assertEqual(self.messages[-1]['headers']['ETag'], '"pagina"')

    def test_request_repete_5xx_e_429(self):
        for statuses, expected in [([502,503,500,200], [2,4,8]), ([429]*7, [60]*6)]:
            self.http.statuses = list(statuses)
            with patch.object(worker.time, 'sleep') as sleep:
                self.w.request(1, 'POST', '/token', {}, False)
            self.assertEqual([c.args[0] for c in sleep.call_args_list], expected)
            self.assertEqual(self.messages[-1]['status'], statuses[-1])

    def test_request_sem_rede_repete(self):
        with patch.object(self.w, 'opener', side_effect=OSError('sem rede')), patch.object(worker.time, 'sleep') as sleep:
            self.w.request(1, 'GET', '/x', None, False)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2,4,8])
        self.assertIsNone(self.messages[-1]['status'])

    def test_get_sem_sha_confere_etag_e_revalida_304(self):
        with tempfile.TemporaryDirectory() as tmp:
            item = {'id': 'bump', 'url': '/bump', 'dest': tmp + '/bump', 'bytes': 0}
            self.w.download(item)
            self.assertEqual(self.messages[-1]['type'], 'done')
            self.assertEqual(Path(item['dest']).read_bytes(), b'imagem')
            self.w.download(item)
            self.assertEqual(self.messages[-1]['type'], 'done')
            self.assertIn('If-None-Match', self.http.seen[-1][1])

    def test_recusa_hash_divergente(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.w.download({'id': 'x', 'url': '/x', 'dest': tmp + '/x', 'sha256': '0'*64})
            self.assertEqual(self.messages[-1]['code'], 'hash')
            self.assertFalse(Path(tmp + '/x').exists())

    def test_recuos_e_limites(self):
        self.assertEqual([download_core.retry_delay(i, None) for i in range(1,5)], [2,4,8,None])
        self.assertIsNone(download_core.retry_delay(7,429,'3'))

    def test_get_sem_sha_recusa_etag_divergente(self):
        self.http.bad_etag = True
        with tempfile.TemporaryDirectory() as tmp:
            self.w.download({'id':'x', 'url':'/x', 'dest':tmp + '/x'})
            self.assertEqual(self.messages[-1]['code'], 'hash')
            self.assertFalse(Path(tmp + '/x').exists())

    def test_subprocesso_transporta_formulario_headers_e_etag(self):
        proc = subprocess.Popen([sys.executable, str(_bootstrap.PACKAGE / 'texture_library/downloader.py'),
                                 '--base', self.w.base, '--ua', self.w.user_agent],
                                stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            proc.stdin.write(download_core.encode({'type':'request','rid':1,'method':'POST','path':'/codigo',
                             'body':{'client_id':'caffmob-draw'},'auth':False,'form':True,'headers':{'If-Match':'"7"'}}))
            proc.stdin.flush()
            import select
            self.assertTrue(select.select([proc.stdout], [], [], 5)[0])
            reply = json.loads(proc.stdout.readline())
            self.assertEqual(reply['status'],200)
            self.assertEqual(reply['etag'],'"pagina"')
            self.assertEqual(self.http.seen[-1][1]['If-Match'],'"7"')
            self.assertEqual(self.http.seen[-1][2],b'client_id=caffmob-draw')
        finally:
            proc.stdin.close()
            proc.wait(timeout=5)
            proc.stdout.close()
