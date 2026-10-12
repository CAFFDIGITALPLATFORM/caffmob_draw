# Porta e Janela Reais e Região na Parede (openings) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/openings/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `data/i18n.py` com `tr(msgid)` e `N_(msgid)`; `data/units.py` com `unit_to_string(unit_settings, value)`, reexportada por `caffmob_draw/units.py` (de onde `region.py` importa) _(Revisão 2026-10-10: region.py:24)_; chaves em `data/translations/openings.json`.
- [ ] 🟢 `hb_types.GeoNodeObject`, `GeoNodeCage`, `GeoNodeWall` com `get_input`/`set_input`.
- [ ] 🟢 `aggregates/group.create_group`, `aggregates/leaf.make_leaf`, `aggregates/apply._write`, `aggregates/collision.OPENING_FRAME_PROP` e o PropertyGroup `btm_aggregate` registrados (feature 003/007).
- [ ] 🟢 `inspection/room_door_leaf.remove_leaves`; `hb_placement.PlacementMixin`, `draw_header_text`, `clear_header_text`; `hb_snap.snap_value_to_grid`; `scene.home_builder.show_entry_door_and_window_cages`.
- [ ] 🟢 `operators/doors_windows.py` criando a caixa (`GeoNodeCage` com `IS_ENTRY_DOOR_BP`/`IS_WINDOW_BP` e o símbolo `GeoNodeDoorSwing` filho com `IS_2D_ANNOTATION`), o corte e `_sync_opening` (contratos em `design.md` › Superfície usada pelos consumidores).
- [ ] 🟢 `ui/view_mode.py` com `register`/`unregister` (registrado por este pacote).

## Tarefas

- [ ] T-01, Criar `door_core.py` puro: papéis, materiais, constantes, `Part` (`size_xyz`, `lo`, `hi`), `hole_size`, `leaf_size` (RN-01, RN-02)
  - Origem no legado: `caffmob_draw/openings/door_core.py:Part/hole_size/leaf_size`
  - Critério de pronto: CA-01; importa sem `bpy`; ida e volta furo ↔ folha exata a 6 casas (EC-01)
  - Confiança: 🟢

- [ ] T-02, Implementar `_Builder` (`box`, `cyl`, `screw_y`), `_leaf`, `_frame` e `door_parts` com a conversão para a caixa (F-01, RN-03, RN-04)
  - Origem no legado: `caffmob_draw/openings/door_core.py:_Builder/_leaf/_frame/door_parts`
  - Critério de pronto: CA-02; tabelas de `design.md` reproduzidas (143/256/15 peças para 0,80 × 2,10 × 0,15); dobradiças a 0,25 m e maçaneta a 1,02 m absolutas
  - Confiança: 🟢

- [ ] T-03, Criar `window_core.py` puro: constantes, `_box`, `travel`, `window_parts` (RN-07, RN-08)
  - Origem no legado: `caffmob_draw/openings/window_core.py`
  - Critério de pronto: CA-03; 25 peças; `travel(1.2) == 0.535`; guarnições só na face y = `wall`
  - Confiança: 🟢

- [ ] T-04, Criar `region_core.py` puro: `Fit`, motivos, `MIN_SIZE`, `TOLERANCE`, `REASONS` (com `N_`), `_refuse`, `fit` (F-02, RN-18)
  - Origem no legado: `caffmob_draw/openings/region_core.py`
  - Critério de pronto: CA-13, CA-14; tolerâncias de EC-08 e EC-09 reproduzidas (inclusive aceitar `x0` em (−5 mm, 0) sem prender)
  - Confiança: 🟢

- [ ] T-05, Criar `materials.py`: `TAG`, `ASSETS`, `SPECS`, `_image`, `_wood_textures`, `get` com reaproveitamento por marca (F-03, RN-15); copiar `assets/nogueira_cor.jpg` e `nogueira_rugosidade.jpg`
  - Origem no legado: `caffmob_draw/openings/materials.py`
  - Critério de pronto: duas chamadas `get('WOOD')` devolvem o mesmo material; vidro com `surface_render_method == 'BLENDED'` e `diffuse_color` alpha 0,25; sem as imagens não levanta (EC-19)
  - Confiança: 🟢

- [ ] T-06, Criar `build.py`: `BEVEL`, `_AXIS`, `group_key`, `group_name`, `_add_part` (bmesh, slots, UV de caixa com `offset` pelo nome), `build` com "Chanfro" e "Normais ponderadas" (F-04, RN-14)
  - Origem no legado: `caffmob_draw/openings/build.py`
  - Critério de pronto: porta simples → 4 objetos ("Marco", "Ferragens do marco", "Folha 1", "Ferragens da folha 1"); janela → 3; puxador e vidro da janela na malha da folha; objetos sem pai, ligados à coleção; chanfro único por malha (EC-12)
  - Confiança: 🟢

- [ ] T-07, Criar `props.py`: `KIND_ITEMS`, `MODEL_VERSION = 1`, `BTM_PG_Opening` (`kind`, `signature`, `model_version`, `assembly`), `Object.btm_opening_real` com `register`/`unregister` simétricos
  - Origem no legado: `caffmob_draw/openings/props.py`
  - Critério de pronto: arquivo antigo lê `kind == 'NONE'`, `model_version == 0`, `assembly is None`; `unregister` remove a propriedade
  - Confiança: 🟢

