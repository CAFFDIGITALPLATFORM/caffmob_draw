# Padrão de Dimensões (standards) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar a unit a partir do código de 2026-10-10 (`caffmob_draw/standards/`, `data/dimension_schema.py`, `operators/ops_standards.py`, `ui/standards_tree.py`; sem alterações sem commit nesses arquivos). IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`. Ordem: esquema puro → núcleos puros → arquivos → dados RNA → serviço → sincronização → migração → interface.

## Pré-requisitos

- [ ] 🟢 `data/units.py` (`get_scene_length_unit`, `format_length`, `parse_length`) e `data/i18n.py` (`tr`, `N_`) — ver `_reversa_sdd/data/`.
- [ ] 🟢 `hb_project.get_main_scene` / `ensure_main_scene`.
- [ ] 🟢 `selection/classify.py` (`btm_kind`, `module_library`, `module_root`, `free_group`, `MODULE_TAGS`) — ver `_reversa_sdd/selection/`.
- [ ] 🟢 `legacy/gate.py` (`legacy_ui`, `legacy_roots`) e preferência `show_legacy_libraries`.
- [ ] 🟢 `cabinet_editor/structure.py:ROLE_COMPONENT` e `cabinet_editor/bridge.py:is_own_standard/origin_definition` — ver `_reversa_sdd/cabinet_editor/`.
- [ ] 🟢 `data/properties.py`: `Object.btm_cabinet` (campos de F-12), `suspended_geometry`, `update_cabinet_geom`, `Scene.btm_settings.cut_plan_stale`, `dimension_settings`, `config_*`.
- [ ] 🟢 Bibliotecas herdadas: `frameless/operators/ops_defaults.py` (3 funções `(context, skip)`), `closets/types_closets.recalculate_closet_starter`, `Scene.hb_frameless`, `Scene.hb_closets`.
- [ ] 🟢 34 imagens `caffmob_draw/assets/dimension_refs/<image_key>.png`; fixture `tests/fixtures/dimensionexport_me_moveis.xml` (692 atributos).
- [ ] 🟢 Sem banco de dados nem variáveis de ambiente; pasta do usuário via `bpy.utils.extension_path_user(…, path="standards", create=True)`.

## Tarefas

- [ ] T-01, Esquema: constantes (`INCH_MM`, `MARKETS`, `LINES`, `LINE_CODES`, grupos, árvores, `_THICKNESS`), `Component` e os 20 `COMPONENTS` na ordem, `PROMOB_EDGE_TO_SIDE`/`SIDE_TO_PROMOB_EDGE`, `MATERIALS`, `Param` (com `default(market)`) (RN-02, RN-03)
  - Origem no legado: `caffmob_draw/data/dimension_schema.py` (até `Param`)
  - Critério de pronto: módulo importa sem `bpy`; tabela de componentes idêntica à de `design.md`
  - Confiança: 🟢

- [ ] T-02, Esquema: `_MAX_FIELDS`, `_EXTERNAL_FIELDS`, `_EXTERNAL_OVERRIDES`, `_LEGACY_TARGETS` (17), `_PROMOB_EXTERNAL`, campos/rótulos de chapa, `sheet_key`/`external_key`/`max_key` e `_build` (F-01) com `round(us, 4)`
  - Origem no legado: `caffmob_draw/data/dimension_schema.py:_build`
  - Critério de pronto: CA-01 (870 / 20 / 1042 / 17); `test_dimension_schema` (14 testes) passa, inclusive "toda imagem de referência existe"
  - Confiança: 🟢

- [ ] T-03, Esquema: `get_param`, `params_for`, `label`, `line_label`, `validate` (F-02) com `_fmt`, `PROMOB_INDEX` (`setdefault`), `parse_promob_id`, `canonical_component` (RN-04)
  - Origem no legado: `caffmob_draw/data/dimension_schema.py:get_param..canonical_component`
  - Critério de pronto: CA-02; mensagens exatamente com o prefixo "Valor Inválido:"; NaN aceito como hoje (EC-04) ou divergência registrada se for corrigido (🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-49):** corrigir; DT-02)
  - Confiança: 🟢

