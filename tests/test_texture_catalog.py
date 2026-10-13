"""Testes do catálogo de texturas dos fabricantes (feature 014, T009; RN-01 a RN-04, data-delta §1)."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.texture_library import catalog_core as cc

FILES = [
    "duratex/Design/Carvalho_Avela_Design.jpg",
    "duratex/Design/Carvalho_Avela_Design.jpg.bump",
    "duratex/Design/Thumbs.db",
    "duratex/Design/legenda.txt",
    "duratex/Solta.JPG",
    "Placas_do_Brasil/Linha Unicolor/Branco_TX.PNG",
    "arauco/Tons_do_Brasil/Matt/Jalapao.jpg",
    "formica/Bumps/B5.png",
    "formica/Bumps/_Formica Legenda.txt",
    "formica/Facility/F696_SO.jpg",
    "formica/Facility/F696_SO.jpg.bump",
    "formica/Facility/F696_SO.resources",
    "Brastemp/Fogao/Inox.jpg",
    "duratex/.oculto/x.jpg",
    "duratex/Design/carvalho avela design.jpeg",
]
SIZES = {
    "duratex/Design/Carvalho_Avela_Design.jpg": (466, 700),
    "duratex/Solta.JPG": (500, 500),
    "Placas_do_Brasil/Linha Unicolor/Branco_TX.PNG": (800, 400),
    "arauco/Tons_do_Brasil/Matt/Jalapao.jpg": (1850, 2750),
    "formica/Facility/F696_SO.jpg": (1000, 1000),
    "Brastemp/Fogao/Inox.jpg": (300, 300),
    "duratex/Design/carvalho avela design.jpeg": (600, 600),
}


def items_by_id(catalog):
    return {i["id"]: i for m in catalog["manufacturers"] for c in m["collections"] for i in c["items"]}


class CatalogCoreTest(unittest.TestCase):
    def setUp(self):
        self.catalog, self.warnings = cc.build_catalog(FILES, SIZES)
        self.items = items_by_id(self.catalog)

    def test_so_fabricantes_aceitos(self):
        """RN-01: só os 12 fabricantes de chapas, comparando o nome da pasta sem caixa."""
        self.assertEqual(len(cc.MANUFACTURERS), 12)
        names = [m["name"] for m in self.catalog["manufacturers"]]
        self.assertEqual(names, ["Arauco", "Duratex", "Formica", "Placas do Brasil"])
        self.assertFalse(any(i.startswith("brastemp/") for i in self.items))

    def test_ignorados(self):
        """RN-03: relevos, auxiliares, pasta Bumps e ocultos não viram textura."""
        files = {i["file"] for i in self.items.values()}
        self.assertFalse(any(f.endswith((".bump", ".txt", ".resources", ".db")) for f in files))
        self.assertFalse(any("/Bumps/" in f or "/.oculto/" in f for f in files))
        self.assertEqual(len(self.items), 6)

    def test_colecao_e_nome(self):
        """RN-02: coleção pela subpasta, "Geral" para imagem solta, nome legível, subcoleção no nome."""
        item = self.items["duratex/design/carvalho-avela-design"]
        self.assertEqual(item["name"], "Carvalho Avela Design")
        self.assertEqual(item["file"], "duratex/Design/Carvalho_Avela_Design.jpg")
        self.assertEqual(self.items["duratex/geral/solta"]["name"], "Solta")
        self.assertEqual(self.items["arauco/tons-do-brasil/matt-jalapao"]["name"], "Jalapao (Matt)")
        collections = {c["name"] for m in self.catalog["manufacturers"] for c in m["collections"]}
        self.assertIn("Tons do Brasil", collections)
        self.assertIn("Geral", collections)

    def test_id_estavel_com_colisao(self):
        """Mesmo slug na mesma coleção ganha sufixo -2, com aviso; a ordem é estável."""
        self.assertIn("duratex/design/carvalho-avela-design-2", self.items)
        self.assertTrue(any("carvalho-avela-design" in w for w in self.warnings))
        again, _ = cc.build_catalog(list(reversed(FILES)), SIZES)
        self.assertEqual(json.dumps(again, sort_keys=True), json.dumps(self.catalog, sort_keys=True))

    def test_tamanho_real(self):
        """RN-04: chapa inteira vale 1 px = 1 mm; o resto usa 600 mm no maior lado."""
        self.assertEqual(self.items["arauco/tons-do-brasil/matt-jalapao"]["size-mm"], [1850.0, 2750.0])
        self.assertEqual(self.items["duratex/design/carvalho-avela-design"]["size-mm"], [399.4, 600.0])
        self.assertEqual(self.items["placas-do-brasil/linha-unicolor/branco-tx"]["size-mm"], [600.0, 300.0])
        self.assertEqual(cc.size_mm((1820, 2750)), [397.1, 600.0])     # 1.820 px fica fora da faixa de RN-04

    def test_relevo(self):
        self.assertEqual(self.items["formica/facility/f696-so"]["bump"], "formica/Facility/F696_SO.jpg.bump")
        self.assertIsNone(self.items["duratex/geral/solta"]["bump"])

    def test_imagem_ilegivel(self):
        """Imagem sem dimensões (ilegível) vira aviso e fica fora."""
        catalog, warnings = cc.build_catalog(["duratex/Design/Quebrada.jpg"], {})
        self.assertEqual(items_by_id(catalog), {})
        self.assertTrue(any("Quebrada.jpg" in w for w in warnings))

    def test_hash_e_bytes(self):
        meta = {"duratex/Solta.JPG": ("ab" * 32, 1234)}
        catalog, _ = cc.build_catalog(FILES, SIZES, meta=meta)
        item = items_by_id(catalog)["duratex/geral/solta"]
        self.assertEqual((item["sha256"], item["bytes"]), ("ab" * 32, 1234))
        self.assertEqual(item["thumb"], "thumbs/duratex/geral/solta.png")

    def test_ler_catalogo(self):
        text = json.dumps(self.catalog)
        parsed, warnings = cc.parse_catalog(text)
        self.assertEqual(parsed, self.catalog)
        self.assertEqual(warnings, [])
        for bad in ("{", json.dumps({"schema-version": 2}), json.dumps({"schema-version": 1, "manufacturers": 5})):
            parsed, warnings = cc.parse_catalog(bad)
            self.assertEqual(parsed["manufacturers"], [])
            self.assertEqual(warnings, [cc.INVALID])

    def test_busca(self):
        """Busca sem caixa e sem acento, com filtro de fabricante e coleção (D-17)."""
        found = [i["id"] for i in cc.search(self.catalog, "CARVALHO avelã")]
        self.assertEqual(found, ["duratex/design/carvalho-avela-design", "duratex/design/carvalho-avela-design-2"])
        self.assertEqual([i["id"] for i in cc.search(self.catalog, "", manufacturer="formica")],
                         ["formica/facility/f696-so"])
        self.assertEqual(len(cc.search(self.catalog, "", manufacturer="duratex", collection="geral")), 1)


if __name__ == "__main__":
    unittest.main()
