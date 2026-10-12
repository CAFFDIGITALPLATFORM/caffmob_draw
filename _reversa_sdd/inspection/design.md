# Inspeção de frentes (inspection) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/inspection/` em 2026-10-10 (sem alterações pendentes na pasta). IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `pivot_math.py` | não (`math`) | Poses, limites, encaixe, conversões | 🟢 |
| Núcleo puro | `room_door_math.py` | não (`math`, `namedtuple`) | Folhas da porta de ambiente | 🟢 |
| Contrato | `fronts.py` | não diretamente (`data.i18n.N_`, `pivot_math`; adaptadores importados tarde) | `Front`, descoberta, raiz de módulo | 🟢 |
| Adaptadores | `adapters/frameless.py`, `face_frame.py`, `closets.py`, `btm.py`, `room_doors.py`, `aggregate_leaf.py` | `mathutils` (e `bpy` em frameless/aggregate_leaf) | Uma linha de produto cada | 🟢 |
| Cena | `room_door_leaf.py` | `bpy`, `bmesh`, `hb_types` | Pivôs e folhas cinzas da porta de ambiente | 🟢 |
| Estado | `props.py` | `bpy` | `WindowManager.btm_inspection` | 🟢 |
| Operadores | `ops_inspect.py`, `ops_interference.py` | `bpy`, `bpy_extras.view3d_utils` | 4 operadores | 🟢 |
| Detector | `interference.py` | `bmesh`, `mathutils`, `BVHTree` | Envelope e choque | 🟢 |
| Viewport | `gizmo.py`, `overlay.py` | `bpy`, `gpu`, `blf`, `gpu_extras` | Gizmo e destaque | 🟢 |
| Handlers | `save_guard.py` | `bpy`, `persistent` | Salvar fechado | 🟢 |

🟢 Registro (`__init__.py:_modules`, import tardio): `props, ops_inspect, ops_interference, gizmo, overlay, save_guard`; `unregister` na ordem inversa. O pacote principal chama `inspection.register()` (`caffmob_draw/__init__.py:292`) e `inspection.unregister()` (linha 374).

## Interface

### `pivot_math.py`

| Símbolo | Assinatura / valor | Comportamento | Confiança |
|---|---|---|---|
| `MAX_ANGLE` | `90.0` | teto comum (D-20 da 001) | 🟢 |
| `SNAP_STOPS`, `SNAP_TOLERANCE` | `(0.0, 45.0, 90.0)`, `5.0` | paradas do dial | 🟢 |
| `FACE_FRAME_MAX_ANGLE`, `CLOSETS_MAX_ANGLE`, `BTM_MAX_ANGLE` | `100.0`, `110.0`, `90.0` | RN-14 | 🟢 |
| `clamp_angle(degrees, maximum=MAX_ANGLE)` | `max(0, min(maximum, degrees))` em float | — | 🟢 |
| `clamp_fraction(f)` | `max(0, min(1, f))` | — | 🟢 |
| `snap_angle(degrees, stops, tolerance)` | limita com `clamp_angle` (teto **90** fixo), escolhe a parada mais próxima; devolve a parada se `|parada − valor| ≤ tolerance`, senão o valor limitado | EC-02 | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-62):** "Abrir 90°" (e o clique) ficam em 90°; o dial passa a ser limitado por `front.max_value` em vez do teto fixo de 90, coerente com a varredura e com o `max_angle` da 003. Pendência de implementação: DT-02 |
| `degrees_to_fraction(deg, legacy_max)` | `clamp_fraction(clamp_angle(deg)/legacy_max)` | 90° no face frame → 0,9 | 🟢 |
| `fraction_to_degrees(f, legacy_max)` | `clamp_angle(f·legacy_max)` | 1,0 no closets → 90 (limitado) | 🟢 |
| `dot, cross, scale, add, sub, length, mat_vec` | tuplas 3D; matriz = tupla de linhas | — | 🟢 |
| `normalize(a)` | `ValueError("Vetor nulo")` se comprimento `< 1e-12` | — | 🟢 |
| `axis_angle_matrix(axis, radians)` | Rodrigues com eixo normalizado | — | 🟢 |
| `matrix_to_euler_xyz(m)` | `R = Rz·Ry·Rx`; `ry = asin(clamp(−m[2][0]))`; se `|cos ry| > 1e-9`: `rx = atan2(m21, m22)`, `rz = atan2(m10, m00)`; senão `rx = atan2(−m12, m11)`, `rz = 0` | — | 🟢 |
| `swing_sign(axis, free, outward)` | `+1` se `dot(cross(normalize(axis), free), outward) ≥ 0`, senão `−1` | sentido que leva a borda livre para a face frontal | 🟢 |
| `edge_rotation(axis, hinge_offset, free, outward, degrees, maximum=MAX_ANGLE)` | `angle = rad(clamp_angle(deg, max))·swing_sign`; `R = axis_angle_matrix`; devolve `(matrix_to_euler_xyz(R), hinge_offset − R·hinge_offset)` | pivô na aresta, pose em deltas | 🟢 |
| `slide(direction, travel, fraction)` | `normalize(direction)·travel·clamp_fraction(fraction)` | — | 🟢 |
| `frame_from_extents(rotation, length_vec, width_vec, thickness_vec)` | aplica `rotation` aos 3 vetores locais | — | 🟢 |
| `side_hinge(L, W, T)` | `{'axis': L, 'hinge_offset': (0,0,0), 'free': W, 'outward': T}` | — | 🟢 |
| `top_hinge(L, W, T)` | eixo `W`; se `L.z ≥ 0`: offset `L`, free `−L`; senão offset 0, free `L` | basculante | 🟢 |
| `bottom_hinge(L, W, T)` | eixo `W`; se `L.z ≥ 0`: offset 0, free `L`; senão offset `L`, free `−L` | basculante p/ baixo; **sem consumidor** nos adaptadores atuais | 🟢 |
| `pose_for(hinge, degrees, maximum=MAX_ANGLE)` | `edge_rotation(**hinge)` | — | 🟢 |

