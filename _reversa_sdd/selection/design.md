# Seleção, Componente e Dimensões (selection) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/selection/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`; EC-xx os de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Contratos de outras units são citados, não redescritos: cotas em `_reversa_sdd/measure/` (consome `classify`), "Mover Sobre" em `_reversa_sdd/move_over/` (consome `movable_root`/`reference_root`), Editor de Paredes em `_reversa_sdd/walls2d/` (consome `classify` em `scene_io.py`), desenho 2D do aviso em `_reversa_sdd/canvas2d/` (`draw.text_width`, usado por `overlays/element_toast.py`).

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `classify.py` (165) | não (`collections.namedtuple`, `data.i18n.N_`) | Tipos, marcas, classificação, raízes de módulo, grupo de topo, raízes do Mover Sobre | 🟢 |
| Núcleo puro | `component.py` (146) | não (`collections.namedtuple`, `classify`) | Raiz do componente, `collapse`, agregados próprios, plano de exclusão | 🟢 |
| Ponte | `editing.py` (125) | não diretamente; usa `hb_types`, `data.units`, `data.i18n`; imports tardios de `standards.sync`, `hb_utils`, `operators.walls` | Dimensões, peitoril e parede por biblioteca | 🟢 |
| Ponte | `element_size.py` (61) | sim (`bpy.context.evaluated_depsgraph_get`); imports tardios de `openings.sync`, `aggregates.group`, `operators.doors_windows` | Elemento tocado e medidas | 🟢 |
| Ponte | `resize.py` (129) | sim (`bpy.data.objects`); imports tardios de `aggregates.apply`, `aggregates.limits`, `operators.doors_windows` | Redimensionar com agregados | 🟢 |
| Blender | `component_props.py` (45) | sim | Propriedades e desenho do interruptor | 🟢 |
| Blender | `component_select.py` (180) | sim (`bpy.app.handlers`) | Normalizador, isenções, modos | 🟢 |
| Blender | `component_pick.py` (97) | sim | Operadores do clique e keymap | 🟢 |
| Pacote | `__init__.py` (1) | não | Só docstring; **sem** `register`. O registro é feito por `caffmob_draw/__init__.py`: `component_props`, `component_select`, `component_pick` nessa ordem (após `openings`, antes de `legacy`) e o inverso no `unregister` | 🟢 |

## Interface

### `classify.py` 🟢

| Símbolo | Assinatura / valor | Observação |
|---|---|---|
| `Classified` | `namedtuple('Classified', 'kind obj root library')` | RN-01 |
| Constantes de tipo | `ANNOTATION, FRONT, PART, MODULE, ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE, WALL, FLOOR, CEILING, OTHER` (strings iguais ao nome) | `KINDS` é a tupla nessa ordem |
| `KIND_LABELS` | `N_`: "Cota / anotação", "Frente", "Peça", "Módulo", "Porta", "Janela", "Geometria", "Obstáculo", "Parede", "Piso", "Teto", "Objeto" | Marcados, não traduzidos (o consumidor aplica `tr`) |
| `LIBRARY_LABELS` | `{'FRAMELESS': "Frameless", 'FACE_FRAME': "Face frame", 'CLOSETS': "Closets", 'BTM': "Módulo rápido", 'HB': "Ambiente"}` | Sem chave `''`: consumidores usam `.get` |
| `MODULE_TAGS` | `(('IS_FRAMELESS_CABINET_CAGE','FRAMELESS'), ('IS_FACE_FRAME_CABINET_CAGE','FACE_FRAME'), ('IS_FACE_FRAME_PRODUCT_CAGE','FACE_FRAME'), ('IS_CLOSET_STARTER_CAGE','CLOSETS'))` | Ordem de teste |
| `FRONT_TAGS`, `FRONT_ROLES`, `BTM_FRONT_SUFFIXES` | RN-03 | `FRONT_ROLES` é `frozenset` |
| `btm_kind(obj)` | `str` | RN-04: `getattr(obj,'btm_plane',None)`; `is_property_set` ausente → lê direto. `_btm_kind` é alias |
| `module_library(obj)` | `str` ou `None` | `obj.get(tag)` truthy na ordem de `MODULE_TAGS`; depois `btm_kind == 'MODULE'` → `'BTM'` |
| `_ancestors(obj)` | gerador | `obj`, `obj.parent`, … até `None` |
| `module_root(obj)` | `(root, library)` ou `(None, None)` | Primeiro ancestral com `module_library` |
| `classify(obj)` | `Classified` ou `None` | F-01 |
| `free_group(obj)` | `Object` ou `None` | RN-06: último (mais alto) ancestral com `btm_group.is_group` |
| `movable_root(obj)`, `reference_root(obj)` | `Object` ou `None` | RN-05 |

