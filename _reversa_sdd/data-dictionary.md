# Dicionário de Dados Completo — BlenderToMob

Este documento apresenta o dicionário de dados formal e completo do add-on **BlenderToMob**, mapeado pelo agente **Archaeologist** no nível de documentação **Detalhado**.

---

## 1. Mapeamento das Entidades Paramétricas

### 1.1 Segmento de Parede (`BTM_PG_WallSegment`)
Esta estrutura de dados gerencia a definição paramétrica de um segmento de parede individual na cena. É registrada como um pointer property em `bpy.types.Object.btm_wall`.

| Propriedade | Tipo | Subtipo | Padrão | Mínimo | Máximo | Callback de Update | Descrição | Certeza |
|-------------|------|---------|--------|--------|--------|--------------------|-----------|----------|
| `length` | Float | - | 2000.0 | 10.0 | 100000.0 | `update_wall_geom` | Comprimento linear do segmento de parede em milímetros. | 🟢 CONFIRMADO |
| `absolute_angle` | Float | `ANGLE` | 0.0 | -360.0 | 360.0 | - | Ângulo absoluto em relação ao sistema global de coordenadas do Blender (em graus). | 🟢 CONFIRMADO |
| `relative_angle` | Float | `ANGLE` | 0.0 | -360.0 | 360.0 | - | Ângulo do segmento medido em relação ao segmento anterior da polilinha (em graus). | 🟢 CONFIRMADO |
| `thickness` | Float | - | 150.0 | 10.0 | 2000.0 | `update_wall_geom` | Espessura física da extrusão lateral da parede em milímetros. | 🟢 CONFIRMADO |
| `height_start` | Float | - | 2700.0 | 100.0 | 10000.0 | `update_wall_geom` | Altura vertical da parede no ponto inicial em milímetros (Pé-Direito inicial). | 🟢 CONFIRMADO |
| `height_end` | Float | - | 2700.0 | 100.0 | 10000.0 | `update_wall_geom` | Altura vertical da parede no ponto final em milímetros (Pé-Direito final). | 🟢 CONFIRMADO |
| `offset` | Float | - | 0.0 | - | - | - | Afastamento vertical (elevação) da base da parede em relação ao plano de piso Z=0. | 🟢 CONFIRMADO |
| `sagitta` | Float | - | 0.0 | - | - | - | Flecha do arco de curvatura para modelagem de paredes redondas em milímetros. | 🟢 CONFIRMADO |
| `linear_increment` | Float | - | 50.0 | 1.0 | 1000.0 | - | Intervalo de incremento linear (passo de snap) em milímetros para o cursor de desenho. | 🟢 CONFIRMADO |
| `angular_increment` | Float | `ANGLE` | 5.0 | 0.5 | 90.0 | - | Passo de incremento angular em graus para o ajuste de inclinação via cursor. | 🟢 CONFIRMADO |
| `orientation` | Enum | - | `RIGHT` | - | - | - | Lado do alinhamento da espessura em relação ao eixo da parede (`RIGHT` = Direita/Horário, `LEFT` = Esquerda/Anti-horário). | 🟢 CONFIRMADO |
| `wall_type` | Enum | - | `NORMAL` | - | - | - | Preset de estilo e materialização da parede (`NORMAL` = Alvenaria, `DRYWALL` = Gesso, `GLASS` = Divisória de Vidro). | 🟢 CONFIRMADO |
| `use_as_default` | Bool | - | `False` | - | - | - | Salva as propriedades atuais para serem usadas como default em novos segmentos. | 🟢 CONFIRMADO |

### 1.2 Plano de Inserção (`BTM_PG_InsertionPlane`)
Registrado em `bpy.types.Object.btm_plane`. Mapeia metadados espaciais e físicos necessários para as regras de snapping e colisão de arrasto de mobiliário.

| Propriedade | Tipo | Padrão | Valores Válidos | Descrição | Certeza |
|-------------|------|--------|-----------------|-----------|----------|
| `object_kind` | Enum | `WALL` | `WALL`, `FLOOR`, `MODULE`, `GEOMETRY`, `OPENING` | Classificação da entidade no add-on para identificação na hierarquia espacial. | 🟢 CONFIRMADO |
| `parent_plane` | Pointer | - | `bpy.types.Object` | Referência direta ao objeto pai na árvore espacial (hospedeiro). | 🟢 CONFIRMADO |
| `layer_id` | String | `"Default"` | - | Nome ou ID da camada à qual o plano pertence (usado no Promob para ocultar/isolar). | 🟢 CONFIRMADO |
| `collision_override` | Enum | `INHERIT` | `INHERIT`, `ON`, `OFF` | Exceção de colisão por objeto. No código só `OFF` age (exclui o item dos pares); `ON` equivale a `INHERIT`, e a chave global `collision_global` desligada vence qualquer valor _(Revisão cruzada 2026-10-10: collision/rules.py:excluded; collision RN-10/RN-11)_ | 🟢 CONFIRMADO |

### 1.3 Propriedades de Vãos de Abertura (`BTM_PG_OpeningProperties`)
Registrado em `bpy.types.Object.btm_opening`. Controla vãos de portas e janelas associados a paredes.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Descrição | Certeza |
|-------------|------|--------|--------|--------|-----------|----------|
| `opening_type` | Enum | `DOOR` | `DOOR`, `WINDOW` | Categoria da abertura que define o comportamento de movimentação vertical (Porta ou Janela). | 🟢 CONFIRMADO |
| `width` | Float | 800.0 | 100.0 | 5000.0 | Largura física em milímetros do vão que será subtraído da parede. | 🟢 CONFIRMADO |
| `height` | Float | 2100.0 | 100.0 | 5000.0 | Altura física em milímetros do vão que será subtraído da parede. | 🟢 CONFIRMADO |
| `sill_height` | Float | 0.0 | 0.0 | 5000.0 | Altura do peitoril a partir da base em milímetros (janelas). Obrigatoriamente zero para portas. | 🟢 CONFIRMADO |
| `parent_wall` | Pointer | - | `bpy.types.Object` | Referência ao objeto de parede correspondente que hospeda e é recortado pela abertura. | 🟢 CONFIRMADO |

### 1.4 Propriedades de Módulos de Armário (`BTM_PG_CabinetProperties`)
Registrado em `bpy.types.Object.btm_cabinet`. Controla as dimensões paramétricas dos armários modulares de MDF.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Callback de Update | Descrição | Certeza |
|-------------|------|--------|--------|--------|--------------------|-----------|----------|
| `width` | Float | 800.0 | 100.0 | 3000.0 | `update_cabinet_geom` | Largura externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `height` | Float | 700.0 | 100.0 | 3000.0 | `update_cabinet_geom` | Altura externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `depth` | Float | 550.0 | 100.0 | 2000.0 | `update_cabinet_geom` | Profundidade externa total do módulo em milímetros. | 🟢 CONFIRMADO |
| `thickness` | Float | 18.0 | 6.0 | 50.0 | `update_cabinet_geom` | Espessura das placas de MDF/MDP (laterais, base, tampo, prateleiras) em milímetros. | 🟢 CONFIRMADO |
| `cabinet_type` | Enum | `BASE` | `BASE`, `WALL`, `TALL` | Categoria do módulo (`BASE` = Balcão Inferior, `WALL` = Aéreo, `TALL` = Paneleiro/Torre). | 🟢 CONFIRMADO |

### 1.5 Configurações Globais da Cena (`BTM_PG_SceneSettings`)
Registrado em `bpy.types.Scene.btm_settings`. Controla os ajustes ambientais, snaps e overlays visuais ativos na Viewport.

| Propriedade | Tipo | Padrão | Mínimo | Máximo | Descrição | Certeza |
|-------------|------|--------|--------|--------|-----------|----------|
| `snap_grid` | Bool | `True` | - | - | Ativa globalmente o snap posicional para movimentação de módulos. | 🟢 CONFIRMADO |
| `snap_increment` | Float | 50.0 | 1.0 | 1000.0 | Tamanho da grade de snap em milímetros. | 🟢 CONFIRMADO |
| `collision_global` | Bool | `True` | - | - | Liga/desliga o cálculo de prevenção de colisões físicas entre os objetos de marcenaria. | 🟢 CONFIRMADO |
| `show_grid` | Bool | `True` | - | - | Controla a exibição visual da grade de orientação no plano de piso Z=0. | 🟢 CONFIRMADO |
| `grid_spacing_x` | Float | 500.0 | 50.0 | 5000.0 | Intervalo horizontal das linhas da grade de piso em milímetros. | 🟢 CONFIRMADO |
| `grid_spacing_y` | Float | 500.0 | 50.0 | 5000.0 | Intervalo vertical das linhas da grade de piso em milímetros. | 🟢 CONFIRMADO |
| `grid_snap_enabled`| Bool | `True` | - | - | Se ativo, os módulos serão atraídos para as linhas do grid do piso ao serem movidos. | 🟢 CONFIRMADO |
| `grid_snap_gap` | Float | 50.0 | 5.0 | 500.0 | Distância limite em milímetros na qual o snap de atração magnética do grid é ativado. | 🟢 CONFIRMADO |
| `show_insertion_plane`| Bool | `True`| - | - | Exibe o realce visual (sombreamento amarelo) no plano de inserção sob o cursor. | 🟢 CONFIRMADO |
| `show_dimensions` | Bool | `True` | - | - | Ativa a renderização de linhas de cota e dimensões na viewport. | 🟢 CONFIRMADO |

---

## 2. Dicionário de Persistência Interna (Custom Properties)

O add-on utiliza propriedades internas do Blender (armazenadas em dicionários `IDPropertyGroup` nos próprios objetos) para persistir estruturas mais complexas que não possuem correspondência direta na API nativa `bpy.props`:

### 2.1 Polilinha de Parede (`btm_wall_segments`)
Armazenado como propriedade dinâmica no objeto de parede (ex: `obj["btm_wall_segments"]`).
* **Tipo:** String contendo um dump JSON serializado.
* **Schema JSON:**
  ```json
  [
    {
      "start": [float, float],     // Coordenada X, Y inicial em mm
      "end": [float, float],       // Coordenada X, Y final em mm
      "thickness": float,          // Espessura do segmento em mm
      "height": float,             // Altura do segmento em mm
      "offset": float              // Elevação em mm
    }
  ]
  ```
* **Uso:** Preserva a estrutura de polilinhas gerada pelo operador modal de parede, permitindo a atualização dos parâmetros sem colapsar os segmentos em uma única parede retilínea simples.

---

# Re-extração 2026-10 (Fase 2c)

## 3. Módulo `canvas2d` (estruturas em memória, sem persistência)

### 3.1 `View2D` (`caffmob_draw/canvas2d/view.py`) 🟢

| Campo | Tipo | Obrigatório | Padrão | Descrição |
|-------|------|-------------|--------|-----------|
| `rect` | `(float, float, float, float)` | sim | — | x, y, largura, altura em px; origem embaixo à esquerda |
| `scale` | `float` | não | `100.0` | Pixels por metro; piso `1e-6`, sem teto |
| `center` | `(float, float)` | não | `(0, 0)` | Ponto do mundo (m) no centro do retângulo |

Sem relacionamentos persistidos: a instância vive na `Session` do editor que a usa (`walls2d/props.Session.view`,
`cabinet_editor`, `move_over`).

### 3.2 Constantes de `gestures.py` 🟢

| Nome | Tipo | Valor | Descrição |
|------|------|-------|-----------|
| `PINCH_SENSITIVITY` | `float` | `1/150` | Expoente por unidade de delta da pinça |
| `WHEEL_STEP` | `float` | `1.15` | Fator de um passo da roda |
| `ZOOM_WINDOW_MIN_PX` | `int` | `5` | Lado mínimo do retângulo do zoom janela |

### 3.3 Paleta `draw.COLORS` 🟢

Dicionário `nome → RGBA` com 13 entradas (`panel`, `pane`, `border`, `text`, `muted`, `reference`, `moving`, `target`,
`target_hot`, `warning`, `button`, `button_hot`, `button_primary`). `FONT = 0`, `FONT_SIZE = 12`.

### 3.4 Campos da sessão lidos por `window.py` 🟢

| Campo (na sessão do editor) | Tipo | Descrição |
|-----------------------------|------|-----------|
| `window_ptr` | `int` | `Window.as_pointer()` da janela do editor |
| `area_ptr` | `int` | `Area.as_pointer()` da área do editor |
| `restore_area_type` | `str` ou `None` | Tipo original da área quando o editor ocupou a área atual |

