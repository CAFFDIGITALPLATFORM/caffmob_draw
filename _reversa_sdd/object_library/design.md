# Biblioteca de objetos (object_library) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/object_library/` em 2026-10-10 (sem alterações pendentes na pasta). IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `catalog.py` | não (`re`, `secrets`, `unicodedata`, `dataclasses`, `data.i18n.N_`) | Categorias, manifesto, id, busca | 🟢 |
| Núcleo puro | `store.py` | não (`json`, `os`, `dataclasses`, `catalog`) | Pastas, listagem, nome único, apagar, checagem de origem | 🟢 |
| Estado | `props.py` | `bpy` | `Object.btm_object_item`, `WindowManager.btm_object_library` | 🟢 |
| E/S de cena | `item_io.py` | `bpy`; `aggregates.group`, `library_common`, `customize.library_io` | Salvar e inserir | 🟢 |
| Materiais | `retexture.py` | `bpy`; `customize.adapters.common` | Acabamento e imagem própria | 🟢 |
| Miniaturas | `previews.py` | `bpy`, `bpy.utils.previews` | Coleção de ícones por caminho+mtime | 🟢 |
| UI | `panels.py` | não diretamente (recebe `layout`/`context`) | Funções de desenho chamadas pela barra lateral | 🟢 |
| Operadores | `ops.py` | `bpy`, `bpy_extras.view3d_utils`, `ImportHelper`, `mathutils` | 5 operadores | 🟢 |

🟢 Registro (`__init__.py:_modules`): `props, previews, ops` (importados de forma tardia dentro de `_modules`); `unregister` em ordem inversa. `panels.py`, `item_io.py`, `retexture.py`, `catalog.py`, `store.py` não registram nada. O pacote principal importa `object_library` (`caffmob_draw/__init__.py:41`), chama `object_library.register()` (linha 303) e `object_library.unregister()` (linha 363).

## Interface

### `catalog.py`

| Símbolo | Assinatura / valor | Observação | Confiança |
|---|---|---|---|
| `FORMAT`, `VERSION` | `"caffmob_draw.object_item"`, `1` | RN-02 | 🟢 |
| `BUNDLED_SOURCE` | `"CAFFMob Draw"` | origem dos embutidos | 🟢 |
| `FORBIDDEN_BUNDLED_SOURCE` | `"3D Warehouse"` | RN-09 | 🟢 |
| `CATEGORIES` | tupla de `(chave, rótulo N_, ícone)` na ordem de RN-01 | — | 🟢 |
| `CATEGORY_KEYS` | `tuple(c[0] for c in CATEGORIES)` | — | 🟢 |
| `CATEGORY_ITEMS` | `[(key, label, "", icon, i)]`, `i` = índice | itens de `EnumProperty`; rótulo não traduzido no item (o Blender traduz pela UI) | 🟢 |
| `FEATURES` | `('GROUP', 'FRAME', 'LEAF_SWING', 'LEAF_SLIDE', 'AGGREGATE', 'PRODUCTION_PART', 'TEXTURED')` | ordem canônica | 🟢 |
| `_ID` | `re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")` | — | 🟢 |
| `ManifestError` | `class ManifestError(ValueError)` | — | 🟢 |
| `Entry` | `@dataclass(item_id, name, category, root, source="", author="", license="", size_mm=[0.0,0.0,0.0], features=[], materials=[], created_at="", addon_version="")` | listas por `default_factory` | 🟢 |
| `slug(text)` | `-> str` | RN-03 | 🟢 |
| `new_item_id(name, token=None)` | `-> "{slug}-{token or secrets.token_hex(3)}"` | — | 🟢 |
| `read_manifest(data)` | `dict -> Entry`; `ManifestError` | F-01 | 🟢 |
| `to_manifest(entry)` | `-> dict` com as 14 chaves na ordem: `format, version, item_id, name, category, root, source, author, license, size_mm (floats), features, materials, created_at, addon_version` | inversa de `read_manifest` para entradas válidas | 🟢 |
| `search(entries, text)` | `-> list[Entry]` | RN-04 | 🟢 |

