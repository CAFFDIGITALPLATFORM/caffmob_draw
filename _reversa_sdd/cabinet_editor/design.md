# Editor de Armário (cabinet_editor) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/cabinet_editor/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN/RF/CA de `requirements.md`; EC-xx de `edge-cases.md`; fluxos F-xx abaixo. Contratos citados, não redescritos: `canvas2d.window` (`open_window`, `editor_area`, `is_editor_area`, `focus_tab`, `close_later`, `window_alive`, `over_side_panel`, `visible_width`), `canvas2d.view.View2D` (`fit`, `zoom`, `to_world`, `to_screen`) e `canvas2d.draw` (`begin`, `end`, `rect`, `box`, `outline`, `lines`, `dashed`, `text`, `text_width`, `COLORS`) em `_reversa_sdd/canvas2d/design.md`; `walls2d.history.History` em `_reversa_sdd/walls2d/design.md`; adaptadores (`for_root`, `for_object`, `module_root`, contrato obrigatório e opcional via `common.call`), `spec`, `reapply.reapply`, `common` (`gn_modifier`, `set_cutpart_material`, `RAW_MATERIAL_PROP`, `removed_roles`, `local_box`, `NO_LIBRARY_REASON`, `tr`) em `_reversa_sdd/customize/design.md`; `selection.classify` e `selection.editing.get_dimension/set_dimension` em `_reversa_sdd/selection/design.md`; `collision.obb.from_box/overlap` em `_reversa_sdd/collision/design.md`; `stick.apply.local_box` em `_reversa_sdd/stick/design.md`; `aggregates.group.create_group/is_group`, `aggregates.leaf.make_leaf/measure_free_travel/FREE_CONTACT_KEY`, `aggregates.convert.unconvert` em `_reversa_sdd/aggregates/design.md`. Também importados (contratos em outras units): `standards.api`, `standards.apply_core`, `standards.sync` (`bridge.py`, `scene_divisions.py`; ciclo descrito em `_reversa_sdd/standards/`), `data.dimension_schema`, `data.units`, `cutting.part_roles`, `cutting.machining`, `hb_types`, `compat`, `ui.save_feedback` e `product_libraries.frameless.types_frameless.CabinetPart` _(Revisão cruzada 2026-10-10: imports `from ..` em caffmob_draw/cabinet_editor/*.py; antes só nos pré-requisitos de tasks.md)_.

## Visão de Camadas

