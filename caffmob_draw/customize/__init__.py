"""Personalização de módulos inseridos e biblioteca de módulos do usuário (feature 003, bloco A).

- `spec`, `manifest`: núcleos puros (testáveis fora do Blender)
- `props`: `Object.btm_custom`, gravado no vão ou na peça
- `adapters`: um adaptador por biblioteca (frameless, face frame, closets, `btm`)
- `reapply`: reaplica a personalização depois da reconstrução das frentes
- `library_io`, `ops_library`: salvar e inserir módulos
- `ops_customize`, `panels`: operadores e painel "Personalizar módulo"
- `finish_core`, `finish`, `finish_props`, `ops_finish`, `ops_finish_classify`, `finish_migration`: acabamentos por
  domínio (067 onda 2)
"""


def _modules():
    # Import tardio: `spec` e `manifest` são usados nos testes fora do Blender sem carregar `bpy`.
    from . import (finish_migration, finish_props, ops_customize, ops_finish, ops_finish_classify, ops_library,
                   panels, props)
    return (props, finish_props, finish_migration, ops_customize, ops_finish, ops_finish_classify, ops_library,
            panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
