# Padrão de Dimensões (standards) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído em 2026-10-10 de `caffmob_draw/standards/`, `data/dimension_schema.py`, `operators/ops_standards.py` e `ui/standards_tree.py`. IDs RN/RF/CA são os de `requirements.md`; EC-xx de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Fluxogramas complementares: `_reversa_sdd/flowcharts/standards*.md` (conferidos contra o código, sem divergência).

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Esquema puro | `data/dimension_schema.py` | não | O QUE é configurável: linhas, componentes, parâmetros, validação, índice Promob | 🟢 |
| Núcleo puro | `standards/apply_core.py` | não | Padrão próprio e plano segue/difere | 🟢 |
| Núcleo puro | `standards/cabinet_defaults.py` | não (importa `cabinet_editor.structure` e `data.i18n`, ambos sem `bpy` no caminho usado) | Medidas de armário novo | 🟢 |
| Arquivo puro | `standards/io_promob.py` | não | Ler/escrever `DIMENSIONEXPORT` | 🟢 |
| Arquivo misto | `standards/io_json.py` | só em `user_folder` e via `api` | Documento puro + integração com a cena | 🟢 |
| Dados RNA | `standards/model.py` | sim | PropertyGroups e ponteiros | 🟢 |
| Serviço | `standards/builtin.py`, `api.py` | `api` usa RNA por duck typing | Definições, valores, rascunho, árvore | 🟢 |
| Integração com a cena | `standards/sync.py`, `migration.py`, `previews.py` | sim | Propagação, migração, imagens | 🟢 |
| Interface | `operators/ops_standards.py`, `ui/standards_tree.py` | sim | 13 operadores, diálogos, UIList | 🟢 |

🟢 Ordem de registro do pacote: `model` → `previews` → `migration`; `unregister` na ordem inversa (`standards/__init__.py`). Operadores e UIList são registrados por `operators/__init__.py` e `ui/__init__.py`, não por `standards/__init__.py`.

## Interface

### `data/dimension_schema.py` (esquema)

| Símbolo | Valor / assinatura | Observação | Confiança |
|---|---|---|---|
| `INCH_MM` | `25.4` | Conversão dos padrões US | 🟢 |
| `MARKETS` | `('BR', 'US')` | — | 🟢 |
| `LINES` | `(('COZ',"Cozinhas","Kitchens"), ('DOR',"Dormitórios","Bedrooms"), ('BAN',"Banheiros","Bathrooms"), ('SAL',"Salas","Living rooms"), ('ESC',"Escritórios","Offices"))` | Ordem = ordem da árvore | 🟢 |
| `LINE_CODES` | `('COZ','DOR','BAN','SAL','ESC')` | — | 🟢 |
| `GROUP_MAX/EXTERNAL/SHEET` | `'MAX'`, `'EXTERNAL'`, `'SHEET'` | Grupo do `Param` | 🟢 |
| `TREE_SHEETS/TREE_COMPONENTS` | `'CHAPAS'`, `'COMPONENTES'` | Árvore do componente; usado no caminho da árvore e no JSON | 🟢 |
| `_THICKNESS` | `CAIXA (15, 19.05)`, `FRENTE (18, 19.05)`, `FUNDO (6, 6.35)`, `TAMPO (15, 19.05)` mm (BR, US) | US = 0,75″ ou 0,25″ | 🟢 |
| `Component` | dataclass frozen `(code, label_pt, label_en, tree, thickness_class, promob=(), promob_fit=(), visible_sides_br=(1,))` | — | 🟢 |
| `COMPONENTS` | 20 itens, tabela abaixo | Ordem = ordem da árvore | 🟢 |
| `PROMOB_EDGE_TO_SIDE` | `{4: 1, 3: 2, 1: 3, 2: 4}`; `SIDE_TO_PROMOB_EDGE` inverso | Promob 1 topo/2 base/3 direita/4 esquerda → lados 1/2 = comprimento, 3/4 = largura (C-1) | 🟢 |
| `MATERIALS` | `('MDF','MDP','COMPENSADO','OSB','VIDRO','OUTRO')` | Itens do ENUM material | 🟢 |
| `Param` | dataclass frozen `(key, line, group, label_pt, label_en, unit, type, default_br, default_us, min=0.0, max=0.0, step=1.0, precision=1, enum_items=(), zero_meaning="", negative_allowed=False, image_key="", promob_codes=(), legacy_targets=(), component="", field="", description_pt="")`; `default(market='BR')` → `default_br` se `'BR'`, senão `default_us` | `type ∈ {'FLOAT','ENUM'}` | 🟢 |
| `SHEET_FIELDS` | `('material','max_width','max_length','thickness','edge_1','edge_2','edge_3','edge_4')` | — | 🟢 |
| `EDGE_FIELDS` | `('edge_1','edge_2','edge_3','edge_4')` | — | 🟢 |
| `sheet_key(line, component, field)` | `f"{line}.sheets.{component}.{field}"` | — | 🟢 |
| `external_key(line, field)` | `f"{line}.external.{field}"` | — | 🟢 |
| `max_key(field)` | `f"GLOBAL.max.{field}"` | `line = 'GLOBAL'` | 🟢 |
| `PARAMS` | `dict[str, Param]`, 870 itens, ordem F-01 | Construído na importação (`_build`) | 🟢 |
| `get_param(key)` | `Param` ou `None` | — | 🟢 |
| `params_for(line=None, group=None, component=None)` | lista na ordem de declaração | Filtros combinados por E | 🟢 |
| `label(param_or_key, lang='pt')`, `line_label(code, lang='pt')` | rótulo pt/en; `line_label` devolve o próprio código se desconhecido | — | 🟢 |
| `validate(param, value)` | `(True, "")` ou `(False, msg)` | F-02 | 🟢 |
| `PROMOB_INDEX` | `dict[código, chave]`, 1.042 itens, `setdefault` (primeiro parâmetro vence) | — | 🟢 |
| `parse_promob_id(attr_id)` | dict `{line, family, component, field, side}` ou `None` | Famílias `C`, `L`, `ESP`, `MAT`, `FIT` (`_<n>A`, n ∈ 1..4) | 🟢 |
| `canonical_component(promob_component)` | código canônico ou `None` | Alias de `promob + promob_fit`; sem consumidor no pacote | 🟢 |

Componentes 🟢 `dimension_schema.py:COMPONENTS` (árvore, classe de espessura, códigos Promob C/L/ESP/MAT, códigos FIT, lados com fita 0,4 no BR):

