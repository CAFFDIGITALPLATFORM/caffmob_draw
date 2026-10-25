"""Núcleo da fita de borda (feature 067, T028; RF-080 a RF-083)."""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.edgeband import core

T = 0.015


def stack(count=3, width=0.6, depth=0.4):
    """Chapas de 15 mm empilhadas em Z (espessura em Z)."""
    return [core.Box(f"p{i}", (0.0, 0.0, i * T), (width, depth, (i + 1) * T)) for i in range(count)]


class FacesTest(unittest.TestCase):
    def test_quatro_faces_estreitas(self):
        faces = core.narrow_faces(stack(1)[0])
        self.assertEqual(sorted(f.key for f in faces), ['p0|X+', 'p0|X-', 'p0|Y+', 'p0|Y-'])
        self.assertTrue(all(f.axis != 2 for f in faces))             # a face larga (Z) nunca é borda

    def test_chave_estavel(self):
        self.assertEqual(core.edge_key("uid", 1, -1), "uid|Y-")


class ExposedTest(unittest.TestCase):
    def test_lateral_coberta_pelo_tampo(self):
        side = core.Box("lat", (0.0, 0.0, 0.0), (T, 0.4, 0.7))
        top = core.Box("tampo", (0.0, 0.0, 0.7), (0.6, 0.4, 0.7 + T))
        keys = {f.key for f in core.exposed([side, top])}
        self.assertNotIn("lat|Z+", keys)          # o topo da lateral encosta no tampo
        self.assertIn("lat|Y-", keys)             # a frente da lateral está exposta
        self.assertIn("tampo|Y-", keys)

    def test_empilhadas_tem_as_bordas_expostas(self):
        keys = {f.key for f in core.exposed(stack())}
        self.assertEqual(len(keys), 12)


class MergeTest(unittest.TestCase):
    def test_tres_de_15_viram_45(self):
        bands = core.merge(core.exposed(stack()))
        front = [b for b in bands if b.axis == 1 and b.sign < 0]
        self.assertEqual(len(front), 1)
        length, width = front[0].size()
        self.assertAlmostEqual(width, 0.045, places=6)
        self.assertAlmostEqual(length, 0.6, places=6)
        self.assertEqual(front[0].keys, ('p0|Y-', 'p1|Y-', 'p2|Y-'))
        self.assertEqual(len(bands), 4)

    def test_tolerancia_de_01_mm(self):
        boxes = stack(2)
        shifted = core.Box("p1", (0.0, 0.00009, T), (0.6, 0.4, 2 * T))          # 0,09 mm: coplanar
        self.assertEqual(len([b for b in core.merge(core.exposed([boxes[0], shifted])) if b.axis == 1]), 2)
        far = core.Box("p1", (0.0, 0.0005, T), (0.6, 0.4, 2 * T))               # 0,5 mm: duas faixas na frente
        front = [b for b in core.merge(core.exposed([boxes[0], far])) if b.axis == 1 and b.sign < 0]
        self.assertEqual(len(front), 2)

    def test_componente_girado_no_referencial_do_dono(self):
        # O mesmo empilhamento girado 90° (espessura em X): no referencial do componente a conta é a mesma.
        boxes = [core.Box(f"p{i}", (i * T, 0.0, 0.0), ((i + 1) * T, 0.4, 0.6)) for i in range(3)]
        bands = [b for b in core.merge(core.exposed(boxes)) if b.axis == 1 and b.sign < 0]
        self.assertEqual(len(bands), 1)
        self.assertAlmostEqual(bands[0].size()[1], 0.045, places=6)


class StateTest(unittest.TestCase):
    def test_rotulos(self):
        self.assertEqual(core.label_state(['a', 'b'], []), (core.CREATE, ['a', 'b']))
        self.assertEqual(core.label_state(['a', 'b'], ['a', 'b', 'c']), (core.CHANGE, []))
        self.assertEqual(core.label_state(['a', 'b'], ['a']), (core.MIXED, ['b']))

    def test_idempotente(self):
        bands = core.merge(core.exposed(stack()))
        again = core.merge(core.exposed(stack()))
        self.assertEqual([b.uid for b in bands], [b.uid for b in again])
        self.assertEqual(core.band_uid(['b', 'a']), core.band_uid(['a', 'b']))
        band = bands[0]
        self.assertEqual(core.params_hash(band, 0.001, 0.0002), core.params_hash(band, 0.001, 0.0002))
        self.assertNotEqual(core.params_hash(band, 0.001, 0.0002), core.params_hash(band, 0.002, 0.0002))

    def test_malha_fora_da_face_e_dentro_do_retangulo(self):
        band = [b for b in core.merge(core.exposed(stack())) if b.axis == 1 and b.sign < 0][0]
        lo, hi = core.band_box(band, 0.001, 0.0002)
        self.assertAlmostEqual(hi[1], -0.0002, places=7)
        self.assertAlmostEqual(lo[1], -0.0012, places=7)
        self.assertEqual((lo[0], hi[0]), (0.0, 0.6))
        self.assertAlmostEqual(hi[2] - lo[2], 0.045, places=6)

    def test_json(self):
        self.assertEqual(core.loads(core.dumps(['a', 'b'])), ['a', 'b'])
        self.assertEqual(core.loads("lixo"), [])


if __name__ == '__main__':
    unittest.main()