### `store.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `BUNDLED_DIR` | `os.path.join(os.path.dirname(__file__), "items")` | raiz embutida | 🟢 |
| `Item` | `@dataclass(entry: Entry, user: bool, blend: str, manifest: str, thumb: str = None)` | `manifest` = caminho do JSON lido | 🟢 |
| `paths_for(folder, category, item_id)` | `-> {"blend", "json", "png"}` = `<folder>/<category>/<item_id>.<ext>` | — | 🟢 |
| `_scan(folder, user, warnings)` | `-> list[Item]` | F-02 | 🟢 |
| `list_items(bundled_dir, user_dir)` | `-> (list[Item], list[str])` | embutidos + usuário; avisos compartilhados | 🟢 |
| `by_category(items, category)` | `-> [i for i in items if i.entry.category == category]` | RN-06 | 🟢 |
| `unique_name(existing, name)` | `-> str` | `name` se livre; senão `f"{name} {n}"`, `n` = 2, 3… o primeiro livre | 🟢 |
| `delete(item)` | `-> None`; `PermissionError("item embutido")` se `not item.user` | remove `base + ext` para `.blend, .json, .png, .blend1` existentes, `base = item.blend[:-6]`; `OSError` propaga | 🟢 |
| `check_bundled(entries)` | `-> list[item_id]` | `e.source.strip().lower().startswith("3d warehouse")` | 🟢 |

### Estado — `props.py`

| Símbolo | Definição | Confiança |
|---|---|---|
| `BTM_PG_ObjectItem` | `is_item: BoolProperty(default=False)`; `item_id: StringProperty(name="Id do item")`; `category: EnumProperty(name="Categoria", items=CATEGORY_ITEMS, default='OTHER')`; `source: StringProperty(name="Origem")`; `license: StringProperty(name="Licença")` | 🟢 |
| `Object.btm_object_item` | `PointerProperty(type=BTM_PG_ObjectItem)`; vai para o `.blend` (do projeto e do item) | 🟢 |
| `BTM_PG_ObjectLibraryUI` | `category: EnumProperty(items=CATEGORY_ITEMS, default='DOORS')`; `search: StringProperty(name="Buscar", description="Parte do nome do objeto", options={'TEXTEDIT_UPDATE'})` | 🟢 |
| `WindowManager.btm_object_library` | `PointerProperty(type=BTM_PG_ObjectLibraryUI)`; sessão, não salva no arquivo | 🟢 |

🟢 `unregister` apaga as duas propriedades (com `hasattr`) e desregistra as classes só se `is_registered`.

### `item_io.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `_extension_package()` | `-> __package__.rsplit('.', 1)[0]` | nome do pacote da extensão | 🟢 |
| `user_dir(create=True)` | `-> bpy.utils.extension_path_user(pacote, path="object_library", create=create)` | — | 🟢 |
| `all_items()` | `-> store.list_items(store.BUNDLED_DIR, user_dir(create=False))` | relê o disco a cada chamada | 🟢 |
| `_addon_version()` | delega a `customize.library_io._addon_version()` | importação tardia | 🟢 |
| `tree(root)` | `-> [root] + list(root.children_recursive)` | — | 🟢 |
| `root_of(obj)` | `-> Object | None` | sobe por `.parent` até o primeiro com `btm_object_item.is_item` | 🟢 |
| `prepare_root(objs, name)` | `-> Object | None` | RN-11; `tops = [o for o in objs if o.parent not in objs]`; se `len(tops) == 1` e (`group.is_group(tops[0])` ou `root_of(tops[0]) is tops[0]`) → `tops[0]`; senão `group.create_group([malhas de topo], 'PLAIN', name)` ou `None` | 🟢 |
| `features_of(objs)` | `-> list[str]` | F-03 | 🟢 |
| `existing_names(category)` | `-> [nome dos itens do usuário na categoria]` | — | 🟢 |
| `save(context, root, name, category, source="", license_text="", author="", replace_id=None, thumb=True, folder=None, item_id=None)` | `-> (store.Item | None, list[str])` | F-04 | 🟢 |
| `insert(context, item, location=None)` | `-> (root, loaded)`; `ValueError("Item corrompido: <nome>")` | F-05 | 🟢 |

