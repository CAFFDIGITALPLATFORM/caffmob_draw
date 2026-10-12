# Editor de Paredes 2D (walls2d) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/walls2d/` a partir do código de 2026-10-10 (inclui a feature 013 sem commit em `ops_editor.py`, `props.py` e `compat.py`). IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 Unit `canvas2d` implementada conforme `_reversa_sdd/canvas2d/` (`View2D`, `ortho_snap`, `snap_to_grid`, distâncias, `gestures`, `draw`, `window`).
- [ ] 🟢 `compat.trackpad_delta(event)` e `compat.pinch_delta(event)` (`caffmob_draw/compat.py`, 013).
- [ ] 🟢 `hb_types.GeoNodeWall/GeoNodeCage/GeoNodeObject`, `operators/walls.py` (esquadrias, cadeias, piso/teto), `operators/ops_wall_extras.py` (`remove_wall`, `KEEP_WITH_WALL`), `openings/sync.py`, `selection/classify.btm_kind`, `measure/scene_cotas.ceiling_height`.
- [ ] 🟢 `data/units.py` (`parse_length`, `format_length`, `format_value`, `get_scene_length_unit`), `data/expr.py` (`preview`, `MAX_LENGTH`), `data/i18n.py` (`tr`, `N_`) e o catálogo `data/translations/walls2d.json` (inclui a chave da lupa, 013).
- [ ] 🟢 Sem banco, variáveis de ambiente ou configuração própria.

## Tarefas

- [ ] T-01, Modelo base: constantes (`INNER/OUTER`, `SIDES`, `WALL_TYPES`, `TYPE_DEFAULTS`, `LIMITS`, `LABELS`), `validate`, `Segment`, `Chain` (topologia, ângulos, `miter_angles`, `is_ccw`, `outward_side`) (RN-01, RN-02, RN-04)
  - Origem no legado: `caffmob_draw/walls2d/model.py:1-127`
  - Critério de pronto: CA-02; `Chain(..., side='UP')` levanta `ValueError`; `rectangle(4,3).is_ccw()` é True e `outward_side()` é `'RIGHT'`
  - Confiança: 🟢

- [ ] T-02, Faces e deslocamentos: `inner_line`, `outer_line` (F-01), `line`, `face_length`, `shifted_nodes` (F-02), `hb_order` (RN-01, RN-19)
  - Origem no legado: `caffmob_draw/walls2d/model.py:130-182`
  - Critério de pronto: CA-01; `hb_order` de cadeia `RIGHT` devolve nós invertidos sem alterar a original
  - Confiança: 🟢

- [ ] T-03, Edição: `set_length` (F-03), `set_angle_abs`, `set_angle_rel`, `_move_end`, `move_node` (RN-06), `set_segment_value` (RN-03), `split` (RN-07), `remove_node` (RN-08), `invert` (F-04), `touches_start`, `close_if_touching` (RN-10), `close`
  - Origem no legado: `caffmob_draw/walls2d/model.py:185-308`
  - Critério de pronto: CA-03, CA-04; `set_length(OUTER)` converge em ≤ 12 passos com erro < 1e−7; `invert` duas vezes devolve nós, trechos e `side` originais
  - Confiança: 🟢

- [ ] T-04, `WallPlan` (`bounds` com padrão `((-1,-1),(4,3))`, `remove_chain_segment_sources`), `plan_signature` (RN-11) e `rectangle`
  - Origem no legado: `caffmob_draw/walls2d/model.py:311-351`
  - Critério de pronto: assinatura muda com nó movido 1e−5 m (arredondamento a 6 casas) e não muda com seleção, vista ou `references`
  - Confiança: 🟢

- [ ] T-05, `History` com `LIMIT = 100`, assinatura injetável, `checkpoint`/`undo`/`redo` com cópias profundas
  - Origem no legado: `caffmob_draw/walls2d/history.py`
  - Critério de pronto: CA-15 no nível puro; `checkpoint` sem mudança devolve False; 101 passos mantêm só 100 no desfazer; `cabinet_editor/state.py` continua funcionando com sua assinatura
  - Confiança: 🟢

- [ ] T-06, `inference.Index` (listas ordenadas + `bisect`, `query` com tolerância inclusiva e exclusão) e `plan_points`; `direction.py` (`ORTHO_TOLERANCE_DEG`, `ARROWS`, `initial_direction`, `next_point`, `segment_direction`, `arrow_direction`, `label`) (RN-13, RN-14)
  - Origem no legado: `caffmob_draw/walls2d/inference.py`, `caffmob_draw/walls2d/direction.py`
  - Critério de pronto: `test_wall_inference` e `test_wall_direction` passam; `label(0) == "→ 0°"`; `initial_direction(p, p) is None`
  - Confiança: 🟢

