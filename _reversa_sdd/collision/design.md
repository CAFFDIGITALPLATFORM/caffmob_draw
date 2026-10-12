# Colisão de Corpo (collision) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/collision/` (9 arquivos, 986 linhas) em 2026-10-10, sem alterações sem commit na pasta. IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`; fluxos F-xx abaixo. 🟡 marca inferência; 🔴 lacuna. Contratos citados, não redescritos: `selection/classify` (`classify`, `movable_root`, `reference_root`, tipos `MODULE`, `GEOMETRY`, `ROOM_DOOR`, `WINDOW`, `WALL`, `OBSTACLE`, `FLOOR`, `CEILING`, `OTHER`) em `_reversa_sdd/selection/`; `stick/apply` (`local_box`, `linked`, `face_of`, `project`) e `stick/ops_stick.item_of` no código (`caffmob_draw/stick/`, sem spec própria); `ui/save_feedback.show` e a barra lateral única (`group_scope`, `sidebar_proxy`) em `_reversa_sdd/ui/`.

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `obb.py` (86), `rules.py` (130) | não (`math`, `dataclasses`) | Caixa orientada, SAT; itens, pares, exclusões, classificação, ordem | 🟢 |
| Estado | `props.py` (52) | sim | `WindowManager.btm_collision` (sessão) | 🟢 |
| Aplicação | `scan.py` (273), `stale.py` (66) | sim (`mathutils.Vector`, `mathutils.bvhtree.BVHTree`) | Cena → itens, confirmação BVH, gravação; marcador desatualizado | 🟢 |
| Interface | `ops_collision.py` (143), `overlay.py` (94), `panels.py` (118) | sim (`gpu`, `blf`, `gpu_extras`, `bpy_extras.view3d_utils`) | Operadores, destaque, funções de painel | 🟢 |
| Pacote | `__init__.py` (24) | não | `_modules()` importa tarde `ops_collision, overlay, panels, props, stale` e devolve `(props, stale, ops_collision, overlay, panels)`; `register` nessa ordem, `unregister` na inversa. Chamado por `caffmob_draw/__init__.py` (`collision.register()`/`unregister()`; `"collision"` está na lista de submódulos recarregáveis) | 🟢 |

## Interface

### `obb.py` 🟢 (puro)

| Símbolo | Assinatura / valor | Comportamento |
|---|---|---|
| `_EPS` | `1e-9` | Empate/folga numérica do SAT |
| `_dot`, `_cross`, `_sub` | tuplas de 3 | Álgebra vetorial em tuplas |
| `OBB` | `@dataclass(frozen=True)`: `center: tuple`, `axes: tuple` (3 vetores unitários), `half: tuple` (meias medidas) | — |
| `OBB.corners()` | → lista de 8 tuplas | Laços `sx`, `sy`, `sz` ∈ (−1, +1) aninhados nessa ordem: índice = `4·[sx>0] + 2·[sy>0] + [sz>0]`; canto = `center + Σ axes[i]·half[i]·s[i]`. Ordem assumida por `overlay._EDGES` e pelas faces de `scan._Meshes._build` |
| `OBB.aabb()` | → `(lo, hi)` | `ext_k = Σ_i |axes[i][k]|·half[i]`; `center ∓ ext` |
| `from_box(origin, axes, lo, hi)` | → `OBB` | `mid = (lo+hi)/2`; `center = origin + Σ axes[i]·mid[i]`; `axes` copiados como tuplas; `half = |hi−lo|/2` (aceita `lo > hi`) |
| `_radius(box, axis)` | → `float` | `Σ half[i]·|axes[i]·axis|` |
| `overlap(a, b)` | → `None` ou `{'depth', 'push', 'axis'}` | F-04 |
| `aabb_overlap(a, b, margin=0.0)` | `a`, `b` = `(lo, hi)` → `bool` | `∀i: alo[i] − margin ≤ bhi[i] e blo[i] − margin ≤ ahi[i]` |

### `rules.py` 🟢 (puro)

