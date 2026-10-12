# Mover Sobre — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/move_over/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 Unit `canvas2d` pronta (`View2D.to_screen/fit`, `distance_point_segment`, `draw.begin/end/rect/outline/lines/dashed/text/button/box/length_label`, `COLORS` com `panel, pane, border, muted, reference, moving, target, target_hot, warning`), conforme `_reversa_sdd/canvas2d/design.md`.
- [ ] 🟢 `selection/classify.py` com `movable_root`, `reference_root`, `classify` (kind `WALL`) e `module_library`.
- [ ] 🟢 `aggregates/group.py:object_corners(obj, depsgraph)`.
- [ ] 🟢 `measure/scene_cotas.py:for_object`, `measure/cotas.py:slide`, `hb_placement.PlacementMixin.avoid_overlap`.
- [ ] 🟢 `customize/library_io.py:list_modules/load`; `data/units.py:parse_length/get_scene_length_unit/format_length`; `data/i18n.py:tr/N_`; `hb_gpu_draw.point_in_rect`.
- [ ] 🟢 `Scene.btm_settings.collision_global` (`data/properties.py`) para o aviso de sobreposição (opcional: ausente, não verifica).

## Tarefas

- [ ] T-01, Criar `align.py` puro: `FRACTIONS`, `DEFAULT_TOLERANCE_PX = 12.0`, `Target`, constantes de tipo, `size`, `translate`, `delta_for` (RN-04, `ValueError` em tipo desconhecido), `combine` (RN-08)
  - Origem no legado: `caffmob_draw/move_over/align.py:delta_for/combine`
  - Critério de pronto: CA-04 (parte de cálculo); `combine` com dois alvos no mesmo eixo devolve o último não nulo; o módulo importa sem `bpy`
  - Confiança: 🟢

- [ ] T-02, Implementar `top_view_lines` (com `wall` só lados + `WALL_FACE`), `front_view_lines`, `pick` (F-01, um alvo por eixo, tolerância inclusiva, import tardio de `canvas2d.view`), `pick_stack` (RN-07), `gaps` (RN-09), `overlaps` (estrito, `tolerance=1e-4`)
  - Origem no legado: `caffmob_draw/move_over/align.py:top_view_lines/front_view_lines/pick/pick_stack/gaps/overlaps`
  - Critério de pronto: CA-04 e CA-05; com B parede a Superior tem exatamente 3 alvos; `gaps` negativo quando sobrepostos em X
  - Confiança: 🟢

- [ ] T-03, Criar `reposition.py` puro: `box_center_base`, `rotate_point_z`, `origin_after_rotation`, `rotated_box`, `step_delta`, `absolute_values`, `side_of` (empate → `RIGHT`), `save_position`, `apply_position` (RN-03, RN-12, RN-13)
  - Origem no legado: `caffmob_draw/move_over/reposition.py`
  - Critério de pronto: CA-08 (cálculo) e CA-11; girar 90° não move o centro da base; tecla fora da tabela → `None`
  - Confiança: 🟢

- [ ] T-04, Criar `props.py` com os 3 PropertyGroups, ponteiros em `WindowManager`/`Scene`, `_redraw` e `unregister` que remove tudo (tabela em `design.md` › `props.py`)
  - Origem no legado: `caffmob_draw/move_over/props.py`
  - Critério de pronto: após `register`/`unregister`, `bpy.types.WindowManager` e `bpy.types.Scene` não têm mais `btm_move_over`, `btm_insertion_plane`, `btm_saved_positions(_index)`; faixas e padrões iguais (12/4–40; 0,01/0,0001–1; `show_relative=True`)
  - Confiança: 🟢

- [ ] T-05, Implementar `scene.py`: `_frame`, `_local_box`, `_wall_of`, `MoveOver.__init__` (F-02), caixas (`_unrotated_box`, `box_a`, `original_box_a`), `_target_matrix` (F-03), `preview`/`restore` (RN-14), `align_to`, `set_gap` (F-04), `gaps`, `set_rotation`, `nudge`, `world_min`, `set_world`, `saved`, `apply_saved`, `overlapping` (F-05)
  - Origem no legado: `caffmob_draw/move_over/scene.py:MoveOver`
  - Critério de pronto: CA-06 (cálculo), CA-10; X digitado com A à direita dá a folga exata; rotação 90° mantém o centro da base no mundo; `restore` devolve a matriz original com tolerância 1e-4 (`tests/blender_003_move_over_smoke.py` §1)
  - Confiança: 🟢

- [ ] T-06, Implementar `caffmob.move_over_toggle` e `caffmob.move_over_drag` (F do passo 2 de `design.md`), com `raycast`, `mode_enabled`, `DRAG_THRESHOLD_PX = 5`, desenho tracejado e keymaps em "3D View" + 19 `VIEW3D_MODE_KEYMAPS` (`head=True`) com remoção protegida (RN-17, RN-18)
  - Origem no legado: `caffmob_draw/move_over/ops_drag.py`
  - Critério de pronto: CA-01, CA-02, CA-03; em Modo Objeto **e** em Edição o botão direito com o modo ligado inicia o arraste (`tests/blender_002_ui_events.py`)
  - Confiança: 🟢