### `room_door_math.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `Leaf` | `namedtuple('Leaf', 'side hinge_x hinge_y dx dy length thickness height rot_sign')` | 🟢 |
| `leaves(width, wall_depth, height, is_left, is_double, swing_inside, door_thickness)` | `sign = −1 if swing_inside else 1`; `hinge_y = wall_depth if swing_inside else 0`; `dy = −sign`; dupla: `(('L',0,1),('R',width,−1))`, `length = width/2`; simples: `('R',width,−1)` se `is_left`, senão `('L',0,1)`, `length = width`; `rot_sign = sign·dx` | 🟢 |
| `leaf_corners(leaf)` | 8 cantos de `x∈{0, dx·length}`, `y∈{0, dy·thickness}`, `z∈{0, height}` | 🟢 |
| `open_tip(leaf, degrees)` | ponta livre no piso, rotação 2D por `rot_sign·degrees` em torno da dobradiça | 🟢 (sem consumidor fora dos testes) |

### `fronts.py` — contrato `Front`

| Membro | Contrato | Confiança |
|---|---|---|
| Constantes | `DOOR`, `FLIP_UP`, `FLIP_DOWN`, `DRAWER`, `PULLOUT`; `HINGED = {DOOR, FLIP_UP, FLIP_DOWN}`; `KIND_LABELS` com `N_()` | 🟢 |
| `Front(kind, module_root, obj, key)` | `obj` = objeto representativo (clique/seleção/rótulo); `key` = identificador de sessão `"<LIB>:<nome>"`; `library` por subclasse | 🟢 |
| `hinged`, `max_value`, `label`, `clamp`, `is_open`, `open_value` | RN-01 a RN-03; `label = "<tipo> — <obj.name>"` | 🟢 |
| `get()` / `apply(v)` / `commit(v)` / `hinge_frame()` | abstratos (`NotImplementedError`); `apply` = só pose; `commit` = pose + estado persistente; `hinge_frame` = `(ponto, eixo, referência)` no mundo, eixo positivo = sentido de abrir | 🟢 |
| `travel()` | **não está na base**; definido só em `FramelessFront`, `FaceFrameFront`, `ClosetFront` (EC-01) | 🟢 |
| `objects()` | padrão `[obj]` | 🟢 |
| `can_sweep()` | padrão `True` | 🟢 |
| `is_valid()` | `obj.name` e `module_root.name` acessíveis; `False` em `ReferenceError` | 🟢 |
| `_adapters()` | ordem `frameless, face_frame, closets, btm, room_doors, aggregate_leaf` (import tardio) | 🟢 |
| `iter_fronts(scene)` | concatena `adapter.find_fronts(scene)`; sem deduplicação entre adaptadores; cria wrappers novos a cada chamada | 🟢 |
| `fronts_of(root, scene)` | filtra `iter_fronts` por `module_root == root` | 🟢 |
| `front_for_object(obj, scene)` | `None` para `obj None`; primeiro adaptador que reconhece | 🟢 |
| `module_root_of(obj)` | RN-17 | 🟢 |

### Adaptadores

