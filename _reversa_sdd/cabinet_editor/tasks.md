# Editor de Armário (cabinet_editor) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/cabinet_editor/` a partir do código de 2026-10-10 (sem alterações sem commit na pasta). IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`. Ordem: núcleos puros → dados → sessão → ponte e cena → interface.

## Pré-requisitos

- [ ] 🟢 `canvas2d` conforme `_reversa_sdd/canvas2d/` (`window`, `view.View2D`, `draw`).
- [ ] 🟢 `walls2d.history.History` com assinatura injetável (`_reversa_sdd/walls2d/`, T-05).
- [ ] 🟢 `customize`: adaptadores com contrato obrigatório e opcional (`inner_spaces`, `structure_parts`, `structure_caps`, `remove_part`, `restore_part`, `set_part_thickness`, `reaffirm`, `structure_info`, `elevation_parts`, `opening_boxes`, `set_back_recess`), `spec`, `reapply`, `common`, `props.PULL_POSITION_ITEMS` (`_reversa_sdd/customize/`).
- [ ] 🟢 `selection.classify` (`classify`, `module_library`, `btm_kind`, `LIBRARY_LABELS`, `FRONT`) e `selection.editing` (`get_dimension`, `set_dimension`); `collision.obb`; `stick.apply.local_box`; `aggregates.group/leaf/convert`; `cutting.part_roles.classify`, `cutting.machining.AGGREGATE_PREFIX`.
- [ ] 🟢 `standards.api` (`get_value`, `get_value_m`, `find_definition`, `active_definition`), `standards.apply_core.is_own`, `standards.sync.get_overrides`, `data.dimension_schema.sheet_key`, `data.units`, `data.i18n`, `compat` (`try_get_gn_input`, `try_set_gn_input`), `hb_types.GeoNodeCutpart`, `product_libraries.frameless.types_frameless.CabinetPart`, `ui.save_feedback.show`, operador `caffmob.module_save`.
- [ ] 🟢 Sem banco, variáveis de ambiente ou configuração própria; miniaturas PNG em `cabinet_editor/thumbnails/<id em minúsculas>.png` (47).

## Tarefas

- [ ] T-01, Rascunho: `EditorState` (8 campos), `_rounded`, `signature` (`PRECISION = 6`), `Draft` (`checkpoint`, `undo`, `redo`, `dirty`, `apply_point`) (RN-03, RN-04, RN-05)
  - Origem no legado: `caffmob_draw/cabinet_editor/state.py`
  - Critério de pronto: `test_cabinet_editor_state` passa; checkpoint de largura +1e−8 devolve False; mutar o estado depois do checkpoint não altera o histórico
  - Confiança: 🟢

- [ ] T-02, Validação: `Message`, `DEFAULT_LIMITS`, `limits_for`, `parse_dimension`, `check_dimension`, `outside_volume`, `internal_overlaps`, `unsupported`, `blocking`, `sort_messages` (RN-07 a RN-09)
  - Origem no legado: `caffmob_draw/cabinet_editor/validate.py`
  - Critério de pronto: `test_cabinet_editor_validate` passa; CA-10 e CA-13 no nível puro
  - Confiança: 🟢

- [ ] T-03, Vista frontal: tipos, `kind_from_role`, `Part`, `draw_order`, `hit`, `bounds`, `diff` (RN-10, RN-22)
  - Origem no legado: `caffmob_draw/cabinet_editor/elevation.py`
  - Critério de pronto: `test_cabinet_editor_elevation` passa; `hit` escolhe a peça de menor Y e, empatando, a de menor área
  - Confiança: 🟢

- [ ] T-04, Componentes externos: `ROLES`, labels, modos, `THICKNESS_RANGE`, `ROLE_COMPONENT`, `RoleState`, `state_from_dict`/`state_to_dict`, `allowed_mode`, `check_thickness`, `unsupported_mode`, `layout` (F-09), `carcass_lengths`, `shrink_change` (RN-11, RN-32)
  - Origem no legado: `caffmob_draw/cabinet_editor/structure.py`
  - Critério de pronto: `test_cabinet_editor_structure` passa; `layout` com lateral removida em EXTEND faz o vão começar em `−L/2`; `BASE` põe a base na largura toda
  - Confiança: 🟢

