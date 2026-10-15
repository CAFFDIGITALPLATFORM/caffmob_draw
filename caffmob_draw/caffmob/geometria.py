# (063 RF-01; D-02) Núcleo puro portado da 061.
"""
Geometria derivada do contrato (061 RN-10; contrato §3.1). Espelho de shared/caffmob do MOBI
(polilinha.ts, arco.ts, contorno.ts, piso.ts, aberturas.ts): as mesmas definições, os mesmos números.
Sem arredondar no meio: o arredondamento é só na saída para o contrato.
"""

import math

from .contrato import normalizar_relativo

ERRO_DE_CORDA_MM = 1
LIMITE_DA_ESQUADRIA = 10


def _somar(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _subtrair(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _escalar(a, k):
    return (a[0] * k, a[1] * k)


def distancia(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _normal_esquerda(d):
    return (-d[1], d[0])


def trechos_da_parede(parede):
    """Vértices inicial e final de cada segmento, a partir da origem da parede."""
    inicio = (parede["origem"]["x"], parede["origem"]["y"])
    trechos = []
    for segmento in parede["segmentos"]:
        angulo = math.radians(segmento["angulo_absoluto"])
        fim = _somar(inicio, (segmento["comprimento"] * math.cos(angulo), segmento["comprimento"] * math.sin(angulo)))
        trechos.append((inicio, fim))
        inicio = fim
    return trechos


def angulos_relativos(segmentos):
    relativos = []
    for indice, segmento in enumerate(segmentos):
        anterior = segmentos[indice - 1]["angulo_absoluto"] if indice else 0
        relativos.append(normalizar_relativo(segmento["angulo_absoluto"] - anterior))
    return relativos


def folga_de_fechamento(parede):
    trechos = trechos_da_parede(parede)
    if not trechos:
        return 0
    return distancia(trechos[-1][1], (parede["origem"]["x"], parede["origem"]["y"]))


def mudar_comprimento(parede, indice, comprimento):
    """Os vértices seguintes andam junto; numa parede fechada, o último segmento é refeito para fechar."""
    segmentos = [dict(segmento) for segmento in parede["segmentos"]]
    segmentos[indice]["comprimento"] = comprimento
    ultimo = len(segmentos) - 1
    if parede["fechada"] and indice != ultimo and ultimo > 0:
        trechos = trechos_da_parede({"origem": parede["origem"], "segmentos": segmentos})
        dx = parede["origem"]["x"] - trechos[ultimo][0][0]
        dy = parede["origem"]["y"] - trechos[ultimo][0][1]
        segmentos[ultimo]["comprimento"] = math.hypot(dx, dy)
        segmentos[ultimo]["angulo_absoluto"] = math.degrees(math.atan2(dy, dx))
    relativos = angulos_relativos(segmentos)
    for segmento, relativo in zip(segmentos, relativos):
        segmento["angulo_relativo"] = relativo
    return {**parede, "segmentos": segmentos}


def geometria_do_arco(inicio, fim, flecha, sentido, espessura):
    corda = distancia(inicio, fim)
    direcao = _escalar(_subtrair(fim, inicio), 1 / corda)
    normal = _normal_esquerda(direcao)
    f = abs(flecha)
    raio = (corda * corda / 4 + f * f) / (2 * f)
    angulo_central = 4 * math.atan((2 * f) / corda)
    meio = _escalar(_somar(inicio, fim), 0.5)
    centro = _somar(meio, _escalar(normal, flecha - math.copysign(raio, flecha)))
    varredura = -math.copysign(angulo_central, flecha)
    de_fora = (sentido == "LEFT" and flecha > 0) or (sentido == "RIGHT" and flecha < 0)
    raio_da_face = raio + espessura if de_fora else raio - espessura
    maior = max(raio, raio_da_face)
    partes = max(1, math.ceil(angulo_central / (2 * math.acos(1 - ERRO_DE_CORDA_MM / maior))))
    return {
        "raio": raio, "centro": centro, "angulo_central": angulo_central, "comprimento": raio * angulo_central,
        "angulo_inicial": math.atan2(inicio[1] - centro[1], inicio[0] - centro[0]), "varredura": varredura,
        "raio_da_face": raio_da_face, "partes": partes,
    }


def pontos_do_arco(arco, r):
    pontos = []
    for k in range(arco["partes"] + 1):
        angulo = arco["angulo_inicial"] + arco["varredura"] * k / arco["partes"]
        pontos.append((arco["centro"][0] + r * math.cos(angulo), arco["centro"][1] + r * math.sin(angulo)))
    return pontos


def ponto_no_arco(arco, s):
    angulo = arco["angulo_inicial"] + math.copysign(1, arco["varredura"]) * (s / arco["raio"])
    return (arco["centro"][0] + arco["raio"] * math.cos(angulo), arco["centro"][1] + arco["raio"] * math.sin(angulo))


def _intersecao(p1, p2, p3, p4):
    d1 = _subtrair(p2, p1)
    d2 = _subtrair(p4, p3)
    cruz = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cruz) < 1e-9:
        return None
    u = ((p3[0] - p1[0]) * d2[1] - (p3[1] - p1[1]) * d2[0]) / cruz
    return _somar(p1, _escalar(d1, u))


def geometria_da_parede(parede):
    """Para cada segmento: trecho, linha desenhada, face deslocada (com esquadrias), comprimento e arco."""
    trechos = trechos_da_parede(parede)
    geometrias = []
    for segmento, (inicio, fim) in zip(parede["segmentos"], trechos):
        if segmento["flecha"] == 0:
            direcao = _escalar(_subtrair(fim, inicio), 1 / segmento["comprimento"])
            lado = 1 if segmento["sentido"] == "LEFT" else -1
            deslocamento = _escalar(_normal_esquerda(direcao), lado * segmento["espessura"])
            geometrias.append({"trecho": (inicio, fim), "linha": [inicio, fim], "face": [_somar(inicio, deslocamento), _somar(fim, deslocamento)],
                               "comprimento": segmento["comprimento"], "arco": None})
            continue
        arco = geometria_do_arco(inicio, fim, segmento["flecha"], segmento["sentido"], segmento["espessura"])
        linha = pontos_do_arco(arco, arco["raio"])
        linha[0] = inicio
        linha[-1] = fim
        geometrias.append({"trecho": (inicio, fim), "linha": linha, "face": pontos_do_arco(arco, arco["raio_da_face"]), "comprimento": arco["comprimento"], "arco": arco})
    n = len(parede["segmentos"])
    juntas = [(i, i + 1) for i in range(n - 1)] + ([(n - 1, 0)] if parede["fechada"] and n > 1 else [])
    for i, j in juntas:
        a, b = geometrias[i], geometrias[j]
        sa, sb = parede["segmentos"][i], parede["segmentos"][j]
        if a["arco"] or b["arco"] or sa["sentido"] != sb["sentido"]:
            continue
        ponto = _intersecao(a["face"][0], a["face"][1], b["face"][0], b["face"][1])
        if ponto is None or distancia(ponto, a["trecho"][1]) > LIMITE_DA_ESQUADRIA * max(sa["espessura"], sb["espessura"]):
            continue
        a["face"][1] = ponto
        b["face"][0] = ponto
    return geometrias


def poligono_do_segmento(geometria):
    return list(geometria["linha"]) + list(reversed(geometria["face"]))


def area_com_sinal(poligono):
    soma = 0
    for k in range(len(poligono)):
        a, b = poligono[k], poligono[(k + 1) % len(poligono)]
        soma += a[0] * b[1] - b[0] * a[1]
    return soma / 2


def _acrescentar(lista, ponto):
    if not lista or distancia(lista[-1], ponto) > 1e-6:
        lista.append(ponto)


def piso_da_parede(parede, geometrias):
    """Polígono da face interna de uma parede fechada (clarify Q3); parede aberta não gera piso."""
    if not parede["fechada"] or not geometrias:
        return None
    linha = []
    for geometria in geometrias:
        for ponto in geometria["linha"]:
            _acrescentar(linha, ponto)
    if len(linha) > 1 and distancia(linha[0], linha[-1]) < 1e-6:
        linha.pop()
    anti_horario = area_com_sinal(linha) > 0
    vertices = []
    for segmento, geometria in zip(parede["segmentos"], geometrias):
        para_dentro = segmento["sentido"] == "LEFT" if anti_horario else segmento["sentido"] == "RIGHT"
        for ponto in (geometria["face"] if para_dentro else geometria["linha"]):
            _acrescentar(vertices, ponto)
    if len(vertices) > 1 and distancia(vertices[0], vertices[-1]) < 1e-6:
        vertices.pop()
    return {"parede_id": parede["id"], "vertices": vertices, "area_mm2": abs(area_com_sinal(vertices))}


def ocupacao_na_linha(geometria, largura):
    if not geometria["arco"]:
        return largura
    raio = geometria["arco"]["raio"]
    if largura > 2 * raio:
        return None
    return raio * 2 * math.asin(largura / (2 * raio))


def pe_direito_em(segmento, fracao):
    return segmento["pe_direito_inicial"] + (segmento["pe_direito_final"] - segmento["pe_direito_inicial"]) * fracao


def _ponto_na_linha(geometria, s):
    if geometria["arco"]:
        return ponto_no_arco(geometria["arco"], s)
    inicio, fim = geometria["trecho"]
    return _somar(inicio, _escalar(_subtrair(fim, inicio), s / distancia(inicio, fim)))


def vao_da_abertura(abertura, segmento, geometria):
    ocupa = ocupacao_na_linha(geometria, abertura["largura"])
    if ocupa is None:
        return None
    total = geometria["comprimento"]
    menor = min(pe_direito_em(segmento, abertura["posicao"] / total), pe_direito_em(segmento, (abertura["posicao"] + ocupa) / total))
    return {"id": abertura["id"], "faixa": (0, total - ocupa), "peitoril_max": menor - abertura["altura"],
            "inicio": _ponto_na_linha(geometria, abertura["posicao"]), "fim": _ponto_na_linha(geometria, abertura["posicao"] + ocupa), "ocupa": ocupa}
