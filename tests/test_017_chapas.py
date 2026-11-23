"""017 (T007; RN-02, RN-03, RF-03, RF-04): contrato de chapas e conferência das peças contra a chapa máxima.

Contrato de `armario_v2/chapas.py` (T014): `Contrato`, `PAPEIS`, `contrato_vazio()`, `padrao()`,
`apply_host_contract(comprimento_max, largura_max, espessuras, montagem, orientacao_frente, orientacao_tras)` e
`pode_gerar(contrato)`. Contrato de `armario_v2/conferencia.py` (T015): `Peca`, `Violacao`, `Decisao`,
`conferir(pecas, contrato)` e `decidir(pecas, contrato, bloquear_chapa)`. Medidas em milímetros.
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


chapas = _modulo('chapas')
conferencia = _modulo('conferencia')
PENDENTE = 'armario_v2/chapas.py (T014) ou armario_v2/conferencia.py (T015) ainda não existe'


def _peca(papel, nome, comprimento, largura, espessura=15.0):
    return conferencia.Peca(papel=papel, nome=nome, comprimento=comprimento, largura=largura, espessura=espessura)


@unittest.skipIf(chapas is None or conferencia is None, PENDENTE)
class ChapasTest(unittest.TestCase):
    def test_contrato_vazio_recusa_geracao(self):
        vazio = chapas.contrato_vazio()
        self.assertFalse(vazio.configurado)
        motivos = chapas.pode_gerar(vazio)
        self.assertTrue(motivos)
        self.assertTrue(any('contrato' in motivo.lower() for motivo in motivos))

    def test_padrao_semeado_e_injecao_do_hospedeiro(self):
        padrao = chapas.padrao()
        self.assertTrue(padrao.configurado)
        self.assertEqual((padrao.comprimento_max, padrao.largura_max), (2750.0, 1830.0))
        self.assertEqual(len(chapas.PAPEIS), 8)
        self.assertEqual(set(padrao.espessuras), set(chapas.PAPEIS))
        self.assertNotIn('espessura_folha', padrao.espessuras)       # a folha é ferragem, não chapa
        self.assertEqual(padrao.espessuras['espessura_fundo'], 6.0)
        self.assertEqual(chapas.pode_gerar(padrao), [])

        novo = chapas.apply_host_contract(3000.0, 2000.0, {'espessura_lateral': 18.0},
                                          'BASE_PASSANTE', 'DEITADA', 'EM_PE')
        self.assertTrue(novo.configurado)
        self.assertEqual((novo.comprimento_max, novo.largura_max), (3000.0, 2000.0))
        self.assertEqual(novo.espessuras['espessura_lateral'], 18.0)
        self.assertEqual(novo.espessuras['espessura_fundo'], 6.0)     # o que não veio mantém o padrão
        self.assertEqual(novo.montagem_padrao, 'BASE_PASSANTE')
        self.assertEqual(novo.orientacao_frente_padrao, 'DEITADA')
        self.assertEqual(novo.orientacao_tras_padrao, 'EM_PE')

    def test_peca_de_3000_mm_em_chapa_de_2750(self):
        contrato = chapas.padrao()
        violacoes = conferencia.conferir([_peca('LATERAL', 'Lateral', 3000.0, 560.0)], contrato)
        self.assertEqual(len(violacoes), 1)
        self.assertEqual(violacoes[0].papel, 'LATERAL')
        self.assertEqual(violacoes[0].medida, 3000.0)
        self.assertEqual(violacoes[0].limite, 2750.0)
        texto = violacoes[0].texto()
        self.assertIn('Lateral', texto)
        self.assertIn('3000', texto)
        self.assertIn('2750', texto)

    def test_maior_lado_com_maior_limite_e_menor_com_menor(self):
        contrato = chapas.padrao()
        self.assertEqual(conferencia.conferir([_peca('PORTA', 'Porta', 2750.0, 1830.0)], contrato), [])
        larga = conferencia.conferir([_peca('PORTA', 'Porta', 2600.0, 1900.0)], contrato)
        self.assertEqual(len(larga), 1)                              # 2600 ≤ 2750, mas 1900 > 1830
        self.assertEqual((larga[0].medida, larga[0].limite), (1900.0, 1830.0))
        comprida = conferencia.conferir([_peca('PRATELEIRA', 'Prateleira', 3000.0, 900.0)], contrato)
        self.assertEqual(len(comprida), 1)
        self.assertEqual((comprida[0].medida, comprida[0].limite), (3000.0, 2750.0))

    def test_bloqueio_ligado_e_desligado(self):
        contrato = chapas.padrao()
        pecas = [_peca('LATERAL', 'Lateral', 3000.0, 560.0)]
        bloqueado = conferencia.decidir(pecas, contrato, bloquear_chapa=True)
        self.assertFalse(bloqueado.gera)
        self.assertEqual(len(bloqueado.violacoes), 1)
        liberado = conferencia.decidir(pecas, contrato, bloquear_chapa=False)
        self.assertTrue(liberado.gera)
        self.assertTrue(liberado.avisos)
        self.assertTrue(any('3000' in aviso for aviso in liberado.avisos))


if __name__ == '__main__':
    unittest.main()
