"""
Módulo em chapas e lista de peças parts_catalog 1.0.0 (061 RN-11 a RN-13; contrato §4).
Espelho de chapas.ts, regras.ts e listaDePecas.ts do MOBI. Com o padrão de fábrica, dá peça a peça o
que dá o extrator antigo (cutting/part_extractor.py); os casos-ouro pecas-addon/ provam.
"""

from .contrato import arredondar_medida

MEDIDA_MINIMA_DA_CHAPA = 50

CODIGOS = {
    "LATERAL_ESQUERDA": "LAT_ESQ", "LATERAL_DIREITA": "LAT_DIR", "BASE": "BASE", "TAMPO": "TAMPO", "FUNDO": "FUNDO",
    "PRATELEIRA": "PRAT", "DIVISORIA": "DIV", "PORTA": "PORTA", "FRENTE_DE_GAVETA": "GAV", "RODAPE": "RODAPE", "TRAVESSA": "TRAV",
}
NOMES = {
    "LATERAL_ESQUERDA": "Lateral Esquerda", "LATERAL_DIREITA": "Lateral Direita", "BASE": "Base Inferior", "TAMPO": "Tampo Superior",
    "FUNDO": "Fundo Traseiro", "PRATELEIRA": "Prateleira Interna", "DIVISORIA": "Divisória", "TRAVESSA": "Travessa", "RODAPE": "Rodapé",
    "FRENTE_DE_GAVETA": "Frente de Gaveta", "PORTA": "Porta Frontal",
}

CONSTRUCAO_DE_FABRICA = {
    "laterais": "PASSANTE", "tampo": "ENTRE_LATERAIS", "fundo": {"modo": "CANAL", "espessura": 6, "encaixe": 8},
    "rodape": {"altura": 0, "recuo": 0}, "porta": {"modo": "SOBREPOSTA", "folga": 2, "folga_central": 2, "espessura": 18},
    "prateleiras": {"quantidade": 1, "recuo_frontal": 20, "folga_lateral": 1, "espessura": 15},
    "divisorias": {"quantidade": 0}, "gavetas": {"quantidade": 0, "altura_frente": 180}, "travessas": {"quantidade": 0, "largura": 80},
    "fitas": {"frente": 1, "demais": 0.45, "portas": 1},
}


def medidas_derivadas(modulo):
    k = modulo["construcao"]
    pc = modulo["profundidade"] - k["fundo"]["espessura"] if k["fundo"]["modo"] == "SOBREPOSTO" else modulo["profundidade"]
    return {
        "li": modulo["largura"] - 2 * modulo["espessura"],
        "hi": modulo["altura"] - k["rodape"]["altura"] - 2 * modulo["espessura"],
        "pc": pc,
        "pi": pc - k["porta"]["espessura"] if k["porta"]["modo"] == "EMBUTIDA" else pc,
    }