- [ ] T-04, Núcleo de aplicação: `CAFFMOB/LEGACY/OTHER`, `ModuleInfo`, `Plan`, `is_own`, `plan`, `targets` (RN-13)
  - Origem no legado: `caffmob_draw/standards/apply_core.py`
  - Critério de pronto: `test_standards_apply_core` (3 testes) passa; uid vazio segue, uid diferente difere
  - Confiança: 🟢

- [ ] T-05, Medidas de armário: `Defaults`, `LINES`, `FALLBACK`, `FALLBACK_SHEET = 0.018`, `FALLBACK_BACK = 0.006`, `EXTERNAL`, `_fallback`, `defaults` (F-09) (RN-18)
  - Origem no legado: `caffmob_draw/standards/cabinet_defaults.py`
  - Critério de pronto: `test_cabinet_defaults` (3 testes) passa; CA-10 e CA-11; tipo desconhecido → BASE; avisos traduzidos com `tr`
  - Confiança: 🟢

- [ ] T-06, Promob: `PromobFormatError`, `PromobDocument`, `read_dimensionexport`, `ASSEMBLY_ID`/`ASSEMBLY_VALUES`, `_parse_number`, `to_definition_data` (F-15) (RN-21)
  - Origem no legado: `caffmob_draw/standards/io_promob.py:read_dimensionexport/to_definition_data`
  - Critério de pronto: `test_promob_io.ReadTest` e `ErrorsTest`; fixture → 692 total, 335 mapeados, 357 não reconhecidos, 294 chaves; ID duplicado vale o último (EC-09)
  - Confiança: 🟢

- [ ] T-07, Promob: `_format_number`, `build_attributes`, `write_dimensionexport` (F-16, escrita atômica), `attributes_from_values` (RN-22, RN-23)
  - Origem no legado: `caffmob_draw/standards/io_promob.py:_format_number..attributes_from_values`
  - Critério de pronto: `test_promob_io.RoundTripTest` (mesmos 692 pares; 18 → "18"; 1 → "1"; desconhecido intocado) e `test_promob_assembly` (3) passam
  - Confiança: 🟢

- [ ] T-08, JSON: `FORMAT`, `ACCEPTED_FORMATS`, `SCHEMA_VERSION = 1`, `StandardFileError`, `values_to_document` (F-13), `document_to_values` (F-14 passos 1–3), `write_document`, `read_document` (RN-20, RN-23)
  - Origem no legado: `caffmob_draw/standards/io_json.py`
  - Critério de pronto: documento das 870 chaves padrão volta a 870 valores sem avisos (executado nesta extração); CA-17; `BUILTIN` exportado como `USER`. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-48):** `assembly` entra no formato, opcional na leitura (EC-03) — hoje não entra; pendência DT-01
  - Confiança: 🟢

- [ ] T-09, Dados RNA: `ASSEMBLY_ITEMS`, as 6 PropertyGroups com campos/padrões de `design.md`, callbacks com import tardio de `api`, ponteiros `Scene.btm_standards` e `WindowManager.btm_standards_draft`, `register`/`unregister` simétricos
  - Origem no legado: `caffmob_draw/standards/model.py`
  - Critério de pronto: anotações com `# type: ignore`; `unregister` remove os dois ponteiros antes das classes; `.blend` salvo mantém definições e não o rascunho
  - Confiança: 🟢

- [ ] T-10, Embutidas: `BUILTINS`, `BUILTIN_BR_UID`, `BUILTIN_US_UID`, `now_iso`, `fill_from_schema`, `ensure_builtins` (relendo a coleção após `add`) (RN-06)
  - Origem no legado: `caffmob_draw/standards/builtin.py`
  - Critério de pronto: CA-03; chamar duas vezes não duplica nem sobrescreve valores
  - Confiança: 🟢

- [ ] T-11, API de definições e valores: `StandardsError`, `main_scene`, `standards`, `ensure_ready` (F-03), `active_definition`, `active_assembly`, `find_definition`, `set_active`, `new_uid`, `unique_name`, `copy_values`, `duplicate_definition` (F-04), `remove_definition`, `get_definition_value`, `get_value`, `get_value_m`, `definition_values`, `_write`, `set_value`, `set_values` (RN-05 a RN-10)
  - Origem no legado: `caffmob_draw/standards/api.py:main_scene..set_values`
  - Critério de pronto: CA-04, CA-05, CA-06; comparação de definições por `as_pointer()`
  - Confiança: 🟢

