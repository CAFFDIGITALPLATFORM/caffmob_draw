# Cotas de Módulo (measure) — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/measure/` em 2026-10-10 (sem alterações sem commit na pasta). IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`; EC-xx os de `edge-cases.md`. 🟡 marca inferência; 🔴 marca lacuna. Contratos de outras units são citados, não redescritos: o modal "Mover na Parede" está em `_reversa_sdd/move_over/design.md` F-08; o filtro vertical de obstáculos em `_reversa_sdd/hb_placement/requirements.md` RN-12; o Editor de Paredes em `_reversa_sdd/walls2d/`.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `cotas.py` (94) | não (`collections.namedtuple`; `data.i18n.N_`, `tr`) | Tipos, limites, cálculo, cota inversa, deslize | 🟢 |
| Ponte Blender ↔ modelo | `scene_cotas.py` (125) | não diretamente; usa objetos `bpy` via `hb_types`, `selection.classify`; imports tardios de `hb_project` e `hb_placement` | Lê módulo/parede/obstáculos/pé-direito; escreve `location` | 🟢 |
| Pacote | `__init__.py` (1) | não | Só docstring. **Sem** `register`/`unregister`: a unit não registra classes nem propriedades | 🟢 |

## Interface

### `cotas.py` 🟢

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `Cotas` | `namedtuple('Cotas', 'afastamento anterior posterior inferior superior')` | — | Metros; campos laterais e afastamento podem ser `None` (módulo livre) |
| `Placement` | `namedtuple('Placement', 'x0 width z0 height back_y')` | — | Metros, referencial da parede (RN-01) |
| `FIELDS` | constante | `('afastamento', 'anterior', 'posterior', 'inferior', 'superior')` | Ordem dos campos no painel |
| `LABELS` | constante `dict` | campo → `N_(...)` | `"Afastamento da parede"`, `"Cota anterior"`, `"Cota posterior"`, `"Cota inferior"`, `"Cota superior"` (marcados, não traduzidos; `apply` traduz com `tr`) |
| `_vertical_overlap` | `(z0, z1, oz0, oz1)` | `bool` | `z0 < oz1 and oz0 < z1` (estrito) |
| `limits` | `(placement, obstacles, wall_length)` | `(left, right)` | F-01 |
| `compute` | `(placement, obstacles, wall_length, ceiling_height)` | `Cotas` | RN-02, usa `limits` |
| `compute_free` | `(placement, ceiling_height)` | `Cotas` | `Cotas(None, None, None, z0, ceiling − (z0 + height))` |
| `apply` | `(field, value, placement, obstacles, wall_length, ceiling_height)` | `Placement` | F-02; levanta `ValueError` |
| `slide` | `(placement, obstacles, wall_length, target_x0, avoid=True)` | `float` (x0) | RN-12 |

`obstacles` é um iterável de tuplas `(x0, x1, z0, z1)` em metros no referencial da parede. 🟢

### `scene_cotas.py` 🟢

Funções do módulo:

| Símbolo | Assinatura | Retorno | Observação |
|---|---|---|---|
| `_dims` | `(root)` | `(largura, profundidade, altura)` | RN-09. `GeoNodeObject(root)` e `get_input('Dim X'/'Dim Y'/'Dim Z')` dentro de `try/except Exception`; depois `getattr(root, 'btm_cabinet', None)` com `width > 0`; depois `root.dimensions.x/.y/.z` |
| `_wall_of` | `(root)` | `Object` ou `None` | `root.parent` se existir e `parent.get('IS_WALL_BP')` truthy |
| `_on_front_side` | `(root, wall)` | `bool` | RN-07: `rz = rotation_euler.z % (2π)`; `min(rz, 2π − rz) < 0.01 and location.y < 0.5 · _wall_thickness(wall)` |
| `_wall_thickness` | `(wall)` | `float` | `GeoNodeWall(wall).get_input('Thickness')`; qualquer exceção → `0.0` |
| `ceiling_height` | `(scene, wall=None)` | `float` m | F-04 (RN-08). Import tardio de `hb_project` |
| `for_object` | `(obj, scene)` | `ModuleCotas` ou `None` | RN-13 |

`class ModuleCotas(root, scene)`:

