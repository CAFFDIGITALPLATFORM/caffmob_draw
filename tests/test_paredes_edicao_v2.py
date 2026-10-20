"""065 T123: operações de edição de parede contra o resultado real do TypeScript (teto 0,1 mm)."""
import copy
import hashlib
import json
import math
import unittest
from pathlib import Path
import _bootstrap  # noqa: F401
from caffmob_draw.caffmob.v2 import paredes_edicao as pe

PASTA = Path(__file__).resolve().parent / 'casos_ouro_v2' / 'edicao'


def casos(prefixo=''):
    return [(p, json.loads(p.read_text(encoding='utf-8'))) for p in sorted(PASTA.glob(prefixo + '*.json')) if p.name != 'fontes.json']


def executar(d, c):
    p = c['parametros']
    op = c['operacao']
    if op == 'editarTrecho':
        return pe.editar_trecho(d, p['segmento_id'], p['edicao'])
    if op == 'dividirTrecho':
        return pe.dividir_trecho(d, p['segmento_id'], p['posicao'], p['novo_id'])
    if op == 'ocultarTrecho':
        return pe.ocultar_trecho(d, p['segmento_id'])
    if op == 'restaurarTrecho':
        return pe.restaurar_trecho(d, p['segmento_id'])
    if op == 'removerTrecho':
        return pe.remover_trecho(d, p['segmento_id'], p.get('confirmar_dependencias', False), p.get('nova_parede_id'))
    if op == 'limparParedes':
        return pe.limpar_paredes(d, p['pavimento_id'], p.get('confirmar_dependencias', False))
    if op == 'moverVertice':
        return pe.mover_vertice(d, p['parede_id'], p['indice'], p['ponto'])
    if op == 'fundirTrechos':
        return pe.fundir_trechos(d, p['parede_id'], p['indice'])
    if op == 'aplicarEspessuraATodas':
        return pe.aplicar_espessura_a_todas(d, p['pavimento_id'], p['espessura'])
    if op == 'criarModeloDeParede':
        ids = iter(p['ids'])
        return pe.criar_modelo_de_parede(d, {**{k: v for k, v in p.items() if k != 'ids'}, 'gerar_id': lambda: next(ids)})
    raise AssertionError('Operação sem porte: ' + op)


def maior_diferenca(obtido, esperado, caminho='$'):
    """Números com folga; o resto igual, inclusive códigos, caminhos e mensagens de erro."""
    if isinstance(esperado, bool) or esperado is None or isinstance(esperado, str):
        if obtido != esperado or type(obtido) is not type(esperado):
            raise AssertionError(f'{caminho}: {obtido!r} != {esperado!r}')
        return 0
    if isinstance(esperado, (float, int)):
        if type(obtido) not in (float, int):
            raise AssertionError(f'{caminho}: {obtido!r} != {esperado!r}')
        return abs(obtido - esperado)
    if isinstance(esperado, list):
        if not isinstance(obtido, list) or len(obtido) != len(esperado):
            raise AssertionError(f'{caminho}: tamanhos {obtido!r} != {esperado!r}')
        return max((maior_diferenca(a, b, f'{caminho}[{i}]') for i, (a, b) in enumerate(zip(obtido, esperado))), default=0)
    if not isinstance(obtido, dict) or set(obtido) != set(esperado):
        raise AssertionError(f'{caminho}: chaves {sorted(obtido)} != {sorted(esperado)}')
    return max((maior_diferenca(obtido[k], v, f'{caminho}.{k}') for k, v in esperado.items()), default=0)