| Código | Rótulo | Árvore | Classe | `promob` | `promob_fit` | `visible_sides_br` |
|---|---|---|---|---|---|---|
| LAT | Lateral | CHAPAS | CAIXA | LAT | LAT | (1,) |
| DIV | Divisória | CHAPAS | CAIXA | DIV | DIV | (1,) |
| BAS | Base | CHAPAS | CAIXA | BAS | BAS | (1,) |
| FUN_INF | Fundo - Inferiores | CHAPAS | FUNDO | FUN | FUN | () |
| FUN_SUP | Fundo - Superiores | CHAPAS | FUNDO | FUN_SUP | FUN_SUP | () |
| FUN_ALT | Fundo - Altos | CHAPAS | FUNDO | FUN_ALT | FUN_ALT | () |
| TRAS | Traseira | CHAPAS | CAIXA | TRAS | TRAS | (1,) |
| TRA | Travessas Traseiras | CHAPAS | CAIXA | TRA | TRA | (1,) |
| PRAT | Prateleira | CHAPAS | CAIXA | PRAT | PRA, PRAT | (1,) |
| POR | Portas \| Frentes | CHAPAS | FRENTE | PORTAS | POR | (1,2,3,4) |
| PAI_POR | Painel p/ Portas | CHAPAS | FRENTE | PAI_PRO_MDF, PAI_POR_VID, PAI_PRO_PALHA, PAI_PRO_VID, PAI_PRO_MAD | () → usa `promob` | () |
| FRE_GAV_INT | Frente Gav Int | CHAPAS | FRENTE | FRE_GAV_INT | FRE_GAV_INT | (1,2,3,4) |
| FRE_FORNO | Frente Forno/Micro de Embutir | CHAPAS | FRENTE | FRE_ELE_EMB | FRE_ELE_EMB | (1,2,3,4) |
| TAMP | Tampo | CHAPAS | TAMPO | TAMP | TAMP | (1,) |
| TAMPON | Tamponamento | CHAPAS | CAIXA | TAMPON | TAN, TAMPON | (1,) |
| PAI | Painel | CHAPAS | CAIXA | PAI | PAI, PAINEL | (1,2,3,4) |
| ESP | Especial | CHAPAS | CAIXA | ESP | ESP | (1,) |
| SAR | Sarrafo | COMPONENTES | CAIXA | SAR | SAR | (1,) |
| ROD | Rodapé | COMPONENTES | CAIXA | ROD | ROD | (1,) |
| MOL | Moldura | COMPONENTES | CAIXA | MOL, MOL_ENG | MOL | (1,) |

Medidas máximas globais 🟢 `_MAX_FIELDS` (campo: BR / US / mín.–máx., mm, passo 1, precisão 1, `image_key='max_measures'`): `module_width_max` 1200 / 1219,2 / 100–6000; `module_height_max` 2700 / 2438,4 / 100–4000; `module_depth_max` 900 / 762 / 100–2000; `sheet_width_max` 2730 / 2420 / 300–6000; `sheet_length_max` 1810 / 1200 / 300–6000.

Dimensões externas por linha 🟢 `_EXTERNAL_FIELDS` (BR / US em mm / faixa; `image_key = "ext_<campo>"`; `zero_meaning = "sem rodapé"` para `toe_kick_*`): `base_height` 720 / 876,3 / 300–1200; `base_depth` 550 / 587,375 / 200–1000; `upper_low_height` 350 / 381 / 100–1500; `upper_mid_height` 700 / 762 / 100–1500; `upper_high_height` 900 / 1066,8 / 100–1500; `upper_depth` 350 / 330,2 / 150–800; `install_height_upper` 1500 / 1371,6 / 0–2600; `tall_height` 2200 / 2133,6 / 1000–3000; `tall_depth` 550 / 647,7 / 200–1000; `island_depth` 900 / 609,6 / 300–2000; `top_overhang` 20 / 25,4 / 0–200; `toe_kick_height` 100 / 101,6 / 0–300; `toe_kick_setback` 50 / 63,5 / 0–200. Exceções DOR (BR, US): `tall_height` (2400, 2131), `tall_depth` (550, 355,6), `base_height` (720, 819), `toe_kick_height` (100, 96), `toe_kick_setback` (50, 41,275).

Campos de chapa 🟢 `_build`: `material` ENUM (`'MDF'`/`'MDF'`, `MATERIALS`, unidade `''`); `thickness` FLOAT pela classe, 3–60, passo 0,5; `max_width` 2730/2420, 100–6000; `max_length` 1810/1200, 100–6000; `edge_n` 0,4 se `n ∈ visible_sides_br` senão 0 (US 0), 0–5, passo 0,1, `zero_meaning = "sem fita"`. `image_key = "sheet_<código em minúsculas>"`. Rótulos: "Material", "Largura Máxima da Chapa", "Comprimento Máximo da Chapa", "Espessura da Chapa", "Fita Borda 1 (comprimento)" … "Fita Borda 4 (largura)".

Códigos Promob 🟢: chapa `"{linha}_{família}_{c}"` para `c ∈ promob`, famílias `MAT`/`L`(max_width)/`C`(max_length)/`ESP`(thickness); fita `"{linha}_FIT_{c}_{SIDE_TO_PROMOB_EDGE[n]}A"` para `c ∈ (promob_fit or promob)`; externos só `ALT_ARM` → `DOR.external.tall_height` e `PROF_ARM` → `DOR.external.tall_depth` (🟡 semântica). Destinos legados (17) 🟢 `_LEGACY_TARGETS`: COZ LAT.thickness → `hb_frameless.default_carcass_part_thickness`; COZ externos base_height/base_depth/upper_mid_height/upper_depth/tall_height/tall_depth/install_height_upper/toe_kick_height/toe_kick_setback → `hb_frameless.base_cabinet_height/base_cabinet_depth/upper_cabinet_height/upper_cabinet_depth/tall_cabinet_height/tall_cabinet_depth/default_wall_cabinet_location/default_toe_kick_height/default_toe_kick_setback`; DOR LAT.thickness → `hb_closets.panel_thickness`, PRAT.thickness → `shelf_thickness`, base_height → `base_panel_height`, tall_height → `tall_panel_height`, tall_depth → `default_panel_depth`, toe_kick_height → `toe_kick_height`, toe_kick_setback → `toe_kick_setback`.

### `standards/model.py` (dados RNA)