- [ ] T-07, `heights.py` (`TOLERANCE = 0.001`, `LOW_WALL_TYPES`, `follows_project_height`, `walls_to_equalize`) e `convert.py` (`JOIN_TOLERANCE = 0.01`, `chains_from_segments`, F-05) (RN-18, RN-22)
  - Origem no legado: `caffmob_draw/walls2d/heights.py`, `caffmob_draw/walls2d/convert.py`
  - Critério de pronto: `test_walls2d_heights` e `test_walls2d_convert` passam; trechos fora de ordem formam uma única cadeia fechada com `side` para fora; `geometry/floor_outline.py` continua obtendo contornos
  - Confiança: 🟢

- [ ] T-08, `scene_io.py`: `walls_in`, `reference_segments`, `read_plan`/`_chain_from` (F-06), `is_other_layer_wall`, `convert_into` (F-07) (RN-17, RN-18)
  - Origem no legado: `caffmob_draw/walls2d/scene_io.py`
  - Critério de pronto: sala de 4 paredes HB encadeadas vira 1 cadeia fechada `LEFT` com `source` = nomes; paredes soltas viram cadeias de 1 trecho; objeto sem `btm_wall_segments` volta na lista de ignorados e continua nas referências
  - Confiança: 🟢

- [ ] T-09, `apply.py`: avisos (`items_that_do_not_fit`, `modules_of_removed`, `height_mismatches`), `apply_plan` (F-12), `_rehost_opening`, `_swap_mesh`, `refresh_floors_and_ceilings` (F-13), `sync_project_height` (F-14) (RN-19 a RN-23, RN-29)
  - Origem no legado: `caffmob_draw/walls2d/apply.py`
  - Critério de pronto: CA-18 e CA-24 no Blender; inverter a Direção de uma parede com porta mantém a porta no mesmo vão, dentro da espessura, abrindo para o mesmo lado (BUG-20261007-YIMY); relatório tem as 7 chaves
  - Confiança: 🟢

- [ ] T-10, `props.py`: `Session` (campos do Estado Interno em `design.md`, incluindo `zoom_window`/`zoom_box_end` da 013), `dirty`, `segment`, `checkpoint`, `undo`/`redo`/`_restore`, `redraw`; singleton `session`/`start`/`end`
  - Origem no legado: `caffmob_draw/walls2d/props.py:17-118`
  - Critério de pronto: `undo` limpa lápis, digitação, perguntas e direção e descarta seleção inválida; a lupa não entra na assinatura
  - Confiança: 🟢

- [ ] T-11, Campos virtuais e `BTM_PG_WallEditorState` (tabela em `design.md`): `_guard`, `_seg_get/_seg_set`, `_text_get/_text_set` (unidade do projeto, `allow_zero=False`), enums `line`/`direction`/`wall_type`, `equalize_height`, `remove_modules`; `register` em `WindowManager.btm_wall_editor`, `unregister` com `end()` (RN-28)
  - Origem no legado: `caffmob_draw/walls2d/props.py:121-352`
  - Critério de pronto: CA-13, CA-14, CA-25; trocar `direction` de cadeia com `source` mostra o aviso "Direção trocada em paredes existentes…"
  - Confiança: 🟢

- [ ] T-12, `window.py` (embrulhos com `EDITOR_CATEGORY`, mensagem de janela, handler `POST_PIXEL` único) e `panels.py` (4 painéis, `poll` por área do editor) (RF-13)
  - Origem no legado: `caffmob_draw/walls2d/window.py`, `caffmob_draw/walls2d/panels.py`
  - Critério de pronto: painéis só aparecem na área do editor, na aba "Editor de Paredes"; listas de avisos truncam em 8 com "… e mais {}"; `unregister` remove o handler
  - Confiança: 🟢

- [ ] T-13, Operador de abertura `caffmob.wall_editor` (poll, diálogo `other_walls`, F-08) e `caffmob.wall_editor_fit`
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:BTM_OT_WallEditor/BTM_OT_WallEditorFit`
  - Critério de pronto: CA-05, CA-06; segunda abertura com sessão ativa é bloqueada pelo `poll`
  - Confiança: 🟢

- [ ] T-14, Esqueleto do modal `caffmob.wall_editor_modal`: `invoke` (timer 0,1 s), `modal` na ordem de F-09, `_local`, `_end`, `cancel`, `_handle_undo` (RN-26), checkpoint pós-ação
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:BTM_OT_WallEditorModal.invoke/_end/cancel/_local/modal/_handle_undo`
  - Critério de pronto: CA-16; eventos sobre o painel N chegam aos campos; OK/Cancelar do painel fecham em ≤ 0,1 s mais 0,05 s
  - Confiança: 🟢

