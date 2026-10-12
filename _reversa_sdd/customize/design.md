# Personalizar Módulo e Biblioteca do Usuário (customize) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/customize/` (15 arquivos, 3.028 linhas) em 2026-10-10, sem alterações sem commit na pasta. IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`; fluxos F-xx abaixo. 🟡 marca inferência; 🔴 lacuna. Contratos citados, não redescritos: `selection/classify` (`module_root(obj) → (raiz, biblioteca)`, `module_library(obj) → 'FRAMELESS'|'FACE_FRAME'|'CLOSETS'|'BTM'|None`) em `_reversa_sdd/selection/`; `hb_placement.PlacementMixin` (`init_placement`, `register_placement_object`, `update_snap` → `hit_location`, `cancel_placement`, `draw_header_text`, `clear_header_text`) em `_reversa_sdd/hb_placement/`; `hb_snap.snap_vector_to_grid`, `event_is_pass_through`; `library_common.world_box(objects)` (cantos avaliados de malhas visíveis; vazio → origem) e `library_common.thumbnail(context, objects, filepath)` (câmera ortográfica temporária, Workbench 256 × 256 transparente, erro `RuntimeError`/`OSError` só impresso, cena restaurada em `finally`); `cutting/part_roles.classify/base_name` em `_reversa_sdd/cutting/`; `cabinet_editor` (`scene_divisions`, `scene_extras`, `scene_interiors`, `scene_slides`, `structure`, `divisions.Box`, `btm_structure`) na feature 006/008; mecanismos das bibliotecas em `_reversa_sdd/frameless/`, `face_frame/`, `closets/`; `geometry/door_controller`, `geometry/mesh_gen` em `_reversa_sdd/geometry/`; `ui/sidebar_proxy` em `_reversa_sdd/ui/`.

## Visão de Camadas

| Camada | Arquivo (linhas) | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `spec.py` (191), `manifest.py` (149) | não (`dataclasses`, `json`, `re`, `..data.i18n`) | Domínio da personalização; manifesto do módulo salvo | 🟢 |
| Dados | `props.py` (76) | sim | `Object.btm_custom` (salvo no `.blend`) | 🟢 |
| Adaptadores | `adapters/__init__.py` (40), `common.py` (374), `frameless.py` (399), `face_frame.py` (318), `closets.py` (262), `btm.py` (203) | sim | Um por biblioteca + utilidades | 🟢 |
| Aplicação | `reapply.py` (80), `library_io.py` (262) | sim | Gancho pós-reconstrução; disco | 🟢 |
| Interface | `ops_customize.py` (263), `ops_library.py` (232), `panels.py` (154) | sim | 11 operadores; funções de desenho | 🟢 |
| Pacote | `__init__.py` (25) | não | `_modules()` importa tarde `ops_customize, ops_library, panels, props` e devolve `(props, ops_customize, ops_library, panels)`; `register` nessa ordem, `unregister` na inversa. `caffmob_draw/__init__.py` importa `customize`, chama `customize.register()`/`unregister()` e o põe em `_submodule_names` | 🟢 |

`reapply`, `library_io` e `adapters` não têm `register`. `panels.classes = ()`: as duas classes de painel não são registradas; a barra lateral única as desenha por `sidebar_proxy` (`ui/object_properties.py:337-341`, grupo `sel_customize` "Personalizar"; `ui/my_modules.py:23-24`). 🟢

## Interface

### `spec.py` 🟢 (puro)

| Símbolo | Valor / assinatura | Comportamento |
|---|---|---|
| `SECTIONS` | `('FRONTS', 'PULLS', 'MATERIALS', 'INTERIOR')` | Chaves de `capabilities` |
| `SECTION_LABELS` | `N_("Frentes")`, `N_("Puxadores")`, `N_("Materiais")`, `N_("Divisões internas")` | — |
| `FRONT_TYPES` | `('DOOR_LEFT', 'DOOR_RIGHT', 'DOUBLE_DOORS', 'DRAWERS', 'FLIP_UP', 'PANEL', 'OPEN')` | — |
| `FRONT_LABELS` | "Porta à esquerda", "Porta à direita", "Duas portas", "Gavetas", "Basculante", "Painel fixo", "Vazio" (`N_`) | — |
| `PULL_POSITIONS` | `('DEFAULT', 'TOP', 'MIDDLE', 'BOTTOM', 'SIDE')` | — |
| `NO_PULL` | `"__NONE__"` | Sem puxador |
| `GROUPS` / `GROUP_LABELS` | `('CAIXA', 'FRENTES', 'FUNDO', 'INTERNO')` / "Caixa", "Frentes", "Fundo", "Interno" (sem `N_`) | — |
| `MAX_DRAWERS`, `MAX_SHELVES`, `MAX_DIVIDERS` | `8`, `20`, `10` | RN-10 |
| `Interior` | `@dataclass`: `shelves=0`, `dividers=0`, `drawers=0`, `heights=[]` (m) | — |
| `Opening` | `@dataclass`: `path` (obrigatório), `front=""`, `drawer_count=0`, `door_style=""`, `drawer_style=""`, `pull_model=""`, `pull_position='DEFAULT'`, `front_material=""`, `interior=None` | — |
| `Spec` | `@dataclass`: `library=""`, `openings=[]`, `part_materials={}`, `group_materials={}`, `pull_all_fronts=""`, `aggregates=[]` | `opening(path)` (linear; `None`), `ensure_opening(path)` (cria e anexa), `is_empty()` |
| `to_dict(spec)` | → `dict` | `asdict`; remove a chave `interior` dos vãos onde é `None` |
| `from_dict(data)` | → `Spec` | `data or {}`; vãos: só campos conhecidos de `Opening`; `interior` só campos conhecidos de `Interior`, `heights` → `float`; `library`/`pull_all_fronts` → `str`; dicionários/listas copiados |
| `validate(spec)` | → `list[str]` | Por vão: `"vão sem caminho"`; `"vão {p}: repetido"`; frente fora de `FRONT_TYPES`; `DRAWERS` com `drawer_count` fora de 1..8; posição fora de `PULL_POSITIONS`; `validate_interior` prefixado `"vão {p}: "`. Grupos fora de `GROUPS`; material vazio/branco em grupo ou peça (`"material vazio em '{chave}'"`) |
| `validate_interior(interior, inner_height=None)` | → `list[str]` | "prateleiras fora de 0 a 20", "divisórias fora de 0 a 10", "gavetas internas fora de 0 a 8"; com alturas: quantidade ≠ `shelves`, não estritamente crescentes, `heights[0] ≤ 0` ou `heights[-1] ≥ inner_height` → "altura fora do vão" |
| `shelf_positions(count, inner_height, thickness, heights=None)` | → `list[float]` | `count ≤ 0` → `[]`; alturas dadas → elas; senão RN-10 |
| `group_of_component(component)` | → grupo | RN-13 |
| `interior_to_json(interior)` | → `str` | `json.dumps({"shelves", "dividers", "drawers", "heights"})` com `int`/`float` |
| `interior_from_json(text)` | → `Interior` ou `None` | Vazio ou JSON inválido → `None`; tipos não convertidos levantam (EC-09) |