| Adaptador / key | Reconhece | `get` / `apply` / `commit` | `hinge_frame` / `objects` / `travel` | Confiança |
|---|---|---|---|---|
| `FramelessFront` `FRAMELESS:<obj>` | RN-16; `_kind`: `IS_FLIP_UP_DOOR`→FLIP_UP, `IS_DOOR_FRONT`→DOOR, `IS_PULLOUT_FRONT`→PULLOUT, `IS_DRAWER_FRONT`→DRAWER (nessa ordem); `front_for_object` sobe ancestrais e para no `IS_FRAMELESS_CABINET_CAGE` | `get = clamp(obj['btm_open'] or 0)`; `apply(v≤0)` zera os deltas; senão `_prepare()` (lazy) e `pose_for`/`slide` nos deltas; `commit` aplica e grava `btm_open` (apaga em 0) | `_local_frame`: extremo com sinal de cada eixo da `bound_box` avaliada × `obj.scale`, rotacionado por `rotation_euler`; DOOR = `side_hinge`, FLIP_UP = `top_hinge`, gaveta: direção = espessura; curso `_travel`: `Dim Y` do filho `IS_DRAWER_BOX`, senão `max(|Dim Y do pai| − 0,0254, 0,05)`, senão `0,4`; ponto = `parent.matrix_world @ matrix_parent_inverse @ (location + offset)`; eixo × `swing_sign`; `objects` = obj + filhos MESH/CURVE | 🟢 |
| `FaceFrameFront` `FACE_FRAME:<vão>` | vão `IS_FACE_FRAME_OPENING_CAGE` sem `IS_MANUAL_FRONT`, com filho `hb_part_role='FRONT_PIVOT'`; `front_type` DOOR→DOOR (hinge TOP→FLIP_UP, BOTTOM→FLIP_DOWN), TILT_OUT→FLIP_DOWN, DRAWER_FRONT→DRAWER, PULLOUT→PULLOUT; clique só vale vindo de frente/pivô (`via_front`) | `get` de `swing_percent` (÷100° se articulada); `apply` via `op_open_mode._apply_swing(ctx, swing)` com contexto `_build_tween_context` refeito 1 vez em `ReferenceError`; `commit` aplica e, se `swing` mudou > 1e-6, chama `cutting.stale.skip_next_update()` e grava `swing_percent` (recalcula o gabinete), depois zera o contexto | eixo pela diferença de rotação do pivô entre `front_leaves` com swing 0 e 1 (proxy `_SwingOverrideProxy`); gaveta: direção = deslocamento do pivô (fallback −Y); `travel` = comprimento desse deslocamento no mundo; `objects` = MESH/CURVE dos pivôs; `is_valid` só checa o vão | 🟢 |
| `ClosetFront` `CLOSETS:<obj>` | `hb_part_role == PART_ROLE_DOOR` com `hb_door_cx`, ou `PART_ROLE_DRAWER_FRONT` com `hb_slide_dist`; clique na caixa de gaveta resolve a frente irmã de mesmo `hb_drawer_index` | `get` = `types_closets.open_fraction(obj, chave)` (×110° se porta); `apply` = `apply_door_open`/`apply_drawer_open(obj, fração)`; `commit` grava `hb_door_open`/`hb_drawer_open` como fração | dobradiça de `hb_door_cx/cy/cz`, `hb_door_leaf`, `hb_hinge` (LEFT: sinal −1), `hb_door_side='BACK'` inverte; gaveta: `hb_slide_y0`, sentido −Y (BACK: +Y); `travel = hb_slide_dist`; `objects` inclui a caixa de gaveta irmã | 🟢 |
| `BtmFront` `BTM:<módulo>` | MESH com `btm_plane.object_kind == 'MODULE'`, `btm_cabinet.door_swing != 'NONE'`, filho `*_Controller` e portas `*_Door_L/_Door_R/_Door_Flip`; `FLIP` → FLIP_UP | `get` = `Controller.location.y/0,2 × 90`; `apply` escreve `Controller.location.y`; `commit` também grava `module['btm_open']` (só escrito) | ponto = posição da 1ª porta; FLIP_UP eixo −X; `_Door_R` eixo −Z; senão +Z; `objects` = portas; sem `travel` (sempre articulada) | 🟢 |
| `RoomDoorFront` `ROOM:<porta>` | `is_room_door`; sempre DOOR; rótulo "Porta de ambiente — <nome>" | `get = |graus(pivôs[0].rotation_euler.z)|` (0 sem pivô); `apply(v≤0)` sem pivô não faz nada; senão `ensure_leaves` e `pivô.rotation_euler.z = rad(rot_sign·v)`; `commit` grava `porta['btm_open']` | `can_sweep` = existe pivô; ponto `(hinge_x, hinge_y, 0)` da 1ª folha; eixo `±Z` por `rot_sign`; `objects` = folhas sob os pivôs, ou `[porta]` quando ainda não há pivô _(Revisão 2026-10-10: `adapters/room_doors.py:objects`, fallback `or [self.module_root]`)_ | 🟢 |
| `AggregateLeafFront` `LEAF:<obj>` | `btm_aggregate.is_aggregate`, `kind == 'LEAF'`, `leaf.pivot_of(obj)` existente; clique no pivô via idprop `btm_leaf`; SWING→DOOR, senão DRAWER; raiz = `module_root_of(parent_ref)` ou `parent_ref` | `clamp`/`max_value` com `max_angle`; `get = leaf.current_fraction × max_angle`; `apply = leaf.apply_fraction` (sem contato); `commit` grava `btm_aggregate.open_value` (fração), cujo update `leaf.update_open` para na batida — contrato em `_reversa_sdd/aggregates/` | base = `pivô['btm_leaf_base']` no mundo do `parent_ref`; SLIDE: eixo Z, referência ±X por `slide_dir`; SWING: eixo Z (LEFT/RIGHT) ou X (TOP/BOTTOM) com sinal de `leaf.swing_angle(agg, 1)`; `objects` = obj + descendentes; **sem `travel`**; `is_valid` sobrescrito = nome em `bpy.data.objects` e `is_leaf` _(Revisão 2026-10-10: `adapters/aggregate_leaf.py:is_valid`; sonda no Blender: `hasattr(AggregateLeafFront, 'travel')` é `False`)_ | 🟢 |