### `retexture.py`

| Símbolo | Assinatura / valor | Comportamento | Confiança |
|---|---|---|---|
| `PACKAGE` | pasta `caffmob_draw/` | — | 🟢 |
| `LIBRARIES` | `product_libraries/frameless/frameless_assets/materials/cabinet_material.blend`, `product_libraries/face_frame/face_frame_assets/materials/cabinet_material.blend`, `product_libraries/closets/assets/materials/library.blend` | relativos a `PACKAGE`; ausentes são pulados | 🟢 |
| `PATH_PROP`, `SIZE_PROP` | `'btm_texture_path'`, `'btm_texture_size_mm'` | propriedades **ID** (`mat[...]`) no material, não `bpy.props` | 🟢 |
| `_names_cache` | `{}` módulo-global | `{nome do material: caminho do .blend}`; primeira biblioteca vence (`setdefault`); nunca limpo | 🟢 |
| `library_materials()` | `-> dict` | lê `data_from.materials` de cada `.blend` uma vez por sessão | 🟢 |
| `finish_names()` | `-> list[str]` | RN-16 | 🟢 |
| `_finish(name)` | `-> Material | None` | `bpy.data.materials.get(name)` ou append de `[name]` do `.blend` de origem | 🟢 |
| `targets(objs)` | `-> [o for o in objs if o.type == 'MESH']` | — | 🟢 |
| `apply_finish(objs, name)` | `-> int` | `0` se o material não existe; senão conta `common.set_cutpart_material(obj, mat)` verdadeiros | 🟢 |
| `image_material(path, size_mm)` | `-> Material` | F-07 | 🟢 |
| `apply_image(objs, path, size_mm)` | `-> int` | `image_material` + `set_cutpart_material` em cada malha; `RuntimeError` de `images.load` propaga | 🟢 |

### `previews.py`

| Símbolo | Comportamento | Confiança |
|---|---|---|
| `_collection` | `[None]` ou `[ImagePreviewCollection]` | 🟢 |
| `icon_id(path)` | `0` se `path` vazio ou inexistente; senão cria a coleção sob demanda, chave `"{path}:{int(os.path.getmtime(path))}"`, `collection.load(key, path, 'IMAGE')` se nova, devolve `collection[key].icon_id` | 🟢 |
| `register()` / `unregister()` | `register` não faz nada; `unregister` chama `bpy.utils.previews.remove` e zera | 🟢 |

### `panels.py`

| Função | Desenho | Confiança |
|---|---|---|
| `draw_insert(layout, context)` | 1) `row(align=True).prop_tabs_enum(ui, "category", icon_only=True)`; 2) `label(tr(rótulo da categoria))`; 3) `prop(ui, "search", text="", icon='VIEWZOOM')`; 4) `items, warnings = item_io.all_items()`; `shown` = itens da categoria que passam na busca; 5) vazio → linha inativa "Nenhum objeto nesta categoria" ou "Nenhum objeto com esse nome" (se há busca); 6) `grid_flow(row_major=True, columns=2, even_columns=True, align=False)`; por item: `template_icon(icon_value, scale=4.0)` ou `label(icon='MESH_CUBE')`; linha com `caffmob.object_insert` (texto = nome, `key`) e, se do usuário, `caffmob.object_library_remove` (ícone `X`, `key`); 7) avisos → linha inativa "{n} arquivo(s) da biblioteca ignorado(s)" ícone `ERROR`; 8) `caffmob.object_library_add` "Acrescentar à biblioteca" ícone `ADD`, `scale_y = 1.2` | 🟢 |
| `draw_retexture(layout, context)` | coluna com 2 linhas ("Parte selecionada" → `scope='PART'`, "Item inteiro" → `scope='ITEM'`), cada uma com `caffmob.object_retexture_finish` "Acabamento" (`MATERIAL`) e `caffmob.object_retexture_image` "Imagem" (`IMAGE_DATA`) | 🟢 |
| `_key(item)` | `ops.item_key(item)` (import tardio) | 🟢 |

