"""Capacidades por tipo (feature 067, T014; RF-002, RN-04)."""

import unittest

import _bootstrap  # noqa: F401
import _target_stubs as stubs
from caffmob_draw.target import capabilities as caps
from caffmob_draw.target import resolver as r

# Onde cada botão de "Agregados e folhas" executa (o resto fica cinza com motivo).
EXPECTED = {
    'authored_adopt': {'btm_module', 'hb_module', 'part', 'front', 'geometry', 'free'},
    'member_add': {'authored', 'member'},
    'member_remove': {'member'},
    'member_transfer': {'member'},
    'authored_leaf': {'member'},
    'authored_leaves_open': {'authored', 'member'},
    'authored_update_links': {'authored', 'member'},
    'aggregate_convert': {'geometry', 'free'},
    'leaf_convert': {'part', 'geometry', 'free'},
    'window_assemble': {'room_door', 'btm_door', 'window'},
    'group_create': set(),
    'group_dissolve': set(),
}
TYPES = ('btm_module', 'hb_module', 'authored', 'member', 'part', 'geometry', 'front', 'leaf', 'wall', 'room_door',
         'btm_door', 'window', 'cladding', 'floor', 'ceiling', 'light', 'camera', 'annotation', 'free', 'obstacle')


class CapabilitiesTest(unittest.TestCase):
    def setUp(self):
        s = stubs.scene()
        self.targets = {name: r.resolve(getattr(s, name)) for name in TYPES}

    def test_tabela_comandos_por_tipo(self):
        self.assertGreaterEqual(len(caps.AGGREGATE_COMMANDS), 11)
        self.assertEqual(set(caps.AGGREGATE_COMMANDS), set(EXPECTED))
        for command, where in EXPECTED.items():
            for name, target in self.targets.items():
                ok, reason = caps.check(command, target)
                with self.subTest(comando=command, tipo=name):
                    self.assertEqual(ok, name in where)
                    if not ok:
                        self.assertTrue(reason, "indisponível sem motivo")

    def test_member_remove_sem_membro_tem_motivo(self):
        ok, reason = caps.check('member_remove', self.targets['part'])
        self.assertFalse(ok)
        self.assertIn("membro", reason)

    def test_selecao_multipla_e_grupo(self):
        s = stubs.scene()
        multiple = r.resolve(s.part, [s.part, s.free])
        self.assertTrue(caps.check('group_create', multiple)[0])
        self.assertFalse(caps.check('member_remove', multiple)[0])
        self.assertTrue(caps.check('member_remove', r.resolve(s.part, [s.part, s.member]))[0])

    def test_cabecalho_mover_e_cotas(self):
        t = self.targets
        self.assertTrue(caps.check('select_owner', t['part'])[0])
        self.assertFalse(caps.check('select_owner', t['wall'])[0])
        for name in ('wall', 'floor', 'light', 'camera', 'annotation'):
            self.assertFalse(caps.check('move_over', t[name])[0], name)
            self.assertFalse(caps.check('cotas', t[name])[0], name)
        self.assertTrue(caps.check('cotas', t['free'])[0])

    def test_sem_alvo_e_poll(self):
        self.assertFalse(caps.check('member_remove', None)[0])

        class Op:
            message = None

            @classmethod
            def poll_message_set(cls, text):
                cls.message = text
        self.assertFalse(caps.poll(Op, 'member_remove', self.targets['wall']))
        self.assertTrue(Op.message)
        self.assertTrue(caps.poll(Op, 'member_remove', self.targets['member']))


if __name__ == '__main__':
    unittest.main()
