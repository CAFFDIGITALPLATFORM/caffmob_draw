# Geometria livre: placa e caixa (geometry_free) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/geometry_free/` em 2026-10-10 (sem alterações pendentes na pasta). IDs RN/RF/CA de `requirements.md`; EC de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender. Fluxogramas: `_reversa_sdd/flowcharts/geometry_free.md`, `geometry_free-modal.md`, `geometry_free-edit.md`, `geometry_free-sheets.md`; máquina de estados em `_reversa_sdd/state-machines.md` › Geometria livre.

## Visão de Camadas

| Camada | Arquivo | Importa | Papel | Confiança |
|---|---|---|---|---|
| Fachada | `__init__.py` | (tardio) `ops_create`, `ops_edit`, `props` | Registra `props` → `ops_create` → `ops_edit`; desregistra na ordem inversa | 🟢 |
| Dados | `props.py` | `bpy`, `data.i18n.N_`, `data.dimension_schema` | `BTM_PG_GeometryProps` + `Object.btm_geometry`; callback `_update` (import tardio de `mesh`) | 🟢 |
| Medida e malha | `mesh.py` | `bmesh`, `bpy` | `size`/`sheets` puras; `update`, `create_object`, `is_geometry` | 🟢 |
| Criação | `ops_create.py` | `bpy`, `bpy_extras.view3d_utils`, `mathutils.Vector`, `mathutils.geometry.intersect_line_plane`, `data.i18n.tr`, `hb_snap`, `data.units`, `mesh` | Modal `caffmob.geometry_create` | 🟢 |
| Edição | `ops_edit.py` | `bpy`, `mathutils.Vector`, `mesh` | Duplicar, espelhar, excluir | 🟢 |

🟢 Registro no pacote: `caffmob_draw/__init__.py:34` importa `geometry_free`; `geometry_free.register()` na linha 295 (depois de `walls2d`, antes de `ui`, que desenha os botões e o painel); `geometry_free.unregister()` na linha 371 (depois de `ui.unregister()`, antes de `walls2d.unregister()`). O nome consta da lista de hot-reload da linha 10.

🟢 A unit não registra handlers de aplicação, timers, draw handlers nem keymaps. O único handler é o `modal_handler_add` do operador de criação, encerrado por `_finish`/`_cancel` (ver Riscos para a saída externa).

## Modelo de Dados

### `BTM_PG_GeometryProps` → `bpy.types.Object.btm_geometry` (`PointerProperty`, persistido no `.blend`)

| Propriedade | Tipo / padrão | Limites / itens | `update` | Confiança |
|---|---|---|---|---|
| `kind` | `EnumProperty` `name="Forma"`, padrão `'PLACA'` | `KINDS = [('PLACA', "Placa", "Uma chapa"), ('CAIXA', "Caixa", "Uma caixa fechada de seis chapas")]` | `_update` | 🟢 |
| `plane` | `EnumProperty` `name="Posição da Placa"`, padrão `'XY'` | `PLANES = [('XY', "Deitada", "Espessura na vertical (Z)"), ('XZ', "Em pé, de frente", "Espessura na profundidade (Y)"), ('YZ', "Em pé, de lado", "Espessura na largura (X)")]` | `_update` | 🟢 |
| `width` | `FloatProperty` `name=N_("Largura")`, 0,6 | `subtype='DISTANCE'`, `unit='LENGTH'`, `min=0,001`, `max=10,0`, `precision=1` | `_update` | 🟢 |
| `depth` | idem, `N_("Profundidade")`, 0,4 | idem | `_update` | 🟢 |
| `height` | idem, `N_("Altura")`, 0,4 | idem | `_update` | 🟢 |
| `thickness` | idem, `N_("Espessura")`, 0,018, descrição `N_("Espessura da placa; numa caixa, das seis placas")` | idem | `_update` | 🟢 |
| `fabrication` | `BoolProperty` `name="Peça de Fabricação"`, `False`, descrição "Entra na lista de peças e no orçamento; sem a marca é só visual" | — | — | 🟢 |
| `component` | `EnumProperty` `name="Componente"`, padrão `'ESP'` | `COMPONENT_ITEMS = [(c.code, c.label_pt, "") for c in dimension_schema.COMPONENTS]` (20 componentes; `ESP` = "Especial") | — | 🟢 |
| `material` | `StringProperty` `name="Matéria-prima"`, `"MDF"` | texto livre | — | 🟢 |
| `finish` | `StringProperty` `name="Acabamento"`, `""` | texto livre | — | 🟢 |

