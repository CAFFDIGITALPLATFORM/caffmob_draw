"""Colisão de corpo entre itens e com paredes, piso e teto (feature 004, incremento I2; feature 066, onda 1).

- `obb`, `rules`: núcleos puros (caixa orientada, pares, classificação, ordem, primeiro contato)
- `props`: `WindowManager.btm_collision` (não salvo), lista efêmera do diagnóstico
- `scan`: itens da cena, confirmação pela malha e gravação do diagnóstico
- `guard`: o movimento para no primeiro contato, em silêncio (066, D-03)
- `ops_collision`, `panels`: diagnóstico técnico sob pedido (popup com Ir para e Afastar) e os painéis

O destaque permanente na viewport (`overlay.py`) e o "desatualizado" (`stale.py`) saíram na 066 (D-07, RF-010).
"""


def _modules():
    # Import tardio: `obb` e `rules` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import guard, ops_collision, panels, props
    return (props, guard, ops_collision, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