| Classe | Campos (tipo = padrão) | Confiança |
|---|---|---|
| `BTM_PG_StandardValue` | `name` herdado = chave; `value: Float = 0.0` (mm); `text: String = ""`; `is_text: Bool = False` | 🟢 |
| `BTM_PG_RawAttribute` | `attr_id: String`; `value: String` (texto original); `key: String` ("" = não reconhecido) | 🟢 |
| `BTM_PG_StandardDefinition` | `name` herdado; `uid: String`; `builtin: Bool = False`; `market: Enum {BR, US} = BR`; `source: Enum {BUILTIN, USER, PROMOB_IMPORT, MIGRATED} = USER`; `version: Int = 1, min 1`; `updated_at: String`; `values: Collection[StandardValue]`; `raw_attributes: Collection[RawAttribute]`; `assembly: Enum ASSEMBLY_ITEMS = LATERAL` | 🟢 |
| `BTM_PG_Standards` | `definitions: Collection[StandardDefinition]`; `active_index: Int = 0, min 0`; `schema_version: Int = 1` (não lido por ninguém) | 🟢 |
| `BTM_PG_StandardTreeItem` | `label`; `node_type: Enum {GROUP, PARAM} = GROUP`; `key`; `depth: Int = 0`; `path` | 🟢 |
| `BTM_PG_StandardsDraft` | `definition_uid`; `definition_name`; `values`; `tree`; `tree_index: Int = 0, update=activate_tree_row`; `expanded` (caminhos separados por `|`); `search` (`TEXTEDIT_UPDATE`, update=`rebuild_tree`); `selected_key`; `edit_text` (update=`commit_edit_text`); `edit_enum` (items=`edit_enum_items`, update=`commit_edit_enum`); `error`; `assembly: Enum = LATERAL`; `include_manual: Bool = False` | 🟢 |

🟢 `ASSEMBLY_ITEMS = [('LATERAL', "Lateral passante", …), ('BASE', "Base passante", …)]`. Ponteiros: `Scene.btm_standards` e `WindowManager.btm_standards_draft` (o rascunho não é salvo no `.blend`). As callbacks importam `api` tardiamente para evitar ciclo. Fonte: `model.py`.

### `standards/builtin.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `BUILTINS` | `(('builtin-br', "Padrão Brasil", 'BR'), ('builtin-us', "Padrão EUA (HB5)", 'US'))` | `BUILTIN_BR_UID`, `BUILTIN_US_UID` | 🟢 |
| `now_iso()` | `str` | `datetime.now().astimezone().isoformat(timespec='seconds')` | 🟢 |
| `fill_from_schema(definition, market)` | `None` | Para cada chave de `PARAMS` ausente em `definition.values`: adiciona; ENUM → `is_text=True, text=str(default)`; senão `value=float(default)`. Funciona com o rascunho (duck typing) | 🟢 |
| `ensure_builtins(standards)` | `dict[uid, definition]` | Embutidas são reconhecidas por `builtin=True`+`uid`; faltando, cria com `builtin=True`, `market`, `source='BUILTIN'`, `updated_at`; completa com `fill_from_schema`; relê a coleção no fim | 🟢 |

### `standards/api.py`

| Símbolo | Assinatura | Retorno / efeito | Confiança |
|---|---|---|---|
| `StandardsError` | `Exception` | Mensagem pronta para o usuário | 🟢 |
| `main_scene` | `(scene=None)` | `hb_project.get_main_scene()` ou `scene` | 🟢 |
| `standards` | `(scene=None)` | `main_scene(scene).btm_standards` ou `None` | 🟢 |
| `ensure_ready` | `(scene=None)` | `BTM_PG_Standards`; erro "Padrão de Dimensões indisponível nesta cena." | 🟢 |
| `active_definition` | `(scene=None)` | definição em `min(active_index, n-1)` ou `None` | 🟢 |
| `active_assembly` | `(scene=None)` | `'LATERAL'`/`'BASE'` | 🟢 |
| `find_definition` | `(scene, uid=None, name=None)` | primeira com uid **ou** nome igual | 🟢 |
| `set_active` | `(scene, definition)` | compara por `as_pointer()`; erro "Definição não encontrada." | 🟢 |
| `new_uid` / `unique_name` | `()` / `(scene, base)` | `uuid4().hex` / `base`, `base (2)`, `base (3)`… | 🟢 |
| `copy_values` | `(source, target)` | copia `assembly` se ambos têm; limpa e copia `name/value/text/is_text` (não copia crus) | 🟢 |
| `duplicate_definition` | `(scene, definition, name=None)` | nova definição (RN-08), ativa | 🟢 |
| `remove_definition` | `(scene, definition)` | remove; `active_index = min(active_index, max(n-1, 0))` | 🟢 |
| `get_definition_value` | `(definition, key)` | `text` se `is_text`, senão `value`; ausente → padrão do mercado | 🟢 |
| `get_value` / `get_value_m` | `(scene, key, definition=None)` | valor (mm/texto) / `float(valor)/1000` | 🟢 |
| `definition_values` | `(definition)` | `dict` completo (RN-09) | 🟢 |
| `set_value` / `set_values` | `(definition, key, value)` / `(definition, dict)` | RN-06, RN-10; `_write` cria item e grava texto (ENUM) ou `float` | 🟢 |
| `user_unit` | `(scene=None)` | `units.get_scene_length_unit(scene)` | 🟢 |
| `format_param_value` | `(param, value, unit='MM')` | ENUM → `str`; FLOAT → `units.format_length(value/1000, unit)` (vírgula decimal) | 🟢 |
| `begin_draft` | `(scene, window_manager)` | rascunho preenchido (F-05) | 🟢 |
| `set_draft_value` | `(draft, key, value)` | `_write` no rascunho (sem bloqueio de embutida) | 🟢 |
| `draft_definition` | `(scene, draft)` | `find_definition(uid=draft.definition_uid)` | 🟢 |
| `pending_changes` | `(scene, draft)` | lista de `{'key','label','old','new'}` (F-06) | 🟢 |
| `apply_draft` | `(scene, draft, include_manual=False, modules=None)` | relatório de `sync.apply_definition` + `'changes'` | 🟢 |
| `expanded_paths` / `toggle_group` | `(draft)` / `(draft, path)` | conjunto / diferença simétrica, grava ordenado com `|` e reconstrói | 🟢 |
| `rebuild_tree` | `(draft)` | F-07 | 🟢 |
| `activate_tree_row` | `(draft, scene=None)` | grupo → `toggle_group`; parâmetro → `select_param` | 🟢 |
| `tree_image_key` | `(draft)` | `image_key` do parâmetro selecionado ou `""`; sem consumidor | 🟢 |
| `select_param` | `(draft, key, scene=None)` | F-08 | 🟢 |
| `commit_edit_text` / `commit_edit_enum` | `(draft)` | F-08 | 🟢 |
| `edit_enum_items` | `(draft)` | `[(o, o, "")]` das opções do parâmetro, ou `('-',)`; cache por tupla | 🟢 |

