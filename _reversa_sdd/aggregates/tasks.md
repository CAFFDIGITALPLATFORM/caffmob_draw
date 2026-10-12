# Agregados, Folhas, Grupos de Peças e Importação (aggregates) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/aggregates/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr(msgid)` e `N_(msgid)`; `data/units.py` com `format_value(valor, scene)`; chaves em `data/translations/aggregates.json`.
- [ ] 🟢 `hb_types.GeoNodeCage` (`create`, `set_input`, `var_input`), `GeoNodeWall.get_input`, `GeoNodeObject.driver_location`, `GeoNodeCutpart.add_part_modifier`; `compat.try_get_gn_input`/`try_set_gn_input`.
- [ ] 🟢 `cutting/machining.AGGREGATE_PREFIX`; `inspection/fronts.module_root_of`; `operators/doors_windows.cut_wall`.
- [ ] 🟢 `selection/component` (`own_aggregates`, `deletes_subtree`, `delete_plan`; contrato em `_reversa_sdd/selection/`); `stick/apply.stuck_items`, `stick/link.release`, `Object.btm_stick`; `ui/save_feedback.show`; `Object.btm_geometry` (unit `geometry_free`).
- [ ] 🟢 Wheels `openskp`, `defusedxml`, `mapbox_earcut`, `shapely` declaradas em `blender_manifest.toml` (opcionais em tempo de execução).

## Tarefas

- [ ] T-01, Criar `limits.py` puro: `FACES`, `FACE_LABELS`, `face_axes`, `size`, `thickness`, `nearest_face`, `limits`, `clamp`, `box_for` (com `clamp_to_face`), `params_from_box`, `sunk_box`, `sunk_depth` (RN-01 a RN-03)
  - Origem no legado: `caffmob_draw/aggregates/limits.py`
  - Critério de pronto: CA-03, CA-04; `box_for` ∘ `params_from_box` é identidade nas seis faces; empate de `nearest_face` fica com `POS_X`; caixa degenerada reproduz EC-01
  - Confiança: 🟢

- [ ] T-02, Criar `sweep.py` puro com passos/tolerâncias e `sweep(..., close, floor, floor_contact)` (F-06, RN-13, RN-14)
  - Origem no legado: `caffmob_draw/aggregates/sweep.py`
  - Critério de pronto: CA-11 (cálculo), CA-14; fechar sem `close` é livre; obstáculo entre amostras atravessado como em EC-05
  - Confiança: 🟢

- [ ] T-03, Criar `slide_limits.py`, `grouping.py` e `import_units.py` puros (RN-15, RN-16, RN-20, RN-24)
  - Origem no legado: `caffmob_draw/aggregates/slide_limits.py`, `grouping.py`, `import_units.py`
  - Critério de pronto: CA-13, CA-17 (sugestão), CA-19 (unidade); casos de nome de EC-19; `AUTO` com exatamente 50 → metros
  - Confiança: 🟢

- [ ] T-04, Criar `skp_core.py` puro: `MeshPlan`, `GroupPlan`, `_FIGURE`, `to_blender`, `material_names`, `_nodes`, `tree`, `_prune`, `walk`, `plan`, `texture_filename`, `failure_message` (RN-26 a RN-28)
  - Origem no legado: `caffmob_draw/aggregates/skp_core.py`
  - Critério de pronto: CA-21 (árvore), instâncias repetidas pela `position_mm`, contêiner de um filho colapsa, figura de escala contada, deduplicação de EC-18, `texture_filename` sem pastas
  - Confiança: 🟢

- [ ] T-05, Criar `props.py` (`BTM_PG_Aggregate`, `_guard`, `_guarded` e os seis destinos de `update`), `group_props.py` e `window_props.py` com `register`/`unregister` simétricos (RN-18)
  - Origem no legado: `caffmob_draw/aggregates/props.py`, `group_props.py`, `window_props.py`
  - Critério de pronto: tabelas de `design.md` reproduzidas (nomes, padrões, `min`/`max`, `subtype`/`unit`, `update`); `apply._write` não dispara `update`; `unregister` remove `btm_aggregate`, `btm_group`, `btm_window`
  - Confiança: 🟢

- [ ] T-06, Criar `apply.py`: caixas, `_write`, `update_position`, `aggregates_of` e o handler `@persistent` de depsgraph com `_busy` e `_last_parent_box` (F-02, F-02b, RN-04)
  - Origem no legado: `caffmob_draw/aggregates/apply.py`
  - Critério de pronto: CA-05; reposiciona só quando a caixa avaliada do pai muda; ignora `LEAF` e pai Blender ≠ `parent_ref`; um único `_last_parent_box`
  - Confiança: 🟢

