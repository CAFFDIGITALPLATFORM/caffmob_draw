# Editor de Paredes 2D (walls2d) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/walls2d/` em 2026-10-10, incluindo a árvore de trabalho sem commit da feature 013 (`ops_editor.py`: barra superior, lupa, gestos; `props.py`: `zoom_window`/`zoom_box_end`; `compat.py`: `trackpad_delta`/`pinch_delta`). IDs RN/RF/CA são os de `requirements.md`; EC-xx de `edge-cases.md`. Vista, gestos, desenho e janela seguem `_reversa_sdd/canvas2d/design.md` (citado como `canvas2d`).

## Visão de Camadas

| Camada | Arquivo | `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `model.py` | não (`copy`, `math`, `data.i18n`) | Cadeias, trechos, faces, edição, validação, assinatura | 🟢 |
| Núcleo puro | `history.py` | não | Desfazer/refazer do rascunho (assinatura injetável) | 🟢 |
| Núcleo puro | `inference.py`, `direction.py`, `heights.py`, `convert.py` | não | Alinhamento da mira, direção do lápis, pé-direito, conversão | 🟢 |
| Ponte | `scene_io.py` | sim (`hb_types`, `mathutils` tardio) | Cena → rascunho | 🟢 |
| Ponte | `apply.py` | sim | Rascunho → paredes do Home Builder 5 | 🟢 |
| Estado/UI | `props.py` | sim | `Session` em memória e `BTM_PG_WallEditorState` | 🟢 |
| Interface | `ops_editor.py`, `panels.py`, `window.py` | sim | Operadores, modal, desenho GPU, painéis, handler | 🟢 |
| Pacote | `__init__.py` | não no topo | `register` na ordem props → window → ops_editor → panels; `unregister` na inversa; imports tardios | 🟢 |

## Interface

### `model.py`

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `INNER`, `OUTER` | constantes | `'INNER'`, `'OUTER'` | Faces | 🟢 |
| `SIDES` | constante | `('LEFT', 'RIGHT')` | Direção da espessura | 🟢 |
| `WALL_TYPES` | constante | `('NORMAL', 'DIVISORIA', 'MURETA')` | Ordem usada pelo enum do painel | 🟢 |
| `TYPE_DEFAULTS` | dict | `NORMAL: {}`, `DIVISORIA: {thickness: 0.10}`, `MURETA: {height: 1.10, end_height: 1.10}` | RN-03 | 🟢 |
| `LIMITS` | dict | ver RN-02 | Chaves `length`, `thickness`, `height`, `end_height`, `angle_abs`, `angle_rel` | 🟢 |
| `validate` | `(field, value)` | `None` ou `ValueError` | Mensagem traduzida; unidade `°` se o campo começa com `angle`, senão ` m`; números com `:g` | 🟢 |
| `Segment.__init__` | `(thickness=0.15, height=2.6, end_height=None, wall_type='NORMAL', lock_angle=False, source=None)` | — | `end_height=None` → `height`; sem validação | 🟢 |
| `Chain.__init__` | `(nodes, segments, closed=False, side='LEFT')` | — | `side` fora de `SIDES` → `ValueError("Direção inválida: …")`; nós convertidos para tuplas de float; listas copiadas (rasas) | 🟢 |
| `Chain.endpoints/direction/length` | `(i)` | pontos / rad `atan2` / `hypot` | Último trecho de fechada liga `nodes[-1]` a `nodes[0]` | 🟢 |
| `Chain.prev_index/next_index` | `(i)` | int ou `None` | Circulares só quando fechada | 🟢 |
| `Chain.angle_abs` | `(i)` | graus `[0, 360)` | `degrees(direction) % 360` | 🟢 |
| `Chain.angle_rel` | `(i)` | graus `[−180, 180]` | Virada sobre o anterior; 0 se não há anterior; +90 = esquerda | 🟢 |
| `Chain.miter_angles` | `(i)` | `(left, right)` rad | `left = norm(dir_i − dir_prev)/2`; `right = −norm(dir_next − dir_i)/2`; 0 sem vizinho | 🟢 |
| `Chain.is_ccw` / `outward_side` | `()` | bool / `'RIGHT'|'LEFT'` | Ver RN-04 (fórmula do cadarço, `area > 0` estrito; aberta: `signed_turn() ≥ 0`) | 🟢 |
| `Chain.inner_line/outer_line/line/face_length` | `(i[, which])` | pontos / float | F-01 | 🟢 |
| `Chain.shifted_nodes` | `(factor)` | lista de pontos | F-02 | 🟢 |
| `Chain.hb_order` | `()` | `(nodes, segments)` | `LEFT`: cópias; `RIGHT`: cópia invertida (`invert` num gêmeo) | 🟢 |
| `Chain.set_length` | `(i, value, which=INNER)` | `None` | F-03 | 🟢 |
| `Chain.set_angle_abs` | `(i, degrees)` | `None` | Valida `degrees % 360` (360 passa como 360); move o fim com o comprimento atual | 🟢 |
| `Chain.set_angle_rel` | `(i, degrees)` | `None` | Valida; base = direção do anterior ou 0 | 🟢 |
| `Chain.move_node` | `(k, point)` | `None` | `k % len(nodes)`; projeção com `lock_angle` do trecho que chega (RN-06); trecho nulo usa tamanho 1 | 🟢 |
| `Chain.set_segment_value` | `(i, field, value)` | `None` | `thickness`/`height`/`end_height` validam; `wall_type` fora da lista → `ValueError("Valor Inválido: tipo de parede {}.")`; `lock_angle` vira bool; outro → `ValueError("Campo desconhecido: …")` | 🟢 |
| `Chain.split` | `(i, point)` | índice do novo trecho `i+1` | RN-07 | 🟢 |
| `Chain.remove_node` | `(k)` | `None` | RN-08; aberta k=0 remove `segments[0]`, k=último remove `segments[-1]`; interno remove `segments[k]` (ou `[0]` se `k == len(segments)`) | 🟢 |
| `Chain.invert` | `()` | `None` | F-04 | 🟢 |
| `Chain.touches_start` | `(point, tolerance=0.01)` | bool | `≤` inclusivo | 🟢 |
| `Chain.close_if_touching` | `(tolerance=0.01)` | bool | RN-10 | 🟢 |
| `Chain.close` | `()` | `None` | Com 4+ nós e último a < 1e−6 do primeiro, tira o último; sempre `closed = True` | 🟢 |
| `WallPlan.__init__` | `(chains=None, references=None)` | — | `removed_sources = []`, `converted_sources = []` | 🟢 |
| `WallPlan.bounds` | `()` | `((x0,y0),(x1,y1))` | Nós + pontas das referências; vazio → `((-1,-1),(4,3))` | 🟢 |
| `WallPlan.remove_chain_segment_sources` | `(chain)` | `None` | Acrescenta os `source` da cadeia; sem chamador no pacote | 🟢 |
| `plan_signature` | `(plan)` | tupla | RN-11 | 🟢 |
| `rectangle` | `(width, depth, thickness=0.15, height=2.6, origin=(0,0))` | `Chain` | 4 nós anti-horários, fechada, `side='RIGHT'` | 🟢 |

### Núcleo auxiliar

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `history.LIMIT` | constante | `100` | | 🟢 |
| `History.__init__` | `(plan, limit=LIMIT, signature=model.plan_signature)` | — | `_current = deepcopy(plan)`; consumido também por `cabinet_editor/state.py` | 🟢 |
| `History.checkpoint` | `(plan)` | bool | Assinatura igual → `False`; senão empilha `_current` em `_undo`, corta para os últimos `limit`, limpa `_redo`, `_current = deepcopy(plan)` | 🟢 |
| `History.undo/redo` | `()` | cópia profunda do plano ou `None` | Move `_current` para a outra pilha | 🟢 |
| `History.can_undo/can_redo` | `()` | bool | | 🟢 |
| `inference.Index` | `(points)` | — | `by_x` ordenado por (x, y); `by_y` por (y, x) | 🟢 |
| `Index.query` | `(cursor, tol, exclude=())` | `(x, ref_x, y, ref_y)` | Por eixo: candidatos em `[v−tol, v+tol]` (inclusivo), menor `|Δ|`; empate fica com o primeiro na ordem; excluídos por igualdade exata de tupla float | 🟢 |
| `inference.plan_points` | `(plan, extra=())` | lista | Nós de todas as cadeias + extras | 🟢 |
| `direction.ORTHO_TOLERANCE_DEG` | constante | `2.5` | Cópia da constante de `canvas2d.view` | 🟢 |
| `direction.ARROWS` | dict | `RIGHT_ARROW 0`, `UP_ARROW π/2`, `LEFT_ARROW π`, `DOWN_ARROW 3π/2` | | 🟢 |
| `direction.initial_direction` | `(start, cursor, tolerance_deg=2.5)` | rad `[0, 2π)` ou `None` | `None` se `hypot < 1e-12`; encaixe ortogonal inclusivo | 🟢 |
| `direction.next_point/segment_direction/arrow_direction/label` | — | ponto / rad / rad ou `None` / str | `label`: "→ 0°", "↑ 90°", "← 180°", "↓ 270°"; demais "37°" (arredondado) | 🟢 |
| `heights.TOLERANCE`, `LOW_WALL_TYPES` | constantes | `0.001`, `{'Half', 'Fake'}` | | 🟢 |
| `heights.follows_project_height` | `(btm_wall_type=None, legacy_wall_type=None)` | bool | RN-22 | 🟢 |
| `heights.walls_to_equalize` | `(walls, project_height, tolerance=0.001)` | nomes | `|h − p| > tol` ou `|end − p| > tol` | 🟢 |
| `convert.JOIN_TOLERANCE` | constante | `0.01` | | 🟢 |
| `convert.chains_from_segments` | `(segments)` | `[Chain]` | F-05 | 🟢 |

### Ponte com a cena

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `scene_io.CLOSE_TOLERANCE` | constante | `0.01` | Fechamento estrito `< 0.01` | 🟢 |
| `scene_io.walls_in` | `(scene)` | objetos | `IS_WALL_BP` e `GeoNodeWall(o).has_modifier()` | 🟢 |
| `scene_io.reference_segments` | `(scene, exclude=())` | `[((x,y),(x,y))]` | Arestas da malha com as duas pontas a < 1e−4 da cota mínima (mundo), só paredes da camada nova | 🟢 |
| `scene_io.read_plan` | `(scene)` | `WallPlan` | F-06 | 🟢 |
| `scene_io.is_other_layer_wall` | `(obj)` | bool | `MESH`, sem `IS_WALL_BP`, `selection.classify.btm_kind(obj) == 'WALL'` | 🟢 |
| `scene_io.convert_into` | `(plan, objects, scene)` | nomes ignorados | F-07 | 🟢 |
| `apply.OPENING_TAGS` | constante | `('IS_ENTRY_DOOR_BP', 'IS_WINDOW_BP')` | | 🟢 |
| `apply.items_that_do_not_fit` | `(plan)` | `[(parede, item)]` | Filhos de paredes de origem, exceto `obj_x` e `IS_2D_ANNOTATION`; largura = `Dim X` se `home_builder.mod_name`, falha → 0; `location.x + largura > comprimento novo + 1e−4` | 🟢 |
| `apply.modules_of_removed` | `(plan)` | `[(parede, filho)]` | Filhos sem nenhuma marca de `KEEP_WITH_WALL` | 🟢 |
| `apply.height_mismatches` | `(plan, project_height)` | `["nome (NNNN mm)"]` | Trecho novo usa "nova {i+1}" (índice no trecho da cadeia) | 🟢 |
| `apply.apply_plan` | `(context, plan, remove_modules=False, project_height=None)` | dict | F-12; chaves `created`, `updated`, `removed`, `closed`, `floors`, `ceilings`, `openings` | 🟢 |
| `apply.refresh_floors_and_ceilings` | `(context)` | `(pisos, tetos)` | F-13 | 🟢 |
| `apply.sync_project_height` | `(context, height)` | int | F-14 | 🟢 |

### Estado (`props.py`)

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `Session.__init__` | `(plan, scene_name)` | — | Campos na seção Estado Interno | 🟢 |
| `Session.dirty` | `()` | bool | `plan_signature(plan) != signature` (assinatura da abertura) | 🟢 |
| `Session.segment` | `()` | `(chain, i)` ou `(None, None)` | Índices fora da faixa limpam `selected` | 🟢 |
| `Session.checkpoint` | `()` | bool | `history.checkpoint(plan)` | 🟢 |
| `Session.undo/redo` | `()` | bool | Restaura e limpa `drawing`, `selected_node`, `typed`, `prompt`, `prompt_chain`, `pending_point`, direção e travas; revalida a seleção | 🟢 |
| `Session.redraw` | `()` | `None` | `tag_redraw` na área com `as_pointer() == area_ptr` (usa `bpy.context`) | 🟢 |
| `session` / `start` / `end` | `()` / `(plan, scene_name)` / `()` | sessão / sessão / `None` | Singleton `_session[0]` | 🟢 |

`BTM_PG_WallEditorState` em `WindowManager.btm_wall_editor` 🟢 (`props.py:286`):

| Propriedade | Tipo | Padrão / faixa | Leitura/escrita |
|---|---|---|---|
| `tool` | Enum `SELECT` (RESTRICT_SELECT_OFF), `DRAW` (GREASEPENCIL), `INVERT` (ARROW_LEFTRIGHT), `ADD_NODE` (ADD), `REMOVE_NODE` (REMOVE) | `SELECT` | armazenada |
| `grid_size` | Float DISTANCE/LENGTH | 1.0; 0.01–5.0; `update` redesenha | armazenada |
| `magnetic` | Bool | False | armazenada |
| `new_direction` | Enum `LEFT`/`RIGHT` | `LEFT` | armazenada |
| `new_thickness` | Float DISTANCE | 0.15; 0.01–2.0 | armazenada |
| `new_height` | Float DISTANCE | 2.6; 0.5–10.0 (sobrescrita na abertura) | armazenada |
| `line` | Enum `INNER`/`OUTER` | — | `s.line` |
| `length`, `thickness`, `height`, `end_height` | Float DISTANCE, `precision=1` | — | `_seg_get`/`_seg_set` |
| `angle_abs`, `angle_rel` | Float ANGLE/ROTATION, `precision=2` (radianos na UI) | — | graus no modelo |
| `lock_angle` | Bool | — | `_seg_get('lock_angle', False)` |
| `length_text`, `thickness_text`, `height_text`, `end_height_text` | String | — | `_text_get`/`_text_set` (unidade do projeto) |
| `direction` | Enum `LEFT`/`RIGHT` | — | `chain.side` (sem `_guard`, sem passo de desfazer imediato) |
| `wall_type` | Enum `NORMAL`/`DIVISORIA`/`MURETA` | — | índice em `WALL_TYPES` |
| `equalize_height` | Bool | `Session.equalize_height = True` | sessão |
| `remove_modules` | Bool | `Session.remove_modules = False` | sessão |

🟢 `_guard(apply)`: sem sessão → nada; executa; sucesso limpa `s.error`; `ValueError` → `s.error = str(exc)`; **sempre** `s.checkpoint()` e `s.redraw()`. Getters sem trecho devolvem `0.0` (texto: `""`), enum 0, bool False. `register()` cria `WindowManager.btm_wall_editor`; `unregister()` chama `end()`, apaga a propriedade e desregistra a classe.

### Operadores (`ops_editor.py`)

| `bl_idname` | Classe | `bl_options` | Comportamento | Confiança |
|---|---|---|---|---|
| `caffmob.wall_editor` | `BTM_OT_WallEditor` ("Editar Paredes…") | `REGISTER` | `poll` RN-27; `invoke` abre `invoke_props_dialog` (título "Paredes de outra camada") se há paredes da camada nova selecionadas; propriedade `other_walls` `CONVERT` (padrão)/`REFERENCE`; F-08 | 🟢 |
| `caffmob.wall_editor_modal` | `BTM_OT_WallEditorModal` | `REGISTER`, `UNDO`, `INTERNAL` | Modal com timer `TIMER_STEP = 0.1` s na janela do editor; F-09 | 🟢 |
| `caffmob.wall_editor_ok` | `BTM_OT_WallEditorOk` | `REGISTER`, `INTERNAL` | Duas fases (RN-12); `request = 'ok'` | 🟢 |
| `caffmob.wall_editor_cancel` | `BTM_OT_WallEditorCancel` | `REGISTER`, `INTERNAL` | Sujo → `invoke_confirm(title="Descartar alterações", message="Descartar as alterações e fechar o editor?", confirm_text="Descartar", icon='WARNING')`; `request = 'cancel'` | 🟢 |
| `caffmob.wall_editor_fit` | `BTM_OT_WallEditorFit` ("Enquadrar Tudo") | `REGISTER`, `INTERNAL` | `view.fit(plan.bounds(), margin=0.15)` e redesenha | 🟢 |

Chamadores de `caffmob.wall_editor` 🟢: `ui/panels.py:238`, `ui/sidebar_build.py:66`, `ui/menus.py:71`.

Constantes 🟢 `ops_editor.py`: `NODE_HIT_PX 9`, `LINE_HIT_PX 7`, `SNAP_CLOSE_PX 15`, `CLOSE_TOLERANCE 0.01`, `ALIGN_PX 8`, `TYPING_CHARS "0123456789,.+-*/() "`, `UNIT_CHARS "mMcC"`, `TIMER_STEP 0.1`, `TOOLBAR_HEIGHT 32`, `NAVIGATION_EVENTS {TRACKPADZOOM, TRACKPADPAN, WHEELUPMOUSE, WHEELDOWNMOUSE, MIDDLEMOUSE}`, `PROMPT_W/H 380/90`, `PROMPTS` (`close`, `close_existing`, `discard`), `ZOOM_WINDOW_HINT`.

Cores próprias 🟢 `ops_editor.COLORS`: `background (0.12,0.12,0.13,1)`, `grid (1,1,1,0.06)`, `grid_axis (1,1,1,0.14)`, `wall (0.85,0.85,0.88,1)`, `wall_fill (0.55,0.55,0.6,0.18)` (sem uso no desenho atual), `selected (1,0.62,0.15,1)`, `node (0.25,0.6,1,1)`, `preview (0.35,1,0.45,1)`, `preview_locked (0.8,0.8,0.8,1)`, `reference (0.7,0.7,0.75,0.55)`.

Funções de módulo 🟢: `toolbar_height()`, `_region_rect(region, area=None)` → `(0, 0, visible_width ou region.width, max(1, region.height − toolbar_height()))`, `ensure_view(region, area=None)` (cria `View2D` e `fit(bounds, 0.15)` na 1ª vez; depois só atualiza `rect`), `draw_plan(context)`, `handle_zoom_window(event, s, view, pixel)`, `resolve_point(context, s, view, cursor, origin=None, shift=False, exclude=())`, `hit_node(s, pixel)`, `close_snap(s, view, pixel)`, `hit_line(s, pixel)`, `remove_segment(s, ci, i)`, `accept_typing(s, char)`.

### Painéis (`panels.py`) e janela (`window.py`)

| Painel | `bl_idname` | Ordem | Conteúdo | Confiança |
|---|---|---|---|---|
| Ferramentas | `BTM_PT_wall_editor_tools` | 0 | `tool` expandido; botão `caffmob.wall_editor_fit` | 🟢 |
| Painel | `BTM_PT_wall_editor_segment` | 1 | Sem trecho: "Selecione um trecho na planta."; senão `line`, `length_text`, `angle_abs`, `angle_rel`, rótulo desabilitado "Ângulo do Arco: paredes curvas não são suportadas", `lock_angle`, `thickness_text`, `height_text`, `end_height_text`, `direction` expandido, `wall_type` | 🟢 |
| Grid | `BTM_PT_wall_editor_grid` | 2 | `grid_size`, `magnetic`, "Novas paredes": `new_direction`, `new_thickness`, `new_height` | 🟢 |
| Confirmar | `BTM_PT_wall_editor_confirm` | 99 | `s.error`; caixas de avisos (até 8 linhas + "… e mais {}"): "Itens que não cabem:", "Módulos em trechos apagados:" + `remove_modules`, pé-direito do projeto + `equalize_height`; OK/Cancelar (`scale_y 1.4`) | 🟢 |

🟢 Todos: `IMAGE_EDITOR`/`UI`, `bl_category = "Editor de Paredes"`, `poll = window.is_editor_area(context)`. `window.py`: `EDITOR_CATEGORY = "Editor de Paredes"`; reexporta `side_panel`, `over_side_panel`, `visible_width`, `close_later` de `canvas2d.window`; `editor_area(context)`, `is_editor_area(context)`, `focus_editor_tab(area)`, `open_editor(context)` (mensagem "O Editor de Paredes precisa de uma janela do Blender aberta.") embrulham `canvas2d` com `props.session()`; `register` adiciona um único `SpaceImageEditor.draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')`; `_draw` chama `draw_plan` só na área do editor; `unregister` remove.

