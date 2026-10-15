"""Referência do modelo no módulo do ambiente, com a mesma regra do MOBI (063 T059; RF-06).

O ensaio contra o MOBI achou o envio recusado com 422 (`modulos[1].modelo`, ESQUEMA): o addon gravava a referência sem
o escopo, e a validação local não olhava o campo.
"""
import copy
import json
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401

from caffmob_draw.caffmob.validacao import validar_ambiente  # noqa: E402

CASO = Path(__file__).resolve().parent / "casos_ouro" / "carga" / "carga-200-segmentos-30-modulos.json"


def ambiente_com(modelo):
    caso = json.loads(CASO.read_text(encoding="utf-8"))
    ambiente = copy.deepcopy(caso["entrada"])
    ambiente["modulos"][1]["modelo"] = modelo
    return ambiente


def erros_do_modelo(modelo):
    return [e for e in validar_ambiente(ambiente_com(modelo)) if e["caminho"] == "modulos[1].modelo"]


class ReferenciaDoModeloTest(unittest.TestCase):
    ID = "4a1d2b9e-5c3f-4e8a-9b7d-1f2e3d4c5b6a"

    def test_com_escopo_passa(self):
        for escopo in ("titular", "pessoal"):
            self.assertEqual(erros_do_modelo({"id": self.ID, "version": 3, "escopo": escopo}), [])

    def test_sem_escopo_e_recusada(self):
        self.assertEqual(erros_do_modelo({"id": self.ID, "version": 3}), [{"caminho": "modulos[1].modelo", "codigo": "ESQUEMA"}])

    def test_escopo_desconhecido_versao_zero_e_chave_a_mais_sao_recusados(self):
        for modelo in ({"id": self.ID, "version": 3, "escopo": "outro"}, {"id": self.ID, "version": 0, "escopo": "titular"},
                       {"id": self.ID, "version": 3, "escopo": "titular", "nome": "x"}):
            self.assertEqual(len(erros_do_modelo(modelo)), 1, modelo)

    def test_modulo_sem_modelo_continua_valido(self):
        caso = json.loads(CASO.read_text(encoding="utf-8"))
        self.assertFalse([e for e in validar_ambiente(caso["entrada"]) if e["caminho"].endswith(".modelo")])


if __name__ == "__main__":
    unittest.main()
