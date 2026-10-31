"""Medida física de módulo: leitura e conversão (feature 080, T003; CA-01, CA-03)."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.target import module_geometry as mg


def _matrix(rot=None, scale=(1.0, 1.0, 1.0), loc=(0.0, 0.0, 0.0)):
    rot = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    m = [[rot[r][c] * scale[c] for c in range(3)] + [loc[r]] for r in range(3)]
    return m + [[0, 0, 0, 1]]


def _rot_z(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _matmul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


PARAMS = (0.8, 0.55, 0.7)      # largura, profundidade, altura (m)


def _mm(values):
    return tuple(round(v * 1000, 4) for v in values)


class ReadTest(unittest.TestCase):
    def read(self, world, own=(1, 1, 1)):
        scales = mg.axis_scales(world)
        return mg.physical(PARAMS, scales), mg.ancestor_scales(scales, own)

    def test_identity(self):
        phys, anc = self.read(_matrix())
        self.assertEqual(_mm(phys), (800, 550, 700))
        self.assertEqual(anc, (1.0, 1.0, 1.0))

    def test_own_scale(self):
        phys, anc = self.read(_matrix(scale=(0.8125, 1, 1)), own=(0.8125, 1, 1))
        self.assertEqual(_mm(phys), (650, 550, 700))
        self.assertEqual(anc, (1.0, 1.0, 1.0))

    def test_parent_scale_only(self):
        world = _matmul(_matrix(scale=(2, 1, 1)), _matrix(loc=(1, 0, 0)))
        phys, anc = self.read(world)
        self.assertEqual(_mm(phys), (1600, 550, 700))
        self.assertEqual(anc, (2.0, 1.0, 1.0))

    def test_two_ancestors_compose(self):
        world = _matmul(_matmul(_matrix(scale=(2, 1, 1)), _matrix(scale=(1.5, 1, 0.5))),
                        _matrix(scale=(0.5, 1, 1)))
        phys, anc = self.read(world, own=(0.5, 1, 1))
        self.assertEqual(_mm(phys), (1200, 550, 350))
        self.assertAlmostEqual(anc[0], 3.0)
        self.assertAlmostEqual(anc[2], 0.5)

    def test_non_uniform_own(self):
        phys, _ = self.read(_matrix(scale=(0.5, 2, 1.25)), own=(0.5, 2, 1.25))
        self.assertEqual(_mm(phys), (400, 1100, 875))

    def test_rotated_root_37(self):
        phys, anc = self.read(_matrix(_rot_z(37), scale=(0.8125, 1, 1)), own=(0.8125, 1, 1))
        self.assertEqual(_mm(phys), (650, 550, 700))
        self.assertAlmostEqual(anc[0], 1.0)

    def test_parent_rotated_90_non_uniform(self):
        # Pai com escala 2 em X do pai; raiz girada 90°: o X da raiz é o Y do pai (escala 1), e o Y da raiz é o X.
        world = _matmul(_matrix(scale=(2, 1, 1)), _matrix(_rot_z(90)))
        phys, anc = self.read(world)
        self.assertEqual(_mm(phys), (800, 1100, 700))
        self.assertAlmostEqual(anc[0], 1.0)
        self.assertAlmostEqual(anc[1], 2.0)

    def test_reflection_one_axis(self):
        phys, anc = self.read(_matrix(scale=(-0.75, 1, 1)), own=(-0.75, 1, 1))
        self.assertEqual(_mm(phys), (600, 550, 700))
        self.assertAlmostEqual(anc[0], 1.0)

    def test_reflection_two_axes(self):
        phys, _ = self.read(_matrix(scale=(-1, -0.5, 1)), own=(-1, -0.5, 1))
        self.assertEqual(_mm(phys), (800, 275, 700))


class RefusalTest(unittest.TestCase):
    def test_shear_refused_with_module_message(self):
        sheared = [[1, 0.3, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        with self.assertRaises(mg.ModuleGeometryError) as caught:
            mg.axis_scales(sheared)
        self.assertIn("módulo", str(caught.exception))

    def test_near_zero_axis_refused(self):
        with self.assertRaises(mg.ModuleGeometryError) as caught:
            mg.axis_scales(_matrix(scale=(0.9e-9, 1, 1)))
        self.assertIn("módulo", str(caught.exception))

    def test_boundary_accepted(self):
        scales = mg.axis_scales(_matrix(scale=(1e-9, 1, 1)))
        self.assertAlmostEqual(scales[0], 1e-9)

    def test_not_finite_refused(self):
        for bad in (math.nan, math.inf):
            with self.assertRaises(mg.ModuleGeometryError):
                mg.axis_scales(_matrix(scale=(bad, 1, 1)))

    def test_own_scale_zero_refused(self):
        with self.assertRaises(mg.ModuleGeometryError):
            mg.ancestor_scales((1, 1, 1), (0.0, 1, 1))


class ParamForTest(unittest.TestCase):
    def test_compensates_ancestor(self):
        self.assertAlmostEqual(mg.param_for(1.0, 2.0), 0.5)

    def test_round_trip(self):
        for anc in (1.0, 2.0, 0.37, 3.5):
            self.assertAlmostEqual(mg.physical((mg.param_for(0.65, anc),), (anc,))[0], 0.65)


if __name__ == '__main__':
    unittest.main()