🟢 Todas as anotações levam `# type: ignore`. O ponteiro é criado em `props.register()` depois de registrar a classe e removido em `props.unregister()` com `hasattr` antes de desregistrar a classe. Como é um `PointerProperty` em `bpy.types.Object`, **todo** objeto tem `btm_geometry` enquanto o pacote está registrado (`getattr(obj, 'btm_geometry', None)` nunca é `None`).

### Marcas no objeto

| Item | Valor | Quem grava / lê | Confiança |
|---|---|---|---|
| `btm_plane.object_kind` | `'GEOMETRY'` (enum de `data/properties.py:BTM_PG_InsertionPlane`, padrão `'WALL'`) | grava `mesh.create_object`; lê `mesh.is_geometry`, `selection/classify.py:_btm_kind`, `overlays/draw_handlers.py:184` | 🟢 |
| idprop `IS_BTM_GEOMETRY` | `True` | grava `mesh.create_object`; nenhum leitor | 🟢 |
| idprop `HB_CURRENT_DRAW_OBJ` | `True` durante o modal | grava `invoke`; apaga `_finish`; lê `hb_snap.best_hit` (exclui do raycast) | 🟢 |
| idprop `btm_mirrored` | `True` ou ausente | grava/apaga `BTM_OT_GeometryMirror` | 🟢 |
| idprop `btm_uid` | 12 hex | grava `cutting/part_sources.py:ensure_module_uid` na 1ª extração; apaga `BTM_OT_GeometryDuplicate` na cópia; lê `cutting/stale.py` (marca plano desatualizado) | 🟢 |
| Nome do objeto e da malha | `"Placa"` ou `"Caixa"` (ou `name`), com sufixo `.001` do Blender em colisão | `mesh.create_object` | 🟢 |

### Estado do modal (`BTM_OT_GeometryCreate`, atributos Python, efêmeros)

| Atributo | Tipo | Significado | Confiança |
|---|---|---|---|
| `kind` | `EnumProperty` `name="Forma"` `PLACA`/`CAIXA`, padrão `PLACA` | forma a criar (o botão define) | 🟢 |
| `region` | `bpy.types.Region` | região do `invoke`; usada por `_ray` e `hb_snap` | 🟢 |
| `mouse_pos` | `Vector((x, y))` | `event.mouse_region_x/y` | 🟢 |
| `step` | `int` 0/1/2 | canto / largura-profundidade / altura | 🟢 |
| `corner` | `Vector` ou `None` | cópia de `obj.location` no 1º clique | 🟢 |
| `typed` | `str` | buffer de digitação | 🟢 |
| `typed_width` | `float` ou `None` | largura digitada (trava o X do mouse) | 🟢 |
| `obj` | `bpy.types.Object` | a peça em criação (referência RNA direta) | 🟢 |
| `hit_location`, `hit_grid`, `hit_face_index`, `hit_object`, `view_point` | escritos por `hb_snap.main` | resultado do encaixe | 🟢 |

### Chapa de produção

🟢 Tupla `(nome, comprimento, largura, espessura)` em metros (`mesh.sheets`); o consumidor `geometry_records` converte em `PartRecord` (campos em `cutting/part_sources.py:PartRecord`; contrato geral da produção em `_reversa_sdd/cutting/design.md`).

## Interface

### `mesh.py`