class ParedesEdicaoV2(unittest.TestCase):
    def test_somas_e_fontes(self):
        linhas = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(PASTA.glob('*.json'))]
        self.assertEqual('\n'.join(linhas) + '\n', (PASTA / 'SHA256SUMS').read_text())
        self.assertIn('shared/studio/paredes.ts', json.loads((PASTA / 'fontes.json').read_text()))

    def test_cobertura(self):
        todos = casos()
        self.assertGreaterEqual(len(todos), 30)
        operacoes = {c['operacao'] for _, c in todos}
        self.assertEqual(operacoes, {'editarTrecho', 'dividirTrecho', 'ocultarTrecho', 'restaurarTrecho', 'removerTrecho',
                                     'limparParedes', 'moverVertice', 'fundirTrechos', 'aplicarEspessuraATodas', 'criarModeloDeParede'})
        recusas = {c['operacao'] for _, c in todos if not c['esperado']['ok']}
        self.assertEqual(recusas, operacoes)
        nomes = {p.stem for p, _ in todos}
        for trecho in ('retangulo', 'polilinha', '-L', 'arco', 'aberturas', 'dois-pavimentos'):
            self.assertTrue(any(trecho in n for n in nomes), trecho)

    def test_entrada_nao_muda(self):
        for p, c in casos():
            entrada = copy.deepcopy(c['entrada'])
            executar(entrada, c)
            with self.subTest(caso=p.name):
                self.assertEqual(entrada, c['entrada'])

    def test_controle_positivo(self):
        p, c = casos('editar-retangulo-inicio-interna')[0]
        r = executar(c['entrada'], c)
        r['valor']['paredes'][0]['segmentos'][0]['comprimento'] += 0.5
        self.assertGreater(maior_diferenca(r, c['esperado']), 0.1)
        r['valor']['paredes'][0]['segmentos'][0]['estado'] = 'oculto'
        with self.assertRaises(AssertionError):
            maior_diferenca(r, c['esperado'])

    def test_recusas_fora_dos_casos_json(self):
        c = casos('mover-retangulo-canto')[0][1]
        d, parede_id = c['entrada'], c['parametros']['parede_id']
        for ponto in (dict(x=math.inf, y=0), dict(x=0, y=math.nan)):
            r = pe.mover_vertice(d, parede_id, 1, ponto)
            self.assertEqual(r, dict(ok=False, erros=[pe.erro('paredes[0].vertices[1]', 'DIMENSAO', 'Informe coordenadas finitas em milímetros.')]))
        for indice in (True, -1, '1'):
            self.assertEqual(pe.mover_vertice(d, parede_id, indice, dict(x=0, y=0))['erros'][0]['codigo'], 'ESQUEMA')
        for espessura in (math.nan, math.inf, -1):
            self.assertEqual(pe.aplicar_espessura_a_todas(d, d['pavimentos'][0]['id'], espessura)['erros'][0]['caminho'], 'espessura')
        r = pe.editar_trecho(d, d['paredes'][0]['segmentos'][0]['id'], dict(ancora='inicio', lado_medida='interna', comprimento=math.nan))
        self.assertEqual(r['erros'][0]['codigo'], 'DIMENSAO')

    def test_gerador_que_so_repete(self):
        c = casos('criar-U-dois-pavimentos')[0][1]
        o = {**{k: v for k, v in c['parametros'].items() if k != 'ids'}, 'gerar_id': lambda: c['entrada']['id']}
        with self.assertRaises(ValueError):
            pe.criar_modelo_de_parede(c['entrada'], o)

    def test_sem_bpy(self):
        self.assertNotRegex(Path(pe.__file__).read_text(encoding='utf-8'), r'(?m)^\s*(import|from)\s+(bpy|mathutils)\b')
        self.assertIs(pe.excluir_ponto, pe.fundir_trechos)


DIFERENCAS = {}

for _p, _c in casos():
    def _teste(self, caso=_c, nome=_p.stem):
        obtido = executar(caso['entrada'], caso)
        diferenca = maior_diferenca(obtido, caso['esperado'])
        DIFERENCAS[nome] = diferenca
        self.assertLessEqual(diferenca, 0.1)
    setattr(ParedesEdicaoV2, 'test_caso_' + _p.stem.replace('-', '_'), _teste)