### `room_door_leaf.py`

| Símbolo | Comportamento | Confiança |
|---|---|---|
| `DOOR_TAG`, `PIVOT_TAG`, `LEAF_TAG` | `'IS_ENTRY_DOOR_BP'`, `'btm_room_door_pivot'`, `'btm_room_door_leaf'` (idprops) | 🟢 |
| `swing_of(door)` | filho com `IS_2D_ANNOTATION`, modificador GN e input `Swing Inside` (via `hb_types.GeoNodeObject`) | 🟢 |
| `has_real_door(door)` | `door.btm_opening_real.assembly` existe em `bpy.data.objects` (feature 010) | 🟢 |
| `is_room_door(obj)` | tag + símbolo + sem porta real | 🟢 |
| `remove_leaves(door)` | apaga pivôs/folhas (e malhas sem usuário) e `btm_open`; consumidor: `openings/sync.py:155` | 🟢 |
| `pivots_of(door)` | filhos com `PIVOT_TAG`, ordenados pelo lado | 🟢 |
| `leaf_specs(door)` | `room_door_math.leaves(Dim X, Dim Y, Dim Z, Is Left, Is Double, Swing Inside, Door Thickness or 0.035)` | 🟢 |
| `ensure_leaves(door)` | F-08 | 🟢 |

### Estado — `props.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `BTM_PG_Interference` | `front_name`, `module_name`, `hit_name`: `StringProperty`; `location: FloatVectorProperty(size=3, subtype='TRANSLATION')`; `kind: EnumProperty(DOOR, FLIP_UP, FLIP_DOWN, DRAWER, PULLOUT; default 'DOOR')` | 🟢 |
| `BTM_PG_InspectionState` | `active: Bool=False`; `snap_stops: Bool=True`; `default_angle: Enum('90','45')='90'`; `interferences: Collection(BTM_PG_Interference)`; `interference_index: Int=0`; `checked_fronts: Int=-1` (−1 = nunca) | 🟢 |
| `WindowManager.btm_inspection` | `PointerProperty(type=BTM_PG_InspectionState)`; `unregister` apaga com `hasattr` | 🟢 |

### Operadores

| `bl_idname` | Classe | `bl_options` | Propriedades | Retornos | Confiança |
|---|---|---|---|---|---|
| `caffmob.fronts_set_open` | `BTM_OT_FrontsSetOpen` | `{'REGISTER'}` | `scope` ALL/SELECTED/ACTIVE_MODULE (=ALL); `mode` CLOSE/OPEN_45/OPEN_90 (=OPEN_90) | `CANCELLED` + WARNING sem alvos; `FINISHED` + INFO "{n} frente(s) {abertas|fechadas}." (n = alvos, inclusive os pulados por `ReferenceError`) | 🟢 |
| `caffmob.inspect_fronts` | `BTM_OT_InspectFronts` | `{'REGISTER'}` | nenhuma; `poll`: área `VIEW_3D` | F-03 | 🟢 |
| `caffmob.check_front_interference` | `BTM_OT_CheckFrontInterference` | `{'REGISTER'}` | `scope` ALL/SELECTED (=ALL) | sempre `FINISHED`; WARNING (0 verificadas ou com choques) ou INFO | 🟢 |
| `caffmob.interference_goto` | `BTM_OT_InterferenceGoto` | `{'REGISTER'}` | `index: Int(min=0)=0` | `CANCELLED` fora da faixa; `FINISHED` | 🟢 |

