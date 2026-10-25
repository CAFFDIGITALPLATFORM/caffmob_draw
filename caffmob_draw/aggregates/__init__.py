"""Agregados e folhas de porta convertidas (feature 003, blocos B e folha de porta).

- `limits`, `sweep`: núcleos puros (testáveis fora do Blender)
- `props`: `Object.btm_aggregate`
- `convert`, `apply`: converter, desconverter e posicionar no espaço do pai
- `perforate`, `production`: recorte 3D, furo real e peça de produção
- `leaf`, `collision`, `overlay`: folha de porta, parada na batida e simulação gráfica
- `ops_import`, `ops_aggregate`, `panels`: importação, operadores e painel
- Feature 007: `import_units`, `grouping`, `slide_limits` (núcleos puros); `group_props`, `group`, `ops_group` (grupo
  de peças e Montar esquadria); `window_props`, `install`, `ops_install` (janela na parede)
"""


def _modules():
    # Import tardio: `limits` e `sweep` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import (apply, authored_props, collision, group_props, ops_aggregate, ops_authored, ops_authored_leaf,
                   ops_component_u, ops_group, ops_import, ops_install, ops_members, overlay, panels, props, stretch,
                   window_props)
    return (props, authored_props, ops_authored, ops_members, ops_authored_leaf, ops_component_u, group_props,
            window_props, apply, collision, ops_import, ops_aggregate, ops_group, ops_install, stretch, overlay, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
