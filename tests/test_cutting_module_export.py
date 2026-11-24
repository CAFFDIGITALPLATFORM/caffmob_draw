"""Testes unitários puros da lista agrupada por módulo e exportação SVG/HTML/PDF (feature 021, T006; RF-01, RF-02)."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.cutting import module_list_core as mlc
from caffmob_draw.cutting import opcut_core as oc
from caffmob_draw.cutting import plan_export as pe


class _FakePart:
    def __init__(self, id, name, width, height, thickness=15.0, material="Branco",
                 grain_direction="NONE", module_ref="Balcão", quantity=1,
                 component="LAT", is_hardware=False, cut_exclude=False):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.thickness = thickness
        self.material = material
        self.grain_direction = grain_direction
        self.module_ref = module_ref
        self.quantity = quantity
        self.component = component
        self.is_hardware = is_hardware
        self.cut_exclude = cut_exclude


class TestCuttingModuleExport(unittest.TestCase):
    def test_group_parts_by_module_excludes_hardware_and_excluded(self):
        parts = [
            _FakePart("1", "Lateral E", 550, 720, module_ref="Balcão Pia", quantity=2),
            _FakePart("2", "Base", 800, 550, module_ref="Balcão Pia", quantity=1),
            _FakePart("3", "Corrediça", 450, 45, module_ref="Balcão Pia", component="FER", is_hardware=True),
            _FakePart("4", "Origem Oculta", 500, 500, module_ref="Balcão Pia", cut_exclude=True),
            _FakePart("5", "Lateral Aéreo", 320, 700, module_ref="Aéreo", quantity=2),
        ]
        groups = mlc.group_by_module(parts)
        self.assertEqual(len(groups), 2)
        by_name = {g.module_name: g for g in groups}
        self.assertEqual(by_name["Balcão Pia"].total_pieces, 3)
        self.assertEqual(by_name["Aéreo"].total_pieces, 2)

    def test_export_svg_html_and_pdf_atomic(self):
        items = [
            oc.CutItem(id="p1", label="Lateral", width=550, height=720, quantity=2,
                       thickness=15, material="Branco", can_rotate=True, module_ref="Balcão Pia"),
            oc.CutItem(id="p2", label="Base", width=800, height=550, quantity=1,
                       thickness=15, material="Branco", can_rotate=True, module_ref="Balcão Pia"),
        ]
        plan = oc.calculate(items, sheet_width=2750, sheet_height=1830, margin=10, kerf=4)
        parts = [
            _FakePart("p1", "Lateral", 550, 720, module_ref="Balcão Pia", quantity=2),
            _FakePart("p2", "Base", 800, 550, module_ref="Balcão Pia", quantity=1),
        ]
        groups = mlc.group_by_module(parts)

        with tempfile.TemporaryDirectory() as tmp:
            svg_path = os.path.join(tmp, "chapa_1.svg")
            html_path = os.path.join(tmp, "plano.html")
            pdf_path = os.path.join(tmp, "plano.pdf")

            pe.write_svg(plan.sheets[0], svg_path)
            pe.write_html(plan, groups, html_path, title="Projeto Teste")
            pe.write_pdf(plan, groups, pdf_path, title="Projeto Teste")

            svg = Path(svg_path).read_text(encoding="utf-8")
            self.assertIn("<svg", svg)
            self.assertIn("Lateral", svg)

            html = Path(html_path).read_text(encoding="utf-8")
            self.assertIn("<!DOCTYPE html>", html)
            self.assertIn("Balcão Pia", html)
            self.assertIn("<svg", html)

            pdf_bytes = Path(pdf_path).read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-1.4"))
            self.assertIn(b"%%EOF", pdf_bytes)


if __name__ == "__main__":
    unittest.main()
