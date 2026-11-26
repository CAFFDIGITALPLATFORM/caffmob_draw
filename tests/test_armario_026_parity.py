"""Ensaios puros da paridade 026 (export/cutlist/vista/tema/grade/alvo de toque), sem Blender."""

import unittest
from collections import namedtuple

import _bootstrap  # noqa: F401
from caffmob_draw.armario_v2 import parity_core as pc
from caffmob_draw.library_panel import grid_core as gc
from caffmob_draw.library_panel import layout_core as lc
from caffmob_draw.library_panel import style

Spec = namedtuple('Spec', 'largura altura profundidade tipo_montagem acabamento')
ITEM = {'nome': 'Lateral Esquerda', 'papel': 'LATERAL', 'espessura': 15.0,
        'box': ((-300.0, -300.0, 0.0), (-285.0, 0.0, 1800.0))}
ITEM2 = dict(ITEM, box=((-285.0, -300.0, 0.0), (-270.0, 0.0, 1800.0)))


class ExportTest(unittest.TestCase):
    def test_payload_tem_spec_pecas_e_cutlist(self):
        spec = Spec(600.0, 1800.0, 300.0, 'LATERAL_PASSANTE', 'MADEIRADO')
        data = pc.payload(spec, [ITEM, ITEM2])
        self.assertEqual(data['schema'], 'caffmob.armario.v1')
        self.assertEqual(data['armario']['largura'], 600.0)
        self.assertEqual(data['totais']['pecas'], 2)
        self.assertEqual(len(data['cutlist']), 1)
        self.assertEqual(data['cutlist'][0]['quantidade'], 2)
        self.assertEqual(data['pecas'][0]['comprimento_mm'], 15.0)
        self.assertEqual(data['pecas'][0]['altura_mm'], 1800.0)

    def test_cutlist_separa_medidas_diferentes(self):
        outro = dict(ITEM, box=((0.0, -300.0, 0.0), (15.0, 0.0, 900.0)))
        grupos = pc.cutlist([ITEM, ITEM, outro])
        self.assertEqual(len(grupos), 2)
        self.assertEqual(sorted(g['quantidade'] for g in grupos), [1, 2])


class NormalizacaoTest(unittest.TestCase):
    def test_vista_e_tema(self):
        self.assertEqual(pc.vista_valida('LATERAL'), 'LATERAL')
        self.assertEqual(pc.vista_valida('x'), 'SPLIT')
        self.assertEqual(pc.tema_valido('DARK'), 'DARK')
        self.assertEqual(pc.alternar_tema('LIGHT'), 'DARK')
        self.assertEqual(pc.alternar_tema('DARK'), 'LIGHT')


class LibraryThemeGridTest(unittest.TestCase):
    def tearDown(self):
        style.aplicar_tema('LIGHT')

    def test_tema_dark_troca_tokens_e_volta(self):
        claro = style.SURFACE
        style.aplicar_tema('DARK')
        self.assertNotEqual(style.SURFACE, claro)
        self.assertEqual(style.TEMA, 'DARK')
        style.aplicar_tema('LIGHT')
        self.assertEqual(style.SURFACE, claro)

    def test_grade_de_blocos_2_colunas(self):
        self.assertEqual(gc.columns(900, 1.0, fixed=2), 2)
        cells = gc.visible_cells((0, 0, 900, 500), count=6, scale=1.0, scroll=0.0, fixed=2)
        self.assertEqual([i for i, _r in cells][:2], [0, 1])
        self.assertEqual(cells[2][1][0], cells[0][1][0])       # terceiro item desce para a 2ª linha

    def test_alvo_de_toque_de_44px(self):
        width = lambda text: 6.0 * len(text)  # noqa: E731
        lay = lc.max_layout((0.0, 0.0, 900.0, 600.0), 1.0, width, [('BLOCKS', 'Blocos')], "x",
                            footer=False)
        key, rect = lay.buttons[-1]
        cx, cy = rect[0] + rect[2] / 2.0, rect[1] + rect[3] / 2.0
        self.assertEqual(lc.hit_max(lay, cx, cy - 16.0, scale=1.0), key)


if __name__ == '__main__':
    unittest.main()
