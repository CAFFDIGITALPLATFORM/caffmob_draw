"""Biblioteca CAFFMob no topo da viewport (feature 012, incremento I3).

- `props`: estado de sessão (`WindowManager.btm_library`);
- `categories_core`, `categories`: categorias fixas e do usuário;
- `models_core`: modelos prontos (catálogo em `data/library_models.json`);
- `layout_core`, `draw`, `ops_click`: painel desenhado sempre e clique por keymap;
- `popover`: conteúdo da categoria; `ops_categories`: Criar categoria; `ops_cabinet`: Criar armário.
"""


def _modules():
    from . import draw, ops_cabinet, ops_categories, ops_click, popover, props
    return (props, popover, ops_categories, ops_cabinet, ops_click, draw)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
