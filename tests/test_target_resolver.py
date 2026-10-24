"""Resolvedor da seleção (feature 067, T013; RF-001, RF-003, RN-04)."""

import dataclasses
import unittest

import _bootstrap  # noqa: F401
import _target_stubs as stubs
from caffmob_draw.target import resolver as r


class ResolverTest(unittest.TestCase):
    def setUp(self):
        self.s = stubs.scene()

    def check(self, obj, kind, scope, owner=None, library=None, **fields):
        target = r.resolve(obj, [obj])
        self.assertEqual((target.kind, target.scope), (kind, scope), obj.name)
        self.assertEqual(target.owner_uid, owner.session_uid if owner else 0, obj.name)
        if library is not None:
            self.assertEqual(target.library, library, obj.name)
        for name, value in fields.items():
            self.assertEqual(getattr(target, name), value, f"{obj.name}.{name}")
        return target

    def test_quinze_tipos(self):
        s = self.s
        self.check(s.btm_module, r.MODULE, r.SCOPE_ASSEMBLY, library='BTM')
        self.check(s.hb_module, r.MODULE, r.SCOPE_ASSEMBLY, library='FRAMELESS')
        self.check(s.authored, r.MODULE, r.SCOPE_ASSEMBLY, library='AUTHORED', authored_owner=True)
        self.check(s.member, r.MEMBER, r.SCOPE_PART, owner=s.authored, role='SHELF', has_member=True,
                   path=("Armário Torre", "Prateleira 2"))
        self.check(s.part, r.PART, r.SCOPE_PART, owner=s.hb_module, role='LEFT_SIDE', detail='LIBRARY')
        self.check(s.geometry, r.GEOMETRY, r.SCOPE_OBJECT, library='BTM')
        self.check(s.front, r.FRONT, r.SCOPE_PART, owner=s.hb_module, name="Porta HB")
        self.check(s.leaf, r.LEAF, r.SCOPE_LEAF, owner=s.btm_module, path=("Balcão rápido", "Folha"))
        self.check(s.wall, r.WALL, r.SCOPE_OBJECT)
        self.check(s.room_door, r.OPENING, r.SCOPE_OBJECT, detail='DOOR')
        self.check(s.btm_door, r.OPENING, r.SCOPE_OBJECT, detail='DOOR', library='BTM')   # BTM DOOR é Porta
        self.check(s.window, r.OPENING, r.SCOPE_OBJECT, detail='WINDOW')
        self.check(s.cladding, r.CLADDING, r.SCOPE_OBJECT, owner=s.wall)                 # não vira a parede
        self.check(s.floor, r.FLOOR, r.SCOPE_OBJECT)
        self.check(s.ceiling, r.CEILING, r.SCOPE_OBJECT)
        self.check(s.light, r.LIGHT, r.SCOPE_OBJECT, detail='AREA', move_uid=0)
        self.check(s.camera, r.CAMERA, r.SCOPE_OBJECT, move_uid=0)
        self.check(s.annotation, r.ANNOTATION, r.SCOPE_OBJECT)
        self.check(s.free, r.OTHER, r.SCOPE_OBJECT, move_uid=s.free.session_uid)

    def test_fallback_rotulado(self):
        target = self.check(self.s.obstacle, r.OBSTACLE, r.SCOPE_OBJECT)
        self.assertEqual(target.adapter, 'FALLBACK')
        self.assertIn(target.kind, r.KIND_LABELS)
        for kind in r.KINDS:
            self.assertIn(kind, r.KIND_LABELS)

    def test_peca_move_o_modulo_e_parede_nao_se_move(self):
        self.assertEqual(r.resolve(self.s.part).move_uid, self.s.hb_module.session_uid)
        self.assertEqual(r.resolve(self.s.wall).move_uid, 0)

    def test_selecao_multipla(self):
        s = self.s
        target = r.resolve(s.part, [s.part, s.member, s.geometry])
        self.assertEqual((target.kind, target.scope, target.count), (r.MULTIPLE, r.SCOPE_MULTIPLE, 3))
        self.assertEqual(target.selected_uids[0], s.part.session_uid)
        self.assertTrue(target.has_member)
        self.assertEqual(r.resolve(s.part, [s.part]).kind, r.PART)       # o ativo sozinho não é múltiplo

    def test_snapshot_imutavel_e_vazio(self):
        target = r.resolve(self.s.part)
        with self.assertRaises(dataclasses.FrozenInstanceError):
            target.kind = r.MODULE
        self.assertIsNone(r.resolve(None, []))
        self.assertEqual(r.resolve(None, [self.s.wall]).kind, r.WALL)


if __name__ == '__main__':
    unittest.main()
