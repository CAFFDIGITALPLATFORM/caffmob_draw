"""017 (T011; RN-16, RN-19, RF-18, RF-19): a linha de estado em texto e a lista de peças do painel.

Contrato de `armario_v2/resumo.py` (T019): `linha_estado(spec, vao, peca, violacoes=())` e
`lista_de_pecas(pecas, contrato)`, com os itens `{'nome', 'comprimento', 'largura', 'espessura', 'fora_da_chapa'}`.
A conformidade de chapa aparece em texto além da cor, e peça de ferragem (papel vazio) fica fora da lista.
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


spec = _modulo('spec')
chapas = _modulo('chapas')
conferencia = _modulo('conferencia')
resumo = _modulo('resumo')
PENDENTE = 'armario_v2/resumo.py (T019) e as dependências spec/chapas/conferencia ainda não existem'


@unittest.skipIf(None in (spec, chapas, conferencia, resumo), PENDENTE)
class ResumoTest(unittest.TestCase):
    def test_linha_de_estado_em_texto(self):
        s = spec.Spec(largura=1000.0, altura=2000.0, profundidade=560.0)
        texto = resumo.linha_estado(s, vao='s0.b', peca='LATERAL')
        self.assertIn('1000', texto)
        self.assertIn('2000', texto)
        self.assertIn('560', texto)
        self.assertIn('Lateral passante', texto)                     # montagem por extenso, não o enum
        self.assertIn('s0.b', texto)
        self.assertIn('LATERAL', texto)
        self.assertIn('conforme', texto.lower())

        violacao = conferencia.Violacao(papel='LATERAL', nome='Lateral', medida=3000.0, limite=2750.0)
        com_violacao = resumo.linha_estado(s, vao='s0', peca='LATERAL', violacoes=[violacao])
        self.assertIn('fora da chapa', com_violacao.lower())

    def test_lista_de_pecas_com_marca_de_fora_da_chapa(self):
        contrato = chapas.padrao()
        pecas = [
            conferencia.Peca(papel='LATERAL', nome='Lateral', comprimento=3000.0, largura=560.0, espessura=15.0),
            conferencia.Peca(papel='PORTA', nome='Porta', comprimento=1000.0, largura=400.0, espessura=18.0),
            conferencia.Peca(papel='', nome='Trilho externo', comprimento=500.0, largura=40.0, espessura=0.0),
            conferencia.Peca(papel='', nome='Gaiola', comprimento=60.0, largura=60.0, espessura=20.0),
        ]
        lista = resumo.lista_de_pecas(pecas, contrato)
        self.assertEqual([item['nome'] for item in lista], ['Lateral', 'Porta'])   # ferragem fora da lista
        self.assertEqual(set(lista[0]), {'nome', 'comprimento', 'largura', 'espessura', 'fora_da_chapa'})
        self.assertEqual((lista[0]['comprimento'], lista[0]['largura'], lista[0]['espessura']),
                         (3000.0, 560.0, 15.0))
        self.assertTrue(lista[0]['fora_da_chapa'])
        self.assertFalse(lista[1]['fora_da_chapa'])


if __name__ == '__main__':
    unittest.main()
