# Agregados, Folhas, Grupos de Peças e Importação (aggregates) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/aggregates/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`; EC-xx os de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Contratos de outras units são citados, não redescritos: raiz de componente, `own_aggregates` e `delete_plan` em `_reversa_sdd/selection/` (RN-09, RN-10, F-03, F-04; `own_aggregates` desce em módulos filhos da parede, selection EC-07); porta e janela reais que montam grupos `FRAME`/`LEAF` e chamam `make_leaf` em `_reversa_sdd/openings/` (F-05, RN-11, RN-12); "Mover Sobre" em `_reversa_sdd/move_over/` (usa `group.object_corners`); Editor de Paredes em `_reversa_sdd/walls2d/` (muda `Thickness`, que os drivers da esquadria instalada acompanham).

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `limits.py` (103), `sweep.py` (48), `slide_limits.py` (35), `grouping.py` (39), `import_units.py` (18), `skp_core.py` (206) | não (`re`, `dataclasses`, `data.i18n`) | Limites na face, varredura, batentes de correr, sugestão de grupos, unidade, árvore do SketchUp | 🟢 |
| Estado | `props.py` (141), `group_props.py` (43), `window_props.py` (29) | sim | `Object.btm_aggregate`, `Object.btm_group`, `Object.btm_window` (salvos no `.blend`) | 🟢 |
| Aplicação | `apply.py` (116), `convert.py` (84), `perforate.py` (161), `production.py` (22), `leaf.py` (294), `collision.py` (171), `group.py` (112), `install.py` (110), `skp.py` (36), `skp_build.py` (121) | sim (`bmesh`, `mathutils.bvhtree`; `skp.py` só `openskp` tardio) | Posição, conversão, recorte, folha, contato, grupo, instalar, leitura e montagem do SketchUp | 🟢 |
| Interface | `ops_aggregate.py` (322), `ops_group.py` (197), `ops_import.py` (181), `ops_install.py` (98), `overlay.py` (138), `panels.py` (146) | sim (`gpu`, `blf`, `bpy_extras`) | Operadores, keymap, importador, simulação gráfica, painel | 🟢 |
| Pacote | `__init__.py` (29) | não diretamente | `_modules()` importa tarde e registra `props`, `group_props`, `window_props`, `apply`, `collision`, `ops_import`, `ops_aggregate`, `ops_group`, `ops_install`, `overlay`, `panels` nessa ordem; `unregister` na inversa. `perforate`, `production`, `leaf`, `group`, `install`, `skp*` não têm `register`. Chamado por `caffmob_draw/__init__.py` (`aggregates.register()`) | 🟢 |

## Interface

### `limits.py` 🟢 (puro)

| Símbolo | Assinatura / valor | Comportamento |
|---|---|---|
| `FACES`, `FACE_LABELS` | RN-01 | — |
| `_AXIS` | `{'X': 0, 'Y': 1, 'Z': 2}` | — |
| `face_axes(face)` | → `(n, sign, u, v)` | `n = _AXIS[face[-1]]`; `sign = 1.0` se começa com `POS`, senão `−1.0`; `u, v` = os índices ≠ `n` em ordem crescente (`NEG_Y` → `u = 0` (X), `v = 2` (Z)) |
| `size(box)` | → `(hi − lo)` por eixo | — |
| `thickness(parent_box, face)` | → `size(parent_box)[n]` | — |
| `nearest_face(parent_box, point)` | → face | Mínimo de `abs(point[n] − plano)`, `plano = hi[n]` (POS) ou `lo[n]` (NEG); comparação estrita `<`: empate fica com a primeira de `FACES` |
| `limits(parent_box, agg_size, face)` | → `{'u': (0, max(0, ps[u] − s[u])), 'v': (0, max(0, ps[v] − s[v])), 'offset': (−ps[n], None)}` | RN-02 |
| `clamp(parent_box, agg_size, face, u, v, offset)` | → `(u, v, offset)` | `max(lo, float(x))`, depois `min(hi, …)` se `hi` não é `None` |
| `box_for(parent_box, agg_size, face, u, v, offset, clamp_to_face=True)` | → `(lo, hi)` | RN-03; `clamp_to_face=False` não tem chamador no pacote (`stick/` não chama `box_for`) _(Revisão cruzada 2026-10-10: grep `box_for` em caffmob_draw/stick/ vazio)_ |
| `params_from_box(parent_box, agg_box, face)` | → `(u, v, offset)` | `offset = a_lo[n] − hi[n]` (POS) ou `lo[n] − a_hi[n]` (NEG); `u = a_lo[u] − lo[u]`, `v = a_lo[v] − lo[v]` |
| `sunk_box(parent_box, agg_box, face)` | → `(lo, hi)` ou `None` | Interseção; `None` se alguma medida ≤ 1e‑9 (`face` não é usado) |
| `sunk_depth(parent_box, agg_box, face)` | → `float` | 0 sem afundamento; senão a medida da interseção no eixo `n` |

### `sweep.py` 🟢 (puro)

| Símbolo | Valor | |
|---|---|---|
| `SWING_STEP`, `SWING_TOLERANCE` | `2.0`, `0.25` (graus) | |
| `SLIDE_STEP`, `SLIDE_TOLERANCE` | `0.01`, `0.001` (metros) | |
| `sweep(current, target, hit, step, tolerance, close=False, floor=0.0, floor_contact=None)` | → `(alcançado, contato ou None)` | F-06 |

### `slide_limits.py` 🟢 (puro)

| Símbolo | Comportamento |
|---|---|
| `LOW_TRAVEL_RATIO = 0.10` | — |
| `default_direction(leaf, frame)` | Intervalos `(mín, máx)` em X: `'NEG_X'` se o centro da folha < centro da esquadria, senão `'POS_X'` (empate → `POS_X`) |
| `sign(direction)` | `1.0` se `'POS_X'`, senão `−1.0` |
| `low_travel(free, leaf_width)` | `free < 0.10 × leaf_width` |
| `rest_overlap(a, b)` | `max(0, min(a1, b1) − max(a0, b0))` |
| `close_stop(open_sign, other_shift)` | `max(0, open_sign × other_shift)` |

### `grouping.py`, `import_units.py` 🟢 (puros)

| Símbolo | Comportamento |
|---|---|
| `LEAF_WORDS = ('folha', 'leaf', 'sash')`, `FRAME_NAME = "Esquadria"`, `_SUFFIX = r"\.\d{3}$"` | — |
| `leaf_key(name)` | `_clean` (tira `.NNN`, `None` → ""), `split("_")`; `len ≥ 2` e `tokens[0].lower() in LEAF_WORDS` → `"_".join(tokens[:2])`, senão `None` |
| `suggest(names)` | `[(chave, 'LEAF', [nomes originais])]` ordenado pela chave + `("Esquadria", 'FRAME', resto)` se houver resto |
| `SCALE = {'MM': 0.001, 'CM': 0.01, 'M': 1.0, 'IN': 0.0254}`, `AUTO_LIMIT = 50.0` | — |
| `suggest(largest)` | `'MM'` se `float(largest) > 50.0`, senão `'M'` |
| `scale_for(unit, largest)` | `SCALE[suggest(largest)]` se `unit == 'AUTO'`, senão `SCALE[unit]` |

### `skp_core.py` 🟢 (puro)