## 4. Módulo `walls2d`

### 4.1 `Segment` (`walls2d/model.py`) 🟢

| Campo | Tipo | Obrigatório | Padrão | Limites (RN-18) |
|-------|------|-------------|--------|-----------------|
| `thickness` | float m | não | 0,15 | 0,01 a 2 |
| `height` | float m | não | 2,6 | 0,5 a 10 |
| `end_height` | float m | não | = `height` | 0,5 a 10 |
| `wall_type` | enum | não | `NORMAL` | `NORMAL`, `DIVISORIA`, `MURETA` |
| `lock_angle` | bool | não | False | — |
| `source` | str ou None | não | None | nome da parede existente |

### 4.2 `Chain` 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `nodes` | list[(float, float)] m | Face interna; N nós para N trechos (fechada) ou N+1 (aberta) |
| `segments` | list[Segment] | Um por trecho |
| `closed` | bool | Último trecho liga ao primeiro nó |
| `side` | `LEFT` / `RIGHT` | Lado da espessura em relação ao sentido dos nós |

### 4.3 `WallPlan` 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `chains` | list[Chain] | O ambiente |
| `removed_sources` | list[str] | Paredes apagadas no rascunho (removidas no OK) |
| `converted_sources` | list[str] | Objetos da camada nova convertidos (removidos no OK) |
| `references` | list[((x,y),(x,y))] | Contornos só para ver |

### 4.4 `BTM_PG_WallEditorState` (`WindowManager.btm_wall_editor`) 🟢

| Campo | Tipo Blender | Padrão / faixa | Virtual? |
|-------|--------------|----------------|----------|
| `tool` | Enum | SELECT; DRAW, INVERT, ADD_NODE, REMOVE_NODE | não |
| `grid_size` | Float DISTANCE | 1,0 (0,01–5) | não |
| `magnetic` | Bool | False | não |
| `new_direction` | Enum LEFT/RIGHT | LEFT | não |
| `new_thickness` | Float DISTANCE | 0,15 (0,01–2) | não |
| `new_height` | Float DISTANCE | 2,6 (0,5–10) | não |
| `line` | Enum INNER/OUTER | — | sim (sessão) |
| `length`, `thickness`, `height`, `end_height` | Float DISTANCE | — | sim (trecho selecionado) |
| `length_text`, `thickness_text`, `height_text`, `end_height_text` | String | unidade do projeto | sim |
| `angle_abs`, `angle_rel` | Float ANGLE | — | sim |
| `lock_angle` | Bool | — | sim |
| `direction` | Enum LEFT/RIGHT | — | sim (cadeia) |
| `wall_type` | Enum | — | sim |
| `equalize_height` | Bool | True (sessão) | sim |
| `remove_modules` | Bool | False (sessão) | sim |

Nada é persistido no `.blend` por este grupo: todos os campos virtuais leem e gravam a `Session`.

### 4.5 Persistência tocada em objetos (idprops) 🟢

| Chave | Onde | Escrita por | Significado |
|-------|------|-------------|-------------|
| `btm_wall_type` | parede `IS_WALL_BP` | `apply.apply_plan` | `NORMAL` / `DIVISORIA` / `MURETA` |
| `btm_wall_segments` | parede da camada nova | `caffmob.wall_builder` (lida por `scene_io.convert_into`) | JSON `[{start, end, thickness, height}]` |
| `WALL_TYPE` | parede legada | legado (lida por `heights`) | `Half` / `Fake` ficam fora do pé-direito |

## 5. Módulo `move_over`

Convenção comum (🟢): caixas `((xmin, ymin, zmin), (xmax, ymax, zmax))` em metros, no referencial de B (posição e
rotação de B, sem escala). X = largura, Y = profundidade com a frente em Y mínimo, Z = altura.

### 5.1 `align.Target` (`move_over/align.py`) 🟢

| Campo | Tipo | Valores |
|-------|------|---------|
| `kind` | str | `LEFT`, `RIGHT`, `DEPTH`, `HEIGHT`, `STACK`, `WALL_FACE` |
| `value` | float ou None | Fração 0–1 em `DEPTH`/`HEIGHT` (`FRACTIONS` = 0, 0,30, 0,50, 0,75, 1); `None` nos demais |

### 5.2 `MoveOver` (`move_over/scene.py`, estado em memória de uma sessão da janela) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `a`, `b` | `Object` | Raízes devolvidas por `classify.movable_root` / `classify.reference_root` |
| `b_is_wall` | bool | B é parede (`classify.WALL`) |
| `original_parent`, `original_matrix`, `original_parent_inverse` | `Object`, `Matrix`, `Matrix` | Para `restore()` |
| `b_frame`, `b_frame_inv` | `Matrix` 4×4 | Loc + rot de B sem escala, e o inverso |
| `box_b`, `a_local_box` | caixa | Caixas locais com a escala do objeto (`group.object_corners`) |
| `a_scale` | `Vector` | Escala original de A, preservada na matriz alvo |
| `origin_in_b` | `Vector` | Origem de A no referencial de B ao abrir |
| `delta` | `Vector` | Deslocamento acumulado no referencial de B (começa em 0) |
| `rotation` | float ° | Giro em Z pelo centro da base de A, módulo 360 (começa em 0) |

### 5.3 Posição salva (dicionário de `reposition.save_position` e `BTM_PG_SavedPosition`) 🟢

| Campo | Tipo Blender | Descrição |
|-------|--------------|-----------|
| `name` | String | "Posição N" (N = tamanho da coleção ao salvar) |
| `delta` | FloatVector(3) TRANSLATION, LENGTH | (`ref_x − anchor_x`, frente de A − frente de B, base de A − base de B) |
| `rotation` | Float | Graus |
| `b_side` | Enum `LEFT` / `RIGHT` | Lado de B em que estava o centro de A; define qual canto em X é a âncora |

Coleção `Scene.btm_saved_positions` + `Scene.btm_saved_positions_index` (Int, 0): **persistidas no `.blend`**. A janela
exibe só os 4 últimos itens; nenhum operador deste módulo remove itens.

### 5.4 `BTM_PG_MoveOverState` (`WindowManager.btm_move_over`, não salvo) 🟢

| Campo | Tipo Blender | Padrão / faixa | Efeito |
|-------|--------------|----------------|--------|
| `enabled` | Bool | False | Liga o atalho do botão direito; `update` redesenha as VIEW_3D |
| `tolerance_px` | Int | 12 (4–40) | Tolerância do clique nos alvos |
| `step` | Float DISTANCE | 0,01 m (0,0001–1) | Setas e Page Up/Down |
| `show_relative` | Bool | True | Campos mostram distância a B (True) ou posição no projeto (False) |

### 5.5 `BTM_PG_InsertionPlane` (`WindowManager.btm_insertion_plane`, não salvo) 🟢

| Campo | Tipo Blender | Padrão | Descrição |
|-------|--------------|--------|-----------|
| `active` | Bool | False | Plano em uso; `update` redesenha |
| `matrix` | FloatVector(16) | zeros | Matriz 4×4 achatada linha a linha: translação = ponto clicado, coluna Z = normal |
| `source_name` | String | "" | Objeto cuja face foi clicada |

### 5.6 Propriedades de operadores 🟢

| Operador | Propriedade | Tipo | Observação |
|----------|-------------|------|------------|
| `caffmob.move_over_dialog` | `a_name`, `b_name` | String `HIDDEN`, `SKIP_SAVE` | Nomes dos objetos (A arrastado, B referência) |
| `caffmob.move_over_substitute` | `a_name`, `b_name` | String `HIDDEN` | idem |
| `caffmob.move_over_substitute` | `module` | Enum dinâmico | id = caminho do `.blend` da biblioteca do usuário; rótulo "categoria / nome" |

### 5.7 Efeitos persistentes em objetos 🟢

| Alteração | Onde | Quando |
|-----------|------|--------|
| `A.parent = parede`, `A.matrix_parent_inverse = Identity` | `scene.MoveOver.preview` | B é parede ou está numa parede; desfeito por `restore()` no Cancelar, mantido no Confirmar |
| `novo.parent = A.parent`, A e descendentes removidos | `ops_substitute.substitute` | Substituir |
| `objeto.location` do módulo | `ops_move_on_wall` | Mover na Parede (restaurado no Esc) |

Idprops lidas, nunca escritas: `IS_WALL_BP` (parede), `btm_settings.collision_global` (cena, "Evitar Sobreposição"),
`btm_group` via `classify.free_group`.

## 6. Módulo `measure` (estruturas em memória, sem persistência própria)

### 6.1 `Placement` (`measure/cotas.py`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `x0` | float m | Início do módulo ao longo da parede (0 = começo da parede) |
| `width` | float m | Largura (`Dim X`) |
| `z0` | float m | Base a partir do piso |
| `height` | float m | Altura (`Dim Z`) |
| `back_y` | float m | Y do fundo do módulo; face da parede em 0, frente em Y < 0 |

### 6.2 `Cotas` 🟢

| Campo | Tipo | Fórmula | Módulo livre |
|-------|------|---------|--------------|
| `afastamento` | float m | `−back_y` | None |
| `anterior` | float m | `x0 − limite esquerdo` | None |
| `posterior` | float m | `limite direito − (x0 + width)` | None |
| `inferior` | float m | `z0` | `z0` mundial |
| `superior` | float m | `pé‑direito − (z0 + height)` | idem |

Obstáculo: tupla `(x0, x1, z0, z1)` em metros no referencial da parede; só conta se a faixa de altura cruza a do módulo
(sobreposição estrita).

### 6.3 `ModuleCotas` (`measure/scene_cotas.py`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `root` | `Object` | Raiz do módulo (`classify.classify(obj).root`) |
| `scene` | `Scene` | Cena de origem |
| `wall` | `Object` ou None | Pai com `IS_WALL_BP` |
| `on_wall` | bool | Parede presente e módulo do lado da frente sem rotação própria |
| `placement` | `Placement` | Na parede: `location` local; livre: `x0 = 0`, `back_y = 0`, `z0` mundial |
| `wall_length` | float m ou None | `Length` da parede |
| `ceiling` | float m | `home_builder.ceiling_height` da cena principal, `Height` da parede ou 2,6 |
| `depth` | float m | `Dim Y` (usada por `move_over/ops_move_on_wall` para o plano da frente) |

### 6.4 Dados lidos e escritos em objetos 🟢

| Dado | Origem | Leitura/Escrita |
|------|--------|-----------------|
| `Dim X`, `Dim Y`, `Dim Z` | inputs GN do módulo (`home_builder.mod_name` preenchido) | leitura |
| `btm_cabinet.width/depth/height` | módulo rápido da camada nova | leitura (fallback) |
| `root.dimensions` | Blender | leitura (último fallback) |
| `Length`, `Thickness`, `Height` | inputs GN da parede | leitura |
| `home_builder.ceiling_height` | cena principal | leitura |
| `IS_WALL_BP`, `IS_2D_ANNOTATION`, `IS_SNAP_LINE` | idprops | leitura |
| `root.location` (x, y, z local) ou `location.z` | módulo | **escrita** em `ModuleCotas.apply` |

## 7. Módulo `selection`

### 7.1 `Classified` (`selection/classify.py`) 🟢

| Campo | Tipo | Valores |
|-------|------|---------|
| `kind` | str | `ANNOTATION`, `FRONT`, `PART`, `MODULE`, `ROOM_DOOR`, `WINDOW`, `GEOMETRY`, `OBSTACLE`, `WALL`, `FLOOR`, `CEILING`, `OTHER` |
| `obj` | Object | O objeto que representa o tipo (a frente, a porta, a parede…) |
| `root` | Object | Módulo dono (frente e peça) ou o próprio |
| `library` | str | `FRAMELESS`, `FACE_FRAME`, `CLOSETS`, `BTM`, `HB` ou `''` (OTHER) |

### 7.2 `DeletePlan` (`selection/component.py`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `remove` | list[Object] | Tudo o que sai, filhos antes dos pais, sem repetir |
| `openings` | list[Object] | Vãos de porta e janela que saem (para tirar o furo da parede) |

### 7.3 `Element` (`selection/element_size.py`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `obj` | Object | O elemento (módulo, vão, parede, grupo de topo ou o próprio) |
| `info` | `Classified` | Classificação (frente e peça já convertidas no módulo) |
| `label` | str | `KIND_LABELS[kind]` ou "Objeto" |

