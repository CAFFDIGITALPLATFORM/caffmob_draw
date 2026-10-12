# Bibliotecas herdadas: porta e conversão (legacy) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído em 2026-10-10 de `caffmob_draw/legacy/` (7 arquivos, sem alterações sem commit) e dos pontos de integração lidos nos consumidores. IDs RN/RF/CA são os de `requirements.md`; EC-xx de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Fluxogramas complementares: `_reversa_sdd/flowcharts/legacy.md`, `legacy-translate.md`, `legacy-convert_scene.md`, `legacy-groups.md` (conferidos contra o código, sem divergência); os `legacy-<unit HB>-*.md` pertencem às units do HB5. ADR: `adrs/0006-biblioteca-propria-e-gate-legado.md`.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Porta | `legacy/gate.py` | sim (`bpy.context` por padrão) | Visibilidade da UI herdada e detecção de raízes | 🟢 |
| Núcleo puro | `legacy/convert_core.py` | não (só `data.i18n.N_`) | Tradução armário → campos `btm_cabinet` + perdas | 🟢 |
| Integração com a cena | `legacy/convert.py` | sim (`bpy`, `mathutils`) | Leitura, construção, exclusão em lote, relatório | 🟢 |
| Núcleo puro | `legacy/groups_core.py` | não (só `json`) | Pendentes, marcador, nome de destino | 🟢 |
| Integração com arquivos | `legacy/groups.py` | sim | Grupos salvos: carregar, converter, salvar, limpar; marcador em disco | 🟢 |
| Interface | `legacy/ops.py` | sim | 2 operadores e o aviso por timer | 🟢 |
| Ciclo de vida | `legacy/__init__.py` | sim | Neutralização, `load_post`, registro | 🟢 |

🟢 `caffmob_draw/__init__.py` chama `legacy.register()` depois da seleção por componente (011) e antes de `library_panel.register()`; `legacy.unregister()` logo depois de `library_panel.unregister()`. Imports dos colaboradores são tardios (dentro das funções), exceto `gate`, `convert_core` e `groups_core` entre si e `convert` em `ops.py`. _(Revisão 2026-10-10: ops.py:14 importa convert e gate no topo)_

## Interface

### `legacy/gate.py`

| Símbolo | Valor / assinatura | Observação | Confiança |
|---|---|---|---|
| `LEGACY_LIBRARIES` | `frozenset({'FRAMELESS', 'FACE_FRAME', 'CLOSETS'})` | Valores de `classify.module_library` | 🟢 |
| `_preferences(context)` | `context.preferences.addons.get(pacote).preferences` ou `None` | Pacote = `__package__.rsplit('.', 1)[0]` (ex.: `caffmob_draw` ou o nome da extensão instalada) | 🟢 |
| `legacy_ui(context=None) -> bool` | `bool(getattr(prefs, 'show_legacy_libraries', False))` | `context or bpy.context` | 🟢 |
| `is_legacy(obj) -> bool` | `classify.module_library(obj) in LEGACY_LIBRARIES` | Só raízes (objeto com a tag), não peças | 🟢 |
| `legacy_roots(scene) -> list[Object]` | Raízes de `scene.objects` sem ancestral herdado | O(objetos + raízes × profundidade) | 🟢 |

Preferência 🟢 `caffmob_draw/__init__.py:BTM_AddonPreferences`: `show_legacy_libraries: BoolProperty(name="Mostrar bibliotecas herdadas", description="Mostra a interface das bibliotecas frameless, face frame, closets e de molduras, que foram substituídas pelos armários CAFFMob. Use só para suporte ou para comparar uma conversão", default=False)`, desenhada no grupo "Avançado" (`advanced.prop(self, "show_legacy_libraries")`).

### `legacy/__init__.py`

