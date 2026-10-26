"""071, 5ª auditoria: chapas prontas para o plano de corte, portas e gavetas que abrem, e as câmeras do Promob.

- Chapa: a regra do OpenMob (`classify_leaf`: espessura até 40 mm, largura a partir de 60 mm, com material),
  corrigida: porta com filhos entra, vidro e decoração não, papel pelo nome, veio do código do Promob;
- Abertura: o OPENSERVICE (Door, Dumping, Sliding, Drawer) com as fórmulas do Promob (`@($I$?-$WIDTH$:$WIDTH$)`);
- Câmeras: `VIEWPOINTCOLLECTION` e a vista dinâmica (`VIEWPOINT`).
"""
import unittest

import _promob_sintetico as ps
from caffmob_draw.promob import leitor, para_v2

from test_071_referencial import caixa, converter, por_nome


def abre(tipo, **attrs):
    extra = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
    return f'<OPENSERVICE TYPE="{tipo}" {extra} />'


def item_falso(w=400, h=700, d=18, inv=False):
    return leitor.Item('MODULO', 'x', 'x', '', True, (0, 0, 0), 0, w, h, d, invertido=inv)


class FormulasTest(unittest.TestCase):
    def test_formulas_do_promob(self):
        casos = [('@($I$?-$WIDTH$:$WIDTH$)', False, 400.0), ('@($I$?-$WIDTH$:$WIDTH$)', True, -400.0),
                 ('-$DEPTH$', False, -18.0), ('$W$-50', False, 350.0), ('@($I$? 10:-10)', True, 10.0),
                 ('@($I$?-($H$+$D$/2):$H$-$D$/2)', False, 691.0), ('90', False, 90.0)]
        for formula, inv, esperado in casos:
            self.assertEqual(para_v2.avaliar(formula, item_falso(inv=inv)), esperado, formula)

    def test_formula_do_catalogo_nao_vale(self):
        for formula in ('#%p.p.$opening.max$%#', "@(#P.P.MOVEDOBRADICA# == 'TRUE' ? 0 : -4)", '$X$+1',
                        '__import__("os")', ''):
            self.assertIsNone(para_v2.avaliar(formula, item_falso()), formula)


