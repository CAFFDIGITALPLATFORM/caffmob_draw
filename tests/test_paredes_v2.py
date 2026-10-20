"""065 T113: diferenças numéricas contra o cálculo real do TypeScript (teto 0,1 mm)."""
import unittest
import _bootstrap  # noqa: F401
from test_contrato_v2 import casos
from caffmob_draw.caffmob.v2.paredes import calcular_paredes, comprimento_da_linha, recortes_da_parede
from caffmob_draw.caffmob.v2.limites_espaciais import limites_espaciais, cantos_no_mundo, sobrepoem


def maior_diferenca(obtido, esperado):
    if isinstance(esperado, bool) or esperado is None or isinstance(esperado, str):
        if obtido != esperado:
            raise AssertionError((obtido, esperado))
        return 0
    if isinstance(esperado, (float, int)):
        if type(obtido) not in (float, int):
            raise AssertionError((obtido, esperado))
        return abs(obtido - esperado)
    if isinstance(esperado, list):
        if len(obtido) != len(esperado):
            raise AssertionError((len(obtido), len(esperado)))
        return max((maior_diferenca(a, b) for a, b in zip(obtido, esperado)), default=0)
    if set(obtido) != set(esperado):
        raise AssertionError((set(obtido), set(esperado)))
    return max((maior_diferenca(obtido[k], v) for k, v in esperado.items()), default=0)


class ParedesV2(unittest.TestCase):
    def test_modelos_e_cobertura(self):
        nomes = {p.stem for p, _ in casos('parede-')}
        for nome in ('retangulo', 'L', 'U', 'angulo-30', 'polilinha-aberta', 'arco-positivo',
                     'arco-negativo', 'semicirculo', 'pe-direito-inclinado', 'afastamento',
                     'trecho-oculto', 'porta-janela', 'dois-pavimentos'):
            self.assertIn('parede-' + nome, nomes)

    def test_medidas_das_faces(self):
        for p, c in casos('parede-'):
            for m in c['medidas']:
                parede = next(v for v in c['entrada']['paredes'] if v['id'] == m['parede_id'])
                j = next(i for i, s in enumerate(parede['segmentos']) if s['id'] == m['segmento_id'])
                s = parede['segmentos'][j]
                obtido = comprimento_da_linha(parede, j, m['medida'], m['lado'], s['angulo_absoluto'], s['espessura'])
                with self.subTest(caso=p.name, segmento=j, lado=m['lado']):
                    self.assertLessEqual(abs(obtido - m['esperado']), 0.1)

    def test_limites_espaciais(self):
        for _, c in casos('limites-'):
            self.assertLessEqual(maior_diferenca(limites_espaciais(c['entrada'], c['elevacao']), c['esperado']), 0.1)
            self.assertLessEqual(maior_diferenca(cantos_no_mundo(c['entrada'], c['elevacao']), c['cantos']), 0.1)
            a = c['esperado']
            self.assertTrue(sobrepoem(a, a))
            self.assertFalse(sobrepoem(a, {k: {e: v + 10000 for e, v in p.items()} for k, p in a.items()}))

    def test_recorte_sem_trecho(self):
        self.assertEqual(recortes_da_parede({'paredes': []}, 'inexistente'), [])

    def test_controle_positivo(self):
        c = casos('parede-retangulo')[0][1]
        resultado = calcular_paredes(c['entrada'])
        resultado[0]['segmentos'][0]['face'][0] = (99999, 99999)
        self.assertGreater(maior_diferenca(resultado, c['esperado']), 0.1)


for _p, _c in casos('parede-'):
    def _teste(self, caso=_c):
        self.assertLessEqual(maior_diferenca(calcular_paredes(caso['entrada']), caso['esperado']), 0.1)
    setattr(ParedesV2, 'test_' + _p.stem.replace('-', '_'), _teste)
