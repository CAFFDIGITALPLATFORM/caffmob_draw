"""Editor de Paredes 2D: contrato MOBI v2 ou planta a lápis do Home Builder 5.

- `studio` / `studio_interacao`: prancheta v2 e despacho puros, com documento em mm
- `scene_v2` / `studio_ui`: leitura, montagem v2, ações e campos do Studio
- `classico_v2`: o editor clássico sobre a cena v2 (desenho, ferramentas e painéis na unidade do projeto)
- `model`: nós, trechos, linhas interna/externa/referência e edição (Python puro, testável fora do Blender)
- `scene_io` / `apply`: leitura das paredes da cena e aplicação do rascunho no OK
- `props`: sessão do editor e campos do trecho (`WindowManager.btm_wall_editor`)
- `window`: janela própria (Image Editor) e desenho da planta
- `ops_editor`: abrir, modal de interação, OK/Cancelar
- `panels`: região lateral do editor
"""


def _modules():
    # Import tardio: `model` é usado nos testes fora do Blender sem carregar `bpy`.
    from . import classico_v2, ops_editor, panels, props, window, studio_ui
    return (props, studio_ui, classico_v2, window, ops_editor, panels)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
