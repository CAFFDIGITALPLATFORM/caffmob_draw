# Biblioteca CAFFMob (library_panel) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/library_panel/` em 2026-10-10 (sem alterações pendentes na pasta). IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`/`gpu`/`blf`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `categories_core.py` | não (`json`, `data.i18n`) | Categorias fixas, validação, (de)serialização, migração de pastas | 🟢 |
| Núcleo puro | `models_core.py` | não (`json`, `pathlib`, `data.i18n`) | Catálogo de modelos prontos | 🟢 |
| Núcleo puro | `layout_core.py` | não (`data.i18n.N_`) | Itens do menu, retângulos e acerto | 🟢 |
| E/S | `categories.py` | não diretamente; usa `customize.library_io.modules_root()` (que usa `bpy`) | `categories.json` em disco com cache | 🟢 |
| Estado | `props.py` | `bpy` | `WindowManager.btm_library` | 🟢 |
| Apresentação | `draw.py` | `bpy`, `gpu`, `blf`; `hb_gpu_draw` | Handler `POST_PIXEL`, cache de layout | 🟢 |
| Eventos | `ops_click.py` | `bpy` | Keymap e operadores de clique/hover/Esc | 🟢 |
| UI nativa | `popover.py`, `ops_categories.py`, `ops_cabinet.py` | `bpy` | Popover, diálogos e inserção | 🟢 |

🟢 Registro (`__init__.py:_modules`): `props, popover, ops_categories, ops_cabinet, ops_click, draw`; `unregister` em ordem inversa. O pacote principal chama `library_panel.register()` logo depois de `legacy.register()` e `library_panel.unregister()` logo antes de `legacy.unregister()` (`caffmob_draw/__init__.py:309/358`).

## Interface

### Estado — `props.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `BTM_PG_LibraryState` | `open: BoolProperty(default=False)`; `category: StringProperty()`; `line: StringProperty(default='COZ')` | 🟢 |
| `WindowManager.btm_library` | `PointerProperty(type=BTM_PG_LibraryState)`; removida no `unregister` se existir. Por ser do `WindowManager`, não é salva no `.blend` | 🟢 |

### `categories_core.py`

| Símbolo | Assinatura / valor | Observação | Confiança |
|---|---|---|---|
| `Category` | `namedtuple('Category', 'name line fixed')` | — | 🟢 |
| `LINES` | `('COZ', 'DOR', 'BAN', 'SAL', 'ESC')` | RN-02 | 🟢 |
| `LINE_LABELS` | `{'COZ': "Cozinha", 'DOR': "Dormitório", 'BAN': "Banheiro", 'SAL': "Sala", 'ESC': "Escritório"}` (marcados `N_`) | ordem de inserção define os itens dos enums | 🟢 |
| `FIXED` | `(Cozinha/COZ, Banheiro/BAN, Sala/SAL, Home office/ESC)`, `fixed=True` | RN-01 | 🟢 |
| `DEFAULT_LINE`, `SCHEMA_VERSION` | `'COZ'`, `1` | — | 🟢 |
| `EMPTY`, `REPEATED`, `INVALID_CHAR` | "Digite um nome para a categoria", "Já existe uma categoria com esse nome", "O nome não pode ter / nem \\" (msgids `N_`) | traduzidos por quem reporta | 🟢 |
| `all_categories(user)` | `list(FIXED) + list(user)` | — | 🟢 |
| `_key(name)` | `name.strip().casefold()` | chave de unicidade | 🟢 |
| `validate_name(name, user)` | `None` ou msgid | F-01; RN-03 | 🟢 |
| `parse(text)` | `(list[Category], list[str])` | F-02; avisos já traduzidos (`tr`) | 🟢 |
| `dump(user)` | `json.dumps({"schema-version": 1, "categories": [{"name", "line"}]}, ensure_ascii=False, indent=2)` | — | 🟢 |
| `merge_folders(user, folders)` | nova lista | RN-05; ignora nomes iniciados por `.` | 🟢 |
| `with_line(user, name, line)` | nova lista com `fixed=False` | casa por `_key`; não valida `line` | 🟢 |

