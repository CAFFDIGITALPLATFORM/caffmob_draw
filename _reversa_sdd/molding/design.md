# Molduras de ambiente por pacote (molding) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/molding/` em 2026-10-10 (sem alterações pendentes na pasta). IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender. Mesmo motor descrito em `_reversa_sdd/catalog_molding/design.md` (caminho antigo `blendertomob/molding/`); diferenças só em `ops.py` (ver `requirements.md`, cabeçalho).

## Visão de Camadas

| Camada | Arquivo | Importa | Papel | Confiança |
|---|---|---|---|---|
| Fachada | `__init__.py` | `ops` | `register`/`unregister` delegam a `ops` | 🟢 |
| Geometria | `engine.py` | `math`, `mathutils`, `hb_types`, `units` | Planta XY mundial: medidas, grupos, cadeias, offsets, percursos | 🟢 |
| Fatos | `adapters.py` | `mathutils`, `engine`, `hb_types`; tardio: `product_libraries.face_frame.props_hb_face_frame`, `hb_project` | Lê bibliotecas face frame e frameless e produz `FACTS` | 🟢 |
| Catálogo de perfis | `packages.py` | `os`, `bpy`, `units` | Pacotes, packs externos, contornos embutidos, métricas | 🟢 |
| Orquestração | `ops.py` | `bpy`, `mathutils`, `data.i18n.tr`, `adapters`, `engine`, `packages` | Limpar, resolver, posicionar, criar sweeps; operador | 🟢 |

🟢 Registro: o pacote principal importa `molding` (`caffmob_draw/__init__.py:74`) e chama `molding.register()` depois de `closets`, `face_frame`, `frameless`, `wood_hoods` (linha 321); `molding.unregister()` na linha 347, logo após `closets.unregister()`. As 14 propriedades da sala são registradas por `hb_props` (classe `Home_Builder_Scene_Props`, `Scene.home_builder`), não por esta unit.

🟢 O motor é agnóstico de biblioteca: `engine.py` nunca lê grupos de propriedades das bibliotecas; tudo que é específico vem em `FACTS` (`engine.py` docstring; padrão de adaptadores por biblioteca, ADR `_reversa_sdd/adrs/0005-adaptadores-por-biblioteca.md`).

## Modelo de Dados

### `FACTS` (efêmero, `dict[id(obj)] → dict`)

| Chave | Tipo | Origem | Consumidor | Confiança |
|---|---|---|---|---|
| `role` | `'CABINET'` \| `'APPLIANCE'` | `IS_APPLIANCE` | `_kick_spans_local` | 🟢 |
| `corner` | `None` \| `{'ld', 'rd', 'diagonal'}` | FF: `face_frame_cabinet.corner_type != 'NONE'` → `left_depth`, `right_depth`, `corner_type == 'DIAGONAL'`; frameless: idprop `IS_CORNER_CABINET` → idprops `Left Depth`, `Right Depth`, `CORNER_TYPE == 'DIAGONAL'` | `corner_plan_data`, `_assemble_*`, `_island_perimeter_spans` | 🟢 |
| `kick` | `{'skip', 'setback', 'stile_left', 'stile_right', 'stile_left_w', 'stile_right_w'}` | RN-08 (montantes só no FF: `extend_left/right_stile_to_floor`, `left/right_stile_width`, `toe_kick_setback`) | `_kick_spans_local`, `_assemble_kick_spans` | 🟢 |
| `crown_mount` | `None` \| `{'rail_width', 'door_overlay'}` | só FF: `_top_rail_width(obj)` (filho recursivo com idprop `hb_part_role == 'TOP_RAIL'`, input GN `Width` não nulo) e `max(default_top_overlay or 0, 0)`; chave ausente no frameless e nas pontes | `ops._crown_datum` | 🟢 |
| `finished_left`, `finished_right` | `bool` | RN-07; pontes `False` | `chain_sweep_points`, `_stretch_segments` | 🟢 |

### Entrada de pilha `(profile_ref, fallback_key, dx, dy)`