### 7.4 Propriedades Blender 🟢

| Propriedade | Dono | Tipo | Padrão | Persistência |
|-------------|------|------|--------|--------------|
| `btm_component_select` | `Scene` | Bool, `update` → `forget()` | True | **`.blend`** (arquivo antigo lê o padrão) |
| `btm_component_exempt` | `WindowManager` | String (nomes separados por `\n`) | "" | sessão; limpa no `load_post` |
| `extend` | `caffmob.component_pick` | Bool | False | — |

### 7.5 Marcas lidas (idprops e grupos de propriedades) 🟢

| Marca | Tipo | Significado para o módulo |
|-------|------|---------------------------|
| `IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_FACE_FRAME_PRODUCT_CAGE`, `IS_CLOSET_STARTER_CAGE` | idprop | Raiz de módulo e biblioteca |
| `IS_DOOR_FRONT`, `IS_DRAWER_FRONT`, `IS_PULLOUT_FRONT`, `IS_FLIP_UP_DOOR`, `IS_CABINET_FRONT` | idprop | Frente |
| `hb_part_role` | idprop str | Frente se em `FRONT_ROLES` |
| `IS_2D_ANNOTATION` | idprop | Cota/anotação |
| `IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP` | idprop | Vão de porta / janela (HB) |
| `IS_OBSTACLE`, `IS_SOFFIT_BP` | idprop | Obstáculo |
| `IS_WALL_BP`, `IS_FLOOR_BP`, `IS_CEILING_BP` | idprop | Estrutura HB |
| `btm_plane.object_kind` | PropertyGroup enum | `WALL`, `MODULE`, `OPENING`, `GEOMETRY`, `FLOOR` da camada nova, **só se `is_property_set`** |
| `btm_group.is_group` / `.kind` | PropertyGroup | Grupo de peças (`PLAIN`, `FRAME`) |
| `btm_aggregate.is_aggregate` / `.kind` / `.parent_ref` / `.face` / `.u` / `.v` / `.size` / `.rest_offset` | PropertyGroup | Agregado (`AGGREGATE`, `LEAF`) |
| `btm_stick.is_stuck` | PropertyGroup | Item grudado |
| `btm_object_item.is_item` | PropertyGroup | Item da biblioteca de objetos |
| `face_frame_cabinet`, `hb_closet_starter`, `btm_cabinet` (`width/height/depth`) | PropertyGroup | Medidas por biblioteca (lidas e **escritas**) |
| `home_builder.mod_name` | PropertyGroup | Tem Geometry Nodes com `Dim X/Y/Z` |
| `btm_geometry.width` | PropertyGroup | Largura da geometria livre (**escrita** no Redimensionar) |
| `hb_frameless.frameless_selection_mode`, `hb_face_frame.*`, `hb_closets.*` | Scene | Modos de seleção herdados (D-07) |

### 7.6 Inputs de Geometry Nodes tocados 🟢

| Input | Objeto | Leitura/Escrita |
|-------|--------|-----------------|
| `Dim X`, `Dim Y`, `Dim Z` | módulo, porta, janela, obstáculo | leitura; escrita em `set_dimension` e `resize` (com `add_override` + `run_calc_fix` no módulo) |
| `Length`, `Height`, `End Height`, `Thickness` | parede HB | leitura; escrita em `set_wall` (`height` arrasta `End Height`) |
| `location.z` | porta/janela | peitoril (escrita só em janela) |
| `scale` | grupo de peças, malha solta, agregado | escrita no Redimensionar |

## 8. Módulo `openings`

### 8.1 `Part` (`openings/door_core.py`, usado também pela janela) 🟢

| Campo | Tipo | Valores / descrição |
|-------|------|---------------------|
| `role` | str | `FRAME`, `FRAME_HW`, `LEAF`, `LEAF_HW` |
| `name` | str | Nome da peça (prefixo agrupa: "Marco_", "Folha_", "Dobradica_"…) |
| `shape` | str | `BOX`, `CYL_X`, `CYL_Y`, `CYL_Z` |
| `center` | (x, y, z) m | Referencial da caixa |
| `size` | (dx, dy, dz) m | BOX; cilindro: (diâmetro, diâmetro, altura) |
| `material` | str | `WOOD`, `METAL`, `RUBBER`, `SLOT`, `BRASS` (porta); `ALU`, `GLASS`, `STONE` (janela) |
| `bevel` | float m | Padrão 1 mm; 0 sem chanfro |
| `leaf` | int ou None | Índice da folha (0, 1); None no marco |
| `horizontal` | bool | Veio da madeira na horizontal (UV) |

### 8.2 `Fit` (`openings/region_core.py`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ok` | bool | Encaixe aceito |
| `x`, `width`, `height`, `sill` | float m | Posição e medidas do vão (porta: `sill` 0) |
| `reason` | str | `''`, `EMPTY`, `OUTSIDE`, `TOO_TALL`, `OVERLAP` |

### 8.3 `BTM_PG_Opening` (`Object.btm_opening_real`, na caixa; salvo no `.blend`) 🟢

| Campo | Tipo Blender | Padrão | Descrição |
|-------|--------------|--------|-----------|
| `kind` | Enum | `NONE` | `NONE` (caixa antiga), `DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`, `WINDOW` |
| `signature` | String | "" | `kind|DimX|DimY|DimZ|IsLeft|SwingInside|vN`; igual = não refaz |
| `model_version` | Int | 0 | Versão do gerador na última montagem (`MODEL_VERSION` = 1) |
| `assembly` | Pointer Object | None | Grupo FRAME montado (filho da caixa) |

### 8.4 `BTM_PG_WallRegion` (`WindowManager.btm_wall_region`, sessão) 🟢

| Campo | Tipo Blender | Descrição |
|-------|--------------|-----------|
| `active` | Bool | Há região marcada |
| `wall` | String | Nome da parede (não ponteiro: apagada ou renomeada descarta a região) |
| `x0`, `x1`, `z0`, `z1` | Float DISTANCE | Espaço local da parede, `x0 < x1`, `z0 < z1` |
| `side` | Enum | `FRONT` (y = 0) / `BACK` (y = espessura) |

### 8.5 Dados lidos e escritos em objetos 🟢

| Dado | Objeto | Leitura/Escrita |
|------|--------|-----------------|
| `IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `IS_2D_ANNOTATION`, `IS_WALL_BP` | idprops | leitura |
| `Dim X`, `Dim Y`, `Dim Z` | caixa (`GeoNodeCage`) | leitura (largura, espessura da parede, altura do furo) |
| `Is Left`, `Swing Inside`, `Is Double` | símbolo 2D (`GeoNodeDoorSwing`) | leitura; `Is Left` **escrita** pela tecla I |
| `Length`, `Height`, `Thickness` | parede | leitura (região) |
| `btm_aggregate.open_value`, `.production_part`, `.kind`, `.is_aggregate`, `travel` | folhas LEAF | leitura em `_remember`; escrita ao restaurar e em `apply._write('travel')` |
| `btm_opening_material` | materiais | chave de reaproveitamento (escrita na criação) |
| `OPENING_FRAME_PROP` (`aggregates/collision`) | malhas do marco | escrita = nome do grupo FRAME |
| `display_type`, `show_in_front`, `hide_set`, `hide_viewport` | caixa e texto | escrita (`WIRE`, oculto) |
| `home_builder.show_entry_door_and_window_cages` | cena | leitura |
| `parent`, `matrix_parent_inverse`, `matrix_world` | marco, folhas, ferragens | escrita (hierarquia caixa → FRAME → LEAF → ferragens) |
| modificadores "Chanfro" (`BEVEL`) e "Normais ponderadas" | malhas montadas | criação |

## 9. Módulo `aggregates`

### 9.1 `BTM_PG_Aggregate` (`Object.btm_aggregate`, salvo no `.blend`) 🟢

| Campo | Tipo Blender | Padrão | `update` | Descrição |
|-------|--------------|--------|----------|-----------|
| `is_aggregate` | Bool | False | — | Convertido |
| `kind` | Enum | `AGGREGATE` | — | `AGGREGATE` ou `LEAF` |
| `parent_ref` | Pointer Object | None | — | Pai lógico (igual ao pai Blender) |
| `face` | Enum 6 faces | `NEG_Y` | posição | Face do pai |
| `u`, `v` | Float DISTANCE | 0 | posição | Do canto mínimo do pai ao do agregado nos eixos da face |
| `offset` | Float DISTANCE | 0 | posição | > 0 afasta, < 0 afunda (até a espessura) |
| `perforate` | Bool | False | recorte | Booleano no pai no volume afundado |
| `real_hole` | Bool | False | recorte | `CPM_CUTOUT` para o plano de corte (pai `GeoNodeCutpart`, face ±Z) |
| `production_part` | Bool | False | produção | Entra no plano de corte como placa |
| `cutter` | Pointer Object | None | — | Caixa cortadora "… - Recorte" |
| `orig_parent`, `orig_matrix` | Pointer, Float[16] | — | — | Para desconverter |
| `size` | FloatVector 3 LENGTH | — | — | Caixa do agregado no pai |
| `rest_offset` | FloatVector 3 | — | — | `box.lo − location` |
| `motion` | Enum | `SWING` | pivô | `SWING` / `SLIDE` |
| `hinge` | Enum | `LEFT` | pivô | `LEFT`, `RIGHT`, `TOP`, `BOTTOM` |
| `swing_sign` | Enum | `OUT` | abertura | `OUT` (frente, −Y do pai) / `IN` |
| `max_angle` | Float 1–180 | 90 | abertura | Graus |
| `slide_dir` | Enum | `POS_X` | pivô | `POS_X` / `NEG_X` |
| `travel` | Float DISTANCE ≥ 0,001 | 0,5 | curso (teto `free_travel`) + abertura | Metros |
| `open_value` | Float FACTOR 0–1 | 0 | abertura | Fração; para no contato |
| `contact_name` | String | "" | — | Objeto em que bateu/encostou |
| `contact_kind` | Enum | `NONE` | — | `OPEN` / `CLOSE` |
| `free_travel` | Float DISTANCE ≥ 0 | 0 | — | Curso livre até a esquadria (007) |
| `rest_overlap` | Float DISTANCE | 0 | — | Sobreposição dos montantes no arquivo (007) |
| `pivot` | Pointer Object | None | — | Empty "… - Eixo" |

### 9.2 `BTM_PG_Group` (`Object.btm_group`) e `BTM_PG_GroupMember` 🟢

| Campo | Tipo Blender | Descrição |
|-------|--------------|-----------|
| `is_group` | Bool | O Empty é um grupo de peças |
| `kind` | Enum | `PLAIN` (grupo), `FRAME` (esquadria), `LEAF` (folha) |
| `members[].obj` | Pointer Object | Peça |
| `members[].orig_parent`, `.orig_matrix` | Pointer, Float[16] | Para desfazer o grupo sem perda |

### 9.3 `BTM_PG_WindowInstall` (`Object.btm_window`, na jaula `IS_WINDOW_BP`) 🟢

| Campo | Tipo Blender | Descrição |
|-------|--------------|-----------|
| `frame` | Pointer Object | Esquadria instalada |
| `frame_matrix` | Float[16] | Matriz do mundo antes de instalar |

### 9.4 `BTM_PG_AssembleRow` (propriedade do operador `caffmob.window_assemble`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `label`, `names`, `count` | String, String (`\n`), Int | Grupo sugerido |
| `role` | Enum | `FRAME`, `SLIDE`, `SWING`, `IGNORE` |

### 9.5 Planos do SketchUp (`skp_core.py`, puro) 🟢

| Entidade | Campos |
|----------|--------|
| `MeshPlan` | `name`, `verts` (Z‑up, m), `tris`, `uvs` (v invertido), `material`, `material_index`, `texture` |
| `GroupPlan` | `name`, `path`, `meshes[]`, `children[]` |

### 9.6 Idprops e chaves 🟢

| Chave | Onde | Significado |
|-------|------|-------------|
| `btm_leaf_rest` (16 floats) | folha | Pose fechada no espaço do pai |
| `btm_leaf`, `btm_leaf_base`, `btm_open_fraction` | pivô | Nome da folha, ponto do eixo, fração atual |
| `btm_free_contact` | folha | Peça da esquadria no fim do curso livre |
| `btm_opening_frame` | malhas do marco (010) | Nome do grupo FRAME, fora do teste da própria folha |
| `IS_CUTTING_OBJ`, `btm_box` | cortador | Marca e chave da caixa |
| `btm_skp_material`, `btm_skp_key` | materiais | Reaproveitamento na reimportação |
| `IS_WINDOW_BP`, `IS_WALL_BP`, `IS_2D_ANNOTATION` | leitura | Jaula, parede, anotação |
| Modificadores | pai | `BOOLEAN` "Agregado (furo): …", `CPM_CUTOUT` "`AGGREGATE_PREFIX`…"; drivers `location.x/y` da esquadria |

## 10. Módulo `collision`

### 10.1 `OBB` (`collision/obb.py`, puro, `frozen`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `center` | tupla 3 floats (m, mundo) | Centro da caixa |
| `axes` | 3 tuplas de 3 floats | Eixos unitários no mundo (colunas da rotação do objeto) |
| `half` | tupla 3 floats (m) | Meias medidas ao longo de cada eixo |

Métodos: `corners()` (8 cantos em ordem binária), `aabb()` → `(lo, hi)`. Construtor de domínio `from_box(origin, axes, lo, hi)`.
Resultado de `overlap`: dicionário `{'depth': float, 'push': tupla 3, 'axis': int 0–14}` ou `None`.

### 10.2 `Item` (`collision/rules.py`, puro) 🟢

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `name` | str | obrigatório | Nome do objeto Blender |
| `box` | `OBB` | obrigatório | Caixa orientada no mundo |
| `kind` | `ITEM` / `WALL` / `OBSTACLE` / `FLOOR` / `CEILING` | `ITEM` | Tipo; `static` = os quatro últimos |
| `root` | str | `''` | Raiz do módulo; vazio = o próprio item (`group = root or name`) |
| `linked` | frozenset de str | vazio | Nomes ou raízes que ele pode tocar sem conflito |
| `override` | `INHERIT` / `ON` / `OFF` | `INHERIT` | Cópia de `btm_plane.collision_override` |

### 10.3 `Conflict` (`collision/rules.py`, puro, `frozen`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `kind` | `WALL` / `ITEM` / `FLOOR_CEILING` | Tipo da ocorrência (RN‑13) |
| `name_a` | str | Item móvel (nunca o estático; entre iguais, o de nome menor) |
| `name_b` | str | O outro item |
| `depth` | float (m) | Menor sobreposição entre os 15 eixos; > `TOLERANCE` |
| `push` | tupla 3 floats (m) | Deslocamento de A que elimina a sobreposição |
| `location` | tupla 3 floats (m) | Média dos centros (ponto do rótulo) |

### 10.4 `_Entry` (`collision/scan.py`, `__slots__`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `item` | `Item` | Entrada para o núcleo |
| `obj` | `bpy.types.Object` | Objeto de origem |
| `fine` | bool | Confirmar o par pela malha (`BVHTree.overlap`) |

### 10.5 `BTM_PG_Collision` (linha de `BTM_PG_CollisionState.items`) 🟢

| Campo | Tipo Blender | Subtipo | Padrão | Descrição |
|-------|--------------|---------|--------|-----------|
| `kind` | Enum `KIND_ITEMS` | — | `ITEM` | `WALL` "Penetração em parede", `ITEM` "Colisão entre itens", `FLOOR_CEILING` "Piso ou teto" |
| `name_a` | String | — | "" | Item |
| `name_b` | String | — | "" | Outro |
| `depth` | Float | `DISTANCE`, `LENGTH` | 0 | Profundidade |
| `push` | FloatVector 3 | `TRANSLATION` | 0 | Afastar |
| `location` | FloatVector 3 | `TRANSLATION` | 0 | Ponto |

### 10.6 `BTM_PG_CollisionState` (`WindowManager.btm_collision`, sessão, não salvo no `.blend`) 🟢

| Campo | Tipo Blender | Padrão | Descrição |
|-------|--------------|--------|-----------|
| `items` | Collection de `BTM_PG_Collision` | vazio | Ocorrências em ordem RN‑13 |
| `index` | Int | 0 | Última linha visitada por "Ir para" |
| `checked` | Int | −1 | Itens verificados na última checagem; −1 = nunca |
| `scope` | Enum `ALL` / `SELECTED` | `ALL` | Escopo da última verificação |
| `stale` | Bool | False | Resultado desatualizado (RN‑14) |
| `error` | String | "" | Falha do cálculo; nunca mostrada como "sem colisões" |
| `checked_names` | String | "" | Nomes verificados, ordenados, separados por `\n` (vigiados por `stale`) |

### 10.7 Propriedades de operadores 🟢

| Operador | Propriedade | Tipo | Padrão |
|----------|-------------|------|--------|
| `caffmob.check_collisions` | `scope` | Enum `ALL` / `SELECTED` | `ALL` |
| `caffmob.collision_goto` | `index` | Int | 0 |
| `caffmob.collision_push_out` | `index` | Int | 0 |

### 10.8 Dados lidos e escritos em objetos 🟢

| Dado | Onde | Leitura/escrita | Uso |
|------|------|-----------------|-----|
| `btm_settings.collision_global` | Scene | lê | Chave global "Evitar Sobreposição" |
| `btm_plane.collision_override` | Object | lê (painel escreve) | `OFF` exclui o item |
| `btm_aggregate.is_aggregate`, `parent_ref` | Object | lê | Agregado é item fino; pai vira `linked` |
| `btm_stick.is_stuck`, `host` | Object | lê | Hospedeiro vira `linked`; afastar só no plano da face |
| `IS_APPLIANCE`, `IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `IS_WALL_BP`, `btm_wall_segments` | idprops | lê | Classificação e ligação porta/janela × parede |
| `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x` | idprops | lê | Fora da verificação |
| `hide_viewport`, `visible_get()`, `display_type` | Object | lê | Ocultos, `WIRE`/`BOUNDS` ficam fora |
| `matrix_world.translation` | Object | escreve | "Afastar até encostar" (um passo de desfazer) |
| `_changed` (set) | módulo `stale` | memória | Raízes vigiadas que mudaram desde a verificação |
| `_Meshes._trees` | por verificação | memória | BVH por `as_pointer()` |

