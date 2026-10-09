"""Testes da decisão de aplicar o padrão (feature 012, T007; D-20, RN-10, RN-11)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.standards import apply_core as ac

M = ac.ModuleInfo


class PlanTest(unittest.TestCase):
    def setUp(self):
        self.modules = [
            M("Balcão 1", ac.CAFFMOB, "padrao-a", False),
            M("Balcão 2", ac.CAFFMOB, "", False),                 # sem origem: segue
            M("Base passante", ac.CAFFMOB, "padrao-a", True),     # padrão próprio
            M("De outro padrão", ac.CAFFMOB, "padrao-b", False),
            M("Frameless antigo", ac.LEGACY, "padrao-a", False),
            M("Cadeira OBJ", ac.OTHER, "", False),
        ]

    def test_plano(self):
        plan = ac.plan(self.modules, previous_uid="padrao-a")
        self.assertEqual(plan.follow, ["Balcão 1", "Balcão 2"])
        self.assertEqual(plan.differ, ["Base passante", "De outro padrão"])
        self.assertEqual(plan.not_applicable, ["Frameless antigo", "Cadeira OBJ"])
        self.assertEqual(plan.legacy, ["Frameless antigo"])

    def test_respostas(self):
        plan = ac.plan(self.modules, previous_uid="padrao-a")
        self.assertEqual(ac.targets(plan, False, False), [])
        self.assertEqual(ac.targets(plan, False, True), [])
        self.assertEqual(ac.targets(plan, True, False), ["Balcão 1", "Balcão 2"])
        self.assertEqual(ac.targets(plan, True, True), ["Balcão 1", "Balcão 2", "Base passante", "De outro padrão"])

    def test_padrao_proprio(self):
        self.assertFalse(ac.is_own({}, 'LATERAL', 'LATERAL', [0.0, 0.0]))
        self.assertTrue(ac.is_own({'height': 1}, 'LATERAL', 'LATERAL', []))
        self.assertTrue(ac.is_own({}, 'BASE', 'LATERAL', []))
        self.assertTrue(ac.is_own({}, 'LATERAL', 'LATERAL', [0.0, 0.025]))


if __name__ == "__main__":
    unittest.main()