def chapas_do_modulo(modulo):
    larg, a, e, k = modulo["largura"], modulo["altura"], modulo["espessura"], modulo["construcao"]
    d = medidas_derivadas(modulo)
    li, hi, pc, pi = d["li"], d["hi"], d["pc"], d["pi"]
    hr = k["rodape"]["altura"]
    caixa = {"topo": k["fitas"]["demais"], "base": k["fitas"]["demais"], "esquerda": k["fitas"]["demais"], "direita": k["fitas"]["frente"]}
    sem_fita = {"topo": 0, "base": 0, "esquerda": 0, "direita": 0}
    frente = {lado: k["fitas"]["portas"] for lado in ("topo", "base", "esquerda", "direita")}
    chapas = []
    contagem = {}

    def chapa(papel, largura, altura, espessura, veio, fitas, quantidade=1, nome=None):
        indice = contagem.get(papel, 0)
        contagem[papel] = indice + 1
        base = nome or NOMES[papel]
        chapas.append({"papel": papel, "indice": indice, "nome": base if indice == 0 else f"{base} {indice + 1}",
                       "largura": max(MEDIDA_MINIMA_DA_CHAPA, largura), "altura": max(MEDIDA_MINIMA_DA_CHAPA, altura),
                       "espessura": espessura, "quantidade": quantidade, "veio": veio, "fitas": fitas})

    tampo_sobreposto = e if k["tampo"] == "SOBREPOSTO" else 0
    altura_da_lateral = a - tampo_sobreposto if k["laterais"] == "PASSANTE" else a - hr - e - tampo_sobreposto
    chapa("LATERAL_ESQUERDA", pc, altura_da_lateral, e, "VERTICAL", caixa)
    chapa("LATERAL_DIREITA", pc, altura_da_lateral, e, "VERTICAL", caixa)
    chapa("BASE", li if k["laterais"] == "PASSANTE" else larg, pc, e, "HORIZONTAL", caixa)
    chapa("TAMPO", li if k["tampo"] == "ENTRE_LATERAIS" else larg, pc, e, "HORIZONTAL", caixa)
    if k["fundo"]["modo"] == "SOBREPOSTO":
        chapa("FUNDO", larg, a - hr, k["fundo"]["espessura"], "VERTICAL", sem_fita)
    else:
        chapa("FUNDO", li + 2 * k["fundo"]["encaixe"], hi + 2 * k["fundo"]["encaixe"], k["fundo"]["espessura"], "VERTICAL", sem_fita)
    divisorias = k["divisorias"]["quantidade"]
    largura_da_prateleira = (li - divisorias * e) / (divisorias + 1) - 2 * k["prateleiras"]["folga_lateral"]
    for _ in range(k["prateleiras"]["quantidade"] * (divisorias + 1)):
        chapa("PRATELEIRA", largura_da_prateleira, pi - k["prateleiras"]["recuo_frontal"], k["prateleiras"]["espessura"], "HORIZONTAL", caixa)
    for _ in range(divisorias):
        chapa("DIVISORIA", pi, hi, e, "VERTICAL", caixa)
    for _ in range(k["travessas"]["quantidade"]):
        chapa("TRAVESSA", li, k["travessas"]["largura"], e, "HORIZONTAL", caixa)
    if hr > 0:
        chapa("RODAPE", li, hr, e, "HORIZONTAL", sem_fita)
    g = k["porta"]["folga"]
    sobreposta = k["porta"]["modo"] == "SOBREPOSTA"
    largura_da_frente = larg - 2 * g if sobreposta else li - 2 * g
    altura_da_frente = a - hr if sobreposta else hi
    gavetas = k["gavetas"]["quantidade"]
    for _ in range(gavetas):
        chapa("FRENTE_DE_GAVETA", largura_da_frente, k["gavetas"]["altura_frente"], k["porta"]["espessura"], "HORIZONTAL", frente)
    altura_da_porta = altura_da_frente - (gavetas + 2) * g - gavetas * k["gavetas"]["altura_frente"]
    if modulo["portas"] == "DOUBLE":
        chapa("PORTA", (largura_da_frente - k["porta"]["folga_central"]) / 2, altura_da_porta, k["porta"]["espessura"], "VERTICAL", frente, 2, "Portas Frontais (Par)")
    elif modulo["portas"] != "NONE":
        chapa("PORTA", largura_da_frente, altura_da_porta, k["porta"]["espessura"], "VERTICAL", frente)

    for edicao in modulo.get("chapas_editadas", []):
        for item in chapas:
            if item["papel"] == edicao["papel"] and item["indice"] == edicao["indice"]:
                for campo in ("largura", "altura", "espessura", "veio"):
                    if campo in edicao:
                        item[campo] = edicao[campo]
    return chapas


def codigo_da_chapa(chapa):
    if chapa["papel"] == "PORTA":
        return "PORTA_PAR" if chapa["quantidade"] == 2 else "PORTA_UN"
    if chapa["papel"] in ("PRATELEIRA", "DIVISORIA", "TRAVESSA", "FRENTE_DE_GAVETA"):
        return f"{CODIGOS[chapa['papel']]}_{chapa['indice'] + 1:02d}"
    return CODIGOS[chapa["papel"]]


def pecas_do_modulo(modulo, nome_do_material=None):
    pecas = []
    for chapa in chapas_do_modulo(modulo):
        espessura = arredondar_medida(chapa["espessura"])
        pecas.append({
            "id": f"{modulo['id']}_{codigo_da_chapa(chapa)}", "name": f"{chapa['nome']} - {modulo['nome']}",
            "width": arredondar_medida(chapa["largura"]), "height": arredondar_medida(chapa["altura"]), "quantity": chapa["quantidade"],
            "thickness": espessura, "material": nome_do_material(espessura) if nome_do_material else f"{modulo['material']} {espessura} mm",
            "grain_direction": chapa["veio"], "module_ref": modulo["id"],
            "edges": {"top": chapa["fitas"]["topo"], "bottom": chapa["fitas"]["base"], "left": chapa["fitas"]["esquerda"], "right": chapa["fitas"]["direita"]},
        })
    return pecas
