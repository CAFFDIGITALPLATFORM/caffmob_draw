# Grudar em Superfície (stick) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/stick/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `aggregates/limits.py` com `FACES`, `FACE_LABELS`, `face_axes`, `thickness` (contrato em `_reversa_sdd/aggregates/`).
- [ ] 🟢 `selection/classify` (`classify`, `movable_root`, constantes `MODULE`, `GEOMETRY`, `WALL`, `FLOOR`, `CEILING`, `OTHER`, `ANNOTATION`; contrato em `_reversa_sdd/selection/`).
- [ ] 🟢 `Object.btm_aggregate.is_aggregate` registrado (unit `aggregates`); `hb_types.GeoNodeWall.get_input('Thickness')`; `hb_placement.PlacementMixin`.
- [ ] 🟢 `ui/save_feedback.show`; `ui/sidebar_proxy.draw_panel` e o grupo "Posição e vínculo" da barra lateral única (`_reversa_sdd/ui/`).
- [ ] 🟢 `data/i18n.tr` e `data/translations/editor_grudar.json` (pt_BR, en_US); duas mensagens vêm de `move_over.json`/`sidebar.json`. _(Revisão 2026-10-10: ver T-15)_
- [ ] 🟢 Preferências `stick_magnet`/`stick_magnet_distance` em `BTM_AddonPreferences` e `Scene.btm_settings.stick_migrated`.

## Tarefas

- [ ] T-01, Criar `frame.py` puro: constantes, álgebra em tuplas, `box_frame`, `plane_frame`, `frame_to_matrix`/`matrix_to_frame`, `frame_for`, `to_frame`/`from_frame`, `footprint`, `params`, `shift`, `face_extent`, `out_of_face`, `is_planar`, `choose_face`, `contact_axis` (RN-01 a RN-03, RN-06, RN-08, RN-13)
  - Origem no legado: `caffmob_draw/stick/frame.py`
  - Critério de pronto: CA-01, CA-02, CA-03; os 8 testes de `tests/test_stick_frame.py` passam; 1,0°/1,1°, 0,5/0,6 mm, 0,69/0,70 e 1,0/1,1 mm reproduzem os resultados executados; nenhum import de `bpy`
  - Confiança: 🟢

- [ ] T-02, Criar `props.py`: `_guard`, `FACE_ITEMS`, `KIND_ITEMS`, `IDENTITY`, `_guarded` (import tardio de `apply`), `BTM_PG_Stick` com os 13 campos e `Object.btm_stick` (RN-25)
  - Origem no legado: `caffmob_draw/stick/props.py`
  - Critério de pronto: nomes, padrões, `subtype`/`unit` e `update` da tabela de `design.md`; `unregister` remove o ponteiro antes da classe; vínculo sobrevive a salvar/reabrir (CA-07)
  - Confiança: 🟢

- [ ] T-03, Criar em `apply.py` as caixas e a posição: `local_box`, `_own_corners`, `_corners` (filhos sem cortadores/anotações/`obj_x`), `item_corners`, `host_box`, `face_of`, `write`, `_store_world`, `_translate_local`, `linked`, `update_position`, `_check_face`, `_warn` (F-03; RN-08, RN-13)
  - Origem no legado: `caffmob_draw/stick/apply.py`
  - Critério de pronto: CA-12, CA-17, CA-21; `write` não dispara `update`; aviso "Item fora da face" só na transição; `last_world` gravado a cada aplicação
  - Confiança: 🟢

- [ ] T-04, Criar `project`, `_OPPOSITE`, `_flip_if_across`, `update_spin`, `lose_link` (F-04 a F-06, F-08; RN-10, RN-12, RN-14)
  - Origem no legado: `caffmob_draw/stick/apply.py`
  - Critério de pronto: CA-09, CA-10, CA-14; `lose_link` só restaura `last_world` se o item ficou sem pai e a matriz não é identidade; `spin` gira pelo centro da pegada no plano de contato
  - Confiança: 🟢

