# Colisão de Corpo (collision) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/collision/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr(msgid)`; chaves da unit em `data/translations/editor_grudar.json` (e as compartilhadas em `geral.json`, `sidebar.json`, `operators.json`).
- [ ] 🟢 `data/properties.py`: `Object.btm_plane.collision_override` (`INHERIT`/`ON`/`OFF`, padrão `INHERIT`) e `Scene.btm_settings.collision_global` (padrão `True`).
- [ ] 🟢 `selection/classify` (`classify`, `movable_root`, `reference_root`, constantes de tipo; contrato em `_reversa_sdd/selection/`).
- [ ] 🟢 `stick/apply` (`local_box`, `linked`, `face_of`, `project`), `stick/ops_stick.item_of`, `Object.btm_stick`, `Object.btm_aggregate` (`is_aggregate`, `parent_ref`; `_reversa_sdd/aggregates/`).
- [ ] 🟢 `ui/save_feedback.show`; barra lateral única (`ui/sidebar.group_scope`, `ui/sidebar_proxy`) para hospedar os painéis.

## Tarefas

- [ ] T-01, Criar `obb.py` puro: `_EPS`, `OBB` imutável com `corners()` (ordem binária sx, sy, sz) e `aabb()`, `from_box`, `_radius`, `overlap` (SAT de 15 eixos, F-04), `aabb_overlap`
  - Origem no legado: `caffmob_draw/collision/obb.py`
  - Critério de pronto: CA-04 (parte geométrica); caixa girada 45° colide a 1,0 m e não a 0,85 m (`test_caixa_girada`); concêntricos dão `push` (1, 0, 0) (EC-12); `from_box` aceita `lo > hi`
  - Confiança: 🟢

- [ ] T-02, Criar `rules.py` puro: constantes, `Item` (`static`, `group`), `Conflict`, `excluded`, `conflict_kind`, `candidate_pairs` (varredura em X + `only`), `evaluate` (tolerância, troca de A/B, `location`), `sort_key`, `conflicts(items, confirm, only)` (F-03; RN-01 a RN-06)
  - Origem no legado: `caffmob_draw/collision/rules.py`
  - Critério de pronto: CA-04 a CA-07; os 6 testes de `tests/test_collision_rules.py` passam; 1,0 mm exato não colide e 1,1 mm colide (EC-11)
  - Confiança: 🟢

- [ ] T-03, Criar `props.py`: `KIND_ITEMS`, `BTM_PG_Collision`, `BTM_PG_CollisionState` e `WindowManager.btm_collision` com `register`/`unregister` simétricos (RN-16)
  - Origem no legado: `caffmob_draw/collision/props.py`
  - Critério de pronto: tabela de `design.md` reproduzida (nomes, padrões, `subtype`/`unit`); `checked` começa em −1; `unregister` remove o ponteiro antes das classes
  - Confiança: 🟢

- [ ] T-04, Criar em `scan.py` a tradução da cena: `_SKIP_TAGS`, `_FINE_KINDS`, `_Entry`, `_skip`, `box_of`, `_override`, `_root_name`, `_links`, `_kind_of` (ordem de F-02), `collect` (RN-03, RN-07, RN-08, RN-11)
  - Origem no legado: `caffmob_draw/collision/scan.py`
  - Critério de pronto: CA-08 (porta filha da parede e agregado no pai fora da lista); peças e frentes nunca viram item; grupos soltos ficam fora (EC-15); escala negativa produz `half` positivo
  - Confiança: 🟢

- [ ] T-05, Criar `_Meshes` (BVH sob demanda, cache por `as_pointer`, `to_mesh_clear` em `finally`, recuo para a OBB) e `_confirm` (RN-09, F-05)
  - Origem no legado: `caffmob_draw/collision/scan.py:_Meshes/_confirm`
  - Critério de pronto: par não fino não constrói BVH; porta no vão da parede não colide (CA-08); árvore ausente confirma
  - Confiança: 🟢 (código) / 🟡 (EC-01 a decidir)

- [ ] T-06, Criar `enabled`, `find`, `_store`, `selected_names`, `check_all` (erro visível) e `_redraw` (F-01, F-06; RN-10, RN-12)
  - Origem no legado: `caffmob_draw/collision/scan.py`
  - Critério de pronto: CA-01, CA-02, CA-10; `checked` conta também os estáticos em `ALL` e as raízes selecionadas em `SELECTED` (EC-09); exceção não chama `_redraw` (EC-10)
  - Confiança: 🟢

- [ ] T-07, Criar `stale.py`: `_changed`, `reset`, `rechecked`, `_checked_root`, handler `@persistent on_depsgraph_update` e `register`/`unregister` sem duplicar (F-08; RN-13)
  - Origem no legado: `caffmob_draw/collision/stale.py`
  - Critério de pronto: CA-13; mudança num filho de item vigiado liga `stale`; `checked < 0` não liga; `unregister` remove o handler e chama `reset`
  - Confiança: 🟢