### Gizmo — `gizmo.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `_state` | `{'front': None, 'pending': None, 'pointer': 0}` módulo-global | 🟢 |
| `_active_front(ctx)` | ativo selecionado; reaproveita o cache se `pointer == obj.as_pointer()` e `is_valid()`; senão `front_for_object` e atualiza cache | 🟢 |
| `_frame_matrix(point, axis, ref)` | Z = eixo; X = `ref` ortogonalizado (fallback `z.orthogonal()` se `< 1e-9`); Y = Z×X; matriz 4×4 | 🟢 |
| `BTM_GGT_front_open` | `bl_space_type='VIEW_3D'`, `bl_region_type='WINDOW'`, `bl_options={'3D','PERSISTENT'}`; `poll` = `_active_front` não nulo | 🟢 |
| `setup` | dial `GIZMO_GT_dial_3d` (target `offset` com get/set; `draw_options={'ANGLE_VALUE'}` em try; `use_draw_value`, `line_width=3`, `scale_basis=0,6`, cor (0,95, 0,55, 0,1) α 0,6, destaque (1, 0,75, 0,2) α 1); seta `GIZMO_GT_arrow_3d` (`scale_basis=1`, mesmas cores) | 🟢 |
| `_dial_get/_dial_set` | radianos ↔ graus; set: `_snap` (encaixe ou `clamp_angle`), `apply`, `pending = graus` | 🟢 |
| `_arrow_get/_arrow_set` | só gavetas; metros = fração × `max(front.travel(), 1e-6)`; set: `clamp_fraction`, `apply`, `pending` | 🟢 |
| `refresh`, `draw_prepare` | `_place`; `draw_prepare` também agenda `_commit_pending` (`bpy.app.timers.register(first_interval=0.0)`) se há `pending`, nenhum gizmo modal e o timer não está registrado | 🟢 |
| `_place` | sem frente → oculta ambos; `hinge_frame` com erro → oculta; dial visível só articulada, seta só gaveta; `matrix_basis` = `_frame_matrix` | 🟢 |
| `_commit_pending()` | lê `front`/`pending`, zera `pending`, `commit` (ignora `ReferenceError`), devolve `None` (timer único) | 🟢 |
| `unregister` | desregistra o timer, zera `_state`, desregistra a classe | 🟢 |

### `interference.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `STEP_DEGREES`, `TOLERANCE`, `_SKIP_DISPLAY` | `15.0`, `0.001` m, `{'WIRE','BOUNDS'}` | 🟢 |
| `_world_corners(objects, depsgraph)` | 8 cantos de `bound_box` avaliada no mundo, só objetos visíveis | 🟢 |
| `_samples(front)` | F-06 passo 1 | 🟢 |
| `_shrink(points, tol)` | cada ponto anda `min(tol, 0,5·dist)` em direção ao centróide; ponto no centro é copiado | 🟢 |
| `envelope_hulls(front, context)` | lista de nuvens (uma por par de poses consecutivas) | 🟢 |
| `_hull_bmesh(hulls)` | `bmesh.ops.convex_hull` por nuvem num BMesh único; apaga vértices interiores/não usados; planos `(centro da face, normal para fora do centróide)` | 🟢 |
| `_inside(p, planes)` | `(p − origem)·normal ≤ 0` para todos | 🟢 |
| `_aabb`, `_aabb_overlap` | caixa alinhada; sobreposição inclusiva nos 3 eixos | 🟢 |
| `_Targets(scene, depsgraph)` | `items = [(obj, aabb, module_root_of(obj))]`; `bvh(obj)` sob demanda com `to_mesh()` avaliado no mundo, `BVHTree.FromPolygons`, cache por `as_pointer()`, `to_mesh_clear()`; `sample_points(obj)` = vértices a cada `max(1, n//2000)` | 🟢 |
| `check_fronts(context, front_list)` | `-> (resultados, checked)`; resultado `{'front', 'module': nome, 'hit': Object, 'location': Vector mundo, 'kind'}` | 🟢 |
| `store_results(wm, results, checked)` | limpa e preenche `interferences`; `interference_index = 0`; `checked_fronts = checked` | 🟢 |

### `overlay.py` e `save_guard.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `overlay.COLOR`, `CROSS` | `(0.95, 0.15, 0.1, 1.0)`, `0.04` m | 🟢 |
| `overlay._draw_3d` | `POST_VIEW`: 3 segmentos ±0,04 m por ponto; shader `POLYLINE_UNIFORM_COLOR`, `lineWidth=3`, `viewportSize` da região; `depth_test_set('NONE')`, `blend_set('ALPHA')` e depois `blend_set('NONE')` | 🟢 |
| `overlay._draw_2d` | `POST_PIXEL`: rótulo `"<frente> × <objeto>"`, fonte 0 tamanho 13, sombra preta α 0,85 em (+9, +7) e texto em `COLOR` em (+8, +8) | 🟢 |
| `overlay.register/unregister` | `_handles` com 2 `SpaceView3D.draw_handler_add(..., 'WINDOW', ...)`; remoção em laço | 🟢 |
| `save_guard._reopen` | `[(nome da cena, key, valor)]` | 🟢 |
| `save_guard._HANDLERS` | `save_pre→save_pre`, `save_post→save_post`, `save_post_fail→save_post`, todos `@persistent`; registro sem duplicar; `unregister` remove todas as ocorrências e limpa `_reopen` | 🟢 |

## Fluxo Principal

### F-01 — `scope_fronts(context, scope)`

