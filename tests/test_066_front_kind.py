"""Mapeamento puro: construção não decide o movimento (066, T017)."""
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.aggregates.front_kind import front_kind


class FrontKindTest(unittest.TestCase):
    def test_giro(self):
        for hinge, expected in [('LEFT', 'DOOR'), ('RIGHT', 'DOOR'), ('TOP', 'FLIP_UP'), ('BOTTOM', 'FLIP_DOWN')]:
            self.assertEqual(front_kind('SWING', hinge), expected)

    def test_correr_nunca_gaveta(self):
        for hinge in ('LEFT', 'RIGHT', 'TOP', 'BOTTOM'):
            self.assertEqual(front_kind('SLIDE', hinge), 'SLIDING')


if __name__ == "__main__":
    unittest.main()
