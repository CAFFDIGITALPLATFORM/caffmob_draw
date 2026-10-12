# Personalizar Módulo e Biblioteca do Usuário (customize) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/customize/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `selection/classify` (`module_root`, `module_library`; contrato em `_reversa_sdd/selection/`).
- [ ] 🟢 `compat` com `try_get_gn_input`, `try_set_gn_input`, `gn_input_data_path`, `try_get_gn_input_by_id`.
- [ ] 🟢 `cutting/part_roles` (`classify`, `base_name`); `data/i18n` (`tr`, `N_`) e `data/translations/customize.json`; `data/units` (`get_scene_length_unit`, `format_length`, `parse_length`).
- [ ] 🟢 `library_common` (`world_box`, `thumbnail`); `hb_placement.PlacementMixin`; `hb_snap`; `hb_project`, `hb_types`, `hb_utils`.
- [ ] 🟢 As três bibliotecas de produto com os operadores e funções citados em `design.md` (Dependências) e o gancho `after_rebuild` nos 5 pontos de reconstrução; `data/properties.update_cabinet_geom` chamando o gancho.
- [ ] 🟢 `geometry/door_controller` (`doors_of`, `set_door_pull`, `set_door_material`) e `geometry/mesh_gen` (`MAT_*`).
- [ ] 🟢 `cabinet_editor` (`btm_structure`, `scene_divisions` com `read`/`objects`/`reflow`, `scene_extras.sync`, `scene_interiors.reflow`, `scene_slides.reflow`, `divisions.Box`/`new_uid`, `structure.layout`/`shrink_change`/`ROLES`/`ROLE_LABELS`) — features 006/008.
- [ ] 🟢 `Object.btm_aggregate` registrado (unit `aggregates`).

## Tarefas

- [ ] T-01, Criar `spec.py` puro: domínios, limites, `Interior`, `Opening`, `Spec` (`opening`, `ensure_opening`, `is_empty`), `to_dict`, `from_dict`, `validate`, `validate_interior`, `shelf_positions`, `group_of_component`, `interior_to_json`, `interior_from_json` (RN-01, RN-10, RN-13)
  - Origem no legado: `caffmob_draw/customize/spec.py`
  - Critério de pronto: CA-26; os 8 testes de `tests/test_customize_spec.py` passam; `shelf_positions(3, 0.72, 0.018)` = 0,1665/0,351/0,5355; sem `bpy`; EC-09 reproduzido ou corrigido conforme decisão
  - Confiança: 🟢

- [ ] T-02, Criar `manifest.py` puro: constantes, `file_stem`, `build` (ordem das chaves, mm com 3 casas, opcionais 1.1.0 só se não vazios), `structure_of`, `divisions_of`, `validate`/`_validate_structure`, `dumps`, `loads` (RN-14, RN-17)
  - Origem no legado: `caffmob_draw/customize/manifest.py`
  - Critério de pronto: CA-27; os 8 testes de `tests/test_module_manifest.py` passam; 1.0.0 continua válido; EC-13 reproduzido
  - Confiança: 🟢

- [ ] T-03, Criar `props.py`: `PULL_POSITION_ITEMS`, `GROUP_ITEMS`, `BTM_PG_GroupMaterial`, `BTM_PG_CustomSpec` (10 campos + `group_material`/`set_group_material`) e `Object.btm_custom` (RN-04)
  - Origem no legado: `caffmob_draw/customize/props.py`
  - Critério de pronto: nomes, padrões e descrições da tabela de `design.md`; sem `update`; `unregister` remove o ponteiro antes das classes; valores sobrevivem a salvar/reabrir
  - Confiança: 🟢

- [ ] T-04, Criar `adapters/__init__.py` (`module_root`, `for_root`, `for_object`, import tardio) e `adapters/common.py` parte de materiais e utilidades: `ordered`, `material`, `rotated`, `gn_modifier`, `set_cutpart_material`, `part_group`, `is_cutpart`, `apply_group_materials`, `read_materials`, `interior_of`, `unique`, `run_operator` (F-09; RN-02, RN-03, RN-05, RN-13)
  - Origem no legado: `caffmob_draw/customize/adapters/__init__.py`, `adapters/common.py`
  - Critério de pronto: CA-10, CA-11; ordem estável com chave `(round(x,4), −round(z,4), nome)`; `Rail Material` recebe a variante `" ROTATED"` quando existe; aviso de material ausente sem repetição
  - Confiança: 🟢

- [ ] T-05, Criar em `common.py` o contrato opcional (006/008): `call` + `default_*`, `keep_only_caps`, `local_box`, `clip_space`, `cage_spaces`, `removed_roles`, `set_removed`, `is_removed`, `cutpart_thickness`, `set_cutpart_thickness`, `reaffirm_parts`, `parts_by_name`, `default_structure_info`, `default_elevation_parts`, `default_opening_boxes`, `set_back_recess` (F-10, F-13; RN-20, RN-21)
  - Origem no legado: `caffmob_draw/customize/adapters/common.py`
  - Critério de pronto: CA-25; driver composto `(expr) or btm_rm` criado e desfeito sem apagar o driver da biblioteca; `clip_space` só corta chapas que cruzam o vão; `delta_location` na direção −Y da raiz
  - Confiança: 🟢