### `standards/apply_core.py` e `cabinet_defaults.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `CAFFMOB, LEGACY, OTHER` | strings homônimas | Tipos de `ModuleInfo.kind` | 🟢 |
| `ModuleInfo` | namedtuple `(name, kind, standard_uid, own)` | — | 🟢 |
| `Plan` | namedtuple `(follow, differ, not_applicable, legacy)` (listas de nomes, ordem de entrada) | — | 🟢 |
| `is_own` | `(overrides, assembly, origin_assembly, role_thickness)` | `bool(overrides) or assembly != origin_assembly or any(t > 0 for t in role_thickness)` | 🟢 |
| `plan` | `(modules, previous_uid)` | RN-13 | 🟢 |
| `targets` | `(the_plan, apply_all, apply_differ)` | `[]` se não `apply_all`; `follow (+ differ)` | 🟢 |
| `Defaults` | namedtuple `(width, height, depth, z, thickness, carcass, warning)` em metros | — | 🟢 |
| `LINES` | `('COZ','DOR','BAN','SAL','ESC')` | Duplica `schema.LINE_CODES` | 🟢 |
| `FALLBACK` | `BASE (0.8, 0.72, 0.55, 0.0)`, `WALL (0.8, 0.70, 0.35, 1.5)`, `TALL (0.6, 2.2, 0.55, 0.0)` (largura, altura, profundidade, Z) | — | 🟢 |
| `FALLBACK_SHEET`, `FALLBACK_BACK` | `0.018`, `0.006` | — | 🟢 |
| `EXTERNAL` | `BASE ('base_height','base_depth',None)`, `WALL ('upper_mid_height','upper_depth','install_height_upper')`, `TALL ('tall_height','tall_depth',None)` | — | 🟢 |
| `defaults` | `(values, line, cabinet_type)` | F-09 | 🟢 |

### `standards/sync.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `OVERRIDES_PROP`, `LINE_PROP`, `STANDARD_UID_PROP` | `'btm_overrides'`, `'btm_line'`, `'btm_standard_uid'` | Custom properties da raiz | 🟢 |
| `FRAMELESS_TAG`, `CLOSET_TAG` | `'IS_FRAMELESS_CABINET_CAGE'`, `'IS_CLOSET_STARTER_CAGE'` | — | 🟢 |
| `is_syncing` | `()` | `_SYNC_DEPTH[0] > 0` | 🟢 |
| `module_root` | `(obj)` | sobe por `parent` até objeto com uma das duas tags; senão `None` | 🟢 |
| `get_overrides` / `add_override` / `clear_overrides` | `(obj)` / `(obj, name)` / `(obj)` | JSON de lista; inválido → `set()`; grava `json.dumps(sorted(...))` na raiz (`module_root(obj) or obj`); apaga a chave | 🟢 |
| `make_skip` | `(include_manual, skipped)` | `skip(obj, name)`: `False` se `include_manual`; senão, se `name` em overrides da raiz, anexa `(root.name, name)` e `True` | 🟢 |
| `affected_modules` | `(scene)` | CAFFMob + (com suporte legado) gaiolas; sem consumidor | 🟢 |
| `write_legacy_targets` | `(scene, values)` | F-11 passo 2; devolve lista ordenada e sem repetição dos destinos (inclusive os que já tinham o valor) | 🟢 |
| `is_caffmob_module` | `(obj)` | `obj.type == 'MESH'`, `classify.btm_kind(obj) == 'MODULE'` e `btm_cabinet` presente | 🟢 |
| `scene_modules` | `(scene, context=None)` | `[(obj, ModuleInfo)]`: CAFFMob (`own = bridge.is_own_standard`), raízes `gate.legacy_roots` (LEGACY, own False), raízes `btm_group.is_group`/`btm_object_item.is_item` de topo fora de módulo e não tomadas (OTHER, uid "") | 🟢 |
| `plan_for` | `(scene, previous_uid, context=None)` | `(Plan, {nome: obj})` | 🟢 |
| `apply_to_module` | `(context, obj, definition, values)` | F-12 | 🟢 |
| `apply_definition` | `(scene, definition, include_manual=False, changed_keys=None, modules=None)` | F-11; relatório | 🟢 |

Relatório 🟢 `sync.py:_apply_definition`: `{'definition': nome, 'modules_updated': caffmob + frameless + closets, 'caffmob', 'frameless', 'closets', 'targets_written': [str], 'skipped_manual': [(módulo, medida)], 'without_target': [chaves alteradas sem legacy_targets]}`; `apply_draft` acrescenta `'changes'`.

### `standards/io_json.py` e `io_promob.py`

| Símbolo | Assinatura | Comportamento | Confiança |
|---|---|---|---|
| `FORMAT`, `ACCEPTED_FORMATS`, `SCHEMA_VERSION` | `"caffmob_draw.dimension-standard"`, `(FORMAT, "blendertomob.dimension-standard")`, `1` | — | 🟢 |
| `StandardFileError` | `Exception` | — | 🟢 |
| `user_folder` | `()` | `bpy.utils.extension_path_user(<pacote raiz>, path="standards", create=True)` | 🟢 |
| `values_to_document` | `(name, uid, market, source, version, updated_at, values, raw_attributes=())` | F-13 | 🟢 |
| `document_to_values` | `(document)` | `(values, warnings)` ou `StandardFileError` (F-14) | 🟢 |
| `write_document` / `read_document` | `(path, document)` / `(path)` | atômica / erro "JSON inválido (linha L, coluna C)." ou "Não foi possível ler o arquivo: …" | 🟢 |
| `export_definition` | `(path, definition)` | grava e devolve o documento | 🟢 |
| `import_definition` | `(scene, path, on_conflict='rename')` | `(definição, avisos)`; `'replace'` remove a homônima não embutida | 🟢 |
| `PromobFormatError` | `Exception` | — | 🟢 |
| `PromobDocument` | dataclass `(name, version="-1", is_system="False", changed="True", attributes=[])` | `attributes`: `[(id, valor)]` | 🟢 |
| `ASSEMBLY_ID`, `ASSEMBLY_VALUES` | `'CAFF_MONTAGEM'`, `('LATERAL', 'BASE')` | — | 🟢 |
| `read_dimensionexport` | `(path)` | F-15 | 🟢 |
| `to_definition_data` | `(doc)` | `{'name','values','raw_attributes','report','assembly'}` (F-15) | 🟢 |
| `build_attributes` | `(values, raw_attributes)` | `[(id, texto)]` (F-16) | 🟢 |
| `write_dimensionexport` | `(path, name, values, raw_attributes, assembly=None)` | F-16 | 🟢 |
| `attributes_from_values` | `(values)` | crus sintéticos `{'id': código, 'value': '', 'key': chave}` para cada código de cada chave presente | 🟢 |

### `standards/migration.py` e `previews.py`

