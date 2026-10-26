"""Onda 8 da 067 (T184; RF-164 a RF-166, D-42, D-43, D-45): edição do documento do MOBI pelo painel."""
import unittest

import _mobi_sintetico as ms
from caffmob_draw.mobi import editar_v2_core as core


class EditarAberturaTest(unittest.TestCase):
    def setUp(self):
        self.d = ms.ambiente()

    def test_campos_da_abertura(self):
        for campo, valor in (('largura', 3000), ('altura', 2400), ('posicao', 1500)):
            r = core.editar(self.d, 'abertura', ms.PORTAO, campo, valor)
            self.assertTrue(r['ok'], r)
            self.assertEqual(next(a for a in r['valor']['aberturas'] if a['id'] == ms.PORTAO)[campo], valor)
        r = core.editar(self.d, 'abertura', ms.JANELA, 'peitoril', 900)
        self.assertTrue(r['ok'], r)

    def test_recusas_nao_mudam_o_documento(self):
        antes = repr(self.d)
        for campo, valor in (('largura', 12000), ('posicao', 8000)):
            r = core.editar(self.d, 'abertura', ms.PORTAO, campo, valor)
            self.assertFalse(r['ok'])
            self.assertTrue(core.mensagem(r))
        self.assertEqual(repr(self.d), antes)

    def test_sobreposicao(self):
        d = ms.ambiente()
        janela = next(a for a in d['aberturas'] if a['id'] == ms.JANELA)
        r = core.editar(d, 'abertura', ms.JANELA, 'posicao', 0)
        self.assertTrue(r['ok'])
        d = r['valor']
        r = core.editar(dict(d, aberturas=[*d['aberturas'], dict(janela, id='06800000-0000-4000-8000-0000000000a3', posicao=500)]),
                        'abertura', '06800000-0000-4000-8000-0000000000a3', 'largura', 1300)
        self.assertFalse(r['ok'])
        self.assertIn('SOBREPOSICAO', [e['codigo'] for e in r['erros']])

    def test_campo_desconhecido(self):
        self.assertFalse(core.editar(self.d, 'abertura', ms.PORTAO, 'escala', 2)['ok'])


class EditarParedeTest(unittest.TestCase):
    def setUp(self):
        self.d = ms.ambiente()
        self.parede = self.d['paredes'][0]['id']

    def test_trechos_numerados(self):
        self.assertEqual([(t['numero'], t['comprimento']) for t in core.trechos_da_parede(self.d, self.parede)],
                         [(1, 30000), (2, 10000), (3, 30000), (4, 10000)])

    def test_altura_e_espessura_da_parede_toda(self):
        r = core.editar(self.d, 'parede', self.parede, 'altura', 2800)
        self.assertTrue(r['ok'], r)
        trechos = r['valor']['paredes'][0]['segmentos']
        self.assertEqual({(s['pe_direito_inicial'], s['pe_direito_final']) for s in trechos}, {(2800, 2800)})
        r = core.editar(r['valor'], 'parede', self.parede, 'espessura', 200)
        self.assertEqual({s['espessura'] for s in r['valor']['paredes'][0]['segmentos']}, {200})

    def test_valor_comum(self):
        self.assertEqual(core.valor_da_parede(self.d, self.parede, 'espessura'), 150)
        d = dict(self.d, paredes=[dict(self.d['paredes'][0], segmentos=[dict(s, espessura=150 + 40 * (k == 2))
                                                                         for k, s in enumerate(self.d['paredes'][0]['segmentos'])])])
        self.assertIsNone(core.valor_da_parede(d, self.parede, 'espessura'))

    def test_aberturas_da_parede_e_dono(self):
        self.assertEqual({a['id'] for a in core.aberturas_da_parede(self.d, self.parede)}, {ms.PORTAO, ms.JANELA})
        parede, numero = core.dono_da_abertura(self.d, ms.PORTAO)
        self.assertEqual((parede['id'], numero), (self.parede, 2))
        self.assertIsNone(core.dono_da_abertura(self.d, 'nao-existe'))

    def test_material_interno_de_tres_trechos_num_lote_do_mobi(self):
        # RF-163 no projeto do MOBI (6ª auditoria A001): o lote do editor muda o material interno das três de uma vez.
        from caffmob_draw.caffmob.v2 import paredes_edicao as pe
        material = self.d['materiais'][0]['id']
        ids = [s['id'] for s in self.d['paredes'][0]['segmentos'][:3]]
        r = pe.editar_paredes_em_lote(self.d, self.d['paredes'][0]['pavimento_id'], ids, {'material_interno_id': material})
        self.assertTrue(r['ok'], r)
        self.assertEqual([s.get('material_interno_id') for s in r['valor']['paredes'][0]['segmentos']],
                         [material, material, material, self.d['paredes'][0]['segmentos'][3].get('material_interno_id')])

    def test_recusa_fora_da_faixa(self):
        r = core.editar(self.d, 'parede', self.parede, 'altura', 9000)
        self.assertFalse(r['ok'])


if __name__ == '__main__':
    unittest.main()
