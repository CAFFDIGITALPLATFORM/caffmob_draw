"""Árvore de vãos e divisórias do armário v2 (feature 017, T013; RN-11, RN-12).

Python puro, em milímetros. A árvore nasce de um vão único (`s0`) e cada divisória parte o vão que a contém em dois:
o primeiro pedaço mantém o caminho do pai, os seguintes ganham `.b`, `.b.b`…, o mesmo formato de
`cabinet_editor.bays` (é a premissa de `ponte.py`). Divisória vertical parte a largura; prateleira horizontal parte a
altura.

As quatro variantes de cada eixo vêm do mockup do anexo: nas verticais o `distanciador` duplo ocupa 30 mm e as
`c_recuo` recuam 15 mm na traseira; nas horizontais a `prat_fixa` recua 20 mm na frente e a `prat_corredica` é a
prateleira que recebe corrediça. A variante fica em campos próprios da divisão (`tipo`, `recuo_tras`,
`recuo_frente`), sem inventar item novo nos enums do `data-delta.md`.

`duplicar` recusa quando o maior vão livre não comporta duas metades de 80 mm (RN-11) e devolve o motivo; a peça nova
nasce no meio desse maior vão livre.
"""

from dataclasses import dataclass
from uuid import uuid4

from ..data.i18n import tr
from . import spec as spec_mod

VERTICAL, HORIZONTAL = 'VERTICAL', 'HORIZONTAL'
FIXA, MOVEL, ESPACADOR = 'FIXA', 'MOVEL', 'ESPACADOR'
VAO_LIVRE_MINIMO = 80.0
RAIZ = 's0'

# Variantes das divisórias verticais: tipo, espessura (None = a do papel) e os recuos de traseira e frente.
VARIANTES_VERTICAIS = {
    'movel_s_recuo': {'tipo': MOVEL, 'espessura': None, 'recuo_tras': 0.0, 'recuo_frente': 0.0},
    'movel_c_recuo': {'tipo': MOVEL, 'espessura': None, 'recuo_tras': 15.0, 'recuo_frente': 0.0},
    'montante': {'tipo': FIXA, 'espessura': None, 'recuo_tras': 0.0, 'recuo_frente': 0.0},
    'distanciador': {'tipo': ESPACADOR, 'espessura': 30.0, 'recuo_tras': 0.0, 'recuo_frente': 0.0},
}

# Variantes das prateleiras horizontais: tipo e os mesmos recuos.
VARIANTES_HORIZONTAIS = {
    'prat_s_recuo': {'tipo': MOVEL, 'recuo_tras': 0.0, 'recuo_frente': 0.0},
    'prat_c_recuo': {'tipo': MOVEL, 'recuo_tras': 15.0, 'recuo_frente': 0.0},
    'prat_fixa': {'tipo': FIXA, 'recuo_tras': 0.0, 'recuo_frente': 20.0},
    'prat_corredica': {'tipo': MOVEL, 'recuo_tras': 0.0, 'recuo_frente': 0.0},
}


@dataclass(frozen=True)
class Divisao:
    """Uma divisória (eixo `VERTICAL`) ou prateleira (`HORIZONTAL`) dentro do vão `vao`."""

    uid: str
    eixo: str
    vao: str
    posicao: float          # mm a partir do início do vão, no eixo da divisão
    tipo: str
    espessura: float
    recuo_tras: float = 0.0
    recuo_frente: float = 0.0


@dataclass(frozen=True)
class Vao:
    """Um vão folha da árvore: caminho estável e medidas internas livres, em milímetros."""

    caminho: str
    largura: float
    altura: float


def _uid():
    return uuid4().hex[:8]


def _ordenar(divisoes, caminho, eixo):
    return sorted((d for d in divisoes if d.vao == caminho and d.eixo == eixo), key=lambda d: d.posicao)


def _segmentos(ordenadas, total):
    """[(início, fim, espessura consumida)] dos espaços livres, na ordem em que aparecem."""
    segmentos = []
    inicio = 0.0
    for divisao in ordenadas:
        corte = min(max(divisao.posicao, inicio), total)
        segmentos.append((inicio, corte, divisao.espessura))
        inicio = corte + divisao.espessura
    if total - inicio > 1e-9:
        segmentos.append((inicio, total, 0.0))
    return segmentos