### `manifest.py` 🟢 (puro)

| Símbolo | Valor / assinatura | Comportamento |
|---|---|---|
| `FORMAT`, `SCHEMA_VERSION`, `SUPPORTED_MAJOR` | `"caffmob_draw.user-module"`, `"1.1.0"`, `1` | — |
| `LIBRARIES`, `ROLES`, `MODES`, `ORIENTATIONS` | `('FRAMELESS','FACE_FRAME','CLOSETS','BTM')`, `('TOP','BOTTOM','BACK','LEFT','RIGHT')`, `('KEEP','EXTEND','SHRINK')`, `('VERTICAL','HORIZONTAL')` | — |
| `_SPACE`, `_FORBIDDEN` | `^s\d+(\.[ab])*$`, `[<>:"/\\|?*\x00-\x1f]` | — |
| `file_stem(name)` | → `str` | `_FORBIDDEN.sub("_", str(name)).strip().rstrip(".")` ou `"modulo"` |
| `build(name, category, library, root_object, spec, *, created="", addon_version="", dimensions_mm=None, styles=None, materials=(), pulls=(), structure=None, divisions=None)` | → `dict` | Chaves nesta ordem: `format`, `schema_version`, `name`, `category`, `library`, `root_object`, `created`, `addon_version`, `dimensions_mm`, `styles`, `materials` (ordenados, sem vazios/repetidos), `pulls` (idem, sem `NO_PULL`), `spec` (`to_dict`); `structure` só se não vazio: por papel ordenado `{removed, mode or 'KEEP', thickness_mm, material}`; `divisions` só se não vazio: `{uid, space, orientation, offset_mm, use_front, front_mm, use_back, back_mm, thickness_mm, material}` |
| `_mm(v)` / `_m(v)` | `round(float(v or 0)·1000, 3)` / `float(v or 0)/1000` | — |
| `structure_of(data)`, `divisions_of(data)` | → metros | Inversos de `build` (vazios na 1.0.0) |
| `validate(data)` | → `list[str]` | Não `dict` → `["o manifesto não é um objeto JSON"]`; formato; major (`int(str(v).split(".")[0])`, falha → `None`) `None` ou > 1; biblioteca; nome/raiz em branco. Sem erros: `spec.validate(from_dict(data.get("spec")))` + `_validate_structure` (papel desconhecido pula o resto da entrada; modo; `thickness_mm < 0`; `space` pela regex; orientação; negativos em `offset_mm`, `front_mm`, `back_mm`, `thickness_mm`) |
| `dumps(data)` | → `str` | `json.dumps(ensure_ascii=False, indent=2, sort_keys=False) + "\n"` |
| `loads(text)` | → `(dados, spec, erros)` | JSON inválido → `(None, None, ["JSON inválido: …"])`; com erros → `(dados, None, erros)`; senão `(dados, from_dict(spec), [])` |

### `props.py` 🟢

| Símbolo | Definição |
|---|---|
| `PULL_POSITION_ITEMS` | `DEFAULT` "Padrão", `TOP` "Topo", `MIDDLE` "Meio", `BOTTOM` "Base", `SIDE` "Lateral" (com descrições) |
| `GROUP_ITEMS` | `[(g, GROUP_LABELS[g], "") for g in GROUPS]` |
| `BTM_PG_GroupMaterial` | `group: EnumProperty(name="Grupo", items=GROUP_ITEMS)`; `material: StringProperty(name="Material")` |
| `BTM_PG_CustomSpec` | `door_style`, `drawer_style` (String, "Vazio = estilo do módulo"); `pull_model` (String, "vazio = puxador do projeto"); `pull_position: EnumProperty(items=PULL_POSITION_ITEMS, default='DEFAULT')`; `pull_all_fronts: BoolProperty(default=False)`; `front_material`; `material` ("Vence o material do grupo"); `group_materials: CollectionProperty(type=BTM_PG_GroupMaterial)`; `slide_kind` (String; `BLUM`, 008); `interior` (String JSON). Métodos `group_material(group)` → material ou `""`; `set_group_material(group, material)` atualiza a entrada existente ou cria |
| `register()` | Registra as duas classes; `bpy.types.Object.btm_custom = PointerProperty(type=BTM_PG_CustomSpec)` |
| `unregister()` | `del Object.btm_custom` se existir; desregistra as registradas em ordem inversa |

Sem `update` nos campos: gravar não reaplica nada; quem reaplica é o operador (F-01..F-05) ou o gancho (F-06). Anotações com `# type: ignore`. 🟢

### `reapply.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `_running` | `set` de nomes de raiz em reaplicação |
| `DIVISION_SIGNATURE` | `'btm_division_sig'` (= `cabinet_editor.scene_divisions.SIGNATURE_PROP`) |
| `has_structure(root)` | `btm_structure` com `components` ou `back_mode == 'RECESSED'`; ou idprop `btm_division_sig` na raiz; ou filho direto com `btm_extra.is_extra` |
| `has_custom(root)` | `has_structure`; ou raiz com `group_materials` ou `pull_all_fronts`; ou, na raiz e em `children_recursive`, algum de `door_style`, `drawer_style`, `pull_model`, `pull_position != 'DEFAULT'`, `front_material`, `material`, `interior` (não olha `slide_kind`) |
| `reapply(context, root)` | → avisos. `adapter = adapters.for_root(root)`; `None` ou `root.name in _running` → `[]`; senão marca, `adapter.reapply(context, root)`, desmarca em `finally` |
| `after_rebuild(context, obj)` | F-06 |

### `adapters/__init__.py` 🟢

`_adapters()` (import tardio) → `(frameless, face_frame, closets, btm)`. `module_root(obj)` = `classify.module_root(obj)[0]` (`None` com `obj None`). `for_root(root)` = adaptador cujo `LIBRARY == classify.module_library(root)`, ou `None`. `for_object(obj)` → `(raiz, adaptador)`.

Contrato obrigatório de cada adaptador: `LIBRARY`; `capabilities(root)`; `front_types(root)`; `openings(root)` → `[(caminho, objeto)]`; `read(root)` → `Spec`; `set_front(context, root, opening, front, drawer_count=1)` → mensagens; `set_interior(context, root, opening, interior)` → mensagens; `reapply(context, root)` → avisos; `style_names()`; `pull_items()` → `[(chave, rótulo)]`. Contrato opcional (006/008), chamado por `common.call`: `inner_spaces`, `structure_parts`, `structure_caps`, `remove_part`, `restore_part`, `set_part_thickness`, `reaffirm`, `structure_info`, `elevation_parts`, `opening_boxes`, `set_back_recess`. 🟢

