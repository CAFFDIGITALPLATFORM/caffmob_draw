"""Testes unitários puros da supressão do ímã após desgrudar (feature 021, T008; RF-09, RN-08)."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.stick import release_guard_core as rgc


class TestStickReleaseGuard(unittest.TestCase):
    def test_suppresses_restick_to_same_host_within_hysteresis_band(self):
        # Usuário desgrudou da Parede_1 e moveu 30 mm para frente (ainda dentro da tolerância 50 mm do ímã)
        self.assertTrue(rgc.should_suppress_magnet(
            released_host_name="Parede_1",
            candidate_host_name="Parede_1",
            distance_m=0.03,
            magnet_tolerance_m=0.05,
        ))

    def test_does_not_suppress_different_host(self):
        self.assertFalse(rgc.should_suppress_magnet(
            released_host_name="Parede_1",
            candidate_host_name="Parede_2",
            distance_m=0.02,
            magnet_tolerance_m=0.05,
        ))

    def test_clears_release_guard_once_item_moves_well_past_band(self):
        self.assertTrue(rgc.should_clear_release_guard(
            released_host_name="Parede_1",
            min_distance_to_released_host_m=0.20,
            magnet_tolerance_m=0.05,
        ))
        self.assertFalse(rgc.should_clear_release_guard(
            released_host_name="Parede_1",
            min_distance_to_released_host_m=0.04,
            magnet_tolerance_m=0.05,
        ))


if __name__ == "__main__":
    unittest.main()