| Símbolo | Valor / assinatura | Comportamento |
|---|---|---|
| `TOLERANCE` | `0.001` (m) | Mesma de `inspection/interference.py` |
| `ITEM`, `WALL`, `OBSTACLE`, `FLOOR`, `CEILING` | strings homônimas | Tipos de item |
| `STATIC` | `{WALL, OBSTACLE, FLOOR, CEILING}` | — |
| `KIND_WALL`, `KIND_ITEM`, `KIND_FLOOR_CEILING` | `'WALL'`, `'ITEM'`, `'FLOOR_CEILING'` | Tipos de ocorrência (mesmas chaves de `props.KIND_ITEMS`) |
| `_ORDER` | `{WALL: 0, ITEM: 1, FLOOR_CEILING: 2}` | RN-06 |
| `Item` | `@dataclass`: `name: str`, `box: OBB`, `kind=ITEM`, `root=''`, `linked=frozenset()`, `override='INHERIT'` | Propriedades `static` (`kind in STATIC`) e `group` (`root or name`) |
| `Conflict` | `@dataclass(frozen=True)`: `kind`, `name_a`, `name_b`, `depth`, `push` (tupla, deslocamento de A), `location` (tupla) | — |
| `excluded(a, b)` | → `bool` | RN-02 |
| `conflict_kind(a, b)` | → tipo | RN-04: `{a.kind, b.kind} & {WALL, OBSTACLE}` → `KIND_WALL`; `& {FLOOR, CEILING}` → `KIND_FLOOR_CEILING`; senão `KIND_ITEM` |
| `candidate_pairs(items, only=None)` | → `[(a, b)]` | F-03 passo 1 |
| `evaluate(a, b)` | → `Conflict` ou `None` | F-03 passo 2 |
| `sort_key(conflict)` | → `(_ORDER[kind], −round(depth, 6), name_a, name_b)` | — |
| `conflicts(items, confirm=None, only=None)` | → `list[Conflict]` ordenada | `candidate_pairs` → `evaluate` → `confirm(a, b)` (chamado **depois** de `evaluate`, só se não `None`) → `sort(key=sort_key)` |

### `props.py` 🟢

| Símbolo | Definição |
|---|---|
| `KIND_ITEMS` | `[('WALL', "Penetração em parede", "Item entra numa parede ou obstáculo"), ('ITEM', "Colisão entre itens", "Dois itens ocupam o mesmo espaço"), ('FLOOR_CEILING', "Piso ou teto", "Item entra no piso ou no teto")]` |
| `BTM_PG_Collision` (linha) | `kind: EnumProperty(name="Tipo", items=KIND_ITEMS, default='ITEM')`; `name_a: StringProperty(name="Item")`; `name_b: StringProperty(name="Outro")`; `depth: FloatProperty(name="Profundidade", subtype='DISTANCE', unit='LENGTH')`; `push: FloatVectorProperty(name="Afastar", size=3, subtype='TRANSLATION')`; `location: FloatVectorProperty(name="Ponto", size=3, subtype='TRANSLATION')` |
| `BTM_PG_CollisionState` | `items: CollectionProperty(type=BTM_PG_Collision)`; `index: IntProperty(default=0)`; `checked: IntProperty(name="Itens verificados", description="Itens verificados na última checagem (-1 = nunca)", default=-1)`; `scope: EnumProperty(name="Escopo", items=[('ALL', "Cena", "Todos os itens da cena"), ('SELECTED', "Selecionado", "Só o item selecionado e o que ele toca")], default='ALL')`; `stale: BoolProperty(name="Desatualizado", default=False)`; `error: StringProperty(name="Erro")`; `checked_names: StringProperty()` (nomes separados por `"\n"`) |
| `register()` | Registra as duas classes; `bpy.types.WindowManager.btm_collision = PointerProperty(type=BTM_PG_CollisionState)` |
| `unregister()` | `del WindowManager.btm_collision` se existir; desregistra as classes registradas em ordem inversa |

Todas as anotações levam `# type: ignore` (convenção do repo). 🟢

### `scan.py` 🟢