| Membro | Retorno | Comportamento |
|---|---|---|
| `__init__` | — | F-03 |
| `obstacles()` | `list[(x0, x1, z0, z1)]` | Livre → `[]`. Na parede: import tardio de `hb_placement.PlacementMixin`; `PlacementMixin().get_wall_children_sorted(self.wall, exclude_obj=self.root, object_z_start=placement.z0, object_height=placement.height)`; para cada `(x0, x1, obj)` com `obj is not None` e sem `IS_2D_ANNOTATION`/`IS_SNAP_LINE`, devolve `(x0, x1, placement.z0, placement.z0 + placement.height)` (RN-10) |
| `compute()` | `Cotas` | Na parede: `cotas.compute(placement, obstacles(), wall_length, ceiling)`; livre: `cotas.compute_free(placement, ceiling)` |
| `apply(field, value)` | `Placement` | F-05; levanta `ValueError` sem escrever nada |

### Contrato consumido de `get_wall_children_sorted` 🟢 (`hb_placement.py:PlacementMixin`)

Para cada filho da parede: pula `obj_x` e `exclude_obj`; `x_start = child.location.x`; se `child.home_builder.mod_name`, `x_end = x_start + Dim X` e `z_end = location.z + Dim Z` (exceção → mantém `x_end = x_start`, `z_end = z_start`); com `object_z_start`/`object_height`, pula filhos cuja faixa `[z_start, z_end]` não cruza estritamente a do módulo; devolve `(x_start, x_end, child)` ordenados por `x_start`. Filhos sem `mod_name` ficam com largura e altura zero (EC-03).

### Superfície exposta pelos consumidores 🟢 (fora da unit, citada para reimplementação)

| Consumidor | O que usa | Comportamento |
|---|---|---|
| `ui/object_properties.py:BTM_PG_SelectionEdit` (ponteiro `Scene.btm_selection`) | `FIELDS`, `for_object`, `compute`, `apply` | 5 `FloatProperty` virtuais `afastamento`, `anterior`, `posterior`, `inferior`, `superior` (`subtype='DISTANCE'`, `unit='LENGTH'`, `precision=1`, sem `min`/`max`, `get`/`set`). Getter: `for_object(active_object, scene)`; `None` ou valor `None` → `0.0`. Setter: `mc.apply(field, value)` dentro de `_guard`: `ValueError` → `window_manager['btm_selection_error'] = str(exc)`; sucesso → apaga a chave. Descrições: "Do fundo do módulo até a face da parede", "Da lateral esquerda até o item ou o fim de parede mais próximo", "Da lateral direita…", "Do piso até a base do módulo", "Do topo do módulo até o teto" |
| `ui/object_properties.py:_draw_cotas` | `for_object`, `on_wall`, `FIELDS` | Caixa "Cotas" (ícone `DRIVER_DISTANCE`). Na parede: os 5 campos em ordem `FIELDS` + botão `caffmob.move_on_wall` ("Mover na Parede", `ARROW_LEFTRIGHT`). Livre: rótulo "Módulo livre (sem parede): só cotas verticais." (`INFO`) + `inferior` e `superior` |
| `overlays/selection_cotas.py:_draw` (`SpaceView3D.draw_handler_add(..., 'WINDOW', 'POST_PIXEL')`) | `for_object`, `compute`, `limits`, `placement`, `wall`, `depth`, `ceiling` | F-06 |
| `move_over/ops_move_on_wall.py` | `for_object(...).on_wall`, `placement`, `depth`, `wall`, `obstacles()`, `wall_length`, `compute()`, `cotas.slide` | Contrato em `_reversa_sdd/move_over/design.md` F-08. Escreve `mc.placement` diretamente |
| `walls2d/ops_editor.py` (abrir o editor) | `ceiling_height(context.scene)` | `session.project_height` e `btm_wall_editor.new_height` = pé-direito do projeto (D-36) |
| `stick/migrate.py` | só docstring | Cita `_on_front_side` como a mesma regra de face (não importa) |

## Fluxo Principal

1. 🟢 Um consumidor chama `for_object(obj, scene)` com o objeto ativo (F-07).
2. 🟢 `ModuleCotas.__init__` decide `on_wall` e monta `Placement`, `wall_length`, `ceiling`, `depth` (F-03).
3. 🟢 Leitura: `compute()` lista os obstáculos (na parede) e chama `cotas.compute` (F-01 dentro) ou `compute_free`.
4. 🟢 Escrita: `apply(field, value)` valida, chama `cotas.apply` (F-02) e grava `root.location` (F-05).
5. 🟢 O valor exibido é formatado pelo consumidor (`units.format_value` no overlay, propriedade `DISTANCE` no painel).

