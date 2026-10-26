"""071, onda B (T014; RN-07, D-20): núcleo da escada, com os testes do `stairs.rs` do OpenMob."""
import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.stairs import core


def contar(pecas, nome):
    return sum(1 for p in pecas if p['nome'].startswith(nome))


class RetaTest(unittest.TestCase):
    def test_reta_segue_espelho_confortavel(self):
        e = core.Escada()
        x, y = core.planta_confortavel(e)
        self.assertEqual(x, 900)
        e.x, e.y = x, y
        p = core.plano(e)
        self.assertEqual(p.espelhos, 16)
        self.assertAlmostEqual(p.espelho, 175)
        self.assertTrue(600 < p.blondel < 660 and p.confortavel, p.blondel)
        pecas, corrimao = core.pecas(e)
        self.assertEqual((contar(pecas, 'Degrau'), contar(pecas, 'Espelho'), contar(pecas, 'Lateral da escada')),
                         (15, 15, 30))
        topo = max(q['pos'][2] + q['tam'][2] for q in pecas if q['papel'] == 'degrau')
        self.assertAlmostEqual(topo, 2800 - 175)          # o último degrau fica um espelho abaixo do piso de cima
        self.assertGreater(corrimao, 2800)

    def test_pecas_opcionais(self):
        e = core.Escada(espelhos=False, laterais=False, corrimao=False)
        e.x, e.y = core.planta_confortavel(e)
        pecas, corrimao = core.pecas(e)
        self.assertEqual((contar(pecas, 'Espelho'), contar(pecas, 'Lateral'), corrimao), (0, 0, 0))


class PatamarTest(unittest.TestCase):
    def test_l_e_u_tem_patamar(self):
        for tipo in ('L', 'U'):
            e = core.Escada(tipo=tipo)
            e.x, e.y = core.planta_confortavel(e)
            pecas, _ = core.pecas(e)
            self.assertEqual(contar(pecas, 'Patamar'), 1, tipo)
            self.assertEqual(contar(pecas, 'Degrau'), 14, tipo)
            for q in pecas:
                hi = [q['pos'][k] + q['tam'][k] for k in range(3)]
                self.assertTrue(min(q['pos']) >= -21 and hi[0] <= e.x + 21 and hi[1] <= e.y + 21 and hi[2] <= e.z + 21,
                                (tipo, q['nome'], q['pos'], hi))

    def test_giro_a_esquerda_espelha(self):
        direita = core.Escada(tipo='L')
        direita.x, direita.y = core.planta_confortavel(direita)
        esquerda = core.Escada(**{**direita.__dict__, 'giro': 'esquerda'})
        a, _ = core.pecas(direita)
        b, _ = core.pecas(esquerda)
        self.assertEqual(len(a), len(b))
        for p, q in zip(a, b):
            self.assertAlmostEqual(q['pos'][0], direita.x - p['pos'][0] - p['tam'][0])
            self.assertEqual((p['pos'][1:], p['tam']), (q['pos'][1:], q['tam']))
        ultimo = [q for q in b if q['papel'] == 'degrau'][-1]
        self.assertLess(ultimo['pos'][0], direita.x / 2)         # o segundo lance vai para a esquerda


class LimitesTest(unittest.TestCase):
    def test_limites_do_openmob(self):
        e = core.Escada(largura=100, degrau=500, vao=-5, z=10000, y=100, x=99999, tipo='U').normalizada()
        self.assertEqual((e.largura, e.degrau, e.vao, e.z, e.y, e.x), (500, 100, 0, 6000, 500, 6000))
        self.assertEqual(core.Escada(tipo='reta', largura=800, x=3000).normalizada().x, 800)
        self.assertEqual(core.Escada(tipo='xis', giro='cima').normalizada().tipo, 'reta')

    def test_leitura_e_conforto(self):
        e = core.Escada()
        e.x, e.y = core.planta_confortavel(e)
        _, texto = core.leitura(e)
        self.assertTrue(texto.startswith('16 espelhos de 175 mm · piso de'), texto)
        self.assertTrue(core.medidas_sao_confortaveis(e))
        e.y = 2000
        p, _ = core.leitura(e)
        self.assertFalse(p.confortavel)
        self.assertFalse(core.medidas_sao_confortaveis(e))

    def test_ida_e_volta(self):
        e = core.Escada(tipo='U', giro='esquerda', largura=1000, material_frente='m1')
        self.assertEqual(core.Escada.de_dict(e.para_dict()), e.normalizada())


if __name__ == '__main__':
    unittest.main()
