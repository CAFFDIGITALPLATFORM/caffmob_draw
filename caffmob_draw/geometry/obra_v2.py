"""065 T114 a T117: geometria do Studio em mm, sem Blender nem rede.

A extrusão usa faixas verticais do polígono com paridade dos contornos. Os furos
participam da triangulação das duas tampas e das laterais; não há caixa ou booleano.
"""
import math
from ..caffmob.v2.paredes import calcular_paredes
from ..caffmob.geometria import geometria_da_parede, piso_da_parede, area_com_sinal

EPS = 1e-7


def elevacoes_dos_pavimentos(documento):
    z, elevacoes = 0, {}
    for p in sorted(documento['pavimentos'], key=lambda p: p['ordem']):
        elevacoes[p['id']] = z
        z += p['pe_direito'] + (p['laje']['espessura'] + p['laje']['contrapiso'] if p['laje']['ativa'] else 0)
    return elevacoes


def calcular_escada(e):
    # Math.round do JavaScript, inclusive nos empates.
    n = max(2, math.floor(e['altura'] / e['espelho_alvo'] + 0.5))
    espelho = e['altura'] / n
    piso = max(280, min(320, math.floor(635 - 2 * espelho + 0.5)))
    w, n1 = e['largura'], math.ceil(n / 2)
    n2 = n - n1
    d = w if e['tipo'] == 'reta' else w + (n2 - 1) * piso if e['tipo'] == 'L' else 2 * w + 100
    blocos, patamares = [], []

    def bloco(papel, x, z, largura, profundidade, topo):
        return dict(papel=papel, x=x, y=d - z - profundidade, largura=largura, profundidade=profundidade, topo=topo)

    if e['tipo'] == 'reta':
        blocos = [bloco(f'Degrau {i + 1}', i * piso, 0, piso, w, (i + 1) * espelho) for i in range(n - 1)]
    else:
        x0 = (n1 - 1) * piso
        blocos = [bloco(f'Degrau {i + 1}', i * piso, 0, piso, w, (i + 1) * espelho) for i in range(n1 - 1)]
        if e['tipo'] == 'L':
            patamares = [bloco('Patamar', x0, 0, w, w, n1 * espelho)]
            blocos += [bloco(f'Degrau {n1 + j + 1}', x0, w + j * piso, w, piso, (n1 + j + 1) * espelho)
                       for j in range(n2 - 1)]
        else:
            patamares = [bloco('Patamar 1', x0, 0, w, w, n1 * espelho),
                         bloco('Patamar 2', x0, w, w, w + 100, n1 * espelho)]
            blocos += [bloco(f'Degrau {n1 + j + 1}', x0 - (j + 1) * piso, w + 100, piso, w,
                             (n1 + j + 1) * espelho) for j in range(n2 - 1)]
    return dict(degraus=n, espelho=espelho, piso=piso, pisos=n - 1, blondel=2 * espelho + piso,
                primeiro_lance=n1, profundidade=d, projecao=(n - 1) * piso if e['tipo'] == 'reta' else (n1 - 1) * piso + w,
                patamares=patamares, blocos=blocos + patamares)


def geometria_do_forro(p):
    f = p['forro']
    if f['tipo'] == 'nenhum':
        return None
    s = f['sanca']
    return dict(altura=p['pe_direito'], sanca=dict(tipo=s['tipo'], largura=s['largura'],
                altura_rebaixada=p['pe_direito'] - s['rebaixo'], led=s['led']) if s else None)


def contorno_do_recorte(r):
    x, y = r['posicao']['x'], r['posicao']['y']
    if r['forma'] == 'retangular':
        w, h = r['largura'] / 2, r['altura'] / 2
        return [(x - w, y - h), (x + w, y - h), (x + w, y + h), (x - w, y + h)]
    return [(x + math.cos(i * math.pi / 32) * r['diametro'] / 2,
             y + math.sin(i * math.pi / 32) * r['diametro'] / 2) for i in range(64)]


