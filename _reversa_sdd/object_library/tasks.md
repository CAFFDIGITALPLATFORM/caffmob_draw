# Biblioteca de objetos (object_library) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/object_library/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `caffmob_draw/data/i18n.py` com `tr(msgid)` e `N_(msgid)`; catálogo `data/translations/object_library.json`.
- [ ] 🟢 `aggregates/group.py` com `is_group(obj)` e `create_group(objs, kind, name)`; propriedades `btm_group` (`is_group`, `kind`) e `btm_aggregate` (`is_aggregate`, `kind`, `motion`, `production_part`) (`_reversa_sdd/aggregates/`).
- [ ] 🟢 Operador `caffmob.import_model(filepath)` (`_reversa_sdd/aggregates/` RF-14 a RF-16).
- [ ] 🟢 `library_common.py` com `world_box(objects)` e `thumbnail(context, objects, filepath)`.
- [ ] 🟢 `customize/library_io._addon_version()` e `customize/adapters/common.set_cutpart_material(obj, mat)` (`_reversa_sdd/customize/`).
- [ ] 🟢 Os 3 `.blend` de materiais em `product_libraries/` (`retexture.LIBRARIES`).
- [ ] 🟢 Barra lateral com `group_scope` (`ui/sidebar.py`), que chama as funções de `panels.py`.
- [ ] 🟢 Sem banco de dados, rede ou variáveis de ambiente.

## Tarefas

- [ ] T-01, Criar `catalog.py` puro: `FORMAT`, `VERSION`, `BUNDLED_SOURCE`, `FORBIDDEN_BUNDLED_SOURCE`, `CATEGORIES` (ordem e ícones de RN-01), `CATEGORY_KEYS`, `CATEGORY_ITEMS`, `FEATURES`, `_ID`, `ManifestError(ValueError)`, `Entry`, `slug`, `new_item_id` (RN-01 a RN-04, RF-01)
  - Origem no legado: `caffmob_draw/object_library/catalog.py:1-62`
  - Critério de pronto: `test_categorias` e `test_slug_e_id` passam; `slug("")` = `"item"`, `slug("Ação!!")` = `"acao"`
  - Confiança: 🟢

- [ ] T-02, Implementar `read_manifest` (F-01), `to_manifest` (14 chaves, ordem de `design.md`) e `search` (RN-04)
  - Origem no legado: `caffmob_draw/object_library/catalog.py:read_manifest/to_manifest/search`
  - Critério de pronto: `test_manifesto_valido` (ida e volta idêntica), `test_manifesto_invalido`, `test_categoria_desconhecida_vira_outros`, `test_busca` passam; EC-01 e EC-03 reproduzíveis como documentados
  - Confiança: 🟢

- [ ] T-03, Criar `store.py` puro: `BUNDLED_DIR`, `Item`, `paths_for`, `_scan` (F-02), `list_items`, `by_category`, `unique_name`, `delete`, `check_bundled` (RN-05 a RN-10)
  - Origem no legado: `caffmob_draw/object_library/store.py`
  - Critério de pronto: os 4 testes de `StoreTest` passam (listagem com 1 aviso, "Mesa 3", `PermissionError` no embutido, origem proibida detectada); `delete` também remove `.blend1`
  - Confiança: 🟢

- [ ] T-04, Criar `props.py`: `BTM_PG_ObjectItem` (5 campos), `BTM_PG_ObjectLibraryUI` (`category` padrão `DOORS`, `search` com `TEXTEDIT_UPDATE`), `Object.btm_object_item`, `WindowManager.btm_object_library`; `unregister` simétrico
  - Origem no legado: `caffmob_draw/object_library/props.py`
  - Critério de pronto: registrar/desregistrar duas vezes seguidas sem erro; `obj.btm_object_item.category == 'OTHER'` em objeto novo
  - Confiança: 🟢

- [ ] T-05, Implementar em `item_io.py` as consultas: `_extension_package`, `user_dir`, `all_items`, `_addon_version`, `tree`, `root_of`, `prepare_root` (RN-11), `features_of` (F-03), `existing_names`
  - Origem no legado: `caffmob_draw/object_library/item_io.py:24-84`
  - Critério de pronto: `prepare_root` devolve a própria raiz de um item selecionado sozinho e cria grupo `PLAIN` para malhas soltas; `features_of` da porta embutida = `['GROUP', 'FRAME', 'LEAF_SWING', 'AGGREGATE']`; da mesa = `['GROUP', 'AGGREGATE', 'PRODUCTION_PART']`
  - Confiança: 🟢

