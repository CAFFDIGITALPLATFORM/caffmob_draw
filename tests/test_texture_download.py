"""Testes do núcleo de download das texturas (feature 014, T011; RN-12, D-11; interfaces/servidor-texturas.md)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.texture_library import download_core as dc


def item(i, size=100):
    return {"id": f"t{i}", "url": f"/api/draw/v1/texturas/t{i}/imagem?tamanho=trabalho", "dest": f"/tmp/t{i}.jpg", "sha256": "a" * 64,
            "bytes": size}


class QueueTest(unittest.TestCase):
    def test_sem_duplicar_e_ate_quatro(self):
        queue = dc.Queue(max_parallel=4)
        self.assertTrue(queue.add(item(1)))
        self.assertFalse(queue.add(item(1)))
        for i in range(2, 7):
            queue.add(item(i))
        batch = queue.next_batch()
        self.assertEqual(batch, ["t1", "t2", "t3", "t4"])
        self.assertEqual(queue.next_batch(), [])
        queue.finish("t1", ok=True)
        self.assertEqual(queue.next_batch(), ["t5"])
        self.assertFalse(queue.add(item(1)))                 # já concluída não volta para a fila

    def test_progresso_total_e_cancelar(self):
        queue = dc.Queue()
        queue.add(item(1, 100))
        queue.add(item(2, 300))
        queue.next_batch()
        queue.progress("t1", 50)
        self.assertEqual(queue.totals(), (0, 2, 50, 400))
        queue.finish("t1", ok=True)
        self.assertEqual(queue.totals(), (1, 2, 100, 400))
        queue.cancel("t2")
        self.assertEqual(queue.state("t2"), dc.CANCELLED)
        self.assertTrue(queue.idle())
        queue.cancel_all()
        self.assertTrue(queue.idle())

    def test_falha_libera_vaga(self):
        queue = dc.Queue(max_parallel=1)
        queue.add(item(1))
        queue.add(item(2))
        self.assertEqual(queue.next_batch(), ["t1"])
        queue.finish("t1", ok=False, error="server_error")
        self.assertEqual(queue.state("t1"), dc.FAILED)
        self.assertEqual(queue.next_batch(), ["t2"])
        self.assertTrue(queue.add(item(1)))                  # falhou: pode tentar de novo


class RulesTest(unittest.TestCase):
    def test_retomada(self):
        self.assertEqual(dc.resume_offset(0, 100), 0)
        self.assertEqual(dc.resume_offset(40, 100), 40)
        self.assertEqual(dc.resume_offset(100, 100), 0)      # .part completo mas não conferido: recomeça
        self.assertEqual(dc.resume_offset(150, 100), 0)
        self.assertEqual(dc.resume_offset(40, None), 0)      # sem tamanho esperado não retoma

    def test_verificacao(self):
        self.assertTrue(dc.verify("AB" * 32, "ab" * 32))
        self.assertFalse(dc.verify("ab" * 32, "cd" * 32))
        self.assertFalse(dc.verify("ab" * 32, None))

    def test_recuo(self):
        self.assertEqual([dc.retry_delay(n, 503) for n in (1, 2, 3, 4)], [2, 4, 8, None])
        self.assertEqual([dc.retry_delay(n, None) for n in (1, 2, 3, 4)], [2, 4, 8, None])   # erro de rede
        self.assertEqual(dc.retry_delay(1, 429, retry_after="3"), 3)
        self.assertEqual(dc.retry_delay(1, 429, retry_after="999"), 60)
        self.assertEqual(dc.retry_delay(2, 429), 4)
        self.assertIsNone(dc.retry_delay(7, 429))
        for status in (400, 401, 403, 404):
            self.assertIsNone(dc.retry_delay(1, status))

    def test_protocolo(self):
        line = dc.encode({"type": "progress", "id": "t1", "received": 10, "total": 100})
        self.assertTrue(line.endswith("\n"))
        self.assertEqual(dc.parse_line(line), {"type": "progress", "id": "t1", "received": 10, "total": 100})
        for bad in ("", "lixo\n", "[1, 2]\n", '{"id": "t1"}\n'):
            self.assertIsNone(dc.parse_line(bad))

    def test_mesmo_dominio(self):
        """Authorization só vai para o mesmo servidor (redirecionamento para storage assinado não leva o token)."""
        self.assertTrue(dc.same_origin("https://exemplo.test/api/draw/v1/texturas", "https://exemplo.test/storage/y"))
        self.assertFalse(dc.same_origin("https://exemplo.test/api/draw/v1/texturas", "https://cdn.exemplo.com/y"))
        self.assertFalse(dc.same_origin("https://exemplo.test/api/draw/v1/texturas", "http://exemplo.test/y"))


if __name__ == "__main__":
    unittest.main()
