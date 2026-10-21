"""Contrato local 1.2.0, com compatibilidade dos módulos nativos (T018)."""
import copy
import unittest
from unittest.mock import patch

import _bootstrap  # noqa: F401
from caffmob_draw.customize import manifest, spec
from caffmob_draw.stable_id import new_uid


def authored():
    a, b, c = new_uid(), new_uid(), new_uid()
    block = {'uid': a, 'asset_version': 1, 'front_axis': '-Y', 'size_local_mm': [600, 473.2, 2600],
             'external_refs': [], 'leaves': [], 'members': [
                 {'uid': b, 'role': 'CARCASS', 'rule': 'FIXED', 'refs': [], 'params': {'axis': 'X'}},
                 {'uid': c, 'role': 'LED', 'rule': 'FIT_BETWEEN', 'refs': [b], 'params': {'axis': 'X'}}]}
    return manifest.build('Torre', 'Armários autorais', 'AUTHORED', 'Torre', spec.Spec(), authored=block)


class ManifestoAutoral(unittest.TestCase):
    def test_valido_e_leitor_antigo(self):
        data = authored()
        self.assertEqual(manifest.validate(data), [])
        self.assertEqual(manifest.loads(manifest.dumps(data))[2], [])
        data['spec'] = 7  # Estado paramétrico nativo não se aplica ao autoral.
        self.assertEqual(manifest.loads(manifest.dumps(data))[2], [])
        with patch.object(manifest, 'LIBRARIES', ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM')):
            self.assertIn('biblioteca desconhecida', ' '.join(manifest.validate(data)))

    def test_nativos_continuam_11_e_leem_10(self):
        for library in ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM'):
            data = manifest.build('Nativo', 'Geral', library, 'Raiz', spec.Spec())
            self.assertEqual(data['schema_version'], '1.1.0')
            self.assertNotIn('authored', data)
            for version in ('1.0.0', '1.1.0'):
                data['schema_version'] = version
                self.assertEqual(manifest.validate(data), [])

    def test_rejeita_referencia_ciclo_e_duplicata_com_caminho(self):
        for kind in ('ciclo', 'ausente', 'duplicata'):
            data = authored()
            members = data['authored']['members']
            if kind == 'ciclo':
                members[0]['refs'] = [members[1]['uid']]
            elif kind == 'ausente':
                members[1]['refs'] = [new_uid()]
            else:
                members[1]['uid'] = members[0]['uid']
            self.assertIn('authored.members', ' '.join(manifest.validate(data)))

    def test_rejeita_formas_invalidas(self):
        for key, value in [('size_local_mm', [0, 1, 2]), ('size_local_mm', [float('nan'), 1, 2]),
                           ('external_refs', [{}]), ('front_axis', 'Z'), ('asset_version', 0), ('members', None)]:
            data = copy.deepcopy(authored())
            data['authored'][key] = value
            self.assertTrue(manifest.validate(data), key)
        for key, value in [('role', 'OUTRO'), ('rule', 'OUTRA'), ('params', {}), ('refs', {})]:
            data = authored()
            data['authored']['members'][0][key] = value
            self.assertTrue(manifest.validate(data), key)

    def test_folha_compartilha_identidade_do_membro_e_valida_detalhes(self):
        data = authored()
        block = data['authored']
        a, b = [m['uid'] for m in block['members']]
        block['leaves'] = [{'uid': a, 'members': [a], 'construction': 'GLASS_FRAMED', 'motion': 'SWING',
                            'hinge': 'LEFT', 'sign': 'OUT', 'max_angle': 95, 'travel_mm': None,
                            'pivot_uid': b, 'rest_matrix_parent': [[int(i == j) for i in range(4)] for j in range(4)]}]
        self.assertEqual(manifest.validate(data), [])
        for key, value in [('construction', 'OUTRO'), ('motion', 'DRAWER'), ('max_angle', 0),
                           ('pivot_uid', new_uid()), ('rest_matrix_parent', []), ('members', [new_uid()]),
                           ('uid', [1])]:
            invalid = copy.deepcopy(data)
            invalid['authored']['leaves'][0][key] = value
            self.assertTrue(manifest.validate(invalid), key)
