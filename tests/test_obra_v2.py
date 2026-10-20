"""065 T114 a T117: oráculo TypeScript e integridade dos sólidos, sem bpy."""
import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path
import _bootstrap  # noqa: F401
from caffmob_draw.geometry import obra_v2 as obra
from test_paredes_v2 import maior_diferenca

PASTA = Path(__file__).parent / 'casos_ouro_v2' / 'obra'


def casos(prefixo):
    return [(p, json.loads(p.read_text())) for p in sorted(PASTA.glob(prefixo + '*.json'))]


def extremos(vertices):
    if not vertices:
        return dict(min=None, max=None)
    return dict(min=[min(p[k] for p in vertices) for k in range(3)],
                max=[max(p[k] for p in vertices) for k in range(3)])


def area_das_faces(m, tag):
    return sum(abs(obra.area_com_sinal([m['vertices'][i][:2] for i in f]))
               for f, t in zip(m['faces'], m['materiais']) if t == tag)


def arestas(m, tag=None):
    return Counter(tuple(sorted((a, f[(i + 1) % len(f)]))) for f, t in zip(m['faces'], m['materiais'])
                   if tag is None or t == tag for i, a in enumerate(f))


def lacos_de_borda(m, tag):
    edges = {e for e, n in arestas(m, tag).items() if n == 1}
    vizinhos = {}
    for a, b in edges:
        vizinhos.setdefault(a, set()).add(b)
        vizinhos.setdefault(b, set()).add(a)
    assert all(len(v) == 2 for v in vizinhos.values()), 'Borda aberta ou vértice em T'
    n = 0
    while vizinhos:
        fila = [next(iter(vizinhos))]
        n += 1
        while fila:
            v = fila.pop()
            fila += list(vizinhos.pop(v, ()))
    return n


class ObraV2(unittest.TestCase):
    def test_inventario_e_hashes(self):
        linhas = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}' for p in sorted(PASTA.glob('*.json'))]
        self.assertEqual('\n'.join(linhas) + '\n', (PASTA / 'SHA256SUMS').read_text())
        self.assertEqual(len(linhas), 54)

    def test_fontes(self):
        raiz = PASTA.parents[3] / 'caff-mobi'
        if not raiz.exists():
            self.skipTest('Fontes do MOBI só presentes na entrega.')
        for f, soma in casos('fontes')[0][1].items():
            self.assertEqual(hashlib.sha256((raiz / f).read_bytes()).hexdigest(), soma)

    def test_pavimentos_sem_mutar(self):
        c = casos('pavimentos')[0][1]
        antes = copy.deepcopy(c['entrada'])
        self.assertEqual(obra.elevacoes_dos_pavimentos(antes), c['esperado'])
        self.assertEqual(antes, c['entrada'])
        antes['pavimentos'].reverse()
        self.assertEqual(obra.elevacoes_dos_pavimentos(antes), c['esperado'])
        antes['pavimentos'][1]['laje']['ativa'] = False
        self.assertEqual(obra.elevacoes_dos_pavimentos(antes)[antes['pavimentos'][0]['id']], 2600)

    def test_escalas(self):
        for c in casos('escalas')[0][1]:
            self.assertLessEqual(maior_diferenca(obra.escala_da_textura(**c['entrada']), c['esperado']), 0.1)
        self.assertEqual(obra.escala_da_textura(imagem=dict(largura=0, altura=5)), dict(largura=1000, altura=1000))

    def test_camadas_independentes(self):
        c = casos('camadas')[0][1]
        d = c['entrada']
        obtidos = [e['id'] for familia in ('paredes', 'modulos', 'pecas_avulsas', 'primitivas', 'escadas', 'itens_externos')
                   for e in d[familia] if obra.visivel(d, e)]
        self.assertEqual(obtidos, c['esperado']['visiveis'])

    def test_trecho_oculto_preservado(self):
        c = casos('parede-trecho-oculto')[0][1]['entrada']
        parede = c['paredes'][0]
        antes = copy.deepcopy(parede)
        malha = obra.malha_da_parede(c, parede)
        self.assertEqual(parede, antes)
        self.assertGreater(len(malha['faces']), 0)
        for s in parede['segmentos']:
            s['estado'] = 'oculto'
        self.assertEqual(obra.malha_da_parede(c, parede)['vertices'], [])

    def test_abertura_reta_e_curva_sem_faces_no_vao(self):
        for _, c in casos('parede-'):
            d = c['entrada']
            for p in d['paredes']:
                malha = obra.malha_da_parede(d, p)
                for s, g in zip(p['segmentos'], obra.calcular_paredes(d)[0]['segmentos']):
                    if not g['recortes']:
                        continue
                    # Cada prisma só pode estar antes/depois ou acima/abaixo do vão.
                    # O volume removido é positivo e a face externa não o fecha.
                    vazio = dict(d, aberturas=[])
                    solida = obra.malha_da_parede(vazio, p)
                    def volume(m):
                        total = 0
                        for face in m['faces']:
                            a = m['vertices'][face[0]]
                            for i in range(1, len(face) - 1):
                                b, c = m['vertices'][face[i]], m['vertices'][face[i + 1]]
                                total += sum(a[k] * (b[(k + 1) % 3] * c[(k + 2) % 3] -
                                                    b[(k + 2) % 3] * c[(k + 1) % 3]) for k in range(3)) / 6
                        return abs(total)
                    self.assertLess(volume(malha), volume(solida))

    def test_material_interno_na_face_deslocada(self):
        d = json.loads((PASTA.parent / 'referencia-rica.json').read_text())['entrada']
        p = d['paredes'][0]
        m = obra.malha_da_parede(d, p)
        self.assertEqual(m['materiais'][2], p['segmentos'][0]['material_externo_id'])
        self.assertEqual(m['materiais'][4], p['segmentos'][0]['material_interno_id'])

    def test_topologia_invariante_ao_sentido_do_contorno(self):
        c = casos('laje-concava')[0][1]
        pol = [(p['x'], p['y']) for p in c['entrada']['contorno']]
        for contorno in (pol, pol[::-1]):
            m = obra.extrudar(contorno, [p[::-1] for p in c['furos']], 100, 120)
            self.assertEqual(set(arestas(m).values()), {2})
            self.assertEqual(lacos_de_borda(m, 'cima'), 3)
            self.assertAlmostEqual(area_das_faces(m, 'cima'), c['area_mm2'], delta=0.01)


