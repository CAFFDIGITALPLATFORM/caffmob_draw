"""072 (T013; D-07, D-08, D-11): ferragens por corrediça e comprimento, sem contar duas vezes."""
import unittest

import _gavetas_072  # noqa: F401
from caffmob_draw.cutting import hardware
from caffmob_draw.drawers import catalogo


class FerragensTest(unittest.TestCase):
    def test_uma_linha_por_corredica_e_comprimento(self):
        t, o = catalogo.por_id('telescopica_soft'), catalogo.por_id('oculta_soft')
        linhas = hardware.slide_rows([(t, 500, 'm1'), (t, 500, 'm1'), (t, 500, 'm1'), (o, 450, 'm1')])
        self.assertEqual([(l['code'], l['quantity']) for l in linhas],
                         [('CORREDICA_OCULTA_SOFT_450', 1), ('CORREDICA_TELESCOPICA_SOFT_500', 3)])
        self.assertEqual(linhas[1]['name'], 'Corrediça telescópica soft 500 mm (par)')

    def test_gaveta_do_construtor_fora_da_contagem_generica(self):
        class Frente(dict):
            parent = None
        nova = Frente({'hb_part_role': 'DRAWER_FRONT', 'btm_drawer': '{}'})
        antiga = Frente({'hb_part_role': 'DRAWER_FRONT'})
        self.assertFalse(hardware._is_drawer_front(nova))
        self.assertTrue(hardware._is_drawer_front(antiga))


if __name__ == '__main__':
    unittest.main()
