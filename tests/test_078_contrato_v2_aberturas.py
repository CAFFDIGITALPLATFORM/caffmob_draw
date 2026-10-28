"""078 T007/T014: validação do contrato v2 para modelo e material em aberturas[]."""
import copy
import json
import unittest
from pathlib import Path
import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2.contrato import (
    MATERIAIS_DE_ABERTURA,
    MODELOS_DE_ABERTURA,
    MODELOS_DE_JANELA,
    MODELOS_DE_PORTA,
    PADRAO_ABERTURA,
)
from caffmob_draw.caffmob.v2.serializacao import ler_documento, serializar
from caffmob_draw.caffmob.v2.validacao import validar_documento

PASTA = Path(__file__).parent / 'casos_ouro_v2'


def _documento_base():
    p = sorted(PASTA.glob('referencia-*.json'))[0]
    return copy.deepcopy(json.loads(p.read_text(encoding='utf-8'))['entrada'])


class Test078ContratoV2Aberturas(unittest.TestCase):
    def test_constantes_30_modelos_3_materiais(self):
        self.assertEqual(len(MODELOS_DE_PORTA), 10)
        self.assertEqual(len(MODELOS_DE_JANELA), 20)
        self.assertEqual(len(MODELOS_DE_ABERTURA), 30)
        self.assertEqual(MATERIAIS_DE_ABERTURA, ('madeira', 'aluminio', 'blindex'))
        self.assertEqual(PADRAO_ABERTURA['DOOR'], {'modelo': 'porta_giro_almofadada', 'material': 'madeira'})
        self.assertEqual(PADRAO_ABERTURA['WINDOW'], {'modelo': 'janela_correr_2f', 'material': 'aluminio'})

    def test_aceita_todos_os_10_modelos_de_porta_e_20_de_janela(self):
        base = _documento_base()
        seg_id = base['paredes'][0]['segmentos'][0]['id']
        for modelo in MODELOS_DE_PORTA:
            for material in MATERIAIS_DE_ABERTURA:
                d = copy.deepcopy(base)
                d['aberturas'] = [{
                    'id': '07800000-0000-4000-8000-000000000001',
                    'tipo': 'DOOR',
                    'segmento_id': seg_id,
                    'posicao': 100,
                    'largura': 800,
                    'altura': 2100,
                    'peitoril': 0,
                    'modelo': modelo,
                    'material': material,
                }]
                self.assertEqual(validar_documento(d), [], f"Falhou para {modelo}/{material}")
                self.assertEqual(ler_documento(serializar(d)), d)

        for modelo in MODELOS_DE_JANELA:
            for material in MATERIAIS_DE_ABERTURA:
                d = copy.deepcopy(base)
                d['aberturas'] = [{
                    'id': '07800000-0000-4000-8000-000000000002',
                    'tipo': 'WINDOW',
                    'segmento_id': seg_id,
                    'posicao': 100,
                    'largura': 1200,
                    'altura': 1000,
                    'peitoril': 1000,
                    'modelo': modelo,
                    'material': material,
                }]
                self.assertEqual(validar_documento(d), [], f"Falhou para {modelo}/{material}")
                self.assertEqual(ler_documento(serializar(d)), d)

    def test_recusa_cruzamento_tipo_modelo_e_valores_invalidos(self):
        base = _documento_base()
        seg_id = base['paredes'][0]['segmentos'][0]['id']

        d1 = copy.deepcopy(base)
        d1['aberturas'] = [{
            'id': '07800000-0000-4000-8000-000000000001',
            'tipo': 'DOOR',
            'segmento_id': seg_id,
            'posicao': 100,
            'largura': 800,
            'altura': 2100,
            'peitoril': 0,
            'modelo': 'janela_correr_2f',
        }]
        self.assertEqual(
            validar_documento(d1),
            [{'caminho': 'aberturas[0].modelo', 'codigo': 'ESQUEMA', 'mensagem': 'Valor fora do formato, enumeração ou faixa permitida.'}],
        )

        d2 = copy.deepcopy(base)
        d2['aberturas'] = [{
            'id': '07800000-0000-4000-8000-000000000002',
            'tipo': 'WINDOW',
            'segmento_id': seg_id,
            'posicao': 100,
            'largura': 1200,
            'altura': 1000,
            'peitoril': 1000,
            'modelo': 'porta_giro_lisa',
        }]
        self.assertEqual(
            validar_documento(d2),
            [{'caminho': 'aberturas[0].modelo', 'codigo': 'ESQUEMA', 'mensagem': 'Valor fora do formato, enumeração ou faixa permitida.'}],
        )

        d3 = copy.deepcopy(base)
        d3['aberturas'] = [{
            'id': '07800000-0000-4000-8000-000000000001',
            'tipo': 'DOOR',
            'segmento_id': seg_id,
            'posicao': 100,
            'largura': 800,
            'altura': 2100,
            'peitoril': 0,
            'material': 'pvc_invalido',
        }]
        self.assertEqual(
            validar_documento(d3),
            [{'caminho': 'aberturas[0].material', 'codigo': 'ESQUEMA', 'mensagem': 'Valor fora do formato, enumeração ou faixa permitida.'}],
        )

    def test_retrocompatibilidade_omissao_modelo_material(self):
        base = _documento_base()
        self.assertTrue(len(base['aberturas']) > 0)
        for ab in base['aberturas']:
            self.assertNotIn('modelo', ab)
            self.assertNotIn('material', ab)
        self.assertEqual(validar_documento(base), [])


if __name__ == '__main__':
    unittest.main()