### F-01 `limits` 🟢 `cotas.py:limits` (ver `_reversa_sdd/flowcharts/measure-apply.md`)
1. `x0, x1 = placement.x0, placement.x0 + width`; `z0, z1 = placement.z0, placement.z0 + height`.
2. `left, right = 0.0, wall_length`.
3. Para cada `(ox0, ox1, oz0, oz1)`: se não `_vertical_overlap(z0, z1, oz0, oz1)`, pula; se `ox1 <= x0 + 1e-9`, `left = max(left, ox1)`; **elif** `ox0 >= x1 − 1e-9`, `right = min(right, ox0)`; senão (cruza o módulo) ignora.
4. Devolve `(left, right)`.

### F-02 `apply` 🟢 `cotas.py:apply`
1. `value < 0` → `ValueError(tr("Valor Inválido: {} não pode ser negativa.").format(tr(LABELS[field])))`. Atenção: com campo desconhecido e valor negativo, `LABELS[field]` levanta `KeyError` (EC-07).
2. `afastamento` → `placement._replace(back_y=−value)`.
3. `inferior` → `_replace(z0=value)`.
4. `superior` → `z0 = ceiling − value − height`; `z0 < 0` → `ValueError(... "maior que o espaço até o piso.")`; senão `_replace(z0=z0)`.
5. Demais: `left, right = limits(placement, obstacles, wall_length)`; `anterior` → `x0 = left + value`; `posterior` → `x0 = right − value − width`; outro → `ValueError(f"Cota desconhecida: {field}")`.
6. `x0 < 0 or x0 + width > wall_length + 1e-9` → `ValueError(... "tira o módulo da parede.")`; senão `_replace(x0=x0)`.

### F-03 `ModuleCotas.__init__(root, scene)` 🟢 `scene_cotas.py`
1. `self.root`, `self.scene`; `self.wall = _wall_of(root)`.
2. `width, depth, height = _dims(root)`.
3. `self.on_wall = wall is not None and _on_front_side(root, wall)`.
4. Na parede: `loc = root.location`; `placement = Placement(loc.x, width, loc.z, height, loc.y)`; `wall_length = GeoNodeWall(wall).get_input('Length')` (**sem** `try`: exceção propaga, EC-08).
5. Livre: `placement = Placement(0.0, width, root.matrix_world.translation.z, height, 0.0)`; `wall_length = None`.
6. `self.ceiling = ceiling_height(scene, self.wall)` (com a parede mesmo quando o módulo é livre do lado de trás); `self.depth = depth`.

### F-04 `ceiling_height(scene, wall=None)` 🟢 `scene_cotas.py`
1. `main = hb_project.get_main_scene() or scene` (efeito colateral possível: `get_main_scene` marca `IS_MAIN_SCENE` numa cena se nenhuma estiver marcada; em contexto de desenho a escrita falha com `AttributeError` e é ignorada).
2. `props = getattr(main, 'home_builder', None)`; `value = props.ceiling_height` (ou `0.0` sem `props`). `value > 0` → devolve. O padrão da propriedade é `inch(96)` = 2,4384 m (`hb_props.py`), então na prática o fallback só vale com valor 0 ou sem `home_builder`.
3. Com `wall`: `GeoNodeWall(wall).get_input('Height')` (exceção → ignora).
4. Devolve `2.6`.

### F-05 `ModuleCotas.apply(field, value)` 🟢 `scene_cotas.py`
1. Livre e `field ∈ {anterior, posterior, afastamento}` → `ValueError(tr("Valor Inválido: módulo livre (sem parede) não tem cota anterior, posterior ou afastamento."))`.
2. Na parede: `new = cotas.apply(field, value, placement, self.obstacles(), wall_length, ceiling)`; `root.location = (new.x0, new.back_y, new.z0)`.
3. Livre: `new = cotas.apply(field, value, placement, [], 1e9, ceiling)`; `root.location.z += new.z0 − placement.z0`.
4. `self.placement = new`; devolve `new`. Sem `view_layer.update()` nem `undo_push` próprios.

