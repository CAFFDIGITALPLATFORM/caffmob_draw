"""Seleção por clique no preview da janela do construtor (feature 023; RF-02, A005).

Núcleo puro, importável sem `bpy`: recebe os retângulos que o desenho do preview registrou e devolve a peça sob o
ponto. A última peça desenhada vence, porque é a que está por cima na vista.
"""


def peca_no_ponto(hits, x, y):
    """Item de `hits` cujo retângulo contém (x, y), ou None.

    `hits` é a lista que `preview.desenhar_preview` grava na sessão: dicionários com `rect` em pixels da região.
    """
    for item in reversed(hits or ()):
        x0, y0, x1, y1 = item['rect']
        if x0 <= x <= x1 and y0 <= y <= y1:
            return item
    return None


def rotulo(item):
    """Texto da barra "Selecionado: …" para o item escolhido."""
    if not item:
        return ""
    return item.get('nome') or item.get('papel') or ""


def chave(item):
    """Identidade do hit na vista: a mesma peça aparece uma vez na frontal e outra no corte lateral."""
    return item.get('nome'), item.get('vista')


def aplicar_clique(hits, x, y, atuais=(), acumular=False):
    """Nova seleção depois de um clique (RN-06).

    - clique no vazio limpa a seleção;
    - clique simples escolhe só a peça sob o ponto;
    - Shift/Ctrl acumula e alterna: peça já escolhida sai da seleção.
    """
    alvo = peca_no_ponto(hits, x, y)
    atuais = list(atuais or ())
    if alvo is None:
        return []
    if not acumular:
        return [alvo]
    if any(chave(item) == chave(alvo) for item in atuais):
        return [item for item in atuais if chave(item) != chave(alvo)]
    return atuais + [alvo]


def rotulo_conjunto(itens):
    """Texto da barra de seleção: nome da peça, contagem ou o convite ao clique."""
    itens = list(itens or ())
    if not itens:
        return ""
    if len(itens) == 1:
        return rotulo(itens[0])
    return f"{len(itens)} peças selecionadas"
