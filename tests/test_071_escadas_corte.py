"""071, onda B (T015; RN-08, D-26, D-27): a escada no plano de corte e o corrimão nas ferragens."""
import json
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.cutting import hardware
from caffmob_draw.stairs import core, scene


class Raiz(dict):
    """Imita o objeto do Blender só no que `stairs.scene` lê."""
    def __init__(self, nome, props, pai=None):
        super().__init__(props)
        self.name, self.parent, self.hide_viewport = nome, pai, False

    def hide_get(self):
        return False


class CorteTest(unittest.TestCase):
    def setUp(self):
        self.e = core.Escada()
        self.e.x, self.e.y = core.planta_confortavel(self.e)

    def test_registros_da_reta(self):
        pecas, _ = core.pecas(self.e)
        regs = core.registros(pecas)
        papeis = [r['papel'] for r in regs]
        self.assertEqual((papeis.count('degrau'), papeis.count('espelho'), papeis.count('lateral')), (15, 15, 30))
        degrau = next(r for r in regs if r['papel'] == 'degrau')
        self.assertEqual((degrau['espessura'], degrau['comprimento']), (40, 840))   # 900 − 2 laterais de 30
        self.assertTrue(all(r['comprimento'] >= r['largura'] >= r['espessura'] for r in regs))
        self.assertEqual({r['material'] for r in regs if r['papel'] == 'degrau'}, {'frente'})

    def test_corrimao_em_metros(self):
        _, percurso = core.pecas(self.e)
        linhas = hardware.handrail_rows([('esc-1', percurso), ('esc-2', 0.0)])
        self.assertEqual(len(linhas), 1)
        self.assertEqual((linhas[0]['code'], linhas[0]['module_uid'], linhas[0]['quantity']), ('CORRIMAO', 'esc-1', 1))
        self.assertAlmostEqual(linhas[0]['length_m'], round(percurso / 1000, 2))
        self.assertIn(f"{percurso / 1000:.2f} m", linhas[0]['name'])

    def test_leitura_da_cena(self):
        raiz = Raiz('Escada', {scene.ROOT_PROP: json.dumps(self.e.para_dict()), scene.UID_PROP: 'esc-1',
                               scene.HANDRAIL_PROP: 4321.0})
        degrau = Raiz('Degrau 1', {scene.PART_PROP: '{}'}, pai=raiz)
        self.assertIs(scene.root_of(degrau), raiz)
        self.assertEqual(scene.spec(raiz), self.e.normalizada())
        self.assertEqual((scene.uid(raiz), scene.handrail_mm(raiz), scene.visible(raiz)), ('esc-1', 4321.0, True))
        self.assertEqual(scene.spec(Raiz('quebrada', {scene.ROOT_PROP: 'x'})), core.Escada().normalizada())


if __name__ == '__main__':
    unittest.main()