🟢 Consumidores: `ui/sidebar_insert.py:draw` chama `draw_insert` dentro do grupo recolhível `'objects'` "Objetos" (ícone `ASSET_MANAGER`); `ui/sidebar_selected.py:draw` chama `draw_retexture` no grupo `'sel_retexture'` "Retexturizar" (ícone `MATERIAL`) só se houver malha selecionada (RN-19). Ambos na barra lateral `VIEW_3D` / região `UI` (`ui/sidebar.py:BTM_PT_Sidebar`).

### Operadores — `ops.py`

| `bl_idname` | Classe | `bl_options` | Propriedades | Confiança |
|---|---|---|---|---|
| `caffmob.object_insert` | `BTM_OT_ObjectInsert` "Inserir objeto" | `REGISTER, UNDO` | `key: StringProperty(options={'HIDDEN'})` | 🟢 |
| `caffmob.object_library_remove` | `BTM_OT_ObjectLibraryRemove` "Remover da biblioteca" | `REGISTER` | `key` (HIDDEN); `poll` sempre `True` | 🟢 |
| `caffmob.object_library_add` | `BTM_OT_ObjectLibraryAdd` "Acrescentar à biblioteca" | `REGISTER, UNDO` | `name` ("Meu objeto"), `category` (enum, `'OTHER'`), `source` ("Uso próprio"), `license_text` ("Uso próprio"), `author` (""), `filepath` (`FILE_PATH`, "" = seleção), `duplicate` (`RENAME`/`REPLACE`, `'RENAME'`) | 🟢 |
| `caffmob.object_retexture_finish` | `BTM_OT_ObjectRetextureFinish` "Retexturizar com acabamento" | `REGISTER, UNDO`; `bl_property = "finish"` | `finish: EnumProperty(items=_finish_items)`; `scope` (`SCOPE_ITEMS`, `'PART'`); `poll`: há objeto ativo | 🟢 |
| `caffmob.object_retexture_image` | `BTM_OT_ObjectRetextureImage(Operator, ImportHelper)` "Retexturizar com imagem" | `REGISTER, UNDO` | `filepath` (do `ImportHelper`); `filter_glob` ("*.png;*.jpg;*.jpeg;*.tif;*.tiff;*.webp", HIDDEN); `size_mm: FloatProperty(default=600.0, min=1.0, max=100000.0)`; `scope`; `poll`: há objeto ativo | 🟢 |

🟢 Auxiliares: `item_key(item)` → `"{'U'|'B'}:{categoria}:{item_id}"`; `find_item(key)` → primeiro item de `item_io.all_items()` com a chave, ou `None`; `SCOPE_ITEMS = [('PART', "Parte selecionada", "Só as peças selecionadas"), ('ITEM', "Item inteiro", "Todas as peças do item do objeto ativo")]`; `_finish_items(self, context)` → `[(nome, nome, "")]` de `finish_names()` ou `[('NONE', tr("Nenhum acabamento"), "")]`.

## Fluxo Principal

### F-01 — `catalog.read_manifest(data)`
1. 🟢 `data` não é dict ou `format` ≠ `FORMAT` → `ManifestError("formato desconhecido")`.
2. 🟢 `version != 1` → `ManifestError("versão {v} não suportada")` (comparação `!=`: `True` e `1.0` passam — EC-03).
3. 🟢 Para `item_id`, `name`, `root`: não string ou vazia após `strip` → `ManifestError("campo obrigatório ausente: <chave>")`.
4. 🟢 `item_id` fora de `_ID` → `ManifestError("item_id inválido: …")`.
5. 🟢 Monta `Entry`: categoria válida ou `'OTHER'`; `size_mm = [float(v) for v in (size_mm or [0,0,0])][:3]`; `source/author/license/created_at/addon_version` por `str(...)` (ausente = `""`); `features` filtradas por `FEATURES` (ordem do arquivo preservada); `materials = list(...)`.