### `adapters/common.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `NO_STYLE_REASON`, `NO_LIBRARY_REASON`, `NO_NEIGHBOR_REASON` | "A biblioteca não tem estilos de porta" (não usado pelos adaptadores atuais 🟢), "Esta biblioteca não tem estrutura editável", "Esta biblioteca não ajusta as chapas vizinhas; use Manter tudo" | _(Revisão 2026-10-10: `NO_STYLE_REASON` só aparece na própria definição, `common.py:10`)_
| `REMOVED_PROP`, `RAW_MATERIAL_PROP`, `_DRIVER_VAR` | `'btm_removed'`, `'btm_raw_material'`, `'btm_rm'` |
| `ordered(objs)` | RN-03 |
| `material(name, warnings)` | `""` → `None`; `bpy.data.materials.get`; ausente → aviso e `None` |
| `rotated(mat)` | `materials.get(mat.name + " ROTATED") or mat` |
| `gn_modifier(obj, base_name)` | Primeiro modificador `NODES` cujo `node_group.name.split(".")[0] == base_name` |
| `set_cutpart_material(obj, mat)` | F-09 |
| `part_group(obj, cabinet_type=None)` | RN-13 |
| `is_cutpart(obj)` | `MESH` com `GeoNodeCutpart` |
| `apply_group_materials(root, warnings, cabinet_type=None, parts=None)` | Para cada peça (padrão: `children_recursive` que são cutpart): `obj.btm_custom.material or grupos[part_group]`; se houver, `set_cutpart_material(obj, material(nome))` |
| `read_materials(root, target, parts)` | `target.group_materials` (só com material), `target.part_materials = {obj.name: material}` |
| `interior_of(opening)` | `interior_from_json(opening.btm_custom.interior)` |
| `unique(messages)` | `list(dict.fromkeys(...))` |
| `run_operator(context, op, obj, **kw)` | `context.temp_override(object=obj, active_object=obj, selected_objects=[obj])` → `op(**kw)` |
| `call(adapter, name, *args)` | `getattr(adapter, name, None) or globals()['default_' + name]` |
| `keep_only_caps(parts, thickness=None)` | `{papel: {'remove': None, 'thickness': thickness, 'modes': {'KEEP': None, 'EXTEND': motivo, 'SHRINK': motivo}}}` |
| `default_*` | `inner_spaces` → `{}`; `structure_parts` → `{}`; `structure_caps` → `{}`; `remove_part`/`restore_part`/`set_part_thickness` → `[NO_LIBRARY_REASON]`; `reaffirm` → `reaffirm_parts`; `structure_info` (papel → `size` (maior, menor) de `Length`/`Width` da primeira peça, `thickness`, `removed` = todas removidas); `elevation_parts` → `[]`; `opening_boxes` (F-13) |
| `local_box(root, obj, depsgraph)` | Caixa avaliada no referencial da raiz; `bound_box` todo nulo (< 1e‑9) → `None` |
| `clip_space(box, part_boxes)` | Recorta o vão pelas faces internas: `LEFT` sobe `lo.x` até `hi.x` da chapa, `RIGHT` desce `hi.x`, `BOTTOM` sobe `lo.z`, `TOP` desce `hi.z`, `BACK` desce `hi.y`; só chapas que cruzam o vão nos outros dois eixos (folga 1e‑6); resultado preso dentro do vão |
| `cage_spaces(context, root, adapter, tag)` | Jaulas `tag` em `children_recursive` → caixas locais, ordenadas por `(round(lo.x,4), round(lo.z,4))`; chapas de `structure_parts` não removidas e visíveis → `{"s<i>": clip_space(...)}` |
| `removed_roles(root)` | Papéis com `removed` em `btm_structure.components` |
| `set_removed(obj, removed)` | F-10 |
| `is_removed(obj)` | `bool(obj.get('btm_removed'))` |
| `cutpart_thickness(obj)` / `set_cutpart_thickness(obj, value, drop_driver=False)` | Input `Thickness` do `GeoNodeCutpart`; com `drop_driver`, remove antes o driver do caminho `compat.gn_input_data_path(mod, 'Thickness')` |
| `reaffirm_parts(context, root, adapter=None, drop_driver=False)` | Para cada entrada de `btm_structure.components` e cada peça do papel: `set_removed` se divergir; espessura > 0 e diferença > 1e‑7 → `set_cutpart_thickness`; `material` → idprop `btm_raw_material` (vazio apaga). Devolve `[]` |
| `parts_by_name(root, names)` | Filhos diretos cutpart cujo `part_roles.base_name(nome)` está em `names` |
| `set_back_recess(context, root, adapter, setback)` | Para cada peça `BACK`: direção −Y da raiz levada ao espaço do pai, normalizada; `delta_location = dir · setback`; `update_tag` |

### Adaptadores 🟢