| Assinatura | Contrato | Confiança |
|---|---|---|
| `GEOMETRY_FLAG = 'IS_BTM_GEOMETRY'` | nome da idprop de marca | 🟢 |
| `size(kind, plane, width, depth, height, thickness) -> (x, y, z)` | RN-02; puro | 🟢 |
| `sheets(kind, plane, width, depth, height, thickness) -> list[(str, float, float, float)]` | RN-14; puro | 🟢 |
| `_props(obj) -> (kind, plane, width, depth, height, thickness)` | lê `obj.btm_geometry` | 🟢 |
| `update(obj) -> None` | A-03; escreve `obj.data` e chama `obj.data.update()` | 🟢 |
| `create_object(context, kind='PLACA', name=None) -> Object` | F-01 passo 1 | 🟢 |
| `is_geometry(obj) -> bool` | `obj is not None and obj.type == 'MESH' and btm_plane existe and btm_plane.object_kind == 'GEOMETRY' and btm_geometry existe` | 🟢 |

### Operadores

| Classe | `bl_idname` | `bl_label` | `bl_options` | `poll` | Confiança |
|---|---|---|---|---|---|
| `BTM_OT_GeometryCreate` | `caffmob.geometry_create` | "Criar Geometria" | `{'REGISTER', 'UNDO'}` | `context.area` não nulo, `area.type == 'VIEW_3D'`, `context.mode == 'OBJECT'` | 🟢 |
| `BTM_OT_GeometryDuplicate` | `caffmob.geometry_duplicate` | "Duplicar Geometria" | herdado de `_GeometryAction`: `{'REGISTER', 'UNDO'}` | `context.mode == 'OBJECT'` e `is_geometry(context.active_object)` | 🟢 |
| `BTM_OT_GeometryMirror` | `caffmob.geometry_mirror` | "Espelhar Geometria" | idem | idem | 🟢 |
| `BTM_OT_GeometryDelete` | `caffmob.geometry_delete` | "Excluir Geometria" | idem | idem | 🟢 |

🟢 Docstrings (tooltips, traduzidas pelo catálogo): "Cria uma placa ou caixa por pontos de referência no ambiente", "Duplica a geometria ao lado da original", "Passa a geometria para o outro lado do ponto de origem (X local)", "Exclui a geometria". `_GeometryAction` é mixin (não `Operator`) com `bl_options` e `poll` de classe.

### Teclas do modal de criação

| Evento | Passo | Efeito | Confiança |
|---|---|---|---|
| `MIDDLEMOUSE`, `WHEELUPMOUSE`, `WHEELDOWNMOUSE` (qualquer valor) | todos | `PASS_THROUGH` (navegar) — testado **antes** de Esc | 🟢 |
| `ESC` ou `RIGHTMOUSE` `PRESS` | todos | `_cancel` | 🟢 |
| `MOUSEMOVE` | todos | atualiza `mouse_pos` e chama `_move(context, event.ctrl)` | 🟢 |
| `PRESS` com `event.unicode` em `"0123456789,."` | todos (inclusive 0) | acrescenta ao buffer e redesenha o cabeçalho | 🟢 |
| `BACK_SPACE` `PRESS` | todos | remove o último caractere | 🟢 |
| `RET`/`NUMPAD_ENTER` `PRESS` com buffer e `step > 0` | 1, 2 | `_typed_value` | 🟢 |
| `LEFTMOUSE` `PRESS` | todos | `_advance` | 🟢 |
| qualquer outro | — | `RUNNING_MODAL` (consumido; Ctrl só tem efeito no próximo `MOUSEMOVE`) | 🟢 |

🟢 `context.area.tag_redraw()` é chamado no começo de **todo** evento.

### Cabeçalho (`_header`, `context.area.header_text_set`)