def _faixas(ordenadas, total):
    """[(início, fim)] dos espaços livres com largura positiva."""
    return [(inicio, fim) for inicio, fim, _espessura in _segmentos(ordenadas, total) if fim - inicio > 1e-9]


def _reservar(caminho, indice, sufixo, usados):
    """Caminho do filho `indice`: o primeiro herda o do pai, os demais ganham o sufixo do eixo."""
    if indice == 0:
        usados.add(caminho)
        return caminho
    candidato = caminho + sufixo * indice
    nome, extra = candidato, 2
    while nome in usados:
        nome = f"{candidato}{extra}"
        extra += 1
    usados.add(nome)
    return nome


def _reservar_todos(caminho, quantidade, sufixo, usados):
    """Reserva todos os caminhos irmãos antes de descer na árvore, para um ramo não roubar o nome do outro."""
    return [_reservar(caminho, indice, sufixo, usados) for indice in range(quantidade)]


def _varrer(divisoes, spec):
    """(regiões, células, folhas) da árvore inteira.

    `regiões` guarda a **primeira** medida de cada caminho: o vão inteiro, referencial das posições das suas
    divisórias. `células` guarda a **última**: o primeiro pedaço, que herda o caminho, e é onde o conteúdo do vão é
    colocado (gaveta, interno, porta). As `folhas` são os vãos sem subdivisão.
    """
    regioes = {}
    celulas = {}
    folhas = []
    usados = set()

    def visitar(caminho, x, z, largura, altura, ignorar=frozenset()):
        regioes.setdefault(caminho, (x, z, largura, altura))
        celulas[caminho] = (x, z, largura, altura)
        usados.add(caminho)
        verticais = [] if VERTICAL in ignorar else _ordenar(divisoes, caminho, VERTICAL)
        horizontais = [] if HORIZONTAL in ignorar else _ordenar(divisoes, caminho, HORIZONTAL)
        if verticais:
            # As verticais partem o vão em colunas. As prateleiras do mesmo caminho ficam para a primeira coluna, que
            # herda o caminho e é quem as aplica: assim o vão nunca aplica os dois eixos no mesmo nível e os caminhos
            # das colunas (`.b`) não disputam nome com os das faixas (`.a`).
            segmentos = [s for s in _segmentos(verticais, largura) if s[1] - s[0] > 1e-9]
            nomes = _reservar_todos(caminho, len(segmentos), '.b', usados)
            for nome, (inicio, fim, _espessura) in zip(nomes, segmentos):
                # O filho que herda o caminho acumula o eixo já aplicado e desce sem repetir a mesma divisão; os
                # demais têm caminho próprio e começam sem restrição.
                visitar(nome, x + inicio, z, fim - inicio, altura,
                        ignorar | {VERTICAL} if nome == caminho else frozenset())
        elif horizontais:
            segmentos = [s for s in _segmentos(horizontais, altura) if s[1] - s[0] > 1e-9]
            nomes = _reservar_todos(caminho, len(segmentos), '.a', usados)
            for nome, (inicio, fim, _espessura) in zip(nomes, segmentos):
                visitar(nome, x, z + inicio, largura, fim - inicio,
                        ignorar | {HORIZONTAL} if nome == caminho else frozenset())
        else:
            folhas.append(Vao(caminho, largura, altura))

    visitar(RAIZ, 0.0, 0.0, spec_mod.largura_interna(spec), spec_mod.altura_interna(spec))
    return regioes, celulas, folhas


def arvore(divisoes, spec):
    """Vãos folha da árvore, em ordem de leitura (esquerda para a direita, de baixo para cima)."""
    return _varrer(divisoes, spec)[2]


def regioes(divisoes, spec):
    """{caminho: (x, z, largura, altura)} onde o conteúdo de cada vão é colocado, em mm desde o canto interno."""
    return _varrer(divisoes, spec)[1]


def _regiao(divisoes, spec, caminho):
    registro = _varrer(divisoes, spec)[0]
    if caminho not in registro:
        raise ValueError(f"Vão desconhecido: {caminho}")
    _x, _z, largura, altura = registro[caminho]
    return largura, altura


