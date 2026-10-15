# (063 RF-10; RN-07) Mensagens e bloqueio de contrato incompatível.
import _bootstrap
import unittest
from caffmob_draw.mobi import respostas


class Respostas(unittest.TestCase):
    def test_http_e_motivo(self):
        for status in (401, 409, 413, 429, 502):
            text = respostas.message(status)
            self.assertIn('HTTP ' + str(status), text)
            self.assertGreater(len(text), 20)
        self.assertIn('novamente', respostas.message(400, {'error': 'invalid_grant'}))
        self.assertIn('Sem rede', respostas.message(None))
        self.assertIn('desligado', respostas.message(None, {'message': 'Internet do Blender desligado'}))

    def test_contrato(self):
        self.assertTrue(respostas.compatible({'X-Caffmob-Contrato': 'ambiente/v1, modulo/v1'}))
        self.assertFalse(respostas.compatible({'x-caffmob-contrato': 'ambiente/v2, modulo/v1'}))
        self.assertIn('Atualize', respostas.message(200, headers={'X-Caffmob-Contrato': 'v2'}))
