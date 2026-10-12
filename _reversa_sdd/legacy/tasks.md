# Bibliotecas herdadas: porta e conversão (legacy) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar a unit a partir do código de 2026-10-10 (`caffmob_draw/legacy/`, sem alterações sem commit, e a preferência em `caffmob_draw/__init__.py`). IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`. Ordem: preferência e porta → núcleos puros → integração com a cena → grupos → operadores → ciclo de vida → consumidores.

## Pré-requisitos

- [ ] 🟢 `selection/classify.py` (`module_library`, `module_root`, `classify`, `MODULE_TAGS`), `selection/editing.get_dimension`, `selection/component.own_aggregates` — ver `_reversa_sdd/selection/`.
- [ ] 🟢 `customize/adapters` (`for_object`, `read`) e `customize/library_io` (`modules_root`, `list_modules`, `save`) — ver `_reversa_sdd/customize/`.
- [ ] 🟢 `operators/cabinet_builder.py` (`standard_defaults`, `build_module`) e `standards/api.active_assembly` — ver `_reversa_sdd/standards/`.
- [ ] 🟢 `aggregates/ops_aggregate.delete_components` — ver `_reversa_sdd/aggregates/`.
- [ ] 🟢 `operators/ops_standards` (`_set_report`, `caffmob.standards_report`), `ui/save_feedback.show`, `library_panel/categories.invalidate`, `data/i18n` (`tr`, `N_`).
- [ ] 🟢 Bibliotecas herdadas registradas (frameless, face frame, closets, HB core) para ler `face_frame_cabinet`, `face_frame_opening`, `hb_closet_starter`, `Scene.home_builder` e `ops_library.get_user_library_items` — ver `_reversa_sdd/frameless/`, `face_frame/`, `closets/`, `hb_core/`.

## Tarefas

- [ ] T-01, Preferência `show_legacy_libraries` (BoolProperty, `default=False`, nome e descrição de `design.md`) em `BTM_AddonPreferences`, desenhada no grupo "Avançado" (RN-01)
  - Origem no legado: `caffmob_draw/__init__.py:BTM_AddonPreferences`
  - Critério de pronto: preferência aparece em Avançado e vale falso numa instalação nova
  - Confiança: 🟢

- [ ] T-02, Porta: `LEGACY_LIBRARIES`, `_preferences`, `legacy_ui`, `is_legacy`, `legacy_roots` (RN-01 a RN-03)
  - Origem no legado: `caffmob_draw/legacy/gate.py`
  - Critério de pronto: CA-01, CA-02, CA-03; contexto `None`/add-on ausente → `False`; ordem de `scene.objects` preservada
  - Confiança: 🟢

- [ ] T-03, Tradução pura: `LegacyOpening`, `Loss`, `LegacyCabinet`, `LINES`, `TALL_FROM`, chaves e `LOSS_LABELS`, `_TYPES`, `_DOORS`, `_type`, `_line`, `translate` (F-02; RN-06 a RN-11)
  - Origem no legado: `caffmob_draw/legacy/convert_core.py`
  - Critério de pronto: módulo importa sem `bpy`; `test_legacy_convert` (4 testes) passa; CA-06 a CA-09. Se a regra "a maior abertura manda" (D-24) for adotada, registrar a divergência com EC-02
  - Confiança: 🟢

- [ ] T-04, Leitura do armário: `Result`, `LIBRARY_LABELS`, `AGGREGATES` (com `LOSS_LABELS.setdefault`), `SPECIAL_FACE_FRAME`, `_local_box`, `_cabinet_type`, `_openings` (exceção → `[]`), `_other_fronts`, `read_cabinet` (RN-12, RN-13)
  - Origem no legado: `caffmob_draw/legacy/convert.py:_local_box..read_cabinet`
  - Critério de pronto: frameless, face frame e closet devolvem medidas da caixa local avaliada; raiz sem volume usa `get_dimension`; EC-01, EC-04 e EC-08 reproduzidos ou corrigidos com registro
  - Confiança: 🟢

- [ ] T-05, Construção e lote: `Reading`, `_read`, `_build` (F-03), `convert_scene` (F-04), `report_lines` (RN-14 a RN-17)
  - Origem no legado: `caffmob_draw/legacy/convert.py:_read..report_lines`
  - Critério de pronto: CA-10 (mesma caixa no mundo com 2 mm de tolerância, nomes originais, peças herdadas removidas); ordem ler → construir → apagar em lote → renomear; 50 armários em menos de 5 s na fumaça. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-54):** o lote ganha rollback: `try/except` no operador remove os módulos já criados, reporta ERROR com o nome do armário e devolve CANCELLED (EC-05). Pendência de implementação: DT-01
  - Confiança: 🟢

