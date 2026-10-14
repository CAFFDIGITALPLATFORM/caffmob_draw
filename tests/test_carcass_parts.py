"""Testes da caixa por estrutura (feature 015, T008): `structure.carcass_parts`.

Medidas em mm (a função não tem unidade própria). Casos de referência: requirements §7 e roadmap D-04, D-09.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import structure as st
from caffmob_draw.cabinet_editor import structures_core as sc

CAT = sc.load(sc.CATALOG)


def thick(t, back=6.0):
    return {'LEFT': t, 'RIGHT': t, 'BOTTOM': t, 'TOP': t, 'BACK': back, 'SAR': t, 'ROD': t, 'TAMP': t, 'TRA': t}


def build(sid, w, h, d, t, **kw):
    params = st.default_params()
    params.update(kw.pop('params', {}))
    return st.carcass_parts(CAT.by_id(sid), w, h, d, thick(t), params=params, **kw)


def by_role(parts):
    return {p.role: p for p in parts}


class BalcaoTest(unittest.TestCase):
    def test_inferior_tem_sarrafos_e_nao_tem_base_superior(self):
        parts, inner = build('coz_inferior_divisoria', 500, 720, 550, 15)
        roles = by_role(parts)
        self.assertEqual(set(roles), {'LEFT', 'RIGHT', 'BOTTOM', 'STRETCHER_FRONT', 'STRETCHER_BACK', 'BACK'})
        front = roles['STRETCHER_FRONT']
        self.assertEqual((front.length, front.width, front.component), (470, 100, 'SAR'))
        self.assertEqual(front.name, "Sarrafo frontal")
        self.assertEqual(roles['STRETCHER_BACK'].name, "Sarrafo traseiro")
        (ix0, _iy0, iz0), (ix1, _iy1, iz1) = inner
        self.assertEqual((ix1 - ix0, iz1 - iz0), (470, 690))
        back = roles['BACK']
        self.assertEqual((back.length, back.width, back.component), (690 + 16, 470 + 16, 'FUN_INF'))

    def test_superior_com_as_mesmas_medidas_tem_base_superior(self):
        parts, _inner = build('coz_superior_divisoria', 800, 700, 550, 15)
        roles = by_role(parts)
        self.assertIn('TOP', roles)
        self.assertNotIn('STRETCHER_FRONT', roles)
        self.assertEqual(roles['TOP'].name, "Base superior")
        self.assertEqual(roles['BACK'].component, 'FUN_SUP')

    def test_tampo_linear_marcado_na_arvore(self):
        parts, _inner = build('coz_inferior_divisoria', 500, 720, 550, 15,
                              settings={'TOP_LINEAR': {'enabled': True}})
        top = by_role(parts)['TOP_LINEAR']
        self.assertEqual((top.length, top.width, top.component), (500, 570, 'TAMP'))
        self.assertEqual(top.box[0][2], 720)                       # sobre a caixa: a altura do padrão é sem tampo
        self.assertIn('STRETCHER_FRONT', by_role(parts))           # os sarrafos continuam

    def test_desmarcar_sarrafo_frontal(self):
        parts, _inner = build('coz_inferior_divisoria', 500, 720, 550, 15,
                              settings={'STRETCHER_FRONT': {'enabled': False}})
        self.assertNotIn('STRETCHER_FRONT', by_role(parts))

    def test_marcar_base_superior_tira_os_sarrafos(self):
        parts, _inner = build('coz_inferior_divisoria', 500, 720, 550, 15, present={'TOP': True})
        roles = by_role(parts)
        self.assertIn('TOP', roles)
        self.assertNotIn('STRETCHER_FRONT', roles)
        self.assertNotIn('STRETCHER_BACK', roles)

    def test_sarrafo_traseiro_em_pe(self):
        parts, _inner = build('coz_inferior_divisoria', 500, 720, 550, 15, rear_stretcher=st.VERTICAL)
        rear = by_role(parts)['STRETCHER_BACK']
        self.assertEqual(rear.box[0][2], 620)                      # 100 de altura, em pé
        self.assertEqual(round(rear.box[1][1] - rear.box[0][1], 6), 15)
        self.assertEqual(by_role(parts)['BACK'].box[1][2], 620)    # o fundo para embaixo dele

    def test_montagem_base_passante(self):
        parts, _inner = build('coz_inferior_divisoria', 500, 720, 550, 15, assembly=st.BASE)
        roles = by_role(parts)
        self.assertEqual(roles['BOTTOM'].length, 500)
        self.assertEqual(roles['LEFT'].box[0][2], 15)
        self.assertEqual(roles['LEFT'].length, 705)


class RodapeEPisoTest(unittest.TestCase):
    def test_armario_3_vaos_com_rodape_dentro_da_altura(self):
        parts, inner = build('dor_armario', 3000, 2500, 550, 18, params={'toe_kick_height': 80})
        roles = by_role(parts)
        (_x0, _y0, iz0), (_x1, _y1, iz1) = inner
        self.assertEqual(iz1 - iz0, 2384)
        self.assertEqual(roles['LEFT'].box[1][2], 2500)            # a altura total não muda
        kick = roles['TOE_KICK']
        self.assertEqual((kick.length, kick.width, kick.component), (3000, 80, 'ROD'))
        self.assertEqual(kick.box[0][1], -550 + 50)                # recuo do padrão
        self.assertEqual(roles['BACK'].component, 'FUN_ALT')

    def test_divisoria_sobre_base_sem_base_inferior(self):
        parts, inner = build('dor_divisoria_sobre_base', 1000, 2500, 600, 18)
        self.assertNotIn('BOTTOM', by_role(parts))
        self.assertEqual(inner[0][2], 100)                         # vão começa no rodapé

    def test_ate_piso_laterais_no_chao_e_base_na_altura_do_rodape(self):
        parts, inner = build('coz_inferior_divisoria_piso', 500, 720, 550, 15)
        roles = by_role(parts)
        self.assertEqual(roles['LEFT'].box[0][2], 0)
        self.assertEqual(roles['LEFT'].length, 720)
        self.assertEqual(roles['BOTTOM'].box[0][2], 100)
        self.assertNotIn('TOE_KICK', roles)                        # só a variante "e Rod" tem o rodapé frontal
        self.assertEqual(inner[0][2], 115)

    def test_ate_piso_e_rod_rodape_entre_as_laterais(self):
        parts, _inner = build('coz_inferior_divisoria_piso_rod', 500, 720, 550, 15)
        self.assertEqual(by_role(parts)['TOE_KICK'].length, 470)

    def test_sem_lateral_esquerda_nao_reserva_espaco(self):
        parts, inner = build('dor_armario_s_lat_esq', 1000, 2500, 550, 18)
        self.assertNotIn('LEFT', by_role(parts))
        self.assertEqual(inner[0][0], -500)


class FundoTest(unittest.TestCase):
    def test_rebaixado_igual_ao_encaixado(self):
        a, _ = build('coz_inferior_divisoria', 500, 720, 550, 15, back_kind=st.ENCAIXADO)
        b, _ = build('coz_inferior_divisoria', 500, 720, 550, 15, back_kind=st.REBAIXADO)
        self.assertEqual(by_role(a)['BACK'], by_role(b)['BACK'])

    def test_pregado_nas_medidas_externas(self):
        parts, inner = build('coz_superior_divisoria', 800, 700, 350, 15, back_kind=st.PREGADO)
        roles = by_role(parts)
        self.assertEqual((roles['BACK'].length, roles['BACK'].width), (700, 800))
        self.assertEqual(roles['LEFT'].width, 344)                 # a lateral encurta a espessura do fundo
        self.assertEqual(inner[1][1], -6)

    def test_travessas(self):
        parts, _inner = build('coz_superior_divisoria', 800, 700, 350, 15, back_kind=st.TRAVESSAS)
        roles = by_role(parts)
        self.assertEqual((roles['RAIL_LOW'].length, roles['RAIL_LOW'].width, roles['RAIL_LOW'].component),
                         (770, 100, 'TRA'))
        self.assertIn('RAIL_HIGH', roles)
        self.assertEqual((roles['BACK'].length, roles['BACK'].width), (670, 770))   # sem sobra de encaixe

    def test_fundo_recuado_da_008(self):
        parts, inner = build('coz_superior_divisoria', 800, 700, 350, 15, back_setback=20)
        self.assertEqual(by_role(parts)['BACK'].box[1][1], -20)
        self.assertEqual(inner[1][1], -26)


class CortaSarTest(unittest.TestCase):
    def test_divisoria_corta_sar_divide_os_sarrafos(self):
        parts, _inner = build('coz_inferior_divisoria', 800, 720, 550, 15, stretcher_cuts=[(-7.5, 7.5)])
        fronts = sorted((p for p in parts if p.role == 'STRETCHER_FRONT'), key=lambda p: p.name)
        self.assertEqual([p.name for p in fronts], ["Sarrafo frontal 1", "Sarrafo frontal 2"])
        self.assertEqual([p.length for p in fronts], [377.5, 377.5])          # (770 − 15) / 2
        self.assertEqual(len([p for p in parts if p.role == 'STRETCHER_BACK']), 2)

    def test_corte_fora_do_sarrafo_nao_muda(self):
        parts, _inner = build('coz_inferior_divisoria', 800, 720, 550, 15, stretcher_cuts=[(500, 520)])
        self.assertEqual(by_role(parts)['STRETCHER_FRONT'].name, "Sarrafo frontal")


class NomesUnicosTest(unittest.TestCase):
    def test_nomes_unicos_em_todas_as_estruturas(self):
        for structure in CAT.structures:
            parts, _ = st.carcass_parts(structure, 1000, 2400, 550, thick(18), params=st.default_params(),
                                        back_kind=st.TRAVESSAS, settings={'TOP_LINEAR': {'enabled': True}})
            names = [p.name for p in parts]
            self.assertEqual(len(names), len(set(names)), structure.id)
            self.assertTrue(all(p.length > 0 and p.width > 0 for p in parts), structure.id)


if __name__ == '__main__':
    unittest.main()