### F-06 Desenho das cotas ao selecionar 🟢 `overlays/selection_cotas.py:_draw/_specs`
1. `scene.btm_settings.show_dimensions` desligado → não desenha (sem `btm_settings`, desenha).
2. `obj = active_object`; `None` ou não selecionado → nada. `mc = for_object(obj, scene)`; `None` → nada.
3. Na parede: `matrix = wall.matrix_world`; `y = back_y − depth` (frente do módulo); `z_mid = z0 + height/2`; `left, right = cotas.limits(...)`. `anterior > 1e-4` → linha `(left, y, z_mid)`→`(x0, y, z_mid)`; `posterior > 1e-4` → `(x1, y, z_mid)`→`(right, y, z_mid)`. Verticais no `x_mid` da frente: piso `(x_mid, y, 0)`→base e topo→`(x_mid, y, ceiling)`, todos por `matrix @`.
4. Livre: verticais no X/Y mundial da origem, de `z = 0` e até `z = ceiling`.
5. `inferior > 1e-4` e `superior > 1e-4` → linhas verticais. Texto = `units.format_value(valor)`. Desenho por `hb_placement.draw_placement_dimensions` (via portador `_Specs` com `_placement_dim_specs`).
6. `ReferenceError`, `AttributeError` e `ValueError` em `_specs` → não desenha naquele quadro.

### F-07 `for_object(obj, scene)` 🟢 `scene_cotas.py`
1. `info = classify.classify(obj)` (`None` para `obj is None`).
2. `info is None` ou `info.kind ∉ {MODULE, PART, FRONT}` → `None`.
3. `ModuleCotas(info.root, scene)`.

## Fluxos Alternativos

- **Módulo do lado de trás da parede ou girado**: tratado como livre (RN-06, RN-07); o pé-direito ainda pode vir da parede. 🟢
- **Parede da camada nova (BTM, `btm_wall`)**: não tem `IS_WALL_BP`; o módulo filho dela é livre. 🟢 `_wall_of`. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-14):** comportamento transitório, aceito até a camada BTM ter contrato de parede; registrado, sem mudança agora.
- **Módulo sem Geometry Nodes nem `btm_cabinet`**: dimensões = `root.dimensions` (Empty → 0, 0, 0). 🟢
- **Leitura de `Length` falha**: `ModuleCotas.__init__` levanta; o overlay engole se for `ValueError`; o getter do painel não trata (EC-08). 🟢
- **Valor inválido no painel**: `ValueError` vira `window_manager['btm_selection_error']`, o objeto não muda. 🟢 `ui/object_properties.py:_guard`

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `data/i18n.py` | `N_` (marca) e `tr` (`pgettext_iface` no Blender; texto original fora) | 🟢 |
| `selection/classify.py` | `classify(obj) → Classified(kind, obj, root, library)`; constantes `MODULE`, `PART`, `FRONT`. Raiz de módulo = ancestral com `IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_FACE_FRAME_PRODUCT_CAGE`, `IS_CLOSET_STARTER_CAGE` ou tipo BTM `MODULE` | 🟢 |
| `hb_types.GeoNodeObject(obj).get_input(name)` | `Dim X/Y/Z` do módulo; levanta `ValueError` sem `home_builder.mod_name`, modificador ou node group | 🟢 |
| `hb_types.GeoNodeWall(obj).get_input(name)` | `Length`, `Thickness`, `Height` da parede | 🟢 |
| `hb_placement.PlacementMixin().get_wall_children_sorted` | Obstáculos da parede (contrato acima) | 🟢 |
| `hb_project.get_main_scene()` | Cena principal com `home_builder.ceiling_height` | 🟢 |
| idprops | `IS_WALL_BP` (parede), `IS_2D_ANNOTATION`, `IS_SNAP_LINE` (não obstáculos), `obj_x` (pulado pelo `hb_placement`) | 🟢 |
| `data/translations/measure.json`, `geral.json`, `ui.json` | 4 mensagens de erro; 5 rótulos + "Cotas"; rótulo de módulo livre | 🟢 |