- [ ] T-06, Implementar `item_io.save` (F-04): marcação da raiz, `Entry` com medidas em mm (0,1), materiais ordenados, data ISO com fuso, temporários + `os.replace` (`.blend` antes do `.json`), limpeza em `OSError`/`RuntimeError`, miniatura depois (RF-03, RF-04)
  - Origem no legado: `caffmob_draw/object_library/item_io.py:save`
  - Critério de pronto: CA-08 e CA-11; o JSON usa `ensure_ascii=False, indent=1`; `libraries.write(..., path_remap='RELATIVE_ALL', fake_user=True)`; `Item.user` é `folder != BUNDLED_DIR`
  - Confiança: 🟢

- [ ] T-07, Implementar `item_io.insert` (F-05): append de todos os objetos, achar a raiz (nome exato, prefixo antes do ponto, ou raiz sem pai marcada), corrompido → limpar objetos e `ValueError`, ligar à coleção ativa, tirar fake user, posicionar (RN-13)
  - Origem no legado: `caffmob_draw/object_library/item_io.py:insert`
  - Critério de pronto: CA-04, CA-07 e CA-12; EC-06 a EC-08 reproduzíveis como documentados
  - Confiança: 🟢

- [ ] T-08, Implementar `retexture.py`: `LIBRARIES`, `PATH_PROP`, `SIZE_PROP`, `_names_cache`, `library_materials`, `finish_names`, `_finish`, `targets`, `apply_finish`, `image_material` (F-07), `apply_image` (RN-15 a RN-17, RF-06, RF-07)
  - Origem no legado: `caffmob_draw/object_library/retexture.py`
  - Critério de pronto: CA-15 a CA-17; nó Mapping com `Scale = 1/0,6` para 600 mm; segundo pedido igual devolve o mesmo material; nome "Textura: madeira.png 600 mm"
  - Confiança: 🟢

- [ ] T-09, Criar `previews.py` (`icon_id` com chave `caminho:int(mtime)`, coleção sob demanda, `unregister` remove)
  - Origem no legado: `caffmob_draw/object_library/previews.py`
  - Critério de pronto: caminho inexistente → 0; mesmo arquivo → mesmo `icon_id`; arquivo regravado (mtime novo) → nova entrada (EC-11)
  - Confiança: 🟢

- [ ] T-10, Implementar `ops.py` — `item_key`, `find_item`, `_scope_objects`, `SCOPE_ITEMS` e `BTM_OT_ObjectInsert` com `execute`, `invoke`, `_follow`, `modal`, `cancel` (F-06, RN-14, RF-02)
  - Origem no legado: `caffmob_draw/object_library/ops.py:25-126`
  - Critério de pronto: CA-04 a CA-07; Esc remove os objetos em ordem inversa; meio/roda passam adiante; demais eventos consumidos; cabeçalho limpo em todos os caminhos de saída
  - Confiança: 🟢 (código) / 🟢 modal pela barra lateral não acompanha o mouse (EC-10) _(Revisão 2026-10-10: sonda com eventos simulados)_

- [ ] T-11, Implementar `BTM_OT_ObjectLibraryRemove` (confirmação, `store.delete`, `PermissionError`/`OSError`) e `BTM_OT_ObjectLibraryAdd` (F-08, RN-10, RN-11)
  - Origem no legado: `caffmob_draw/object_library/ops.py:129-240`
  - Critério de pronto: CA-09, CA-10, CA-13, CA-14; diálogo de 360 px; `duplicate` só aparece com nome repetido; nome sugerido sem sufixo `.001`
  - Confiança: 🟢

- [ ] T-12, Implementar `_finish_items`, `BTM_OT_ObjectRetextureFinish` (busca em popup, `bl_property = "finish"`) e `BTM_OT_ObjectRetextureImage` (`ImportHelper`, `filter_glob`, `size_mm`) (F-09)
  - Origem no legado: `caffmob_draw/object_library/ops.py:245-305`
  - Critério de pronto: CA-15 a CA-18; `poll` falso sem objeto ativo; enum vazio mostra "Nenhum acabamento"
  - Confiança: 🟢 (código) / 🟡 (estabilidade das strings do enum dinâmico)

- [ ] T-13, Criar `panels.py` (`draw_insert`, `draw_retexture`, `_key`) e ligar em `ui/sidebar_insert.py` (grupo "Objetos") e `ui/sidebar_selected.py` (grupo "Retexturizar", só com malha selecionada) (RF-01, RN-19)
  - Origem no legado: `caffmob_draw/object_library/panels.py`; `caffmob_draw/ui/sidebar_insert.py:draw`; `caffmob_draw/ui/sidebar_selected.py:draw`
  - Critério de pronto: CA-03; grade de 2 colunas com miniatura em escala 4; `X` só em itens do usuário; contagem de avisos visível
  - Confiança: 🟢