### `component.py` 🟢

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `DeletePlan` | `namedtuple('DeletePlan', 'remove openings')` | — | Listas de objetos |
| `is_opening_root(node)` | — | `bool` | `IS_ENTRY_DOOR_BP` ou `IS_WINDOW_BP` truthy, ou `btm_kind == 'OPENING'` |
| `_is_stuck(node)` | — | `bool` | `btm_stick.is_stuck` (atributos ausentes → falso) |
| `_is_frame_leaf(node)` | — | `bool` | Acessa `node.btm_aggregate` **sem** `getattr` (só chamado após `_is_own_aggregate` checar o atributo) |
| `_is_own_aggregate(node)` | — | `bool` | RN-08 |
| `_is_item(node)` | — | `bool` | `btm_object_item.is_item` |
| `component_root(obj, modes=None)` | `modes: dict[str,bool]` | `Object` ou `None` | F-02 |
| `collapse(objs, modes=None)` | — | `list` | Raízes sem repetir por `id()`, na ordem; `None` descartado |
| `own_aggregates(target)` | — | `list` | F-03 |
| `_is_frame_group(node)` | — | `bool` | `btm_group.is_group` e `kind == 'FRAME'` |
| `deletes_subtree(obj)` | — | `bool` | `info is None or info.obj is not obj or info.kind ∉ {WALL, FLOOR, CEILING}` |
| `delete_plan(targets, keep_aggregates=False)` | — | `DeletePlan` | F-04 |

### `component_props.py` 🟢

| Propriedade | Dono | Definição | Persistência |
|---|---|---|---|
| `btm_component_select` | `bpy.types.Scene` | `BoolProperty(name="Seleção por componente", default=True, update=_on_toggle, description="Clicar numa peça seleciona o componente inteiro (porta, janela, item importado). Alt + clique seleciona só a peça")` | `.blend`; arquivo antigo lê o padrão |
| `btm_component_exempt` | `bpy.types.WindowManager` | `StringProperty()` | Sessão (limpa no `load_post`) |

- `_on_toggle(_self, _context)`: import tardio de `component_select` e `forget()`. 🟢
- `draw_toggle(layout, context)`: sai se a cena não tem a propriedade; `row(align=True).prop(scene, "btm_component_select", text=tr("Seleção por componente"), icon='CHECKBOX_HLT' ou 'CHECKBOX_DEHLT', toggle=True)`; linha desabilitada com `tr("Ligada: Alt + clique seleciona uma peça")` ou `tr("Desligada: clique seleciona a peça")`. Consumidor: `ui/view3d_sidebar.py` (caixa de modos de seleção). 🟢
- `unregister`: `delattr` de `WindowManager.btm_component_exempt` e `Scene.btm_component_select` se existirem. 🟢

### `component_select.py` 🟢

| Símbolo | Assinatura | Comportamento |
|---|---|---|
| `_busy`, `_last` | listas de 1 elemento (`[False]`, `[None]`) | Trava de reentrada e última assinatura |
| `forget()` | — | `_last[0] = None` |
| `suspended()` | `@contextmanager` | Salva `_busy[0]`, põe `True`, restaura o valor anterior no `finally` (aninhável) |
| `cabinet_modes(scene)` | `dict` | RN-13; import tardio de `legacy.gate` |
| `exempt_names(context)` | `set[str]` | `split("\n")` sem vazios; atributo ausente → `""` |
| `set_exempt(context, names)` | — | `"\n".join(sorted(names))` |
| `_modal_running(context)` | `bool` | Percorre `window_manager.windows[*].modal_operators`; `bl_idname.lower()` com `'transform'` ou `'caffmob'` contido ou prefixo `'btm'` |
| `_selected(context, view_layer)` | `list` | `context.selected_objects`; se `None` (fundo), `[o for o in view_layer.objects if o.select_get(view_layer=view_layer)]`; mantém só `obj is not None and obj.name in view_layer.objects` (`ReferenceError` → pula) |
| `_signature(context, view_layer)` | `(frozenset[str], str)` | Nomes selecionados e nome do ativo (`""` sem ativo) |
| `normalize(context, scene)` | `int` | F-05 |
| `on_depsgraph_update(scene, _depsgraph=None)` | `@persistent` | F-06 |
| `on_load_post(*_args)` | `@persistent` | `forget()`; zera `btm_component_exempt` se o WM existe e tem a propriedade |
| `register()` / `unregister()` | — | Anexa/remove `on_depsgraph_update` em `depsgraph_update_post` e `on_load_post` em `load_post` só se (não) presentes; `unregister` termina com `forget()` |

