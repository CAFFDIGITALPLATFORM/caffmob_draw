"""Testes do núcleo da sessão MOBI (feature 063, T012; RN-11, D-12, D-13; interfaces/servidor-texturas.md §1)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.texture_library import auth_core as ac

START = {"device_code": "dev", "user_code": "WDJB-MJHT", "verification_uri": "https://x/ativar",
         "verification_uri_complete": "https://x/ativar?code=WDJB-MJHT", "expires_in": 600, "interval": 5}
TOKENS = {"access_token": "acc", "expires_in": 900, "refresh_token": "ref",
          "titular": {"id": 1, "nome": "Oficina de teste"}}


class DeviceFlowTest(unittest.TestCase):
    def setUp(self):
        self.flow = ac.DeviceFlow()
        self.flow.start(START, now=1000.0)

    def test_inicio(self):
        self.assertEqual(self.flow.user_code, "WDJB-MJHT")
        self.assertEqual(self.flow.open_url, "https://x/ativar?code=WDJB-MJHT")
        self.assertEqual(self.flow.state, ac.WAITING)
        self.assertFalse(self.flow.due(1004.0))
        self.assertTrue(self.flow.due(1005.0))

    def test_pendente_e_slow_down(self):
        self.assertEqual(self.flow.handle(400, {"error": "authorization_pending"}, now=1005.0), ac.WAITING)
        self.assertFalse(self.flow.due(1009.0))
        self.assertEqual(self.flow.handle(400, {"error": "slow_down"}, now=1010.0), ac.WAITING)
        self.assertEqual(self.flow.interval, 10)
        self.assertFalse(self.flow.due(1019.0))
        self.assertTrue(self.flow.due(1020.0))

    def test_sucesso(self):
        self.assertEqual(self.flow.handle(200, TOKENS, now=1005.0), ac.DONE)
        self.assertEqual(self.flow.tokens["refresh_token"], "ref")

    def test_negado_expirado_e_erro(self):
        flow = ac.DeviceFlow()
        flow.start(START, now=0.0)
        self.assertEqual(flow.handle(400, {"error": "access_denied"}, now=5.0), ac.DENIED)
        flow.start(START, now=0.0)
        self.assertEqual(flow.handle(400, {"error": "expired_token"}, now=5.0), ac.EXPIRED)
        flow.start(START, now=0.0)
        self.assertFalse(flow.due(601.0))
        self.assertEqual(flow.state, ac.EXPIRED)
        flow.start(START, now=0.0)
        self.assertEqual(flow.handle(500, {}, now=5.0), ac.WAITING)       # servidor instável: tenta de novo
        self.assertEqual(flow.handle(400, {"error": "invalid_request"}, now=10.0), ac.ERROR)


class SessionTest(unittest.TestCase):
    def test_sessao_unica_com_tokens_e_titular(self):
        data = ac.session_payload(TOKENS, server="https://x", saved_at="2026-10-12T10:00:00-03:00")
        self.assertEqual(data["refresh_token"], "ref")
        self.assertEqual(data["tokens"], TOKENS)
        self.assertNotIn("password", str(data).lower())
        self.assertEqual(data["titular"], TOKENS["titular"])
        self.assertEqual(ac.load_session(data, server="https://x"), data)

    def test_sessao_invalida_ou_de_outro_servidor(self):
        data = ac.session_payload(TOKENS, server="https://x", saved_at="")
        self.assertIsNone(ac.load_session(data, server="https://outro"))
        self.assertIsNone(ac.load_session(dict(data, **{"schema-version": 2}), server="https://x"))
        self.assertIsNone(ac.load_session({"schema-version": 1}, server="https://x"))
        self.assertIsNone(ac.load_session("lixo", server="https://x"))

    def test_renovacao(self):
        self.assertEqual(ac.refresh_outcome(200, dict(TOKENS, refresh_token="novo")),
                         (ac.OK, dict(TOKENS, refresh_token="novo")))
        self.assertEqual(ac.refresh_outcome(401, {"error": "invalid_token"}), (ac.RETRY, None))
        self.assertEqual(ac.refresh_outcome(400, {"error": "invalid_grant"}), (ac.LOGOUT, None))
        self.assertEqual(ac.refresh_outcome(429, {}), (ac.RETRY, None))
        self.assertEqual(ac.refresh_outcome(503, {}), (ac.RETRY, None))
        self.assertEqual(ac.refresh_outcome(None, None), (ac.RETRY, None))   # sem rede
        self.assertEqual(ac.refresh_outcome(200, {"access_token": "x"}), (ac.RETRY, None))  # resposta incompleta preserva a sessão

    def test_validade_do_token_de_acesso(self):
        self.assertTrue(ac.access_valid(expires_at=1000.0, now=900.0))
        self.assertFalse(ac.access_valid(expires_at=1000.0, now=980.0))   # renova 30 s antes
        self.assertFalse(ac.access_valid(expires_at=None, now=0.0))


if __name__ == "__main__":
    unittest.main()