| Passo | Texto (chave do catálogo) | Confiança |
|---|---|---|
| 0 | "Clique o canto da peça (Ctrl encaixa em vértices e arestas). Esc cancela." (o buffer não aparece) | 🟢 |
| 1 | "Largura {} × Profundidade {} — digite a {} e Enter, ou clique.{}" com `format_length(width)`, `format_length(depth)`, `tr("Largura")` se `typed_width is None` senão `tr("Profundidade")`, e o sufixo | 🟢 |
| 2 | "Altura {} — digite e Enter, ou clique.{}" | 🟢 |
| sufixo | `tr("  Digitado: {}").format(typed)` se há buffer, senão `""` | 🟢 |

🟢 `unit = units.get_scene_length_unit()` (`btm_settings.btm_unit` ou unidade da cena; padrão `MM`); `format_length(v, unit)` usa vírgula decimal e a precisão padrão da unidade (MM 1, CM 2, M 4).

## Algoritmos

### A-01 — `size` (RN-02)

```
se kind == 'PLACA':
    se plane == 'XY': devolve (width, depth, thickness)
    se plane == 'XZ': devolve (width, thickness, height)
    devolve (thickness, depth, height)        # YZ e qualquer outro valor
devolve (width, depth, height)                # CAIXA (plane ignorado)
```
🟢 `mesh.py:size`. Sonda: `size('PLACA','YZ',.6,.4,.4,.018) = (0.018, 0.4, 0.4)`; `size('CAIXA','XY',.6,.4,.7,.018) = (0.6, 0.4, 0.7)`.

### A-02 — `sheets` (RN-14)

```
se kind == 'PLACA':
    a, b, c = sorted(size(...), reverse=True)
    devolve [("Placa", a, b, c)]
t = thickness
inner_h = max(0.001, height - 2*t); inner_w = max(0.001, width - 2*t)
devolve [("Fundo", width, depth, t), ("Tampo", width, depth, t),
         ("Lateral esquerda", inner_h, depth, t), ("Lateral direita", inner_h, depth, t),
         ("Frente", inner_w, inner_h, t), ("Trás", inner_w, inner_h, t)]
```
🟢 `mesh.py:sheets`. Sondas: placa `XY` 0,6 × 0,01 com espessura 0,018 → `[("Placa", 0.6, 0.018, 0.01)]` (a profundidade de 10 mm vira a espessura); caixa 0,6 × 0,5 × 0,7 / 0,018 → laterais `0.664 × 0.5`, frente/trás `0.564 × 0.664`. Na caixa, `plane` e `depth − 2t` não entram (frente e trás têm a largura interna e a altura interna; fundo e tampo a profundidade inteira).

### A-03 — `update(obj)` (RN-03)

1. 🟢 `x, y, z = size(*_props(obj))`.
2. 🟢 `bm = bmesh.new()`; `bmesh.ops.create_cube(bm, size=1.0)` (vértices em ±0,5).
3. 🟢 Para cada vértice: `co.x = (co.x + 0,5) · x`, idem Y e Z → caixa `[0, x] × [0, y] × [0, z]`.
4. 🟢 `bm.to_mesh(obj.data)`; `bm.free()`; `obj.data.update()`.

🟢 Sem UV, materiais, normais personalizadas ou cavidade: a caixa é um sólido de 6 faces; as seis chapas só existem na produção.

### A-04 — `_update_footprint(point)` (RN-09)

```
dx, dy = point.x - corner.x, point.y - corner.y
width = typed_width se não None, senão max(MIN_SIZE, |dx|)
depth = max(MIN_SIZE, |dy|)
g.width, g.depth = width, depth                       # duas reconstruções da malha
obj.location = (corner.x - (width se dx < 0 senão 0),
                corner.y - (depth se dy < 0 senão 0),
                corner.z)
```
🟢 `ops_create.py:_update_footprint`; `MIN_SIZE = 0.001`. `point` vem de `_on_plane(corner, (0, 0, 1))` = `intersect_line_plane(origem, origem + vetor · 1e6, corner, normal)`; `None` (raio paralelo ao plano) → nada muda. O deslocamento usa o `width` não limitado pela propriedade (EC-07).

### A-05 — `_update_height()` (RN-10)

