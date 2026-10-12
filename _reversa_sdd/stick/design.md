# Grudar em Superfície (stick) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/stick/` (11 arquivos, 1.486 linhas) em 2026-10-10, sem alterações sem commit na pasta. IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`; fluxos F-xx abaixo. 🟡 marca inferência; 🔴 lacuna. Contratos citados, não redescritos: `selection/classify` (`classify` → `info.kind/root/obj`, `movable_root`, tipos `MODULE`, `GEOMETRY`, `WALL`, `FLOOR`, `CEILING`, `OTHER`, `ANNOTATION`) em `_reversa_sdd/selection/`; `aggregates/limits` (`FACES`, `FACE_LABELS`, `face_axes(face) → (eixo normal, sinal, eixo u, eixo v)`, `thickness(box, face)`) em `_reversa_sdd/aggregates/`; `collision/scan.check_moved` em `_reversa_sdd/collision/` (F-07); `ui/save_feedback.show(text)` (barra de status de todas as janelas por alguns segundos + `print("CAFFMob Draw: …")`) e `ui/sidebar_proxy.draw_panel` em `_reversa_sdd/ui/`; `hb_placement.PlacementMixin` em `_reversa_sdd/hb_placement/`.

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `frame.py` (192) | não (`math`, `..aggregates.limits`) | Referencial da face, posição, fora da face, planicidade, escolha da face | 🟢 |
| Dados | `props.py` (73) | sim | `BTM_PG_Stick` → `Object.btm_stick` (salvo) | 🟢 |
| Aplicação | `apply.py` (335), `link.py` (175), `settle.py` (102), `migrate.py` (51), `magnet.py` (101) | sim (`mathutils`) | Caixas, posição, handlers, temporizador; grudar/desgrudar; assentar; migração; ímã | 🟢 |
| Interface | `ops_stick.py` (232), `panels.py` (69), `magnet_preview.py` (131) | sim (`gpu`, `blf`, `gpu_extras`, `bpy_extras.view3d_utils`, `mathutils.geometry`) | 3 operadores, painel, prévia do ímã | 🟢 |
| Pacote | `__init__.py` (25) | não | `_modules()` importa tarde `apply, magnet_preview, ops_stick, panels, props` e devolve `(props, apply, ops_stick, panels, magnet_preview)`; `register` nessa ordem, `unregister` na inversa. `caffmob_draw/__init__.py` chama `stick.register()`/`unregister()`, importa `stick.migrate` e põe `"stick"` em `_submodule_names` | 🟢 |

`settle.py`, `link.py`, `magnet.py`, `migrate.py` não têm `register` próprio. 🟢

## Interface

### `frame.py` 🟢 (puro; tudo no espaço local do hospedeiro)

| Símbolo | Assinatura / valor | Comportamento |
|---|---|---|
| `BOX_SIDE`, `PLANE` | `'BOX_SIDE'`, `'PLANE'` | Tipos de face |
| `FACES` | `limits.FACES` = `('POS_X','NEG_X','POS_Y','NEG_Y','POS_Z','NEG_Z')` | Ordem de busca de `choose_face` |
| `PLANAR_TOLERANCE` | `0.0005` m | RN-01 |
| `ANGLE_TOLERANCE_DEG` | `1.0` | RN-02 |
| `SIDE_TOLERANCE` | `0.0005` m | RN-02 |
| `OUT_TOLERANCE` | `0.001` m | RN-12, RN-13 |
| `_sub/_add/_scale/_dot/_cross/_length/_normalized/_axis` | tuplas de 3 | `_normalized` levanta `ValueError("vetor nulo")` se comprimento < 1e‑12; `_axis(i, sign)` = vetor unitário |
| `box_frame(host_box, face)` | `host_box = (lo, hi)` → `(o, U, V, N)` | `n, sign, ua, va = face_axes(face)`; `o = (0,0,0)` com `o[n] = hi[n]` (sign > 0) ou `lo[n]`; `U = _axis(ua)`, `V = _axis(va)`, `N = _axis(n, sign)` (ex. `NEG_Y`: o = (0, lo_y, 0), U = X, V = Z, N = −Y) |
| `plane_frame(origin, normal, up=(0,0,1))` | → `(o, U, V, N)` | `n = normal unitária`; `hint = up` se `|up·n| < 0.999`, senão `(1,0,0)`; `U = normalizado(hint − n·(hint·n))`; `V = n × U` |
| `frame_to_matrix(frame)` | → 16 floats (por linha) | Linhas `(U[i], V[i], N[i], o[i])` para i = 0..2 + `(0,0,0,1)` |
| `matrix_to_frame(values)` | → `(o, U, V, N)` | Colunas 3, 0, 1, 2 |
| `frame_for(host_box, face_kind, face, plane_values)` | → frame | `BOX_SIDE` → `box_frame`; senão `matrix_to_frame(plane_values)` |
| `to_frame(frame, point)` | → `(u, v, n)` | `d = point − o`; `(d·U, d·V, d·N)` |
| `from_frame(frame, coords)` | → ponto | `o + U·c0 + V·c1 + N·c2` |
| `footprint(frame, corners)` | → `((u,v,n) mín., (u,v,n) máx.)` | Caixa dos cantos no referencial |
| `params(frame, corners)` | → `(u, v, distance)` | `footprint(...)[0]` |
| `shift(frame, corners, u=None, v=None, distance=None)` | → delta (espaço do hospedeiro) | `None` mantém o atual; `U·Δu + V·Δv + N·Δd` |
| `face_extent(host_box, face)` | → `((lo[ua], hi[ua]), (lo[va], hi[va]))` | Retângulo do lado |
| `out_of_face(frame, corners, extent)` | → `bool` | `extent is None` → `False`; centro da pegada fora de `[u0 − tol, u1 + tol] × [v0 − tol, v1 + tol]` |
| `is_planar(points, normal, tolerance=PLANAR_TOLERANCE)` | → `bool` | Vazio ou normal nula → `False`; `|(p − points[0])·n| ≤ tol` para todos |
| `choose_face(host_box, point, normal)` | → `(BOX_SIDE, face)` ou `(PLANE, None)` | RN-02 |
| `contact_axis(normal, up=(0,0,1))` | → `'BOTTOM'` ou `'BACK'` | `|n·up| ≥ 0.7` → `'BOTTOM'` |