| Símbolo | Comportamento |
|---|---|
| `DEFAULT_MATERIAL = N_("SketchUp padrão")` | Passa por `tr` ao usar |
| `_EXT` | `image/png` `.png`, `image/jpeg`/`image/jpg` `.jpg`, `image/bmp` `.bmp`, `image/tiff` `.tif` |
| `MeshPlan` | `@dataclass`: `name`, `verts`, `tris`, `uvs=None`, `material=""`, `material_index=-1`, `texture=None` |
| `GroupPlan` | `@dataclass`: `name`, `path`, `meshes=[]`, `children=[]` |
| `_FIGURE` | `^2D[_ ]?(Woman|Man|Person|Figure|People)(_|\b)` ou `^(Sandra|Chris|Susan|Lily|Derrick|Laura|Nancy|Bryce|Steve|Mark|Ivan|Emily|Kelly|Joe)(\b|_)`, `IGNORECASE` |
| `is_scale_figure(name)` | `match` em `str(name or "").strip()` |
| `clean_material_name(name)` | Tira o prefixo `Layer_` se sobra algo |
| `to_blender(point)` | `(x, −z, y)` em `float` |
| `_triples(flat, size)`, `_rgb(material)`, `_texture_index(material)` | Agrupa em tuplas de `size`; RGB 0–255 de `pbrMetallicRoughness.baseColorFactor` (padrão branco); índice de `baseColorTexture` ou `None` |
| `material_names(scene, model)` | RN-27: por textura (`scene.textures[i].filename` → nome do material do SketchUp com aquela textura) ou por cor (primeiro material liso com aquela cor); `clean_material_name`; senão `tr(DEFAULT_MATERIAL)` |
| `_nodes(scene)` | F-13, passo 1 |
| `_distance_to_box(point, lo, hi)` | Distância euclidiana do ponto à caixa (0 dentro) |
| `tree(scene, model)` | → `(grupos de topo, figuras puladas)`; F-13 |
| `_prune(groups)`, `walk(groups)`, `plan(scene, model)` | Poda; percorre em pré-ordem; lista plana dos grupos com malha (API da 009) |
| `texture_filename(texture, index)` | Último componente do caminho (separadores `\` e `/`); radical reduzido a `[A-Za-z0-9_-]` com `_` e sem `_` nas pontas; extensão em minúsculas ou pela `mime_type` (padrão `.png`); `skp_<i>_<radical><ext>` ou `skp_<i><ext>` |
| `failure_message(reason)` | RN-28 |

### `props.py` 🟢

| Propriedade (`BTM_PG_Aggregate`, em `Object.btm_aggregate`) | Definição | `update` |
|---|---|---|
| `is_aggregate` | `BoolProperty(default=False)` | — |
| `kind` | `EnumProperty(name="Tipo", items=KIND_ITEMS, default='AGGREGATE')`; `AGGREGATE` "Agregado" ("Peça presa ao pai"), `LEAF` "Folha de porta" ("Folha que abre e fecha") | — |
| `parent_ref` | `PointerProperty(name="Pai", type=Object)` | — |
| `face` | `EnumProperty(name="Face", items=FACE_ITEMS, default='NEG_Y')` | `_position` |
| `u`, `v`, `offset` | `FloatProperty(name="Horizontal"/"Vertical"/"Afastamento", subtype='DISTANCE', unit='LENGTH')`; `offset` com descrição "Positivo afasta do pai; negativo afunda no pai até a espessura dele" | `_position` |
| `perforate` | `BoolProperty(name="Perfurar", description="Recorta o pai no volume em que o agregado afunda (só no 3D)")` | `_perforate` |
| `real_hole` | `BoolProperty(name="Furo real no plano de corte", …)` | `_perforate` |
| `production_part` | `BoolProperty(name="Peça de produção", …)` | `_production` |
| `cutter`, `orig_parent`, `pivot` | `PointerProperty(type=Object)` | — |
| `orig_matrix` | `FloatVectorProperty(size=16)` (linhas da matriz de mundo) | — |
| `size` | `FloatVectorProperty(size=3, subtype='XYZ', unit='LENGTH')` | — |
| `rest_offset` | `FloatVectorProperty(size=3)` | — |
| `motion` | `EnumProperty(name="Movimento", items=MOTION_ITEMS, default='SWING')`; `SWING` "Giro", `SLIDE` "Correr" | `_leaf_setup` |
| `hinge` | `EnumProperty(name="Eixo", items=HINGE_ITEMS, default='LEFT')`; `LEFT` "Esquerda", `RIGHT` "Direita", `TOP` "Topo", `BOTTOM` "Base" | `_leaf_setup` |
| `swing_sign` | `EnumProperty(name="Sentido", items=SWING_ITEMS, default='OUT')`; `OUT` "Para fora", `IN` "Para dentro" | `_open` |
| `max_angle` | `FloatProperty(name="Ângulo máximo", default=90.0, min=1.0, max=180.0)` | `_open` |
| `slide_dir` | `EnumProperty(name="Sentido", items=SLIDE_ITEMS, default='POS_X')`; `POS_X` "Para a direita", `NEG_X` "Para a esquerda" | `_leaf_setup` |
| `travel` | `FloatProperty(name="Curso", default=0.5, min=0.001, subtype='DISTANCE', unit='LENGTH')` | `_travel` |
| `open_value` | `FloatProperty(name="Abertura", min=0.0, max=1.0, subtype='FACTOR', description="0 = fechada; 1 = abertura máxima. Para ao encostar em parede ou objeto")` | `_open` |
| `contact_name` | `StringProperty(name="Encostou em")` | — |
| `contact_kind` | `EnumProperty(items=[NONE "Nenhum", OPEN "Abrindo", CLOSE "Fechando"], default='NONE')` | — |
| `free_travel` | `FloatProperty(subtype='DISTANCE', unit='LENGTH', min=0.0)` | — |
| `rest_overlap` | `FloatProperty(subtype='DISTANCE', unit='LENGTH')` | — |

- `_guarded(name, func)` → `update(self, context)`: `obj = self.id_data`; `key = (obj.name, name)`; se `key in _guard` sai; senão adiciona, chama `func(obj, context)` e remove no `finally`. 🟢
- Destinos (import tardio): `_position` → `apply.update_position(obj)`; `_perforate` → `perforate.sync(obj)`; `_production` → `production.sync(obj)`; `_open` → `leaf.update_open(obj, context)`; `_travel` → se `free_travel > 0` e `travel > free_travel + 1e‑6`, `apply._write(obj, 'travel', free_travel)`; depois `_open`; `_leaf_setup` → `leaf.rebuild_pivot(obj)`. 🟢
- `register`: classe e `Object.btm_aggregate = PointerProperty(type=BTM_PG_Aggregate)`; `unregister`: `del` se existir e desregistra se registrada. 🟢

### `group_props.py`, `window_props.py` 🟢

| PropertyGroup | Campos |
|---|---|
| `BTM_PG_GroupMember` | `obj`, `orig_parent` (`PointerProperty(type=Object)`), `orig_matrix` (`FloatVectorProperty(size=16)`) |
| `BTM_PG_Group` (`Object.btm_group`) | `is_group` (`BoolProperty(default=False)`), `kind` (`EnumProperty(name="Papel", items=KIND_ITEMS, default='PLAIN')`; `PLAIN` "Grupo", `FRAME` "Esquadria", `LEAF` "Folha"), `members` (`CollectionProperty(type=BTM_PG_GroupMember)`) |
| `BTM_PG_WindowInstall` (`Object.btm_window`, na jaula) | `frame` (`PointerProperty(type=Object)`), `frame_matrix` (`FloatVectorProperty(size=16)`) |

🟢 Registro: classes na ordem (membro antes do grupo) e a `PointerProperty` em `bpy.types.Object`; `unregister` simétrico.

### `apply.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `local_box(obj)` | Caixa `(lo, hi)` do `bound_box` do objeto **avaliado** (com modificadores), no espaço local |
| `box_in_parent(obj, parent)` | Cantos do `bound_box` avaliado levados por `parent.matrix_world⁻¹ @ obj.matrix_world`; AABB no espaço do pai |
| `parent_box(obj)` | `local_box(parent_ref)` ou `None` |
| `current_box(obj)` | `lo = location + rest_offset`, `hi = lo + size` |
| `_write(obj, name, value)` | Adiciona `(obj.name, name)` a `props._guard`, `setattr(obj.btm_aggregate, name, value)`, remove no `finally` |
| `update_position(obj, sync_cut=True)` | F-02; devolve `(u, v, offset)` ou `None` |
| `aggregates_of(parent)` | Filhos diretos com `btm_aggregate.is_aggregate` e `parent_ref == parent` |
| `_busy`, `_last_parent_box` | Trava de reentrada; `{nome do pai: caixa}` (declarado duas vezes no arquivo, o segundo após o handler) |
| `on_depsgraph_update(scene, depsgraph)` | `@persistent`; F-02b |
| `register`/`unregister` | Acrescenta/remove o handler em `depsgraph_update_post` se ausente/presente |

### `convert.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `can_convert(obj, parent)` | → texto do motivo (`tr`) ou `None`; RN-05 |
| `convert(obj, parent, face=None)` | → face; F-01 |
| `unconvert(obj)` | → `bool`; F-01b |

### `perforate.py`, `production.py` 🟢

| Símbolo | Valor / comportamento |
|---|---|
| `BOOL_PREFIX`, `CUTTER_SUFFIX`, `EPSILON` | `"Agregado (furo): "`, `" - Recorte"`, `0.001` |
| `_cutpart_mod(obj)` | Primeiro modificador `NODES` cujo `node_group.name.split('.')[0] == 'GeoNodeCutpart'` |
| `real_hole_reason(obj)` | RN-09 |
| `_box_mesh(mesh, lo, hi)` | `bmesh.ops.create_cube(size=1.0)`, cada vértice `lo + (co + 0.5) × (hi − lo)`, `to_mesh`, `free`, `mesh.update()` |
| `_expanded(sunk, parent_box, face)` | Face POS: `hi[n] += EPSILON` e, se `lo[n] ≤ lo_p[n] + 1e‑9`, `lo[n] −= EPSILON`; face NEG: `lo[n] −= EPSILON` e, se `hi[n] ≥ hi_p[n] − 1e‑9`, `hi[n] += EPSILON` |
| `_remove_boolean(obj)` | Remove `parent.modifiers[BOOL_PREFIX + obj.name]`; apaga `cutter` e a malha dele se ficou sem usuários; `cutter = None` |
| `_remove_cutout(obj)` | Remove `parent.modifiers[machining.AGGREGATE_PREFIX + obj.name]` |
| `_sync_boolean(obj, sunk, parent_box)` | F-03, passo 3 |
| `_sync_cutout(obj, sunk)` | F-03, passo 4 |
| `sync(obj)` | F-03 |
| `production.sync(obj)` | `btm_geometry.fabrication = bool(production_part)` se o objeto tem `btm_geometry` |
| `production.sheet(obj)` | RN-10 |

### `leaf.py` 🟢

| Símbolo | Valor / comportamento |
|---|---|
| `PIVOT_SUFFIX`, `REST_KEY`, `FREE_CONTACT_KEY`, `OPEN_KEY` | `" - Eixo"`, `'btm_leaf_rest'`, `'btm_free_contact'`, `'btm_open_fraction'` |
| `OUT_SIGN` | RN-12 |
| `_matrix(values)`, `rest_matrix(obj)` | 16 floats → `Matrix` 4×4 por linhas; `None` sem `REST_KEY` |
| `local_corners(obj)` | Grupo: `box_corners(*group_box(obj))` (ou 8 × `Vector()` sem malhas); senão os 8 cantos do `bound_box` avaliado |
| `leaf_box(obj)` | AABB de `rest_matrix @ canto` (folha fechada no espaço do pai) |
| `frame_of(obj)` | `parent_ref` se é grupo `FRAME`, senão `None` |
| `sibling_leaves(obj)` | Varre `bpy.data.objects`: outros agregados `LEAF` com o mesmo `parent_ref` (só se há esquadria) |
| `_span_x(box)`, `frame_span(frame)` | `(lo.x, hi.x)`; da `group_box(frame)` (espaço do próprio grupo) ou `None` |
| `displacement(obj)` | `0` se não `SLIDE`; senão `sign(slide_dir) × travel × current_fraction` |
| `base_point(box, motion, hinge)` | RN-12 |
| `swing_angle(agg, fraction)` | RN-12 (fração presa a [0, 1]; radianos) |
| `pose_matrix(agg, base, fraction)` | RN-12 |
| `pivot_of(obj)` | `agg.pivot` se ainda em `bpy.data.objects`; `ReferenceError` → `None` |
| `_base(obj)` | `Vector(pivot['btm_leaf_base'])` ou `None` |
| `apply_fraction(obj, fraction)` | `pivot.matrix_basis = pose_matrix(agg, _base, fraction)`; `pivot[OPEN_KEY] = fraction` (sem teste) |
| `current_fraction(obj)` | `pivot[OPEN_KEY]` (padrão 0) ou 0 sem pivô |
| `rebuild_pivot(obj)` | F-04, passos 3 a 6 |
| `default_slide_dir(obj)` | `slide_limits.default_direction(_span_x(leaf_box), frame_span)` ou `'POS_X'` sem esquadria |
| `measure_free_travel(obj)` | F-07 |
| `low_travel(obj)` | Só `SLIDE` em esquadria com `free_travel > 0`: `slide_limits.low_travel(free_travel, largura X de leaf_box)` |
| `make_leaf(obj, parent, motion='SWING', hinge='LEFT', swing_sign='OUT', max_angle=90.0, slide_dir='POS_X', travel=0.5)` | F-04 |
| `remove_pivot(obj)` | Com pai e pose fechada: folha filha direta do pai, identidade, `matrix_basis = rest`; apaga o pivô; `pivot = None`; apaga `REST_KEY` |
| `update_open(obj, context)` | F-05 |
| `_close_floor(obj, scale)` | `(0, None)` se não `SLIDE`; senão o maior `close_stop(sign(slide_dir), displacement(irmã))` entre as irmãs, preso a `scale`, e a irmã que o impõe |

### `collision.py` 🟢

| Símbolo | Valor / comportamento |
|---|---|
| `SHRINK`, `OPENING_FRAME_PROP`, `_SKIP_DISPLAY` | `0.001`, `'btm_opening_frame'`, `{'WIRE', 'BOUNDS'}` |
| `_BOX_FACES` | `((0,1,2,3), (4,7,6,5), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0))` na ordem do `bound_box` |
| `_cache` | `{nome da folha: [[objeto, (lo, hi) de mundo, BVH/False/None], …]}` |
| `_aabb(points)`, `_overlap(a, b)` | AABB; sobreposição fechada (`≤`) nos 3 eixos |
| `_own(obj)` | Nomes da folha, do pivô e de `obj.children_recursive` |
| `invalidate(obj=None)` | Limpa tudo ou só a entrada da folha |
| `_excluded(obj)`, `_targets(obj)`, `_bvh(item)` | F-08 |
| `Tester(obj)` | `parent_world` (cópia), `base = leaf._base(obj)`, `local = obj.matrix_basis` (folha no pivô), `corners` = cantos de `local_corners` cada um movido `SHRINK` em direção ao centro (se a distância ao centro > `SHRINK`); `corners_at(fraction) = parent_world @ pose_matrix(agg, base, fraction) @ local @ canto`; `hit(fraction)` F-08 |
| `on_depsgraph_update` | `@persistent`; F-08b |
| `register`/`unregister` | Handler em `depsgraph_update_post`; `unregister` limpa `_cache` |

### `group.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `is_group(obj)` | `obj.btm_group.is_group` (falso para `None` ou sem a propriedade) |
| `members(group)` | `m.obj` vivos em `bpy.data.objects` |
| `object_corners(obj, depsgraph)` | Não-Empty: cantos do `bound_box` avaliado; Empty: cantos de mundo das malhas de `children_recursive` levados por `matrix_world.inverted_safe()`; nenhum → 8 × `Vector()` |
| `world_box(objs)` | AABB de mundo das **malhas** de `objs` ou `None` |
| `group_box(group, space=None)` | AABB das malhas de `members(group)` no espaço `space` (padrão `group.matrix_world`), por `inverted_safe()`; `None` sem malhas |
| `create_group(objs, kind='PLAIN', name="Grupo")` | F-09 |
| `ungroup(group)` | F-09b |
| `box_corners(lo, hi)` | 8 cantos na ordem `(x0,y0,z0), (x0,y0,z1), (x0,y1,z1), (x0,y1,z0), (x1,y0,z0), (x1,y0,z1), (x1,y1,z1), (x1,y1,z0)` |

### `install.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `WINDOW_FLAG`, `WALL_FLAG`, `DEFAULT_SILL`, `NOT_HB_WALL` | `'IS_WINDOW_BP'`, `'IS_WALL_BP'`, `1.0`, `N_("Converta a parede pelo editor de paredes antes de instalar")` |
| `is_frame(obj)`, `frame_of(obj)` | Grupo `FRAME`; sobe pelos pais até o primeiro grupo `FRAME` |
| `cage_of(frame)` | O pai, se tem `IS_WINDOW_BP` e `btm_window.frame == frame`; senão `None` |
| `can_install(frame, wall)` | Sem esquadria → "Selecione a esquadria (Montar esquadria) e a parede"; já instalada → "A janela já está instalada"; sem parede → "Selecione também a parede"; parede sem `IS_WALL_BP` → `NOT_HB_WALL` |
| `install(context, frame, wall, sill=DEFAULT_SILL)` | F-11 |
| `uninstall(context, cage)` | F-11b |

### Operadores 🟢

| Classe | `bl_idname` | `bl_label` | `bl_options` | Propriedades | `poll` |
|---|---|---|---|---|---|
| `BTM_OT_AggregateConvert` | `caffmob.aggregate_convert` | "Converter em agregado" | `{'REGISTER', 'UNDO'}` | `face`: `AUTO` "Mais próxima" + `FACES` (padrão `AUTO`) | ativo não nulo e ao menos um selecionado ≠ ativo que é malha ou grupo |
| `BTM_OT_LeafConvert` | `caffmob.leaf_convert` | "Converter em folha de porta" | `{'REGISTER', 'UNDO'}` | `motion`, `hinge`, `swing_sign`, `max_angle` (1–180, 90), `slide_dir`, `travel` (≥ 0,001, 0,5) | ativo e **exatamente um** selecionado malha/grupo além dele |
| `BTM_OT_AggregateUnconvert` | `caffmob.aggregate_unconvert` | "Desconverter" | `{'REGISTER', 'UNDO'}` | — | algum selecionado com `is_aggregate` |
| `BTM_OT_AggregateMove` | `caffmob.aggregate_move` | "Mover agregado" | `{'REGISTER', 'UNDO', 'BLOCKING'}` | — | área `VIEW_3D` e ativo com `is_aggregate` |
| `BTM_OT_DeleteWithAggregates` | `caffmob.delete_with_aggregates` | "Apagar" | `{'REGISTER', 'UNDO'}` | `with_aggregates` "Apagar também os agregados" (padrão `True`; descrição "Desligado: os agregados ficam soltos na mesma posição") | RN-29 |
| `BTM_OT_GroupCreate` | `caffmob.group_create` | "Criar grupo" | `{'REGISTER', 'UNDO'}` | `name` "Nome" (padrão "Grupo") | malhas selecionadas cujo pai não é grupo; senão `poll_message_set("Selecione as peças do grupo")` |
| `BTM_OT_GroupDissolve` | `caffmob.group_dissolve` | "Desfazer grupo" | `{'REGISTER', 'UNDO'}` | — | `_active_group` não nulo |
| `BTM_OT_WindowAssemble` | `caffmob.window_assemble` | "Montar esquadria" | `{'REGISTER', 'UNDO'}` | `rows` (`CollectionProperty(BTM_PG_AssembleRow)`), `name` (padrão "Janela") | `_assemble_meshes` não vazio; senão "Selecione as peças do grupo" |
| `BTM_OT_WindowInstall` | `caffmob.window_install` | "Instalar na parede" | `{'REGISTER', 'UNDO'}` | `sill` "Peitoril" (≥ 0, 1,0, `DISTANCE`) | `can_install(*_selection)` é `None`; senão `poll_message_set(motivo)` |
| `BTM_OT_WindowUninstall` | `caffmob.window_uninstall` | "Desinstalar" | `{'REGISTER', 'UNDO'}` | — | `_cage(context)` não nulo |
| `BTM_OT_ImportModel` (`Operator`, `ImportHelper`) | `caffmob.import_model` | "Importar modelo 3D" | `{'REGISTER', 'UNDO'}` | `filter_glob` `"*.obj;*.fbx;*.glb;*.gltf;*.skp"` (`HIDDEN`), `unit` (`AUTO` "Automática", `MM`, `CM`, `M`, `IN`; padrão `AUTO`), `up_axis` (`Z`, `Y`; padrão `Z`) | — |

- `BTM_PG_AssembleRow`: `label`, `names` (nomes separados por `"\n"`), `count` (`IntProperty`), `role` (`EnumProperty(name="Papel", items=ROLE_ITEMS)`; `FRAME` "Esquadria", `SLIDE` "Folha de correr", `SWING` "Folha de giro", `IGNORE` "Ignorar"). 🟢
- Auxiliares: `_selected_meshes(context)` → `(ativo, [selecionados ≠ ativo, malha ou grupo])`; `_aggregates(context)` → selecionados com `is_aggregate`; `ops_group._meshes` → malhas selecionadas cujo pai **não** é grupo; `_import_groups` → grupos `PLAIN` selecionados; `_assemble_meshes` → `_meshes` + malhas membros desses grupos sem repetir; `_active_group` → ativo (ou `bpy.data.objects[ativo['btm_leaf']]`) subindo até um grupo; `ops_install._selection` → (esquadria = primeiro `frame_of` não nulo entre os selecionados sem `IS_WALL_BP`, parede = **último** selecionado com `IS_WALL_BP`; objeto sem `IS_WALL_BP` nunca vira parede, o que torna `NOT_HB_WALL` inalcançável pelo operador) _(Revisão 2026-10-10: texto corrigido; ops_install.py:_selection)_; `_cage(context)` → ativo se tem `IS_WINDOW_BP` e `btm_window.frame`, senão `cage_of(frame_of(ativo))`. 🟢
- Keymap: `keyconfigs.addon`, mapa "Object Mode" (`space_type='EMPTY'`), itens `X` e `DEL` `PRESS` com `head=True` → `caffmob.delete_with_aggregates`; `unregister` remove engolindo `ReferenceError`/`RuntimeError`. 🟢

### `overlay.py`, `panels.py` 🟢

| Símbolo | Valor |
|---|---|
| `PATH_COLOR`, `AXIS_COLOR`, `LEAF_COLOR`, `HIT_COLOR` | `(0.2, 0.75, 1.0, 0.9)`, `(1.0, 0.8, 0.1, 1.0)`, `(0.2, 0.75, 1.0, 0.6)`, `(1.0, 0.2, 0.2, 1.0)` |
| `ARC_STEPS`, `_EDGES` | `24`; 12 arestas da caixa pela ordem do `bound_box` |
| `_handles` | Lista com os 2 handles (`_draw_3d` `POST_VIEW`, `_draw_2d` `POST_PIXEL`), adicionados uma vez no `register` e removidos no `unregister` |
| `_active_leaf(context)` | Ativo; se tem `btm_leaf`, a folha apontada; sobe pelos pais até um agregado `LEAF`; exige `pivot_of` |
| `panels.draw_aggregate(layout, context, include_import=True)` | F-16 |
| `BTM_PT_Aggregate` | `bl_label "Agregados e folhas"`, `bl_idname "BTM_PT_aggregate"`, `VIEW_3D`/`UI`, `bl_category "CAFFMob Draw"`, `bl_parent_id "BTM_PT_object_properties"`, `DEFAULT_CLOSED`; **não registrado** (`classes = ()`); a barra lateral única chama `draw_aggregate(body, context, include_import=False)` no grupo `sel_aggregates` |

### Superfície usada pelos consumidores 🟢 (fora da unit, citada para reimplementação)

| Consumidor | Usa | Contrato |
|---|---|---|
| `openings/sync.py` | `group.create_group`, `leaf.make_leaf`, `apply._write('travel')`, `collision.OPENING_FRAME_PROP` | Contrato em `_reversa_sdd/openings/` F-05 |
| `cabinet_editor/scene_slides.py` | `group.create_group('FRAME'/'LEAF')`, `leaf.make_leaf('SLIDE')`, `leaf.measure_free_travel`, `leaf.FREE_CONTACT_KEY`, `convert.unconvert` | Deslizantes do editor: curso livre < altura do trilho vira aviso `BLOCKED` |
| `selection/component.py` | `btm_aggregate`, `btm_group` | Raiz e `own_aggregates` (contrato em `_reversa_sdd/selection/` RN-10, EC-07) |
| `selection/resize.py` | `apply.local_box`, `apply.update_position`, `limits` | Estica/reposiciona agregados ao redimensionar o pai |
| `selection/element_size.py`, `move_over/scene.py` | `group.object_corners` | Caixa de Empty pela união das malhas |
| `object_library/item_io.py`, `object_library/ops.py` | `group.is_group`, `group.create_group`; `bpy.ops.caffmob.import_model(filepath=…)` | Item da biblioteca vira grupo `PLAIN` |
| `stick/frame.py`, `stick/props.py`, `stick/link.py` | `limits` (`FACES`, `FACE_LABELS`, `face_axes`, `thickness`; **não** usa `box_for`) | Grudar sem limite de contorno (o grudar calcula a própria pegada) _(Revisão cruzada 2026-10-10: imports de `aggregates.limits` em caffmob_draw/stick/)_ |
| `operators/doors_windows.py`, `legacy/convert.py` | `ops_aggregate.delete_components` | Apagar porta/janela inteira; apagar herdados em lote com `keep_aggregates=False` |
| `cutting/part_sources.py` | `production.sheet` | Agregado marcado entra como placa, dentro de `geometry_records`: `source="FREE_GEOMETRY"`, `module_uid=None`, uid `<btm_uid>/<btm_geometry.component>/0`, `finish`/`material`/`component` lidos de `btm_geometry` (ver EC-23) _(Revisão cruzada 2026-10-10: part_sources.py:294-306)_ |
| `inspection/adapters/aggregate_leaf.py` | `leaf.pivot_of`, `current_fraction`, `apply_fraction`, `swing_angle` | Folha convertida aberta na inspeção, sem teste de contato |
| `ui/object_properties.py` | `panels.draw_aggregate`, `apply.parent_box`, `limits.limits` | Grupo "Agregados e folhas"; linha "Agregado: horizontal até…, vertical até…, afunda até…" |
| `ui/sidebar_insert.py` | `caffmob.import_model` | Botão "Importar modelo 3D" em Inserir |
| `stick/settle.py` | `'caffmob.aggregate_move'` em `_MOVE_IDS` | Reconhece o arraste do agregado como movimento |

## Fluxo Principal

1. 🟢 O usuário importa um modelo (`caffmob.import_model`, F-12/F-13) ou usa uma malha da cena; opcionalmente agrupa (F-09) ou monta a esquadria (F-10).
2. 🟢 Converte em agregado (F-01) ou em folha (F-04); o agregado é posicionado por F-02 e pode perfurar (F-03); a folha abre por F-05 com o contato de F-08.
3. 🟢 A esquadria pode ser instalada numa parede (F-11). O X/Delete apaga componentes (F-15).

### F-01 `convert(obj, parent, face=None)` 🟢 (ver `_reversa_sdd/flowcharts/aggregates.md` §1)
1. Se `not agg.is_aggregate`: `orig_parent = obj.parent`, `orig_matrix` = 16 valores por linha de `obj.matrix_world`.
2. `world = matrix_world.copy()`; `obj.parent = parent`; `matrix_parent_inverse = Identity`; `matrix_basis = parent.matrix_world⁻¹ @ world`; `view_layer.update()`.
3. `box_p = local_box(parent)`; `box_a = box_in_parent(obj, parent)`; centro de `box_a`; `face = face or nearest_face(box_p, centro)`.
4. `size = limits.size(box_a)`; `rest_offset = box_a.lo − location`; `(u, v, offset) = params_from_box(box_p, box_a, face)`; grava `face`, `u`, `v`, `offset` por `_write` (sem `update`).
5. `parent_ref = parent`; `is_aggregate = True`; `update_position(obj)`; devolve `face`.

F-01b `unconvert(obj)`: `not is_aggregate` → `False`. Se `perforate` ou `cutter`: `_write(perforate=False)`, `_write(real_hole=False)`, `perforate.sync`. `kind == 'LEAF'` → `leaf.remove_pivot`. `production_part` → `_write(False)` e `production.sync`. `obj.parent = orig_parent`, identidade, `matrix_world = orig_matrix`; `is_aggregate = False`, `kind = 'AGGREGATE'` (atribuição direta), `parent_ref = None`; `True`. Não limpa `orig_*`, `size`, `travel`, `free_travel`, `rest_overlap`, `contact_*` (EC-02). 🟢

### F-02 `update_position(obj, sync_cut=True)` 🟢 (ver `flowcharts/aggregates-limits.md`)
1. Sai com `None` se `not is_aggregate`, `kind == 'LEAF'`, `parent_ref is None` ou `obj.parent != parent_ref`.
2. `box_p = parent_box(obj)`; `(u, v, offset) = clamp(box_p, size, face, u, v, offset)`; cada campo que difere > 1e‑9 é regravado por `_write`.
3. `lo = box_for(...).lo`; `target = lo − rest_offset`; `location = target` se difere > 1e‑9.
4. Se `sync_cut` e (`perforate` ou `cutter`): `perforate.sync(obj)`. Devolve `(u, v, offset)`.

F-02b `on_depsgraph_update(scene, depsgraph)`: `_busy` → sai; senão `_busy = True`; para cada `update` com `is_updated_geometry` e `id` `Object`: `original = update.id.original`; `aggregates_of(original)` vazio → próximo; `box = local_box(original)`; igual a `_last_parent_box[original.name]` → próximo; grava e chama `update_position` em cada filho. `ReferenceError` é engolido; `finally` solta `_busy`. 🟢

### F-03 `perforate.sync(obj)` 🟢
1. `parent_ref is None` → sai. `parent_box = local_box(pai)`; `sunk = sunk_box(parent_box, current_box(obj), face)` se `perforate`, senão `None`.
2. `sunk is None` → `_remove_boolean` e `_remove_cutout`; sai.
3. `_sync_boolean`: `lo, hi = _expanded(...)`; sem `cutter`, cria malha e objeto "`<agregado> - Recorte`", liga às coleções do pai, `parent = pai` (sem mexer em `matrix_parent_inverse`), `IS_CUTTING_OBJ = True`, `display_type = 'WIRE'`, `hide_render = True`, `hide_set(True)`, `agg.cutter`. `key = [round(v, 6) for v in lo + hi]`; se difere de `cutter['btm_box']`, `_box_mesh` e grava a chave. Modificador "Agregado (furo): `<agregado>`" criado se ausente (`BOOLEAN`, `DIFFERENCE`, `EXACT`); `mod.object = cutter`.
4. `real_hole` e `real_hole_reason is None` → `_sync_cutout`: lê `Mirror Y`, `Mirror Z`, `Thickness` do `GeoNodeCutpart` por `compat.try_get_gn_input`; `(x0, y0), (x1, y1)` do `sunk`; `Mirror Y` → `y0, y1 = −y1, −y0`; `depth = min(sunk_z, Thickness)`; cria o `CPM_CUTOUT` por `GeoNodeCutpart(pai).add_part_modifier('CPM_CUTOUT', nome)` se ausente; grava `X`, `End X`, `Y`, `End Y`, `Route Depth`, `Flip Z` só os que diferem > 1e‑7 (ou ilegíveis); liga `show_viewport`/`show_render`. Senão `_remove_cutout`.

### F-04 `make_leaf(obj, parent, ...)` e `rebuild_pivot(obj)` 🟢 (ver `flowcharts/aggregates.md` §2)
1. Se `not is_aggregate`: guarda `orig_parent`/`orig_matrix`. `obj['btm_leaf_rest'] = parent.matrix_world⁻¹ @ obj.matrix_world` (16 floats, a pose **atual** vira a fechada).
2. Grava por `_write` `kind='LEAF'`, `motion`, `hinge`, `swing_sign`, `max_angle`, `slide_dir`, `travel`, `open_value=0.0`; `parent_ref = parent`; `is_aggregate = True`; `contact_name = ""`; `contact_kind = 'NONE'`. Para cada irmã com `REST_KEY`: `rest_overlap` nas duas (RN-16). Devolve `rebuild_pivot(obj)`.
3. `rebuild_pivot`: sai com `None` se `kind != 'LEAF'`, sem `parent_ref` ou sem `REST_KEY`. `base = base_point(leaf_box(obj), motion, hinge)`.
4. Sem pivô vivo: Empty novo "`<folha> - Eixo`" (`SINGLE_ARROW` se `SWING`, senão `PLAIN_AXES`; tamanho 0,1), ligado às coleções da folha (ou do pai); `agg.pivot = pivô`.
5. `pivot['btm_leaf'] = obj.name`; `pivot['btm_leaf_base'] = list(base)`; `pivot.parent = pai` (identidade); `obj.parent = pivot` (identidade); `obj.matrix_basis = Translation(−base) @ rest`; `apply_fraction(obj, 0.0)`.
6. `SLIDE` com esquadria → `measure_free_travel(obj)` (F-07). `update_open(obj, bpy.context)` (leva à `open_value` atual). Devolve o pivô.

### F-05 `update_open(obj, context)` 🟢 (ver `flowcharts/aggregates-leaf_sweep.md`)
1. Sai se `kind != 'LEAF'` ou sem pivô. `target = clamp(open_value, 0, 1)`; `current = current_fraction(obj)`.
2. `SLIDE` → `scale = travel`, `SLIDE_STEP`, `SLIDE_TOLERANCE`; senão `scale = max_angle`, `SWING_STEP`, `SWING_TOLERANCE`. `scale ≤ 0` → sai.
3. `tester = collision.Tester(obj)`; `closing = target < current`.
4. Sem esquadria: `sweep(current·scale, target·scale, lambda v: tester.hit(v/scale), step, tol)`. Com esquadria: `floor, floor_contact = _close_floor(obj, scale)`; mesma chamada com `close=True, floor=floor, floor_contact=floor_contact`.
5. `fraction = alcançado/scale`; `apply_fraction`; `contact_name` = nome do contato (se tem `name`) ou "". Se sem contato, abrindo, `SLIDE`, `free_travel > 0` e `alcançado ≥ free_travel − tol`: `contact_name = obj['btm_free_contact']`.
6. `contact_kind = ('CLOSE' se closing senão 'OPEN')` se há `contact_name`, senão `'NONE'`. Se `|fraction − open_value| > 1e‑6`, `_write('open_value', fraction)`. Redesenha as áreas `VIEW_3D` da `context.screen`.

### F-06 `sweep(current, target, hit, step, tolerance, close, floor, floor_contact)` 🟢 (puro)
1. `target ≤ current` (fechar): sem `close` → `(target, None)`. Com `close`: `stop = max(target, floor)`; `stop ≥ current` → `(current, floor_contact se floor > target, senão None)`; senão varredura espelhada `sweep(−current, −stop, lambda v: hit(−v), step, tolerance)`, negada; sem contato e `floor > target` → contato = `floor_contact`.
2. Abrir: `free = current`; enquanto `free < target`: `probe = min(free + step, target)`; `hit(probe)` truthy → `blocked = probe`; enquanto `blocked − free > tolerance`: `middle = (free + blocked)/2`; contato → `blocked = middle` (contato atualizado), senão `free = middle`; devolve `(free, contato)`. Sem contato → `free = probe`.
3. Fim → `(target, None)`. Só os pontos amostrados são testados (EC-05).

### F-07 `measure_free_travel(obj)` e `_close_floor` 🟢
1. `span = frame_span(frame_of(obj))`; sem `span` ou sem pivô → `0.0`.
2. `probe = span.hi − span.lo`; `_write(free_travel=0)`, `_write(travel=probe)`; `collision.invalidate(obj)`; `tester = Tester(obj)`.
3. `reached, contact = sweep(0, probe, lambda v: tester.hit(v/probe), SLIDE_STEP, SLIDE_TOLERANCE)`; `free = max(0, reached)`; `obj['btm_free_contact'] = contact.name` (ou "").
4. `_write(free_travel=free)`, `_write(travel=max(free, 0.001))`; `apply_fraction(obj, 0)`; devolve `free`.

### F-08 Contato (`collision.py`) 🟢
1. `_excluded(obj)`: `_own(obj)`; com esquadria: `+ _own(irmã)` de cada irmã `+ nome do FRAME`. Sem esquadria e com pai: `root = fronts.module_root_of(pai) or pai`; `+ root`, `+ root.children_recursive`, `+ pai`.
2. `_targets(obj)` (cache por nome da folha): para cada objeto da cena fora de `skip`, `MESH`, `display_type` fora de `WIRE`/`BOUNDS`, sem `IS_CUTTING_OBJ`/`IS_2D_ANNOTATION`, `visible_get()`, e `get('btm_opening_frame') != nome do pai`: AABB de mundo do avaliado; BVH ainda `None`.
3. `_bvh(item)`: na primeira vez, `evaluated.to_mesh()`, vértices em mundo e polígonos → `BVHTree.FromPolygons` (ou `False` sem geometria), `to_mesh_clear()`.
4. `Tester.hit(fraction)`: cantos na pose, AABB; candidatos cuja AABB cruza; nenhum → `None`; senão `BVHTree.FromPolygons(cantos, _BOX_FACES)` e devolve o **primeiro** candidato (ordem de `scene.objects`) cuja BVH cruza.
5. F-08b `on_depsgraph_update`: com cache, monta o conjunto dos nomes das folhas em cache e seus pivôs; qualquer `update` de `Object` cujo `original.name` está fora desse conjunto limpa o cache inteiro.

### F-09 `create_group(objs, kind, name)` 🟢
1. Filtra malhas; nenhuma → `None`. `lo, hi = world_box(objs)`.
2. Empty `name` (`CUBE`, 0,05), ligado às coleções de `objs[0]` (ou `scene.collection`); `location = ((lo.x+hi.x)/2, (lo.y+hi.y)/2, lo.z)` (eixos do mundo).
3. Se `{o.parent}` tem um único elemento não nulo: o grupo vira filho dele mantendo o mundo. `view_layer.update()`.
4. `is_group = True`, `kind`; por malha: `members.add()` com `obj`, `orig_parent`, `orig_matrix`; filha do grupo mantendo o mundo (identidade). Devolve o grupo.

F-09b `ungroup(group)`: `view_layer.update()`; cada membro vivo volta a `orig_parent` com a matriz de mundo **atual** (identidade); apaga o Empty; devolve as peças. `orig_matrix` dos membros nunca é lido. 🟢

### F-10 `caffmob.window_assemble` 🟢 (ver `flowcharts/aggregates.md` §3)
1. `invoke`: `_suggest` (limpa `rows`; por `grouping.suggest` dos nomes de `_assemble_meshes`: linha com `label`, `names`, `count`, `role = 'FRAME'` para a esquadria, `'SLIDE'` para as folhas); diálogo de largura 380 com `name` e uma linha "{rótulo} ({n} peças)" + papel por grupo.
2. `execute`: sem `rows` (script) → `_suggest`. `frame_names` = nomes das linhas `FRAME`; `objs` = `{nome: malha}` de `_assemble_meshes`; desfaz (`ungroup`) cada grupo `PLAIN` selecionado.
3. `frame = create_group(malhas FRAME, 'FRAME', name or "Janela")`; `None` → WARNING, `CANCELLED` (EC-12).
4. Por linha `SLIDE`/`SWING`: `sash = create_group(peças, 'LEAF', label)`; filho da esquadria com `matrix_parent_inverse = frame.matrix_world⁻¹` e o mundo preservado. `view_layer.update()`.
5. `SLIDE`: `make_leaf(sash, frame, 'SLIDE', slide_dir='POS_X', travel=0.5)`; `direction = default_slide_dir(sash)`; se difere, `sash.btm_aggregate.slide_dir = direction` (o `update` refaz o pivô e mede o curso). `SWING`: `make_leaf(sash, frame, 'SWING')`.
6. Seleciona e ativa a esquadria; INFO "{esquadria}: esquadria com {n} peça(s) e {m} folha(s)".

### F-11 `install(context, frame, wall, sill)` 🟢
1. `lo, hi = group_box(frame)` (espaço do grupo); `width = hi.x − lo.x`, `height = hi.z − lo.z`; `Length`, `Thickness` da parede; `center = frame.matrix_world @ ((lo + hi)/2)`; `x = (wall.matrix_world⁻¹ @ center).x − width/2`, preso a `[0, Length − width]` por `max(0, min(x, …))`; `saved` = matriz de mundo da esquadria.
2. `GeoNodeCage().create("Window")`; `IS_WINDOW_BP = True`; `WIRE`; `Dim X = width`, `Dim Y = Thickness`, `Dim Z = height`; filha da parede (identidade) em `(x, 0, sill)`, rotação zero; `btm_window.frame = frame`, `frame_matrix = saved`.
3. Esquadria filha da jaula (identidade), rotação zero, `location = (0, 0, −lo.z)`; drivers `location.x = dim_x/2` e `location.y = dim_y/2` por `GeoNodeObject(frame).driver_location` com `cage.var_input('Dim X', 'dim_x')`/`('Dim Y', 'dim_y')`.
4. `doors_windows.cut_wall(wall, cage)` (modificador `BOOLEAN` "Boolean_`<jaula>`" `DIFFERENCE`/`EXACT`, jaula fora do render); `view_layer.update()`; devolve a jaula. O operador seleciona e ativa a jaula; INFO "{esquadria} instalada em {parede}".

F-11b `uninstall(context, cage)`: com esquadria: guarda o mundo, `driver_remove('location', 0)` e `(…, 1)`, `parent = None`, identidade, restaura o mundo. Com parede: remove todo `BOOLEAN` com `object == cage`. Apaga os filhos da jaula que não são a esquadria e a jaula; `view_layer.update()`; devolve a esquadria. O operador seleciona e ativa a esquadria; INFO "Janela desinstalada". 🟢

### F-12 `caffmob.import_model.execute` (OBJ, FBX, glTF) 🟢
1. `ext` em minúsculas; `.skp` → F-13. Fora de `FORMATS` → ERROR "Formato não suportado: {ext ou "sem extensão"} (use OBJ, FBX, glTF, GLB ou SKP)", `CANCELLED`.
2. `before = set(bpy.data.objects)`; chama `bpy.ops.<módulo>.<operador>(filepath, **_kwargs(ext))`. `RuntimeError` → ERROR "O Blender não conseguiu importar {arquivo}: {erro}"; resultado sem `FINISHED` → ERROR "Importação cancelada: {arquivo}"; ambos `CANCELLED`.
3. `new` = objetos novos; `meshes` = os `MESH`. `_apply_unit`: glTF com `AUTO` → "m" sem escala; senão `view_layer.update()`, `largest` = maior medida de `world_box(new)` (0 sem malhas), `factor = scale_for(unit, largest)`; se `|factor − 1| > 1e‑12`, `matrix_world = Scale(factor) @ matrix_world` nas raízes (pai ausente ou fora de `new`) e, em toda malha de `new` com `data.users == 1`, `data.transform(Diagonal(scale))` e `scale = (1, 1, 1)`. Devolve "mm"/"cm"/"m"/"pol".
4. `root = _group_import(new, meshes, nome do arquivo sem extensão)` (RN-25). Com raiz: seleciona e ativa a raiz; INFO "{n} malha(s) importada(s) num grupo, unidade: {u}. Alt + clique seleciona uma peça; para converter, selecione as peças com Alt + Shift + clique, o pai por último". Sem raiz: seleciona as malhas, ativa a primeira; INFO "{n} malha(s) importada(s), unidade: {u}. Selecione o pai por último e use "Converter em agregado" ou "Montar esquadria"".

### F-13 SketchUp (`_import_skp`, `skp.read`, `skp_core.tree`, `skp_build.build`) 🟢 (ver `flowcharts/aggregates-skp_tree.md`)
1. `progress_begin(0, 2)`; `skp.read(path)`: `available()` (import de `openskp`; falha → "leitor de SketchUp indisponível nesta instalação ({módulo})"); `SkpFile(path).parse()` e `build_scene()`; `FileNotFoundError` → "arquivo não encontrado"; outra exceção → `str(exc)` ou o nome do tipo; sem `glb_primitives` → "o arquivo não tem geometria"; tudo como `ValueError` → ERROR `failure_message`, `CANCELLED`.
2. `tree`: `names = material_names`; `_nodes`: sem `scene_hierarchy`, um nó falso por caminho distinto das primitivas, todos no topo; com ela, percurso em pré-ordem (pilha) com ids sequenciais, pulando figuras de escala (nome ou `definition_name`) e guardando o caminho delas em `banned`.
3. Por primitiva: caminho do `mesh_index` (ou "ROOT"); caminho banido ou descendente (`b + " / "`) → pula; `verts = to_blender`; vários nós no caminho → o de menor `_distance_to_box(position_mm, caixa da primitiva em mm)`; um → ele; nenhum → `root_plan` "SketchUp". Chave = `frozenset` dos vértices arredondados a 6 casas: repetida no mesmo alvo → pula. `tris`; `uvs` com `v → 1 − v`; material pelo índice (fora da faixa → "SketchUp padrão"); `MeshPlan("{grupo} {k}", …)`.
4. Pendura cada plano no pai (`parent` 0 → topo); `_prune` (pós-ordem): sem malhas e sem filhos sai; sem malhas e com um filho só é substituído pelo filho; `root_plan` com malhas entra na frente.
5. `build`: `collection = context.collection or scene.collection`; pasta `tempfile.mkdtemp(prefix="caffmob_skp_")`; `_build_node` recursivo: filhos primeiro; malhas (`from_pydata`, UV "UVMap" se `len(uvs) == len(verts)`, material, `validate`, `update`); `view_layer.update()`; grupo `create_group(malhas, 'PLAIN', nome)` ou `_empty_group` (Empty `CUBE` 0,05 no centro da base das malhas dos filhos, `btm_group` `PLAIN`, sem membros); filhos parentados ao grupo mantendo o mundo.
6. `_material`: cache por `(nome, índice)`; cor `baseColorFactor` (padrão `[0.8, 0.8, 0.8, 1]`); assinatura RN-27; material existente com `btm_skp_material` e a mesma `btm_skp_key` → reaproveita; senão `materials.new(nome)`, marcas, `diffuse_color`, `Base Color` do Principled e, com textura, um `ShaderNodeTexImage` 320 à esquerda ligado a `Base Color`; `_image` grava os bytes, `images.load(check_existing=False)`, `pack()`.
7. Exceção em `build` → apaga os objetos novos (só objetos), ERROR `failure_message`, `CANCELLED`; `progress_end` no `finally`. Sucesso → seleciona os grupos de topo, ativa o primeiro, INFO RN-28/CA-21.

### F-14 `caffmob.aggregate_move` 🟢
1. `invoke`: `obj` = ativo; `start = (u, v)`; `anchor = _hit` (raio do mouse × plano da face do pai: ponto = face da `parent_box` levada ao mundo, normal = eixo da face girado por `parent.matrix_world.to_3x3()`); `None` → WARNING, `CANCELLED`. `modal_handler_add`; texto de status "Mover agregado  |  Clique: confirmar  |  Botão direito/Esc: cancelar".
2. `MOUSEMOVE`: `hit` válido → `delta = pai⁻¹ @ hit − pai⁻¹ @ anchor`; `agg.u = start.u + delta[eixo u]`, `agg.v = start.v + delta[eixo v]` (cada atribuição dispara F-02).
3. `LEFTMOUSE PRESS` → limpa o status, `FINISHED`. `RIGHTMOUSE`/`ESC` `PRESS` → `u, v = start`, limpa, `CANCELLED`. Qualquer outro evento → `RUNNING_MODAL` (consumido, inclusive navegação: EC-11).

### F-15 X/Delete (`BTM_OT_DeleteWithAggregates`, `delete_components`) 🟢 (ver `flowcharts/aggregates.md` §4)
1. `poll`: `context.mode == 'OBJECT'` e algum selecionado com (`children` e `component.deletes_subtree(o)`) ou `_children_aggregates(o)` (= `component.own_aggregates`, `ReferenceError` → `[]`) ou `_stuck_children(o)` (= `stick.apply.stuck_items`, `ReferenceError` → `[]`).
2. `invoke`: sem agregados próprios → `execute` direto (sem diálogo); senão `invoke_props_dialog(title="O objeto tem agregados")` com "{n} agregado(s) presos aos objetos selecionados." e `with_aggregates`.
3. `execute` → `delete_components(list(selecionados), keep_aggregates=not with_aggregates)`; `FINISHED`.
4. `delete_components(targets, keep_aggregates=False)`: `_release_stuck_children(targets)` (para cada item grudado que não é alvo: zera `btm_stick.orig_parent` se aponta para um alvo; `stick.link.release(item)`; `save_feedback.show("Vínculo perdido: {item}")`); `plan = component.delete_plan(targets, keep_aggregates)`; se `keep_aggregates`, `convert.unconvert` em cada `own_aggregates(alvo)`; para cada vão do plano cujo pai é parede (`IS_WALL_BP`), remove os `BOOLEAN` com `object == vão`; apaga o `cutter` de cada objeto do plano que não está no plano; `bpy.data.batch_remove` dos objetos ainda vivos.

### F-16 `draw_aggregate(layout, context, include_import=True)` 🟢
1. `include_import` → botão `caffmob.import_model`. Coluna: Converter em agregado, Converter em folha de porta, Montar esquadria; linha Criar grupo + "Desfazer grupo".
2. `_draw_frame`: esquadria do ativo (`install.frame_of`) ou da jaula ativa (`btm_window.frame`) → caixa "Esquadria: {nome}" com Desinstalar (se instalada) ou Instalar na parede.
3. `_active_aggregate`: ativo (ou a folha do pivô), subindo pelos pais até o primeiro `is_aggregate`; nenhum → "Selecione a malha e, por último, o elemento pai."; sai.
4. Caixa "{objeto} — pai: {pai ou —}". `AGGREGATE`: `face`; `u`/`v` com "{mín} a {máx}" (de `limits.limits`, formatado por `units.format_value`); `offset` com "mín. {}"; Mover agregado; Perfurar; Furo real habilitado só com `perforate` e sem motivo (motivo exibido se `perforate`); Peça de produção e, marcada, `btm_geometry.component`/`material`.
5. `LEAF`: `motion` expandido; giro: `hinge`, `swing_sign`, `max_angle`; correr: `slide_dir`, `travel` e o aviso de pouco curso (alerta); `open_value` em barra; contato (alerta, "Folha encostou em {}" se `CLOSE`, senão "Folha bateu em {}"); sem pivô → "Pivô ausente; desconverta e converta de novo".
6. Botão Desconverter.

### F-17 Simulação gráfica (`overlay.py`) 🟢
1. `_draw_3d` (`POST_VIEW`): folha ativa e `context.region`; `Tester(obj)`; `base_world = parent_world @ base`; `far` = índice do canto fechado mais longe de `base_world`; caminho = esse canto em `corners_at(i/24)`, `i = 0..24`.
2. Eixo: giro → de `base_world` ao longo da coluna Z (`LEFT`/`RIGHT`) ou X (`TOP`/`BOTTOM`) da pose fechada no mundo, com o comprimento da folha nessa direção; correr → do primeiro ao último ponto do caminho.
3. Shader `POLYLINE_UNIFORM_COLOR` (`color`, `lineWidth`, `viewportSize`); `depth_test_set('NONE')`, `blend_set('ALPHA')`; caminho 2,0; eixo 3,0; caixa atual `HIT_COLOR` 3,0 com contato ou `LEAF_COLOR` 1,5; caixa da peça de contato (grupo: união das peças) `HIT_COLOR` 2,5; `blend_set('NONE')`.
4. `_draw_2d` (`POST_PIXEL`): com contato, projeta a origem da folha; texto com sombra preta (alpha 0,85) em `(x+11, y+9)` e vermelho em `(x+10, y+10)`, `blf.size(0, 14)` (sem `ui_scale`).

### F-18 `caffmob.group_dissolve` e `caffmob.group_create` 🟢
1. Dissolve: `target = _active_group`; `inner` = grupos em `target.children_recursive` (todos os níveis, inclusive grupos aninhados do SketchUp); para `inner + [target]` com `is_aggregate`: `unconvert`; depois `ungroup` de cada um (internos primeiro); INFO "Grupo {nome} desfeito: {n} peça(s)".
2. Create: `invoke` sugere o nome do único grupo de `grouping.suggest` (senão "Grupo") e abre o diálogo; `execute`: `create_group(_meshes, 'PLAIN', name or "Grupo")`; `None` → `CANCELLED`; seleciona e ativa o grupo; INFO "Grupo {nome} com {n} peça(s)".

## Fluxos Alternativos

- **Converter vários**: cada objeto recusado gera WARNING "{nome}: {motivo}" e os outros seguem; nenhum convertido → `CANCELLED`. O primeiro de `meshes` fica ativo mesmo que tenha sido o recusado (EC-13). 🟢
- **Folha com pai já folha**: `can_convert` recusa; uma **peça** dentro de um grupo-folha não é `LEAF` e pode ser pai. 🟢
- **Reconverter uma folha aberta**: `make_leaf` grava a pose atual como fechada (EC-08); pelo operador só com outro pai, porque o mesmo pai é recusado por `can_convert` _(Revisão 2026-10-10: convert.py:can_convert linha 126)_. 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-3):** `can_convert` passa a testar `parent in obj.children_recursive`. Pendência de implementação: DT-01.
- **Importação glTF/GLB**: já métrico e Y-up; com unidade explícita ≠ `AUTO` a escala é aplicada. 🟢
- **FBX com Empty raiz**: o Empty vira grupo `PLAIN` sem `members` (EC-10). 🟢
- **Sem janela (modo fundo)**: sem `keyconfigs.addon` não há keymap; handlers de depsgraph e desenho continuam registrados; os núcleos puros e `create_group`/`make_leaf` funcionam nos testes de fumaça. 🟢 (código) / 🟡 (efeito)

