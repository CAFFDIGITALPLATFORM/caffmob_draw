"""073 (RN-04 a RN-06, RN-09, RF-04, RF-05, RF-08, RF-10): o importador do Promob grava textura PBR em vez de cor.

- parede com face de tijolo: material `tipo='textura'` no documento v2, com o UUID do manifesto, o tamanho real em
  `escala_mm` e o nome original do Promob; o documento valida;
- o mesmo arquivo importado duas vezes dá o mesmo `textura_id`;
- puxador de inox no complemento recebe a textura PBR (`textura_catalogo`); nome sem casamento continua em cor;
- relatório: acabamentos com textura, aproximados e em cor, e o aviso de cada aproximação;
- sem manifesto (como nos testes da 071), nada muda.
"""
import unittest

import _pbr_sintetico as ps
import _promob_sintetico as ps_promob
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.promob import leitor, para_v2
from caffmob_draw.texture_library import pbr_core


def converter(itens, pbr=True):
    principal = ps_promob._ambiente(itens, nome='Texturas')
    projeto = leitor.abrir(ps_promob.zip_de(ps_promob.entradas(principal=principal))).projeto(0)
    return para_v2.converter(projeto, catalogo=[], pbr=ps.manifesto() if pbr else None)


def parede_com_faces(faces):
    parede = ps_promob._parede([(0, 0, 150), (3000, 0, 150), (3000, 2500, 150)], 2700)
    regioes = ''.join(f'<REGION ID="PAREDE_FACE_PERFIL_MOVIMENTACAO_INDICEFORMA_{i}"><MATERIAL ID="{m}" /></REGION>'
                      for i, m in faces)
    return parede.replace('</REGION></REGIONS>', '</REGION>' + regioes + '</REGIONS>', 1)


def puxador(material, id_='pux'):
    return ps_promob._item('MODULO', id_, base=(500, 0, 900), dim=(160, 20, 30), rot=0, nome='Puxador',
                           camada='Default', material=material)


class ImportadorPbrTest(unittest.TestCase):
    def test_parede_de_tijolo_vira_textura(self):
        r = converter([parede_com_faces([(0, 'reboco'), (1, 'par_tijolos_tijolos 003')])])
        doc = r['documento']
        self.assertEqual(validar_documento(doc), [])
        tijolo = next(m for m in doc['materiais'] if m['nome'] == 'par_tijolos_tijolos 003')
        self.assertEqual((tijolo['tipo'], tijolo['textura_id'], tijolo['escala_mm']),
                         ('textura', pbr_core.uuid_de('tijolo-aparente'), {'largura': 1200, 'altura': 1200}))
        s1 = doc['paredes'][0]['segmentos'][1]
        self.assertEqual(s1['material_externo_id'], tijolo['id'])

    def test_mesmo_uuid_em_duas_importacoes(self):
        ids = [next(m['textura_id'] for m in converter([parede_com_faces([(1, 'granito_preto')])])['documento']
                    ['materiais'] if m['tipo'] == 'textura') for _ in range(2)]
        self.assertEqual(ids[0], ids[1])
        self.assertEqual(ids[0], pbr_core.uuid_de('granito-preto'))

    def test_sem_casamento_continua_cor(self):
        doc = converter([parede_com_faces([(1, 'cin_cor_000_x')])])['documento']
        self.assertTrue(all(m['tipo'] == 'cor' for m in doc['materiais']))

    def test_sem_manifesto_nada_muda(self):
        doc = converter([parede_com_faces([(1, 'par_tijolos_tijolos 003')])], pbr=False)['documento']
        self.assertTrue(all(m['tipo'] == 'cor' for m in doc['materiais']))

    def test_puxador_de_inox(self):
        r = converter([puxador('inox escovado')])
        dado = r['complemento']['materiais']['inox escovado']
        self.assertEqual((dado['textura_catalogo'], dado['nome']), (pbr_core.uuid_de('inox-escovado'), 'inox escovado'))

    def test_relatorio_com_aproximada(self):
        r = converter([parede_com_faces([(1, 'granito verde ubatuba')]), puxador('cin_cor_000', 'p2')])
        t = r['relatorio']['texturas']
        self.assertEqual(t['aproximadas'], [{'material': 'granito verde ubatuba', 'textura': 'granito-preto'}])
        self.assertGreaterEqual(t['com_textura'], 1)
        self.assertTrue(any('Textura aproximada' in a for a in r['relatorio']['avisos']))


if __name__ == '__main__':
    unittest.main()