### `props.py` 🟢

| Símbolo | Definição |
|---|---|
| `_guard` | `set` de `(nome do objeto, campo)` |
| `FACE_ITEMS` | `[(f, limits.FACE_LABELS[f], "") for f in limits.FACES]` |
| `KIND_ITEMS` | `[('BOX_SIDE', "Lado da caixa", "Um dos seis lados do hospedeiro; acompanha a medida dele"), ('PLANE', "Plano", "Plano fixo no hospedeiro (face inclinada)")]` |
| `IDENTITY` | 16 floats da identidade 4×4 por linha |
| `_guarded(name)` | Fábrica de `update(self, context)`: `obj = self.id_data`; se `(obj.name, name)` em `_guard` → sai; senão marca, chama `apply.update_spin(obj)` (`spin`) ou `apply.update_position(obj)` (demais), desmarca em `finally` (import tardio de `apply`) |
| `BTM_PG_Stick` | `is_stuck: BoolProperty(name="Grudado", default=False)`; `host: PointerProperty(name="Hospedeiro", type=Object)`; `face_kind: EnumProperty(name="Tipo de face", items=KIND_ITEMS, default='BOX_SIDE')`; `face: EnumProperty(name="Face", items=FACE_ITEMS, default='NEG_Y')`; `plane: FloatVectorProperty(name="Plano", size=16, default=IDENTITY)`; `u: FloatProperty(name="Posição U", subtype='DISTANCE', unit='LENGTH', update=_guarded('u'))`; `v`: idem "Posição V"; `distance: FloatProperty(name="Distância", subtype='DISTANCE', unit='LENGTH', description="Distância à face; negativo = entra no hospedeiro", update=_guarded('distance'))`; `spin: FloatProperty(name="Giro", subtype='ANGLE', unit='ROTATION', description="Giro do item em torno da normal da face", update=_guarded('spin'))`; `applied_spin: FloatProperty(subtype='ANGLE')`; `out_of_face: BoolProperty(name="Fora da face", default=False)`; `orig_parent: PointerProperty(type=Object)`; `last_world: FloatVectorProperty(size=16, default=IDENTITY)` |
| `register()` | Registra a classe; `bpy.types.Object.btm_stick = PointerProperty(type=BTM_PG_Stick)` |
| `unregister()` | `del Object.btm_stick` se existir; desregistra as classes registradas em ordem inversa |

Todas as anotações levam `# type: ignore`. Sem `min`/`max`/`soft_*` nos campos. 🟢

### `apply.py` 🟢

