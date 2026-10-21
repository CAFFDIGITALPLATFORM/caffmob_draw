"""Plano dimensional: sem escala e sem mutação parcial (T020)."""
import copy
import unittest
import _bootstrap  # noqa: F401
from caffmob_draw.aggregates import rules


def member(uid, lo, hi, rule='FIXED', refs=(), **params):
    return {'uid': uid, 'box': (lo, hi), 'rule': rule, 'refs': list(refs), 'params': {'axis': 'X', **params}}


def ref(uid, face):
    return {'uid': uid, 'face': face}


class Regras(unittest.TestCase):
    def test_fixo_ancorado_e_vao_5794_7994(self):
        left = member('esquerda', (0, 0, 0), (15, 400, 2600))
        right = member('direita', (594.4, 0, 0), (609.4, 400, 2600), 'ANCHORED')
        top = member('bancada', (15, 0, 0), (594.4, 400, 15), 'FIT_BETWEEN',
                     [ref('esquerda', 'POS_X'), ref('direita', 'NEG_X')])
        hardware = member('ferragem', (580, 0, 0), (590, 20, 30), 'ANCHORED', [ref('direita', 'NEG_X')])
        source = [top, hardware, right, left]
        before = copy.deepcopy(source)
        plan = rules.solve(source, (609.4, 400, 2600), (829.4, 400, 2600))
        self.assertEqual(source, before)
        self.assertEqual(plan['esquerda'].shift, (0, 0, 0))
        self.assertAlmostEqual(plan['direita'].shift[0], 220)
        self.assertAlmostEqual(plan['bancada'].box[1][0] - plan['bancada'].box[0][0], 799.4)
        self.assertEqual(plan['bancada'].box[1][2] - plan['bancada'].box[0][2], 15)
        self.assertAlmostEqual(plan['ferragem'].shift[0], 220)
        self.assertEqual(plan['ferragem'].extension, (0, 0, 0))

    def test_distribuir_16_centros_sem_escala(self):
        members = [member('a', (0, 0, 0), (15, 15, 15)), member('b', (815, 0, 0), (830, 15, 15))]
        for i in range(16):
            members.append(member(str(i), (20 * i, 0, 0), (20 * i + 10, 10, 10), 'DISTRIBUTE',
                                  [ref('a', 'POS_X'), ref('b', 'NEG_X')], count=16, index=i))
        plan = rules.solve(members, (600, 400, 2600), (830, 400, 2600))
        self.assertEqual(plan['0'].box[0][0], 15)
        self.assertEqual(plan['15'].box[1][0], 815)
        self.assertTrue(all(plan[str(i)].extension == (0, 0, 0) for i in range(16)))

    def test_ciclo_ausente_espessura_e_vao_negativo(self):
        a = member('a', (0, 0, 0), (15, 100, 100))
        b = member('b', (10, 0, 0), (25, 100, 100))
        fitting = member('p', (15, 0, 0), (25, 100, 15), 'FIT_BETWEEN',
                         [ref('a', 'POS_X'), ref('b', 'NEG_X')])
        with self.assertRaisesRegex(ValueError, 'Vão negativo'):
            rules.solve([a, b, fitting], (600, 400, 2600), (600, 400, 2600))
        b['box'] = ((20, 0, 0), (35, 100, 100))
        with self.assertRaisesRegex(ValueError, 'Espessura inviável'):
            rules.solve([a, b, fitting], (600, 400, 2600), (600, 400, 2600))
        a['refs'] = [ref('b', 'POS_X')]
        b['refs'] = [ref('a', 'NEG_X')]
        with self.assertRaisesRegex(ValueError, 'Ciclo'):
            rules.topological([a, b])
        with self.assertRaisesRegex(ValueError, 'ausente'):
            rules.topological([a])
