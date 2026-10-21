"""T027/T062: medidas, juntas, faixa e grade no plano, fora do Blender."""
import _bootstrap  # noqa: F401
from dataclasses import replace
import math
import unittest
from caffmob_draw.cladding.core import Params, area, layout, rotate, rotation, rectangle_clip


WALL = ((0, 0), (5410, 0), (5410, 2600), (0, 2600))


class LayoutTest(unittest.TestCase):
    def test_junta_e_minimo_distintos(self):
        self.assertTrue(layout(WALL, Params(joint_mm=3)))
        with self.assertRaises(ValueError):
            layout(WALL, Params(kind='SLATS', joint_mm=17))
        self.assertTrue(layout(WALL, Params(kind='SLATS', joint_mm=18)))

    def test_faixa_nao_arredonda(self):
        for side in ('START', 'END'):
            pieces = layout(WALL, Params(band='PARTIAL', band_from=side, band_mm=1600))
            xs = [x for p in pieces for x, _y in p.polygon]
            self.assertAlmostEqual(max(xs) - min(xs), 1600)
            self.assertAlmostEqual(min(xs), 0 if side == 'START' else 3810)

    def test_chapa_e_sem_sobreposicao(self):
        for kind in ('BOARDS', 'SLATS', 'PANEL', 'PLATES'):
            p = Params(kind=kind, joint_mm=18 if kind == 'SLATS' else 3)
            pieces = layout(WALL, p)
            self.assertEqual(len({p.key for p in pieces}), len(pieces))
            boxes = []
            for piece in pieces:
                xs, ys = zip(*piece.polygon)
                self.assertLessEqual(max(xs) - min(xs), 2730.000001)
                self.assertLessEqual(max(ys) - min(ys), 1810.000001)
                box = min(xs), min(ys), max(xs), max(ys)
                for other in boxes:
                    overlap = max(0, min(box[2], other[2]) - max(box[0], other[0])) * \
                        max(0, min(box[3], other[3]) - max(box[1], other[1]))
                    self.assertLess(overlap, 1e-5)
                boxes.append(box)

    def test_inclinacao_e_limite_no_plano(self):
        outline = ((0, 0), (5410, 0), (5410, 2100), (0, 2600))
        for orientation in ('HORIZONTAL', 'VERTICAL', 'ANGLED'):
            p = Params(orientation=orientation, angle=32)
            for piece in layout(outline, p):
                xy = rotate(piece.polygon, -rotation(p))
                xs, ys = zip(*xy)
                self.assertLessEqual(max(xs) - min(xs), 2730.00001)
                self.assertLessEqual(max(ys) - min(ys), 1810.00001)
                for x, y in piece.polygon:
                    self.assertGreaterEqual(y, -1e-7)
                    self.assertLessEqual(y, 2600 - 500 * x / 5410 + 1e-7)

    def test_area_sem_junta_cobre_exatamente(self):
        p = Params(kind='PANEL', joint_mm=0)
        self.assertAlmostEqual(sum(area(x.polygon) for x in layout(WALL, p)), 5410 * 2600)

    def test_chave_nao_depende_da_ordem_do_contorno(self):
        self.assertEqual({p.key for p in layout(WALL)}, {p.key for p in layout(WALL[1:] + WALL[:1])})

    def test_fundo_separado_e_modulado(self):
        pieces = layout(WALL, Params(kind='SLATS', joint_mm=18, backing=True))
        self.assertTrue(any(p.role == 'BACKING' for p in pieces))
        self.assertTrue(any(p.role == 'FACE' for p in pieces))
        self.assertEqual(len(pieces), len({p.key for p in pieces}))

    def test_entrada_invalida(self):
        for field, value in [('width_mm', 0), ('joint_mm', -1), ('angle', math.nan), ('thickness_mm', -1)]:
            with self.assertRaises(ValueError):
                layout(WALL, replace(Params(), **{field: value}))
        with self.assertRaises(ValueError):
            layout(())

    def test_recorte_tangente_nao_cria_fragmento(self):
        self.assertFalse(rectangle_clip(WALL, (5410, 0, 6000, 2600)))
