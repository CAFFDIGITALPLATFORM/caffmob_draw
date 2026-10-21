"""Testes da identidade estável (feature 066, T009): `caffmob_draw/stable_id.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw import stable_id as sid


class Holder:
    def __init__(self, uid=""):
        self.uid = uid


class StableIdTest(unittest.TestCase):
    def test_formato(self):
        uid = sid.new_uid()
        self.assertTrue(sid.is_uid(uid))
        self.assertFalse(sid.is_uid("Porta.001"))
        self.assertFalse(sid.is_uid(""))
        self.assertEqual(sid.short(uid), uid[:8])

    def test_ensure_grava_so_quando_falta(self):
        holder = Holder()
        uid = sid.ensure_uid(holder)
        self.assertTrue(sid.is_uid(uid))
        self.assertEqual(sid.ensure_uid(holder), uid)
        self.assertNotEqual(sid.ensure_uid(Holder("Porta")), "Porta")

    def test_duplicata_renovada_e_dono_estavel(self):
        uid = sid.new_uid()
        original, copy, other = Holder(uid), Holder(uid), Holder(sid.new_uid())
        other_uid = other.uid
        renewed = sid.renew_duplicates([(7, copy), (3, original), (5, other)])
        self.assertEqual(original.uid, uid)
        self.assertEqual(other.uid, other_uid)
        self.assertNotEqual(copy.uid, uid)
        self.assertEqual(renewed, [copy])

    def test_sem_uid_recebe_um(self):
        holder = Holder()
        self.assertEqual(sid.renew_duplicates([(1, holder)]), [holder])
        self.assertTrue(sid.is_uid(holder.uid))

    def test_remap_sem_colisao_com_a_origem(self):
        olds = [sid.new_uid() for _ in range(5)]
        first, second = sid.remap(olds + [olds[0], ""]), sid.remap(olds)
        self.assertEqual(set(first), set(olds))
        self.assertFalse(set(first.values()) & set(olds))
        self.assertFalse(set(first.values()) & set(second.values()))


if __name__ == "__main__":
    unittest.main()