- [ ] T-07, Criar `convert.py`: `can_convert` (5 motivos na ordem), `convert`, `unconvert` (F-01, F-01b, RN-05 a RN-07)
  - Origem no legado: `caffmob_draw/aggregates/convert.py`
  - Critério de pronto: CA-01, CA-02, CA-10; `orig_*` só na primeira conversão; desconverter volta à matriz da conversão (EC-02)
  - Confiança: 🟢

- [ ] T-08, Criar `perforate.py` (cortador, `BOOLEAN`, `CPM_CUTOUT`, `real_hole_reason`) e `production.py` (F-03, RN-08 a RN-10)
  - Origem no legado: `caffmob_draw/aggregates/perforate.py`, `production.py`
  - Critério de pronto: CA-07 a CA-09; cortador refeito só quando `btm_box` muda; `Flip Z` e espelho de Y conforme `Mirror Y`/`Mirror Z`; sem afundamento remove tudo
  - Confiança: 🟢

- [ ] T-09, Criar `group.py`: `is_group`, `members`, `object_corners`, `world_box`, `group_box`, `create_group`, `ungroup`, `box_corners` (F-09, F-09b, RN-19)
  - Origem no legado: `caffmob_draw/aggregates/group.py`
  - Critério de pronto: CA-16; o grupo herda o pai comum; desfazer devolve à posição atual; ordem dos cantos igual à do `bound_box`
  - Confiança: 🟢

- [ ] T-10, Criar `leaf.py`: pose fechada, pivô, `base_point`, `swing_angle`, `pose_matrix`, `make_leaf`, `rebuild_pivot`, `remove_pivot`, `update_open`, esquadria (`frame_of`, `sibling_leaves`, `default_slide_dir`, `measure_free_travel`, `low_travel`, `_close_floor`) (F-04, F-05, F-07, RN-11 a RN-16)
  - Origem no legado: `caffmob_draw/aggregates/leaf.py`
  - Critério de pronto: CA-11 a CA-14; `OUT` leva a borda para −Y do pai nos quatro eixos; abrir não altera a malha; `remove_pivot` devolve a pose fechada; EC-06, EC-08 e EC-21 reproduzidos
  - Confiança: 🟢

- [ ] T-11, Criar `collision.py`: `_excluded`, `_targets` (cache), `_bvh` sob demanda, `Tester` com encolhimento diagonal, `invalidate`, handler de depsgraph (F-08, F-08b, RN-17)
  - Origem no legado: `caffmob_draw/aggregates/collision.py`
  - Critério de pronto: peças da esquadria contam e as irmãs não; marco da porta real (`btm_opening_frame` = pai) excluído; cache limpo por mudança fora das folhas/pivôs; `unregister` limpa o cache; EC-04 e EC-07 reproduzidos
  - Confiança: 🟢

- [ ] T-12, Criar `install.py` e `ops_install.py` (`caffmob.window_install`, `caffmob.window_uninstall`) (F-11, F-11b, RN-22, RN-23)
  - Origem no legado: `caffmob_draw/aggregates/install.py`, `ops_install.py`
  - Critério de pronto: CA-18; drivers `dim_x/2`, `dim_y/2` acompanham a espessura do Editor de Paredes; desinstalar remove drivers, corte e jaula (EC-14, EC-20)
  - Confiança: 🟢

- [ ] T-13, Criar `ops_group.py`: `caffmob.group_create`, `caffmob.group_dissolve`, `BTM_PG_AssembleRow`, `caffmob.window_assemble` (F-10, F-18, RN-21, RN-31)
  - Origem no legado: `caffmob_draw/aggregates/ops_group.py`
  - Critério de pronto: CA-16, CA-17; `execute` sem diálogo usa a sugestão; folhas de correr com o sentido do próprio lado e curso medido; EC-03 e EC-12 reproduzidos
  - Confiança: 🟢

- [ ] T-14, Criar `ops_import.py` (`caffmob.import_model`, `_kwargs`, `_apply_unit`, `_group_import`), `skp.py` (`available`, `read`) e `skp_build.py` (`_image`, `_material`, `_mesh_object`, `_empty_group`, `_build_node`, `build`) (F-12, F-13, RN-24 a RN-28)
  - Origem no legado: `caffmob_draw/aggregates/ops_import.py`, `skp.py`, `skp_build.py`
  - Critério de pronto: CA-19 a CA-22; glTF `AUTO` sem escala; 2+ malhas viram componente; reimportar não duplica materiais; texturas empacotadas; falha não deixa objetos (EC-17, EC-22)
  - Confiança: 🟢

