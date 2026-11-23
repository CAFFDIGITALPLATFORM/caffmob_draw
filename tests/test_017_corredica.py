"""017 (T038; RN-08, RF-10, RF-19): a corrediça do núcleo, fora do plano de chapa.

Teste puro, sem `bpy`: as duas corrediças de cada gaveta, as três partes de cada conjunto com `papel` vazio e
`ferragem` preenchida, o trilho externo na lateral do vão, o interno na caixa da gaveta, o recuo com a base da
deslizante por dentro, as mesmas medidas no conjunto de reserva e a ausência da corrediça na lista de peças e na
conferência de chapa.
"""

import unittest

import _bootstrap  # noqa: F401

from caffmob_draw.armario_v2 import build, chapas, conferencia, corredica, gavetas, resumo, spec

CAIXA = ((-485.0, -500.0, 20.0), (485.0, -20.0, 200.0))


def _por_ferragem(itens, ferragem):
    return [item for item in itens if item.get('ferragem') == ferragem]


def _tamanho(item):
    (x0, y0, z0), (x1, y1, z1) = item['box']
    return (round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3))


class CorredicaTest(unittest.TestCase):
    def test_duas_corredicas_por_gaveta(self):
        itens = corredica.pecas(CAIXA, curso=350.0)
        self.assertEqual(len(_por_ferragem(itens, corredica.TRILHO_EXT)), 2)
        self.assertEqual(len(_por_ferragem(itens, corredica.TRILHO_INT)), 2)
        self.assertEqual(len(_por_ferragem(itens, corredica.GAIOLA)), 2)
        self.assertEqual({item['lado'] for item in itens}, {'ESQUERDA', 'DIREITA'})
        self.assertEqual(len(itens), 6)

    def test_papel_vazio_e_ferragem_preenchida(self):
        itens = corredica.pecas(CAIXA, curso=350.0, indice=3)
        self.assertEqual({item['papel'] for item in itens}, {''})
        self.assertEqual([item['ferragem'] for item in itens],
                         [corredica.TRILHO_EXT, corredica.TRILHO_INT, corredica.GAIOLA] * 2)
        self.assertTrue(all('gaveta 3' in item['nome'] for item in itens))
        self.assertTrue(all(item['material'] == 'FERRAGEM' for item in itens))

    def test_trilho_externo_na_lateral_do_vao_e_interno_na_caixa(self):
        itens = corredica.pecas(CAIXA)
        esquerdo = _por_ferragem(itens, corredica.TRILHO_EXT)[0]
        interno = _por_ferragem(itens, corredica.TRILHO_INT)[0]
        self.assertEqual(esquerdo['box'], ((-493.5, -220.0, 92.5), (-485.0, -20.0, 127.5)))
        self.assertEqual(_tamanho(esquerdo), (8.5, 200.0, 35.0))
        self.assertEqual(interno['box'], ((-485.0, -193.5, 100.0), (-479.0, -20.0, 120.0)))
        self.assertEqual(_tamanho(interno), (6.0, 173.5, 20.0))
        direito = _por_ferragem(itens, corredica.TRILHO_EXT)[1]
        self.assertEqual(direito['box'][0][0], 485.0)             # por fora da caixa, à direita
        self.assertEqual(direito['box'][0][0], CAIXA[1][0])

    def test_gaiola_a_meio_curso(self):
        gaiola = _por_ferragem(corredica.pecas(CAIXA), corredica.GAIOLA)[0]
        self.assertEqual(_tamanho(gaiola), (5.8, 60.0, 3.92))
        (x0, _y0, _z0), (x1, y1, _z1) = gaiola['box']
        self.assertEqual((round(x0, 2), round(x1, 2)), (-490.8, -485.0))
        centro = (gaiola['box'][0][1] + y1) / 2.0
        self.assertAlmostEqual(centro, (CAIXA[0][1] + CAIXA[1][1]) / 2.0)     # meio curso
        self.assertEqual(gaiola['curso'], 0.0)

    def test_curso_do_trilho_interno_e_da_gaiola(self):
        itens = corredica.pecas(CAIXA, curso=350.0)
        self.assertEqual(_por_ferragem(itens, corredica.TRILHO_EXT)[0]['curso'], 0.0)
        self.assertTrue(all(item['curso'] == 350.0 for item in _por_ferragem(itens, corredica.TRILHO_INT)))
        self.assertTrue(all(item['curso'] == 350.0 for item in _por_ferragem(itens, corredica.GAIOLA)))

    def test_recuo_com_a_base_da_deslizante_por_dentro(self):
        livre = spec.Spec()
        dentro = spec.Spec(deslizante_ativa=True, deslizante_base='DENTRO', trilho_profundidade=70.0)
        frente = spec.Spec(deslizante_ativa=True, deslizante_base='FRENTE', trilho_profundidade=70.0)
        self.assertEqual(corredica.recuo(livre), 0.0)
        self.assertEqual(corredica.recuo(dentro), 70.0)
        self.assertEqual(corredica.recuo(frente), 0.0)
        self.assertEqual(corredica.recuo(None), 0.0)

    def test_conjunto_de_reserva_com_as_mesmas_medidas(self):
        """O `build` usa as caixas de `corredica` quando o OBJ falta: as duas listas têm de bater."""
        armario = spec.Spec(largura=1000.0, altura=2000.0, profundidade=560.0,
                            lateral_esq_ativa=True, lateral_dir_ativa=True,
                            base_inf_ativa=True, base_sup_ativa=True)
        gaveta = gavetas.bloco(700.0, 1, vao='s0')[0]
        do_build = _por_ferragem(build.pecas(armario, (), [gaveta]), corredica.TRILHO_EXT)
        self.assertEqual(len(do_build), 2)                       # o bloco liga `corredica_3d` por padrão
        reserva = corredica.pecas(((485.0, -538.0, 20.0), (1000.0, -30.0, 326.5)))
        for ferragem in corredica.FERRAGENS:
            self.assertEqual(_tamanho(_por_ferragem(reserva, ferragem)[0]),
                             (corredica.MEDIDAS[ferragem]['espessura'],
                              corredica.MEDIDAS[ferragem]['comprimento'],
                              corredica.MEDIDAS[ferragem]['altura']))

    def test_fora_da_lista_de_pecas_e_da_conferencia(self):
        itens = corredica.pecas(CAIXA)
        pecas = [conferencia.Peca(item['papel'], item['nome'], *build.medidas_de_corte(item), item['espessura'])
                 for item in itens]
        self.assertEqual(chapas.pode_gerar(chapas.padrao()), [])
        self.assertEqual(resumo.lista_de_pecas(pecas, chapas.padrao()), [])
        self.assertEqual(conferencia.conferir(pecas, chapas.padrao()), [])


if __name__ == '__main__':
    unittest.main()
