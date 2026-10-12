# Seleção, Componente e Dimensões (selection) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/selection/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr(msgid)` (devolve o texto fora do Blender) e `N_(msgid)`; `data/units.py` com `get_scene_length_unit()` e `format_length(value, unit)`.
- [ ] 🟢 `hb_types.GeoNodeObject`, `GeoNodeWall`, `GeoNodeCage` com `get_input`/`set_input` levantando `ValueError` sem Geometry Nodes.
- [ ] 🟢 PropertyGroups das outras units registrados: `btm_plane`, `btm_group`, `btm_aggregate`, `btm_stick`, `btm_object_item`, `btm_cabinet`, `btm_geometry`, `face_frame_cabinet`, `hb_closet_starter`, `home_builder`.
- [ ] 🟢 `aggregates/group.object_corners`, `aggregates/apply` (`local_box`, `aggregates_of`, `_write`, `update_position`), `aggregates/limits.face_axes`, `operators/doors_windows` (`_hole_to_leaf`, `_leaf_to_hole`, `_sync_opening`), `openings/sync.kind_of`, `standards/sync.add_override`, `hb_utils.run_calc_fix`, `operators/walls.update_all_wall_miters`, `legacy/gate.legacy_ui` (contratos em `design.md` › Dependências).

## Tarefas

- [ ] T-01, Criar `classify.py` puro: `Classified`, constantes de tipo, `KINDS`, `KIND_LABELS`, `LIBRARY_LABELS`, `MODULE_TAGS`, `FRONT_TAGS`, `FRONT_ROLES`, `BTM_FRONT_SUFFIXES`, `btm_kind` (com `is_property_set`) e alias `_btm_kind`, `module_library`, `_is_front`, `_ancestors`, `module_root` (RN-02 a RN-04)
  - Origem no legado: `caffmob_draw/selection/classify.py`
  - Critério de pronto: importa sem `bpy`; objeto com `btm_plane` não gravado tem `btm_kind == ''` (BUG-TBY3); ordem de `MODULE_TAGS` preservada
  - Confiança: 🟢

- [ ] T-02, Implementar `classify` (F-01, RN-01), `free_group` (RN-06), `movable_root` e `reference_root` (RN-05)
  - Origem no legado: `caffmob_draw/selection/classify.py:classify/free_group/movable_root/reference_root`
  - Critério de pronto: CA-01, CA-02; puxador filho de porta classifica como `FRONT` com `obj` = porta; `OTHER` com biblioteca `''`
  - Confiança: 🟢

- [ ] T-03, Criar `component.py` puro: `is_opening_root`, `_is_stuck`, `_is_frame_leaf`, `_is_own_aggregate` (RN-08), `_is_item`, `component_root` (F-02, RN-07) e `collapse`
  - Origem no legado: `caffmob_draw/selection/component.py:component_root/collapse`
  - Critério de pronto: CA-03, CA-04, CA-05; cota filha de janela sobe para a janela (EC-01); folha LEAF de esquadria sobe para o grupo FRAME
  - Confiança: 🟢

- [ ] T-04, Implementar `own_aggregates` (F-03, RN-10), `_is_frame_group`, `deletes_subtree` e `delete_plan` (F-04, RN-09) com `DeletePlan`
  - Origem no legado: `caffmob_draw/selection/component.py:own_aggregates/deletes_subtree/delete_plan`
  - Critério de pronto: CA-06, CA-07; pós-ordem; sem repetição; grudado nunca entra; `own_aggregates(parede)` reproduz o comportamento atual (desce em módulos, EC-07)
  - Confiança: 🟢

- [ ] T-05, Criar `component_props.py`: `Scene.btm_component_select` (padrão True, `update=_on_toggle` → `forget`), `WindowManager.btm_component_exempt`, `draw_toggle` e `unregister` com `delattr`
  - Origem no legado: `caffmob_draw/selection/component_props.py`
  - Critério de pronto: CA-10; arquivo antigo lê True; desligar e religar promove a seleção atual
  - Confiança: 🟢