### `component_pick.py` 🟢

| Operador | `bl_idname` | `bl_options` | Propriedades | `poll` | `invoke` |
|---|---|---|---|---|---|
| `BTM_OT_ComponentPick` ("Selecionar peça") | `caffmob.component_pick` | `{'REGISTER', 'UNDO'}` | `extend: BoolProperty(name="Somar à seleção", default=False)` | `_enabled(context)` | F-07 |
| `BTM_OT_ComponentClickReset` ("Voltar à seleção por componente") | `caffmob.component_click_reset` | `{'INTERNAL'}` | — | `_enabled(context)` e `btm_component_exempt` não vazio | `set_exempt(context, set())`, `forget()`, devolve `{'PASS_THROUGH'}` |

- `_enabled(context)`: `context.mode == 'OBJECT'`, `context.area` não nulo com `type == 'VIEW_3D'` e `scene.btm_component_select` verdadeiro. 🟢
- Keymap (`wm.keyconfigs.addon`; sem ele, o `register` registra só as classes): `km = keymaps.new(name='3D View', space_type='VIEW_3D')`; `caffmob.component_pick` em `LEFTMOUSE` `CLICK` `alt=True` com `shift=False` (`extend=False`) e `shift=True` (`extend=True`), ambos `head=True`; `caffmob.component_click_reset` em `LEFTMOUSE` `PRESS` sem modificadores, `head=True`. Itens guardados em `_addon_keymaps` e removidos no `unregister` (exceções `ReferenceError`/`RuntimeError` engolidas). 🟢

### `editing.py` 🟢

| Símbolo | Valor / assinatura | Observação |
|---|---|---|
| `DIM_FIELDS` | `('width', 'height', 'depth')` | — |
| `DIM_LABELS` | `N_`: "Largura", "Altura", "Profundidade" | — |
| `GN_DIM` | `{'width': 'Dim X', 'depth': 'Dim Y', 'height': 'Dim Z'}` | — |
| `WALL_FIELDS` | `length→('Length',"Comprimento")`, `height→('Height',"Pé-direito inicial")`, `end_height→('End Height',"Pé-direito final")`, `thickness→('Thickness',"Espessura")` | — |
| `LIMITS` | `width (0.01,10)`, `height (0.01,10)`, `depth (0.005,10)`, `length (0.05,100)`, `end_height (0.5,10)`, `thickness (0.01,2)`, `sill (0.0,5.0)` | Inclusivos |
| `WALL_LIMITS` | `{'height': (0.5, 10.0)}` | Sobrepõe `LIMITS` em `set_wall` |
| `_check(field, value, label, limits=None)` | levanta `ValueError` | Mensagem com `units.format_length(x, units.get_scene_length_unit())` |
| `has_dimensions(info)`, `editable_dimensions(info)` | `bool`, `tuple` | RN-16 |
| `get_dimension(info, field)` | `float` | F-08 |
| `set_dimension(context, info, field, value)` | — | F-09 |
| `get_sill(info)` / `set_sill(info, value)` | — | RN-19 |
| `get_wall(info, field)` / `set_wall(info, field, value)` | — | `GeoNodeWall(info.obj).get_input/set_input`; RN-20 |

### `element_size.py` 🟢

| Símbolo | Assinatura | Comportamento |
|---|---|---|
| `Element` | `namedtuple('Element', 'obj info label')` | `label` é o `N_` do tipo (não traduzido) |
| `_GN_KINDS` | `(MODULE, ROOM_DOOR, WINDOW, GEOMETRY, OBSTACLE)` | — |
| `element(obj)` | `Element` ou `None` | RN-21 |
| `_door_kind(cage)` | `str` | `openings.sync.kind_of(cage)`: `WINDOW`, o `btm_opening_real.kind` ≠ `NONE`, `OPEN_DOOR` sem giro, `DOUBLE_DOOR` ou `DOOR` |
| `box_size(obj)` | `(largura, altura, profundidade)` | `aggregates.group.object_corners(obj, depsgraph)` (Empty: cantos das malhas descendentes no espaço local; sem malhas → 8 zeros); extensões X, Y, Z × `matrix_world.to_scale()`, em valor absoluto; devolve `(x, z, y)` |
| `size(el)` | `(largura, altura, profundidade)` m | RN-22 |