## Fluxo Principal

1. 🟢 `caffmob.wall_editor` (F-08) lê o rascunho, cria a sessão, abre a janela (`canvas2d` F-09) e invoca o modal com `temp_override(window, area, region)`.
2. 🟢 O handler desenha a planta (F-11) em cada redesenho da área marcada.
3. 🟢 O modal (F-09) converte o evento para pixel local, atualiza cursor e mira e despacha para navegação, lupa, perguntas, lápis, digitação ou ferramentas; após ação concluída fora de arraste, grava passo de desfazer se a assinatura mudou.
4. 🟢 Painéis alteram o rascunho pelos campos virtuais (`_guard`).
5. 🟢 OK/Cancelar marcam `s.request`; o modal, no próximo evento (o timer garante), chama `_end`: OK aplica (F-12) e reporta; ambos agendam `close_later` e encerram a sessão.

### F-01 Faces 🟢 `model.py:outer_line/face_length`
1. `sign = +1` se `side == 'LEFT'`, senão `−1`; `d = direction(i)`; `(dx, dy) = (cos d, sin d)`; normal `(−dy·sign, dx·sign)`.
2. `(left, right) = miter_angles(i)`; `s0 = sign·t·tan(left)`; `s1 = sign·t·tan(right)`.
3. Externa = `(p0 + n·t + u·s0, p1 + n·t + u·s1)`; interna = os nós. `face_length` = `hypot` da face.

