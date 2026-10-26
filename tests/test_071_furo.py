"""071, emendas E001 a E005 (7ª auditoria): a parede importada fura onde o Promob marca o furo.

- E001: fura o item com `HOLE PRICK="Y"`, em qualquer camada; `HOLE` sem `PRICK` não fura; o trecho sai primeiro do
  `WALL` que hospeda o item; a janela de malha OBJ fica desenhada no vão;
- E002: porta elevada vai ao piso; vão recusado pelo editor de paredes devolve o item ao complemento;
- E003: abertura que passa da divisão entre trechos colineares fura os dois;
- E004: janela sobre porta no mesmo trecho entra com as peças, sem o furo;
- E005: passagem sem folha genérica, com o marco em moldura.
"""
import unittest
from unittest import mock

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2

from test_071_referencial import por_nome

FURA = '<HOLE PRICK="Y" DEPTH="150" />'


def converter(itens):
    principal = ps._ambiente(itens, nome='Furo')
    return para_v2.converter(leitor.abrir(ps.zip_de(ps.entradas(principal=principal))).projeto(0), catalogo=[])


def janela(id_, x, z, w, h, camada='Default', extra=FURA, nome='Janela', material='m', filhos=(), y=150, d=150):
    return ps._item('MODULO', id_, base=(x, y, z), dim=(w, h, d), rot=0, nome=nome, camada=camada, material=material,
                    extra=extra, filhos=filhos)


def parede(pontos, hospedados, id_='PAREDE'):
    return ps._parede([(x, y, 150) for x, y in pontos], 2700, hospedados, id_=id_)


class FuroTest(unittest.TestCase):
    def test_e001_fura_pelo_prick_em_qualquer_camada(self):
        r = converter([parede([(0, 0), (4000, 0)], [
            janela('j1', 500, 1000, 1200, 1000),                                   # Default, PRICK="Y": fura
            janela('j2', 2500, 1000, 800, 800, extra='<HOLE DEPTH="150" />'),      # só DEPTH: não fura
        ])])
        aberturas = r['documento']['aberturas']
        self.assertEqual([(a['tipo'], a['posicao'], a['largura']) for a in aberturas], [('WINDOW', 500.0, 1200.0)])

    def test_e001_trecho_do_wall_hospedeiro(self):
        # duas paredes paralelas a 100 mm; a janela encosta nas duas, mas é filha da segunda
        a = parede([(0, 0), (3000, 0)], [], id_='A')
        b = parede([(0, 100), (3000, 100)], [janela('j', 1000, 1000, 800, 800, y=250, d=160)], id_='B')
        r = converter([a, b])
        parede_b = r['documento']['paredes'][1]
        self.assertEqual(r['documento']['aberturas'][0]['segmento_id'], parede_b['segmentos'][0]['id'])

    def test_e001_janela_de_malha_obj_fica_no_vao(self):
        obj = (f'<FILE3D NAME="%LinkedFilesFolder%\\{ps.OBJ_GUID}.obj" LINKEDFILE="Y" />' + FURA)
        externa = ps._item('ENTIDADEEXTERNA', 'ext', base=(800, 150, 1000), dim=(1400, 850, 150), rot=0,
                           material='m', extra=obj)
        r = converter([parede([(0, 0), (4000, 0)], [externa])])
        aberturas = r['documento']['aberturas']
        self.assertEqual(len(aberturas), 1)
        visual = next(n for n in r['complemento']['moveis'] if n.get('abertura'))
        self.assertEqual((visual['tipo'], visual['abertura']), ('malha', aberturas[0]['id']))

    def test_e002_porta_elevada_vai_ao_piso(self):
        porta = janela('p', 1000, 71.5, 800, 2100, camada='Decore-Aberturas', nome='Porta')
        r = converter([parede([(0, 0), (4000, 0)], [porta])])
        a, = r['documento']['aberturas']
        self.assertEqual((a['tipo'], a['peitoril'], a['altura']), ('DOOR', 0, 2171.5))

    def test_e002_vao_recusado_devolve_o_item(self):
        real = para_v2.validar_documento
        chamadas = []

        def recusa_a_primeira(doc):
            chamadas.append(1)
            erros = real(doc)
            if doc['aberturas'] and len(chamadas) == 1:
                erros = erros + [dict(caminho='aberturas[0].peitoril', codigo='PEITORIL_FORA')]
            return erros
        folha = janela('f', 1005, 5, 790, 2090, extra='', nome='Folha', material='vidro_fume', y=140, d=30)
        porta = janela('p', 1000, 0, 800, 2100, camada='Decore-Aberturas', nome='Porta', filhos=[folha])
        with mock.patch.object(para_v2, 'validar_documento', recusa_a_primeira):
            r = converter([parede([(0, 0), (4000, 0)], [porta])])
        self.assertEqual(r['documento']['aberturas'], [])
        grupo = por_nome(r['complemento']['moveis'], 'Porta')
        self.assertEqual(grupo['tipo'], 'grupo')
        self.assertIn('Folha', [f['nome'] for f in grupo['filhos']])
        self.assertTrue(any('recusada' in a for a in r['relatorio']['avisos']))

    def test_e003_vao_nos_dois_trechos_colineares(self):
        r = converter([parede([(0, 0), (2000, 0), (4000, 0)], [janela('j', 1973.271, 1000, 2000, 1180)])])
        segs = [s['id'] for s in r['documento']['paredes'][0]['segmentos']]
        pedacos = sorted((segs.index(a['segmento_id']), a['posicao'], a['largura']) for a in r['documento']['aberturas'])
        self.assertEqual(pedacos, [(0, 1973.271, 26.729), (1, 0.0, 1973.271)])
        fragmento = next(a['id'] for a in r['documento']['aberturas'] if a['largura'] < 100)
        self.assertEqual(r['complemento']['aberturas_sem_folha'], [fragmento])

    def test_e004_janela_sobre_porta_entra_sem_o_furo(self):
        porta = janela('p', 1000, 0, 1050, 2000, camada='Decore-Aberturas', nome='Porta')
        alta = janela('j', 1000, 2100, 1050, 500, camada='Decore-Aberturas', nome='Janela alta')
        r = converter([parede([(0, 0), (4000, 0)], [porta, alta])])
        self.assertEqual([a['tipo'] for a in r['documento']['aberturas']], ['DOOR'])
        no = por_nome(r['complemento']['moveis'], 'Janela alta')
        self.assertEqual((no['tipo'], len(no['filhos'])), ('grupo', 3))             # marco: dois lados e o topo
        self.assertTrue(any('sobreposta' in i['motivo'] for i in r['relatorio']['ignorados']))

    def test_e005_passagem_sem_folha_generica(self):
        marco = janela('m', 1000, 0, 810, 2403, camada='Decore-Aberturas', nome='Marco Interno s/ Porta')
        r = converter([parede([(0, 0), (4000, 0)], [marco])])
        a, = r['documento']['aberturas']
        self.assertEqual(r['complemento']['aberturas_sem_folha'], [a['id']])
        visual = next(n for n in r['complemento']['moveis'] if n.get('abertura'))
        self.assertEqual(sorted(f['nome'] for f in visual['filhos']), ['Marco Interno s/ Porta · moldura'] * 3)


if __name__ == '__main__':
    unittest.main()