- [ ] T-05, Subvãos: `Box`, `Division`, `new_uid`, `to_dict`/`from_dict`, `children`, `depth_of`, `_split`, `resolve` (F-07), `place`, `middle_offset`, `add`, `add_many`, `remove_in_space`, `update`, `remove`, `offset_range`, `validate`, `space_at`, `space_tokens` (RN-13 a RN-16)
  - Origem no legado: `caffmob_draw/cabinet_editor/divisions.py`
  - Critério de pronto: `test_cabinet_editor_divisions` passa; CA-17, CA-18, CA-19 no nível puro; distanciador não cria `.a`/`.b`
  - Confiança: 🟢

- [ ] T-06, Catálogo: `Item` (`thumb`, `param`, `too_small`), os 47 `ITEMS` com ids estáveis, `APPLIANCE_SIZE_MM`, `get`, `items`, `TREE`, `TREE_GROUPS`, `CHILDREN`, `DEFAULT_ON`
  - Origem no legado: `caffmob_draw/cabinet_editor/catalog.py`
  - Critério de pronto: `test_cabinet_catalog` passa; `len(ITEMS) == 47`; `TREE_GROUPS == {FEET, KICKS, VIEWS, VIEWS_TALL}`; cada id tem miniatura com o mesmo nome em minúsculas
  - Confiança: 🟢

- [ ] T-07, Geometria 008: `extras.layout` (F-10), `bays` (`plan`, `count`, `apply`, `removed`), `slides` (`missing_depth`, `layout` F-11), `appliances` (`missing`, `layout` F-12, `support_offset`), `position` (`cotas`, `offset_from_cota`, `step_move`) (RN-18 a RN-21, RN-26, RN-27)
  - Origem no legado: `caffmob_draw/cabinet_editor/extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py`
  - Critério de pronto: `test_cabinet_extras`, `test_cabinet_bays`, `test_cabinet_slides`, `test_cabinet_appliances`, `test_cabinet_position` passam; CA-21, CA-22, CA-24, CA-27, CA-28 no nível puro
  - Confiança: 🟢

- [ ] T-08, Dados salvos: `BTM_PG_Extra`, `BTM_PG_StructureExtra`, `BTM_PG_StructureItem`, `BTM_PG_Structure` (métodos de dicionário), `BTM_PG_Division` (`FIELDS`), registro dos ponteiros `Object.btm_structure`/`btm_division`/`btm_extra` e remoção simétrica
  - Origem no legado: `caffmob_draw/cabinet_editor/data_props.py`
  - Critério de pronto: `to_dict` → `from_dict` devolve o mesmo dicionário; `unregister` remove os três ponteiros; `.blend` salvo mantém os dados
  - Confiança: 🟢

- [ ] T-09, Sessão e campos: `Session` (campos e métodos; `redraw` marca a área do editor e as `VIEW_3D`), `start`/`end`, `BTM_PG_CabinetEditorState` com campos virtuais (`_dim_*`, `_space_*`, `_tree_*`, `_value_*`, `_comp_*`, `_bays_*`, `_pos_*`), `_add_virtual_fields` antes do registro, enums das abas com números estáveis, `WindowManager.btm_cabinet_editor` (RN-01, RN-19)
  - Origem no legado: `caffmob_draw/cabinet_editor/props.py`
  - Critério de pronto: todo `set` virtual só acrescenta à fila (sem tocar a cena); `tab` sem item 2; `unregister` encerra a sessão e remove o ponteiro
  - Confiança: 🟢

- [ ] T-10, Peças próprias: `scene_divisions` (linha, `configured`, leitura, `apply`, `_create`, `_borrow_material`, `_place`, `_signature`, `reflow` F-13) e `scene_parts` (`extras_of`, `delete`, `_link`, `_tag`, `place`, `make_part`, `make_box`, `make_cylinder`, `carcass_box`) (RN-15, RN-31)
  - Origem no legado: `caffmob_draw/cabinet_editor/scene_divisions.py`, `scene_parts.py`
  - Critério de pronto: divisão vertical criada com −90° em Y e `Mirror Z`; segundo `reflow` sem mudança não regrava a assinatura; sem divisões a assinatura some
  - Confiança: 🟢

- [ ] T-11, Extras, internos e deslizantes na cena: `scene_extras.sync`, `scene_interiors` (`entries`, `apply`, `_build`, `_cutout`, `reflow`), `scene_slides` (`frame_of`, `state_of`, `clear`, `missing_depth`, `apply` F-14, `reflow`) (RN-21, RN-26, RN-27)
  - Origem no legado: `caffmob_draw/cabinet_editor/scene_extras.py`, `scene_interiors.py`, `scene_slides.py`
  - Critério de pronto: CA-24 e CA-28 no Blender; painel embutido com recorte `CPM_CUTOUT` cujo nome começa com `AGGREGATE_PREFIX`; reinserir deslizantes não deixa grupos órfãos
  - Confiança: 🟢