| Símbolo | Valor / assinatura | Observação | Confiança |
|---|---|---|---|
| `NEUTRAL_TAB` | `'FRAMELESS'` | Valor de fábrica do enum `home_builder.product_tab`; com ele os keymaps herdados (que exigem FACE FRAME ou CLOSET) ficam inertes (D-04 da 012) | 🟢 código / 🟢 face frame: o overlay e o keymap de clique exigem `product_tab == 'FACE FRAME'` / 🟡 closets: nenhum gate por `product_tab` encontrado _(Revisão 2026-10-10: product_libraries/face_frame/dim_edit_overlay.py:_active_mode)_ |
| `NEUTRAL_MODES` | `(('hb_frameless','frameless_selection_mode','Cabinets'), ('hb_face_frame','face_frame_selection_mode','Cabinets'), ('hb_closets','closet_selection_mode','Starters'))` | Arquivo salvo em "Parts" deixaria a caixa sem seleção pela 011 | 🟢 |
| `neutralize_product_tab(context=None) -> bool` | RN-04 | Import tardio de `gate` | 🟢 |
| `on_load_post(*_args)` | `@persistent`; F-01 | — | 🟢 |
| `_modules()` | `(ops,)` | Só `ops` tem classes | 🟢 |
| `register()` / `unregister()` | RN-25 | — | 🟢 |

### `legacy/convert_core.py` (puro)

| Símbolo | Valor / assinatura | Confiança |
|---|---|---|
| `LegacyOpening` | `namedtuple('LegacyOpening', 'front drawer_count shelves', defaults=(0, 0))` | 🟢 |
| `Loss` | `namedtuple('Loss', 'key count')` | 🟢 |
| `LegacyCabinet` | `@dataclass`: `library: str`, `cabinet_type: str`, `width: float`, `height: float`, `depth: float`, `line: str = ""`, `openings: list = field(default_factory=list)`, `shelves: int = 0`, `other_fronts: list = field(default_factory=list)` | 🟢 |
| `LINES` | `('COZ', 'DOR', 'BAN', 'SAL', 'ESC')` | 🟢 |
| `TALL_FROM` | `1.2` (m) | 🟢 |
| Chaves de perda | `TYPE_APPROX='TYPE_APPROX'`, `DRAWERS='DRAWERS'`, `PANEL='PANEL'`, `SPECIAL_FRONT='SPECIAL'`, `EXTRA_DOORS='EXTRA_DOORS'` | 🟢 |
| `LOSS_LABELS` | `N_("Tipo de armário aproximado")`, `N_("Gavetas")`, `N_("Painéis fixos")`, `N_("Frentes especiais (basculante de puxar, painel embutido, eletrodoméstico)")`, `N_("Portas além de duas")`; `convert.py` acrescenta `AGGREGATES: N_("Agregados presos ao armário")` por `setdefault` na importação | 🟢 |
| `_TYPES` | `{'BASE':'BASE','UPPER':'WALL','WALL':'WALL','TALL':'TALL'}` | 🟢 |
| `_DOORS` | `{'DOOR_LEFT':1,'DOOR_RIGHT':1,'DOUBLE_DOORS':2}` | 🟢 |
| `_type(cabinet) -> (tipo, aproximado: bool)` | RN-06 | 🟢 |
| `_line(cabinet) -> str` | RN-07 | 🟢 |
| `translate(cabinet) -> (dict, list[Loss])` | F-02; chaves do dict: `cabinet_type, width, height, depth, door_swing, shelves, line, assembly` | 🟢 |

### `legacy/convert.py`