```
origem, vetor = _ray()                                # region_2d_to_origin_3d / region_2d_to_vector_3d
normal = (vetor.x, vetor.y, 0); se |normal| < 1e-6: retorna
anchor = obj.location.copy()
p = intersect_line_plane(origem, origem + vetor·1e6, anchor, normal.normalized())
se p não None: g.height = max(MIN_SIZE, p.z - anchor.z)
```
🟢 `ops_create.py:_update_height`. Mouse abaixo da origem → altura mínima 1 mm.

## Fluxos Principais

### F-01 — Criar (`caffmob.geometry_create`)

1. 🟢 `invoke`: guarda `region`, `mouse_pos`; `step = 0`, `corner = None`, `typed = ""`, `typed_width = None`.
2. 🟢 `obj = mesh.create_object(context, self.kind)`: malha e objeto com o rótulo `"Placa"`/`"Caixa"`, ligados a `context.collection` (coleção ativa), `obj['IS_BTM_GEOMETRY'] = True`, `obj.btm_plane.object_kind = 'GEOMETRY'`, `obj.btm_geometry.kind = kind` (dispara `_update`) e `mesh.update(obj)`. Posição inicial = `(0, 0, 0)` (padrão de `bpy.data.objects.new`).
3. 🟢 `obj['HB_CURRENT_DRAW_OBJ'] = True`; `g.width = g.depth = 0,01`; na caixa, `g.height = 0,01`.
4. 🟢 `modal_handler_add(self)`; `_header`; `RUNNING_MODAL`.
5. 🟢 Passo 0 (`_move`): `hb_snap.main(self, ctrl, context)` → se `hit_location` não é `None`, `obj.location = hit`. Clique: `corner = obj.location.copy()`, `step = 1`.
6. 🟢 Passo 1: A-04 a cada movimento. Clique (ou 2º Enter): placa → F-01.8; caixa → `step = 2`.
7. 🟢 Passo 2 (caixa): A-05 a cada movimento. Clique ou Enter → F-01.8.
8. 🟢 `_finish`: `header_text_set(None)`; `del obj['HB_CURRENT_DRAW_OBJ']`; `select_set(False)` em `context.selected_objects`; `obj.select_set(True)`; `view_layer.objects.active = obj`; `FINISHED`.
9. 🟢 Cancelar (`_cancel`): `header_text_set(None)`; `data = obj.data`; `bpy.data.objects.remove(obj, do_unlink=True)`; `bpy.data.meshes.remove(data)` se `data.users == 0`; `CANCELLED`.

### F-02 — Medida digitada (`_typed_value`)

1. 🟢 `value = units.parse_length(typed, units.get_scene_length_unit(), allow_zero=False)`; `ValueError` → `report({'WARNING'}, str(exc))`, `typed = ""`, `RUNNING_MODAL`.
2. 🟢 `typed = ""`. Passo 1 sem largura digitada: `typed_width = value`, `g.width = value`, cabeçalho, `RUNNING_MODAL` (a posição só é recalculada no próximo movimento — EC-06).
3. 🟢 Passo 1 com largura digitada: `g.depth = value` → `_advance` (sem recalcular `location` — EC-06).
4. 🟢 Passo 2: `g.height = value` → `_finish`.

🟢 `parse_length` (contrato de `data/units.py`): vírgula ou ponto decimal; sem sufixo vale a unidade da cena; `"600"` em MM = 0,6 m, em CM = 6,0 m; `"1.200"` em MM = 0,0012 m (ponto é decimal); `"0"` → "Valor Inválido: a medida não pode ser zero."; `"1,2,3"` → "Valor Inválido: \"1,2,3\" não é um número válido." (sondado). Como o modal só aceita `0-9 , .`, sufixos (`mm`, `cm`, `m`), sinal e contas (`expr`) nunca chegam ao parser.

### F-03 — Duplicar (`BTM_OT_GeometryDuplicate.execute`)

