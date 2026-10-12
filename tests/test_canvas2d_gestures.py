"""Testes dos gestos de navegação das telas 2D (013, T004; RF-01, RF-02, RF-10): `caffmob_draw/canvas2d/gestures.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.canvas2d import gestures as g
from caffmob_draw.canvas2d import view as v


class PinchTest(unittest.TestCase):
    def test_sentido(self):
        self.assertGreater(g.pinch_factor(40), 1.0)          # afastar os dedos aproxima
        self.assertLess(g.pinch_factor(-40), 1.0)            # juntar os dedos afasta

    def test_proporcional_ao_gesto_sem_degrau(self):
        small, big = g.pinch_factor(20), g.pinch_factor(40)
        self.assertGreater(big, small)
        for factor in (small, big):
            self.assertNotAlmostEqual(factor, 1.15, places=6)

    def test_ida_e_volta(self):
        view = v.View2D((0, 0, 800, 600), scale=100.0)
        for _ in range(7):
            view.zoom(g.pinch_factor(33), (100.0, 100.0))
        for _ in range(7):
            view.zoom(g.pinch_factor(-33), (100.0, 100.0))
        self.assertLessEqual(abs(view.scale - 100.0) / 100.0, 0.001)      # erro ≤ 0,1%

    def test_delta_zero(self):
        view = v.View2D((0, 0, 800, 600), scale=100.0, center=(1.0, 2.0))
        view.zoom(g.pinch_factor(0), (300.0, 200.0))
        self.assertEqual(view.scale, 100.0)
        self.assertEqual(view.center, (1.0, 2.0))

    def test_ancora_parada(self):
        view = v.View2D((0, 0, 800, 600), scale=100.0)
        anchor = (650.0, 120.0)
        before = view.to_world(anchor)
        view.zoom(g.pinch_factor(75), anchor)
        after = view.to_screen(before)
        self.assertLessEqual(abs(after[0] - anchor[0]), 1.0)
        self.assertLessEqual(abs(after[1] - anchor[1]), 1.0)

    def test_mesma_pinca_em_qualquer_escala(self):
        self.assertAlmostEqual(g.pinch_factor(30), g.pinch_factor(30))
        for scale in (10.0, 100.0, 5000.0):
            view = v.View2D((0, 0, 800, 600), scale=scale)
            view.zoom(g.pinch_factor(30))
            self.assertAlmostEqual(view.scale / scale, g.pinch_factor(30))


class WheelTest(unittest.TestCase):
    def test_roda(self):
        self.assertAlmostEqual(g.wheel_factor(True), 1.15)
        self.assertAlmostEqual(g.wheel_factor(False), 1 / 1.15)

    def test_roda_invertida_pela_preferencia(self):
        self.assertAlmostEqual(g.wheel_factor(True, inverted=True), 1 / 1.15)
        self.assertAlmostEqual(g.wheel_factor(False, inverted=True), 1.15)


class ZoomWindowTest(unittest.TestCase):
    def test_retangulo_pequeno_nao_muda_a_vista(self):
        view = v.View2D((0, 0, 800, 600), scale=100.0)
        self.assertIsNone(g.zoom_window_bounds(view, (100.0, 100.0), (103.0, 103.0)))
        self.assertIsNone(g.zoom_window_bounds(view, (100.0, 100.0), (300.0, 102.0)))   # lado fino demais
        self.assertIsNone(g.zoom_window_bounds(view, (100.0, 100.0), (100.0, 100.0)))   # só um clique

    def test_enquadra_centrado(self):
        view = v.View2D((0, 0, 800, 600), scale=100.0)
        p0, p1 = (500.0, 400.0), (200.0, 150.0)                # marcado em qualquer sentido
        bounds = g.zoom_window_bounds(view, p0, p1)
        self.assertIsNotNone(bounds)
        (x0, y0), (x1, y1) = bounds
        self.assertLess(x0, x1)
        self.assertLess(y0, y1)
        center_world = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        view.fit(bounds, margin=0)
        cx, cy = view.to_screen(center_world)
        self.assertLessEqual(abs(cx - 400.0), 2.0)             # centro do retângulo no centro da vista (± 2 px)
        self.assertLessEqual(abs(cy - 300.0), 2.0)
        sx0, sy0 = view.to_screen((x0, y0))
        sx1, sy1 = view.to_screen((x1, y1))
        self.assertGreaterEqual(sx0, -2.0)                     # o retângulo inteiro cabe na vista
        self.assertGreaterEqual(sy0, -2.0)
        self.assertLessEqual(sx1, 802.0)
        self.assertLessEqual(sy1, 602.0)
        self.assertTrue(abs(sx1 - sx0 - 800.0) <= 2.0 or abs(sy1 - sy0 - 600.0) <= 2.0)   # o lado que limita enche


if __name__ == "__main__":
    unittest.main()