- [ ] T-12, Ponte — leitura e vista: `CUSTOM_FIELDS`, `_raw`, `read_state`, `library_limits`, `set_dimension`, `parts` (F-04), `_kind`, `root_box`, `view_shift`, `root_size`, `opening_of` (RN-03, RN-08)
  - Origem no legado: `caffmob_draw/cabinet_editor/bridge.py:1-80,214-296`
  - Critério de pronto: `read_state` → `apply_state` sem mudança deixa a assinatura igual; gaiolas em arame não aparecem e vãos aparecem como OPENING
  - Confiança: 🟢

- [ ] T-13, Ponte — `apply_state` (F-05) e `reflow_all`
  - Origem no legado: `caffmob_draw/cabinet_editor/bridge.py:apply_state/_slides_key/reflow_all`
  - Critério de pronto: CA-03 e CA-07; ordem: medidas → frentes/interior → crus → `reapply` → estrutura → fundo → divisões → extras → internos → deslizantes
  - Confiança: 🟢

- [ ] T-14, Ponte — ações da 003 em `edit` (FRONT com atalho de mesma frente, STYLE, PULL, MATERIAL, INTERIOR) (RF-15)
  - Origem no legado: `caffmob_draw/cabinet_editor/bridge.py:edit`
  - Critério de pronto: CA-25 (mesma frente não refaz); `PULL` com "todas as frentes" grava a posição em todos os vãos
  - Confiança: 🟢

- [ ] T-15, Ponte — estrutura e montagem: `structure_rows`, `configured_part`, `is_caffmob_module`, `origin_definition`, `is_own_standard`, `set_assembly`, `_item`, `_tidy`, `remove_part`, `restore_part`, `edit_part`, `_apply_structure` (F-08) (RN-11, RN-12, RN-32)
  - Origem no legado: `caffmob_draw/cabinet_editor/bridge.py:299-435`
  - Critério de pronto: CA-15, CA-16, CA-32; registro em `btm_structure` gravado antes da chamada ao adaptador
  - Confiança: 🟢

- [ ] T-16, Ponte — divisões e 008: `division_context`, `_raw_entry`, `add_division`, `edit_division`, `remove_division`, `toggle_extra`, `set_bays`, `set_back`, `add_many`, `remove_in_space`, `library_opening`, `DOOR_FRONTS`, `_front_steps`, `insert_doors`, `insert_drawers`, `insert_interior`, `remove_interior`, `insert_slides`, `remove_slides`, `EDIT_006`, `EDIT_008` (RN-15 a RN-18, RN-21, RN-23 a RN-28)
  - Origem no legado: `caffmob_draw/cabinet_editor/bridge.py:438-674`
  - Critério de pronto: CA-17 a CA-21, CA-25 a CA-29 no Blender; 23 ações despachadas por `edit`
  - Confiança: 🟢

- [ ] T-17, Handlers fora do editor: `_roots`, `_reflow` com trava, `on_depsgraph_update`/`on_frame_change` `@persistent`, registro sem duplicar e remoção (RN-31)
  - Origem no legado: `caffmob_draw/cabinet_editor/reflow_handler.py`
  - Critério de pronto: CA-31; com sessão aberta os handlers não fazem nada; `unregister` remove os dois
  - Confiança: 🟢

- [ ] T-18, Janela e desenho: wrappers de `canvas2d.window`, `ensure_view` (margem 0,18), cores, `_dashed_rect`, `_draw_006`, `_hinge`, `_swing_lines`, `_library_outline`, `status_text`, `_status_bar`, `draw_editor` (F-16), `_labels`, handler `POST_PIXEL` e remoção; `previews.icon_id` sob demanda e `unregister` (RF-04)
  - Origem no legado: `caffmob_draw/cabinet_editor/window.py`, `previews.py`
  - Critério de pronto: CA-11, CA-12 (barra "Selecionado"); peça removida desenhada tracejada com "removido"; sem miniatura usa ícone `MESH_PLANE`
  - Confiança: 🟢

