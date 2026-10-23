"""Regressão #30 e #31: catálogo embutido, slug → UUID ao aplicar e falhas recuperáveis.

Desde BUG-20261023-EIAR (#153) a navegação é sempre local: conectar não troca o catálogo nem pede páginas, fabricantes
ou miniaturas à conta; a conta só entra ao aplicar ou soltar a textura (`resolve`)."""
import shutil
import unicodedata
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import caffmob_draw as addon
from caffmob_draw.library_panel import draw
from caffmob_draw.texture_library import auth, catalog, downloads, apply, handlers, downloader

ITEM = {'id': 'uuid-grade', 'fabricante': 'Fabricante', 'linha': 'Linha', 'nome': 'Madeira',
        'largura': 1200, 'altura': 1200, 'formato': 'jpeg', 'sha256_trabalho': 'a' * 64,
        'sha256_miniatura': 'b' * 64, 'mapas': []}


class Grade(unittest.TestCase):
    def setUp(self):
        catalog.invalidate()
        self.state = bpy.context.window_manager.btm_library
        self.state.mode, self.state.tab = 'MAX', 'TEXTURES'
        self.state.search = self.state.manufacturer = self.state.collection = ''
        self.pending, self.images = [], []
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        for target, options in [
            ('signed_in', {'return_value': True}),
        ]:
            p = patch.object(auth, target, **options); p.start(); self.addCleanup(p.stop)
        for target, options in [
            ('unavailable_reason', {'return_value': ''}),
            ('cache_dir', {'return_value': self.directory.name}),
            ('request', {'side_effect': self.request}),
            ('fetch', {'side_effect': self.fetch}),
        ]:
            p = patch.object(downloads, target, **options); p.start(); self.addCleanup(p.stop)
        self.clock = patch.object(draw.time, 'monotonic', return_value=100.0).start()
        self.addCleanup(patch.stopall)

    def request(self, method, path, body=None, callback=None, **kwargs):
        ticket = {'rid': None, 'cancelled': False, 'path': path, 'callback': callback, 'headers': kwargs.get('headers', {}), 'response_headers': kwargs.get('response_headers', False)}
        self.pending.append(ticket)
        return ticket

    def fetch(self, item_id, callback=None, entry=None):
        self.images.append((item_id, callback, entry))

    def answer(self, ticket, status=200, body=None, headers=None):
        body = body if body is not None else {'itens': [ITEM], 'proximo': None}
        args = (status, body, headers or {}) if ticket['response_headers'] else (status, body)
        ticket['callback'](*args)

    def tick(self, advance=1.0):
        self.clock.return_value += advance
        return draw._remote_tick()

    def populate(self):
        self.tick(); self.tick()
        for ticket in list(self.pending):
            if 'fabricantes' in ticket['path']:
                self.answer(ticket, body={'itens': [{'fabricante': 'Fabricante', 'total': 1, 'linhas': []}]})
            else:
                self.answer(ticket)
        self.tick()

    def test_00_conectado_navega_no_catalogo_local_sem_rede(self):
        self.state.manufacturer, self.state.collection = 'arauco', 'colecao-realce'
        for _ in range(4):
            self.tick()
        self.assertEqual([m[0] for m in catalog.manufacturers()][:1], ['arauco'])
        self.assertEqual(len(draw.texture_items(self.state)), 14)
        self.assertEqual((self.state.manufacturer, self.state.collection), ('arauco', 'colecao-realce'))
        self.assertFalse(self.pending, 'Navegar não chama a conta')
        self.assertFalse(self.images, 'As miniaturas são as do catálogo local')
        self.assertFalse(catalog.has_more())

    def test_05_callback_falho_avisa(self):
        def broken(*args):
            raise ValueError('callback de teste')
        downloads._requests[999] = broken
        downloads._dispatch({'type': 'reply', 'rid': 999, 'status': 200, 'body': {}})
        self.assertTrue(catalog.load()[1])

    def test_06_sem_sessao_mostra_embutido_sem_rede(self):
        with patch.object(auth, 'signed_in', return_value=False):
            self.tick()
            items = draw.texture_items(self.state)
            self.assertEqual(len(items), 1209)
            self.assertTrue(draw.texture_tree())
            self.assertTrue(all(Path(catalog.thumb_path(i)).is_file() for i in items))
            self.assertFalse(self.pending)
            self.assertFalse(self.images)
            self.state.manufacturer = draw.texture_tree()[0][0]
            self.assertLess(len(draw.texture_items(self.state)), 1209)
            self.assertFalse(catalog.has_more())

    def test_08_slug_resolve_uuid_e_metadados_atuais(self):
        with patch.object(auth, 'signed_in', return_value=False):
            local = draw.texture_items(self.state)[0]
        expected = str(uuid.uuid5(uuid.UUID('5b0c7d6e-2f41-4c8a-9e3d-0a62e7f1c062'), local['file']))
        result = []
        catalog.resolve(local['id'], lambda entry, error: result.append((entry, error)))
        ticket = self.pending[-1]
        self.assertEqual(ticket['path'], '/api/draw/v1/texturas/' + expected)
        self.answer(ticket, body=dict(ITEM, id=expected))
        entry, error = result[0]
        self.assertFalse(error)
        self.assertEqual(entry['id'], expected)
        self.assertEqual(entry['sha256'], ITEM['sha256_trabalho'])
        self.assertNotEqual(entry['sha256'], local['sha256'])
        # Aplicação grava UUID e hash atuais; relink continua pelo sha do derivado.
        obj = bpy.context.active_object
        path = catalog.thumb_path(local)
        self.assertEqual(apply.apply_cached([obj], entry['id'], path), 1)
        mat = obj.data.materials[0]
        self.assertEqual(mat['btm_texture_id'], expected)
        self.assertEqual(mat['btm_texture_sha256'], ITEM['sha256_trabalho'])
        # Retoma também o caminho público a partir do slug, gravando o UUID.
        status, value = apply.apply([obj], local['id'])
        self.assertEqual(status, apply.QUEUED)
        tid, callback, entry = self.images[-1]
        self.assertEqual(tid, expected)
        callback(path, None)
        cache = Path(downloads.cache_path(catalog.item(tid)))
        shutil.copyfile(path, cache)
        mat = obj.data.materials[0]
        from caffmob_draw.object_library import retexture
        mat[retexture.PATH_PROP] = '/caminho/antigo.jpg'
        fixed, unknown = handlers.relink([mat])
        self.assertEqual(fixed, 1)
        self.assertFalse(unknown)
        self.assertEqual(mat['btm_texture_id'], expected)
        self.assertEqual(mat['btm_texture_sha256'], ITEM['sha256_trabalho'])

    def test_10_ligacao_nfc_e_item_ausente_no_mobi(self):
        with patch.object(auth, 'signed_in', return_value=False):
            items = draw.texture_items(self.state)
        self.assertEqual(len({i['mobi_id'] for i in items}), 1209)
        for entry in items:
            nfc = unicodedata.normalize('NFC', entry['file'])
            self.assertEqual(entry['mobi_id'], str(uuid.uuid5(catalog.NAMESPACE, nfc)))
        status, value = apply.apply([bpy.context.active_object], items[0]['id'])
        self.assertEqual(status, apply.QUEUED)
        self.answer(self.pending[-1], 404, {})
        self.assertFalse(self.images, 'Miniatura local nunca substitui a imagem de trabalho')

    def test_11_json_invalido_nao_vira_sucesso_vazio(self):
        body = downloader.Worker._json(b'{invalido')
        self.assertTrue(body.get('error'))


addon.register()
try:
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Grade))
    assert result.wasSuccessful(), 'REGRESSAO_GRADE_FALHOU'
    print('REGRESSAO_GRADE_OK: catálogo local conectado, embutido e ids')
finally:
    addon.unregister()
