"""AABB mundial de peça fechada: porte de shared/studio/limitesEspaciais.ts."""
import math


def cantos_no_mundo(peca, elevacao_do_piso):
    a = math.radians(peca['rotacao_z'])
    c, s = math.cos(a), math.sin(a)
    p, d = peca['posicao'], peca['dimensoes']
    return [dict(x=p['x'] + x * c - y * s, y=p['y'] + x * s + y * c, z=elevacao_do_piso + p['z'] + z)
            for x in (0, d['largura']) for y in (0, d['profundidade']) for z in (0, d['altura'])]


def limites_espaciais(peca, elevacao_do_piso=0):
    cantos = cantos_no_mundo(peca, elevacao_do_piso)
    return {lado: {eixo: f(p[eixo] for p in cantos) for eixo in ('x', 'y', 'z')} for lado, f in (('min', min), ('max', max))}


def sobrepoem(a, b, folga=0.5):
    return all(min(a['max'][e], b['max'][e]) - max(a['min'][e], b['min'][e]) > folga for e in ('x', 'y', 'z'))