- [ ] T-12, API do rascunho: `user_unit`, `format_param_value`, `begin_draft` (F-05), `set_draft_value`, `draft_definition`, `pending_changes` (F-06), `_component_label`, `apply_draft` (versão só com pendências) (RN-11)
  - Origem no legado: `caffmob_draw/standards/api.py:user_unit..apply_draft`
  - Critério de pronto: CA-09; renomear sozinho não incrementa versão; embutida ou definição removida → `StandardsError`
  - Confiança: 🟢

- [ ] T-13, Árvore e edição: `expanded_paths`, `toggle_group`, `rebuild_tree` (F-07, guarda `_suppress`), `activate_tree_row`, `tree_image_key`, `select_param`, `commit_edit_text` (arredonda a 4 casas em mm), `edit_enum_items` com `_ENUM_ITEMS_CACHE`, `commit_edit_enum` (F-08)
  - Origem no legado: `caffmob_draw/standards/api.py:expanded_paths..commit_edit_enum`
  - Critério de pronto: CA-07, CA-08; busca "lateral" abre todos os grupos que contêm o componente; `tree_index` nunca fica fora da lista. 🟡 Validar EC-15 no Blender com clique real (sonda pelo Python já dispara o `update` com o mesmo valor) _(Revisão 2026-10-10)_
  - Confiança: 🟢

- [ ] T-14, Overrides e destinos legados: constantes de propriedades/tags, `_SYNC_DEPTH`, `is_syncing`, `module_root`, `get_overrides`, `add_override`, `clear_overrides`, `make_skip`, `_scenes_for`, `write_legacy_targets`, `_update_frameless`, `_update_closets`, `_tag_lines`, `affected_modules` (RN-16, RN-17, RN-19)
  - Origem no legado: `caffmob_draw/standards/sync.py:is_syncing.._tag_lines`
  - Critério de pronto: CA-15; JSON inválido em `btm_overrides` lido como conjunto vazio; destino inexistente na cena é ignorado
  - Confiança: 🟢

- [ ] T-15, Módulos CAFFMob: `STANDARD_UID_PROP`, `is_caffmob_module`, `_other_roots`, `scene_modules`, `plan_for`, `apply_to_module` (F-12), `apply_definition`/`_apply_definition` (F-11, contador em `finally`) (RN-15, RN-16)
  - Origem no legado: `caffmob_draw/standards/sync.py:apply_definition.._apply_definition`
  - Critério de pronto: CA-13, CA-14; `modules=[]` não toca módulos CAFFMob mas grava destinos e `cut_plan_stale` (EC-02); relatório com as 8 chaves de `design.md`; smoke `tests/blender_012_apply_smoke.py` passa no Blender
  - Confiança: 🟢

- [ ] T-16, Integração JSON com a cena: `user_folder`, `export_definition`, `import_definition` (F-14 passos 4–5) (RF-08)
  - Origem no legado: `caffmob_draw/standards/io_json.py:user_folder/export_definition/import_definition`
  - Critério de pronto: CA-16; importação não ativa; conflito de nome renomeia; `replace` nunca remove embutida
  - Confiança: 🟢

- [ ] T-17, Migração: constantes, `_is_set` (`is_property_set` protegido), `legacy_values`, `_has_legacy_cabinets`, `migrate_scene`, `stamp_standard_uid`, `run` (só `StandardsError` capturado), `_startup_timer`, `register`/`unregister` do timer; chamada em `caffmob_draw/__init__.py` no `load_file_post` após garantir a cena principal (RN-24, F-17)
  - Origem no legado: `caffmob_draw/standards/migration.py`; `caffmob_draw/__init__.py:99`
  - Critério de pronto: CA-20, CA-21; `config_*` prevalece sobre `dimension_settings` nas mesmas chaves; M-03 roda a cada abertura
  - Confiança: 🟢

- [ ] T-18, Imagens: `REFS_DIR`, `_collection`, `_missing`, `image_path`, `icon_id` (F-18), `register`/`unregister` (RF-12)
  - Origem no legado: `caffmob_draw/standards/previews.py`
  - Critério de pronto: CA-23; `unregister` remove a coleção e limpa `_missing`
  - Confiança: 🟢

