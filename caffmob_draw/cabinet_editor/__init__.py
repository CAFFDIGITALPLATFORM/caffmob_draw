"""Editor de Armário (feature 004, incremento I3).

- `elevation`, `validate`, `state`: núcleos puros (vista frontal, validação, rascunho)
- `props`: sessão em memória e `WindowManager.btm_cabinet_editor`
- `bridge`: ler, editar e reaplicar o módulo pela biblioteca (adaptadores da 003)
- `window`: janela própria e desenho da vista frontal
- `ops_editor`, `ops_actions`, `panels`: abrir, modal, confirmar/cancelar, botões internos e painéis
- Feature 006: `data_props` (estrutura e divisões gravadas no módulo), `divisions` e `structure` (núcleos puros),
  `scene_divisions` (chapas na cena), `reflow_handler` (divisões acompanham o vão), `panels_structure` e
  `panels_divisions` (abas Estrutura e Divisão)
- Feature 008: `catalog`, `extras`, `bays`, `slides`, `appliances`, `position` (núcleos puros), `scene_parts`,
  `scene_extras`, `scene_interiors`, `scene_slides` (peças na cena), `previews` (miniaturas) e os painéis das abas
  Gavetas, Internos, Portas, Deslizantes e Fundos
"""


def _modules():
    # Import tardio: os núcleos puros são usados nos testes fora do Blender sem carregar `bpy`.
    from . import (data_props, gallery, ops_actions, ops_editor, panels, panels_backs, panels_divisions, panels_doors,
                   panels_drawers, panels_interior, panels_sliding, panels_structure, previews, props, reflow_handler,
                   window)
    return (data_props, props, previews, window, gallery, ops_editor, ops_actions, panels, panels_structure,
            panels_divisions, panels_drawers, panels_interior, panels_doors, panels_sliding, panels_backs,
            reflow_handler)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