| Item | frameless | face frame | closets | `btm` |
|---|---|---|---|---|
| `LIBRARY` | `'FRAMELESS'` | `'FACE_FRAME'` | `'CLOSETS'` | `'BTM'` |
| Vãos | `bay<i>/opening<j>` (RN-03) | `opening<i>` folhas | `opening<i>` todas | `"module"` = raiz |
| Leitura da frente | `leaf_opening` (desce pela primeira jaula filha): `IS_FLIP_UP_DOOR` → `FLIP_UP`; `'Door Swing'` 0/1/2 com porta → `DOOR_LEFT`/`DOOR_RIGHT`/`DOUBLE_DOORS` (outro → dupla); gavetas (`IS_DRAWER_FRONT`/`IS_PULLOUT_FRONT`) todas `False Front` → `PANEL`; gavetas → `DRAWERS`, n; nada → `OPEN` (ou `""` com `APPLIANCE_NAME`) | `face_frame_opening.front_type`: `DOOR` + `hinge_side` (`LEFT` → `DOOR_LEFT`, `RIGHT` → `DOOR_RIGHT`, `DOUBLE` → `DOUBLE_DOORS`, `TOP`/`BOTTOM` → `FLIP_UP`; outro → `DOOR_RIGHT`); `DRAWER_FRONT`/`PULLOUT`/`TILT_OUT` → `DRAWERS`, 1; `FALSE_FRONT`/`INSET_PANEL` → `PANEL`; `NONE` → `OPEN`; resto `""` | `hb_door_swing` `LEFT`/`RIGHT`/`DOUBLE`; `hb_drawer_qty` > 0 → `DRAWERS`, n; `hb_cubby_cols` → `""`; senão `OPEN` | `btm_cabinet.door_swing`: `LEFT`, `RIGHT`, `DOUBLE`, `FLIP` → `FLIP_UP`, `NONE` → `OPEN` |
| `read` estilos | `door_style` do vão ou `DOOR_STYLE_NAME` da primeira porta; `drawer_style` do vão | do vão ou idprops `hb_front_door_style`/`hb_front_drawer_style` | só do vão | não tem |
| `read` interior | `btm_custom.interior` ou `Interior(shelves=Shelf Quantity da jaula interior)` | pedido, ou soma de `interior_items` (`ADJUSTABLE_SHELF`/`GLASS_SHELF` → prateleiras, `ROLLOUT` → gavetas) | pedido ou `hb_adj_shelf_qty` | pedido ou `btm_cabinet.shelves` |
| `read` materiais / puxador geral | `read_materials` de todos os cutparts; `pull_all_fronts` = `root.pull_model` se a flag | idem | idem | só `group_materials`; `pull_all_fronts` não lido |
| `set_front` | F-02 | F-03 | `apply_opening_config(opening, cfg)` com `DOOR_LEFT`/`DOOR_RIGHT`/`DOOR_DOUBLE`/`DRAWERS_<1..8>` (falso → "A biblioteca recusou a troca da frente"); `OPEN` → `clear_opening_contents` + `recalculate_closet_starter`; outras → "O closets não tem a frente '{rótulo}'" | `door_swing = FRONT_TO_SWING[front]` (o `update` refaz malha e portas e chama `after_rebuild`); fora → "O módulo paramétrico não tem a frente '{rótulo}'" |
| `set_interior` | F-04 | F-05 | Valida; grava JSON; `hb_adj_shelf_qty` = n ou apagado; avisos para divisórias ("O closets não tem divisória vertical dentro do vão; use outro compartimento"), gavetas ("No closets as gavetas são frentes; troque a frente do vão para Gavetas"), alturas; `recalculate_closet_starter` | Valida (sem altura interna); grava JSON e `btm_cabinet.shelves`; avisos para divisórias/gavetas e para alturas |
| `style_names()` | `hb_frameless.door_styles` (ordem da coleção) | união ordenada de `door_styles` e `drawer_front_styles` | identificadores de `fronts_closets.FRONT_STYLES` | `[]` |
| `pull_items()` | `(filename, name)` de todas as categorias exceto `ALL`, sem repetição, por rótulo | `("<pasta>/<arquivo>", stem)` exceto `NONE`, por rótulo | `(arquivo, stem)` de `pulls_closets.get_pull_files()` | = frameless |
| `reapply` | F-07 | F-08 | F-08 (estilo por `apply_style_to_front(front, is_drawer, style=)` + `DOOR_STYLE_NAME`, só se `style in style_names()`) | F-11 |
| Estrutura (006) | Peças por nome `Left Side`/`Right Side`/`Bottom`/`Top`/`Back` (filhos diretos); `keep_only_caps` + `BOTTOM.EXTEND` com `Remove Bottom`; remover/restaurar por `set_removed` (ou `Remove Bottom`) + `run_calc_fix`; espessura > 0 tira o driver; 0 recria o driver `Thickness ← Material Thickness`; `reaffirm` com `drop_driver=True` | Peças por `hb_part_role` `LEFT_SIDE`/`RIGHT_SIDE`/`TOP`/`BOTTOM`/`BACK`; só `KEEP`; remover sem recálculo; restaurar e espessura 0 recalculam | Laterais = primeiro/último `CLOSET_PANEL` por `hb_panel_index`; `CLOSET_BOTTOM_SHELF`/`CLOSET_TOP_SHELF`/`CLOSET_APPLIED_BACK`/`CLOSET_CENTER_BACK`; só `KEEP`; restaurar e espessura 0 recalculam | Tudo em `btm_cabinet` (`has_*`, `mode_*`, `thickness_*`); três modos em todas; `SHRINK` muda medidas e `location` por `structure.shrink_change(role, espessura)`; `structure_parts` `{}`; `structure_info`/`elevation_parts`/`inner_spaces` por `cabinet_editor/structure.layout`; `reaffirm` `[]` |
| `inner_spaces` | `cage_spaces(..., BAY_TAG)` | `cage_spaces(..., TAG_BAY_CAGE)` | `cage_spaces(..., TAG_OPENING_CAGE)` | `{"s0": Box(inner)}` |
| `set_back_recess` | `common.set_back_recess` | idem | idem | `update_cabinet_geom(btm_cabinet, context)` |

Constantes: frameless `OPENING_TAG = 'IS_FRAMELESS_OPENING_CAGE'`, `BAY_TAG = 'IS_FRAMELESS_BAY_CAGE'`, `INTERIOR_TAG = 'IS_FRAMELESS_INTERIOR_CAGE'`, `FRONT_TO_TYPE = {DOOR_LEFT: LEFT_DOOR, DOOR_RIGHT: RIGHT_DOOR, DOUBLE_DOORS: DOUBLE_DOORS, FLIP_UP: FLIP_UP_DOOR, PANEL: FALSE_FRONT, OPEN: OPEN}`, `MAX_STACKED_DRAWERS = 4`, `ROLLOUT_SECTION_HEIGHT = 0.18`, `REMOVE_BOTTOM = 'Remove Bottom'`, `MATERIAL_THICKNESS = 'Material Thickness'`; face frame `FRONT_ROLES = (DOOR, DRAWER_FRONT, PULLOUT_FRONT, FALSE_FRONT, TILT_OUT, INSET_PANEL)`, `DRAWER_ROLES = (DRAWER_FRONT, PULLOUT_FRONT, TILT_OUT)`, `FRONT_TO_HINGE = {DOOR_LEFT: LEFT, DOOR_RIGHT: RIGHT, DOUBLE_DOORS: DOUBLE, FLIP_UP: TOP}`, `PULL_EDGE = 0.05`; closets `DOOR_ROLE = 'CLOSET_DOOR_FRONT'`, `DRAWER_ROLE = 'CLOSET_DRAWER_FRONT'`, `PULL_EDGE = 0.05`; `btm` `NO_STYLES`. 🟢

### `library_io.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `MODULES_DIR`, `GENERAL` | `"modules"`, `"Geral"` |
| `_package()` | `__package__` sem o sufixo `.customize` |
| `modules_root()` | `bpy.utils.extension_path_user(_package(), path="modules", create=True)` |
| `paths_for(name, category)` | `{ext: <raiz>/<file_stem(category or "Geral")>/<file_stem(name)>.<ext>}` para `blend`, `png`, `json` |
| `exists(name, category)` | `.blend` existe |
| `list_modules()` | Categorias (pastas) e `.blend` em ordem alfabética; entrada `{name: stem, category, blend, png, json, has_manifest}`; com `.json` válido, `name` = nome do manifesto (inválido: mantém o stem). Exceções de leitura propagam |
| `_tree(root)`, `_data_blocks(objects)` | Raiz + descendentes; blocos = objetos, `obj.data`, materiais dos dados (+ imagens de nós `TEX_IMAGE`), grupos de nós dos modificadores `NODES` |
| `_addon_version()` | `bl_info["version"]` do módulo do add-on em `addon_utils.modules()` unido por "."; falha → `""` |
| `build_manifest(root, name, category)` | `current = adapter.read(root)`; `world_box(_tree)` → `dimensions_mm = {width: round(Δx·1000), height: round(Δz·1000), depth: round(Δy·1000)}`; `door_styles` = união ordenada de `door_style` e `drawer_style` dos vãos; materiais = frentes + grupos + peças; puxadores = dos vãos + `pull_all_fronts`; `current.aggregates = [{name, parent_path: nome do pai, kind}]` dos descendentes com `btm_aggregate.is_aggregate`; `created` = agora com fuso, ISO em segundos; `structure = btm_structure.to_dict()`; `divisions = scene_divisions.read(root)` |
| `save(context, root, name, category, thumbnail=True)` | F-14 |
| `_geo_node_refs(objects)` | Objetos ligados a inputs `NodeSocketObject` dos modificadores `NODES` (via `compat.try_get_gn_input_by_id`) |
| `_missing_styles(data)` | `styles.door_styles` menos os existentes: frameless `hb_frameless.door_styles`; face frame `door_styles` ∪ `drawer_front_styles`; outras bibliotecas: conjunto vazio (EC-02) |
| `load(context, entry)` | F-15 |
| `_renew_divisions(context, root)` | `btm_division.uid = divisions.new_uid()` em cada divisão; `scene_divisions.reflow(context, root, force=True)` |
| `delete(entry)` | Remove os três arquivos que existirem |
| `rename(entry, new_name)` | Alvo na mesma categoria; `.blend` alvo existe → `["Já existe um módulo '{}' nessa categoria"]`; `os.replace` dos três que existirem; manifesto válido regravado com `name` novo (`root_object` não muda) |

