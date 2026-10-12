# Mover Sobre — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/move_over/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`; EC-xx os de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Contratos de outras units são citados, não redescritos: `View2D`, `distance_point_segment` e as primitivas de `draw` estão em `_reversa_sdd/canvas2d/design.md`.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `align.py` (132) | não (`collections`; `canvas2d.view` importado **dentro** de `pick`) | Alvos, deslocamentos, escolha pelo clique, folgas | 🟢 |
| Núcleo puro | `reposition.py` (70) | não (`math`) | Rotação pelo centro da base, passo, posição salva | 🟢 |
| Ponte Blender ↔ modelo | `scene.py` (175) | `mathutils`; `aggregates.group`, `selection.classify`, `data.i18n` | Sessão `MoveOver` | 🟢 |
| Estado | `props.py` (68) | sim | PropertyGroups e ponteiros em `WindowManager`/`Scene` | 🟢 |
| Interface | `ops_drag.py` (158), `ops_dialog.py` (382), `ops_move_on_wall.py` (117), `ops_substitute.py` (110), `insertion_plane.py` (98) | sim | Operadores, modais, desenho GPU, keymaps | 🟢 |
| Pacote | `__init__.py` (28) | não no topo | `_modules()` com import tardio; `register` na ordem `props, ops_dialog, ops_drag, ops_move_on_wall, ops_substitute, insertion_plane`; `unregister` na ordem inversa | 🟢 |

## Interface

### `align.py` 🟢

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `FRACTIONS` | constante | `(0.0, 0.30, 0.50, 0.75, 1.0)` | RN-04 |
| `DEFAULT_TOLERANCE_PX` | constante | `12.0` | Padrão de `pick`/`pick_stack` |
| `Target` | `namedtuple('Target', 'kind value')` | — | `kind` ∈ `LEFT, RIGHT, DEPTH, HEIGHT, STACK, WALL_FACE` (strings iguais ao nome); `value` = fração ou `None` |
| `size` | `(box)` | `(dx, dy, dz)` | `hi − lo` por eixo (sem chamador no pacote, 🟢 utilitário _(Revisão 2026-10-10: grep: nenhum uso de `align.size` em caffmob_draw/ nem tests/)_) |
| `translate` | `(box, delta)` | caixa | Soma `delta` a `lo` e `hi` |
| `delta_for` | `(target, box_a, box_b, wall=False)` | `(dx, dy, dz)` | Fórmulas de RN-04; eixos não afetados = 0.0; `kind` desconhecido → `ValueError(f"Alvo desconhecido: {kind}")`; `wall` é ignorado |
| `combine` | `(targets, box_a, box_b, wall=False)` | `(dx, dy, dz)` | `total = [0,0,0]`; para cada alvo, cada eixo com `d[i]` truthy **substitui** `total[i]` (RN-08) |
| `top_view_lines` | `(box_b, wall=False)` | `[(Target, ((x0,y0),(x1,y1)))]` | Ordem: `LEFT` em `x=bx0` de `by0` a `by1`; `RIGHT` em `x=bx1`; com `wall`: `WALL_FACE` em `y=by0` de `bx0` a `bx1` e retorna; senão `DEPTH f` em `y = by0 + f·(by1−by0)` para cada fração |
| `front_view_lines` | `(box_b)` | idem em `(x, z)` | `LEFT`, `RIGHT`, depois `HEIGHT f` em `z = bz0 + f·(bz1−bz0)` |
| `pick` | `(click_px, lines_px, tolerance_px=12.0)` | `list[Target]` | Ver F-01 |
| `pick_stack` | `(click_px, top_line_px, tolerance_px=12.0)` | `bool` | `lo ≤ cx ≤ hi` (X dos extremos, ordenados) **e** `cy > y0 + tol` (`y0` do primeiro ponto) |
| `gaps` | `(box_a, box_b)` | `(dx, dy, dz)` | `dx`: `ax0 ≥ bx1` → `ax0 − bx1`; `bx0 ≥ ax1` → `bx0 − ax1`; senão `−min(ax1 − bx0, bx1 − ax0)`. `dy = ay0 − by0`; `dz = az0 − bz0` |
| `overlaps` | `(box_a, box_b, tolerance=1e-4)` | `bool` | Para os 3 eixos: `a.lo < b.hi − tol` e `b.lo < a.hi − tol` (estrito) |

### `reposition.py` 🟢

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `box_center_base` | `(box)` | `(cx, cy, zmin)` | Centro da planta na cota da base |
| `rotate_point_z` | `(point, center, degrees)` | ponto 3D | Rotação anti-horária em XY; Z preservado |
| `origin_after_rotation` | `(origin, box, degrees)` | ponto 3D | `rotate_point_z(origin, box_center_base(box), degrees)` |
| `rotated_box` | `(box, degrees)` | caixa | AABB dos 4 cantos da planta girados pelo centro da base; `lo.z`, `hi.z` inalterados |
| `step_delta` | `(key, step)` | `(dx,dy,dz)` ou `None` | `RIGHT_ARROW (+s,0,0)`, `LEFT_ARROW (−s,0,0)`, `UP_ARROW (0,+s,0)`, `DOWN_ARROW (0,−s,0)`, `PAGE_UP (0,0,+s)`, `PAGE_DOWN (0,0,−s)`; outra tecla → `None` |
| `absolute_values` | `(b_matrix_apply, box_a)` | tupla | `tuple(b_matrix_apply(box_a[0]))`; só usado em `tests/test_reposition.py` (`scene.world_min` refaz a conta) |
| `side_of` | `(box_a, box_b)` | `'LEFT'`/`'RIGHT'` | `'RIGHT'` se `ax0 + ax1 ≥ bx0 + bx1` |
| `save_position` | `(box_a, box_b, rotation)` | `dict` | RN-13: `{'delta': (ref_x − anchor_x, ay0 − by0, az0 − bz0), 'rotation': float, 'b_side'}`; direita: `anchor_x = bx1`, `ref_x = ax0`; esquerda: `anchor_x = bx0`, `ref_x = ax1` |
| `apply_position` | `(saved, box_a, box_b)` | `(dx,dy,dz)` | Direita: `bx1 + dx − ax0`; esquerda: `bx0 + dx − ax1`; `by0 + dy − ay0`; `bz0 + dz − az0`. `box_a` já deve ter a rotação salva |

