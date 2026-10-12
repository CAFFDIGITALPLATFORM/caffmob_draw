"""Testes das regras de colisão (feature 004, T018): `caffmob_draw/collision/rules.py` e `obb.py`."""

import math
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.collision import obb, rules

AXES = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def box(lo, hi, axes=AXES, origin=(0.0, 0.0, 0.0)):
    return obb.from_box(origin, axes, lo, hi)


def item(name, lo, hi, **kw):
    return rules.Item(name, box(lo, hi), **kw)


WALL = item('Parede', (0.0, 0.0, 0.0), (4.0, 0.15, 2.6), kind=rules.WALL)


class CollisionRulesTest(unittest.TestCase):
    def test_encostados_nao_colidem(self):
        a = item('Balcão A', (0.0, -0.55, 0.0), (0.8, 0.0, 0.72))
        b = item('Balcão B', (0.7995, -0.55, 0.0), (1.6, 0.0, 0.72))
        self.assertEqual(rules.conflicts([a, b, WALL]), [])

    def test_penetracao_de_20_mm_na_parede(self):
        a = item('Balcão', (0.0, -0.53, 0.0), (0.8, 0.02, 0.72))
        found = rules.conflicts([a, WALL])
        self.assertEqual(len(found), 1)
        c = found[0]
        self.assertEqual((c.kind, c.name_a, c.name_b), (rules.KIND_WALL, 'Balcão', 'Parede'))
        self.assertAlmostEqual(c.depth, 0.02, places=6)
        self.assertAlmostEqual(c.push[1], -0.02, places=6)

    def test_pares_excluidos(self):
        a = item('Agregado', (0.0, -0.53, 0.0), (0.8, 0.02, 0.72), linked=frozenset({'Parede'}))
        b = item('Porta', (1.0, -0.05, 0.0), (1.8, 0.2, 2.1), linked=frozenset({'Parede'}))
        c = item('Rodapé', (2.0, -0.05, 0.0), (3.0, 0.05, 0.1), override='OFF')
        d1 = item('Prateleira', (3.4, -0.6, 0.0), (3.9, -0.1, 0.02), root='Roupeiro')
        d2 = item('Lateral', (3.4, -0.6, 0.0), (3.42, -0.1, 2.0), root='Roupeiro')
        e = item('Nicho', (0.2, -0.5, 1.0), (0.4, -0.3, 1.2), linked=frozenset({'Painel'}))
        f = item('Painel', (0.3, -0.6, 0.9), (0.32, -0.2, 1.3), root='Painel')
        self.assertEqual(rules.conflicts([a, b, c, d1, d2, WALL]), [])
        self.assertEqual(rules.conflicts([e, f]), [])
        floor = item('Piso', (-1, -1, -0.1), (5, 5, 0.0), kind=rules.FLOOR)
        self.assertEqual(rules.conflicts([WALL, floor]), [])

    def test_caixa_girada(self):
        r = math.radians(45)
        axes = ((math.cos(r), math.sin(r), 0.0), (-math.sin(r), math.cos(r), 0.0), (0.0, 0.0, 1.0))
        a = rules.Item('Girado', box((-0.2, -0.2, 0.0), (0.2, 0.2, 0.5), axes, origin=(1.0, -0.2, 0.0)))
        b = item('Reto', (1.2, -0.6, 0.0), (1.8, -0.1, 0.5))
        found = rules.conflicts([a, b])
        self.assertEqual(len(found), 1)
        # Afastado: a quina do girado (a 0,283 m do centro) não alcança o reto.
        c = rules.Item('Girado', box((-0.2, -0.2, 0.0), (0.2, 0.2, 0.5), axes, origin=(0.85, -0.2, 0.0)))
        self.assertEqual(rules.conflicts([c, b]), [])

    def test_uma_ocorrencia_por_par_e_ordem_estavel(self):
        items = [
            item('B', (0.0, -0.5, 0.0), (1.0, 0.0, 0.7)),
            item('A', (0.5, -0.5, 0.0), (1.5, 0.0, 0.7)),
            item('C', (3.0, -0.53, 0.0), (3.5, 0.03, 0.7)),
            item('Teto', (-1, -1, 2.6), (5, 5, 2.7), kind=rules.CEILING),
            item('D', (2.0, -0.5, 2.0), (2.5, 0.0, 2.65)),
            WALL,
        ]
        first = rules.conflicts(items)
        again = rules.conflicts(list(reversed(items)))
        self.assertEqual(first, again)
        self.assertEqual([(c.kind, c.name_a, c.name_b) for c in first],
                         [(rules.KIND_WALL, 'C', 'Parede'), (rules.KIND_ITEM, 'A', 'B'),
                          (rules.KIND_FLOOR_CEILING, 'D', 'Teto')])

    def test_confirmacao_pela_malha_e_so_o_item(self):
        a = item('A', (0.0, -0.5, 0.0), (1.0, 0.0, 0.7))
        b = item('B', (0.5, -0.5, 0.0), (1.5, 0.0, 0.7))
        c = item('C', (0.8, -0.5, 0.0), (1.2, 0.0, 0.7))
        self.assertEqual(rules.conflicts([a, b], confirm=lambda x, y: False), [])
        only = rules.conflicts([a, b, c], only={'C'})
        self.assertEqual({(x.name_a, x.name_b) for x in only}, {('A', 'C'), ('B', 'C')})


    def test_tolerancia_de_1_mm_estavel(self):
        # BUG-20261011-SRPV (pergunta 31): 1,0 mm de sobreposição nunca conta, em qualquer posição; 1,1 mm conta.
        for edge in (0.999, 0.599, 3.7):
            a = item('A', (edge - 0.8, -0.55, 0.0), (edge, 0.0, 0.72))
            b = item('B', (edge - 0.001, -0.55, 0.0), (edge + 0.8, 0.0, 0.72))
            self.assertEqual(rules.conflicts([a, b]), [], edge)
            b = item('B', (edge - 0.0011, -0.55, 0.0), (edge + 0.8, 0.0, 0.72))
            self.assertEqual(len(rules.conflicts([a, b])), 1, edge)

if __name__ == "__main__":
    unittest.main()