### F-02 `shifted_nodes(factor)` 🟢 `model.py`
Para cada nó `k`: trechos incidentes = `k` (se existir) e o anterior (`k−1`, ou o último se fechada). Soma das normais esquerdas `(−sin d, cos d)·t·factor`. Com dois trechos: `half = norm(dir[k] − dir[prev])/2`; escala `1/(2·cos²(half))` se `|cos half| > 1e−6`, senão 0,5. Positivo = esquerda do sentido.

### F-03 `set_length` 🟢 `model.py`
1. `validate('length', value)`.
2. `INNER`: move o nó `i+1` para `start + u·value` via `move_node` (sujeito a RN-06).
3. `OUTER`: `ref = length(i)`; até 12 vezes: `ref += value − face_length(i, OUTER)`; `validate('length', ref)`; move o fim com `ref`; para se `|face − value| < 1e−7`. Falha no meio deixa o nó na última posição válida (EC-08).

### F-04 `invert` 🟢 `model.py`
`side` troca; `nodes.reverse()`. Fechada: tira o último trecho, inverte os demais, insere-o na frente; o último nó vai para a frente. Aberta: `segments.reverse()`.

### F-05 `chains_from_segments` 🟢 `convert.py`
1. Descarta trechos com comprimento ≤ 1e−6.
2. Enquanto houver pendentes: começa com o primeiro; cresce enquanto achar trecho cujo início toca o fim da cadeia (acrescenta) ou cujo fim toca o início (insere na frente), tolerância `≤ 0.01`.
3. Fechada se 3+ trechos e fim toca início. Nós = inícios (+ fim do último se aberta). `Segment(thickness, height=s.get('height', 2.6))`.
4. Cadeia de centro `side='LEFT'`; `side` final = `outward_side()` se fechada, senão `LEFT`; nós internos = `shifted_nodes(+0.5)` se `side == 'RIGHT'`, senão `shifted_nodes(−0.5)` (meia espessura para longe da espessura). Mesmos objetos `Segment` nas duas cadeias.