| Símbolo | Valor / assinatura | Comportamento | Confiança |
|---|---|---|---|
| `MIGRATED_FLAG`, `MIGRATED_NAME` | `'btm_standards_migrated'`, `"Migrada"` | — | 🟢 |
| `CONFIG_COMPONENTS` | `config_lateral→(LAT)`, `config_divisoria→(DIV)`, `config_base→(BAS)`, `config_fundo→(FUN_INF, FUN_SUP, FUN_ALT)`, `config_prateleira→(PRAT)`, `config_porta→(POR)` | Linha COZ | 🟢 |
| `CONFIG_FIELDS` | `('material','max_width','max_length','thickness','edge_1'..'edge_4')` | m → mm, exceto material | 🟢 |
| `DIMENSION_SETTINGS_KEYS` | `carcass_thickness→COZ LAT/DIV/BAS.thickness`; `back_thickness→COZ FUN_INF/FUN_SUP/FUN_ALT.thickness`; `door_thickness→POR`; `shelf_thickness→PRAT`; `height_default→COZ.external.base_height`; `depth_default→base_depth`; `base_height→toe_kick_height` | m → mm | 🟢 |
| `legacy_values` | `(settings)` | F-17 | 🟢 |
| `migrate_scene` / `stamp_standard_uid` / `run` | `(scene)` / `(scene)` / `(scene=None)` | F-17; `run` devolve lista de `'M-0x'` aplicadas | 🟢 |
| `register` / `unregister` | — | timer `_startup_timer` (`first_interval=0.5`, sem repetição) / remove se registrado | 🟢 |
| `REFS_DIR` | `caffmob_draw/assets/dimension_refs` | 34 PNGs no pacote | 🟢 |
| `image_path` / `icon_id` | `(image_key)` | `<REFS_DIR>/<key>.png` / F-18 | 🟢 |

### Operadores (`operators/ops_standards.py`)

| `bl_idname` | Classe | `bl_options` | Propriedades | Comportamento | Confiança |
|---|---|---|---|---|---|
| `caffmob.standards_configurator` | `BTM_OT_StandardsConfigurator` | REGISTER, UNDO | — | `invoke`: `begin_draft`; diálogo `invoke_props_dialog(width=980, title="Configurador de Dimensões", confirm_text="Fechar" se embutida senão "Aplicar")`. `execute`: embutida → FINISHED sem efeito; senão `apply_draft(modules=[])` e `ask_apply(context, definition.uid)` | 🟢 |
| `caffmob.standards_apply` | `BTM_OT_StandardsApply` | REGISTER, UNDO | — | `apply_draft(modules=[])` + `ask_apply(uid do rascunho)` | 🟢 |
| `caffmob.standards_set_active` | `BTM_OT_StandardsSetActive` | REGISTER, UNDO; `bl_property="definition"` | `definition: Enum` dinâmico `(uid, nome, source, ícone, índice)`; vazio → `('NONE', "Nenhuma", …)` | guarda uid anterior, `set_active`, `sync.apply_definition(modules=[])`, `ask_apply(uid anterior)` | 🟢 |
| `caffmob.standards_duplicate` | `BTM_OT_StandardsDuplicate` | REGISTER, UNDO | — | `ensure_ready` + `duplicate_definition(ativa)`; se `draft.definition_uid` não vazio, redireciona o rascunho para a cópia | 🟢 |
| `caffmob.standards_rename` | `BTM_OT_StandardsRename` | REGISTER, UNDO | `name: String` | `poll`: ativa existe e não é embutida; nome vazio após `strip` → erro "Informe um nome."; nome diferente → `unique_name` | 🟢 |
| `caffmob.standards_delete` | `BTM_OT_StandardsDelete` | REGISTER, UNDO | — | mesmo `poll`; `invoke_confirm` "Excluir \"<nome>\"?"; `remove_definition` | 🟢 |
| `caffmob.standards_export_json` | `BTM_OT_StandardsExportJSON` (ExportHelper) | REGISTER | `filename_ext=".btmdim.json"`, `filter_glob="*.btmdim.json;*.json"` | `invoke` sugere `user_folder()/<nome saneado>.btmdim.json` (caracteres fora de alfanumérico e ` -_.` viram `_`; vazio → "padrao"); `OSError` → erro | 🟢 |
| `caffmob.standards_import_json` | `BTM_OT_StandardsImportJSON` (ImportHelper) | REGISTER, UNDO | idem | `import_definition` (rename); captura `StandardFileError` e `StandardsError`; relatório | 🟢 |
| `caffmob.standards_import_promob` | `BTM_OT_StandardsImportPromob` (ImportHelper) | REGISTER, UNDO | `.xml`, `"*.xml;*.dimensionExport"` | F-15 + criação (BR, PROMOB_IMPORT, `fill_from_schema`, `set_value` por chave, crus, `assembly`); relatório | 🟢 |
| `caffmob.standards_export_promob` | `BTM_OT_StandardsExportPromob` (ExportHelper) | REGISTER | `.xml`, `"*.xml"` | crus da definição ou `attributes_from_values`; `write_dimensionexport(assembly=definition.assembly)` | 🟢 |
| `caffmob.standards_report` | `BTM_OT_StandardsReport` | INTERNAL | — | `invoke_popup(width=620)` com `_LAST_REPORT` | 🟢 |
| `caffmob.standards_apply_scene` | `BTM_OT_StandardsApplyScene` | REGISTER, UNDO | `previous_uid: String`, `apply_differ: Bool = False`, `interactive: Bool = False` (todos HIDDEN, SKIP_SAVE) | F-10 | 🟢 |
| `caffmob.standards_apply_differ` | `BTM_OT_StandardsApplyDiffer` | REGISTER, UNDO | `previous_uid` (HIDDEN, SKIP_SAVE) | F-10 | 🟢 |

🟢 Módulo: `_LAST_REPORT = {'title': "", 'lines': []}` (processo, não salvo), `PENDING_ROWS = 8`; `_show_report` e `ask_apply` não fazem nada se `bpy.app.background` ou `context.window is None`. Linhas do relatório de aplicação (`_apply_report_lines`): definição; "Módulos atualizados: N (cozinha F, dormitório C)"; até 20 alterações + "… e mais N"; até 10 medidas manuais; até 10 chaves sem destino.

🟢 Layout do Configurador (`draw`): cabeçalho (embutida: rótulo "<nome> (somente leitura)" + botão Duplicar; senão campo "Definição" = `definition_name`); `split(factor=0.55)`: esquerda busca + `template_list("BTM_UL_StandardsTree", …, rows=20, maxrows=20)`; direita `draw_editor` (ícone `template_icon(scale=12)` ou "Imagem de referência indisponível.", título linha › componente, rótulo, campo `edit_text`/`edit_enum`, "Faixa: <min> a <max>" na unidade do usuário, erro em `alert`); pendências (até 8); montagem `expand=True` só para não embutida; dica "Ao aplicar, o sistema pergunta…" se houver pendências.

🟢 `BTM_UL_StandardsTree` (`ui/standards_tree.py`): indentação `separator(factor=1.6)` por nível; grupo com `DISCLOSURE_TRI_DOWN` (aberto ou busca ativa) / `DISCLOSURE_TRI_RIGHT`; parâmetro com ícone `DOT` se selecionado (`BLANK1` senão) e valor do rascunho à direita via `format_param_value` na unidade da cena; `filter_items` devolve `([], [])` (filtragem é feita em `rebuild_tree`).

## Fluxos