### F-02 — `store._scan(folder, user, warnings)`
1. 🟢 Pasta vazia/ausente → `[]`.
2. 🟢 Para cada subpasta ordenada (arquivos soltos na raiz são ignorados), para cada `*.json` ordenado: abre em UTF-8, `json.load`, `read_manifest`. `OSError` ou `ValueError` (inclui `ManifestError`, JSON inválido, `float` inválido) → aviso `"{path}: {exc}"` e segue.
3. 🟢 `paths_for(folder, <nome da subpasta>, entry.item_id)`; sem `.blend` → aviso `"{path}: falta o .blend"`.
4. 🟢 `Item(entry, user, blend, json_path, png ou None)`.

### F-03 — `item_io.features_of(objs)`
🟢 Para cada objeto: grupo → `FRAME` se `btm_group.kind == 'FRAME'`, senão `GROUP`; `btm_aggregate.is_aggregate` → `AGGREGATE`, mais `PRODUCTION_PART` se `production_part`, mais `LEAF_SLIDE` (`motion == 'SLIDE'`) ou `LEAF_SWING` se `kind == 'LEAF'`; malha com algum material de nome iniciado por "Textura: " → `TEXTURED`. Devolve na ordem de `FEATURES`.

### F-04 — `item_io.save(...)` (acrescentar)
1. 🟢 `objs = tree(root)`; `item_id = item_id or replace_id or new_item_id(name)`.
2. 🟢 Marca a raiz **antes** de gravar: `is_item=True`, `item_id`, `category`, `source`, `license`.
3. 🟢 `lo, hi = library_common.world_box(objs)` (malhas visíveis, avaliadas); `size_mm = [round((hi-lo)[i]*1000, 1)]`.
4. 🟢 `Entry(item_id, name, category, root.name, source, author, license, size_mm, features_of(objs), sorted({nomes dos materiais das malhas}), now().astimezone().isoformat(timespec='seconds'), _addon_version())`.
5. 🟢 `folder = folder or user_dir()`; `os.makedirs(<folder>/<category>, exist_ok=True)`.
6. 🟢 Dentro de `try`: `mkstemp(.blend)` → `bpy.data.libraries.write(tmp, set(objs), path_remap='RELATIVE_ALL', fake_user=True)`; `mkstemp(.json)` → `json.dump(to_manifest(entry), ensure_ascii=False, indent=1)`; `os.replace` do `.blend` e depois do `.json`.
7. 🟢 `OSError`/`RuntimeError` → apaga os temporários registrados e devolve `(None, ["Não foi possível gravar o item em {folder}: {exc}"])`.
8. 🟢 Se `thumb`: `library_common.thumbnail(context, objs, png)` (câmera ortográfica 256×256, Workbench, fundo transparente; falha só imprime no console).
9. 🟢 Devolve `(Item(entry, folder != BUNDLED_DIR, blend, json, png se existir), [])`.

### F-05 — `item_io.insert(context, item, location=None)`
1. 🟢 `bpy.data.libraries.load(item.blend, link=False)`: `data_to.objects = list(data_from.objects)` (todos os objetos do arquivo).
2. 🟢 Raiz = primeiro carregado com `name == entry.root` ou `name.split(".")[0] == entry.root`; senão o primeiro sem pai com `btm_object_item.is_item`.
3. 🟢 Sem raiz → remove os objetos carregados e `ValueError(tr("Item corrompido: {}"))`.
4. 🟢 `collection = context.collection or context.scene.collection`; para cada carregado: `use_fake_user = False` e `link` se ainda não está nela.
5. 🟢 `root.location = location` (se dado); `context.view_layer.update()`; devolve `(root, loaded)`.

