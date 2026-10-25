"""Medidas semânticas da chapa (feature 067, T016; RF-006, RF-008, RF-011)."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.target import part_geometry as pg


def _matrix(rot=None, scale=(1.0, 1.0, 1.0), loc=(0.0, 0.0, 0.0)):
    rot = rot or [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    m = [[rot[r][c] * scale[c] for c in range(3)] + [loc[r]] for r in range(3)]
    return m + [[0, 0, 0, 1]]


def _rot_x(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _rot_z(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _matmul(a, b):
    return [[sum(a[r][k] * b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def _fields(m):
    return {item.field: round(item.value * 1000, 3) for item in m.face + (m.thickness,)}


# Placa de 800 × 400 × 18 mm: X = 0,8, Y = 0,018, Z = 0,4 (em pé, face para −Y).
STANDING = ((0, 0, 0), (0.8, 0.018, 0.4))
# A mesma placa deitada: X = 0,8, Y = 0,4, Z = 0,018.
LYING = ((0, 0, 0), (0.8, 0.4, 0.018))


class MeasureTest(unittest.TestCase):
    def test_em_pe_largura_e_altura(self):
        m = pg.measure(*STANDING, _matrix())
        self.assertEqual(_fields(m), {pg.WIDTH: 800, pg.HEIGHT: 400, pg.THICKNESS: 18})
        self.assertEqual([i.field for i in m.face], [pg.WIDTH, pg.HEIGHT])

    def test_deitada_largura_e_profundidade(self):
        self.assertEqual(_fields(pg.measure(*LYING, _matrix())), {pg.WIDTH: 800, pg.DEPTH: 400, pg.THICKNESS: 18})

    def test_lateral_altura_e_profundidade(self):
        lateral = ((0, 0, 0), (0.018, 0.5, 0.7))
        self.assertEqual(_fields(pg.measure(*lateral, _matrix())), {pg.HEIGHT: 700, pg.DEPTH: 500, pg.THICKNESS: 18})

    def test_deitada_girada_90_em_x_fica_em_pe(self):
        m = pg.measure(*LYING, _matrix(_rot_x(90)))
        self.assertEqual(_fields(m), {pg.WIDTH: 800, pg.HEIGHT: 400, pg.THICKNESS: 18})

    def test_girada_90_em_z_no_mundo_e_no_referencial_do_dono(self):
        world = _matrix(_rot_z(90))
        m = pg.measure(*STANDING, world)
        self.assertEqual(_fields(m), {pg.HEIGHT: 400, pg.DEPTH: 800, pg.THICKNESS: 18})
        m = pg.measure(*STANDING, world, reference=_rot_z(90))   # o módulo dono girou junto
        self.assertEqual(_fields(m), {pg.WIDTH: 800, pg.HEIGHT: 400, pg.THICKNESS: 18})

    def test_pai_com_escala_2x(self):
        parent = _matrix(scale=(2.0, 2.0, 2.0))
        m = pg.measure(*STANDING, _matmul(parent, _matrix()))
        self.assertEqual(_fields(m), {pg.WIDTH: 1600, pg.HEIGHT: 800, pg.THICKNESS: 36})

    def test_escala_negativa_mede_o_comprimento(self):
        self.assertEqual(_fields(pg.measure(*STANDING, _matrix(scale=(-1.0, 1.0, 1.0)))),
                         {pg.WIDTH: 800, pg.HEIGHT: 400, pg.THICKNESS: 18})

    def test_recusa_shear_escala_zero_e_nao_finito(self):
        sheared = _matrix()
        sheared[0][1] = 0.5
        for matrix in (sheared, _matrix(scale=(1.0, 0.0, 1.0)), _matrix(loc=(0, 0, 0), scale=(math.inf, 1, 1))):
            with self.assertRaises(pg.PartGeometryError):
                pg.measure(*STANDING, matrix)
        with self.assertRaises(pg.PartGeometryError):
            pg.measure((0, 0, 0), (math.nan, 0.018, 0.4), _matrix())

    def test_valor_digitado(self):
        self.assertEqual(pg.validate_length("0.5"), 0.5)
        for bad in (-0.1, 0.0, math.inf, math.nan, "abc", None):
            with self.assertRaises(pg.PartGeometryError):
                pg.validate_length(bad)


if __name__ == '__main__':
    unittest.main()