| Símbolo | Valor / assinatura | Observação | Confiança |
|---|---|---|---|
| `Result` | `namedtuple('Result', 'legacy_name library module_name losses')` | Um por armário | 🟢 |
| `LIBRARY_LABELS` | `{'FRAMELESS': N_("Frameless"), 'FACE_FRAME': N_("Face frame"), 'CLOSETS': N_("Closets")}` | Cópia local (não a de `classify`) | 🟢 |
| `AGGREGATES` | `'AGGREGATES'` | Chave de perda extra | 🟢 |
| `SPECIAL_FACE_FRAME` | `('PULLOUT', 'TILT_OUT', 'INSET_PANEL', 'APPLIANCE')` | `face_frame_opening.front_type` | 🟢 |
| `_local_box(root) -> (Vector lo, Vector hi) \| None` | Cantos de `root.evaluated_get(bpy.context.evaluated_depsgraph_get()).bound_box`; `None` se `min(hi − lo) ≤ 1e-6` | 🟢 |
| `_cabinet_type(root, library) -> str` | RN-12 | 🟢 |
| `_openings(root) -> list[LegacyOpening]` | RN-13 | 🟢 |
| `_other_fronts(root, library) -> list[str]` | RN-13 | 🟢 |
| `read_cabinet(root) -> (LegacyCabinet, (lo, hi))` | Caixa: largura = Δx, profundidade = Δy, altura = Δz; `line = str(root.get('btm_line', ""))`; `shelves` do armário fica 0 | 🟢 |
| `Reading` | `namedtuple('Reading', 'name library cabinet box world parent collection aggregates')` | `world` = cópia de `matrix_world`; `collection` = `users_collection[0]` ou `context.collection`; `aggregates` = `len(component.own_aggregates(root))` | 🟢 |
| `_read(context, root) -> Reading` | — | 🟢 |
| `_build(context, reading) -> (Object, list[Loss])` | F-03 | 🟢 |
| `convert_scene(context, roots=None) -> list[Result]` | F-04 | 🟢 |
| `report_lines(results) -> list[str]` | RN-17 | 🟢 |

### `legacy/groups_core.py` (puro) e `legacy/groups.py`

| Símbolo | Valor / assinatura | Confiança |
|---|---|---|
| `SCHEMA_VERSION` | `1` | 🟢 |
| `pending(files, marker) -> list` | `files` menos `marker['converted']`, na ordem de `files` | 🟢 |
| `should_offer(files, marker) -> bool` | `bool(pending) and not marker.get('offered', False)` | 🟢 |
| `parse_marker(text) -> dict` | `json.loads(text or "")`; `ValueError` → `{}`; valida tipos (RN-20); devolve `{"offered", "converted"}` | 🟢 |
| `mark(marker, converted=()) -> dict` | `{"offered": True, "converted": anteriores + novos sem repetir}` | 🟢 |
| `dump_marker(marker) -> str` | `json.dumps({"schema-version": 1, "offered": bool, "converted": list}, ensure_ascii=False, indent=2)` (sem `\n` final) | 🟢 |
| `target_name(name, existing) -> str` | `name` se `name.casefold()` ∉ `existing`; senão menor `"<name> (n)"`, n ≥ 2, livre | 🟢 |
| `TARGET_CATEGORY` / `MARKER_FILE` | `"Geral"` / `"legacy_groups.json"` | 🟢 |
| `_DATA_KINDS` | `('objects','meshes','materials','node_groups','images','curves','collections','textures','lights','cameras','actions')` | 🟢 |
| `_offer_cache` | `[None]` (None = não calculado) | 🟢 |
| `invalidate()`, `group_items()`, `_marker_path()`, `read_marker()`, `write_marker(marker)`, `pending_files()`, `should_offer()` | RN-19 a RN-21; `read_marker` captura só `OSError` | 🟢 |
| `_snapshot() -> dict[str, set]` / `_cleanup(before, keep=())` | Conjuntos por tipo; remove na ordem de `_DATA_KINDS` o que não estava antes e não está em `keep`, ignorando `ReferenceError`/`RuntimeError` por bloco | 🟢 |
| `_existing_names() -> set[str]` | `casefold` dos nomes de `library_io.list_modules()` com `category == "Geral"` | 🟢 |
| `convert_group(context, name, filepath) -> (salvos, linhas, erro\|None)` | F-06 | 🟢 |
| `convert_pending(context) -> (salvos, linhas)` | F-07 | 🟢 |
| `dismiss()` | `write_marker(mark(read_marker(), []))` | 🟢 |

### Operadores (`legacy/ops.py`)

| `bl_idname` | Classe | `bl_label` | `bl_options` | Propriedades | `poll` | Confiança |
|---|---|---|---|---|---|---|
| `caffmob.legacy_convert` | `BTM_OT_LegacyConvert` | "Converter para CAFFMob" | `{'REGISTER','UNDO'}` | `only_active: BoolProperty(name="Só o armário selecionado", default=False, options={'SKIP_SAVE'})` | modo OBJECT, cena e `legacy_roots` não vazio | 🟢 |
| `caffmob.legacy_groups_convert` | `BTM_OT_LegacyGroupsConvert` | "Converter grupos antigos" | `{'REGISTER'}` | — | modo OBJECT | 🟢 |