| Símbolo | Assinatura / valor | Comportamento |
|---|---|---|
| `SETTLE_SECONDS` | `0.2` | Atraso e reagendamento do temporizador |
| `QUIET_SECONDS` | `0.6` | Período quieto após abrir/desfazer/refazer |
| `_depsgraph()` | → `bpy.context.evaluated_depsgraph_get()` | — |
| `local_box(obj, depsgraph=None)` | → `((x,y,z) mín., (x,y,z) máx.)` | Mín./máx. de `_corners(obj, Matrix.Identity(4), dg)` |
| `_own_corners(obj, to_ref, dg)` | → lista | Só tipos `MESH`, `CURVE`, `FONT`, `SURFACE`, `META`; 8 cantos de `obj.evaluated_get(dg).bound_box`; todos com comprimento < 1e‑9 → `[]`; senão `to_ref @ canto` |
| `_corners(obj, to_ref, dg)` | → lista | Próprios; se vazios, une os de `children_recursive` que não têm idprop `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION` ou `obj_x`, com `to_ref @ obj.matrix_world⁻¹ @ child.matrix_world`; nada → `[to_ref @ (0,0,0)]` |
| `item_corners(item, host, dg=None)` | → lista de tuplas | `_corners(item, host.matrix_world⁻¹ @ item.matrix_world)` (inversas com `inverted_safe`) |
| `host_box(host, dg=None)` | → `(lo, hi)` tuplas | `local_box` |
| `face_of(item, dg=None)` | → `(frame, extent ou None)` | `frame.frame_for(host_box, face_kind, face, tuple(plane))`; `extent = face_extent` só em `BOX_SIDE` |
| `write(item, name, value)` | — | Marca `(item.name, name)` em `props._guard`, `setattr(item.btm_stick, name, value)`, desmarca em `finally` |
| `_store_world(item)` | — | `write(item, 'last_world', 16 floats de matrix_world por linha)` |
| `_translate_local(item, host, delta)` | → `bool` | `wd = host.matrix_world.to_3x3() @ delta`; `|wd| ≤ 1e-9` → `False`; `item.matrix_world = Translation(wd) @ item.matrix_world` |
| `linked(item)` | → `bool` | `btm_stick` existe, `is_stuck`, `host` não `None` e `item.parent == host` |
| `update_position(item, dg=None)` | → `bool` (moveu) | F-03 |
| `project(item, dg=None)` | → `bool` | F-04 |
| `_OPPOSITE` | `POS_X↔NEG_X`, `POS_Y↔NEG_Y`, `POS_Z↔NEG_Z` | — |
| `_flip_if_across(item, dg)` | → `bool` | F-05 |
| `update_spin(item)` | — | F-06 |
| `_check_face(item, fr, corners, extent)` | — | `out = frame.out_of_face(...)`; se diferente do gravado: `write('out_of_face', out)`; se `out`: `_warn(tr("Item fora da face: {}").format(item.name))` |
| `_warn(text)` | — | `ui.save_feedback.show(text)` (import tardio) |
| `lose_link(item, warn=True)` | — | F-08 |
| `_index`, `_index_ok` | `dict`, `[False]` | Índice nome do hospedeiro → nomes dos itens; chave `''` = `is_stuck` com `host` `None` |
| `invalidate()` | — | `_index_ok[0] = False` |
| `index()` | → `_index` | Se inválido: limpa e varre `bpy.data.objects` com `btm_stick.is_stuck` |
| `stuck_items(host)` | → lista de objetos | Nomes de `index().get(host.name)` que ainda existem em `bpy.data.objects` |
| `_busy`, `_last_box`, `_pending`, `_quiet_until` | `[False]`, `{}`, `set()`, `[0.0]` | Estado do handler/temporizador |
| `on_depsgraph_update(scene, depsgraph)` | `@persistent` | F-09 |
| `modal_running()` | → `bool` | Para cada `window` de `bpy.context.window_manager.windows` (`AttributeError` → `False`) e cada `op` de `window.modal_operators`: `settle.is_move_operator(op)` |
| `_settle_timer()` | → `0.2` ou `None` | F-10 |
| `on_load_or_undo(*_args)` | `@persistent` | `_quiet_until = monotonic() + 0.6`; `invalidate()`; limpa `_last_box` e `_pending` |
| `_HANDLERS` | `depsgraph_update_post → on_depsgraph_update`; `load_post`, `undo_post`, `redo_post → on_load_or_undo` | — |
| `register()` / `unregister()` | — | Acrescenta sem duplicar / remove os presentes, desregistra `_settle_timer` se registrado e chama `on_load_or_undo()` |

### `link.py` 🟢

| Símbolo | Assinatura | Comportamento |
|---|---|---|
| `UP` | `Vector((0,0,1))` | — |
| `host_for(obj)` | → Object ou `None` | RN-04 |
| `can_stick(item, host)` | → mensagem traduzida ou `None` | RN-05 |
| `_to_host(host, point, normal)` | → `(p, n)` | `p = host.matrix_world⁻¹ @ point`; `n = (host.matrix_world.to_3x3()ᵀ @ normal).normalized()` |
| `oriented_matrix(world, normal_world)` | → `Matrix` | F-02 passo 3 |
| `orient(item, normal_world)` | — | `item.matrix_world = oriented_matrix(...)` |
| `_attach(item, host)` | — | Se não `is_stuck`: `write('orig_parent', item.parent)`; `world = copy`; `parent = host`; `matrix_parent_inverse = I`; `matrix_basis = host.matrix_world⁻¹ @ world` |
| `_record(item, host, kind, face, plane_values, u, v, distance)` | — | `write` de `host`, `face_kind`, `face or 'NEG_Y'`, `plane`, `u`, `v`, `distance`, `spin = 0`, `applied_spin = 0`, `out_of_face = False`, `is_stuck = True` (nessa ordem); `apply.invalidate()` |
| `stick(item, hit_obj, point_world, normal_world, polygon_world=None, center=True, rotate=True)` | → `(host, face)` ou `ValueError` | F-02 |
| `link_in_place(item, host, face)` | — | F-12 |
| `release(item)` | → `bool` | F-07 |
| `face_label(item)` | → `str` | `""` sem `host`; RN-22 |

### `settle.py` 🟢

| Símbolo | Valor / assinatura | Comportamento |
|---|---|---|
| `_MOVE_IDS` | `{'caffmob.stick_move', 'caffmob.stick_to_face', 'caffmob.aggregate_move', 'caffmob.move_on_wall', 'caffmob.move_over_drag', 'caffmob.move_over_dialog', 'caffmob.cabinet_editor_modal'}` | Modais que movem objetos |
| `_MAGNET_KINDS` | `(classify.MODULE, classify.GEOMETRY)` | — |
| `_idname(op)` | → `str` | `bl_idname` `"PREFIXO_OT_resto"` → `"prefixo.resto"`; senão o próprio |
| `is_move_operator(op)` | → `bool` | `_idname` começa com `transform.` ou está em `_MOVE_IDS`, ou `isinstance(op, hb_placement.PlacementMixin)` (import tardio) |
| `_undo_push(message)` | — | `temp_override(window=windows[0])` + `bpy.ops.ed.undo_push(message=...)`; `IndexError`/`RuntimeError`/`AttributeError` ignorados |
| `_settled` | `dict` nome → `_world_key` | — |
| `_world_key(obj)` | → 16 floats `round(v, 6)` | — |
| `returned_to_rest(obj)` | → `bool` | `_settled.get(obj.name) == _world_key(obj)` |
| `run(names)` | — | F-11 |
| `_check_collisions(objs)` | — | `from ..collision import scan` (`ImportError` → sai); `scan.check_moved(objs)` |

