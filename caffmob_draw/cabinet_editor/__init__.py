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

Feature 017 (T027, D-04): a interface do editor 2D não é mais registrada — `window`, `ops_editor`, `ops_actions`,
`panels*` e `props` saem de `_modules()`, e com eles o `WindowManager.btm_cabinet_editor`. Continuam registrados só
`data_props` (os dados gravados no módulo, lidos pela biblioteca e pelo corte), `previews` (miniaturas),
`reflow_handler` (divisões acompanhando o vão) e `gallery` (a galeria de estruturas do "Criar armário" da biblioteca,
que `library_panel/ops_cabinet.py` chama sem guarda). Os núcleos puros (`structure`, `structures_core`, `divisions`,
`structure_inputs`, `elevation`, `validate`, `state`, `bays`, `catalog`, `extras`, `slides`, `appliances`, `position`,
`bridge`, `scene_*`, `gallery_core`) seguem importáveis fora do Blender.
"""


def _modules():
    # Import tardio: os núcleos puros são usados nos testes fora do Blender sem carregar `bpy`.
    from . import data_props, gallery, previews, reflow_handler
    return (data_props, previews, gallery, reflow_handler)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