🟢 Diálogos por `context.window_manager.invoke_confirm(self, event, title=…, message=…, confirm_text=tr("Converter"))`. Mensagens: "{n} armário(s) de bibliotecas antigas viram armários CAFFMob. Ctrl+Z desfaz." e "{n} grupo(s) salvos nas bibliotecas antigas viram módulos CAFFMob em Geral. Os arquivos originais ficam na pasta.". 🟢 `_show_report(context, title, lines)`: `operators.ops_standards._set_report(title, lines)` e, se não estiver em background e houver `context.window`, `bpy.ops.caffmob.standards_report('INVOKE_DEFAULT')` (relatório compartilhado com o Padrão de Dimensões, `_reversa_sdd/standards/`). Os nomes `caffmob.*` divergem da convenção `btm.*`/`caffmob_draw.*` do `CLAUDE.md` para código novo, como em `standards`.

## Fluxos

**F-01 — Abrir arquivo** 🟢 `__init__.py:on_load_post`: (1) `neutralize_product_tab()` (RN-04); (2) se `ops.notify_legacy` não está registrado, `bpy.app.timers.register(ops.notify_legacy, first_interval=1.0)` (depois da interface pronta, D-26). `notify_legacy`: `scene = bpy.context.scene`; `None` ou porta aberta → `None`; `count = len(legacy_roots(scene))`; `count > 0` → `save_feedback.show(texto)`; devolve `None` (o timer não se repete). Só a cena ativa é contada.

**F-02 — `translate(cabinet)`** 🟢 `convert_core.py`: (1) `_type` → tipo e se é aproximado (→ `TYPE_APPROX` 1); (2) `doors = 0`, `sides = []`, `flip = False`, `shelves = int(cabinet.shelves or 0)`; (3) para cada abertura: `shelves += int(opening.shelves or 0)`; `front ∈ _DOORS` → `doors += _DOORS[front]`, `sides.append(front)`; `FLIP_UP` → `flip = True`; `DRAWERS` → `DRAWERS += max(1, int(drawer_count or 0))`; `PANEL` → `PANEL += 1`; outra frente ∉ (`OPEN`, `''`, `None`) → `SPECIAL += 1`; (4) cada `other_fronts` → `SPECIAL += 1`; (5) `doors ≥ 2` → `DOUBLE` e `EXTRA_DOORS += doors − 2`; `doors == 1` → `LEFT` se `sides[0] == 'DOOR_LEFT'` senão `RIGHT`; senão `FLIP` se `flip` senão `NONE`; (6) `flip and doors` → `SPECIAL += 1`; (7) devolve `{cabinet_type, width, height, depth, door_swing, shelves, line: _line(), assembly: 'LATERAL'}` e `[Loss(k, n)]` na ordem de inserção.

**F-03 — `_build(context, reading)`** 🟢 `convert.py`: (1) `fields, losses = translate(reading.cabinet)`; `reading.aggregates > 0` → `losses.append(Loss('AGGREGATES', n))`; (2) `found, definition = cabinet_builder.standard_defaults(context, fields['line'], fields['cabinet_type'])` (medidas do padrão ativo, ver `_reversa_sdd/standards/` F-09); (3) `obj = build_module(context, width, height, depth` traduzidos`, carcass=found.carcass, cabinet_type, line, assembly=standards.api.active_assembly(context.scene), door_swing, shelves, role_thickness=found.thickness, definition=definition, collection=reading.collection)`; (4) o módulo CAFFMob vai de −largura/2 a +largura/2 em X, de −profundidade a 0 em Y e de 0 à altura em Z, então `world = reading.world @ Matrix.Translation(((lo.x + hi.x)/2, hi.y, lo.z))`; (5) `obj.parent = reading.parent`; com pai, `obj.matrix_parent_inverse = parent.matrix_world.inverted()`; (6) `obj.matrix_world = world`. Escala e rotação do original são herdadas pela matriz. Só `width/height/depth` do padrão **não** são usados: as medidas são as lidas do original.

