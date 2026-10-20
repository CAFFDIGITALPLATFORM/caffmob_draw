"""Símbolos 2D de desenharAberturaStudio.ts, em mm e sem Blender."""
import math


def simbolo(abertura, vao, espessura, sentido):
    inicio, fim = vao['inicio'], vao['fim']
    dx, dy = fim[0] - inicio[0], fim[1] - inicio[1]
    comprimento = math.hypot(dx, dy) or 1
    sinal = 1 if sentido == 'LEFT' else -1
    nx, ny = -dy / comprimento * sinal, dx / comprimento * sinal

    def p(s, normal):
        return inicio[0] + dx * s + nx * normal, inicio[1] + dy * s + ny * normal

    recorte = [p(0, -2), p(1, -2), p(1, espessura + 2), p(0, espessura + 2)]
    if abertura['tipo'] == 'WINDOW':
        linhas = [(p(0, espessura * f), p(1, espessura * f)) for f in (0.25, 0.5, 0.75)]
        linhas += [(p(0, 0), p(0, espessura)), (p(1, 0), p(1, espessura))]
        return dict(recorte=recorte, linhas=linhas, arco=[])
    centro, ponta = p(0, 0), p(0, -abertura['largura'])
    a0 = math.atan2(ponta[1] - centro[1], ponta[0] - centro[0])
    a1 = math.atan2(fim[1] - centro[1], fim[0] - centro[0])
    giro = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    raio = abertura['largura']
    arco = [(centro[0] + raio * math.cos(a0 + giro * k / 32),
             centro[1] + raio * math.sin(a0 + giro * k / 32)) for k in range(33)]
    return dict(recorte=recorte, linhas=[(centro, ponta)], arco=arco)


def projetar(geometria, ponto):
    """projetarNoSegmento de shared/caffmob/aberturas.ts, distância ao longo da linha."""
    arco = geometria['arco']
    if arco:
        c = arco['centro']
        delta = ((math.atan2(ponto[1] - c[1], ponto[0] - c[0]) - arco['angulo_inicial'])
                 * (1 if arco['varredura'] >= 0 else -1)) % (2 * math.pi)
        total = arco['angulo_central']
        angulo = delta if delta <= total else total if delta - total < 2 * math.pi - delta else 0
        return angulo * arco['raio']
    a, b = geometria['trecho']
    dx, dy = b[0] - a[0], b[1] - a[1]
    l = math.hypot(dx, dy)
    return max(0, min(1, ((ponto[0] - a[0]) * dx + (ponto[1] - a[1]) * dy) / (l * l))) * l