## Máquinas de Estado

### Objeto convertido 🟢

| Estado | Condição | Transição |
|---|---|---|
| Solto | `is_aggregate = False` | `aggregate_convert` → Agregado; `leaf_convert`, `window_assemble`, `openings.sync`, `scene_slides` → Folha |
| Agregado | `is_aggregate`, `kind = 'AGGREGATE'`, filho Blender de `parent_ref` | `perforate` → Agregado perfurado; `aggregate_unconvert`, X/Delete com "Apagar também" desligado, `group_dissolve` → Solto (matriz original); apagar o pai com a opção ligada → removido |
| Agregado perfurado | + `cutter` e `BOOLEAN` no pai | deixar de afundar/desligar → Agregado; desconverter → Solto |
| Folha | `kind = 'LEAF'`, filha do pivô, `btm_leaf_rest` | mudar `open_value` → Folha (abrindo/fechando por F-05); pivô apagado → Folha sem pivô; desconverter → Solto |
| Folha sem pivô | `kind = 'LEAF'` e `pivot_of` `None` | Nenhum movimento; painel pede "desconverta e converta de novo"; mudar `motion`/`hinge`/`slide_dir` refaz o pivô (`rebuild_pivot`) se `REST_KEY` existe |

### Contato da folha 🟢

| `contact_kind` | Entrada | Saída |
|---|---|---|
| `NONE` | Varredura sem contato e sem chegar ao fim do curso livre | Varredura com contato |
| `OPEN` | Abrindo, contato ou fim do curso livre | Nova varredura |
| `CLOSE` | Fechando numa esquadria, contato ou batente da irmã | Nova varredura |