- [ ] T-05, Criar o índice (`_index`, `_index_ok`, `invalidate`, `index`, `stuck_items`), o handler `@persistent on_depsgraph_update`, `modal_running`, `_settle_timer`, `on_load_or_undo` e `register`/`unregister` dos 4 handlers (F-09, F-10; RN-11, RN-16)
  - Origem no legado: `caffmob_draw/stick/apply.py`
  - Critério de pronto: CA-08, CA-11; reentrância bloqueada por `_busy`; registrar duas vezes não duplica; `unregister` cancela o temporizador e limpa o estado; comportamento de EC-01/EC-03 reproduzido ou corrigido conforme decisão
  - Confiança: 🟢

- [ ] T-06, Criar `link.py`: `UP`, `host_for`, `can_stick`, `_to_host`, `oriented_matrix`, `orient`, `_attach`, `_record`, `stick`, `link_in_place`, `release`, `face_label` (F-02, F-07, F-12; RN-04 a RN-09, RN-15, RN-21, RN-22)
  - Origem no legado: `caffmob_draw/stick/link.py`
  - Critério de pronto: CA-04, CA-05, CA-15, CA-16; `orig_parent` gravado só no primeiro grudar; `link_in_place` não move; rótulos "frente"/"trás"/"plano"/`FACE_LABELS`; verificação de descendente em `release` comparando objetos (corrigir EC-09) ou mantida conforme decisão
  - Confiança: 🟢

- [ ] T-07, Criar `migrate.py` (`wall_of`, `wall_side`, `run`) e chamá-lo em `caffmob_draw/__init__.py:load_file_post` (RN-20; 004 D-08)
  - Origem no legado: `caffmob_draw/stick/migrate.py`; `caffmob_draw/__init__.py:load_file_post`
  - Critério de pronto: CA-24; idempotente (segunda chamada devolve 0); regra igual a `measure/scene_cotas._on_front_side`; EC-05 documentado
  - Confiança: 🟢

- [ ] T-08, Criar `magnet.py`: `DEFAULT_DISTANCE`, `_MAX_STEPS`, `_FACING`, `preferences`, `_back`, `find`, `_polygon`, `preview_pose`, `try_stick` (F-13, F-14; RN-19)
  - Origem no legado: `caffmob_draw/stick/magnet.py`
  - Critério de pronto: CA-22, CA-23; sem preferências devolve `(True, 0.05)`; `preview_pose` não altera o objeto e usa a mesma orientação de `link.oriented_matrix`
  - Confiança: 🟢

- [ ] T-09, Criar `settle.py`: `_MOVE_IDS`, `_MAGNET_KINDS`, `_idname`, `is_move_operator`, `_undo_push`, `_settled`, `_world_key`, `returned_to_rest`, `run`, `_check_collisions` (F-11; RN-16 a RN-18)
  - Origem no legado: `caffmob_draw/stick/settle.py`
  - Critério de pronto: CA-11, CA-18, CA-22, CA-25; ordem por objeto de RN-18; um único passo de desfazer "Grudar" por lote; `ImportError` de `collision` silencioso
  - Confiança: 🟢

- [ ] T-10, Criar `ops_stick.py`: `_STICK_FIELDS`, `item_of`, `_ray`, `scene_hit`, `snapshot`, `restore` e os operadores `caffmob.stick_to_face`, `caffmob.stick_release`, `caffmob.stick_move` (F-01, F-15; RN-23)
  - Origem no legado: `caffmob_draw/stick/ops_stick.py`
  - Critério de pronto: CA-05, CA-06, CA-19, CA-20; `bl_options` da tabela; barra de status limpa em toda saída; Esc restaura os 13 campos; navegação (`MIDDLEMOUSE`, roda) passa adiante
  - Confiança: 🟢

- [ ] T-11, Criar `panels.py` (`BTM_PT_Stick`, `classes = ()`) e ligá-lo em `ui/object_properties._position_group`; ligar `STICK`/`RELEASE`/`STICK_MOVE` em `ui/sidebar_vocab.py` e `ui/context_menu.item_actions` (RF-08; RN-22)
  - Origem no legado: `caffmob_draw/stick/panels.py`; `caffmob_draw/ui/object_properties.py`; `caffmob_draw/ui/sidebar_vocab.py`; `caffmob_draw/ui/context_menu.py`
  - Critério de pronto: CA-16; estado sempre em texto; lista "Elementos filhos" ordenada por nome; `tests/blender_005_sidebar_inventory.py` continua passando
  - Confiança: 🟢

