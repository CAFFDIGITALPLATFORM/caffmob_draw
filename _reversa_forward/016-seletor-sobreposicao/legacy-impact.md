# Legacy Impact: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`
> Política de edição do legado na execução: `allowLegacyEdits: true`, `allowedPaths: ["***", "caffmob_draw/*", "tests/*"]`
> (o padrão `***` casa com qualquer caminho, então a liberação foi irrestrita na prática)

## 1. Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|-----------------|------------|------|------------|---------------|
| `caffmob_draw/selection/overlap_core.py` | Seleção (novo núcleo) | componente-novo | LOW | Ordenação, estado do seletor e geometria do painel, puro, sem `bpy` |
| `caffmob_draw/selection/overlap_select.py` | Seleção (viewport) | componente-novo | MEDIUM | Operador modal novo, dois `draw_handler` de sessão e item de keymap próprio |
| `caffmob_draw/ui/context_menu.py` | Interface (menu de contexto) | regra-alterada | LOW | Ganha um item a mais no menu de objeto, com `INVOKE_DEFAULT`; os itens anteriores ficam iguais |
| `caffmob_draw/__init__.py` | Registro da extensão | regra-alterada | MEDIUM | Duas entradas na lista de hot-reload, import explícito e chamadas nas cascatas de `register`/`unregister` |
| `caffmob_draw/data/translations/sobreposicao.json` | Tradução | componente-novo | LOW | Catálogo de uma área nova, dez textos, `pt_BR` e `en_US` |
| `tests/test_overlap_core.py` | Testes | componente-novo | LOW | Testes puros do núcleo |
| `tests/blender_016_overlap_smoke.py` | Testes | componente-novo | LOW | Fumaça no Blender 5.2, em segundo plano |

Nenhum arquivo de dado, `.blend` do pacote, esquema de propriedade ou biblioteca de produto foi tocado.

## 2. Diff conceitual por componente

**Seleção (viewport).** O pacote ganha um núcleo puro e um operador modal. O núcleo não conhece o Blender: recebe a
lista `(distância, objeto)` e devolve os objetos ordenados sem repetir, guarda marcados, foco e rolagem, e calcula o
retângulo do painel (390 px, linhas de 25, cabeçalho 78, rodapé 62, 12 linhas visíveis). O operador
`caffmob.overlap_select` é `{'INTERNAL'}` porque não altera dado do projeto: abre com uma passada de `ray_cast` por
objeto `MESH` visível e selecionável, desenha o painel em `POST_PIXEL` e a caixa do foco em `POST_VIEW`, e só aplica a
seleção no `Enter`. O isolamento usa `hide_set` com o mapa original guardado, restaurado no confirmar, no cancelar, no
erro e no `unregister`.

**Interface (menu de contexto).** `draw_context_menu` continua montando o submenu do objeto, as ações frequentes do
alvo, o plano de inserção e o separador de fecho. Entre o plano de inserção e o separador entra o item do seletor, com
rótulo do catálogo e `INVOKE_DEFAULT`, que abre o operador no ponto do cursor da viewport.

**Registro da extensão.** `_submodule_names` ganha `selection.overlap_core` antes de `selection.overlap_select`, o
import explícito acompanha `component_props/component_select/component_pick`, e as cascatas chamam `overlap_select`
depois da seleção por componente (registro) e antes dela (remoção). `overlap_core` só entra na lista de hot-reload,
porque não tem `register`.

**Concorrência com o que já existia.** `Alt + clique` e `Alt + Shift + clique` continuam com
`caffmob.component_pick`; o seletor ocupa `Ctrl + Alt + clique`, que antes caía no `view3d.select`. O modal não altera
seleção nem ativo até o `Enter`, então o normalizador de `component_select` não tem o que promover durante a
inspeção.

## 3. Preservadas

| Regra | Continua verdadeira porque |
|-------|----------------------------|
| RN-SELECTION-01 (precedência do classificador) | Nada em `classify.py` mudou; o seletor só lê `type`, visibilidade e `hide_select` |
| RN-SELECTION-04 (raiz do componente) | A seleção aplicada no `Enter` passa pelo normalizador como qualquer clique |
| RN-SELECTION-06 (excluir leva a subárvore) | O seletor não apaga nada |
| RN-SELECTION-07 (normalizador suspenso com modal da extensão) | O seletor não mexe na seleção durante a inspeção |
| RN-SELECTION-08 (gate das bibliotecas herdadas) | Intocado |
| RN-SELECTION-09 (Alt + clique escolhe a peça) | O novo item usa `Ctrl + Alt`, e a fumaça confere o mapa `3D View` |
| RN-SELECTION-10 (interruptor salvo no arquivo) | Nenhuma propriedade nova foi criada |
| RN-SELECTION-11 a 14 (dimensões editáveis) | Intocados |

## 4. Modificadas

Nenhuma regra 🟢 do `_reversa_sdd/domain.md` foi alterada ou removida. A entrega é aditiva: um operador novo, um
catálogo novo e um item a mais em dois contratos existentes (menu de contexto e cascata de registro), sem mudar o
comportamento anterior de nenhum deles.
