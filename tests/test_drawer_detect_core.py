"""Testes unitários puros do classificador geométrico de gaveteiro (feature 021, T007; RF-12, RF-13, RN-11)."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.armario_v2 import drawer_detect_core as ddc


def _complete_drawer_boxes():
    """Gaveta de 500x450x180 mm (X: -0.25..0.25, Y: -0.45..0.0, Z: 0.0..0.18) com 6 peças."""
    return [
        ddc.PartBox("lat_e", (-0.235, -0.43, 0.01), (-0.220, 0.0, 0.16)),       # Lateral esquerda (15mm)
        ddc.PartBox("lat_d", (0.220, -0.43, 0.01), (0.235, 0.0, 0.16)),         # Lateral direita (15mm)
        ddc.PartBox("contrafrente", (-0.220, -0.43, 0.01), (0.220, -0.415, 0.16)),  # Contrafrente (15mm)
        ddc.PartBox("traseira", (-0.220, -0.015, 0.01), (0.220, 0.0, 0.16)),    # Posterior/Traseira (15mm)
        ddc.PartBox("fundo", (-0.225, -0.425, 0.01), (0.225, -0.005, 0.016)),   # Fundo (6mm)
        ddc.PartBox("frente", (-0.250, -0.450, 0.0), (0.250, -0.432, 0.18)),    # Frente acabamento (18mm)
    ]


class TestDrawerDetectCore(unittest.TestCase):
    def test_detects_all_six_parts_in_complete_drawer(self):
        analysis = ddc.analyze_drawer_parts(_complete_drawer_boxes())
        self.assertTrue(analysis.is_complete)
        self.assertEqual(analysis.missing_roles, [])
        self.assertEqual(analysis.role_map['LATERAL_ESQ'].part_id, "lat_e")
        self.assertEqual(analysis.role_map['LATERAL_DIR'].part_id, "lat_d")
        self.assertEqual(analysis.role_map['CONTRAFRENTE'].part_id, "contrafrente")
        self.assertEqual(analysis.role_map['TRASEIRA'].part_id, "traseira")
        self.assertEqual(analysis.role_map['FUNDO'].part_id, "fundo")
        self.assertEqual(analysis.role_map['FRENTE'].part_id, "frente")

    def test_partial_drawer_never_blocks_and_lists_missing_roles(self):
        partial = [b for b in _complete_drawer_boxes() if b.part_id not in ("contrafrente", "fundo")]
        analysis = ddc.analyze_drawer_parts(partial)
        self.assertFalse(analysis.is_complete)
        self.assertIn('CONTRAFRENTE', analysis.missing_roles)
        self.assertIn('FUNDO', analysis.missing_roles)
        self.assertIn('LATERAL_ESQ', analysis.role_map)
        self.assertIn('LATERAL_DIR', analysis.role_map)
        self.assertIn('TRASEIRA', analysis.role_map)
        self.assertIn('FRENTE', analysis.role_map)

    def test_missing_parts_synthesis_generates_exact_missing_boxes(self):
        partial = [b for b in _complete_drawer_boxes() if b.part_id not in ("contrafrente", "fundo")]
        analysis = ddc.analyze_drawer_parts(partial)
        generated = ddc.synthesize_missing_parts(analysis)
        gen_roles = {g.role for g in generated}
        self.assertEqual(gen_roles, {'CONTRAFRENTE', 'FUNDO'})

    def test_default_hardware_metadata_includes_slides_handle_and_fasteners(self):
        hw = ddc.default_hardware(slide_type='TELESCOPICA', handle_type='EXTERNO')
        self.assertEqual(hw['corredica_tipo'], 'TELESCOPICA')
        self.assertEqual(hw['puxador_tipo'], 'EXTERNO')
        self.assertIn('fita_borda', hw)
        self.assertIn('parafusos', hw)


if __name__ == "__main__":
    unittest.main()