for _p, _c in casos('escada-'):
    def _teste(self, c=_c):
        self.assertLessEqual(maior_diferenca(obra.calcular_escada(c['entrada']), c['esperado']), 0.1)
        m = obra.malha_da_escada(c['entrada'])
        self.assertGreater(len(m['vertices']), 0)
        self.assertLessEqual(max(v[2] for v in m['vertices']), c['entrada']['altura'])
    setattr(ObraV2, 'test_' + _p.stem.replace('-', '_'), _teste)

for _p, _c in casos('forro-'):
    def _teste(self, c=_c):
        self.assertLessEqual(maior_diferenca(obra.geometria_do_forro(c['entrada']), c['esperado']), 0.1)
        d = dict(paredes=[])
        ss = [s for s in obra.superficies_do_pavimento(d, c['entrada']) if s['tipo'] in ('forro', 'sanca')]
        self.assertEqual(len(ss), len(c['superficies']))
        for s, esperado in zip(ss, c['superficies']):
            s = {k:v for k,v in s.items() if k != 'tipo'}
            self.assertLessEqual(maior_diferenca(s, esperado), 0.1)
    setattr(ObraV2, 'test_' + _p.stem.replace('-', '_'), _teste)

for _p, _c in casos('textura-'):
    def _teste(self, c=_c):
        self.assertLessEqual(maior_diferenca(obra.uv_da_textura(**c['entrada']), c['esperado']), 1e-12)
    setattr(ObraV2, 'test_' + _p.stem.replace('-', '_'), _teste)

for _p, _c in casos('laje-'):
    def _teste(self, c=_c):
        e = c['entrada']
        pol = [(p['x'], p['y']) for p in e['contorno']]
        furos = [obra.contorno_do_recorte(r) for r in e['recortes']]
        self.assertLessEqual(maior_diferenca(furos, c['furos']), 0.1)
        m = obra.extrudar(pol, furos, z=2600, profundidade=150)
        self.assertEqual(set(arestas(m).values()), {2})
        self.assertEqual(lacos_de_borda(m, 'cima'), c['lacos'])
        for role in ('cima', 'baixo'):
            self.assertAlmostEqual(area_das_faces(m, role), c['area_mm2'], delta=0.01)
    setattr(ObraV2, 'test_' + _p.stem.replace('-', '_'), _teste)

for _p, _c in casos('parede-'):
    def _teste(self, c=_c):
        for parede, esperado in zip(c['entrada']['paredes'], c['esperado']):
            m = obra.malha_da_parede(c['entrada'], parede)
            self.assertLessEqual(maior_diferenca(extremos(m['vertices']), {k:v for k,v in esperado.items() if k != 'id'}), 0.1)
    setattr(ObraV2, 'test_obra_' + _p.stem.replace('-', '_'), _teste)

for _p, _c in casos('uvs-'):
    def _teste(self, c=_c, nome=_p.stem):
        if nome == 'uvs-parede':
            m = obra.malha_da_parede(c['entrada'], c['entrada']['paredes'][0])
        else:
            m = obra.extrudar(**c['entrada'])
        loops = [(m['vertices'][i], uv) for f, coords in zip(m['faces'], m['uvs']) for i, uv in zip(f, coords)]
        for amostra in c['esperado']:
            candidatos = [uv for p,uv in loops if max(abs(a-b) for a,b in zip(p,amostra['p'])) < 0.01]
            self.assertTrue(candidatos, amostra)
            self.assertLessEqual(min(max(abs(a-b) for a,b in zip(uv,amostra['uv'])) for uv in candidatos), 0.1, amostra)
    setattr(ObraV2, 'test_' + _p.stem.replace('-', '_'), _teste)