- [ ] T-19, Sessão no editor: `_sync_ui`, `_sync_006`, `space_label`, `_divisions_refresh`, `_library_refresh`, `refresh`, `process`, `_apply_now`, `_selected_division`, `_arrow` (F-15), `_boards`, `rollback`, `start_session` (F-03)
  - Origem no legado: `caffmob_draw/cabinet_editor/ops_editor.py:34-297`
  - Critério de pronto: CA-04, CA-09, CA-10, CA-14, CA-22, CA-23; pedido com `ValueError` mostra o erro e não grava passo
  - Confiança: 🟢

- [ ] T-20, Operadores de ciclo: `caffmob.cabinet_editor` (F-01), `caffmob.cabinet_editor_modal` (F-02, atalhos), `_confirm`, `_cancel`, `_close` (RN-02, RN-06, RN-07, RN-29, RN-30)
  - Origem no legado: `caffmob_draw/cabinet_editor/ops_editor.py:300-550`
  - Critério de pronto: CA-01, CA-02, CA-05, CA-06, CA-07, CA-08; timer removido em todos os caminhos de saída
  - Confiança: 🟢

- [ ] T-21, Botões que enfileiram: enums dinâmicos (`_front_items`, `_style_items`, `_pull_items`, `_ENUM_CACHE`), `selected_path`, `_edit`/`_history`/`_save_module`, `_SessionOperator`, divisão (`add`, `edit`, `remove`), componente (`remove`, `restore`, `edit`), `insert_reason`, `_division_payload`, `insert_payload`, `insert`, `apply`, `pick`, `remove_item` (RN-23)
  - Origem no legado: `caffmob_draw/cabinet_editor/ops_actions.py`
  - Critério de pronto: CA-20, CA-26, CA-27, CA-30; nenhum desses operadores tem `UNDO` nem toca a cena (exceto `save_module`, que seleciona a raiz)
  - Confiança: 🟢

- [ ] T-22, Painéis: `_EditorPanel`, `_TabPanel`, `cabinet_type`, `target_box`, `catalog_grid`, `properties_box`, `insert_button`, `draw_materials`, `draw_library_interior`, cabeçalho, Definições, Mensagens, Ajustes, Confirmar; abas Estrutura (montagem, componentes, árvore, Posição, Movimentação, Materiais), Divisões (nova, lista, interior), Gavetas, Internos, Portas, Deslizantes, Fundos; `registrar`
  - Origem no legado: `caffmob_draw/cabinet_editor/panels.py`, `panels_structure.py`, `panels_divisions.py`, `panels_drawers.py`, `panels_interior.py`, `panels_doors.py`, `panels_sliding.py`, `panels_backs.py`, `panels_tabs_common.py`
  - Critério de pronto: 17 painéis registram e somem com `unregister`; Inserir apagado mostra o motivo; Posição só habilitada com divisória selecionada
  - Confiança: 🟢

- [ ] T-23, Pacote: `_modules` com import tardio na ordem de `design.md`; `register`/`unregister` (inversa)
  - Origem no legado: `caffmob_draw/cabinet_editor/__init__.py`
  - Critério de pronto: importar `caffmob_draw.cabinet_editor.state` sem `bpy` funciona; o add-on registra e desregistra sem erro
  - Confiança: 🟢

- [ ] T-24, Decidir as lacunas antes de reimplementar fielmente: montagem e fundo fora da fila (EC-03), erro da seta apagado (EC-01), recuo de trás do catálogo (EC-06), bays sobre divisão comum (EC-07), deslizantes só no primeiro vão (EC-08)
  - Origem no legado: `panels_structure.py:draw_assembly`, `panels_backs.py`, `ops_editor.py:process/_arrow`, `ops_actions.py:_division_payload`, `bays.py:apply`, `scene_slides.py:apply`
  - Critério de pronto: decisão registrada pelo titular (manter como está ou corrigir) para cada item
  - Confiança: 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-42, #pergunta-85, #pergunta-46, #pergunta-44, #pergunta-45):** corrigir todos: EC-03 (DT-01, só a montagem), EC-01 (DT-08), EC-06 (DT-05), EC-07 (DT-03), EC-08 (DT-04)

## Testes

