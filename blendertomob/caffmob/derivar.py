"""Grandezas derivadas no formato dos casos-ouro (contrato §3.1), como o derivarAmbiente do MOBI."""

import math

from .contrato import arredondar_angulo, arredondar_medida
from .geometria import angulos_relativos, geometria_da_parede, piso_da_parede, poligono_do_segmento, vao_da_abertura


def _p(ponto):
    return [arredondar_medida(ponto[0]), arredondar_medida(ponto[1])]


def derivar_ambiente(ambiente, chaves):
    saida = {}
    por_segmento = {}
    for parede in ambiente["paredes"]:
        geometrias = geometria_da_parede(parede)
        relativos = angulos_relativos(parede["segmentos"])
        for segmento, geometria in zip(parede["segmentos"], geometrias):
            por_segmento[segmento["id"]] = (segmento, geometria)
        if "segmentos" in chaves:
            saida.setdefault("segmentos", []).extend({
                "id": s["id"], "inicio": _p(g["trecho"][0]), "fim": _p(g["trecho"][1]), "z_base": arredondar_medida(s["afastamento"]),
                "altura_inicio": arredondar_medida(s["pe_direito_inicial"]), "altura_fim": arredondar_medida(s["pe_direito_final"]), "angulo_relativo": r,
            } for s, g, r in zip(parede["segmentos"], geometrias, relativos))
        if "contornos" in chaves:
            saida.setdefault("contornos", []).extend({"id": s["id"], "poligono": [_p(p) for p in poligono_do_segmento(g)]} for s, g in zip(parede["segmentos"], geometrias))
        if "arcos" in chaves:
            saida.setdefault("arcos", []).extend({
                "id": s["id"], "raio": arredondar_medida(g["arco"]["raio"]), "centro": _p(g["arco"]["centro"]),
                "comprimento_do_arco": arredondar_medida(g["arco"]["comprimento"]), "angulo_central": arredondar_angulo(math.degrees(g["arco"]["angulo_central"])),
            } for s, g in zip(parede["segmentos"], geometrias) if g["arco"])
        if "piso" in chaves:
            saida.setdefault("piso", [])
            piso = piso_da_parede(parede, geometrias)
            if piso:
                saida["piso"].append({"parede_id": piso["parede_id"], "vertices": [_p(v) for v in piso["vertices"]], "area_mm2": arredondar_medida(piso["area_mm2"])})
    if "aberturas" in chaves:
        saida["aberturas"] = []
        for abertura in ambiente["aberturas"]:
            alvo = por_segmento.get(abertura["segmento_id"])
            vao = alvo and vao_da_abertura(abertura, alvo[0], alvo[1])
            if vao:
                saida["aberturas"].append({"id": vao["id"], "faixa": [0, arredondar_medida(vao["faixa"][1])], "peitoril_max": arredondar_medida(vao["peitoril_max"]),
                                           "inicio": _p(vao["inicio"]), "fim": _p(vao["fim"])})
    return saida
