"""071, 10ª auditoria: painel ripado em molde, lajes de MDF no corte, persiana do catálogo e cor pelo nome.

- O "Painel" do Promob traz o contorno como molde de 1000 × 1000 (a caixa `MINBASE`/`MAXBASE`), esticado até a medida
  do item (`LIMITS`); o contorno que já vem em milímetros (caixa-base 1 × 1) fica como está;
- a laje fina de MDF (painel, tampo) é chapa do plano de corte; a de pedra (granito) não;
- a persiana da janela só existe no catálogo do Promob: marcador em arame;
- sem par no catálogo do addon, a cor sai do nome (jacarandá, granito preto).
"""
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import para_v2, texturas

from test_071_furo import converter as converter_furo
from test_071_referencial import converter, por_nome


def laje(id_, nome, limites, base, pontos, altura, material, normal=None, camada='Salas'):
    (a, b, c), (e, f, g) = limites
    (bx0, by0), (bx1, by1) = base
    forma = ''.join(f'<POINT2DG X="{x}" Y="{y}" NAME="" />' for x, y in pontos)
    extra = (f'<REGIONS><REGION ID="FACE"><MATERIAL ID="{material}" /></REGION></REGIONS>'
             f'<GEOMETRY INVERTEDX="N" INVERTEDY="N"><PROFILE><POINT2DGM NAME="" /><POINT2DGM Y="1" NAME="" /></PROFILE>'
             f'<SHAPE>{forma}</SHAPE></GEOMETRY>')
    xml = ps._item('GEOMETRY', id_, base=(0, 0, 0), dim=(e - a, altura, f - b), rot=0, nome=nome, camada=camada,
                   extra=extra, normal=normal)
    lim = (f'<LIMITS><MIN X="{a}" Y="{b}" Z="{c}" /><MAX X="{e}" Y="{f}" Z="{g}" />'
           f'<MINBASE X="{bx0}" Y="{by0}" /><MAXBASE X="{bx1}" Y="{by1}" /></LIMITS>')
    return xml.replace('<LAYER ', lim + '<LAYER ', 1)


QUADRADO = [(0, 0), (1000, 0), (1000, -1000), (0, -1000)]


class PaineisTest(unittest.TestCase):
    def test_painel_em_molde_esticado_ate_a_medida(self):
        painel = laje('pai', 'Painel', ((0, -594, 0), (2450, 0, 15)), ((0, -1000), (1000, 0)), QUADRADO, 15,
                      'dur_des_hor_nogueira_caiena')
        no = por_nome(converter([painel])['complemento']['moveis'], 'Painel')
        xs, ys = [x for x, _ in no['contorno']], [y for _, y in no['contorno']]
        self.assertEqual((round(max(xs) - min(xs)), round(max(ys) - min(ys))), (2450, 594))

    def test_contorno_em_milimetros_fica_como_esta(self):
        tampo = laje('tam', 'GEOMETRIA', ((0, -600, 0), (2151, 0, 30)), ((0, 0), (1, 1)),
                     [(0, 0), (2151, 0), (2151, -600), (0, -600)], 30, 'granito_preto_ouro preto', camada='Geometria')
        no = por_nome(converter([tampo])['complemento']['moveis'], 'GEOMETRIA')
        self.assertEqual(round(max(x for x, _ in no['contorno'])), 2151)
        self.assertNotIn('chapa', no)                                        # pedra não é chapa

    def test_painel_de_mdf_entra_no_corte(self):
        painel = laje('pai', 'Painel', ((0, -594, 0), (2450, 0, 15)), ((0, -1000), (1000, 0)), QUADRADO, 15,
                      'dur_des_hor_nogueira_caiena')
        chapa = por_nome(converter([painel])['complemento']['moveis'], 'Painel')['chapa']
        self.assertEqual((chapa['comprimento'], chapa['largura'], chapa['espessura'], chapa['componente']),
                         (2450.0, 594.0, 15.0, 'TAMPON'))
        self.assertEqual(chapa['material'], 'Nogueira Caiena Design (Duratex)')

    def test_persiana_vira_marcador(self):
        caixa = ps._item('MODULO', 'porta_105', base=(0, 0, 2180), dim=(2000, 1084, 192), rot=0, nome='Caixa Persiana',
                         camada='Decore-Aberturas', extra='<COMPONENTDEFINITIONCOLLECTION><COMPONENTDEFINITION ID="0" '
                                                          'IDMATERIAL="cin_cor_000" /></COMPONENTDEFINITIONCOLLECTION>')
        no = por_nome(converter([caixa])['complemento']['moveis'], 'Caixa Persiana')
        self.assertTrue(no.get('catalogo'))

    def test_face_do_trecho_no_lado_certo(self):
        # 2 trechos: faces 0 e 1 no percurso (externa no addon), 3 e 4 do outro lado, em ordem inversa
        parede = ps._parede([(0, 0, 150), (3000, 0, 150), (3000, 2500, 150)], 2700)
        faces = ''.join(f'<REGION ID="PAREDE_FACE_PERFIL_MOVIMENTACAO_INDICEFORMA_{i}"><MATERIAL ID="{m}" /></REGION>'
                        for i, m in ((0, 'reboco'), (1, 'par_tijolos_tijolos 003'), (3, 'reboco'), (4, 'granito_preto')))
        parede = parede.replace('</REGION></REGIONS>', '</REGION>' + faces + '</REGIONS>', 1)
        r = converter_furo([parede])
        materiais = {m['id']: m['nome'] for m in r['documento']['materiais']}
        s0, s1 = r['documento']['paredes'][0]['segmentos']
        self.assertEqual((materiais.get(s1.get('material_externo_id')), s1.get('material_interno_id')),
                         ('par_tijolos_tijolos 003', None))
        self.assertEqual((s0.get('material_externo_id'), materiais.get(s0.get('material_interno_id'))),
                         (None, 'granito_preto'))

    def test_cor_pelo_nome(self):
        self.assertEqual(texturas.cor_por_nome('jacaranda'), (0x4B, 0x2A, 0x1A))
        self.assertEqual(texturas.cor_por_nome('granito_preto_ouro preto'), (0x22, 0x22, 0x22))
        self.assertIsNone(texturas.cor_por_nome('cin_cor_000'))
        self.assertTrue(para_v2._pedra('granito_bege_quartiziter'))


if __name__ == '__main__':
    unittest.main()
