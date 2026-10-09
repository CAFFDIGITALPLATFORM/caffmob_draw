"""Testes das categorias da Biblioteca CAFFMob (feature 012, T006; D-17, RN-02 a RN-04)."""

import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.library_panel import categories_core as cc


class CategoriesTest(unittest.TestCase):
    def test_fixas_em_ordem(self):
        names = [c.name for c in cc.all_categories([])]
        self.assertEqual(names, ["Cozinha", "Banheiro", "Sala", "Home office"])
        self.assertEqual([c.line for c in cc.FIXED], ['COZ', 'BAN', 'SAL', 'ESC'])
        user = [cc.Category("Lavanderia", 'DOR', False)]
        self.assertEqual([c.name for c in cc.all_categories(user)][-1], "Lavanderia")

    def test_validar_nome(self):
        user = [cc.Category("Lavanderia", 'DOR', False)]
        self.assertIsNone(cc.validate_name("Closet", user))
        self.assertEqual(cc.validate_name("   ", user), cc.EMPTY)
        self.assertEqual(cc.validate_name("lavanderia", user), cc.REPEATED)
        self.assertEqual(cc.validate_name("COZINHA", user), cc.REPEATED)
        self.assertEqual(cc.validate_name("a/b", user), cc.INVALID_CHAR)
        self.assertEqual(cc.validate_name("a\\b", user), cc.INVALID_CHAR)

    def test_json(self):
        text = cc.dump([cc.Category("Lavanderia", 'DOR', False)])
        self.assertEqual(json.loads(text)['categories'], [{"name": "Lavanderia", "line": "DOR"}])
        categories, warnings = cc.parse(text)
        self.assertEqual(categories, [cc.Category("Lavanderia", 'DOR', False)])
        self.assertEqual(warnings, [])

    def test_json_ruim(self):
        categories, warnings = cc.parse("{isso não é json")
        self.assertEqual(categories, [])
        self.assertTrue(warnings)
        text = json.dumps({"categories": [{"name": "Varanda", "line": "XYZ"}, {"line": "COZ"}, "lixo"]})
        categories, warnings = cc.parse(text)
        self.assertEqual(categories, [cc.Category("Varanda", 'COZ', False)])
        self.assertEqual(len(warnings), 3)
        self.assertEqual(cc.parse("")[0], [])

    def test_pastas_soltas(self):
        user = [cc.Category("Lavanderia", 'DOR', False)]
        merged = cc.merge_folders(user, ["Geral", "Lavanderia", "Cozinha", ".oculta"])
        self.assertEqual([(c.name, c.line) for c in merged], [("Lavanderia", 'DOR'), ("Geral", 'COZ')])


if __name__ == "__main__":
    unittest.main()
