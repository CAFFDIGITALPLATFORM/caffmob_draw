# Actions: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-19`
> Roadmap: `_reversa_forward/016-seletor-sobreposicao/roadmap.md`

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 15 |
| Paralelizáveis (`[//]`) | 5 |
| Maior cadeia de dependência | 8 (T003 → T004 → T005 → T007 → T008 → T010 → T014 → T015) |

Fases: preparação 2, testes 1, núcleo 6, integração 4, polimento 2.

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Medir o custo do raio na cena real: script descartável no Blender 5.2 que monta 2.000 malhas sobrepostas e cronometra uma passada de `evaluated.ray_cast` por objeto `MESH` elegível; registrar o número e a conclusão em `investigation.md` (se passar de 1 s, anotar a poda por caixa envolvente e `visible_camera` que será aplicada em T007) | - | `[//]` | `_reversa_forward/016-seletor-sobreposicao/investigation.md` | 🟡 | `[X]` |
| T002 | Criar o catálogo `sobreposicao.json` com os textos do seletor em `pt_BR` e `en_US`: título e total do cabeçalho, isolamento ligado e desligado, aviso de nenhum objeto elegível, rótulos do rodapé (`Enter`, `Esc`, `I`, setas, `+`/`-`, `Ctrl+A`, `Ctrl+/`) e rótulo do item de menu; conferir que nenhum texto já pertence a outro catálogo | - | `[//]` | `caffmob_draw/data/translations/sobreposicao.json` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Escrever `test_overlap_core.py` (unittest puro, sem `bpy`) cobrindo `rank` (ordem por distância e sem repetidos), `Picker` (`toggle`, `mark_all`, `invert`, `add`, `remove`, `move`, `scroll_by`, foco sempre visível na rolagem), `panel_rect` (390 px, cabeçalho 78, rodapé 62, presa à região, vira para o outro lado perto da borda), `row_at` e `action_at` (linha, roda, botões do rodapé e área fora do painel) | - | `[//]` | `tests/test_overlap_core.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Implementar `rank(hits)` no núcleo puro: ordenar por distância de mundo, da frente para trás, sem repetir objeto, aceitando as tuplas que o operador monta com o nome lido na hora do uso | T003 | - | `caffmob_draw/selection/overlap_core.py` | 🟢 | `[X]` |
| T005 | Implementar `Picker` no núcleo puro: guardar achados, marcados, foco e rolagem; `toggle`, `mark_all`, `invert`, `add`, `remove`, `move` (sem passar das pontas), `scroll_by` (uma linha por toque, com `MAX_VISIBLE = 12`) e manter o foco dentro da janela visível | T004 | - | `caffmob_draw/selection/overlap_core.py` | 🟢 | `[X]` |
| T006 | Implementar a geometria do painel no núcleo puro: constantes de largura e altura das linhas, `panel_rect` ao lado do cursor preso à região, `row_at` para a linha sob o ponto e `action_at` para roda, rodapé e clique fora do painel | T004 | - | `caffmob_draw/selection/overlap_core.py` | 🟢 | `[X]` |
| T007 | Criar `overlap_select.py` com o operador `caffmob.overlap_select` (`{'INTERNAL'}`), `poll` de `VIEW_3D` em `WINDOW` e modo `OBJECT`, `invoke` que guarda seleção, ativo e `hide_get()` do view layer e coleta os achados com uma passada em `context.view_layer.objects` (só `MESH`, `visible_get()`, sem `hide_select`), `evaluated_get(depsgraph)` e `evaluated.ray_cast` no espaço local, tudo em `try/except`; incluir a referência de módulo ao seletor aberto e `cancel_active()` (D-10) | T005 | - | `caffmob_draw/selection/overlap_select.py` | 🟢 | `[X]` |
| T008 | Implementar o `modal` no mesmo arquivo: setas e roda para foco e rolagem, `+`/`-`, `Ctrl+A`, `Ctrl+/`, `I` para isolamento, clique em linha e no rodapé via `action_at`, `Enter` aplicando exatamente os marcados (foco vira o ativo) e `Esc`/botão direito restaurando seleção, ativo e visibilidade, sem empilhar desfazer | T006, T007 | - | `caffmob_draw/selection/overlap_select.py` | 🟢 | `[X]` |
| T009 | Desenhar a sessão no mesmo arquivo: painel em `POST_PIXEL` com `canvas2d.draw.begin/rect/outline/text/end` e `hb_gpu_draw.point_in_rect`, cabeçalho com total e estado do isolamento, linhas com marcação e realce do foco, rodapé com os atalhos, e destaque do foco em `POST_VIEW` pela caixa envolvente de `bound_box` com `matrix_world` e `line_width_set`; remover os dois handlers em confirmar, cancelar, erro e `unregister` | T006, T008 | - | `caffmob_draw/selection/overlap_select.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T010 | Ligar o isolamento por `hide_set` (D-06): isolar esconde tudo menos o foco, alternar restaura o mapa guardado, trocar de foco com o isolamento ligado acompanha, e toda saída (confirmar, cancelar, erro, `cancel_active()`) devolve `hide_get()` ao estado da abertura | T008 | - | `caffmob_draw/selection/overlap_select.py` | 🟢 | `[X]` |
| T011 | Registrar o atalho no `keyconfigs.addon`: item `LEFTMOUSE` / `CLICK` com `ctrl=True`, `alt=True`, `head=True` no mapa `3D View`, guardado na lista do módulo e removido no `unregister`, junto das classes | T007 | - | `caffmob_draw/selection/overlap_select.py` | 🟢 | `[X]` |
| T012 | Acrescentar o item do seletor em `draw_context_menu` com `layout.operator_context = 'INVOKE_DEFAULT'` e o rótulo do catálogo, logo antes do separador de fecho; o operador recebe o ponto do cursor por `window.mouse_x/y` menos `region.x/y`, com o centro da região como reserva (D-08) | T007 | `[//]` | `caffmob_draw/ui/context_menu.py` | 🟡 | `[X]` |
| T013 | Registrar o módulo na extensão: `"selection.overlap_core"` antes de `"selection.overlap_select"` em `_submodule_names`, import explícito junto de `component_props/component_select/component_pick`, e entrada nas duas cascatas com `cancel_active()` antes do `unregister` (D-09, D-10) | T007 | `[//]` | `caffmob_draw/__init__.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T014 | Escrever `blender_016_overlap_smoke.py` no padrão das features anteriores: cena com três cubos alinhados, curva, texto, vazio, malha com Geometry Nodes, objeto oculto e objeto com `hide_select` desligado; abrir pelo operador, conferir só os três cubos, marcar por linha, `Ctrl+A`, `Ctrl+/`, isolar e restaurar, confirmar, cancelar e conferir que `hide_get()` voltou e que a pilha de desfazer não cresceu | T009, T010, T011, T012, T013 | - | `tests/blender_016_overlap_smoke.py` | 🟢 | `[X]` |
| T015 | Fechar a verificação: `py -3 -m py_compile` nos arquivos novos, `py -3 docs/rag/tools/check_api.py`, `cd tests && py -3 -m unittest test_overlap_core test_i18n_coverage test_identity` e a fumaça no Blender 5.2 com `EXIT=0`; completar o catálogo se o teste de i18n acusar texto novo e registrar em Notas de execução o tempo medido em T001 | T014 | - | `caffmob_draw/data/translations/sobreposicao.json` | 🟢 | `[X]` |

## Notas de execução

- T001 mediu 2.001 candidatos em 0,015 s de mediana (pior 0,019 s) na cena sintética de 2.000 malhas, muito abaixo
  do limite de 1 s: a poda de candidatos prevista no roadmap não entrou. Sonda em `probe_rays.py`.
- `tests/test_identity.py` lê os arquivos com `read_text()` sem `encoding`, e nesta máquina (Python 3.14, locale
  cp1252) ele quebra em `hb_placement.py` antes de chegar aos arquivos novos. Com `PYTHONUTF8=1` os 28 testes
  puros passam. Defeito pré-existente do teste, fora do escopo da 016.
- A fumaça roda em `--background` e cobre raio, marcação, isolamento, restauração, seleção, atalho e registro. O
  painel desenhado, o destaque e as teclas do modal precisam de janela e ficaram na conferência manual do
  `onboarding.md`.
- `bpy.types` no Blender 5.2 não expõe mais classe de operador por atributo: a fumaça usa `is_registered`.
- O ensaio com janela (`tests/blender_016_overlap_window.py`, eventos simulados) achou três defeitos, já corrigidos:
  o `Enter` substituía a seleção em vez de somar (RF-12), o painel andava junto com o mouse e as linhas nunca
  ficavam clicáveis, e o `poll` escondia o item do menu de contexto (a região do popup não é a da viewport).
- `Window.mouse_x` não existe no Blender 5.2: o ponto do cursor sai de `Event.mouse_x/mouse_y`, que servem ao
  atalho e ao menu.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-11-19 | T001 a T015 executadas por `/reversa-coding` | reversa |
