# Biblioteca CAFFMob (library_panel) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/library_panel/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `caffmob_draw/data/i18n.py` com `tr(msgid)` e `N_(msgid)`; catálogo `data/translations/library.json`.
- [ ] 🟢 `customize/library_io.py` com `modules_root()` e `list_modules()`; operador `caffmob.module_insert(filepath)` (`_reversa_sdd/customize/`).
- [ ] 🟢 `operators/cabinet_builder.py` com `caffmob.cabinet_builder(cabinet_type, width, line, assembly, door_swing, shelves, …)` e `standard_defaults(context, line, cabinet_type)` (`_reversa_sdd/operators/`, `_reversa_sdd/standards/` F-09).
- [ ] 🟢 `standards/api.py:active_assembly(scene)`; `units.unit_to_string(unit_settings, valor)`.
- [ ] 🟢 `cabinet_editor`: operador `caffmob.cabinet_editor` com poll (`_reversa_sdd/cabinet_editor/`).
- [ ] 🟢 `legacy/groups.py:should_offer/pending_files` e `caffmob.legacy_groups_convert` (`_reversa_sdd/legacy/` RN-19 a RN-21, F-08).
- [ ] 🟢 `hb_gpu_draw.py` com `draw_rect`, `draw_rect_outline`, `draw_text`, `get_visible_window_bounds`; `operators/viewport_hud.py` com `_hud_enabled`, `compute_layout`, `_NavButton`.
- [ ] 🟢 Sem banco de dados, rede ou variáveis de ambiente.

## Tarefas

- [ ] T-01, Criar `categories_core.py` puro: `Category`, `LINES`, `LINE_LABELS`, `FIXED` (ordem Cozinha, Banheiro, Sala, Home office), `DEFAULT_LINE='COZ'`, `SCHEMA_VERSION=1`, msgids `EMPTY/REPEATED/INVALID_CHAR`, `all_categories`, `_key`, `validate_name` (F-01) (RN-01 a RN-03, RF-02, RF-03)
  - Origem no legado: `caffmob_draw/library_panel/categories_core.py:FIXED/validate_name/all_categories`
  - Critério de pronto: `test_fixas_em_ordem` e `test_validar_nome` passam; "COZINHA" é repetido; `.` e `..` passam (EC-12)
  - Confiança: 🟢

- [ ] T-02, Implementar `parse`, `dump`, `merge_folders`, `with_line` conforme F-02 e RN-04/RN-05
  - Origem no legado: `caffmob_draw/library_panel/categories_core.py:parse/dump/merge_folders/with_line`
  - Critério de pronto: `test_json`, `test_json_ruim`, `test_pastas_soltas` passam; `dump` usa `ensure_ascii=False, indent=2` e a chave `"schema-version"`; `{"categories": "ab"}` gera 2 avisos "Categoria sem nome ignorada"
  - Confiança: 🟢

- [ ] T-03, Implementar `categories.py`: `FILE_NAME`, `_cache`, `invalidate`, `_folders`, `load` (F-03, sem cachear em `OSError`), `save` atômico (F-04), `create` (F-05), `set_line`, `all_categories`, `find` (nome exato) (RN-05 a RN-07, RF-02, RF-03, RF-07)
  - Origem no legado: `caffmob_draw/library_panel/categories.py`
  - Critério de pronto: CA-04 a CA-06; `load` regrava só se mudou e não há avisos; `save` remove o `.tmp` em falha e relança; EC-01 e EC-03 reproduzíveis como documentados
  - Confiança: 🟢

- [ ] T-04, Criar `models_core.py` puro (`Model`, `CABINET_TYPES`, `DOOR_SWINGS`, `CATALOG`, `parse` F-06, `load_default`, `find`) e o dado `data/library_models.json` com os 5 modelos de `design.md` (RN-08, RF-04)
  - Origem no legado: `caffmob_draw/library_panel/models_core.py`; `caffmob_draw/data/library_models.json`
  - Critério de pronto: `test_catalogo_do_pacote` e `test_itens_invalidos` passam; `load_default` sem arquivo → `([], ["Catálogo de modelos não encontrado"])`; não numérico levanta `ValueError` (EC-07)
  - Confiança: 🟢