**F-01 — Construção de `PARAMS`** 🟢 `dimension_schema.py:_build`: (1) 5 máximas (`line='GLOBAL'`, `GROUP_MAX`); (2) para cada linha em `LINE_CODES`: 13 externas (com exceções DOR, `promob_codes` dos externos Promob, `legacy_targets`), depois para cada componente em `COMPONENTS` os 8 campos de `SHEET_FIELDS`. Padrões US passam por `round(us, 4)` (exceto material e fitas). Ordem de inserção = ordem usada por `params_for`, árvore e JSON.

**F-02 — `validate(param, value)`** 🟢: ENUM → `value in enum_items`, senão "Valor Inválido: <rótulo> deve ser um de MDF, MDP, … (recebido: v)."; FLOAT → `float(value)` (falha: "… precisa ser numérico (recebido: v)."); `< 0` e não `negative_allowed` → "… não aceita valor negativo."; fora de `[min, max]` → "… deve estar entre <min> e <max> <unidade> (recebido: <v> <unidade>)." com `_fmt` = 1 casa, sem zeros finais, vírgula. `True` é aceito como 1.0.

**F-03 — Projeto pronto** 🟢 `api.ensure_ready`: `standards(scene)` (None → `StandardsError`) → `ensure_builtins` → corrige `active_index`.

**F-04 — Duplicar** 🟢 `api.duplicate_definition`: localizar índice da origem por ponteiro → `definitions.add()` → reobter origem por índice e nova pelo último → preencher campos (RN-08) → `copy_values` → copiar crus → `set_active(nova)`.

**F-05 — Abrir rascunho** 🟢 `api.begin_draft`: `ensure_ready` → ativa → `draft.definition_uid/name` ← definição; `error = ""`; `include_manual = False`; `copy_values(definição, rascunho)` (montagem + valores); `fill_from_schema(rascunho, mercado)`; `rebuild_tree`. Não limpa `expanded`, `search`, `selected_key`, `edit_text`.

**F-06 — Pendências** 🟢 `api.pending_changes`: definição do rascunho ausente → `[]`. Montagem diferente → item `{'key': 'assembly', 'label': "Montagem", 'old'/'new': "Lateral passante"/"Base passante"}` primeiro. Depois, para cada valor do rascunho com parâmetro conhecido: compara com `get_definition_value`; rótulo `"<Linha ou 'Medidas Máximas'> › [<Componente> › ]<Parâmetro>"` (traduzidos); `old/new` formatados na unidade do usuário.

**F-07 — Árvore** 🟢 `api.rebuild_tree`: limpa `tree`; `search = strip().lower()`; um grupo está aberto se há busca ou o caminho está em `expanded`. Casa se busca vazia ou contida em `label_pt.lower()`, `key.lower()` ou no rótulo do componente. Itens (rótulo, tipo, profundidade, caminho, chave): "Medidas Máximas" GROUP 0 `MAX` → parâmetros PARAM 1. Para cada linha com algo que case: linha GROUP 0 `<L>`; "Dimensões Externas" GROUP 1 `<L>/EXT` → PARAM 2; para `CHAPAS` ("Chapas") e `COMPONENTES` ("Componentes"): GROUP 1 `<L>/<árvore>` → componente GROUP 2 `<L>/<árvore>/<código>` → PARAM 3. Filhos de grupo fechado não entram. No fim, com `draft['_suppress'] = True`, `tree_index = min(tree_index, max(len-1, 0))`; a chave `_suppress` é apagada em `finally`.

**F-08 — Seleção e edição** 🟢 `api.select_param/commit_edit_text/commit_edit_enum`: clique em PARAM → `selected_key = key`, `error = ""`, preenche `edit_enum` (texto) ou `edit_text = format_param_value(valor, unidade)` sob `_suppress` (valor ausente → padrão BR). Ao confirmar texto: ignora se `_suppress`, parâmetro ausente ou ENUM; `units.parse_length(texto, unidade, allow_negative=param.negative_allowed)` (m) → `set_draft_value(round(m·1000, 4))` → `error = ""`; `ValueError`/`StandardsError` → `error = str(exc)` e o valor anterior fica. ENUM análogo com `set_draft_value(edit_enum)`.

**F-09 — Medidas de armário novo** 🟢 `cabinet_defaults.defaults`: (1) tipo fora de `EXTERNAL` → `'BASE'`; (2) `values` vazio/None → fallback "Sem Padrão de Dimensões ativo: medidas de fábrica"; (3) linha fora de `LINES` ou sem `<L>.external.base_height` → fallback "O padrão não tem a linha {}: medidas de fábrica"; (4) `meters(k, d)` = `float(values[k])/1000` ou `d` em `KeyError/TypeError/ValueError`; largura do `FALLBACK`; altura/profundidade das externas; Z da externa só se houver chave (WALL), senão 0; (5) espessura por papel de `ROLE_COMPONENT` com fallback 0,006 (BACK) ou 0,018; `carcass = thickness['LEFT']`; `warning = None`. Fallback: espessuras de todos os papéis 0,018 exceto BACK 0,006; `carcass = 0,018`.

**F-10 — Duas perguntas** 🟢 `ops_standards.py`: `ask_apply(context, previous_uid)` → `caffmob.standards_apply_scene('INVOKE_DEFAULT', previous_uid)`. `invoke`: `interactive = True`; `plan_for`; sem segue nem difere → se houver não aplicáveis, INFO "Nenhum módulo CAFFMob na cena; N item(ns) não aplicável(is)" e FINISHED; senão diálogo "Aplicar a todos os módulos existentes na cena?" (`confirm_text="Sim"`; desenho: contagens segue/difere/não aplicável e, com herdados, "Converta os armários antigos para CAFFMob para que recebam o padrão"; dica "Cancelar = Não"). `execute`: recalcula `plan_for`; `_apply_names(follow)`; se houver difere: interativo → `caffmob.standards_apply_differ('INVOKE_DEFAULT', previous_uid)`; EXEC com `apply_differ` → `_apply_names(differ)`; INFO "N módulo(s) atualizados". 2ª pergunta: diálogo lista até 6 nomes de difere (+ "e mais N"); `execute` recalcula o plano e aplica difere. `_apply_names`: definição ativa; objetos por nome; vazio → 0; `sync.apply_definition(scene, ativa, modules=escolhidos)`; grava relatório; devolve `report['caffmob']`.