- [ ] T-06, Criar `adapters/frameless.py`: `capabilities`, `front_types`, `openings` (`_bays`, `_stable_openings`), `leaf_opening`, `fronts`, `pulls`, `front_type`, `read`, `set_front`, `set_interior` (`_remove_tree`, `_attach`), `style_names`, `pull_items`, `_pull_object`, `_apply_style`, `_set_pull_position`, `_apply_pull`, `reapply`, `describe` e a parte de estrutura (F-02, F-04, F-07; RN-07, RN-09, RN-11)
  - Origem no legado: `caffmob_draw/customize/adapters/frameless.py`
  - Critério de pronto: CA-03, CA-04, CA-06, CA-07, CA-12, CA-13; fumaça 003 passo 1; `BOTTOM.EXTEND` só com `Remove Bottom`; espessura 0 recria o driver `Material Thickness`; EC-04, EC-05, EC-18 documentados
  - Confiança: 🟢

- [ ] T-07, Criar `adapters/face_frame.py`: vãos folha, `front_type`, `read`, `set_front` (`split_opening`), `set_interior` (`interior_items`, uma divisória), estilos e puxadores por pasta, `reapply` (só reestiliza se o nome mudou), estrutura por `hb_part_role` (F-03, F-05, F-08)
  - Origem no legado: `caffmob_draw/customize/adapters/face_frame.py`
  - Critério de pronto: fumaça 003 passo 3 (frente, estilo, puxador e material sobrevivem ao recálculo); EC-19 reproduzido
  - Confiança: 🟢

- [ ] T-08, Criar `adapters/closets.py`: vãos por `TAG_OPENING_CAGE`, `front_type` por idprops, `set_front` (`apply_opening_config`, `clear_opening_contents`), `set_interior` só prateleiras, estilos de `FRONT_STYLES`, puxadores com cache invalidado, `reapply`, estrutura (primeiro/último painel) (F-08)
  - Origem no legado: `caffmob_draw/customize/adapters/closets.py`
  - Critério de pronto: fumaça 003 passo 4 (`DOUBLE_DOORS` ok, `FLIP_UP` recusado, estilo `WIDE_SHAKER` volta após recálculo)
  - Confiança: 🟢

- [ ] T-09, Criar `adapters/btm.py`: vão `"module"`, `capabilities` com `STYLES`, `SWING_TO_FRONT`/`FRONT_TO_SWING`, `read`, `set_front` por `door_swing`, `set_interior` por `shelves`, `pull_items` do frameless, `_carcass_materials`, `reapply` (portas), estrutura por `btm_cabinet` com `_shrink` (F-11, F-12; RN-08, RN-20)
  - Origem no legado: `caffmob_draw/customize/adapters/btm.py`
  - Critério de pronto: fumaça 003 passo 5 (prateleiras, material do slot 0, puxador em todas as portas); EC-07 documentado (🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-83):** botão de peça escondido/desabilitado com motivo; DT-03)
  - Confiança: 🟢

- [ ] T-10, Criar `reapply.py`: `_running`, `DIVISION_SIGNATURE`, `has_structure`, `has_custom`, `reapply`, `after_rebuild` (F-06; RN-12)
  - Origem no legado: `caffmob_draw/customize/reapply.py`
  - Critério de pronto: CA-15, CA-16; chamada aninhada é ignorada; os 5 pontos das bibliotecas e `update_cabinet_geom` chamam o gancho
  - Confiança: 🟢

- [ ] T-11, Criar `library_io.py`: `modules_root`, `paths_for`, `exists`, `list_modules`, `_tree`, `_data_blocks`, `_addon_version`, `build_manifest`, `_divisions`, `_renew_divisions`, `save`, `_geo_node_refs`, `_missing_styles`, `load`, `delete`, `rename` (F-14, F-15; RN-14, RN-15, RN-18)
  - Origem no legado: `caffmob_draw/customize/library_io.py`
  - Critério de pronto: CA-17, CA-19, CA-20, CA-22, CA-23; gravação atômica sem temporários após erro; decidir e cobrir EC-01 (definir `missing = []` antes do uso) e EC-02 (estilos do closets) antes de considerar pronto
  - Confiança: 🟢

- [ ] T-12, Criar `ops_customize.py`: `_ENUM_CACHE`, `_target`, `_opening`, `_report`, enums dinâmicos, mixin `_OpeningOperator` e os 6 operadores `caffmob.customize_*` (F-01; RF-02 a RF-07; RN-19)
  - Origem no legado: `caffmob_draw/customize/ops_customize.py`
  - Critério de pronto: CA-05, CA-08, CA-13, CA-14; todos com `{'REGISTER', 'UNDO'}`; alturas na unidade da cena; EC-20 e EC-21 documentados
  - Confiança: 🟢

