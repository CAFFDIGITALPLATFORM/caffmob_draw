"""O pacote MOBI não distribui catálogo nem miniaturas (063 RN-12)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build


class TexturePackageTest(unittest.TestCase):
    def test_sem_catalogo_nem_miniaturas(self):
        package = ROOT / "caffmob_draw"
        self.assertFalse((package / "textures").exists())
        self.assertEqual([p for p in package.rglob("catalog.json") if "translations" not in p.parts], [])
        self.assertEqual(list(package.rglob("thumbs")), [])

    def test_prechecagem_de_nos_preservada(self):
        self.assertEqual(build.missing_node_files(str(ROOT / "caffmob_draw")), [])
        self.assertFalse(hasattr(build, "texture_problems"))


if __name__ == "__main__":
    unittest.main()
