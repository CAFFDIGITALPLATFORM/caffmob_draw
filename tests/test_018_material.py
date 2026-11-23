"""Chave de material e migração do nome antigo (T006; D-03, D-12), sem `bpy`.

Dois materiais só são o mesmo com `path` + `size_mm` + `projection` iguais (e a mesma variante de veio girado). O
material antigo "Textura: <arquivo> <tamanho> mm" é renomeado para o nome do catálogo quando esse nome está livre;
com o nome ocupado, o antigo fica e o conflito é sinalizado.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import _bootstrap  # noqa: E402,F401  (carrega o pacote sem `bpy`)
from caffmob_draw.texture_library import catalog_core as cc, uv_core  # noqa: E402

PATH = "C:/texturas/arauco/anis.jpg"
ANTIGO = "Textura: anis.jpg 600 mm"


class TestChaveDeMaterial(unittest.TestCase):
    def test_mesmo_arquivo_tamanho_e_projecao(self):
        self.assertEqual(uv_core.chave_de_material(PATH, 600, uv_core.UV),
                         uv_core.chave_de_material(PATH, 600, uv_core.UV))

    def test_projecao_diferente_nao_reaproveita(self):
        self.assertNotEqual(uv_core.chave_de_material(PATH, 600, uv_core.UV),
                            uv_core.chave_de_material(PATH, 600, uv_core.BOX))

    def test_tamanho_diferente_nao_reaproveita(self):
        self.assertNotEqual(uv_core.chave_de_material(PATH, 600, uv_core.UV),
                            uv_core.chave_de_material(PATH, 300, uv_core.UV))

    def test_arquivo_diferente_nao_reaproveita(self):
        self.assertNotEqual(uv_core.chave_de_material(PATH, 600, uv_core.UV),
                            uv_core.chave_de_material("C:/texturas/outro.jpg", 600, uv_core.UV))

    def test_variante_girada_e_outra_chave(self):
        self.assertNotEqual(uv_core.chave_de_material(PATH, 600, uv_core.UV),
                            uv_core.chave_de_material(PATH, 600, uv_core.UV, rotated=True))

    def test_sem_projecao_conta_como_caixa(self):
        self.assertEqual(uv_core.chave_de_material(PATH, 600), uv_core.chave_de_material(PATH, 600, uv_core.BOX))


class TestNomeAntigo(unittest.TestCase):
    def test_reconhece_o_formato_antigo(self):
        self.assertTrue(cc.eh_nome_antigo(ANTIGO))
        self.assertTrue(cc.eh_nome_antigo("Textura: chapa.png 1830 × 2750 mm"))

    def test_nome_do_catalogo_nao_e_antigo(self):
        self.assertFalse(cc.eh_nome_antigo("Arauco Anis"))
        self.assertFalse(cc.eh_nome_antigo(""))


class TestMigracaoDeNome(unittest.TestCase):
    def test_nome_novo_livre_renomeia(self):
        self.assertEqual(cc.nome_migrado(ANTIGO, "Arauco Anis"), ("Arauco Anis", False))

    def test_nome_novo_ocupado_mantem_e_sinaliza_conflito(self):
        self.assertEqual(cc.nome_migrado(ANTIGO, "Arauco Anis", ["Arauco Anis"]), (ANTIGO, True))

    def test_ja_com_o_nome_novo_nao_muda(self):
        self.assertEqual(cc.nome_migrado("Arauco Anis", "Arauco Anis"), ("Arauco Anis", False))

    def test_sem_nome_novo_mantem(self):
        self.assertEqual(cc.nome_migrado(ANTIGO, ""), (ANTIGO, False))

    def test_conflito_nao_sobrescreve_o_outro_material(self):
        ocupados = {"Arauco Anis"}
        final, conflito = cc.nome_migrado(ANTIGO, "Arauco Anis", ocupados)
        self.assertTrue(conflito)
        self.assertEqual(final, ANTIGO)
        self.assertEqual(ocupados, {"Arauco Anis"})


if __name__ == "__main__":
    unittest.main()