**F-11 — `apply_definition`** 🟢 `sync.py`: `_SYNC_DEPTH[0] += 1` → `try: _apply_definition finally: -= 1`. `_apply_definition`: (1) `scene = scene or context.scene`; `values = definition_values`; (2) `write_legacy_targets`: para cada chave com destinos e presente: `m = v/1000`; para cada destino `"grupo.prop"` e cada cena de `_scenes_for` (principal + a dada, se diferente): grupo ou prop inexistente → pula; difere de `m` por > 1e-9 → `setattr`; anota o destino; (3) `skip = make_skip`; (4) `_tag_lines`; (5) `modules is None` → CAFFMob de `scene_modules` com `include_manual or not own`; (6) para cada objeto ainda em `bpy.data.objects` e CAFFMob → `apply_to_module`; (7) se `gate.legacy_ui(context)`: conta gaiolas frameless e, havendo e existindo `scene.hb_frameless`, `ops_defaults.update_material_thickness_prompts/update_toe_kick_prompts/update_cabinet_sizes(context, skip)`; `_update_closets` se existir `scene.hb_closets`; (8) `btm_settings.cut_plan_stale = True`; (9) relatório.

**F-12 — `apply_to_module`** 🟢: `found = defaults(values, cab.line, cab.cabinet_type)`; dentro de `suspended_geometry()`: `cab.height, cab.depth, cab.thickness = found.height, found.depth, found.carcass`; para TOP, BOTTOM, BACK, LEFT, RIGHT: `thickness_<papel> = 0.0` se `|v − carcass| < 1e-9`, senão `v`; `cab.assembly = definition.assembly`. Depois: `btm_structure.components[*].thickness = 0.0`; `clear_overrides`; `obj['btm_standard_uid'] = uid`; `obj['btm_line'] = cab.line`; `update_cabinet_geom(cab, context)` uma vez. Não toca largura, `found.z`, localização, materiais ou divisões.

**F-13 — Exportar JSON** 🟢 `io_json.values_to_document`: ignora chaves desconhecidas; `GROUP_MAX` → `max_measures[campo]`; externos → `lines[L]['external'][campo]`; chapa → `lines[L]['sheets' se CHAPAS senão 'components'][comp]`, criado como `{'edges': [0.0]*4}`; fita → `edges[n-1]`; demais campos → chave própria. Documento: `schema, schema_version, uid, name, market, source ('BUILTIN' → 'USER'), version, updated_at, unit 'mm', max_measures, lines, raw_attributes [{id, value, key}]`.

**F-14 — Importar JSON** 🟢 `document_to_values` → `import_definition`: (1) não-dict ou `schema` fora de `ACCEPTED_FORMATS` → "O arquivo não é uma definição de dimensões do CAFFMob Draw."; `schema_version` não-int → "Versão do formato ausente."; > 1 → "Arquivo criado por uma versão mais nova…"; `unit` (padrão "mm") ≠ "mm" → erro; (2) `put(chave, v)`: desconhecida → aviso "Parâmetro desconhecido ignorado: k"; válida → guarda (`float` se FLOAT); inválida → erro acumulado; linhas fora de `LINE_CODES` → aviso; `edges` expande para `edge_1..4`; (3) erros → "Valores fora do domínio:\n…"; (4) `ensure_ready`; nome = `name` ou "Definição importada"; conflito: `replace` e não embutida → remove; senão `unique_name`; (5) `definitions.add()`; uid novo; mercado do arquivo se BR/US senão BR; `source='USER'`; `version = int(version or 1)`; `updated_at` do arquivo ou agora; `fill_from_schema`; `set_value` por chave; crus. Não ativa; `assembly` fica no padrão RNA (LATERAL).

**F-15 — Importar Promob** 🟢 `read_dimensionexport`: `ET.parse` (erro → "Arquivo XML inválido (linha, coluna)." ou "Não foi possível ler o arquivo"); raiz ≠ `DIMENSIONEXPORT` → erro com a tag; nome = `DEFINITION@DESCRIPTION` com espaços colapsados, vazio → "Configuração importada do Promob"; `VERSION`, `ISSYSTEM`, `CHANGED` guardados; cada `ATTRIBUTE` com `ID` (em qualquer profundidade, `root.iter`) → `(id, VALUE or '')`; nenhum → "O arquivo não contém atributos de dimensão.". `to_definition_data`: separa `CAFF_MONTAGEM` (`strip().upper()` em LATERAL/BASE; senão LATERAL + `assembly_warning`); `total` = demais; `seen` guarda o último texto por ID e marca duplicados; para cada ocorrência: código em `PROMOB_INDEX` → converte o último texto (ENUM `strip()`; FLOAT `_parse_number` com vírgula→ponto) e valida; ok → `values[chave]`, `mapped += 1`; senão → `invalid` e `unrecognized`, chave "". Código desconhecido → `unrecognized` (e `confirmed_without_equivalent` se `parse_promob_id` o reconhece). Cada ocorrência vira cru `{id, value: texto original, key}`.

**F-16 — Exportar Promob** 🟢 `build_attributes`: cru com chave presente em `values` → ENUM `str(atual)`; FLOAT mantém o original se `|parse(original) − atual| < 1e-6`, senão `_format_number` (`f"{v:.4f}"` sem zeros/ponto finais, vazio → "0", ponto → vírgula); sem chave → texto original. `write_dimensionexport`: `<DIMENSIONEXPORT VERSION="-1"><DEFINITION DESCRIPTION=nome ISSYSTEM="False" CHANGED="True"><ATTRIBUTES>` + `ATTRIBUTE ID VALUE` (descarta crus `CAFF_MONTAGEM`) + `CAFF_MONTAGEM` no fim se `assembly ∈ ASSEMBLY_VALUES`; `ET.indent(space="  ")`; cabeçalho `<?xml version="1.0" encoding="utf-8"?>\n`; escrita atômica.

**F-17 — Migração** 🟢 `migration.run`: cena principal (None → `[]`); `migrate_scene`: sem `btm_standards` ou já marcada → `[]`; `had = len(definitions) > 0`; `ensure_ready`; sem definições antes → ativa US se há objeto com tag frameless/closet, senão BR (`M-02`); `legacy_values(btm_settings)`: `dimension_settings` com `is_property_set` → chaves ×1000; depois grupos `config_*` (sobrescrevem as mesmas chaves) com `is_property_set` por campo (material cru, demais ×1000); só os válidos; havendo valores e nenhuma definição "Migrada": `duplicate_definition(BR, "Migrada")`, `source='MIGRATED'`, `set_values`, ativa (`M-01`); `scene['btm_standards_migrated'] = 1`. Depois `stamp_standard_uid`: com definição ativa, toda raiz `classify.module_library(obj)` (FRAMELESS, FACE_FRAME, CLOSETS ou BTM) sem uid recebe o uid ativo (`M-03`). `StandardsError` é capturado e impresso; outras exceções propagam. Chamadores: `caffmob_draw/__init__.py:99` (`load_file_post`, após `hb_project.ensure_main_scene`) e `_startup_timer` (0,5 s após registrar).

**F-18 — Imagem** 🟢 `previews.icon_id`: chave vazia → 0; já carregada → `icon_id`; arquivo ausente → 0 e aviso único "CAFFMob Draw: imagem de referência ausente: <path>"; senão `pcoll.load(key, path, 'IMAGE').icon_id`.