1. 🟢 `ALL` → `iter_fronts(context.scene)`.
2. 🟢 `ACTIVE_MODULE` → `module_root_of(active)`; `fronts_of(root)` ou `[]`.
3. 🟢 `SELECTED` → `roots = {module_root_of(o) for o in selected} − {None}`; candidatos = frentes da cena cujo `module_root ∈ roots` + `front_for_object(o)` de cada selecionado; deduplica por `key` preservando a ordem.

### F-02 — `caffmob.fronts_set_open`

1. 🟢 `targets = scope_fronts`; vazio → WARNING + `CANCELLED`.
2. 🟢 `degrees = {CLOSE: 0, OPEN_45: 45, OPEN_90: 90}`; por frente: `value = open_value(degrees)` (articulada) ou `degrees/90` (gaveta); `commit(value)`, pulando `ReferenceError`.
3. 🟢 INFO `"{n} frente(s) {fechadas|abertas}."` + `FINISHED`.

### F-03 — `caffmob.inspect_fronts` (modal)

1. 🟢 `invoke`: se `_active` existe → marca `_active._exit_requested = True`, cria (uma vez) `_exit_timer = event_timer_add(0.001)` para acordar o modal e devolve `CANCELLED`.
2. 🟢 Senão: `_tweens = {}`, timer `1/60 s`, `modal_handler_add`, status `"Abrir portas e gavetas | Clique: abrir/fechar | Esc / botão direito: sair"` (traduzido), `viewport_hud.register_active_modal(self)`, `_active = self`, `btm_inspection.active = True`, redesenho; `RUNNING_MODAL`.
3. 🟢 `modal`, nesta ordem: `_exit_requested` → `_finish` + `FINISHED`; `TIMER` → `_step` + `PASS_THROUGH`; `LEFTMOUSE PRESS` → se `_click_on_widget` → `PASS_THROUGH`; senão raycast (`region_2d_to_origin_3d`/`vector_3d` + `scene.ray_cast(depsgraph avaliado)`), `front_for_object`; com frente → `_toggle` + `RUNNING_MODAL`; sem → `PASS_THROUGH`; `ESC`/`RIGHTMOUSE PRESS` → `_finish` + `CANCELLED`; demais → `PASS_THROUGH`.
4. 🟢 `_toggle`: tween existente → `current` interpolado; alvo = 0 se o alvo era > 0, senão `tween['open']`; reinicia `t0`. Sem tween → `{front, start: get(), target: 0 se is_open() senão open_value(default_angle), open, t0: perf_counter()}`.
5. 🟢 `_step`: para cada tween, se `now − t0 ≥ 0,35` → `commit(target)` e remove; senão `apply(start + (target − start)·smoothstep(t))`; `ReferenceError`/`AttributeError` remove o tween; redesenha.
6. 🟢 `_finish`: `commit(target)` de todos os tweens (ignora erros), remove os 2 timers (ignora `ValueError`/`RuntimeError`), `unregister_active_modal`, `_active = None` (se for ele), `active = False`, `status_text_set(None)`, redesenho. `cancel()` chama `_finish`.

### F-04 — Gizmo: arrastar e gravar

1. 🟢 `poll` resolve a frente do ativo selecionado; `_place` posiciona dial ou seta em `hinge_frame()`.
2. 🟢 Arraste chama `_dial_set`/`_arrow_set`: `apply` + `pending`.
3. 🟢 Em cada `draw_prepare`, se há `pending` e nenhum gizmo está modal, registra `_commit_pending` com intervalo 0; o timer faz `commit(pending)` fora do desenho (gravar no face frame recria objetos).

### F-05 — Salvar fechado

1. 🟢 `save_pre` → `close_for_save()`: limpa `_reopen`; para cada cena sem `save_fronts_open`, cada frente de `key` ainda não vista: `value = get()`; se `is_open()` → `commit(0)` e guarda `(cena, key, value)`; `ReferenceError` pula.
2. 🟢 `save_post`/`save_post_fail` → `reopen_after_save()`: copia e limpa `_reopen`, agrupa por cena, redescobre `iter_fronts(cena)` e `commit(valor)` em cada `key` lembrada; cena inexistente é pulada.

### F-06 — Verificar interferência

1. 🟢 Para cada frente válida com `can_sweep()`: `envelope_hulls` — guarda `original = get()`; para cada amostra (`_samples`: `[0, 15, …, < max] + [max]` ou `[0, 1]`) faz `apply`, `view_layer.update()` e coleta `_world_corners(objects())`; em `finally` `apply(original)` + `update()`; nuvens = `_shrink(pose_i + pose_{i+1}, 0,001)`.
2. 🟢 Só depois de restaurar todas as frentes, cria `_Targets(scene, depsgraph)`.
3. 🟢 Por frente com cascos: `checked += 1`; caixa total dos cascos; candidatos = alvos de outro `module_root`, fora de `objects()` e com AABB sobreposta; sem candidatos → próxima.
4. 🟢 `_hull_bmesh` → `BVHTree.FromBMesh`; por candidato com BVH: `pairs = envelope.overlap(tree)`; com pares → centros das faces do casco dos 32 primeiros; sem pares → vértices amostrados do alvo dentro de algum casco (até 32); sem pontos → sem choque; com pontos → média vira `location`. `bm.free()` em `finally`.
5. 🟢 `ops_interference`: `store_results`, redesenha todas as `VIEW_3D` da tela e reporta (RN-13).

