# (063 RF-02; D-02) Testes portados da 061.
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
import _bootstrap  # noqa: F401

from caffmob_draw.texture_library import auth_core  # noqa: E402
from caffmob_draw.caffmob.chapas import aplicar_textura, caixas_das_chapas, chapas_do_modulo, pecas_do_modulo, texturas_do_modulo  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
