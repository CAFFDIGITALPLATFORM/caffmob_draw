"""Testes unitários puros do reconhecimento de parede rebaixada (feature 021, T010; RF-11, RN-10)."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
import _bootstrap  # noqa: F401

from caffmob_draw.selection import lowered_wall_core as lwc


class _FakeObj:
    def __init__(self, name, props=None, parent=None):
        self.name = name
        self._props = dict(props or {})
        self.parent = parent

    def get(self, key, default=None):
        return self._props.get(key, default)


class TestLoweredWallClassify(unittest.TestCase):
    def test_recognizes_explicit_lowered_wall_ref(self):
        wall = _FakeObj("Wall_01", {'IS_WALL_BP': True, 'btm_wall_lowered': True})
        proxy = _FakeObj("Wall_01_Rebaixada", {'btm_is_lowered_wall': True, 'btm_lowered_wall_ref': 'Wall_01'}, parent=wall)
        objects = {"Wall_01": wall, "Wall_01_Rebaixada": proxy}
        self.assertIs(lwc.resolve_lowered_wall(proxy, objects), wall)
        self.assertTrue(lwc.is_lowered_wall_proxy(proxy))

    def test_recognizes_legacy_lowered_wall_proxy_without_new_props(self):
        wall = _FakeObj("Wall_02", {'IS_WALL_BP': True, 'btm_wall_lowered': True})
        proxy = _FakeObj("Wall_02_Rebaixada", {}, parent=wall)
        objects = {"Wall_02": wall, "Wall_02_Rebaixada": proxy}
        self.assertIs(lwc.resolve_lowered_wall(proxy, objects), wall)
        self.assertTrue(lwc.is_lowered_wall_proxy(proxy))

    def test_ignores_regular_mesh_object(self):
        cube = _FakeObj("Cube", {})
        self.assertIsNone(lwc.resolve_lowered_wall(cube, {"Cube": cube}))
        self.assertFalse(lwc.is_lowered_wall_proxy(cube))


if __name__ == "__main__":
    unittest.main()