### Esquadria importada 🟢

| Estado | Condição | Transição |
|---|---|---|
| Peças soltas/grupo `PLAIN` | Importação | `window_assemble` → Montada |
| Montada (solta) | Grupo `FRAME` com folhas `LEAF` | `window_install` → Instalada; `group_dissolve` → Peças soltas |
| Instalada | Filha de jaula `IS_WINDOW_BP` com drivers e corte | `window_uninstall` → Montada (sem pai); apagar a jaula/parede pelo X → removida |

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `hb_types.GeoNodeCage` (`create`, `set_input`, `var_input`), `GeoNodeWall.get_input('Length'/'Thickness')`, `GeoNodeObject.driver_location`, `GeoNodeCutpart.add_part_modifier` | Jaula, parede, drivers da esquadria, `CPM_CUTOUT` | 🟢 |
| `compat.try_get_gn_input`, `try_set_gn_input` | Inputs do `GeoNodeCutpart` e do `CPM_CUTOUT` (regra do repo: sem `mod["Socket_X"]`) | 🟢 |
| `cutting/machining.AGGREGATE_PREFIX` | `"Agregado: "`; a usinagem exporta o recorte | 🟢 |
| `inspection/fronts.module_root_of(obj)` | Sobe até a caixa de módulo (`IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_CLOSET_STARTER_CAGE`, `IS_ENTRY_DOOR_BP`) ou `btm_plane.object_kind == 'MODULE'` | 🟢 |
| `operators/doors_windows.cut_wall(wall, cutter)` | `BOOLEAN` "Boolean_`<cortador>`" `DIFFERENCE`/`EXACT`, cortador fora do render; reaproveita se já existe | 🟢 |
| `selection/component` | `own_aggregates`, `deletes_subtree`, `delete_plan` (contrato em `_reversa_sdd/selection/`) | 🟢 |
| `stick/apply.stuck_items`, `stick/link.release`, `btm_stick` (`is_stuck`, `orig_parent`) | Grudados soltos ao apagar; recusa de converter | 🟢 |
| `ui/save_feedback.show(texto)` | Aviso "Vínculo perdido" | 🟢 |
| `data/i18n` (`tr`, `N_`), `data/units.format_value(valor, scene)` | Textos e medidas do painel | 🟢 |
| `btm_geometry` (unit `geometry_free`): `fabrication`, `component`, `material` | Peça de produção | 🟢 |
| `openskp` (+ `defusedxml`, `mapbox_earcut`, `shapely`) | `SkpFile(path).parse()`, `.build_scene()` → `Scene` (`glb_primitives` com `geom_name`, `positions`, `indices`, `uvs`, `material_index`; `mesh_index[geom].path`; `gltf_materials`; `textures` com `filename`, `mime_type`, `data`; `scene_hierarchy` com `children`, `name`, `definition_name`, `path`, `position_mm`); `SkpModel.materials` (`name`, `color`, `texture.filename`) | 🟢 (uso) / 🟡 (API do OpenSKP fora do repo) |
| API Blender | `bpy.ops.wm.obj_import`, `import_scene.fbx/gltf`, `ImportHelper`, `BVHTree.FromPolygons/overlap`, `Object.evaluated_get/to_mesh`, `bmesh.ops.create_cube`, `depsgraph_update_post`, `SpaceView3D.draw_handler_add`, `gpu` (`POLYLINE_UNIFORM_COLOR`), `blf`, `bpy_extras.view3d_utils`, `mathutils.geometry.intersect_line_plane`, `bpy.data.batch_remove`, `Image.pack` | 🟢 |

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Agregado é filho Blender do pai (mover/girar/apagar o pai o leva) com pai e matriz originais guardados | `convert.py` docstring (003 RN-07, RN-12, D-12) | 🟢 |
| Posição sempre derivada de `u`/`v`/`offset` com limite puro testável e regravação do valor ajustado | `limits.py`, `apply.py` docstrings (RN-08, RN-09) | 🟢 |
| Recorte por caixa do volume afundado, não pela malha do agregado (pode ser pesada ou aberta) | `perforate.py` docstring (D-13, D-14) | 🟢 |
| Folha por pivô Empty, pose fechada guardada, abrir nunca altera a malha (mesmo padrão das portas de ambiente) | `leaf.py` docstring (D-17 a D-19) | 🟢 |
| Varredura pura com teste de contato injetado; contato por caixa encolhida + BVH | `sweep.py`, `collision.py` docstrings (RN-11a, D-19) | 🟢 |
| Na esquadria as peças dela contam; o batente entre folhas é a relação dos montantes do arquivo (folhas em trilhos distintos nunca se tocam) | `collision.py`, `slide_limits.py` docstrings (007 D-07, D-10) | 🟢 |
| Grupo de peças em vez de juntar malhas (nome, material e vidro separados) | `group_props.py` docstring (007 D-03) | 🟢 |
| Janela instalada reaproveita a jaula das janelas de ambiente (deslizar no plano, apagar com a parede, colisão da 004) | `install.py` docstring (007 D-12 a D-14) | 🟢 |
| Escala aplicada após a importação para a unidade automática poder medir em escala 1; escala passada para a malha | `ops_import.py` docstring (007 D-01, D-02) | 🟢 |
| SketchUp pelo OpenSKP em qualquer plataforma, em árvore pela hierarquia, materiais reaproveitados | `skp*.py` docstrings (009 D-15/D-16; 010 D-01 a D-03) | 🟢 |
| Arquivo importado vira um componente | `ops_import.py:_group_import` (011 D-09) | 🟢 |
| X/Delete apaga a subárvore inteira em lote | `ops_aggregate.py:delete_components` (011 D-05, D-06; 012) | 🟢 |