- [ ] T-14, `__init__.py` (`_modules` = `props, previews, ops`) e registro no pacote principal (`register` linha 303, `unregister` linha 363 de `caffmob_draw/__init__.py`)
  - Origem no legado: `caffmob_draw/object_library/__init__.py`; `caffmob_draw/__init__.py`
  - Critério de pronto: `unregister` deixa `bpy.types.Object` e `bpy.types.WindowManager` sem as propriedades e a coleção de previews removida
  - Confiança: 🟢

- [ ] T-15, Gerar os 6 itens embutidos com `tools/build_object_library.py` (porta lisa 80, janela de correr 120, cooktop 4 bocas, mesa 120 × 80 com tampo peça de produção, vaso, quadro; origem "CAFFMob Draw", GPL-3.0-or-later, ids fixos) e manter a checagem do `build.py` (RF-08, RN-09)
  - Origem no legado: `tools/build_object_library.py:ITEMS/main`; `build.py` (verificação de `object_library/items`); `caffmob_draw/object_library/items/*`
  - Critério de pronto: CA-19; `build.py` recusa pacote sem `items/`, sem `.blend` de um manifesto ou com origem "3D Warehouse"
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Rodar os testes puros: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_object_library -v` → 10 testes (executado em 2026-10-10: OK) 🟢
- [ ] TT-02, Fumaça no Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_library_smoke.py` (6 embutidos sem avisos, porta no cursor e folha a 90°, tampo da mesa no plano de corte, acabamento e imagem, acrescentar/renomear/substituir, remover, embutido protegido, porta salva volta noutra sessão) 🟢 (arquivo existe; não executado nesta extração) _(Revisão 2026-10-10: executado no Blender 5.2.0 LTS: OK)_
- [ ] TT-03, Teste do modal com eventos simulados (mover, clique, Esc, botão direito), invocado da barra lateral e da própria viewport (CA-05, CA-06, EC-10) 🟡 (não existe) _(Revisão 2026-10-10: comportamento conhecido por sonda: pela viewport segue e Esc remove; pela barra lateral não segue)_; acrescentar o caso da barra lateral seguindo o mouse após DT-01 (questions.md#pergunta-59)
- [ ] TT-04, Teste de regressão para EC-01: manifesto com `"features": 5` não deve derrubar a listagem (hoje derruba) 🟢 (comportamento reproduzido fora do Blender)
- [ ] TT-05, Teste de `save` com falha simulada no segundo `os.replace` e na escrita do `.blend` (CA-11, EC-05) 🟡

## Tarefas de Migração de Dados

- [ ] TM-01, Nenhuma: o manifesto está na versão 1 e não há leitura de versões anteriores. Itens com `version ≠ 1` são ignorados com aviso. 🟢

## Ordem Sugerida

1. T-01 a T-03 (núcleos puros): fecham TT-01 sem Blender.
2. T-04 (propriedades) antes de T-05 a T-07 (dependem de `btm_object_item`).
3. T-08 e T-09 independentes entre si; precisam do Blender.
4. T-10 a T-12 (operadores) depois de T-05 a T-09; T-13 e T-14 por último.
5. T-15 depois de T-06 (o gerador usa `item_io.save`); TT-02 a TT-05 no fim.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-59):** corrigir: quando `context.region_data` for `None`, `_follow` acha a região `WINDOW` da área e converte `event.mouse_x/y` para as coordenadas dela; o caso entra no teste do modal (TT-03) (EC-10). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-90):** a inserção fica sem snapping por ora; os itens de topo (raiz do grupo) passam a entrar na verificação de colisão. Pendência de implementação: collision DT-05. A parte "itens de topo (raiz Empty do grupo) entram na colisão?" fica numa só pergunta, em `_reversa_sdd/collision/tasks.md` (EC-15; vale também para grupos do SketchUp e para o aviso do Mover Sobre, move_over EC-22) _(Revisão cruzada 2026-10-10: pergunta consolidada em collision)_.
- 🟢 Verificar se o pai de uma raiz salva vai junto no `.blend` (EC-08) e se malhas/materiais ficam com fake user após inserir e cancelar (EC-07). _(Revisão 2026-10-10: sonda: o pai vai junto; malhas e materiais sem fake user, órfãos com 0 usuários)_
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-91):** `cancel()` externo remove os objetos de `_loaded` que ainda existirem, igual ao Esc (EC-19). Pendência de implementação: DT-03.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `BTM_OT_ObjectInsert._follow`, quando `context.region_data` for `None`, achar a região `WINDOW` da área e converter `event.mouse_x/y` para as coordenadas dela; cobrir o caso no teste do modal TT-03 (decisão questions.md#pergunta-59)
- [ ] DT-02 Em `item_io.save`, empacotar (`image.pack()`) as imagens de textura própria antes de gravar o `.blend` do item (decisão questions.md#pergunta-60)
- [ ] DT-03 Em `BTM_OT_ObjectInsert.cancel`, remover os objetos de `_loaded` que ainda existirem, como no Esc (decisão questions.md#pergunta-91)