### `resize.py` 🟢

| Símbolo | Assinatura | Comportamento |
|---|---|---|
| `MIN_WIDTH`, `MAX_WIDTH` | `0.01`, `100.0` | — |
| `can_resize(el)` | `bool` | `None` → falso; `WALL` → `library == 'HB'`; `MODULE` → `'width' in editable_dimensions`; `FLOOR`/`CEILING` → falso; resto → verdadeiro |
| `_parents_with_aggregates(root)` | `list` | `[root] + children_recursive` filtrado por `aggregates.apply.aggregates_of(o)` não vazio |
| `_width_x(obj)` | `float` | `aggregates.apply.local_box(obj)`: `hi[0] − lo[0]` da caixa avaliada local |
| `_stretched(el)` | `bool` | `GEOMETRY` sem `btm_geometry`; `OBSTACLE` sem `home_builder.mod_name`; `OTHER` |
| `_set_width(context, el, width)` | — | F-10 |
| `_stretch_aggregate(child, factor, u, v)` | — | F-11 |
| `resize(context, el, width)` | — | F-12 |

### Superfície exposta pelos consumidores 🟢 (fora da unit, citada para reimplementação)

| Consumidor | O que usa | Comportamento |
|---|---|---|
| `aggregates/ops_aggregate.py:BTM_OT_DeleteWithAggregates` (`caffmob.delete_with_aggregates`, item de X/Delete) | `deletes_subtree`, `own_aggregates`, `delete_plan` | `poll`: modo OBJECT e algum selecionado com (`children` e `deletes_subtree`) ou agregados próprios ou grudados. Com agregados abre o diálogo "O objeto tem agregados" (`with_aggregates`, padrão True). `delete_components`: solta grudados, `delete_plan(targets, keep_aggregates=not with_aggregates)`, `convert.unconvert` dos agregados mantidos, remove booleanos dos vãos (`plan.openings`) na parede `IS_WALL_BP`, apaga recortadores, `bpy.data.batch_remove` |
| `ui/ops_resize.py:BTM_OT_ResizeWidth` (`btm.resize_width`, `REGISTER`/`UNDO`, menu do botão direito) | `element`, `size`, `can_resize`, `resize` | `width: FloatProperty(DISTANCE, LENGTH, min=0.01, max=100.0, precision=5)`; elemento = `element(active_object)` se selecionado; `poll` = `can_resize` (exceção → falso); `invoke` preenche com `size(el)[0]` e abre diálogo de 260 px; `execute`: `ValueError` → `report ERROR` e `CANCELLED`; sucesso → `element_toast.show` |
| `overlays/element_toast.py` (`POST_PIXEL`, 3 s) | `element`, `size` | Texto `tr("{} {}   L {} × A {} × P {}")` com `tr(el.label)`, nome e `units.format_value`; exceção na medida → sem aviso naquele quadro |
| `ui/object_properties.py` | `classify`, `has_dimensions`, `get_dimension`, `set_dimension`, `editable_dimensions`, `get_wall`, `set_wall`, `get_sill`, `set_sill`, `KIND_LABELS`, `LIBRARY_LABELS` | Campos virtuais `FloatProperty(DISTANCE, LENGTH, precision=1, get, set)`; setters em `_guard` (`ValueError` → `window_manager['btm_selection_error']`); getters engolem exceções (→ 0.0) |
| `ui/view3d_sidebar.py` | `component_props.draw_toggle` | Caixa de modos de seleção |
| `cabinet_editor/bridge.py`, `legacy/convert.py` | `classify`, `get_dimension`, `set_dimension`, `own_aggregates` | Medidas do módulo no editor de armário e na conversão de herdados |
| `measure/scene_cotas.py`, `move_over/*`, `stick/*`, `collision/scan.py`, `customize/*`, `standards/*`, `walls2d/scene_io.py`, `overlays/draw_handlers.py`, bibliotecas herdadas | `classify`, `module_root`, `module_library`, `movable_root`, `reference_root`, `free_group`, `btm_kind` | 33 arquivos importam `selection` (grep) |

## Fluxo Principal