### `scene.py` 🟢

Funções do módulo:

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `_frame` | `(obj)` | `Matrix` 4×4 | `LocRotScale(loc, rot, None)` de `matrix_world.decompose()` (sem escala) |
| `_local_box` | `(obj, depsgraph)` | caixa | Cantos de `group.object_corners(obj, depsgraph)` multiplicados componente a componente pela escala decomposta; min/max |
| `_wall_of` | `(obj)` | `Object` ou `None` | `obj.parent` se existir e `parent.get('IS_WALL_BP')` truthy |

`class MoveOver(context, obj_a, obj_b)` — atributos em `Estado Interno`. Métodos:

| Método | Retorno | Comportamento |
|---|---|---|
| `__init__` | — | Ver F-02 |
| `_unrotated_box(delta=None)` | caixa | `a_local_box` transladada por `origin_in_b + (delta or self.delta)` |
| `box_a(delta=None)` | caixa | `_unrotated_box`, envolvida por `reposition.rotated_box(·, rotation)` se `rotation` truthy |
| `original_box_a()` | caixa | Cantos de A pela `original_matrix`, levados por `b_frame_inv` (sem chamador; 🟢 reservado _(Revisão 2026-10-10: grep: `original_box_a` só definido em scene.py:MoveOver)_) |
| `align_to(targets)` | `tuple(delta)` | `step = combine(targets, box_a(), box_b, b_is_wall)`; soma cada eixo com `step[i]` truthy; `preview()` |
| `set_gap(axis, value)` | `None` | Ver F-04 |
| `gaps()` | tupla | `align.gaps(box_a(), box_b)` |
| `_target_matrix()` | `Matrix` | Ver F-03 |
| `set_rotation(degrees)` | `None` | `rotation = float(degrees) % 360.0`; `preview()` |
| `nudge(delta)` | `None` | `self.delta[i] += delta[i]`; `preview()` |
| `world_min()` | tupla | `tuple(b_frame @ Vector(box_a()[0]))` |
| `set_world(axis, value)` | `None` | `current = world_min()`; `target = current` com `target[axis] = value`; `delta += b_frame_inv.to_3x3() @ (target − current)`; `preview()` |
| `saved()` | dict | `reposition.save_position(box_a(), box_b, rotation)` |
| `apply_saved(saved)` | `None` | `rotation = float(saved['rotation']) % 360`; `step = apply_position(saved, box_a(), box_b)`; soma em `delta`; `preview()` |
| `preview()` | `None` | `wall = b if b_is_wall else _wall_of(b)`; se `wall` e `a.parent != wall`: `a.parent = wall`, `a.matrix_parent_inverse = Identity(4)`; depois `a.matrix_world = _target_matrix()` |
| `restore()` | `None` | `a.parent`, `a.matrix_parent_inverse`, `a.matrix_world` ← originais, nessa ordem |
| `overlapping()` | `list[Object]` | Ver F-05 |

### `props.py` 🟢

| PropertyGroup | Registrado em | Campos (`bpy.props`) |
|---|---|---|
| `BTM_PG_MoveOverState` | `WindowManager.btm_move_over` (`PointerProperty`, não salvo) | `enabled: Bool` (nome "Mover Sobre", default `False`, `update=_redraw`); `tolerance_px: Int` (12, 4–40); `step: Float` (0.01, 0.0001–1.0, `subtype='DISTANCE'`, `unit='LENGTH'`); `show_relative: Bool` (`True`, nome "Visualizar posição relativa") |
| `BTM_PG_SavedPosition` | `Scene.btm_saved_positions` (`CollectionProperty`, salvo no `.blend`) + `Scene.btm_saved_positions_index: Int` (0) | `name: String`; `delta: FloatVector(size=3, subtype='TRANSLATION', unit='LENGTH')`; `rotation: Float`; `b_side: Enum [('LEFT',"Esquerda",""),('RIGHT',"Direita","")]` |
| `BTM_PG_InsertionPlane` | `WindowManager.btm_insertion_plane` (`PointerProperty`) | `active: Bool` (`False`, `update=_redraw`); `matrix: FloatVector(size=16)`; `source_name: String` |

- `_redraw(_self, context)`: `tag_redraw()` em toda área `VIEW_3D` de `context.screen` (se houver). 🟢
- `unregister`: `delattr` de `Scene.btm_saved_positions_index`, `Scene.btm_saved_positions`, `WindowManager.btm_insertion_plane` (se existirem), `del WindowManager.btm_move_over`, depois desregistra as classes na ordem inversa. 🟢

### Operadores 🟢