**F-04 — `convert_scene(context, roots=None)`** 🟢: (1) `roots = list(roots)` ou `legacy_roots(context.scene)`; (2) filtra `root.name in bpy.data.objects and is_legacy(root)`; (3) `readings = [_read(…) para todas]` (uma avaliação da cena); (4) `built = [_build(…) para todas]`; (5) `delete_components(roots, keep_aggregates=False)` (011: solta itens grudados no lugar com aviso, tira furos de vãos, remove subárvores e agregados próprios por `bpy.data.batch_remove`; ver `_reversa_sdd/aggregates/`); (6) para cada par: `obj.name = reading.name` e `Result(reading.name, reading.library, obj.name, losses)`. Sem `try`: exceção em (3)–(5) sobe ao chamador (EC-05).

**F-05 — Operador `caffmob.legacy_convert`** 🟢: `invoke` → confirmação; `execute`: `only_active` → `classify.module_root(context.active_object)`; raiz `None` ou biblioteca ∉ `LEGACY_LIBRARIES` → WARNING + CANCELLED; senão `roots = [raiz]`. `results = convert_scene(context, roots)`; `lost = Σ(1 se result.losses)`; INFO "{n} armário(s) convertidos; {m} com perdas"; `_show_report(context, tr("Conversão para CAFFMob"), report_lines(results))`; FINISHED. Chamado com `only_active=True` por `ui/sidebar_selected._draw_legacy` e sem ele por `ui/sidebar_build` (caixa "N armário(s) de bibliotecas antigas").

**F-06 — `convert_group(context, name, filepath)`** 🟢: (1) `before = _snapshot()`; (2) `holder = bpy.data.collections.new("CAFFMob conversão")` ligada a `scene.collection`; (3) `try`: `bpy.data.libraries.load(filepath, link=False)` com `data_to.objects = list(data_from.objects)`; liga cada objeto não `None` ao `holder`; `context.view_layer.update()`; `roots = [o in holder.objects se is_legacy(o) e o in legacy_roots(scene)]`; `results = convert_scene(context, roots)`; `lines = ["Grupo <nome>"] + ["  " + linha do relatório]`; `modules = [bpy.data.objects[r.module_name] se existir]`; `existing = _existing_names()`; para cada módulo (índice a partir de 1): `base = name` (1 módulo) ou `f"{name} {i}"`; `target = target_name(base, existing)`; `existing.add(target.casefold())`; `paths, errors = library_io.save(context, module, target, "Geral")` (miniatura padrão); erros → linhas `"  <erro>"`; senão `saved.append(target)`; sem resultados → `"  nenhum armário de biblioteca antiga no grupo"`; (4) `except (OSError, RuntimeError)` → `error = "Não foi possível abrir o grupo {}: {}"`; (5) `finally`: `_cleanup(before, keep=(holder,))` e `bpy.data.collections.remove(holder)`. Outras exceções propagam depois da limpeza.

**F-07 — `convert_pending(context)`** 🟢: `marker = read_marker()`; `pending = set(groups_core.pending(caminhos de group_items(), marker))`; percorre `group_items()` de novo, na ordem do disco, pulando os não pendentes; acumula `saved` e `lines`; `error` → `lines.append(error)`; senão `done.append(path)`; no fim `write_marker(mark(marker, done))` → devolve `(saved, lines)`. `write_marker`: `tempfile.mkstemp(dir=pasta do marcador, suffix=".tmp")` → escreve `dump_marker` UTF-8 → `os.replace` → `invalidate()`.

**F-08 — Operador `caffmob.legacy_groups_convert`** 🟢: `invoke`: `count = len(pending_files())`; 0 → INFO + CANCELLED; senão `groups.dismiss()` e confirmação. `execute`: `convert_pending` → `library_panel.categories.invalidate()` → INFO "{n} módulo(s) salvos em Geral" → `_show_report(context, tr("Conversão dos grupos antigos"), lines)`. Chamado pelo item "Converter grupos antigos" do painel (`library_panel/ops_click.py`, quando `draw.offer_groups()` é verdadeiro) e pelo diálogo "Criar categoria" (`library_panel/ops_categories.py`, quando há oferta ou `pending_files()` não vazio).