## 11. Módulo `stick`

### 11.1 `BTM_PG_Stick` (`Object.btm_stick`, salvo no `.blend`) 🟢

| Campo | Tipo Blender | Subtipo | Padrão | `update` | Descrição |
|-------|--------------|---------|--------|----------|-----------|
| `is_stuck` | Bool | — | False | — | Grudado |
| `host` | Pointer Object | — | None | — | Hospedeiro (igual ao pai Blender enquanto o vínculo vale) |
| `face_kind` | Enum `BOX_SIDE` / `PLANE` | — | `BOX_SIDE` | — | Lado da caixa (acompanha medida) ou plano fixo (face inclinada) |
| `face` | Enum 6 faces (`FACE_ITEMS`) | — | `NEG_Y` | — | Lado da caixa; parede: `NEG_Y` frente, `POS_Y` trás |
| `plane` | FloatVector 16 | — | `IDENTITY` | — | Matriz do plano (colunas U, V, N, origem) no espaço do hospedeiro; só `PLANE` |
| `u` | Float | `DISTANCE`, `LENGTH` | 0 | `apply.update_position` | Da origem da face ao canto mínimo da pegada, eixo U |
| `v` | Float | `DISTANCE`, `LENGTH` | 0 | `apply.update_position` | Idem, eixo V |
| `distance` | Float | `DISTANCE`, `LENGTH` | 0 | `apply.update_position` | Distância à face; 0 encostado, negativo entra no hospedeiro |
| `spin` | Float | `ANGLE`, `ROTATION` | 0 | `apply.update_spin` | Giro em torno da normal da face |
| `applied_spin` | Float | `ANGLE` | 0 | — | Último giro aplicado (delta = `spin − applied_spin`) |
| `out_of_face` | Bool | — | False | — | Centro da pegada saiu do retângulo da face (RN‑08a) |
| `orig_parent` | Pointer Object | — | None | — | Pai antes de grudar (devolvido no Desgrudar) |
| `last_world` | FloatVector 16 | — | `IDENTITY` | — | Última matriz de mundo (restaurada em "Vínculo perdido") |

Os `update` são guardados por `props._guard` (conjunto de `(nome do objeto, campo)`): `apply.write` grava sem disparar.

### 11.2 Referencial e pegada (`stick/frame.py`, puro) 🟢

| Estrutura | Forma | Descrição |
|-----------|-------|-----------|
| `host_box` | `((x, y, z) mín., (x, y, z) máx.)` | Caixa local avaliada do hospedeiro |
| `frame` | `(origem, U, V, N)` tuplas 3 | Referencial da face; N para fora |
| `plane_values` | 16 floats por linha | `frame_to_matrix(frame)`; inverso `matrix_to_frame` |
| `footprint` | `((u, v, n) mín., (u, v, n) máx.)` | Caixa do item no referencial da face |
| `params` | `(u, v, distance)` | Canto mínimo da pegada |
| `extent` | `((u0, u1), (v0, v1))` ou `None` | Retângulo do lado (`BOX_SIDE`); `None` em `PLANE` |
| `choose_face` | `(BOX_SIDE, face)` ou `(PLANE, None)` | Tipo e lado escolhidos ao grudar |
| `contact_axis` | `'BACK'` / `'BOTTOM'` | Lado do item que encosta |

### 11.3 Estruturas em memória (`apply.py`, `settle.py`, `magnet_preview.py`) 🟢

| Nome | Tipo | Descrição |
|------|------|-----------|
| `apply._index` | dict nome do hospedeiro → lista de nomes | Grudados por hospedeiro; chave `''` = sem hospedeiro; `_index_ok` valida |
| `apply._last_box` | dict nome → `host_box` | Última caixa vista de cada hospedeiro (detecta mudança de medida) |
| `apply._pending` | set de nomes | Objetos que se moveram, à espera do assentar |
| `apply._quiet_until` | float monotônico | Fim do período quieto após abrir/desfazer |
| `apply._busy` | bool | Trava de reentrância do handler e do timer |
| `settle._settled` | dict nome → 16 floats arredondados | Pose de mundo da última vez que o item foi assentado |
| `magnet.find` | `(obj, ponto, normal, vértices do polígono)` | Face alcançada pelo ímã |
| `magnet_preview._last` | `(hospedeiro, ponto, cantos da face, cantos da caixa)` | Último quadro da prévia |
| `ops_stick.snapshot` | `(pai, matrix_parent_inverse, matrix_world, {13 campos})` | Estado para `restore` no cancelar |

### 11.4 Preferências e configuração 🟢

| Campo | Onde | Tipo | Padrão | Limites | Descrição |
|-------|------|------|--------|---------|-----------|
| `stick_magnet` | `BTM_AddonPreferences` | Bool | True | — | Ímã ligado |
| `stick_magnet_distance` | `BTM_AddonPreferences` | Float `DISTANCE` | 0,05 m | 0,001–0,5 m | Alcance do ímã |
| `stick_migrated` | `Scene.btm_settings` | Bool | False | — | Cena já passou pela migração |

### 11.5 Dados lidos e escritos em objetos 🟢