- [ ] T-06, Núcleo puro dos grupos: `SCHEMA_VERSION`, `pending`, `should_offer`, `parse_marker`, `mark`, `dump_marker`, `target_name` (RN-20, RN-21)
  - Origem no legado: `caffmob_draw/legacy/groups_core.py`
  - Critério de pronto: `test_legacy_groups` (3 testes) passa; CA-17, CA-18
  - Confiança: 🟢

- [ ] T-07, Grupos em disco: `TARGET_CATEGORY`, `MARKER_FILE`, `_DATA_KINDS`, `_offer_cache`/`invalidate`, `group_items`, `_marker_path`, `read_marker`, `write_marker` (atômico), `pending_files`, `should_offer` (cache), `dismiss` (RN-19 a RN-21)
  - Origem no legado: `caffmob_draw/legacy/groups.py:invalidate..should_offer/dismiss`
  - Critério de pronto: marcador gravado como em `design.md` (`schema-version` 1, `indent=2`, UTF-8); `OSError` em leitura → `{}`/`[]`; cache invalidado só por `write_marker`
  - Confiança: 🟢

- [ ] T-08, Conversão de grupos: `_snapshot`, `_cleanup`, `_existing_names`, `convert_group` (F-06), `convert_pending` (F-07) (RN-23, RN-24)
  - Origem no legado: `caffmob_draw/legacy/groups.py:_snapshot..convert_pending`
  - Critério de pronto: CA-14, CA-15; nenhum objeto/malha/material carregado sobra e a coleção "CAFFMob conversão" é removida mesmo com erro; `.blend` original intocado; EC-09 e EC-12 com o comportamento atual ou divergência registrada
  - Confiança: 🟢

- [ ] T-09, Aviso e relatório: `_show_report`, `notify_legacy` (F-01, RN-05)
  - Origem no legado: `caffmob_draw/legacy/ops.py:_show_report/notify_legacy`
  - Critério de pronto: CA-05; timer devolve `None`; sem janela o relatório só vai para `_LAST_REPORT`
  - Confiança: 🟢

- [ ] T-10, Operador `caffmob.legacy_convert` (`{'REGISTER','UNDO'}`, `only_active` com `SKIP_SAVE`, `poll`, `invoke_confirm`, `execute`) (F-05, RN-18)
  - Origem no legado: `caffmob_draw/legacy/ops.py:BTM_OT_LegacyConvert`
  - Critério de pronto: CA-10, CA-11; Ctrl+Z desfaz o lote numa etapa (`tests/blender_012_convert_undo.py`, com janela)
  - Confiança: 🟢 _(Revisão 2026-10-10: blender_012_convert_undo passou com xvfb-run)_

- [ ] T-11, Operador `caffmob.legacy_groups_convert` (`{'REGISTER'}`, `poll` OBJECT, dispensa no `invoke` antes da confirmação, `execute` com `categories.invalidate`) (F-08, RN-22)
  - Origem no legado: `caffmob_draw/legacy/ops.py:BTM_OT_LegacyGroupsConvert`
  - Critério de pronto: CA-16, CA-19; INFO "{n} módulo(s) salvos em Geral"
  - Confiança: 🟢

- [ ] T-12, Ciclo de vida: `NEUTRAL_TAB`, `NEUTRAL_MODES`, `neutralize_product_tab`, `on_load_post` (`@persistent`), `_modules`, `register`/`unregister` simétricos; chamada em `caffmob_draw/__init__.py` entre a 011 e o `library_panel` (RN-04, RN-05, RN-25)
  - Origem no legado: `caffmob_draw/legacy/__init__.py`; `caffmob_draw/__init__.py:register/unregister`
  - Critério de pronto: CA-04; desabilitar a extensão remove timer, handler e as 2 classes; reabilitar não duplica o handler
  - Confiança: 🟢

