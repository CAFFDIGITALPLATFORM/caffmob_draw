"""O empacotamento exige o catálogo e as miniaturas e recusa imagem em tamanho real (feature 014, T039; D-04)."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build  # noqa: E402


def make_package(items=("a/b/c",), extra=()):
    root = tempfile.mkdtemp()
    folder = os.path.join(root, "textures")
    os.makedirs(os.path.join(folder, "thumbs"))
    entries = []
    for tid in items:
        thumb = "thumbs/" + tid + ".png"
        os.makedirs(os.path.dirname(os.path.join(folder, thumb)), exist_ok=True)
        open(os.path.join(folder, thumb), "wb").write(b"png")
        entries.append({"id": tid, "thumb": thumb})
    catalog = {"manufacturers": [{"id": "a", "collections": [{"id": "b", "items": entries}]}]}
    json.dump(catalog, open(os.path.join(folder, "catalog.json"), "w"))
    for rel in extra:
        os.makedirs(os.path.dirname(os.path.join(folder, rel)) or folder, exist_ok=True)
        open(os.path.join(folder, rel), "wb").write(b"jpg")
    return root


class TextureProblemsTest(unittest.TestCase):
    def test_pacote_correto(self):
        self.assertEqual(build.texture_problems(make_package()), [])

    def test_sem_catalogo(self):
        root = tempfile.mkdtemp()
        self.assertIn("catalog.json", build.texture_problems(root)[0])

    def test_miniatura_faltando(self):
        root = make_package()
        os.remove(os.path.join(root, "textures", "thumbs", "a", "b", "c.png"))
        self.assertTrue(any("falta a miniatura" in p for p in build.texture_problems(root)))

    def test_recusa_imagem_em_tamanho_real(self):
        root = make_package(extra=("arauco/Colecao/Anis.jpg", "thumbs/nao_listada.png"))
        problems = build.texture_problems(root)
        self.assertEqual(len(problems), 2, problems)
        self.assertTrue(all("tamanho real" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