### `ops_customize.py` 🟢

| `bl_idname` | Rótulo | `bl_options` | Propriedades | Comportamento |
|---|---|---|---|---|
| `caffmob.customize_set_front` | Trocar frente | `REGISTER`, `UNDO` | `path` (oculto), `front` (enum dinâmico `_front_items`), `drawer_count` 1–8 (padrão 1) | `invoke`: `DRAWERS` → `invoke_props_dialog`; senão `execute`. `execute`: F-01 com `adapter.set_front` + `reapply.reapply`; "Frente trocada para {rótulo}" |
| `caffmob.customize_set_style` | Estilo da frente | idem | `path`, `kind` `DOOR`/`DRAWER` (padrão `DOOR`), `style` (enum `_style_items`: `""` "Estilo do módulo" + nomes) | Grava `door_style` ou `drawer_style` do vão; `reapply`; "Estilo aplicado: {nome ou "do módulo"}" |
| `caffmob.customize_set_pull` | Puxador | idem | `path`, `model` (enum `_pull_items`: `""` "Puxador do projeto", `NO_PULL` "Sem puxador", `pull_items`), `position` (`PULL_POSITION_ITEMS`), `all_fronts` | `invoke` pré-preenche `position` do vão e `all_fronts` da raiz; diálogo. `execute`: `root.pull_all_fronts = all_fronts`; com todas: `root.pull_model = model` e `pull_position` em todos os vãos; senão `pull_model`/`pull_position` do vão; `reapply`; "Puxador atualizado" |
| `caffmob.customize_set_material` | Material | idem | `target` `FRONTS`/`GROUP`/`PART`, `path`, `group`, `material` | `poll`: há adaptador. Diálogo com `prop_search` em `bpy.data.materials`. `FRONTS` → `front_material` do vão (vão ausente → `CANCELLED` sem mensagem); `GROUP` → `set_group_material`; `PART` → `active_object.btm_custom.material`; `reapply`; "Material: {nome ou "da biblioteca"}" |
| `caffmob.customize_set_interior` | Divisões internas | idem | `path`, `shelves` 0–20, `dividers` 0–10, `drawers` 0–8, `heights` (texto) | `invoke` pré-preenche de `adapter.read(root).opening(path).interior` e formata alturas com `units.format_length` na unidade da cena unidas por "; ". `execute`: `units.parse_length(parte, default_unit=unidade)` por parte não vazia (`ValueError` → "Alturas inválidas", `CANCELLED`); `adapter.set_interior`; **só sem mensagens** `reapply`; "Divisões internas atualizadas" |
| `caffmob.customize_clear` | Limpar personalização do vão | idem | `path` | RN-19 |

`_OpeningOperator` (mixin): `bl_options = {'REGISTER', 'UNDO'}`, `path` oculto, `poll` = adaptador com `openings`, `resolve(context)` → `(raiz, adaptador, objeto do vão)` ou aviso "Vão não encontrado; selecione o módulo de novo". `_target(context)` = `adapters.for_object(context.active_object)`. `_report(op, mensagens, ok)` → `WARNING` com " | " ou `INFO`. `_ENUM_CACHE` guarda as listas dos enums dinâmicos. 🟢

### `ops_library.py` 🟢

| `bl_idname` | Rótulo | `bl_options` | Propriedades | Comportamento |
|---|---|---|---|---|
| `caffmob.module_save` | Salvar como módulo | `REGISTER` | `module_name`, `category` ("Geral"), `overwrite` (False), `thumbnail` (True) | `poll`: há adaptador. `invoke`: nome = nome da raiz, `overwrite = False`, diálogo 360 px; `draw` mostra caixa de alerta "Já existe um módulo com esse nome nesta categoria." + `overwrite` quando existe. `execute`: nome vazio → ERROR; existe sem `overwrite` → WARNING, `CANCELLED`; `library_io.save(..., category.strip(), thumbnail)`; erro → ERROR; senão INFO "Módulo salvo: {blend}" e redesenha áreas |
| `caffmob.module_insert` | Inserir módulo | `REGISTER`, `UNDO` | `filepath` (oculto), `place` (oculto, `SKIP_SAVE`, padrão True) | Herda `PlacementMixin`. F-16 |
| `caffmob.module_delete` | Apagar módulo | — | `filepath` | `invoke_confirm(title="Apagar módulo da biblioteca?", confirm_text="Apagar", icon='WARNING')`; entrada ausente → ERROR "Módulo não encontrado"; `delete`; INFO; redesenha |
| `caffmob.module_rename` | Renomear módulo | — | `filepath`, `new_name` | Diálogo com o nome atual; entrada ausente ou nome vazio → ERROR "Módulo ou nome inválido"; erros de `rename` → WARNING, `CANCELLED` |
| `caffmob.module_open_folder` | Abrir pasta dos módulos | — | — | `os.startfile` (Windows), `open` (Darwin), `xdg-open` (outros) com `modules_root()` |

`_entry(filepath)` busca em `list_modules()` a entrada com `blend == filepath`. 🟢

### `panels.py` 🟢

`_section(layout, caps, section)`: caixa com o rótulo; motivo → linha desabilitada com ícone `INFO` e devolve `None`. `_opening_label(item)`: rótulo da frente ou "—"; `DRAWERS` com n > 1 → "{n} gavetas". `draw_customize(layout, context)` e `draw_library(layout, context)` descritos em CA-01, CA-02 e RF-11 (biblioteca: "Abrir pasta"; erro `OSError`/`ValueError` → "Biblioteca indisponível: {erro}"; vazia → "Nenhum módulo salvo ainda."; rótulo de categoria quando muda; por entrada: inserir (sem manifesto: "{nome} (sem personalização)"), renomear, apagar). `BTM_PT_CustomizeModule` (`BTM_PT_customize_module`, "Modelos — Personalizar módulo", poll = há adaptador) e `BTM_PT_ModuleLibrary` (`BTM_PT_module_library`, "Biblioteca de módulos"), ambos `VIEW_3D`/`UI`/"CAFFMob Draw", pai `BTM_PT_object_properties`, `DEFAULT_CLOSED`, **não registrados**. 🟢

## Fluxos

### F-01 Operador de vão (frente, estilo, puxador, material, interior) 🟢