## Estado Interno

- 🟢 Global de módulo: `props._guard`; `apply._busy`, `apply._last_parent_box`; `collision._cache`; `overlay._handles`; `ops_aggregate._addon_keymaps`. Nenhum é limpo no `load_post` (só `collision._cache` no `unregister`).
- 🟢 Persistente (`.blend`): `Object.btm_aggregate`, `btm_group`, `btm_window`; idprops `btm_leaf_rest`, `btm_free_contact` (folha), `btm_leaf`, `btm_leaf_base`, `btm_open_fraction` (pivô), `IS_CUTTING_OBJ`, `btm_box` (cortador), `btm_skp_material`, `btm_skp_key` (materiais); modificadores `BOOLEAN`/`CPM_CUTOUT` no pai e drivers na esquadria; imagens empacotadas.
- 🟢 Escritas na cena: pais, matrizes, objetos e malhas novos (pivôs, cortadores, grupos, jaula, importados), remoções (pivô, cortador, grupo, jaula, componentes apagados), modificadores na parede e no pai, seleção e ativo.

## Observabilidade

- 🟢 Nenhum log próprio. Relatórios `INFO`/`WARNING`/`ERROR` dos operadores; aviso "Vínculo perdido" por `save_feedback`; texto de status no arraste; barra de progresso na leitura do SketchUp; avisos no painel (pouco curso, contato, pivô ausente, motivo do furo real); texto do contato na viewport.

