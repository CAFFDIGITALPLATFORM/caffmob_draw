"""Alvo da seleção (feature 067, D-02): a propriedade é do objeto selecionado.

- `resolver`: snapshot `Target` do selecionado (tipo, escopo, dono, papel e caminho)
- `capabilities`: o que cada tipo executa
- `commands`: CommandRouter dos botões
- `view`: ViewModel puro que o painel desenha
- `adapters/`: um adaptador por tipo e o fallback rotulado
"""

_registered = False


def _modules():
    return ()


def register():
    global _registered
    if _registered:
        return
    for module in _modules():
        module.register()
    _registered = True


def unregister():
    global _registered
    if not _registered:
        return
    for module in reversed(_modules()):
        module.unregister()
    _registered = False
