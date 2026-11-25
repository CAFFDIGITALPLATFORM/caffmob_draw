"""Construtor de armário v2 (feature 017, T004).

Cascata de submódulos do pacote. Só os módulos que registram algo no Blender entram em `_MODULES`, na ordem em que
`register()` os chama:

- `props`: PropertyGroups do armário, da peça e do contrato de chapas (T003)
- `exibicao`: variante de exibição e a migração de `exibicao_versao` no `load_post` (024, T010/T011)
- `build`: as chapas na cena (T020)
- `ops`: operadores Abrir, Gerar, Aplicar, Cancelar, Montar Caixa, Semear Contrato e Limpar (T021, T023); `Abrir`
  divide o `bl_idname` com o editor 2D antigo e se protege com a guarda de `ops.register` (D-03, T027)
- `anim`: abertura e fechamento animados e o operador Abrir/Fechar (T022)
- `panel`: painel da vista 3D com as sete abas (T023)
- `menu`: Abrir/Fechar, Duplicar e Excluir no menu de contexto (T024)
- `hud`: alternadores da caixa, inspetor da peça escolhida e realce da seleção na vista 3D (T025)
- `ponte`: módulo de biblioteca para o spec v2, Gerar e Recriar do módulo (T026)
- `window`: sessão da janela própria (Image Editor) do construtor (T001)
- `ops_window`: operadores Abrir/Aplicar/Cancelar/OK da janela própria (T002, T008)
- `panel_window`: painel de 7 abas desenhado na região lateral da janela própria (T006, T007, T011)

Os núcleos puros (`spec`, `vaos`, `chapas`, `conferencia`, `gavetas`, `portas`, `internos`, `resumo`, `corredica`,
`dobradica`, `converter`) ficam de fora: não registram nada no Blender e precisam ser importáveis nos testes sem `bpy`.

O import é tardio, dentro de `_modules()`, como em `cabinet_editor`: importar `caffmob_draw.armario_v2` fora do
Blender não carrega `bpy`. `unregister()` percorre a mesma tupla ao contrário, então desfaz exatamente o que
`register()` fez; as ações seguintes só acrescentam nomes a `_MODULES` (D-01, D-05).
"""

from importlib import import_module

# Cascata de registro, na ordem de `register()`; desregistro na ordem inversa.
_MODULES = ('props', 'exibicao', 'anim', 'ops', 'ops_drawer_convert', 'panel', 'menu', 'hud', 'ponte', 'window',
            'ops_window', 'panel_window')


def _modules():
    return tuple(import_module(f'.{name}', __name__) for name in _MODULES)


def register():
    for module in _modules():
        module.register()


def unregister():
    for module in reversed(_modules()):
        module.unregister()