- [ ] T-19, Pacote: `standards/__init__.py` com `_MODULES = [model, previews, migration]`, registro na ordem e remoção inversa
  - Origem no legado: `caffmob_draw/standards/__init__.py`
  - Critério de pronto: habilitar/desabilitar a extensão duas vezes sem erro de classe já registrada
  - Confiança: 🟢

- [ ] T-20, Operadores de Configurador e gestão: `_LAST_REPORT`, `PENDING_ROWS = 8`, `_set_report`, `_show_report`, `_apply_report_lines`, `_sync_report_message`, `draw_pending`, `draw_editor`, `BTM_OT_StandardsConfigurator`, `BTM_OT_StandardsApply`, `_definition_items` (com cache), `BTM_OT_StandardsSetActive`, `BTM_OT_StandardsDuplicate`, `BTM_OT_StandardsRename`, `BTM_OT_StandardsDelete` (RF-03, RF-04)
  - Origem no legado: `caffmob_draw/operators/ops_standards.py:_set_report..BTM_OT_StandardsDelete`
  - Critério de pronto: `bl_idname`/`bl_options`/propriedades conforme a tabela de `design.md`; Rename/Delete com `poll` falso para embutidas; Configurador com `width=980`
  - Confiança: 🟢

- [ ] T-21, Operadores de arquivo e relatório: `_default_filename`, `BTM_OT_StandardsExportJSON`, `BTM_OT_StandardsImportJSON`, `BTM_OT_StandardsImportPromob` (cria BR, `PROMOB_IMPORT`, montagem de `CAFF_MONTAGEM`), `BTM_OT_StandardsExportPromob`, `BTM_OT_StandardsReport` (RF-08, RF-09, RF-11)
  - Origem no legado: `caffmob_draw/operators/ops_standards.py:_default_filename..BTM_OT_StandardsReport`
  - Critério de pronto: CA-18, CA-19, CA-22; exportações sem `UNDO`; relatório não abre em background
  - Confiança: 🟢

- [ ] T-22, Duas perguntas: `ask_apply`, `_apply_names`, `_draw_counts`, `BTM_OT_StandardsApplyScene` (`previous_uid`, `apply_differ`, `interactive` HIDDEN/SKIP_SAVE), `BTM_OT_StandardsApplyDiffer` (F-10) (RN-12, RN-14)
  - Origem no legado: `caffmob_draw/operators/ops_standards.py:ask_apply..BTM_OT_StandardsApplyDiffer`
  - Critério de pronto: CA-12, CA-13; em EXEC com `apply_differ=True` aplica as duas listas sem diálogo; `execute` recalcula o plano. 🟡 Decidir se EC-01 (reaparecimento na 2ª pergunta) deve ser mantido
  - Confiança: 🟢