## Riscos e Lacunas

- 🟢 Agregado `AGGREGATE` sobre pai Empty/grupo usa o `bound_box` do Empty (EC-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-28):** usar a união das malhas (`group.object_corners`). Pendência de implementação: DT-03.
- 🟢 Desconverter devolve a matriz da época da conversão (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-27):** manter a matriz de mundo corrente. Pendência de implementação: DT-02.
- 🟢 Contato exclui toda a subárvore de um pai que não é módulo (EC-07); obstáculo fino entre amostras é atravessado (EC-05); mudar sentido/ângulo com a folha aberta não testa contato (EC-06). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-29):** excluir só o pai e a folha (DT-04). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-30):** fechar e reabrir pela varredura ao mudar sentido/ângulo/curso (DT-05); passo da varredura mantido.
- 🟡 O encolhimento de 1 mm é ao longo da diagonal de cada canto: numa folha fina a folga real na espessura é de centésimos de milímetro (EC-04).
- 🟢 Renomear o agregado depois de perfurar perde o vínculo pelo nome com o modificador e o cutout (EC-09); o `CPM_CUTOUT` antigo continua no pai e na usinagem _(Revisão 2026-10-10: 🟡→🟢; perforate.py:_remove_cutout)_.
- 🟢 Os `_guard`/`_last_parent_box`/`_cache` usam nomes de objeto como chave; renomear ou abrir outro arquivo com nomes iguais reaproveita entradas antigas _(Revisão 2026-10-10: 🟡→🟢; props.py:_guarded usa `(obj.name, prop)`, apply.py:on_depsgraph_update usa `original.name`, collision.py:_targets usa `obj.name`; nenhum é limpo no `load_post`)_.

