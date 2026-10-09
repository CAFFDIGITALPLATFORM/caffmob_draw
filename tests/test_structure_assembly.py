"""Testes da montagem lateral ou base passante (feature 012, T005; D-09): `cabinet_editor/structure.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import structure as st

W, H, D = 0.8, 0.72, 0.55
T = 0.018
THICK = {'TOP': T, 'BOTTOM': T, 'BACK': 0.006, 'LEFT': T, 'RIGHT': T}


def size(box):
    lo, hi = box
    return tuple(round(hi[i] - lo[i], 6) for i in range(3))


class LayoutTest(unittest.TestCase):
    def test_lateral_igual_ao_de_hoje(self):
        default, inner_default = st.layout(W, H, D, THICK, {})
        lateral, inner = st.layout(W, H, D, THICK, {}, assembly='LATERAL')
        self.assertEqual(default, lateral)
        self.assertEqual(inner_default, inner)
        self.assertEqual(size(lateral['LEFT']), (T, D, H))                 # lateral do piso ao topo
        self.assertEqual(size(lateral['BOTTOM'])[0], round(W - 2 * T, 6))  # base entre as laterais

    def test_base_passante(self):
        boxes, inner = st.layout(W, H, D, THICK, {}, assembly='BASE')
        self.assertEqual(size(boxes['BOTTOM'])[0], W)                      # base com a largura toda
        self.assertEqual(boxes['BOTTOM'][0][0], -W / 2)
        self.assertEqual(size(boxes['LEFT']), (T, D, round(H - T, 6)))     # laterais em cima da base
        self.assertEqual(boxes['LEFT'][0][2], T)
        self.assertEqual(size(boxes['TOP'])[0], round(W - 2 * T, 6))      # tampo continua entre as laterais
        self.assertEqual(inner[0][0], -W / 2 + T)                          # vão interno igual
        self.assertEqual(inner[0][2], T)

    def test_base_passante_sem_base(self):
        states = {'BOTTOM': st.RoleState(removed=True, mode=st.EXTEND)}
        boxes, _inner = st.layout(W, H, D, THICK, states, assembly='BASE')
        self.assertNotIn('BOTTOM', boxes)
        self.assertEqual(boxes['LEFT'][0][2], 0.0)                         # sem base, a lateral desce ao piso


class CarcassLengthsTest(unittest.TestCase):
    def test_lista_de_corte(self):
        # balcão de 800 mm, chapa de 18 mm, altura 720: (comprimento, largura) em mm
        lateral = st.carcass_lengths(800.0, 720.0, 18.0, 18.0, 18.0, 'LATERAL')
        self.assertEqual(lateral['BOTTOM'], 764.0)
        self.assertEqual(lateral['LEFT'], 720.0)
        base = st.carcass_lengths(800.0, 720.0, 18.0, 18.0, 18.0, 'BASE')
        self.assertEqual(base['BOTTOM'], 800.0)
        self.assertEqual(base['LEFT'], 702.0)
        self.assertEqual(base['TOP'], 764.0)


if __name__ == "__main__":
    unittest.main()