1. 🟢 `obj = _active_geometry(context)`; `copy = obj.copy()` (copia idprops, `btm_geometry`, `btm_plane`, `parent`, modificadores); `copy.data = obj.data.copy()`.
2. 🟢 `collection.objects.link(copy)` para cada `obj.users_collection`.
3. 🟢 `x = size(...)[0]`; `copy.matrix_world = obj.matrix_world.copy()`; `copy.location = obj.matrix_world @ Vector((x, 0, 0))` (ponto **mundial** atribuído a `location`, que é relativo ao pai — EC-09). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-65):** duplicar/espelhar calculam no espaço do pai (`copy.matrix_world = obj.matrix_world @ Matrix.Translation((x, 0, 0))`; espelho idem), preservando o que o usuário vê. Pendência de implementação: DT-01.
4. 🟢 `del copy['btm_uid']` se existir (a cópia ganha uid novo na próxima extração); `btm_mirrored` e `IS_BTM_GEOMETRY` são copiados.
5. 🟢 Seleção: `obj.select_set(False)`, `copy.select_set(True)`, ativo = cópia (outros selecionados continuam selecionados). `FINISHED`.

### F-04 — Espelhar (`BTM_OT_GeometryMirror.execute`)

1. 🟢 `x = size(...)[0]`; `offset = obj.matrix_world.to_3x3() @ Vector((x, 0, 0))` (inclui rotação e escala do objeto).
2. 🟢 Com `obj.get('btm_mirrored')` verdadeiro: `obj.location += offset`; `del obj['btm_mirrored']`. Senão: `obj.location -= offset`; `obj['btm_mirrored'] = True`. `FINISHED`.

### F-05 — Excluir (`BTM_OT_GeometryDelete.execute`)

🟢 `data = obj.data`; `bpy.data.objects.remove(obj, do_unlink=True)`; `bpy.data.meshes.remove(data)` se `data.users == 0`; `FINISHED`.

### F-06 — Produção (consumidor `cutting/part_sources.py:geometry_records(scene)`)

1. 🟢 Import tardio de `geometry_free.mesh`. Para cada `obj` em `scene.objects`: pula se não `is_geometry`, se `btm_geometry.fabrication` falso ou se não visível (`_visible`: `not hide_viewport and not hide_get()`; `RuntimeError` no `hide_get` → só `hide_viewport`).
2. 🟢 `uid = ensure_module_uid(obj)` (grava `btm_uid` se falta). Para cada `(índice, (nome, c, l, e))` de `sheets(...)`: `PartRecord` conforme RN-15.
3. 🟢 Em seguida (fora desta unit) os agregados com `production_part` geram uma placa cada, também com `source="FREE_GEOMETRY"`, lendo `component`, `material` e `finish` do `btm_geometry` do agregado (`aggregates/production.py:sheet`).
4. 🟢 Chamado por `cutting/part_extractor.py:106` (`parts.extend(record_to_part(r, values) for r in part_sources.geometry_records(scene))`).

### F-07 — Interface (consumidores)

