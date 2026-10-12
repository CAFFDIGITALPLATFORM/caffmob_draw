# Inspeção de frentes (inspection) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/inspection/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr` e `N_`; catálogo `data/translations/inspection.json`.
- [ ] 🟢 `compat.try_get_gn_input(mod, nome, padrão)` e `hb_types.GeoNodeObject` (`has_modifier`, `has_input`, `get_input`).
- [ ] 🟢 Linhas legadas com as funções listadas em `design.md` › Dependências (face frame `op_open_mode`, `solver_face_frame.front_leaves`; closets `types_closets.*`).
- [ ] 🟢 `aggregates/leaf.py` (`pivot_of`, `current_fraction`, `apply_fraction`, `swing_angle`) e `btm_aggregate.open_value` com update `update_open` (`_reversa_sdd/aggregates/`).
- [ ] 🟢 `cutting/stale.py` com `skip_next_update()` e consulta a `ops_inspect.inspection_running()` (`_reversa_sdd/cutting/`).
- [ ] 🟢 `operators/viewport_hud.py` com `register_active_modal`, `unregister_active_modal`, `click_hits_widget`.
- [ ] 🟢 `Scene.btm_settings.save_fronts_open: BoolProperty(default=False)` (`data/properties.py`).
- [ ] 🟢 Sem banco de dados, rede ou variáveis de ambiente.

## Tarefas

- [ ] T-01, Criar `pivot_math.py` puro com constantes, limites, `snap_angle`, conversões, álgebra de tuplas, Rodrigues, `matrix_to_euler_xyz`, `swing_sign`, `edge_rotation`, `slide`, `frame_from_extents`, `side/top/bottom_hinge`, `pose_for` (RN-01, RN-09, RN-14)
  - Origem no legado: `caffmob_draw/inspection/pivot_math.py`
  - Critério de pronto: os 10 testes de `tests/test_inspection_math.py` passam (encaixe 43→45, 52→52, 120→90; porta esquerda mantém a dobradiça; basculante sobe até a aresta de cima; Euler ida e volta; gaveta desliza pela face)
  - Confiança: 🟢

- [ ] T-02, Criar `room_door_math.py` puro: `Leaf`, `leaves`, `leaf_corners`, `open_tip` (RN-18)
  - Origem no legado: `caffmob_draw/inspection/room_door_math.py`
  - Critério de pronto: os 5 testes de `tests/test_room_door_math.py` passam; CA-18
  - Confiança: 🟢

- [ ] T-03, Criar `fronts.py`: constantes de tipo, `Front` (RN-01 a RN-03, `is_valid`, `can_sweep`, `objects`), `_adapters` com import tardio na ordem fixa, `iter_fronts`, `fronts_of`, `front_for_object`, `module_root_of` (RN-17)
  - Origem no legado: `caffmob_draw/inspection/fronts.py`
  - Critério de pronto: CA-01 e CA-02; `is_open` respeita 0,5° / 0,005
  - Confiança: 🟢

- [ ] T-04, Adaptador frameless: `_kind`, `_openable` (RN-16), `_local_frame`, `_travel` (0,0254 / 0,05 / 0,4), `FramelessFront` com `_prepare` preguiçoso, pose em `delta_*`, `btm_open` apagado ao fechar, `hinge_frame` com `swing_sign`, `travel`, `objects`
  - Origem no legado: `caffmob_draw/inspection/adapters/frameless.py`
  - Critério de pronto: porta esquerda, direita, basculante e gaveta abrem sem objetos novos nem mudança nos drivers de medida; frente falsa e folha oculta ficam de fora
  - Confiança: 🟢

- [ ] T-05, Adaptador face frame: `FaceFrameFront` por vão, conversão ÷100°, `apply` com contexto de tween e 1 nova tentativa, `commit` com `stale.skip_next_update()` antes de gravar `swing_percent`, `hinge_frame`/`travel` por `front_leaves` 0 e 1, clique só via frente/pivô
  - Origem no legado: `caffmob_draw/inspection/adapters/face_frame.py`
  - Critério de pronto: abrir 90° deixa `swing_percent = 0,9`; clicar numa prateleira do vão não abre (CA-02); plano de corte continua atual
  - Confiança: 🟢

- [ ] T-06, Adaptador closets: `ClosetFront` (porta ÷110°, gaveta em fração), `hinge_frame` pelas marcas `hb_door_*`/`hb_hinge`/`hb_slide_*`, caixa de gaveta irmã em `objects` e no clique
  - Origem no legado: `caffmob_draw/inspection/adapters/closets.py`
  - Critério de pronto: abrir 90° grava `hb_door_open = 90/110`; clique na caixa abre a frente de mesmo índice
  - Confiança: 🟢

- [ ] T-07, Adaptador do módulo rápido: `BtmFront` por módulo (`_Controller.location.y` 0–0,2 m ↔ 0–90°), `btm_open` no `commit`, eixos fixos por sufixo
  - Origem no legado: `caffmob_draw/inspection/adapters/btm.py`
  - Critério de pronto: abrir 90° deixa o controlador em y = 0,2; `door_swing='NONE'` não gera frente
  - Confiança: 🟢