| Símbolo | Assinatura / valor | Comportamento |
|---|---|---|
| `_SKIP_TAGS` | `('IS_CUTTING_OBJ', 'IS_2D_ANNOTATION', 'IS_DIMENSION', 'obj_x')` | RN-08 |
| `_FINE_KINDS` | `{rules.WALL, rules.OBSTACLE}` | Força confirmação pela malha |
| `_Entry` | `__slots__ = ('item', 'obj', 'fine')` | Item puro + objeto + flag fino |
| `_skip(obj)` | → `bool` | `any(obj.get(tag))`; senão `obj.hide_viewport or not obj.visible_get()`; `RuntimeError` → `True` |
| `box_of(obj, depsgraph)` | → `OBB` | `lo, hi = stick_apply.local_box(obj, depsgraph)`; `loc, rot, scale = obj.matrix_world.decompose()`; `axes = colunas de rot.to_matrix()`; `lo`/`hi` multiplicados por `scale` eixo a eixo e reordenados (min/max) → `obb.from_box(loc, axes, lo, hi)`. Import tardio de `..stick.apply` |
| `_override(obj)` | → `'INHERIT'`/`'ON'`/`'OFF'` | `obj.btm_plane.collision_override`; sem `btm_plane` → `'INHERIT'` |
| `_root_name(obj)` | → `str` | `''` para `None`; `(classify.movable_root(obj) or classify.reference_root(obj))`, nome dele ou `obj.name` |
| `_links(obj)` | → `frozenset[str]` | RN-03 |
| `_kind_of(obj)` | → `(tipo, raiz, fino)` ou `None` | F-02 |
| `collect(scene, depsgraph)` | → `list[_Entry]` | Para `obj in scene.objects`: pula `_skip`; `_kind_of`; `Item(obj.name, box_of(obj, depsgraph), kind, root, _links(obj), _override(obj))`; `fine = fine or kind in _FINE_KINDS` |
| `_Meshes(depsgraph)` | `.tree(entry)` → `BVHTree` | Cache `{obj.as_pointer(): BVHTree}`; `_build`: F-05. A docstring diz "mesmo cálculo de `inspection/interference._Targets`", mas é uma cópia, não reaproveitamento: `_Targets` aceita também `CURVE`, filtra `display_type` e guarda AABB por objeto; e só o resultado desta unit fica desatualizado ao editar (inspection EC-09/EC-10) _(Revisão cruzada 2026-10-10: scan.py:131-163 × interference.py:117-150)_ |
| `_confirm(by_name, meshes)` | → `confirm(a, b)` | Nenhum fino → `True`; senão `bool(ta.overlap(tb))` (árvore `None` → `True`) |
| `enabled(scene)` | → `bool` | `settings = getattr(scene, 'btm_settings', None)`; `settings is None or settings.collision_global` |
| `find(context, only=None)` | → `(list[Conflict], list[_Entry])` | `depsgraph = context.evaluated_depsgraph_get()`; `collect`; `by_name`; `rules.conflicts(items, confirm=_confirm(by_name, _Meshes(depsgraph)), only=only)` |
| `_store(state, found, names, scope)` | — | F-06 |
| `selected_names(context)` | → `set[str]` | `{(classify.movable_root(o) or o).name for o in context.selected_objects}` |
| `check_all(context, scope='ALL')` | → `list[Conflict]` ou `None` | F-01 |
| `check_moved(objs)` | → `list[Conflict]` | F-07; usa `bpy.context` |
| `_redraw(context)` | — | `tag_redraw` em toda área `VIEW_3D` ou `PROPERTIES` de cada janela; `AttributeError` ignorado |

### `stale.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `_changed` | `set` de módulo: nomes vigiados que mudaram desde a última gravação |
| `reset()` | `_changed.clear()` |
| `rechecked(names)` | `_changed −= names`; se `state.checked ≥ 0`: `state.stale = bool(_changed)` |
| `_checked_root(obj, names)` | Sobe `obj`, `obj.parent`, … e devolve o primeiro nome em `names`, ou `None` |
| `on_depsgraph_update(scene, depsgraph)` | `@persistent`; F-08 |
| `register()` / `unregister()` | Acrescenta/remove de `bpy.app.handlers.depsgraph_update_post` (sem duplicar); `unregister` chama `reset()` |

### `ops_collision.py` 🟢