### F-07 — Ir até a interferência

1. 🟢 Índice fora → `CANCELLED`. Senão `interference_index = index`; desmarca a seleção; seleciona frente e alvo por nome se existirem na cena e estiverem visíveis; frente vira ativa; `region_3d.view_location = location` em toda `VIEW_3D` da tela.

### F-08 — `room_door_leaf.ensure_leaves(door)`

1. 🟢 `specs = leaf_specs(door)`; se os lados dos pivôs atuais ≠ lados de `specs` (ordenados) → apaga todos os pivôs.
2. 🟢 Por spec: cria pivô Empty `"<porta>_Pivo_<lado>"` (`empty_display_size = 0,05`, `PIVOT_TAG = lado`, nas coleções da porta, pai = porta) se faltar; `location = (hinge_x, hinge_y, 0)`; cria folha `"<porta>_Folha_<lado>"` (malha `"<porta>_Folha"`, `LEAF_TAG = True`, pai = pivô) se faltar; reconstrói a malha por `convex_hull` dos 8 cantos a cada chamada.
3. 🟢 Devolve `[(Leaf, pivô)]`.

## Fluxos Alternativos

- 🟢 Face frame com pivôs recriados por recálculo: `apply` refaz o contexto e tenta de novo uma vez (`adapters/face_frame.py:apply`).
- 🟢 Objeto apagado durante a animação: o tween é descartado em `_step` (`ReferenceError`/`AttributeError`).
- 🟢 Clique em HUD (`viewport_hud.click_hits_widget`) ou pílula do overlay do closets (`gpu_overlay_closets._filter_pill_rects`): passa adiante; falhas de import/atributo nessa checagem são engolidas (`ops_inspect.py:_click_on_widget`).
- 🟢 Operadores legados `face_frame/op_open_mode` e `closets/op_open_door_closet` delegam a `caffmob.inspect_fronts('INVOKE_DEFAULT')`; o closets consulta `inspection_running()`.
- 🟢 Porta de ambiente que ganha porta real (010): `openings/sync.py` chama `remove_leaves`; o adaptador `aggregate_leaf` passa a responder pelas folhas reais.

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `data/i18n.py` (`tr`, `N_`) | mensagens e rótulos; catálogo `data/translations/inspection.json` | 🟢 |
| `compat.try_get_gn_input` | `Dim Y` da caixa/vão no frameless | 🟢 |
| `hb_types.GeoNodeObject` | inputs `Dim X/Y/Z`, `Is Left`, `Is Double`, `Swing Inside`, `Door Thickness` | 🟢 |
| `product_libraries/face_frame` (`solver_face_frame.front_leaves`, `types_face_frame.find_cabinet_root`, `op_open_mode._build_tween_context/_apply_swing/_SwingOverrideProxy`) | adaptador face frame | 🟢 |
| `product_libraries/closets` (`types_closets.open_fraction/apply_door_open/apply_drawer_open/find_starter_root`, `PART_ROLE_*`; `gpu_overlay_closets`) | adaptador closets e cliques | 🟢 |
| `aggregates/leaf.py` (`pivot_of`, `current_fraction`, `apply_fraction`, `swing_angle`, `update_open`) | adaptador de folhas; contrato em `_reversa_sdd/aggregates/` | 🟢 |
| `cutting/stale.py` (`skip_next_update`; consulta `inspection_running`) | plano de corte não desatualiza | 🟢 |
| `operators/viewport_hud.py` (`register_active_modal`, `unregister_active_modal`, `click_hits_widget`) | botão do modo e cliques | 🟢 |
| `Scene.btm_settings.save_fronts_open`, `Object.btm_plane`, `Object.btm_cabinet`, `Object.btm_aggregate`, `Object.btm_opening_real` | propriedades de outras units | 🟢 |
| Consumidores | `ui/panels.py:draw_inspection_box`, `ui/object_properties.py:_draw_open`, `ui/context_menu.py` (`FRONTS_OPEN/CLOSE` com `ACTIVE_MODULE`), `ui/sidebar_vocab.py`, `aggregates/collision.py` (`module_root_of`), `openings/sync.py` (`remove_leaves`) | 🟢 |

## Decisões de Design Identificadas

