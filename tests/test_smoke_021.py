"""Smoke e contratos de integração da feature 021 (T031): camadas, OpCut, paleta CAFFMob, sync, stick e gaveteiro."""

import py_compile
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

ROOT = TESTS_DIR.parent


class TestSmoke021(unittest.TestCase):
    def test_all_modified_python_files_compile_cleanly(self):
        targets = [
            "caffmob_draw/data/properties.py",
            "caffmob_draw/data/layers.py",
            "caffmob_draw/stick/props.py",
            "caffmob_draw/stick/release_guard_core.py",
            "caffmob_draw/stick/link.py",
            "caffmob_draw/stick/magnet.py",
            "caffmob_draw/armario_v2/build.py",
            "caffmob_draw/armario_v2/drawer_detect_core.py",
            "caffmob_draw/armario_v2/ops_drawer_convert.py",
            "caffmob_draw/armario_v2/__init__.py",
            "caffmob_draw/cutting/opcut_core.py",
            "caffmob_draw/cutting/module_list_core.py",
            "caffmob_draw/cutting/plan_export.py",
            "caffmob_draw/cutting/plan_render.py",
            "caffmob_draw/cutting/ops_opcut.py",
            "caffmob_draw/cutting/__init__.py",
            "caffmob_draw/texture_library/sync_missing.py",
            "caffmob_draw/texture_library/ops_sync_missing.py",
            "caffmob_draw/texture_library/__init__.py",
            "caffmob_draw/library_panel/style.py",
            "caffmob_draw/library_panel/ops_cabinet.py",
            "caffmob_draw/operators/floor_builder.py",
            "caffmob_draw/operators/ops_wall_extras.py",
            "caffmob_draw/operators/walls.py",
            "caffmob_draw/openings/sync.py",
            "caffmob_draw/walls2d/apply.py",
            "caffmob_draw/walls2d/ops_editor.py",
            "caffmob_draw/selection/lowered_wall_core.py",
            "caffmob_draw/selection/classify.py",
            "caffmob_draw/ui/header_collision.py",
            "caffmob_draw/ui/context_menu.py",
            "caffmob_draw/ui/sidebar_build.py",
            "caffmob_draw/ui/__init__.py",
        ]
        for rel in targets:
            path = ROOT / rel
            self.assertTrue(path.is_file(), f"Arquivo ausente: {rel}")
            py_compile.compile(str(path), doraise=True)

    def test_library_palette_removed_legacy_dark_green(self):
        style_src = (ROOT / "caffmob_draw/library_panel/style.py").read_text(encoding="utf-8")
        for legacy_green in ("#10302F", "#16403E", "#1F5250", "#0B2322"):
            self.assertNotIn(legacy_green, style_src)
        self.assertIn("#F07A2A", style_src)

    def test_opcut_rasterizer_outputs_exact_rgba_buffer(self):
        from caffmob_draw.cutting import opcut_core as oc
        from caffmob_draw.cutting import plan_render as pr

        plan = oc.calculate([
            oc.CutItem(id="1", label="Lateral", width=600, height=700, quantity=2, module_ref="M1"),
        ])
        self.assertEqual(len(plan.sheets), 1)
        buf = pr.rasterize_sheet_rgba(plan.sheets[0], img_w=64, img_h=48)
        self.assertEqual(len(buf), 64 * 48 * 4)

    def test_sync_missing_detector_flags_missing_and_empty_files(self):
        from caffmob_draw.texture_library import sync_missing as sm
        self.assertTrue(sm.is_file_missing_or_corrupt(""))
        self.assertTrue(sm.is_file_missing_or_corrupt("/caminho/inexistente/tex.png"))
        self.assertFalse(sm.is_file_missing_or_corrupt(str(ROOT / "build.py")))


if __name__ == "__main__":
    unittest.main()