- [ ] T-08, Criar `sync.py` (consulta): `DOOR_FLAG`, `WINDOW_FLAG`, `SWING_MAX`, `is_opening`, `_swing`, `kind_of`, `_dims`, `signature`, `_parts`, `openings`, `outdated` (RN-05, RN-06, RN-09, RN-16)
  - Origem no legado: `caffmob_draw/openings/sync.py:is_opening/_swing/kind_of/signature/_parts/openings/outdated`
  - Critério de pronto: `kind_of` prefere o `kind` gravado ao símbolo; `_swing` usa o primeiro filho anotado e os padrões `True, True, False` na falha (EC-02, EC-03); formato da assinatura com 5 casas
  - Confiança: 🟢

- [ ] T-09, Implementar a montagem: `_remember`, `clear`, `_to_world`, `_parent_keep`, `_align`, `_style_cage` e `sync` (F-05, F-05b, RN-10 a RN-13)
  - Origem no legado: `caffmob_draw/openings/sync.py:sync`
  - Critério de pronto: CA-04 a CA-07; hierarquia caixa → FRAME → pivô → LEAF → malha → ferragens; `btm_opening_frame` nas malhas do marco; segunda chamada sem mudança devolve False; abertura e produção restauradas; folha cinza da 005 removida
  - Confiança: 🟢

- [ ] T-10, Criar `ops.py`: `caffmob.openings_update`, `door_of`, `btm.door_invert_hand` e o item de keymap I (head) em "Object Mode" (F-06, RN-16, RN-17)
  - Origem no legado: `caffmob_draw/openings/ops.py`
  - Critério de pronto: CA-08, CA-09, CA-10; `unregister` remove o item de keymap engolindo `ReferenceError`/`RuntimeError`
  - Confiança: 🟢

- [ ] T-11, Criar `region_props.py`: `SIDE_ITEMS`, `BTM_PG_WallRegion`, `WindowManager.btm_wall_region`, `region_wall`, `clear` (RN-20)
  - Origem no legado: `caffmob_draw/openings/region_props.py`
  - Critério de pronto: parede apagada ou sem `IS_WALL_BP` desativa a região e devolve `(None, None)`; `clear` sem a propriedade não levanta
  - Confiança: 🟢

- [ ] T-12, Criar `region.py`: `_live`, cores, `_face_y`, `_rect_world`, `_draw_rect`, `draw_regions`, `_tag_redraw`, `BTM_OT_WallRegion` (modal F-07, RN-19), `BTM_OT_WallRegionClear`, `on_load_post` (`@persistent`), `register`/`unregister` com o desenho `POST_PIXEL`, o `load_post` e o Esc em "3D View" (F-08)
  - Origem no legado: `caffmob_draw/openings/region.py`
  - Critério de pronto: CA-11, CA-12; um único `draw_handler_add` removido no `unregister`; `invoke` descarta a região anterior (EC-14); só botão do meio e roda passam (EC-17)
  - Confiança: 🟢

- [ ] T-13, Criar `__init__.py`: `_modules()` com imports tardios na ordem `props`, `ops`, `ui.view_mode`, `region_props`, `region`; `register` na ordem e `unregister` na inversa
  - Origem no legado: `caffmob_draw/openings/__init__.py`
  - Critério de pronto: `caffmob_draw/__init__.py` chama `openings.register()`/`unregister()`; registrar e desregistrar duas vezes sem erro
  - Confiança: 🟢

- [ ] T-14, Ligar os consumidores: `doors_windows` (`_sync_opening`, `_leaf_to_hole`/`_hole_to_leaf`, `create_placed_object` gravando `kind`, `place_in_region`/`modal_in_region`), `walls2d/apply.apply_plan`, `selection/element_size` e `resize`, `ui/sidebar_build` (aviso, "Marcar região", campos), `hb_props.update_show_entry_door_and_window_cages`, `room_door_leaf.has_real_door`, `aggregates/collision`
  - Origem no legado: `caffmob_draw/operators/doors_windows.py`, `walls2d/apply.py`, `selection/element_size.py`, `selection/resize.py`, `ui/sidebar_build.py`, `hb_props.py`, `inspection/room_door_leaf.py`, `aggregates/collision.py`
  - Critério de pronto: inserção, diálogo, Redimensionar e OK do Editor de Paredes refazem a porta real; região confirmada some e cancelada fica; aviso de "em caixa" aparece com caixas antigas
  - Confiança: 🟢