- [ ] T-15, Criar `ops_aggregate.py`: `caffmob.aggregate_convert`, `caffmob.leaf_convert` (diálogo 320), `caffmob.aggregate_unconvert`, `caffmob.aggregate_move` (modal `BLOCKING`), `caffmob.delete_with_aggregates`, `delete_components`, `_release_stuck_children`, keymap X/Delete `head=True` (F-14, F-15, RN-29)
  - Origem no legado: `caffmob_draw/aggregates/ops_aggregate.py`
  - Critério de pronto: CA-01, CA-02, CA-06, CA-10, CA-23, CA-24; remoção em lote por `batch_remove`; vão apagado tira o `BOOLEAN` da parede; `unregister` remove os itens de keymap engolindo `ReferenceError`/`RuntimeError`; EC-11, EC-13, EC-15, EC-16 reproduzidos
  - Confiança: 🟢

- [ ] T-16, Criar `overlay.py` (dois handlers registrados uma vez) e `panels.py` (`draw_aggregate`, `BTM_PT_Aggregate` não registrado) (F-16, F-17, RN-30)
  - Origem no legado: `caffmob_draw/aggregates/overlay.py`, `panels.py`
  - Critério de pronto: CA-15, CA-25; `draw_handler_remove` de ambos no `unregister`; folha ativa reconhecida pela malha, pelo pivô e por peça do grupo-folha
  - Confiança: 🟢

- [ ] T-17, Criar `__init__.py` com `_modules()` de import tardio na ordem `props`, `group_props`, `window_props`, `apply`, `collision`, `ops_import`, `ops_aggregate`, `ops_group`, `ops_install`, `overlay`, `panels`; `unregister` na inversa
  - Origem no legado: `caffmob_draw/aggregates/__init__.py`
  - Critério de pronto: os testes puros importam `limits`/`sweep`/… sem `bpy`; registrar e desregistrar duas vezes sem erro nem handler duplicado
  - Confiança: 🟢

- [ ] T-18, Ligar os consumidores: `ui/object_properties.py` (grupo "Agregados e folhas" e linha de limites), `ui/sidebar_insert.py`, `openings/sync.py`, `cabinet_editor/scene_slides.py`, `selection/resize.py`, `selection/element_size.py`, `move_over/scene.py`, `object_library/item_io.py`/`ops.py`, `stick/*`, `operators/doors_windows.py`, `legacy/convert.py`, `cutting/part_sources.py`, `inspection/adapters/aggregate_leaf.py`, `stick/settle.py`
  - Origem no legado: arquivos citados em `design.md` › Superfície usada pelos consumidores
  - Critério de pronto: porta/janela real monta folhas que abrem; deslizantes do editor medem curso; apagar porta/janela e herdados usa `delete_components`; peça de produção aparece no plano de corte
  - Confiança: 🟢

- [ ] T-19, Textos: chaves de `tr`/`N_` da unit em `data/translations/aggregates.json` (`pt_BR`, `en_US`)
  - Origem no legado: `caffmob_draw/data/translations/aggregates.json`
  - Critério de pronto: todas as strings de `tr`/`N_` com chave (verificado em 2026-10-10); decidir se "Gire a vista para enxergar a face do pai", o título "O objeto tem agregados" e "{mín} a {máx}" passam por `tr`
  - Confiança: 🟢 (cobertura) / 🟡 (decisão)

## Tarefas de Teste