## Dependências

- 🟢 `selection.classify` — `module_library`, `module_root`, `classify`, `MODULE_TAGS`; `selection.editing.get_dimension`; `selection.component.own_aggregates` (ver `_reversa_sdd/selection/`).
- 🟢 `customize.adapters.for_object` → adaptador com `read(root) -> spec.Spec` (`openings[*].front/drawer_count/interior.shelves`); `customize.library_io.modules_root/list_modules/save` (ver `_reversa_sdd/customize/`, ADR 0005).
- 🟢 `operators.cabinet_builder.standard_defaults/build_module` (grava `btm_line` e `btm_standard_uid`) e `standards.api.active_assembly` (ver `_reversa_sdd/standards/`, `_reversa_sdd/cabinet_editor/`).
- 🟢 `aggregates.ops_aggregate.delete_components` (ver `_reversa_sdd/aggregates/`).
- 🟢 `operators.ops_standards._set_report` e `caffmob.standards_report`; `ui.save_feedback.show`; `library_panel.categories.invalidate`; `data.i18n.tr/N_`.
- 🟢 Bibliotecas herdadas (só leitura): `product_libraries.frameless.operators.ops_library.get_user_library_items` (`_reversa_sdd/frameless/`); `Object.face_frame_cabinet.cabinet_type`, `Object.face_frame_opening.front_type`, tag `IS_FACE_FRAME_OPENING_CAGE` (`_reversa_sdd/face_frame/`); `Object.hb_closet_starter.closet_type` (`_reversa_sdd/closets/`); `Scene.home_builder.product_tab` e os grupos de cena herdados (`_reversa_sdd/hb_core/`); custom property `CABINET_TYPE` do frameless.
- 🟢 Preferência `BTM_AddonPreferences.show_legacy_libraries` (`caffmob_draw/__init__.py`).

### Consumidores

| Símbolo | Consumidores | Confiança |
|---|---|---|
| `gate.legacy_ui` | `selection/component_select.cabinet_modes`, `operators/viewport_hud` (2 pontos), `ui/sidebar_insert`, `ui/sidebar_selected`, `ui/context_menu._legacy_menu_hidden`, `ui/my_modules`, `ui/view3d_sidebar`, `ui/sidebar_project`, `ui/menus`, `ui/sidebar_build`, `standards/sync` (2 pontos), `legacy/groups.should_offer`, `legacy/ops.notify_legacy` | 🟢 |
| `gate.legacy_roots` | `ui/sidebar_build`, `standards/sync.scene_modules`, `legacy/convert`, `legacy/groups`, `legacy/ops` | 🟢 |
| `gate.LEGACY_LIBRARIES` | `ui/sidebar_selected._draw_legacy`, `ui/context_menu._legacy_menu_hidden`, `legacy/ops` | 🟢 _(Revisão 2026-10-10: ui/context_menu.py:46 faltava na lista)_ |
| `groups.should_offer` / `pending_files` | `library_panel/draw.offer_groups`, `library_panel/ops_categories._has_legacy_groups` (ambos capturam `ImportError`, `AttributeError`, `OSError`) | 🟢 |
| `legacy.neutralize_product_tab`, `register`, `unregister` | `caffmob_draw/__init__.py`; `tests/blender_012_legacy_gate_smoke.py` | 🟢 |

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Esconder em vez de remover: código herdado fica registrado para abrir arquivos antigos; remoção numa feature seguinte (012 RN-14, D-01) | `gate.py` docstring; ADR 0006 | 🟢 |
| Porta única por preferência, consultada por todos os pontos de entrada (princípio V citado na 012) | `gate.legacy_ui`; lista de consumidores | 🟢 |
| `product_tab` volta a `FRAMELESS` (valor de fábrica) em vez de um item novo no enum, para não mudar o enum gravado nos arquivos antigos (D-04) | `__init__.py` docstring | 🟢 |
| Leitura pelos adaptadores da personalização em vez de prompts/drivers (D-23, ADR 0005) | `convert.py:_openings` | 🟢 |
| Tradução pura com perdas declaradas e contadas (D-24, "princípio VIII") | `convert_core.py` | 🟢 |
| Ler tudo, construir tudo e apagar em lote (princípio IX) | `convert_scene` docstring | 🟢 |
| Grupo com vários armários vira um módulo por armário (a biblioteca guarda um módulo por arquivo) | `groups.py` docstring | 🟢 |
| Oferta única: abrir a confirmação já dispensa a oferta (D-30) | `ops.py:BTM_OT_LegacyGroupsConvert.invoke` | 🟢 |