| `bl_idname` | Classe | `bl_options` | Propriedades | `poll` | Arquivo |
|---|---|---|---|---|---|
| `caffmob.move_over_toggle` | `BTM_OT_MoveOverToggle` | `REGISTER` | — | — (sempre) | ops_drag.py |
| `caffmob.move_over_drag` | `BTM_OT_MoveOverDrag` | `REGISTER` | — | área `VIEW_3D`, região `WINDOW`, `mode_enabled(context)` | ops_drag.py |
| `caffmob.move_over_dialog` | `BTM_OT_MoveOverDialog` | `REGISTER, UNDO` | `a_name`, `b_name`: String `{'HIDDEN','SKIP_SAVE'}` | área `VIEW_3D` | ops_dialog.py |
| `caffmob.move_on_wall` | `BTM_OT_MoveOnWall` | `REGISTER, UNDO` | — | área `VIEW_3D`, `context.mode == 'OBJECT'`, `_module_cotas(context)` não `None` | ops_move_on_wall.py |
| `caffmob.move_over_substitute` | `BTM_OT_MoveOverSubstitute` | `REGISTER, UNDO` | `a_name`, `b_name`: String `{'HIDDEN'}`; `module`: Enum (nome "Módulo", `items=_module_items`) | — | ops_substitute.py |
| `caffmob.set_insertion_plane` | `BTM_OT_SetInsertionPlane` | `REGISTER` (sem UNDO) | — | área `VIEW_3D` | insertion_plane.py |
| `caffmob.clear_insertion_plane` | `BTM_OT_ClearInsertionPlane` | `REGISTER` (sem UNDO) | — | `btm_insertion_plane.active` | insertion_plane.py |

Keymap 🟢 `ops_drag.py:register`: em `wm.keyconfigs.addon` (se existir), para `('3D View', 'VIEW_3D')` e para cada nome de `VIEW3D_MODE_KEYMAPS` com `space_type='EMPTY'`: `km.keymap_items.new('caffmob.move_over_drag', 'RIGHTMOUSE', 'PRESS', head=True)`; pares guardados em `_addon_keymaps`. `VIEW3D_MODE_KEYMAPS` = `Object Mode, Mesh, Curve, Curves, Armature, Metaball, Lattice, Font, Pose, Particle, Sculpt, Vertex Paint, Weight Paint, Image Paint, Grease Pencil Edit Mode, Grease Pencil Draw Mode, Grease Pencil Sculpt Mode, Grease Pencil Vertex Paint, Grease Pencil Weight Paint` (19). `unregister` remove cada item engolindo `ReferenceError`/`RuntimeError`.

### Constantes de interface 🟢

| Constante | Valor | Arquivo |
|---|---|---|
| `DRAG_THRESHOLD_PX` | 5 (Manhattan) | ops_drag.py |
| `NAV_EVENTS` | `MIDDLEMOUSE, WHEELUPMOUSE, WHEELDOWNMOUSE, TRACKPADPAN, TRACKPADZOOM, MOUSEROTATE, NDOF_MOTION` | ops_dialog.py |
| `FIELD_LABELS` / `ABS_LABELS` | `("X", "Profundidade", "Altura")` / `("X", "Y", "Z")` | ops_dialog.py |
| `ROTATION`, `STEP`, `FIELD_COUNT` | 3, 4, 5 | ops_dialog.py |
| `ARROWS` | `RIGHT_ARROW, LEFT_ARROW, UP_ARROW, DOWN_ARROW, PAGE_UP, PAGE_DOWN` | ops_dialog.py |
| `MAX_SAVED_BUTTONS` | 4 | ops_dialog.py |
| `PCT` | `{0.0:"0%", 0.30:"30%", 0.50:"50%", 0.75:"75%", 1.0:"100%"}` | ops_dialog.py |
| Tolerância de `overlapping` | 1e-3 m | scene.py |
| Raio de `intersect_line_plane` | `origin + vector·1e6` | ops_move_on_wall.py |
| Largura do diálogo Substituir | 360 px, título "Substituir por" | ops_substitute.py |

## Fluxo Principal

1. 🟢 **Modo.** `caffmob.move_over_toggle` (ou o botão do HUD `operators/viewport_hud.py:_MoveOverButton.on_click`, ou o toggle no painel `ui/object_properties.py`) inverte `btm_move_over.enabled`. Relatório: "Mover Sobre ligado: arraste com o botão direito." / "Mover Sobre desligado: o botão direito volta ao normal.". Fonte: `ops_drag.py:BTM_OT_MoveOverToggle.execute`.
2. 🟢 **Arraste** (`ops_drag.py:BTM_OT_MoveOverDrag`):
   1. `invoke`: `start = (mouse_region_x, mouse_region_y)`; `raycast(context, start)` = `region_2d_to_origin_3d` + `region_2d_to_vector_3d` + `scene.ray_cast(evaluated_depsgraph, origin, direction)` → objeto ou `None` (também `None` sem `region`/`region_data`). `a = classify.movable_root(hit)`; `None` → `{'FINISHED'}` (clique consumido, RN-17).
   2. Com A: `cursor = start`, `b = None`, `draw_handler_add(_draw, (), 'WINDOW', 'POST_PIXEL')`, `modal_handler_add`, `status_text_set("Mover Sobre: solte o botão direito sobre o objeto de referência  |  Esc: cancelar  ({A})")` → `RUNNING_MODAL`.
   3. `_draw`: `draw.begin()`; cor `reference` se há B, senão `moving`; `draw.lines(draw.dashed(start, cursor))`; texto `"A → B"` ou `"A"` em `(cursor.x + 12, cursor.y + 10)`; `draw.end()`.
   4. `modal`: `MOUSEMOVE` → atualiza `cursor`, refaz o raycast, `candidate = reference_root(hit)`, `b = candidate` se não `None` e ≠ A, senão `None`; `tag_redraw`. `RIGHTMOUSE RELEASE` → `moved = |Δx| + |Δy|`; `_finish`; se `moved ≥ 5` e `b`: `bpy.ops.caffmob.move_over_dialog('INVOKE_DEFAULT', a_name=a.name, b_name=b.name)`; devolve `FINISHED`. `ESC` (qualquer `value`) → `_finish`, `CANCELLED`. Qualquer outro evento → `RUNNING_MODAL` (consumido).
   5. `_finish`: remove o handler, `status_text_set(None)` (engole `AttributeError`/`RuntimeError`), `tag_redraw`. `cancel()` chama `_finish`.