- [ ] T-08, `room_door_leaf.py` (F-08) e adaptador `RoomDoorFront` (RN-15): folha só na primeira abertura, `can_sweep` = tem pivô, porta real da 010 exclui
  - Origem no legado: `caffmob_draw/inspection/room_door_leaf.py`; `caffmob_draw/inspection/adapters/room_doors.py`
  - Critério de pronto: CA-16, CA-17; mudar de simples para dupla recria os pivôs; `remove_leaves` apaga pivôs, folhas, malhas órfãs e `btm_open`
  - Confiança: 🟢

- [ ] T-09, Adaptador de folhas convertidas: `AggregateLeafFront` com `max_angle` próprio, `apply = leaf.apply_fraction`, `commit` via `open_value`, clique pelo pivô (`btm_leaf`), `hinge_frame` em `btm_leaf_base`; implementa `travel()` (EC-01; DT-01, questions.md#pergunta-61)
  - Origem no legado: `caffmob_draw/inspection/adapters/aggregate_leaf.py`
  - Critério de pronto: folha de giro abre e para na batida via `commit`; seta do gizmo numa folha de correr não gera erro (hoje gera — EC-01)
  - Confiança: 🟢 (comportamento) / 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-61):** implementar `travel()` em `AggregateLeafFront` com o curso de correr da folha (`aggregates/leaf.py`) e um `travel()` na base `Front` devolvendo 0, com a seta oculta quando 0 (contrato uniforme entre adaptadores). Pendência de implementação: DT-01

- [ ] T-10, `props.py`: `BTM_PG_Interference`, `BTM_PG_InspectionState` e `WindowManager.btm_inspection` com `unregister` simétrico
  - Origem no legado: `caffmob_draw/inspection/props.py`
  - Critério de pronto: padrões `active=False`, `snap_stops=True`, `default_angle='90'`, `checked_fronts=-1`; registrar/desregistrar duas vezes sem erro
  - Confiança: 🟢

- [ ] T-11, `ops_inspect.py`: `scope_fronts` (F-01) e `caffmob.fronts_set_open` (F-02) sem `UNDO`
  - Origem no legado: `caffmob_draw/inspection/ops_inspect.py:scope_fronts/BTM_OT_FrontsSetOpen`
  - Critério de pronto: CA-03, CA-04; mensagens idênticas
  - Confiança: 🟢

- [ ] T-12, Modo `caffmob.inspect_fronts` (F-03): singleton `_active`, `inspection_running`, timer 60 Hz, tweens smoothstep 0,35 s, raycast, `_click_on_widget`, `_finish` que conclui alvos e limpa timers/HUD/status, `unregister` que zera `_active`
  - Origem no legado: `caffmob_draw/inspection/ops_inspect.py:BTM_OT_InspectFronts`
  - Critério de pronto: CA-05, CA-06, CA-07; segundo clique no botão encerra a sessão em execução
  - Confiança: 🟢

- [ ] T-13, Gizmo `BTM_GGT_front_open` (F-04): cache por ponteiro, dial/seta com cores e escalas do `design.md`, encaixe opcional, `_commit_pending` por `bpy.app.timers`, `unregister` que remove o timer e zera `_state`
  - Origem no legado: `caffmob_draw/inspection/gizmo.py`
  - Critério de pronto: CA-08, CA-09; soltar o dial grava uma única vez
  - Confiança: 🟢

- [ ] T-14, `save_guard.py` (F-05): `close_for_save`, `reopen_after_save`, handlers `@persistent` em `save_pre`, `save_post` e `save_post_fail`, registro sem duplicar
  - Origem no legado: `caffmob_draw/inspection/save_guard.py`
  - Critério de pronto: CA-10, CA-11; após `unregister`, nenhum dos 3 handlers permanece
  - Confiança: 🟢

- [ ] T-15, `interference.py` (F-06): amostras 15°, `_world_corners`, `_shrink` radial 1 mm, `_hull_bmesh`, `_Targets` com BVH sob demanda, `check_fronts`, `store_results`
  - Origem no legado: `caffmob_draw/inspection/interference.py`
  - Critério de pronto: CA-12, CA-13; todas as frentes leem o valor anterior depois da checagem
  - Confiança: 🟢

- [ ] T-16, `ops_interference.py` (`caffmob.check_front_interference`, `caffmob.interference_goto`; F-07) e `overlay.py` (2 draw handlers com remoção no `unregister`)
  - Origem no legado: `caffmob_draw/inspection/ops_interference.py`; `caffmob_draw/inspection/overlay.py`
  - Critério de pronto: CA-14, CA-15; cruz vermelha e rótulo aparecem só com interferências registradas
  - Confiança: 🟢

