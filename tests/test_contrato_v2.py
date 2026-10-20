"""065 T113: validação fechada e ida e volta com oráculo TypeScript, sem Blender."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path
import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2.validacao import validar_documento
from caffmob_draw.caffmob.v2.serializacao import ler_documento, serializar, DocumentoInvalido, conferir_bytes

PASTA = Path(__file__).parent / 'casos_ouro_v2'


def casos(prefixo):
    return [(p, json.loads(p.read_text(encoding='utf-8'))) for p in sorted(PASTA.glob(prefixo + '*.json'))]


class ContratoV2(unittest.TestCase):
    def test_somas_e_inventario(self):
        # A mesma ordenação ordinal do SHA256SUMS gerado pelo TypeScript.
        linhas = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(PASTA.glob('*.json'))]
        self.assertEqual('\n'.join(linhas) + '\n', (PASTA / 'SHA256SUMS').read_text())
        self.assertGreaterEqual(len(casos('invalido-')), 15)

    def test_fontes_do_oraculo(self):
        raiz = PASTA.parents[2] / 'caff-mobi'
        if not raiz.exists():
            self.skipTest('Fontes do MOBI só presentes na entrega da feature.')
        for arquivo, soma in json.loads((PASTA / 'fontes.json').read_text()).items():
            self.assertEqual(hashlib.sha256((raiz / arquivo).read_bytes()).hexdigest(), soma, arquivo)

    def test_referencia_rica_canonica_sem_perda(self):
        c = casos('referencia-')[0][1]
        original = copy.deepcopy(c['entrada'])
        self.assertEqual(validar_documento(original), [])
        d = ler_documento(json.dumps(original, ensure_ascii=False))
        self.assertEqual(d, c['esperado'])
        self.assertEqual(serializar(d), c['canonico'])
        self.assertEqual(ler_documento(serializar(d)), original)
        self.assertEqual(original, c['entrada'])

    def test_paredes_validas_e_arrays_na_ordem(self):
        for p, c in casos('parede-'):
            with self.subTest(caso=p.name):
                self.assertEqual(validar_documento(c['entrada']), [])
                self.assertEqual(ler_documento(serializar(c['entrada'])), c['entrada'])

    def test_json_invalido_e_limite_antes_do_parse(self):
        for texto in ('{', '[NaN]', '{"a":Infinity}'):
            with self.assertRaises(DocumentoInvalido) as exc:
                ler_documento(texto)
            self.assertEqual(exc.exception.erros[0]['codigo'], 'JSON_INVALIDO')
        self.assertEqual(conferir_bytes(' ' * 1048576), [])
        rico = casos('referencia-')[0][1]['entrada']
        texto = serializar(rico)
        no_teto = texto + ' ' * (1048576 - len(texto.encode('utf-8')))
        self.assertEqual(ler_documento(no_teto), rico)
        with self.assertRaises(DocumentoInvalido) as exc:
            ler_documento(' ' * 1048577)
        self.assertEqual(exc.exception.erros[0]['codigo'], 'DOCUMENTO_GRANDE_DEMAIS')

    def test_numeros_canonicos_e_sem_arredondamento(self):
        self.assertEqual(serializar([1.0, -0.0, 1e-7, 1e-6, 1e20, 1e21, 0.45]),
                         '[1,0,1e-7,0.000001,100000000000000000000,1e+21,0.45]')
        c = copy.deepcopy(casos('referencia-')[0][1]['entrada'])
        c['itens_externos'][0]['posicao']['x'] = 123.456789
        self.assertEqual(ler_documento(serializar(c)), c)

    def test_nao_finitos_ciclos_e_tipos(self):
        for valor in (math.nan, math.inf, -math.inf, True, None, '150'):
            d = copy.deepcopy(casos('referencia-')[0][1]['entrada'])
            d['paredes'][0]['segmentos'][0]['comprimento'] = valor
            self.assertTrue(any(e['codigo'] == 'ESQUEMA' for e in validar_documento(d)))
        d = {}; d['ciclo'] = d
        self.assertEqual(validar_documento(d)[0]['codigo'], 'ESQUEMA')

    def test_validacao_nao_muta(self):
        c = copy.deepcopy(casos('referencia-')[0][1]['entrada'])
        antes = serializar(c)
        validar_documento(c)
        self.assertEqual(serializar(c), antes)


# Um teste por documento permite identificar precisamente a regressão no unittest.
for _p, _c in casos('invalido-'):
    def _teste(self, caso=_c):
        self.assertEqual(validar_documento(caso['entrada']), caso['esperado'])
    setattr(ContratoV2, 'test_' + _p.stem.replace('-', '_'), _teste)