### F-06 `read_plan` 🟢 `scene_io.py`
1. `walls = walls_in(scene)`; `starts` = paredes com `get_connected_wall('left') is None`.
2. Para cada `first` em `starts + walls` não visitado: segue `get_connected_wall('right')` enquanto o objeto estiver em `walls` e não visitado.
3. `_chain_from`: por parede, `Length/Thickness/Height/End Height` do modificador; início = translação do mundo; fim = início + `Length·(cos, sin)(rot_z do mundo)`; `wall_type = obj.get('btm_wall_type', 'NORMAL')`; `source = obj.name`. Fechada se 3+ e `|fim_último − início_primeiro| < 0.01`; senão acrescenta o fim. `side='LEFT'` (`btm_wall_orientation` ignorado).
4. `WallPlan(chains, reference_segments(scene))`.

### F-07 `convert_into` 🟢 `scene_io.py`
Para cada objeto: `json.loads(obj.get("btm_wall_segments", ""))`; erro ou vazio → nome em `skipped`. Senão leva `start`/`end` ao mundo (`matrix_world @ Vector((x, y, 0))`), acrescenta `chains_from_segments(...)` a `plan.chains` e o nome a `converted_sources`. Ao final, `plan.references = reference_segments(scene, exclude=converted_sources)`.

