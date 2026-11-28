"""Conferência do registro da cota fixa (feature 080, T005; RNF-02, CA-08, CA-09)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.overlays import cota_token as ct

IDENTITY = tuple(float(r == c) for r in range(4) for c in range(4))
BOX = ((1.0, 0.0, 0.0), (1.6, 0.55, 0.7))


def _moved(matrix, index, delta):
    values = list(matrix)
    values[index] += delta
    return tuple(values)


def _token(**changes):
    ref = changes.pop('ref', ct.RefToken(ct.OBJECT, uid=22, matrix=IDENTITY, box=BOX))
    top = changes.pop('top', ct.RefToken(ct.CEILING, ceiling=2.6))
    base = dict(uid=11, matrix=IDENTITY, scope='PART', parent=0, scene=99,
                refs={'RIGHT': ref, 'TOP': top, 'BOTTOM': ct.RefToken(ct.FLOOR)})
    base.update(changes)
    return ct.CotaToken(**base)


class CompareTest(unittest.TestCase):
    def test_same_pose_accepted(self):
        for side in ('RIGHT', 'TOP', 'BOTTOM'):
            self.assertIsNone(ct.compare(_token(), _token(), side))

    def test_translation_tolerance(self):
        self.assertIsNone(ct.compare(_token(), _token(matrix=_moved(IDENTITY, 3, 0.9e-6)), 'RIGHT'))
        self.assertEqual(ct.compare(_token(), _token(matrix=_moved(IDENTITY, 3, 1.1e-6)), 'RIGHT'), ct.TARGET_CHANGED)

    def test_rotation_component(self):
        self.assertEqual(ct.compare(_token(), _token(matrix=_moved(IDENTITY, 1, 2e-6)), 'RIGHT'), ct.TARGET_CHANGED)
        self.assertIsNone(ct.compare(_token(), _token(matrix=_moved(IDENTITY, 1, 0.5e-6)), 'RIGHT'))

    def test_target_identity_scene_scope_parent(self):
        for change in ({'uid': 12}, {'scene': 100}, {'scope': 'ASSEMBLY'}, {'parent': 5}):
            self.assertEqual(ct.compare(_token(), _token(**change), 'RIGHT'), ct.TARGET_CHANGED, change)

    def test_reference_recreated_same_name(self):
        recreated = ct.RefToken(ct.OBJECT, uid=23, matrix=IDENTITY, box=BOX)
        self.assertEqual(ct.compare(_token(), _token(ref=recreated), 'RIGHT'), ct.REFERENCE_CHANGED)

    def test_reference_moved_rotated_or_resized(self):
        moved = ct.RefToken(ct.OBJECT, uid=22, matrix=_moved(IDENTITY, 3, 0.01), box=BOX)
        rotated = ct.RefToken(ct.OBJECT, uid=22, matrix=_moved(IDENTITY, 0, -0.01), box=BOX)
        resized = ct.RefToken(ct.OBJECT, uid=22, matrix=IDENTITY, box=((1.0, 0.0, 0.0), (1.7, 0.55, 0.7)))
        for ref in (moved, rotated, resized):
            self.assertEqual(ct.compare(_token(), _token(ref=ref), 'RIGHT'), ct.REFERENCE_CHANGED)

    def test_reference_gone_or_replaced_by_floor(self):
        gone = _token()
        gone = ct.CotaToken(gone.uid, gone.matrix, gone.scope, gone.parent, gone.scene, {'TOP': gone.refs['TOP']})
        self.assertEqual(ct.compare(_token(), gone, 'RIGHT'), ct.REFERENCE_CHANGED)
        self.assertEqual(ct.compare(_token(), _token(ref=ct.RefToken(ct.FLOOR)), 'RIGHT'), ct.REFERENCE_CHANGED)

    def test_ceiling_height_changed(self):
        self.assertEqual(ct.compare(_token(), _token(top=ct.RefToken(ct.CEILING, ceiling=2.7)), 'TOP'),
                         ct.CEILING_CHANGED)
        self.assertIsNone(ct.compare(_token(), _token(top=ct.RefToken(ct.CEILING, ceiling=2.7)), 'RIGHT'))

    def test_rename_only_is_not_compared(self):
        # O nome não entra no registro: renomear a referência mantém uid, matriz e caixa.
        self.assertNotIn('name', ct.RefToken.__dataclass_fields__)
        self.assertIsNone(ct.compare(_token(), _token(), 'RIGHT'))

    def test_not_checkable(self):
        self.assertEqual(ct.compare(None, _token(), 'RIGHT'), ct.NOT_CHECKABLE)
        self.assertEqual(ct.compare(_token(), None, 'RIGHT'), ct.NOT_CHECKABLE)
        self.assertEqual(ct.compare(_token(), _token(), 'LEFT'), ct.NOT_CHECKABLE)

    def test_flat(self):
        self.assertEqual(ct.flat([[1, 0, 0, 2], [0, 1, 0, 3], [0, 0, 1, 4], [0, 0, 0, 1]])[3], 2.0)


if __name__ == '__main__':
    unittest.main()
