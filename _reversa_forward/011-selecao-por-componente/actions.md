# Actions: Seleção por componente e porta e janela na região selecionada

> Identificador: `011-selecao-por-componente`
> Data: `2026-10-09`
> Roadmap: `_reversa_forward/011-selecao-por-componente/roadmap.md` (D-01 a D-12)
> Data delta: `_reversa_forward/011-selecao-por-componente/data-delta.md`
> Interfaces: nenhuma
> Incrementos:
> - I1 seleção e exclusão: T001, T003, T004, T006, T008-T017, T021, T023
> - I2 região na parede: T002, T005, T007, T018-T020, T022, T024
> - T025 (traduções), T026 (regressão) e T027-T028 (guias) atravessam os dois
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 28 (T001–T028) |
| Paralelizáveis (`[//]`) | 21 |
| Maior cadeia de dependência | 7 (T004 → T006 → T009 → T010 → T021 → T023 → T026) |
| Ordem de entrega | I1 → I2; T011 (prova do arraste) logo depois do normalizador, porque decide se o T012 tem código |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `Scene.btm_component_select` (Bool, padrão `True`, salvo) e `WindowManager.btm_component_exempt` (String, sessão), com `register`/`unregister` (data-delta §1; D-04, D-08) | - | `[//]` | `caffmob_draw/selection/component_props.py` | 🟢 | `[X]` |
| T002 | `BTM_PG_WallRegion` (`active`, `wall`, `x0`, `x1`, `z0`, `z1` com `unit='LENGTH'`, `side` FRONT/BACK) em `WindowManager.btm_wall_region`, com `register`/`unregister` (data-delta §1; D-10) | - | `[//]` | `caffmob_draw/openings/region_props.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T003 | Testes da exclusão pura: `delete_plan(targets, keep_aggregates)` devolve a subárvore de baixo para cima, sem repetir; agregados ficam fora quando mantidos; itens grudados ficam fora; vãos de porta e janela listados à parte para tirar o booleano (D-05) | - | `[//]` | `tests/test_component_delete.py` | 🟢 | `[X]` |
| T004 | Testes da raiz (objetos simulados, como `test_classify.py`), pela precedência da nota D-01: | - | `[//]` | `tests/test_component_core.py` | 🟢 | `[X]` |
| | 1. agregado e item grudado são raiz deles mesmos; | | | | | |
| | 2. maçaneta, folha, FRAME, símbolo e texto 2D sobem ao vão; | | | | | |
| | 3. peça de armário sobe ao módulo só com o modo da biblioteca em `Cabinets`, e o módulo rápido sobe sempre; | | | | | |
| | 4. item da biblioteca sobe à raiz `is_item`; SketchUp aninhado sobe ao grupo mais alto; parede, piso, teto e malha solta não sobem; | | | | | |
| | 5. `collapse` não repete raízes e mantém a ordem. | | | | | |
| T005 | Testes da região (D-11): | - | `[//]` | `tests/test_wall_region_core.py` | 🟢 | `[X]` |
| | 1. porta de 820 × 2120 a partir do piso sai exata; | | | | | |
| | 2. porta com região acima do piso vai do piso a `z1`; | | | | | |
| | 3. janela com peitoril `z0`; | | | | | |
| | 4. cantos em ordem invertida dão o mesmo resultado; | | | | | |
| | 5. recusas: região mais larga que o trecho livre, sobreposta a outra abertura, mais alta que a parede, ou com largura ou altura zero, cada uma com o motivo. | | | | | |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T006 | `component_root(obj, modes)` e `collapse(objs, modes)` puros, reaproveitando `classify.classify`, `module_root` e `free_group`; `modes` é `{biblioteca: está_no_modo_gabinete}` (D-01, D-07) | T004 | `[//]` | `caffmob_draw/selection/component.py` | 🟢 | `[X]` |
| T007 | `fit(region, wall_length, wall_height, kind, gaps)` puro: posição x, largura, altura e peitoril exatos ou o motivo da recusa, sem grade nem folga (D-11) | T005 | `[//]` | `caffmob_draw/openings/region_core.py` | 🟢 | `[X]` |
| T008 | `delete_plan(targets, keep_aggregates)` puro no mesmo módulo da raiz (D-05) | T003, T006 | - | `caffmob_draw/selection/component.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Normalizador `depsgraph_update_post` `@persistent` (D-02): | T001, T006 | - | `caffmob_draw/selection/component_select.py` | 🟡 | `[X]` |
| | 1. sai cedo se o interruptor está desligado ou a assinatura (selecionados + ativo) não mudou; | | | | | |
| | 2. com a trava de reentrada, troca as peças pelas raízes com `select_set`, e a raiz da ativa vira ativa; | | | | | |
| | 3. respeita `btm_component_exempt` e limpa a isenção quando a seleção muda sem Alt; | | | | | |
| | 4. não age com modal do "Mover sobre" ou do editor de armário rodando; | | | | | |
| | 5. lê os modos de seleção das três bibliotecas; o `load_post` zera a assinatura; o `unregister` remove os dois handlers. | | | | | |
| T010 | Operador `btm.component_pick` (Alt + clique e Alt + Shift + clique, `CLICK`, `head=True`; poll exige o interruptor ligado): chama `view3d.select(location=…, extend=…)` e grava a peça em `btm_component_exempt`; keymap removido no `unregister` (D-04) | T001, T009 | `[//]` | `caffmob_draw/selection/component_pick.py` | 🟢 | `[X]` |
| T011 | Prova do arraste com eventos simulados (`--enable-event-simulate`, padrão da `blender_002_ui_events.py`). Clicar e arrastar um pé de uma cadeira de 5 malhas tem que mover as 5. Registrar o resultado nas Notas de execução (D-03) | T009, T021 | `[//]` | `tests/blender_011_drag_probe.py` | 🟡 | `[X]` |
| T012 | Plano B do D-03, **só se o T011 reprovar**: `btm.component_click` (`LEFTMOUSE` `PRESS`, `head=True`) chama `view3d.select` e promove na hora, devolvendo `PASS_THROUGH`. Se o T011 passar, marcar `[X]` com a nota "não necessário" | T011 | - | `caffmob_draw/selection/component_pick.py` | 🟡 | `[X]` |
| T013 | `caffmob.delete_with_aggregates`: o poll passa também quando algum selecionado tem descendentes; a execução usa `delete_plan`, mantém a pergunta dos agregados e a soltura dos grudados, e tira o booleano da parede dos vãos (D-05) | T008 | `[//]` | `caffmob_draw/aggregates/ops_aggregate.py` | 🟢 | `[X]` |
| T014 | `delete_door_window` apaga a subárvore inteira (`children_recursive`, de baixo para cima) pela mesma rotina do T013 (D-06) | T008 | `[//]` | `caffmob_draw/operators/doors_windows.py` | 🟢 | `[X]` |
| T015 | Importação OBJ/FBX/glTF com mais de uma malha: `group.create_group(meshes, 'PLAIN', <nome do arquivo>)`, seleciona o grupo e troca a mensagem do relatório; com uma malha, nada muda (D-09) | - | `[//]` | `caffmob_draw/aggregates/ops_import.py` | 🟢 | `[X]` |
| T016 | Interruptor "Seleção por componente" no bloco do topo da barra lateral, junto dos modos de seleção, com o estado escrito (D-08) | T001 | `[//]` | `caffmob_draw/ui/view3d_sidebar.py` | 🟡 | `[X]` |
| T017 | Interruptor no HUD da viewport, ao lado dos modos de seleção, quando o HUD está ligado (D-08) | T001 | `[//]` | `caffmob_draw/operators/viewport_hud.py` | 🟡 | `[X]` |
| T018 | Operador modal `btm.wall_region`, com o mesmo raycast e a mesma projeção no plano da parede do `draw_wall_cutter` (D-10): | T002, T007 | `[//]` | `caffmob_draw/openings/region.py` | 🟢 | `[X]` |
| | 1. dois cliques na parede, em cantos opostos; | | | | | |
| | 2. prévia `POST_VIEW` com as medidas; | | | | | |
| | 3. grava `btm_wall_region`; | | | | | |
| | 4. a região fica desenhada até ser usada ou cancelada com Esc; | | | | | |
| | 5. o desenho sai em todos os caminhos de saída, no `load_post` e no `unregister`. | | | | | |
| T019 | `_PlaceWallObjectBase` em estado "na região" (D-12): | T007, T014, T018 | - | `caffmob_draw/operators/doors_windows.py` | 🟡 | `[X]` |
| | 1. com região válida na parede, `execute` posiciona por `fit` (`Dim X`, `Dim Z`, x, z), sem `find_placement_gap` nem grade; | | | | | |
| | 2. Enter ou clique confirma (`cut_wall` + `_sync_opening`) e limpa a região; | | | | | |
| | 3. Esc cancela e mantém a região; | | | | | |
| | 4. região inválida mostra o motivo e cai no modo de hoje. | | | | | |
| T020 | Botão "Marcar região" em Construir › Aberturas, com o estado da região (marcada, medidas) e "Limpar região" | T018 | `[//]` | `caffmob_draw/ui/sidebar_build.py` | 🟢 | `[X]` |
| T021 | Registro de `selection.component_props`, `component_select` e `component_pick` na extensão | T001, T009, T010 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T022 | Registro de `region_props` e `region` no pacote `openings` | T002, T018 | `[//]` | `caffmob_draw/openings/__init__.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T023 | Fumaça da seleção e da exclusão (fundo): | T013, T014, T015, T021 | `[//]` | `tests/blender_011_component_smoke.py` | 🟢 | `[X]` |
| | 1. peça → raiz pelo normalizador; várias peças → raízes sem repetir; | | | | | |
| | 2. agregado continua dele; armário em `Cabinets` e em `Parts`; | | | | | |
| | 3. interruptor desligado, e salvar e reabrir mantém o estado; isenção do Alt + clique; | | | | | |
| | 4. OBJ de 5 malhas vira 1 grupo; | | | | | |
| | 5. excluir a porta real deixa zero objetos dela e a parede sem booleano; `delete_door_window` idem. | | | | | |
| T024 | Fumaça da região (fundo): porta exata de 820 × 2120 com furo igual, janela de 1200 × 1000 com peitoril de 1100, região que não cabe cai no modo de hoje, Esc mantém a região | T019, T022 | `[//]` | `tests/blender_011_region_smoke.py` | 🟢 | `[X]` |
| T025 | Traduções pt-BR/en-US do interruptor, do Alt + clique, da exclusão, da importação agrupada e da região, em `selection.json`, `openings.json`, `aggregates.json` e `sidebar.json`; `test_i18n_coverage` verde | T010, T013, T015, T016, T017, T019, T020 | - | `caffmob_draw/data/translations/selection.json` | 🟢 | `[X]` |
| T026 | Regressão: fumaças 002, 003, 004, 006, 007 e 010 verdes com o normalizador ligado; registrar no `regression-watch` o risco do undo da seleção (roadmap §9) | T023, T024, T025 | - | `tests/blender_011_component_smoke.py` | 🟡 | `[X]` |
| T027 | Guia novo: seleção por componente, interruptor, Alt + clique (e o aviso sobre "Emular mouse de 3 botões"), armários no modo gabinete, exclusão em profundidade, OBJ agrupado | T023 | `[//]` | `docs/usuario/selecao-por-componente.md` | 🟢 | `[X]` |
| T028 | Guia: "Marcar região" e a porta e a janela na medida exata da região | T024 | `[//]` | `docs/usuario/editor-paredes-e-mover-sobre.md` | 🟢 | `[X]` |

## Notas de execução

- **T011, 2026-10-09:** a prova com eventos simulados passou. O normalizador promove o pé ao grupo antes de o arraste
  começar, e a cadeira inteira se move (0,072 m nas 6 peças). Também passaram o clique simples, o Alt + clique, o
  clique sem Alt e a seleção por caixa. Arrastar move com a ferramenta Tweak; com a de fábrica (Select Box), arrastar
  faz seleção por caixa, que também sobe para o grupo.
- **T012:** não necessário, porque o T011 passou. Fechado sem código.
- **T026, 2026-10-09:** regressão verde. Em segundo plano: `blender_smoke`, 002, 003 (3), 004 (3), 005 (2), 006,
  007, 009 (2), 010 (3) e as duas fumaças da 011. Com janela: `blender_002_ui_events` e `blender_011_drag_probe` (7
  checagens). A `blender_007_window_smoke` foi ajustada: o OBJ entra num grupo e a esquadria se monta a partir dele.
- **Operadores novos com prefixo `caffmob.`** (e não `btm.`), porque o `tests/test_identity.py` exige. O teste
  continua acusando dois operadores `btm.*` anteriores a esta feature.
- **T010:** o `view3d.select` aninhado avalia o depsgraph na hora, e a peça subia para a raiz antes de ser lida. O
  normalizador fica suspenso (`component_select.suspended()`) enquanto o Alt + clique marca a peça.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-to-do` | reversa |
