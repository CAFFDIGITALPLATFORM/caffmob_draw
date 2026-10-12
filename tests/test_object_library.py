"""Testes da biblioteca de objetos (feature 009, T008): `object_library/catalog.py` e `store.py`.

Contrato: `_reversa_forward/009-mira-calculo-skp-biblioteca/interfaces/object-library-item.md`.
"""

import json
import tempfile
import unittest
from pathlib import Path

import _bootstrap  # noqa: F401
from caffmob_draw.object_library import catalog, store


def manifest(**over):
    data = {"format": catalog.FORMAT, "version": 1, "item_id": "porta-lisa-80-a1b2c3", "name": "Porta lisa 80",
            "category": "DOORS", "root": "Porta lisa 80", "source": "CAFFMob Draw", "author": "",
            "license": "GPL-3.0-or-later", "size_mm": [800.0, 35.0, 2100.0], "features": ["LEAF_SWING"],
            "materials": [], "created_at": "2026-10-09T10:00:00-03:00", "addon_version": "1.0.1"}
    data.update(over)
    return data


def write_item(folder, data, png=True):
    cat = Path(folder) / data["category"]
    cat.mkdir(parents=True, exist_ok=True)
    (cat / (data["item_id"] + ".json")).write_text(json.dumps(data), encoding="utf-8")
    (cat / (data["item_id"] + ".blend")).write_bytes(b"BLENDER")
    if png:
        (cat / (data["item_id"] + ".png")).write_bytes(b"\x89PNG")


class CatalogTest(unittest.TestCase):
    def test_categorias(self):
        self.assertEqual([c[0] for c in catalog.CATEGORIES],
                         ['DOORS', 'WINDOWS', 'COOKTOPS', 'TABLES', 'SEATING', 'DECOR', 'OTHER'])
        self.assertEqual(len(catalog.CATEGORY_ITEMS), 7)

    def test_slug_e_id(self):
        self.assertEqual(catalog.slug("Porta Lisa 80 (Branca)"), "porta-lisa-80-branca")
        self.assertEqual(catalog.slug("Cooktop 4 bocas ç"), "cooktop-4-bocas-c")
        self.assertEqual(catalog.new_item_id("Mesa 120", token="abc123"), "mesa-120-abc123")

    def test_manifesto_valido(self):
        entry = catalog.read_manifest(manifest())
        self.assertEqual((entry.name, entry.category, entry.features), ("Porta lisa 80", 'DOORS', ['LEAF_SWING']))
        self.assertEqual(catalog.to_manifest(entry), manifest())

    def test_manifesto_invalido(self):
        for bad in (manifest(format="x"), manifest(version=2), manifest(item_id="Com Espaço"), manifest(root=""),
                    {"format": catalog.FORMAT}):
            with self.subTest(bad=bad), self.assertRaises(catalog.ManifestError):
                catalog.read_manifest(bad)

    def test_id_com_quebra_de_linha(self):
        """BUG-20261011-EVT6: "\n" final no item_id é recusado."""
        with self.assertRaises(catalog.ManifestError):
            catalog.read_manifest(manifest(item_id="porta-lisa-80\n"))

    def test_categoria_desconhecida_vira_outros(self):
        self.assertEqual(catalog.read_manifest(manifest(category="XYZ")).category, 'OTHER')

    def test_busca(self):
        entries = [catalog.read_manifest(manifest(name=n, item_id=catalog.slug(n))) for n in ("Porta lisa", "Mesa")]
        self.assertEqual([e.name for e in catalog.search(entries, "LIS")], ["Porta lisa"])
        self.assertEqual(len(catalog.search(entries, "")), 2)


class StoreTest(unittest.TestCase):
    def test_listagem_das_duas_pastas(self):
        with tempfile.TemporaryDirectory() as bundled, tempfile.TemporaryDirectory() as user:
            write_item(bundled, manifest())
            write_item(user, manifest(item_id="mesa-1", name="Mesa", category="TABLES", root="Mesa",
                                      source="3D Warehouse: Fulano"), png=False)
            (Path(user) / "TABLES" / "quebrado.json").write_text("{", encoding="utf-8")
            items, warnings = store.list_items(bundled, user)
            self.assertEqual([(i.entry.item_id, i.user, i.thumb is not None) for i in items],
                             [("porta-lisa-80-a1b2c3", False, True), ("mesa-1", True, False)])
            self.assertEqual(len(warnings), 1)
            self.assertEqual([i.entry.item_id for i in store.by_category(items, 'TABLES')], ["mesa-1"])

    def test_manifesto_com_tipo_inesperado(self):
        """BUG-20261011-KKHH: tipo inesperado vira aviso e o item é pulado; a listagem continua (EC-01)."""
        with tempfile.TemporaryDirectory() as bundled, tempfile.TemporaryDirectory() as user:
            write_item(bundled, manifest())
            for i, bad in enumerate(({"features": 5}, {"materials": 5}, {"size_mm": [None, 0, 0]})):
                write_item(user, manifest(item_id=f"ruim-{i}", **bad))
            items, warnings = store.list_items(bundled, user)
            self.assertEqual([i.entry.item_id for i in items], ["porta-lisa-80-a1b2c3"])
            self.assertEqual(len(warnings), 3)

    def test_nome_repetido(self):
        self.assertEqual(store.unique_name(["Mesa", "Mesa 2"], "Mesa"), "Mesa 3")
        self.assertEqual(store.unique_name(["Mesa"], "Vaso"), "Vaso")

    def test_paths_e_apagar_so_do_usuario(self):
        with tempfile.TemporaryDirectory() as bundled, tempfile.TemporaryDirectory() as user:
            write_item(bundled, manifest())
            write_item(user, manifest(item_id="meu-1", name="Meu"))
            items, _w = store.list_items(bundled, user)
            with self.assertRaises(PermissionError):
                store.delete(items[0])
            store.delete(items[1])
            self.assertFalse(any((Path(user) / "DOORS").iterdir()))
            paths = store.paths_for(user, 'DECOR', "vaso-1")
            self.assertTrue(paths["blend"].endswith("DECOR/vaso-1.blend"))

    def test_embutido_sem_3d_warehouse(self):
        good = [catalog.read_manifest(manifest())]
        bad = good + [catalog.read_manifest(manifest(item_id="x-1", source="3D Warehouse: Fulano"))]
        self.assertEqual(store.check_bundled(good), [])
        self.assertEqual(len(store.check_bundled(bad)), 1)


if __name__ == '__main__':
    unittest.main()
