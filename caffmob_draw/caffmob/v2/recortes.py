"""Geometria de validação de contornos e recortes, como no Studio."""
import math


def cruz(a, b, c):
    return (b['x'] - a['x']) * (c['y'] - a['y']) - (b['y'] - a['y']) * (c['x'] - a['x'])


def cruza(a, b, c, d):
    def sobre(p, q, r):
        return (abs(cruz(p, q, r)) < 1e-8 and min(p['x'], q['x']) - 1e-8 <= r['x'] <= max(p['x'], q['x']) + 1e-8
                and min(p['y'], q['y']) - 1e-8 <= r['y'] <= max(p['y'], q['y']) + 1e-8)
    return (cruz(a, b, c) * cruz(a, b, d) < 0 and cruz(c, d, a) * cruz(c, d, b) < 0) or sobre(a, b, c) or sobre(a, b, d) or sobre(c, d, a) or sobre(c, d, b)


def dentro(p, pol):
    sim = False
    for i, b in enumerate(pol):
        a = pol[i - 1]
        if (b['y'] > p['y']) != (a['y'] > p['y']) and p['x'] < (a['x'] - b['x']) * (p['y'] - b['y']) / (a['y'] - b['y']) + b['x']:
            sim = not sim
    return sim


def distancia_ao_segmento(p, a, b):
    dx, dy = b['x'] - a['x'], b['y'] - a['y']
    t = max(0, min(1, ((p['x'] - a['x']) * dx + (p['y'] - a['y']) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p['x'] - a['x'] - t * dx, p['y'] - a['y'] - t * dy)


def conferir_recortes(contorno, recortes, caminho):
    erros = []
    def erro(campo, mensagem):
        erros.append(dict(caminho=f'{caminho}.{campo}', codigo='GEOMETRIA', mensagem=mensagem))
    if contorno is None:
        if recortes:
            erro('recortes', 'Informe contorno válido para conferir os recortes.')
        return erros
    n, area = len(contorno), 0
    for i, a in enumerate(contorno):
        b = contorno[(i + 1) % n]
        area += a['x'] * b['y'] - b['x'] * a['y']
        if math.hypot(a['x'] - b['x'], a['y'] - b['y']) < 1e-8:
            erro('contorno', 'O contorno tem aresta degenerada.')
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if cruza(a, b, contorno[j], contorno[(j + 1) % n]):
                erro('contorno', 'O contorno não pode se cruzar.')
    if abs(area) < 1e-8:
        erro('contorno', 'O contorno não pode ter área zero.')
    if erros:
        return erros
    def caixa(r):
        return dict(x=r['posicao']['x'], y=r['posicao']['y'], w=r.get('largura', r.get('diametro')), h=r.get('altura', r.get('diametro')))
    for i, r in enumerate(recortes):
        b = caixa(r)
        cabe = dentro(r['posicao'], contorno)
        if r['forma'] == 'circular':
            if any(distancia_ao_segmento(r['posicao'], contorno[j], contorno[(j + 1) % n]) <= r['diametro'] / 2 + 1e-8 for j in range(n)):
                cabe = False
        else:
            cantos = [dict(x=b['x'] + x * b['w'] / 2, y=b['y'] + y * b['h'] / 2) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
            if not all(dentro(p, contorno) for p in cantos):
                cabe = False
            if any(cruza(contorno[j], contorno[(j + 1) % n], cantos[k], cantos[(k + 1) % 4]) for j in range(n) for k in range(4)):
                cabe = False
        if not cabe:
            erro(f'recortes[{i}]', 'O recorte precisa caber inteiramente no contorno sem tocar a borda.')
        for s in recortes[:i]:
            a = caixa(s)
            if r['forma'] == s['forma'] == 'circular':
                sobrepoe = math.hypot(a['x'] - b['x'], a['y'] - b['y']) < (a['w'] + b['w']) / 2
            elif r['forma'] == s['forma'] == 'retangular':
                sobrepoe = abs(a['x'] - b['x']) < (a['w'] + b['w']) / 2 and abs(a['y'] - b['y']) < (a['h'] + b['h']) / 2
            else:
                c, ret = (b, a) if r['forma'] == 'circular' else (a, b)
                x = max(ret['x'] - ret['w'] / 2, min(c['x'], ret['x'] + ret['w'] / 2))
                y = max(ret['y'] - ret['h'] / 2, min(c['y'], ret['y'] + ret['h'] / 2))
                sobrepoe = math.hypot(c['x'] - x, c['y'] - y) < c['w'] / 2
            if sobrepoe:
                erro(f'recortes[{i}]', 'Recortes não podem se sobrepor.')
    return erros