- 🟢 Botões: barra lateral, grupo "Geometrias" (`ui/sidebar_build.py:118-122`, `row.operator("caffmob.geometry_create", text=N_("Placa"), icon='MESH_PLANE').kind = 'PLACA'` e "Caixa" `MESH_CUBE`); Construtor, caixa "Mobiliário & Iluminação" (`ui/panels.py:260-261`).
- 🟢 Painel de propriedades (`ui/object_properties.py:_draw_geometry`, chamado para `classify.GEOMETRY`): caixa "Geometria" com `kind`; `plane` só na placa; `width`, `depth`, `height` menos o eixo substituído pela espessura (`{'XY': 'height', 'XZ': 'depth', 'YZ': 'width'}[plane]`); `thickness`; `location` ("Posição"); caixa de fabricação (`fabrication`; `component`, `material`, `finish` habilitados só com fabricação); linha Duplicar/Espelhar/Excluir (ícones `DUPLICATE`, `MOD_MIRROR`, `TRASH`).
- 🟢 Seleção (unit `selection`): `classify` devolve `GEOMETRY`/`BTM` para o objeto ou qualquer descendente dele; tamanho do elemento por `obj.dimensions` (`editing.get_dimension`); Redimensionar grava `btm_geometry.width` (`resize.py:_set_width`, faixa 0,01–100 m); "Mover Sobre" move a geometria (`movable_root`). Contratos em `_reversa_sdd/selection/requirements.md` RN-01, RN-05, RN-16, RN-21, RN-23.
- 🟢 Overlay do plano de inserção realça uma geometria ativa como os demais tipos (`overlays/draw_handlers.py:184`).

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `hb_snap.main(op, ctrl, context)` | encaixe do canto; escreve `op.hit_location` etc.; exige `op.region` e `op.mouse_pos` | 🟢 |
| `hb_snap.event_is_pass_through(event)` | navegação | 🟢 |
| `data.units.parse_length`, `get_scene_length_unit`, `format_length` | entrada e cabeçalho | 🟢 |
| `data.i18n.tr`, `N_` + `data/translations/geometry_free.json` (15 chaves) | textos | 🟢 |
| `data.dimension_schema.COMPONENTS` (`code`, `label_pt`) | itens do componente | 🟢 |
| `Object.btm_plane` (`data/properties.py:BTM_PG_InsertionPlane`, registrado fora da unit) | marca `GEOMETRY` | 🟢 |
| `bmesh.ops.create_cube`, `bpy_extras.view3d_utils`, `mathutils.geometry.intersect_line_plane` | malha e raio | 🟢 |
| Consumidores: `cutting/part_sources`, `cutting/part_extractor`, `cutting/stale`, `selection/*`, `ui/object_properties`, `ui/sidebar_build`, `ui/panels`, `overlays/draw_handlers`, `aggregates/production`, `aggregates/panels` | ver F-06/F-07 | 🟢 |

## Decisões de Design Identificadas

- 🟢 Geometria = objeto de malha comum com marca de tipo, sem Geometry Nodes nem cage (feature 002 D-18: `_reversa_forward/002-editor-parede-mover-sobre/roadmap.md:53`).
- 🟢 Origem no canto mínimo para que mudar a espessura não mova a face de apoio (`props.py` docstring; 002 RF-12).
- 🟢 A caixa é um sólido visual; as seis chapas existem só na produção, com fundo e tampo inteiros, laterais entre eles e frente/trás entre as laterais (`mesh.py:sheets`).
- 🟢 Produção pelo mesmo caminho dos módulos (`PartRecord`) com `module_uid=None` e `line=""`, para a matéria-prima digitada valer sem fitas nem limite de chapa do padrão (`part_sources.py:geometry_records` docstring).
- 🟢 Pré-visualização = o objeto real, excluído do raycast por `HB_CURRENT_DRAW_OBJ` (padrão herdado das bibliotecas face frame, `ops_placement.py:2126`).
- 🟢 Espelhar por translação + marca, não por escala negativa (evita normais invertidas e medidas negativas na produção) — 🟡 motivo inferido.

## Estado Interno

| Estado | Escopo | Ciclo de vida | Confiança |
|---|---|---|---|
| Atributos do operador de criação | instância do modal | do `invoke` ao `_finish`/`_cancel` | 🟢 |
| `btm_geometry`, marcas e malha | objeto, persistido no `.blend` | até excluir o objeto | 🟢 |
| Estado em nível de módulo | — | nenhum | 🟢 |

## Observabilidade

- 🟢 Cabeçalho da área durante a criação; `report({'WARNING'})` com a mensagem do `parse_length`. Nenhum `print`, log ou relatório nos operadores de edição.

## Riscos e Lacunas

