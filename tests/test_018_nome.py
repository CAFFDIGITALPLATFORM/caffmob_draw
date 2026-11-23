"""Nome do material pelo catálogo (T004; RN-09, RF-08), sem `bpy`.

O material leva o nome do item no addon — "Fabricante Item" — e não o nome do arquivo. A coleção entra no nome
só quando dois fabricantes têm item homônimo, para os dois materiais continuarem distintos. Entrada sem nome cai
no basename do arquivo.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import _bootstrap  # noqa: E402,F401  (carrega o pacote sem `bpy`)
from caffmob_draw.texture_library import catalog, catalog_core as cc  # noqa: E402

ANIS_ARAUCO = {"id": "arauco/colecao-realce/anis", "name": "Anis", "file": "arauco/Colecao Realce/Anis.jpg"}
ANIS_DURATEX = {"id": "duratex/geral/anis", "name": "Anis", "file": "duratex/Geral/Anis.jpg"}
CATALOGO = {"manufacturers": [
    {"id": "arauco", "name": "Arauco",
     "collections": [{"id": "colecao-realce", "name": "Colecao Realce", "items": [ANIS_ARAUCO]}]},
    {"id": "duratex", "name": "Duratex",
     "collections": [{"id": "geral", "name": "Geral", "items": [ANIS_DURATEX]}]},
]}
SO_ARAUCO = {"manufacturers": [CATALOGO["manufacturers"][0]]}


class TestNomeDeExibicao(unittest.TestCase):
    def test_fabricante_e_item(self):
        self.assertEqual(cc.nome_de_exibicao(ANIS_ARAUCO, SO_ARAUCO), "Arauco Anis")

    def test_homonimo_em_dois_fabricantes_ganha_a_colecao(self):
        self.assertEqual(cc.nome_de_exibicao(ANIS_ARAUCO, CATALOGO), "Arauco Colecao Realce Anis")
        self.assertEqual(cc.nome_de_exibicao(ANIS_DURATEX, CATALOGO), "Duratex Geral Anis")

    def test_nome_vazio_cai_no_basename_do_arquivo(self):
        entrada = {"id": "arauco/colecao-realce/x", "name": "", "file": "arauco/Colecao Realce/Anis_claro.jpg"}
        self.assertEqual(cc.nome_de_exibicao(entrada), "Anis claro")

    def test_nome_nao_depende_do_arquivo(self):
        outro = {"id": "arauco/colecao-realce/anis", "name": "Anis", "file": "arauco/Colecao Realce/Chapa_119.jpg"}
        self.assertEqual(cc.nome_de_exibicao(ANIS_ARAUCO), cc.nome_de_exibicao(outro))

    def test_fabricante_desconhecido_fica_so_o_item(self):
        self.assertEqual(cc.nome_de_exibicao({"name": "MDF Premium"}, {}), "MDF Premium")

    def test_fabricante_pela_pasta_do_arquivo(self):
        entrada = {"id": "x/y/z", "name": "Anis", "file": "berneck/Natural/Anis.jpg"}
        self.assertEqual(cc.nome_de_exibicao(entrada), "Berneck Anis")


class TestNomeDoCatalogo(unittest.TestCase):
    def test_item_do_catalogo_local(self):
        nome = catalog.nome_de("arauco/colecao-realce/anis")
        self.assertTrue(nome.startswith("Arauco "), nome)
        self.assertTrue(nome.endswith(" Anis"), nome)

    def test_item_desconhecido(self):
        self.assertEqual(catalog.nome_de("nao/existe/nada"), "")


if __name__ == "__main__":
    unittest.main()