def contorno_do_pavimento(documento, p):
    if 'contorno' in p['laje']:
        return [(v['x'], v['y']) for v in p['laje']['contorno']]
    pontos = []
    for parede in documento['paredes']:
        if parede['pavimento_id'] == p['id'] and parede['fechada']:
            piso = piso_da_parede(parede, geometria_da_parede(parede))
            if piso:
                pontos += piso['vertices']
    return pontos


def radial(contorno, distancia, minimo=None):
    cx = sum(v[0] for v in contorno) / len(contorno)
    cy = sum(v[1] for v in contorno) / len(contorno)
    saida = []
    for x, y in contorno:
        r = math.hypot(x - cx, y - cy)
        t = 1 + distancia / r if r else 1
        if minimo is not None:
            t = max(minimo, t)
        saida.append((cx + (x - cx) * t, cy + (y - cy) * t))
    return saida


def superficies_do_pavimento(documento, p):
    contorno = contorno_do_pavimento(documento, p)
    if len(contorno) < 3:
        return []
    furos = [contorno_do_recorte(r) for r in p['laje']['recortes']]
    saida = [dict(tipo='piso', contorno=contorno, furos=furos, z=0, profundidade=1)]
    if p['laje']['ativa']:
        saida.append(dict(tipo='laje', contorno=radial(contorno, p['laje']['beiral']), furos=furos,
                          z=p['pe_direito'], profundidade=p['laje']['espessura'] + p['laje']['contrapiso']))
    f = geometria_do_forro(p)
    if f:
        saida.append(dict(tipo='forro', contorno=contorno, furos=furos, z=f['altura'] - 15, profundidade=15))
        if f['sanca']:
            s = f['sanca']
            interno = radial(contorno, -s['largura'], 0.05)
            # Os três tipos usam a faixa radial do renderer atual do Studio.
            saida.append(dict(tipo='sanca', contorno=contorno, furos=[interno],
                              z=s['altura_rebaixada'] - 15, profundidade=15))
    return saida


def malha_vazia():
    return dict(vertices=[], faces=[], materiais=[], uvs=[])


def juntar_malhas(malhas):
    saida = malha_vazia()
    for m in malhas:
        n = len(saida['vertices'])
        saida['vertices'] += m['vertices']
        saida['faces'] += [tuple(i + n for i in f) for f in m['faces']]
        saida['materiais'] += m['materiais']
        saida['uvs'] += m['uvs']
    return saida


