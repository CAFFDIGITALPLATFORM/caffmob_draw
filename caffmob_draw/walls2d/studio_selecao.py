"""Seleção CAD do Studio, sobre o polígono real de cada trecho, sem Blender."""
from ..caffmob.geometria import geometria_da_parede


def combinar(atuais, novas, modo='substituir'):
    ids = list(dict.fromkeys([] if modo == 'substituir' else atuais))
    for id in novas:
        if modo == 'alternar' and id in ids:
            ids.remove(id)
        elif id not in ids:
            ids.append(id)
    return ids


def poligono_no_retangulo(poligono, a, b, toca):
    x0, x1 = sorted((a[0], b[0]))
    y0, y1 = sorted((a[1], b[1]))
    def dentro(q):
        return x0 <= q[0] <= x1 and y0 <= q[1] <= y1
    if not toca:
        return all(dentro(q) for q in poligono)
    if any(dentro(q) for q in poligono):
        return True
    for p, q in zip(poligono, poligono[1:] + poligono[:1]):
        de, ate = 0, 1
        dx, dy = q[0] - p[0], q[1] - p[1]
        for v, w in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
            if v == 0:
                if w < 0:
                    break
                continue
            if v < 0:
                de = max(de, w / v)
            else:
                ate = min(ate, w / v)
            if de > ate:
                break
        else:
            return True
    interior = False
    for p, q in zip(poligono, poligono[-1:] + poligono[:-1]):
        if (p[1] > y0) != (q[1] > y0) and x0 < (q[0] - p[0]) * (y0 - p[1]) / (q[1] - p[1]) + p[0]:
            interior = not interior
    return interior


def selecionar_no_retangulo(d, piso, a, b, toca):
    return [p['segmentos'][k]['id'] for p in d['paredes'] if p['pavimento_id'] == piso
            for k, g in enumerate(geometria_da_parede(p))
            if poligono_no_retangulo(g['linha'] + list(reversed(g['face'])), a, b, toca)]
