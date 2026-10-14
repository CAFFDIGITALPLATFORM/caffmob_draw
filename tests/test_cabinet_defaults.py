"""Testes das medidas do armário pelo Padrão de Dimensões (feature 012, T010; D-07)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.data import dimension_schema as ds
from caffmob_draw.standards import cabinet_defaults as cd
from caffmob_draw.standards import io_promob

FIXTURE = _bootstrap.FIXTURES / "dimensionexport_me_moveis.xml"


def values_from_fixture():
    data = io_promob.to_definition_data(io_promob.read_dimensionexport(FIXTURE))
    values = {key: param.default('BR') for key, param in ds.PARAMS.items()}
    values.update(data['values'])
    return values


class DefaultsTest(unittest.TestCase):
    def setUp(self):
        self.values = values_from_fixture()

    def mm(self, key):
        return float(self.values[key]) / 1000.0

    def test_balcao_aereo_torre(self):
        base = cd.defaults(self.values, 'COZ', 'BASE')
        self.assertAlmostEqual(base.height, self.mm('COZ.external.base_height'))
        self.assertAlmostEqual(base.depth, self.mm('COZ.external.base_depth'))
        self.assertEqual(base.z, 0.0)
        wall = cd.defaults(self.values, 'COZ', 'WALL')
        self.assertAlmostEqual(wall.height, self.mm('COZ.external.upper_mid_height'))
        self.assertAlmostEqual(wall.depth, self.mm('COZ.external.upper_depth'))
        self.assertAlmostEqual(wall.z, self.mm('COZ.external.install_height_upper'))
        tall = cd.defaults(self.values, 'DOR', 'TALL')
        self.assertAlmostEqual(tall.height, self.mm('DOR.external.tall_height'))
        self.assertIsNone(base.warning)

    def test_espessura_por_papel(self):
        base = cd.defaults(self.values, 'BAN', 'BASE')
        self.assertAlmostEqual(base.thickness['LEFT'], self.mm('BAN.sheets.LAT.thickness'))
        self.assertAlmostEqual(base.thickness['BOTTOM'], self.mm('BAN.sheets.BAS.thickness'))
        self.assertAlmostEqual(base.thickness['BACK'], self.mm('BAN.sheets.FUN_INF.thickness'))
        self.assertAlmostEqual(base.carcass, base.thickness['LEFT'])
        self.assertGreater(base.width, 0.0)

    def test_sem_padrao(self):
        fallback = cd.defaults(None, 'COZ', 'BASE')
        self.assertEqual((fallback.width, fallback.height, fallback.depth), cd.FALLBACK['BASE'][:3])
        self.assertTrue(fallback.warning)
        unknown = cd.defaults(self.values, 'XYZ', 'BASE')
        self.assertTrue(unknown.warning)


class EstruturaDefaultsTest(unittest.TestCase):
    """Feature 015 (T025; D-19): largura da estrutura, altura e profundidade do padrão, parâmetros da caixa."""

    def test_inferior_largura_da_estrutura_altura_do_padrao(self):
        from caffmob_draw.cabinet_editor import structures_core as sc
        values = {'COZ.external.base_height': 720.0, 'COZ.external.base_depth': 550.0,
                  'COZ.external.stretcher_width': 80.0}
        found = cd.defaults_for_structure(values, sc.load(sc.CATALOG).by_id('coz_inferior_divisoria'),
                                          '{"INFERIOR": {"back_kind": "PREGADO"}}')
        self.assertAlmostEqual(found.base.width, 0.5)
        self.assertAlmostEqual(found.base.height, 0.72)
        self.assertAlmostEqual(found.params['stretcher_width'], 0.08)
        self.assertAlmostEqual(found.params['toe_kick_height'], 0.10)      # reserva
        self.assertEqual((found.assembly, found.back_kind, found.rear_stretcher),
                         ('LATERAL', 'PREGADO', 'HORIZONTAL'))

    def test_profundidade_fixada_pela_estrutura(self):
        from caffmob_draw.cabinet_editor import structures_core as sc
        found = cd.defaults_for_structure({}, sc.load(sc.CATALOG).by_id('dor_divisoria_sobre_base'))
        self.assertAlmostEqual(found.base.depth, 0.6)
        self.assertTrue(found.warnings)                                     # sem padrão: medidas de fábrica


if __name__ == '__main__':
    unittest.main()