1. `_target` → `(raiz, adaptador)`; `resolve` acha o objeto do vão pelo `path` em `adapter.openings(raiz)`; ausente → aviso e `CANCELLED`.
2. Grava o pedido em `btm_custom` (estilo, puxador, material) ou chama a mudança estrutural do adaptador (`set_front`, `set_interior`).
3. `reapply.reapply(context, raiz)` (sem reafirmar estrutura; isso só ocorre em F-06 quando a biblioteca reconstrói).
4. `_report`; `FINISHED` (o passo de desfazer cobre tudo).

### F-02 `frameless.set_front` 🟢

1. `DRAWERS` com n > 1: pai do vão sem `BAY_TAG` → mensagem RN-09. Senão `count = min(n, 4)`; preset `'SINGLE_DRAWER'` (n = 1) ou `f"{count}_DRAWER_STACK"`; `run_operator(caffmob_frameless.change_bay_opening, pai, opening_type=preset)`; sem `FINISHED` → "A biblioteca recusou a troca das gavetas"; n > 4 → aviso de teto.
2. Senão `opening_type = 'SINGLE_DRAWER'` para `DRAWERS`, ou `FRONT_TO_TYPE[front]`; ausente → "Frente '{}' não suportada"; `run_operator(caffmob_frameless.change_opening_type, vão, opening_type=…)`; sem `FINISHED` → "A biblioteca recusou a troca da frente".

### F-03 `face_frame.set_front` 🟢

`DRAWERS` com n > 1: `count = min(n, 8)`; torna o vão ativo, `temp_override(active_object=vão, object=vão)`, `caffmob_face_frame.split_opening('EXEC_DEFAULT', axis='H', count=count, front_type_<i>='DRAWER_FRONT')`, restaura o ativo; sem `FINISHED` → "A biblioteca recusou dividir o vão em gavetas". Senão grava `hinge_side`/`front_type` (`DOOR`, `DRAWER_FRONT`, `FALSE_FRONT`, `NONE`) e `recalculate_face_frame_cabinet(root)`.

### F-04 `frameless.set_interior` 🟢

1. `leaf = leaf_opening(vão)`; `height = GeoNodeCage(leaf).get_input('Dim Z')`; `validate_interior(interior, height)` → erro devolve.
2. Grava `btm_custom.interior` no vão estável; apaga recursivamente as jaulas `INTERIOR_TAG` filhas da folha.
3. Precedência: `drawers` → `InteriorSplitterVertical` com 1 divisor, `section_sizes = [0, min(0.8·H, 0.18·n)]`, tipos `['SHELVES' se prateleiras senão 'EMPTY', 'ROLLOUTS']`, `rollout_qty = n`; senão `dividers` → `InteriorSplitterHorizontal` com n divisores e n+1 seções; senão `heights` → `InteriorSplitterVertical` com `len(heights)` divisores, `tops = [H] + alturas invertidas`, `bottoms = [h + t para alturas invertidas] + [0]` (`t = default_carcass_part_thickness`), tamanhos `max(0.001, top − bottom)`, último = 0 (resto), todas `EMPTY`; senão `shelves` → `CabinetShelves.create('Interior')` com `Shelf Quantity`.
4. `_attach`: pai = folha; drivers `Dim X/Y/Z` ligados aos da folha. `hb_utils.run_calc_fix_until_stable(context, root)`; devolve `[]`.

### F-05 `face_frame.set_interior` 🟢

Valida (sem altura); alturas → aviso; grava JSON; remove itens `ADJUSTABLE_SHELF`/`GLASS_SHELF`/`ROLLOUT`; adiciona `ADJUSTABLE_SHELF` (`unlock_shelf_qty`, `shelf_qty`) e `ROLLOUT` (`unlock_qty`, `qty`); divisórias: com nó `TAG_INTERIOR_SPLIT_NODE`/`TAG_INTERIOR_REGION` filho → "Este vão já tem divisões; edite-as pela ferramenta do face frame"; senão `add_interior_division(target_name=vão)` (recusa → aviso; n > 1 → "O face frame cria uma divisória por vez…"); `recalculate_face_frame_cabinet`.

### F-06 `after_rebuild(context, obj)` 🟢

1. `root = adapters.module_root(obj)`; `None`, sem `btm_custom` ou `not has_custom(root)` → `[]`.
2. `messages = reapply(context, root)`.
3. Se `has_structure(root)` e raiz livre de `_running`: marca; `common.call(adapter, 'reaffirm', …)`; se `btm_structure.auto_back` e `back_mode == 'RECESSED'` → `call(adapter, 'set_back_recess', context, root, back_setback)`; `scene_divisions.reflow`, `scene_extras.sync`, `scene_interiors.reflow`, `scene_slides.reflow`; desmarca em `finally`.
4. Devolve `messages`.

Chamadores: `data/properties.update_cabinet_geom` (`btm`); frameless `props_hb_frameless.py:803`, `ops_styles.py:883-885` (por gabinete após aplicar estilo), `ops_opening.py:1095`; face frame `types_face_frame.py:8774` (fim de `recalculate_face_frame_cabinet`); closets `types_closets.py:1936` (fim de `recalculate_closet_starter`). 🟢 _(Revisão cruzada 2026-10-10: as linhas antes citadas (802, 1094, 8773, 1935) são o `import` de `reapply`; a chamada `after_rebuild` está na linha seguinte)_

### F-07 `frameless.reapply` 🟢

`apply_group_materials(root, w, CABINET_TYPE)`. Por vão: `model` (RN-06); `mat = material(front_material)`; por frente (`IS_CABINET_FRONT` em `children_recursive`): estilo (`door_style` em porta `IS_DOOR_FRONT`, senão `drawer_style`) → `_apply_style` (`door_styles.find(nome)`; < 0 → aviso; `assign_style_to_front(front)`; grava `DOOR_STYLE_INDEX`/`DOOR_STYLE_NAME`; retorno `str` → aviso "{frente}: {texto}"); modelo ou posição ≠ `DEFAULT` → `_apply_pull` (objeto do puxador por idprop `btm_pull_file` ou `load_pull_object`; `NO_PULL` → `Object` = `None` em cada `GeoNodeHardware`; com objeto → `Object` = objeto e `Pull Length = dimensions.x`; posição por `_set_pull_position` com `Length` da frente); `mat` e frente sem material próprio → `set_cutpart_material`. Pedido de interior com `shelves` e jaula com `Shelf Quantity` → reafirma. `run_calc_fix(context, root)`; `unique(w)`.

`_set_pull_position`: `DEFAULT` nada. Gaveta: `Center Pull = (MIDDLE)`; `BOTTOM` → `Handle Horizontal Location = max(0, L − pl − 0.05)`; `TOP` → `= hb_frameless.pull_vertical_location_drawers`. Porta: `Pull Location` `TOP` 0, `MIDDLE` 1 (+ `Tall Pull Vertical Location = max(0, L/2 − pl/2)`), `BOTTOM` 2. `SIDE` não muda nada. 🟢

### F-08 `reapply` do face frame e closets 🟢

