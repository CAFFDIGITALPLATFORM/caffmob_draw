"""Onda 8 da 067 (T181; RF-160, RF-161, D-37): uma unidade de medida só, a do projeto."""
import re
import unittest
from pathlib import Path
from types import SimpleNamespace

import _bootstrap  # noqa: F401
from caffmob_draw.data import units

RAIZ = Path(__file__).resolve().parents[1] / 'caffmob_draw'


def cena(btm_unit, system='METRIC', length_unit='METERS', scale_length=1.0):
    return SimpleNamespace(btm_settings=SimpleNamespace(btm_unit=btm_unit),
                           unit_settings=SimpleNamespace(system=system, length_unit=length_unit,
                                                         scale_length=scale_length))


class AlinharCenaTest(unittest.TestCase):
    def test_cada_unidade_do_projeto(self):
        for btm, esperado in (('MILLIMETERS', 'MILLIMETERS'), ('CENTIMETERS', 'CENTIMETERS'), ('METERS', 'METERS')):
            c = cena(btm, length_unit='FEET', system='IMPERIAL', scale_length=0.5)
            units.alinhar_cena(c)
            self.assertEqual((c.unit_settings.system, c.unit_settings.length_unit), ('METRIC', esperado))
            self.assertEqual(c.unit_settings.scale_length, 0.5)       # a geometria não muda (RF-161)

    def test_sem_configuracao_do_addon_nao_mexe(self):
        c = SimpleNamespace(unit_settings=SimpleNamespace(system='METRIC', length_unit='METERS', scale_length=1.0))
        units.alinhar_cena(c)
        self.assertEqual(c.unit_settings.length_unit, 'METERS')

    def test_idempotente(self):
        c = cena('MILLIMETERS')
        units.alinhar_cena(c)
        units.alinhar_cena(c)
        self.assertEqual(c.unit_settings.length_unit, 'MILLIMETERS')


class FontesUnicasTest(unittest.TestCase):
    def test_callback_do_btm_unit_usa_alinhar_cena(self):
        texto = (RAIZ / 'data' / 'properties.py').read_text(encoding='utf-8')
        corpo = texto.split('def update_scene_unit', 1)[1].split('\ndef ', 1)[0]
        self.assertIn('alinhar_cena', corpo)
        self.assertNotIn("length_unit = '", corpo)

    def test_menu_de_unidades_grava_btm_unit_e_nao_tem_imperial(self):
        texto = (RAIZ / 'ui' / 'menus.py').read_text(encoding='utf-8')
        self.assertNotIn('IMPERIAL', texto)
        self.assertNotIn('"FEET"', texto)
        operador = texto.split('class HOME_BUILDER_OT_change_units', 1)[1].split('\nclass ', 1)[0]
        self.assertIn('btm_unit', operador)
        self.assertNotIn('unit_settings.length_unit =', operador)

    def test_load_post_e_montagem_do_mobi_alinham(self):
        self.assertIn('alinhar_cena', (RAIZ / '__init__.py').read_text(encoding='utf-8').split('def load_file_post', 1)[1].split('\ndef ', 1)[0])
        montagem = (RAIZ / 'mobi' / 'cena_v2.py').read_text(encoding='utf-8')
        self.assertIn('alinhar_cena', montagem)
        self.assertIsNone(re.search(r"unit_settings\.length_unit\s*=", montagem))


if __name__ == '__main__':
    unittest.main()