- [ ] T-07, Implementar `caffmob.move_over_dialog`: `invoke` (passo 3), `_layout` (passo 4, × `ui_scale`), `_fit_views` (margem 0,15), `_lines_px`/`_top_lines`/`_front_lines`/`_front_top_line_px`/`_hits`, `_draw`/`_draw_pane` (passo 6), `_finish`, `cancel`
  - Origem no legado: `caffmob_draw/move_over/ops_dialog.py:invoke/_layout/_fit_views/_hits/_draw/_draw_pane/_finish/cancel`
  - Critério de pronto: CA-04 na interface; só A e B aparecem; B vira o ativo; o handler é removido em todas as saídas
  - Confiança: 🟢

- [ ] T-08, Implementar o `modal` da janela na ordem de F-06, `_apply_click`, `_commit_typing` (RN-11), `_save_position`, `_apply_saved`, `_saved_items` (4 últimos), `_confirm` (F-07, RN-15), `_substitute`
  - Origem no legado: `caffmob_draw/move_over/ops_dialog.py:modal/_apply_click/_commit_typing/_save_position/_apply_saved/_confirm/_substitute`
  - Critério de pronto: CA-06 a CA-11; navegação fora do painel passa; com campo em edição, cliques são ignorados (EC-05); Relativa/Absoluta não move A
  - Confiança: 🟢

- [ ] T-09, Implementar `caffmob.move_over_substitute` e `substitute` (F-09, RN-19), com `_module_items` guardando `_ITEMS` global e `_tree_box`
  - Origem no legado: `caffmob_draw/move_over/ops_substitute.py`
  - Critério de pronto: CA-12; falha de carregamento remove o que foi carregado e não apaga A; `unregister` checa `is_registered`
  - Confiança: 🟢

- [ ] T-10, Implementar `caffmob.move_on_wall` (F-08, RN-20)
  - Origem no legado: `caffmob_draw/move_over/ops_move_on_wall.py`
  - Critério de pronto: CA-13; invocado pelo botão do painel lateral projeta pela região `WINDOW`; Shift não deixa `z0 < 0`; cabeçalho limpo ao sair
  - Confiança: 🟢

- [ ] T-11, Implementar `caffmob.set_insertion_plane` e `caffmob.clear_insertion_plane` (F-10, RN-21), sem `UNDO`
  - Origem no legado: `caffmob_draw/move_over/insertion_plane.py`
  - Critério de pronto: CA-14; `matrix` lida por `hb_snap.py` como linhas de 4 dá a translação no ponto clicado e a coluna Z na normal
  - Confiança: 🟢

- [ ] T-12, Criar `__init__.py` com `_modules()` de import tardio e a ordem de registro `props, ops_dialog, ops_drag, ops_move_on_wall, ops_substitute, insertion_plane` (inversa no `unregister`); registrar em `caffmob_draw/__init__.py`
  - Origem no legado: `caffmob_draw/move_over/__init__.py`; `caffmob_draw/__init__.py:293/373`
  - Critério de pronto: `from caffmob_draw.move_over import align, reposition` funciona fora do Blender; ativar e desativar o add-on duas vezes não deixa keymaps nem classes órfãs
  - Confiança: 🟢

- [ ] T-13, Integrar os consumidores: botão do HUD (`operators/viewport_hud.py:_MoveOverButton`), vocabulário (`ui/sidebar_vocab.py`: `MOVE_OVER`, `INSERTION_PLANE`, `CLEAR_INSERTION_PLANE`), menu de contexto (`ui/context_menu.py`), painel (`ui/object_properties.py`), plano no snap (`hb_snap.py`), espera do assentar (`stick/settle.py:_MOVE_IDS`)
  - Origem no legado: arquivos citados (fora da unit)
  - Critério de pronto: o modo liga pelo HUD e pelo painel; "Limpar plano de inserção" só aparece com plano ativo; o assentar não roda durante os modais de movimento
  - Confiança: 🟢

- [ ] T-14, Registrar os textos em `data/translations/move_over.json` (48 chaves, `pt_BR` e `en_US`)
  - Origem no legado: `caffmob_draw/data/translations/move_over.json`
  - Critério de pronto: todo texto passado a `tr`/`N_` na unit tem chave; interface em inglês sem texto em português
  - Confiança: 🟢 _(Revisão 2026-10-10: move_over.json tem 48 chaves com 2 idiomas; rótulos curtos (Profundidade, Altura, Cancelar, Confirmar, Módulo, Esquerda/Direita) vêm de geral.json e "Frontal" de cabinet_editor.json)_

## Tarefas de Teste