def extrudar(contorno, furos=(), z=0, profundidade=1):
    """Extrusão estanque, inclusive de contorno côncavo e furos retangulares/circulares.

    Faixas pelo X de todos os vértices. Subdivide as junções verticais para não
    deixar vértices em T; tampas e paredes compartilham índices. Normais para fora.
    """
    m = malha_vazia()
    loops = []
    for k, pol in enumerate([contorno, *furos]):
        pol = [tuple(round(c, 8) for c in v) for v in pol]
        if (area_com_sinal(pol) > 0) != (k == 0):
            pol.reverse()
        loops.append(pol)
    edges = [(a, pol[(i + 1) % len(pol)]) for pol in loops for i, a in enumerate(pol)]
    xs = sorted(set(round(v[0], 8) for pol in loops for v in pol))
    cells, ys = [], {x: set() for x in xs}

    def at(edge, x):
        a, b = edge
        return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])

    for x0, x1 in zip(xs, xs[1:]):
        mid = (x0 + x1) / 2
        crossings = sorted((at(e, mid), e) for e in edges if min(e[0][0], e[1][0]) < mid < max(e[0][0], e[1][0]))
        if len(crossings) % 2:
            raise ValueError('Contorno de extrusão inválido')
        for (_, low), (_, high) in zip(crossings[::2], crossings[1::2]):
            a, b, c, d = at(low, x0), at(low, x1), at(high, x1), at(high, x0)
            cells.append((x0, x1, a, b, c, d))
            ys[x0].update((round(a, 8), round(d, 8)))
            ys[x1].update((round(b, 8), round(c, 8)))
    for pol in loops:
        for x, y in pol:
            ys[round(x, 8)].add(round(y, 8))
    lookup = {}

    def vertex(co):
        key = tuple(round(v, 8) for v in co)
        if key not in lookup:
            lookup[key] = len(m['vertices'])
            m['vertices'].append(tuple(co))
        return lookup[key]

    def face(points, role, uv=None):
        ids = tuple(vertex(p) for p in points)
        if len(set(ids)) < 3:
            return
        m['faces'].append(ids)
        m['materiais'].append(role)
        m['uvs'].append(uv or [(p[0], p[1]) for p in points])

    for x0, x1, a, b, c, d in cells:
        pol = [(x0, a), (x1, b)]
        pol += [(x1, v) for v in sorted(ys[x1]) if b + EPS < v < c - EPS]
        pol += [(x1, c), (x0, d)]
        pol += [(x0, v) for v in sorted(ys[x0], reverse=True) if a + EPS < v < d - EPS]
        pol = [v for i, v in enumerate(pol) if math.dist(v, pol[i - 1]) > EPS]
        if len(pol) < 3:
            continue
        center = (sum(v[0] for v in pol) / len(pol), sum(v[1] for v in pol) / len(pol))
        for i, v in enumerate(pol):
            tri = [center, v, pol[(i + 1) % len(pol)]]
            if abs(area_com_sinal(tri)) < EPS:
                continue
            face([(x, y, z + profundidade) for x, y in tri], 'cima')
            face([(x, y, z) for x, y in reversed(tri)], 'baixo')
    for a, b in edges:
        points = [a, b]
        if abs(a[0] - b[0]) > EPS:
            points += [(x, at((a, b), x)) for x in xs if min(a[0], b[0]) + EPS < x < max(a[0], b[0]) - EPS]
        else:
            points += [(a[0], y) for y in ys[round(a[0], 8)] if min(a[1], b[1]) + EPS < y < max(a[1], b[1]) - EPS]
        points.sort(key=lambda p: math.dist(a, p))
        eixo = 0 if abs(a[1] - b[1]) < abs(a[0] - b[0]) else 1
        for p, q in zip(points, points[1:]):
            face([(*p, z), (*q, z), (*q, z + profundidade), (*p, z + profundidade)], 'lateral',
                 [(p[eixo], 1000), (q[eixo], 1000),
                  (q[eixo], 1000 - profundidade), (p[eixo], 1000 - profundidade)])
    return m


def caixa(x, y, z, largura, profundidade, altura):
    return extrudar([(x, y), (x + largura, y), (x + largura, y + profundidade), (x, y + profundidade)],
                    z=z, profundidade=altura)


def malha_da_entidade(e):
    if e.get('forma') == 'cilindro':
        r = e['diametro'] / 2
        contorno = [(r + math.cos(i * math.pi / 32) * r, r + math.sin(i * math.pi / 32) * r) for i in range(64)]
        return extrudar(contorno, profundidade=e['altura'])
    d = e['dimensoes']
    return extrudar([(0, 0), (d['largura'], 0), (d['largura'], d['profundidade']), (0, d['profundidade'])],
                    [contorno_do_recorte(r) for r in e.get('recortes', [])], profundidade=d['altura'])


def malha_da_escada(e):
    return juntar_malhas(caixa(b['x'], b['y'], 0, b['largura'], b['profundidade'], b['topo'])
                         for b in calcular_escada(e)['blocos'])