- [ ] T-06, Criar `component_select.py`: `_busy`, `_last`, `forget`, `suspended`, `cabinet_modes` (RN-13), `exempt_names`/`set_exempt` (RN-14), `_modal_running`, `_selected`, `_signature`, `normalize` (F-05, RN-12), handlers `@persistent` `on_depsgraph_update` (F-06, RN-11) e `on_load_post`, `register`/`unregister` idempotentes
  - Origem no legado: `caffmob_draw/selection/component_select.py`
  - Critério de pronto: CA-08, CA-09; sem laço de reentrada; assinatura gravada após a promoção; objeto apagado em contexto sobrescrito não quebra; `unregister` remove os dois handlers e chama `forget`
  - Confiança: 🟢

- [ ] T-07, Criar `component_pick.py`: `caffmob.component_pick` (`REGISTER`/`UNDO`, `extend`, F-07) e `caffmob.component_click_reset` (`INTERNAL`, `PASS_THROUGH`), `_enabled` e os 3 itens de keymap em "3D View" com `head=True` (Alt `CLICK`, Alt+Shift `CLICK` com `extend=True`, `PRESS` sem modificadores)
  - Origem no legado: `caffmob_draw/selection/component_pick.py`
  - Critério de pronto: CA-11; o `view3d.select` roda dentro de `suspended()`; `unregister` remove os itens mesmo com keymap já destruído
  - Confiança: 🟢

- [ ] T-08, Registrar no `caffmob_draw/__init__.py`: `component_props`, `component_select`, `component_pick` nessa ordem (após `openings`, antes de `legacy`) e o inverso no `unregister`; `selection/__init__.py` só com a docstring
  - Origem no legado: `caffmob_draw/__init__.py:register/unregister`; `caffmob_draw/selection/__init__.py`
  - Critério de pronto: ativar e desativar a extensão duas vezes sem handler, propriedade ou keymap sobrando
  - Confiança: 🟢

- [ ] T-09, Criar `editing.py`: constantes (`DIM_FIELDS`, `DIM_LABELS`, `GN_DIM`, `WALL_FIELDS`, `LIMITS`, `WALL_LIMITS`), `_check` (mensagem na unidade da cena), `has_dimensions`, `editable_dimensions` (RN-16), `get_dimension` (F-08), `set_dimension` (F-09, RN-18), `get_sill`/`set_sill` (RN-19), `get_wall`/`set_wall` (RN-20)
  - Origem no legado: `caffmob_draw/selection/editing.py`
  - Critério de pronto: CA-12, CA-13, CA-14; validação antes de qualquer escrita; frameless registra override e roda `run_calc_fix`; `height` da parede arrasta `End Height`
  - Confiança: 🟢

- [ ] T-10, Criar `element_size.py`: `Element`, `_GN_KINDS`, `element` (RN-21), `_door_kind`, `box_size` (devolve X, Z, Y × escala), `size` (RN-22, porta pela folha)
  - Origem no legado: `caffmob_draw/selection/element_size.py`
  - Critério de pronto: CA-15; frente devolve o módulo; Empty de grupo mede pelas malhas descendentes
  - Confiança: 🟢

- [ ] T-11, Criar `resize.py`: `MIN_WIDTH`/`MAX_WIDTH`, `can_resize`, `_parents_with_aggregates`, `_width_x`, `_stretched`, `_set_width` (F-10), `_stretch_aggregate` (F-11), `resize` (F-12) (RN-23, RN-24)
  - Origem no legado: `caffmob_draw/selection/resize.py`
  - Critério de pronto: CA-16, CA-17; `u`/`v` capturados **antes** da mudança; fator ignorado se |f − 1| < 1e-6; folhas LEAF intactas; agregado lateral só reposicionado
  - Confiança: 🟢

- [ ] T-12, Integrar os consumidores: `caffmob.delete_with_aggregates` (`aggregates/ops_aggregate.py`), `btm.resize_width` (`ui/ops_resize.py`), aviso `overlays/element_toast.py`, campos de `ui/object_properties.py`, `draw_toggle` em `ui/view3d_sidebar.py`
  - Origem no legado: arquivos citados (fora da unit); contrato em `design.md` › Superfície exposta pelos consumidores
  - Critério de pronto: Delete de uma porta real apaga todas as peças e o furo; Redimensionar abre com a largura atual (da folha, na porta) e mostra o aviso com a medida nova
  - Confiança: 🟢