3. 🟢 **Janela** (`ops_dialog.py:BTM_OT_MoveOverDialog.invoke`): `a, b = scene.objects.get(a_name/b_name)`; `MoveOver(context, a, b)` (`ValueError` → `report WARNING`, `CANCELLED`); desseleciona tudo; seleciona A e B; `view_layer.objects.active = B` (RN-05 da 002); `mo.preview()` (A assume a rotação de B, RN-03); `hot = {'top': [], 'front': [], 'stack': False}`; `mouse`; `typing = None`, `buffer = ""`; `warning = ""`, `warned = False`; `tolerance = btm_move_over.tolerance_px`; `state = btm_move_over`; `_layout`; `_fit_views`; handler `POST_PIXEL`; `modal_handler_add`; texto de status "Mover Sobre  |  Clique perto de um lado ou de uma linha  |  Tab: digitar  |  Setas/PgUp/PgDn: passo  |  Enter: confirmar  |  Esc: cancelar"; `RUNNING_MODAL`.
4. 🟢 **Layout** (`_layout`, `s = ui_scale`, coordenadas locais da região): `pad = 12s`, `pane_w = 330s`, `pane_h = 250s`; `width = 3·pad + 2·pane_w`; `height = 8·pad + pane_h + 150s`; painel centralizado (`x = max(pad, (region.width − width)/2)`, idem `y`). Título em `(x + pad, y + height − pad − 14s)`. `top_y = y + height − pad − 22s − pane_h`; Superior em `(x + pad, top_y)`, Frontal em `(x + 2pad + pane_w, top_y)`. Linha 1 (`row_y = top_y − pad − 26s`): 3 campos de largura `field_w = (width − 4pad)/3`, altura 26s. Linha 2 (`row2 = row_y − pad − 26s`): Rotação, Passo e botão Relativa/Absoluta. Linha 3 (`row3 = row2 − pad − 26s`): `small = (width − 2pad − 5pad)/6`; Salvar posição, 4 posições salvas, Substituir. Aviso em `(x + pad, row3 − pad − 14s)`. Confirmar e Cancelar 120s × 28s no rodapé à direita (`y + pad`).
5. 🟢 **Enquadrar** (`_fit_views`): união das caixas de A (`box_a()`) e B; `inset = 18s`; área útil de cada painel = `(x + inset, y + inset, w − 2inset, h − 2inset − 14)`; `View2D(...).fit(((x0,y0),(x1,y1)), margin=0.15)` com `(X, Y)` na Superior e `(X, Z)` na Frontal (contrato `canvas2d` F-03). Chamado ao abrir e após cada alteração de posição (clique, digitação, posição salva, passo).
6. 🟢 **Desenho** (`_draw`): painel (`COLORS['panel']` + contorno); título "Mover Sobre — {A} sobre {B} (referência)" tamanho 13; para cada vista `_draw_pane`: fundo `pane`, contorno, título ("Superior (frente embaixo)" / "Frontal") em `muted`; B com `draw.box` cor `reference`, preenchimento `(0.25, 0.65, 1.0, 0.15)`; A cor `moving`, preenchimento `(1.0, 0.62, 0.15, 0.12)`; cada alvo: realçado (`target_hot`, linha cheia) se está em `hot`, senão tracejado `target`; rótulo `PCT` (tamanho 10) à direita do segmento nas linhas de fração da vista (DEPTH na Superior, HEIGHT na Frontal); na Frontal com `hot['stack']`, linha do topo realçada e "Empilhar". Campos: valor ativo = `buffer + "▏"`; Rotação `f"{rotation:.1f}°"` com vírgula; Passo e distâncias via `draw.length_label`; rótulos traduzidos. Botões: "Posição relativa"/"Posição absoluta", "Salvar posição", nomes das posições salvas, "Substituir", aviso em `warning`, "Confirmar" (`primary`), "Cancelar"; `hot` quando o mouse está sobre o botão.
7. 🟢 **Eventos** (`modal`, ver F-06).
8. 🟢 **Confirmar** (`_confirm`): F-07. **Cancelar** (`cancel`): `mo.restore()` + `_finish` → `CANCELLED`.

### F-01 `align.pick` 🟢 `align.py:pick`
1. `best = {}`; para cada `(target, (p0, p1))` em `lines_px`: `dist = canvas2d.view.distance_point_segment(click, p0, p1)`.
2. `dist > tol` → ignora (tolerância inclusiva).
3. Eixo = `'x'` se `kind ∈ {LEFT, RIGHT}`, senão `'v'`; guarda se o eixo não tem melhor ou `dist` é menor (empate: o primeiro na ordem das linhas fica).
4. Devolve `[t for _, t in best.values()]` (ordem de inserção dos eixos).