1. 🟢 O usuário clica numa peça no 3D; o `view3d.select` do Blender seleciona a peça (ou o reset limpa isenções antes, F-07b).
2. 🟢 O `depsgraph_update_post` dispara `on_depsgraph_update` (F-06), que chama `normalize` (F-05): a peça vira a raiz do componente (F-02).
3. 🟢 Painel, aviso (`element_toast`) e diálogo Redimensionar leem `classify`/`element`/`size` do ativo; edições passam por `set_dimension`/`set_wall`/`set_sill` (F-09) ou `resize` (F-12).
4. 🟢 Delete usa `delete_plan` (F-04) via `caffmob.delete_with_aggregates`.

### F-01 `classify(obj)` 🟢 `classify.py:classify` (ver `_reversa_sdd/flowcharts/selection-classify.md`)
1. `obj is None` → `None`. `obj.get('IS_2D_ANNOTATION')` → `Classified(ANNOTATION, obj, obj, 'HB')`.
2. `root, library = module_root(obj)`. Com raiz: percorre `_ancestors(obj)` até encontrar `root` (sem testá-lo); primeiro `_is_front(node)` → `Classified(FRONT, node, root, library)`. Depois `obj is root` → `MODULE`; senão `PART` com `obj`.
3. Sem raiz: para cada `node` em `_ancestors(obj)`, testa na ordem de RN-01 (`btm_kind(node)` é lido uma vez por nó, após os testes de porta e janela HB); o primeiro que casa devolve `Classified(kind, node, node, lib)`.
4. Nenhum → `Classified(OTHER, obj, obj, '')`.

### F-02 `component_root(obj, modes=None)` 🟢 `component.py` (ver `flowcharts/selection-component_root.md`)
1. `None` → `None`. `chain = list(_ancestors(obj))`.
2. Primeiro `node` da `chain` com `is_opening_root` → devolve.
3. `obj.get('IS_2D_ANNOTATION')` → `obj`.
4. Para cada `node` da `chain`: `module_library(node)` → para (break); `_is_stuck(node) or _is_own_aggregate(node)` → devolve `node`.
5. `root, library = module_root(obj)`; com raiz → `root if (modes or {}).get(library, True) else obj`.
6. Primeiro `node` com `_is_item` → devolve.
7. `free_group(obj)` ou `obj`.

### F-03 `own_aggregates(target)` 🟢
1. Se `target` é vão ou grupo `FRAME` → `[]`.
2. `walk(node)`: para cada filho: vão → pula (não desce); `_is_own_aggregate(child) and component_root(child) is child` → recolhe e não desce; senão desce. **Desce em módulos e paredes** (EC-07).

### F-04 `delete_plan(targets, keep_aggregates=False)` 🟢 (ver `flowcharts/selection-component_root.md`)
1. `keep = {id(a) for t in targets for a in own_aggregates(t)}` se `keep_aggregates`, senão vazio.
2. `walk(node, is_target)`: já visto → volta; não-alvo e (grudado ou em `keep`) → volta; marca visto; se não-alvo ou `deletes_subtree(node)`, `walk` em cada filho (cópia da lista) com `False`; `remove.append(node)` (pós-ordem).
3. `walk(t, True)` para cada alvo na ordem; `openings = [n for n in remove if is_opening_root(n)]`.

### F-05 `normalize(context, scene)` 🟢
1. `view_layer = context.view_layer`; `selected = _selected(...)`; `names` = nomes.
2. `exempt = exempt_names(context)`; se há isentos fora de `names`, `exempt &= names` e `set_exempt`.
3. `modes = cabinet_modes(scene)`; `promoted = 0`.
4. Para cada `obj` selecionado não isento: `root = component_root(obj, modes)`; pula se `None`, `root is obj` ou `root.name not in view_layer.objects`; `root.select_set(True, view_layer=view_layer)` (`RuntimeError` → pula); se `root.select_get(view_layer=view_layer)`, `obj.select_set(False, ...)` e `promoted += 1`.
5. Ativo não nulo e não isento: `root = component_root(active, modes)`; se `root` não é o ativo e está selecionado → `view_layer.objects.active = root`.
6. Devolve `promoted`.

### F-06 `on_depsgraph_update(scene, _depsgraph=None)` 🟢 (ver `flowcharts/selection.md` §1)
1. `_busy[0]` → sai. `context = bpy.context`.
2. `not getattr(scene, 'btm_component_select', False)` → `_last[0] = None`; sai.
3. `view_layer is None`, `context.mode != 'OBJECT'` ou `window_manager is None` → sai. `_modal_running` → sai.
4. `signature == _last[0]` → sai.
5. `_busy[0] = True`; `normalize(context, scene)`; `finally` `_busy[0] = False`.
6. `_last[0] = _signature(context, view_layer)` (assinatura **depois** da promoção).