- [ ] T-15, Textos: chaves de `tr`/`N_` da unit em `data/translations/openings.json` (`pt_BR`, `en_US`)
  - Origem no legado: `caffmob_draw/data/translations/openings.json`
  - Critério de pronto: as 11 mensagens da unit têm chave (verificado: todas presentes em 2026-10-10)
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Porta: furo pela folha, folha a 8 mm do piso, marco com a parede, guarnições dos dois lados, ferragens, largura maior não distorce, lado e sentido, dupla e vão aberto, papéis — `tests/test_door_core.py` (9 testes) 🟢
- [ ] TT-02, Janela: marco no furo, folhas sobrepostas com vidro, trilhos diferentes, peitoril/trilhos/puxadores, tamanho maior — `tests/test_window_core.py` (5 testes) 🟢
- [ ] TT-03, Região: porta exata do piso, porta com região acima do piso, janela com peitoril, cantos invertidos, clique abaixo do piso, recusas, vizinha que só encosta — `tests/test_wall_region_core.py` (7 testes) 🟢
- [ ] TT-04, Casos puros ainda sem teste: tolerância em `x0`/`x1`/`z1` sem prender (EC-09), porta acima de janela recusada (EC-08), `kind` desconhecido como porta — 🟢 sem teste dedicado; reexecutados _(Revisão 2026-10-10: fit(-0.004,1,…) → x −0,004; z1 2,704 → altura 2,704; porta 0–1 × 1,5–2,0 sobre janela 0,2–0,8 × 0,1–1,0 → OVERLAP (janela aceita); kind 'XYZ' → sill 0; tests/test_wall_region_core.py não cobre)_
- [ ] TT-05, Blender: montagem, assinatura, preservação, Atualizar — `tests/blender_010_openings_smoke.py`; porta real abre — `tests/blender_bug_porta_real_abre.py`; aberturas no Editor de Paredes — `tests/blender_bug_YIMY_openings.py` 🟢 (existem; não executados nesta extração)
- [ ] TT-06, Blender: porta e janela na região, recusa, Esc mantém, confirmar limpa — `tests/blender_011_region_smoke.py`; tecla I — `tests/blender_toast_resize_invert.py` 🟢 (existem; não executados)
- [ ] TT-07, `materials.py`, `build.py` (contagem de malhas, chanfro), EC-02, EC-04, EC-07, EC-10 — 🔴 sem teste identificado

Comando dos testes puros 🟢: `cd tests && python3 -m unittest test_door_core test_window_core test_wall_region_core -v` (21 testes, aprovados em 2026-10-10; o `_bootstrap` dos testes exige rodar de dentro de `tests/` ou com `PYTHONPATH=tests`). Testes Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_openings_smoke.py` (idem para `blender_011_region_smoke.py`).

## Tarefas de Migração de Dados

- 🟢 Arquivos anteriores à 010 têm caixas com `kind == 'NONE'` e sem montagem: não há migração automática; `caffmob.openings_update` (RN-16) monta a porta real sob comando. Subir `MODEL_VERSION` marca todas as caixas como desatualizadas para o mesmo botão.
- 🟢 `btm_wall_region` é de sessão: nada a migrar.

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03 → T-04: núcleo puro (TT-01 a TT-04).
2. 🟢 T-05 → T-06 → T-07 → T-08 → T-09: montagem no Blender (TT-05).
3. 🟢 T-10 → T-11 → T-12 → T-13: operadores, região e registro (TT-06).
4. 🟢 T-14 → T-15: consumidores e textos.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-22):** a abertura segue a face marcada (`side`), como pede 011 RN-11 (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-23):** `_swing` restrito ao símbolo de giro (`has_input('Swing Inside')`) (EC-02). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-24):** trocar simples ↔ dupla refaz a porta real e atualiza `kind` (EC-04). Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-25):** tirar a escrita de `region.active` do callback de desenho (EC-10). Pendência de implementação: DT-04.
- 🟡 Medir o custo de `sync` (bmesh + `view_layer.update()`) em projetos com muitas portas — decisão: medir/testar (DT-06; questions.md#pergunta-78).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-26):** `clear` preserva objetos do usuário pendurados na montagem (EC-05). Pendência de implementação: DT-05.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `doors_windows.place_in_region`, com região de `side = BACK`, gravar `Swing Inside` = falso no símbolo (ou girar a caixa 180°) ao inserir, sem mexer no corte (decisão questions.md#pergunta-22)
- [ ] DT-02 Em `sync._swing`, escolher só o filho com `has_input('Swing Inside')` (ou nome 'Door Swing'), como `room_door_leaf.swing_of` (decisão questions.md#pergunta-23)
- [ ] DT-03 Em `toggle_double_door`, atualizar `btm_opening_real.kind` e chamar `_sync_opening`; incluir o kind efetivo (`Is Double`) na assinatura de `sync` (decisão questions.md#pergunta-24)
- [ ] DT-04 Tirar a escrita `region.active = False` de `draw_regions`: no desenho só ignorar a região inválida; invalidar em `region_wall` chamado por operadores ou num `depsgraph_update_post` (decisão questions.md#pergunta-25)
- [ ] DT-05 Em `sync.clear`, apagar só objetos criados pela montagem (com marca própria, ex. `btm_opening_frame`) e reparentar os demais para a caixa mantendo a matriz de mundo (decisão questions.md#pergunta-26)
- [ ] DT-06 Medir `sync` com 30 portas (Atualizar portas e janelas / OK do Editor de Paredes); abaixo de 1 s no total, não definir meta (decisão questions.md#pergunta-78)
