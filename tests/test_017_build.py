"""017 (T020; RN-04, RN-07, RN-09, RN-15, RN-19): as chapas que o `build.pecas` entrega ao corte e à cena.

Teste puro: o `build.py` importa `bpy`/`bmesh`/`mathutils` só dentro das funções que criam dados na cena, então a
lista de chapas em milímetros roda sem Blender. Aqui ficam a caixa, o fundo nas duas fixações, a posição das
divisórias, as frentes de gaveta e as chapas da caixa da gaveta que o `gavetas.chapas` dimensiona.
"""

import importlib
import unittest
from dataclasses import replace

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


build = _modulo('build')
gavetas = _modulo('gavetas')
spec = _modulo('spec')
vaos = _modulo('vaos')
PENDENTE = 'caffmob_draw/armario_v2/build.py ainda não existe (T020)'


def _spec(**campos):
    """Armário de 1000 × 2000 × 560 mm com as quatro chapas da caixa."""
    base = dict(largura=1000.0, altura=2000.0, profundidade=560.0,
                lateral_esq_ativa=True, lateral_dir_ativa=True,
                base_inf_ativa=True, base_sup_ativa=True)
    base.update(campos)
    return spec.Spec(**base)


def _por_papel(itens, papel):
    return [item for item in itens if item['papel'] == papel]


def _tamanho(item):
    (x0, y0, z0), (x1, y1, z1) = item['box']
    return (round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3))


@unittest.skipIf(build is None or spec is None, PENDENTE)
class PecasTest(unittest.TestCase):
    def test_caixa_em_lateral_passante(self):
        itens = build.pecas(_spec())
        self.assertEqual(len(itens), 4)
        esquerda, direita = _por_papel(itens, 'LATERAL')
        self.assertEqual(_tamanho(esquerda), (15.0, 560.0, 2000.0))     # espessura × profundidade × altura
        self.assertEqual(esquerda['box'][0], (-500.0, -560.0, 0.0))
        self.assertEqual(direita['box'][1], (500.0, 0.0, 2000.0))
        base_inf, base_sup = _por_papel(itens, 'BASE_INF') + _por_papel(itens, 'BASE_SUP')
        self.assertEqual(_tamanho(base_inf), (970.0, 560.0, 15.0))      # entre as laterais
        self.assertEqual(_tamanho(base_sup), (970.0, 560.0, 15.0))
        self.assertEqual(base_sup['box'][0][2], 1985.0)

    def test_caixa_em_base_passante(self):
        itens = build.pecas(_spec(tipo_montagem='BASE_PASSANTE'))
        esquerda, _direita = _por_papel(itens, 'LATERAL')
        self.assertEqual(_tamanho(esquerda), (15.0, 560.0, 1970.0))     # entre as duas bases
        self.assertEqual(esquerda['box'][0][2], 15.0)                   # em cima da base inferior
        base_inf = _por_papel(itens, 'BASE_INF')[0]
        self.assertEqual(_tamanho(base_inf), (1000.0, 560.0, 15.0))     # as bases cobrem a largura

    def test_fundo_encaixado_e_sobreposto(self):
        canal = build.pecas(_spec(fundo_ativo=True, fundo_fixacao='CANAL', fundo_recuo=10.0))
        fundo = _por_papel(canal, 'FUNDO')[0]
        self.assertEqual(_tamanho(fundo), (970.0, 6.0, 1970.0))         # entre as chapas da caixa
        self.assertEqual((fundo['box'][0][1], fundo['box'][1][1]), (-16.0, -10.0))
        sobreposto = build.pecas(_spec(fundo_ativo=True, fundo_fixacao='SOBREPOSTO', fundo_recuo=10.0))
        fundo = _por_papel(sobreposto, 'FUNDO')[0]
        self.assertEqual(_tamanho(fundo), (1000.0, 6.0, 2000.0))        # medidas externas

    def test_divisorias_partem_do_vao(self):
        s = _spec()
        divisoes, vertical = vaos.inserir_vertical([], s, 's0', 'distanciador')
        itens = build.pecas(s, divisoes)
        self.assertEqual(len(_por_papel(itens, 'DIVISORIA')), 1)
        self.assertEqual(vertical.espessura, 30.0)
        self.assertEqual(_tamanho(_por_papel(itens, 'DIVISORIA')[0]), (30.0, 560.0, 1970.0))
        com_prateleira, prateleira = vaos.inserir_horizontal(divisoes, s, 's0.b', 'prat_fixa')
        self.assertIn('PRATELEIRA', [item['papel'] for item in build.pecas(s, com_prateleira)])
        self.assertEqual(prateleira.espessura, 15.0)

    def test_frentes_de_gaveta_empilhadas_com_folga(self):
        s = _spec()
        bloco = gavetas.bloco(700.0, 2, vao='s0')
        itens = build.pecas(s, (), bloco)
        frentes = _por_papel(itens, 'FRENTE_GAVETA')
        self.assertEqual(len(frentes), 2)
        for frente in frentes:
            self.assertEqual(_tamanho(frente), (970.0, 15.0, 345.5))    # (700 − 3 × 3) / 2
            self.assertTrue(frente['movel'])
        self.assertEqual(frentes[0]['box'][0][2], 18.0)                  # piso interno (15) + folga (3)
        self.assertEqual(frentes[1]['box'][0][2], 366.5)                 # 18 + 345,5 + 3

    def test_caixa_da_gaveta_entra_no_plano(self):
        s = _spec()
        gaveta = replace(gavetas.bloco(700.0, 1, vao='s0')[0], separador_colunas=2, separador_linhas=2)
        itens = build.pecas(s, (), [gaveta])
        separadores = _por_papel(itens, 'SEPARADOR')
        afastadores = _por_papel(itens, 'AFASTADOR')
        self.assertEqual(len(separadores), 2)                            # 1 vertical + 1 horizontal
        self.assertEqual(len(afastadores), 4)                            # os quatro independentes
        for separador in separadores:
            self.assertEqual(separador['espessura'], 6.0)                 # chapa do separador, não a da caixa
            self.assertEqual(round(min(_tamanho(separador)), 3), 6.0)
        self.assertEqual(sorted(item['box'][0][1] < item['box'][1][1] for item in separadores), [True, True])
        # as chapas da caixa ficam entre a frente e o fundo do armário, nunca à frente dele
        limite_frente = -s.profundidade - s.espessura_porta
        for item in separadores + afastadores:
            self.assertLessEqual(item['box'][1][1], limite_frente + 1e-6, item['nome'])
            self.assertTrue(item['movel'])
        sem_separador = gavetas.bloco(700.0, 1, vao='s0')[0]
        self.assertEqual(_por_papel(build.pecas(s, (), [sem_separador]), 'SEPARADOR'), [])


if __name__ == '__main__':
    unittest.main()
