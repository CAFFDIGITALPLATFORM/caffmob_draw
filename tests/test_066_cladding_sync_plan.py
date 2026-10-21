"""T028: plano incremental não recebe autorização de marca manual ou de outro dono."""
import _bootstrap  # noqa: F401
import unittest
from caffmob_draw.cladding.core import boundary_signature, sync_plan


def mark(key, generated=True, owner='A'):
    return dict(owner=owner, key=key, generated=generated)


class SyncTest(unittest.TestCase):
    def test_dez_execucoes(self):
        desired = {'FACE:0:0': 'a', 'FACE:0:1': 'b'}
        existing = []
        for i in range(10):
            plan = sync_plan('A', desired, existing)
            self.assertEqual(len(plan.create), 2 if i == 0 else 0)
            self.assertFalse(plan.update or plan.remove)
            existing.extend((key, mark(key), desired[key]) for key in plan.create)
        self.assertEqual(len(existing), 2)

    def test_manual_e_outro_dono_intactos(self):
        existing = [('manual', mark('a', False), 'velho'), ('sem marca', {}, ''),
                    ('externa', mark('a', owner='B'), 'velho')]
        plan = sync_plan('A', {'a': 'novo'}, existing)
        self.assertEqual(plan.create, ('a',))
        self.assertFalse(plan.update or plan.remove)

    def test_hash_igual_nao_faz_nada(self):
        plan = sync_plan('A', {'a': 'novo'}, [('obj', mark('a'), 'velho')], 'hash', 'hash')
        self.assertFalse(plan.create or plan.update or plan.remove)

    def test_janela_mexe_so_afetados(self):
        old = [('a', mark('a'), 'intacto'), ('b', mark('b'), 'cortado'), ('c', mark('c'), 'sumiu')]
        plan = sync_plan('A', {'a': 'intacto', 'b': 'outro corte', 'd': 'novo'}, old)
        self.assertEqual(plan.update, (('b', 'b'),))
        self.assertEqual(plan.create, ('d',))
        self.assertEqual(plan.remove, ('c',))

    def test_duplicata_gerada_removida_manual_nao(self):
        old = [('a', mark('a'), 's'), ('b', mark('a'), 's'), ('c', mark('a', False), 's')]
        self.assertEqual(sync_plan('A', {'a': 's'}, old).remove, ('b',))


class BoundaryTest(unittest.TestCase):
    def test_assinatura_independe_da_triangulacao(self):
        rectangle = [((0,0),(20,0),(20,10),(0,10))]
        triangles = [((0,0),(20,0),(20,10)), ((0,0),(20,10),(0,10))]
        self.assertEqual(boundary_signature(rectangle), boundary_signature(triangles))

    def test_aresta_em_t_cancelada(self):
        rectangles = [((0,0),(10,0),(10,20),(0,20)), ((10,0),(20,0),(20,10),(10,10)),
                      ((10,10),(20,10),(20,20),(10,20))]
        self.assertEqual(boundary_signature(rectangles), boundary_signature([((0,0),(20,0),(20,20),(0,20))]))