| `bl_idname` / classe | `bl_label` | `bl_options` | Propriedades | Comportamento |
|---|---|---|---|---|
| `caffmob.check_collisions` / `BTM_OT_CheckCollisions` | "Verificar colisões" | `{'REGISTER'}` | `scope: EnumProperty(name="Escopo", items=ALL "Cena" / SELECTED "Selecionado", default='ALL')` | F-01 (casca do operador) |
| `caffmob.collision_goto` / `BTM_OT_CollisionGoto` | "Ir para a colisão" | `{'REGISTER'}` | `index: IntProperty()` | F-10 |
| `caffmob.collision_clear` / `BTM_OT_CollisionClear` | "Limpar colisões" | `{'REGISTER'}` | — | F-11 |
| `caffmob.collision_push_out` / `BTM_OT_CollisionPushOut` | "Afastar até encostar" | `{'REGISTER', 'UNDO'}` | `index: IntProperty()` | F-09 |

Nenhum operador tem `invoke`, `poll` ou modal; nenhum atalho de teclado é registrado pela unit. `register` registra as 4 classes; `unregister` desregistra as registradas em ordem inversa. Docstrings (tooltips): "Procura itens que ocupam o mesmo espaço e itens que entram em parede, piso ou teto (encostar não conta)"; "Seleciona os dois itens da colisão e enquadra a vista neles"; "Limpa a lista de colisões e o destaque na viewport"; "Afasta o item pelo menor caminho até ele só encostar no outro (item grudado anda só no plano da face)". 🟢

### `overlay.py` 🟢

| Símbolo | Valor | Comportamento |
|---|---|---|
| `COLOR` | `(1.0, 0.25, 0.2, 1.0)` | Em dia |
| `STALE_COLOR` | `(1.0, 0.65, 0.2, 0.8)` | Desatualizado |
| `_EDGES` | `((0,1),(1,3),(3,2),(2,0),(4,5),(5,7),(7,6),(6,4),(0,4),(1,5),(2,6),(3,7))` | 12 arestas sobre `OBB.corners()` |
| `MAX_ROWS` | `30` | Linhas consideradas |
| `_handles` | lista | Dois handles |
| `_LABELS` | `{chave: rótulo}` de `props.KIND_ITEMS` | — |
| `_rows(context)` | → `(state, linhas[:30])` ou `(None, ())` sem estado/linhas | — |
| `_draw_3d()` | `POST_VIEW` | F-12 |
| `_draw_2d()` | `POST_PIXEL` | F-12 |
| `register()` | Só se `_handles` vazio: `SpaceView3D.draw_handler_add(_draw_3d, (), 'WINDOW', 'POST_VIEW')` e `(_draw_2d, (), 'WINDOW', 'POST_PIXEL')` |
| `unregister()` | `draw_handler_remove(handle, 'WINDOW')` até esvaziar |

### `panels.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `MAX_ROWS = 12`, `_LABELS` | — |
| `draw_collisions(layout, context)` | F-13 |
| `BTM_PT_Collisions` | `bl_label "Colisões"`, `bl_idname "BTM_PT_collisions"`, `VIEW_3D`/`UI`, `bl_category "CAFFMob Draw"`, `DEFAULT_CLOSED`; `draw` → `draw_collisions` |
| `_item(context)` | `stick.ops_stick.item_of(context.active_object)` ou `None` (import tardio) |
| `BTM_PT_ItemCollision` | `bl_label "Colisão"`, `bl_idname "BTM_PT_item_collision"`, `bl_parent_id "BTM_PT_object_properties"`, `DEFAULT_CLOSED`; `poll`: `_item` não `None` e `getattr(item, 'btm_plane', None)` não `None`; `draw`: `prop(item.btm_plane, "collision_override", text=tr("Colisão"))` e até 5 linhas `alert` "Colide com <outro>" (`ERROR`) das ocorrências que citam `item.name` |
| `classes = ()` | Nenhum painel é registrado (barra lateral única da 005): `ui/sidebar_check.draw` chama `draw_collisions` no grupo `check_collisions` ("Colisões", `MOD_PHYSICS`); `ui/object_properties._folded_groups` desenha `BTM_PT_ItemCollision` via `sidebar_proxy` no grupo `sel_collision` ("Colisão") quando `sidebar_proxy.visible(...)` |

## Fluxos

### F-01 Verificar colisões 🟢