### F-02 `MoveOver.__init__` 🟢 `scene.py`
1. `a = movable_root(obj_a)`, `b = reference_root(obj_b)`; `None` ou `a == b` → `ValueError(tr("Esses objetos não podem ser usados no Mover Sobre."))`.
2. `b_is_wall = classify(b).kind == WALL`.
3. Guarda `original_parent`, `original_matrix = a.matrix_world.copy()`, `original_parent_inverse`.
4. `depsgraph = evaluated_depsgraph_get()`; `b_frame = _frame(b)`, `b_frame_inv`; `box_b = _local_box(b)`; `a_local_box = _local_box(a)`; `a_scale` = escala decomposta de A.
5. `origin_in_b = b_frame_inv @ original_matrix.translation`; `delta = Vector((0,0,0))`; `rotation = 0.0`.

### F-03 `_target_matrix` 🟢 `scene.py` (ver `_reversa_sdd/flowcharts/move_over-target_matrix.md`)
1. `local = origin_in_b + delta`; com `rotation`: `local = origin_after_rotation(local, _unrotated_box(), rotation)`.
2. `loc = b_frame @ local`; `rot` = rotação de `b_frame`; com `rotation`: `rot = rot @ Matrix.Rotation(radians(rotation), 3, 'Z').to_quaternion()`.
3. `Matrix.LocRotScale(loc, rot, a_scale)`.

### F-04 `set_gap(axis, value)` 🟢 `scene.py`
- `axis 0`: se `ax0 + ax1 ≥ bx0 + bx1` (A à direita) `delta.x += (bx1 + value) − ax0`; senão `delta.x += (bx0 − value) − ax1`.
- `axis 1`: `delta.y += (by0 + value) − ay0`. `axis 2`: `delta.z += (bz0 + value) − az0`. Depois `preview()`.

### F-05 `overlapping()` 🟢 `scene.py`
1. AABB mundial de A = min/max de `_target_matrix() @ c` para `c` em `group.object_corners(a)`.
2. Para cada `obj` de `scene.objects`, exceto `a`, com `classify.module_library(obj)` truthy: AABB mundial de `obj.matrix_world @ c` para `c` em `obj.evaluated_get(depsgraph).bound_box`.
3. `align.overlaps(box, other, tolerance=1e-3)` → acrescenta. B entra na verificação como qualquer outro módulo.

### F-06 `modal` da janela 🟢 `ops_dialog.py:modal` (ordem exata)
1. `context.area.tag_redraw()`; `pixel`; `over_panel = point_in_rect(pixel[0], pixel[1], panel)`. _(Revisão 2026-10-10: ops_dialog.py:302; assinatura `point_in_rect(x, y, rect)`)_
2. `NAV_EVENTS` fora do painel → `PASS_THROUGH`.
3. `MOUSEMOVE` → `mouse = pixel`; `_hits(pixel)` → `hot` → `RUNNING_MODAL`.
4. Campo em edição e `PRESS`: Enter/NumEnter → `_commit_typing`; `ESC` → sai da edição (descarta buffer); `TAB` → se `buffer` não vazio chama `_commit_typing`; se a gravação **deu certo** ela zera `typing`, e a linha seguinte (`0 if typing is None else (typing + 1) % 5`) leva ao **campo 0**, não ao próximo; se falhou, passa ao próximo campo **mantendo o buffer inválido**; com buffer vazio passa ao próximo campo _(Revisão 2026-10-10: ops_dialog.py:316-319; texto anterior dizia sempre `(typing + 1) % 5`)_. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-15):** Tab grava e vai sempre ao próximo campo; se a gravação falhar, fica no campo atual com o aviso (guardar o índice antes de `_commit_typing`). Pendência de implementação: DT-01; `BACK_SPACE` apaga o último caractere; `event.unicode` em `"0123456789,.-mc °"` é acrescentado. Qualquer outro evento (inclusive cliques) é consumido → `RUNNING_MODAL`.
5. `LEFTMOUSE PRESS`, nesta ordem: Confirmar → `_confirm`; Cancelar → `cancel`, `CANCELLED`; um dos 5 campos → `typing = i`, `buffer = ""`; Relativa/Absoluta → inverte `state.show_relative`; Salvar posição → `_save_position`; botão de posição salva → `_apply_saved`; Substituir → `_substitute`; senão `_apply_click(pixel)`.
6. Outros `PRESS`: Enter/NumEnter → `_confirm`; `ESC`/`RIGHTMOUSE` → `cancel`, `CANCELLED`; `TAB` → `typing = 0`; `ARROWS` → `nudge(step_delta(tipo, state.step))` + `_fit_views`.
7. Demais → `RUNNING_MODAL`.

- `_hits(pixel)`: dentro da Superior → `('top', pick(pixel, _top_lines(), tolerance), False)`; dentro da Frontal → `targets = pick(...)`, `stack = not targets and pick_stack(pixel, _front_top_line_px(), tolerance)`; fora → `(None, [], False)`. `_top_lines` usa `top_view_lines(box_b, b_is_wall)`; as linhas são convertidas por `view.to_screen`.
- `_apply_click`: sem painel → nada; `stack` → `[Target(STACK, None)]`; com alvos → `align_to`, limpa `warned`/`warning`, `_fit_views`.
- `_commit_typing`: Rotação → `float(buffer.replace(",", ".").replace("°", "").strip() or 0.0)`; demais → `units.parse_length(buffer, units.get_scene_length_unit(), allow_negative=typing != STEP, allow_zero=typing != STEP)`. `ValueError` → `warning = str(exc) or "Valor inválido"`, devolve `False` (edição continua). Sucesso → `set_rotation` / `state.step = value` / `set_gap` (relativo) / `set_world` (absoluto); limpa edição, `warned`, `warning`; `_fit_views`.
- `_save_position`: `items.add()`, `name = "Posição {len(items)}"`, copia `delta`, `rotation`, `b_side` de `mo.saved()`; `warning = "{nome} salva ({A} em relação a {B})."`.
- `_apply_saved(item)`: `mo.apply_saved({...})`; `warned = False`; `warning = "{nome} aplicada."`; `_fit_views`.
- `_saved_items()`: `list(bpy.context.scene.btm_saved_positions)[-4:]`.
- `_substitute`: guarda nomes, `_finish` (sem `restore`), `bpy.ops.caffmob.move_over_substitute('INVOKE_DEFAULT', a_name, b_name)`, devolve `FINISHED` (a posição atual de A é gravada como passo de desfazer da janela).

