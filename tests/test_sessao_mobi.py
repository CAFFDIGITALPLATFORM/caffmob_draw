# (063 RN-04, RN-05, RN-06; D-05) Sessão sem Blender nem rede.
import json
import os
import tempfile
import unittest
import _bootstrap
from caffmob_draw.caffmob import sessao
from caffmob_draw.texture_library import auth_core

TOKENS = {'access_token': 'mobd_teste', 'refresh_token': 'mobr_teste', 'titular': {'nome': 'Oficina'}, 'pessoa': {'nome': 'Ana'}}


class Sessao(unittest.TestCase):
    def test_permissao_e_endereco(self):
        with tempfile.TemporaryDirectory() as directory:
            path = directory + '/sessao.json'
            data = sessao.payload(TOKENS, 'http://127.0.0.1:1234')
            sessao.save(path, data)
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)
            self.assertEqual(sessao.read(path, data['server'])['tokens'], TOKENS)
            self.assertIsNone(sessao.read(path, 'http://127.0.0.1:5678'))
            self.assertEqual(sessao.read(path, data['server'])['pessoa'], {'nome': 'Ana'})
            self.assertNotIn('senha', json.dumps(data))
            os.chmod(path, 0o644)
            sessao.save(path, data)
            self.assertEqual(os.stat(path).st_mode & 0o777, 0o600)

    def test_so_invalid_grant_desconecta(self):
        for status, body in [(500, {}), (502, {}), (429, {}), (None, {}), (401, {}), (400, {'error': 'invalid_request'}), (200, {})]:
            self.assertEqual(auth_core.refresh_outcome(status, body), ('RETRY', None))
        self.assertEqual(auth_core.refresh_outcome(400, {'error': 'invalid_grant'}), ('LOGOUT', None))
        self.assertEqual(auth_core.refresh_outcome(200, TOKENS), ('OK', TOKENS))

    def test_revogacao_e_sem_rede(self):
        data = sessao.payload(TOKENS, 'http://127.0.0.1')
        self.assertEqual(sessao.revogacao(data), {'client_id': 'caffmob-draw', 'token': TOKENS['refresh_token']})
        with tempfile.TemporaryDirectory() as directory:
            path = directory + '/sessao.json'
            sessao.save(path, data)
            self.assertIn('Aparelhos conectados', sessao.disconnect(path, None))
            self.assertFalse(os.path.exists(path))
            self.assertEqual(sessao.disconnect(path, 200), '')

    def test_sessao_antiga_sem_pessoa_carrega_e_renovacao_preenche(self):
        antiga = sessao.payload({k: v for k, v in TOKENS.items() if k != 'pessoa'}, 'http://127.0.0.1')
        antiga.pop('pessoa')
        self.assertIsNotNone(sessao.load(antiga, antiga['server']))
        outcome, tokens = sessao.refresh_outcome(200, TOKENS)
        self.assertEqual(outcome, 'OK')
        self.assertEqual(sessao.payload(tokens, antiga['server'])['pessoa'], {'nome': 'Ana'})