`BTM_OT_CheckCollisions.execute`:
1. `not scan.enabled(scene)` → `WARNING` "Colisão desligada (Evitar Sobreposição)", `CANCELLED`.
2. `scope == 'SELECTED'` e sem `selected_objects` → `WARNING` "Selecione um item", `CANCELLED`.
3. `found = scan.check_all(context, scope)`:
   1. `only = selected_names(context)` se `SELECTED`, senão `None`.
   2. `find(context, only)`; **qualquer** `Exception` → `state.items.clear()`, `state.error = str(exc) or nome da classe`, `state.stale = False`, devolve `None` (não chama `_redraw`, não mexe em `checked`/`checked_names`/`scope`).
   3. `names = only` (se `SELECTED`) ou `{nomes de todas as entradas}` (inclui estáticos).
   4. `_store(state, found, names, scope)`; `_redraw(context)`; devolve `found`.
4. `None` → `ERROR` "Não foi possível calcular a colisão: {state.error}", `CANCELLED`.
5. `found` não vazio → `WARNING` "{len} colisão(ões) em {state.checked} item(ns)"; vazio → `INFO` "Sem colisões em {checked} item(ns)"; `FINISHED`.

### F-02 `_kind_of(obj)` 🟢 (ordem importa)

1. `obj.get('btm_wall_segments')` e `obj.type == 'MESH'` → `(WALL, obj.name, True)`.
2. `btm_aggregate.is_aggregate` → `(ITEM, '', True)` (raiz vazia: o grupo é o próprio nome).
3. `obj.get('IS_APPLIANCE')` → `(ITEM, obj.name, False)`.
4. `info = classify.classify(obj)`; `None` ou `info.obj is not obj` → `None` (peças, frentes e filhos de raízes não entram).
5. `MODULE` ou `GEOMETRY` → `(ITEM, obj.name, False)`; `ROOM_DOOR`/`WINDOW` → `(ITEM, obj.name, True)`; `WALL` → `(WALL, …, True)`; `OBSTACLE` → `(OBSTACLE, …, True)`; `FLOOR` → `(FLOOR, …, False)`; `CEILING` → `(CEILING, …, False)`.
6. `OTHER` e `MESH` e `parent is None` e `display_type not in {'WIRE', 'BOUNDS'}` → `(ITEM, obj.name, True)`.
7. Senão `None` (`ANNOTATION`, `FRONT`, `PART`, Empties `OTHER`, malhas `OTHER` com pai).

### F-03 `rules.conflicts` 🟢

1. `candidate_pairs`: lista `(item, aabb)`; ordena por `(aabb.lo.x, name)`; para cada `i`, percorre `j > i`: se `x_min(B) > x_max(A) + TOLERANCE` → `break`; se `only` e nenhum dos nomes em `only` → `continue`; se `excluded(a, b)` ou `not aabb_overlap(box_a, box_b, TOLERANCE)` → `continue`; senão guarda `(a, b)` (A = o de menor `x_min`).
2. `evaluate(a, b)`: `r = obb.overlap(a.box, b.box)`; `None` ou `r['depth'] ≤ TOLERANCE` → `None`. `first, second, push = a, b, r['push']`; troca (e nega `push`) se `first.static and not second.static` **ou** `first.static == second.static and second.name < first.name`. `location` = média dos **centros** das duas OBBs. `Conflict(conflict_kind(a, b), first.name, second.name, depth, push, location)`.
3. `confirm(a, b)` (se dado) falso → descarta.
4. `found.sort(key=sort_key)`.

### F-04 `obb.overlap(a, b)` 🟢

1. `t = b.center − a.center`; eixos = 3 de A, 3 de B, 9 produtos `a.axes[i] × b.axes[j]` (i externo, j interno), índices 0–14.
2. Para cada eixo: comprimento < `1e-6` → pula; normaliza; `dist = t·eixo`; `amount = _radius(a) + _radius(b) − |dist|`.
3. `amount < −_EPS` → devolve `None` imediatamente (eixo separador).
4. Se `best is None` ou `amount < best.amount − _EPS`: `sign = −1.0 se dist > 0 senão +1.0`; `best = (max(0, amount), eixo·sign·max(0, amount), índice)` (empates ficam com o eixo de menor índice).
5. Fim: `best is None` → `None`; senão `{'depth', 'push', 'axis'}`. `push` afasta A de B; com `dist == 0` aponta para `+eixo`.

### F-05 BVH de confirmação 🟢