- [ ] TT-01, Testes puros dos núcleos: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_cabinet_appliances test_cabinet_bays test_cabinet_catalog test_cabinet_editor_divisions test_cabinet_editor_elevation test_cabinet_editor_state test_cabinet_editor_structure test_cabinet_editor_validate test_cabinet_extras test_cabinet_position test_cabinet_slides` dentro de `tests/`
  - Origem no legado: `tests/test_cabinet_*.py`
  - Critério de pronto: 70 testes aprovados (resultado de 2026-10-10)
  - Confiança: 🟢

- [ ] TT-02, Fumaça no Blender do editor e das abas: `xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_004_cabinet_editor_smoke.py` (idem `blender_006_cabinet_editor_tabs_smoke.py`, `blender_008_construtor_smoke.py`; esses três precisam de janela e em `--background` saem com 0 sem testar nada) e `blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_cabinet_standard_smoke.py` _(Revisão 2026-10-10: comando corrigido pelas docstrings dos testes; em `--background` os três primeiros só imprimem "Blender quit")_
  - Origem no legado: `tests/blender_004_cabinet_editor_smoke.py`, `tests/blender_006_cabinet_editor_tabs_smoke.py`, `tests/blender_008_construtor_smoke.py`, `tests/blender_012_cabinet_standard_smoke.py`
  - Critério de pronto: os quatro saem com código 0
  - Confiança: 🟢 _(Revisão 2026-10-10: os quatro executados no Blender 5.2.0, código 0; 39 + 162 + 70 OK e blender_012 OK)_

- [ ] TT-03, Teste puro novo para EC-07: `bays.apply` sobre uma lista com divisão comum em `s0` e `divisions.validate` devolvendo `DIV-003`
  - Origem no legado: `caffmob_draw/cabinet_editor/bays.py`, `divisions.py`
  - Critério de pronto: o teste documenta o comportamento atual (ou o corrigido, conforme T-24; decidido: recusar, DT-03)
  - Confiança: 🟢

- [ ] TT-04, Teste de interface para EC-01 e EC-02: seta sem seleção deixa `s.error` vazio; OK com pedido pendente descarta o pedido
  - Origem no legado: `caffmob_draw/cabinet_editor/ops_editor.py`
  - Critério de pronto: os dois comportamentos reproduzidos num smoke `blender_*` (decididos para mudar: DT-08 e DT-02; o smoke passa a provar a mensagem visível e o pedido executado no OK)
  - Confiança: 🟡

## Ordem e Paralelismo

🟡 T-01 a T-07 são independentes entre si (exceto T-05 antes de T-07, que usa `divisions`) e podem andar em paralelo. T-08 e T-09 antes de T-10 a T-17. T-12 a T-16 dependem de T-10 e T-11. T-18 a T-22 dependem de T-09 e T-12. T-23 fecha. T-24 deve ser decidido antes de T-16, T-19 e T-22 se a reimplementação for corrigir os casos.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Fazer o painel da Montagem enfileirar `SET_ASSEMBLY` (em vez de escrever direto em `btm_cabinet.assembly`) e incluir `assembly` no `EditorState`, para Ctrl+Z, Cancelar e Aplicar a tratarem (decisão questions.md#pergunta-42)
- [ ] DT-02 Em `BTM_OT_CabinetEditorModal.modal`, rodar `process` antes de tratar `request == 'ok'` e descartar a fila no `'cancel'` (decisão questions.md#pergunta-43)
- [ ] DT-03 Em `bays.apply`, recusar com mensagem clara a mudança do Número de vãos quando `s0` já está cortado por divisória que não é `bay` (decisão questions.md#pergunta-44)
- [ ] DT-04 Em `scene_slides.apply`, usar o vão da biblioteca do subvão escolhido (como Portas e Gavetas) ou recusar em armário com bays (decisão questions.md#pergunta-45)
- [ ] DT-05 Em `ops_actions._division_payload`, aplicar pelo item `back = 15 mm` com `use_back = True` nas divisórias "Interna s/ Recuo — Tras 15mm" e "c/ Recuo — Tras 15mm" (decisão questions.md#pergunta-46)
- [ ] DT-06 Em `appliances.layout`, empilhar na ordem de `codes` (não `reversed(codes)`), deixando o forno embaixo no painel Forno/Micro (decisão questions.md#pergunta-47)
- [ ] DT-07 Esconder na aba Portas as regiões Inferior, Superior e Alta (sem efeito), ou documentá-las como só rótulo (decisão questions.md#pergunta-84)
- [ ] DT-08 Em `process`, limpar `s.error` só antes de executar o pedido, preservando o erro definido pela ação (ex. "Selecione uma divisória na vista para mover com as setas") (decisão questions.md#pergunta-85)
- [ ] DT-09 Em `bridge.apply_state`, recriar internos, extras e deslizantes só quando a parte correspondente do instantâneo difere (decisão questions.md#pergunta-86)
