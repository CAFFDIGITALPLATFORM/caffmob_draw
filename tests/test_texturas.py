"""
Texturas de fábrica no addon, sem Blender (feature 062, T032): posição das chapas, acabamento por grupo e o
cache das texturas baixadas. O material no Blender e a ida e volta pela rede ficam em tests/blender_caffmob.py.

Run: python3 -m unittest tests.test_texturas
"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "blendertomob"))

from caffmob import conexao  # noqa: E402
from caffmob.chapas import aplicar_textura, caixas_das_chapas, chapas_do_modulo, pecas_do_modulo, texturas_do_modulo  # noqa: E402

CASO = json.loads((RAIZ / "tests" / "casos_ouro" / "pecas-addon" / "pecas-addon-base-double.json").read_text(encoding="utf-8"))["entrada"]
T = "1b9e2f0a-6c1d-5b8e-9a4f-3c2d1e0f9a8b"


class Acabamento(unittest.TestCase):
    def test_uma_caixa_por_chapa_com_as_medidas_de_corte(self):
        chapas = chapas_do_modulo(CASO)
        caixas = caixas_das_chapas(CASO)
        self.assertEqual(len(caixas), sum(c["quantidade"] for c in chapas))
        for caixa in caixas:
            chapa = next(c for c in chapas if c["papel"] == caixa["papel"] and c["indice"] == caixa["indice"])
            self.assertEqual(sorted([caixa["dx"], caixa["dy"], caixa["dz"]]), sorted([chapa["largura"], chapa["altura"], chapa["espessura"]]))
            self.assertGreaterEqual(caixa["x"], -1e-9)
            self.assertLessEqual(caixa["x"] + caixa["dx"], CASO["largura"] + 1e-9)

    def test_frentes_texturiza_so_as_portas_e_tirar_limpa(self):
        com = aplicar_textura(CASO, "FRENTES", T)
        self.assertEqual(com["chapas_editadas"], [{"papel": "PORTA", "indice": 0, "textura_id": T}])
        self.assertEqual(texturas_do_modulo(com), [T])
        porta = next(p for p in pecas_do_modulo(com, None, {T: {"fabricante": "Berneck", "nome": "Carvalho Japandi - Micro"}}.get) if p["id"].endswith("_PORTA_PAR"))
        self.assertEqual(porta["material"], "MDF 18 mm · Berneck Carvalho Japandi - Micro")
        self.assertEqual(aplicar_textura(com, "FRENTES", None)["chapas_editadas"], [])
        caixa = {c["papel"] for c in chapas_do_modulo(aplicar_textura(CASO, "CAIXA", T)) if c.get("textura_id")}
        self.assertNotIn("PORTA", caixa)
        self.assertNotIn("FUNDO", caixa)


class SessaoFalsa(conexao.Sessao):
    def __init__(self, respostas):
        self.respostas, self.pedidos = respostas, []

    def chamar_bytes(self, caminho, cabecalhos=None):
        self.pedidos.append((caminho, cabecalhos))
        return self.respostas.pop(0)


class CacheDasTexturas(unittest.TestCase):
    def test_baixa_uma_vez_confere_o_hash_e_recusa_conteudo_trocado(self):
        dados = b"\xff\xd8\xff imagem de trabalho"
        textura = {"id": T, "sha256_trabalho": hashlib.sha256(dados).hexdigest(), "sha256_miniatura": "0" * 64}
        with tempfile.TemporaryDirectory() as pasta:
            sessao = SessaoFalsa([(200, dados, {"Content-Type": "image/jpeg"})])
            caminho = sessao.baixar_textura(textura, pasta)
            self.assertTrue(caminho.endswith(f"{textura['sha256_trabalho']}.jpg"))
            self.assertEqual(Path(caminho).read_bytes(), dados)
            self.assertEqual(sessao.baixar_textura(textura, pasta), caminho)
            self.assertEqual(len(sessao.pedidos), 1, "a segunda vez sai do cache, sem pedir")
            trocado = SessaoFalsa([(200, b"outra coisa", {"Content-Type": "image/jpeg"})])
            with self.assertRaises(conexao.ErroDoMobi):
                trocado.baixar_textura(dict(textura, sha256_trabalho="1" * 64), pasta)

    def test_mapa_revalida_pelo_etag(self):
        with tempfile.TemporaryDirectory() as pasta:
            sessao = SessaoFalsa([(200, b"bump", {"ETag": '"abc"'}), (304, b"", {"ETag": '"abc"'})])
            primeiro = sessao.baixar_mapa(T, "bump", pasta)
            self.assertEqual(sessao.baixar_mapa(T, "bump", pasta), primeiro)
            self.assertEqual(sessao.pedidos[1][1], {"If-None-Match": '"abc"'})


if __name__ == "__main__":
    unittest.main()
