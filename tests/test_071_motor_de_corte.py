"""071: motor de corte inspirado no OpenMob (`openmob-bom/nesting.rs`), corrigido.

- o veio da chapa corre no lado maior (2750): a lateral de 2000 mm com veio no comprimento cabe em pé;
- a faixa nunca cresce: nenhuma peça invade a faixa de cima nem sai do refilo (o motor anterior sobrepunha);
- respeitar o veio impede girar; sem ele, gira.
"""
import random
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cutting.nesting import NestingPart, optimize_nesting


def colocadas(resultado):
    return [(s, p) for s in resultado['sheets'] for sh in s['shelves'] for p in sh['parts']]


class MotorDeCorteTest(unittest.TestCase):
    def test_veio_no_lado_maior_da_chapa(self):
        r = optimize_nesting([NestingPart('lat', 'Lateral', 550, 2000, grain_direction='VERTICAL')])
        (_, p), = colocadas(r)
        self.assertEqual((r['stats']['unplaced_count'], p['width'], p['height'], p['rotated']), (0, 2000, 550, True))
        r = optimize_nesting([NestingPart('pra', 'Prateleira', 2000, 400, grain_direction='HORIZONTAL')])
        (_, p), = colocadas(r)
        self.assertEqual((p['width'], p['height'], p['rotated']), (2000, 400, False))

    def test_sem_sobreposicao_nem_fora_do_refilo(self):
        random.seed(3)
        for _ in range(200):
            partes = [NestingPart(f'p{i}', 'P', random.choice([60, 300, 600, 900, 1300, 2000]),
                                  random.choice([60, 300, 720, 1000, 1500, 2200]),
                                  grain_direction=random.choice(['NONE', 'VERTICAL', 'HORIZONTAL']))
                      for i in range(random.randint(3, 25))]
            r = optimize_nesting(partes)
            for s in r['sheets']:
                ret = [(p['x'], p['y'], p['width'], p['height']) for sh in s['shelves'] for p in sh['parts']]
                for i, a in enumerate(ret):
                    self.assertTrue(a[0] >= 10 - 1e-6 and a[1] >= 10 - 1e-6 and a[0] + a[2] <= s['width'] - 10 + 1e-6
                                    and a[1] + a[3] <= s['height'] - 10 + 1e-6, a)
                    for b in ret[i + 1:]:
                        self.assertFalse(a[0] < b[0] + b[2] - 1e-6 and b[0] < a[0] + a[2] - 1e-6
                                         and a[1] < b[1] + b[3] - 1e-6 and b[1] < a[1] + a[3] - 1e-6, (a, b))
            self.assertEqual(r['stats']['total_placed_parts'] + r['stats']['unplaced_count'], len(partes))

    def test_respeitar_o_veio_impede_girar(self):
        p = NestingPart('x', 'X', 500, 1900, grain_direction='HORIZONTAL')
        self.assertEqual(optimize_nesting([p], respect_grain=True)['stats']['unplaced_count'], 1)
        self.assertEqual(optimize_nesting([p], respect_grain=False)['stats']['unplaced_count'], 0)

    def test_uma_chapa_por_material_espessura_e_acabamento(self):
        partes = [NestingPart('a', 'A', 500, 500, material='MDF', finish='Branco'),
                  NestingPart('b', 'B', 500, 500, material='MDF', finish='Cinza'),
                  NestingPart('c', 'C', 500, 500, material='MDF', finish='Branco', thickness=18.0)]
        self.assertEqual(optimize_nesting(partes)['stats']['sheets_count'], 3)


if __name__ == '__main__':
    unittest.main()