- 🔴 Saída externa do modal (sem `cancel()`), troca de área/janela durante o modal e `unregister()` com modal ativo: objeto provisório pode ficar na cena com `HB_CURRENT_DRAW_OBJ` (EC-01).
- 🟢 Geometria com `parent`: duplicar e espelhar misturam espaço mundial e local (EC-09). _(Revisão 2026-10-10: sonda no Blender 5.2 com pai em (2,0,0) girado 90° em Z e placa de 0,5 m — a cópia vai a (1,5, 2,0, 0) em vez de (2, 0,5, 0) e o espelho a (2,5, 0, 0) em vez de (2, −0,5, 0))_ 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-65):** duplicar/espelhar calculam no espaço do pai (`copy.matrix_world = obj.matrix_world @ Matrix.Translation((x, 0, 0))`; espelho idem), preservando o que o usuário vê (DT-01). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-65):** ao excluir, os filhos mantêm a posição mundial (gravar `matrix_world` antes de remover) (EC-14; DT-02).
- 🟢 Escala do objeto (S do Blender) muda o visual mas não a produção nem as propriedades (EC-10). _(Revisão 2026-10-10: `cutting/part_sources.py:geometry_records` lê só `btm_geometry`)_
- 🟢 Callback `_update` sem verificação de tipo reconstrói qualquer malha (EC-11). _(Revisão 2026-10-10: sonda — malha vazia comum vira cubo de 8 vértices ao gravar `btm_geometry.width`)_
- 🔴 Nenhum teste puro da unit. _(Revisão 2026-10-10: o smoke `tests/blender_002_smoke.py:194-224` foi executado e passou no Blender 5.2.0 LTS)_

## Divergências com artefatos anteriores

| Artefato | Afirmação | Código | Confiança |
|---|---|---|---|
| `code-analysis.md` §21 | operador "`CAFFMOB_OT_geometry_create`" | classe `BTM_OT_GeometryCreate`, `bl_idname = "caffmob.geometry_create"` | 🟢 |
| `.reversa/context/modules.json` (geometry_free) `dependencies` | inclui `cutting.part_sources` | a dependência é inversa (`part_sources` importa `geometry_free.mesh`); faltam `data.i18n`, `bpy_extras` | 🟢 |
| `permissions.md` | "molding, geometry_free — Criar/reconstruir malhas/curvas" | geometry_free só cria/reconstrói malhas | 🟢 (detalhe) |
| `ops_edit.py` docstring | Espelhar: "a origem continua no mesmo lugar" | `obj.location` muda; o que fica é o **ponto** da origem anterior, que passa a ser o canto +X da peça | 🟢 |
| `selection/resize.py:_stretched` e `_reversa_sdd/selection/requirements.md` RN-23 | "geometria sem `btm_geometry`" é esticada por escala | ramo inalcançável com o pacote registrado: o `PointerProperty` existe em todo objeto (idem `ui/object_properties.py:_draw_geometry` `g is None`) | 🟢 |
| Feature 002 `requirements.md:337-346` (RF-11) | "digita a espessura de 18 mm"; "só é criada ao confirmar"; "Esc → nenhum objeto é criado" | o modal não pede espessura (vem do padrão 0,018); o objeto existe desde o `invoke` e o Esc o remove | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-96):** aceito o comportamento atual como Won't: a espessura é editável no painel logo depois e material por face não entra na produção (só uma matéria-prima por peça); o registro correspondente na feature 002 fica para o ciclo forward (fora de `_reversa_sdd/`) |
| Feature 002 `requirements.md:170` (RF-12) | "material e acabamento por face" | um único `material`/`finish` em texto, sem material do Blender | 🟢 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-96):** aceito o comportamento atual como Won't: a espessura é editável no painel logo depois e material por face não entra na produção (só uma matéria-prima por peça); o registro correspondente na feature 002 fica para o ciclo forward (fora de `_reversa_sdd/`) |
| `state-machines.md` › Geometria livre | "Dimensoes --> Dimensoes : mouse ou largura digitada" | também a profundidade digitada sai do passo (2º Enter avança ou conclui); dígitos no passo 0 ficam no buffer e valem no passo 1 (EC-05) | 🟢 (detalhe) _(Revisão cruzada 2026-10-10: corrigido em state-machines.md)_ |