### `magnet.py` 🟢

| Símbolo | Valor / assinatura | Comportamento |
|---|---|---|
| `DEFAULT_DISTANCE` | `0.05` | — |
| `_MAX_STEPS` | `8` | Acertos pulados no máximo |
| `_FACING` | `-0.7` | Limite de `normal·dir` |
| `preferences()` | → `(bool, float)` | `package = __package__.rsplit('.', 1)[0]`; `context.preferences.addons.get(package).preferences`; sem ele ou sem `stick_magnet` → `(True, DEFAULT_DISTANCE)`; senão `(bool(stick_magnet), float(stick_magnet_distance))` |
| `_back(item, dg)` | → `(origem, dir)` | `lo, hi = apply.local_box(item)`; origem = `matrix_world @ ((lo.x+hi.x)/2, hi.y, (lo.z+hi.z)/2)`; `dir = (matrix_world.to_3x3() @ (0,1,0)).normalized()` |
| `find(item, distance, dg=None)` | → `(obj, ponto, normal, polígono)` ou `None` | F-13 |
| `_polygon(obj, index, dg)` | → lista de pontos do mundo ou `None` | `obj.evaluated_get(dg).data.polygons[index]` → `obj.matrix_world @ vertices[i].co`; `AttributeError`/`IndexError`/`ReferenceError` → `None` |
| `preview_pose(item, hit_location, hit_normal, dg=None)` | → 8 cantos (mundo) | F-14 |
| `try_stick(item)` | → host ou `None` | Ímã desligado → `None`; `find`; `link.stick(item, obj, ponto, normal, polígono, center=False, rotate=True)`; `ValueError` → `None` |

### `migrate.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `wall_of(root)` | `root.parent` se ele tem idprop `IS_WALL_BP` verdadeira; senão `None` |
| `wall_side(root, wall)` | `t = hb_types.GeoNodeWall(wall).get_input('Thickness')` (qualquer `Exception` → `0.0`); `rz = rotation_euler.z mod 2π`; `'NEG_Y'` se `min(rz, 2π − rz) < 0.01` e `location.y < 0.5·t`; senão `'POS_Y'` (mesma regra de `measure/scene_cotas._on_front_side`) |
| `run(scene)` | `scene is None` → 0; para `obj in scene.objects`: pula sem `btm_stick` ou `is_stuck`; exige `classify(obj).kind == MODULE` e `info.root is obj`; exige `wall_of`; `link.link_in_place(obj, wall, wall_side(obj, wall))`; conta. Ao fim, `scene.btm_settings.stick_migrated = True` (se existir). Devolve a contagem |

### `ops_stick.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `_STICK_FIELDS` | 13 campos: `is_stuck, host, face_kind, face, plane, u, v, distance, spin, applied_spin, out_of_face, orig_parent, last_world` |
| `item_of(obj)` | `None` → `None`; `classify.movable_root(obj)` ou o próprio objeto (inclusive parede, piso, teto, cota: `movable_root` devolve `None` para eles) |
| `_ray(context, event)` | `region_2d_to_origin_3d` / `region_2d_to_vector_3d` em `(mouse_region_x, mouse_region_y)` |
| `scene_hit(context, origin, direction, exclude)` | Até 16 `scene.ray_cast(depsgraph, start, direction)`; pula `exclude`, `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION` avançando `start = acerto + dir·0.0001`; devolve `(obj, ponto, normal, magnet._polygon(...))` ou `None` |
| `snapshot(item)` / `restore(item, snap)` | `(parent, matrix_parent_inverse.copy(), matrix_world.copy(), {13 campos; plane/last_world como tuplas})`; `restore` repõe pai, inversa, mundo, grava cada campo com `apply.write` e `invalidate()` |

| `bl_idname` / classe | `bl_label` | `bl_options` | `poll` | Comportamento |
|---|---|---|---|---|
| `caffmob.stick_to_face` / `BTM_OT_StickToFace` | "Grudar" | `{'REGISTER', 'UNDO', 'BLOCKING'}` | área `VIEW_3D` e `item_of(active_object)` não `None` | F-01 |
| `caffmob.stick_release` / `BTM_OT_StickRelease` | "Desgrudar" | `{'REGISTER', 'UNDO'}` | algum selecionado com `item_of(o).btm_stick.is_stuck` | `items = {item_of(o) for o in selected_objects} − {None}`; `count` de `link.release(item)` verdadeiros; `INFO` "{} item(ns) desgrudado(s)"; `FINISHED` |
| `caffmob.stick_move` / `BTM_OT_StickMove` | "Mover no plano" | `{'REGISTER', 'UNDO', 'BLOCKING'}` | área `VIEW_3D`, `item_of(active)` e `apply.linked(item)` | F-15 |