## Estado Interno

- 🟢 Persistente no `.blend`: nada próprio; a conversão cria objetos `btm_cabinet` com `btm_line`/`btm_standard_uid` e apaga os herdados. A neutralização altera `Scene.home_builder.product_tab` e os modos de seleção herdados.
- 🟢 Em disco: `<modules_root>/legacy_groups.json`; módulos `.blend`/`.json`/`.png` gravados em "Geral" por `library_io.save`.
- 🟢 Sessão: `groups._offer_cache = [None|bool]`; timer `ops.notify_legacy` (uma execução por abertura); `convert_core.LOSS_LABELS` mutado na importação de `convert.py` (chave `AGGREGATES`).

## Observabilidade

- 🟢 `self.report` INFO/WARNING nos operadores; relatório em popup (`caffmob.standards_report`) e em `ops_standards._LAST_REPORT` (lido pela fumaça).
- 🟢 Aviso na barra de status e no console (`save_feedback.show` imprime "CAFFMob Draw: …").
- 🟢 Falhas silenciosas: exceção do leitor do adaptador (`_openings`), `OSError` em `group_items`/`read_marker`, `ReferenceError`/`RuntimeError` por bloco em `_cleanup`. Sem logs persistentes.

## Riscos e Lacunas

- 🟢 Sem rollback explícito do lote: erro em `_build` deixa módulos novos ao lado dos originais; um Ctrl+Z remove o módulo parcial e mantém os originais (EC-05). _(Revisão 2026-10-10: sonda com build_module falhando, xvfb-run)_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-54):** o lote ganha rollback: `try/except` no operador remove os módulos já criados, reporta ERROR com o nome do armário e devolve CANCELLED. Pendência de implementação: DT-01.
- 🟢 Relatório "sem perdas" não cobre frentes perdidas por falha do adaptador (EC-04), nem a troca de chapas/espessuras/montagem pelas do padrão ativo, nem a redistribuição de prateleiras. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-56):** a falha do adaptador vira perda declarada (uma linha "frentes não lidas"); a troca de chapas, espessuras e montagem pelo padrão ativo e a redistribuição de prateleiras ganham só uma nota geral no topo do relatório. Pendência de implementação: DT-03, DT-04.
- 🟢 Divergências entre o plano da 012 e o código _(Revisão 2026-10-10: conferidas em _reversa_forward/012-biblioteca-caffmob-chapas/roadmap.md D-24/D-29 e actions.md T067/T068)_: nota D-24 "várias aberturas: a maior manda; as outras são perda" vs. soma de portas (EC-02); D-29/T067 "cena temporária" e "grupo PLAIN se forem vários" vs. coleção temporária na cena atual e um módulo por armário; T068 prevê `caffmob.legacy_groups_dismiss`, que não existe (a dispensa ocorre no `invoke`); D-24 assina `translate(spec, line)`, o código é `translate(cabinet)`; 012 RN-13 fala em "montagem lateral passante", o código usa a montagem do padrão ativo; 012 RN-16 fala em "linha COZ" na categoria Geral, o módulo salvo mantém a linha traduzida (ex.: DOR para closets).
- 🟡 Pendência por caminho (sem hash/mtime): arquivo alterado no mesmo caminho não é reconvertido; pasta movida faz tudo voltar a pendente (EC-10).
