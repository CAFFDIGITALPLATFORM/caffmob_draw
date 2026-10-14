"""
Casos-ouro do contrato caffmob v1 no Python do addon (feature 061, T093).

Os casos são uma cópia de apps/caff-mobi/shared/caffmob/casos-ouro do CAFF MOBI, que é o dono do
contrato. O SHA256SUMS de lá vem junto: se o MOBI mudar um caso e esta cópia não acompanhar, o
primeiro teste falha antes de comparar com a versão velha.

Roda sem Blender: python3 -m unittest tests.test_casos_ouro
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "blendertomob"))

from caffmob.chapas import pecas_do_modulo  # noqa: E402
from caffmob.contrato import TOLERANCIA_MM  # noqa: E402
from caffmob.derivar import derivar_ambiente  # noqa: E402
from caffmob.validacao import validar_ambiente, validar_medidas_do_modulo  # noqa: E402

PASTA = Path(__file__).resolve().parent / "casos_ouro"


def divergencias(obtido, esperado, caminho=""):
    if isinstance(esperado, bool) or esperado is None or isinstance(esperado, str):
        return [] if obtido == esperado else [f"{caminho}: obtido {obtido!r}, esperado {esperado!r}"]
    if isinstance(esperado, (int, float)):
        ok = isinstance(obtido, (int, float)) and abs(obtido - esperado) <= TOLERANCIA_MM + 1e-9
        return [] if ok else [f"{caminho}: obtido {obtido!r}, esperado {esperado}"]
    if isinstance(esperado, list):
        if not isinstance(obtido, list) or len(obtido) != len(esperado):
            return [f"{caminho}: obtidos {len(obtido) if isinstance(obtido, list) else obtido!r} itens, esperados {len(esperado)}"]
        return [d for i, item in enumerate(esperado) for d in divergencias(obtido[i], item, f"{caminho}[{i}]")]
    if not isinstance(obtido, dict):
        return [f"{caminho}: obtido {obtido!r}, esperado um objeto"]
    return [d for chave, valor in esperado.items() for d in divergencias(obtido.get(chave), valor, f"{caminho}.{chave}" if caminho else chave)]


def calcular(caso):
    if caso["tipo"] == "modulo":
        return {"erros": validar_medidas_do_modulo(caso["entrada"]), "pecas": pecas_do_modulo(caso["entrada"])}
    erros = validar_ambiente(caso["entrada"])
    if "erros" in caso["esperado"]:
        return {"erros": erros}
    return {"erros": erros, **derivar_ambiente(caso["entrada"], list(caso["esperado"]))}


def arquivos():
    return sorted(caminho for caminho in PASTA.rglob("*.json"))


class SomaDosCasos(unittest.TestCase):
    def test_copia_igual_ao_mobi(self):
        linhas = []
        for caminho in arquivos():
            soma = hashlib.sha256(caminho.read_bytes()).hexdigest()
            linhas.append(f"{soma}  {caminho.relative_to(PASTA).as_posix()}")
        self.assertEqual("\n".join(linhas) + "\n", (PASTA / "SHA256SUMS").read_text(encoding="utf-8"),
                         "a cópia dos casos-ouro está diferente da do MOBI: copie de novo de apps/caff-mobi/shared/caffmob/casos-ouro")


class CasosOuro(unittest.TestCase):
    def test_existem_casos_das_duas_origens(self):
        origens = {json.loads(caminho.read_text(encoding="utf-8"))["origem"] for caminho in arquivos()}
        self.assertEqual(origens, {"addon", "manual"})
        self.assertGreaterEqual(len(arquivos()), 50)

    def test_manuais_revisados(self):
        for caminho in arquivos():
            caso = json.loads(caminho.read_text(encoding="utf-8"))
            if caso["origem"] == "manual":
                self.assertIsNotNone(caso["revisadoPor"], caminho.name)

    def test_todos_os_casos(self):
        for caminho in arquivos():
            caso = json.loads(caminho.read_text(encoding="utf-8"))
            with self.subTest(caso=caso["caso"]):
                obtido = calcular(caso)
                if "erros" not in caso["esperado"]:
                    self.assertEqual(obtido["erros"], [], "um caso sem erros esperados precisa ser válido")
                self.assertEqual(divergencias(obtido, caso["esperado"]), [])

    def test_controle_positivo(self):
        caso = json.loads((PASTA / "paredes" / "parede-ambiente-l.json").read_text(encoding="utf-8"))
        alterado = json.loads(json.dumps(caso["esperado"]))
        alterado["piso"][0]["area_mm2"] += 1
        self.assertEqual(len(divergencias(calcular(caso), alterado)), 1)


if __name__ == "__main__":
    unittest.main()