### F-08 Abrir 🟢 `ops_editor.py:BTM_OT_WallEditor.execute`
1. `plan = read_plan(scene)`; `others` = selecionados da camada nova; se `CONVERT`, `convert_into` e `report WARNING "Sem dados de trechos, ficam como referência: …"` para ignorados.
2. `props.start(plan, scene.name)`; `project_height = measure.scene_cotas.ceiling_height(scene)` (cena principal `home_builder.ceiling_height > 0`, senão 2,6); `state.new_height = project_height`.
3. `window.open_editor(context)`; `RuntimeError` → `props.end()`, `report ERROR`, `CANCELLED`.
4. Se há cadeias e a primeira tem trecho, `selected = (0, 0)`.
5. `bpy.ops.caffmob.wall_editor_modal('INVOKE_DEFAULT')` no override da janela nova; `FINISHED`.

### F-09 Despacho do modal 🟢 `ops_editor.py:modal/_handle`
`invoke`: sem sessão → `CANCELLED`; `dragging = panning = None`, `tab_ready = False`, timer, `modal_handler_add`.

`modal`, por evento, nesta ordem:
1. Sem sessão → `_end(False)`, `CANCELLED`.
2. `request == 'ok'` → `_end(True)`, `report INFO "Paredes aplicadas: {n} nova(s), {u} atualizada(s), {r} removida(s){, k sala(s) fechada(s) no OK}."`, `FINISHED`. `request == 'cancel'` → `_end(False)`, `CANCELLED`.
3. `TIMER` → até `focus_editor_tab` devolver True; `PASS_THROUGH`.
4. `_handle_undo` (PRESS de Z/Y com Ctrl ou OS-key; Y ou Shift = refazer; zera `dragging`) → `RUNNING_MODAL`.
5. `_local`: sem região → `PASS_THROUGH`; sobre o painel lateral sem arraste/pan → `PASS_THROUGH`; senão `pixel = mouse − region.xy`.
6. Fora da região sem arraste/pan → `PASS_THROUGH`.
7. `view = ensure_view(region, area)`; `s.cursor = view.to_world(pixel)`; `self.shift = event.shift`; se não é navegação (`NAVIGATION_EVENTS` ou `MOUSEMOVE` com pan), `_update_snap` (F-10).
8. `_handle`: (a) `handle_zoom_window` (F-15); (b) `MIDDLEMOUSE` liga/desliga pan; `MOUSEMOVE` com pan → `view.pan(Δpixel)`; roda → `zoom(wheel_factor(up, invert_zoom_wheel), pixel)`; `TRACKPADZOOM` → `zoom(pinch_factor(compat.pinch_delta(event)), pixel)`; `TRACKPADPAN` → `pan(*compat.trackpad_delta(event))`; `HOME` PRESS → `fit(bounds, 0.15)`; (c) lupa ligada → consome tudo; (d) pergunta aberta → F-17; (e) `tool == 'DRAW'` → F-16; (f) `ESC` PRESS: limpa `typed`, ou `prompt = 'discard'` se sujo, ou `request = 'cancel'`; (g) `SELECT` → digitação (F-18); (h) `DEL`/`X` PRESS com seleção → `remove_segment`; (i) `LEFTMOUSE` → `_handle_click` (F-19); (j) `MOUSEMOVE` com arraste → move o nó para o ponto da mira, ou para o primeiro nó se é o último de cadeia aberta com 3+ trechos a ≤ 15 px dele; (k) senão não tratado.
9. Tratado e sem arraste → `s.checkpoint()`. Sempre `s.redraw()`. Devolve `RUNNING_MODAL` se tratado, senão `PASS_THROUGH`.

`cancel(context)` (Blender cancelou o modal) → `_end(False)`. `_end`: aplica se pedido; remove o timer; `close_later(window_ptr, area_ptr, restore_area_type)`; `props.end()`.

### F-10 Mira 🟢 `ops_editor.py:_update_snap/resolve_point`
`_update_snap`: arrastando nó `k` → `origin` = nó anterior (circular se fechada), `exclude = (nó k,)`; senão, `DRAW` com desenho → `origin` = último nó. Ferramentas `DRAW`/`SELECT` → `s.snap_point = resolve_point(...)`; outras → `snap_point`, `lock_x`, `lock_y` = `None`.

`resolve_point`: zera travas; (1) desenhando e `close_snap` → `(drawing.nodes[0], 'close')`; (2) `hit_node` (primeiro nó a ≤ 9 px, em ordem de cadeia/nó) não excluído → `('node')`; (3) com `origin`, `ortho_snap(origin, cursor)`; travado fixa o eixo Y se `|point.y − origin.y| < 1e−12`, senão X → `'ortho'`; (4) sem Shift, `Index.query(cursor, 8/scale, exclude)`: X travado se o eixo X não está fixo, Y idem → `'align'`, gravando `lock_x/lock_y = (valor, ref)`; (5) ainda `'free'` e `magnetic` → `snap_to_grid(point, grid_size)`, `'grid'`. O índice (`_index`) é refeito quando `plan_signature` muda.