`_Meshes._build(entry)`: se `MESH`: `evaluated = obj.evaluated_get(depsgraph)`; `to_mesh()` (`RuntimeError` → sem malha); vértices `evaluated.matrix_world @ v.co`, polígonos `tuple(p.vertices)`; `to_mesh_clear()` em `finally`; com vértices e polígonos → `BVHTree.FromPolygons(verts, polys)`. Senão (não malha, sem polígonos) → `FromPolygons` dos 8 cantos da OBB com faces `((0,1,3,2), (4,6,7,5), (0,4,5,1), (2,3,7,6), (0,2,6,4), (1,5,7,3))`. `BVHTree.overlap` devolve pares de polígonos que se cruzam (`docs/rag/blender-api/corpus/mathutils.bvhtree.md#mathutils.bvhtree.BVHTree.overlap`); 🟡 contenção sem cruzamento de superfícies não é detectada (EC-01).

### F-06 `_store(state, found, names, scope)` 🟢

`items.clear()`; uma linha por `Conflict` (`kind`, `name_a`, `name_b`, `depth`, `push`, `location`); `index = 0`; `checked = len(names)`; `checked_names = "\n".join(sorted(names))`; `scope`; `stale = False`; `error = ""`; `stale.reset()`.

### F-07 `check_moved(objs)` 🟢

1. `context = bpy.context`; `not enabled(scene)` → `[]`.
2. `names = {o.name for o in objs if o.name in bpy.data.objects}`; vazio → `[]`; acrescenta `c.name for c in obj.children_recursive` de cada `obj`.
3. `find(context, names)`; exceção → `[]` (silencioso; não toca o estado).
4. `keep` = linhas atuais que não citam nenhum nome de `names` (copiadas como tuplas); `items.clear()`; regrava `keep` na ordem original e **acrescenta** as novas ocorrências na ordem RN-06 (sem reordenar o conjunto).
5. `stale.rechecked(names)`.
6. Para cada ocorrência: `moved, other = (a, b) se a ∈ names senão (b, a)`; `save_feedback.show(tr("{} colide com {}").format(moved, other))`.
7. `_redraw(context)`; devolve as novas ocorrências. Não altera `checked`, `checked_names`, `scope`, `error`, `index`.

Chamadores: `stick/settle.run` (fim do assentar, com `moved_roots`: itens grudados reprojetados e raízes `MODULE`/`GEOMETRY` que não voltaram ao repouso; import em `try/except ImportError`) e `BTM_OT_CollisionPushOut`.

### F-08 Desatualizado 🟢

`on_depsgraph_update`: lê `bpy.context.window_manager.btm_collision` (`AttributeError` → sai); `checked < 0` → sai; `names = checked_names.split("\n")` ∪ `name_a`/`name_b` das linhas; para cada `update` com `is_updated_geometry or is_updated_transform` e `id` `Object`: `root = _checked_root(update.id.original, names)` → `_changed.add(root)`; ao fim, `_changed` não vazio e `not stale` → `stale = True`. O handler nunca desliga `stale` (só `_store`, `rechecked` e o operador Limpar).

### F-09 Afastar até encostar 🟢

1. `index` fora de `items` → `CANCELLED` (sem mensagem); `obj = bpy.data.objects.get(row.name_a)` `None` → `CANCELLED`.
2. `push = Vector(row.push)` (valor gravado na verificação).
3. Se `stick_apply.linked(obj)`: `fr, _ = stick_apply.face_of(obj)`; `normal = (obj.btm_stick.host.matrix_world.to_3x3() @ Vector(fr[3])).normalized()`; `push −= normal·(push·normal)`; `push.length < 1e-6` → `WARNING` "O item grudado não pode sair da face; mova o outro item", `CANCELLED`.
4. `obj.matrix_world.translation += push`; `context.view_layer.update()`; se ainda `linked` → `stick_apply.project(obj)`.
5. `scan.check_moved([obj])`; `INFO` "{nome} afastado {push.length·1000:.1f} mm"; `FINISHED` (um passo de desfazer por `UNDO`).

### F-10 Ir para 🟢

