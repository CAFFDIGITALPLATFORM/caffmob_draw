"""078 T008/T015/T016: matriz exaustiva 30 modelos × 3 materiais em door_core e window_core."""
import math
import unittest
import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2.contrato import (
    MATERIAIS_DE_ABERTURA,
    MODELOS_DE_JANELA,
    MODELOS_DE_PORTA,
)
from caffmob_draw.openings import door_core as dc
from caffmob_draw.openings import window_core as wc


class Test078OpeningsCatalog(unittest.TestCase):
    def test_catalogo_10_portas_x_3_materiais(self):
        self.assertEqual(tuple(dc.DOOR_MODELS), MODELOS_DE_PORTA)
        for modelo in MODELOS_DE_PORTA:
            for material in MATERIAIS_DE_ABERTURA:
                with self.subTest(modelo=modelo, material=material):
                    hole_w = 1.60 if modelo in ('porta_giro_dupla', 'porta_correr_2f', 'porta_correr_4f', 'porta_correr_camarao') else 0.90
                    hole_h = 2.15
                    wall = 0.15
                    leaf_w, leaf_h = dc.leaf_size(hole_w, hole_h, model=modelo)
                    parts = dc.door_parts(
                        leaf_w,
                        leaf_h,
                        wall,
                        double=dc.is_double_leaf(modelo),
                        model=modelo,
                        material=material,
                    )
                    self.assertGreaterEqual(len(parts), 6)
                    roles = {p.role for p in parts}
                    self.assertIn(dc.FRAME, roles)
                    self.assertIn(dc.LEAF, roles)
                    leaves = sorted({p.leaf for p in parts if p.leaf is not None})
                    self.assertTrue(len(leaves) >= 1)
                    for idx in leaves:
                        self.assertTrue(any(p.role == dc.LEAF and p.leaf == idx for p in parts))
                    for p in parts:
                        self.assertTrue(all(math.isfinite(c) for c in p.center))
                        self.assertTrue(all(math.isfinite(s) and s > 0 for s in p.size_xyz))
                    mats = {p.material for p in parts}
                    if material == 'madeira':
                        self.assertIn(dc.WOOD, mats)
                    elif material == 'aluminio':
                        self.assertIn(dc.ALU, mats)
                    elif material == 'blindex':
                        self.assertIn(dc.GLASS, mats)

    def test_catalogo_20_janelas_x_3_materiais(self):
        self.assertEqual(tuple(wc.WINDOW_MODELS), MODELOS_DE_JANELA)
        for modelo in MODELOS_DE_JANELA:
            for material in MATERIAIS_DE_ABERTURA:
                with self.subTest(modelo=modelo, material=material):
                    parts = wc.window_parts(1.50, 1.10, 0.15, model=modelo, material=material)
                    self.assertGreaterEqual(len(parts), 6)
                    roles = {p.role for p in parts}
                    self.assertIn(dc.FRAME, roles)
                    self.assertIn(dc.LEAF, roles)
                    leaves = sorted({p.leaf for p in parts if p.leaf is not None})
                    self.assertTrue(len(leaves) >= 1)
                    for idx in leaves:
                        self.assertTrue(any(p.role == dc.LEAF and p.leaf == idx for p in parts))
                    for p in parts:
                        self.assertTrue(all(math.isfinite(c) for c in p.center))
                        self.assertTrue(all(math.isfinite(s) and s > 0 for s in p.size_xyz))
                    mats = {p.material for p in parts}
                    if material == 'madeira':
                        self.assertIn(dc.WOOD, mats)
                    elif material == 'aluminio':
                        self.assertIn(dc.ALU, mats)
                    elif material == 'blindex':
                        self.assertIn(dc.GLASS, mats)


if __name__ == '__main__':
    unittest.main()
