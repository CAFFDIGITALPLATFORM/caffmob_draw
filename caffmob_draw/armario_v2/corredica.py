"""Corrediça telescópica ST48 do armário v2 (feature 017, T036; RN-08, D-19, RF-10).

Python puro, em milímetros. Calcula as duas corrediças de cada gaveta — uma em cada lateral — e as três partes de cada
conjunto: o **trilho externo**, preso na lateral do vão (fora da caixa da gaveta), o **trilho interno**, preso na
caixa da gaveta (dentro dela), e a **gaiola** de esferas a meio curso. As medidas saem do modelo do anexo
(`assets/slides/slide-st48-0200-0.obj`, 200 mm de curso, 35 mm de altura): o conjunto de reserva do `build` usa
exatamente estas caixas quando o arquivo não está disponível, então as três partes aparecem com as mesmas marcas e
medidas nas duas situações.

Nenhuma parte entra no plano de chapa: `papel` fica **vazio** e o papel de ferragem vai no campo `ferragem`
(`TRILHO_EXT`, `TRILHO_INT`, `GAIOLA`). `resumo.lista_de_pecas`, `conferencia.conferir` e
`cutting.part_sources.armario_v2_records` já descartam papel vazio, então a corrediça não aparece no corte (RF-19) e
a animação passa a reconhecer a gaiola por `ferragem` em vez do papel (RN-10, D-19).

Referencial igual ao de `build`: X centrado na largura, Y de `−profundidade` (frente) a 0 (trás), Z de 0 (piso) a
`altura`. A caixa recebida é a da gaveta, já descontada a frente e o recuo do trilho da deslizante (RN-06).
"""

import re

from . import portas as portas_mod

TRILHO_EXT, TRILHO_INT, GAIOLA = 'TRILHO_EXT', 'TRILHO_INT', 'GAIOLA'
FERRAGENS = (TRILHO_EXT, TRILHO_INT, GAIOLA)
ESQUERDA, DIREITA = 'ESQUERDA', 'DIREITA'
LADOS = (ESQUERDA, DIREITA)

# Medidas do conjunto ST48 do anexo, em milímetros: curso, altura e espessura de cada parte.
MEDIDAS = {
    TRILHO_EXT: {'comprimento': 200.0, 'altura': 35.0, 'espessura': 8.5},
    TRILHO_INT: {'comprimento': 173.5, 'altura': 20.0, 'espessura': 6.0},
    GAIOLA: {'comprimento': 60.0, 'altura': 3.92, 'espessura': 5.8},
}

ROTULOS = {TRILHO_EXT: "trilho externo", TRILHO_INT: "trilho interno", GAIOLA: "gaiola"}

# O OBJ traz quatro objetos (`slide-st48-0200-0_1` a `_4`): trilho externo, trilho interno e as duas gaiolas.
PAPEIS_DO_OBJ = {'1': TRILHO_EXT, '2': TRILHO_INT, '3': GAIOLA, '4': GAIOLA}

_OBJ = re.compile(r'_([1-4])(?:[._]\d+)?$')


def recuo(spec):
    """Quanto a gaveta e o conjunto recuam com a base da deslizante por dentro (RN-06), em milímetros."""
    if spec is None:
        return 0.0
    return portas_mod.recuo_por_papel(spec.deslizante_ativa, spec.deslizante_base, spec.trilho_profundidade)['GAVETA']


def papel_do_objeto(nome):
    """Papel de ferragem de um objeto importado do OBJ, pelo sufixo `_1` a `_4`, ou `None`.

    O import pode renomear por colisão (`_1.001`), então o sufixo é lido do fim do nome. Nada no arquivo identifica o
    papel: o casamento é este, como o `investigation.md` já registrava.
    """
    achado = _OBJ.search(str(nome or ''))
    return PAPEIS_DO_OBJ.get(achado.group(1)) if achado else None


def _caixa(x0, x1, y0, y1, z0, z1):
    return ((x0, y0, z0), (x1, y1, z1))


def _parte(ferragem, lado, indice, espessura, caixa, curso, conjunto):
    """Uma parte de ferragem: `papel` vazio e o papel em `ferragem`, fora do plano de chapa."""
    return {'papel': '', 'ferragem': ferragem,
            'nome': f"Corrediça {lado.lower()} {ROTULOS[ferragem]} da gaveta {indice}",
            'box': caixa, 'espessura': espessura, 'material': 'FERRAGEM', 'movel': ferragem != TRILHO_EXT,
            'curso': 0.0 if ferragem == TRILHO_EXT else curso, 'eixo': 'Y', 'lado': lado, 'conjunto': conjunto}


def pecas(caixa, curso=0.0, indice=1, lados=LADOS):
    """[dict] das corrediças de uma gaveta, em milímetros, na ordem trilho externo, interno e gaiola por lado.

    `caixa` é a caixa da gaveta no referencial do armário; `curso` é o curso da gaveta em milímetros (o mesmo que
    `build` grava na frente), usado pelo trilho interno e pela gaiola, que anda `MEIO_CURSO` dele na animação.
    """
    (x0, y0, z0), (x1, y1, z1) = caixa
    altura = z1 - z0
    profundidade = y1 - y0
    if altura <= 0.0 or profundidade <= 0.0:
        return []
    z_centro = (z0 + z1) / 2.0
    itens = []
    for lado in lados:
        esquerda = lado == ESQUERDA
        conjunto = None
        for ferragem in FERRAGENS:
            medidas = MEDIDAS[ferragem]
            espessura = medidas['espessura']
            comprimento = min(medidas['comprimento'], profundidade)
            if comprimento <= 0.0:
                continue
            # A gaiola fica a meio curso; os trilhos ficam ancorados no fundo da gaveta.
            y_ini = (y0 + (profundidade - comprimento) / 2.0) if ferragem == GAIOLA else (y1 - comprimento)
            altura_parte = min(medidas['altura'], altura)
            z_ini = z_centro - altura_parte / 2.0
            # Trilho externo e gaiola por fora da caixa; trilho interno por dentro dela.
            if ferragem == TRILHO_INT:
                x_a, x_b = (x0, x0 + espessura) if esquerda else (x1 - espessura, x1)
            else:
                x_a, x_b = (x0 - espessura, x0) if esquerda else (x1, x1 + espessura)
            parte = _caixa(x_a, x_b, y_ini, y_ini + comprimento, z_ini, z_ini + altura_parte)
            if ferragem == TRILHO_EXT:
                conjunto = parte
            itens.append(_parte(ferragem, lado, indice, espessura, parte, curso, conjunto))
        # O conjunto alinha o modelo importado pelo trilho externo, que é a caixa do conjunto inteiro.
        for item in itens:
            if item['lado'] == lado and item['conjunto'] is None:
                item['conjunto'] = conjunto
    return itens