Tooltips (docstrings): "Clique numa face plana de outro objeto: o item encosta nela e vira elemento filho dela"; "Solta o item da face: ele fica onde está e deixa de acompanhar o hospedeiro"; "Arrasta o item no plano da face; com Ctrl, sobre a face de outro objeto ele troca de hospedeiro". Nenhum atalho de teclado é registrado pela unit; as entradas são o painel, o menu de contexto e o vocabulário da barra lateral (`ui/sidebar_vocab.py`: `STICK`, `RELEASE`, `STICK_MOVE`). 🟢

### `panels.py` 🟢

`BTM_PT_Stick`: `bl_label "Elemento filho"`, `bl_idname "BTM_PT_stick"`, `VIEW_3D`/`UI`, `bl_category "CAFFMob Draw"`, `bl_parent_id "BTM_PT_object_properties"`; `poll`: `item_of(active_object)` não `None`. `draw`: item com `is_stuck` e `host` → caixa com "Elemento filho de: {face_label}" (`SNAP_FACE`), coluna `u`, `v`, `distance`, `spin`, caixa `alert` "Item fora da face: {nome}" (`ERROR`) se `out_of_face`, linha com `caffmob.stick_move` (`SNAP_FACE`) e `caffmob.stick_release` (`UNLINKED`); senão `caffmob.stick_to_face` (`SNAP_FACE`). Depois, se `apply.stuck_items(item)` não vazio: caixa "Elementos filhos: {n}" (`OUTLINER_OB_GROUP_INSTANCE`) e uma linha "{filho} — {lado}" por filho ordenado por nome. `classes = ()`: não registrado; `ui/object_properties._position_group` o desenha via `sidebar_proxy.draw_panel` no grupo `sel_position` ("Posição e vínculo"). 🟢

### `magnet_preview.py` 🟢

| Símbolo | Valor | Comportamento |
|---|---|---|
| `FACE_COLOR`, `BOX_COLOR` | `(0.35, 0.85, 1.0, 1.0)`, `(0.35, 0.85, 1.0, 0.75)` | — |
| `_EDGES` | `((0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7))` | Ordem de `Object.bound_box` |
| `_KINDS` | `(MODULE, GEOMETRY)` | — |
| `_handles`, `_last` | lista, `[None]` | `_last[0] = (host, ponto, polígono, caixa)` do último quadro |
| `_moving_item(context)` | F-16 | — |
| `compute(context)` | F-16 | — |
| `_draw_3d()` | `POST_VIEW` | F-16 |
| `_draw_2d()` | `POST_PIXEL` | F-16 |
| `register()` / `unregister()` | Só se `_handles` vazio: `SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW')` e `(_draw_2d, (), 'WINDOW', 'POST_PIXEL')`; `unregister` remove todos e zera `_last` |

## Fluxos

### F-01 Grudar (operador) 🟢

1. `invoke`: `self.item = item_of(active_object)`; `modal_handler_add`; barra de status "Grudar {nome}  |  Clique numa face plana  |  Botão direito/Esc: cancelar"; `RUNNING_MODAL`.
2. `modal`: `MIDDLEMOUSE`/`WHEELUPMOUSE`/`WHEELDOWNMOUSE` → `PASS_THROUGH`; `RIGHTMOUSE`/`ESC` `PRESS` → limpa barra, `CANCELLED`.
3. `LEFTMOUSE PRESS`: raio do mouse; `scene_hit` excluindo o item e `children_recursive`; nada → `WARNING` "Nenhuma face sob o cursor", continua; acerto → `link.stick(item, obj, ponto, normal, polígono, center=True)`; `ValueError` → `WARNING str(exc)`, limpa, `CANCELLED`; sucesso → limpa, `INFO` "Elemento filho de: {face_label}", `FINISHED`.
4. Demais eventos → `RUNNING_MODAL`.

### F-02 `link.stick` 🟢

1. `host = host_for(hit_obj)`; `can_stick` → `ValueError(motivo)`.
2. Com `polygon_world`: vértices e normal para o espaço do hospedeiro; `not is_planar` → `ValueError("A face não é plana")`.
3. `rotate` → `orient`: `n` unitária; `loc, rot, scale = world.decompose()`; `current = rot.to_matrix()`. `BACK`: `y = −n`; `z = UP − n·(UP·n)` (se < 1e‑6, `current.col[2]` projetado); `x = (y × z)` normalizado. `BOTTOM`: `z = n` se `n·UP > 0`, senão `−n`; `y = current.col[1]` projetado no plano (se < 1e‑6, `current.col[0] × z`); `x = y × z`. `Matrix.LocRotScale(loc, Matrix((x, y, z)).transposed().to_quaternion(), scale)`.
4. `_attach(item, host)`.
5. `box = host_box(host)`; `p, n = _to_host(...)`; `choose_face(box, p, n)`. `BOX_SIDE` → `fr = box_frame`, `plane = IDENTITY`; `PLANE` → `fr = plane_frame(p, n)`, `plane = frame_to_matrix(fr)`.
6. `u, v = params(fr, item_corners)`; com `center`: `hu, hv = to_frame(fr, p)`; `u = hu − (hi_u − lo_u)/2`, `v = hv − (hi_v − lo_v)/2`.
7. `_record(..., distance=0.0)`; `update_position(item)`; devolve `(host, face)` (`face` `None` em `PLANE`).

### F-03 `update_position` 🟢

Não `linked` → `False`. `fr, extent = face_of(item)`; `corners = item_corners`; `moved = _translate_local(item, host, frame.shift(fr, corners, u, v, distance))`; se moveu, recalcula `corners`; `_check_face`; `_store_world`; devolve `moved`.

