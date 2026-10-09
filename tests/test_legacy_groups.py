"""Testes dos grupos salvos das bibliotecas herdadas (feature 012, T065; D-29, D-30, RN-16)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.legacy import groups_core as gc


class GroupsTest(unittest.TestCase):
    def test_pendentes_e_oferta(self):
        files = ["Cozinha L.blend", "Ilha.blend"]
        self.assertEqual(gc.pending(files, {}), files)
        marker = {"offered": True, "converted": ["Ilha.blend"]}
        self.assertEqual(gc.pending(files, marker), ["Cozinha L.blend"])
        self.assertTrue(gc.should_offer(files, {}))
        self.assertFalse(gc.should_offer(files, marker))
        self.assertFalse(gc.should_offer([], {}))

    def test_marcador(self):
        text = gc.dump_marker({"offered": True, "converted": ["a.blend"]})
        self.assertEqual(gc.parse_marker(text), {"offered": True, "converted": ["a.blend"]})
        self.assertEqual(gc.parse_marker("{ruim"), {})                 # inválido: oferece de novo
        self.assertEqual(gc.parse_marker('{"offered": "sim"}'), {})
        self.assertEqual(gc.mark(gc.parse_marker(""), ["b.blend"]), {"offered": True, "converted": ["b.blend"]})

    def test_nome_de_destino(self):
        self.assertEqual(gc.target_name("Cozinha L", set()), "Cozinha L")
        self.assertEqual(gc.target_name("Cozinha L", {"cozinha l"}), "Cozinha L (2)")
        self.assertEqual(gc.target_name("Cozinha L", {"cozinha l", "cozinha l (2)"}), "Cozinha L (3)")


if __name__ == "__main__":
    unittest.main()
