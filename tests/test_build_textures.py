"""O pacote 1.1.2 inclui o catálogo e todas as miniaturas da 014."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build


class TexturePackageTest(unittest.TestCase):
    def test_catalogo_e_1209_miniaturas(self):
        package = ROOT / 'caffmob_draw'
        data = json.loads((package / 'textures/catalog.json').read_text())
        items = [i for m in data['manufacturers'] for c in m['collections'] for i in c['items']]
        self.assertEqual(len(items), 1209)
        self.assertEqual(build.texture_problems(str(package)), [])
        self.assertEqual(len(list((package / 'textures/thumbs').rglob('*.png'))), 1209)

    def test_prechecagem_de_nos_preservada(self):
        self.assertEqual(build.missing_node_files(str(ROOT / 'caffmob_draw')), [])

    def test_recusa_ausencia_incompletude_e_imagem_de_trabalho(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertTrue(build.texture_problems(directory))
            folder = root / 'textures'; folder.mkdir()
            (folder / 'catalog.json').write_text('{invalido')
            self.assertTrue(build.texture_problems(directory))
            (folder / 'catalog.json').write_text(json.dumps({'schema-version': 1, 'manufacturers': [
                {'collections': [{'items': [{'thumb': 'thumbs/falta.png'}]}]}]}))
            self.assertTrue(any('miniatura' in s for s in build.texture_problems(directory)))
            (folder / 'trabalho.jpg').touch()
            self.assertTrue(any('trabalho.jpg' in s for s in build.texture_problems(directory)))


if __name__ == '__main__':
    unittest.main()
