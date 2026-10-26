"""071, terceira auditoria: portas que sumiam, portas de vidro, torneira em caixa e marcadores do Promob.

Conferido nos projetos do titular: item com `COMPONENTDEFINITION` tem corpo próprio (a porta, a torneira, a
dobradiça), mesmo com filhos; sem componente, é montagem (o balcão) e o corpo são os filhos. Folha sem componente de
até 10 mm é marcador (furo, "Sem Puxador", "Processo de Fabricação"). Os materiais do catálogo não vêm no arquivo:
vidro, espelho e metal saem pelo nome.
"""
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2

from test_071_referencial import caixa, converter, por_nome


def componentes(*pares):
    return '<COMPONENTDEFINITIONCOLLECTION>{}</COMPONENTDEFINITIONCOLLECTION>'.format(
        ''.join(f'<COMPONENTDEFINITION NAME="{c}" ID="{c}" IDMATERIAL="{m}" />' for c, m in pares))


def todos(nos):
    for n in nos:
        yield n
        yield from todos(n['filhos'])


class CorposTest(unittest.TestCase):
    def test_porta_com_filhos_desenha_a_folha(self):
        dobradica = ps._item('MODULO', 'ace_fer_dob_sem_ret', base=(10, -5, 100), dim=(31, 42, 2), rot=0, nome='Dobradiça',
                             material='dec_met_lis_alu')
        sem_pux = ps._item('MODULO', 'sem_pux', base=(10, -5, 400), dim=(1, 1, 1), nome='Sem Puxador')
        processo = ps._item('MODULO', 'proc', base=(0, 0, 0), dim=(10, 10, 10), nome='Processo de Fabricação')
        porta = ps._item('MODULO', 'porta', base=(0, 0, 0), dim=(318, 490, 15), rot=0, nome='Porta Reta',
                         material='cin_cor_000', filhos=[dobradica, sem_pux, processo])
        balcao = ps._item('MODULO', 'balcao', base=(0, 0, 0), dim=(650, 500, 435), rot=0, nome='Balcão 2 Portas',
                          filhos=[porta])
        r = converter([balcao])
        moveis = r['complemento']['moveis']
        self.assertEqual(por_nome(moveis, 'Balcão 2 Portas')['tipo'], 'grupo')
        folha = por_nome(moveis, 'Porta Reta')
        self.assertEqual((folha['tipo'], [f['nome'] for f in folha['filhos']]), ('caixa', ['Dobradiça']))
        self.assertEqual((folha['visivel'], folha['filhos'][0]['visivel']), (True, False))   # dobradiça oculta
        self.assertIsNone(por_nome(moveis, 'Sem Puxador'))
        self.assertIsNone(por_nome(moveis, 'Processo de Fabricação'))
        self.assertEqual(r['relatorio']['auxiliares'], 2)

    def test_torneira_e_cuba_ganham_silhueta_de_metal(self):
        torneira = ps._item('MODULO', 'Torneira_20', base=(0, 0, 900), dim=(32, 100, 90), rot=0,
                            material='dec_met_lis_cro')
        cuba = ps._item('MODULO', 'cuba', base=(200, 0, 760), dim=(450, 140, 300), rot=0, nome='Cuba Retangular',
                        material='dec_met_lis_ino')
        r = converter([torneira, cuba])
        mats = r['complemento']['materiais']
        t, c = por_nome(r['complemento']['moveis'], 'Torneira_20'), por_nome(r['complemento']['moveis'], 'Cuba Retangular')
        self.assertEqual((t['forma'], c['forma']), ('torneira', 'cuba'))
        self.assertEqual((mats['dec_met_lis_cro']['classe'], mats['dec_met_lis_cro']['cor']), ('metal', '#d0d2d4'))
        self.assertEqual(mats['dec_met_lis_ino']['cor'], '#a9acae')

    def test_porta_de_madeira_e_vidro_vira_moldura_e_vidro(self):
        porta = ps._item('MODULO', 'porta_110', base=(0, 0, 0), dim=(879, 2025, 76), rot=0, nome='Porta em vidro',
                         extra=componentes(('DEC_PORTA', 'jacaranda'), ('DEC_VIDRO', 'vidro_fume')))
        r = converter([porta])
        no = por_nome(r['complemento']['moveis'], 'Porta em vidro')
        nomes = sorted(f['nome'] for f in no['filhos'])
        self.assertEqual(nomes, ['Porta em vidro · moldura'] * 4 + ['Porta em vidro · vidro'])
        vidro = next(f for f in no['filhos'] if f['nome'].endswith('vidro'))
        self.assertEqual(r['complemento']['materiais'][vidro['material']]['classe'], 'vidro')
        self.assertEqual(caixa(vidro), ((60, -42, 60), (819, -34, 1965)))      # 8 mm no meio dos 76 da folha

    def test_porta_de_aluminio_vira_moldura_em_volta_do_painel(self):
        painel = ps._item('MODULO', 'pai_vid', base=(8, 0, 8), dim=(564, 1976, 15), rot=0, nome='Painel Vidro',
                          material='vid_reflecta')
        porta = ps._item('MODULO', 'alu', base=(0, 0, 0), dim=(580, 1992, 15), rot=0, nome='Porta de Alumínio',
                         material='dec_met_lis_alu', filhos=[painel])
        r = converter([porta])
        no = por_nome(r['complemento']['moveis'], 'Porta de Alumínio')
        molduras = [f for f in no['filhos'] if f['nome'].endswith('moldura')]
        self.assertEqual((no['tipo'], len(molduras)), ('grupo', 4))
        self.assertTrue(all(r['complemento']['materiais'][m['material']]['classe'] == 'metal' for m in molduras))
        self.assertEqual(por_nome(no['filhos'], 'Painel Vidro')['tipo'], 'caixa')

    def test_porta_de_vidro_de_parede_traz_as_folhas(self):
        folha = ps._item('MODULO', 'OCL_PORT_01', base=(1002, -2, 1), dim=(1046, 1998, 15), rot=0, nome='Folha',
                         material='vidro_fume')
        porta = ps._item('MODULO', 'Porta_29', base=(1000, 0, 0), dim=(1050, 2000, 150), rot=0, nome='Porta de Vidro',
                         camada='Decore-Aberturas', material='cin_cor_000', filhos=[folha])
        parede = ps._parede([(0, 0, 150), (4000, 0, 150)], 2700, hospedados=[porta])
        r = converter([parede])
        self.assertEqual(len(r['documento']['aberturas']), 1)
        grupo = next(n for n in r['complemento']['moveis'] if n.get('abertura'))
        self.assertEqual(grupo['abertura'], r['documento']['aberturas'][0]['id'])
        self.assertEqual([f['nome'] for f in grupo['filhos']], ['Folha'])
        self.assertEqual(r['complemento']['materiais']['vidro_fume']['transparencia'], 0.6)

    def test_angulo_relativo_ao_pai_so_quando_cabe(self):
        # o fundo da cuba esculpida: 180° do item somado aos 180° do tampo cai dentro do recorte
        fundo = ps._item('GEOMETRY', 'fundo', base=(5940, 2237, 880), dim=(216, 15, 262), rot=180, nome='Fundo da cuba',
                         limites=((0, -262, 0), (216, 0, 15)))
        porta = ps._item('MODULO', 'porta', base=(6000, 2100, 880), dim=(100, 10, 15), rot=180, nome='Porta',
                         material='m', limites=((0, -15, 0), (100, 0, 10)))
        tampo = ps._item('MODULO', 'tampo', base=(6270, 1760, 860), dim=(450, 100, 650), rot=180, nome='Tampo',
                         filhos=[fundo, porta])
        r = converter([tampo])
        lo, hi = caixa(por_nome(r['complemento']['moveis'], 'Fundo da cuba'))
        self.assertTrue(lo[0] >= 5820 and hi[0] <= 6270 and lo[1] >= 1760 and hi[1] <= 2410, (lo, hi))
        lo, hi = caixa(por_nome(r['complemento']['moveis'], 'Porta'))
        self.assertEqual((lo[0], hi[0]), (5900, 6000))              # cabe dos dois jeitos: fica o ângulo absoluto

    def test_classe_do_material(self):
        casos = {'vid_verde': 'vidro', 'coz_vid_pre': 'vidro', 'vidro_fume': 'vidro', 'espelho_01': 'espelho',
                 'dec_met_lis_cro': 'metal', 'arauco_tx_cinza_cristal': None, 'cin_cor_000': None, 'jacaranda': None,
                 'vid_reflecta(1)': 'vidro'}
        self.assertEqual({m: para_v2.classe_do_material(m) for m in casos}, casos)

    def test_leitor_le_componentes_e_transparencia(self):
        item = ps._item('MODULO', 'p', dim=(10, 10, 10), extra=componentes(('A', 'x'), ('B', 'y')))
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([item])
        mapa['solucao\\materials\\materials.material'] = (
            f'{ps.BOM}<?xml version="1.0" encoding="utf-8"?><MATERIALS><MATERIAL ID="vid(1)" NAME="Vidro">'
            '<COLORBASE R="1" G="2" B="3" /><TRANSPARENCY>0.3</TRANSPARENCY><FINISHSCHEME>Mirror</FINISHSCHEME>'
            '</MATERIAL></MATERIALS>')
        projeto = leitor.abrir(ps.zip_de(mapa)).projeto(1)
        self.assertEqual(projeto.itens[0].componentes, [('A', 'x'), ('B', 'y')])
        m = projeto.materiais['vid(1)']
        self.assertEqual((m.transparencia, m.acabamento, para_v2.classe_do_material('vid(1)', m)), (0.3, 'Mirror', 'vidro'))

    def test_macro_do_catalogo_sai_do_nome(self):
        item = leitor.Item('MODULO', 'd', 'Dobradiça $REFERENCE(MODEL_DESCRIPTION)$ s/ Amort.', '', True, (0, 0, 0), 0,
                           1, 1, 1)
        self.assertEqual(para_v2.resolver_macros(item.nome, item), 'Dobradiça s/ Amort.')


if __name__ == '__main__':
    unittest.main()
