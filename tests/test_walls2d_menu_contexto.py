"""Reprodução e regressão do BUG-20261117-AKYJ: caixa de contexto da parede no editor.

Run: py -3 tests/test_walls2d_menu_contexto.py

O layout e o alvo da caixa são Python puro: a geometria e a resolução do clique são provadas aqui, fora do Blender.
Pedido do titular em 2026-11-17: botão direito sobre a parede abre a caixa no ponto do clique, com Linha/Direção,
inverter o sentido de todas as paredes ativas e o tipo de parede com cor.
"""

import unittest

import _bootstrap  # noqa: F401
from caffmob_draw.walls2d import cores, menu_contexto as mc

REGIAO = (0, 0, 800, 600)


class CaixaTest(unittest.TestCase):
    def test_itens_na_ordem_pedida(self):
        itens = mc.itens('INNER', 'LEFT', 'NORMAL')
        self.assertEqual([i['id'] for i in itens],
                         ['linha', 'direcao', 'inverter', 'tipo:NORMAL', 'tipo:DIVISORIA', 'tipo:MURETA'])

    def test_valores_mostram_o_estado_atual(self):
        itens = mc.itens('OUTER', 'RIGHT', 'MURETA')
        self.assertEqual(itens[0]['valor'], 'Externa')
        self.assertEqual(itens[1]['valor'], 'Direita')
        self.assertEqual([i['id'] for i in itens if i.get('marcado')], ['tipo:MURETA'])

    def test_direcao_divergente_mostra_multiplas(self):
        itens = mc.itens('INNER', None, None)
        self.assertEqual(itens[1]['valor'], 'Múltiplas')
        self.assertFalse(any(i.get('marcado') for i in itens))

    def test_layout_cabe_na_regiao_em_qualquer_clique(self):
        itens = mc.itens('INNER', 'LEFT', 'NORMAL')
        for pixel in [(2, 2), (798, 598), (400, 300), (1, 590), (790, 5)]:
            caixa = mc.layout(pixel, itens, REGIAO)
            self.assertGreaterEqual(caixa['x'], REGIAO[0], pixel)
            self.assertGreaterEqual(caixa['y'], REGIAO[1], pixel)
            self.assertLessEqual(caixa['x'] + caixa['largura'], REGIAO[2], pixel)
            self.assertLessEqual(caixa['y'] + caixa['altura'], REGIAO[3], pixel)
            for _chave, r in caixa['itens']:
                self.assertGreaterEqual(r[0], caixa['x'], pixel)
                self.assertGreaterEqual(r[1], caixa['y'], pixel)
                self.assertLessEqual(r[0] + r[2], caixa['x'] + caixa['largura'], pixel)
                self.assertLessEqual(r[1] + r[3], caixa['y'] + caixa['altura'], pixel)

    def test_alvo_resolve_cada_linha_e_nada_fora(self):
        caixa = mc.layout((400, 300), mc.itens('INNER', 'LEFT', 'NORMAL'), REGIAO)
        for chave, r in caixa['itens']:
            centro = (r[0] + r[2] / 2, r[1] + r[3] / 2)
            self.assertEqual(mc.alvo(caixa, centro), chave, r)
        self.assertIsNone(mc.alvo(caixa, (caixa['x'] - 5, caixa['y'] + 5)))
        self.assertIsNone(mc.alvo(caixa, (caixa['x'] + caixa['largura'] + 5, caixa['y'] + caixa['altura'] / 2)))

    def test_apenas_botao_direito_no_modo_selecionar_abre(self):
        self.assertTrue(mc.abre_menu('SELECT', 'RIGHTMOUSE', 'PRESS'))
        self.assertFalse(mc.abre_menu('DRAW', 'RIGHTMOUSE', 'PRESS'))      # desenho: encerra o lápis, não abre caixa
        self.assertFalse(mc.abre_menu('SELECT', 'RIGHTMOUSE', 'RELEASE'))
        self.assertFalse(mc.abre_menu('SELECT', 'ESC', 'PRESS'))
        self.assertFalse(mc.abre_menu('MOVE', 'RIGHTMOUSE', 'PRESS'))

    def test_tipo_escolhido_pela_caixa_devolve_o_valor_do_modelo(self):
        self.assertEqual(mc.tipo_da_chave('tipo:DIVISORIA'), 'DIVISORIA')
        self.assertIsNone(mc.tipo_da_chave('inverter'))


class CoresTest(unittest.TestCase):
    def test_cada_tipo_tem_cor_propria(self):
        normal, divisoria, mureta = (cores.cor(t) for t in ('NORMAL', 'DIVISORIA', 'MURETA'))
        self.assertNotEqual(normal, divisoria)
        self.assertNotEqual(normal, mureta)
        self.assertNotEqual(divisoria, mureta)

    def test_normal_mantem_o_cinza_do_editor(self):
        self.assertEqual(cores.cor('NORMAL'), cores.CINZA)

    def test_toda_cor_e_rgba_valida(self):
        for tipo in ('NORMAL', 'DIVISORIA', 'MURETA'):
            cor = cores.cor(tipo)
            self.assertEqual(len(cor), 4, tipo)
            for canal in cor:
                self.assertGreaterEqual(canal, 0.0, tipo)
                self.assertLessEqual(canal, 1.0, tipo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