def inserir_vertical(divisoes, spec, vao, variante, posicao=None):
    """(lista nova, divisão criada). Sem `posicao`, a divisória nasce no meio do vão."""
    dados = VARIANTES_VERTICAIS.get(variante)
    if dados is None:
        raise ValueError(f"Variante de divisória desconhecida: {variante}")
    largura, _altura = _regiao(divisoes, spec, vao)
    if posicao is None:
        posicao = largura / 2.0
    if not 0.0 < posicao < largura:
        raise ValueError(f"Posição da divisória fora do vão de {largura:g} mm")
    espessura = dados['espessura'] if dados['espessura'] is not None else spec.espessura_divisoria
    divisao = Divisao(_uid(), VERTICAL, vao, float(posicao), dados['tipo'], float(espessura),
                      dados['recuo_tras'], dados['recuo_frente'])
    return list(divisoes) + [divisao], divisao


def inserir_horizontal(divisoes, spec, vao, variante, posicao=None):
    """(lista nova, prateleira criada). Sem `posicao`, a prateleira nasce no meio do vão."""
    dados = VARIANTES_HORIZONTAIS.get(variante)
    if dados is None:
        raise ValueError(f"Variante de prateleira desconhecida: {variante}")
    _largura, altura = _regiao(divisoes, spec, vao)
    if posicao is None:
        posicao = altura / 2.0
    if not 0.0 < posicao < altura:
        raise ValueError(f"Posição da prateleira fora do vão de {altura:g} mm")
    divisao = Divisao(_uid(), HORIZONTAL, vao, float(posicao), dados['tipo'], float(spec.espessura_prateleira),
                      dados['recuo_tras'], dados['recuo_frente'])
    return list(divisoes) + [divisao], divisao


def matriz(divisoes, spec, vao, linhas, colunas, prioridade=VERTICAL):
    """Insere `colunas` divisórias e `linhas` prateleiras em cada coluna resultante (RN-12).

    `linhas` e `colunas` são quantidades de divisórias, não de células: 2 × 1 num vão de 970 mm cria uma divisória e
    duas prateleiras, como no RF-07. A prioridade só decide a ordem em que as peças entram na lista.
    """
    largura, altura = _regiao(divisoes, spec, vao)
    colunas = max(1, int(colunas))
    linhas = max(1, int(linhas))
    verticais = [Divisao(_uid(), VERTICAL, vao, largura * i / (colunas + 1), MOVEL,
                         float(spec.espessura_divisoria)) for i in range(1, colunas + 1)]
    horizontais = []
    for indice in range(colunas + 1):
        caminho = vao if indice == 0 else vao + '.b' * indice
        for linha in range(1, linhas + 1):
            horizontais.append(Divisao(_uid(), HORIZONTAL, caminho, altura * linha / (linhas + 1), MOVEL,
                                       float(spec.espessura_prateleira)))
    novas = horizontais + verticais if prioridade == HORIZONTAL else verticais + horizontais
    return list(divisoes) + novas


def duplicar(divisoes, uid, spec):
    """(lista, nova divisão ou None, motivo). A nova nasce no meio do maior vão livre do pai (RN-11)."""
    alvo = next((d for d in divisoes if d.uid == uid), None)
    if alvo is None:
        return list(divisoes), None, tr("Divisão não encontrada")
    largura, altura = _regiao(divisoes, spec, alvo.vao)
    total = largura if alvo.eixo == VERTICAL else altura
    faixas = _faixas(_ordenar(divisoes, alvo.vao, alvo.eixo), total)
    if not faixas:
        return list(divisoes), None, tr("Não há vão livre para duplicar")
    inicio, fim = max(faixas, key=lambda faixa: faixa[1] - faixa[0])
    meio = (inicio + fim) / 2.0
    livre_esq = meio - inicio
    livre_dir = fim - (meio + alvo.espessura)
    menor_livre = min(livre_esq, livre_dir)
    if menor_livre < VAO_LIVRE_MINIMO - 1e-9:
        return list(divisoes), None, tr(
            "Vão livre insuficiente para duplicar: {} mm (mínimo {} mm de cada lado)").format(
            f"{menor_livre:g}", f"{VAO_LIVRE_MINIMO:g}")
    nova = Divisao(_uid(), alvo.eixo, alvo.vao, meio, alvo.tipo, alvo.espessura, alvo.recuo_tras, alvo.recuo_frente)
    return list(divisoes) + [nova], nova, ''


def remover(divisoes, uid):
    """Lista sem a divisão `uid`; o vão do pai volta a ser único."""
    return [d for d in divisoes if d.uid != uid]
