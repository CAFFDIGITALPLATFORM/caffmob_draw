"""Núcleo da rotação do Mover Sobre (feature 067, T033; RF-121 a RF-125)."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.move_over import rotation as rot

BOX = ((0.0, -0.6, 0.0), (0.8, 0.0, 0.72))      # caixa local de A (frente em −Y)


def close(a, b, tol=1e-9):
    return all(abs(a[i] - b[i]) <= tol for i in range(len(a)))


class RotateAboutTest(unittest.TestCase):
    def test_pivo_invariante_em_90_e_180(self):
        origin, orientation = (1.0, 2.0, 0.0), rot.IDENTITY
        pivot = rot.local_point(BOX, 'C100')
        start = rot.world_point(origin, orientation, pivot)
        origin, orientation = rot.rotate_about(origin, orientation, pivot, rot.AXES['Z'], 90.0)
        self.assertTrue(close(rot.world_point(origin, orientation, pivot), start))
        origin, orientation = rot.rotate_about(origin, orientation, pivot, rot.AXES['Z'], 180.0)
        self.assertTrue(close(rot.world_point(origin, orientation, pivot), start))
        self.assertAlmostEqual(rot.angle_about(orientation, 'Z'), -90.0, places=9)

    def test_composicao_t_r_t(self):
        # M = T(P)·R(N,θ)·T(−P)·M0: a origem gira em torno do pivô.
        origin, orientation = rot.rotate_about((0.0, 0.0, 0.0), rot.IDENTITY, (1.0, 0.0, 0.0), rot.AXES['Z'], 90.0)
        self.assertTrue(close(origin, (1.0, -1.0, 0.0)))
        self.assertTrue(close(rot.rotate_vector(orientation, (1.0, 0.0, 0.0)), (0.0, 1.0, 0.0)))

    def test_frontal_gira_no_plano_xz(self):
        _o, q = rot.rotate_about((0.0, 0.0, 0.0), rot.IDENTITY, (0.0, 0.0, 0.0), rot.AXES[rot.VIEW_AXIS['front']], 90)
        v = rot.rotate_vector(q, (1.0, 0.0, 0.0))
        self.assertAlmostEqual(v[1], 0.0, places=9)          # fica no plano X/Z
        self.assertAlmostEqual(abs(v[2]), 1.0, places=9)

    def test_escolher_outro_ponto_nao_move(self):
        origin, orientation = (0.3, 0.1, 0.0), rot.axis_angle(rot.AXES['Z'], 30.0)
        for key in rot.POINT_KEYS:
            rot.local_point(BOX, key)
        self.assertEqual((origin, orientation), ((0.3, 0.1, 0.0), rot.axis_angle(rot.AXES['Z'], 30.0)))

    def test_pontos_locais(self):
        self.assertEqual(rot.local_point(BOX, 'BASE_CENTER'), (0.4, -0.3, 0.0))
        self.assertEqual(rot.local_point(BOX, 'C111'), (0.8, 0.0, 0.72))
        self.assertEqual(len(rot.POINT_KEYS), 10)
        with self.assertRaises(ValueError):
            rot.local_point(BOX, 'NADA')


class AngleTest(unittest.TestCase):
    def test_atan2_com_desdobramento(self):
        a = rot.signed_angle((0, 0), (1, 0.01))
        b = rot.unwrap(170.0, -175.0)
        self.assertAlmostEqual(b, 185.0)
        self.assertAlmostEqual(rot.unwrap(-170.0, 175.0), -185.0)
        self.assertGreater(a, 0.0)

    def test_raio_paralelo_sem_nan(self):
        value = rot.signed_angle((5.0, 5.0), (5.0, 5.0), previous=42.0)
        self.assertEqual(value, 42.0)
        self.assertFalse(math.isnan(rot.signed_angle((0, 0), (1e-12, 0), previous=0.0)))

    def test_snap(self):
        self.assertEqual(rot.snap(37.0), 30.0)
        self.assertEqual(rot.snap(38.0), 45.0)
        self.assertEqual(rot.snap(37.26, fine=True), 37.3)


class CoordinatesTest(unittest.TestCase):
    def test_relativa_e_absoluta_sem_salto(self):
        b_rot = rot.axis_angle(rot.AXES['Z'], 90.0)
        world_a, world_b = (1.0, 3.0, 0.5), (1.0, 1.0, 0.0)
        r = rot.relative(world_a, world_b, rot.conjugate(b_rot))
        self.assertTrue(close(rot.add(rot.rotate_vector(b_rot, r), world_b), world_a))   # volta ao mesmo pA

    def test_cruzar_o_centro_da_base_nao_troca_a_ancora(self):
        anchor = rot.local_point(BOX, 'C000')
        path = []
        for z in (-2.33, 0.0, 2.33):
            path.append(rot.world_point((0.0, 0.0, z), rot.IDENTITY, anchor)[2] - z)
        self.assertEqual(len(set(round(v, 9) for v in path)), 1)


if __name__ == '__main__':
    unittest.main()