### F-04 `project` (depois de movimento livre) 🟢

Não `linked` → `False`. `_flip_if_across`; `fr = face_of(item)`; `u, v, _ = params(fr, item_corners)`; grava `u`/`v` com `write` só se diferirem mais de 1e‑9; `update_position` (restaura `distance`).

### F-05 `_flip_if_across` 🟢

Só `BOX_SIDE`. `box = host_box`; `t = limits.thickness(box, face)`; `d = params(box_frame(box, face), corners)[2]`; `d ≥ −t − OUT_TOLERANCE` → `False`. `d_other` pela face oposta; `d_other < −OUT_TOLERANCE` → `False`. Senão `write('face', oposta)`, `write('distance', d_other)`, `True`.

### F-06 `update_spin` 🟢

Não `linked` → sai. `delta = spin − applied_spin`; se `|delta| > 1e‑9`: `lo, hi = footprint(fr, item_corners)`; centro = `from_frame(fr, ((lo_u+hi_u)/2, (lo_v+hi_v)/2, lo_n))` no mundo; eixo = `host.matrix_world.to_3x3() @ N` normalizado; `item.matrix_world = T(c) @ R(delta, eixo) @ T(−c) @ item.matrix_world`; `write('applied_spin', spin)`. Sempre termina com `update_position`.

### F-07 `release` 🟢

Não `is_stuck` → `False`. `world = copy`; `parent = orig_parent`; se `parent` existe, `parent.name not in item.children_recursive` (compara nome com objetos: sempre verdadeiro, EC-09) e `parent != item` → `parent = parent`, inversa `I`, `matrix_basis = parent⁻¹ @ world`; senão `parent = None`, `matrix_world = world`. `write` de `is_stuck = False`, `host = None`, `orig_parent = None`, `out_of_face = False`; `invalidate()`; `True`.

### F-08 `lose_link` 🟢

`world` = `last_world` como matriz; se `item.parent is None` e `world` difere da identidade em algum termo (> 1e‑12) → `matrix_world = world`. `write` de `is_stuck = False`, `host = None`, `out_of_face = False`; `invalidate()`; com `warn`, "Vínculo perdido: {nome}".

### F-09 Handler `on_depsgraph_update` 🟢

1. `_busy` → sai; senão marca (desmarca em `finally`); `ReferenceError` engolido.
2. `idx = index()`. Para cada `update` em `depsgraph.updates` com `update.id` `Object`: `obj = update.id.original`.
   - `is_updated_geometry` e `obj.name in idx`: `box = host_box(obj, depsgraph)`; se `_last_box.get(nome) != box`: grava e `update_position(item, depsgraph)` para cada `stuck_items(obj)`.
   - `is_updated_transform` e `monotonic() ≥ _quiet_until` → `_pending.add(nome)`.
3. Para cada nome em `idx.get('')` existente → `lose_link(item)`.
4. `_pending` não vazio e `_settle_timer` não registrado → `bpy.app.timers.register(_settle_timer, first_interval=0.2)`.

### F-10 Temporizador `_settle_timer` 🟢

`modal_running()` → devolve `0.2` (reagenda). Senão `names = list(_pending)`; limpa; `_busy = True`; `settle.run(names)` (`ReferenceError` engolido); `_busy = False`; devolve `None` (encerra).

### F-11 `settle.run(names)` 🟢

Para cada nome existente em `bpy.data.objects`: `returned_to_rest` → pula; `apply.linked` → `apply.project`, entra em `moved_roots`; `is_stuck` → pula; `classify` sem `info`, `info.root is not obj` ou tipo fora de `MODULE`/`GEOMETRY` → pula; `wall_of` → `link_in_place(obj, parede, wall_side)`; senão `magnet.try_stick` não `None` → `stuck_now`; entra em `moved_roots`. Depois: `_settled[nome] = _world_key` de cada `moved_roots` vivo; com `stuck_now`, `save_feedback.show("Elemento filho de: {face_label}")` por item e um `_undo_push(tr("Grudar"))`; com `moved_roots`, `_check_collisions(moved_roots)`.

### F-12 `link_in_place` 🟢

`parent != host` → `_attach`; `write('orig_parent', host)`; `fr = box_frame(host_box(host), face)`; `u, v, d = params(fr, item_corners)`; `_record(item, host, BOX_SIDE, face, IDENTITY, u, v, d)`; `write('last_world', matriz do mundo)`. Não chama `update_position` (nada se move, sem `_check_face`).

### F-13 `magnet.find` 🟢

`origem, dir = _back(item)`; `own = {item} ∪ children_recursive`; `start = origem − dir·0.001`. Até 8 vezes: `scene.ray_cast(depsgraph, start, dir, distance=distance + 0.002)`; sem acerto → `None`; acerto em `own`/`IS_CUTTING_OBJ`/`IS_2D_ANNOTATION` → `start = ponto + dir·0.0001`, continua; `(ponto − origem)·dir > distance` ou `normal·dir > −0.7` → `None`; `host_for(obj)` com tipo `FLOOR`/`CEILING` → `None`; senão `(obj, ponto, normal, _polygon)`. Esgotou → `None`.

### F-14 `magnet.preview_pose` 🟢