`index` inválido → `CANCELLED`; `state.index = index`; objetos `name_a`, `name_b` existentes e `visible_get()`; nenhum → `WARNING` "Os itens da colisão não estão visíveis", `CANCELLED`. Desseleciona `selected_objects`, seleciona os encontrados, ativa o primeiro; para cada área `VIEW_3D` de `context.window.screen` com região `WINDOW`: `context.temp_override(window, area, region)` + `bpy.ops.view3d.view_selected()`. `FINISHED`.

### F-11 Limpar 🟢

`items.clear()`; `checked = −1`; `checked_names = ""`; `stale = False`; `error = ""`; `scan._redraw(context)`; `FINISHED`. Não chama `stale.reset()` (o conjunto `_changed` fica até a próxima gravação).

### F-12 Destaque 🟢

- `_draw_3d`: sem linhas ou sem `context.region` → retorna; `depsgraph = context.evaluated_depsgraph_get()`; para cada linha e cada nome (sem repetir, existente e visível): `scan.box_of(obj, depsgraph).corners()` → 24 pontos por `_EDGES`; shader `POLYLINE_UNIFORM_COLOR`; `depth_test_set('NONE')`, `blend_set('ALPHA')`; `batch_for_shader(shader, 'LINES', {"pos": coords})`; uniformes `color` (`STALE_COLOR` se `stale`, senão `COLOR`), `lineWidth` 2.5, `viewportSize (region.width, region.height)`; desenha; `blend_set('NONE')`.
- `_draw_2d`: sem linhas, `region` ou `region_data` → retorna; `blf.size(0, 13)`; por linha: `co = location_3d_to_region_2d(region, rv3d, row.location)` (`None` → pula); texto `"{tr(rótulo)}: {name_a} × {name_b}"` (+ `tr("{} (desatualizado)")` se `stale`); sombra preta `(0,0,0,0.85)` em `(x+11, y+9)`; texto na cor do estado em `(x+10, y+10)`.

### F-13 Painel 🟢 (ordem de decisão)

1. Linha alinhada: "Verificar colisões" (`MOD_PHYSICS`, `scope='ALL'`), "Selecionado" (`RESTRICT_SELECT_OFF`, `scope='SELECTED'`) e, se `items` ou `checked ≥ 0`, botão `X` (`caffmob.collision_clear`).
2. `not enabled` → "Colisão desligada (Evitar Sobreposição)" (`INFO`) + "Ligue em Produção/Projeto › Configurações"; fim.
3. `error` → caixa `alert` "Não foi possível calcular a colisão: {error}" (`ERROR`); fim.
4. `checked < 0` e sem linhas → "Ainda não verificado." (`INFO`); fim.
5. `stale` → caixa `alert` "Desatualizado, verifique de novo" (`ERROR`).
6. Sem linhas → se não `stale`, "Sem colisões em {checked} item(ns)." (`CHECKMARK`); fim.
7. Coluna `alert = not stale`: "{n} colisão(ões):" (`ERROR`); até 12 linhas "{tr(rótulo)}: A × B ({depth·1000:.0f} mm)" com `VIEWZOOM` (`collision_goto`, `index`) e `MOD_OFFSET` (`collision_push_out`, `index`); excedente → "… e mais {n − 12}".

## Máquina de Estados do Resultado 🟢

| Estado | Condição (`btm_collision`) | Entradas |
|---|---|---|
| Nunca verificado | `checked < 0`, `items` vazio, `error == ""` | Início da sessão; Limpar |
| Avulso (sem verificação) | `checked < 0`, `items` não vazio | `check_moved` antes de qualquer verificação (EC-04) |
| Erro | `error != ""` | `check_all` com exceção (sai por nova verificação bem-sucedida ou Limpar) |
| Em dia | `checked ≥ 0`, `stale` falso, `error == ""` | `_store`; `rechecked` com `_changed` vazio |
| Desatualizado | `checked ≥ 0`, `stale` verdadeiro | Handler F-08; `rechecked` com `_changed` não vazio |

## Dependências

