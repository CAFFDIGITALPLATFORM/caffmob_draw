"""Testes unitários puros do motor de corte guilhotinado OpCut (feature 021, T005; RF-02, RN-02)."""

import unittest
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.cutting import opcut_core as oc


class TestOpCutCore(unittest.TestCase):
    def test_packs_parts_without_overlap_respecting_margin_and_kerf(self):
        items = [
            oc.CutItem(id="p1", label="Lateral E", width=600, height=700, quantity=2,
                       thickness=15, material="Branco", can_rotate=True, module_ref="Balcão"),
            oc.CutItem(id="p2", label="Base", width=800, height=550, quantity=2,
                       thickness=15, material="Branco", can_rotate=True, module_ref="Balcão"),
            oc.CutItem(id="p3", label="Prateleira", width=770, height=520, quantity=2,
                       thickness=15, material="Branco", can_rotate=True, module_ref="Balcão"),
        ]
        result = oc.calculate(items, sheet_width=2750, sheet_height=1830, margin=10, kerf=4, method='forward_greedy')
        self.assertEqual(len(result.unplaced), 0)
        self.assertGreaterEqual(len(result.sheets), 1)
        total_placed = sum(len(s.used) for s in result.sheets)
        self.assertEqual(total_placed, 6)
        for sheet in result.sheets:
            for r in sheet.used:
                self.assertGreaterEqual(r.x, 10.0 - 1e-6)
                self.assertGreaterEqual(r.y, 10.0 - 1e-6)
                self.assertLessEqual(r.x + r.width, 2750.0 - 10.0 + 1e-6)
                self.assertLessEqual(r.y + r.height, 1830.0 - 10.0 + 1e-6)
            for i, a in enumerate(sheet.used):
                for b in sheet.used[i + 1:]:
                    overlap_x = (a.x < b.x + b.width - 1e-6) and (b.x < a.x + a.width - 1e-6)
                    overlap_y = (a.y < b.y + b.height - 1e-6) and (b.y < a.y + a.height - 1e-6)
                    self.assertFalse(overlap_x and overlap_y, f"Sobreposição entre {a} e {b}")

    def test_respects_grain_lock_when_can_rotate_false(self):
        items = [
            oc.CutItem(id="v1", label="Porta Alta", width=500, height=1800, quantity=1,
                       thickness=15, material="Carvalho", can_rotate=False, module_ref="Torre"),
        ]
        result = oc.calculate(items, sheet_width=2750, sheet_height=1830, margin=10, kerf=4)
        self.assertEqual(len(result.unplaced), 0)
        placed = result.sheets[0].used[0]
        self.assertFalse(placed.rotated)
        self.assertAlmostEqual(placed.width, 500.0)
        self.assertAlmostEqual(placed.height, 1800.0)

    def test_oversized_part_goes_to_unplaced_without_crash(self):
        items = [
            oc.CutItem(id="big", label="Tampo Gigante", width=2900, height=600, quantity=1,
                       thickness=18, material="Freijó", can_rotate=True, module_ref="Bancada"),
        ]
        result = oc.calculate(items, sheet_width=2750, sheet_height=1830, margin=10, kerf=4)
        self.assertEqual(len(result.sheets), 0)
        self.assertEqual(len(result.unplaced), 1)
        self.assertEqual(result.unplaced[0].id, "big")

    def test_empty_items_returns_empty_result(self):
        result = oc.calculate([], sheet_width=2750, sheet_height=1830, margin=10, kerf=4)
        self.assertEqual(result.sheets, [])
        self.assertEqual(result.unplaced, [])


if __name__ == "__main__":
    unittest.main()
