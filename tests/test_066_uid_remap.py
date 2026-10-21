"""Duas inserções têm identidades e referências independentes (T019)."""
import copy
import unittest
import _bootstrap  # noqa: F401
from caffmob_draw.customize.authored_io import remap_block
from test_066_authored_manifest import authored


class Remapeamento(unittest.TestCase):
    def test_duas_copias_e_pivo(self):
        block = authored()['authored']
        a, b = [m['uid'] for m in block['members']]
        block['leaves'] = [{'uid': a, 'members': [a], 'pivot_uid': b}]
        original = copy.deepcopy(block)
        first, mapa = remap_block(block)
        second, outro = remap_block(block)
        self.assertEqual(block, original)
        self.assertFalse(set(mapa.values()) & set(outro.values()))
        self.assertFalse(set(mapa) & set(mapa.values()))
        for result, mapping in ((first, mapa), (second, outro)):
            self.assertEqual(result['members'][1]['refs'], [mapping[a]])
            self.assertEqual(result['leaves'][0]['pivot_uid'], mapping[b])
            self.assertEqual(result['leaves'][0]['members'], [mapping[a]])
            self.assertEqual(result['leaves'][0]['uid'], mapping[a])