### F-07 `_confirm` 🟢 `ops_dialog.py`
1. `settings = getattr(scene, 'btm_settings', None)`; se `settings.collision_global` e `not warned`: `overlapping()`; não vazio → `warning = "Sobrepõe: {até 4 nomes}. Confirme de novo para gravar mesmo assim."`, `warned = True`, `RUNNING_MODAL`.
2. Senão `_finish`, `report INFO "{A} alinhado a {B}."`, `FINISHED`.

### F-08 Mover na Parede 🟢 `ops_move_on_wall.py`
1. `_module_cotas(context)`: `scene_cotas.for_object(active_object, scene)`; devolve só se `mc.on_wall`.
2. `invoke`: `mc`, `original = mc.root.location.copy()`, `grab = _wall_point(event)`; `None` → `WARNING "Não foi possível projetar o mouse na parede."`, `CANCELLED`; `start = mc.placement`; modal; cabeçalho.
3. `_wall_point`: região = primeira `WINDOW` da área (o botão do painel lateral também invoca); `rv3d = area.spaces.active.region_3d`; `mouse = (event.mouse_x − region.x, event.mouse_y − region.y)`; plano: ponto `wall.matrix_world @ (0, back_y − mc.depth, 0)`, normal `(wall 3×3 @ (0,1,0)).normalized()`; `intersect_line_plane(origin, origin + vector·1e6, ponto, normal)`; devolve o ponto no referencial da parede ou `None`.
4. `modal`: `tag_redraw`; `MIDDLEMOUSE`/rodas → `PASS_THROUGH`; `ESC`/`RIGHTMOUSE PRESS` → `root.location = original`, `CANCELLED`; `LEFTMOUSE`/Enter/NumEnter `PRESS` → `FINISHED`; `MOUSEMOVE` → `_move(point, event.shift)` se o ponto existir.
5. `_move`: Shift → `z0 = max(0, start.z0 + point.z − grab.z)`; senão `x0 = cotas.slide(current, mc.obstacles(), mc.wall_length, start.x0 + point.x − grab.x, PlacementMixin.avoid_overlap(context))`; `root.location = (x0, back_y, z0)`; `mc.placement = new`; cabeçalho.
6. `_header`: `mc.compute()`; `area.header_text_set("Anterior {} | Posterior {} | Inferior {} | Shift: altura | Clique confirma | Esc cancela")` com `units.format_length(v, unidade da cena)` ou "—". `_end` limpa o cabeçalho.

### F-09 Substituir 🟢 `ops_substitute.py` (ver `_reversa_sdd/flowcharts/move_over-substitute.md`)
1. `invoke` → `invoke_props_dialog(self, width=360, title="Substituir por")`. `_module_items` = `[(e["blend"], f"{e['category']} / {e['name']}", "") for e in library_io.list_modules()]` guardado no global `_ITEMS` (mantém as strings vivas); vazio → `[("", "Nenhum módulo salvo", "")]`.
2. `execute`: `a, b = bpy.data.objects.get(...)`; `entry` = item de `list_modules()` com `blend == module`; falta algum → `WARNING "Escolha um módulo da biblioteca do usuário"`, `CANCELLED`.
3. `substitute(context, a, b, entry)`: `root, loaded, warnings = library_io.load(context, entry)`; `root is None` → remove os objetos de `loaded` ainda existentes, devolve `(None, warnings)`.
4. `root.matrix_world = a.matrix_world.copy()`; `root.parent = a.parent`; se A tem pai: `matrix_parent_inverse` de A e `matrix_world` reaplicada; `view_layer.update()`.
5. `frame = _frame(b)`; `box_a = _tree_box(frame_inv, a)`; `box_b = _local_box(b, depsgraph)`; `box_new = _tree_box(frame_inv, root)`. `_tree_box` = união das caixas (bound box avaliado → `frame_inv @ matrix_world`) de raiz + descendentes `MESH`, visíveis (`not hide_get()`), com `display_type ∉ {WIRE, BOUNDS}`; nenhuma → caixa da raiz.
6. `side = side_of(box_a, box_b)`; `dx` = `xmin(A) − xmin(novo)` (RIGHT) ou `xmax(A) − xmax(novo)` (LEFT); `delta = (dx, ymin(A) − ymin(novo), zmin(A) − zmin(novo))`; `root.matrix_world.translation += frame.to_3x3() @ delta`.
7. Remove `[a] + reversed(a.children_recursive)` que ainda existam (`do_unlink=True`); devolve `(root, warnings)`.
8. `execute`: `new is None` → `WARNING` com avisos juntos por " | ", `CANCELLED`; senão desseleciona tudo, seleciona e ativa o novo, `report` `WARNING` (avisos) ou `INFO "{A} substituído por {novo}"`, `FINISHED`.

