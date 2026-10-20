"""Cálculos de paredes do Studio, sem operações de edição nem dependência do Blender.

O Studio usa shared/caffmob/{polilinha,arco,contorno,aberturas}; o porte v1 já espelha
essas rotinas. Reutilizar o cálculo evita duas definições de arco e esquadria no addon.
Trecho oculto continua na cadeia e nas juntas; cabe ao futuro construtor omitir sua malha.
"""
import math
from ..contrato import normalizar_relativo
from ..geometria import (geometria_da_parede, trechos_da_parede, geometria_do_arco,
                         poligono_do_segmento, pe_direito_em, vao_da_abertura)


def comprimento_da_linha(parede, indice, medida, lado, angulo, espessura):
    """Cálculo de comprimentoDaLinha de shared/studio/paredes.ts (sem editar trecho)."""
    s = parede['segmentos'][indice]
    if lado == 'interna' or s['flecha'] != 0:
        return medida
    deslocamento = espessura / 2 if lado == 'eixo' else espessura
    esquerda = 1 if s['sentido'] == 'LEFT' else -1
    segmentos = parede['segmentos']
    n = len(segmentos)
    anterior = segmentos[indice - 1] if indice > 0 else segmentos[-1] if parede['fechada'] and n > 1 else None
    seguinte = segmentos[indice + 1] if indice < n - 1 else segmentos[0] if parede['fechada'] and n > 1 else None
    giros = [normalizar_relativo(angulo - anterior['angulo_absoluto']) if anterior else None,
             normalizar_relativo(seguinte['angulo_absoluto'] - angulo) if seguinte else None]
    soma = sum(math.tan(math.radians(phi) / 2) for phi in giros if phi is not None and abs(phi) < 179)
    return medida + esquerda * deslocamento * soma


def recortes_da_parede(documento, segmento_id):
    """recortesDaParede de shared/studio/aberturas.ts, inclusive ocupação em arco."""
    for parede in documento['paredes']:
        for j, segmento in enumerate(parede['segmentos']):
            if segmento['id'] != segmento_id:
                continue
            geometria = geometria_da_parede(parede)[j]
            recortes = []
            for a in documento['aberturas']:
                if a['segmento_id'] != segmento_id:
                    continue
                vao = vao_da_abertura(a, segmento, geometria)
                if vao is not None:
                    ocupa = geometria['comprimento'] - vao['faixa'][1]
                    recortes.append(dict(id=a['id'], tipo=a['tipo'], inicio=a['posicao'], fim=a['posicao'] + ocupa,
                                         largura=a['largura'], altura=a['altura'], peitoril=a['peitoril'],
                                         base=segmento['afastamento'] + a['peitoril'],
                                         topo=segmento['afastamento'] + a['peitoril'] + a['altura']))
            return recortes
    return []


def calcular_paredes(documento):
    """Derivação numérica para comparação com o TypeScript; nenhuma malha é construída.

    `linha` é a face desenhada (interna na medição do Studio), `face` é a externa
    deslocada pelo sentido. Alturas e afastamento são relativos ao piso do pavimento.
    """
    resultado = []
    for parede in documento['paredes']:
        segmentos = []
        for s, g in zip(parede['segmentos'], geometria_da_parede(parede)):
            segmentos.append(dict(id=s['id'], estado=s['estado'], trecho=g['trecho'], linha=g['linha'], face=g['face'],
                                  comprimento=g['comprimento'], arco=g['arco'], poligono=poligono_do_segmento(g),
                                  base=s['afastamento'], topo_inicial=s['afastamento'] + pe_direito_em(s, 0),
                                  topo_final=s['afastamento'] + pe_direito_em(s, 1),
                                  recortes=recortes_da_parede(documento, s['id'])))
        resultado.append(dict(id=parede['id'], pavimento_id=parede['pavimento_id'], visivel=parede['visivel'], segmentos=segmentos))
    return resultado