`target = link.oriented_matrix(item.matrix_world, normal)`; cantos de `apply._corners(item, target)` levados por `target⁻¹`; caixa `lo/hi` local; 8 cantos na ordem de `bound_box` levados por `target`; `gap = min((c − ponto)·n)`; devolve `c − n·gap` (a caixa encosta no plano acertado). Não altera o objeto.

### F-15 Mover no plano 🟢

1. `_plane()`: `fr = face_of(item)`; plano no mundo = `host.matrix_world @ o + N_mundo·distance`, normal `N_mundo`.
2. `_plane_coords`: `mathutils.geometry.intersect_line_plane(origem, origem + dir, ponto do plano, normal)`; `None` → `None`; senão `to_frame(fr, host⁻¹ @ acerto)`.
3. `invoke`: `snap = snapshot(item)`; `anchor = _plane_coords`; `None` → `WARNING` "Gire a vista para enxergar a face", `CANCELLED`; `start = (u, v)`; modal; barra "Mover no plano  |  Ctrl: trocar de face  |  Clique: confirmar  |  Botão direito/Esc: cancelar".
4. `modal`: navegação → `PASS_THROUGH`; `MOUSEMOVE`: `_switch_face` (ímã ligado e `event.ctrl`; `scene_hit` sem o item; hospedeiro diferente do atual; `link.stick(center=True)` sem `ValueError`; reancora `anchor`/`start`) → `RUNNING_MODAL`; senão `st.u = start_u + (c_u − anchor_u)`, `st.v = …` (atribuição normal: o `update` reposiciona); `LEFTMOUSE PRESS` → limpa barra, `FINISHED`; `RIGHTMOUSE`/`ESC PRESS` → `restore(snap)`, limpa barra, `CANCELLED`.

### F-16 Prévia do ímã 🟢

- `_moving_item`: percorre `modal_operators` das janelas; só considera os `is_move_operator`; para um `PlacementMixin`, devolve o primeiro de `preview_cage`, `cabinet`, `obj` (desembrulhando `.obj`) que seja `Object`. Sem modal de movimento → `None`. Senão o ativo, se `classify` dá `MODULE`/`GEOMETRY` com raiz → a raiz.
- `compute`: ímã desligado → `None`; sem item, item `is_stuck` ou `migrate.wall_of(item)` → `None`; `magnet.find` (`ReferenceError`/`RuntimeError` → `None`); `preview_pose` (+ `ValueError` → `None`); devolve `(host_for(obj), ponto, polígono or [], caixa)`.
- `_draw_3d`: `_last[0] = compute(context)` (sem região → `None`); shader `POLYLINE_UNIFORM_COLOR`; `depth_test_set('NONE')`, `blend_set('ALPHA')`; contorno do polígono (≥ 3 pontos) em `FACE_COLOR` largura 3,0; 12 arestas da caixa em `BOX_COLOR` largura 2,0; uniformes `color`, `lineWidth`, `viewportSize`; `blend_set('NONE')`.
- `_draw_2d`: usa `_last[0]`; `location_3d_to_region_2d` do ponto; texto "Grudar em: {hospedeiro}" com `blf.size(0, 13)`, sombra `(0,0,0,0.85)` em `(x+11, y+9)` e texto em `FACE_COLOR` em `(x+10, y+10)`.

## Máquina de Estados do Vínculo 🟢

| Estado | Condição (`btm_stick` + parentesco) | Entradas | Saídas |
|---|---|---|---|
| Solto | `is_stuck = False` | Início; Desgrudar; Vínculo perdido | Grudar (F-01/F-02), ímã (F-11), migração/parede (F-12) → Grudado |
| Grudado | `linked` e `out_of_face = False` | F-02, F-12; volta da pegada ao retângulo | Hospedeiro encolhe → Fora da face; Desgrudar → Solto; hospedeiro apagado → Vínculo quebrado; pai trocado → Órfão |
| Fora da face | `linked` e `out_of_face = True` | `_check_face` (aviso só na entrada) | Pegada volta ao retângulo → Grudado (sem aviso) |
| Vínculo quebrado | `is_stuck` e `host is None` | Hospedeiro apagado sem o operador | Próximo handler com índice válido → `lose_link` → Solto (EC-01) |
| Órfão | `is_stuck`, `host` presente, `item.parent != host` | Pai trocado fora do plugin | 🟢 nenhuma saída automática; só Desgrudar (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-36):** o handler leva o Órfão a "sem vínculo" com `lose_link`. Pendência de implementação: DT-01 |

## Dependências