- 🟢 Adaptador por linha com valor comum (ADR 0005): a UI e o detector não conhecem as estruturas legadas.
- 🟢 `apply` × `commit`: animação, arraste e varredura só posam; gravar estado (que no face frame recalcula o gabinete) acontece no fim (`fronts.py` docstring; `gizmo.py` docstring).
- 🟢 Pose do frameless em `delta_*`, preservando os drivers de medida (`adapters/frameless.py` docstring).
- 🟢 Sem `UNDO` nos operadores (RN-14 da 001).
- 🟢 Commit do gizmo por `bpy.app.timers` para não alterar dados dentro do desenho.
- 🟢 Envelope por cascos convexos de pares de poses e encolhimento de 1 mm para que encostar não conte (mesma tolerância de `collision/rules.py`).
- 🟢 Própria peça e próprio módulo fora do detector (D-29 da 001): portas vizinhas do mesmo vão não são acusadas.

## Estado Interno

| Estado | Escopo | Ciclo de vida | Confiança |
|---|---|---|---|
| `ops_inspect._active` | módulo | instância modal em execução; zerado em `_finish` e no `unregister` | 🟢 |
| `BTM_OT_InspectFronts._tweens` | instância | `{key: {front, start, target, open, t0}}` | 🟢 |
| `gizmo._state` | módulo | frente em cache, valor pendente, ponteiro do ativo | 🟢 |
| `save_guard._reopen` | módulo | entre `save_pre` e `save_post` | 🟢 |
| `overlay._handles` | módulo | do `register` ao `unregister` | 🟢 |
| `WindowManager.btm_inspection` | sessão | resultados até a próxima verificação; não invalidados por edição (EC-11) | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-93):** limpar a lista (ou marcar "desatualizado" no painel) num `depsgraph_update_post` quando um objeto MESH/CURVE muda transformação, reaproveitando o padrão de `collision/`; sem nova verificação automática. Pendência de implementação: DT-05 |
| Persistido no `.blend` | objetos | `btm_open` (frameless, porta de ambiente, módulo btm), `swing_percent`, `hb_door_open`/`hb_drawer_open`, `_Controller.location.y`, `open_value`, `delta_*`, pivôs e folhas da porta de ambiente | 🟢 |

## Observabilidade

- 🟢 `self.report` nos operadores (F-02, F-06); texto de status no modo; `checked_fronts` e lista no painel (`ui/panels.py`); cruz e rótulo no viewport.
- 🟢 Sem logs nem `print`; exceções fora das capturadas (`ReferenceError`, `AttributeError`, `ValueError`, `RuntimeError` em pontos específicos) propagam ao Blender.

## Riscos e Lacunas

- 🟢 Comportamento do gizmo com folha deslizante sem `travel()` (EC-01): `AttributeError` a cada leitura. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-61):** implementar `travel()` em `AggregateLeafFront` com o curso de correr da folha (`aggregates/leaf.py`) e um `travel()` na base `Front` devolvendo 0, com a seta oculta quando 0 (contrato uniforme entre adaptadores). Pendência de implementação: DT-01.
- 🟡 Salvar durante animação ou com `pending` do gizmo (EC-07). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-63):** em `save_pre`, concluir os tweens do `_active` e o `pending` do gizmo (commit do alvo) antes de `close_for_save`. Pendência de implementação: DT-03.
- 🟢 Desregistrar com o modo ativo (EC-04) só zera `_active`. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-92):** o `unregister` encerra a sessão chamando `_active._finish(bpy.context)` dentro de `try`, como pede a regra do repositório de remover todo handler em todos os caminhos de saída. Pendência de implementação: DT-04.
- 🟡 Envelope por caixas (`bound_box`) e passo de 15° é aproximação: puxadores e folhas finas podem gerar falso positivo/negativo (EC-12).
- 🟢 `tests/blender_inspection_smoke.py` executado e aprovado _(Revisão 2026-10-10: Blender 5.2.0 LTS, `--background --factory-startup`, saída `BLENDER_INSPECTION_SMOKE_OK`, código 0)_; o modal, o gizmo e as portas de ambiente/folhas convertidas seguem sem teste (TT-03 a TT-05).

## Divergências com artefatos anteriores

| Artefato | Afirmação | Código | Confiança |
|---|---|---|---|
| `data-dictionary.md` §18 | "BTM Controller.location.y e raiz.btm_open" como persistência | `btm_open` no módulo btm e na porta de ambiente é **só escrito**; `get` lê o Controller / a rotação do pivô | 🟢 |
| `state-machines.md` (Inspeção) | "Ativa → Encerrada: nova invocação" | A nova invocação devolve `CANCELLED`; quem encerra é a sessão antiga, acordada pelo timer de 0,001 s, com `FINISHED` | 🟢 (detalhe) |
| `interference.py` docstring | "encolhido 1 mm" | Encolhimento radial por ponto em direção ao centróide, `min(1 mm, metade da distância)` — não é offset das faces (já registrado em `code-analysis.md` §19) | 🟢 |
| `__init__.py` docstring | 6 adaptadores implícitos em `adapters/*` | Confere; `pivot_math.bottom_hinge` e `room_door_math.open_tip` não têm consumidor no pacote | 🟢 |
