"""017 (T009; RN-06, RN-10, RN-14, RF-13, RF-14): portas de abrir, folhas deslizantes, exclusividade e recuo.

Contrato de `armario_v2/portas.py` (T017): `Folha`, `MATERIAIS`, `ABERTURA_GRAUS = 95.0`,
`portas_de_abrir(comprimento, folhas, dobradica='ALTERNADA', espessura=15.0, material='MDF')`,
`folhas_deslizantes(comprimento, folhas, sobreposicao=30.0, material='MDF', espessura=15.0)`,
`exclusividade(porta_ativa, deslizante_ativa)` e `recuo_por_papel(deslizante_ativa, base, trilho)`. Milímetros.
"""
import importlib
import unittest

import _bootstrap  # noqa: F401


def _modulo(nome):
    """Módulo do núcleo da Fase 3, ou `None` enquanto a ação que o cria não rodou."""
    completo = f'caffmob_draw.armario_v2.{nome}'
    try:
        return importlib.import_module(completo)
    except ModuleNotFoundError as erro:
        if erro.name == completo:
            return None
        raise


portas = _modulo('portas')
PENDENTE = 'caffmob_draw/armario_v2/portas.py ainda não existe (T017)'


@unittest.skipIf(portas is None, PENDENTE)
class PortasTest(unittest.TestCase):
    def test_duas_folhas_com_dobradica_alternada(self):
        folhas = portas.portas_de_abrir(1000.0, 2, dobradica='ALTERNADA', espessura=18.0)
        self.assertEqual(len(folhas), 2)
        self.assertEqual([f.dobradica for f in folhas], ['ESQUERDA', 'DIREITA'])
        self.assertEqual([f.sentido for f in folhas], [-1.0, 1.0])   # abrem em sentidos opostos
        self.assertAlmostEqual(sum(f.largura for f in folhas), 1000.0)
        for folha in folhas:
            self.assertEqual(folha.espessura, 18.0)                  # espessura por papel
            self.assertEqual(folha.graus, portas.ABERTURA_GRAUS)
        self.assertEqual(portas.ABERTURA_GRAUS, 95.0)
        esquerda = portas.portas_de_abrir(1000.0, 2, dobradica='ESQUERDA')
        self.assertEqual([f.dobradica for f in esquerda], ['ESQUERDA', 'ESQUERDA'])

    def test_folha_deslizante_pela_formula(self):
        duas = portas.folhas_deslizantes(1000.0, 2, sobreposicao=30.0)
        self.assertEqual(len(duas), 2)
        for folha in duas:
            self.assertAlmostEqual(folha.largura, 515.0)             # (1000 + 1 × 30) / 2
        tres = portas.folhas_deslizantes(1000.0, 3, sobreposicao=30.0)
        for folha in tres:
            self.assertAlmostEqual(folha.largura, 1060.0 / 3.0)      # (1000 + 2 × 30) / 3
        quatro = portas.folhas_deslizantes(1000.0, 4, sobreposicao=30.0)
        for folha in quatro:
            self.assertAlmostEqual(folha.largura, 272.5)             # (1000 + 3 × 30) / 4
        self.assertEqual([f.sentido for f in quatro], [-1.0, 1.0, -1.0, 1.0])

    def test_exclusividade_entre_abrir_e_deslizante(self):
        self.assertTrue(portas.exclusividade(True, True))
        self.assertEqual(portas.exclusividade(True, False), [])
        self.assertEqual(portas.exclusividade(False, True), [])
        self.assertEqual(portas.exclusividade(False, False), [])

    def test_recuo_com_base_dentro_e_base_na_frente(self):
        dentro = portas.recuo_por_papel(True, 'DENTRO', 70.0)
        for papel in ('DIVISORIA', 'PRATELEIRA', 'GAVETA', 'INTERNO'):
            self.assertEqual(dentro[papel], 70.0, papel)
        for papel in ('LATERAL', 'BASE_INF', 'BASE_SUP'):
            self.assertEqual(dentro[papel], 0.0, papel)              # laterais e bases na profundidade total
        frente = portas.recuo_por_papel(True, 'FRENTE', 70.0)
        self.assertTrue(all(valor == 0.0 for valor in frente.values()))
        desligada = portas.recuo_por_papel(False, 'DENTRO', 70.0)
        self.assertTrue(all(valor == 0.0 for valor in desligada.values()))


if __name__ == '__main__':
    unittest.main()