## Dependências

- 🟢 `hb_project.get_main_scene` — cena que guarda o padrão (`api.main_scene`).
- 🟢 `data.units` — `get_scene_length_unit`, `format_length`, `parse_length` (Configurador; ver `_reversa_sdd/data/`).
- 🟢 `data.i18n` — `tr`, `N_` (mensagens e rótulos).
- 🟢 `selection.classify` — `btm_kind`, `module_library`, `module_root`, `free_group` (ver `_reversa_sdd/selection/`).
- 🟢 `legacy.gate` — `legacy_ui(context)`, `legacy_roots(scene)` (ADR 0006).
- 🟢 `cabinet_editor.bridge.is_own_standard`/`origin_definition` e `cabinet_editor.structure.ROLE_COMPONENT` (ver `_reversa_sdd/cabinet_editor/`).
- 🟢 `data.properties.suspended_geometry` e `update_cabinet_geom`; `Object.btm_cabinet` (`line`, `cabinet_type`, `height`, `depth`, `thickness`, `thickness_top/bottom/back/left/right`, `assembly`); `Object.btm_structure.components[*].thickness`.
- 🟢 `product_libraries.frameless.operators.ops_defaults` (3 funções `(context, skip)`) e `product_libraries.closets.types_closets.recalculate_closet_starter`; `Scene.hb_frameless`, `Scene.hb_closets`, `Object.hb_closet_starter`.
- 🟢 `Scene.btm_settings` (`cut_plan_stale`, `dimension_settings`, `config_*`).
- 🟢 Consumidores: `operators/cabinet_builder.py:standard_defaults/build_module` (grava `btm_standard_uid`), `library_panel/ops_cabinet.py`, `legacy/convert.py:_build`, `cabinet_editor/bridge.py:configured_part`, `cabinet_editor/scene_divisions.py:configured`, `cutting/part_extractor.py:_active_values`, `operators/ops_cutting.py:project_info/standard_info`, `ui/panels.py:draw_standards_box` (`SUMMARY_KEYS`), `selection/editing.py` e bibliotecas frameless/closets (`add_override`, `is_syncing`), `legacy/ops.py` (`_set_report`).

## Decisões de Design Identificadas

| Decisão | Evidência | Confiança |
|---|---|---|
| Esquema declarativo separado dos valores (valores em coleção genérica por chave) | `dimension_schema.py` docstring; `model.py:BTM_PG_StandardValue` | 🟢 |
| Embutidas somente leitura; edição por duplicação | `api.py:set_value`; `ops_standards.py:BTM_OT_StandardsConfigurator.draw` | 🟢 |
| Rascunho no WindowManager, gravado só ao aplicar (D-16) | `model.py:BTM_PG_StandardsDraft`; ADR 0004 | 🟢 |
| Mudar o padrão global não altera módulos sem as duas perguntas (D-22) | `ops_standards.py` docstring e `ask_apply` | 🟢 |
| Origem do módulo por `btm_standard_uid` para separar segue/difere (ADR 0003) | `apply_core.plan`; `sync.apply_to_module`; `migration.stamp_standard_uid` | 🟢 |
| Largura nunca vem do padrão | `cabinet_defaults.py` docstring; `sync.apply_to_module` | 🟢 |
| Montagem fora do Promob, transportada em `CAFF_MONTAGEM` (D-27) | `io_promob.py:ASSEMBLY_ID` | 🟢 |
| Reexportação Promob sem perda guardando crus na ordem | `model.py:BTM_PG_RawAttribute`; `io_promob.build_attributes` | 🟢 |
| Suporte legado só com a preferência ligada (ADR 0006) | `sync.py:_apply_definition` | 🟢 |
| Namespace `caffmob.standards_*` (diverge da convenção `btm.*`/`caffmob_draw.*` do `CLAUDE.md` para código novo) | `ops_standards.py` | 🟢 |

## Estado Interno

- 🟢 Persistente no `.blend`: `Scene.btm_standards` (cena principal); custom properties na raiz do módulo `btm_overrides` (JSON), `btm_line`, `btm_standard_uid`; `scene['btm_standards_migrated'] = 1`.
- 🟢 Sessão: `WindowManager.btm_standards_draft` (inclui `_suppress` temporário); `_SYNC_DEPTH = [0]`; `_ENUM_ITEMS_CACHE`; `previews._collection`/`_missing`; `ops_standards._LAST_REPORT`; `_definition_items.cache`.
- 🟢 Ciclo do rascunho: vazio → `begin_draft` (cópia) → edições (valores/montagem/nome) → `apply_draft` grava, ou fechar o diálogo descarta (nada é revertido porque nada foi gravado). O rascunho permanece no WM depois de fechado e é sobrescrito no próximo `begin_draft`.

## Observabilidade

- 🟢 `print` no console: imagem de referência ausente (uma vez por chave) e "migração do Padrão de Dimensões não aplicada: <erro>".
- 🟢 `self.report` INFO/WARNING/ERROR nos operadores; relatório em popup (`caffmob.standards_report`) após importações e aplicações com janela.
- 🟢 Sem logs persistentes nem métricas.

## Riscos e Lacunas

- 🟢 JSON não transporta `assembly`: ida e volta de uma definição "Base passante" volta como LATERAL (`io_json.py`). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-48):** transportar, opcional na leitura. Pendência de implementação: DT-01.
- 🟢 `validate` aceita NaN (e `True` como 1,0); valores não finitos podem chegar à geometria por JSON (`dimension_schema.py:validate`). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-49):** recusar não finitos com `math.isfinite`. Pendência de implementação: DT-02.
- 🔴 `document_to_values` não valida a forma interna (`lines` com lista, `edges` não lista) → `AttributeError`/`TypeError` não capturados pelo operador (EC-05).
- 🟢 Docstrings divergentes do código _(Revisão 2026-10-10: sync.py:170-171 docstring "None = todos os que seguem" × 263-265 que filtra só por `own`; ops_standards.py:177 e 211 "atualiza os módulos" × `modules=[]` em 187 e 239; standards/__init__.py:10 "propagação para as bibliotecas legadas")_: `sync.apply_definition` diz "None = todos os que seguem o padrão", mas `None` não compara UID (RN-STANDARDS-09 em `domain.md`); `BTM_OT_StandardsSetActive`/`StandardsApply` dizem "atualiza os módulos", mas usam `modules=[]`; `standards/__init__.py` descreve `sync` como "propagação para as bibliotecas legadas" (pré-012).
- 🟢 `draft.include_manual`, `sync.affected_modules`, `apply_core.targets`, `api.tree_image_key`, `schema.canonical_component`, `Standards.schema_version` não têm consumidor no pacote _(Revisão 2026-10-10: grep em caffmob_draw/ só encontra as definições; `targets` só em tests/test_standards_apply_core.py:31-33)_.