### F-07 `caffmob.component_pick.invoke` 🟢
1. `exempt = exempt_names(context)` se `extend`, senão `set()`.
2. Dentro de `suspended()`: `result = bpy.ops.view3d.select(extend=self.extend, deselect_all=not self.extend, location=(event.mouse_region_x, event.mouse_region_y))`; `obj = view_layer.objects.active`; se `'FINISHED' in result` e `obj` selecionado → `exempt.add(obj.name)`; `set_exempt(context, exempt)` (ainda suspenso).
3. `forget()`; devolve `{'FINISHED'}` (mesmo se o clique não acertou nada).

F-07b `caffmob.component_click_reset`: só passa no `poll` com isenções; limpa e devolve `PASS_THROUGH` para o `view3d.select` seguir; o normalizador age em seguida. 🟢

### F-08 `get_dimension(info, field)` 🟢
1. `obj = info.root` para `MODULE`/`FRONT`/`PART`, senão `info.obj`.
2. Para esses três tipos: `FACE_FRAME` com `face_frame_cabinet` → atributo; `CLOSETS` com `hb_closet_starter` → atributo; `BTM` com `btm_cabinet` → atributo.
3. `home_builder.mod_name` preenchido e campo em `GN_DIM` → `GeoNodeObject(obj).get_input(GN_DIM[field])` (exceção → segue).
4. `obj.dimensions` → `{'width': x, 'depth': y, 'height': z}[field]`.