- [ ] T-08, Criar `check_moved(objs)` (F-07; RN-14) e ligá-lo ao fim do assentar (`stick/settle._check_collisions`, import protegido por `ImportError`)
  - Origem no legado: `caffmob_draw/collision/scan.py:check_moved`; `caffmob_draw/stick/settle.py:run/_check_collisions`
  - Critério de pronto: CA-14, CA-15, CA-16; linhas sem os movidos preservadas e novas acrescentadas ao fim (EC-05); não altera `checked`/`error`; comportamento de EC-04 reproduzido
  - Confiança: 🟢

- [ ] T-09, Criar `ops_collision.py` com `caffmob.check_collisions`, `caffmob.collision_goto`, `caffmob.collision_clear` e `caffmob.collision_push_out` (`UNDO` só no último), mensagens e códigos de retorno de F-01, F-09, F-10, F-11 (RN-15, RN-17)
  - Origem no legado: `caffmob_draw/collision/ops_collision.py`
  - Critério de pronto: CA-03, CA-11, CA-12, CA-20, CA-21, CA-22; "Afastar" grudado projeta no plano da face pela normal `host.matrix_world.to_3x3() @ frame[3]`; Limpar não chama `stale.reset` 
  - Confiança: 🟢

- [ ] T-10, Criar `overlay.py`: constantes, `_rows`, `_draw_3d` (`POST_VIEW`, `POLYLINE_UNIFORM_COLOR`, 2,5 px, sem profundidade) e `_draw_2d` (`POST_PIXEL`, `blf` 13, sombra), registrados uma vez e removidos no `unregister` (F-12; RF-08)
  - Origem no legado: `caffmob_draw/collision/overlay.py`
  - Critério de pronto: CA-17; sem linhas não desenha nada; `draw_handler_remove` dos dois handles no `unregister`; `docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
  - Confiança: 🟢 (código) / 🟡 (validação visual)

- [ ] T-11, Criar `panels.py`: `draw_collisions` na ordem de F-13, `BTM_PT_Collisions`, `BTM_PT_ItemCollision` (`poll`, campo `collision_override`, até 5 "Colide com"), `classes = ()`; ligar em `ui/sidebar_check.draw` e `ui/object_properties._folded_groups`; `CHECK_ITEM` em `ui/sidebar_vocab` (RF-04, RF-09)
  - Origem no legado: `caffmob_draw/collision/panels.py`; `caffmob_draw/ui/sidebar_check.py`; `caffmob_draw/ui/object_properties.py`; `caffmob_draw/ui/sidebar_vocab.py`
  - Critério de pronto: CA-09, CA-10, CA-18; nunca exibe "Sem colisões" com `stale` ou `error`; botão `X` só com linhas ou `checked ≥ 0`; `tests/test_layout_probe.py` continua passando
  - Confiança: 🟢

- [ ] T-12, Criar `__init__.py` com `_modules()` de import tardio e registro `(props, stale, ops_collision, overlay, panels)` / inverso; incluir `"collision"` em `_submodule_names` e nas chamadas de `caffmob_draw/__init__.py`
  - Origem no legado: `caffmob_draw/collision/__init__.py`; `caffmob_draw/__init__.py`
  - Critério de pronto: `import caffmob_draw.collision.rules` funciona fora do Blender; registrar/desregistrar duas vezes não duplica handlers
  - Confiança: 🟢

- [ ] T-13, Expor o estado ao aviso de salvar (`ui/save_feedback._collision_note`, 004 RF-27) e o núcleo ao validador do editor de armário (`cabinet_editor/validate.py`, GEO-002)
  - Origem no legado: `caffmob_draw/ui/save_feedback.py:_collision_note`; `caffmob_draw/cabinet_editor/validate.py`
  - Critério de pronto: CA-23; "Colisões não verificadas desde a última mudança" com `stale`; validação GEO-002 usa `obb.overlap` com eixos identidade
  - Confiança: 🟢

- [ ] T-14, Textos: todas as strings de `tr` da unit com chave em `data/translations/` (`pt_BR`, `en_US`)
  - Origem no legado: `caffmob_draw/data/translations/editor_grudar.json`
  - Critério de pronto: as 20 mensagens de `tr(...)` e os 3 rótulos de `KIND_ITEMS` encontrados (verificado em 2026-10-10)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Núcleo puro: encostados, penetração de 20 mm, pares excluídos, caixa girada, ordem estável, confirmação e `only` — `tests/test_collision_rules.py` (6 testes, aprovados em 2026-10-10) 🟢
- [ ] TT-02, Casos puros ainda sem teste: tolerância exata 1,0/1,1 mm (EC-11), item em dois estáticos (EC-11), concêntricos (EC-12), ponto do rótulo (EC-02), eixo cruzado (EC-13) — 🟡 executados manualmente nesta extração
- [ ] TT-03, Blender: penetração, Ir para, Afastar, encostados, override `OFF`, porta e agregado excluídos, desatualizado, `_collision_note`, aviso ao soltar, chave desligada, 200 itens ≤ 2 s — `tests/blender_004_collision_smoke.py` 🟢 (existe; não executado nesta extração, Blender ausente)
- [ ] TT-04, Sem teste identificado: contenção em objeto fino (EC-01), objeto novo após verificar (EC-03), `check_moved` sem verificação (EC-04), ordem após `check_moved` (EC-05), escopo `SELECTED` com abertura/agregado (EC-09), erro persistente (EC-10), grudado com `push` normal (CA-22), painel do item em agregado (EC-16) — 🟡 (EC-01, EC-03, EC-04, EC-05, EC-10 e EC-16 decididos pelo titular em 2026-10-10; testes junto de DT-03, DT-04, DT-06 e DT-07)

Comando dos testes puros 🟢: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_collision_rules -v` (o `_bootstrap` exige rodar de dentro de `tests/` ou com `PYTHONPATH=tests`). Fumaça: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_collision_smoke.py`.

## Tarefas de Migração de Dados

- 🟢 Nenhuma: o estado é de sessão (`WindowManager`, não salvo); `collision_override` e `collision_global` já existiam em `data/properties.py` com padrões.

## Ordem Sugerida

1. 🟢 T-01 → T-02 (TT-01, TT-02): núcleo puro, sem Blender.
2. 🟢 T-03 → T-04 → T-05 → T-06: estado, coleta, BVH, verificação manual.
3. 🟢 T-07 → T-08: desatualizado e aviso ao soltar (dependem de `_store`/`find`).
4. 🟢 T-09 → T-10 → T-11 → T-12: operadores, desenho, painéis, registro (TT-03).
5. 🟢 T-13 → T-14: consumidores externos e textos.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-32):** "Afastar" age sobre o selecionado (invertendo o `push`) e recusa com resultado desatualizado; sem prévia (RN-17). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-33):** a confirmação fina trata contenção total por ray-cast de paridade, validado antes no Blender (EC-01). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-34):** objetos novos/apagados/renomeados deixam o resultado desatualizado (EC-03, EC-07) e `check_moved` sem verificação prévia marca `checked` (EC-04). Pendência de implementação: DT-04.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-81):** `check_moved` reordena por `sort_key` (EC-05) e limpa `error` após sucesso (EC-10). Pendência de implementação: DT-07.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-35):** grupos soltos entram na colisão como `ITEM` fino (EC-15; DT-05) e o painel do item edita o agregado ativo (EC-16; DT-06).
- 🔴 Executar `blender_004_collision_smoke.py` no Blender 5.2 e validar visualmente o overlay.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `rules.evaluate`, tratar `depth <= TOLERANCE + 1e-9` como sem ocorrência (1,0 mm estável como encostar) e cobrir 1,0/1,1 mm em `tests/test_collision_rules.py` (decisão questions.md#pergunta-31)
- [ ] DT-02 Em `BTM_OT_CollisionPushOut`, mover o item selecionado quando ele é um dos dois do par (invertendo o `push`) e recusar com mensagem quando o resultado está desatualizado (decisão questions.md#pergunta-32)
- [ ] DT-03 Validar no Blender a contenção total em objeto fino (EC-01) e, quando a BVH não acusa e o SAT acusa, testar o centro do item contra a malha fina por ray-cast de paridade em `scan._confirm` (decisão questions.md#pergunta-33)
- [ ] DT-04 Em `stale.on_depsgraph_update`, ligar `stale` para objeto novo, apagado ou renomeado que `_kind_of` aceitaria e não está em `checked_names`; em `scan.check_moved` sem verificação prévia, marcar `checked` (decisão questions.md#pergunta-34)
- [ ] DT-05 Em `scan._kind_of`, incluir a raiz de `free_group` (SketchUp, biblioteca de objetos) como `ITEM` fino (decisão questions.md#pergunta-35)
- [ ] DT-06 Em `BTM_PT_ItemCollision`, editar o `collision_override` do próprio objeto ativo quando ele é agregado, em vez da raiz do módulo (decisão questions.md#pergunta-35)
- [ ] DT-07 Em `scan.check_moved`, ordenar a lista inteira por `sort_key` ao regravar e limpar `error` quando `find` termina sem exceção (decisão questions.md#pergunta-81)

- [ ] DT-90 Rodar sonda no Blender 5.2 com porta real aberta a 90° e janela instalada; se sair "Colisão entre itens" ou "Penetração em parede" falsa, ligar a folha `LEAF` à raiz da abertura (`IS_WINDOW_BP`/`IS_ENTRY_DOOR_BP`) e à parede hospedeira em `scan._links` (decisão questions.md#pergunta-68; revisão cruzada, numeração 90+ para não colidir com as DT da unit)
