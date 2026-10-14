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
sys.path.insert(0, str(RAIZ / "blendertomob"))

from caffmob import conexao  # noqa: E402
from caffmob.contrato import de_metros, para_metros, sem_envelope_do_servidor, serializar  # noqa: E402

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


@unittest.skipUnless(URL, "defina CAFFMOB_ENSAIO_URL para rodar contra o MOBI de ensaio")
class ContraOMobiDeEnsaio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.TemporaryDirectory()
        cls.sessao = conexao.Sessao(os.path.join(cls.pasta.name, "sessao.json"), URL)
        codigo = conexao.pedir_codigo(URL, "Blender de ensaio")
        cls.sessao.guardar(conexao.esperar_token(URL, codigo))

    @classmethod
    def tearDownClass(cls):
        cls.pasta.cleanup()

    def test_fluxo_de_codigo_deu_tokens_de_aparelho(self):
        self.assertTrue(self.sessao.tokens["access_token"].startswith("mobd_"))
        self.assertEqual(self.sessao.titular, "Marcenaria de Ensaio")
        with open(self.sessao.arquivo, encoding="utf-8") as arquivo:
            self.assertNotIn("senha", arquivo.read().lower())

    def test_cada_caso_ouro_vai_e_volta_pelo_mobi(self):
        for caso in AMBIENTES:
            with self.subTest(caso=caso["caso"]):
                original = caso["entrada"]
                criado = self.sessao.criar_ambiente(original)
                baixado = self.sessao.baixar_ambiente(criado["id"])
                self.assertEqual(comparavel(baixado), comparavel(original))
                self.assertNotIn("customerId", json.dumps(baixado))
                pelo_blender = {**de_metros(para_metros(baixado)), "origem": "blender"}
                status, corpo = self.sessao.enviar_ambiente(pelo_blender, baixado["version"])
                self.assertEqual((status, corpo["version"]), (200, baixado["version"] + 1))
                self.assertEqual(comparavel(self.sessao.baixar_ambiente(criado["id"])), comparavel(original))
                status, corpo = self.sessao.enviar_ambiente(pelo_blender, baixado["version"])
                self.assertEqual(status, 409)
                self.assertEqual(corpo["versao_atual"], baixado["version"] + 1)

    def test_lista_mostra_os_ambientes_sem_cliente(self):
        itens = self.sessao.listar_ambientes()
        self.assertTrue(all(set(item) == {"id", "nome", "version", "atualizado_em", "origem", "vinculado_a_cliente"} for item in itens))

    def test_renovacao_gira_o_token(self):
        antes = dict(self.sessao.tokens)
        self.sessao._renovar()
        self.assertNotEqual(self.sessao.tokens["refresh_token"], antes["refresh_token"])
        self.assertEqual(self.sessao.chamar("GET", "/ambientes?depois=0")[0], 200)


if __name__ == "__main__":
    unittest.main()