- [ ] T-12, Criar `magnet_preview.py` (cores, `_EDGES`, `_moving_item`, `compute`, `_draw_3d`, `_draw_2d`, `register`/`unregister` dos 2 `draw_handler`) (F-16; RN-24)
  - Origem no legado: `caffmob_draw/stick/magnet_preview.py`
  - Critério de pronto: CA-26; nada no objeto muda; `draw_handler_remove` dos dois handles no `unregister`; `python3 docs/rag/tools/check_api.py` sem `[UNKNOWN in 5.2]`
  - Confiança: 🟢 (código) / 🟡 (validação visual)

- [ ] T-13, Criar `__init__.py` com `_modules()` de import tardio e ordem `(props, apply, ops_stick, panels, magnet_preview)` / inversa; incluir `"stick"` em `_submodule_names` e as chamadas em `caffmob_draw/__init__.py`
  - Origem no legado: `caffmob_draw/stick/__init__.py`; `caffmob_draw/__init__.py`
  - Critério de pronto: `import caffmob_draw.stick.frame` funciona fora do Blender; registrar/desregistrar duas vezes não duplica handlers nem `draw_handler`
  - Confiança: 🟢

- [ ] T-14, Ligar os consumidores externos: `collision/scan.box_of` e `_links`, `collision/ops_collision` ("Afastar" no plano), `cabinet_editor/bridge.root_box`, `aggregates/ops_aggregate` (`_stuck_children`, `_release_stuck_children`), `aggregates/convert.can_convert`, `selection/component._is_stuck` (RF-09, RF-10; RN-26)
  - Origem no legado: arquivos citados em `design.md` › Consumidores
  - Critério de pronto: CA-13, CA-17, CA-18; `collision` CA-22; `aggregates` RN-05 e RN-29; `selection` CA-07
  - Confiança: 🟢

- [ ] T-15, Textos: as 19 mensagens de `tr(...)` da unit com chave no catálogo (17 em `data/translations/editor_grudar.json`; "Nenhuma face sob o cursor" em `move_over.json`; "Grudar em: {}" em `sidebar.json`) _(Revisão 2026-10-10: cruzamento por script; os 6 rótulos de `limits.FACE_LABELS` não têm entrada em catálogo algum)_
  - Origem no legado: `caffmob_draw/data/translations/editor_grudar.json`
  - Critério de pronto: todas encontradas (verificado por script em 2026-10-10); rótulos de `FACE_LABELS` traduzíveis
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Núcleo puro: seis faces, aéreo de trás com parede mais grossa, dez mudanças sem erro, frente = `NEG_Y`, plano inclinado, fora da face, face plana, escolha da face — `tests/test_stick_frame.py` (8 testes, aprovados em 2026-10-10) 🟢
- [ ] TT-02, Casos puros sem teste: limites exatos de `choose_face` (1°, 0,5 mm), de `contact_axis` (0,7) e de `out_of_face` (1 mm); `plane_frame` com normal Z; normal nula em `choose_face` e `plane_frame` (EC-19) — 🟢 executados manualmente nesta extração _(Revisão 2026-10-10: reexecutados em Python puro: 1,0°→BOX_SIDE, 1,1°→PLANE, 0,5/0,6 mm, 0,69→BACK, 0,70→BOTTOM, 1,0/1,1 mm, normal nula → PLANE e `ValueError("vetor nulo")`; continuam sem teste automatizado)_
- [ ] TT-03, Blender: migração frente/trás e idempotência, espessura 150→200 mm e cinco mudanças, troca de face, grudar no painel e girar, projeção após G, ímã desligado/20 mm/50 mm, fora da face, apagar pelo operador e direto, desgrudar, salvar e reabrir — `tests/blender_004_stick_smoke.py` 🟢 (existe; não executado, Blender ausente) _(Revisão 2026-10-10: executado no Blender 5.2.0 LTS → OK)_
- [ ] TT-04, Blender (005): prévia do ímã aparece, some ao cancelar sem grudar, não aparece com ímã desligado ou longe — `tests/blender_005_viewport_smoke.py` 🟢 (existe; não executado) _(Revisão 2026-10-10: executado com `xvfb-run` no Blender 5.2.0 LTS → 11 checagens OK)_
- [ ] TT-05, Sem teste identificado: pai trocado (EC-02), hospedeiro renomeado (EC-03), desgrudar módulo da parede (EC-04), `wall_side` sem espessura (EC-05), face interna → `PLANE` (EC-06), hospedeiro escalado (EC-07), giro livre do grudado (EC-08), `stick_move` com Ctrl, `spin` pelo painel, `stick_to_face` com face não plana via operador (CA-05), apagar hospedeiro sem `invalidate()` (EC-01) — 🟡 (EC-01 a EC-04, EC-07 e EC-08 decididos pelo titular em 2026-10-10; testes junto de DT-01 a DT-05)