class ChapaEAberturaTest(unittest.TestCase):
    def converter_balcao(self):
        porta = ps._item('MODULO', 'porta', base=(0, 0, 0), dim=(400, 700, 18), rot=0, nome='Porta Reta',
                         material='Dur_Cri_titanio_v',
                         extra=abre('Door', MAX='110', X='@($I$?-$WIDTH$:$WIDTH$)', Y='-$DEPTH$', CURRENTVALUE='0'),
                         filhos=[ps._item('MODULO', 'ace_fer_dob', base=(380, 0, 100), dim=(31, 42, 2), nome='Dobradiça',
                                          material='dec_met_lis_alu', extra=abre('Door', X='10', CURRENTVALUE='0'))])
        caixa = ps._item('MODULO', 'gav', base=(0, 0, 720), dim=(400, 150, 450), rot=0, nome='Gaveta Externa',
                         extra=abre('Drawer', MAX='400', CURRENTVALUE='100'), filhos=[
                             ps._item('MODULO', 'lg', base=(0, 0, 720), dim=(15, 120, 400), rot=0,
                                      nome='Lateral de Gaveta 400', material='cin_cor_000')])
        frente = ps._item('MODULO', 'fg', base=(0, 18, 715), dim=(400, 160, 18), rot=0, nome='Frente Gaveta',
                          material='mas_carvalho_mel_h', extra=abre('Drawer', MAX='400', CURRENTVALUE='100'))
        vidro = ps._item('MODULO', 'pv', base=(0, 0, 1000), dim=(400, 300, 6), rot=0, nome='Painel Vidro',
                         material='vidro_fume')
        lateral = ps._item('MODULO', 'lat', base=(0, 0, 0), dim=(15, 2000, 550), rot=0, nome='Lateral 15mm',
                           material='Dur_Cri_titanio_v')
        balcao = ps._item('MODULO', 'bal', base=(0, 0, 0), dim=(800, 2000, 550), rot=0, nome='Balcão',
                          filhos=[lateral, porta, caixa, frente, vidro])
        return converter([balcao])

    def test_chapas_prontas_para_o_corte(self):
        r = self.converter_balcao()
        moveis = r['complemento']['moveis']
        lateral = por_nome(moveis, 'Lateral 15mm')['chapa']
        self.assertEqual((lateral['comprimento'], lateral['largura'], lateral['espessura']), (2000.0, 550.0, 15.0))
        self.assertEqual((lateral['componente'], lateral['modulo'], lateral['veio']), ('LAT', 'Balcão', 'VERTICAL'))
        self.assertEqual(lateral['material'], 'Titanio Cristallo (Duratex)')
        porta = por_nome(moveis, 'Porta Reta')
        self.assertEqual((porta['chapa']['componente'], porta['chapa']['veio']), ('POR', 'VERTICAL'))   # com filhos
        frente = por_nome(moveis, 'Frente Gaveta')['chapa']
        self.assertEqual((frente['componente'], frente['veio']), ('FRENTE_GAVETA', 'VERTICAL'))   # _h na peça deitada
        self.assertNotIn('chapa', por_nome(moveis, 'Painel Vidro'))                            # vidro não é MDF
        self.assertNotIn('chapa', por_nome(moveis, 'Dobradiça'))                               # ferragem

    def test_portas_e_gavetas_abrem(self):
        r = self.converter_balcao()
        moveis = r['complemento']['moveis']
        porta = por_nome(moveis, 'Porta Reta')['mecanismo']
        self.assertEqual((porta['tipo'], porta['maximo'], porta['abertura']), ('HINGE', 110.0, 0.0))
        self.assertEqual(tuple(round(v) for v in porta['eixo']), (400, -18, 0))
        self.assertNotIn('mecanismo', por_nome(moveis, 'Dobradiça'))         # dentro da porta: corre junto
        caixa = por_nome(moveis, 'Gaveta Externa')
        self.assertEqual((caixa['mecanismo']['tipo'], caixa['mecanismo']['abertura']), ('DRAWER', 0.25))
        self.assertEqual(tuple(round(v) for v in caixa['mecanismo']['sentido']), (0, -1, 0))
        self.assertIn('Frente Gaveta', [f['nome'] for f in caixa['filhos']])  # a frente abre com a caixa
        self.assertEqual(r['relatorio']['moveis_que_abrem'], 2)

    def test_pose_aberta_do_projeto(self):
        """O Promob grava a gaveta deslocada e a porta girada (a porta sem ROTATION herda o ângulo do pai)."""
        porta = ps._item('MODULO', 'porta', base=(80.94824, 1024.178, 1545), dim=(440, 1060, 15), nome='Porta Reta',
                         material='m', limites=((-440, -15, 0), (0, 0, 1060)),
                         extra=abre('Door', MAX='90', X='@($I$?-$W$+$D$/2:$W$-$D$/2)', Y='-$D$/2', CURRENTVALUE='90'))
        porta = porta.replace('ID="porta"', 'ID="porta" INVERTED="true"')
        gaveta = ps._item('MODULO', 'gav', base=(176, 2847, 83), dim=(394, 247, 15), rot=90, nome='Frente Reta',
                          material='m', limites=((0, -15, 0), (394, 0, 247)),
                          extra=abre('Drawer', MAX='400', CURRENTVALUE='400'))
        armario = ps._item('MODULO', 'arm', base=(-709.0518, 1454.178, 1540), dim=(450, 1070, 350), rot=90,
                           nome='Armário', limites=((-450, -350, 0), (0, 0, 1070)), filhos=[porta])
        balcao = ps._item('MODULO', 'bal', base=(-224, 2844, 80), dim=(400, 670, 420), rot=90, nome='Balcão',
                          limites=((0, -420, 0), (400, 0, 670)), filhos=[gaveta])
        r = converter([armario, balcao])
        moveis = r['complemento']['moveis']
        m = por_nome(moveis, 'Porta Reta')['mecanismo']
        self.assertEqual((m['abertura'], round(m['fechar']['angulo'])), (1.0, 90))
        lo, hi = caixa(por_nome(moveis, 'Porta Reta'))
        self.assertEqual((lo[0], hi[0]), (-359, 81))           # aberta a 90°: sai da quina do armário
        g = por_nome(moveis, 'Frente Reta')['mecanismo']
        self.assertEqual(tuple(round(v) for v in g['fechar']['translacao']), (-400, 0, 0))   # volta 400 mm para dentro

    def test_cameras_do_ambiente(self):
        vistas = ('<VIEWPOINTCOLLECTION><VIEWPOINT ID="CAM 0001" NAME="CAM 0001" ZNEAR="50" ZFAR="50000" '
                  'PERSPECTIVA="Y" ORTHOL="-2058" ORTHOR="2058"><FOV>51.9</FOV><PTTARGET X="4625" Y="1453" Z="1200" />'
                  '<PTOBSERVER X="306" Y="3729" Z="1810" /><PTUP Z="1" /></VIEWPOINT></VIEWPOINTCOLLECTION>'
                  '<VIEWPOINT ID="CAM 0002" NAME="CAM 0002" ZNEAR="1" ZFAR="50000" PERSPECTIVA="Y"><FOV>51.9</FOV>'
                  '<PTTARGET X="1552" Y="3270" Z="-328" /><PTOBSERVER X="2042" Y="5251" Z="565.5" /></VIEWPOINT>')
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([]).replace(
            '<AMBIENT3D>', '<AMBIENT3D>' + vistas)
        projeto = leitor.abrir(ps.zip_de(mapa)).projeto(1)
        self.assertEqual([(c.nome, c.atual) for c in projeto.cameras], [('CAM 0001', False), ('CAM 0002', True)])
        c = projeto.cameras[0]
        self.assertEqual((c.observador, c.alvo, c.fov, c.corte_anterior, c.largura_ortogonal),
                         ((306, 3729, 1810), (4625, 1453, 1200), 51.9, 50.0, 4116.0))
        self.assertEqual(projeto.cameras[1].alvo[2], -328)                    # a Altura alvo da Vista Dinâmica
        r = para_v2.converter(projeto)
        self.assertEqual((len(r['complemento']['cameras']), r['relatorio']['cameras']), (2, 2))

    def test_camadas_desligadas(self):
        estado = ('<LAYERSTATUSMANAGER><LAYERSTATUSCOLLECTION><LAYERSTATUS LAYER="PORTAS_Visual" ON="N" />'
                  '<LAYERSTATUS LAYER="Default_Visual" SELECTED="Y" /><LAYERSTATUS LAYER="Decore_Area" ON="N" />'
                  '</LAYERSTATUSCOLLECTION></LAYERSTATUSMANAGER>')
        mapa = ps.entradas()
        mapa['solucao\\container1\\document2\\document2.ambient3d'] = ps._ambiente([]).replace(
            '<AMBIENT3D>', '<AMBIENT3D>' + estado)
        projeto = leitor.abrir(ps.zip_de(mapa)).projeto(1)
        self.assertEqual(projeto.camadas_ocultas, frozenset({'PORTAS'}))
        self.assertEqual(para_v2.converter(projeto)['complemento']['camadas_ocultas'], ['PORTAS'])


if __name__ == '__main__':
    unittest.main()