### `categories.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `FILE_NAME` | `"categories.json"` | em `library_io.modules_root()` | 🟢 |
| `_cache` | `[None]` ou `[(categorias, avisos)]` | módulo-global | 🟢 |
| `invalidate()` | `()` | `_cache[0] = None` | 🟢 |
| `_folders(root)` | `sorted` das subpastas; `OSError` → `[]` | — | 🟢 |
| `load()` | `() -> (list[Category], list[str])` | F-03 | 🟢 |
| `save(user)` | `(list[Category]) -> None` | F-04; propaga exceções | 🟢 |
| `create(name, line)` | `-> None | msgid` | F-05 | 🟢 |
| `set_line(name, line)` | `-> None` | `save(with_line(load()[0], name, line))` | 🟢 |
| `all_categories()` | `-> list[Category]` | fixas + `load()[0]` | 🟢 |
| `find(name)` | `-> Category | None` | igualdade **exata** de nome (não casefold) | 🟢 |

### `models_core.py`

| Símbolo | Assinatura / valor | Observação | Confiança |
|---|---|---|---|
| `Model` | `namedtuple('Model', 'id label cabinet_type width_mm door_swing shelves')` | — | 🟢 |
| `CABINET_TYPES` / `DOOR_SWINGS` | `('BASE','WALL','TALL')` / `('NONE','LEFT','RIGHT','DOUBLE','FLIP')` | — | 🟢 |
| `CATALOG` | `Path(__file__).resolve().parents[1] / "data" / "library_models.json"` | — | 🟢 |
| `parse(text)` | `(list[Model], list[str])` | JSON inválido → `([], ["Catálogo de modelos inválido"])`; F-06 | 🟢 |
| `load_default()` | `parse(CATALOG.read_text('utf-8'))`; `OSError` → `([], ["Catálogo de modelos não encontrado"])` | sem cache: relido a cada desenho do popover | 🟢 |
| `find(models, model_id)` | primeiro com `m.id == model_id` ou `None` | IDs repetidos: vale o primeiro | 🟢 |

Catálogo do pacote (`data/library_models.json`, `schema-version` 1) 🟢:

| id | label | cabinet_type | width_mm | door_swing | shelves |
|---|---|---|---|---|---|
| balcao_1p | Balcão 1 porta | BASE | 450 | LEFT | 1 |
| balcao_2p | Balcão 2 portas | BASE | 800 | DOUBLE | 1 |
| aereo_1p | Aéreo 1 porta | WALL | 450 | LEFT | 1 |
| aereo_2p | Aéreo 2 portas | WALL | 800 | DOUBLE | 1 |
| torre | Torre | TALL | 600 | DOUBLE | 4 |

🟢 Sem balcão gaveteiro: o módulo CAFFMob ainda não tem gavetas (docstring de `models_core.py`; D-16 da 012).

### `layout_core.py`

| Símbolo | Assinatura / valor | Observação | Confiança |
|---|---|---|---|
| `Layout` | `namedtuple('Layout', 'label items')`; `label = (x, y, w, h)`; `items = [(chave, (x, y, w, h))]` | pixels da região, Y para cima | 🟢 |
| `TITLE` | `"BIBLIOTECA CAFFMOB"` | sem tradução | 🟢 |
| Constantes | `MARGIN_X=8.0, MARGIN_Y=12.0, GAP=8.0, ROW_HEIGHT=24.0, ROW_GAP=2.0, PAD_X=12.0` | multiplicadas pela escala | 🟢 |
| Chaves | `'CREATE_CABINET'`, `'CREATE_CATEGORY'`, `'CONVERT_GROUPS'`, `"CAT:" + nome`; `'LABEL'` (só no `hit`) | — | 🟢 |
| `LABELS` | Criar armário / Criar categoria / Converter grupos antigos (`N_`) | — | 🟢 |
| `menu_items(category_names, offer_groups=False)` | `[(chave, rótulo)]` | RN-11 | 🟢 |
| `category_of(key)` | `key[4:]` se começa com `"CAT:"`, senão `None` | — | 🟢 |
| `panel_layout(x_min, y_max, scale, nav_right, is_open, items, text_width)` | `Layout` | F-07 | 🟢 |
| `hit(layout, px, py)` | `'LABEL'`, chave ou `None` | bordas inclusivas; rótulo testado antes | 🟢 |
| `bounds(layout)` | `(x, y, w, h)` envolvendo tudo | 🟢 sem consumidor no pacote (código morto; o clique fora usa `hit is None`) | 🟢 |

### `draw.py`