- [ ] T-05, Criar `layout_core.py` puro: `Layout`, `TITLE`, constantes (8/12/8/24/2/12), chaves, `LABELS`, `menu_items` (RN-11), `category_of`, `panel_layout` (F-07), `hit` (bordas inclusivas, rótulo primeiro), `bounds` (RN-12, RF-01)
  - Origem no legado: `caffmob_draw/library_panel/layout_core.py`
  - Critério de pronto: os 5 testes de `test_library_layout` passam; com escala 1 e `menu_items(['Cozinha'])` o rótulo fica em `(8, 464, w, 24)` para `y_max=500`; intervalo entre linhas não acerta nada (EC-06)
  - Confiança: 🟢

- [ ] T-06, Criar `props.py`: `BTM_PG_LibraryState(open=False, category, line='COZ')` e `WindowManager.btm_library`; `unregister` remove a propriedade e a classe
  - Origem no legado: `caffmob_draw/library_panel/props.py`
  - Critério de pronto: registrar/desregistrar duas vezes sem erro; `bpy.context.window_manager.btm_library.line == 'COZ'`
  - Confiança: 🟢

- [ ] T-07, Criar `draw.py`: `FONT_SIZE=11`, cores, `_scale`, `_nav_right` (HUD), `offer_groups` (captura `ImportError/AttributeError/OSError`), `items`, `layout` com cache por `region.as_pointer()` (F-08), `draw_panel` (F-09), `tag_redraw`, `register`/`unregister` do handler `POST_PIXEL` em `SpaceView3D` (RN-12, RN-16, RF-01)
  - Origem no legado: `caffmob_draw/library_panel/draw.py`
  - Critério de pronto: CA-01; o handler é adicionado uma só vez e removido no `unregister` com `_cache` limpo; o painel aparece com o HUD desligado; blend volta a `NONE` antes do texto
  - Confiança: 🟢

- [ ] T-08, Criar `ops_click.py`: `_in_viewport`, `_hit`, `_run` (só com poll), `dispatch` (F-11), operadores `caffmob.library_click` (F-10), `caffmob.library_hover` (F-12), `caffmob.library_close`, todos `INTERNAL`; keymap "3D View" `head=True` (LEFTMOUSE PRESS any, MOUSEMOVE ANY any, ESC PRESS) e remoção simétrica (RN-13, RN-14, RF-01)
  - Origem no legado: `caffmob_draw/library_panel/ops_click.py`
  - Critério de pronto: CA-02, CA-03; fora do painel sempre `PASS_THROUGH`; abrir invalida o cache de categorias; em background (`keyconfigs.addon is None`) registra só as classes
  - Confiança: 🟢

- [ ] T-09, Criar `popover.py`: `_open`, `_draw` (F-13), `show(context, category)` com `wm.popover(_draw, ui_units_x=16)`, operador `caffmob.library_insert_model` (`REGISTER, UNDO`; F-14) (RN-09, RN-15, RF-04, RF-05)
  - Origem no legado: `caffmob_draw/library_panel/popover.py`
  - Critério de pronto: CA-08 a CA-11; grade de 2 colunas sem miniaturas; engrenagem só em categoria do usuário; `OSError/ValueError` de `list_modules` vira "Biblioteca indisponível: {}"
  - Confiança: 🟢

- [ ] T-10, Criar `ops_categories.py`: `_LINE_ITEMS`, `caffmob.library_category_create` (diálogo, botão de conversão quando há oferta ou pendentes, WARNING com motivo, INFO e `tag_redraw`) e `caffmob.library_category_set_line` (recusa fixas no `invoke`), ambos `{'REGISTER'}` (RN-06, RN-07, RN-17, RF-03, RF-07, RF-08)
  - Origem no legado: `caffmob_draw/library_panel/ops_categories.py`
  - Critério de pronto: CA-06, CA-07, CA-14, CA-15; `execute` do set_line não revalida (EC-08)
  - Confiança: 🟢

- [ ] T-11, Criar `ops_cabinet.py`: `caffmob.library_create_cabinet` (`REGISTER, UNDO`, poll modo OBJECT), `invoke` com linha da última categoria, montagem ativa e largura do padrão; `draw` com dica de altura/profundidade; `execute` com `cabinet_builder(cabinet_type, width, line, assembly)` e abertura do editor (F-15) (RN-10, RF-06)
  - Origem no legado: `caffmob_draw/library_panel/ops_cabinet.py`
  - Critério de pronto: CA-12, CA-13; cancelar o diálogo não cria objeto; `open_editor=False` não abre o editor; largura não muda ao trocar o tipo (EC-10)
  - Confiança: 🟢