### F-06 — `caffmob.object_insert`
1. 🟢 `_load`: `find_item(key)` (ausente → ERROR "Objeto não encontrado na biblioteca", `None`); `insert(..., location=cursor.location.copy())` (`ValueError` → ERROR com a mensagem); desmarca a seleção, seleciona a raiz, torna-a ativa; guarda `_root`, `_loaded`, `_name`.
2. 🟢 `execute`: `_load`; INFO "{nome} inserido"; `FINISHED`.
3. 🟢 `invoke`: sem área ou área ≠ `VIEW_3D` → `execute`. Senão `_load`, `_plane_z = cursor.z`, cabeçalho "Mova para posicionar · Clique solta · Esc cancela", `modal_handler_add`, `RUNNING_MODAL`.
4. 🟢 `modal`: `MOUSEMOVE` → `_follow` (raio `region_2d_to_origin_3d`/`region_2d_to_vector_3d` com `context.region`/`region_data`; `intersect_line_plane(origin, origin + dir*1000, (0,0,z), (0,0,1))`; se acerta, `root.location = (x, y, z)`); `LEFTMOUSE PRESS` → limpa cabeçalho, INFO, `FINISHED`; `ESC`/`RIGHTMOUSE PRESS` → limpa cabeçalho, remove `_loaded` em ordem inversa (se ainda em `bpy.data.objects`), `CANCELLED`; `MIDDLEMOUSE`/`WHEELUPMOUSE`/`WHEELDOWNMOUSE` → `PASS_THROUGH`; demais → `RUNNING_MODAL` (consome).
5. 🟢 `cancel` (cancelamento externo) → só limpa o cabeçalho. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-91):** `cancel()` externo remove os objetos de `_loaded` que ainda existirem, igual ao Esc. Pendência de implementação: DT-03.

### F-07 — `retexture.image_material(path, size_mm)`
1. 🟢 `path = abspath(path)`; procura material com `mat.get(PATH_PROP) == path` e `|mat.get(SIZE_PROP, 0) − size_mm| < 1e-6` → reaproveita.
2. 🟢 `bpy.data.images.load(path, check_existing=True)`; `materials.new("Textura: {basename} {size_mm:g} mm")`; grava as duas propriedades ID.
3. 🟢 Nós: `ShaderNodeTexCoord` (−900, 0) `Object` → `ShaderNodeMapping` (−700, 0) `Vector`, `Scale = (s, s, s)`, `s = 1/max(size_mm/1000, 1e-4)` → `ShaderNodeTexImage` (−450, 0) `projection='BOX'`, `projection_blend=0.2` → `Color` → `Base Color` do Principled existente (o primeiro nó `BSDF_PRINCIPLED`).

### F-08 — `caffmob.object_library_add`
1. 🟢 `invoke`: se há ativo e `filepath` vazio, `name = (root_of(ativo) or ativo).name.split(".")[0]` e, se é item, `category = raiz.btm_object_item.category`; abre `invoke_props_dialog(width=360)`.
2. 🟢 `draw`: `use_property_split`; campos `name, category, source, author, license_text, filepath`; `duplicate` só se `self.name` (sem `strip`) está em `existing_names(category)`.
3. 🟢 `execute`: `name.strip()` vazio → ERROR; `_objects` = seleção, ou (com arquivo) `bpy.ops.caffmob.import_model(filepath=abspath)` e os objetos novos de `bpy.data.objects` (diferença de conjuntos); vazio → ERROR; nome repetido → `REPLACE` (busca o `item_id` do item do usuário com esse nome e categoria) ou `unique_name`; `prepare_root` (`None` → ERROR "A seleção não tem malhas"); `save` (erros → ERROR unidos por "; "); INFO "{nome} acrescentado à biblioteca em {rótulo da categoria}".

### F-09 — Retexturizar (operadores)
1. 🟢 Acabamento: `invoke` abre `invoke_search_popup` (busca no enum `finish`) e devolve `RUNNING_MODAL`; `execute` → `apply_finish(_scope_objects(scope), finish)`; 0 → WARNING, `CANCELLED`; senão INFO "{n} peça(s) com {acabamento}".
2. 🟢 Imagem: `invoke` do `ImportHelper` (seletor de arquivo); `execute` exige `os.path.isfile(filepath)`; `apply_image`; `RuntimeError` → ERROR; 0 → WARNING "A seleção não tem malhas"; senão INFO "{n} peça(s) com a textura {arquivo}".