- [ ] T-13, Criar `ops_library.py`: `_entry`, `_redraw` e os 5 operadores `caffmob.module_*`, com o modal de inserção sobre `PlacementMixin` (F-16; RF-09 a RF-11; RN-16)
  - Origem no legado: `caffmob_draw/customize/ops_library.py`
  - Critério de pronto: CA-18, CA-21, CA-24; fumaça 003 passos 2 e 6; Esc/botão direito não deixa objetos; `module_insert` com `place=False` não entra no modal
  - Confiança: 🟢

- [ ] T-14, Criar `panels.py` (`_section`, `_opening_label`, `draw_customize`, `draw_library`, `BTM_PT_CustomizeModule`, `BTM_PT_ModuleLibrary`, `classes = ()`) e ligá-los em `ui/object_properties.py` (grupo `sel_customize`) e `ui/my_modules.py` (RF-01, RF-11)
  - Origem no legado: `caffmob_draw/customize/panels.py`; `caffmob_draw/ui/object_properties.py:337-341`; `caffmob_draw/ui/my_modules.py:23-24`
  - Critério de pronto: CA-01, CA-02; seções sem suporte desabilitadas com o motivo; EC-06 resolvido (passar `kind`) ou documentado
  - Confiança: 🟢

- [ ] T-15, Criar `customize/__init__.py` com `_modules()` tardio e registro na ordem `props, ops_customize, ops_library, panels` (inversa no `unregister`); incluir `customize` em `caffmob_draw/__init__.py` (`_submodule_names`, `register`, `unregister`)
  - Origem no legado: `caffmob_draw/customize/__init__.py`; `caffmob_draw/__init__.py:10,35,298,368`
  - Critério de pronto: `import caffmob_draw.customize.spec` sem `bpy` funciona; registrar/desregistrar duas vezes sem erro
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Testes puros de `spec` (8): ida e volta, vão sem interior sem chave, válido, inválidos, vão repetido, alturas do interior, posições iguais, grupos e JSON do interior — `tests/test_customize_spec.py` 🟢
- [ ] TT-02, Testes puros do manifesto (8): montar e ler, formato e biblioteca, versão maior recusada, JSON inválido, nome de arquivo, 1.0.0 válido, estrutura/divisões ida e volta, erros de estrutura — `tests/test_module_manifest.py` 🟢
- [ ] TT-03, Fumaça Blender `tests/blender_003_customize_smoke.py` (6 passos: frameless, salvar, face frame, closets, `btm`, inserir em arquivo novo) — não executada nesta extração 🟢 _(Revisão 2026-10-10: executada no Blender 5.2.0 LTS → OK)_
- [ ] TT-04, Acrescentar testes para EC-01 (inserir `.blend` sem `.json`), EC-02 (closets com estilo), EC-09 (`interior_from_json` com tipo errado) e EC-13 (`schema_version` 0.x) 🟡

## Tarefas de Migração de Dados

- [ ] 🟢 Nenhuma migração automática: o leitor aceita manifestos 1.0.0 e 1.1.0 (major ≤ 1) sem conversão; `structure`/`divisions` ausentes = vazios.
- [ ] 🟢 Módulos `.blend` sem manifesto (grupos antigos) dependem da correção de EC-01 para serem inseridos. _(Revisão 2026-10-10: confirmado no Blender 5.2 (EC-01))_

## Ordem Sugerida

1. T-01, T-02 (puros, com TT-01 e TT-02).
2. T-03, T-04, T-05.
3. T-06 a T-09 (um adaptador por vez, cada um com o passo correspondente da fumaça).
4. T-10 e os ganchos nas bibliotecas.
5. T-11, T-12, T-13, T-14, T-15; TT-03 por último.

## Lacunas Pendentes (🔴)

- EC-01: `UnboundLocalError` ao inserir `.blend` sem `.json` (também em "Substituir").
- EC-02: estilos do closets tratados como ausentes na inserção.
- EC-05: posição `SIDE` sem efeito. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-40):** tirar do menu. Pendência de implementação: DT-01.
- EC-06: estilo de gaveta inacessível pelo painel.
- TT-03: fumaça 003 não executada (Blender ausente). _(Revisão 2026-10-10: executada → OK; item resolvido)_

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Tirar `SIDE` ("Lateral") de `PULL_POSITION_ITEMS`, mantendo o valor em `PULL_POSITIONS` para manifestos antigos (decisão questions.md#pergunta-40)
- [ ] DT-02 Em `frameless.set_front` (troca para 2 a 4 gavetas), copiar o `btm_custom` do vão antigo para cada vão novo, exceto o interior (decisão questions.md#pergunta-41)
- [ ] DT-03 Esconder ou desabilitar o botão "Peça …" de `BTM_OT_CustomizeSetMaterial` quando a biblioteca é BTM ou a peça não tem `GeoNodeCutpart`, mostrando o motivo em texto (decisão questions.md#pergunta-83)
