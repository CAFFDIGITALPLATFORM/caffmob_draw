"""Implantação física e recusas do destino (066, T015)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.openings import region_core as rc, transfer_core as tc


class TransferTest(unittest.TestCase):
    def test_canto_independe_do_sentido(self):
        a, b = (4, 2, 0), (4, 7, 0)
        for ref in ('START', 'END', 'EDGE'):
            corner = tc.reference_corner(a, b, ref, b)
            self.assertEqual(corner, tc.reference_corner(b, a, ref, b))
            x = tc.local_x(a, b, corner, 400, 0.978)
            reverse = tc.local_x(b, a, corner, 400, 0.978)
            self.assertAlmostEqual(x + reverse + 0.978, 5)
            self.assertAlmostEqual(tc.distance_mm(a, b, corner, x, 0.978), 400)

    def test_destino(self):
        args = ((0, 0, 0), (4, 0, 0), 2.8, 0.978, 2.2)
        fit = tc.destination(*args, distance=400)
        self.assertTrue(fit.ok)
        self.assertAlmostEqual(fit.x, 0.4)
        self.assertAlmostEqual(fit.width, 0.978)
        self.assertEqual(tc.destination((0, 0, 0), (0.7, 0, 0), 2.8, 0.978, 2.2).reason, rc.OUTSIDE)
        self.assertEqual(tc.destination(*args, distance=400, others=[(1, 2, 1, 2)]).reason, rc.OVERLAP)
        self.assertEqual(tc.destination((0, 0, 0), (4, 0, 0), 2.0, 0.978, 2.2).reason, rc.TOO_TALL)

    def test_topo_inclinado(self):
        args = ((0, 0, 0), (4, 0, 0), 3.0, 0.978, 2.2)
        self.assertTrue(tc.destination(*args, distance=100, end_height=1.8).ok)
        self.assertEqual(tc.destination(*args, distance=2900, end_height=1.8).reason, rc.TOO_TALL)


if __name__ == '__main__':
    unittest.main()
