"""017 (T006; RN-11, RN-12): a árvore de vãos, as quatro variantes de divisória e prateleira, a matriz e duplicar.

Contrato de `armario_v2/vaos.py` (T013): `Divisao`, `Vao`, `VARIANTES_VERTICAIS`, `VARIANTES_HORIZONTAIS`,
`arvore(divisoes, spec)`, `inserir_vertical(divisoes, spec, vao, variante, posicao=None)`,
`inserir_horizontal(divisoes, spec, vao, variante, posicao=None)`, `matriz(divisoes, spec, vao, linhas, colunas,
prioridade)`, `duplicar(divisoes, uid, spec)` e `remover(divisoes, uid)`. Medidas em milímetros.
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
vaos = _modulo('vaos')
PENDENTE = 'armario_v2/vaos.py (T013) ou armario_v2/spec.py (T012) ainda não existe'


def _spec(**campos):
    """Armário de 1000 × 2000 × 560 mm: vão único de 970 × 1970 mm com as quatro chapas da caixa."""
    base = dict(largura=1000.0, altura=2000.0, profundidade=560.0,
                lateral_esq_ativa=True, lateral_dir_ativa=True,
                base_inf_ativa=True, base_sup_ativa=True)
    base.update(campos)
    return spec.Spec(**base)


@unittest.skipIf(spec is None or vaos is None, PENDENTE)
class VaosTest(unittest.TestCase):
    def test_quatro_variantes_de_divisoria_vertical(self):
        s = _spec()
        esperado = {
            'movel_s_recuo': ('MOVEL', 15.0, 0.0, 0.0),
            'movel_c_recuo': ('MOVEL', 15.0, 15.0, 0.0),
            'montante': ('FIXA', 15.0, 0.0, 0.0),
            'distanciador': ('ESPACADOR', 30.0, 0.0, 0.0),
        }
        self.assertEqual(set(vaos.VARIANTES_VERTICAIS), set(esperado))
        for variante, (tipo, espessura, recuo_tras, recuo_frente) in esperado.items():
            novas, divisao = vaos.inserir_vertical([], s, 's0', variante)
            self.assertEqual(len(novas), 1)
            self.assertEqual(divisao.eixo, 'VERTICAL')
            self.assertEqual(divisao.vao, 's0')
            self.assertEqual(divisao.posicao, 485.0)                 # meio do vão de 970 mm
            self.assertEqual((divisao.tipo, divisao.espessura, divisao.recuo_tras, divisao.recuo_frente),
                             (tipo, espessura, recuo_tras, recuo_frente), variante)

    def test_quatro_variantes_de_prateleira_horizontal(self):
        s = _spec()
        esperado = {
            'prat_s_recuo': ('MOVEL', 0.0, 0.0),
            'prat_c_recuo': ('MOVEL', 15.0, 0.0),
            'prat_fixa': ('FIXA', 0.0, 20.0),
            'prat_corredica': ('MOVEL', 0.0, 0.0),
        }
        self.assertEqual(set(vaos.VARIANTES_HORIZONTAIS), set(esperado))
        for variante, (tipo, recuo_tras, recuo_frente) in esperado.items():
            novas, divisao = vaos.inserir_horizontal([], s, 's0', variante)
            self.assertEqual(len(novas), 1)
            self.assertEqual(divisao.eixo, 'HORIZONTAL')
            self.assertEqual(divisao.posicao, 985.0)                 # meio da altura interna de 1970 mm
            self.assertEqual(divisao.espessura, 15.0)                # espessura_prateleira
            self.assertEqual((divisao.tipo, divisao.recuo_tras, divisao.recuo_frente),
                             (tipo, recuo_tras, recuo_frente), variante)

    def test_matriz_2_linhas_por_1_coluna(self):
        s = _spec()
        novas = vaos.matriz([], s, 's0', linhas=2, colunas=1, prioridade='VERTICAL')
        verticais = [d for d in novas if d.eixo == 'VERTICAL']
        horizontais = [d for d in novas if d.eixo == 'HORIZONTAL']
        self.assertEqual(len(verticais), 1)
        self.assertEqual(len(horizontais), 4)                        # duas prateleiras em cada vão resultante
        self.assertEqual(sorted({d.vao for d in horizontais}), ['s0', 's0.b'])
        for caminho in ('s0', 's0.b'):
            alturas = sorted(d.posicao for d in horizontais if d.vao == caminho)
            self.assertAlmostEqual(alturas[0], 1970.0 / 3.0, places=6)
            self.assertAlmostEqual(alturas[1], 2.0 * 1970.0 / 3.0, places=6)

    def test_prioridade_do_eixo_ordena_a_insercao(self):
        s = _spec()
        por_vertical = vaos.matriz([], s, 's0', linhas=2, colunas=2, prioridade='VERTICAL')
        por_horizontal = vaos.matriz([], s, 's0', linhas=2, colunas=2, prioridade='HORIZONTAL')
        self.assertEqual([d.eixo for d in por_vertical], ['VERTICAL'] * 2 + ['HORIZONTAL'] * 6)
        self.assertEqual([d.eixo for d in por_horizontal], ['HORIZONTAL'] * 6 + ['VERTICAL'] * 2)
        self.assertEqual(len(por_vertical), len(por_horizontal))
        self.assertEqual(sorted({d.vao for d in por_vertical if d.eixo == 'HORIZONTAL'}),
                         ['s0', 's0.b', 's0.b.b'])
        posicoes = sorted(d.posicao for d in por_vertical if d.eixo == 'VERTICAL')
        self.assertAlmostEqual(posicoes[0], 970.0 / 3.0, places=6)
        self.assertAlmostEqual(posicoes[1], 2.0 * 970.0 / 3.0, places=6)

    def test_duplicar_nasce_no_meio_do_maior_vao_livre(self):
        s = _spec()
        novas, divisao = vaos.inserir_vertical([], s, 's0', 'movel_s_recuo', posicao=900.0)
        outras, repetida, motivo = vaos.duplicar(novas, divisao.uid, s)
        self.assertEqual(motivo, '')
        self.assertIsNotNone(repetida)
        self.assertEqual(len(outras), 2)
        self.assertEqual(repetida.posicao, 450.0)                    # meio do vão livre de 900 mm

    def test_duplicar_recusado_abaixo_de_80_mm_livres(self):
        s = _spec(largura=180.0)                                     # vão interno de 150 mm
        novas, divisao = vaos.inserir_vertical([], s, 's0', 'movel_s_recuo', posicao=75.0)
        outras, repetida, motivo = vaos.duplicar(novas, divisao.uid, s)
        self.assertIsNone(repetida)
        self.assertEqual(len(outras), 1)
        self.assertIn('80', motivo)

    def test_caminho_do_vao_estavel_entre_insercoes(self):
        s = _spec()
        self.assertEqual([v.caminho for v in vaos.arvore([], s)], ['s0'])
        novas, _ = vaos.inserir_vertical([], s, 's0', 'movel_s_recuo')
        arvore = vaos.arvore(novas, s)
        self.assertEqual([v.caminho for v in arvore], ['s0', 's0.b'])
        self.assertEqual([round(v.largura, 6) for v in arvore], [485.0, 470.0])
        mais, _ = vaos.inserir_vertical(novas, s, 's0.b', 'movel_s_recuo')
        self.assertEqual([v.caminho for v in vaos.arvore(mais, s)], ['s0', 's0.b', 's0.b.b'])

    def test_divisoria_e_prateleira_no_mesmo_vao_nao_colidem(self):
        s = _spec()
        com_divisoria, _ = vaos.inserir_vertical([], s, 's0', 'movel_s_recuo')
        misto, _ = vaos.inserir_horizontal(com_divisoria, s, 's0', 'prat_fixa')
        caminhos = [v.caminho for v in vaos.arvore(misto, s)]
        self.assertEqual(len(caminhos), len(set(caminhos)))              # nenhum caminho repetido
        self.assertEqual(sorted(caminhos), ['s0', 's0.a', 's0.b'])
        larguras = {v.caminho: v.largura for v in vaos.arvore(misto, s)}
        self.assertAlmostEqual(larguras['s0'], 485.0)
        self.assertAlmostEqual(larguras['s0.a'], 485.0)
        self.assertAlmostEqual(larguras['s0.b'], 470.0)                  # a coluna da direita segue inteira

    def test_vertical_dentro_de_coluna_com_prateleiras_nao_repete_caminho(self):
        s = _spec()
        plano = vaos.matriz([], s, 's0', linhas=2, colunas=2, prioridade='VERTICAL')
        caminhos = [v.caminho for v in vaos.arvore(plano, s)]
        self.assertEqual(len(caminhos), 9)                               # 3 colunas × 3 faixas
        self.assertEqual(len(caminhos), len(set(caminhos)))
        com_divisoria, _ = vaos.inserir_vertical(plano, s, 's0.b', 'montante')
        novos = [v.caminho for v in vaos.arvore(com_divisoria, s)]
        self.assertEqual(len(novos), len(set(novos)))                    # 's0.b.b' já era da terceira coluna

    def test_remover_devolve_o_vao_unico(self):
        s = _spec()
        novas, divisao = vaos.inserir_vertical([], s, 's0', 'montante')
        volta = vaos.remover(novas, divisao.uid)
        self.assertEqual([v.caminho for v in vaos.arvore(volta, s)], ['s0'])


if __name__ == '__main__':
    unittest.main()