- [ ] T-15, Mira: `_index`, `resolve_point` (F-10), `hit_node`, `close_snap`, `hit_line`, `_update_snap`, constantes de alvo (RN-13)
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:_index/resolve_point/hit_node/close_snap/hit_line/_update_snap`
  - Critério de pronto: com origem e cursor a 1° do eixo X perto de um vértice alinhado em X, o ponto fica com Y da origem e X do vértice (`'align'`); com Shift, só `'ortho'`
  - Confiança: 🟢

- [ ] T-16, Seleção, arraste, digitação e ferramentas: `_handle_click` (F-19), `_handle_typing` (F-18), `accept_typing`, `remove_segment` (RN-16), arraste com ímã, Esc fora do lápis (RN-12)
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:_handle/_handle_click/_handle_typing/accept_typing/remove_segment`
  - Critério de pronto: CA-07, CA-08, CA-12, CA-19 (via Esc)
  - Confiança: 🟢

- [ ] T-17, Lápis e perguntas: `_handle_draw` (F-16), `_append`, `_finish_drawing`, `_answer_no`, `_handle_prompt` (F-17), `PROMPTS`, `_prompt_rects`
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:_handle_draw/_append/_finish_drawing/_answer_no/_handle_prompt`
  - Critério de pronto: CA-09, CA-10, CA-11; "Não" em `close` com Enter mantém o trecho digitado
  - Confiança: 🟢

- [ ] T-18 _(pendente de commit da 013; questions.md#pergunta-70, DT-07)_, Navegação 013: roda com `invert_zoom_wheel`, pinça, `TRACKPADPAN`, botão do meio, Home; `_is_navigation` pulando `_update_snap` (RN-24)
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:_handle/_is_navigation/_invert_zoom_wheel`; `caffmob_draw/compat.py:trackpad_delta/pinch_delta`
  - Critério de pronto: CA-20, CA-21; navegar não altera `snap_point` nem grava passo
  - Confiança: 🟢

