"""
Paredes do contrato como prismas de base quadrilátera (061 RF-37), em mm. Espelho do prismasDoAmbiente
da visão 3D do MOBI: a abertura parte a parede reta em até quatro pedaços (antes, depois, abaixo do
peitoril e acima da verga), então o vão sai na malha sem modificador booleano.
"""

from .geometria import geometria_da_parede, piso_da_parede


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def prismas_da_parede(parede, aberturas):
    prismas = []
    geometrias = geometria_da_parede(parede)
    for segmento, g in zip(parede["segmentos"], geometrias):
        z0 = segmento["afastamento"]

        def altura(u, s=segmento, z=z0):
            return z + s["pe_direito_inicial"] + (s["pe_direito_final"] - s["pe_direito_inicial"]) * u

        def pedaco(u0, u1, baixo, cima, linha, face):
            if u1 - u0 < 1e-6:
                return
            prismas.append({
                "base": [_lerp(linha[0], linha[1], u0), _lerp(linha[0], linha[1], u1), _lerp(face[0], face[1], u1), _lerp(face[0], face[1], u0)],
                "baixo": [baixo(u0), baixo(u1), baixo(u1), baixo(u0)], "cima": [cima(u0), cima(u1), cima(u1), cima(u0)],
            })

        if g["arco"]:
            partes = len(g["linha"]) - 1
            for k in range(partes):
                pedaco(0, 1, lambda u, z=z0: z, lambda u, k=k: altura((k + u) / partes), (g["linha"][k], g["linha"][k + 1]), (g["face"][k], g["face"][k + 1]))
            continue
        linha = (g["linha"][0], g["linha"][1])
        face = (g["face"][0], g["face"][1])
        vaos = sorted(({"u0": a["posicao"] / g["comprimento"], "u1": (a["posicao"] + a["largura"]) / g["comprimento"],
                        "peitoril": a["peitoril"], "verga": a["peitoril"] + a["altura"]}
                       for a in aberturas if a["segmento_id"] == segmento["id"]), key=lambda v: v["u0"])
        u = 0
        for vao in vaos:
            pedaco(u, vao["u0"], lambda _u, z=z0: z, altura, linha, face)
            if vao["peitoril"] > 0:
                pedaco(vao["u0"], vao["u1"], lambda _u, z=z0: z, lambda _u, z=z0, p=vao["peitoril"]: z + p, linha, face)
            pedaco(vao["u0"], vao["u1"], lambda _u, z=z0, v=vao["verga"]: z + v, altura, linha, face)
            u = max(u, vao["u1"])
        pedaco(u, 1, lambda _u, z=z0: z, altura, linha, face)
    return prismas, piso_da_parede(parede, geometrias)
