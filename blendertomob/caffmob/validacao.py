"""
Validação do ambiente (061 RN-10; contrato §6): as regras de geometria, com os mesmos caminhos e códigos
do núcleo do MOBI. O esquema fechado é conferido pelo servidor na gravação (422); aqui o addon recusa
antes de enviar o que o servidor recusaria pela geometria.
"""

from .geometria import folga_de_fechamento, geometria_da_parede, geometria_do_arco, ocupacao_na_linha, pe_direito_em

TOLERANCIA_DE_FECHAMENTO_MM = 0.1
LIMITES_DO_MODULO = {"largura": (100, 3000), "altura": (100, 3000), "profundidade": (100, 2000), "espessura": (6, 50)}


def validar_ambiente(ambiente):
    erros = []

    def erro(caminho, codigo):
        erros.append({"caminho": caminho, "codigo": codigo})

    validos = {}
    for i, parede in enumerate(ambiente["paredes"]):
        parede_valida = True
        for j, segmento in enumerate(parede["segmentos"]):
            caminho = f"paredes[{i}].segmentos[{j}]"
            valido = True
            for campo in ("comprimento", "espessura", "pe_direito_inicial", "pe_direito_final"):
                if segmento[campo] <= 0:
                    erro(f"{caminho}.{campo}", "MAIOR_QUE_ZERO")
                    valido = False
            if valido and segmento["flecha"] != 0:
                arco = None
                if abs(segmento["flecha"]) <= segmento["comprimento"] / 2:
                    arco = geometria_do_arco((0, 0), (segmento["comprimento"], 0), segmento["flecha"], segmento["sentido"], segmento["espessura"])
                if not arco or arco["raio_da_face"] <= 0:
                    erro(f"{caminho}.flecha", "FLECHA_FORA")
                    valido = False
            if valido:
                validos[segmento["id"]] = (i, j)
            else:
                parede_valida = False
        if parede_valida and parede["fechada"] and folga_de_fechamento(parede) > TOLERANCIA_DE_FECHAMENTO_MM:
            erro(f"paredes[{i}].fechada", "PAREDE_ABERTA")

    geometrias = {}
    for k, abertura in enumerate(ambiente["aberturas"]):
        caminho = f"aberturas[{k}]"
        onde = validos.get(abertura["segmento_id"])
        if onde is None:
            if not any(s["id"] == abertura["segmento_id"] for p in ambiente["paredes"] for s in p["segmentos"]):
                erro(f"{caminho}.segmento_id", "SEGMENTO_INEXISTENTE")
            continue
        i, j = onde
        if i not in geometrias:
            geometrias[i] = geometria_da_parede(ambiente["paredes"][i])
        geometria = geometrias[i][j]
        segmento = ambiente["paredes"][i]["segmentos"][j]
        for campo in ("largura", "altura"):
            if abertura[campo] <= 0:
                erro(f"{caminho}.{campo}", "MAIOR_QUE_ZERO")
        if abertura["largura"] <= 0 or abertura["altura"] <= 0:
            continue
        ocupa = ocupacao_na_linha(geometria, abertura["largura"])
        if ocupa is None or ocupa > geometria["comprimento"]:
            erro(f"{caminho}.largura", "ABERTURA_MAIOR_QUE_SEGMENTO")
            continue
        maximo = geometria["comprimento"] - ocupa
        if abertura["posicao"] < 0 or abertura["posicao"] > maximo + 1e-9:
            erro(f"{caminho}.posicao", "ABERTURA_FORA_DO_SEGMENTO")
            continue
        total = geometria["comprimento"]
        menor = min(pe_direito_em(segmento, abertura["posicao"] / total), pe_direito_em(segmento, (abertura["posicao"] + ocupa) / total))
        if abertura["altura"] > menor:
            erro(f"{caminho}.altura", "ABERTURA_MAIOR_QUE_SEGMENTO")
            continue
        if abertura["tipo"] == "DOOR":
            fora = abertura["peitoril"] != 0
        else:
            fora = abertura["peitoril"] < 0 or abertura["peitoril"] > menor - abertura["altura"] + 1e-9
        if fora:
            erro(f"{caminho}.peitoril", "PEITORIL_FORA")

    for m, modulo in enumerate(ambiente["modulos"]):
        erros.extend(validar_medidas_do_modulo(modulo, f"modulos[{m}]"))
    return erros


def validar_medidas_do_modulo(modulo, caminho=""):
    prefixo = f"{caminho}." if caminho else ""
    return [{"caminho": f"{prefixo}{campo}", "codigo": "MEDIDA_DO_MODULO"}
            for campo, (minimo, maximo) in LIMITES_DO_MODULO.items() if not minimo <= modulo[campo] <= maximo]