Consumidores 🟢 (grep): `overlays/selection_cotas.py`, `ui/object_properties.py`, `move_over/ops_move_on_wall.py`, `walls2d/ops_editor.py`, `tests/test_cotas.py`, `tests/blender_002_smoke.py`.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Cotas pelos mesmos obstáculos do posicionamento (`get_wall_children_sorted` + filtro vertical), não por raios (D-11) | `scene_cotas.py` docstring; `_reversa_forward/002…/roadmap.md` D-11 | 🟢 |
| Núcleo puro separado para testar sem Blender | `cotas.py` docstring "Python puro, sem `bpy`" | 🟢 |
| Cota editada move só a posição (RN-04 da 002) | `cotas.apply` docstring | 🟢 |
| Desenho ao vivo por handler `POST_PIXEL` reaproveitando `draw_placement_dimensions`, sem objetos de cota na cena (D-12) | `overlays/selection_cotas.py` docstring | 🟢 |
| Pé-direito único do projeto, compartilhado com o Editor de Paredes (D-36) | `walls2d/ops_editor.py`; `roadmap.md` D-36 | 🟢 |
| Validação por `ValueError` com prefixo "Valor Inválido", exibida pelo consumidor | `cotas.apply`; `ui/object_properties.py:_guard` | 🟢 |

## Estado Interno

- 🟢 Nenhum estado persistente nem global. `ModuleCotas` é efêmero (criado a cada leitura): `root`, `scene`, `wall`, `on_wall`, `placement`, `wall_length`, `ceiling`, `depth`. `placement` é atualizado por `apply` e, de fora, por `ops_move_on_wall._move`.
- 🟢 Único dado escrito: `root.location` do módulo.

## Observabilidade

- 🟢 Nenhum log nem `report`. Erros de domínio são `ValueError` com mensagem traduzida; o painel guarda a última em `window_manager['btm_selection_error']`. Exceções do Geometry Nodes em `_dims`, `_wall_thickness` e no `Height` de `ceiling_height` são engolidas (`except Exception`).

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-12):** `apply` rejeita com "Valor Inválido" sobreposição ao vizinho oposto e passagem do teto. 🟢 (código) hoje não valida (EC-01, EC-02). Pendência de implementação: DT-01.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-13):** vizinhos sem `mod_name` medidos pela largura de `btm_cabinet` ou bounding box. 🟢 (código) hoje contam como obstáculos pontuais (EC-03). Pendência de implementação: DT-02.
- 🟡 Desempenho: `ModuleCotas` recriado e filhos relistados por redesenho e por campo — decisão: medir/testar (DT-03; questions.md#pergunta-74).
- 🟢 `obstacles()` descarta a faixa de altura real do obstáculo (devolve a do módulo); irrelevante hoje porque `limits` só testa sobreposição, mas quebra se outro consumidor usar `z0`/`z1` do obstáculo. _(Revisão 2026-10-10: `scene_cotas.py:obstacles` devolve `(x0, x1, z0, z1)` do módulo; únicos usos são `limits`/`slide` (overlay, `ops_move_on_wall.py:88`))_
- 🟡 `on_wall` lê `root.location` como coordenada no referencial da parede; vale se `matrix_parent_inverse` for identidade (o "Mover Sobre" garante isso ao reparentar; outros caminhos não verificados) (EC-06).

## Divergências entre artefatos e código

- 🟢 `_reversa_forward/002…/requirements.md` RF-18 pede o grupo Cotas "para módulos e geometrias"; `for_object` só aceita `MODULE`, `PART` e `FRONT`.
- 🟢 `_reversa_forward/002…/roadmap.md` D-11 diz "inferior por `location.z` no mundo"; na parede o código usa `location.z` **local** (relativo à parede); só o módulo livre usa a Z mundial da origem.
- 🟢 `code-analysis.md` §7.3 apresenta 2,6 m como o pé-direito usado "sem `home_builder.ceiling_height`": a propriedade tem padrão 2,4384 m (`inch(96)`), então 2,6 m só vale com valor 0 ou cena sem `home_builder` e sem parede.
- 🟢 `.reversa/context/modules.json` lista `tests/test_cotas.py` e `blender_002_smoke.py` como testes: correto; `tests/test_measure_expr.py`, apesar do nome, testa `data/expr.py`.
- 🟢 `flowcharts/measure.md` e `code-analysis.md` §7.2 estão alinhados com o código; não registram o efeito colateral de `get_main_scene` (marcar `IS_MAIN_SCENE`) nem a ausência de `try` na leitura de `Length`.