| Dado | Onde | Leitura/escrita | Uso |
|------|------|-----------------|-----|
| `parent`, `matrix_parent_inverse`, `matrix_basis`, `matrix_world` | item | escreve | Grudar (inversa identidade), desgrudar, reposicionar, girar |
| `bound_box` do avaliado | item, hospedeiro | lê | `local_box`, pegada |
| `IS_WALL_BP` | pai | lê | Migração e módulo novo na parede |
| `GeoNodeWall` input `Thickness` | parede | lê | Lado frente/trás na migração |
| `rotation_euler.z`, `location.y` | módulo | lê | Lado frente/trás na migração |
| `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `obj_x` | filhos / acertos | lê | Fora da caixa e dos raios |
| `btm_aggregate.is_aggregate` | item | lê | Agregado não gruda |
| `window.modal_operators` | janelas | lê | Adiar o assentar durante movimentos |
| `preview_cage` / `cabinet` / `obj` | `PlacementMixin` ativo | lê | Item da prévia do ímã |

## 12. Módulo `customize`

### 12.1 `BTM_PG_CustomSpec` (`Object.btm_custom`, salvo no `.blend`; no vão, na peça ou na raiz) 🟢

| Campo | Tipo Blender | Padrão | Onde vale | Descrição |
|-------|--------------|--------|-----------|-----------|
| `door_style` | String | "" | vão | Estilo da porta por nome; vazio = do módulo |
| `drawer_style` | String | "" | vão | Estilo da gaveta por nome |
| `pull_model` | String | "" | vão (ou raiz com `pull_all_fronts`) | Nome/arquivo do puxador; `__NONE__` = sem puxador; vazio = do projeto |
| `pull_position` | Enum `PULL_POSITION_ITEMS` | `DEFAULT` | vão | `DEFAULT`, `TOP`, `MIDDLE`, `BOTTOM`, `SIDE` |
| `pull_all_fronts` | Bool | False | raiz | Mesmo puxador em todas as frentes |
| `front_material` | String | "" | vão | Material das frentes do vão |
| `material` | String | "" | peça | Material da peça; vence o do grupo |
| `group_materials` | Collection `BTM_PG_GroupMaterial` | vazio | raiz | Material por grupo |
| `slide_kind` | String | "" | vão | Corrediça das gavetas (`BLUM`, feature 008); vazio = padrão |
| `interior` | String JSON | "" | vão | `{shelves, dividers, drawers, heights}`; vazio = interior da biblioteca |

`BTM_PG_GroupMaterial`: `group` (Enum `CAIXA`/`FRENTES`/`FUNDO`/`INTERNO`), `material` (String).

### 12.2 `Spec`, `Opening`, `Interior` (`customize/spec.py`, puros) 🟢

| Estrutura | Campo | Tipo | Padrão | Descrição |
|-----------|-------|------|--------|-----------|
| `Interior` | `shelves`, `dividers`, `drawers` | int | 0 | Faixas 0–20, 0–10, 0–8 |
| `Interior` | `heights` | list[float] m | [] | Alturas da face de baixo de cada prateleira; vazio = iguais |
| `Opening` | `path` | str | obrigatório | `bay<i>/opening<j>` (frameless), `opening<i>` (face frame, closets), `module` (btm) |
| `Opening` | `front` | `FRONT_TYPES` ou "" | "" | Vazio = como está |
| `Opening` | `drawer_count` | int | 0 | Só com `DRAWERS` (1–8) |
| `Opening` | `door_style`, `drawer_style`, `pull_model`, `front_material` | str | "" | Por nome |
| `Opening` | `pull_position` | `PULL_POSITIONS` | `DEFAULT` | — |
| `Opening` | `interior` | `Interior` ou None | None | Omitido na serialização quando None |
| `Spec` | `library` | `FRAMELESS`/`FACE_FRAME`/`CLOSETS`/`BTM` | "" | — |
| `Spec` | `openings` | list[Opening] | [] | — |
| `Spec` | `part_materials` | dict nome da peça → material | {} | — |
| `Spec` | `group_materials` | dict grupo → material | {} | — |
| `Spec` | `pull_all_fronts` | str | "" | Puxador de todas as frentes; vazio = por frente |
| `Spec` | `aggregates` | list[{name, parent_path, kind}] | [] | Só no manifesto |

### 12.3 Manifesto `caffmob_draw.user-module` 1.1.0 (`<nome>.json`) 🟢

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `format` | str | sim | `caffmob_draw.user-module` |
| `schema_version` | str | sim | `1.1.0`; leitor aceita major 1 |
| `name`, `category`, `library`, `root_object` | str | sim (nome e raiz não vazios) | Nome original, categoria, biblioteca, nome da raiz |
| `created`, `addon_version` | str | não | ISO 8601 com fuso; versão do add‑on |
| `dimensions_mm` | {width, height, depth} | não | Caixa de mundo em mm |
| `styles` | {door_styles: [str]} | não | Estilos usados |
| `materials`, `pulls` | [str] ordenados | não | Por nome, sem repetição |
| `spec` | `Spec.to_dict()` | sim | Personalização |
| `structure` | {papel: {removed, mode, thickness_mm, material}} | não (006) | Papéis `TOP`/`BOTTOM`/`BACK`/`LEFT`/`RIGHT`; modos `KEEP`/`EXTEND`/`SHRINK` |
| `divisions` | [{uid, space, orientation, offset_mm, use_front, front_mm, use_back, back_mm, thickness_mm, material}] | não (006) | `space` casa `^s\d+(\.[ab])*$`; `orientation` `VERTICAL`/`HORIZONTAL` |

Arquivos irmãos: `<nome>.blend` (`libraries.write`, `RELATIVE_ALL`, `fake_user`) e `<nome>.png` (256 px), em
`extension_path_user(pkg, "modules")/<categoria sanitizada>/`.

### 12.4 Entrada da biblioteca (`library_io.list_modules`) 🟢

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `name` | str | Nome do manifesto, ou o nome base do arquivo |
| `category` | str | Pasta |
| `blend`, `png`, `json` | caminhos | Os três arquivos |
| `has_manifest` | bool | `.json` presente (sem ele: "sem personalização") |

### 12.5 Propriedades de operadores 🟢

| Operador | Propriedades |
|----------|--------------|
| `caffmob.customize_set_front` | `path` (oculto), `front` (enum dinâmico), `drawer_count` 1–8 |
| `caffmob.customize_set_style` | `path`, `kind` `DOOR`/`DRAWER`, `style` (enum dinâmico, `""` = do módulo) |
| `caffmob.customize_set_pull` | `path`, `model` (enum dinâmico), `position`, `all_fronts` |
| `caffmob.customize_set_material` | `target` `FRONTS`/`GROUP`/`PART`, `path`, `group`, `material` |
| `caffmob.customize_set_interior` | `path`, `shelves` 0–20, `dividers` 0–10, `drawers` 0–8, `heights` "a; b" |
| `caffmob.customize_clear` | `path` |
| `caffmob.module_save` | `module_name`, `category` (`Geral`), `overwrite`, `thumbnail` |
| `caffmob.module_insert` | `filepath` (oculto), `place` (oculto, `SKIP_SAVE`) |
| `caffmob.module_delete`, `module_rename` | `filepath`; `new_name` |

### 12.6 Dados lidos e escritos em objetos 🟢

| Dado | Onde | Leitura/escrita | Uso |
|------|------|-----------------|-----|
| `IS_FRAMELESS_BAY_CAGE`, `IS_FRAMELESS_OPENING_CAGE`, `IS_FRAMELESS_INTERIOR_CAGE` | jaulas frameless | lê | Caminho do vão e interior |
| `Door Swing`, `False Front`, `APPLIANCE_NAME`, `Shelf Quantity` | vão/jaula frameless | lê/escreve | Tipo de frente; prateleiras |
| `IS_CABINET_FRONT`, `IS_DOOR_FRONT`, `IS_DRAWER_FRONT`, `IS_PULLOUT_FRONT`, `IS_FLIP_UP_DOOR`, `IS_CABINET_PULL` | frentes/puxadores | lê | Classificação |
| `DOOR_STYLE_INDEX`, `DOOR_STYLE_NAME` | frente | escreve | Estilo aplicado por nome |
| `Pull Location`, `Tall Pull Vertical Location`, `Center Pull`, `Handle Horizontal Location`, `Pull Length` | frente frameless | escreve | Posição do puxador |
| `GeoNodeHardware` input `Object` | puxador frameless/btm | escreve (`compat`) | Modelo do puxador |
| `GeoNodeCutpart` `Top Surface`/`Bottom Surface`/`Thickness`/`Length`/`Width` | peças | lê/escreve (`compat`) | Material e espessura |
| `Material`, `Stile Material`, `Panel Material`, `Rail Material` | outros modificadores de nós | escreve | Material das frentes compostas |
| `hb_part_role`, `hb_panel_index`, `btm_component`, `CABINET_TYPE` | peças | lê | Grupo e papel |
| `face_frame_opening.front_type/hinge_side/interior_items` | vão face frame | lê/escreve | Frente e interior |
| `hb_front_door_style`, `hb_front_drawer_style` | vão face frame | lê | Estilo gravado pela biblioteca |
| `hb_door_swing`, `hb_drawer_qty`, `hb_adj_shelf_qty`, `hb_cubby_cols`, `hb_pull_name` | vão/puxador closets | lê/escreve | Frente, prateleiras, puxador |
| `btm_cabinet.door_swing/shelves/has_*/mode_*/thickness_*` | raiz btm | lê/escreve | Frente, interior, estrutura |
| `btm_structure` (`cabinet_editor/data_props`), `btm_division`, `btm_extra`, `btm_division_sig` | raiz/filhos | lê | Estrutura e divisões (006, 008) |
| `btm_removed`, `btm_raw_material`, drivers `hide_viewport`/`hide_render` (`btm_rm`) | chapas | escreve | Remoção e material bruto |
| `btm_pull_file` | objeto de puxador | lê/escreve | Cache por chave |
| `Remove Bottom`, `Material Thickness` | raiz frameless | lê/escreve | Estender base; espessura por driver |
| `delta_location` | peça do fundo | escreve | Fundo recuado (008) |
| `btm_aggregate.is_aggregate/kind` | filhos | lê | Agregados no manifesto |
| `_ENUM_CACHE`, `reapply._running` | memória | — | Strings dos enums dinâmicos; trava de reentrância |

---

## 13. Módulo `cabinet_editor`

### 13.1 Dados gravados no módulo (`data_props.py`, salvos no `.blend`) 🟢

`Object.btm_structure` — `BTM_PG_Structure`, na **raiz** do módulo (features 006 e 008):

| Campo | Tipo Blender | Padrão | Descrição |
|-------|--------------|--------|-----------|
| `components` | Collection `BTM_PG_StructureItem` | vazio | Só os papéis que o usuário mexeu; ausente = como a biblioteca faz |
| `back_mode` | Enum `FULL` / `RECESSED` | `FULL` | Fundo Inteiro / Inteiro Recuado (008, D‑11) |
| `back_setback` | Float DISTANCE, min 0 | 0,02 m | Recuo do fundo |
| `auto_back` | Bool | True | "Inserir automaticamente": reaplica o recuo depois de cada reconstrução |
| `extras` | Collection `BTM_PG_StructureExtra` | vazio | Estado da árvore de extras (RN‑07a) |

`BTM_PG_StructureItem`:

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `role` | Enum `TOP`/`BOTTOM`/`BACK`/`LEFT`/`RIGHT` | `TOP` | Tampo, base, fundo, laterais |
| `removed` | Bool | False | Chapa removida |
| `mode` | Enum `KEEP`/`EXTEND`/`SHRINK` | `KEEP` | Modo usado na remoção |
| `thickness` | Float DISTANCE, min 0 | 0 | 0 = segue o Configurador; faixa de validação 3–60 mm (`STR-002`) |
| `material` | String | "" | Vazio = segue o Configurador |

`BTM_PG_StructureExtra`: `kind` (String, chave de `catalog.TREE`), `enabled` (Bool, False), `value` (Float DISTANCE;
0 = padrão de `extras.DEFAULTS`). As posições dos pés `FOOT_1`–`FOOT_4` contam como ligadas quando não há registro.

`Object.btm_division` — `BTM_PG_Division`, em cada **chapa de divisão** (`CabinetPart` filho direto da raiz):

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `is_division` | Bool | False | Marca a chapa (posto por `from_dict`) |
| `uid` | String | "" | 8 hex (`uuid4`); identidade estável |
| `space` | String | `s0` | Subvão‑folha cortado: `s<i>(.a|.b)*` |
| `orientation` | Enum `VERTICAL`/`HORIZONTAL` | `VERTICAL` | Em pé (esquerda/direita) ou deitada (baixo/cima) |
| `offset` | Float DISTANCE | 0 | Face esquerda/de baixo do subvão até a chapa |
| `use_front`, `front` | Bool, Float ≥ 0 | False, 0,02 m | Recuo na frente |
| `use_back`, `back` | Bool, Float ≥ 0 | False, 0,02 m | Recuo atrás |
| `thickness` | Float ≥ 0 | 0 | 0 = Divisória do Configurador (o distanciador grava a própria) |
| `material` | String | "" | Vazio = Configurador |
| `bay` | Bool | False | Gerada pelo Número de vãos (008) |
| `kind` | Enum `FIXED`/`MOVABLE`/`SPACER` | `FIXED` | Fixa, móvel (furação nas vizinhas, `cutting/drilling`), distanciador |
| `follow` | String | "" | uid da divisória seguida (distanciador "p/ Divisão") |

`Object.btm_extra` — `BTM_PG_Extra`, nas peças das abas da 008 (filhas diretas da raiz):

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `is_extra` | Bool | Marca a peça |
| `kind` | Enum (19) | `BASE_TOP_RECESSED`, `FOOT`, `KICK_FRONT`, `KICK_LEFT`, `KICK_RIGHT`, `KICK_GRANITE`, `CLOSURE`, `VIEW_FRONT`, `VIEW_LEFT`, `VIEW_RIGHT`, `VIEW_TALL_LEFT`, `VIEW_TALL_RIGHT`, `VIEW_TALL_FRONT`, `APPLIANCE_PANEL`, `APPLIANCE`, `APPLIANCE_SUPPORT`, `PISTON`, `SLIDE_TRACK`, `SLIDE_LEAF` |
| `catalog_id` | String | Item do catálogo (internos, deslizantes) |
| `space` | String | Subvão onde foi inserido (internos) |
| `slot` | Int | Pé 1–4, lado do fechamento 1–2, número do interno, índice da folha |
| `params` | String JSON | Parâmetros (hoje `{}`) |

### 13.2 Idprops e dados lidos/escritos em objetos 🟢

| Dado | Onde | Leitura/escrita | Uso |
|------|------|-----------------|-----|
| `btm_division_sig` | raiz | escreve/lê | Assinatura (vãos + divisões + material + espessura); sem ela o handler ignora o módulo |
| `btm_component` | chapas (`DIV`, `BAS`, `ROD`, `TAMPON`, `ESP`, `PRAT`, `FRE_FORNO`, `POR`) | escreve | Componente do Configurador / papel no corte |
| `btm_raw_material` | chapas | escreve | Material bruto (`MDF`, `GRANITO`…) |
| `btm_hardware` | pés, trilhos, pistão | escreve | `PE_PLASTICO`, `TRILHO_INF`, `TRILHO_SUP`, `PISTAO` |
| `btm_slides` | grupo FRAME "Deslizantes" | escreve/lê | JSON `{item, leaves, invert}`; `opens` vem das folhas |
| `btm_line` | raiz | lê | Linha do Configurador (`COZ`, `DOR`…) |
| `btm_standard_uid` | raiz | lê | Padrão global de origem (012) |
| `btm_cabinet.assembly`, `width`/`height`/`depth` (limites) | raiz `btm` | lê/escreve | Montagem (012); faixa das medidas |
| `face_frame_cabinet`, `hb_closet_starter` (`width`/`height`/`depth`, `closet_type`) | raiz | lê | Faixa das medidas; tipo |
| `CABINET_TYPE` | raiz | lê | Tipo do armário no cabeçalho |
| `btm_custom` (todos os campos; `slide_kind = 'BLUM'`) | vão, raiz, peças | lê/escreve | Instantâneo cru e aba Gavetas (Blum) |
| `GeoNodeCutpart` `Length`/`Width`/`Thickness`/`Mirror Y`/`Mirror Z`, `Top Surface` | chapas | escreve/lê (`compat`) | Medidas da chapa; material emprestado |
| Modificador `CPM_CUTOUT` (`X`, `End X`, `Y`, `End Y`, `Route Depth`, `Flip Z`), nome com `machining.AGGREGATE_PREFIX` | painel p/ eletro | escreve | Recorte que vai para a usinagem |
| `btm_aggregate.open_value`, `btm_group.kind` | folhas e grupos dos deslizantes | lê/escreve | Abertura; FRAME/LEAF (007) |
| `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x`, `IS_CABINET_FRONT`, `hb_part_role` | filhos | lê | Fora da vista; tipo do componente |

### 13.3 Estruturas em memória (puras) 🟢

| Estrutura | Campos | Onde |
|-----------|--------|------|
| `EditorState` | `dimensions` (L, A, P) m; `spec` (dict de `Spec` + `_raw`); `structure`; `divisions` (crus); `extras`; `slides`; `interiors` [{catalog_id, space, slot}]; `backs` {mode, setback, auto} | `state.py` |
| `Draft` | `initial`, `current`, `history` | `state.py` |
| `_raw` | `openings` {caminho: {door_style, drawer_style, pull_model, pull_position, front_material, interior}}, `pull_model`, `pull_all_fronts`, `groups`, `parts` | `bridge.py` |
| `Message` | `code`, `severity` `ERROR`/`WARNING`/`INFO`, `component`, `parameter`, `value`, `range`, `action`; `blocks` | `validate.py` |
| `Part` | `name`, `kind`, `lo`, `hi`; `rect`, `size` | `elevation.py` |
| `RoleState` | `removed`, `mode`, `thickness`, `material`; `changed` | `structure.py` |
| `Box`, `Division` | `lo`, `hi`; ver §13.1 | `divisions.py` |
| `Item` | `id`, `tab`, `group`, `label`, `description`, `action`, `params`, `size_mm`, `margin_mm`, `invertible`, `filter`, `groove` | `catalog.py` |
| `extras.Piece` | `kind`, `box`, `component`, `hardware`, `material`, `slot` | `extras.py` |
| `slides.Leaf`, `Track`, `Layout` | `index`, `track`, `box`, `groove`; `box`; `leaves`, `tracks` | `slides.py` |
| `appliances.Layout` | `panel` (Piece ou None), `cutout`, `appliances` ((código, caixa), …) | `appliances.py` |

Códigos de mensagem: `DIM-001` vazio, `DIM-002` não é número, `DIM-003` fora da faixa (erros); `GEO-001` fora do
volume (erro em prateleira/divisória, senão aviso); `GEO-002` sobreposição interna > 1 mm (erro); `CAT-001` seção sem
suporte (aviso); `STR-001` modo que a biblioteca não faz (aviso, cai em `KEEP`); `STR-002` espessura fora de 3–60 mm
(erro); `DIV-001` subvão < 50 mm, `DIV-002` profundidade < 50 mm, `DIV-003` subvão inexistente (erros); `LIB-001`
aviso da biblioteca (aviso).

### 13.4 Sessão e campos do painel (`props.py`, em memória) 🟢

`Session`: ver code-analysis §14.9. `WindowManager.btm_cabinet_editor` (`BTM_PG_CabinetEditorState`):

| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `width`, `height`, `depth` | Float virtual | — | `get` do rascunho; `set` enfileira `dimension` |
| `components`, `messages`, `adjustments`, `structure`, `divisions` | Collections (espelhos) | — | Linhas das listas do painel |
| `component_index`, `structure_index`, `division_index` | Int | −1 | Índice; o de componentes seleciona na sessão |
| `tab` | Enum (7, números estáveis 0,1,3–7) | `STRUCTURE` | Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos |
| `new_orientation`, `new_use_front`, `new_front`, `new_use_back`, `new_back` | Enum, Bool, Float 0–1 m | `VERTICAL`, False, 0,02 | Próxima divisão |
| `space` | Enum dinâmico virtual | — | Subvão escolhido (lê/grava `Session.space`) |
| `catalog_item` | String | "" | Item do catálogo escolhido |
| `invert` | Bool | False | Inserir invertido |
| `div_mode`, `div_kind`, `div_count` | Enum, Enum, Int 1–10 | `VERTICAL`, `FIXED`, 2 | Aba Divisões (`MULTIPLE`; `MOVABLE`/`FIXED`/`SPACER`/`NONE`) |
| `drawer_tab`, `drawer_count`, `drawer_style`, `drawer_pull` | Enum, Int 1–8, enums dinâmicos | `DRAWERS`, 4 | Aba Gavetas |
| `door_region`, `door_scope`, `door_style`, `door_pull` | Enum, Enum, dinâmicos | `LOWER`, `BOTH` | Aba Portas |
| `interior_group`, `interior_filter` | Enum | `PANELS`, `EXTERNAL` | Aba Internos |
| `slide_family`, `slide_leaves` | Enum, Int 2–3 | `WOOD`, 2 | Aba Deslizantes |
| `back_tab` | Enum | `FULL` | Aba Fundos |
| `step`, `step_initial` | Float | 10 mm, 0 | Movimentação pelas setas |
| `tree_<chave>`, `value_<chave>` | Bool/Float virtuais (20 + 8) | — | Árvore de extras (grupo liga/desliga os filhos) |
| `comp_<papel>` | Bool virtual (5) | — | Chapa presente; desmarcar = `REMOVE_PART` `KEEP` |
| `bays` | Int virtual 1–10 | — | Número de vãos (`SET_BAYS`) |
| `pos_front`, `pos_low`, `pos_back`, `pos_high` | Float virtuais | — | Cotas da divisória selecionada (`EDIT_DIVISION`) |

### 13.5 Propriedades de operadores 🟢

| Operador | Propriedades |
|----------|--------------|
| `caffmob.cabinet_editor_edit` | `action` (`FRONT`/`STYLE`/`PULL`/`MATERIAL`/`INTERIOR`), `front` (dinâmico), `drawer_count` 1–8, `kind`, `style`, `model`, `position`, `all_fronts`, `target` `FRONTS`/`GROUP`, `group`, `material`, `shelves` 0–20, `dividers` 0–10, `drawers` 0–8, `heights` "a; b" |
| `caffmob.cabinet_editor_history` | `redo` |
| `caffmob.cabinet_editor_close` | `choice` `CONTINUE`/`DISCARD`/`CONFIRM` |
| `caffmob.cabinet_editor_division_edit` | `uid` (oculto), `offset`, `use_front`, `front`, `use_back`, `back`, `thickness`, `material` (`MATERIAL_ITEMS`: "", MDF, MDP, COMPENSADO, OSB, VIDRO, OUTRO) |
| `caffmob.cabinet_editor_division_remove` | `uid` |
| `caffmob.cabinet_editor_part_remove` | `role`, `mode` |
| `caffmob.cabinet_editor_part_restore` | `role` |
| `caffmob.cabinet_editor_part_edit` | `role`, `thickness` 0–60 mm, `material` |
| `caffmob.cabinet_editor_insert` | `tab` (`DIVISIONS`/`DRAWERS`/`INTERIOR`/`DOORS`/`SLIDING`/`BACKS`) |
| `caffmob.cabinet_editor_pick` | `item` |
| `caffmob.cabinet_editor_remove_item` | `kind` `INTERIOR`/`SLIDES`, `slot` |

### 13.6 Pedidos da fila do modal 🟢

| Tipo | Dados | Efeito |
|------|-------|--------|
| `dimension` | (campo, m) | Valida (`DIM-003`); válido → `set_dimension`; `refresh` |
| `edit` | (ação, payload com `targets`) | `bridge.edit`; `targets` entram em `edited` (fora dos Ajustes automáticos) |
| `apply` | — | `ed.undo_push` + `apply_point` |
| `arrow` | (`X`/`Z`, ±1) | `position.step_move` na divisória selecionada |
| `undo` / `redo` | — | Instantâneo do rascunho → `apply_state` |

Payloads de `edit`: `FRONT` {path, front, drawer_count}; `STYLE` {path, kind, style}; `PULL` {path, model, position,
all_fronts}; `MATERIAL` {path, target, group, material}; `INTERIOR` {path, shelves, dividers, drawers, heights};
`ADD_DIVISION` {space, orientation, use_front, front, use_back, back, kind, thickness?, follow?}; `EDIT_DIVISION`
{uid, campos}; `REMOVE_DIVISION` {uid}; `EDIT_PART` {role, thickness, material}; `REMOVE_PART` {role, mode};
`RESTORE_PART` {role}; `SET_ASSEMBLY` {assembly}; `TOGGLE_EXTRA` {key, enabled?, value?}; `SET_BAYS` {count};
`SET_BACK` {mode, setback, auto, insert}; `ADD_MANY` {space, orientation, count, kind, recuos}; `REMOVE_IN_SPACE`
{space}; `INSERT_DOORS` {space, scope, region, style, invert, pull}; `INSERT_DRAWERS` {space, count, variant, style,
pull}; `INSERT_INTERIOR` {catalog_id, space}; `REMOVE_INTERIOR` {slot}; `INSERT_SLIDES` {item, leaves, invert};
`REMOVE_SLIDES` {}.


## 14. Módulo `standards`

🟢 **CONFIRMADO** por `standards/model.py`, `apply_core.py`, `cabinet_defaults.py`, `io_json.py`, `io_promob.py`,
`sync.py` e `data/dimension_schema.py`; análise 2026-10-10. Nome (`PropertyGroup.name`) é herdado nas coleções.
Propriedades RNA são acessadas por atributo; as marcas `btm_*` abaixo são custom properties distintas.

### 14.1. Modelo persistido na cena principal

`Scene.btm_standards` → BTM_PG_Standards (`model.py:59–63`):

| Campo | Tipo | Default / domínio | Significado |
|---|---|---|---|
| definitions | Collection[BTM_PG_StandardDefinition] | vazia antes de ensure_ready | Definições do projeto |
| active_index | int | 0, min 0 | Índice da definição ativa |
| schema_version | int | 1 | Formato do modelo de cena; distinto de version por definição |

BTM_PG_StandardDefinition (`model.py:34–56`):

| Campo | Tipo | Default / domínio | Uso |
|---|---|---|---|
| name | string herdada | preenchida por criação | Nome único via API |
| uid | string | vazio; UUID nas cópias/importações | IDs estáveis das embutidas: builtin-br/builtin-us |
| builtin | bool | false | Embutida protegida nos métodos públicos |
| market | enum | BR; BR/US | Defaults do esquema |
| source | enum | USER; BUILTIN/USER/PROMOB_IMPORT/MIGRATED | Proveniência |
| version | int | 1, min 1 | Incrementada por apply_draft com mudança de valor/montagem |
| updated_at | string | vazio | ISO-8601 com timezone local em now_iso |
| values | Collection[StandardValue] | vazia | Valor por chave do esquema, mm ou texto |
| raw_attributes | Collection[RawAttribute] | vazia | Ordem original dos atributos XML |
| assembly | enum | LATERAL; LATERAL/BASE | Montagem da caixa |

BTM_PG_StandardValue (`:20–24`): `name` = chave (ex. COZ.sheets.LAT.thickness), `value: float=0.0` (mm),
`text: string=''`, `is_text: bool=False`; leitura usa text se is_text, value caso contrário.
BTM_PG_RawAttribute (`:27–31`): `attr_id`, `value`, `key`: string vazia; key vazia = não mapeado/inválido,
original permanece disponível para reexportação. CAFF_MONTAGEM fica fora da coleção.

### 14.2. Modelo transitório do Configurador

`WindowManager.btm_standards_draft` → BTM_PG_StandardsDraft (`model.py:101–122`), rascunho do editor:

| Campo | Tipo/default | Callback / função |
|---|---|---|
| definition_uid, definition_name | string vazia | Origem e nome editado |
| values | Collection[StandardValue] | Cópia dos valores |
| tree | Collection[StandardTreeItem] | Árvore achatada, apenas linhas visíveis |
| tree_index | int 0 | activate_tree_row |
| expanded | string vazia | Caminhos abertos separados por `|` |
| search | string vazia, TEXTEDIT_UPDATE | rebuild_tree |
| selected_key | string vazia | Parâmetro em edição |
| edit_text | string vazia | commit_edit_text; medida com unidade/vírgula |
| edit_enum | enum dinâmico | commit_edit_enum; opções do parâmetro ou `-` |
| error | string vazia | Erro do último setter |
| assembly | enum LATERAL/BASE, LATERAL | Copiada para definição no apply |
| include_manual | bool false | Campo existente; seleção moderna usa as duas perguntas |
| _suppress | custom property bool, temporária | Guard contra callbacks; removida em finally |

BTM_PG_StandardTreeItem (`:66–73`): `label: string=''`, `node_type: GROUP/PARAM=GROUP`,
`key: string=''`, `depth: int=0`, `path: string=''` (COZ/CHAPAS/LAT etc.).
Begin_draft não limpa busca, expansão ou seleção anterior; tree_index é limitado na reconstrução.

### 14.3. Metadados e estruturas puras

| Entidade | Campos / contrato | Fonte |
|---|---|---|
| Component, dataclass frozen | code, label_pt, label_en, tree, thickness_class obrigatórios; promob=(), promob_fit=(), visible_sides_br=(1,) | dimension_schema.py |
| Param, dataclass frozen | key,line,group,label_pt,label_en,unit,type,default_br,default_us obrigatórios; min=0,max=0,step=1,precision=1,enum_items=(),zero_meaning='',negative_allowed=False,image_key='',promob_codes=(),legacy_targets=(),component='',field='',description_pt='' | dimension_schema.py |
| ModuleInfo, namedtuple | name, kind, standard_uid, own; sem defaults | apply_core.py:14–15 |
| Plan, namedtuple | follow,differ,not_applicable,legacy: list[str] | apply_core.py:16 |
| Defaults, namedtuple | width,height,depth,z: m; thickness: dict[papel,m]; carcass: m; warning: str ou None | cabinet_defaults.py:18 |
| PromobDocument, dataclass | name obrigatório; version='-1',is_system='False',changed='True',attributes=list nova | io_promob.py:24–29 |

PARAMS: dict[str,Param], 870 entradas; PROMOB_INDEX: dict[str,str], 1.042 códigos → chave;
COMPONENTS: tuple de 20 Component; LINES: COZ/DOR/BAN/SAL/ESC. 17 parâmetros têm legacy_targets.
Folhas do esquema: 5 máximas globais, 65 externas e 800 campos de componente.
ROLE_COMPONENT usa BAS para TOP/BOTTOM, LAT para LEFT/RIGHT e FUN_INF para BACK.
🟡 Semântica externa de ALT_ARM/PROF_ARM é inferida; mapeamento em código é confirmado.

### 14.4. Marcas persistidas e estado interno

| Proprietário / chave | Tipo/default na ausência | Escrita / leitura |
|---|---|---|
| Raiz.btm_overrides | string JSON de lista; leitura → set() sem valor/JSON inválido | add_override ordena nomes, clear_overrides remove |
| Raiz.btm_line | string | COZ frameless, DOR closet quando falta; CAFFMob recebe cab.line |
| Raiz.btm_standard_uid | string vazia | Origem; aplicação grava UID; M-03 só preenche ausentes |
| Cena principal.btm_standards_migrated | int ausente/falso → 1 | Bloqueia M-01/M-02 subsequentes |
| Objeto.IS_FRAMELESS_CABINET_CAGE / IS_CLOSET_STARTER_CAGE | valor truthy | Tags existentes, seleção/override/migração |
| Scene.btm_settings.cut_plan_stale | bool de outro módulo | Sincronização escreve True |
| _SYNC_DEPTH | list[int]=[0] | Profundidade reentrante; finally decrementa |
| _ENUM_ITEMS_CACHE | dict[tuple, list[tuple]] | Referências vivas dos enums |
| previews._collection / _missing | PreviewCollection ou None / set | Cache e aviso único; limpos no unregister |
| operators._LAST_REPORT | dict title='', lines=[] | Relatório da sessão, não salvo no projeto |

`get_overrides` recupera erro JSON de TypeError/ValueError; JSON válido de forma errada não tem validação de lista.
Overrides exprimem nomes de medidas, não seus valores. Fontes: sync.py:22–82, migration.py:21–22.

### 14.5. Contratos de arquivo e relatórios

JSON (`io_json.py:35–115`): schema string, schema_version int=1, uid/name/market/source,
version, updated_at, unit='mm', max_measures dict, lines dict, raw_attributes list de {id,value,key}.
Cada linha tem external/sheets/components; componente tem material/max_width/max_length/thickness e edges[4].
**Assembly não é serializado**. source BUILTIN é exportada USER; importação sempre USER, UID novo,
mercado inválido → BR, completa defaults e não ativa. Nome em conflito → renomeia, ou substitui usuário com
on_conflict='replace'. Estrutura interna/metadados não são inteiramente validados (ver code-analysis §15.9).

XML: raiz DIMENSIONEXPORT VERSION; DEFINITION DESCRIPTION/ISSYSTEM/CHANGED; ATTRIBUTE ID/VALUE.
PromobDocument.attributes guarda list[tuple[str,str]] na ordem. Conversão → {name,values,raw_attributes,
report,assembly}; `report`: total, mapped (ocorrências), unrecognized/invalid/duplicates/
confirmed_without_equivalent (listas de IDs), assembly_warning (None/string). Fixture: total 692,
mapped 335, unrecognized 357, values 294. CAFF_MONTAGEM válido é LATERAL/BASE; inválido → LATERAL + aviso.

Relatório sync (`sync.py:282–291`): definition string, modules_updated/caffmob/frameless/closets int,
targets_written list[str], skipped_manual list[tuple[nome,medida]], without_target list[str].
Apply_draft acrescenta changes: list[dict(key,label,old,new)] com valores formatados string;
assembly usa rótulos. without_target mede falta de destino **legado**, sem concluir que campo não tenha uso.

### 14.6. Operadores e parâmetros

Namespace real: `caffmob.standards_*` (mantido na análise, sem renomear).
Configurator, Apply, Duplicate e Report não declaram campos de operador.
SetActive: definition enum dinâmico dos UIDs; Rename: name string vazia; Delete sem campos.
ExportJSON/ImportJSON: filename_ext .btmdim.json, filter_glob *.btmdim.json;*.json;
ImportPromob: .xml, *.xml;*.dimensionExport; ExportPromob: .xml, *.xml. Filepath vem dos helpers.
ApplyScene: previous_uid string vazia, apply_differ bool false, interactive bool false, HIDDEN/SKIP_SAVE;
ApplyDiffer: previous_uid string vazia, HIDDEN/SKIP_SAVE. Fonte: operators/ops_standards.py.

🔴 **LACUNA:** integração RNA/undo e round-trip no aplicativo Promob não foram executados nesta escavação.


## 15. Módulo `legacy`

🟢 **CONFIRMADO**, fontes legacy/*.py, 2026-10-10. Comprimentos em metros; sem PropertyGroup próprio de domínio.

| Entidade | Campos e defaults | Persistência |
|---|---|---|
| LegacyCabinet (dataclass) | library,cabinet_type,width,height,depth obrigatórios; line=''; openings=list nova; shelves=0; other_fronts=list nova | DTO de leitura em memória |
| LegacyOpening (namedtuple) | front obrigatório; drawer_count=0; shelves=0 | Em memória |
| Loss | key,count obrigatórios | Em memória e texto de relatório |
| Result | legacy_name,library,module_name,losses | Resultado de conversão em memória |
| Reading | name,library,cabinet,box,world,parent,collection,aggregates | Referências transitórias bpy; world é cópia |
| marker JSON | schema-version=1 na escrita; offered bool=false na ausência; converted list[str]=[] | modules_root/legacy_groups.json |

Campos traduzidos: cabinet_type BASE/WALL/TALL, width/height/depth m, door_swing NONE/LEFT/RIGHT/DOUBLE/FLIP, shelves int somado, line COZ/DOR/BAN/SAL/ESC, assembly LATERAL. Construção integrada substitui assembly pelo padrão ativo, grava btm_line e btm_standard_uid via builder.

Loss.key: TYPE_APPROX,DRAWERS,PANEL,SPECIAL,EXTRA_DOORS; integração acrescenta AGGREGATES a LOSS_LABELS. TALL_FROM=1.2 m. LEGACY_LIBRARIES=frozenset FRAMELESS/FACE_FRAME/CLOSETS. NEUTRAL_TAB=FRAMELESS; NEUTRAL_MODES são triplas grupo/propriedade/valor.

Configuração externa: preferences.show_legacy_libraries bool; Scene.home_builder.product_tab, hb_frameless.frameless_selection_mode, hb_face_frame.face_frame_selection_mode, hb_closets.closet_selection_mode. Marcas de leitura: CABINET_TYPE, btm_line, IS_FACE_FRAME_OPENING_CAGE; frentes especiais vêm de face_frame_opening.front_type.

Estado de grupos: TARGET_CATEGORY='Geral', MARKER_FILE='legacy_groups.json', _offer_cache=[None] (triestado), _DATA_KINDS=(objects,meshes,materials,node_groups,images,curves,collections,textures,lights,cameras,actions). _snapshot é dict[str,set[data-block]]. convert_group retorna (list[str],list[str],str|None); convert_pending retorna (list[str],list[str]). Parse de marker valida offered e converted, mas ignora schema-version.

Operadores: caffmob.legacy_convert REGISTER/UNDO com only_active bool=false, SKIP_SAVE; caffmob.legacy_groups_convert REGISTER sem campos RNA. notify_legacy timer retorna None. Handler on_load_post é persistent.

🔴 **LACUNA**: cancelamento/undo e preservação da cena durante limpeza de grupos não foram exercitados no Blender nesta sessão.


## 16. Módulo `library_panel`

🟢 **CONFIRMADO**, library_panel/*.py e data/library_models.json.

| Entidade | Campos/defaults | Persistência |
|---|---|---|
| BTM_PG_LibraryState | open bool=false; category string=''; line string='COZ' | WindowManager.btm_library, estado de sessão |
| Category | name str,line COZ/DOR/BAN/SAL/ESC,fixed bool, sem defaults | Fixas do pacote ou categories.json |
| Layout | label=(x,y,w,h),items=list[(key,rect)] | Cache por região |
| Model | id,label,cabinet_type,width_mm,door_swing,shelves | data/library_models.json |
| categories.json | schema-version=1, categories=[{name,line}] | modules_root; pasta por categoria |
| library_models.json | schema-version=1, models=[{id,label,cabinet_type,width_mm,door_swing,shelves}] | Pacote, 5 modelos |

width_mm=0 significa largura default; largura negativa vira zero no parse; shelves negativo vira zero; não há teto no parser. Linhas fixas: Cozinha/COZ, Banheiro/BAN, Sala/SAL, Home office/ESC; DEFAULT_LINE COZ. Modelos de porta têm shelves=1, torre=4.

Caches: categories._cache=[None] ou [(categorias,avisos)]; draw._handle=[None] ou handle; draw._mouse={'pos':(-1,-1),'region':0}; draw._cache dict de ponteiro→(chave,Layout); ops_click._addon_keymaps list[(keymap,item)]; popover._open={'category':'','drawn':0}. Nenhum é contrato persistente de domínio.

Layout constants: FONT_SIZE=11; MARGIN_X=8,MARGIN_Y=12,GAP=8,ROW_HEIGHT=24,ROW_GAP=2,PAD_X=12. Chaves de menu LABEL,CREATE_CABINET,CREATE_CATEGORY,CONVERT_GROUPS,CAT:<nome>. BIBLIOTECA CAFFMOB é nome próprio sem tradução.

Operadores caffmob.*: library_click/library_hover/library_close INTERNAL; library_category_create name string,line enum COZ; library_category_set_line category string,line enum COZ (ambos REGISTER); library_insert_model model_id string,line string COZ (REGISTER/UNDO); library_create_cabinet cabinet_type BASE/WALL/TALL=BASE,width m=0.8 faixa 0.1–3.0,assembly LATERAL/BASE=LATERAL,line enum=COZ,open_editor bool=true HIDDEN/SKIP_SAVE (REGISTER/UNDO).

🔴 **LACUNA**: RNA/caches de regiões e múltiplos popovers não exercitados nesta sessão.


## 17. Módulo `object_library`

🟢 **CONFIRMADO**, object_library/*.py, 2026-10-10.

| Entidade | Campos/defaults | Persistência |
|---|---|---|
| Entry dataclass | item_id,name,category,root obrigatórios; source/author/license/created_at/addon_version=''; size_mm lista nova [0,0,0]; features/materials listas novas | JSON |
| Item dataclass | entry,user,blend,manifest obrigatórios; thumb=None | Resultado de scan/save |
| BTM_PG_ObjectItem | is_item=false,item_id='',category=OTHER,source='',license='' | Object.btm_object_item |
| BTM_PG_ObjectLibraryUI | category=DOORS,search='' TEXTEDIT_UPDATE | WindowManager.btm_object_library (sessão) |

Manifesto: format='caffmob_draw.object_item',version=1; campos da Entry. Entry.size_mm dimensões world X/Y/Z em mm, arredondadas na escrita; parser não exige exatamente três. ID lowercase alfanumérico com hífens; default de categoria OTHER para desconhecida. FEATURES ordenadas GROUP,FRAME,LEAF_SWING,LEAF_SLIDE,AGGREGATE,PRODUCTION_PART,TEXTURED. CATEGORIES: DOORS/WINDOWS/COOKTOPS/TABLES/SEATING/DECOR/OTHER. Arquivos categoria/id.blend,json,png; thumbnail opcional; delete inclui blend1. Item.key='U:categoria:id' ou 'B:categoria:id'.

Materiais de imagem: custom properties Material.btm_texture_path string absoluto, btm_texture_size_mm float; node Mapping scale=1/max(mm/1000,0.0001), projeção BOX com blend 0.2. State retexture._names_cache dict nome→caminho; previews._collection=[None] ou PreviewCollection, chave path:int(mtime).

Operadores caffmob.*: object_insert key string HIDDEN (REGISTER/UNDO), modal mantém _root,_loaded,_name,_plane_z; object_library_remove key string HIDDEN (REGISTER); object_library_add name='Meu objeto',category=OTHER,source='Uso próprio',license_text='Uso próprio',author='',filepath='',duplicate RENAME/REPLACE=RENAME (REGISTER/UNDO). object_retexture_finish finish enum dinâmico,scope PART/ITEM=PART; object_retexture_image filepath do ImportHelper,filter_glob, size_mm=600 faixa 1–100000,scope PART/ITEM=PART (ambos REGISTER/UNDO).

Root é grupo/item; outras marcas btm_group/btm_aggregate permanecem nos filhos. Não confundir is_item com módulo CAFFMob: padrão de dimensões classifica item não paramétrico como OTHER. Fonte: standards/sync.py:191–222.

🔴 **LACUNA**: relações RNA após append/undo não foram validadas em runtime.


## 18. Módulo `inspection`

🟢 **CONFIRMADO**, inspection/*.py e adapters/*.py.

| Entidade | Campos/contrato | Persistência |
|---|---|---|
| Front | kind,module_root,obj,key; library por subclasse | Wrapper transitório de RNA |
| BTM_PG_InspectionState | active=false,snap_stops=true,default_angle enum 90/45='90',interferences coleção,interference_index=0,checked_fronts=-1 | WindowManager.btm_inspection, sessão |
| BTM_PG_Interference | front_name,module_name,hit_name strings; location vector3 mundo; kind enum DOOR/FLIP_UP/FLIP_DOWN/DRAWER/PULLOUT=DOOR | Coleção transitória |
| Leaf namedtuple | side,hinge_x,hinge_y,dx,dy,length,thickness,height,rot_sign | Matemática ambiente |
| Tween dict | front,start,target,open,t0 perf_counter | _active._tweens por front.key |
| _Targets | depsgraph,items[(obj,AABB,root)],_bvh por ponteiro,_verts por ponteiro | Uma checagem |

Graus para HINGED; fração [0,1] drawer/pullout; common MAX_ANGLE=90, SNAP_STOPS=(0,45,90), tolerância 5 graus; teto face_frame=100,closets=110,BTM=90. Folha convertida usa agg.max_angle. Poses são Euler radians + delta_location m; hinge frame ponto/eixo/ref mundo.

Persistência por adaptador: frameless obj.btm_open (custom property, remove fechada); face_frame opening.face_frame_opening.swing_percent; closets hb_door_open/hb_drawer_open e marcas hb_hinge/hb_slide_dist/hb_drawer_index; BTM Controller.location.y e raiz.btm_open; ambiente raiz.btm_open, Empty.btm_room_door_pivot='L'/'R', folha.btm_room_door_leaf=true; agregado btm_aggregate.open_value fração.

ROOM Leaf: uma/duas folhas, espaço da porta; size em m, rot_sign ±1; pares ensure_leaves (Leaf,pivot). BTM Controller curso 0.2 m; frameless fallback drawer 0.4 m. Interference: STEP_DEGREES=15,TOLERANCE=0.001 m, _SKIP_DISPLAY WIRE/BOUNDS; resultado dict front,module string,hit Object,location Vector,kind string.

Estados globais: ops_inspect._active=None; timer 60 Hz e ANIM_DURATION=0.35; gizmo._state={front:None,pending:None,pointer:0}; save_guard._reopen list[(scene_name,key,value)]; overlay._handles list de handlers. Chaves de Front: FRAMELESS:<obj>,FACE_FRAME:<opening>,CLOSETS:<obj>,BTM:<module>,ROOM:<door>,LEAF:<obj>. São baseadas em nome, não UUID estável após rename.

Operadores caffmob.fronts_set_open scope ALL/SELECTED/ACTIVE_MODULE=ALL,mode CLOSE/OPEN_45/OPEN_90=OPEN_90; inspect_fronts sem props RNA; check_front_interference scope ALL/SELECTED=ALL; interference_goto index int=0 min0. Todos REGISTER sem UNDO, decisão existente de tratar abertura como inspeção. Gizmo BTM_GGT_front_open bl_options 3D/PERSISTENT.

🔴 **LACUNAS**: RNA/save/undo/BVH e pending ao trocar frente não testados no Blender nesta sessão.


## 19. Módulo `molding`

🟢 **CONFIRMADO** — `molding/adapters.py`, `engine.py`, `packages.py`, `ops.py`; opções em `hb_props.py`.

| Estrutura/campo | Tipo / padrão | Contrato |
|---|---|---|
| FACTS | dict[id(Object), dict] | Efêmero; identidade Python, não persistência |
| role | CABINET / APPLIANCE | Appliance produz vãos ignorados |
| corner | dict opcional ou None | ld/rd: profundidades laterais em m; diagonal: bool |
| kick | dict | skip, setback, montantes/medidas de extremidade |
| crown_mount | dict opcional | rail_width, door_overlay |
| finished_left/right | bool | Controlam retornos traseiros |
| stack | lista de tuplas | profile_ref, fallback_key, dx, dy; sentinelas antes da resolução |
| segmento de rodapé | pontos + classificação | FRONT / RECESS / SKIP |
| sweep tags | custom properties | IS_HB_MOLDING_SWEEP, HB_MOLDING_TYPE, HB_MOLDING_MEMBERS |
| perfil tag | bool | IS_HB_MOLDING_PROFILE; oculto para viewport/render |
| tipo | enum | CROWN / CAP / BASE / LIGHT_RAIL |
| molduras da cena | enums dinâmicos | NONE / pacotes disponíveis; overrides DEFAULT |
| base_include_recessed | bool, false | Habilita spans RECESS |
| crown_reveal | float, 0,015875 m, ≥ 0 | Reveal acima da porta |
| stack_offset | float, 0,0889 m, ≥ 0 | Deslocamento da coroa empilhada |
| crown_furniture_cap | bool, false | Capa independente |
| cap_offset | float, 0 m | Limites soft de ±6 polegadas; sem restrição hard |
| base_shoe | bool, false | Complemento independente do rodapé |
| caches de perfis | dict em memória | Enum e altura/profundidade; limpos ao registrar caminho |

Dimensões internas em metros; polegadas convertidas nos defaults e nos contornos fallback. Sweeps dependem do primeiro armário da cadeia; não há entidade de moldura com identidade própria ou serialização de sua topologia.


## 20. Módulo `geometry_free`

🟢 **CONFIRMADO** — `geometry_free/props.py`, `mesh.py`, `ops_create.py`, `ops_edit.py`, `cutting/part_sources.py`.

| Campo/estrutura | Tipo / padrão | Regra |
|---|---|---|
| Object.btm_geometry | PointerProperty | Grupo de parâmetros persistido no blend |
| kind | enum PLACA | PLACA / CAIXA |
| plane | enum XY | XY / XZ / YZ; efetivo para placas |
| width | float 0,6 m | 0,001…10; reconstrói malha |
| depth / height | float 0,4 m | 0,001…10; reconstrói malha |
| thickness | float 0,018 m | 0,001…10; reconstrói malha |
| fabrication | bool false | Entrada optativa na produção |
| component | enum ESP | Códigos de dimension_schema |
| material / finish | string MDF / vazio | Não alteram malha |
| btm_plane.object_kind | GEOMETRY | Identificação funcional |
| IS_BTM_GEOMETRY | bool true | Tag auxiliar criada com objeto |
| HB_CURRENT_DRAW_OBJ | bool temporário | Removido ao confirmar |
| btm_uid | identidade persistida | Removido da cópia para regeneração |
| btm_mirrored | bool alternado | Não representa uma escala negativa |
| step | int 0/1/2 | Origem, dimensões no chão, altura |
| corner / typed / typed_width | Vector / str / float ou None | Estado efêmero modal |
| sheet | tuple(nome, comprimento, largura, espessura) | Metros; 1 ou 6 por objeto |
| PartRecord | dados produtivos | source FREE_GEOMETRY; module_uid None; dimensões mm |

Não há entidade independente por chapa visual: os seis registros de fabricação derivam de um único objeto sólido. Alterações de propriedades refazem a malha, não preservam edições manuais dos vértices.