def malha_da_parede(documento, parede):
    """Uma malha por cadeia, como a 063; cortes também atravessam as faixas curvas."""
    calculo = next(p for p in calcular_paredes(dict(documento, paredes=[parede])) if p['id'] == parede['id'])
    m = malha_vazia()
    for s, g in zip(parede['segmentos'], calculo['segmentos']):
        if s['estado'] == 'oculto':
            continue
        n, total = len(g['linha']) - 1, g['comprimento']
        for j in range(n):
            a, b = total * j / n, total * (j + 1) / n
            cortes = sorted({a, b, *(max(a, min(b, v[k])) for v in g['recortes'] for k in ('inicio', 'fim'))})
            for u0, u1 in zip(cortes, cortes[1:]):
                v = next((v for v in g['recortes'] if v['inicio'] < (u0 + u1) / 2 < v['fim']), None)
                faixas = [(g['base'], None)] if v is None else [(g['base'], v['base']), (v['topo'], None)]
                for baixo, cima in faixas:
                    if cima is not None and cima - baixo < EPS:
                        continue
                    def top(u):
                        return cima if cima is not None else g['topo_inicial'] + (g['topo_final'] - g['topo_inicial']) * u / total
                    if max(top(u0), top(u1)) - baixo < EPS:
                        continue
                    def ponto(linha, u):
                        t = (u - a) / (b - a)
                        p, q = linha[j], linha[j + 1]
                        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
                    xy = [ponto(g['linha'], u0), ponto(g['linha'], u1), ponto(g['face'], u1), ponto(g['face'], u0)]
                    vs = [(*p, baixo) for p in xy] + [(*p, top(u)) for p, u in zip(xy, (u0, u1, u1, u0))]
                    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
                    tags = [parede.get('material_id')] * 6
                    tags[2] = s.get('material_externo_id', parede.get('material_id'))
                    tags[4] = s.get('material_interno_id', parede.get('material_id'))
                    # Abertura pode tocar o topo em uma ponta: o prisma vira
                    # cunha triangular. Une os cantos coincidentes e omite só
                    # faces de área zero, sem descartar a cunha inteira.
                    mapa, cantos = {}, {}
                    for i, ponto_ in enumerate(vs):
                        chave = tuple(round(c, 8) for c in ponto_)
                        if chave not in cantos:
                            cantos[chave] = len(m['vertices'])
                            m['vertices'].append(ponto_)
                        mapa[i] = cantos[chave]
                    for k, f in enumerate(faces):
                        if area_com_sinal(xy) < 0:
                            f = tuple(reversed(f))
                        usados, distintos = set(), []
                        for i in f:
                            if mapa[i] not in usados:
                                usados.add(mapa[i])
                                distintos.append(i)
                        f = distintos
                        if len(f) < 3:
                            continue
                        m['faces'].append(tuple(mapa[i] for i in f))
                        m['materiais'].append(tags[k])
                        # UV de ExtrudeGeometry antes de deformar o plano (s, altura).
                        # Nas laterais, a web substitui V pela espessura restante.
                        ss = (u0, u1, u1, u0)
                        coords = []
                        horizontal = k == 0 or (k == 1 and abs(top(u1) - top(u0)) < u1 - u0)
                        for i in f:
                            u, h = ss[i % 4], vs[i][2]
                            esp = math.dist(ponto(g['linha'], u), ponto(g['face'], u))
                            coords.append((u, h) if k in (2, 4) else
                                          (u if horizontal else h, esp if i % 4 in (0, 1) else 0))
                        m['uvs'].append(coords)
    return m


def escala_da_textura(escala=None, imagem=None):
    if escala:
        return dict(escala)
    imagem = imagem or dict(largura=1, altura=1)
    w, h = imagem['largura'], imagem['altura']
    return dict(largura=1000, altura=1000 * h / w if w > 0 and h > 0 else 1000)


def uv_da_textura(uv, escala, rotacao=0, veio='HORIZONTAL'):
    """Matrix3 de Three.Texture: centro 0,5, repeat antes da rotação."""
    a = math.radians(rotacao + (90 if veio == 'VERTICAL' else 0))
    x, y = uv[0] - 0.5, uv[1] - 0.5
    return ((math.cos(a) * x + math.sin(a) * y) / escala['largura'] + 0.5,
            (-math.sin(a) * x + math.cos(a) * y) / escala['altura'] + 0.5)


def visivel(documento, entidade, categoria=None):
    if not entidade.get('visivel', True):
        return False
    pid = entidade.get('pavimento_id', entidade.get('id'))
    aplicaveis = [c for c in documento['camadas'] if c['pavimento_id'] in (None, pid)]
    categorias = {c['categoria']: all(x['visivel'] for x in aplicaveis if x['categoria'] == c['categoria']) for c in aplicaveis}
    camada = next((c for c in documento['camadas'] if c['id'] == entidade.get('camada_id')), None)
    return ((not camada or (camada['visivel'] and categorias.get(camada['categoria'], True)))
            and (not categoria or (categorias.get(categoria, True) and categorias.get('ambiente', True))))