| Símbolo | Valor / assinatura | Observação | Confiança |
|---|---|---|---|
| `FONT_SIZE` | `11` (× `ui_scale`) | fonte `blf` 0 | 🟢 |
| Cores RGBA | `BG (0.13,0.13,0.14,0.95)`, `BG_HOVER (0.25,0.25,0.27,0.96)`, `BG_TITLE (0.20,0.43,0.70,0.98)`, `BORDER (1,1,1,0.14)`, `TEXT (0.90,0.90,0.90,1.0)` | rótulo azul; itens escuros; hover mais claro | 🟢 |
| `_handle`, `_mouse`, `_cache` | `[None]`; `{'pos': (-1,-1), 'region': 0}`; `{ponteiro_região: (chave, Layout)}` | módulo-globais | 🟢 |
| `_scale(context)` | `context.preferences.system.ui_scale`, `AttributeError` → `1.0` | — | 🟢 |
| `_nav_right(context, area)` | `None` se `viewport_hud._hud_enabled()` falso; senão `x + w` do widget `_NavButton` em `viewport_hud.compute_layout` (ou `None`) | importação tardia | 🟢 |
| `offer_groups()` | `legacy.groups.should_offer()`; `ImportError/AttributeError/OSError` → `False` | contrato em `_reversa_sdd/legacy/` RN-21 | 🟢 |
| `items(context)` | `[(chave, tr(rótulo))]` de `menu_items([c.name for c in categories.all_categories()], offer_groups())` | nomes de categoria também passam por `tr` | 🟢 |
| `layout(context, area, region)` | F-08 | compartilhado com `ops_click` | 🟢 |
| `draw_panel()` | F-09 | — | 🟢 |
| `tag_redraw(context)` | `tag_redraw()` em toda área `VIEW_3D` de todas as janelas | — | 🟢 |
| `register` / `unregister` | `SpaceView3D.draw_handler_add(draw_panel, (), 'WINDOW', 'POST_PIXEL')` uma vez / remove, zera `_handle` e limpa `_cache` | — | 🟢 |

### Operadores

| bl_idname | Classe | bl_label | bl_options | Propriedades | Poll | Confiança |
|---|---|---|---|---|---|---|
| `caffmob.library_click` | `BTM_OT_LibraryClick` | "Biblioteca CAFFMob" | `{'INTERNAL'}` | — | `_in_viewport` | 🟢 |
| `caffmob.library_hover` | `BTM_OT_LibraryHover` | "Biblioteca CAFFMob (hover)" | `{'INTERNAL'}` | — | `_in_viewport` | 🟢 |
| `caffmob.library_close` | `BTM_OT_LibraryClose` | "Fechar biblioteca" | `{'INTERNAL'}` | — | `_in_viewport` e `btm_library.open` | 🟢 |
| `caffmob.library_insert_model` | `BTM_OT_LibraryInsertModel` | "Inserir modelo" | `{'REGISTER','UNDO'}` | `model_id: String`; `line: String(default='COZ')` | — | 🟢 |
| `caffmob.library_category_create` | `BTM_OT_LibraryCategoryCreate` | "Criar categoria" | `{'REGISTER'}` | `name: String(name="Nome")`; `line: Enum(_LINE_ITEMS, default='COZ', name="Linha do padrão")` | — | 🟢 |
| `caffmob.library_category_set_line` | `BTM_OT_LibraryCategorySetLine` | "Trocar linha" | `{'REGISTER'}` | `category: String`; `line: Enum(_LINE_ITEMS, default='COZ')` | — | 🟢 |
| `caffmob.library_create_cabinet` | `BTM_OT_LibraryCreateCabinet` | "Criar armário" | `{'REGISTER','UNDO'}` | `cabinet_type: Enum[BASE "Balcão", WALL "Aéreo", TALL "Torre"]='BASE'`; `width: Float(0.8, min 0.1, max 3.0, DISTANCE, LENGTH)`; `assembly: Enum[LATERAL "Lateral passante", BASE "Base passante"]='LATERAL'`; `line: Enum(_LINE_ITEMS)='COZ'`; `open_editor: Bool(True, {'SKIP_SAVE','HIDDEN'})` | `context.mode == 'OBJECT'` | 🟢 |

🟢 `_LINE_ITEMS = [(code, label, "") for code, label in LINE_LABELS.items()]` em `ops_categories.py` e `ops_cabinet.py` (rótulos sem `tr` explícito no enum). `_in_viewport`: área `VIEW_3D`, região `WINDOW` e `WindowManager` com `btm_library`.

