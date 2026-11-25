"""Fila de pedidos da janela do construtor (feature 023, T019; RN-02).

Núcleo puro, importável sem `bpy`: a fila guarda ações e o modal as processa em ordem, devolvendo os avisos das que
falharam sem interromper as seguintes. É o que permite os botões do painel só enfileirarem — quem escreve na cena é o
modal, num passo só.
"""


def enfileirar(fila, acao):
    """Acrescenta uma ação (callable ou pedido) ao fim da fila."""
    fila.append(acao)
    return acao


def processar(fila, executar):
    """Executa as ações em ordem, esvaziando a fila; devolve a mensagem de cada falha."""
    avisos = []
    while fila:
        acao = fila.pop(0)
        try:
            executar(acao)
        except Exception as erro:  # noqa: BLE001
            avisos.append(str(erro) or erro.__class__.__name__)
    return avisos