- [ ] T-13, Consumidores da porta: cada ponto de `design.md` › Consumidores pergunta a `gate.legacy_ui` (seletor `product_tab`, modos no HUD, menus de contexto e de encaixe, grupos em "Meus módulos", subpainel de molduras, opções face frame no Selecionado, sincronização herdada do padrão) e a caixa "N armário(s) de bibliotecas antigas" usa `legacy_roots`
  - Origem no legado: `ui/sidebar_insert.py`, `ui/sidebar_selected.py`, `ui/sidebar_build.py`, `ui/context_menu.py`, `ui/my_modules.py`, `ui/view3d_sidebar.py`, `ui/sidebar_project.py`, `ui/menus.py`, `operators/viewport_hud.py`, `selection/component_select.py`, `standards/sync.py`, `library_panel/draw.py`, `library_panel/ops_categories.py`, `library_panel/ops_click.py`
  - Critério de pronto: `tests/blender_012_legacy_gate_smoke.py` passa com a porta aberta e fechada
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Rodar os testes puros existentes: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_legacy_convert test_legacy_groups -v` → 7 testes (executado em 2026-10-10: OK) 🟢
- [ ] TT-02, Teste puro novo de `translate` documentando EC-01 (dupla contagem com `other_fronts`) e EC-03 (vários basculantes) 🟡 (não existe hoje)
- [ ] TT-03, Fumaças no Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_012_legacy_gate_smoke.py` e `tests/blender_012_convert_smoke.py` (CA-01 a CA-04, CA-10) 🟢 (arquivos existem; não executados, Blender ausente) _(Revisão 2026-10-10: executados no Blender 5.2.0 LTS: ambos OK)_
- [ ] TT-04, Desfazer com janela: `blender --factory-startup --enable-event-simulate --python tests/blender_012_convert_undo.py` (RF-07, D-31 da 012) 🟢 (arquivo existe; não executado) _(Revisão 2026-10-10: executado com xvfb-run: OK)_
- [ ] TT-05, Teste de integração de `convert_group`/`convert_pending` com um `.blend` de grupo real: nomes "Nome 1/2", sufixo " (2)", limpeza de dados e marcador (CA-14, CA-15, EC-09, EC-11, EC-12) 🟡 (não existe hoje)
- [ ] TT-06, Teste de falha no meio do lote (`build_module` levantando) para fixar o comportamento do undo (EC-05) 🟡 _(Revisão 2026-10-10: comportamento observado por sonda: módulo parcial fica, Ctrl+Z o remove e mantém os originais; o teste ainda não existe)_

## Tarefas de Migração de Dados

- [ ] TM-01, A conversão é a própria migração de dados herdados para módulos CAFFMob (cena: F-04; grupos: F-06/F-07); não há versão de formato a migrar: `legacy_groups.json` grava `schema-version` 1 e não o lê 🟢

## Ordem Sugerida

1. T-01 e T-02 (preferência e porta): todos os consumidores dependem delas.
2. T-03 e T-06 (núcleos puros): testáveis sem Blender; fecham TT-01.
3. T-04 e T-05 (leitura, construção, lote), que precisam de `selection`, `customize`, `standards`, `aggregates`.
4. T-07 e T-08 (grupos), que reutilizam T-05 e `library_io`.
5. T-09 a T-12 (aviso, operadores, ciclo de vida), por fim T-13 e TT-03 a TT-06.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-54):** o lote ganha rollback: `try/except` no operador remove os módulos já criados, reporta ERROR com o nome do armário e devolve CANCELLED (EC-05; DT-01).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-55):** eliminar a dupla contagem no face frame: `_other_fronts` ignora as gaiolas folha já lidas pelo adaptador (EC-01; DT-02); soma de portas entre aberturas mantida (EC-02).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-56):** a falha do adaptador vira perda declarada (uma linha "frentes não lidas"); a troca de chapas, espessuras e montagem pelo padrão ativo e a redistribuição de prateleiras ganham só uma nota geral no topo do relatório (EC-04; DT-03, DT-04).
- Desfazer, transformações com pai/escala e importação real de `.blend` de grupos só verificáveis no Blender.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `BTM_OT_LegacyConvert.execute`, envolver `convert_scene` em `try/except`: remover os módulos já criados, reportar ERROR com o nome do armário e devolver CANCELLED (decisão questions.md#pergunta-54)
- [ ] DT-02 Em `convert.py:_other_fronts`, ignorar as gaiolas folha do face frame já lidas pelo adaptador, eliminando a dupla contagem de PULLOUT/TILT_OUT/INSET_PANEL (decisão questions.md#pergunta-55)
- [ ] DT-03 Quando `adapter.read(root)` falhar em `_openings`, registrar a perda "frentes não lidas" no relatório em vez de "sem perdas" (decisão questions.md#pergunta-56)
- [ ] DT-04 Acrescentar ao topo do relatório de conversão uma nota geral: chapas, espessuras e montagem passam a ser as do padrão ativo e as prateleiras são redistribuídas (decisão questions.md#pergunta-56)