- [ ] T-17, `__init__.py`: `_modules` com import tardio e ordem `props, ops_inspect, ops_interference, gizmo, overlay, save_guard`; `unregister` inverso
  - Origem no legado: `caffmob_draw/inspection/__init__.py`
  - Critério de pronto: após `unregister`, `WindowManager` sem `btm_inspection` e `GizmoGroup.bl_rna_get_subclass_py('BTM_GGT_front_open')` é `None` (fumaça, linhas 141-142)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Testes puros: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_inspection_math test_room_door_math -v` → 15 testes (10 + 5) (executado em 2026-10-10: OK) 🟢
- [ ] TT-02, Fumaça no Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_inspection_smoke.py` (descoberta nas 4 linhas, abrir 45/90 com conversões, plano de corte não desatualiza, interferência com obstáculo e restauração da pose, salvar fechado e tela aberta, desregistro limpo) 🟢 _(Revisão 2026-10-10: executado no Blender 5.2.0 LTS — `BLENDER_INSPECTION_SMOKE_OK`, código 0)_
- [ ] TT-03, Teste do modal com eventos simulados: clique, clique durante a animação, Esc no meio da animação, segunda invocação (CA-05 a CA-07) 🔴 (não existe)
- [ ] TT-04, Teste do gizmo numa folha de correr convertida (EC-01) e numa folha de giro com `max_angle` > 90 (EC-02) 🟡 (não existe; cobre DT-01 e DT-02, questions.md#pergunta-61 e #pergunta-62)
- [ ] TT-05, Teste de salvar com frente frameless no meio da animação e com `pending` do gizmo (EC-07) 🟡 (não existe; cobre DT-03, questions.md#pergunta-63)

## Tarefas de Migração de Dados

- [ ] TM-01, `hb_door_open`/`hb_drawer_open` do closets aceitam os 0/1 inteiros de arquivos antigos e a fração gravada pela inspeção (`types_closets.open_fraction`, M-05 da 001); não há outra migração 🟢

## Ordem Sugerida

1. T-01 e T-02 (puros): fecham TT-01 sem Blender.
2. T-03, depois T-04 a T-09 (adaptadores independentes entre si; T-08 antes do adaptador de ambiente).
3. T-10 antes de T-11 a T-16 (todos leem `btm_inspection`).
4. T-11 → T-12 → T-13; T-14; T-15 → T-16.
5. T-17 por último; depois TT-02 a TT-05.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-61):** implementar `travel()` em `AggregateLeafFront` com o curso de correr da folha (`aggregates/leaf.py`) e um `travel()` na base `Front` devolvendo 0, com a seta oculta quando 0 (contrato uniforme entre adaptadores) (EC-01). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-62):** "Abrir 90°" (e o clique) ficam em 90°; o dial passa a ser limitado por `front.max_value` em vez do teto fixo de 90, coerente com a varredura e com o `max_angle` da 003 (EC-02). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-92):** o `unregister` encerra a sessão chamando `_active._finish(bpy.context)` dentro de `try`, como pede a regra do repositório de remover todo handler em todos os caminhos de saída (EC-04). Pendência de implementação: DT-04.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-63):** em `save_pre`, concluir os tweens do `_active` e o `pending` do gizmo (commit do alvo) antes de `close_for_save` (EC-07; DT-03). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-63):** aceito o comportamento atual para cenas compartilhadas (o objeto é salvo fechado, o lado seguro) (EC-06).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-93):** limpar a lista (ou marcar "desatualizado" no painel) num `depsgraph_update_post` quando um objeto MESH/CURVE muda transformação, reaproveitando o padrão de `collision/`; sem nova verificação automática (EC-11). Pendência de implementação: DT-05.
- 🟡 decisão: testar (DT-06) — **Decisão do titular (2026-10-10, questions.md#pergunta-94):** aceito que a criação de pivô e folha fique fora do desfazer (RN-14 da 001); validar no Blender que o undo não deixa pivô sem folha e, se deixar, tornar `ensure_leaves` idempotente na próxima abertura (EC-16).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Implementar `travel()` em `AggregateLeafFront` com o curso de correr da folha (`aggregates/leaf.py`) e `travel()` na base `Front` devolvendo 0; o gizmo oculta a seta quando `travel()` é 0 (decisão questions.md#pergunta-61)
- [ ] DT-02 No gizmo (`gizmo.py:_snap` / `pivot_math.snap_angle`), limitar o dial por `front.max_value` em vez do teto fixo de 90; "Abrir 90°" e o clique continuam em 90° (decisão questions.md#pergunta-62)
- [ ] DT-03 Em `save_pre`, concluir os tweens da sessão `_active` e o `pending` do gizmo (commit do alvo) antes de `close_for_save` (decisão questions.md#pergunta-63)
- [ ] DT-04 Em `ops_inspect.unregister`, chamar `_active._finish(bpy.context)` dentro de `try` antes de zerar `_active` (timers, modal handler e registro no HUD) (decisão questions.md#pergunta-92)
- [ ] DT-05 Registrar `depsgraph_update_post` (`@persistent`, removido no `unregister`) que limpa os resultados de interferência ou os marca "desatualizado" quando um objeto MESH/CURVE muda transformação, no padrão de `collision/` (decisão questions.md#pergunta-93)
- [ ] DT-06 Validar no Blender que o Ctrl+Z depois da primeira abertura de uma porta de ambiente não deixa pivô sem folha; se deixar, tornar `ensure_leaves` idempotente na próxima abertura (decisão questions.md#pergunta-94)