Comando dos testes puros 🟢: `cd tests && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest test_stick_frame -v` (o `_bootstrap` exige rodar de dentro de `tests/` ou com `PYTHONPATH=tests`). Fumaça: `blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_stick_smoke.py`.

## Tarefas de Migração de Dados

- [ ] 🟢 Arquivos antigos: `migrate.run` ao abrir dá vínculo aos módulos raiz filhos de parede (T-07). Não há versão de esquema de `btm_stick`; campos novos precisariam de padrão compatível.
- 🟡 `stick_migrated` não é lido: decidir se deve encerrar a varredura nas aberturas seguintes ou ser removido.

## Ordem Sugerida

1. 🟢 T-01 (TT-01, TT-02): núcleo puro, sem Blender.
2. 🟢 T-02 → T-03 → T-04 → T-05: dados, posição, manutenção, handler e temporizador.
3. 🟢 T-06 → T-07 → T-08 → T-09: grudar/desgrudar, migração, ímã, assentar (TT-03).
4. 🟢 T-10 → T-11 → T-12 → T-13: operadores, painel, prévia, registro (TT-04).
5. 🟢 T-14 → T-15: consumidores e textos.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-36):** trocar o pai fora do plugin perde o vínculo com aviso (EC-02). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-37):** invalidar o índice quando objetos com `btm_stick` são apagados ou renomeados fora do plugin (EC-01, EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-38):** "Desgrudar" um módulo da parede é durável por marca própria (EC-04); consultar `stick_migrated` não basta. Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-39):** Grudar não aceita parede, piso, teto nem não-itens: poll e painel seguem `_ITEM_KINDS` (EC-18). Pendência de implementação: DT-04.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-82):** `project` restaura orientação/`spin` (004 D-04b; EC-08; DT-05); hospedeiro com escala ≠ 1 fica como aviso documentado (EC-07).
- 🔴 Executar `blender_004_stick_smoke.py` e `blender_005_viewport_smoke.py` no Blender 5.2 e validar visualmente a prévia do ímã. _(Revisão 2026-10-10: as duas fumaças passaram no 5.2.0 LTS; resta só a validação visual da prévia)_

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `apply.on_depsgraph_update`, tratar `is_stuck` com `host` presente e `item.parent != host` como vínculo perdido (`lose_link`, aviso "Vínculo perdido") (decisão questions.md#pergunta-36)
- [ ] DT-02 Em `apply.on_depsgraph_update`, invalidar o índice quando algum update traz objeto com `btm_stick` (hospedeiro apagado ou renomeado), ou guardar o hospedeiro por `PointerProperty` em vez do nome (decisão questions.md#pergunta-37)
- [ ] DT-03 Gravar uma marca (ex. `btm_stick.opt_out`) no `link.release` de item cujo `orig_parent` é parede e respeitá-la em `settle.run` e `migrate.run` (decisão questions.md#pergunta-38)
- [ ] DT-04 Alinhar `BTM_OT_StickToFace.poll` e `panels.poll` ao filtro `_ITEM_KINDS` do menu de contexto (`MODULE`, `FRONT`, `PART`, `GEOMETRY`, `OBSTACLE` e malha `OTHER`) (decisão questions.md#pergunta-39)
- [ ] DT-05 Em `apply.project`, restaurar a orientação do item em relação à face (reaplicar `oriented_matrix` + `spin`) depois de um giro livre (decisão questions.md#pergunta-82)