`apply_group_materials(root, w)`; por vão e frente: estilo (gaveta pelo papel) — face frame só se `DOOR_STYLE_NAME != estilo`, pool de gaveta ou porta, `assign_style_to_front(front, record_override=True)`; closets só se o identificador existe. Puxador: `NO_PULL` → remove os objetos de puxador da frente; com modelo → `pull.data = objeto.data` (closets também `hb_pull_name`); posição: face frame em `location.x` com `L = Length` do cutpart: `TOP` `L − 0.05 − e`, `BOTTOM` `0.05 + e`, `MIDDLE` `L/2` (`e = 0` se o puxador está girado 90° em Z, senão meio comprimento); closets em `location.y` com `h = Width`: `TOP` `h − 0.05 − meio`, `BOTTOM` `0.05 + meio`, `MIDDLE` `h/2`. Material das frentes como em F-07. Sem recálculo no fim. Objeto do puxador: chave `"<pasta>/<arquivo>"` (face frame) ou `"closets/<arquivo>"` (closets, que também zera `pulls_closets._pull_cache['selection'/'object']`). 🟢

### F-09 `set_cutpart_material(obj, mat)` 🟢

`mat None` → `False`. Sem `GeoNodeCutpart`: não malha → `False`; senão garante 1 slot e põe `mat` em todos. Com: `Top Surface` e `Bottom Surface` = `mat`; modificador desligado na viewport e malha com slots → todos os slots = `mat` (porta 5 peças do face frame); demais modificadores `NODES` com os sockets `Material`, `Stile Material`, `Panel Material` → `mat`, `Rail Material` → `rotated(mat)`. `True`.

### F-10 `set_removed(obj, removed)` 🟢

Idprop `btm_removed = removed`. Para `hide_viewport` e `hide_render`: sem driver e `removed` falso → pula; sem driver → cria com expressão `btm_rm`; sem variável `btm_rm` → cria `SINGLE_PROP` lendo `["btm_removed"]` do próprio objeto e, se a expressão não é `btm_rm`, vira `"(<expr>) or btm_rm"`; ao restaurar, driver com expressão exatamente `btm_rm` é removido. Restaurado e sem driver → `hide_* = False`. `update_tag()`.

### F-11 `btm.reapply` 🟢

`_carcass_materials`: com grupos, slots 0..2 garantidos e `MAT_CARCASS` = `CAIXA`, `MAT_SHELF` = `INTERNO` ou caixa, `MAT_BACK` = `FUNDO` ou caixa (só os não nulos). `front_mat = material(front_material or grupo FRENTES)`. Puxador: `pull_model` real → `frameless._pull_object`. Por porta de `door_controller.doors_of(root)`: se `NO_PULL` ou há objeto → `set_door_pull(root, porta, objeto ou None, pull_position, comprimento = dimensions.x ou 0.1)` (`TOP`/`BOTTOM` a 50 mm da borda; resto no meio da altura; basculante: centro em X); `set_door_material(porta, front_mat)` (no-op com `None`).

### F-12 `btm` estrutura (`_shrink`) 🟢

`remove_part`: já ausente → `[]`; grava `mode_<papel>`, `has_<papel> = False`; `SHRINK` → `_shrink(+1)`: espessura = `thickness_<papel>` ou `thickness`; `delta, shift = structure.shrink_change(papel, esp)`; soma `sinal·delta` nos campos e `location += matrix_basis.to_3x3() @ (shift·sinal)`. `restore_part` desfaz com −1 se o modo era `SHRINK`, `has = True`, `mode = 'KEEP'`.

### F-13 `default_opening_boxes` 🟢

Para cada vão de `openings`: vão = raiz → primeiro (menor chave) de `inner_spaces`; senão `local_box` do vão → `Box`. Consumido por `cabinet_editor/ops_editor.py:146` e `bridge.py:572`.

### F-14 `library_io.save` 🟢

1. Sem adaptador → `(None, ["O objeto selecionado não é um módulo"])`.
2. `paths_for`; `makedirs(exist_ok=True)`; `build_manifest`.
3. `mkstemp(".blend", dir=pasta)`; `bpy.data.libraries.write(tmp, _data_blocks(_tree(root)), path_remap='RELATIVE_ALL', fake_user=True)`.
4. `mkstemp(".json")` com `dumps(data)` em UTF-8.
5. `os.replace(tmp_blend → .blend)`, `os.replace(tmp_json → .json)`.
6. `OSError`/`RuntimeError` em 2..5 → apaga temporários e devolve `(None, ["Não foi possível gravar o módulo em {pasta}: {erro}"])`.
7. Com `thumbnail` → `library_common.thumbnail(context, _tree(root), .png)` (falha não vira erro). Devolve `(caminhos, [])`.

### F-15 `library_io.load` 🟢

1. Com `has_manifest`: `loads(texto)`; erros → `(None, [], ["Manifesto inválido: " + "; ".join(erros)])`.
2. `bpy.data.libraries.load(blend, link=False)` com **todos** os objetos; liga cada um a `context.scene.collection`.
3. `roots` = carregados sem pai com `module_library`; raiz = o primeiro.
4. Objetos de `_geo_node_refs(carregados)` → `hide_set(True)`, `hide_viewport`, `hide_render`.
5. Com manifesto: `missing = _missing_styles(data)` → aviso "Estilos ausentes neste arquivo (mantida a geometria salva): {lista}".
6. Raiz e manifesto → `+= reapply.reapply(context, raiz)` (lê `btm_custom` do `.blend`; o `spec` do manifesto não é usado).
7. Raiz → `_renew_divisions`; sem raiz → "Nenhum módulo encontrado no arquivo".
8. `if missing:` remove os avisos que começam com o prefixo traduzido de "Estilo '{}' não existe neste arquivo" (sem manifesto, `missing` não existe: EC-01).
9. Devolve `(raiz, carregados, unique(avisos))`.

### F-16 Inserir módulo (`BTM_OT_ModuleInsert`) 🟢

`execute`: `_entry(filepath)` ausente ou arquivo inexistente → ERROR, `CANCELLED`. `init_placement`; `load`; registra objetos sem pai como objetos de colocação. Sem raiz: remove os carregados ainda existentes, zera `placement_objects`, WARNING, `CANCELLED`. Avisos → WARNING. `others = {obj: obj.location − raiz.location}` dos sem pai, não raiz, visíveis. Desmarca a seleção; raiz selecionada e ativa. `place` falso ou sem área → zera `placement_objects`, `FINISHED`. Senão cabeçalho "Clique para posicionar  |  R: girar 90°  |  Botão direito/Esc: cancelar", cursor `CROSSHAIR`, `modal_handler_add`, `RUNNING_MODAL`.

`modal`: `tag_redraw`; `INBETWEEN_MOUSEMOVE` → continua. Esconde raiz, descendentes e `others` visíveis (`hide_set`), `update_snap`, mostra de novo. Com `hit_location`: `p = snap_vector_to_grid(hit)`; raiz em `p`; `others` em `p + offset`. `LEFTMOUSE PRESS` → limpa cabeçalho, cursor `DEFAULT`, `FINISHED`. `R PRESS` → `raiz.rotation_euler.z += 90°`. `RIGHTMOUSE`/`ESC PRESS` → `cancel_placement`, limpa, `CANCELLED`. `event_is_pass_through` → `PASS_THROUGH`; senão `RUNNING_MODAL`.