- [ ] T-13, Registrar textos em `data/translations/selection.json` (23 chaves: rótulos de tipo e biblioteca, mensagens "Valor Inválido…", interruptor e dicas)
  - Origem no legado: `caffmob_draw/data/translations/selection.json`
  - Critério de pronto: interface em inglês sem português nestes textos (`tests/test_i18n_coverage.py` passa)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Classificador: precedência e raízes do Mover Sobre — `tests/test_classify.py` (2 testes) 🟢
- [ ] TT-02, Raiz do componente: porta e janela, agregado e grudado, armário pelo modo, item/grupo/soltos, `collapse` — `tests/test_component_core.py` (5 testes) 🟢
- [ ] TT-03, Plano de exclusão: porta de baixo para cima, sem repetir, agregados e grudados, parede sai sozinha, agregados próprios — `tests/test_component_delete.py` (5 testes) 🟢
- [ ] TT-04, Casos puros ainda sem teste: cota filha de vão (EC-01), `own_aggregates(parede)` (EC-07), agregado dentro de grupo SketchUp (EC-02), `btm_kind` sem `is_property_set` — 🟢 sem teste dedicado; comportamento reexecutado com os objetos simulados de `test_component_core.py` _(Revisão 2026-10-10: EC-01 → Janela, cota do balcão → ela mesma/ANNOTATION; EC-02 → AggInGroup; own_aggregates(parede) → [Fruteira]; btm_plane sem is_property_set → 'WALL')_
- [ ] TT-05, Blender: normalizador, Alt + clique, reset, interruptor, Delete em profundidade — `tests/blender_011_component_smoke.py` 🟢 (existe; não executado nesta extração)
- [ ] TT-06, Blender: aviso e Redimensionar com agregados — `tests/blender_toast_resize_invert.py`; parede sem marca — `tests/blender_bug_TBY3_walls.py`; modos sem interface herdada — `tests/blender_012_legacy_gate_smoke.py` 🟢 (existem; não executados)
- [ ] TT-07, `editing.py` (limites, overrides, `set_wall`) e EC-08/EC-10 — 🔴 sem teste identificado

Comando dos testes puros 🟢: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_classify test_component_core test_component_delete -v` (12 testes, aprovados em 2026-10-10). Testes Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_011_component_smoke.py`.

## Tarefas de Migração de Dados

- 🟢 Nenhuma: `btm_component_select` tem padrão True, então arquivos antigos sem a propriedade já leem o comportamento novo; `btm_component_exempt` é de sessão.

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03 → T-04: núcleo puro (TT-01 a TT-04).
2. 🟢 T-05 → T-06 → T-07 → T-08: seleção por componente no Blender (TT-05).
3. 🟢 T-09 → T-10 → T-11: dimensões, elemento e Redimensionar (TT-06, TT-07).
4. 🟢 T-12 → T-13: consumidores e textos.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-20):** o painel refaz a porta real e mostra a folha, como o Redimensionar (EC-08; também questions.md#pergunta-69). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-2):** `own_aggregates` para em módulos e em parede/piso/teto (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-21):** janela BTM bloqueada em `can_resize` até existir caminho próprio (EC-10). Pendência de implementação: DT-03.
- 🟡 Medir o custo do normalizador com seleções grandes — decisão: medir/testar (DT-04; questions.md#pergunta-77).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Fazer `component.own_aggregates` parar em raízes de módulo e em alvos que não levam a subárvore (parede, piso, teto) (decisão questions.md#pergunta-2)
- [ ] DT-02 Em `editing.set_dimension`/`get_dimension` de porta/janela HB, usar o caminho do Redimensionar: `_leaf_to_hole` ao gravar, `doors_windows._sync_opening` depois, e exibir a medida da folha (decisão questions.md#pergunta-20 e questions.md#pergunta-69)
- [ ] DT-03 Bloquear janela BTM (`btm_plane OPENING`) em `resize.can_resize` até existir caminho próprio (decisão questions.md#pergunta-21)
- [ ] DT-04 Medir o normalizador (`on_depsgraph_update`) com ~500 objetos selecionados; abaixo de 5 ms por atualização, não definir meta (decisão questions.md#pergunta-77)
- [ ] DT-05 Fazer o X/Delete (plugin e `delete_components`) numa parede usar `operators/ops_wall_extras.remove_wall` (regra `KEEP_WITH_WALL`, filhos soltos com a matriz de mundo preservada) (decisão questions.md#pergunta-5)
