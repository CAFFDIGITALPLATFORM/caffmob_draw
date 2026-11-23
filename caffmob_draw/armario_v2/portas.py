"""Portas de abrir e folhas deslizantes do armário v2 (feature 017, T017; RN-06, RN-10, RN-14).

Python puro, em milímetros. As portas de abrir dividem o comprimento entre 1 e 4 folhas, com a dobradiça à esquerda,
à direita ou alternada, e cada folha abre 95° no sentido da própria dobradiça. As folhas deslizantes seguem a fórmula
do mockup: `(comprimento + (n − 1) × sobreposição) / n`.

As duas famílias são exclusivas (RN-14). O recuo por papel (RN-06) é o que a porta deslizante com base por dentro
impõe: divisórias, prateleiras, gavetas e internos perdem a profundidade do trilho; laterais e bases continuam na
profundidade total. Com a base na frente, nada recua.
"""

from dataclasses import dataclass

ABERTURA_GRAUS = 95.0
SOBREPOSICAO_PADRAO = 30.0
MATERIAIS = ('MDF', 'VIDRO', 'ALUMINIO')
ESQUERDA, DIREITA, ALTERNADA = 'ESQUERDA', 'DIREITA', 'ALTERNADA'
DENTRO, FRENTE = 'DENTRO', 'FRENTE'

# Papéis que recuam na profundidade do trilho e papéis que não recuam nunca (RN-06).
PAPEIS_RECUADOS = ('DIVISORIA', 'PRATELEIRA', 'GAVETA', 'INTERNO')
PAPEIS_FIXOS = ('LATERAL', 'BASE_INF', 'BASE_SUP')


@dataclass(frozen=True)
class Folha:
    """Uma folha de porta ou de deslizante: largura, dobradiça, sentido de abertura, espessura e material."""

    indice: int
    largura: float
    dobradica: str
    sentido: float
    graus: float
    espessura: float
    material: str


def _validar_material(material):
    if material not in MATERIAIS:
        raise ValueError(f"Material de folha desconhecido: {material}")


def portas_de_abrir(comprimento, folhas, dobradica=ALTERNADA, espessura=15.0, material='MDF'):
    """Folhas de porta de abrir: largura igual entre elas e sentido oposto na dobradiça alternada (RF-13)."""
    folhas = int(folhas)
    if folhas < 1:
        raise ValueError("A porta precisa de pelo menos uma folha")
    if dobradica not in (ESQUERDA, DIREITA, ALTERNADA):
        raise ValueError(f"Dobradiça desconhecida: {dobradica}")
    _validar_material(material)
    largura = float(comprimento) / folhas
    resultado = []
    for indice in range(folhas):
        if dobradica == ALTERNADA:
            lado = ESQUERDA if indice % 2 == 0 else DIREITA
        else:
            lado = dobradica
        resultado.append(Folha(indice, largura, lado, -1.0 if lado == ESQUERDA else 1.0, ABERTURA_GRAUS,
                               float(espessura), material))
    return resultado


def folhas_deslizantes(comprimento, folhas, sobreposicao=SOBREPOSICAO_PADRAO, material='MDF', espessura=15.0):
    """Folhas deslizantes de 2 a 4, com sobreposição e sentidos alternados (RN-14)."""
    folhas = int(folhas)
    if not 2 <= folhas <= 4:
        raise ValueError("A porta deslizante tem de 2 a 4 folhas")
    _validar_material(material)
    largura = (float(comprimento) + (folhas - 1) * float(sobreposicao)) / folhas
    return [Folha(indice, largura, '', -1.0 if indice % 2 == 0 else 1.0, 0.0, float(espessura), material)
            for indice in range(folhas)]


def exclusividade(porta_ativa, deslizante_ativa):
    """`True` quando as duas famílias estão ativas juntas; lista vazia quando não há conflito (RN-14)."""
    return True if porta_ativa and deslizante_ativa else []


def recuo_por_papel(deslizante_ativa, base, trilho):
    """Recuo em mm de cada papel na profundidade, conforme a base da deslizante (RN-06)."""
    recuo = float(trilho) if deslizante_ativa and base == DENTRO else 0.0
    valores = {papel: 0.0 for papel in PAPEIS_FIXOS}
    valores.update({papel: recuo for papel in PAPEIS_RECUADOS})
    return valores