| Campo | Tipo | Significado | Confiança |
|---|---|---|---|
| `profile_ref` | `str` `"Categoria/Nome"` (aceita `\`) | caminho dentro de um pack; a categoria (1º segmento) chaveia overrides | 🟢 |
| `fallback_key` | `str` | chave de `_PROFILE_OUTLINES`; também nome do perfil `Molding_Profile_<key>` | 🟢 |
| `dx` | `float` \| `'STACK_FRONT'` | deslocamento para fora (offset à direita do percurso), m | 🟢 |
| `dy` | `float` \| `'STACK_OFFSET'` | deslocamento vertical somado ao Z do tipo, m | 🟢 |

### Sweep criado (persistido no `.blend`)

| Item | Valor | Confiança |
|---|---|---|
| Objeto | `bpy.data.objects.new("MoldingSweep", curve)` ligado a `scene.collection`; `parent = chain[0]` sem `matrix_parent_inverse` (identidade) → coordenadas no espaço local do 1º membro; `location.z` = RN-12 | 🟢 |
| Curva | `bpy.data.curves.new("MoldingSweep", 'CURVE')`; `dimensions = '2D'`, `bevel_mode = 'OBJECT'`, `bevel_object = perfil`, `use_fill_caps = True`; 1 spline `BEZIER` por segmento, handles `VECTOR`, `use_smooth = False`, `use_cyclic_u` conforme o segmento; material = RN-17 | 🟢 |
| idprops | `IS_HB_MOLDING_SWEEP = True`; `HB_MOLDING_TYPE` ∈ {`CROWN`, `CAP`, `BASE`, `LIGHT_RAIL`} (string, não enum); `HB_MOLDING_MEMBERS = ",".join(nomes da cadeia)` | 🟢 |
| Perfil | objeto `Molding_Profile_<fallback_key>` (ou o objeto anexado do pack) em `scene.collection`, `parent = sweep`, `hide_viewport = hide_render = True`, `scale = (1,1,1)`, idprop `IS_HB_MOLDING_PROFILE = True`; curva: `dimensions='2D'`, `bevel_depth=0`, `fill_mode='NONE'` (nessa ordem: `fill_mode='NONE'` é rejeitado em curva 3D) | 🟢 |
| Consumidores das idprops | nenhum fora de `molding/` (grep de `IS_HB_MOLDING`/`HB_MOLDING_` no pacote) | 🟢 |

### Propriedades da sala (`Scene.home_builder`, definidas em `hb_props.py:512-599`)

| Propriedade | Tipo / padrão | Uso | Confiança |
|---|---|---|---|
| `molding_crown_package`, `molding_base_package`, `molding_light_rail_package` | `EnumProperty` dinâmico (`packages.enum_items(tipo)`): `NONE` + pacotes; padrão = 1º item (`NONE`) | pilha do tipo | 🟢 |
| `molding_base_include_recessed` | `BoolProperty`, `False` | mantém `RECESS` | 🟢 |
| `molding_crown_reveal` | `FloatProperty`, `inch(0.625)` = 0,015875 m, `min=0`, `LENGTH`, `precision=4` | RN-11 | 🟢 |
| `molding_crown_stack_offset` | `FloatProperty`, `inch(3.5)` = 0,0889 m, `min=0` | `STACK_OFFSET` | 🟢 |
| `molding_crown_furniture_cap` | `BoolProperty`, `False` | RN-15 | 🟢 |
| `molding_cap_offset` | `FloatProperty`, `0.0`, `soft_min/soft_max = ∓inch(6)` (sem limite rígido) | RN-12 | 🟢 |
| `molding_crown_profile`, `molding_spacer_profile`, `molding_cap_profile`, `molding_base_profile`, `molding_light_rail_profile` | `EnumProperty` dinâmico (`packages.profile_enum_items(categoria)`): `DEFAULT` + nomes; categorias `Crown Molding`, `Spacer`, `Furniture Caps`, `Base Molding`, `Light Rail` | overrides | 🟢 |
| `molding_base_shoe` | `BoolProperty`, `False` | RN-14 | 🟢 |

🟢 Todas as 14 têm `update=update_molding_package` (`hb_props.py:177`), que chama `ops.on_package_changed(self, context)`.

## Interface

### `packages.py`

| Símbolo | Contrato | Confiança |
|---|---|---|
| `_PROFILE_PATHS` | lista de módulo; `register_profile_path(path)`: acrescenta se `path` verdadeiro, `os.path.isdir(path)` e ainda não presente, e limpa os 2 caches; `unregister_profile_path(path)`: remove se presente e limpa os caches; `profile_paths()` → `tuple` | 🟢 |
| `profile_enum_items(category)` | cache por categoria; para cada pack em ordem, `os.listdir(<pack>/<categoria>)` ordenado, arquivos `*.blend` (case-insensitive), nome sem os 6 últimos caracteres, sem repetir; devolve `(('DEFAULT', "Default", "Use the package's standard profile"), (nome, nome, ""), …)` | 🟢 |
| `CROWN_PACKAGES` | `SIMPLE` "Simple Crown" `[('Crown Molding/51 Crown','crown_simple',0,0)]`; `STACKED` "Stacked w/ Spacer" `[('Spacer/Square Edge Spacer','flat_stock',0,0), ('Crown Molding/51 Crown','crown_simple','STACK_FRONT','STACK_OFFSET')]`; `SPACER` "Spacer Only" `[('Spacer/Square Edge Spacer','flat_stock',0,0)]` | 🟢 |
| `FURNITURE_CAP_STACK` | `[('Furniture Caps/Furniture 3 Inch','furniture_cap',0,0)]` | 🟢 |
| `BASE_PACKAGES` | `SIMPLE` "Simple Base" `[('Base Molding/Standard Base','base_simple',0,0)]` | 🟢 |
| `BASE_SHOE_REF`, `BASE_SHOE_FALLBACK` | `'Base Molding/Base Shoe'`, `'base_shoe'` | 🟢 |
| `LIGHT_RAIL_PACKAGES` | `SIMPLE` "Simple Light Rail" `[('Light Rail/Cove Cut LR','light_rail_simple',0,0)]` | 🟢 |
| `PACKAGES` | `{'CROWN': …, 'BASE': …, 'LIGHT_RAIL': …}` (sem `CAP`) | 🟢 |
| `package_stack(tipo, ident)` | pilha do pacote ou `None` (inclusive `NONE`) | 🟢 |
| `stack_has_adjustable_offset(tipo, ident)` | há entrada com `dy == 'STACK_OFFSET'` | 🟢 |
| `stack_uses_category(tipo, ident, categoria)` | há entrada cujo 1º segmento do `ref` é `categoria` | 🟢 |
| `enum_items(tipo)` | tupla pré-calculada no import: `('NONE', "None", "No molding")` + `(ident, label, desc)` | 🟢 |
| `make_profile_object(ref, fallback, name, collection)` | `_load_library_profile` → se `None`, contorno embutido: curva `name` 2D, `fill_mode='NONE'`, 1 spline `POLY` com os pontos `(x, y, 0, 1)`, `use_cyclic_u=True`, objeto `name`, `_finish_profile`; `None` se não há contorno | 🟢 |
| `_load_library_profile(ref, collection)` | `stem` = último segmento; para cada pack: `<pack>/<segmentos>.blend`; `bpy.data.libraries.load(path)` (append) pedindo `[stem]` se existir; exceção → próximo pack; objeto `None`/ausente → próximo; senão `_finish_profile` | 🟢 |
| `profile_top_height(ref, fb)` / `profile_front_depth(ref, fb)` | `_profile_metrics(ref, fb)[0]` / `[1]` | 🟢 |
| `_profile_metrics(ref, fb)` | cache por `ref` (ignora `fb`); carrega o objeto do pack como acima; se `CURVE` → `_curve_metrics`; remove o objeto e a curva órfã; sem métrica → do contorno embutido: `(max y, max x − min x)`, `(0, 0)` se não houver | 🟢 |
| `_curve_metrics(obj)` | sobre os pontos de controle de todos os splines (`bezier_points` ou `points`): `(max y, max x − min x)`; `(0, 0)` sem pontos | 🟢 |

**Contornos embutidos** (`_PROFILE_OUTLINES`, polegadas; +Y sobe pela face, X negativo = para dentro do armário) — 🟢

| Chave | Pontos (x, y) | Topo / espessura |
|---|---|---|
| `crown_simple` | (0,0) (0,0.5) (−0.125,0.75) (−0.625,2.5) (−0.75,2.75) (−0.75,3) (−0.875,3) (−0.875,0) | 3" / 0,875" |
| `flat_stock` | (0,0) (0,3.5) (−0.75,3.5) (−0.75,0) | 3,5" / 0,75" |
| `furniture_cap` | (0.375,0) (0.375,1) (−0.75,1) (−0.75,0) | 1" / 1,125" (nariz 0,375" para fora) |
| `base_simple` | (0,0) (0,2.5) (−0.25,3) (−0.625,3) (−0.625,0) | 3" / 0,625" |
| `base_shoe` | (0,0) (0,0.375) (−0.1875,0.75) (−0.4375,0.75) (−0.4375,0) | 0,75" / 0,4375" |
| `light_rail_simple` | (0,0) (0,−1.25) (−0.25,−1.5) (−0.75,−1.5) (−0.75,0) | 0" / 0,75" (pende para baixo) |

### `adapters.py`

| Símbolo | Contrato | Confiança |
|---|---|---|
| `collect_targets(scene, molding_type)` | RN-01; `molding_type` ∈ {`CROWN`, `CAP`, `BASE`, `LIGHT_RAIL`} (outro → `KeyError`) | 🟢 |
| `collect_bridges(scene)` | RN-02 | 🟢 |
| `build_facts(scene, members)` | `FACTS` para todos os membros; calcula `_wall_bounds(scene)` uma vez (AABB XY mundial de cada `IS_WALL_BP` via `bound_box`) | 🟢 |
| `_frameless_end_finished(obj, side, wall_bounds)` | meio da lateral `(0 ou largura, −prof/2, 0)` no mundo; sonda = meio + 0,03 m na direção `±X` local projetada em XY e normalizada; acabada = `not _near_wall(sonda, bounds, 0,05)` | 🟢 |
| `finish_material(obj)` | FF: idprop `STYLE_NAME` → estilo de mesmo nome em `props_hb_face_frame.get_style_props().cabinet_styles` → `style.get_finish_material()[0]`; frameless: `hb_project.get_main_scene().hb_frameless.cabinet_styles[CABINET_STYLE_INDEX (padrão 0)]` → `get_finish_material()[0]`; índice fora, estilo ausente, qualquer exceção → `None` | 🟢 |

### `engine.py`

| Símbolo | Contrato | Confiança |
|---|---|---|
| `cage_dims(obj)` | `GeoNodeObject(obj).get_input('Dim X'/'Dim Y'/'Dim Z')`; se exceção ou algum valor falso (0/None) → `obj.dimensions` (inclui escala) | 🟢 |
| `footprint_xy(obj)` | cantos locais `(0,0)`, `(w,0)`, `(0,−d)`, `(w,−d)` (fundo-esq, fundo-dir, frente-esq, frente-dir) × `matrix_world`, só XY | 🟢 |
| `top_z(obj)` / `bottom_z(obj)` | `translation.z + h` / `translation.z` (ignora inclinação e escala vertical) | 🟢 |
| `front_normal_xy(obj)` | `matrix_world.to_3x3() @ (0,−1,0)`, XY normalizado (se > 1e-6) | 🟢 |
| `members_touch(a, b, tolerance=0.02, align='top')` | RN-03; AABB testado com `min_a − tol > max_b` ou `min_b − tol > max_a` em X e Y | 🟢 |
| `connected_components(members, align)` | `remaining.pop()` (do fim) como semente; BFS com `queue.pop()`; ordem não determinada pelo usuário | 🟢 |
| `order_chain(component, align)` | RN-04 | 🟢 |
| `offset_polyline_right(points, offset)` | ver A-01 | 🟢 (sondado) |
| `offset_polygon_right(points, offset)` | ver A-02 | 🟢 (sondado) |
| `corner_plan_data(obj, corner)` | `w, d = cage_dims`; `ld = corner['ld'] or inch(24)`; `rd = corner['rd'] or inch(24)`; `left_front = (ld, −d)`; `right_front = (w, −rd)`; `front = [left_front, right_front]` se `diagonal`, senão `[left_front, (ld, −rd), right_front]`; `left_end = (left_front, (0, −d))`; `right_end = (right_front, (w, 0))` (pares frente, fundo) | 🟢 |
| `chain_sweep_points(chain, facts, face_offset, end_offset)` | ver A-04; `(pontos_mundo, cadeia)` ou `None` | 🟢 |
| `kick_sweep_segments(chain, facts, x_off, include_recessed)` | ver A-05; `[(pontos_mundo, cíclico)]` | 🟢 |

### `ops.py`

| Símbolo | Contrato | Confiança |
|---|---|---|
| `MOLDING_TAG`, `MOLDING_TYPE`, `MOLDING_MEMBERS` | `'IS_HB_MOLDING_SWEEP'`, `'HB_MOLDING_TYPE'`, `'HB_MOLDING_MEMBERS'` | 🟢 |
| `_TYPES` | `(('molding_crown_package','CROWN','top'), ('molding_base_package','BASE','bottom'), ('molding_light_rail_package','LIGHT_RAIL','bottom'))` | 🟢 |
| `clear_scene_molding(scene, molding_type=None)` | F-02 | 🟢 |
| `apply_scene_packages(scene) → int` | F-01; devolve o nº de sweeps criados | 🟢 |
| `on_package_changed(self, context)` | `apply_scene_packages(self.id_data)` dentro de `try/except Exception` → `print(f"CAFFMob Draw molding: apply failed: {ex}")` | 🟢 |
| `home_builder_OT_refresh_room_molding` | `bl_idname = "caffmob.refresh_room_molding"`, `bl_label = "Refresh Room Molding"`, `bl_options = {'UNDO'}`; `execute`: `made = apply_scene_packages(context.scene)`; `report({'INFO'}, tr("Rebuilt {} molding run(s)").format(made))`; `FINISHED` | 🟢 |
| `register()` / `unregister()` | por classe: `reg_cls = cls if cls.is_registered else getattr(bpy.types, cls.__name__, None)`; se houver, `unregister_class` (exceção engolida); `register` então `register_class(cls)` (exceção engolida) | 🟢 |

## Algoritmos

### A-01 — `offset_polyline_right(points, offset)` (aberto)

1. 🟢 Remove duplicatas consecutivas (distância ≤ 1e-6). Se restam < 2 pontos ou `|offset| < 1e-9`, devolve os pontos.
2. 🟢 Por segmento `a→b`: `d = normalizado(b − a)`, normal direita `n = (d.y, −d.x)`, linha deslocada `(a + n·offset, d, |b − a|)`.
3. 🟢 Saída começa no início da 1ª linha. Para cada par de linhas consecutivas: `cross = d1.x·d2.y − d1.y·d2.x`; se `|cross| < 1e-6` (paralelas) acrescenta o fim da 1ª (`p1 + d1·len1`) e o início da 2ª (`p2`); senão a interseção `p1 + d1·t`, `t = ((p2.x − p1.x)·d2.y − (p2.y − p1.y)·d2.x) / cross` (meia-esquadria, **sem limite de comprimento**).
4. 🟢 Acrescenta o fim da última linha; remove duplicatas consecutivas (1e-6). Pontas só deslocam perpendicularmente; tratamento de ponta é do chamador.
5. 🟢 Sonda (com `Vector` substituto): `[(0,0),(1,0),(1,1)]`, 0,1 → `[(0,−0,1),(1,1,−0,1),(1,1,1)]`; colinear `[(0,0),(1,0),(2,0)]` → `[(0,−0,1),(1,−0,1),(2,−0,1)]`; recuo em degrau `[(0,0),(1,0),(1,−0,05),(2,−0,05)]` → `[(0,−0,1),(0,9,−0,1),(0,9,−0,15),(2,−0,15)]`.

### A-02 — `offset_polygon_right(points, offset)` (fechado)

1. 🟢 Remove duplicatas consecutivas e o último ponto se igual ao primeiro; < 3 pontos ou `|offset| < 1e-9` → devolve os pontos.
2. 🟢 Linha deslocada por aresta `i → i+1 (mod n)`; vértice `i` = interseção da linha `i−1` com a linha `i` (paralelas → início da linha `i`). Inclui a costura.
3. 🟢 "Direita do percurso" é para fora só em laço anti-horário; em laço horário o offset encolhe (sonda: quadrado horário `(0,0)→(0,1)→(1,1)→(1,0)` com 0,1 → `(0,1,0,1)…(0,9,0,1)`). O perímetro de ilha percorre a frente no sentido `t = (−fn.y, fn.x)`, cuja direita é a normal frontal (para fora).

### A-03 — `_assemble_front_raw(chain, facts)`

Para cada membro `i` (`prev_ref` = último ponto acumulado; `next_ref` = centro do footprint do próximo):

1. 🟢 **Canto:** `corner_plan_data` → pontos da frente e das pontas no mundo. Inverte se `prev_ref` existe e está mais longe do 1º que do último ponto; sem `prev_ref`, inverte se `next_ref` está mais longe do último que do 1º. Entrada/saída = `left_end`/`right_end` (trocadas se invertido). Estende os pontos. Terminal 0 (se `i == 0`) = `{'obj', 'side': 'left'|'right' da entrada, 'back': canto traseiro da entrada}`; terminal 1 (se último) idem pela saída.
2. 🟢 **Reto:** `fl, fr, bl, br` (frente-esq `(0,−d)`, frente-dir `(w,−d)`, fundo-esq `(0,0)`, fundo-dir `(w,0)`). `left_first` = `|prev − fl| ≤ |prev − fr|`; sem `prev`, `|next − fr| ≤ |next − fl|`; sem ambos, `True`. O 1º membro reto com normal frontal não nula registra `first_straight = (índice do seu 1º ponto, normal)`. Estende 2 pontos de frente; terminais com o lado e o canto traseiro correspondentes.
3. 🟢 Devolve `(pontos, [terminal0, terminal1], first_straight)`.

### A-04 — `chain_sweep_points` (coroa, capa, light rail)

1. 🟢 Monta A-03. Se há `first_straight` e ≥ 2 pontos: `travel = normalizado(raw[idx+1] − raw[idx])`; se `(travel.y, −travel.x) · normal < 0`, inverte a cadeia e remonta (RN-05). Sem membro reto (só cantos) não há normalização (EC-07).
2. 🟢 < 2 pontos → `None`. `off = offset_polyline_right(raw, face_offset)`.
3. 🟢 Para cada extremidade com terminal: `outward` = `raw[0] − raw[1]` (início) ou `raw[−1] − raw[−2]` (fim), normalizado (ignora se ≤ 1e-6) — é o prolongamento da frente além da ponta. Se `finished_<side>` do terminal: a ponta de `off` avança `outward·end_offset` e é acrescentado (antes do início / depois do fim) `back + outward·end_offset`, gerando o retorno pela lateral até o fundo (RN-06).
4. 🟢 Devolve `(off, cadeia)` — a cadeia possivelmente invertida; `ops` usa essa cadeia para o pai e o Z.

### A-05 — `kick_sweep_segments` (rodapé)

1. 🟢 Normaliza o sentido como A-04 passo 1 (usando A-03).
2. 🟢 Se a cadeia não é vazia e **todos** os membros têm `parent is None`, tenta `_island_perimeter_spans`; se reconhecida (RN-10), devolve `_stretch_segments(perímetro, include_recessed, x_off, island=True)`.
3. 🟢 Senão `_assemble_kick_spans` (A-06) → vazio devolve `[]`; senão `_stretch_segments(…, facts, terminals, island=False)` (A-07).

### A-06 — Trechos por armário

1. 🟢 `_kick_spans_local(obj, f)` (local, esquerda→direita, `front = −d`): pontes ou `kick.skip` → `[([(0,front),(w,front)], 'SKIP')]`; `setback ≤ 1e-5` → `FRONT` igual; senão `r = front + setback`, `x0` = largura do montante esquerdo (se existe e > 1e-5, senão 0), `x1 = w −` largura do direito; trechos `[(0,front),(x0,front),(x0,r)] FRONT` (se montante esq.), `[(x0,r),(x1,r)] RECESS`, `[(x1,r),(x1,front),(w,front)] FRONT` (se montante dir.).
2. 🟢 `_assemble_kick_spans`: canto → frente de `corner_plan_data`; `skip` → `SKIP`; `setback > 1e-5` → `offset_polyline_right(frente, −setback)` (para dentro) e `RECESS` (sem montantes); reto → trechos de 1. Ambos para o mundo; inverte a lista e cada trecho quando `prev_ref` (último ponto acumulado) está mais perto do fim que do início (sem `prev_ref`, pelo centro do próximo). Terminais com `obj`, `side`, `front` e `back` (canto traseiro do lado de entrada/saída).

### A-07 — `_stretch_segments(spans, include_recessed, x_off, facts, terminals, island)`

1. 🟢 Mantidos = {`FRONT`, `RECESS`} se `include_recessed`, senão {`FRONT`}.
2. 🟢 Ilha com todos mantidos → concatena os pontos, `offset_polygon_right(x_off)`; ≥ 3 pontos → `[(laço, True)]`, senão `[]`.
3. 🟢 Ilha com descartes → a ordem de visita é girada para começar no 1º trecho descartado.
4. 🟢 Varredura: trecho mantido abre um segmento (se o anterior na ordem foi descartado, o segmento começa pelo **último ponto** dele) e estende pontos, guardando `start_idx`/`end_idx`; trecho descartado fecha o segmento aberto acrescentando seu **primeiro ponto**. No fim, ilha com o trecho da costura descartado acrescenta o 1º ponto dele.
5. 🟢 Cada segmento: `offset_polyline_right(x_off)`; < 2 pontos → descarta. Fora de ilha, nas extremidades da cadeia (`start_idx == 0`, `end_idx == n−1`) com terminal e ponta acabada: mesmo retorno de A-04 passo 3 com `x_off` como avanço. Saída `[(pontos, False)]`.

### A-08 — `_island_perimeter_spans(members, facts)`

1. 🟢 Algum membro de canto → `None`. Agrupa em fileiras por `round(rotation_euler_world.z, 2)`; > 2 fileiras → `None`; 2 fileiras com `|Δ| mod 2π` fora de `π ± 0,05` → `None`.
2. 🟢 Fileira: `t = (−fn.y, fn.x)` do 1º membro; ordena pelos centros projetados em `t`; trechos locais de cada membro no mundo, invertidos se o `+X` local do membro aponta contra `t`.
3. 🟢 Uma fileira: frente da fileira; lateral distante `[frente_extrema, fundo_extremo]` `FRONT`; fundo da fileira (cantos traseiros dos membros em ordem inversa, escolhendo o mais próximo do último ponto) `FRONT`; lateral próxima `FRONT`.
4. 🟢 Duas fileiras: frente A; ligação `[canto frontal extremo de A, canto frontal de B no mesmo extremo]` `FRONT`; frente B; ligação de volta `FRONT`. (Fundo e laterais são sempre `FRONT`, sem considerar pontas acabadas.)

## Fluxos Principais

### F-01 — `apply_scene_packages(scene)`

1. 🟢 `hb = scene.home_builder` (ausente → 0); cena com `IS_LAYOUT_VIEW`/`IS_DETAIL_VIEW` → 0 (RN-18).
2. 🟢 `clear_scene_molding(scene)` (todos os tipos).
3. 🟢 `opts`: `include_recessed`, `crown_reveal`, `stack_offset`, `cap_offset`, `crown_stack` (pilha do pacote de coroa ou `None`), `overrides` `{'Crown Molding', 'Spacer', 'Furniture Caps', 'Light Rail'}` → valor do enum ou `None` se `DEFAULT`/vazio. (`Base Molding` não entra: tratado em `_base_stack`.)
4. 🟢 Para cada `_TYPES` em ordem CROWN, BASE, LIGHT_RAIL: pilha do pacote (`None` com `NONE`); para `BASE`, `stack = _base_stack(hb, pilha or [])`; pilha vazia → pula; `made += _apply_type(...)`.
5. 🟢 Se `molding_crown_furniture_cap`: `made += _apply_type(scene, 'CAP', 'top', FURNITURE_CAP_STACK, opts)`.
6. 🟢 Devolve `made`.

### F-02 — `clear_scene_molding(scene, molding_type=None)`

🟢 Para cada objeto de `scene.objects` com `IS_HB_MOLDING_SWEEP` (e, se pedido, do tipo): marca o objeto e, se for `CURVE` com `bevel_object` que tem `IS_HB_MOLDING_PROFILE`, o perfil. Remove cada marcado com `bpy.data.objects.remove(do_unlink=True)` e, se o dado ficou com 0 usuários, `bpy.data.curves.remove(dado)`.

### F-03 — `_apply_type(scene, tipo, align, stack, opts)`

1. 🟢 `targets = collect_targets`; vazio → 0. `members = targets` + (só `BASE`) pontes não repetidas. `facts = build_facts`. `resolved = _resolve_stack(stack, opts)`.
2. 🟢 Para cada componente de `connected_components(members, align)` que contém algum alvo: `chain = order_chain`; para cada entrada resolvida: `BASE` → `kick_sweep_segments(chain, facts, dx, include_recessed)` com a cadeia original como dona; outros → `chain_sweep_points(chain, facts, dx, dx)` (mesmo `dx` para face e ponta) → `[(pts, False)]` e a cadeia devolvida como dona; sem segmentos → pula; `_spawn_sweep` não `None` → `made += 1`.

### F-04 — `_spawn_sweep(scene, tipo, chain, segments, ref, fb, dy, facts, opts)`

1. 🟢 `profile = make_profile_object(ref, fb, f"Molding_Profile_{fb}", scene.collection)`; `None` → `None`.
2. 🟢 Cria curva/objeto (ver Modelo de Dados), liga a `scene.collection`, grava as 3 idprops, `parent = chain[0]`, `location.z = _sweep_z(tipo, chain[0], dy, facts, opts)`, `profile.parent = sweep`.
3. 🟢 Para cada segmento: cada ponto mundial `(x, y, 0)` vai ao espaço local de `chain[0]` (`matrix_world.inverted()`); mantém `(lx, ly, 0)` se difere do anterior em X ou Y por > 1e-4; cíclico com > 2 pontos e 1º ≈ último (1e-4) remove o último; exige ≥ 3 (cíclico) ou ≥ 2 pontos; cria o spline.
4. 🟢 Nenhum spline → remove o objeto sweep e o perfil (os dados de curva ficam órfãos — EC-03) e devolve `None`.
5. 🟢 Material (RN-17); devolve o sweep.

### F-05 — `_resolve_stack(stack, opts)` e cotas

🟢 `front = 0`; por entrada: `STACK_OFFSET` → `opts['stack_offset']`; override da categoria → `"<categoria>/<override>"`; `STACK_FRONT` → `front`; acrescenta; `front = max(front, dx + profile_front_depth(ref, fb))`. `_crown_datum`, `_crown_stack_top` e `_sweep_z` conforme RN-11/RN-12 (o topo da pilha re-resolve a pilha de coroa com as mesmas `opts`).

### F-06 — Interação (consumidores)

🟢 `draw_molding_ui` (face frame › OPTIONS › Molding): caixas Crown (pacote; Reveal habilitado com pacote ≠ `NONE`; Stack Offset habilitado por `stack_has_adjustable_offset`; Profile/Spacer só com pack instalado e habilitados por `stack_uses_category`; Furniture Cap, Cap Offset e Cap Profile), Base (pacote; Profile com pack; Base Shoe; Include Recessed habilitado com pacote ou shoe), Light Rail (pacote; Profile com pack) e o botão `caffmob.refresh_room_molding` "Refresh Molding". 🟡 Essa UI só aparece com a biblioteca face frame visível — na barra lateral principal ela fica atrás da porta legado (`ui/sidebar_insert.py` + `legacy/gate.py`, D-28 da feature 012); `ui/view3d_sidebar.py:HOME_BUILDER_PT_product_library` e a aba GALERIA de `ui/panels.py` também desenham a biblioteca. _(Revisão 2026-10-10: a porta na barra lateral confirmada em `ui/sidebar_insert.py:23-24` (`gate.legacy_ui(context)`); os demais caminhos de UI não foram conferidos)_

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `hb_types.GeoNodeObject.get_input` | `Dim X/Y/Z` do cage e `Width` do `TOP_RAIL` | 🟢 |
| `units.inch` (reexporta `data/units.py:inch`) | defaults, contornos, canto padrão de 24" | 🟢 |
| `product_libraries/face_frame/props_hb_face_frame.get_style_props` + `cabinet_styles[].get_finish_material()` | material FF | 🟢 |
| `hb_project.get_main_scene().hb_frameless.cabinet_styles[].get_finish_material()` | material frameless | 🟢 |
| Props FF lidas: `face_frame_cabinet.{cabinet_type, corner_type, left_depth, right_depth, toe_kick_type, toe_kick_setback, extend_left/right_stile_to_floor, left/right_stile_width, left/right_finished_end_condition, default_top_overlay}` | fatos | 🟢 |
| idprops lidas: `IS_FACE_FRAME_CABINET_CAGE`, `IS_FRAMELESS_CABINET_CAGE`, `IS_FRAMELESS_PRODUCT_CAGE`, `CABINET_TYPE`, `IS_APPLIANCE`, `CLASS_NAME`, `hb_part_role`, `IS_WALL_BP`, `IS_CORNER_CABINET`, `Left Depth`, `Right Depth`, `CORNER_TYPE`, `Toe Kick Setback`, `STYLE_NAME`, `CABINET_STYLE_INDEX`, `IS_LAYOUT_VIEW`, `IS_DETAIL_VIEW` | fatos e filtros | 🟢 |
| `data.i18n.tr` + `data/translations/molding.json` | mensagem do operador | 🟢 |
| Packs de perfis externos | chamam `register_profile_path` no próprio `register()`; nenhum chamador no repositório | 🟢 (ausência) |

## Decisões de Design Identificadas

- 🟢 Fatos por adaptador, motor agnóstico (ADR 0005): novas bibliotecas exigem só um adaptador em `adapters.py`.
- 🟢 Reconstrução total em vez de atualização incremental: estado é só a cena; nenhuma identidade de moldura é guardada (`ops.py` docstring).
- 🟢 O menu **é** a interação: cada mudança de propriedade reaplica na hora (`hb_props.py:update_molding_package`).
- 🟢 Pacote = pilha de perfis com sentinelas `STACK_FRONT`/`STACK_OFFSET` para empilhar sem configuração por armário (`packages.py` docstring).
- 🟢 Geometria de perfil fora do add-on; contornos substitutos mantêm o recurso funcional (`packages.py` docstring).
- 🟢 Percurso em XY mundial, depois localizado no 1º membro; o Z vem só de `location.z` (pontos com Z = 0).
- 🟢 Caches de enum em nível de módulo porque o Blender guarda só referências fracas das strings de enums dinâmicos.

## Estado Interno

| Estado | Escopo | Ciclo de vida | Confiança |
|---|---|---|---|
| `packages._PROFILE_PATHS` | módulo | do `register_profile_path` do pack ao `unregister_profile_path`; não persistido | 🟢 |
| `packages._category_enum_cache`, `_profile_height_cache` | módulo | até o próximo (des)registro de pack; não veem arquivos novos na pasta (EC-10) | 🟢 |
| `packages._ENUM_CACHE` | módulo | fixo no import | 🟢 |
| `FACTS` | chamada | por `_apply_type` | 🟢 |
| Persistido no `.blend` | cena | sweeps, perfis, idprops, 14 props da sala | 🟢 |

## Observabilidade

- 🟢 `report INFO` do operador com o nº de sweeps; `print` no console quando o callback falha; sem log estruturado.

## Riscos e Lacunas

- 🔴 Nenhum teste automatizado da unit.
- 🟡 decisão: testar (DT-01) — **Decisão do titular (2026-10-10, questions.md#pergunta-64):** rodar um smoke visual no Blender 5.2 com 3 aéreos face frame, um canto em L e uma ilha (TT-03) e conferir por captura de tela o lado do perfil no bevel, retornos e meias-esquadrias; expectativa: lado correto (direita do percurso = fora), salvo EC-07/EC-08. Comportamento visual (lado do perfil no bevel, retornos, mitras) não validado nesta extração.
- 🟡 decisão: testar (DT-01, questions.md#pergunta-64) Pai com escala ou rotação fora de Z: pontos e Z ficam no espaço local do 1º membro e o perfil herda a escala (EC-08).
- 🔴 Perfil de pack que não é curva quebra métrica e/ou `bevel_object` (EC-04).
- 🟢 Mitras sem limite em ângulos agudos (EC-05); cadeia ramificada produz salto (EC-06). _(Revisão 2026-10-10: sonda no Blender — `offset_polyline_right([(0,0),(1,0),(0,0,1)], 0,1)` gera `(3,005, −0,1)`; `engine.py:order_chain` anexa os não alcançados ao fim)_
- 🟢 Moldura não acompanha mudanças dos armários (RN-19). _(Revisão 2026-10-10: `molding/` não registra handler de depsgraph; só `hb_props.py:update_molding_package` e o operador chamam `apply_scene_packages`)_

## Divergências com artefatos anteriores

| Artefato | Afirmação | Código | Confiança |
|---|---|---|---|
| `catalog_molding/legacy-mapping.md` | caminho `blendertomob/molding/`; botão `blendertomob.refresh_room_molding`; "13 props `molding_*`" | caminho `caffmob_draw/molding/`; `caffmob.refresh_room_molding`; 14 props (`hb_props.py:512-599`; a cópia da raiz `molding/ops.py` ainda usa `home_builder.refresh_room_molding`); números de linha de `ops.py` deslocados +1 (import de `tr`) | 🟢 |
| `modules.json` (molding) `dependencies` | inclui `product_libraries.frameless` | não importa o frameless; lê `hb_frameless` via `hb_project`; faltam `hb_project`, `units`, `data.i18n` | 🟢 |
| `code-analysis.md` §20 | "`offset_polygon` faz o fechamento" | nome real `offset_polygon_right` | 🟢 (detalhe) |
| `data-dictionary.md` §19 | "tipo — enum CROWN / CAP / BASE / LIGHT_RAIL" | `HB_MOLDING_TYPE` é idprop string livre; não há enum | 🟢 (detalhe) |
| `permissions.md` | molding "Criar/reconstruir malhas/curvas" | só curvas (sweep e perfil) | 🟢 (detalhe) |
| `ops.py` docstring | "rebuilds from the scene's three package props" | também capa e base shoe (interruptores) e 9 propriedades auxiliares | 🟢 |
| `hb_props.py:update_molding_package` docstring | "package dropdown (or the recessed-kick toggle)" | ligado às 14 propriedades | 🟢 |
