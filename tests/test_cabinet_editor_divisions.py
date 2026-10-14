"""Testes do núcleo de divisões (feature 006, T005): `caffmob_draw/cabinet_editor/divisions.py`."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cabinet_editor import divisions as dv

T = 0.015
ROOT = {'s0': dv.Box((0.0, 0.0, 0.0), (0.768, 0.540, 0.690))}


def close(test, a, b):
    for x, y in zip(a, b):
        test.assertAlmostEqual(x, y, places=6)


class DivisionsTest(unittest.TestCase):
    def test_vertical_no_meio_com_recuo_na_frente(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T, use_front=True, front=0.02)
        d = divs[0]
        self.assertAlmostEqual(d.offset, (0.768 - T) / 2.0)
        leaves, cuts, orphans = dv.resolve(ROOT, divs)
        self.assertEqual(sorted(leaves), ['s0.a', 's0.b'])
        self.assertEqual(orphans, [])
        plate = dv.place(cuts[d.uid][1], d)
        close(self, plate.lo, (d.offset, 0.02, 0.0))
        close(self, plate.hi, (d.offset + T, 0.540, 0.690))
        self.assertAlmostEqual(leaves['s0.a'].size(0) + leaves['s0.b'].size(0) + T, 0.768)

    def test_horizontal_sem_recuo(self):
        divs = dv.add(ROOT, [], 's0', dv.HORIZONTAL, T)
        _leaves, cuts, _o = dv.resolve(ROOT, divs)
        plate = dv.place(cuts[divs[0].uid][1], divs[0])
        self.assertAlmostEqual(plate.size(0), 0.768)
        self.assertAlmostEqual(plate.size(1), 0.540)
        self.assertAlmostEqual(plate.lo[2], (0.690 - T) / 2.0)

    def test_recuos_diferentes(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T, use_front=True, front=0.02, use_back=True, back=0.01)
        _l, cuts, _o = dv.resolve(ROOT, divs)
        plate = dv.place(cuts[divs[0].uid][1], divs[0])
        self.assertAlmostEqual(plate.size(1), 0.510)
        self.assertAlmostEqual(plate.lo[1], 0.02)
        self.assertAlmostEqual(plate.hi[1], 0.530)

    def test_horizontal_so_no_subvao_esquerdo(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        divs = dv.update(divs, divs[0].uid, offset=0.400)
        divs = dv.add(ROOT, divs, 's0.a', dv.HORIZONTAL, T)
        leaves, cuts, _o = dv.resolve(ROOT, divs)
        self.assertEqual(sorted(leaves), ['s0.a.a', 's0.a.b', 's0.b'])
        plate = dv.place(cuts[divs[1].uid][1], divs[1])
        close(self, (plate.lo[0], plate.hi[0]), (0.0, 0.400))
        self.assertAlmostEqual(leaves['s0.b'].size(2), 0.690)       # o direito não muda
        tokens = dv.space_tokens('s0.a.b', divs)
        self.assertEqual(tokens, [('ROOT', 1), ('LEFT',), ('TOP',)])

    def test_vao_ja_cortado_nao_aceita_divisao(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        with self.assertRaises(ValueError):
            dv.add(ROOT, divs, 's0', dv.VERTICAL, T)

    def test_div_001_e_002(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        uid = divs[0].uid
        self.assertEqual(dv.validate(ROOT, divs), [])
        bad = dv.update(divs, uid, offset=0.020)
        msgs = dv.validate(ROOT, bad)
        self.assertEqual([m.code for m in msgs], ['DIV-001'])
        self.assertTrue(msgs[0].blocks)
        self.assertEqual(msgs[0].range, "50 mm – 703 mm")
        deep = dv.update(divs, uid, use_front=True, front=0.30, use_back=True, back=0.20)
        self.assertEqual([m.code for m in dv.validate(ROOT, deep)], ['DIV-002'])

    def test_orfa_quando_o_espaco_raiz_some(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        msgs = dv.validate({'s1': ROOT['s0']}, divs)
        self.assertEqual([m.code for m in msgs], ['DIV-003'])

    def test_reflow_preserva_a_posicao_da_face_esquerda(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        divs = dv.update(divs, divs[0].uid, offset=0.400)
        wider = {'s0': dv.Box((0.0, 0.0, 0.0), (0.968, 0.540, 0.690))}
        leaves, cuts, _o = dv.resolve(wider, divs)
        self.assertAlmostEqual(cuts[divs[0].uid][1].lo[0], 0.400)
        self.assertAlmostEqual(leaves['s0.b'].size(0), 0.968 - 0.400 - T)

    def test_remover_leva_as_de_dentro(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        divs = dv.add(ROOT, divs, 's0.a', dv.HORIZONTAL, T)
        divs = dv.add(ROOT, divs, 's0.b', dv.HORIZONTAL, T)
        rest, removed = dv.remove(divs, divs[0].uid)
        self.assertEqual(rest, [])
        self.assertEqual(len(removed), 3)
        rest, removed = dv.remove(divs, divs[1].uid)
        self.assertEqual(len(rest), 2)

    def test_clique_escolhe_o_menor_subvao(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        leaves, _c, _o = dv.resolve(ROOT, divs)
        self.assertEqual(dv.space_at(leaves, 0.1, 0.3), 's0.a')
        self.assertEqual(dv.space_at(leaves, 0.7, 0.3), 's0.b')
        self.assertIsNone(dv.space_at(leaves, 2.0, 0.3))

    def test_dicionario_ida_e_volta(self):
        d = dv.add(ROOT, [], 's0', dv.HORIZONTAL, T, use_back=True, back=0.01)[0]
        self.assertEqual(dv.from_dict(dv.to_dict(d)), d)

    # Feature 008 (T010, T053) ---------------------------------------------------------------------------------
    def test_insercao_multipla(self):
        divs = dv.add_many(ROOT, [], 's0', dv.VERTICAL, 3, T)
        leaves, _c, _o = dv.resolve(ROOT, divs)
        self.assertEqual(len(leaves), 4)
        for box in leaves.values():
            self.assertAlmostEqual(box.size(0), (0.768 - 3 * T) / 4)
        many = dv.add_many(ROOT, [], 's0', dv.VERTICAL, 10, 0.07)
        self.assertIn('DIV-001', [m.code for m in dv.validate(ROOT, many)])

    def test_distanciador_ocupa_sem_dividir(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, 0.030, kind=dv.SPACER)
        leaves, cuts, _o = dv.resolve(ROOT, divs)
        self.assertEqual(sorted(leaves), ['s0'])
        self.assertAlmostEqual(leaves['s0'].size(0), 0.738)
        self.assertAlmostEqual(cuts[divs[0].uid][1].lo[0], 0.0)

    def test_distanciador_segue_a_divisoria(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        first = divs[0]
        divs = dv.add(ROOT, divs, 's0.b', dv.VERTICAL, T, kind=dv.SPACER, follow=first.uid)
        moved = dv.update(divs, first.uid, offset=0.200)
        _l, cuts, _o = dv.resolve(ROOT, moved)
        self.assertAlmostEqual(cuts[divs[1].uid][1].lo[0], 0.200 + T)

    def test_sem_divisoria_junta(self):
        divs = dv.add(ROOT, [], 's0', dv.VERTICAL, T)
        rest, removed = dv.remove_in_space(divs, 's0.a')
        self.assertEqual(rest, [])
        self.assertEqual(removed, [divs[0].uid])
        self.assertEqual(dv.remove_in_space(divs, 's0'), (divs, []))

    def test_movel_igual_a_fixa(self):
        fixed = dv.add(ROOT, [], 's0', dv.HORIZONTAL, T, uid="x")
        movable = dv.add(ROOT, [], 's0', dv.HORIZONTAL, T, uid="x", kind=dv.MOVABLE)
        self.assertEqual(dv.resolve(ROOT, fixed)[1], dv.resolve(ROOT, movable)[1])


class DivisoesSemPecaTest(unittest.TestCase):
    """Feature 015 (T024; RN-15): Invisível e Somente Divisão dividem sem chapa; variantes do catálogo."""

    ROOT = {'s0': dv.Box((0.0, 0.0, 0.0), (0.964, 0.5, 2.0))}

    def test_invisivel_divide_com_espessura_zero(self):
        divs = dv.add(self.ROOT, [], 's0', dv.HORIZONTAL, 0.018, kind=dv.INVISIBLE)
        self.assertEqual(divs[0].thickness, 0.0)
        leaves, _cuts, _orphans = dv.resolve(self.ROOT, divs)
        self.assertEqual(sorted(leaves), ['s0.a', 's0.b'])
        self.assertAlmostEqual(leaves['s0.a'].size(2) + leaves['s0.b'].size(2), 2.0)
        self.assertFalse(dv.makes_part(divs[0]))

    def test_somente_divisao_e_aramada_nao_viram_peca(self):
        only = dv.Division("a", 's0', dv.HORIZONTAL, 0.5, 0.0, kind=dv.DIVISION_ONLY)
        wire = dv.Division("b", 's0', dv.HORIZONTAL, 0.5, 0.018, variant=dv.ARAMADA)
        fixed = dv.Division("c", 's0', dv.HORIZONTAL, 0.5, 0.018, variant=dv.CORREDICA)
        self.assertEqual([dv.makes_part(d) for d in (only, wire, fixed)], [False, False, True])

    def test_corta_sar_da_a_faixa_da_chapa(self):
        divs = dv.add(self.ROOT, [], 's0', dv.VERTICAL, 0.018, variant=dv.CORTA_SAR)
        _leaves, cuts, _orphans = dv.resolve(self.ROOT, divs)
        (a, b), = dv.stretcher_cuts(cuts, divs)
        self.assertAlmostEqual(b - a, 0.018)
        self.assertAlmostEqual(a, (0.964 - 0.018) / 2)


if __name__ == '__main__':
    unittest.main()
