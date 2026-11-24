"""Testes unitários puros da direção de espessura do piso e mapeamento de camadas (feature 021, T009; RF-05, RF-06)."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.data import layers


class TestFloorDirectionAndLayers(unittest.TestCase):
    def test_floor_thickness_down_bounds(self):
        z_min, z_max = layers.floor_z_bounds(0.0, 0.15, 'DOWN')
        self.assertAlmostEqual(z_min, -0.15)
        self.assertAlmostEqual(z_max, 0.0)

    def test_floor_thickness_up_bounds(self):
        z_min, z_max = layers.floor_z_bounds(0.0, 0.15, 'UP')
        self.assertAlmostEqual(z_min, 0.0)
        self.assertAlmostEqual(z_max, 0.15)

    def test_floor_thickness_respects_nonzero_base_z(self):
        z_min, z_max = layers.floor_z_bounds(2.80, 0.12, 'DOWN')
        self.assertAlmostEqual(z_min, 2.68)
        self.assertAlmostEqual(z_max, 2.80)

    def test_arch_subcollection_names(self):
        self.assertEqual(layers.arch_subcollection_name('WALL'), 'Parede')
        self.assertEqual(layers.arch_subcollection_name('FLOOR'), 'Piso')
        self.assertEqual(layers.arch_subcollection_name('CEILING'), 'Teto')
        self.assertEqual(layers.arch_subcollection_name('OPENING'), 'Aberturas')
        self.assertIsNone(layers.arch_subcollection_name('OTHER'))
        self.assertEqual(layers.ARQUITETURA, 'Arquitetura')
        self.assertEqual(layers.MARCENARIA, 'Marcenaria')


if __name__ == "__main__":
    unittest.main()