### F-10 Plano de inserção 🟢 `insertion_plane.py`
1. `invoke`: `modal_handler_add`, status "Plano de inserção  |  Clique na face  |  Esc/botão direito: cancelar", cursor `EYEDROPPER`, `RUNNING_MODAL`.
2. `modal`: `LEFTMOUSE PRESS` → raycast na região do evento; `_end` (limpa status e cursor `DEFAULT`); sem acerto → `WARNING "Nenhuma face sob o cursor"`, `CANCELLED`; com acerto → `set_plane(location, normal, obj.name)`. `ESC`/`RIGHTMOUSE PRESS` → `_end`, `CANCELLED`. `MIDDLEMOUSE`/rodas → `PASS_THROUGH`; demais → `RUNNING_MODAL`.
3. `set_plane`: `matrix = [v for row in _plane_matrix(location, normal) for v in row]` (linha a linha); `source_name`; `active = True`; `INFO "Plano de inserção: face de {}"`; `FINISHED`. `_plane_matrix = Translation(location) @ normal.normalized().to_track_quat('Z','Y').to_matrix().to_4x4()`.
4. `execute` (sem invoke): `WARNING "Use com o botão direito sobre uma face"`, `CANCELLED`.
5. `clear`: `active = False`, `FINISHED`.
6. Consumo (fora da unit): `hb_snap.py:snap_to_grid` reconstrói `Matrix([matrix[i*4:(i+1)*4] for i in range(4)])` e usa `translation` e `col[2].xyz.normalized()` quando a vista não é ortográfica lateral.

## Fluxos Alternativos

- **A ou B inválidos ao abrir a janela**: `WARNING` com a mensagem do `ValueError`, `CANCELLED`, nada muda (RN-02). 🟢 `ops_dialog.py:invoke`
- **Referência é parede**: Superior só com lados e face; A vira filho da parede na prévia; `WALL_FACE` põe o fundo de A na face (RN-05, RN-14). 🟢
- **B está numa parede (pai com `IS_WALL_BP`)**: A é reparentado à parede de B mesmo que estivesse em outra parede ou solto. 🟢 `scene.py:preview`
- **Campo em edição**: cliques e Esc do modal não confirmam nem cancelam; Esc só sai da edição. 🟢 `ops_dialog.py:modal`
- **Substituir**: a janela fecha com `FINISHED` (posição atual mantida) e abre o diálogo; cancelar o diálogo não desfaz a posição. 🟢 `ops_dialog.py:_substitute`
- **Sem `btm_settings` na cena**: Confirmar nunca avisa sobreposição; já o Mover na Parede considera "Evitar Sobreposição" ligado. 🟢 `ops_dialog.py:_confirm`; `hb_placement.py:avoid_overlap`
- **Plano de inserção chamado por `execute`** (ex. sem `INVOKE_DEFAULT`): só avisa. 🟢

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `selection/classify.py` | `movable_root`, `reference_root`, `classify(...).kind == WALL`, `module_library` (raízes com `IS_*_CABINET_CAGE`/`IS_CLOSET_STARTER_CAGE` ou tipo BTM `MODULE`) | 🟢 |
| `aggregates/group.py:object_corners(obj, depsgraph)` | Cantos locais; Empty usa as malhas descendentes no espaço do Empty (sem malhas → 8 vetores nulos) | 🟢 |
| `canvas2d` (`draw`, `view.View2D`, `view.distance_point_segment`) | Contratos em `_reversa_sdd/canvas2d/design.md` | 🟢 |
| `hb_gpu_draw.point_in_rect` | Hit-test dos retângulos `(x, y, w, h)` | 🟢 |
| `data/units.py` | `parse_length(text, default_unit, allow_negative, allow_zero)` (levanta `ValueError` em português), `get_scene_length_unit`, `format_length` | 🟢 |
| `data/i18n.py` | `tr`, `N_`; textos em `data/translations/move_over.json` (48 chaves) | 🟢 |
| `measure/scene_cotas.py:for_object` | `ModuleCotas` com `root`, `wall`, `on_wall`, `placement` (`x0, width, z0, height, back_y`), `depth`, `wall_length`, `obstacles()`, `compute()` | 🟢 |
| `measure/cotas.py:slide` | Limita `x0` (RN-20) | 🟢 |
| `hb_placement.PlacementMixin.avoid_overlap(context)` | Lê `btm_settings.collision_global` (ligado se ausente) | 🟢 |
| `customize/library_io.py` | `list_modules()` → dicts com `blend`, `category`, `name`; `load(context, entry)` → `(root, loaded, warnings)` | 🟢 |
| `bpy_extras.view3d_utils`, `mathutils`, `mathutils.geometry.intersect_line_plane`, `Scene.ray_cast` | Raycast e matrizes | 🟢 |