### Keymap (`ops_click.register`)

🟢 Em `wm.keyconfigs.addon` (se `None`, ex. modo background, registra só as classes): `km = keymaps.new(name='3D View', space_type='VIEW_3D')` e, com `head=True`:

| Operador | Evento | Valor | `any` |
|---|---|---|---|
| `caffmob.library_click` | `LEFTMOUSE` | `PRESS` | `True` |
| `caffmob.library_hover` | `MOUSEMOVE` | `ANY` | `True` |
| `caffmob.library_close` | `ESC` | `PRESS` | `False` |

🟢 Pares `(km, kmi)` guardados em `_addon_keymaps`; `unregister` remove cada `kmi` (ignora `ReferenceError`/`RuntimeError`) e depois as classes.

## Fluxo Principal

**F-01 — `validate_name(name, user)`** 🟢: `clean = (name or "").strip()`; vazio → `EMPTY`; contém `/` ou `\` → `INVALID_CHAR`; `_key(clean)` em `{_key(c.name) for c in FIXED + user}` → `REPEATED`; senão `None`.

**F-02 — `categories_core.parse(text)`** 🟢: (1) `(text or "").strip()` vazio → `([], [])`. (2) `json.loads`; `ValueError` → `([], [tr("Arquivo de categorias inválido; as categorias do usuário foram ignoradas")])`. (3) `items = data.get('categories', [])` se `data` é dict, senão `[]`. (4) Para cada item: não-dict ou `str(item.get('name',"")).strip()` vazio → aviso "Categoria sem nome ignorada"; `name` limpo repetido (fixas ou já aceitas, por `_key`) → "Categoria repetida ignorada: {}"; `line ∉ LINES` → "Linha desconhecida na categoria {}: usada Cozinha" e `COZ`; aceita `Category(name, line, False)`.

**F-03 — `categories.load()`** 🟢: (1) cache presente → devolve. (2) lê `<modules_root>/categories.json` (`utf-8`); `FileNotFoundError` → `""`; outro `OSError` → devolve `([], [str(exc)])` **sem cachear**. (3) `user, warnings = parse(text)`. (4) `merged = merge_folders(user, _folders(modules_root()))`. (5) `merged != user and not warnings` → `save(merged)`. (6) `_cache[0] = (merged, warnings)`; devolve.

**F-04 — `categories.save(user)`** 🟢: `os.makedirs(dir, exist_ok=True)`; `tempfile.mkstemp(dir=dir, suffix=".tmp")`; escreve `dump(user)`; `os.replace(tmp, path)`; `_cache[0] = (list(user), [])`. Em qualquer `BaseException`, apaga o temporário se existir e relança.

**F-05 — `categories.create(name, line)`** 🟢: `user = load()[0]`; motivo de `validate_name` → devolve; `os.makedirs(modules_root()/name.strip(), exist_ok=True)`; `save(user + [Category(clean, line if line in LINES else 'COZ', False)])`; devolve `None`. A pasta é criada antes da gravação e não é desfeita se `save` falhar.

**F-06 — `models_core.parse(text)`** 🟢: para cada item de `data['models']`: sem `id` → "Modelo sem identificador ignorado"; tipo inválido → "Modelo {}: tipo desconhecido"; frente inválida → "Modelo {}: frente desconhecida"; senão `Model(str(id), str(item.get('label', id)), tipo, max(0, int(width_mm or 0)), item.get('door_swing', 'NONE'), max(0, int(shelves or 0)))`; `label: null` vira "None" e `door_swing: null` já foi recusado como frente desconhecida. _(Revisão 2026-10-10: models_core.py:225-230 e sonda; texto anterior dizia `str(label or id)` e `door_swing or 'NONE'`)_ Valor não conversível por `int` levanta `ValueError`/`TypeError` (não capturado; EC-07).

**F-07 — `panel_layout`** 🟢: `s = float(scale)`; `row_h = 24s`; `pad = 12s`; `x = nav_right + 8s` se `nav_right` não é `None`, senão `x_min + 8s`; `top = y_max − 12s`; `label_w = text_width(TITLE) + 2·pad`. Fechado → `Layout((x, top−row_h, label_w, row_h), [])`. Aberto → `col_w = max(label_w, text_width(t)+2·pad para cada item)`; `y = top − row_h`; para cada item `y −= row_h + 2s` e retângulo `(x, y, col_w, row_h)`; rótulo vira `(x, top−row_h, col_w, row_h)`.

**F-08 — `draw.layout(context, area, region)`** 🟢: `state = wm.btm_library`; `entries = items(context)` só se aberto (senão `[]`); `x_min, _, _, y_max = hb_gpu_draw.get_visible_window_bounds(area)` (descontando ferramentas, painel N, cabeçalhos, prateleira de ativos); `key = (x_min, y_max, scale, open, tuple(entries), _nav_right(...))`; cache por `region.as_pointer()` com a mesma chave → devolve; senão `blf.size(0, 11·scale)` e `panel_layout(..., lambda t: blf.dimensions(0, t)[0])`, grava cache. Observação: `items()` e `_nav_right()` rodam a cada chamada mesmo com cache válido (a chave depende deles).

**F-09 — `draw_panel()`** 🟢: sai se área não é `VIEW_3D`, região não é `WINDOW` ou não há `btm_library`; `lay = layout(...)`; `mouse = _mouse['pos']` se `_mouse['region']` é a região atual, senão `(-1,-1)`; `hovered = hit(lay, *mouse)`; blend `ALPHA`; shader `gpu.shader.from_builtin('UNIFORM_COLOR')`; rótulo com `BG_HOVER` se hover, senão `BG_TITLE`, contorno `BORDER`; cada item `BG_HOVER`/`BG` + contorno; blend `NONE`; textos (`TITLE` e `tr` dos rótulos) em `x + 12·size/11`, centrados na vertical por `blf.dimensions`.

**F-10 — Clique (`BTM_OT_LibraryClick.invoke`)** 🟢: `key = hit(draw.layout(...), mouse_region_x, mouse_region_y)`. `None` → se aberto, fecha e `tag_redraw`; devolve `PASS_THROUGH`. Senão `dispatch(context, key)`, `tag_redraw`, `FINISHED`.

**F-11 — `dispatch(context, key)`** 🟢 (também usado por testes): `'LABEL'` → alterna `open`; se abriu, `categories.invalidate()`; retorna. Qualquer outro → `open = False` e: `CREATE_CABINET` → `_run("caffmob.library_create_cabinet")`; `CREATE_CATEGORY` → `_run("caffmob.library_category_create")`; `CONVERT_GROUPS` → `_run("caffmob.legacy_groups_convert")`; `CAT:<nome>` → `found = categories.find(nome)`, `state.category = nome`, `state.line = found.line or 'COZ'`, `popover.show(context, nome)`. `_run` só chama `operator('INVOKE_DEFAULT')` se `operator.poll()`; com poll falso nada acontece (sem mensagem).

**F-12 — Hover** 🟢: calcula o alvo atual e o anterior (`hit` na posição guardada, se da mesma região); atualiza `_mouse`; `region.tag_redraw()` só se mudou; sempre `PASS_THROUGH`.

**F-13 — Popover** 🟢: `show(context, category)` grava `_open['category']` e chama `wm.popover(_draw, ui_units_x=16)`. `_draw`: incrementa `_open['drawn']`; resolve a linha (`find` ou `COZ`); cabeçalho `row(align=True)` com `label(nome, icon='ASSET_MANAGER')` e "Linha: {rótulo traduzido}"; engrenagem `caffmob.library_category_set_line` (`icon='PREFERENCES'`, `category=nome`) só se `found` não é fixa; separador; "Modelos prontos"; `grid_flow(columns=2, align=True)` com um `caffmob.library_insert_model` por modelo (`text=tr(label)`, `icon='MESH_CUBE'`, `model_id`, `line`); avisos do catálogo com `icon='ERROR'`; separador; "Meus módulos"; `entries = [e for e in library_io.list_modules() if e["category"].casefold() == nome.casefold()]` (`OSError/ValueError` → "Biblioteca indisponível: {}" e retorna); vazio → dica inativa; coluna com `caffmob.module_insert(filepath=e["blend"])`, `text=e["name"]`, `icon='IMPORT'`.

**F-14 — Inserir modelo** 🟢: `load_default()`; `find` → `None` reporta ERROR e `CANCELLED`; `kwargs = {cabinet_type, line (válida ou 'COZ'), door_swing, shelves}` + `width = width_mm/1000` se `width_mm`; devolve o resultado de `bpy.ops.caffmob.cabinet_builder(**kwargs)` (contrato do builder em `_reversa_sdd/operators/`: cria no cursor 3D; aéreo com cursor em Z≈0 sobe à altura de instalação do padrão; seleciona e ativa o módulo).

**F-15 — Criar armário** 🟢: `invoke`: `line = state.line` se válida senão `COZ`; `assembly = standards.api.active_assembly(scene)`; `width = standard_defaults(context, line, cabinet_type).width` (de `operators/cabinet_builder.py`, que chama `standards.cabinet_defaults.defaults`, F-09 de `_reversa_sdd/standards/`); `invoke_props_dialog(title="Criar armário", confirm_text="Criar")`. `draw`: tipo (expandido), largura, montagem (expandido), linha e dica inativa "Altura {} · profundidade {} (do padrão)" recalculada a cada desenho pelo tipo/linha atuais (`units.unit_to_string`). `execute`: `cabinet_builder(cabinet_type, width, line, assembly)`; sem `'FINISHED'` → `CANCELLED`; se `open_editor` e `bpy.ops.caffmob.cabinet_editor.poll()` → `cabinet_editor('INVOKE_DEFAULT')`; `FINISHED`.

## Fluxos Alternativos

- 🟢 **Criar categoria** (`BTM_OT_LibraryCategoryCreate`): `invoke` zera `name` e abre `invoke_props_dialog(title="Criar categoria")`; `draw` mostra nome, linha e, se `draw.offer_groups()` ou `_has_legacy_groups()` (`legacy.groups.pending_files()` não vazio; exceções → `False`), um botão `caffmob.legacy_groups_convert` "Converter grupos antigos" (`FILE_REFRESH`). `execute`: motivo → WARNING `tr(motivo)` + `CANCELLED`; senão INFO "Categoria criada: {}", `draw.tag_redraw`, `FINISHED`.
- 🟢 **Trocar linha** (`BTM_OT_LibraryCategorySetLine`): `invoke` recusa fixa ou inexistente (WARNING + `CANCELLED`), pré-preenche `line` e abre diálogo com o nome como título; `execute` chama `categories.set_line` sem repetir a verificação (EC-08). Não chama `tag_redraw` (a linha não aparece no painel).
- 🟢 **Fechar por Esc** (`BTM_OT_LibraryClose.execute`): `open = False`, `tag_redraw`, `FINISHED`.
- 🟢 **Conversão de grupos**: o painel só invoca; a dispensa da oferta e a invalidação das categorias ficam em `legacy/ops.py` (F-08 de `_reversa_sdd/legacy/`).

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `customize.library_io` | `modules_root()` (pasta `modules` em `extension_path_user`, criada), `list_modules()` (lista `{name, category, blend, png, json, has_manifest}`); `caffmob.module_insert` insere o `.blend` | 🟢 |
| `operators.cabinet_builder` | `caffmob.cabinet_builder` (cria o módulo; propriedades não passadas vêm do padrão) e `standard_defaults(context, line, cabinet_type) -> (Defaults, definition)` | 🟢 |
| `standards.api` | `active_assembly(scene)` (`'LATERAL'` sem padrão) | 🟢 |
| `cabinet_editor` | `caffmob.cabinet_editor` (poll: há janela, sem sessão aberta e um módulo selecionado) | 🟢 |
| `legacy.groups` / `legacy.ops` | `should_offer()`, `pending_files()`, `caffmob.legacy_groups_convert` | 🟢 |
| `operators.viewport_hud` | `_hud_enabled()`, `compute_layout(context, area)`, `_NavButton` (membros privados) | 🟢 |
| `hb_gpu_draw` | `draw_rect(shader,x,y,w,h,color)`, `draw_rect_outline(...)`, `draw_text(font_id,x,y,size,color,text)`, `get_visible_window_bounds(area)` | 🟢 |
| `units` | `unit_to_string(unit_settings, valor)` na dica do diálogo | 🟢 |
| `data.i18n` | `tr`, `N_`; catálogo `data/translations/library.json` | 🟢 |

Consumidores 🟢: `caffmob_draw/__init__.py` (registro); `legacy/ops.py:BTM_OT_LegacyGroupsConvert.execute` (`categories.invalidate()`); testes `tests/test_library_*.py`, `tests/blender_012_library_ui.py`, `tests/blender_012_cabinet_standard_smoke.py`.

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Painel em GPU sempre registrado + keymap `head=True`, sem modal permanente (D-13) | `ops_click.py` docstring; roadmap 012 | 🟢 |
| Canto superior esquerdo da parte **visível**, à direita do botão de navegação do HUD (D-14) | `layout_core.py` docstring | 🟢 |
| Popover nativo `WindowManager.popover` em vez de galeria GPU (D-15) | `popover.py` | 🟢 |
| Modelos prontos como dado JSON para crescer sem código (D-16, "princípio III") | `models_core.py` docstring | 🟢 |
| Categorias fixas no código, do usuário em `categories.json` ao lado das pastas de módulos; pastas existentes migradas como COZ (D-17) | `categories.py` docstring | 🟢 |
| Criar armário por diálogo curto + editor aberto em seguida (D-18) | `ops_cabinet.py` docstring | 🟢 |
| Cache de disco/layout para não ler a cada quadro ("princípio IX") | `categories.py:_cache`; `draw.py` docstring | 🟢 |
| Biblioteca própria substitui as herdadas na UI (ADR 0006) | `adrs/0006-biblioteca-propria-e-gate-legado.md` | 🟢 |

## Estado Interno

- 🟢 Sessão (`WindowManager`, não salvo): `btm_library.open/category/line`.
- 🟢 Módulo-globais: `categories._cache`, `draw._handle/_mouse/_cache`, `ops_click._addon_keymaps`, `popover._open = {'category', 'drawn'}` (`drawn` só serve aos testes de UI).
- 🟢 Disco: `<modules_root>/categories.json` e uma pasta por categoria criada.
- 🟢 Cena: nada próprio; os módulos são criados pelo `cabinet_builder`/`module_insert`.

## Observabilidade

- 🟢 `self.report`: INFO "Categoria criada: {}"; WARNING com motivo de nome ou "Só as categorias do usuário trocam de linha"; ERROR "Modelo não encontrado: {}". Avisos do catálogo e "Biblioteca indisponível" aparecem no popover.
- 🟢 Avisos de leitura de `categories.json` (`load()[1]`) não são mostrados em lugar nenhum do pacote (EC-02).
- 🟢 Sem logs persistentes.

## Riscos e Lacunas

- 🟢 Coluna sem rolagem nem limite de altura (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-88):** limitar a coluna à altura visível e, acima disso, agrupar as categorias do usuário num item "Mais…" que abre um popover (sem rolagem em GPU). Pendência de implementação: DT-03.
- 🟢 Estado global por processo com várias janelas/viewports; `_mouse` guarda uma única região. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-89):** aceito por ora o estado único por `WindowManager` com várias viewports/janelas (uso típico é uma viewport); ordem do keymap com o HUD: 🟡 decisão: testar (DT-04).
- 🟢 Pasta da categoria e pasta de gravação de módulos podem divergir para nomes com caracteres que `customize.manifest.file_stem` troca (EC-04). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-57):** `validate_name` recusa os mesmos caracteres que `customize.manifest.file_stem` troca (e ponto final), evitando a divergência de pasta e a falha no Windows. Pendência de implementação: DT-01.
- 🟢 `bounds()` sem consumidor.
- 🟢 Divergências com artefatos anteriores _(Revisão 2026-10-10: (a) state-machines.md:214-226; (b) roadmap 012 D-15 linha 85; (c) domain.md:349-351; (d) corrigido abaixo)_: (a) _(Revisão cruzada 2026-10-10: corrigido em state-machines.md)_ `state-machines.md` › "Biblioteca lateral" descrevia "clicar categoria" abrindo o painel e "clicar mesma categoria" fechando; no código o rótulo alterna e **qualquer** item fecha o painel antes de agir, e o painel fica no topo, não na lateral; (b) D-15 da 012 cita `ui/my_modules.py` como fonte dos módulos do popover; o código usa `customize.library_io.list_modules()` direto; (c) `domain.md` RN-LIBRARY_PANEL-01..03 e `code-analysis.md` §17 citam faixas de linhas levemente deslocadas (ex. `draw.py:85–119`), sem divergência de conteúdo; (d) `data/translations/library.json` não tem o msgid "BIBLIOTECA CAFFMOB" isolado, só frases que o contêm ("Clique no painel BIBLIOTECA CAFFMOB" etc.); o título não é traduzido (RN-16). _(Revisão 2026-10-10: grep em data/translations: nenhuma chave exata; texto anterior dizia que o msgid existia)_