### F-11 `draw_plan` 🟢 `ops_editor.py`
Ordem: fundo da região inteira → grade (`grid_lines(grid_size)`, linhas entre extremos) → referências tracejadas → para cada trecho: interna tracejada + externa + pontas (cor `wall`); selecionado: face escolhida em laranja (2 linhas, +1 px) e seta de sentido (18 px); rótulo da medida no meio da interna (face escolhida se selecionado, senão interna; tamanho 11) → nós como quadrados 8×8 (laranja se `selected_node`) → texto "Medida: …" quando há digitação sem lápis → mira em cruz (`DRAW`/`SELECT`, sem pergunta; vertical até o topo da área útil, horizontal na largura da região; eixo travado em laranja com guia tracejada e anel de 7 px na referência) → prévia do lápis (cheia se travada, tracejada se livre; com digitação válida segue `direction`; anel de 11 px e "Fechar" no ímã; "Comprimento: …"; seta da direção 26 px com `label`) → dica da ferramenta em (12, 12) → erro em (12, 32) → barra superior (F-15) → caixa de pergunta 380×90 centrada com "Sim" (primário) e "Não" → `draw.end()`.

### F-12 `apply_plan` 🟢 `apply.py`
Para cada cadeia:
1. `close_if_touching()` → se fechou e nenhum trecho tem `source`, `side = outward_side()`; `closed += 1`.
2. `project_height` dado → `height = end_height = project_height` nos trechos que `follows_project_height(wall_type, WALL_TYPE da origem)`.
3. `(nodes, segments) = hb_order()`; `draft = Chain(nodes, segments, closed, 'LEFT')`.
4. Para cada trecho: objeto de `source` ou `GeoNodeWall().create("Wall")` (created/updated); guarda `rot_z` antiga e matrizes de mundo dos filhos sem `obj_x`; remove restrições `COPY_LOCATION`; 1º trecho: `location = (nó0.x, nó0.y, z atual)`; demais: `connect_to_wall(anterior)`; `rotation_euler = (0, 0, direção)`; se há filhos e `|norm(nova − antiga)| > π/2`: `view_layer.update()`, filhos voltam à matriz guardada, aberturas → `_rehost_opening`; `set_input` `Length`, `Thickness`, `Height`, `End Height`; `obj['btm_wall_type']`; aberturas filhas `Dim Y = thickness`; `seg.source = obj.name`.
5. Depois de todas as cadeias: remove `removed_sources` existentes e não usados (`ops_wall_extras.remove_wall(obj, remove_modules)`); limpa a lista. Remove `converted_sources` (e a malha sem usuários); limpa a lista.
6. `view_layer.update()`; `operators.walls.update_all_wall_miters()`; `refresh_floors_and_ceilings`; `view_layer.update()`; `openings` = quantidade de jaulas com `btm_opening_real.assembly` e `openings.sync.sync(context, cage)` verdadeiro. Sem `try`: uma exceção em `sync` (openings EC-11) sobe para fora de `apply_plan` depois de as paredes já terem sido gravadas, e caixas sem montagem real não são refeitas _(Revisão cruzada 2026-10-10: walls2d/apply.py:175-178; ao contrário de `_sync_opening`, que engole a exceção)_.

`_rehost_opening`: `location = (x − Dim X, 0, z)`, rotação zerada; em filhos com "Door Swing" no nome, inverte `Swing Inside` e `Is Left`.

### F-13 `refresh_floors_and_ceilings` 🟢 `apply.py`
Salas = cadeias de `walls_ops.find_wall_chains()` com `get_room_boundary_points` de 3+ pontos e `is_closed_loop`. Pisos (`IS_FLOOR_BP`, `MESH`) e tetos (`IS_CEILING_BP`) ordenados por nome, emparelhados com as salas por `zip`. Piso: `create_floor_mesh(None, nome+"_tmp", pontos)`; teto: altura = `Height` da 1ª parede da sala ou `scene.home_builder.ceiling_height`; `_swap_mesh` copia materiais para a malha nova, troca `obj.data`, remove o temporário e a malha antiga órfã.

### F-14 `sync_project_height` 🟢 `apply.py`
Para todo `bpy.data.objects` com `IS_WALL_BP`, de altura cheia e com modificador: se `Height` ou `End Height` diferem > 1 mm, grava ambos. Com mudanças: `view_layer.update()`, esquadrias, piso/teto da cena atual. Devolve o total. Chamado por `hb_props.py:84` ao mudar o pé-direito.

### F-15 Barra superior e lupa 🟢 `ops_editor.py:_toolbar_rects/handle_zoom_window/_draw_toolbar`
1. Retângulos: barra `(0, rect.h, rect.w, toolbar_height())`; lupa `(8, rect.h + 4, h − 8, h − 8)`. `point_in_rect` é inclusivo.
2. `LEFTMOUSE` PRESS na lupa → alterna `zoom_window` entre `None` e `'ARMED'`, zera `zoom_box_end`.
3. `LEFTMOUSE` (qualquer valor) na barra → consumido.
4. Desligado → não consumido. `ESC` PRESS → desliga. `LEFTMOUSE` PRESS → `zoom_window = zoom_box_end = pixel`. Com tupla: `MOUSEMOVE` → `zoom_box_end = pixel`; `LEFTMOUSE` RELEASE → `zoom_window_bounds(view, início, pixel)`; não `None` → `fit(bounds, margin=0)`; desliga.
5. Desenho: faixa `panel`, linha `border` na base, botão `button_primary` (armado) / `button_hot` (mouse em cima) / `button`, contorno, ícone em linhas (anel 16 lados, cabo a 45°, quadrado); dica `ZOOM_WINDOW_HINT` ao lado quando quente ou armado; retângulo elástico tracejado laranja.

### F-16 Lápis 🟢 `ops_editor.py:_handle_draw/_append/_finish_drawing`
1. Valor ≠ PRESS → tratado só se `MOUSEMOVE`.
2. `ESC`/`RIGHTMOUSE` → `_finish_drawing` (remove a cadeia se tem 0 trechos; `drawing = None`; limpa digitação e direção).
3. `BACK_SPACE` → apaga o último caractere e refaz a prévia.
4. Desenhando e seta → `direction = ARROWS[seta]`, travada.
5. `accept_typing(event.unicode)` → tratado.
6. `RET`/`NUMPAD_ENTER` com desenho e digitação: `parse_length` (erro → `s.error`, limpa digitação); sem direção travada → `initial_direction(último nó, cursor)` (None → erro "Mova o mouse…"); `target = next_point`; se 2+ trechos e `target` toca o início (≤ 0,01) → `prompt = 'close'`, `pending_point = target`; senão `_append(target)`.
7. Não é `LEFTMOUSE` → não tratado. Clique: `resolve_point(view.to_world(pixel), origin=último nó)`; sem desenho → `reset_direction`, nova `Chain([ponto], [], False, new_direction)` adicionada ao plano; `'close'` → `prompt = 'close'`; ponto igual ao último → nada; senão `_append(ponto)`.
8. `_append`: `direction = segment_direction(último, ponto)` travada; acrescenta o nó e `Segment(new_thickness, new_height)`; limpa digitação e prévia.