- 🟢 `selection/classify`: `classify`, `movable_root`, `reference_root` e as constantes de tipo (`scan.py`).
- 🟢 `stick/apply`: `local_box(obj, depsgraph)` (caixa local avaliada, com filhos quando sem geometria), `linked`, `face_of` (devolve `(frame, extent)`; `frame = (o, u, v, n)`, normal no espaço do hospedeiro), `project`; `stick/ops_stick.item_of` (painel do item).
- 🟢 `ui/save_feedback.show(text)` (barra de status por alguns segundos + console).
- 🟢 `data/i18n.tr`; chaves em `data/translations/editor_grudar.json` (todas as strings da unit; "Ainda não verificado." também em `geral.json`, "Ligue em Produção/Projeto › Configurações" em `sidebar.json`, "… e mais {}" em `operators.json`/`walls2d.json`).
- 🟢 `data/properties`: `Object.btm_plane.collision_override` (linha 240), `Scene.btm_settings.collision_global` (linha 740; também lida por `hb_placement.avoid_overlap` e `move_over/ops_dialog._confirm`).
- 🟢 Blender: `mathutils.bvhtree.BVHTree.FromPolygons/overlap`, `Object.evaluated_get/to_mesh/to_mesh_clear`, `Matrix.decompose`, `gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')`, `blf`, `bpy_extras.view3d_utils.location_3d_to_region_2d`, `bpy.ops.view3d.view_selected`, `Context.temp_override`.

### Consumidores 🟢

| Consumidor | Uso |
|---|---|
| `caffmob_draw/__init__.py` | `collision.register()`/`unregister()` |
| `stick/settle.py:_check_collisions` | `scan.check_moved(moved_roots)` |
| `ui/sidebar_check.py:draw` | `panels.draw_collisions` |
| `ui/object_properties.py:_folded_groups` | `panels.BTM_PT_ItemCollision` via `sidebar_proxy` |
| `ui/save_feedback.py:_collision_note` | Lê `checked`, `stale`, `items` no `save_post` |
| `ui/sidebar_vocab.py` | `CHECK_ITEM` → `caffmob.check_collisions` |
| `cabinet_editor/validate.py` | `obb.from_box` (eixos identidade) e `obb.overlap` para GEO-002 |

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| OBB + SAT de 15 eixos no núcleo puro; malha só para confirmar pares finos | `obb.py`; `scan.py:_confirm`; 004 D-12/D-13 | 🟢 |
| Item móvel em `name_a` e `push` já orientado para ele, para "Afastar" não precisar decidir | `rules.py:evaluate`; 004 D-19 | 🟢 |
| Estado só de sessão em `WindowManager` (como `inspection/props.py`) | `props.py` docstring; 004 D-14 | 🟢 |
| Desatualizado por handler de depsgraph sobre nomes, no padrão `cutting/stale.py` | `stale.py` docstring; 004 D-15 | 🟢 |
| Aviso ao soltar acoplado ao assentar do grudar (cobre G nativo e modais listados em `settle._MOVE_IDS`) em vez de um gancho por operador | `stick/settle.py` docstring; diverge de 004 D-16 | 🟢 (código) / 🟡 (motivo) |
| Handlers de desenho permanentes que retornam cedo (padrão `aggregates/overlay.py`) | `overlay.py` docstring; diverge de 004 D-17 | 🟢 |
| Painéis não registrados, desenhados pela barra lateral única (005) | `panels.py:classes = ()` | 🟢 |

## Observabilidade

- 🟢 `self.report` nos operadores (F-01, F-09, F-10); `save_feedback.show` imprime "CAFFMob Draw: <texto>" no console e na barra de status (F-07).
- 🟢 Sem logs de exceção: `check_all` só guarda `str(exc)`; `check_moved` engole a exceção.

## Riscos e Lacunas

- 🟢 Contenção total dentro de objeto fino não detectada pela BVH (EC-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-33):** ray-cast de paridade do centro do item. Pendência de implementação: DT-03.
- 🟢 Objetos novos/apagados/renomeados depois da verificação não afetam `stale` (EC-03, EC-07). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-34):** passam a afetar. Pendência de implementação: DT-04.
- 🟡 `on_depsgraph_update` e `check_moved` usam `bpy.context` global; correto no thread principal, frágil fora dele.
- 🟢 `overlay._draw_3d` recalcula `box_of` (e `local_box`) por objeto a cada redesenho _(Revisão 2026-10-10: 🟡→🟢 no mecanismo; overlay.py:48)_; 🟡 custo não medido.
- 🟡 Push de eixo cruzado (índice ≥ 6) em caixas giradas move na diagonal (EC-13).
