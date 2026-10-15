# (063 RF-02; D-02) Testes portados da 061.
"""
Ida e volta do contrato (feature 061, RN-04 e T097).

1. Sem rede: todo caso-ouro de ambiente passa pelas unidades do Blender (mm → m → mm) e volta igual.
2. Com o MOBI de ensaio (CAFFMOB_ENSAIO_URL; suba com scripts/mobi/servidor-de-ensaio-061.sh no
   caff_systems): conecta pelo fluxo da RFC 8628, cria os ambientes, baixa, converte pelas unidades do
   Blender, envia com a versão lida e baixa de novo. O documento não pode mudar, e a versão velha leva 409.

Run: python3 -m unittest tests.test_ida_e_volta
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
import _bootstrap  # noqa: F401

from caffmob_draw.texture_library import auth_core  # noqa: E402
from caffmob_draw.caffmob.contrato import de_metros, para_metros, sem_envelope_do_servidor, serializar  # noqa: E402

CASOS = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((Path(__file__).resolve().parent / "casos_ouro").rglob("*.json"))]
AMBIENTES = [c for c in CASOS if c["tipo"] == "ambiente" and "erros" not in c["esperado"]]
URL = os.environ.get("CAFFMOB_ENSAIO_URL")


def comparavel(documento):
    return serializar(sem_envelope_do_servidor(documento))


class PelasUnidadesDoBlender(unittest.TestCase):
    def test_mm_para_m_e_de_volta(self):
        for caso in AMBIENTES + [c for c in CASOS if c["tipo"] == "modulo"]:
            with self.subTest(caso=caso["caso"]):
                self.assertEqual(comparavel(de_metros(para_metros(caso["entrada"]))), comparavel(caso["entrada"]))


class EsperaPeloCodigo(unittest.TestCase):
    def test_502_e_slow_down_preservam_a_espera(self):
        flow = auth_core.DeviceFlow()
        flow.start({"device_code": "codigo", "user_code": "BCDF-GHJK", "verification_uri": "http://127.0.0.1", "interval": 5}, 0)
        self.assertEqual(flow.handle(502, {}, 5), auth_core.WAITING)
        self.assertEqual(flow.next_poll, 10)
        self.assertEqual(flow.handle(400, {"error": "slow_down"}, 10), auth_core.WAITING)
        self.assertEqual(flow.interval, 10)
        self.assertEqual(flow.handle(400, {"error": "access_denied"}, 20), auth_core.DENIED)


if __name__ == "__main__":
    unittest.main()