Consumidores 🟢 (grep): `caffmob_draw/__init__.py` (registro), `operators/viewport_hud.py` (`_MoveOverButton`: inverte `enabled` direto, visível com o modo ligado ou em ambiente), `ui/sidebar_vocab.py` (ações `MOVE_OVER` → `move_over_toggle`, `INSERTION_PLANE`, `CLEAR_INSERTION_PLANE`), `ui/context_menu.py` (Mover Sobre nas ações do item; plano de inserção sempre; "Limpar" só com plano ativo), `ui/object_properties.py` (toggle `enabled`, `step`, `show_relative`, plano de inserção com `INVOKE_DEFAULT`; botão "Mover na Parede" quando `mc.on_wall`), `hb_snap.py` (plano), `stick/settle.py` (`_MOVE_IDS` inclui `caffmob.move_on_wall`, `caffmob.move_over_drag`, `caffmob.move_over_dialog`: o assentar espera esses modais).

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Modo como propriedade + atalho com `poll`, sem modal permanente (autosave continua) | `ops_drag.py` docstring; `viewport_hud.py:_MoveOverButton` | 🟢 |
| Atalho também nos 19 mapas de modo da viewport (D-29, A001 da 002) | Comentário em `ops_drag.py` antes de `VIEW3D_MODE_KEYMAPS` | 🟢 |
| Todo o alinhamento no referencial de B sem escala, com A forçado à rotação de B (RN-08 da 002) | `scene.py` docstring; `_frame` | 🟢 |
| Matemática pura separada para testar fora do Blender | `align.py`/`reposition.py` docstrings; `__init__.py:_modules` | 🟢 |
| Janela GPU sobre a própria viewport (`POST_PIXEL`), não uma área nova | `ops_dialog.py` docstring (D-15) | 🟢 |
| Rotação pelo centro da base de A (D-21); posições salvas relativas ao canto do mesmo lado (D-22) | `reposition.py` docstring | 🟢 |
| A vira filho da parede de B para as cotas continuarem valendo | `scene.py` docstring | 🟢 |
| Plano de inserção é estado de sessão, sem UNDO | `insertion_plane.py` (`bl_options = {'REGISTER'}`); `props.py` (WindowManager) | 🟢 |
| Substituir só cobre a biblioteca do usuário "nesta versão" | `ops_substitute.py` docstring (D-23) | 🟢 |

## Estado Interno

- 🟢 `MoveOver` (memória, uma por janela): `context`, `a`, `b`, `b_is_wall`, `original_parent`, `original_matrix`, `original_parent_inverse`, `b_frame`, `b_frame_inv`, `box_b`, `a_local_box`, `a_scale`, `origin_in_b`, `delta` (`Vector`), `rotation` (graus, `[0, 360)`). `box_b` e `a_local_box` são calculados uma vez; geometria alterada durante a janela não é relida.
- 🟢 `BTM_OT_MoveOverDialog`: `mo`, `hot`, `mouse`, `typing` (`None` ou 0–4), `buffer`, `warning`, `warned`, `tolerance`, `state`, retângulos do layout (`panel`, `pane_top`, `pane_front`, `fields[5]`, `button_mode`, `button_save`, `saved_buttons[4]`, `button_substitute`, `button_ok`, `button_cancel`, `title_pos`, `warning_pos`), `view_top`, `view_front`, `_handle`. O layout não é recalculado se a região mudar de tamanho.
- 🟢 `BTM_OT_MoveOverDrag`: `a`, `b`, `start`, `cursor`, `_handle`. `_addon_keymaps` (lista global do módulo).
- 🟢 `BTM_OT_MoveOnWall`: `mc`, `original`, `grab`, `start`.
- 🟢 Persistente: `Scene.btm_saved_positions` (arquivo); `WindowManager.btm_move_over` e `btm_insertion_plane` (sessão; o `WindowManager` não é salvo como dado de cena — 🟡 comportamento do Blender, conforme docstring de `props.py`).

## Observabilidade

- 🟢 Só `self.report` (`INFO`/`WARNING`), texto de status/cabeçalho e o aviso desenhado no painel. Nenhum log. Exceções tratadas: `ValueError` (construtor e digitação), `AttributeError`/`RuntimeError` em `status_text_set(None)`, `ReferenceError`/`RuntimeError` na remoção do keymap. Mensagens de `float()` na Rotação aparecem cruas (em inglês) no painel (EC-08).

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-16):** usar `_tree_box` também nas caixas de A/B do alinhamento e em `overlapping`. 🟢 (código) hoje usam a raiz (`object_corners`) e podem ignorar frentes e puxadores. Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-17):** `move_on_wall` e `set_insertion_plane` definem `cancel()` que restaura a posição e chama `_end`. 🟢 (código) hoje não definem: se o modal for interrompido pelo Blender, a posição/cabeçalho/cursor não são restaurados (EC-10). Pendência de implementação: DT-03.
- 🟡 Sem meta de desempenho verificada para prévia e redesenho — decisão: medir/testar (DT-06; questions.md#pergunta-76).
- 🟢 `delta_for`/`combine` aceitam `wall` e o ignoram (resíduo de assinatura). _(Revisão 2026-10-10: align.py:34-62, `wall` só repassado, nunca lido)_
- 🟢 `original_box_a`, `align.size` e `reposition.absolute_values` não têm chamador no pacote (o último é usado só em teste). _(Revisão 2026-10-10: grep; tests/test_reposition.py:33)_

## Divergências entre artefatos e código

- 🟢 `_reversa_forward/002…/requirements.md` RF-26 pede "saída por Esc" do modo e RF-27 pede "destaca o objeto sob o cursor": o código não desliga o modo por Esc e só mostra o nome de B e muda a cor da linha (sem realce do objeto no 3D).
- 🟢 `_reversa_forward/003…/requirements.md` RF-27 fala em "módulo do catálogo"; o código busca só a biblioteca do usuário (`library_io.list_modules`).
- 🟢 `code-analysis.md` §6.2 diz que `absolute_values` não tem chamador: vale para o pacote, mas `tests/test_reposition.py:test_absoluta_nao_move` o usa.
- 🟢 `flowcharts/move_over.md` §1 desenha "Esc → CANCELLED" no arraste como `PRESS`; o código aceita `ESC` com qualquer `value`. §3 diz "Translation local": a translação é o ponto de acerto **no mundo** devolvido por `scene.ray_cast`.
- 🟢 `data-dictionary.md` §5.7 lista `btm_settings.collision_global` entre "idprops"; é uma propriedade `bpy.props` de `btm_settings` (`data/properties.py`).
- 🟢 `ops_dialog.py` docstring cita "RF-28 a RF-33" (IDs da 002); estes IDs não correspondem aos RF-xx deste `requirements.md`.