### F-09 `set_dimension(context, info, field, value)` 🟢
1. Campo fora de `editable_dimensions(info)` → `ValueError(tr("Valor Inválido: {} não é editável para este objeto.").format(tr(DIM_LABELS[field])))`.
2. `_check(field, value, DIM_LABELS[field])`.
3. `obj = info.root` se `MODULE`, senão `info.obj`. `MODULE` + `FACE_FRAME`/`CLOSETS`/`BTM` → `setattr` no grupo da biblioteca.
4. Senão `GeoNodeObject(obj).set_input(GN_DIM[field], value)`; se `MODULE` (frameless): `standards.sync.add_override(obj, GN_DIM[field])` (grava `json.dumps(sorted(...))` na idprop de overrides da raiz) e `hb_utils.run_calc_fix(context, obj)` (2 passes, contorno do bug #133392). Porta/janela HB: **só** o input (EC-08).

### F-10 `_set_width(context, el, width)` 🟢
1. `_stretched(el)`: `current = size(el)[0]`; `≤ 1e-9` → `ValueError(tr("Valor Inválido: o objeto não tem largura para redimensionar."))`; `obj.scale.x *= width / current` (via cópia de `scale`).
2. `MODULE` → `editing.set_dimension(context, info, 'width', width)`.
3. `ROOM_DOOR`/`WINDOW` → porta: `width = _leaf_to_hole(kind_of(obj), 'X', width)`; `GeoNodeCage(obj).set_input('Dim X', width)`; `doors_windows._sync_opening(context, obj)` (exceção → `print` e segue).
4. `WALL` → `editing.set_wall(info, 'length', width)`. `GEOMETRY` → `obj.btm_geometry.width = width`. Senão (obstáculo com GN) → `GeoNodeObject(obj).set_input('Dim X', width)`.

### F-11 `_stretch_aggregate(child, factor, u, v)` 🟢
1. `agg.kind == 'LEAF'` → nada.
2. `normal, _sign, u_axis, v_axis = limits.face_axes(agg.face)` (`_AXIS = {'X':0,'Y':1,'Z':2}` pela última letra; `u`, `v` = os outros dois eixos em ordem).
3. `normal != 0`: `to_parent = (parent_ref.matrix_world.inverted() @ child.matrix_world).to_3x3()`; `axis = argmax_j |to_parent.col[j].normalized()[0]|`; `child.scale[axis] *= factor`; `agg.size[0] *= factor`; `agg.rest_offset[0] *= factor`.
4. `apply._write(child, 'u', u·factor se u_axis == 0 senão u)`; idem `v`; `apply.update_position(child)` (clamp de `u`, `v`, `offset` na caixa do pai).

### F-12 `resize(context, el, width)` 🟢
1. `not can_resize(el)` → `ValueError(tr("Valor Inválido: este elemento não pode ser redimensionado por aqui."))`.
2. Fora de `[0.01, 100.0]` → `ValueError(tr("Valor Inválido: a largura deve estar entre {} e {} m.").format(0.01, 100.0))` (números crus).
3. `before = {}` se esticado; senão `{o.name: (_width_x(o), {c.name: (c.btm_aggregate.u, c.btm_aggregate.v) for c in aggregates_of(o)}) for o in _parents_with_aggregates(el.obj)}` (antes da mudança: o gancho dos agregados reajusta posições assim que o pai muda).
4. `_set_width`; `context.view_layer.update()`.
5. Para cada pai (por nome em `bpy.data.objects`): ausente ou largura antiga `≤ 1e-9` → pula; `factor = _width_x(parent) / old`; `|factor − 1| < 1e-6` → pula; para cada agregado atual que estava em `positions` → `_stretch_aggregate(child, factor, u, v)`.
6. `context.view_layer.update()`.

## Fluxos Alternativos

- **Interruptor desligado**: o normalizador esquece a assinatura a cada atualização; `component_pick` e `component_click_reset` saem pelo `poll` e o Alt + clique volta ao do Blender. 🟢
- **Modo peça da biblioteca herdada** (`show_legacy_libraries` ligado e modo ≠ gabinete): `component_root` devolve a própria peça (não a frente). 🟢
- **Raiz oculta ou fora da camada de vista**: `select_set` falha ou não pega; a peça continua selecionada (EC-03). 🟢
- **Sem janela (modo fundo)**: `_selected` lê pela camada de vista. 🟢
- **Porta real falha ao refazer no Redimensionar**: `_sync_opening` imprime e devolve `False`; caixa e furo ficam valendo. 🟢

## Máquina de Estados do Normalizador 🟢

| Estado | Entrada | Saída |
|---|---|---|
| Inativo | interruptor desligado (`_last = None`), modo ≠ OBJECT, modal rodando, `_busy` | Mudança de condição na próxima atualização |
| Em repouso | assinatura igual a `_last` | Assinatura diferente → Normalizando |
| Normalizando | `_busy = True` | Grava `_last` pós-promoção → Em repouso |
| Suspenso | `suspended()` (Alt + clique) | Fim do bloco restaura `_busy` anterior; `forget()` força reavaliar |

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `data/i18n.py` | `N_`, `tr` | 🟢 |
| `data/units.py` | `get_scene_length_unit`, `format_length` (mensagens de `_check`) | 🟢 |
| `hb_types.GeoNodeObject` | `get_input`/`set_input` de `Dim X/Y/Z`; levanta `ValueError("Object does not have geometry node modifier")` sem `home_builder.mod_name` | 🟢 |
| `hb_types.GeoNodeWall`, `GeoNodeCage` | Inputs da parede e do vão | 🟢 |
| `standards/sync.add_override(obj, name)` | Medida manual do frameless (001 RN-23) | 🟢 |
| `hb_utils.run_calc_fix(context, obj=None, passes=2)` | Recalcular drivers | 🟢 |
| `operators/walls.update_all_wall_miters()` | Meias-esquadrias de todas as paredes `IS_WALL_BP` | 🟢 |
| `operators/doors_windows` | `_hole_to_leaf(kind, axis, value)`, `_leaf_to_hole(kind, axis, value)` (só `DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`; porta dupla divide/multiplica a folha por 2 em X), `_sync_opening(context, obj)` | 🟢 |
| `openings/sync.kind_of(cage)` | Tipo de porta | 🟢 |
| `aggregates/group.object_corners`, `aggregates/apply` (`local_box`, `aggregates_of`, `_write`, `update_position`), `aggregates/limits.face_axes` | Caixas e agregados | 🟢 |
| `legacy/gate.legacy_ui(context=None)` | `preferences.show_legacy_libraries` | 🟢 |
| idprops / PropertyGroups | `IS_*` (RN-01 a RN-03), `hb_part_role`, `btm_plane.object_kind`, `btm_group.is_group/kind`, `btm_aggregate.*`, `btm_stick.is_stuck`, `btm_object_item.is_item`, `face_frame_cabinet`, `hb_closet_starter`, `btm_cabinet`, `btm_geometry.width`, `home_builder.mod_name`, `Scene.hb_frameless/hb_face_frame/hb_closets` | 🟢 |
| `data/translations/selection.json` | 23 chaves `pt_BR`/`en_US` | 🟢 |

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Classificador único para todas as bibliotecas, com frente/peça antes do módulo e módulo antes da parede (gabinetes são filhos da parede) | `classify.py` docstring (002 D-09, RN-01) | 🟢 |
| Núcleo puro testável sem Blender | docstrings de `classify.py` e `component.py`; testes com objetos simulados | 🟢 |
| Seleção por componente por normalização pós-depsgraph (qualquer origem de seleção), não por operador de clique | `component_select.py` docstring (011 D-02) | 🟢 |
| Isenção de sessão em `WindowManager` (não salva no arquivo) | `component_props.py` (011 D-04, D-08) | 🟢 |
| Exclusão por plano puro executado pelo operador de Delete existente | `component.delete_plan`; `ops_aggregate.delete_components` (011 D-05) | 🟢 |
| Módulos sobem sempre sem a interface herdada | `cabinet_modes` (012 D-05) | 🟢 |
| Porta medida e redimensionada pela folha | `element_size.size`, `resize._set_width` (feature 010 RN-02) | 🟢 |
| `btm_kind` só com `is_property_set` | `classify.btm_kind` (BUG-TBY3, commit `b92ac2e`) | 🟢 |

## Estado Interno

- 🟢 Global de módulo: `_busy[0]`, `_last[0]` (`component_select`), `_addon_keymaps` (`component_pick`).
- 🟢 Persistente: `Scene.btm_component_select` (`.blend`). Sessão: `WindowManager.btm_component_exempt`.
- 🟢 Escritas na cena: seleção e ativo (normalizador, Alt + clique); grupos de biblioteca, inputs GN, idprop de overrides, `location.z`, inputs da parede, `scale`, `btm_geometry.width`, `btm_aggregate.size/rest_offset/u/v` (edição e Redimensionar).

## Observabilidade

- 🟢 Nenhum log próprio. Erros de domínio são `ValueError` "Valor Inválido: …" traduzidos (o consumidor exibe: `report` no Redimensionar, `btm_selection_error` no painel). `_sync_opening` imprime no console em falha. O normalizador é silencioso.

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-20):** painel pelo caminho do Redimensionar (`_leaf_to_hole` + `_sync_opening`), mostrando a folha (também questions.md#pergunta-69). 🟢 (código) hoje não refaz a porta real (EC-08). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-2):** `own_aggregates` para em raízes de módulo e em parede/piso/teto. 🟢 (código) hoje desce (EC-07). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-21):** `can_resize` bloqueia janela BTM. 🟢 (código) hoje aceita sem caminho de gravação válido (EC-10). Pendência de implementação: DT-03.
- 🟢 _(Revisão 2026-10-10: component_select.py:80)_ `_modal_running` por substring: qualquer modal de terceiros com `transform` no nome também suspende o normalizador; um modal da extensão com outro prefixo não suspende (EC-05).
- 🟢 Assinatura por **nomes**: renomear um objeto selecionado reavalia a seleção _(Revisão 2026-10-10: component_select.py:99-101 usa `o.name`, não `name_full`)_; 🟡 nomes duplicados entre bibliotecas vinculadas colidem (inferido; não testado).

## Divergências entre artefatos e código

- 🟢 `_reversa_forward/011…/roadmap.md` D-04 nomeia o operador `btm.component_pick`; o código usa `caffmob.component_pick`. D-03 previa `btm.component_click` que **promovia** na hora; o código tem `caffmob.component_click_reset`, que só **limpa isenções** e deixa a promoção ao normalizador.
- 🟢 `domain.md` RN-SELECTION-13 e a docstring de `editing.py` falam em "recálculo das esquadrias"; o código chama `update_all_wall_miters` (ângulos de meia-esquadria das paredes), não as esquadrias de porta/janela.
- 🟢 `code-analysis.md` §8.2 descreve `own_aggregates` como "agregados abaixo de `target`" sem dizer que desce em módulos/paredes; o efeito no Delete de parede (EC-07) não está registrado.
- 🟢 `code-analysis.md` §8.6 e `domain.md` RN-SELECTION-11 tratam porta/janela HB como editáveis pelo painel sem notar que a porta real não é refeita (EC-08).
- 🟢 `state-machines.md` não tem a máquina do normalizador (incluída acima). `flowcharts/selection*.md`, `data-dictionary.md` §7 e `erd-complete.md` estão alinhados com o código.