### F-17 Perguntas 🟢 `ops_editor.py:_handle_prompt/_answer_no`
`ESC` PRESS → "Não". Só `LEFTMOUSE` PRESS age (outros eventos consumidos, exceto `MOUSEMOVE`). Botões: Sim `(x+60, y+12, 100, 26)`, Não `(x+200, y+12, 100, 26)` na caixa centrada na região. Sim: `discard` → `request = 'cancel'`; `close_existing` → `close_if_touching(0.01)` na cadeia `prompt_chain` (e `outward_side` se toda nova); `close` → acrescenta o primeiro nó, `close()`, `side = outward_side()`, termina o lápis, `tool = 'SELECT'`. Não: em `close` com `pending_point`, acrescenta o trecho digitado; limpa `prompt` e `pending_point`.

### F-18 Digitação na seleção 🟢 `ops_editor.py:_handle_typing`
Só PRESS com `selected` ou `selected_node`. Caractere aceito → tratado. `BACK_SPACE` com texto → apaga. `RET`/`NUMPAD_ENTER` com texto: `parse_length` na unidade da cena; vértice selecionado → trecho que chega nele (`k−1`, ou o último se fechada e `k == 0`; aberta `k == 0` → erro) com `set_length(..., INNER)`; senão `set_length(i, valor, s.line)`; erro → `s.error`; sempre limpa `typed`.

### F-19 Clique por ferramenta 🟢 `ops_editor.py:_handle_click`
RELEASE: termina arraste; se o nó arrastado é o último de cadeia aberta de 3+ trechos e toca o início (0,01) → `prompt = 'close_existing'`, `prompt_chain = ci`. Só PRESS segue; limpa `s.error`. `SELECT`: limpa digitação; nó → arraste + `selected_node`, `selected = None`; senão linha → `selected`, `line = face clicada`; nada → limpa seleção. `REMOVE_NODE`: `remove_node` (erro → `s.error`), limpa seleção. `ADD_NODE`/`INVERT`: na linha clicada, `split(i, cursor)` ou `invert()`; limpa seleção.

## Fluxos Alternativos

- **Paredes da camada nova sem `btm_wall_segments`**: ficam como referência tracejada; aviso no operador. 🟢 `scene_io.convert_into`
- **Janela indisponível**: `RuntimeError` → sessão encerrada, `CANCELLED` (CA-06). 🟢
- **Usuário fecha a janela/Blender cancela o modal**: `cancel()` → `_end(False)`; rascunho descartado. 🟢 `ops_editor.py:cancel`
- **Sessão encerrada por fora** (ex. `unregister`): no próximo evento o modal chama `_end(False)` e sai. 🟢 `ops_editor.py:modal`
- **Digitação inválida**: `s.error` com a mensagem de `units`/`expr`; rascunho intacto. 🟢
- **Esc na ferramenta Construir**: só termina o desenho; nunca pede descarte nem cancela o editor (EC-04). 🟢

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `caffmob_draw/canvas2d/` | `View2D`, `snap_to_grid`, `ortho_snap`, distâncias, `gestures.wheel_factor/pinch_factor/zoom_window_bounds`, `draw.*`, `window.*` (contrato em `_reversa_sdd/canvas2d/`) | 🟢 |
| `caffmob_draw/compat.py` | `trackpad_delta(event) = (mouse_x − mouse_prev_x, mouse_y − mouse_prev_y)`; `pinch_delta(event) = −(dx + dy)` (013, sem commit) | 🟢 |
| `caffmob_draw/hb_types.py` | `GeoNodeWall` (`get_input`, `set_input`, `has_modifier`, `get_connected_wall`, `connect_to_wall`, `create`), `GeoNodeCage`, `GeoNodeObject` | 🟢 |
| `caffmob_draw/operators/walls.py` | `update_all_wall_miters`, `find_wall_chains`, `get_room_boundary_points`, `is_closed_loop`, `create_floor_mesh`, `create_ceiling_mesh` | 🟢 |
| `caffmob_draw/operators/ops_wall_extras.py` | `remove_wall(obj, remove_modules)`, `KEEP_WITH_WALL = ('obj_x', 'IS_2D_ANNOTATION', 'IS_ENTRY_DOOR_BP', 'IS_WINDOW_BP', LOWERED_PROXY)` | 🟢 |
| `caffmob_draw/openings/sync.py` | `openings(scene)`, `sync(context, cage)` | 🟢 |
| `caffmob_draw/selection/classify.py` | `btm_kind(obj)` | 🟢 |
| `caffmob_draw/measure/scene_cotas.py` | `ceiling_height(scene)` | 🟢 |
| `caffmob_draw/data/units.py`, `data/expr.py`, `data/i18n.py` | `parse_length`, `format_length`, `format_value`, `get_scene_length_unit`; `preview`, `MAX_LENGTH = 64`; `tr`, `N_` | 🟢 |
| `caffmob_draw/hb_gpu_draw.py` | `point_in_rect` (inclusivo) | 🟢 |

