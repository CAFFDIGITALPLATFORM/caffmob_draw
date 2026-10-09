"""Testes da tradução de armário herdado para módulo CAFFMob (feature 012, T046; D-24, RN-13)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.legacy import convert_core as cv

Op = cv.LegacyOpening


def cab(library='FRAMELESS', kind='BASE', openings=(), shelves=0, line='', height=0.72, other_fronts=()):
    return cv.LegacyCabinet(library=library, cabinet_type=kind, width=0.8, height=height, depth=0.55, line=line,
                            openings=list(openings), shelves=shelves, other_fronts=list(other_fronts))


def loss_keys(losses):
    return {loss.key: loss.count for loss in losses}


class TranslateTest(unittest.TestCase):
    def test_tipos(self):
        self.assertEqual(cv.translate(cab(kind='BASE'))[0]['cabinet_type'], 'BASE')
        self.assertEqual(cv.translate(cab(kind='UPPER'))[0]['cabinet_type'], 'WALL')
        self.assertEqual(cv.translate(cab(kind='TALL'))[0]['cabinet_type'], 'TALL')
        fields, losses = cv.translate(cab(kind='LAP_DRAWER'))
        self.assertEqual(fields['cabinet_type'], 'BASE')
        self.assertIn(cv.TYPE_APPROX, loss_keys(losses))
        self.assertEqual(cv.translate(cab(library='CLOSETS', kind='HANGING', height=2.2))[0]['cabinet_type'], 'TALL')
        self.assertEqual(cv.translate(cab(kind='PANEL', height=0.7))[0]['cabinet_type'], 'BASE')

    def test_frentes(self):
        self.assertEqual(cv.translate(cab(openings=[Op('DOOR_LEFT')]))[0]['door_swing'], 'LEFT')
        self.assertEqual(cv.translate(cab(openings=[Op('DOOR_RIGHT')]))[0]['door_swing'], 'RIGHT')
        self.assertEqual(cv.translate(cab(openings=[Op('DOUBLE_DOORS')]))[0]['door_swing'], 'DOUBLE')
        self.assertEqual(cv.translate(cab(openings=[Op('DOOR_LEFT'), Op('DOOR_RIGHT')]))[0]['door_swing'], 'DOUBLE')
        self.assertEqual(cv.translate(cab(openings=[Op('FLIP_UP')]))[0]['door_swing'], 'FLIP')
        self.assertEqual(cv.translate(cab(openings=[Op('OPEN')]))[0]['door_swing'], 'NONE')
        self.assertEqual(cv.translate(cab())[0]['door_swing'], 'NONE')

    def test_perdas(self):
        fields, losses = cv.translate(cab(openings=[Op('DOOR_LEFT'), Op('DRAWERS', 3), Op('DRAWERS', 2), Op('PANEL')],
                                          other_fronts=['PULLOUT', 'APPLIANCE']))
        self.assertEqual(fields['door_swing'], 'LEFT')
        keys = loss_keys(losses)
        self.assertEqual(keys[cv.DRAWERS], 5)
        self.assertEqual(keys[cv.PANEL], 1)
        self.assertEqual(keys[cv.SPECIAL_FRONT], 2)
        self.assertNotIn(cv.EXTRA_DOORS, keys)
        _f, losses = cv.translate(cab(openings=[Op('DOUBLE_DOORS'), Op('DOOR_LEFT')]))
        self.assertEqual(loss_keys(losses)[cv.EXTRA_DOORS], 1)
        self.assertEqual(cv.translate(cab(openings=[Op('DOOR_LEFT')]))[1], [])

    def test_prateleiras_e_linha(self):
        fields, _losses = cv.translate(cab(openings=[Op('DOOR_LEFT', shelves=2), Op('OPEN', shelves=1)], shelves=1))
        self.assertEqual(fields['shelves'], 4)
        self.assertEqual(fields['line'], 'COZ')
        self.assertEqual(cv.translate(cab(line='BAN'))[0]['line'], 'BAN')
        self.assertEqual(cv.translate(cab(library='CLOSETS', kind='TALL'))[0]['line'], 'DOR')
        self.assertEqual(cv.translate(cab(line='XYZ'))[0]['line'], 'COZ')
        fields, _l = cv.translate(cab())
        self.assertEqual((fields['width'], fields['height'], fields['depth']), (0.8, 0.72, 0.55))
        self.assertEqual(fields['assembly'], 'LATERAL')


if __name__ == "__main__":
    unittest.main()
