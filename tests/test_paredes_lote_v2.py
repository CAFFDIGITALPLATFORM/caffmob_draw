"""065 T133: operações em lote e seleção por retângulo contra os casos-ouro do TypeScript (T131)."""
import hashlib
import json
from pathlib import Path
import unittest
import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2 import paredes_edicao as pe
from caffmob_draw.walls2d.studio_selecao import combinar, selecionar_no_retangulo
from test_paredes_edicao_v2 import maior_diferenca

PASTA = Path(__file__).resolve().parent / 'casos_ouro_v2' / 'lote'
MOBI = Path(__file__).resolve().parents[2] / 'caff-mobi'


def casos():
    return [(p, json.loads(p.read_text(encoding='utf-8'))) for p in sorted(PASTA.glob('*.json')) if p.name != 'fontes.json']


def uuid(n):
    return f'06400000-0000-4000-8000-{n:012d}'


def executar(c):
    d, p, op = c['entrada'], c['parametros'], c['operacao']
    if op == 'editarParedesEmLote':
        return pe.editar_paredes_em_lote(d, p['piso'], p['ids'], p.get('edicao', {}))
    if op == 'excluirParedesEmLote':
        n = iter(range(800, 900))
        return pe.excluir_paredes_em_lote(d, p['piso'], p['ids'], lambda: uuid(next(n)),
                                          confirmar_dependencias=bool(p.get('confirmar_dependencias')))
    if op == 'moverParedesEmLote':
        return pe.mover_paredes_em_lote(d, p['piso'], p['ids'], p.get('delta', dict(x=200, y=-150)))
    if op == 'selecionarNoRetangulo':
        return selecionar_no_retangulo(d, p['piso'], p['a'], p['b'], p['toca'])
    raise AssertionError('Operação sem porte: ' + op)


class ParedesEmLoteV2(unittest.TestCase):
    def test_somas(self):
        linhas = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(PASTA.glob('*.json'))]
        self.assertEqual('\n'.join(linhas) + '\n', (PASTA / 'SHA256SUMS').read_text())

    def test_fontes_do_oraculo(self):
        if not MOBI.is_dir():
            self.skipTest('Fontes do MOBI só presentes na entrega da feature.')
        for arquivo, soma in json.loads((PASTA / 'fontes.json').read_text()).items():
            self.assertEqual(hashlib.sha256((MOBI / arquivo).read_bytes()).hexdigest(), soma, arquivo)

    def test_cobertura(self):
        operacoes = {c['operacao'] for _, c in casos()}
        self.assertEqual(operacoes, {'editarParedesEmLote', 'excluirParedesEmLote', 'moverParedesEmLote', 'selecionarNoRetangulo'})
        self.assertTrue(any(not c['esperado']['ok'] for _, c in casos() if isinstance(c['esperado'], dict)))

    def test_casos_ouro(self):
        maior = 0
        for caminho, c in casos():
            with self.subTest(caso=caminho.name):
                obtido = executar(c)
                maior = max(maior, maior_diferenca(obtido, c['esperado']))
        self.assertLess(maior, 0.1)

    def test_entrada_nao_muda(self):
        for caminho, c in casos():
            antes = json.dumps(c['entrada'], sort_keys=True)
            executar(c)
            self.assertEqual(json.dumps(c['entrada'], sort_keys=True), antes, caminho.name)

    def test_combinar_selecao(self):
        self.assertEqual(combinar(['a', 'b'], ['c'], 'substituir'), ['c'])
        self.assertEqual(combinar(['a', 'b'], ['b', 'c'], 'somar'), ['a', 'b', 'c'])
        self.assertEqual(combinar(['a', 'b'], ['b', 'c'], 'alternar'), ['a', 'c'])


if __name__ == '__main__':
    unittest.main()