- [ ] T-19 _(pendente de commit da 013; questions.md#pergunta-70, DT-07)_, Barra superior e lupa: `toolbar_height`, `_ui_scale`, `_region_rect` (área útil sem barra e painel N), `_toolbar_rects`, `handle_zoom_window` (F-15), `_draw_toolbar`, `_draw_magnifier` (RN-25)
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:60-281`
  - Critério de pronto: CA-22, CA-23; Home e Enquadrar não escondem paredes atrás da barra; clique na barra fora da lupa não seleciona nada
  - Confiança: 🟢

- [ ] T-20, Desenho da planta `draw_plan` na ordem de F-11, com `_draw_crosshair`, `_draw_direction`, `_draw_arrow`, `_draw_prompt`, `COLORS` e dicas por ferramenta
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:draw_plan` e auxiliares
  - Critério de pronto: face interna tracejada e externa contínua; seleção em laranja com seta; mira com eixo travado em laranja; validação visual no Blender
  - Confiança: 🟢

- [ ] T-21, OK e Cancelar: `caffmob.wall_editor_ok` (duas fases, mensagens dos avisos) e `caffmob.wall_editor_cancel` (`invoke_confirm` quando sujo) (RN-12)
  - Origem no legado: `caffmob_draw/walls2d/ops_editor.py:BTM_OT_WallEditorOk/BTM_OT_WallEditorCancel`
  - Critério de pronto: CA-17, CA-19
  - Confiança: 🟢

- [ ] T-22, Registro do pacote: `__init__.py` com imports tardios e ordem props → window → ops_editor → panels (inversa no `unregister`); ligação em `caffmob_draw/__init__.py` e `hb_props.py` (`sync_project_height`)
  - Origem no legado: `caffmob_draw/walls2d/__init__.py`; `caffmob_draw/__init__.py:294/372`; `caffmob_draw/hb_props.py:83-84` (import na 83, chamada `sync_project_height` na 84) _(Revisão cruzada 2026-10-10)_
  - Critério de pronto: `import caffmob_draw.walls2d.model` funciona sem `bpy`; registrar/desregistrar duas vezes não deixa handler nem propriedade órfã
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Modelo: faces, esquadria, limites, edição, inversão, fechamento (CA-01 a CA-04) — `tests/test_walls2d_model.py` 🟢
- [ ] TT-02, Histórico (CA-15) — `tests/test_walls2d_history.py` 🟢
- [ ] TT-03, Mira e direção — `tests/test_wall_inference.py`, `tests/test_wall_direction.py` 🟢
- [ ] TT-04, Pé-direito e conversão — `tests/test_walls2d_heights.py`, `tests/test_walls2d_convert.py` 🟢
- [ ] TT-05, Ciclo abrir → editar → OK no Blender (CA-05, CA-17, CA-18) — `tests/blender_002_smoke.py` 🟢 (existência; não executado nesta extração)
- [ ] TT-06, Eventos da planta (CA-07 a CA-12, CA-19) — `tests/blender_002_ui_events.py`, `tests/blender_009_walls_smoke.py` 🟢 (existência)
- [ ] TT-07, Navegação e lupa (CA-20 a CA-23) — `tests/blender_013_touchpad_smoke.py`; prova de eventos `tests/blender_013_trackpad_probe.py` 🟢 (existência)
- [ ] TT-08, Casos extremos EC-01, EC-03, EC-05, EC-06 — 🟡 sem teste identificado; decidir a intenção antes (ver Lacunas)
- [ ] TT-09, Remover vértice com "Bloquear Ângulo" e campos de ângulo (EC-07) — 🟢 sem teste identificado _(Revisão 2026-10-10: tests/test_walls2d_model.py:89-94 só cobre move_node com lock_angle)_

Comando dos testes puros 🟢: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_wall_direction test_wall_inference test_walls2d_convert test_walls2d_heights test_walls2d_history test_walls2d_model` (36 testes). Fumaça no Blender 🟢 (CLAUDE.md): `blender --background --factory-startup --python-exit-code 1 --python tests/<arquivo>.py`.

## Tarefas de Migração de Dados

- [ ] TM-01, 🟢 Nenhuma migração própria: o rascunho não é persistido. Atenção ao legado: `btm_wall_orientation` antigo é ignorado na leitura (`scene_io.py:_chain_from`, M-11) e `btm_wall_type` é gravado em toda parede aplicada.

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03 → T-04: o modelo puro, base de tudo.
2. 🟢 T-05, T-06, T-07 em paralelo (dependem só do modelo).
3. 🟢 T-08 e T-09 (ponte com a cena); T-09 depende de `hb_order` (T-02) e `heights` (T-07).
4. 🟢 T-10 → T-11 → T-12 (estado e UI lateral).
5. 🟢 T-13 → T-14 → T-15 → T-16/T-17 → T-18/T-19 → T-20 → T-21 → T-22: o modal depende da sessão, a mira do índice (T-06), a lupa de `canvas2d.gestures`.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-1):** `remove_node` registra o `source` descartado em `removed_sources` (EC-01). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-8):** o "Não" da pergunta de fechamento por arraste sobrevive ao OK (EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-9):** soltar sobre a barra conclui o arraste/retângulo; a barra consome só `PRESS` (EC-05). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-10):** `confirm_pending` é recalculado quando o rascunho muda depois do 1º aviso (EC-06). Pendência de implementação: DT-04.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `model.remove_node` (ou em `_handle_click`), acrescentar o `source` do trecho eliminado a `plan.removed_sources`, igual a `remove_segment` (decisão questions.md#pergunta-1)
- [ ] DT-02 Fazer o "Não" da pergunta `close` marcar a cadeia para pular `close_if_touching` em `apply_plan` (decisão questions.md#pergunta-8)
- [ ] DT-03 Em `handle_zoom_window`, consumir na barra só `LEFTMOUSE PRESS` e deixar o `RELEASE` seguir quando há arraste de vértice ou retângulo da lupa em curso (decisão questions.md#pergunta-9)
- [ ] DT-04 Guardar a assinatura do rascunho no 1º aviso do OK e zerar `confirm_pending` (recalcular avisos) se ela mudou (decisão questions.md#pergunta-10)
- [ ] DT-05 Desabilitar `angle_abs`/`angle_rel` em `BTM_PT_wall_editor_segment` quando o trecho tem `lock_angle` (decisão questions.md#pergunta-11)
- [ ] DT-06 Validar o sinal da pinça com `tests/blender_013_trackpad_probe.py` em cada plataforma-alvo e registrar em `investigation.md` §6 da 013 (decisão questions.md#pergunta-72)
- [ ] DT-07 Commitar a feature 013 (alterações em `ops_editor.py`, `props.py`, `compat.py`, `walls2d.json` e testes 013) antes de congelar as specs (decisão questions.md#pergunta-70)
