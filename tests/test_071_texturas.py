"""071, 4ª auditoria: texturas de marca dos armários (Duratex, Arauco...), veio e componentes do Promob.

O material de chapa do Promob é o código do catálogo dele (`Dur_Cri_titanio_h`); o `cin_cor_000` dos componentes é a
"cor do modelo", que o modelo do item diz por face (`coz_ass_duratex_ext` → `coz_dur_cri_titanio_h`).
"""
import json
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2, texturas

from test_071_referencial import converter, por_nome

CATALOGO = texturas.itens_do_catalogo(json.load(open(ps.__file__.rsplit('/', 2)[0] + '/caffmob_draw/textures/catalog.json',
                                                     encoding='utf-8')))


def modelos(**faces):
    return '<MODELS>{}</MODELS>'.format(''.join(
        f'<MODEL IDMODEL="x_mod_{f}" IDMODELTYPE="y"><MODEL IDMODEL="coz_ass_duratex_{f}" IDMODELTYPE="{v}" /></MODEL>'
        for f, v in faces.items()))


def componentes(*pares):
    return '<COMPONENTDEFINITIONCOLLECTION>{}</COMPONENTDEFINITIONCOLLECTION>'.format(
        ''.join(f'<COMPONENTDEFINITION NAME="{c}" ID="{c}" IDMATERIAL="{m}" />' for c, m in pares))


class TexturasTest(unittest.TestCase):
    def test_codigos_do_promob_no_catalogo_do_addon(self):
        casos = {
            'Dur_Cri_titanio_h': ('duratex/cristallo/titanio-cristallo', 'H'),
            'Dur_Cri_titanio_v': ('duratex/cristallo/titanio-cristallo', 'V'),
            'dur_des_ver_nogueira_caiena': ('duratex/design/nogueira-caiena-design', 'V'),
            'Dur_Mad_The_Hor_Fre_Imp': ('duratex/thera/freijo-imperial-thera', 'H'),
            'arauco_tx_cinza_cristal': ('arauco/cores-e-tecidos/tx-cinza-cristal', None),
            'mas_carvalho_mel_h': ('arauco/madeiras/bold-carvalho-mel', 'H'),
            'coz_dur_cri_titanio_h': ('duratex/cristallo/titanio-cristallo', 'H'),
            'ara_lor_lis': ('arauco/cores-e-tecidos/matt-lord', None),     # Lord, liso (o acabamento não é cor)
            'ara_xyz_lis': (None, None),            # sem par seguro: não chuta
            'dor_branco': (None, None),
        }
        achados = {c: ((lambda r: (r[0] and r[0]['id'], r[1]))(texturas.resolver(c, CATALOGO))) for c in casos}
        self.assertEqual(achados, casos)

    def test_caminho_da_biblioteca_vence(self):
        item, veio = texturas.resolver('Dur_Mad_The_Fre_Imp_V(1)', CATALOGO,
                                       '%PastaTextures%/fabrica/duratex/Thera/Freijo_Imperial_Thera.jpg')
        self.assertEqual((item['id'], veio), ('duratex/thera/freijo-imperial-thera', 'V'))

    def test_cor_do_modelo_vira_textura_com_veio_e_componente(self):
        lateral = ps._item('MODULO', 'lat', base=(0, 0, 0), dim=(15, 720, 550), rot=0, nome='Lateral 15mm',
                           extra=componentes(('CORPO_INTERNO', 'cin_cor_000'), ('FITA_V', 'cin_cor_000'),
                                             ('CORPO_EXTERNO', 'cin_cor_000')))
        balcao = ps._item('MODULO', 'bal', base=(0, 0, 0), dim=(600, 720, 550), rot=0, nome='Balcão',
                          filhos=[lateral], extra=modelos(ext='coz_dur_cri_titanio_h', int='coz_branco',
                                                          fita='coz_branco'))
        r = converter([balcao])
        no = por_nome(r['complemento']['moveis'], 'Lateral 15mm')
        dado = r['complemento']['materiais'][no['material']]
        self.assertEqual((dado['textura_catalogo'], dado['veio'], dado['tamanho']),
                         ('duratex/cristallo/titanio-cristallo', 'H', (600.0, 600.0)))
        self.assertEqual(no['componente'], 'LAT')
        self.assertEqual(no['componentes'][0], ['CORPO_EXTERNO', 'coz_dur_cri_titanio_h'])      # face externa primeiro
        self.assertIn(['FITA_V', 'coz_branco'], no['componentes'])
        self.assertEqual(texturas.cor_por_nome('coz_branco'), (0xF4, 0xF4, 0xF2))      # branco do modelo

    def test_leitor_herda_o_acabamento_do_pai(self):
        filho = ps._item('MODULO', 'f', dim=(10, 10, 10), extra=modelos(int='dor_branco'))
        pai = ps._item('MODULO', 'p', dim=(10, 10, 10), filhos=[filho], extra=modelos(ext='dor_dur_cri_titanio_h'))
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([pai])
        it = leitor.abrir(ps.zip_de(mapa)).projeto(1).itens[0].filhos[0]
        self.assertEqual(it.acabamentos, {'ext': 'dor_dur_cri_titanio_h', 'int': 'dor_branco'})

    def test_componente_pelo_nome(self):
        nomes = {'Lateral 15mm': 'LAT', 'Lateral de Gaveta 400': 'LATERAL_GAVETA', 'Prateleira Linear': 'PRAT',
                 'Frente Gaveta Reta 180mm': 'FRENTE_GAVETA', 'Porta Reta': 'POR', 'Fundo 6': 'FUN_INF', 'Base 15': 'BAS',
                 'Rodapé 100': 'ROD', 'Torneira': None}
        self.assertEqual({n: para_v2.componente_da_peca(n) for n in nomes}, nomes)


if __name__ == '__main__':
    unittest.main()
