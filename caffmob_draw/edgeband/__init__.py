"""Fita de borda visual (feature 067, onda 4; D-21, D-22; RF-080 a RF-085).

- `core`: núcleo puro (bordas expostas, união coplanar, estado do rótulo, chaves por uid de borda)
- `props`: `Object.btm_edgeband` e `Object.btm_cut_exclude` na malha da fita
- `pieces`: as peças do componente como caixas no referencial do dono
- `build`, `sync`: a malha da faixa e a sincronia incremental por `params_hash`
- `ops`: criar e aplicar, mudar cor e criar nas faltantes, num passo de Undo

A fita é visual: fica fora do plano de corte (`btm_cut_exclude`), da colisão e dos alvos de textura (RN-11). As linhas
`Edge L1/L2/W1/W2` do corte não mudam (D-22).
"""


def _modules():
    # Import tardio: `core` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import ops, props, sync
    return (props, sync, ops)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