## Máquina de Estados da Inserção 🟢

| De | Evento | Para | Efeito |
|---|---|---|---|
| — | `execute` sem entrada/arquivo, manifesto inválido ou sem raiz | `CANCELLED` | Objetos carregados removidos |
| — | `execute` com `place=False` ou sem área | `FINISHED` | Fica onde foi salvo |
| — | `execute` normal | `RUNNING_MODAL` | Handler modal, cabeçalho, cursor |
| `RUNNING_MODAL` | movimento | `RUNNING_MODAL` | Raiz no raycast com snap à grade |
| `RUNNING_MODAL` | `R` | `RUNNING_MODAL` | +90° no Z da raiz |
| `RUNNING_MODAL` | clique esquerdo | `FINISHED` | Posição mantida (um passo de desfazer) |
| `RUNNING_MODAL` | Esc / botão direito | `CANCELLED` | `cancel_placement` |

A personalização em si não tem estados: é um conjunto de pedidos (`btm_custom`) reaplicados de forma idempotente. 🟢

## Dependências

`selection/classify`, `cutting/part_roles`, `compat`, `data/i18n`, `data/units`, `data/properties` (`structure_of`, `back_setback_of`, `update_cabinet_geom`), `library_common`, `hb_placement`, `hb_snap`, `hb_project` (`get_main_scene`), `hb_types` (`GeoNodeCage`, `GeoNodeObject`), `hb_utils` (`run_calc_fix`, `run_calc_fix_until_stable`), `geometry/door_controller`, `geometry/mesh_gen` (`MAT_BACK`, `MAT_CARCASS`, `MAT_SHELF`), `cabinet_editor` (`scene_divisions`, `scene_extras`, `scene_interiors`, `scene_slides`, `structure`, `divisions`), bibliotecas `frameless` (`types_frameless`, `props_hb_frameless`, operadores `caffmob_frameless.change_opening_type`/`change_bay_opening`), `face_frame` (`types_face_frame`, `pulls`, operadores `caffmob_face_frame.split_opening`/`add_interior_division`), `closets` (`types_closets`, `fronts_closets`, `pulls_closets`); `addon_utils` (opcional). 🟢

### Consumidores 🟢

| Consumidor | Usa |
|---|---|
| `caffmob_draw/__init__.py` | `register`/`unregister` |
| `data/properties.py:81` | `reapply.after_rebuild` _(Revisão cruzada 2026-10-10: linha 80 é o import; chamada na 81)_ |
| Bibliotecas (5 pontos) | `reapply.after_rebuild` (F-06) |
| `cabinet_editor/bridge.py` | `adapters`, `spec.to_dict/from_dict`, `adapter.openings/read/set_front/set_interior`, `reapply.reapply`, `common.call` (estrutura, `opening_boxes`, `elevation_parts`, `set_back_recess`) |
| `cabinet_editor/ops_actions.py` | `spec`, `PULL_POSITION_ITEMS`, `front_types`, `style_names`, `pull_items`, `capabilities` | _(Revisão 2026-10-10: `panels_drawers.py` e `cabinet_editor/panels.py` não importam `customize`; `ops_actions.py:13-14,314` importa `spec`, `PULL_POSITION_ITEMS` e `common`)_
| `cabinet_editor/scene_divisions.py`, `scene_parts.py`, `ops_editor.py`, `reflow_handler.py` | `adapters.for_root/module_root`, `common.call`, `local_box` |
| `legacy/convert.py` | `adapter.read` |
| `legacy/groups.py` | `library_io.save`, `list_modules`, `modules_root` |
| `move_over/ops_substitute.py` | `library_io.list_modules`, `load` |
| `library_panel/popover.py`, `categories.py` | `library_io.list_modules`, `modules_root` |
| `object_library/item_io.py`, `retexture.py` | `library_io._addon_version`; `common` |
| `cutting/drilling.py` | `common` |
| `ui/object_properties.py`, `ui/my_modules.py`, `ui/context_menu.py` | `BTM_PT_CustomizeModule`/`draw_customize`, `draw_library`, `adapters.for_object` |

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Um adaptador por biblioteca, sem tocar o motor delas (`set_front` e interior pela própria biblioteca) | 003 D-02, D-05; ADR 0005 | 🟢 |
| Pedido gravado no vão (que sobrevive) e reaplicado por gancho, em vez de impedir a reconstrução | 003 D-03, D-04; `reapply.py` | 🟢 |
| Por nome, não índice | 003 RN-06; `common.material`, `_apply_style` | 🟢 |
| `.blend` como fonte da verdade; manifesto como cabeçalho, filtro de versão e índice | `library_io.load` (spec descartado) | 🟢 |
| Remoção de chapa por driver somado ao da biblioteca | 006 D-07; `common.set_removed` | 🟢 |
| Fundo recuado por `delta_location` | 008 D-11; `common.set_back_recess` | 🟢 |
| Painéis sem registro próprio, desenhados pela barra única | 005; `panels.classes = ()` | 🟢 |

## Observabilidade

Sem log próprio: mensagens voltam em listas e viram `self.report` (`INFO`/`WARNING`/`ERROR`) nos operadores; `after_rebuild` devolve avisos que as bibliotecas descartam 🟢; a miniatura imprime "CAFFMob Draw: miniatura não gerada (…)" em falha (`library_common`). 🟢 _(Revisão 2026-10-10: as 6 chamadas (`data/properties.py:81`, `props_hb_frameless.py:803`, `ops_styles.py:885`, `ops_opening.py:1095`, `types_face_frame.py:8774`, `types_closets.py:1936`) ignoram o retorno)_

## Riscos e Lacunas

- 🟢 EC-01 (`.blend` sem `.json`), EC-02 (estilos do closets), EC-05 (`SIDE`), EC-06 (estilo de gaveta no painel). _(Revisão 2026-10-10: EC-01, EC-02 e EC-06 confirmados (EC-01 e EC-02 reproduzidos no Blender 5.2); só EC-05 segue dependendo de decisão do titular)_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-40):** EC-05: tirar `SIDE` do menu. Pendência de implementação: DT-01.
- 🟢 Trocar várias gavetas no frameless recria os vãos do bay (`change_bay_opening`); a personalização do vão anterior se perde (EC-04; 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-41):** copiar `btm_custom` para os vãos novos, exceto interior. Pendência de implementação: DT-02). _(Revisão 2026-10-10: executado no Blender 5.2: vão "Doors" com `front_material`/`door_style` → 3 gavetas: o objeto antigo some e os três vãos novos têm `btm_custom` vazio)_
- 🟢 `_data_blocks` não inclui materiais de slot ligados ao objeto nem grupos de nós aninhados; o resultado depende de `libraries.write` levar as dependências indiretas (não verificado). _(Revisão 2026-10-10: a API grava as dependências indiretas: "Indirectly referenced data-blocks will be expanded and written too" (`docs/rag/blender-api/corpus/bpy.types.BlendDataLibraries.md#bpy.types.BlendDataLibraries.write`); a fumaça 003 passo 6 reinsere com estilo e material)_