| Camada | Arquivos | `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `state.py`, `validate.py`, `elevation.py`, `structure.py`, `divisions.py` | não (`validate` usa `collision.obb`, `data.units`, `data.i18n`) | Rascunho, mensagens, vista frontal, caixa `btm`, subvãos | 🟢 |
| Núcleo puro (008) | `catalog.py`, `extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py` | não | Catálogo e geometria das abas novas | 🟢 |
| Dados salvos | `data_props.py` | sim | `Object.btm_structure`, `btm_division`, `btm_extra` | 🟢 |
| Sessão/UI | `props.py` | sim | `Session` e `WindowManager.btm_cabinet_editor` | 🟢 |
| Ponte | `bridge.py` | sim (`mathutils`; `bpy` tardio) | Instantâneo ↔ cena, ações | 🟢 |
| Cena | `scene_divisions.py`, `scene_parts.py`, `scene_extras.py`, `scene_interiors.py`, `scene_slides.py`, `reflow_handler.py` | sim | Objetos filhos da raiz; handlers | 🟢 |
| Interface | `ops_editor.py`, `ops_actions.py`, `window.py`, `previews.py`, `panels.py`, `panels_*.py` | sim | Operadores, modal, desenho, painéis | 🟢 |
| Pacote | `__init__.py` | não no topo | `register` na ordem `data_props, props, previews, window, ops_editor, ops_actions, panels, panels_structure, panels_divisions, panels_drawers, panels_interior, panels_doors, panels_sliding, panels_backs, reflow_handler`; `unregister` na inversa | 🟢 |

- 🟢 Dependência circular com `customize` (imports tardios dos dois lados): `cabinet_editor` importa `customize` em 6 arquivos (`bridge`, `ops_editor`, `ops_actions`, `scene_divisions`, `scene_parts`, `reflow_handler`); no sentido inverso `customize/adapters/common.py:190,216,345` e `customize/adapters/btm.py:114,131,152,165` importam `cabinet_editor.divisions.Box`/`cabinet_editor.structure`, `customize/library_io.py:127,133` importa `divisions`/`scene_divisions` e `customize/reapply.py:67` importa `scene_divisions`, `scene_extras`, `scene_interiors`, `scene_slides`. Mesmo padrão do ciclo com `standards` (ver `_reversa_sdd/standards/`) _(Revisão cruzada 2026-10-10: grep `from ...cabinet_editor` em caffmob_draw/customize/)_

## Estruturas de Dados

### `EditorState` (`state.py`) 🟢

| Campo | Tipo | Conteúdo |
|---|---|---|
| `dimensions` | `(L, A, P)` m | `editing.get_dimension(info, 'width'/'height'/'depth') or 0.0` |
| `spec` | dict | `customize.spec.to_dict(adapter.read(root))` + `"_raw"`: `{"openings": {caminho: {door_style, drawer_style, pull_model, pull_position, front_material, interior}}, "pull_model", "pull_all_fronts", "groups": {grupo: material}, "parts": {nome: material}}` (só peças com `btm_custom.material`) |
| `structure` | dict | `BTM_PG_Structure.to_dict()` = `{papel: {removed, mode, thickness, material}}` |
| `divisions` | list | `scene_divisions.read(root)` = dicionários crus dos 13 `FIELDS` (espessura 0 = Configurador) |
| `extras` | dict | `{chave: {enabled, value}}` |
| `slides` | dict | `{item, leaves, invert, opens: [open_value a 6 casas por folha]}` ou `{}` |
| `interiors` | list | `[{catalog_id, space, slot}]` ordenada por `(space, catalog_id, slot)` |
| `backs` | dict | `{mode, setback, auto}` |

`PRECISION = 6`; `signature(state)` = `json.dumps({"dims", "spec", "structure", "divisions", "extras", "slides", "interiors", "backs"}, sort_keys=True, default=str)` com floats arredondados recursivamente em dict/list/tuple (`spec` **não** é arredondado). `Draft(initial)`: `initial = initial.copy()`, `current = initial.copy()`, `history = History(current, signature=signature)`; `checkpoint(state)` faz `current = state.copy()` e devolve `history.checkpoint(current)`; `undo`/`redo` atualizam `current` se não `None`; `dirty()`; `apply_point()` recria o histórico a partir de `current`.

### Objetos salvos (`data_props.py`) 🟢

| Classe → ponteiro | Campos | Métodos |
|---|---|---|
| `BTM_PG_Structure` → `Object.btm_structure` (raiz) | `components` (`BTM_PG_StructureItem`: `role` enum TOP/BOTTOM/BACK/LEFT/RIGHT, `removed`, `mode` KEEP/EXTEND/SHRINK, `thickness` ≥ 0, `material`), `back_mode` FULL/RECESSED, `back_setback` 0,02 (≥ 0), `auto_back` True, `extras` (`BTM_PG_StructureExtra`: `kind`, `enabled`, `value`) | `item(role, create=False)`, `extra(kind, create=False)`, `to_dict`/`from_dict` (limpa e recria, ordenado), `extras_dict`/`extras_from_dict`, `backs_dict`/`backs_from_dict` (padrões FULL, 0,02, True) |
| `BTM_PG_Division` → `Object.btm_division` (chapa) | `is_division`, `uid`, `space` "s0", `orientation`, `offset`, `use_front`, `front` 0,02, `use_back`, `back` 0,02, `thickness`, `material`, `bay`, `kind` FIXED/MOVABLE/SPACER, `follow` | `FIELDS` (13), `to_dict`, `from_dict` (só chaves presentes; `is_division = True`) |
| `BTM_PG_Extra` → `Object.btm_extra` (peças 008) | `is_extra`, `kind` (19 tipos), `catalog_id`, `space`, `slot`, `params` JSON | — |

`MATERIAL_ITEMS` = `""` ("Do Configurador"), MDF, MDP, COMPENSADO, OSB, VIDRO, OUTRO. Idprops na cena: `btm_component` (componente do Configurador da peça: `DIV`, `BAS`, `ROD`, `TAMPON`, `ESP`, `PRAT`, `FRE_FORNO`, `POR`), `btm_division_sig` (raiz), `btm_hardware` (`PE_PLASTICO`, `PISTAO`, `TRILHO_INF`, `TRILHO_SUP`), `btm_slides` (grupo FRAME, JSON), `common.RAW_MATERIAL_PROP` (material bruto da chapa).

### `Session` (`props.py`) 🟢

`Session(root_name, library, draft)` com: `parts`, `initial_parts` (`elevation.Part`), `selected` (nome), `messages`, `adjustments` (`[(nome, mudança)]`), `limits`, `view`, `window_ptr`, `area_ptr`, `restore_area_type`, `requests` (fila `[(tipo, dados)]`), `request` (`'ok'|'cancel'|None`), `error`, `space` (caminho do subvão alvo), `spaces` (`{caminho: Box}` no **referencial da vista**), `space_labels`, `removed_parts`, `library_path`, `library_box` (referencial da vista), `last_moved` (uid), `applied`. Criados fora do `__init__` por `ops_editor.start_session`: `dim_messages` (`{campo: [Message]}`), `edited` (set de nomes), `view_key`. Métodos: `root()` = `bpy.data.objects.get(root_name)`; `push(kind, data=None)` acrescenta e redesenha; `blocking()`; `redraw()` marca a área do editor **e todas as `VIEW_3D`**. Módulo: `_session = [None]`, `session()`, `start(...)`, `end()`.

Tipos de pedido: `('dimension', (campo, valor))`, `('edit', (ação, payload))`, `('apply', None)`, `('arrow', (eixo, sentido))`, `('undo', None)`, `('redo', None)`. Todo payload de `edit` leva `targets` (nomes editados, para o diff).

### `BTM_PG_CabinetEditorState` → `WindowManager.btm_cabinet_editor` 🟢

| Campo | Tipo / itens | Comportamento |
|---|---|---|
| `width`, `height`, `depth` | Float DISTANCE, sem min/max | `get` = `draft.current.dimensions[i]` (0 sem sessão); `set` → `push('dimension', (campo, valor))` |
| `components`, `component_index` (−1) | Coleção (`kind`, `label`, `flagged`) | Espelho das peças (vãos primeiro, por nome); `update` do índice seleciona; **nenhum painel desenha a lista** |
| `messages`, `adjustments`, `structure`, `structure_index`, `divisions`, `division_index` | Coleções espelho | Preenchidas por `_sync_ui` |
| `tab` | `TAB_ITEMS` (STRUCTURE 0, DIVISIONS 1, DRAWERS 3, INTERIOR 4, DOORS 5, SLIDING 6, BACKS 7) | Número 2 (antigo FINISH) não existe |
| `new_orientation` | VERTICAL/HORIZONTAL | Orientação do modo múltiplo |
| `new_use_front`, `new_front` (0,02; 0–1), `new_use_back`, `new_back` (0,02; 0–1) | Bool/Float | Recuos da próxima divisão |
| `space` | Enum dinâmico (`_space_items`: subvãos ordenados ou `("", "Sem vão interno")`, cache em `_SPACE_CACHE`) | `get`/`set` na sessão |
| `catalog_item` | String | Item escolhido (qualquer aba) |
| `invert` | Bool | Compartilhado por Portas e Deslizantes |
| `div_mode` | VERTICAL/HORIZONTAL/MULTIPLE | — |
| `div_kind` | MOVABLE/FIXED (padrão)/SPACER/NONE | — |
| `div_count` | 2 (1–10) | — |
| `drawer_tab` | DRAWERS/TALL/INTERNAL/BLUM | — |
| `drawer_count` | 4 (1–8) | — |
| `drawer_style`, `door_style` | Enum dinâmico `ops_actions._style_items` ("" = estilo do módulo) | — |
| `drawer_pull`, `door_pull` | Enum dinâmico `ops_actions._pull_items` ("", `spec.NO_PULL`, puxadores) | — |
| `door_region` | LOWER/UPPER/TALL/FLIP | Só FLIP tem efeito (EC-13; 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-84):** esconder as três sem efeito ou documentá-las como rótulo; DT-07) |
| `door_scope` | BOTH/WHOLE/LEFT/RIGHT | — |
| `interior_group` | PANELS/LIBRARY/SUPPORTS/PISTONS | — |
| `interior_filter` | EXTERNAL/BUILT_IN | — |
| `slide_family` | WOOD/ALUMINIUM | — |
| `slide_leaves` | 2 (2–3) | — |
| `back_tab` | FULL/RECESSED | — |
| `step` | 0,01 (≥ 0,0001) | Passo das setas |
| `step_initial` | 0,0 (≥ 0) | Passo inicial |
| `tree_<chave>` (20) | Bool virtual | `get`: grupo (exceto FEET) = algum filho ligado; sem registro = `chave in DEFAULT_ON`; `set`: um `TOGGLE_EXTRA {key, enabled}` **por filho** nos grupos KICKS/VIEWS/VIEWS_TALL, senão um para a chave |
| `value_<chave>` (chaves com padrão: FEET, CLOSURE, VIEW_*, VIEW_TALL_*) | Float virtual ≥ 0 | `get`: valor gravado ou `extras.DEFAULTS`; `set`: `TOGGLE_EXTRA {key, value}` |
| `comp_<papel>` (5) | Bool virtual | `get` = não removido; `set` → `REMOVE_PART`/`RESTORE_PART` em `KEEP` |
| `bays` | Int virtual 1–10 | `get` = `bays.count` das divisões da cena; `set` → `SET_BAYS {count}` |
| `pos_front`, `pos_low`, `pos_back`, `pos_high` | Float virtual | Cotas da divisória selecionada (RN-19); `set` → `EDIT_DIVISION` |

Os campos `tree_*`, `value_*`, `comp_*`, `bays`, `pos_*` são acrescentados às anotações por `_add_virtual_fields()` na importação, antes do registro.

## Interface

### `validate.py` 🟢

| Símbolo | Assinatura | Retorno / regra |
|---|---|---|
| `ERROR`, `WARNING`, `INFO`; `TOLERANCE = 0.001`; `DEFAULT_LIMITS` | — | `{'width': (0.01, 10), 'height': (0.01, 10), 'depth': (0.005, 10)}` |
| `Message` | `(code, severity, component, parameter='', value='', range='', action='')` frozen | `blocks` = `severity == ERROR` |
| `limits_for` | `(library_limits=None)` | Por campo `(max(lo_g, lo_b), min(hi_g, hi_b))`; campo desconhecido entra como veio |
| `parse_dimension` | `(name, text, limits, unit='MM')` | `(None, [DIM-001])` vazio; `(None, [DIM-002])` `ValueError` de `units.parse_length`; senão `(valor, check_dimension)` — sem chamador |
| `check_dimension` | `(name, value, limits, unit='MM')` | `[]` se `lo − 1e−9 ≤ v ≤ hi + 1e−9`; senão `DIM-003` com `value`/`range` formatados por `units.format_length` |
| `outside_volume` | `(root_size (L, P, A), parts)` | RN-09; usa `size[0]` e `size[2]` |
| `internal_overlaps` | `(parts)` | Prateleiras/divisórias ordenadas por nome; `obb.overlap(...)['depth'] > TOLERANCE` → `GEO-002` (`component` = a, `value` = b) |
| `unsupported` | `(section, reason)` | `CAT-001` aviso — sem chamador |
| `blocking`, `sort_messages` | `(messages)` | Ordem ERROR < WARNING < INFO, código, componente, parâmetro |

### `elevation.py` 🟢

`TOLERANCE = 0.0001`; tipos `FRONT`, `SHELF`, `DIVIDER`, `STRUCTURE`, `OPENING`, `AGGREGATE`, `PART`; `INTERIOR = {SHELF, DIVIDER}`; `kind_from_role(code)`: `POR`→FRONT, `PRAT`→SHELF, `DIV`→DIVIDER, `LAT`/`BAS`/`ROD`/`TRA`/`FUN_INF`/`FUN_SUP`/`FUN_ALT`/`TAMPON`/`SAR`→STRUCTURE, resto PART. `Part(name, kind, lo, hi)` frozen, `rect = (lo.x, lo.z, hi.x, hi.z)`, `size`. `draw_order` = ordenado por `(−lo.y, nome)`. `hit(parts, x, z)` → nome: dentro inclusivo; mínimo de `(round(lo.y, 4), área frontal, nome)`. `bounds(parts)` → `(x0, z0, x1, z1)` ou `None`. `diff(before, after, targets=())` → RN-10.

### `structure.py` 🟢

`ROLES = ('TOP','BOTTOM','BACK','LEFT','RIGHT')`; `ROLE_LABELS` (Tampo, Base, Fundo, Lateral esquerda, Lateral direita); `KEEP/EXTEND/SHRINK`, `MODE_LABELS`; `THICKNESS_RANGE = (0.003, 0.06)`; `ROLE_COMPONENT = {TOP: BAS, BOTTOM: BAS, LEFT: LAT, RIGHT: LAT, BACK: FUN_INF}`; `LATERAL`, `BASE`.

| Símbolo | Assinatura | Regra |
|---|---|---|
| `RoleState` | `(removed=False, mode=KEEP, thickness=0.0, material="")` frozen | `changed` = espessura ou material |
| `state_from_dict` / `state_to_dict` | `(data)` / `(states)` | Ignora papéis desconhecidos / omite estados iguais ao padrão |
| `allowed_mode` | `(mode, caps)` | `caps.get(mode, "Modo desconhecido") is None` → `(mode, None)`; senão `(KEEP, caps.get(mode))` |
| `check_thickness` | `(role, value, unit)` | 0 ou dentro de 3–60 mm (folga 1e−9) → `[]`; senão `STR-002` |
| `unsupported_mode` | `(role, mode, reason)` | `STR-001` — sem chamador |
| `layout` | `(width, height, depth, thick, states, back_setback=0.0, assembly=LATERAL)` | F-09 |
| `carcass_lengths` | `(width, height, left, right, bottom, assembly=LATERAL)` | `BASE`: laterais `A − base`, base `L`, tampo `L − e − d`; `LATERAL`: laterais `A`, base e tampo `L − e − d` |
| `shrink_change` | `(role, thickness)` | LEFT `({'width': −t}, (t/2,0,0))`; RIGHT `(…, (−t/2,0,0))`; BOTTOM `({'height': −t}, (0,0,t))`; TOP `({'height': −t}, (0,0,0))`; BACK `({'depth': −t}, (0,−t,0))` |

### `divisions.py` 🟢

`MIN_SPACE = 0.05`, `MIN_DEPTH = 0.05`, `DEFAULT_SETBACK = 0.02`, `VERTICAL`/`HORIZONTAL`, `FIXED`/`MOVABLE`/`SPACER`, `_AXIS = {VERTICAL: 0, HORIZONTAL: 2}`. `Box(lo, hi)` frozen com `size(axis)` e `contains_front(x, z)` (inclusivo). `Division(uid, space, orientation, offset, thickness, use_front=False, front=0.02, use_back=False, back=0.02, material="", kind=FIXED, follow="", bay=False)` frozen.

| Símbolo | Assinatura | Regra |
|---|---|---|
| `new_uid` | `()` | `uuid4().hex[:8]` |
| `to_dict` / `from_dict` | — | `asdict`; ignora chaves desconhecidas |
| `children` / `depth_of` | `(path)` | `(path+".a", path+".b")` / nº de pontos |
| `resolve` | `(roots, divisions)` | F-07 |
| `place` | `(plate, division)` | `lo.y += front` se `use_front`; `hi.y −= back` se `use_back` |
| `middle_offset` | `(space, orientation, thickness)` | `max(0, (tamanho − t)/2)` |
| `add` | `(roots, divisions, space, orientation, thickness, *, use_front, front, use_back, back, uid=None, kind=FIXED, follow="", bay=False, offset=None)` | Folha inexistente → `ValueError("Escolha um vão livre para a divisão")`; offset `None` → 0 (SPACER) ou meio; devolve lista nova |
| `add_many` | `(roots, divisions, space, orientation, count, thickness, **options)` | `gap = (tamanho − N·t)/(N+1)`; N chamadas de `add(offset=max(gap, 0))` em `space`, `space.b`, `space.b.b`… |
| `remove_in_space` | `(divisions, leaf)` | Sem "." → `(lista, [])`; pai = `leaf.rsplit(".",1)[0]`; primeira divisão não SPACER com `space == pai` → `remove` |
| `update` | `(divisions, uid, **changes)` | `dataclasses.replace` |
| `remove` | `(divisions, uid)` | `(restantes, removidos)`: a divisão e toda com `space` igual ou descendente de `.a`/`.b` dela |
| `offset_range` | `(space, division)` | SPACER `(0, max(0, tam − t))`; senão `(0.05, tam − t − 0.05)` |
| `validate` | `(roots, divisions, unit='MM', names=None)` | RN-14; `component` = nome do objeto ou uid; DIV-001 `range` usa `max(lo, hi)` |
| `space_at` | `(leaves, x, z)` | Folha de menor área frontal, desempate por caminho |
| `space_tokens` | `(path, divisions)` | `[('ROOT', n+1), ('LEFT'|'RIGHT'|'BOTTOM'|'TOP'), …]` pela orientação da divisão de cada nível (padrão vertical) |

### `catalog.py`, `extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py` 🟢

- `catalog.Item(id, tab, group, label, description="", action="", params=(), size_mm=None, margin_mm=10.0, invertible=False, filter="", groove=False, extra={})`; `thumb` = `id.lower()`; `param(name, default)`; `too_small(space_mm)` → `None` ou `(L+20, A+20, 0)` (só largura e altura, folga 1e−6). `ITEMS` (47): `DIV_NO_RECESS` (front 0, back 15), `DIV_RECESS` (front 20, back 15), `SPACER_15`, `SPACER_30`, `SPACER_DIV` (follow), `DRAWER_CF`, `DRAWER_TALL` (min 2, max 4), `DRAWER_INTERNAL`, `DRAWER_BLUM`, `FRONT_RETA`, `BACK_FULL`, `BACK_RECESSED`, 10 painéis (`PANEL_OVEN_MICRO_*`, `PANEL_OVEN_*`, `PANEL_MICRO_*`, `PANEL_COFFEE_*`, `FRONT_*` × EXT/BI), `OVEN`, `MICRO`, `COFFEE`, `VENT`, `SUPPORT`, `PISTON`, 14 `SLIDE_<estilo>` em madeira, 4 integrados, `SLIDE_ALU_FRAME`. `APPLIANCE_SIZE_MM`: OVEN 595×595×560, MICRO 595×390×400, COFFEE 595×455×400. `get(id)`, `items(tab, group=None, filter_=None)` (filtro "" vale em todos). `TREE` (20), `TREE_GROUPS = {FEET, KICKS, VIEWS, VIEWS_TALL}`, `CHILDREN`, `DEFAULT_ON = {FOOT_1..4}`.
- `extras`: `FOOT_RADIUS 0.02`, `FOOT_INSET 0.05`, `KICK_SETBACK 0.05`, `RECESS 0.02`, `CEILING 2.70`, `DEFAULTS`, `FOOT_SLOTS`; `Piece(kind, box, component=None, hardware=None, material="", slot=0)`; `layout(box, t, settings, ceiling=2.70)` — F-10.
- `bays`: `ROOT = 's0'`, `MAX_BAYS = 10`; `plan(space, count, thickness)` → `[(s0.b*i, largura)]` com count preso a 1–10; `count(divisions)` = 1 + nº `bay`; `apply(roots, divisions, count_, thickness)`; `removed(before, after)`.
- `slides`: `PITCH 0.020`, `LEAF_THICKNESS 0.018`, `OVERLAP 0.030`, `TRACK_HEIGHT 0.010`, `DEPTH_MARGIN 0.050`, `GROOVE (0.020, 0.008)`; `Leaf(index, track, box, groove=None)`, `Track(box)`, `Layout(leaves, tracks)`; `missing_depth(space, leaves)`; `layout(space, leaves, style_id, invert=False)` — F-11.
- `appliances`: `MM = 0.001`, `VENT_SIZE (0.440, 0.030)`; `Piece(box)`, `Layout(panel, cutout, appliances)`; `_space_mm(space)` = (L, A, P) em mm; `missing(space, item_id)`; `layout(space, item_id, thickness)` — F-12; `support_offset` sem chamador.
- `position`: `cotas(space, division)`, `offset_from_cota(space, division, which, value)` (`front`/`back` devolvem o offset atual), `step_move(space, division, direction, step, initial, first=False)` = `min(max(offset + dir·passo, lo), max(lo, hi))`.

### `bridge.py` 🟢

| Símbolo | Assinatura | Comportamento |
|---|---|---|
| `CUSTOM_FIELDS`, `_LIBRARY_HOLDER`, `_SKIP_TAGS` | constantes | Ver estruturas; holder FACE_FRAME `face_frame_cabinet`, CLOSETS `hb_closet_starter`, BTM `btm_cabinet` (frameless sem holder → sem estreitamento); skip `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x` |
| `info_of`, `adapter_of` | `(root)` | `classify.classify`, `adapters.for_root` |
| `read_state` | `(root)` | `EditorState` (RN-03) |
| `library_limits` | `(root, library)` | `{campo: (max(hard_min, 0), hard_max)}` |
| `set_dimension` | `(context, root, field, value)` | `editing.set_dimension(context, info_of(root), field, value)` |
| `apply_state` | `(context, root, target)` | F-05; devolve avisos |
| `reflow_all` | `(context, root)` | `scene_divisions.reflow(force)`, `scene_extras.sync`, `scene_interiors.reflow`, `scene_slides.reflow` |
| `edit` | `(context, root, action, data)` | F-06 |
| `parts` | `(context, root)` | F-04 |
| `view_shift` / `root_size` | `(context, root)` | Canto mínimo / tamanho de `stick.apply.local_box(root, depsgraph)` |
| `opening_of` | `(root, name)` | Vão (de `adapter.openings`) ancestral do objeto com menos descendentes; `None` sem adaptador ou nome |
| `structure_rows` | `(context, root)` | `[(papel, info, caps, RoleState)]` na ordem de `ROLES`, só papéis em `structure_info` |
| `configured_part` | `(context, root, role)` | `(material or 'MDF', espessura or 0.0)` do componente `ROLE_COMPONENT[role]` na linha (`standards.api.get_value`/`get_value_m`, `dimension_schema.sheet_key`) |
| `is_caffmob_module`, `origin_definition`, `is_own_standard`, `set_assembly` | — | RN-32; `set_assembly` fora do CAFFMob → `["Só armários CAFFMob têm montagem"]` |
| `remove_part`, `restore_part`, `edit_part`, `_apply_structure`, `_tidy` | — | F-08 |
| `division_context` | `(context, root)` | `(roots, core, raw, names)` |
| `add_division`, `edit_division`, `remove_division`, `set_bays`, `add_many`, `remove_in_space` | `(context, root, data)` | F-06 |
| `toggle_extra`, `set_back`, `library_opening`, `insert_doors`, `insert_drawers`, `insert_interior`, `remove_interior`, `insert_slides`, `remove_slides` | `(context, root, data)` / `library_opening(context, root, space_path)` | F-06 |
| `EDIT_006`, `EDIT_008`, `DOOR_FRONTS` | dicts | Despacho e mapa de portas |

### `scene_*.py` e `reflow_handler.py` 🟢

| Símbolo | Comportamento |
|---|---|
| `scene_divisions` | `NAME "Divisória"`, `COMPONENT 'DIV'`, `COMPONENT_PROP 'btm_component'`, `SIGNATURE_PROP 'btm_division_sig'`, `DEFAULT_LINE {FRAMELESS: COZ, FACE_FRAME: COZ, CLOSETS: DOR, BTM: COZ}`; `line_of(root)` (`btm_line` ou padrão); `configured(scene, root)` → `(material or 'MDF', espessura or 0.015)`; `objects(root)` (filhos diretos com `is_division`, por nome); `read`, `to_core(data, t)` (espessura 0 → t), `core(scene, root, data=None)`, `roots(context, root)` = `common.call(adapter, 'inner_spaces', …)`, `names`; `apply(context, root, wanted)` cria (`CabinetPart` "Divisória {n+1}", pai = raiz, `matrix_parent_inverse` identidade, `btm_component`, `from_dict`, `_borrow_material`, mesmas coleções da raiz), atualiza ou apaga por uid e chama `reflow(force=True)`; `reflow` F-13; `_place` |
| `scene_parts` | `extras_of(root, kinds=None)`, `delete(objs)` (descendentes primeiro), `_link` (coleções da raiz ou da cena; pai = raiz), `_tag`, `place(obj, box)` (eixo mais fino: Z → sem rotação; X → −90° em Y + `Mirror Z`, `Length`=Z, `Thickness`=X; Y → +90° em X + `Mirror Z`, `Width`=Z, `Thickness`=Y) devolve o eixo; `make_part(root, name, box, kind, component, material="", **tag)`; `make_box`/`make_cylinder` (BMesh, 16 segmentos) com `btm_hardware`; `carcass_box(context, root)` (btm: `elevation_parts`; outras: `local_box` das `structure_parts`; sem nada: `bound_box` da raiz) |
| `scene_extras` | `KINDS` (13), `NAMES`; `sync(context, root)`: apaga todos os extras desses tipos; se algum `enabled`, `t = configured_part('LEFT')[1] or 0.015`, recria pela `extras.layout` (ferragem → cilindro; resto → `make_part`) |
| `scene_interiors` | `KINDS = {APPLIANCE_PANEL, APPLIANCE, APPLIANCE_SUPPORT, PISTON}`, `PANEL_THICKNESS 0.018`, `PISTON_BOX (0.02, 0.25, 0.02)`; `entries(root)`; `apply(context, root, wanted)` apaga tudo e recria pela folha atual (sem item ou folha → aviso com o `catalog_id`, ignorado pelos chamadores); `_build` (apoio: `PRAT` em z = lo.z + A/3 com espessura da Divisória; pistão a 30 mm do canto superior esquerdo-frente; painel `FRE_FORNO` + `_cutout` com `CPM_CUTOUT` `machining.AGGREGATE_PREFIX + nome`, sockets `X`, `End X`, `Y`, `End Y`, `Route Depth` 0,018, `Flip Z` False; eletros `make_box`); `reflow` = `apply(entries)` |
| `scene_slides` | `FRAME_TAG 'btm_slides'`, `TRACK_NAMES`, `TRACK_CODES`; `frame_of`, `state_of`, `_sashes` (grupos LEAF por nome), `clear` (desconverte folhas agregadas, `view_layer.update`, apaga FRAME, descendentes e extras SLIDE_*), `missing_depth(context, root, leaves)` (primeiro vão-raiz), `apply` F-14, `reflow` |
| `reflow_handler` | `_running = [False]`; `_roots(depsgraph)` (originais das atualizações → `adapters.module_root` → com `btm_division_sig`); `on_depsgraph_update` e `on_frame_change` `@persistent`, saem com `_running` ou sessão aberta; `_reflow` engole `ReferenceError`/`RuntimeError`; `register`/`unregister` sem duplicar |

## Operadores

| `bl_idname` | `bl_options` | Propriedades | Comportamento | Confiança |
|---|---|---|---|---|
| `caffmob.cabinet_editor` | REGISTER | — | RN-02; F-01 | 🟢 |
| `caffmob.cabinet_editor_modal` | REGISTER, UNDO, INTERNAL | — | F-02 | 🟢 |
| `caffmob.cabinet_editor_confirm` | REGISTER, INTERNAL | — | `poll`: sessão e sem erro; `request = 'ok'` | 🟢 |
| `caffmob.cabinet_editor_cancel` | REGISTER, INTERNAL | — | Sujo → `invoke_confirm(title "Descartar alterações", confirm "Descartar", icon WARNING)`; `request = 'cancel'` | 🟢 |
| `caffmob.cabinet_editor_close` | REGISTER, INTERNAL | `choice` CONTINUE/DISCARD/CONFIRM | Sujo → `invoke_props_dialog` "O armário tem alterações"; limpo ou DISCARD → cancel; CONFIRM → ok (bloqueado → WARNING, CANCELLED); CONTINUE → nada | 🟢 |
| `caffmob.cabinet_editor_edit` | REGISTER, INTERNAL | `action` FRONT/STYLE/PULL/MATERIAL/INTERIOR, `front` (dinâmico: `spec.FRONT_TYPES` que `adapter.front_types(root)` permite; nenhum → só `OPEN` "Vazio"), `drawer_count` 1–`spec.MAX_DRAWERS`, `kind` DOOR/DRAWER, `style`, `model`, `position` (`PULL_POSITION_ITEMS`), `all_fronts`, `target` FRONTS/GROUP, `group` (`spec.GROUPS`), `material`, `shelves`, `dividers`, `drawers`, `heights` "a; b" | Sem vão (`selected_path`) e ação ≠ MATERIAL-GROUP → WARNING "Selecione um vão ou uma frente na vista"; INTERIOR pré-preenche do `adapter.read`; FRONT ≠ DRAWERS executa direto, demais abrem diálogo; alturas inválidas → WARNING "Alturas inválidas"; enfileira `edit` com `path` e `targets=[selected]` | 🟢 |
| `caffmob.cabinet_editor_history` | REGISTER, INTERNAL | `redo` | Enfileira `undo`/`redo` | 🟢 |
| `caffmob.cabinet_editor_save_module` | REGISTER, INTERNAL | — | Desseleciona tudo, seleciona e ativa a raiz, devolve `caffmob.module_save('INVOKE_DEFAULT')` | 🟢 |
| `caffmob.cabinet_editor_division_add` | REGISTER, INTERNAL | — | Sem subvão válido → WARNING; `ADD_DIVISION` com `new_*` (sem `kind`) | 🟢 |
| `caffmob.cabinet_editor_division_edit` | REGISTER, INTERNAL | `uid` (HIDDEN), `offset`, `use_front`, `front`, `use_back`, `back`, `thickness`, `material` (`MATERIAL_ITEMS`) | Pré-preenche do objeto; diálogo com título = nome; `EDIT_DIVISION` com todos os campos e `targets=[nome]` | 🟢 |
| `caffmob.cabinet_editor_division_remove` | REGISTER, INTERNAL | `uid` | `REMOVE_DIVISION` | 🟢 |
| `caffmob.cabinet_editor_part_remove` | REGISTER, INTERNAL | `role`, `mode` | Diálogo "Remover {papel}" com os 3 modos (indisponível desabilitado com o motivo); modo indisponível → WARNING e CANCELLED; `REMOVE_PART` | 🟢 |
| `caffmob.cabinet_editor_part_restore` | REGISTER, INTERNAL | `role` | `RESTORE_PART` | 🟢 |
| `caffmob.cabinet_editor_part_edit` | REGISTER, INTERNAL | `role`, `thickness` 0–0,06, `material` | `EDIT_PART` | 🟢 |
| `caffmob.cabinet_editor_insert` | REGISTER, INTERNAL | `tab` (HIDDEN) | `description` = motivo ou "Insere no vão escolhido o item da aba"; `insert_reason` → WARNING; `insert_payload` → `_push` | 🟢 |
| `caffmob.cabinet_editor_apply` | REGISTER, INTERNAL | — | `poll`: sem erro ("Corrija os erros para aplicar"), sujo ("Nada para aplicar"); enfileira `apply` | 🟢 |
| `caffmob.cabinet_editor_pick` | REGISTER, INTERNAL | `item` | `catalog_item = item`; `description` = descrição ou rótulo | 🟢 |
| `caffmob.cabinet_editor_remove_item` | REGISTER, INTERNAL | `kind` INTERIOR/SLIDES, `slot` | `REMOVE_INTERIOR {slot}` ou `REMOVE_SLIDES` | 🟢 |

Os operadores da 006/008 herdam `_SessionOperator.poll` (sessão com raiz). Consumidores que abrem o editor: `ui/object_properties.py:190` (módulo, frente ou peça), `ui/sidebar_vocab.py:25`, `library_panel/ops_cabinet.py:69` (abrir após inserir). `stick/settle.py:19` lista o modal entre os operadores que suspendem o assentar. 🟢

### `insert_payload(context, tab)` 🟢

| Aba | Ação | Payload |
|---|---|---|
| DIVISIONS, `div_kind` NONE | `REMOVE_IN_SPACE` | `{space}` |
| DIVISIONS, SPACER | `ADD_DIVISION` | item SPACER escolhido (senão `SPACER_15`); `orientation` = `new_orientation` se MULTIPLE, senão `div_mode`; `kind` SPACER; `thickness` = mm/1000; `follow` |
| DIVISIONS, MOVABLE/FIXED | `ADD_MANY` (MULTIPLE) ou `ADD_DIVISION` | `space`, recuos de `new_*`; item do grupo RECESS → `use_front = front > 0`, `front = front/1000 or new_front`; `count = div_count`; `kind` |
| DRAWERS | `INSERT_DRAWERS` | `space`, `count`, `variant = drawer_tab`, `style`, `pull` |
| DOORS | `INSERT_DOORS` | `space`, `scope` (FLIP se região FLIP), `region`, `style`, `invert`, `pull` |
| INTERIOR | `INSERT_INTERIOR` | `catalog_id`, `space` |
| SLIDING | `INSERT_SLIDES` | `item`, `leaves`, `invert` |
| BACKS | `SET_BACK` | `mode = back_tab`, `setback`/`auto` atuais da raiz (0,02/True sem raiz), `insert: True` |

## Atalhos e eventos da vista (modal) 🟢

| Evento | Condição | Efeito |
|---|---|---|
| qualquer | `process` executou algo | `RUNNING_MODAL` (o evento é consumido) |
| `TIMER` | — | Até conseguir, `window.focus_tab(area)`; `PASS_THROUGH` |
| Ctrl/⌘ + Z (PRESS) | em qualquer lugar | `push('undo')`; com Shift → `redo` |
| Ctrl/⌘ + Y (PRESS) | em qualquer lugar | `push('redo')` |
| ← → ↓ ↑ (PRESS) | região existe e mouse fora do painel lateral | `push('arrow', ('X', ∓1))` / `('Z', ∓1)` |
| `WHEELUPMOUSE` / `WHEELDOWNMOUSE` | mouse dentro da região e fora do painel | `view.zoom(1.15)` / `view.zoom(1/1.15)` no cursor |
| `LEFTMOUSE` PRESS | idem | Seleção (RN-22), `_sync_ui` |
| `ESC` PRESS | idem | `caffmob.cabinet_editor_close('INVOKE_DEFAULT')` |
| outros | — | `PASS_THROUGH` |

## Fluxos

### F-01 Abrir (`BTM_OT_CabinetEditor.execute`, `start_session`) 🟢

1. `root = module_root(context)` (`adapters.for_object(context.active_object)`; raiz só se houver adaptador).
2. `start_session`: `info = classify.classify(root)`; `draft = Draft(read_state(root))`; `s = props.start(root.name, info.library, draft)`; `s.limits = limits_for(library_limits(root, info.library))`; `dim_messages = {}`, `edited = set()`, `view_key = None`; `parts = bridge.parts`; `initial_parts = list(parts)`; zera `space`, `spaces`, `space_labels`, `removed_parts`, `library_path`, `library_box`, `last_moved`, `applied`; `ui.tab = 'STRUCTURE'`; `_divisions_refresh` (mensagens descartadas); `_sync_ui`.
3. `window.open_editor(context)` (= `canvas2d.window.open_window` com a mensagem RN-02); `RuntimeError` → `props.end()`, ERROR, `CANCELLED`.
4. Com `temp_override(window, area, region)`: `caffmob.cabinet_editor_modal('INVOKE_DEFAULT')`; `s.redraw()`; `FINISHED`.

### F-02 Modal (`BTM_OT_CabinetEditorModal`) 🟢

`invoke`: sem sessão → `CANCELLED`; `tab_ready = False`; timer `TIMER_STEP = 0.1` na janela; `modal_handler_add`. `modal`, em ordem: (1) sem sessão → `_end(False)`, CANCELLED; (2) raiz sumiu → `_end(False)`, WARNING "O módulo não existe mais; o editor foi fechado", CANCELLED; (3) janela morta → `dirty` anotado, `_end(False)`, se sujo `ui.save_feedback.show("Editor fechado: alterações descartadas")`, CANCELLED; (4) `request == 'ok'` → `_end(True)`, INFO "Armário atualizado: {raiz}", FINISHED; (5) `request == 'cancel'` → `_end(False)`, CANCELLED; (6) `process` → se mudou, RUNNING_MODAL; (7) eventos da tabela de atalhos. `_end(keep)`: se não `keep`, `rollback` (= `apply_state(initial)` só se sujo); remove o timer; `window.close_later(s)`; `props.end()`; limpa `components`, `messages`, `adjustments`, `structure`, `divisions`. `cancel(context)` = `_end(False)`.

### F-03 `process` e `refresh` 🟢

`process(context, s)`: enquanto houver pedidos, tira o primeiro; raiz sumiu → devolve; dentro de `try`:
- `dimension`: `msgs = check_dimension(campo, valor, s.limits, unidade)`; `dim_messages[campo] = msgs`; sem erro → `bridge.set_dimension`; `refresh(checkpoint=not msgs)`.
- `edit`: `edited |= targets` não vazios; `refresh(context, s, bridge.edit(context, root, ação, payload))`.
- `apply`: `_apply_now` (RN-05; nada se bloqueado ou limpo).
- `arrow`: `_arrow` (F-15).
- `undo`/`redo`: alvo `None` → `s.error` "Nada para desfazer."/"Nada para refazer." e `continue` (sem marcar mudança); senão `dim_messages.clear()`, `refresh(context, s, apply_state(context, root, alvo), checkpoint=False)`, `draft.current = alvo`.
- Depois de cada pedido sem exceção: `s.error = ""`; `ValueError`/`RuntimeError` → `s.error = str(exc)`. Marca mudança.

`refresh(context, s, library_messages=(), checkpoint=True)`: raiz sumiu → nada; `parts = bridge.parts`; seleção que sumiu → `None`; `current = read_state`; `checkpoint` → `draft.checkpoint(current)`, senão `draft.current = current`; `adjustments = diff(initial_parts, parts, edited)`; mensagens = DIM guardadas + `outside_volume((L, P, A) de root_size, parts)` + `internal_overlaps(parts)` + `_divisions_refresh` + `LIB-001` (WARNING, `action` = texto) por aviso da biblioteca; `_sync_ui`; `redraw`.

`_divisions_refresh`: `leaves` de `resolve(roots, core)` deslocadas por `view_shift` → `s.spaces`; `space_labels` = "Vão n › esquerdo/direito/de baixo/de cima"; `space` inválido → menor caminho (ou ""); mensagens `dv.validate` + `check_thickness` por papel gravado; `removed_parts` = peças **iniciais** cujo nome está nas `structure_parts` dos papéis removidos (ou é o rótulo do papel); `_library_refresh` (vão da biblioteca do alvo, caixa no referencial da vista). `_sync_ui`: espelhos; muda `component_index` com `props._session[0] = None` temporário para não disparar o `update`; estrutura com tamanho/material/espessura formatados e motivos `reason_remove`/`reason_edit`; divisões com "Vertical · offset · frente x · trás y · material espessura".

### F-04 `bridge.parts` 🟢

`depsgraph`; nomes dos vãos do adaptador; `lo_root` de `local_box(root)` como deslocamento; para cada `root.children_recursive`: vãos sempre entram; demais saem se tiverem tag de `_SKIP_TAGS`, `hide_viewport`, `not visible_get()` ou `display_type` WIRE/BOUNDS; só `MESH` com `bound_box` avaliada não degenerada; cantos levados à raiz; `Part(nome, _kind, lo − shift, hi − shift)`. `_kind`: vão → OPENING; `btm_aggregate.is_aggregate` → AGGREGATE; `classify` FRONT ou idprop `IS_CABINET_FRONT` → FRONT; senão `part_roles.classify(nome, hb_part_role, component=btm_component)` → `kind_from_role`. Acrescenta `elevation_parts` do adaptador (chapas da malha única do `btm`) como STRUCTURE.

### F-05 `apply_state(context, root, target)` 🟢

1. `current = read_state(root)`; medidas que diferem > 1e−7 → `set_dimension`. Sem adaptador → devolve.
2. Para cada vão de `target.spec`: frente/quantidade diferente → `adapter.set_front` (relê vãos); interior diferente → `adapter.set_interior`.
3. Grava `_raw`: campos de `btm_custom` por vão, `pull_model`, `pull_all_fronts`, material por grupo (`spec.GROUPS`), material por peça (ausente → "").
4. `reapply.reapply(context, root)`; `_apply_structure(current.structure, target.structure)`; fundo diferente → `set_back(target.backs or {FULL, 0.02, True})`.
5. Divisões diferentes das gravadas → `scene_divisions.apply`, senão `reflow(force=True)`.
6. Extras diferentes → `extras_from_dict`; sempre `scene_extras.sync`; sempre `scene_interiors.apply(target.interiors)`; deslizantes refeitos se mudou (sem `opens`) **ou** se o alvo tem deslizantes.

### F-06 `bridge.edit` e ações 🟢

`edit`: `EDIT_006` → `EDIT_008` → ações da 003 (adaptador `None` → `[]`; `opening = openings[data['path']]`):
- `FRONT`: sem vão → `[]`; mesma `(frente, gavetas)` (gavetas 0 se não DRAWERS) → `[]`; senão `set_front` + `reapply`.
- `STYLE`: `door_style` ou `drawer_style` do vão. `PULL`: `all_fronts` → modelo na raiz e posição em todos os vãos; senão modelo e posição no vão. `MATERIAL`: GROUP → `set_group_material`; FRONTS → `front_material` do vão. Essas três terminam em `reapply`.
- `INTERIOR`: `spec.Interior(shelves, dividers, drawers, heights)`; `set_interior`; avisos ou `reapply`.

Ações 006/008 (todas devolvem lista de avisos):
- `add_division`: `(roots, core, raw, names)`; espessura do Configurador ou própria (`data['thickness']`); `follow` (RN-17); `dv.add(...)[-1]`; `scene_divisions.apply(raw + [_raw_entry(nova, own_thickness)])` (espessura 0 salvo própria; material ""); `reflow_all`.
- `edit_division`: muda o dicionário cru do uid com as chaves do payload (exceto `uid`, inclusive `targets`, ignorado por `from_dict`) e `scene_divisions.apply` — sem `reflow_all`.
- `remove_division`, `remove_in_space` (sem removidos → aviso), `add_many` (só as novas por uid), `set_bays` (mantém dicionários crus, troca `space`/`offset`): `scene_divisions.apply` + `reflow_all`.
- `toggle_extra`: registro `create=True`; `value` grava; `enabled` diferente grava e, para `BASE_TOP_RECESSED`, remove (`KEEP`) ou restaura o `TOP`; `scene_extras.sync`.
- `set_back`: guarda (RN-28); `backs_from_dict` mesclado com `mode`/`setback`/`auto`; `insert` e fundo removido → `restore_part`; `set_back_recess(setback se RECESSED, senão 0)`; `reflow_all`.
- `library_opening`: centro do subvão; vãos de `opening_boxes` que o contêm (folga 1e−4); menor área frontal.
- `insert_doors`, `insert_drawers` (RN-24, RN-25) via `_front_steps` = `edit('FRONT')` + `edit('STYLE')` se estilo + `edit('PULL', posição DEFAULT, all_fronts False)` se puxador.
- `insert_interior` (RN-26) → `scene_interiors.apply(atuais + nova)`; `remove_interior` filtra por `slot`.
- `insert_slides` → `scene_slides.apply({item, leaves, invert})`; avisos `('BLOCKED', folha, contato)` → "{} não corre: esbarra em {}" (contato vazio → "—"); demais → "Os trilhos precisam de mais profundidade ({})". `remove_slides` → `apply({})`.

### F-07 `divisions.resolve(roots, divisions)` 🟢

`spaces = dict(roots)`; percorre as divisões ordenadas por `(nº de pontos de space, space)` (estável); folha ausente → órfã; `_split`: no eixo, `cut0 = lo + offset`, `cut1 = cut0 + t`; `a` = `[lo, cut0]`, `b` = `[cut1, hi]`, chapa = `[cut0, cut1]` (Y e o outro eixo inteiros). SPACER: `spaces[space] = b` se `b ≥ a` no eixo, senão `a`; demais: apaga `space` e cria `.a`, `.b`. `cuts[uid] = (subvão, chapa)`. Devolve `(spaces, cuts, orphans)`.

### F-08 Componentes externos 🟢

`remove_part(data)`: `caps = structure_caps(root)[role]`; ausente ou `caps['remove']` → `[motivo ou NO_LIBRARY_REASON]`; `mode, reason = allowed_mode(mode, caps['modes'])`; já removido → `[]`; grava `removed, mode`; avisos = `[reason]` + `adapter.remove_part(role, mode)`; `reflow(force)`. `restore_part`: sem registro removido → `[]`; grava `removed False, mode KEEP`; `adapter.restore_part(role, modo antigo)`; `_tidy`; `reflow(force)`. `edit_part`: `thickness` → `caps['thickness']` com motivo recusa toda a edição; diferente > 1e−9 → grava e `set_part_thickness`; `material` grava; `reaffirm`; `_tidy`; `reflow(force)`. `_apply_structure(a, b)` por papel diferente: removido em `a` e (não removido em `b` ou modo diferente) → restaura; espessura/material diferentes → `edit_part`; removido em `b` e não (removido em `a` com o mesmo modo) → `remove_part`.

### F-09 `structure.layout` 🟢

`w2 = L/2`; `t[p]` = 0 se removido em EXTEND/SHRINK, senão `thick[p]`; `x0 = −w2 + t.LEFT`, `x1 = w2 − t.RIGHT`, `z0 = t.BOTTOM`, `z1 = A − t.TOP`; `side_z = t.BOTTOM` se BASE senão 0; base em X = `(−w2, w2)` se BASE senão `(x0, x1)`. Caixas (Y de −P a 0): LEFT `(−w2, −P, side_z)–(−w2 + thick.LEFT, 0, A)`; RIGHT espelhada; BOTTOM `(bx0, −P, 0)–(bx1, 0, thick.BOTTOM)`; TOP `(x0, −P, A − thick.TOP)–(x1, 0, A)`; BACK `(x0, −thick.BACK − setback, z0)–(x1, −setback, z1)`. Presentes = não removidas. Vão = `(x0, −P, z0)–(x1, −t.BACK − (setback se t.BACK > 0), z1)`.

### F-10 `extras.layout(box, t, settings, ceiling)` 🟢

Ordem: Base Superior Recuada `(x0+t, y0+0,02, z1−t)–(x1−t, y1, z1)` `BAS`; pés (se FEET ligado) nos cantos `(x0+0,05, y0+0,05)`, `(x1−0,05, y0+0,05)`, `(x0+0,05, y1−0,05)`, `(x1−0,05, y1−0,05)` = slots 1–4, pulando slot com `enabled False`, caixa ±0,02 de `z0 − pés` a `z0`, `PE_PLASTICO`; altura do rodapé = pés (padrão 0,15); rodapé frontal (KICK_FRONT e/ou KICK_GRANITE com material `GRANITO`) `(x0, y0+0,05, z0−h)–(x1, y0+0,05+t, z0)` `ROD`; laterais KICK_LEFT/RIGHT de `y0+0,05` a `y1`; fechamentos (largura `value`) por fora dos dois lados, slots 1 e 2, `TAMPON`; vistas `ESP` na ordem LEFT, RIGHT, FRONT, TALL_LEFT, TALL_RIGHT, TALL_FRONT: FRONT = faixa em cima `z1` a `z1 + w` (alta: até `max(teto, z1)`); LEFT/RIGHT por fora, de `z0` a `z1` (alta: até `max(teto, z1)`), profundidade `t` na frente.

### F-11 `slides.layout(space, leaves, style_id, invert)` 🟢

`n = int(leaves)`; `largura = ((x1 − x0) + (n − 1)·0,030)/n`; folha i em `lx0 = x0 + i·(largura − 0,030)`, trilho `n−1−i` se invertido senão `i`, `y = y0 + trilho·0,020` a `+0,018`, `z` de `z0 + 0,010` a `z1 − 0,010`; rasgo (estilo `groove`): folha 0 `(borda direita − 0,020, borda direita)`, demais `(borda esquerda, + 0,020)`. Trilhos: `(x0, y0, z0)–(x1, y0 + n·0,020, z0 + 0,010)` e o espelho no topo.

### F-12 `appliances.layout(space, item_id, thickness)` 🟢

`built_in = filter == 'BUILT_IN'`; painel Y `(y0 + t, y0 + 2t)` embutido ou `(y0 − t, y0)` externo, na largura e altura do vão. Com `appliances` no item ou `VENT`: recorte centrado `(w, h)` = `VENT_SIZE` ou (maior largura, soma das alturas) em mm·0,001, na espessura do painel; eletros empilhados de baixo para cima em ordem inversa da tupla: com `('OVEN', 'MICRO')` o **micro fica embaixo e o forno em cima** (o comentário do código diz "forno embaixo", o que o laço não faz) _(Revisão 2026-10-10: appliances.py:57-61, `for code in reversed(codes)` começa por MICRO em `bottom = cz − h/2`)_ (🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-47):** forno embaixo, como diz o comentário: trocar `reversed(codes)` por `codes`. Pendência de implementação: DT-06), atrás do painel (`y` de `py1` a `py1 + profundidade`). Item que é eletro solto (`OVEN`, `MICRO`, `COFFEE`): sem painel, eletro centrado em X, no chão do vão, a partir de `y0`. Painel sem recorte (`FRONT_*`): só o painel.

### F-13 `scene_divisions.reflow(context, root, force=False)` 🟢

Sem divisões → apaga `btm_division_sig` e devolve `[]`. Senão `(material, t) = configured`; `spaces = roots`; assinatura = JSON (vãos com `lo + hi` a 6 casas, crus, material, `round(t, 6)`); igual e não `force` → `[]`. `resolve`; para cada divisão com objeto e corte: `_place(obj, place(chapa, divisão), orientação, material da divisão or do Configurador)` — VERTICAL gira −90° em Y com `Length` = Z, `Width` = Y, `Thickness` = X, `Mirror Z` True; HORIZONTAL sem rotação com `Length` = X, `Width` = Y, `Thickness` = Z; grava `RAW_MATERIAL_PROP`; `update_tag`. Grava a assinatura e devolve os órfãos.

### F-14 `scene_slides.apply(context, root, wanted)` 🟢

`clear`; vazio → `[]`; sem vãos-raiz → `["sem vão interno"]`; vão = `spaces[min(spaces)]`; falta profundidade → `["profundidade {need:.3f}"]`; trilhos `make_box` (`SLIDE_TRACK`, `TRILHO_INF/SUP`); `view_layer.update`; `create_group(trilhos, 'FRAME', "Deslizantes")` com `btm_slides = {item, leaves, invert}`; cada folha `make_part` "Folha Deslizante {i+1}" (`SLIDE_LEAF`, `POR`, slot i) → grupo `LEAF` "Folha {i+1}" reparentado ao FRAME mantendo a matriz de mundo; `make_leaf(sash, frame, 'SLIDE', slide_dir = POS_X se o meio da folha < centro do vão senão NEG_X, travel=0.5)`; `measure_free_travel < 0,010` → `('BLOCKED', nome, contato)`; reaplica `opens[i] > 0`.

### F-15 `_arrow(context, s, root, axis, direction)` 🟢

Sem divisória selecionada (objeto filho direto com `is_division`) → `s.error` "Selecione uma divisória na vista para mover com as setas" (apagado em seguida por `process`, EC-01; 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-85):** preservar; DT-08); eixo incompatível → nada; divisão órfã → nada; `first = last_moved != uid`; `offset = step_move(subvão, divisão, sentido, ui.step, ui.step_initial, first)`; `last_moved = uid`; `refresh(edit('EDIT_DIVISION', {uid, offset}))`; `reflow(force=True)`.

### F-16 Desenho (`window.draw_editor`) 🟢

Handler `POST_PIXEL` global em `SpaceImageEditor` só na área do editor. `ensure_view`: `rect = (0, 0, visible_width, região.altura)`; chave `(rect, bounds a 4 casas)` (bounds padrão `(0,0,1,1)`); mudou → `View2D(rect).fit(bounds, margin=0.18)` (o zoom do usuário se perde, EC-11). Ordem: fundo `(0.13, 0.13, 0.14)`; peças em `draw_order` (vão = retângulo tracejado `OPENING_EDGE`; demais `draw.box` com preenchimento `FILL[kind]` e borda `FLAGGED` vermelha se há mensagem com o nome, senão `EDGE`); `_draw_006` (removidas tracejadas + "removido"; subvão alvo preenchido e contornado com rótulo; demais subvãos tracejados só na aba Divisões); linhas de abertura das frentes que não são gaveta pelo nome (`_hinge`: `flip`/`bascul` → topo; `right`, `_r` nos 4 últimos caracteres ou `direit` → direita; senão esquerda); abas Gavetas/Portas: vão da biblioteca contornado (`LIBRARY_EDGE`) com aviso "A frente ocupa o vão inteiro da biblioteca" se maior que o subvão (> 0,1 mm); seleção contornada; textos; `_labels` (largura embaixo, altura à direita, título "{raiz} — L × A × P", "Rascunho alterado"/"Sem alterações" e "— corrija os erros para confirmar" em vermelho); barra de 24 px "Selecionado: {peça | rótulo do vão | (nenhum)}".

## Painéis 🟢

Todos `IMAGE_EDITOR`/`UI`, categoria `EDITOR_CATEGORY = "Editor de Armário"`, `poll` = `window.is_editor_area` (abas: e `tab == TAB`).

| Painel (`bl_idname`) | Ordem | Aba | Conteúdo |
|---|---|---|---|
| `BTM_PT_cabinet_editor_tabs` | 0, sem cabeçalho | todas | "Tipo: {tipo} · {biblioteca}" (`cabinet_type`), estado (Rascunho alterado/Aplicado/Sem alterações), abas só ícone, nome da aba, `s.error` |
| `BTM_PT_cabinet_editor_dimensions` "Definições" | 1 | STRUCTURE | `bays`, medidas com alerta por `dim_messages` e "faixa: lo – hi" |
| `BTM_PT_cabinet_editor_structure` "Componentes" | 2 | STRUCTURE | Montagem (CAFFMob, escreve direto em `btm_cabinet.assembly`), linhas `comp_<papel>` + ✎ + ▾, árvore de extras (`layout.panel` recolhível), aviso de face frame |
| `BTM_PT_cabinet_editor_position` | 3 | STRUCTURE | `pos_*`, habilitado só com divisória selecionada |
| `BTM_PT_cabinet_editor_movement` | 4, fechado | STRUCTURE | `step_initial`, `step` |
| `BTM_PT_cabinet_editor_materials` | 5, fechado | STRUCTURE | Material de grupo / das frentes do vão |
| `BTM_PT_cabinet_editor_division_new` | 1 | DIVISIONS | Alvo, chapa do Configurador, modo, tipo, contagem, catálogo, recuos, Inserir, propriedades |
| `BTM_PT_cabinet_editor_division_list` | 2 | DIVISIONS | Linhas com editar/remover |
| `BTM_PT_cabinet_editor_library_interior` | 3, fechado | DIVISIONS | Interior da biblioteca (motivo de `capabilities()['INTERIOR']`) |
| `BTM_PT_cabinet_editor_drawers` / `_interior` / `_doors` / `_sliding` / `_backs` | 1, sem cabeçalho | DRAWERS/INTERIOR/DOORS/SLIDING/BACKS | Alvo, opções, grade de catálogo (2 colunas, `scale_y` 2,6, miniatura ou `MESH_PLANE`, apagado se não cabe), Inserir com motivo, propriedades ("Não há propriedades disponíveis"); Fundos escreve direto `auto_back`/`back_setback` |
| `BTM_PT_cabinet_editor_messages` | 90 | todas | Mensagens ordenadas ou "Sem erros nem avisos" |
| `BTM_PT_cabinet_editor_adjustments` | 91, fechado | todas | Até 30 ajustes + "… e mais N" |
| `BTM_PT_cabinet_editor_confirm` | 99, sem cabeçalho | todas | Desfazer/Refazer, aviso de erro, OK/Cancelar/Aplicar, Fechar, Salvar como módulo |

## Divergências entre artefatos anteriores e o código

- 🟢 `code-analysis.md` §14 fala em "25 ações de edição"; o código tem 23 (`EDIT_006` 7 + `EDIT_008` 11 + 5 da 003).
- 🟢 `code-analysis.md` §14.9 diz "Todo `set` só enfileira um pedido `edit`"; a montagem e os campos `auto_back`/`back_setback` são escritos direto pelos painéis (EC-03), e `SET_ASSEMBLY` não tem quem o enfileire. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-42):** enfileirar `SET_ASSEMBLY` (DT-01).
- 🟢 `code-analysis.md` §14.13 e o fluxograma `cabinet_editor-modal_process.md` dizem "Esc = Fechar" sem condição; o Esc só é tratado com o mouse dentro da região da vista e fora do painel lateral (EC-10).
- 🟢 `state-machines.md` (Editor de armário) mostra "Editando → Restaurado : Cancelar ou fechar janela" sem considerar que pedidos pendentes são descartados no OK/Cancelar (EC-02) e que a montagem não é restaurada (EC-03). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-43):** OK executa a fila antes de encerrar (DT-02); 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-42):** Cancelar restaura a montagem (DT-01).
- 🟢 `code-analysis.md` §14.6 descreve os itens com/sem recuo como "trás 15"; o payload não usa o recuo de trás do item (EC-06). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-46):** vale o catálogo (DT-05).