Consumidores 🟢 (grep): `caffmob_draw/__init__.py` (register), `hb_props.py:84` (`sync_project_height`; _(Revisão cruzada 2026-10-10: a 83 é o import)_), `cabinet_editor/state.py` (`history`), `geometry/floor_outline.py` (`convert`, `model`), `ui/panels.py`, `ui/sidebar_build.py`, `ui/menus.py` (operador).

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Rascunho em memória, aplicado só no OK (RN-16 da 002) | `props.py` docstring; `ops_editor.py:_end` | 🟢 |
| Nós = face interna; espessura por `side`; Home Builder sempre à esquerda (D-25) | `model.py` docstring; `apply.py:hb_order` | 🟢 |
| Atualizar paredes existentes por `source` em vez de recriar | `scene_io.py` docstring; `apply.py:apply_plan` | 🟢 |
| Desfazer próprio por assinatura, reutilizado pelo Editor de Armário (D-21 da 004) | `history.py` docstring | 🟢 |
| Campos do painel como propriedades virtuais `get`/`set` sobre a sessão | `props.py:_seg_get/_seg_set` | 🟢 |
| OK/Cancelar por pedido (`request`) processado no modal, fechamento diferido | `ops_editor.py:modal/_end`; `canvas2d.close_later` | 🟢 |
| Cadeia única de travas da mira (009, D-02) e tolerâncias em pixels | `ops_editor.py:resolve_point` | 🟢 |
| Navegação fora do encaixe e do histórico (013, D-06); lupa como estado só de vista (D-09) | `ops_editor.py:_is_navigation`; `props.py:zoom_window` | 🟢 |
| `handle_zoom_window` como função de módulo para os testes de fumaça | Docstring de `handle_zoom_window` | 🟢 |
| Barra superior desenhada em GPU; área útil exclui barra e painel N (013, D-07/D-08) | `ops_editor.py:_region_rect` | 🟢 |

## Estado Interno

`Session` 🟢 `props.py:Session.__init__` (uma por vez em `_session[0]`; vive da abertura ao `_end`):

| Campo | Inicial | Papel |
|---|---|---|
| `plan`, `scene_name` | argumentos | Rascunho e cena |
| `view` | `None` | `View2D` criada no 1º desenho/evento |
| `window_ptr`, `area_ptr`, `restore_area_type` | 0, 0, `None` | Contrato `canvas2d.window` |
| `selected`, `selected_node`, `line` | `None`, `None`, `INNER` | Seleção |
| `drawing`, `cursor`, `typed`, `typed_preview` | `None`, `None`, `""`, `""` | Lápis/digitação |
| `direction`, `direction_locked` | `None`, False | Direção do lápis |
| `lock_x`, `lock_y`, `snap_point`, `inference_index`, `inference_signature` | `None` | Mira |
| `prompt`, `prompt_chain`, `pending_point` | `None` | Perguntas |
| `error`, `warnings`, `removed_modules`, `height_mismatches` | `""`, `[]`, `[]`, `[]` | Mensagens |
| `remove_modules`, `equalize_height`, `project_height` | False, True, 2.6 (sobrescrito na abertura) | Opções do OK |
| `confirm_pending`, `request` | False, `None` | Fases do OK |
| `signature`, `history` | assinatura e `History(plan)` da abertura | Sujo e desfazer |
| `zoom_window`, `zoom_box_end` | `None`, `None` | Lupa (013): `None` / `'ARMED'` / pixel inicial |

Operador modal (instância) 🟢: `dragging` (`(ci, k)` ou `None`), `panning` (pixel ou `None`), `tab_ready`, `shift`, `_timer`.

🟡 `WindowManager` não é persistido com valores de propriedades Python no `.blend`; as propriedades "armazenadas" do grupo (`tool`, `grid_size`, …) duram a sessão do Blender. Não verificado no corpus.

## Observabilidade

- 🟢 `report`: WARNING na conversão (nomes sem dados), ERROR ao abrir sem janela, WARNING "Confira os avisos no painel e clique OK de novo para aplicar.", INFO com o resumo do OK.
- 🟢 Mensagens de erro do modelo e da digitação aparecem em `s.error` (painel "Confirmar" e planta em (12, 32)).
- 🟢 Sem logs nem métricas; `get_input('Dim X')` com exceção conta como largura 0 (`apply.items_that_do_not_fit`).

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-1):** `remove_node` (ou o chamador) acrescenta o `source` do trecho descartado a `removed_sources`. 🟢 (código) hoje o `source` se perde (EC-01). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-8):** respeitar o "Não" de `close_existing` marcando a cadeia para pular `close_if_touching`. 🟢 (código) hoje o OK sobrepõe o "Não" (EC-03). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-9):** `handle_zoom_window` consome na barra só `LEFTMOUSE PRESS`; o `RELEASE` segue com arraste ou retângulo em curso. 🟢 (código) hoje consome qualquer `LEFTMOUSE` (EC-05). Pendência de implementação: DT-03.
- 🟢 `confirm_pending` nunca volta a False: depois do 1º aviso, um OK posterior aplica mesmo com avisos novos (EC-06). _(Revisão 2026-10-10: ops_editor.py:887-891; props.py:38)_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-10):** guardar a assinatura do rascunho no aviso e recalcular se ela mudou. Pendência de implementação: DT-04.
- 🟢 Direção trocada pelo painel não grava passo na hora; entra no próximo passo gravado (EC-10). _(Revisão 2026-10-10: props.py:188-197 sem _guard)_
- 🟢 `ops_editor.COLORS['wall_fill']` não é usado.

## Divergências entre artefatos e código

- 🟢 `code-analysis.md` §5.6 diz "Todo `set` passa por `_guard`"; no código, `direction`, `line`, `equalize_height` e `remove_modules` não passam, e o erro de parse de `*_text` grava `s.error` sem `_guard` (sem passo de desfazer).
- 🟢 `flowcharts/walls2d.md` §1 liga "Esc / Cancelar → dirty?" sem exceção; com a ferramenta Construir, Esc só termina o lápis (F-16) e nunca chega à pergunta de descarte.
- 🟢 `state-machines.md` (Editor de paredes) mostra "PerguntaFechar → Desenhando : recusar"; isso só vale para `close`; em `close_existing` (arraste) não há desenho, e o "Não" é anulado no OK (EC-03). A lupa também desarma por 2º clique no botão, não só por retângulo ou Esc.
- 🟢 `legacy-mapping.md`: linhas desatualizadas após a 013 (`_region_rect` está na 85, não 70; `draw_plan` 104, não 88; barra superior 196–281, não 179–242; `handle_zoom_window` 250, não 245; `session/start/end` 108–117, não 104–114; `_guard` 123, não 119). _(Revisão 2026-10-10: linhas corrigidas em legacy-mapping.md)_
- 🟢 `domain.md` RN-WALLS2D-07 resume o fechamento como "3+ trechos"; no lápis o ímã exige 2+ trechos já desenhados (o trecho de fechamento é o 3º).
