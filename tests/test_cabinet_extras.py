"""Testes das peças extras (feature 008, T006): `caffmob_draw/cabinet_editor/extras.py`.

Caso do Promob: caixa de 800 × 550 × 2250 (X, Y, Z) com chapas de 15; frente em Y = 0 (menor Y).
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import extras as ex

BOX = ((0.0, 0.0, 0.0), (0.8, 0.55, 2.25))
T = 0.015


def size(b):
    return tuple(round(b[1][i] - b[0][i], 6) for i in range(3))


class ExtrasTest(unittest.TestCase):
    def test_desligado_nao_gera(self):
        self.assertEqual(ex.layout(BOX, T, {}), [])
        self.assertEqual(ex.layout(BOX, T, {'KICK_FRONT': {'enabled': False}}), [])

    def test_rodape_frontal_na_altura_dos_pes(self):
        parts = ex.layout(BOX, T, {'KICK_FRONT': {'enabled': True}, 'FEET': {'enabled': True, 'value': 0.15}})
        kick = next(p for p in parts if p.kind == 'KICK_FRONT')
        self.assertEqual(kick.component, 'ROD')
        self.assertEqual(size(kick.box), (0.8, T, 0.15))
        self.assertAlmostEqual(kick.box[0][1], 0.05)                # recuo de 50
        self.assertAlmostEqual(kick.box[1][2], 0.0)                 # abaixo da caixa

    def test_pes_nos_quatro_cantos(self):
        parts = ex.layout(BOX, T, {'FEET': {'enabled': True, 'value': 0.15}})
        feet = [p for p in parts if p.kind == 'FOOT']
        self.assertEqual(len(feet), 4)
        self.assertTrue(all(p.hardware == 'PE_PLASTICO' and p.component is None for p in feet))
        self.assertAlmostEqual(min(p.box[0][0] for p in feet), 0.05 - ex.FOOT_RADIUS)
        parts = ex.layout(BOX, T, {'FEET': {'enabled': True, 'value': 0.15}, 'FOOT_2': {'enabled': False}})
        self.assertEqual(len([p for p in parts if p.kind == 'FOOT']), 3)

    def test_fechamento_e_vistas(self):
        parts = ex.layout(BOX, T, {'CLOSURE': {'enabled': True, 'value': 0.05},
                                   'VIEW_LEFT': {'enabled': True, 'value': 0.15},
                                   'VIEW_FRONT': {'enabled': True, 'value': 0.15}})
        closures = [p for p in parts if p.kind == 'CLOSURE']
        self.assertEqual(len(closures), 2)
        self.assertEqual(size(closures[0].box), (0.05, T, 2.25))
        view = next(p for p in parts if p.kind == 'VIEW_LEFT')
        self.assertEqual(view.box[1][0], 0.0)
        self.assertEqual(size(view.box), (0.15, T, 2.25))
        top = next(p for p in parts if p.kind == 'VIEW_FRONT')
        self.assertEqual(size(top.box), (0.8, T, 0.15))
        self.assertAlmostEqual(top.box[0][2], 2.25)

    def test_vista_alta_ate_o_teto(self):
        parts = ex.layout(BOX, T, {'VIEW_TALL_FRONT': {'enabled': True}}, ceiling=2.7)
        self.assertAlmostEqual(parts[0].box[1][2], 2.7)
        self.assertAlmostEqual(parts[0].box[0][2], 2.25)

    def test_base_superior_recuada(self):
        parts = ex.layout(BOX, T, {'BASE_TOP_RECESSED': {'enabled': True}})
        top = parts[0]
        self.assertEqual(top.component, 'BAS')
        self.assertAlmostEqual(top.box[0][1], 0.02)
        self.assertAlmostEqual(top.box[1][2], 2.25)
        self.assertEqual(size(top.box), (0.8 - 2 * T, 0.53, T))


class EstruturaTest(unittest.TestCase):
    """Feature 015 (T022; D-04)."""

    def test_rodizios_sao_ferragem_nos_cantos(self):
        parts = ex.layout(BOX, T, {'CASTERS': {'enabled': True}})
        casters = [p for p in parts if p.kind == 'CASTER']
        self.assertEqual(len(casters), 4)
        self.assertEqual({p.hardware for p in casters}, {'RODIZIO'})
        self.assertAlmostEqual(casters[0].box[0][2], -0.10)

    def test_com_estrutura_o_rodape_da_008_nao_gera_peca(self):
        settings = {'KICK_FRONT': {'enabled': True}, 'KICK_LEFT': {'enabled': True}}
        self.assertEqual(ex.layout(BOX, T, settings, structure=True), [])
        self.assertEqual(len(ex.layout(BOX, T, settings)), 2)

    def test_recuo_do_rodape_pelo_padrao(self):
        kick = ex.layout(BOX, T, {'KICK_FRONT': {'enabled': True}}, kick_setback=0.08)[0]
        self.assertAlmostEqual(kick.box[0][1], 0.08)


if __name__ == '__main__':
    unittest.main()