## Divergências entre artefatos e código

- 🟢 `data-dictionary.md` §9.1 descreve `parent_ref` como "igual ao pai Blender": vale para `AGGREGATE`; numa `LEAF` o pai Blender é o pivô e `parent_ref` é o pai lógico.
- 🟢 `data-dictionary.md` §9.2 e `group_props.py` dizem que `members[].orig_matrix` serve para "desfazer o grupo sem perda"; `group.ungroup` usa a posição **atual** e nunca lê `orig_matrix`.
- 🟢 `window_props.py` docstring diz que `frame_matrix` existe "para Desinstalar devolver a janela solta no mesmo lugar"; `install.uninstall` nunca o lê e solta a esquadria na posição atual, sem o pai anterior (EC-14). `code-analysis.md` §10.7 descreve o comportamento real. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-79):** o comportamento atual fica; corrigir a docstring. Pendência de implementação: DT-07.
- 🟢 A descrição de `with_aggregates` ("os agregados ficam soltos na mesma posição") contradiz `unconvert`, que devolve a matriz da conversão (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-27):** vale a descrição; pendência DT-02.
- 🟢 `_reversa_forward/003…/requirements.md` (NFR de desempenho) pede que Perfurar não recalcule durante o arraste; `aggregate_move` atribui `u` e `v` a cada movimento e cada atribuição chama `perforate.sync` (EC-11). Decisão: medir (DT-06; questions.md#pergunta-80).
- 🟢 `domain.md` RN-AGGREGATES-07 e `code-analysis.md` §10.4 dizem "caixa encolhida 1 mm"; o código move cada canto 1 mm na direção do centro (diagonal), não 1 mm por eixo (EC-04).
- 🟢 `erd-complete.md` dá à entidade `AGGREGATE` os campos `uid`, `owner`, `kind`, `scope`, e `domain.md` (glossário) fala em "escopo"; `BTM_PG_Aggregate` não tem `uid`, `owner` nem `scope`.
- 🟢 `state-machines.md` não descreve a unit; as máquinas de estado acima são novas. `permissions.md` só a cita genericamente.
- 🟢 `code-analysis.md` §10.1 já registra `_last_parent_box` declarado duas vezes; `data-dictionary.md` §9 e `domain.md` RN-AGGREGATES-01 a 17 estão alinhados com o código nos demais pontos verificados.
