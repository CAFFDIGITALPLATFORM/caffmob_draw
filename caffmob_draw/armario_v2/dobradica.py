"""Dobradiça de giro do armário v2 (feature 026; modelo `MODELS/DOBRADIÇA.obj`).

Python puro, em milímetros. Calcula as dobradiças de cada folha de porta de abrir: a quantidade pela altura da folha e
a posição de cada uma na aresta da dobradiça, com o copo no verso da porta e o braço entrando no armário.

As medidas saem do modelo do anexo (`assets/hinges/dobradica.obj`, 27,2 × 87,8 × 52,2 mm, já em metros): quando o
arquivo não está disponível, o `build` gera a caixa equivalente com exatamente estas medidas, então a dobradiça aparece
com a mesma marca e o mesmo tamanho nas duas situações.

Nenhuma parte entra no plano de chapa: `papel` fica **vazio** e o papel de ferragem vai no campo `ferragem`
(`DOBRADICA`), como na corrediça (RN-08). `resumo.lista_de_pecas`, `conferencia.conferir` e
`cutting.part_sources.armario_v2_records` já descartam papel vazio, então a dobradiça não aparece no corte.

Referencial igual ao de `build`: X centrado na largura, Y de `−profundidade` (frente) a 0 (trás), Z de 0 (piso) a
`altura`. A caixa recebida é a da folha de porta.
"""

from . import portas as portas_mod

DOBRADICA = 'DOBRADICA'
ESQUERDA, DIREITA = 'ESQUERDA', 'DIREITA'

# Medidas do modelo do anexo, em milímetros: espessura (X), braço (Y) e altura (Z).
MEDIDAS = {'espessura': 27.2, 'braco': 87.8, 'altura': 52.2}

# Regra de mercado para a quantidade e para a distância do parafuso de ponta à borda da folha.
DISTANCIA_DAS_PONTAS = 100.0


def quantidade(altura):
    """Número de dobradiças de uma folha pela altura, em milímetros (2 até 900, 5 acima de 2000)."""
    altura = float(altura)
    if altura <= 900.0:
        return 2
    if altura <= 1600.0:
        return 3
    if altura <= 2000.0:
        return 4
    return 5


def alturas(altura):
    """Z central de cada dobradiça, de baixo para cima, na folha de altura `altura`."""
    altura = float(altura)
    total = quantidade(altura)
    if altura <= 2.0 * DISTANCIA_DAS_PONTAS:
        passo = altura / (total + 1.0)          # folha baixa: distribui sem passar das bordas
        return [passo * (indice + 1) for indice in range(total)]
    inferior, superior = DISTANCIA_DAS_PONTAS, altura - DISTANCIA_DAS_PONTAS
    if total == 2:
        return [inferior, superior]
    passo = (superior - inferior) / (total - 1)
    return [inferior + passo * indice for indice in range(total)]


def _caixa(x0, x1, y0, y1, z0, z1):
    return ((x0, y0, z0), (x1, y1, z1))


def _parte(nome, lado, caixa, espessura, graus):
    """Uma dobradiça: `papel` vazio e o papel em `ferragem`, fora do plano de chapa."""
    return {'papel': '', 'ferragem': DOBRADICA, 'nome': nome, 'box': caixa, 'espessura': espessura,
            'material': 'FERRAGEM', 'movel': True, 'curso': graus, 'eixo': 'GIRO', 'lado': lado,
            'conjunto': caixa}


def pecas(caixa_porta, lado, indice, graus=portas_mod.ABERTURA_GRAUS):
    """[dict] das dobradiças de uma folha de porta, em milímetros, de baixo para cima.

    `caixa_porta` é a caixa da folha no referencial do armário e `lado` é a aresta da dobradiça
    (`ESQUERDA`/`DIREITA`). O copo fica no verso da porta (y mínimo da caixa) e o braço entra no armário; a
    espessura do modelo vai da aresta da dobradiça para dentro da folha.
    """
    (x0, y0, z0), (x1, y1, z1) = caixa_porta
    altura, largura_folha = z1 - z0, x1 - x0
    if altura <= 0.0 or largura_folha <= 0.0:
        return []
    espessura = min(MEDIDAS['espessura'], largura_folha)
    braco = min(MEDIDAS['braco'], max(0.0, -y0))          # o braço não passa da face de trás do armário
    altura_parte = min(MEDIDAS['altura'], altura)
    if braco <= 0.0 or altura_parte <= 0.0:
        return []
    esquerda = lado != DIREITA
    x_a, x_b = (x0, x0 + espessura) if esquerda else (x1 - espessura, x1)
    itens = []
    for numero, centro in enumerate(alturas(altura), start=1):
        z_a = z0 + centro - altura_parte / 2.0
        z_a = min(max(z0, z_a), z1 - altura_parte)
        itens.append(_parte(f"Dobradiça {numero} da porta {indice}", lado,
                            _caixa(x_a, x_b, y0, y0 + braco, z_a, z_a + altura_parte), espessura, graus))
    return itens