- [ ] TT-01, Alinhamento puro: lados, frações, alturas/empilhar, lado + profundidade, parede, clique e tolerância, empilhar pelo clique, folgas e sobreposição — `tests/test_move_over_align.py` (8 testes) 🟢
- [ ] TT-02, Reposicionar puro: rotação pelo centro da base, caixa girada 90°, passo, absoluta não move, posição salva em outro par, lado esquerdo — `tests/test_reposition.py` (6 testes) 🟢
- [ ] TT-03, Casos ainda sem teste puro: `combine` com dois alvos no mesmo eixo, `gaps` com sobreposição em X, empate de `side_of`, `delta_for` com tipo desconhecido (EC-01, EC-02) — 🟢 sem teste identificado _(Revisão 2026-10-10: tests/test_move_over_align.py:68 testa só gaps separados e overlaps; nenhum teste de combine no mesmo eixo, side_of empatado ou tipo desconhecido)_
- [ ] TT-04, Camada de cena e operadores: X digitado, rotação, cancelar, passo/absoluta, posição salva, Substituir, plano de inserção — `tests/blender_003_move_over_smoke.py` 🟢 (existe; não executado nesta extração)
- [ ] TT-05, Botão direito em Modo Objeto e Edição abrindo arraste e janela — `tests/blender_002_ui_events.py` 🟢 (existe; não executado)
- [ ] TT-06, Regressão: grupo `btm_group` do SketchUp como A — `tests/blender_bug_skp_mover_sobre.py` 🟢 (existe; não executado)
- [ ] TT-07, Aviso de sobreposição em duas confirmações e reset do aviso (CA-09, EC-04) — 🔴 sem teste identificado; exige janela no Blender
- [ ] TT-08, Mover na Parede com vizinho e Shift (CA-13) — 🔴 sem teste de modal identificado (`blender_002_smoke.py` só importa o módulo)
- [ ] TT-09, Tab com valor válido: hoje volta ao campo 0 em vez de ir ao próximo (ver `design.md` F-06 passo 4) — sem teste _(Revisão 2026-10-10: ops_dialog.py:316-319)_. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-15):** Tab grava e vai ao próximo campo; com falha fica no campo atual com o aviso. Pendência de implementação: DT-01

Comando dos testes puros 🟢: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_move_over_align test_reposition -v` (14 testes, aprovados em 2026-10-10). Testes Blender: `blender --background --factory-startup --python-exit-code 1 --python tests/<arquivo>.py`.

## Tarefas de Migração de Dados

- 🟢 `Scene.btm_saved_positions` é salvo no `.blend`: manter os nomes de propriedade (`name`, `delta`, `rotation`, `b_side` com itens `LEFT`/`RIGHT`) e o nome da coleção para abrir projetos existentes. Não há versão de esquema nem conversão no código.
- 🟢 `btm_move_over` e `btm_insertion_plane` são de sessão: sem migração.

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03: núcleo puro, testável sem Blender (TT-01..TT-03).
2. 🟢 T-04 → T-05: estado e camada de cena (dependem de T-01/T-03).
3. 🟢 T-06 e T-07 → T-08: a janela depende de T-05 e da unit `canvas2d`; o arraste só precisa da janela registrada para abri-la.
4. 🟢 T-09, T-10, T-11 em paralelo (independentes entre si; T-09 depende de T-03 e de `scene._frame/_local_box`).
5. 🟢 T-12 → T-13 → T-14, validando com TT-04..TT-08 no Blender.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-75):** Esc não desliga o modo e sem realce 3D durante o arraste (Won't nesta versão); o código já faz isso.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-16):** caixas de A/B pela árvore de malhas visíveis (`_tree_box`). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-17):** `cancel()` restaura posição e chama `_end`. Pendência de implementação: DT-03.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-18):** passo do teclado zera `warned` (EC-04). Pendência de implementação: DT-04.
- 🟡 Medir desempenho de prévia/redesenho — decisão: medir/testar (DT-06; questions.md#pergunta-76).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 No modal da janela (`ops_dialog.py`, ramo de digitação), guardar o índice do campo antes de `_commit_typing`: Tab com gravação válida vai ao próximo campo; com falha fica no campo atual com o aviso (decisão questions.md#pergunta-15)
- [ ] DT-02 Usar a caixa da árvore visível (`_tree_box`) nas caixas de A/B de `scene.py` e em `overlapping`, como o Substituir (decisão questions.md#pergunta-16)
- [ ] DT-03 Definir `cancel()` em `move_on_wall` e `set_insertion_plane` que restaura a posição original e chama `_end` (cabeçalho/status e cursor) (decisão questions.md#pergunta-17)
- [ ] DT-04 Zerar `warned` no passo do teclado (setas/Page Up/Down) da janela Mover Sobre (decisão questions.md#pergunta-18)
- [ ] DT-05 No Substituir, dar ao novo módulo só posição e rotação de A (`Matrix.LocRotScale` sem escala), não `a.matrix_world` inteira (decisão questions.md#pergunta-19)
- [ ] DT-06 Medir uma vez prévia (meta 200 ms) e redesenho (meta 100 ms) num projeto com ~100 módulos; sem medição, retirar a meta (decisão questions.md#pergunta-76)