## Fluxos Alternativos
- **Item corrompido:** `insert` remove os objetos anexados e levanta `ValueError`; o operador reporta e cancela (CA-07). Malhas, materiais e imagens anexados junto não são removidos (EC-07). 🟢
- **Inserir fora da viewport** (script, outro editor): `invoke` cai em `execute` (sem modal). 🟢
- **Gravar falhou:** temporários removidos; a raiz já marcada como item e o grupo criado por `prepare_root` permanecem na cena (EC-05). 🟢
- **Miniatura falhou:** item salvo sem `.png`; a grade mostra o ícone `MESH_CUBE`. 🟢
- **Arquivo 3D não importou:** `import_model` sem `FINISHED` → lista vazia → ERROR "Selecione o objeto ou escolha um arquivo" (mensagem genérica). 🟢
- **Remover:** `invoke_confirm(title="Remover da biblioteca", message="Apagar este objeto da sua biblioteca?", confirm_text="Remover", icon='WARNING')`; `PermissionError` → ERROR; `OSError` → ERROR com a mensagem. 🟢

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `aggregates/group.py` (`is_group`, `create_group`) | Raiz de grupo `PLAIN` (Empty `CUBE`, origem no centro-base da caixa) — contrato em `_reversa_sdd/aggregates/` | 🟢 |
| `btm_group`, `btm_aggregate` (aggregates) | Lidos por `features_of`; conversões viajam nos próprios objetos | 🟢 |
| `bpy.ops.caffmob.import_model(filepath)` | Acrescentar de arquivo (OBJ/FBX/glTF/SKP) — `_reversa_sdd/aggregates/` RF-14 a RF-16 | 🟢 |
| `library_common.world_box`, `thumbnail` | Medidas e miniatura (mesma mecânica de `customize`) | 🟢 |
| `customize/library_io._addon_version` | `addon_version` do manifesto | 🟢 |
| `customize/adapters/common.set_cutpart_material` | Material em `GeoNodeCutpart` (Top/Bottom Surface e porta 5 peças) ou em todos os slots de malha comum — `_reversa_sdd/customize/` | 🟢 |
| `data/i18n` (`tr`, `N_`), `data/translations/object_library.json` | Textos | 🟢 |
| `product_libraries/*/materials/*.blend` | Acabamentos do plugin | 🟢 |
| Consumidores: `ui/sidebar_insert.py`, `ui/sidebar_selected.py` (painéis); `selection/component.py:_is_item` (precedência 5 da raiz do componente); `selection/classify.py:free_group/movable_root` (raiz `btm_group` móvel no Mover Sobre); `standards/sync.py:_other_roots` (item de topo entra como componente); `tools/build_object_library.py`, `build.py` (embutidos) | Leem `btm_object_item.is_item` ou chamam a API | 🟢 |
| Colisão | Raiz Empty e malhas filhas de item ficam **fora** da varredura (`_reversa_sdd/collision/` EC-15) | 🟢 |

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Item = trio de arquivos por nome-base; manifesto JSON descreve, o `.blend` é a verdade | store.py (docstring); item_io.py:save | 🟢 |
| Duas raízes (embutida só leitura, usuário em `extension_path_user`) | store.py; item_io.py:user_dir | 🟢 |
| Conversões nos próprios objetos, não no manifesto (D-09 da 009) | props.py (docstring) | 🟢 |
| Núcleos sem `bpy` para teste fora do Blender | catalog.py; store.py; tests/test_object_library.py | 🟢 |
| Chave textual U/B na UI em vez de índice (estável entre redesenhos) | ops.py (docstring) | 🟢 |
| Textura por projeção em caixa em coordenadas de objeto (dispensa UV de malha importada) | retexture.py (docstring) | 🟢 |
| Inserção sem snapping/colisão: só plano horizontal do cursor | ops.py:_follow | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-90):** a inserção fica sem snapping por ora; os itens de topo (raiz do grupo) passam a entrar na verificação de colisão (collision DT-05) |
| Reutilizar a mecânica da biblioteca de módulos (003) | item_io.py (docstring) | 🟢 |