- 🟢 `aggregates/limits`: `FACES`, `FACE_LABELS`, `face_axes`, `thickness` (não usa `box_for`).
- 🟢 `selection/classify`: `classify`, `movable_root` e constantes de tipo.
- 🟢 `hb_types.GeoNodeWall(...).get_input('Thickness')` (migração); `hb_placement.PlacementMixin` (detecção de modal e item da prévia).
- 🟢 `ui/save_feedback.show`; `data/i18n.tr` com chaves em `data/translations/editor_grudar.json` (17 das 19 mensagens de `tr(...)` da unit estão nele; "Nenhuma face sob o cursor" está em `move_over.json` e "Grudar em: {}" em `sidebar.json`; os rótulos de `limits.FACE_LABELS` passam por `tr`, mas não têm entrada em nenhum catálogo, então ficam em português no en_US). _(Revisão 2026-10-10: script cruzando `tr("…")` de `stick/*.py` com `data/translations/*.json`)_
- 🟢 `collision/scan.check_moved` (import tardio protegido).
- 🟢 Preferências `BTM_AddonPreferences.stick_magnet` (`BoolProperty`, "Ímã", padrão `True`) e `stick_magnet_distance` (`FloatProperty`, "Distância do ímã", padrão 0,05, `min=0.001`, `max=0.5`, `DISTANCE`/`LENGTH`) em `caffmob_draw/__init__.py:198-208`, desenhadas na caixa "Grudar em superfície"; `Scene.btm_settings.stick_migrated` em `data/properties.py:746`.
- 🟢 Blender: `Object.evaluated_get`, `bound_box`, `children_recursive`, `matrix_parent_inverse`, `matrix_basis`, `Matrix.LocRotScale/decompose/inverted_safe`, `Scene.ray_cast`, `mathutils.geometry.intersect_line_plane`, `bpy.app.timers`, `bpy.app.handlers` (`depsgraph_update_post`, `load_post`, `undo_post`, `redo_post`), `Window.modal_operators`, `WorkSpace.status_text_set`, `bpy.ops.ed.undo_push`, `gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')`, `blf`, `location_3d_to_region_2d`.

### Consumidores 🟢

| Consumidor | Uso |
|---|---|
| `caffmob_draw/__init__.py` | `stick.register()`/`unregister()`; `stick.migrate.run(bpy.context.scene)` em `load_file_post` (`load_post`); preferências do ímã |
| `collision/scan.py` | `apply.local_box` (`box_of`); `btm_stick.is_stuck/host` em `_links` |
| `collision/ops_collision.py` | `apply.linked`, `face_of`, `project` ("Afastar" só no plano) |
| `collision/panels.py` | `ops_stick.item_of` |
| `cabinet_editor/bridge.py:root_box` | `apply.local_box` |
| `aggregates/ops_aggregate.py` | `apply.stuck_items` (poll e apagar), `link.release` + aviso "Vínculo perdido" |
| `aggregates/convert.py:can_convert` | Recusa `btm_stick.is_stuck` |
| `selection/component.py:_is_stuck` | Grudado é raiz de componente e não sai no plano de exclusão |
| `ui/object_properties.py:_position_group` | `panels.BTM_PT_Stick` via `sidebar_proxy` |
| `ui/context_menu.py:item_actions` | `item_of`; grudado → `RELEASE`, `STICK_MOVE`; senão `STICK` (só para tipos de item) |
| `ui/sidebar_vocab.py` | `STICK`, `RELEASE`, `STICK_MOVE` → os 3 operadores |

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Núcleo puro do referencial, reaproveitando `limits.face_axes` (004 D-01) | `frame.py` | 🟢 |
| Dois tipos de face, sem guardar índice de polígono (muda quando o GN reavalia) (004 D-02) | `frame.py:choose_face`; `link.py:stick` | 🟢 |
| Vínculo = parentesco Blender com inversa identidade + PropertyGroup; mover/girar/apagar o hospedeiro "de graça" (004 D-03) | `link.py:_attach` | 🟢 |
| Handler só anota; tratamento pós-movimento num temporizador que espera o modal acabar, para não brigar com o arraste | `apply.py` docstring; `settle.py` docstring | 🟢 |
| Ímã depois do movimento (cobre G nativo e todas as bibliotecas) em vez de dentro do `PlacementMixin` (diverge de 004 D-06); prévia só desenho (005 D-15) | `settle.py:run`; `magnet_preview.py` docstring | 🟢 (código) / 🟡 (motivo) |
| Avisos sem operador pela barra de status (004 D-10) | `apply.py:_warn` | 🟢 |
| Painel não registrado, desenhado pela barra lateral única (005) | `panels.py:classes = ()` | 🟢 |
| Reverificação de colisão acoplada ao assentar (diverge de 004 D-16; ver `_reversa_sdd/collision/`) | `settle.py:_check_collisions` | 🟢 |

## Observabilidade

- 🟢 `self.report` nos operadores (F-01, F-15, Desgrudar); `save_feedback.show` imprime "CAFFMob Draw: <texto>" no console e na barra de status ("Vínculo perdido", "Item fora da face", "Elemento filho de").
- 🟢 Sem log de exceções: `ReferenceError` é engolido no handler e no temporizador; outras exceções propagam (EC-15).

## Riscos e Lacunas

- 🟢 Pai trocado fora do plugin deixa o vínculo órfão sem aviso (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-36):** vira vínculo perdido com aviso. Pendência de implementação: DT-01.
- 🟢 Índice por nome: apagar ou renomear hospedeiro sem `invalidate()` atrasa "Vínculo perdido" e o acompanhamento de medida (EC-01, EC-03). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-37):** atualizar na hora. Pendência de implementação: DT-02.
- 🟡 Hospedeiro sem geometria própria (caixa vinda dos filhos) pode não receber `is_updated_geometry` quando só os filhos mudam (EC-16); não verificado no Blender.
- 🟢 `_undo_push` usa sempre `windows[0]` (EC-13); `magnet_preview` faz até 8 `ray_cast` por quadro. _(Revisão 2026-10-10: `settle.py:_undo_push`; `magnet.find` com `_MAX_STEPS = 8`, chamado por `magnet_preview._draw_3d` a cada redesenho; efeito no histórico e custo seguem sem medição)_