- [ ] TT-01, Limites na face: borda, afundar até a espessura, caixa inversa nas seis faces, afundado, maior que a face, face mais próxima — `tests/test_aggregate_limits.py` (6 testes) 🟢
- [ ] TT-02, Varredura: para no contato do giro, correr, fechar livre, sem obstáculo, já encostada, fechar com contato, com limite mínimo, livre até zero — `tests/test_leaf_sweep.py` (8 testes) 🟢
- [ ] TT-03, Batentes de correr: sentido padrão, pouco curso, sobreposição, fechar com a outra em repouso e no caminho — `tests/test_slide_limits.py` (5 testes) 🟢
- [ ] TT-04, Sugestão de grupos (4), unidade (2), SketchUp plano (5) e árvore (5) — `tests/test_grouping.py`, `test_import_units.py`, `test_skp_core.py`, `test_skp_tree.py` 🟢
- [ ] TT-05, Casos puros ainda sem teste: obstáculo entre amostras (EC-05), `bound_box` degenerado (EC-01), nomes `"Sash_"`/`"Folha"` (EC-19), deduplicação de primitivas distintas (EC-18) — 🟢 reexecutados em Python puro na revisão (EC-05 corrigido para 2,75°; EC-19 e o cálculo de EC-01 conferem); EC-18 confirmado pela leitura de `skp_core.py:tree` linhas 149-152; continuam sem teste automatizado _(Revisão 2026-10-10: 🟡→🟢)_
- [ ] TT-06, Blender: converter, limites, perfurar, furo real, produção, folha que para — `tests/blender_003_aggregates_smoke.py`; contato — `blender_004_collision_smoke.py`; esquadria, curso livre, batentes, instalar — `blender_007_window_smoke.py` 🟢 (existem; não executados nesta extração)
- [ ] TT-07, Blender: SketchUp — `blender_009_skp_smoke.py`, `blender_010_skp_tree_smoke.py`, `blender_bug_skp_mover_sobre.py`; componente e Delete — `blender_011_component_smoke.py`; exclusão em lote — `blender_012_apply_smoke.py` 🟢 (existem; não executados)
- [ ] TT-08, Sem teste identificado: desconverter após mover o pai (EC-02), folha com pai parede (EC-07), reconverter folha aberta (EC-08), renomear agregado perfurado (EC-09), arraste com perfurado (EC-11), desinstalar com pai anterior (EC-14), simulação gráfica — 🟡 (EC-02, EC-07 e EC-14 decididos pelo titular em 2026-10-10: questions.md#pergunta-27, #pergunta-29, #pergunta-79; testes junto de DT-02, DT-04, DT-07)

Comando dos testes puros 🟢: `cd tests && python3 -m unittest test_aggregate_limits test_leaf_sweep test_slide_limits test_grouping test_import_units test_skp_core test_skp_tree -v` (35 testes, aprovados em 2026-10-10; o `_bootstrap` exige rodar de dentro de `tests/` ou com `PYTHONPATH=tests`). Testes Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_003_aggregates_smoke.py` (idem para os demais).

## Tarefas de Migração de Dados

- 🟢 Nenhuma migração automática: `btm_aggregate`, `btm_group` e `btm_window` são `PointerProperty` com padrões; arquivos anteriores à 007 leem `free_travel = 0`, `rest_overlap = 0`, `contact_kind = 'NONE'` (sem teto de curso e sem batente de fechar até reconverter).
- 🟢 Folhas com pivô apagado não são refeitas sozinhas; o painel pede desconverter e converter de novo.

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03 → T-04: núcleos puros (TT-01 a TT-05).
2. 🟢 T-05 → T-06 → T-07 → T-08 → T-09: estado, posição, conversão, recorte e grupo.
3. 🟢 T-10 → T-11: folha e contato (TT-06).
4. 🟢 T-12 → T-13 → T-14 → T-15 → T-16 → T-17: operadores, importação, desenho, painel e registro (TT-06, TT-07).
5. 🟢 T-18 → T-19: consumidores e textos.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-28):** `apply.local_box` usa a união das peças quando o pai é grupo/Empty (EC-01). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-27):** desconverter mantém a posição atual (EC-02, EC-16). Pendência de implementação: DT-02. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-4):** Delete de parede/piso/teto não pergunta pelos agregados dos módulos filhos (EC-16). Pendência de implementação: selection DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-29):** folha com pai fora de módulo exclui só o pai e a si mesma (EC-07). Pendência de implementação: DT-04.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-30):** mudar `swing_sign`/`max_angle`/`travel` com a folha aberta fecha e reabre pela varredura (EC-06; DT-05); o passo da varredura fica como está até haver caso real (EC-05).
- 🟡 Medir o custo da varredura, de `measure_free_travel` e do recorte durante o arraste em cenas grandes (EC-11); decisão: medir (DT-06; questions.md#pergunta-80).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `convert.can_convert`, trocar o 3º teste para `parent in obj.children_recursive` (recusar pai descendente do objeto, como diz a mensagem) (decisão questions.md#pergunta-3)
- [ ] DT-02 Em `convert.unconvert`, manter a matriz de mundo corrente e devolver só `orig_parent` (decisão questions.md#pergunta-27)
- [ ] DT-03 Confirmar com teste de fumaça o `bound_box` de Empty no 5.2 e fazer `apply.local_box` usar a união das malhas (`group.object_corners`) quando o pai é Empty/grupo (decisão questions.md#pergunta-28)
- [ ] DT-04 Em `collision._excluded`, quando `module_root_of(pai)` é None, excluir só o pai e a própria folha, não a subárvore do pai (decisão questions.md#pergunta-29)
- [ ] DT-05 Ao mudar `swing_sign`/`max_angle`/`travel` com a folha aberta, fechar (fração 0) e reabrir pela varredura (decisão questions.md#pergunta-30)
- [ ] DT-06 Medir uma vez numa cena típica a varredura, `measure_free_travel` e o recorte por movimento do arraste; acima de ~30 ms por movimento, recortar só ao soltar (decisão questions.md#pergunta-80)
- [ ] DT-07 Corrigir a docstring de `window_props.py` (`frame_matrix`): Desinstalar solta a esquadria no lugar, sem pai (decisão questions.md#pergunta-79)

- [ ] DT-90 No laço de agregados de `cutting/part_sources.geometry_records`, pular objetos com `btm_geometry.is_geometry` para a geometria livre convertida em agregado sair uma vez só (como geometria) e o uid não duplicar (decisão questions.md#pergunta-67; revisão cruzada, numeração 90+ para não colidir com as DT da unit)