- [ ] T-23, UIList `BTM_UL_StandardsTree` (indentação, ícones de grupo, valor à direita, `filter_items` vazio) e o bloco `ui/panels.py:draw_standards_box` (`SUMMARY_KEYS`) como consumidor
  - Origem no legado: `caffmob_draw/ui/standards_tree.py`; `caffmob_draw/ui/panels.py:draw_standards_box`
  - Critério de pronto: árvore desenhada no Configurador; valores na unidade da cena com vírgula decimal
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Rodar os testes puros existentes: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_dimension_schema test_standards_apply_core test_cabinet_defaults test_promob_io test_promob_assembly` → 35 testes (executado em 2026-10-10: OK) 🟢
- [ ] TT-02, Teste puro novo de `io_json`: ida e volta `values_to_document` → `document_to_values` para as 870 chaves; recusa de `schema`, `schema_version` > 1, `unit` ≠ mm e valor fora da faixa (CA-17) 🟢 (não existe hoje: nenhum teste puro importa `io_json`; só `blender_identity_smoke.py:66-70` confere `FORMAT`/`ACCEPTED_FORMATS`) _(Revisão 2026-10-10)_
- [ ] TT-03, Teste puro de `validate` com NaN/`inf` documentando o comportamento atual (EC-04) 🟡 (decidido recusar: o teste passa a provar "Valor Inválido"; DT-02)
- [ ] TT-04, Smoke no Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_apply_smoke.py` e `blender_012_cabinet_standard_smoke.py` (CA-12 a CA-14) 🟢 (arquivos existem; não executados) _(Revisão 2026-10-10: os dois executados no Blender 5.2.0, código 0)_
- [ ] TT-05, Teste no Blender da migração (CA-20, CA-21, EC-13) com um `.blend` herdado 🟡
- [ ] TT-06, Teste manual das duas perguntas após "Definir ativa" (EC-01) e do Configurador com duplicação (EC-07) 🟡 (decididos pelo titular em 2026-10-10: questions.md#pergunta-50 e #pergunta-51; testar junto de DT-03 e DT-04)
- [ ] TT-07, Abrir no Promob um XML exportado com `CAFF_MONTAGEM` 🟡 decisão: testar (DT-06; questions.md#pergunta-53)

## Tarefas de Migração de Dados

- [ ] TM-01, M-01/M-02/M-03 são as migrações da unit (T-17); nenhuma migração adicional de formato existe (`Standards.schema_version` fica 1 e não é lido) 🟢

## Ordem Sugerida

1. T-01 a T-03 (esquema): tudo depende das chaves e da validação.
2. T-04 a T-08 (núcleos puros e arquivos): testáveis sem Blender; fecham TT-01/TT-02.
3. T-09 a T-13 (RNA, embutidas, API, rascunho, árvore).
4. T-14 e T-15 (sincronização), que precisam de `cabinet_editor`, `selection` e `legacy`.
5. T-16 a T-19 (integração de arquivos, migração, imagens, registro).
6. T-20 a T-23 (operadores e UI), por fim TT-04 a TT-07.

## Lacunas Pendentes (🔴)

- Montagem no `.btmdim.json` (EC-03): 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-48):** incluir. Pendência de implementação: DT-01.
- Finitude em `validate` (EC-04) e validação da forma interna do JSON (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-49):** EC-04: recusar não finitos (DT-02).
- Reclassificação na 2ª pergunta após "Definir ativa" (EC-01) e rótulo "Fechar" que aplica após duplicar (EC-07). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-50):** excluir da 2ª pergunta os já aplicados (DT-03). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-51):** manter a gravação na cópia e ajustar o rótulo (DT-04).
- Intenção de M-02 ignorar face frame (EC-13). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-52):** incluir face frame em `_has_legacy_cabinets` (DT-05).
- Disparo do `update` de `tree_index` ao clicar na linha já ativa (EC-15).
- Undo encadeado dos três operadores e interoperabilidade real com o Promob. Decisão: testar (DT-07; questions.md#pergunta-87: um passo por operador é aceito) e testar no Promob (DT-06; questions.md#pergunta-53).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `io_json`, escrever `assembly` em `values_to_document` e lê-lo em `import_definition` (opcional, `LATERAL` como padrão), sem subir `schema_version` (decisão questions.md#pergunta-48)
- [ ] DT-02 Em `dimension_schema.validate`, recusar valores não finitos (NaN, inf) como "Valor Inválido" com `math.isfinite` (decisão questions.md#pergunta-49)
- [ ] DT-03 Depois de "Definir ativa" com Sim na 1ª pergunta, excluir da 2ª pergunta ("difere") os módulos já aplicados na 1ª (passar a lista ou recalcular o plano com o uid novo) (decisão questions.md#pergunta-50)
- [ ] DT-04 Confirmar no Blender se o diálogo do Configurador continua aberto após "Duplicar para editar"; manter a gravação na cópia e ajustar o rótulo do botão ("Aplicar") ao reabrir (decisão questions.md#pergunta-51)
- [ ] DT-05 Incluir a tag de face frame em `migration._has_legacy_cabinets`, para M-02 ativar "Padrão EUA (HB5)" também em projetos só com face frame (decisão questions.md#pergunta-52)
- [ ] DT-06 Abrir uma vez no Promob um XML exportado com `CAFF_MONTAGEM`; se recusar, exportar `CAFF_MONTAGEM` só sob opção (decisão questions.md#pergunta-53)
- [ ] DT-07 Registrar num smoke com janela o desfazer da sequência Configurador → 1ª pergunta → 2ª pergunta, aceitando um passo por operador (decisão questions.md#pergunta-87)