- [ ] T-12, Criar `__init__.py` com `_modules()` na ordem `props, popover, ops_categories, ops_cabinet, ops_click, draw`, `register` e `unregister` invertido; chamar no `caffmob_draw/__init__.py` depois de `legacy.register()` (e antes de `legacy.unregister()` na saída)
  - Origem no legado: `caffmob_draw/library_panel/__init__.py`; `caffmob_draw/__init__.py:309/358`
  - Critério de pronto: desabilitar e reabilitar a extensão não duplica handler nem keymaps; `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erros
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Rodar os testes puros: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_library_layout test_library_models test_library_categories -v` → 12 testes (executado em 2026-10-10: OK) 🟢
- [ ] TT-02, Fumaça de interface com eventos simulados: `blender --factory-startup --enable-event-simulate --python tests/blender_012_library_ui.py` (CA-01, CA-02, CA-08, CA-12; categoria criada aparece antes de "Criar categoria") 🟢 (arquivo existe; não executado, precisa de janela) _(Revisão 2026-10-10: executado com xvfb-run: OK)_
- [ ] TT-03, Fumaça do padrão: `tests/blender_012_cabinet_standard_smoke.py` cobre o armário criado pelo padrão 🟢 (arquivo existe; não executado) _(Revisão 2026-10-10: executado em background: OK)_
- [ ] TT-04, Teste puro novo de `categories.load/create` com pasta temporária (monkeypatch de `library_io.modules_root`) fixando EC-01 (sobrescrita do arquivo corrompido) e o não-cache de `OSError` (EC-03) 🟡 (não existe hoje)
- [ ] TT-05, Teste puro de `models_core.parse` com valores não numéricos e IDs repetidos (EC-07) 🟡 (não existe hoje)
- [ ] TT-06, Verificar no Blender: coluna com muitas categorias (EC-05), duas viewports (EC-16) e categoria com `:` no nome (EC-04) 🟡 _(Revisão 2026-10-10: EC-04 reproduzido por sonda no Blender; EC-05 e EC-16 seguem pendentes)_ decisão: testar (DT-04); EC-04 e EC-05 mudam por DT-01 e DT-03 (questions.md#pergunta-57, #pergunta-88)

## Tarefas de Migração de Dados

- [ ] TM-01, Migração implícita das pastas de módulos existentes para categorias COZ na primeira leitura (`merge_folders` + `save`, só sem avisos); `schema-version` gravada e não lida 🟢

## Ordem Sugerida

1. T-01, T-02, T-04, T-05 (núcleos puros): fecham TT-01 sem Blender.
2. T-03 (disco) e T-06 (estado).
3. T-07 e T-08 (desenho e eventos), que compartilham `draw.layout`.
4. T-09 a T-11 (popover e diálogos), que dependem de `customize`, `operators`, `standards`, `cabinet_editor` e `legacy`.
5. T-12 e TT-02 a TT-06.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-88):** limitar a coluna à altura visível e, acima disso, agrupar as categorias do usuário num item "Mais…" que abre um popover (sem rolagem em GPU) (EC-05; DT-03).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-89):** aceito por ora o estado único por `WindowManager` com várias viewports/janelas (uso típico é uma viewport) (EC-16); ordem do keymap frente ao HUD: 🟡 decisão: testar (DT-04).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-57):** `validate_name` recusa os mesmos caracteres que `customize.manifest.file_stem` troca (e ponto final), evitando a divergência de pasta e a falha no Windows (EC-04; DT-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-58):** antes de `save`, se a última leitura teve aviso de arquivo inválido, renomear para `categories.json.bak` e mostrar o aviso uma vez (`save_feedback`) (EC-01, EC-02; DT-02).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `categories_core.validate_name`, recusar os caracteres que `customize.manifest.file_stem` troca (`< > : " | ? *`, controle) e nome terminado em `.` (decisão questions.md#pergunta-57)
- [ ] DT-02 Em `categories.save`, se a última leitura teve aviso de arquivo inválido, renomear o arquivo para `categories.json.bak` antes de regravar e mostrar o aviso uma vez via `save_feedback` (decisão questions.md#pergunta-58)
- [ ] DT-03 Em `layout_core.panel_layout`, limitar a coluna à altura visível e agrupar o excedente das categorias do usuário num item "Mais…" que abre um popover (decisão questions.md#pergunta-88)
- [ ] DT-04 Acrescentar à fumaça de UI um caso com o HUD ligado que fixe a ordem do keymap do painel frente ao HUD e à seleção por componente (decisão questions.md#pergunta-89)