## Estado Interno
- 🟢 Persistente no projeto: `Object.btm_object_item` na raiz de cada item inserido/salvo; propriedades ID `btm_texture_path`/`btm_texture_size_mm` nos materiais de imagem.
- 🟢 Sessão: `WindowManager.btm_object_library` (categoria ativa, busca); `previews._collection`; `retexture._names_cache`; atributos do operador modal (`_root`, `_loaded`, `_name`, `_plane_z`) como referências RNA diretas.
- 🟢 Disco: as duas raízes de itens; nada é cacheado entre redesenhos.
- 🟡 Os valores do diálogo Acrescentar (`name`, `category`, `source`…) são lembrados pelo Blender entre invocações (propriedades sem `SKIP_SAVE`), exceto o que `invoke` sobrescreve.

## Observabilidade
- 🟢 `self.report` INFO/WARNING/ERROR em todos os operadores (mensagens em CA-04 a CA-18).
- 🟢 Avisos de listagem só como contagem na UI ("{n} arquivo(s) da biblioteca ignorado(s)"); o texto de cada aviso não é mostrado.
- 🟢 Falha de miniatura: `print("CAFFMob Draw: miniatura não gerada (…)")` (`library_common.thumbnail`).
- 🟢 Cabeçalho da área durante o modal.

## Riscos e Lacunas
- 🟢 Modal invocado pelo botão da barra lateral: `context.region` é a região `UI` e `region_data` é `None` nos eventos do modal, então `_follow` sai cedo e a raiz não acompanha o mouse (EC-10). _(Revisão 2026-10-10: sonda com xvfb-run e eventos simulados)_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-59):** corrigir: quando `context.region_data` for `None`, `_follow` acha a região `WINDOW` da área e converte `event.mouse_x/y` para as coordenadas dela; o caso entra no teste do modal (TT-03). Pendência de implementação: DT-01.
- 🟢 `libraries.write` expande referências indiretas: se a raiz salva tem pai (grupo criado com pai comum), o pai também vai para o `.blend` e volta ao inserir (EC-08). _(Revisão 2026-10-10: sonda: malha filha de 'PaiX' salva → .blend com ['Teste pai', 'PaiX', 'Cube'])_
- 🟢 Fake user: só os objetos (o conjunto passado a `libraries.write`) chegam com fake user; malhas e materiais anexados chegam sem fake user. Após Esc ficam órfãos com 0 usuários até salvar e recarregar, sem persistir (EC-07). _(Revisão 2026-10-10: sonda: porta embutida inserida, 0/2 malhas e 0 materiais com fake user; após remover os objetos, malhas com users = 0)_
- 🟢 `cancel()` externo (fechar janela, sair do arquivo) não remove os objetos carregados. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-91):** `cancel()` externo remove os objetos de `_loaded` que ainda existirem, igual ao Esc. Pendência de implementação: DT-03.
- 🟢 `_finish_items` devolve strings novas a cada chamada, sem guardar referência (armadilha de `EnumProperty(items=callback)` em `docs/rag/project/04_armadilhas.md`); o efeito visível (texto corrompido no menu) é 🟡 e não foi observado. _(Revisão 2026-10-10: ops.py:245-246; retexture.py:41-44 monta nomes de bpy.data.materials a cada chamada)_
- 🟢 Manifesto com tipo inesperado em `size_mm`/`features`/`materials` (`TypeError`) derruba a listagem inteira (EC-01). _(Revisão 2026-10-10: read_manifest executado em Python: features 5, materials 5 e size_mm [null,0,0] dão TypeError; store.py:137 só captura OSError/ValueError)_
- 🟢 Escrita não transacional entre `.blend`, `.json` e `.png` (domain RN-OBJECT_LIBRARY-03).

## Divergências com artefatos anteriores
- 🟢 `domain.md` (tabela de glossário, "Biblioteca de objetos") cita `manifest.py`: não existe arquivo com esse nome na unit; o manifesto está em `catalog.py`.
- 🟢 `panels.py` (docstring) diz que "o tooltip de cada item diz se ele vem com o plugin ou é seu": no código, o botão usa o tooltip fixo do operador (`BTM_OT_ObjectInsert.__doc__`); a distinção visível é só o botão `X` nos itens do usuário.
- 🟢 Os demais artefatos (`code-analysis.md` §18, `data-dictionary.md` §17, `state-machines.md`, flowcharts `object_library*.md`, `erd-complete.md`) conferem com o código.
