"""Testes do primeiro contato do conjunto móvel (feature 066, T007): `rules.first_contact`.

RF-005 (corpo efetivo, sem autocolisão) e RN-04 (contato não é colisão; pares excluídos continuam fora).
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.collision import obb, rules

AXES = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def item(name, lo, hi, **kw):
    return rules.Item(name, obb.from_box((0.0, 0.0, 0.0), AXES, lo, hi), **kw)


PAREDE = item('Parede', (2.0, -2.0, 0.0), (2.15, 2.0, 2.6), kind=rules.WALL)
CORPO = item('Balcão', (0.0, -0.3, 0.0), (0.6, 0.3, 0.8), root='Balcão')
PUXADOR = item('Puxador', (0.6, -0.05, 0.4), (0.64, 0.05, 0.42), root='Balcão')     # saliente 40 mm à direita
PRATELEIRA = item('Prateleira', (0.02, -0.28, 0.4), (0.58, 0.28, 0.42), root='Balcão')


class FirstContactTest(unittest.TestCase):
    def test_para_na_parede(self):
        hit = rules.first_contact([CORPO], (3.0, 0.0, 0.0), [PAREDE])
        self.assertIsNotNone(hit)
        self.assertEqual(hit.obstacle.name, 'Parede')
        self.assertAlmostEqual(hit.t * 3.0, 1.4, places=9)
        self.assertAlmostEqual(hit.normal[0], -1.0, places=9)

    def test_puxador_saliente_toca_primeiro(self):
        hit = rules.first_contact([CORPO, PUXADOR, PRATELEIRA], (3.0, 0.0, 0.0), [PAREDE])
        self.assertEqual(hit.mover.name, 'Puxador')
        self.assertAlmostEqual(hit.t * 3.0, 1.36, places=9)

    def test_pecas_da_mesma_raiz_nao_se_bloqueiam(self):
        # A prateleira está dentro do corpo; mesmo como "obstáculo" da mesma raiz, não conta.
        self.assertIsNone(rules.first_contact([CORPO], (0.0, 0.0, 0.5), [PRATELEIRA, PUXADOR]))

    def test_par_ligado_nao_bloqueia(self):
        porta = item('Porta', (1.0, -0.5, 0.0), (1.8, 0.5, 2.1), linked=frozenset({'Parede'}))
        self.assertIsNone(rules.first_contact([porta], (1.0, 0.0, 0.0), [PAREDE]))
        agregado = item('Nicho', (0.1, -0.1, 0.1), (0.2, 0.1, 0.2), linked=frozenset({'Balcão'}))
        self.assertIsNone(rules.first_contact([agregado], (0.5, 0.0, 0.0), [CORPO]))

    def test_colisao_desativada_nao_bloqueia(self):
        livre = item('Livre', (0.0, -0.3, 0.0), (0.6, 0.3, 0.8), override='OFF')
        self.assertIsNone(rules.first_contact([livre], (3.0, 0.0, 0.0), [PAREDE]))

    def test_estatico_contra_estatico_nao_conta(self):
        coluna = item('Coluna', (0.0, 0.0, 0.0), (0.3, 0.3, 2.6), kind=rules.OBSTACLE)
        self.assertIsNone(rules.first_contact([coluna], (3.0, 0.0, 0.0), [PAREDE]))

    def test_menor_t_entre_varios_obstaculos(self):
        cubo = item('Cubo', (1.0, -0.2, 0.0), (1.2, 0.2, 0.3))
        hit = rules.first_contact([CORPO], (3.0, 0.0, 0.0), [PAREDE, cubo])
        self.assertEqual(hit.obstacle.name, 'Cubo')
        self.assertAlmostEqual(hit.t * 3.0, 0.4, places=9)

    def test_obstaculo_fora_do_caminho_e_ignorado(self):
        alto = item('Aéreo', (1.0, -0.3, 1.5), (1.6, 0.3, 2.2))
        self.assertIsNone(rules.first_contact([CORPO], (1.0, 0.0, 0.0), [alto]))

    def test_ja_penetrado_nao_prende(self):
        # Interpenetração existente não bloqueia: dá para sair dela (fontes, 3.3 item 10).
        dentro = item('Dentro', (1.9, -0.3, 0.0), (2.5, 0.3, 0.8))
        self.assertIsNone(rules.first_contact([dentro], (-1.0, 0.0, 0.0), [PAREDE]))

    def test_refino_pode_liberar_ou_adiantar(self):
        # O refino pela malha (vão de porta) decide o par: None libera, um t menor adianta a parada.
        self.assertIsNone(rules.first_contact([CORPO], (3.0, 0.0, 0.0), [PAREDE], refine=lambda m, o, s: None))
        hit = rules.first_contact([CORPO], (3.0, 0.0, 0.0), [PAREDE], refine=lambda m, o, s: 0.1)
        self.assertAlmostEqual(hit.t, 0.1)
        self.assertIsNone(hit.normal)                     # parada refinada pela malha não desliza

    def test_refino_avalia_vao_mesmo_dentro_da_caixa(self):
        dentro = item('Dentro do vão', (1.9, -0.3, 0.0), (2.5, 0.3, 0.8))
        calls = []

        def refine(mover, obstacle, hit):
            calls.append(hit)
            return 0.25

        hit = rules.first_contact([dentro], (1.0, 0.0, 0.0), [PAREDE], refine=refine)
        self.assertTrue(calls)
        self.assertAlmostEqual(hit.t, 0.25)

    def test_sem_movimento_sem_contato(self):
        self.assertIsNone(rules.first_contact([CORPO], (0.0, 0.0, 0.0), [PAREDE]))


if __name__ == "__main__":
    unittest.main()
