"""T029/T063: JSON reutilizável sem herança implícita de MDF."""
import _bootstrap  # noqa: F401
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from caffmob_draw.cladding import presets


class PresetsTest(unittest.TestCase):
    def test_empresa_roundtrip(self):
        for original in presets.COMPANY.values():
            with self.subTest(preset=original['name']), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / 'preset.json'
                presets.save(path, original)
                self.assertEqual(presets.load(path), original)

    def test_madeira_e_ceramica_sem_regra_de_mdf(self):
        for kind in ('SOLID_WOOD', 'CERAMIC'):
            value = deepcopy(presets.COMPANY['painel_horizontal'])
            value['material_kind'] = kind
            value['params'].update(thickness_mm=9, sheet_w_mm=3200, sheet_h_mm=2200, joint_mm=2, min_gap_mm=0)
            restored = presets.loads(presets.dumps(value))
            self.assertEqual(restored['params'], value['params'])

    def test_escala_fisica_persistida(self):
        value = deepcopy(presets.COMPANY['tabuas_castanhas'])
        value.update(texture_size_mm=1275.5, grain_angle=31, texture='/arquivo/local.jpg')
        self.assertEqual(presets.loads(presets.dumps(value)), value)

    def test_invalido_nao_destroi_anterior(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'preset.json'
            value = deepcopy(presets.COMPANY['ripado_mdf'])
            presets.save(path, value)
            before = path.read_bytes()
            value['params']['joint_mm'] = 17
            with self.assertRaises(ValueError):
                presets.save(path, value)
            self.assertEqual(path.read_bytes(), before)

    def test_sem_heranca_de_medida_omitida(self):
        value = deepcopy(presets.COMPANY['tabuas_castanhas'])
        del value['params']['sheet_w_mm']
        with self.assertRaises(ValueError):
            presets.loads(presets.dumps(value))

    def test_versao_desconhecida_recusada(self):
        with self.assertRaises(ValueError):
            presets.loads('{"format":"caffmob_draw.cladding-preset","version":2}')
