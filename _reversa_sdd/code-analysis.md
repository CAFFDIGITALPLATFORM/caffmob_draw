# Análise de Código — BlenderToMob

Este documento apresenta a análise técnica aprofundada da estrutura, lógica e algoritmos do add-on **BlenderToMob**, conduzida pelo agente **Archaeologist** na fase de Escavação.

---

## 1. Dicionário de Dados do Sistema

O add-on registra propriedades customizadas em tipos internos do Blender (usando a API `bpy.props`). A tabela abaixo cataloga a estrutura de dados paramétrica utilizada na cena.

### 1.1 Parâmetros de Parede (`BTM_PG_WallSegment`)
Registrado em `bpy.types.Object.btm_wall`. Controla a geometria paramétrica das paredes.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `length` | Float | Comprimento do segmento de parede em milímetros | 2000.0 (10.0 a 100000.0) | 🟢 CONFIRMADO |
| `absolute_angle`| Float | Ângulo do segmento em relação ao sistema global | 0.0° (-360.0° a 360.0°) | 🟢 CONFIRMADO |
| `relative_angle`| Float | Ângulo em relação ao segmento anterior da polilinha | 0.0° (-360.0° a 360.0°) | 🟢 CONFIRMADO |
| `thickness` | Float | Espessura da parede em milímetros | 150.0 (10.0 a 2000.0) | 🟢 CONFIRMADO |
| `height_start` | Float | Altura da parede no ponto inicial (Pé-Direito) | 2700.0 (100.0 a 10000.0) | 🟢 CONFIRMADO |
| `height_end` | Float | Altura da parede no ponto final | 2700.0 (100.0 a 10000.0) | 🟢 CONFIRMADO |
| `offset` | Float | Afastamento vertical da base da parede em relação ao piso | 0.0 mm | 🟢 CONFIRMADO |
| `sagitta` | Float | Flecha do arco para paredes curvas (0 para retas) | 0.0 mm | 🟢 CONFIRMADO |
| `linear_increment`| Float| Passo do salto do cursor durante a construção do comprimento | 50.0 mm (1.0 a 1000.0) | 🟢 CONFIRMADO |
| `angular_increment`| Float| Passo do salto do ângulo ao mover o mouse | 5.0° (0.5° a 90.0°) | 🟢 CONFIRMADO |
| `orientation` | Enum | Lado da parede que recebe o comprimento (`RIGHT` / `LEFT`) | `RIGHT` | 🟢 CONFIRMADO |
| `wall_type` | Enum | Estilo e material da parede (`NORMAL` / `DRYWALL` / `GLASS`) | `NORMAL` | 🟢 CONFIRMADO |
| `use_as_default`| Bool | Salvar as propriedades atuais como padrão para novas paredes | `False` | 🟢 CONFIRMADO |

### 1.2 Parâmetros de Plano de Inserção (`BTM_PG_InsertionPlane`)
Registrado em `bpy.types.Object.btm_plane`. Mapeia o tipo de entidade CAD do objeto na hierarquia espacial.

| Propriedade | Tipo | Descrição | Valores Possíveis | Certeza |
|-------------|------|-----------|-------------------|----------|
| `object_kind` | Enum | Tipo de elemento de ambiente | `WALL`, `FLOOR`, `MODULE`, `GEOMETRY`, `OPENING` | 🟢 CONFIRMADO |
| `parent_plane`| Pointer | Referência ao objeto hospedeiro | `bpy.types.Object` | 🟢 CONFIRMADO |
| `layer_id` | String | ID da camada (Camada do Promob para isolamento) | `"Default"` | 🟢 CONFIRMADO |
| `collision_override`| Enum| Controle de colisão específico do objeto | `INHERIT` (padrão), `ON`, `OFF` | 🟢 CONFIRMADO |

### 1.3 Parâmetros de Abertura (`BTM_PG_OpeningProperties`)
Registrado em `bpy.types.Object.btm_opening`. Utilizado para portas e janelas que realizam corte boolean nas paredes.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `opening_type` | Enum | Tipo de abertura de vão (`DOOR` / `WINDOW`) | `DOOR` | 🟢 CONFIRMADO |
| `width` | Float | Largura útil da abertura em milímetros | 800.0 (100.0 a 5000.0) | 🟢 CONFIRMADO |
| `height` | Float | Altura útil da abertura em milímetros | 2100.0 (100.0 a 5000.0) | 🟢 CONFIRMADO |
| `sill_height` | Float | Altura do peitoril a partir da base (0.0 para portas) | 0.0 (0.0 a 5000.0) | 🟢 CONFIRMADO |
| `parent_wall` | Pointer | Referência ao objeto de parede que hospeda o vão | `bpy.types.Object` | 🟢 CONFIRMADO |

### 1.4 Parâmetros de Módulos de Mobiliário (`BTM_PG_CabinetProperties`)
Registrado em `bpy.types.Object.btm_cabinet`. Controla as dimensões da caixa estrutural de MDF/MDP.

| Propriedade | Tipo | Descrição | Padrão / Limites | Certeza |
|-------------|------|-----------|-------------------|----------|
| `width` | Float | Largura total do módulo (mm) | 800.0 (100.0 a 3000.0) | 🟢 CONFIRMADO |
| `height` | Float | Altura total do módulo (mm) | 700.0 (100.0 a 3000.0) | 🟢 CONFIRMADO |
| `depth` | Float | Profundidade total do módulo (mm) | 550.0 (100.0 a 2000.0) | 🟢 CONFIRMADO |
| `thickness` | Float | Espessura das chapas de MDF (laterais/base/topo) | 18.0 mm (6.0 a 50.0) | 🟢 CONFIRMADO |
| `cabinet_type` | Enum | Categoria do módulo (`BASE` / `WALL` / `TALL`) | `BASE` | 🟢 CONFIRMADO |

---

## 2. Fluxo de Controle e Interações

### 2.1 Construtor de Parede Modal (`BTM_OT_WallBuilder`)
Este operador implementa uma máquina de estado modal para a modelagem interativa de polilinhas de paredes no plano:

```
[Iniciar Operador] ──> [Aguardar Clique no Piso (Z=0)] 
                             │
                             ▼
                    [Registrar Início]
                             │
                             ▼
     ┌───────────> [Aguardar Input do Mouse/Teclado] <──────────┐
     │                       │                                  │
     │                       ├─> [MOUSEMOVE] ──> Atualiza preview/snap
     │                       │
     │                       ├─> [Dígito 0-9] ─> Adiciona ao buffer numérico
     │                       │
     │                       ├─> [TAB] ────────> Alterna campo ativo (Length/Angle)
     │                       │
     │                       ├─> [ENTER] ──────> _confirm_segment()
     │                       │                     │
     │                       │                     ├─> Fecha loop? ─> [Finaliza e reconstrói]
     │                       │                     └─> Continua? ───> Salva segmento e move origem
     │                       │
     │                       └─> [RMB / ESC] ──> [Cancela / Limpa Tudo]
```

### 2.2 Inserção de Aberturas com Snapping (`BTM_OT_InsertOpening`)
Implementa o comportamento interativo de arrasto e deslizamento de portas e janelas nas paredes:
1. **Ativação**: O operador é invocado abrindo uma janela de propriedades iniciais (Largura/Altura/Peitoril).
2. **Ciclo Modal**:
   - **Mapeamento Tridimensional**: Realiza raycast a partir da posição 2D do cursor no plano de projeção 3D do Blender.
   - **Cálculo da Distância de Snapping**: Projeta a coordenada de impacto em todos os segmentos das paredes existentes na cena (usando o algoritmo de menor distância ponto-segmento 2D).
   - **Transição Automática**: Se a distância até um segmento adjacente se torna menor do que a do segmento atual (ex: ao contornar quinas), a abertura altera seu pai para o novo segmento de parede, adotando instantaneamente sua rotação, espessura e direção.
   - **Movimentação Travada**: A abertura é travada localmente nos eixos X (comprimento) e Z (altura do peitoril). Não é possível arrastá-la para fora da parede.
   - **Cálculo de Cotas Visuais**: Calcula as distâncias do centro do preview até o início ($d_1$) e o fim ($d_2$) do segmento ativo e renderiza como linhas de extensão e dimensões em tempo real.
   - **Confirmação**: Cria o objeto cortador (`BTM_Porta_Cut` / `BTM_Janela_Cut`), realiza o parentesco e aplica o modificador `Boolean` em modo de diferença exata na parede-alvo.

---

## 3. Algoritmos Relevantes

### 3.1 Geração de Piso a partir do Contorno das Paredes (`_convex_hull_2d`)
Para ajustar o piso automaticamente, o sistema utiliza o algoritmo de **Graham Scan** para encontrar o fecho convexo dos vértices inferiores das paredes:
1. Encontra o ponto com menor coordenada Y (e menor X em caso de empate) como ponto inicial.
2. Ordena os demais pontos pelo ângulo polar em relação ao ponto inicial.
3. Filtra pontos duplicados ou excessivamente próximos.
4. Percorre os pontos ordenados mantendo uma pilha (hull) de vértices. Para cada ponto, realiza o produto vetorial 2D (cruzamento) para garantir que a curva continue no sentido anti-horário (ângulo à esquerda). Se o produto for $\le 0$, remove o topo da pilha (curva à direita/colinear).
5. Cria a malha poligonal plana conectando os vértices finais do fecho convexo em um único loop fechado.

### 3.2 Otimização de Plano de Corte (`optimize_nesting`)
Para planejar a produção do mobiliário na chapa de MDF de $2750 \times 1830$ mm, o add-on implementa um otimizador de nesting 2D baseado em **Guilhotina Híbrida com Shelf-Packing (Next-Fit Decreasing)**:
- **Pré-filtragem**: Verifica se cada peça cabe no espaço útil descontando a margem de refilo (padrão 10mm).
- **Ordenação**: Ordena todas as peças por área de corte decrescente.
- **Shelf Packing**:
  - Tenta colocar a peça nas prateleiras (shelves) existentes das chapas ativas, respeitando o sentido da fibra de madeira (grain direction). Se a rotação violar a fibra horizontal/vertical, ela é descartada.
  - Se a peça cabe em uma prateleira, ela é colocada adjacente às outras. O espaçamento da serra (kerf, padrão 4mm) é adicionado após cada peça.
  - Se a prateleira cresce em altura, a altura da prateleira é reajustada e a altura restante da chapa é reduzida.
  - Se não couber em nenhuma prateleira de nenhuma chapa existente, cria uma nova prateleira na chapa que possuir espaço vertical suficiente.
  - Se nenhuma chapa existente tiver espaço vertical, inicializa uma nova chapa de MDF e inicia uma prateleira com a peça.
- **Métricas**: Retorna a eficiência percentual de aproveitamento das chapas, número de chapas utilizadas e a lista de coordenadas exatas $(x, y)$ de cada peça.

---

# Re-extração 2026-10 (Fase 2c): módulos do ciclo forward

> As seções abaixo foram acrescentadas em 2026-10-10 pelo Archaeologist. Cobrem módulos criados pelas features 001 a
> 013 depois da extração de 2026-07. As seções 1 a 3 acima continuam válidas para `data`, `geometry`, `operators`,
> `overlays`, `ui` e `cutting`.

## 4. Módulo `canvas2d` (`caffmob_draw/canvas2d/`)

Núcleo das telas 2D próprias do add-on (Editor de Paredes, Editor de Armário, diálogo do "Mover Sobre"). Nasceu na
feature 002 e cresceu nas 004 e 013. Quatro arquivos, 392 linhas, duas camadas bem separadas:

| Arquivo | Camada | `bpy`? | Papel |
|---------|--------|--------|-------|
| `view.py` (106 l.) | núcleo puro | não | `View2D`: mundo 2D (metros) ↔ pixels; pan, zoom ancorado, enquadrar, grade, encaixe ortogonal, distâncias |
| `gestures.py` (41 l.) | núcleo puro | não | Fator de zoom da pinça e da roda; retângulo do zoom janela (013) |
| `draw.py` (117 l.) | interface | sim (`gpu`, `blf`) | Primitivas em pixels e no mundo 2D sobre `hb_gpu_draw.py`; paleta `COLORS`; texto traduzido |
| `window.py` (128 l.) | integração Blender | sim | Janela 2D própria: duplica a área 3D, vira Image Editor sem imagem, painel lateral na aba do editor, fechamento por timer |

Dependentes (🟢, por `grep`): `walls2d/ops_editor.py`, `walls2d/window.py`, `walls2d/direction.py`, `cabinet_editor/
window.py`, `move_over/ops_dialog.py`, `move_over/ops_drag.py`, `move_over/align.py`, `overlays/element_toast.py`,
`data/i18n.py`. Dependências do módulo: `hb_gpu_draw.py`, `compat.get_builtin_shader`, `data/units.py`, `data/i18n.py`.

### 4.1 `View2D` (`view.py`) 🟢

Estado: `rect = (x, y, largura, altura)` em px com origem embaixo à esquerda (convenção do `POST_PIXEL`), `scale` em
pixels por metro (padrão 100) e `center`, o ponto do mundo no centro do retângulo.

- `to_screen(point)` = `(x + w/2 + (px − cx)·scale, y + h/2 + (py − cy)·scale)`; `to_world(pixel)` é a inversa exata.
- `pan(dx_px, dy_px)`: desloca `center` em `−d/scale` (o conteúdo segue o mouse).
- `zoom(factor, anchor_px=None)`: multiplica `scale` (piso técnico `1e-6`); com âncora, recalcula `center` para que o
  ponto do mundo sob `anchor_px` continue no mesmo pixel: `center += before − after`. Sem limite superior de escala
  (decisão da 013, esclarecimento Q1).
- `fit(bounds, margin=0.1)`: `scale = min(w / w_mundo, h / h_mundo)` com `w_mundo = (x1−x0)·(1+2·margin)` (mínimo
  `1e-6` para bounds degenerados); `center` no centro dos bounds. O lado que limita cabe inteiro.
- `grid_lines(step)`: linhas verticais e horizontais visíveis em múltiplos de `step`; devolve vazio se `step ≤ 0` ou
  se extensão/passo > 400 num eixo (grade densa demais; até ~402 linhas ainda passam) _(Revisão cruzada 2026-10-10:
  view.py:64)_.
- Funções soltas: `snap_to_grid(point, step)` (arredonda ao múltiplo); `ortho_snap(origin, point, tol=2,5°)` encaixa
  em 0/90/180/270° quando o ângulo está a até `ORTHO_TOLERANCE_DEG`, devolvendo `(ponto, travado)`;
  `distance_point_point`; `distance_point_segment` (projeção com `t` em [0, 1]).

### 4.2 Gestos (`gestures.py`, feature 013) 🟢

- `PINCH_SENSITIVITY = 1/150`, `WHEEL_STEP = 1.15`, `ZOOM_WINDOW_MIN_PX = 5`.
- `pinch_factor(delta)` = `exp(delta · sensibilidade)`: exponencial, logo simétrico (ida e volta devolvem a escala) e
  independente da escala de partida; delta 0 → fator 1. Sinal: `delta > 0` aproxima.
- `wheel_factor(up, inverted)` = `WHEEL_STEP` quando `up != inverted`, senão `1/WHEEL_STEP`: a roda obedece à
  preferência do Blender "inverter zoom pela roda".
- `zoom_window_bounds(view, p0, p1, min_px)`: `None` se algum lado do retângulo em px tem menos de `min_px`; senão os
  bounds do mundo ordenados (`min`/`max` por eixo), prontos para `View2D.fit(bounds, margin=0)`.
- A leitura do delta no `Event` fica fora deste módulo, em `compat.trackpad_delta` / `compat.pinch_delta`
  (`−(dx + dy)`, convenção do Blender para o gesto Magnify; sinal 🟡 até a prova à mão, ver
  `_reversa_forward/013-touchpad-editor-parede/investigation.md` §6).

### 4.3 Desenho (`draw.py`) 🟢

- `begin()` liga `gpu.state.blend_set('ALPHA')` e devolve o shader `UNIFORM_COLOR` (via `compat.get_builtin_shader`);
  `end()` desliga o blend. Todo desenho de uma tela 2D fica entre os dois.
- Pixels: `rect`, `outline`, `lines` (pares de pontos), `dashed(p0, p1, dash=6, gap=4)` (gera os pares de uma linha
  tracejada), `text` (traduz com `tr` antes de desenhar; o catálogo tem o texto do código como chave), `text_width`,
  `button(sh, r, label, hot, primary)` (fundo por estado, contorno, texto centrado com `vcenter_baseline`).
- Mundo 2D: `box(sh, view, lo, hi, color, fill)` e `segment(sh, view, p0, p1, color, dashed_line)` convertem por
  `View2D.to_screen` e desenham em pixels.
- `COLORS`: paleta RGBA da interface 2D (`panel`, `pane`, `border`, `text`, `muted`, `reference` = azul "B",
  `moving` = laranja "A", `target`, `target_hot`, `warning`, `button`, `button_hot`, `button_primary`). `FONT = 0`,
  `FONT_SIZE = 12`. `length_label(m)` formata na unidade do usuário (`data/units.format_value`).

### 4.4 Janela própria (`window.py`) 🟢

Extraída de `walls2d/window.py` na 004 para servir também ao Editor de Armário. Opera sobre a **sessão** do editor
(`s.window_ptr`, `s.area_ptr`, `s.restore_area_type`), identificando janela e área por `as_pointer()`.

- `open_window(context, s, msg)`: se o contexto está numa área 3D, duplica a área (`screen.area_dupli`,
  `INVOKE_DEFAULT`) e pega a maior área da janela nova; se não conseguiu, usa a própria área atual e guarda
  `restore_area_type` para devolvê-la ao fechar; sem área nem janela, `RuntimeError(msg)`. Chama `prepare(area)`.
- `prepare(area)`: `area.type = 'IMAGE_EDITOR'`, `image = None`, mostra só a região lateral (N); esconde barra de
  ferramentas, cabeçalho de ferramenta, menus e cabeçalho (View/New/Open). Devolve a região `WINDOW`. É por isso que a
  013 desenha a barra superior em GPU em vez de reativar o cabeçalho.
- `focus_tab(area, category)`: põe a região lateral na aba do editor; só funciona depois do primeiro desenho da região
  (o Editor de Paredes tenta por timer até conseguir).
- `editor_area(context, s)`, `is_editor_area`, `window_alive`: localizam a área do editor pelo ponteiro.
- `side_panel`, `over_side_panel(area, mx, my)`, `visible_width(area, region)`: tratam a sobreposição de regiões
  (padrão do Blender): o painel lateral fica por cima do desenho, então o modal deixa passar eventos sobre ele e a
  largura útil do desenho desconta o painel quando ele invade a região.
- `close_later(...)`: fecha num `bpy.app.timers` (50 ms) **fora** do modal que roda na janela. `_close`: se havia
  `restore_area_type`, devolve menus, cabeçalho e tipo; senão fecha a janela (`wm.window_close`) se houver mais de
  uma, com fallback para `area.type = 'VIEW_3D'` em `RuntimeError`.

### 4.5 Regras embutidas e constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `ORTHO_TOLERANCE_DEG` | 2,5° | `view.py` | Tolerância da trava ortogonal |
| piso de `scale` | `1e-6` px/m | `view.py` | Único limite de zoom (não há teto) |
| limite da grade | extensão/passo > 400 num eixo | `view.py:64` | Acima disso a grade não é desenhada (até ~402 linhas passam) _(Revisão cruzada 2026-10-10: view.py:64)_ |
| `PINCH_SENSITIVITY` | 1/150 | `gestures.py:17` | Sensibilidade da pinça; o código a dá como "calibrado na prova D-02" (o sinal da pinça segue 🔴 em canvas2d/walls2d) _(Revisão cruzada 2026-10-10: gestures.py:17)_ |
| `WHEEL_STEP` | 1,15 | `gestures.py` | Passo da roda |
| `ZOOM_WINDOW_MIN_PX` | 5 px | `gestures.py` | Lado mínimo do zoom janela |
| `dash`/`gap` | 6/4 px | `draw.py` | Padrão do tracejado |
| atraso do fechamento | 50 ms | `window.py` | Timer de `close_later` |

Tratamento de erros: `RuntimeError` em `area_dupli` e `window_close` é engolido com fallback; `TypeError/
AttributeError/ValueError` ao trocar a aba devolvem `False`. Nenhum log.

Testes puros: `tests/test_canvas2d_view.py`, `tests/test_canvas2d_gestures.py`.

## 5. Módulo `walls2d` (`caffmob_draw/walls2d/`)

Editor de Paredes 2D (features 002, 009, 013 e correções BUG-20261007-ZZUK/VQ72/YIMY): planta vista de cima onde o
projetista desenha e edita as paredes do Home Builder 5 como rascunho; nada muda no 3D até o OK. 13 arquivos, 2.497
linhas, em três camadas (Princípio IV):

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `model.py` (351), `history.py` (58), `inference.py` (43), `direction.py` (47), `heights.py` (30), `convert.py` (49) | não | Rascunho (cadeias, trechos, faces), desfazer, mira, direção do lápis, pé-direito, conversão de paredes da camada nova |
| Ponte Blender ↔ modelo | `scene_io.py` (136), `apply.py` (262), `props.py` (352) | sim | Ler as paredes da cena para o modelo, gravar o modelo nas paredes, sessão e campos virtuais do painel |
| Interface | `ops_editor.py` (944), `panels.py` (140), `window.py` (60) | sim | Operadores (abrir, modal, OK, Cancelar, Enquadrar), desenho GPU da planta, painéis da região lateral, janela |

Dependências: `canvas2d` (vista, desenho, gestos, janela), `hb_types.GeoNodeWall/GeoNodeCage/GeoNodeObject`,
`operators/walls.py` (esquadrias, cadeias de parede, piso e teto), `operators/ops_wall_extras.py` (remover parede),
`openings/sync.py` (portas e janelas reais), `selection/classify.py`, `data/units.py`, `data/expr.py`, `data/i18n.py`,
`compat.py`. Dependentes: `caffmob_draw/cabinet_editor/state.py`, `caffmob_draw/geometry/floor_outline.py`, `caffmob_draw/hb_props.py`, `caffmob_draw/__init__.py`.

### 5.1 Modelo do rascunho (`model.py`) 🟢

- **`Segment`**: `thickness` (0,15 m), `height` (2,6), `end_height` (= `height` se omitido), `wall_type`
  (`NORMAL`/`DIVISORIA`/`MURETA`), `lock_angle`, `source` (nome da parede existente; `None` = trecho novo).
- **`Chain`**: `nodes` (pontos 2D em metros, **a face interna**, RN-15), `segments` (um entre cada par de nós; fechada,
  o último liga ao primeiro), `closed`, `side` (`LEFT`/`RIGHT`: lado da espessura em relação ao sentido dos nós).
  - Topologia: `endpoints`, `direction` (atan2), `length`, `prev_index`/`next_index` (circulares quando fechada).
  - Ângulos: `angle_abs` (0 a 360°), `angle_rel` (−180 a 180, +90 = virou à esquerda), `miter_angles(i)` =
    (esq, dir) em radianos como `calculate_wall_miter_angles` do legado: metade da virada com o vizinho.
  - Orientação: `is_ccw` pela área com sinal (fórmula do cadarço) quando fechada, senão pela virada total;
    `outward_side` = `RIGHT` se anti-horária, senão `LEFT` (deixa a espessura para fora).
  - Faces: `inner_line` = os nós; `outer_line` = nós deslocados `t` pela normal do lado `side` e prolongados
    `t·tan(meia virada)` nas pontas (esquadria); `face_length` mede a face escolhida.
  - `shifted_nodes(factor)`: nós deslocados `factor × espessura` com esquadria nos cantos, escala
    `1 / (2·cos²(θ/2))`; usado pela conversão (linha de centro → face interna).
  - `hb_order()`: o Home Builder 5 põe a espessura sempre à esquerda; `side == 'RIGHT'` devolve a cadeia invertida.
  - Edição: `set_length(i, v, which)` (face interna: move o nó final na direção do trecho; face externa: ajuste
    iterativo de até 12 passos porque a esquadria muda com o nó); `set_angle_abs`/`set_angle_rel`; `move_node`
    (com `lock_angle` no trecho que chega, o nó só anda na direção dele: projeção escalar); `set_segment_value`
    (`height` arrasta `end_height`; trocar `wall_type` aplica `TYPE_DEFAULTS`); `split(i, point)` (projeção
    `t` presa a [0,05, 0,95], clone sem `source`); `remove_node` (une vizinhos; ponta aberta remove o trecho da ponta);
    `invert` (troca `side`, inverte nós e trechos mantendo a parede no lugar); `touches_start`,
    `close_if_touching` (3+ trechos, fim a até 10 mm do início: tira o nó duplicado), `close`.
- **`WallPlan`**: `chains`, `removed_sources` (paredes apagadas no rascunho), `converted_sources` (objetos da camada
  nova convertidos, removidos no OK), `references` (segmentos só para ver). `bounds()` dos nós e referências,
  com padrão `((-1,-1),(4,3))` para o plano vazio.
- `plan_signature(plan)`: tupla com nós arredondados a 6 casas, `closed`, `side`, campos dos trechos, e as duas
  listas de removidos: base do "sujo" (Cancelar pergunta) e do histórico.
- `rectangle(w, d, t, h, origin)`: sala retangular por medidas internas, anti-horária, espessura para fora.
- `validate(field, value)` aplica `LIMITS` (RN-18): comprimento 0,01 a 100 m, espessura 0,01 a 2 m, pés-direitos
  0,5 a 10 m, ângulos 0 a 360 / −180 a 180; mensagem traduzida "Valor Inválido: …".

### 5.2 Histórico (`history.py`) 🟢

`History(plan, limit=100, signature=plan_signature)`: pilhas `_undo`/`_redo` de cópias profundas do rascunho.
`checkpoint(plan)` só grava quando a assinatura muda (navegar, selecionar e a lupa não geram passo); refazer é
descartado a cada passo novo. A assinatura é injetável: o editor de armário (004) reusa a classe.

### 5.3 Mira e direção (`inference.py`, `direction.py`) 🟢

- `Index(points)`: duas listas ordenadas (por X e por Y) e `bisect` dão a referência mais próxima em cada eixo em
  O(log n) por movimento; `query(cursor, tol, exclude)` devolve `(x travado, ref X, y travado, ref Y)`. A
  tolerância chega em metros (`8 px / escala`), então a trava vale 8 px em qualquer zoom. `plan_points(plan, extra)`
  reúne os vértices das cadeias e o início do desenho. O índice é refeito só quando `plan_signature` muda
  (`ops_editor._index`).
- `direction.py`: direção do lápis em radianos; `initial_direction(start, cursor)` encaixa em 0/90/180/270° a até
  2,5°; `ARROWS` mapeia as setas do teclado; `label(angle)` → "→ 0°". Regra: o mouse sozinho nunca muda a direção
  depois de fixada (RN-05/RN-06 da 009).

### 5.4 Pé-direito e conversão (`heights.py`, `convert.py`) 🟢

- `follows_project_height(btm_type, legacy_type)`: falso para `MURETA` e para `WALL_TYPE` `Half`/`Fake`;
  `walls_to_equalize(walls, h, tol=1 mm)` lista as paredes de altura cheia fora do pé-direito do projeto.
- `chains_from_segments(segments)`: une trechos da camada nova (`btm_wall_segments`, linha de centro) em cadeias
  crescendo pelas duas pontas com tolerância de 10 mm; fecha com 3+ trechos quando o fim volta ao início; desloca a
  linha de centro meia espessura para o lado oposto ao da espessura (`shifted_nodes(±0.5)`), com Direção para fora
  se fechada e esquerda se aberta; trechos degenerados (< 1 µm) são descartados.

### 5.5 Leitura e aplicação (`scene_io.py`, `apply.py`) 🟢

- `read_plan(scene)`: paredes `IS_WALL_BP` com modificador; uma cadeia começa na parede sem vizinha à esquerda
  (`get_connected_wall('left') is None`) e segue pela direita; laços sem início também entram; fecha com 3+ paredes
  quando o fim coincide com o início (10 mm). Nós = base da parede (Y local 0 = face interna), `side='LEFT'`;
  `btm_wall_orientation` antigo é ignorado (M-11). `reference_segments` desenha o contorno no piso das paredes da
  camada nova (`caffmob.wall_builder`): arestas da malha com as duas pontas na cota mínima.
- `convert_into(plan, objects, scene)`: lê `obj["btm_wall_segments"]` (JSON), leva ao mundo, chama
  `convert.chains_from_segments`; o objeto vai para `converted_sources`; sem dados, fica como referência.
- `apply_plan(context, plan, remove_modules, project_height)`:
  1. rede de segurança: `close_if_touching` em cadeias abertas com fim no início (ajusta `side` se toda nova);
  2. "Igualar ao pé-direito" grava `height = end_height = project_height` nas paredes de altura cheia;
  3. `hb_order()` → rascunho com espessura à esquerda; para cada trecho: atualiza a parede de origem ou cria
     (`GeoNodeWall.create`), limpa `COPY_LOCATION`, a primeira fica no primeiro nó, as seguintes `connect_to_wall`;
     rotação = direção do trecho; se a parede girou mais de 90° (Direção trocada), os filhos voltam à matriz de
     mundo guardada e as aberturas são re-hospedadas (`_rehost_opening`: desloca `−Dim X`, zera rotação, inverte
     `Swing Inside`/`Is Left`); grava `Length`, `Thickness`, `Height`, `End Height`, `btm_wall_type`; aberturas
     recebem `Dim Y` = espessura (BUG-YIMY);
  4. remove as paredes de `removed_sources` não reutilizadas (`ops_wall_extras.remove_wall`, com ou sem módulos) e
     os objetos de `converted_sources` (malha órfã também);
  5. `update_all_wall_miters()`, `refresh_floors_and_ceilings` (troca só a malha de pisos e tetos existentes, uma
     sala fechada por piso, na ordem dos nomes), `openings/sync` para portas e janelas reais (010).
  Devolve `{'created', 'updated', 'removed', 'closed', 'floors', 'ceilings', 'openings'}`.
- `items_that_do_not_fit(plan)`: filhos (fora `obj_x` e anotações) cujo `location.x + Dim X` passa do novo
  comprimento; `modules_of_removed(plan)`: filhos de paredes apagadas que não saem com a parede
  (`KEEP_WITH_WALL`); `height_mismatches(plan, h)`.
- `sync_project_height(context, h)`: Configurações → todas as paredes de altura cheia do arquivo (todas as cenas),
  tolerância 1 mm, esquadrias e piso/teto refeitos; devolve quantas mudaram.

### 5.6 Sessão e campos virtuais (`props.py`) 🟢

- **`Session`** (uma por vez, em memória): `plan`, `view` (`View2D`), `window_ptr`/`area_ptr`/`restore_area_type`,
  seleção (`selected` = (cadeia, trecho), `selected_node`, `line` INNER/OUTER), lápis (`drawing`, `direction`,
  `direction_locked`, `typed`, `typed_preview`, `pending_point`), mira (`lock_x`, `lock_y`, `snap_point`,
  `inference_index`/`inference_signature`), perguntas (`prompt` ∈ {`close`, `close_existing`, `discard`},
  `prompt_chain`), confirmação do OK (`warnings`, `removed_modules`, `remove_modules`, `height_mismatches`,
  `project_height`, `equalize_height`, `confirm_pending`), `request` (`ok`/`cancel`), `signature` de abertura,
  `history`, e (013) `zoom_window`/`zoom_box_end`. `dirty()`, `segment()` (descarta seleção inválida),
  `checkpoint()`, `undo()`/`redo()` (restauram e limpam lápis, seleção de nó, digitação e perguntas), `redraw()`.
- **`BTM_PG_WallEditorState`** em `WindowManager.btm_wall_editor`: `tool` (SELECT, DRAW, INVERT, ADD_NODE,
  REMOVE_NODE), `grid_size` (0,01 a 5 m), `magnetic`, padrões do lápis (`new_direction`, `new_thickness` 0,01 a 2,
  `new_height` 0,5 a 10), e os **campos virtuais** do trecho selecionado com `get`/`set` sobre o rascunho (`line`,
  `length`, `angle_abs`, `angle_rel`, `lock_angle`, `thickness`, `height`, `end_height`, `direction`, `wall_type`) e as
  versões texto (`*_text`) na unidade do projeto sem arredondar (BUG-VQ72), que aceitam mm/cm/m. Todo `set` passa por
  `_guard`: captura `ValueError` em `s.error`, grava passo de desfazer e redesenha. Trocar a Direção de paredes
  existentes avisa que no OK elas mudam de sentido.

### 5.7 Operadores e interação (`ops_editor.py`) 🟢

- `caffmob.wall_editor` (`BTM_OT_WallEditor`): `poll` exige janela e nenhuma sessão aberta; paredes da camada nova
  selecionadas abrem um diálogo (`other_walls`: converter ou só referência); lê o plano, cria a sessão com o
  pé-direito do projeto (`measure/scene_cotas.ceiling_height`), abre a janela e dispara o modal; seleciona o primeiro
  trecho.
- `caffmob.wall_editor_modal` (`BTM_OT_WallEditorModal`, `UNDO`, `INTERNAL`): timer de 0,1 s (foca a aba do
  editor), `_handle_undo` (Ctrl+Z/Ctrl+Shift+Z/Ctrl+Y ficam no rascunho), `_local` (sobre o painel lateral →
  `PASS_THROUGH`), cursor no mundo, `_update_snap` (pulado em eventos de navegação, 013), `_handle`, `checkpoint`
  fora do arraste. Ordem de `_handle`: barra superior e lupa (013) → botão do meio / roda / pinça / arraste com dois
  dedos / Home → com a lupa ligada nada mais passa → pergunta aberta → ferramenta DRAW → Esc (limpa digitação →
  pergunta de descarte se sujo → cancela) → digitação em SELECT → Delete/X remove o trecho → clique → arraste de
  nó (com ímã do início a 15 px).
- Lápis (`_handle_draw`): Esc/botão direito terminam; Backspace; setas fixam a direção; dígitos, operadores e
  sufixos de unidade entram em `typed` (`data/expr.preview` mostra "= 16 mm" ou "Valor Inválido"); Enter cria o
  trecho na direção atual (a do primeiro movimento com trava ortogonal, depois só clique ou setas) e, se o alvo
  toca o início com 2+ trechos, pergunta "fechar?"; clique fixa o ponto da mira (`resolve_point`: ímã do início →
  vértice → trava ortogonal (fixa um eixo) → alinhamento X/Y no eixo livre → grade; a docstring inverte ortogonal e
  alinhamento, o código faz ortogonal antes _(Revisão cruzada 2026-10-10: ops_editor.py:389-402)_) e a direção do trecho.
- Perguntas (`_handle_prompt`): Sim fecha o contorno (espessura para fora, volta a SELECT) ou descarta; Não mantém
  o trecho digitado (`pending_point`).
- `caffmob.wall_editor_ok`: na primeira chamada com itens que não cabem, módulos em trechos apagados ou pé-direito
  diferente, só preenche os avisos (`confirm_pending`); na segunda, `request = 'ok'`. `caffmob.wall_editor_cancel`
  confirma se sujo. `caffmob.wall_editor_fit` enquadra com margem 15%.
- Desenho (`draw_plan`): fundo, grade, referências tracejadas, face interna tracejada e externa contínua, trecho
  selecionado em laranja com seta de sentido, nós como quadrados de 8 px, medida por trecho, digitação, mira, prévia
  do lápis (anel "Fechar" no ímã), dica da ferramenta, erro, barra superior (013) e caixa de pergunta.

### 5.8 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `LIMITS` | 0,01–100 m; 0,01–2 m; 0,5–10 m; 0–360°; −180–180° | `model.py` | RN-18 |
| `TYPE_DEFAULTS` | Divisória 0,10 m; Mureta 1,10 m | `model.py` | Padrões por tipo |
| `CLOSE_TOLERANCE` / `JOIN_TOLERANCE` | 0,01 m | `scene_io`, `convert`, `model` | Fechar e unir cadeias |
| `LIMIT` | 100 passos | `history.py` | Profundidade do desfazer |
| `TOLERANCE` | 1 mm | `heights.py` | Igualdade de pé-direito |
| `NODE_HIT_PX`, `LINE_HIT_PX`, `SNAP_CLOSE_PX`, `ALIGN_PX` | 9, 7, 15, 8 px | `ops_editor.py` | Alvos de clique, ímã, mira |
| `TIMER_STEP` | 0,1 s | `ops_editor.py` | Foco da aba |
| `TOOLBAR_HEIGHT` | 32 px × `ui_scale` | `ops_editor.py` | Barra superior (013) |
| `PROMPT_W/H` | 380 × 90 px | `ops_editor.py` | Caixa de pergunta |

Tratamento de erros: `ValueError` do modelo vira `s.error` no painel e na planta; `RuntimeError` ao abrir a janela
cancela o operador com `report({'ERROR'})`; `get_input('Dim X')` falho conta como largura 0.

Testes: `tests/blender_002_smoke.py`, `tests/blender_002_ui_events.py`, `tests/blender_009_walls_smoke.py`, `tests/blender_013_touchpad_smoke.py`, `tests/test_wall_direction.py`, `tests/test_wall_inference.py`, `tests/test_walls2d_convert.py`, `tests/test_walls2d_heights.py`, `tests/test_walls2d_history.py`, `tests/test_walls2d_model.py`.

## 6. Módulo `move_over` (`caffmob_draw/move_over/`)

"Mover Sobre" (feature 002, bloco 2) ampliado pelo "Reposicionar" (feature 003) e pela correção do SketchUp
(commit 7948a79): arrastar um objeto A sobre uma referência B com o botão direito e alinhá-los numa janela com as
vistas superior e frontal, mais rotação, passo do teclado, posições salvas, Substituir, Mover na Parede e o plano de
inserção. 10 arquivos, 1.338 linhas, em três camadas (Princípio IV):

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `align.py` (132), `reposition.py` (70) | não | Alvos e deslocamentos no referencial de B; rotação pelo centro da base, passo, posição relativa salva |
| Ponte Blender ↔ modelo | `scene.py` (175), `props.py` (68) | sim | Caixas de A e B no referencial de B, prévia, restauração, sobreposição; estado do modo e coleções |
| Interface | `ops_drag.py` (158), `ops_dialog.py` (382), `ops_move_on_wall.py` (117), `ops_substitute.py` (110), `insertion_plane.py` (98) | sim | Botão e atalho do botão direito, janela GPU, arraste na parede, Substituir, plano de inserção |

`__init__.py` importa os submódulos tardiamente (`_modules()`), para `align` e `reposition` rodarem nos testes sem
`bpy`. Dependências: `canvas2d` (`draw`, `View2D`, `distance_point_segment`), `selection/classify.py`
(`movable_root`, `reference_root`, `classify`, `module_library`), `aggregates/group.object_corners` (caixa de Empty
pelas malhas filhas), `measure/cotas.slide` e `measure/scene_cotas.for_object`, `hb_placement.PlacementMixin.avoid_overlap`,
`customize/library_io` (`list_modules`, `load`), `hb_gpu_draw.point_in_rect`, `data/units`, `data/i18n`,
`bpy_extras.view3d_utils`, `mathutils`. Dependentes: `caffmob_draw/__init__.py` (registro),
`operators/viewport_hud.py` (botão do modo no HUD), `ui/sidebar_vocab.py` (ações `MOVE_OVER`, `INSERTION_PLANE`,
`CLEAR_INSERTION_PLANE`), `ui/context_menu.py` (plano de inserção no menu do objeto), `ui/object_properties.py`
(botão "Mover na Parede", estado do modo e do plano), `hb_snap.py` (consome `btm_insertion_plane` no lugar do piso),
`stick/settle.py` (`_MOVE_IDS` inclui `move_on_wall`, `move_over_drag`, `move_over_dialog`).

### 6.1 Convenção de referencial e alvos (`align.py`) 🟢

Tudo em metros no referencial de B (posição e rotação de B, sem escala): X = largura, Y = profundidade com a
**frente em Y mínimo** (todas as bibliotecas e o módulo rápido têm a frente em −Y e o fundo em Y ≈ 0; uma parede como B
tem a face da frente em Y = 0), Z = altura. Caixas são `((xmin, ymin, zmin), (xmax, ymax, zmax))`.

- `Target(kind, value)`: `LEFT`, `RIGHT` (A encostado no lado de B), `DEPTH` (fração: frente de A na profundidade de B,
  0% = frente, 100% = fundo), `HEIGHT` (fração: base de A na altura de B), `STACK` (A em cima de B), `WALL_FACE`
  (fundo de A na face da parede). `FRACTIONS = (0, 0,30, 0,50, 0,75, 1)`.
- `delta_for(target, box_a, box_b)` devolve `(dx, dy, dz)` com os eixos não afetados em 0: `LEFT` → `bx0 − ax1`;
  `RIGHT` → `bx1 − ax0`; `DEPTH` → `by0 + f·(by1 − by0) − ay0`; `WALL_FACE` → `by0 − ay1`; `HEIGHT` →
  `bz0 + f·(bz1 − bz0) − az0`; `STACK` → `bz1 − az0`; tipo desconhecido levanta `ValueError`. O parâmetro `wall`
  é aceito e ignorado (🟡 resíduo de assinatura).
- `combine(targets, …)`: soma alvos de eixos diferentes (lado + profundidade); dois alvos no mesmo eixo, o último vence.
- `top_view_lines(box_b, wall)`: arestas esquerda e direita de B; com parede, **só** a linha da face (`WALL_FACE`), sem
  frações; senão as cinco linhas de profundidade. `front_view_lines`: lados + cinco linhas de altura.
- `pick(click_px, lines_px, tol=12 px)`: distância ponto‑segmento na tela; guarda o melhor alvo por eixo (`x` para
  lados, `v` para profundidade/altura), logo no máximo **dois** alvos por clique.
- `pick_stack(click_px, top_line_px, tol)`: clique dentro da largura de B e **acima** do topo além da tolerância = empilhar.
- `gaps(box_a, box_b)` = (X entre as faces mais próximas, negativo = sobreposição em X; frente de A − frente de B;
  base de A − base de B). `overlaps(a, b, tol=1e‑4)`: interseção estrita nos três eixos.

### 6.2 Reposicionar (`reposition.py`) 🟢

- Rotação em graus em torno do eixo vertical pelo **centro da base** de A (D‑21): `box_center_base`,
  `rotate_point_z`, `origin_after_rotation(origin, box, deg)` (nova origem de A, o centro não se move) e
  `rotated_box(box, deg)` (caixa alinhada que envolve a planta girada; Z inalterado), usada nas vistas e distâncias.
- `step_delta(key, step)`: setas movem X (←→) e profundidade (↑↓), Page Up/Down a altura.
- `side_of(box_a, box_b)`: `RIGHT` se o centro de A está à direita do centro de B, senão `LEFT`.
- `save_position(box_a, box_b, rotation)` → `{'delta': (ref_x − anchor_x, ay0 − by0, az0 − bz0), 'rotation',
  'b_side'}`, onde do lado direito compara `xmin` de A com `xmax` de B e do esquerdo `xmax` de A com `xmin` de B;
  `apply_position(saved, …)` devolve o deslocamento inverso para repetir a posição num outro par.
- `absolute_values` existe mas nenhum chamador do pacote o usa (`scene.world_min` faz o cálculo) (🟡 código ocioso).

### 6.3 Camada de cena (`scene.py`) 🟢

`MoveOver(context, obj_a, obj_b)`:
- `a = classify.movable_root(obj_a)` (módulo para frentes e peças; geometria; obstáculo; grupo solto do SketchUp ou da
  biblioteca de objetos), `b = classify.reference_root(obj_b)` (o mesmo, mais paredes). `None`, ou A == B, levanta
  `ValueError` traduzido ("Esses objetos não podem ser usados no Mover Sobre.").
- Guarda `original_parent`, `original_matrix`, `original_parent_inverse`; `b_frame = LocRotScale(loc, rot, None)` de B e
  o inverso; `box_b` e `a_local_box` pela caixa local **com a escala do objeto** (`group.object_corners`: um Empty usa
  as malhas filhas); `origin_in_b`; `delta = 0`; `rotation = 0`.
- Caixas: `_unrotated_box` = caixa local de A posta em `origin_in_b + delta` (A já assumiu a rotação de B, RN‑08);
  `box_a()` aplica `rotated_box` quando há rotação. `original_box_a()` (A como estava) não é chamado por `ops_dialog`
  (🟡 reservado ou ocioso).
- `align_to(targets)`: `combine` → soma só os eixos não nulos → `preview()`. `set_gap(axis, value)`: em X mantém o
  lado em que A está (pelos centros); em profundidade põe a frente de A a `value` da frente de B; em altura a base.
  `set_rotation` (mod 360), `nudge`, `world_min` (canto mínimo de `box_a` levado ao mundo, só exibição), `set_world`
  (`delta += b_frame_inv.to_3x3() @ (alvo − atual)`), `saved()`/`apply_saved()`.
- `_target_matrix()`: `local = origin_in_b + delta`, girado por `origin_after_rotation` se houver rotação;
  `loc = b_frame @ local`; rotação = a de B, composta com `Rz(rotation)`; escala = a original de A.
- `preview()`: se B é parede, ou B está numa parede (`parent` com `IS_WALL_BP`), A vira **filho dessa parede** com
  `matrix_parent_inverse = Identity` (as cotas continuam valendo); grava `matrix_world`. `restore()` devolve pai,
  inverso e matriz originais.
- `overlapping()`: AABB mundial de A na posição alvo contra todos os objetos da cena com `classify.module_library`
  (bound box avaliado), tolerância 1 mm (RN‑11).

### 6.4 Estado e coleções (`props.py`) 🟢

- `WindowManager.btm_move_over` (`BTM_PG_MoveOverState`, não salvo): `enabled` (redesenha as VIEW_3D ao mudar),
  `tolerance_px` 12 (4–40), `step` 0,01 m (0,0001–1), `show_relative` True.
- `Scene.btm_saved_positions` (`BTM_PG_SavedPosition`, **salvo no arquivo**): `name`, `delta` (vetor 3, TRANSLATION),
  `rotation`, `b_side` LEFT/RIGHT; `Scene.btm_saved_positions_index`. Nenhum operador deste pacote remove itens; a janela
  mostra só os **4 últimos** (`MAX_SAVED_BUTTONS`).
- `WindowManager.btm_insertion_plane` (`BTM_PG_InsertionPlane`): `active`, `matrix` (16 floats, linha a linha),
  `source_name`.

### 6.5 Modo e arraste (`ops_drag.py`) 🟢

- `caffmob.move_over_toggle` inverte `enabled` (sem modal permanente: o salvamento automático continua).
- `caffmob.move_over_drag`: item de keymap do add‑on `RIGHTMOUSE PRESS head=True` em "3D View" **e** nos 19 mapas de
  modo (`VIEW3D_MODE_KEYMAPS`: Object Mode, Mesh, Sculpt, Grease Pencil…), porque esses mapas são processados antes e
  o menu de contexto capturaria o clique (D‑29, A001). `poll` exige VIEW_3D, região WINDOW e modo ligado; desligado, o
  evento segue para o menu do Blender.
- `invoke`: `raycast` (`region_2d_to_origin_3d` + `region_2d_to_vector_3d` + `scene.ray_cast`) → `movable_root`;
  sem objeto movível devolve `FINISHED` e **consome** o clique (RN‑10: com o modo ligado o botão direito nunca abre menu).
- `modal`: `MOUSEMOVE` refaz o raycast e guarda `reference_root` ≠ A como candidato B; `RELEASE` com deslocamento
  Manhattan ≥ `DRAG_THRESHOLD_PX` (5) e B definido abre `caffmob.move_over_dialog(a_name, b_name)`; Esc cancela.
  Desenho `POST_PIXEL`: linha tracejada do início ao cursor (laranja; azul com B) e rótulo "A → B".

### 6.6 Janela "Mover Sobre" (`ops_dialog.py`) 🟢

`caffmob.move_over_dialog` (`BTM_OT_MoveOverDialog`, `REGISTER`, `UNDO`; `a_name`/`b_name` ocultos, `SKIP_SAVE`):
- `invoke`: cria `MoveOver` (`ValueError` → `WARNING`, `CANCELLED`); desseleciona tudo, seleciona A e B, **B vira o
  ativo** (RN‑05); `preview()` já aplica a rotação de B em A (RN‑08); `_layout`, `_fit_views`, `draw_handler_add`
  `POST_PIXEL`, `modal_handler_add`, texto de status.
- `_layout` (× `ui_scale`): painel centralizado com dois painéis de 330 × 250 px (Superior: X × profundidade, frente
  embaixo; Frontal: X × altura), linha 1 com três campos (X, Profundidade, Altura), linha 2 (Rotação, Passo, botão
  Relativa/Absoluta), linha 3 (Salvar posição, até 4 posições salvas, Substituir), linha de aviso, Confirmar e
  Cancelar (120 × 28). `_fit_views`: um `View2D` por painel enquadrando a união das caixas de A e B com margem 15%.
- `_hits(pixel)`: identifica o painel, `align.pick` com `tolerance_px` do estado; na frontal, sem alvo, testa
  `pick_stack`. `MOUSEMOVE` só atualiza `hot` (alvos realçados).
- Desenho: B azul (`reference`) e A laranja (`moving`) com preenchimento; alvos tracejados, realçado contínuo; rótulos
  0%/30%/50%/75%/100% nas linhas de fração; "Empilhar" no topo de B. Campos mostram `gaps()` (relativa) ou
  `world_min()` (absoluta) com `draw.length_label`; Rotação "0,0°"; Passo.
- Digitação: clique no campo ou Tab (Tab circula os 5 campos e grava o buffer se houver); aceita `0123456789,.-mc °`;
  Backspace; Esc limpa; Enter grava (`_commit_typing`): Rotação como float (vírgula aceita, "°" removido); os demais
  por `units.parse_length` na unidade da cena, Passo sem zero nem negativo; `ValueError` vira aviso. O valor vai para
  `set_rotation`, `state.step`, `set_gap` (relativa) ou `set_world` (absoluta).
- Cliques: Confirmar, Cancelar, campos, Relativa/Absoluta (só exibição, nada se move), Salvar posição (acrescenta
  "Posição N" à cena com `saved()`), posições salvas (`apply_saved`), Substituir, senão `_apply_click` (alvos ou
  empilhar → `align_to`). Fora do painel só `NAV_EVENTS` passam (`PASS_THROUGH`); os demais cliques são ignorados.
- `_confirm`: com `scene.btm_settings.collision_global` ligado e ainda não avisado, `overlapping()` não vazio escreve
  "Sobrepõe: …" (até 4 nomes), marca `warned` e permanece; a segunda confirmação fecha com `FINISHED` (um passo de
  desfazer). Esc, botão direito ou Cancelar → `cancel()` → `restore()` → `CANCELLED`. Setas e Page Up/Down →
  `step_delta` → `nudge`.
- `_substitute`: fecha a janela mantendo a posição atual e abre `caffmob.move_over_substitute('INVOKE_DEFAULT')`.

### 6.7 Mover na Parede (`ops_move_on_wall.py`) 🟢

`caffmob.move_on_wall` (`REGISTER`, `UNDO`): `poll` exige VIEW_3D, modo OBJECT e objeto ativo com cotas de parede
(`scene_cotas.for_object(...).on_wall`). `invoke` guarda a posição original e o ponto de pega `_wall_point`: o raio do
mouse (sempre pela região WINDOW da área, porque o botão do painel lateral também chama) cortado no plano da **frente do
módulo** (Y local = `back_y − depth` no referencial da parede) por `intersect_line_plane` com raio de 10⁶. `modal`:
botão do meio e roda passam; Esc/botão direito restauram e cancelam; clique esquerdo ou Enter confirmam; `MOUSEMOVE` →
`_move`: com Shift, `z0 = max(0, z0 inicial + Δz)`; sem, `x0` alvo = `x0 inicial + Δx` passa por `cotas.slide`
(para no vizinho da mesma faixa de altura e nas pontas da parede quando `PlacementMixin.avoid_overlap(context)`), e a
localização vira `(x0, back_y, z0)`. O cabeçalho mostra Anterior | Posterior | Inferior formatados na unidade da cena.

### 6.8 Substituir (`ops_substitute.py`) 🟢

`caffmob.move_over_substitute` (`REGISTER`, `UNDO`; `module` Enum preenchido por `library_io.list_modules()`, id = caminho
do `.blend`, rótulo "categoria / nome"; `_ITEMS` global mantém as strings vivas): `invoke_props_dialog` 360 px.
`substitute(context, a, b, entry)`: `library_io.load` → (`root`, `loaded`, `warnings`); sem raiz, apaga o que carregou
e devolve avisos. O novo recebe a matriz de mundo e o pai de A (com o `matrix_parent_inverse`), `view_layer.update()`;
caixas no referencial de B: `_tree_box` (malhas visíveis, fora `WIRE`/`BOUNDS`, senão a raiz) de A e do novo, e
`_local_box` de B; `side_of(box_a, box_b)` escolhe o canto: do lado direito alinha `xmin`, do esquerdo `xmax`; frente e
base de A; translada por `frame.to_3x3() @ delta`; apaga A e seus descendentes (do fundo para a raiz). O operador
seleciona e ativa o novo e reporta avisos ou "{A} substituído por {novo}".

### 6.9 Plano de inserção (`insertion_plane.py`) 🟢

- `caffmob.set_insertion_plane` (`REGISTER`, sem `UNDO`: estado de sessão): `invoke` entra em modal com cursor
  `EYEDROPPER` esperando um clique na face; `LEFTMOUSE` → `scene.ray_cast`; sem acerto, `WARNING` e `CANCELLED`; com
  acerto, `matrix = Translation(local) @ to_track_quat('Z', 'Y')` da normal, achatada em 16 floats, `source_name` e
  `active = True`. Esc/botão direito cancelam; `execute` direto só avisa "Use com o botão direito sobre uma face".
- `caffmob.clear_insertion_plane`: `poll` exige plano ativo; desliga.
- Consumo (fora do módulo): `hb_snap.py` substitui o plano do piso Z = 0 pela translação e pela coluna Z da matriz
  quando não está em vista ortográfica lateral (RN‑17, D‑24); `ui/context_menu.py` mostra "Limpar" só com plano ativo.

### 6.10 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `FRACTIONS` | 0, 30, 50, 75, 100% | `align.py` | Linhas de profundidade e altura |
| `DEFAULT_TOLERANCE_PX` | 12 px | `align.py` | Tolerância padrão do clique nos alvos |
| `tolerance_px` | 12 (4–40) | `props.py` | Tolerância efetiva da janela |
| `step` | 0,01 m (0,0001–1) | `props.py` | Passo das setas e Page Up/Down |
| `DRAG_THRESHOLD_PX` | 5 px | `ops_drag.py` | Distância Manhattan mínima para abrir a janela |
| `VIEW3D_MODE_KEYMAPS` | 19 mapas | `ops_drag.py` | Mapas de modo que recebem o atalho do botão direito |
| `MAX_SAVED_BUTTONS` | 4 | `ops_dialog.py` | Posições salvas visíveis |
| `FIELD_COUNT`, `ROTATION`, `STEP` | 5, índices 3 e 4 | `ops_dialog.py` | Campos digitáveis |
| `NAV_EVENTS` | botão do meio, roda, trackpad, NDOF | `ops_dialog.py` | Passam fora do painel |
| Painéis / botões | 330 × 250 px; 120 × 28 px; pad 12 px | `ops_dialog.py` | Geometria da janela (× `ui_scale`) |
| Tolerância de sobreposição | 1e‑3 m (padrão 1e‑4) | `scene.py` / `align.py` | `overlapping()` |
| Raio de projeção | 10⁶ | `ops_move_on_wall.py` | `intersect_line_plane` |

Tratamento de erros: `ValueError` do construtor `MoveOver` e de `parse_length` viram `report({'WARNING'})` ou aviso no
painel; `status_text_set(None)` protegido contra `AttributeError`/`RuntimeError` ao fechar; remoção dos itens de keymap
protegida contra `ReferenceError`/`RuntimeError`; `is_registered` antes de desregistrar (`ops_substitute`,
`insertion_plane`). `cancel()` dos modais remove o `draw_handler` em todos os caminhos de saída.

Testes: `tests/test_move_over_align.py` (puro: lados, frações, empilhar, parede, clique e tolerância, folgas),
`tests/blender_003_move_over_smoke.py` (camada de cena: X digitado, rotação pelo centro da base, cancelar, relativa/
absoluta sem mover, posição salva em outro par, Substituir, plano de inserção), `tests/blender_bug_skp_mover_sobre.py`
(regressão: grupo `btm_group` do SketchUp como A). Textos em `data/translations/move_over.json` (48 chaves).

## 7. Módulo `measure` (`caffmob_draw/measure/`)

Cotas de um módulo na parede (feature 002, bloco 1; RN‑04, D‑11): afastamento, cota anterior, posterior, inferior e
superior, lidas e **aplicadas** (a cota digitada move o módulo sem mudar as dimensões). 3 arquivos, 220 linhas, em duas
camadas:

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `cotas.py` (94) | não | `Placement`, `Cotas`, limites por obstáculos, cálculo, aplicação, deslizar |
| Ponte Blender ↔ modelo | `scene_cotas.py` (125) | sim (`hb_types`, `classify`) | Lê o módulo, a parede, os obstáculos e o pé‑direito; escreve `location` |

`__init__.py` é vazio (só docstring). Dependências: `data/i18n`, `hb_types.GeoNodeObject/GeoNodeWall`
(`get_input('Dim X/Y/Z', 'Length', 'Thickness', 'Height')`), `selection/classify.classify`,
`hb_placement.PlacementMixin.get_wall_children_sorted` (import tardio), `hb_project.get_main_scene` (import tardio).
Dependentes: `overlays/selection_cotas.py` (desenho ao vivo das cotas do módulo selecionado), `ui/object_properties.py`
(campos de cota no painel; botão "Mover na Parede"), `move_over/ops_move_on_wall.py` (`cotas.slide`,
`scene_cotas.for_object`), `walls2d/ops_editor.py` (`ceiling_height` como pé‑direito do projeto, D‑36),
`tests/blender_002_smoke.py`.

### 7.1 Núcleo puro (`cotas.py`) 🟢

Referencial da parede, em metros: X ao longo da parede (0 = início, `wall_length` = fim), Z = altura a partir do piso,
Y = profundidade com a face da parede em Y = 0 e os módulos do lado da frente em Y < 0.

- **`Placement(x0, width, z0, height, back_y)`**: módulo (`back_y` = Y do fundo). **`Cotas(afastamento, anterior,
  posterior, inferior, superior)`**; `FIELDS` na mesma ordem; `LABELS` traduzíveis ("Afastamento da parede", "Cota
  anterior"…).
- Obstáculos: intervalos `(x0, x1, z0, z1)` de outros itens da parede (módulos, portas, janelas).
  `_vertical_overlap` é **estrita** (`z0 < oz1 and oz0 < z1`, como RN‑12 do `hb_placement`): itens em outra faixa de
  altura não contam.
- `limits(placement, obstacles, wall_length)` → (esquerda, direita): começa em `(0, wall_length)`; para cada obstáculo
  na mesma faixa, se termina antes do módulo (`ox1 ≤ x0 + 1e‑9`) empurra a esquerda para `max(left, ox1)`; se começa
  depois (`ox0 ≥ x1 − 1e‑9`) puxa a direita para `min(right, ox0)`. Obstáculos que cruzam o módulo são ignorados.
- `compute(placement, obstacles, wall_length, ceiling)` = `Cotas(−back_y, x0 − left, right − x1, z0,
  ceiling − (z0 + height))`. `compute_free(placement, ceiling)`: módulo sem parede, só inferior e superior (as demais
  `None`).
- `apply(field, value, …)` → nova `Placement` com a cota igual a `value`, dimensões intactas (RN‑04): negativo levanta
  `ValueError` "Valor Inválido: … não pode ser negativa."; `afastamento` → `back_y = −value`; `inferior` → `z0`;
  `superior` → `z0 = ceiling − value − height` (abaixo do piso: "maior que o espaço até o piso"); `anterior` →
  `x0 = left + value`; `posterior` → `x0 = right − value − width`; `x0 < 0` ou `x1 > wall_length + 1e‑9` → "tira o
  módulo da parede"; campo desconhecido → `ValueError` não traduzido.
- `slide(placement, obstacles, wall_length, target_x0, avoid=True)` (RF‑34): com Evitar Sobreposição, `x0` fica em
  `[left, max(left, right − width)]`; sem, em `[0, max(0, wall_length − width)]`.

### 7.2 Ponte com a cena (`scene_cotas.py`) 🟢

- `_dims(root)`: com `home_builder.mod_name` preenchido lê `Dim X/Y/Z` do Geometry Nodes; senão `btm_cabinet`
  (`width > 0`); senão `root.dimensions`. Exceções do `get_input` são engolidas (`except Exception`).
- `_wall_of(root)`: pai com `IS_WALL_BP`. `_on_front_side(root, wall)`: rotação Z própria < 0,01 rad (os de trás giram
  180°) **e** `location.y < meia espessura` da parede.
- `ceiling_height(scene, wall=None)`: `home_builder.ceiling_height` da cena principal (`hb_project.get_main_scene()`),
  se > 0; senão `Height` da parede; senão **2,6 m**.
- **`ModuleCotas(root, scene)`**: `wall`, `on_wall` (parede e lado da frente), `placement` (na parede: `location`
  local `x`, `z`, `y` e as dimensões; livre: `x0 = 0`, `z0` = Z mundial, `back_y = 0`), `wall_length` (`Length` da
  parede ou `None`), `ceiling`, `depth`.
  - `obstacles()`: `PlacementMixin().get_wall_children_sorted(wall, exclude_obj=root, object_z_start, object_height)`
    filtrando `IS_2D_ANNOTATION` e `IS_SNAP_LINE`; a faixa de altura devolvida é a **do próprio módulo** (`z0`, `z1`)
    porque a seleção por faixa já foi feita pelo `hb_placement` (🟡 a faixa real do obstáculo não é preservada).
  - `compute()` → `cotas.compute` ou `compute_free`.
  - `apply(field, value)`: módulo livre com `anterior`/`posterior`/`afastamento` → `ValueError`; na parede grava
    `location = (x0, back_y, z0)`; livre chama `cotas.apply` com `wall_length = 1e9` e soma só o `Δz` em
    `location.z` (mundial). Atualiza `placement`.
- `for_object(obj, scene)`: `classify.classify(obj)`; só `MODULE`, `PART` ou `FRONT` (a raiz do módulo) → `ModuleCotas`;
  senão `None`.

### 7.3 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| Pé‑direito (último recurso) | 2,6 m | `scene_cotas.ceiling_height` | Só sem `home_builder.ceiling_height` > 0 nem parede; com o add-on registrado o padrão efetivo é `home_builder.ceiling_height = inch(96)` = 2,4384 m _(Revisão cruzada 2026-10-10: hb_props.py:481; scene_cotas.py:55-67)_ |
| Tolerância de lado | 0,01 rad; meia espessura | `_on_front_side` | Módulo do lado da frente |
| Epsilon | 1e‑9 m | `cotas.limits`, `apply` | Comparações de borda |
| `wall_length` do módulo livre | 1e9 | `ModuleCotas.apply` | Sem limite lateral |
| `FIELDS` | 5 cotas | `cotas.py` | Ordem dos campos no painel |

Tratamento de erros: toda validação é `ValueError` com prefixo traduzido "Valor Inválido:"; os consumidores (`ui`,
`overlays`) exibem a mensagem sem alterar o objeto. `get_input` falho em `_dims` e `_wall_thickness` cai para o próximo
fallback ou 0.

Testes: `tests/test_cotas.py` (cálculo com vizinho e janela alta em outra faixa, cota anterior 75 mm, demais cotas,
inválidos, módulo livre, deslizar), `tests/blender_002_smoke.py` (`for_object` na cena). `data/translations/measure.json`
(4 chaves).

## 8. Módulo `selection` (`caffmob_draw/selection/`)

Classificação do objeto selecionado para todas as bibliotecas (feature 002, bloco 1; RN‑01, D‑09), leitura e escrita
de dimensões por tipo (RN‑03, D‑10), seleção e exclusão **por componente** (feature 011; D‑01 a D‑08), medidas do
elemento tocado para o aviso na viewport e o **Redimensionar** do botão direito (commit 640b2c2). 9 arquivos, 949
linhas:

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `classify.py` (165), `component.py` (146) | não (só `.get()`, `.parent`, `.children`) | Tipo, raiz e biblioteca do objeto; raiz do componente, `collapse`, plano de exclusão |
| Ponte Blender ↔ modelo | `editing.py` (125), `element_size.py` (61), `resize.py` (129), `component_props.py` (45) | sim | Dimensões por biblioteca, medidas do elemento, redimensionar com agregados, propriedades |
| Interface e handlers | `component_select.py` (180), `component_pick.py` (97) | sim | Normalizador em `depsgraph_update_post`, Alt + clique e reset |

`__init__.py` é vazio; o registro é feito por `caffmob_draw/__init__.py` (`component_props`, `component_select`,
`component_pick`, nessa ordem, e o inverso no `unregister`). Dependências: `data/i18n`, `data/units`,
`hb_types.GeoNodeObject/GeoNodeWall/GeoNodeCage`, `standards/sync.add_override`, `hb_utils.run_calc_fix`,
`operators/walls.update_all_wall_miters`, `operators/doors_windows` (`_hole_to_leaf`, `_leaf_to_hole`,
`_sync_opening`), `openings/sync.kind_of`, `aggregates/group.object_corners`, `aggregates/apply` e `aggregates/limits`,
`legacy/gate.legacy_ui`. É o módulo **mais consumido** do ciclo forward: 33 arquivos importam `selection`
(`aggregates`, `cabinet_editor`, `collision`, `customize`, `legacy`, `measure`, `move_over`, `operators`, `overlays`,
`standards`, `stick`, `ui`, `walls2d`).

### 8.1 Classificador (`classify.py`) 🟢

- `Classified(kind, obj, root, library)`: `kind` ∈ `KINDS` (`ANNOTATION`, `FRONT`, `PART`, `MODULE`, `ROOM_DOOR`,
  `WINDOW`, `GEOMETRY`, `OBSTACLE`, `WALL`, `FLOOR`, `CEILING`, `OTHER`), `obj` = o que representa o tipo, `root` =
  módulo dono (frente e peça) ou o próprio, `library` ∈ {`FRAMELESS`, `FACE_FRAME`, `CLOSETS`, `BTM`, `HB`, `''`}.
  `KIND_LABELS` e `LIBRARY_LABELS` traduzíveis.
- Marcas: `MODULE_TAGS` (`IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_FACE_FRAME_PRODUCT_CAGE`,
  `IS_CLOSET_STARTER_CAGE`), `FRONT_TAGS` (`IS_DOOR_FRONT`, `IS_DRAWER_FRONT`, `IS_PULLOUT_FRONT`, `IS_FLIP_UP_DOOR`,
  `IS_CABINET_FRONT`), `FRONT_ROLES` (`hb_part_role` ∈ DOOR, DRAWER_FRONT, PULLOUT_FRONT, TILT_OUT, FRONT_PIVOT,
  CLOSET_DOOR_FRONT, CLOSET_DRAWER_FRONT), `BTM_FRONT_SUFFIXES` (`_Door_L`, `_Door_R`, `_Door_Flip` no nome).
- `btm_kind(obj)`: `btm_plane.object_kind` **só se `is_property_set('object_kind')`**; o enum tem padrão `WALL` em todo
  objeto e sem a checagem qualquer malha passava por parede (BUG‑20261007‑TBY3, commit b92ac2e).
- `module_library(obj)`: biblioteca pelas `MODULE_TAGS` ou `BTM` se `btm_kind == 'MODULE'`. `module_root(obj)`: primeiro
  ancestral (inclusive) com biblioteca.
- `classify(obj)` (precedência RN‑01): `None` → `None`; `IS_2D_ANNOTATION` → `ANNOTATION`/HB; com raiz de módulo: o
  primeiro ancestral **abaixo da raiz** que é frente → `FRONT` (o puxador conta como a frente); `obj is root` →
  `MODULE`; senão `PART`. Sem módulo, sobe pelos ancestrais testando na ordem: `IS_ENTRY_DOOR_BP` → `ROOM_DOOR`/HB;
  `IS_WINDOW_BP` → `WINDOW`/HB; `btm_kind` `OPENING` → `WINDOW`/BTM; `GEOMETRY` → `GEOMETRY`/BTM; `IS_OBSTACLE` ou
  `IS_SOFFIT_BP` → `OBSTACLE`/HB; `IS_WALL_BP` → `WALL`/HB; `btm_kind` `WALL` → `WALL`/BTM; `IS_FLOOR_BP` ou `FLOOR` →
  `FLOOR`; `IS_CEILING_BP` → `CEILING`/HB; nada → `OTHER` com biblioteca vazia. Módulo antes de parede importa porque
  gabinetes são filhos da parede.
- `free_group(obj)`: o grupo de peças **mais alto** (`btm_group.is_group`) entre os ancestrais (SketchUp, biblioteca de
  objetos). `movable_root(obj)` (RN‑05): raiz para `FRONT`/`PART`/`MODULE`/`GEOMETRY`/`OBSTACLE`; `free_group` para
  `OTHER`; `None` para parede, piso, teto, cota, porta e janela. `reference_root(obj)`: o mesmo, mais paredes.

### 8.2 Componente (`component.py`) 🟢

- `component_root(obj, modes=None)`, precedência D‑01 (a primeira que casa vale):
  1. vão de porta ou janela em qualquer ancestral (`is_opening_root`: `IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `btm_kind`
     `OPENING`), inclusive folha, ferragem, símbolo e texto 2D;
  2. cota ou anotação solta: ela mesma;
  3. subindo até (sem incluir) o primeiro módulo: item grudado (`btm_stick.is_stuck`) ou agregado próprio
     (`btm_aggregate.is_aggregate` e não folha de esquadria, isto é `LEAF` cujo `parent_ref` é grupo `FRAME`) → ele
     mesmo (RN‑03);
  4. módulo: a raiz se `modes.get(library, True)` (modo gabinete), senão o próprio objeto; o módulo rápido não tem modo
     e sobe sempre;
  5. raiz de item da biblioteca de objetos (`btm_object_item.is_item`);
  6. grupo de peças mais alto (`free_group`);
  7. o próprio objeto (parede, piso, malha solta).
- `collapse(objs, modes)`: raízes sem repetir (por `id`), na ordem de aparição.
- `own_aggregates(target)`: agregados que são componentes próprios abaixo de `target` (para a pergunta "levar os
  agregados junto?"); não desce em vãos nem em grupos `FRAME`, e não entra em vãos encontrados.
- `deletes_subtree(obj)`: falso para parede, piso e teto classificados **como o próprio objeto** (o que está preso neles
  é outro componente).
- `delete_plan(targets, keep_aggregates=False)` → `DeletePlan(remove, openings)`: percorre a subárvore de cada alvo,
  **filhos antes dos pais**, sem repetir; itens grudados nunca entram (são soltos no lugar); com `keep_aggregates`, os
  agregados próprios e suas peças ficam; parede/piso/teto como alvo saem sozinhos; `openings` = vãos que saem (para
  tirar o furo da parede).

### 8.3 Normalizador (`component_select.py`) 🟢

- Handler `@persistent on_depsgraph_update` em `depsgraph_update_post`: sai se `_busy`, se
  `Scene.btm_component_select` está desligado (e esquece a assinatura), fora do modo OBJECT, sem `window_manager`, ou com
  um **modal** rodando (`_modal_running`: qualquer `window.modal_operators` cujo `bl_idname` contenha `transform` ou
  `caffmob`, ou comece por `btm`). Compara `_signature` (nomes selecionados + ativo) com a última; se igual, sai cedo.
  Então `normalize()` sob a trava e grava a nova assinatura.
- `normalize(context, scene)`: `_selected` (pelo contexto ou, sem janela, pela camada de vista; descarta objetos
  apagados com `ReferenceError`); poda as isenções que não estão mais selecionadas; `cabinet_modes(scene)`; para cada
  selecionado não isento, `component_root` ≠ ele mesmo e presente na camada → seleciona a raiz e desseleciona a peça
  (`RuntimeError` ignorado); o ativo também sobe para a raiz se ela ficou selecionada. Devolve quantas subiram.
- `cabinet_modes(scene)` (D‑07; 012 D‑05): sem a interface herdada (`legacy/gate.legacy_ui()` falso) devolve `{}` (todo
  módulo sobe); senão `FRAMELESS` = `hb_frameless.frameless_selection_mode == 'Cabinets'`, `FACE_FRAME` = modo
  desligado ou `'Cabinets'`, `CLOSETS` = modo desligado ou `'Starters'`.
- Isenções: `exempt_names`/`set_exempt` em `WindowManager.btm_component_exempt` (nomes separados por `\n`, ordenados).
  `suspended()` (context manager) e `forget()`. `on_load_post`: esquece a assinatura e limpa as isenções.
  `register`/`unregister` idempotentes (testam presença nas listas de handlers).

### 8.4 Alt + clique (`component_pick.py`) 🟢

- `caffmob.component_pick` (`REGISTER`, `UNDO`; `extend`): `poll` exige OBJECT, VIEW_3D e interruptor ligado. `invoke`
  roda `view3d.select` **dentro de `suspended()`** (o `view3d.select` aninhado pode avaliar o depsgraph na hora), marca
  o ativo selecionado como isento (somando com Shift) e `forget()`.
- `caffmob.component_click_reset` (`INTERNAL`): `poll` exige isenções; clique sem modificador limpa as isenções e
  devolve `PASS_THROUGH` para o `view3d.select` seguir.
- Keymap do add‑on em "3D View", `head=True`: `LEFTMOUSE CLICK alt` (e `alt+shift` com `extend=True`) e
  `LEFTMOUSE PRESS` para o reset. Com o interruptor desligado, ambos saem pelo `poll` e o Alt + clique volta ao do Blender.

### 8.5 Propriedades (`component_props.py`) 🟢

`Scene.btm_component_select` (Bool, **padrão True, salvo no arquivo**; `update` → `forget()` para promover a seleção
atual na próxima atualização) e `WindowManager.btm_component_exempt` (String, sessão). `draw_toggle(layout, context)`:
interruptor com ícone de checkbox e dica "Ligada: Alt + clique seleciona uma peça" / "Desligada: clique seleciona a peça".

### 8.6 Dimensões por tipo (`editing.py`) 🟢

- Onde cada biblioteca guarda as medidas: frameless → inputs `Dim X/Y/Z` da raiz, registrando medida manual
  (`standards/sync.add_override`, 001 RN‑23) e `run_calc_fix`; face frame → `root.face_frame_cabinet.width/height/depth`
  (o `update` recalcula); closets → `root.hb_closet_starter.*`; módulo rápido → `root.btm_cabinet.*`; porta e janela de
  ambiente (HB) → `Dim X` e `Dim Z`, peitoril = `location.z`; parede HB → `Length`, `Height`, `End Height`,
  `Thickness`, com `update_all_wall_miters`.
- `has_dimensions(info)`: `MODULE`, `ROOM_DOOR`, `WINDOW`, `GEOMETRY`, `OBSTACLE`. `editable_dimensions(info)`:
  módulo → `width/height/depth`; porta e janela **HB** → `width/height`; o resto só leitura.
- `get_dimension(info, field)`: para módulo/frente/peça usa a raiz e a biblioteca (face frame, closets, BTM); senão
  `Dim X/Y/Z` do GN quando `home_builder.mod_name` existe (exceções engolidas); senão `obj.dimensions`.
- `set_dimension(context, info, field, value)`: campo não editável → `ValueError`; `_check` contra `LIMITS`
  (largura e altura 0,01–10 m, profundidade 0,005–10) com mensagem na unidade da cena; grava na biblioteca ou no GN.
- `get_sill`/`set_sill`: porta sempre 0 (`ValueError`); janela 0–5 m. `get_wall`/`set_wall(info, field, value)`: só
  `library == 'HB'`; `length` 0,05–100, `height` 0,5–10 (`WALL_LIMITS`), `end_height` 0,5–10, `thickness` 0,01–2;
  mudar `height` arrasta `End Height` (RN‑18); esquadrias refeitas.

### 8.7 Elemento e medidas (`element_size.py`) 🟢

`element(obj)` → `Element(obj, info, label)`: cota → `None`; frente e peça viram o módulo; módulo, porta, janela,
geometria, obstáculo e parede → o próprio `info.obj` com `KIND_LABELS`; o resto → `free_group` ou o objeto, rótulo
"Objeto". `size(el)` → (largura, altura, profundidade): parede HB pelos inputs; `_GN_KINDS` por `editing.get_dimension`,
e **porta pela folha** (`doors_windows._hole_to_leaf` com `openings/sync.kind_of`, 80 × 210 como o campo da porta);
o resto por `box_size` (caixa nos eixos do objeto × escala, via `group.object_corners`).

### 8.8 Redimensionar (`resize.py`) 🟢

- `can_resize(el)`: parede só HB; módulo só se `width` é editável; piso e teto nunca; o resto sim.
- `_stretched(el)`: sem largura própria → esticado em X pela escala: geometria sem `btm_geometry`, obstáculo sem
  `home_builder.mod_name`, e `OTHER` (grupo de peças, malha solta).
- `_set_width`: esticado → `scale.x *= width / atual` (atual ≤ 1e‑9 → `ValueError`); módulo → `editing.set_dimension`;
  porta → largura da folha convertida em furo (`_leaf_to_hole`) e `GeoNodeCage.set_input('Dim X')` + `_sync_opening`;
  janela idem sem conversão; parede → `set_wall('length')`; geometria → `btm_geometry.width`; senão `Dim X`.
- `resize(context, el, width)`: `MIN_WIDTH`/`MAX_WIDTH` 0,01–100 m; antes de mudar, mede a largura local
  (`aggregates/apply.local_box`) de cada pai com agregados (raiz e descendentes) e guarda `u`/`v` dos agregados; aplica;
  `view_layer.update()`; para cada pai, `factor = nova / antiga` (ignora |factor − 1| < 1e‑6) e `_stretch_aggregate`:
  folha `LEAF` não muda; agregado numa face com normal ≠ 0 em X só é reposicionado; senão escala o eixo local alinhado
  ao X do pai e multiplica `agg.size[0]` e `rest_offset[0]`; `u`/`v` escalam quando o eixo da face é X;
  `apply.update_position`.

### 8.9 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `KINDS` | 12 tipos | `classify.py` | Vocabulário do classificador |
| `MODULE_TAGS` / `FRONT_TAGS` / `FRONT_ROLES` / `BTM_FRONT_SUFFIXES` | 4 / 5 / 7 / 3 | `classify.py` | Marcas das bibliotecas |
| `LIMITS` | largura, altura 0,01–10; profundidade 0,005–10; comprimento 0,05–100; pé‑direito final 0,5–10; espessura 0,01–2; peitoril 0–5 m | `editing.py` | Validação de dimensões |
| `WALL_LIMITS['height']` | 0,5–10 m | `editing.py` | Pé‑direito inicial |
| `MIN_WIDTH`, `MAX_WIDTH` | 0,01–100 m | `resize.py` | Redimensionar |
| `GN_DIM` | width→Dim X, depth→Dim Y, height→Dim Z | `editing.py` | Mapa campo → input GN |
| `btm_component_select` | True | `component_props.py` | Interruptor salvo no arquivo |
| Keymap | Alt+clique, Alt+Shift+clique, PRESS | `component_pick.py` | "3D View", `head=True` |

Tratamento de erros: toda validação é `ValueError` "Valor Inválido: …" sem alterar o objeto; `get_input` falho em
`get_dimension` cai para `obj.dimensions`; o normalizador ignora `ReferenceError` (objeto apagado) e `RuntimeError`
(`select_set` inválido); remoção de keymap protegida.

Testes: `tests/test_classify.py` (precedência e Mover Sobre), `tests/test_component_core.py` (raiz por regra, modos,
`collapse`), `tests/test_component_delete.py` (plano de exclusão, agregados e grudados, parede sai sozinha),
`tests/blender_011_component_smoke.py`, `tests/blender_bug_TBY3_walls.py`, `tests/blender_toast_resize_invert.py`,
`tests/blender_012_legacy_gate_smoke.py`, `tests/blender_002_smoke.py`, `tests/blender_bug_skp_mover_sobre.py`.
`data/translations/selection.json` (23 chaves).

## 9. Módulo `openings` (`caffmob_draw/openings/`)

Porta e janela **reais** dentro da caixa da parede (feature 010, incrementos I3 e I4; RN‑01 a RN‑04, RN‑10, D‑07 a
D‑16), tecla I que inverte o giro (commit 640b2c2), e a **região marcada** na parede antes de inserir (feature 011;
D‑10 a D‑12). 11 arquivos, 1.169 linhas:

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `door_core.py` (192), `window_core.py` (71), `region_core.py` (50) | não | Geradores paramétricos das peças (porta de giro, janela de correr); encaixe da região |
| Ponte Blender ↔ modelo | `materials.py` (81), `build.py` (94), `sync.py` (212), `props.py` (36), `region_props.py` (55) | sim (`bmesh`, materiais) | Materiais compartilhados, montagem em poucas malhas, sincronização com a caixa, estado |
| Interface | `ops.py` (98), `region.py` (256) | sim (`gpu`, `blf`) | Atualizar portas e janelas, tecla I, marcar/limpar região com desenho `POST_PIXEL` |

`__init__.py` registra `props`, `ops`, **`ui/view_mode`** (módulo de outra pasta registrado aqui), `region_props` e
`region`, nessa ordem. Dependências: `hb_types.GeoNodeObject/GeoNodeCage/GeoNodeWall`, `aggregates` (`apply._write`,
`collision.OPENING_FRAME_PROP`, `group.create_group`, `leaf.make_leaf`), `inspection/room_door_leaf.remove_leaves`,
`hb_placement.PlacementMixin` (snap e cabeçalho), `hb_snap.snap_value_to_grid`, `units.unit_to_string`, `data/i18n`,
`assets/nogueira_cor.jpg` e `nogueira_rugosidade.jpg`. Dependentes: `operators/doors_windows.py` (coloca a caixa,
chama `sync.sync`, converte furo ↔ folha com `door_core`, usa `region_core.fit` e `region_props` no modo "na região"),
`walls2d/apply.py` (re‑sincroniza as aberturas no OK do editor de paredes), `selection/element_size.py`
(`sync.kind_of`), `ui/sidebar_build.py` (aviso "Atualizar portas e janelas" quando há `outdated`).

### 9.1 Porta paramétrica (`door_core.py`) 🟢

Peças tiradas do gerador da porta realista do projeto (`docs/porta_realista_080x210/gerar_porta.py`). A medida da porta
é a da **folha** ("porta de 80"); o furo na parede (a caixa) é a folha mais marco e folga. Referencial da caixa: x ao
longo do furo (0 = borda esquerda), y na espessura da parede (0 a `wall`), z para cima (0 = piso).

- `Part(role, name, shape, center, size, material, bevel, leaf, horizontal)` (`dataclass` congelada): `role` ∈
  `FRAME`, `FRAME_HW`, `LEAF`, `LEAF_HW`; `shape` `BOX` ou `CYL_X/Y/Z` (`size` = diâmetro, diâmetro, altura);
  `material` ∈ `WOOD`, `METAL`, `RUBBER`, `SLOT`, `BRASS`; `lo`/`hi`/`size_xyz` derivados; `horizontal` orienta o veio.
- Constantes: `LEAF_T` 40 mm, `FLOOR_GAP` 8 mm, `MARCO` 46 mm, `GAP` 3 mm, `SIDE` = 49 mm (borda do furo → folha),
  `TOP` 59 mm (folha → topo do furo), `CENTER_GAP` 3 mm (porta dupla), `HANDLE_Z` 1,02 m.
- `hole_size(w, h, double)` = (`2w + 3 mm` ou `w`, + 98 mm; `h` + 59 mm), arredondado a 6 casas: 80 × 210 → 898 × 2159;
  dupla → 1701 × 2159. `leaf_size` é o inverso.
- `_leaf(b, x0, w, h, leaf, hinge_left, lock)`: montantes de 110 mm, 3 travessas (inferior 140, central 140 a
  `h·0,93/2,1`, superior 130), 2 almofadas de 21 mm com frisos verticais e horizontais dos dois lados, vedação inferior
  de borracha; 3 dobradiças (chapa na folha = `LEAF_HW`, chapa no marco = `FRAME_HW`, 5 nós alternados, 2 pinos,
  3 + 3 parafusos com fenda) em z = 0,25, meio e `h − 0,248`; maçanetas nas duas faces (roseta, anel, eixo, alavanca
  125 × 20 × 17), e com `lock` roseta de chave, cilindro de latão, rasgo, testa, lingueta e contratesta. `X(x)` mede
  do lado da dobradiça.
- `_frame(b, span, h, wall, leaves)`: marcos esquerdo/direito (46 × `wall` × `h + 16`), batentes e vedações só com
  folhas, marco superior, guarnições de 72 mm com filete dos dois lados da parede (`face = wall/2 + 8,5 mm`).
- `door_parts(width, height, wall, hinge='LEFT', side='NEG_Y', double, open_door)`: vão aberto → só marco e
  guarnições; dupla → folha 0 com dobradiça à esquerda e fechadura, folha 1 à direita sem fechadura; simples → uma
  folha. Converte para a caixa: `x + SIDE`, `y → wall/2 + y·flip` (`flip = −1` se `POS_Y`). Ferragens e perfis têm
  tamanho fixo (largura maior não os distorce).

### 9.2 Janela paramétrica (`window_core.py`) 🟢

Janela de correr de alumínio no furo: marco `PROFILE` 40 mm com a profundidade da parede; trilhos inferior e superior
em dois eixos (`wall/2 ± 20 mm`); 2 folhas com perfil `SASH` 35 mm, profundidade 30 mm, vidro `GLASS_T` 4 mm, cada
uma com largura `inner/2 + OVERLAP/2` (sobreposição 50 mm) em trilhos diferentes; puxador concha no montante externo;
guarnições na face interna (y = `wall`); peitoril de granito 20 mm saindo 30 mm para os dois lados, com pingadeira.
Materiais `ALU`, `GLASS`, `STONE`. `travel(width)` = curso de cada folha até o batente do outro lado =
`inner − (inner/2 + OVERLAP/2)`.

### 9.3 Região marcada (`region_core.py`) 🟢

`fit(x0, x1, z0, z1, wall_length, wall_height, kind, others)` → `Fit(ok, x, width, height, sill, reason)`: ordena os
cantos; `z0` entre −5 mm e 0 vira 0; região menor que `MIN_SIZE` 1 mm → `EMPTY`; fora da parede além de `TOLERANCE`
5 mm ou abaixo do piso → `OUTSIDE`; acima do topo → `TOO_TALL`; porta (`DOOR`, `DOUBLE_DOOR`, `OPEN_DOOR`) tem
`sill = 0` e vai do piso à borda de cima; janela usa `z0` como peitoril; interseção estrita (1 mm) com `others` →
`OVERLAP`. Largura e altura são exatamente as da região, sem grade e sem folga. `REASONS` traduzíveis.

### 9.4 Materiais (`materials.py`) 🟢

`SPECS` por chave: nome, cor, metálico, rugosidade, extras do Principled (`Coat Weight`, `Coat Roughness`,
`Transmission Weight`, `IOR` 1,52, `Alpha` 0,25 no vidro). `get(key)`: reaproveita o material marcado
`btm_opening_material == key` em `bpy.data.materials`; senão cria, grava `diffuse_color`, `metallic`, `roughness`, os
sockets do BSDF; `WOOD` recebe as texturas de nogueira (cor → Base Color e Bump 0,025/0,22 mm; rugosidade em
`Non-Color` → Roughness); `GLASS` usa `surface_render_method = 'BLENDED'`.

### 9.5 Montagem (`build.py`) 🟢

`group_key(part)` agrupa por papel: `FRAME`, `FRAME_HW`, e por folha `LEAF` (inclui `ALU` e `GLASS` da janela) e
`LEAF_HW`. `group_name`: "Marco", "Ferragens do marco", "Folha N", "Ferragens da folha N". `build(parts, collection)`:
uma malha por grupo via `bmesh` (`create_cube` escalado ou `create_cone` de 32 segmentos girado por `_AXIS`),
`material_index` por slot ordenado, faces lisas só nos cilindros, UV de caixa com o veio por peça (`a/0,45 + offset`,
`b/2,3 + 0,3·offset`, `offset` derivado do nome) e, se alguma peça tem `bevel`, modificadores "Chanfro" (`BEVEL`
1 mm, 2 segmentos, por ângulo) e "Normais ponderadas" (`keep_sharp`). Cerca de 5 a 6 objetos por porta no lugar das
157 peças originais (D‑08). Saem no referencial da caixa, sem pai.

### 9.6 Sincronização (`sync.py`) 🟢

- `is_opening(obj)`: `IS_ENTRY_DOOR_BP` ou `IS_WINDOW_BP`. `_swing(cage)`: no filho `IS_2D_ANNOTATION`
  (`GeoNodeDoorSwing`) lê `Is Left`, `Swing Inside`, `Is Double` (falha → `True, True, False`). Medido no 5.2:
  `Swing Inside` desenha o arco no lado −Y, `Is Left` põe a dobradiça em x = largura.
- `kind_of(cage)`: `WINDOW` pela marca; senão `btm_opening_real.kind` se ≠ `NONE`; senão pelo símbolo (`OPEN_DOOR`
  sem símbolo, `DOUBLE_DOOR` ou `DOOR`). `signature(cage)` = `kind|DimX|DimY|DimZ|left|inside|vN` (5 casas).
- `_parts(cage, kind)`: janela → `window_parts(DimX, DimZ, DimY)`; porta → `leaf_size` do furo e `door_parts` com
  `hinge = RIGHT se Is Left`, `side = NEG_Y se Swing Inside (ou None)`.
- `sync(context, cage, force=False)`: não é abertura → False; assinatura igual e montagem viva → False (não refaz);
  `_remember` guarda `open_value` das folhas e `production_part`; `clear` apaga a montagem anterior (malhas órfãs
  também); `room_door_leaf.remove_leaves` tira a folha cinza da porta de ambiente da 005; `build`; nomes
  "`<caixa>` Marco"…; `_to_world`; grupo **FRAME** com marco e ferragens do marco (`group.create_group`), cada malha
  marcada `collision.OPENING_FRAME_PROP` = nome do grupo (a folha não esbarra no próprio marco), `_align` (gira só o
  Empty para os eixos da caixa, peças ficam) e `_parent_keep` na caixa; por folha: grupo **LEAF** com a malha,
  ferragens filhas da **folha** (o eixo de giro é o canto da folha), alinhado e filho do FRAME; `leaf.make_leaf`:
  janela `SLIDE` (`POS_X` para a folha 0, `NEG_X` para a 1, `travel` gravado), porta `SWING` (`hinge` pela dobradiça,
  dupla = esquerda/direita, `swing_sign` `OUT` se Swing Inside, `max_angle` 90°); restaura abertura e produção; grava
  `kind`, `assembly = frame`, `signature`, `model_version`; `_style_cage`: caixa em `WIRE`, `hide_set` conforme
  `home_builder.show_entry_door_and_window_cages`, texto "DOOR"/"WINDOW" (`FONT` ou "Text" no nome) oculto.
- `openings(scene)`, `outdated(scene)`: caixas com `model_version < MODEL_VERSION` ou sem montagem.

### 9.7 Operadores (`ops.py`, `region.py`) 🟢

- `caffmob.openings_update` (`REGISTER`, `UNDO`): `sync(force=True)` em cada `outdated`; nunca roda sozinho (a barra
  lateral só avisa).
- `btm.door_invert_hand` (`REGISTER`, `UNDO`; tecla **I** em "Object Mode", `head=True`): `poll` exige ativo
  selecionado dentro de uma porta **com símbolo** (`door_of`); inverte `Is Left` e re‑sincroniza; se o ativo sumiu
  (folha refeita) seleciona a primeira malha nova ou a caixa.
- `caffmob.wall_region` (`PlacementMixin`): `poll` exige OBJECT e alguma parede na cena. Primeiro clique: `ray_cast`
  subindo até `IS_WALL_BP`, lado `BACK` se `y local > espessura/2`, canto no plano da face (`intersect_line_plane`),
  na grade de 10 mm (Shift: 1 mm, `hb_snap.snap_value_to_grid`) e preso a `[0, Length] × [0, Height]`; segundo clique
  grava `btm_wall_region` (`x0 < x1`, `z0 < z1`) e reporta "Região marcada: L × A". Esc/botão direito cancelam;
  botão do meio e roda passam. `_live` guarda a prévia.
- `caffmob.wall_region_clear`: `poll` exige região ativa; keymap `ESC PRESS` em "3D View".
- Um único `draw_handler` `POST_PIXEL` (`draw_regions`) registrado no `register` e removido no `unregister`: retângulo
  preenchido (azul 18%) e contorno (2 px) no plano da face, com o texto "L × A" centralizado (`blf` 14 px × `ui_scale`).
  `on_load_post` limpa prévia e região.

### 9.8 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `LEAF_T`, `FLOOR_GAP`, `MARCO`, `GAP`, `TOP`, `CENTER_GAP` | 40, 8, 46, 3, 59, 3 mm | `door_core.py` | Folha, folgas, marco |
| `HANDLE_Z` | 1,02 m | `door_core.py` | Altura das maçanetas |
| `PROFILE`, `SASH`, `SASH_DEPTH`, `GLASS_T`, `OVERLAP`, `SILL_T`, `SILL_OUT` | 40, 35, 30, 4, 50, 20, 30 mm | `window_core.py` | Janela de correr |
| `MIN_SIZE`, `TOLERANCE` | 1 mm, 5 mm | `region_core.py` | Região vazia; clique quase fora vale a borda |
| `SWING_MAX` | 90° | `sync.py` | Abertura máxima da folha |
| `MODEL_VERSION` | 1 | `props.py` | Versão do gerador (dispara "Atualizar") |
| `KIND_ITEMS` | NONE, DOOR, DOUBLE_DOOR, OPEN_DOOR, WINDOW | `props.py` | Tipo montado |
| `BEVEL` | 1 mm, 2 segmentos | `build.py` | Chanfro |
| `SPECS` | 8 materiais | `materials.py` | Nogueira, inox, EPDM, cavidades, latão, alumínio, vidro, granito |
| Grade da região | 10 mm (Shift 1 mm) | `region.py` via `hb_snap` | Cantos |
| `FILL`, `LINE` | azul 18% / 95% | `region.py` | Desenho da região |

Tratamento de erros: `_swing` engole exceções do `get_input` (`except Exception`) e assume porta simples à esquerda
abrindo para dentro (🟡); `clear` só remove objetos ainda existentes e malhas sem usuários; keymaps protegidos; classes
desregistradas só se `is_registered`. `materials._image` devolve `None` sem o arquivo e a nogueira fica sem textura.

Testes: `tests/test_door_core.py` (furo pela folha, folha 40 mm a 8 mm do piso, marco, guarnições, ferragens fixas,
lado e sentido, dupla e vão aberto, papéis), `tests/test_window_core.py`, `tests/test_wall_region_core.py` (encaixe e
recusas), `tests/blender_010_openings_smoke.py`, `tests/blender_011_region_smoke.py`,
`tests/blender_bug_porta_real_abre.py`, `tests/blender_toast_resize_invert.py`, `tests/blender_011_component_smoke.py`.
`data/translations/openings.json` (25 chaves).

## 10. Módulo `aggregates` (`caffmob_draw/aggregates/`)

Agregados e folhas de porta convertidas (feature 003, blocos B e folha; RN‑07 a RN‑13, D‑12 a D‑20), grupos de peças,
esquadria importada e janela na parede (feature 007; RN‑01 a RN‑09, D‑01 a D‑14), importação de SketchUp pelo OpenSKP
(feature 009; RN‑13, RN‑14) com árvore de instâncias (feature 010; RN‑07 a RN‑09), e a exclusão por componente em lote
(features 011 e 012). 26 arquivos, 3.000 linhas, o maior módulo do ciclo forward:

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `limits.py` (103), `sweep.py` (48), `slide_limits.py` (35), `grouping.py` (39), `import_units.py` (18), `skp_core.py` (206) | não | Limites na face do pai, varredura com parada no contato, batentes de correr, sugestão de grupos, unidade de importação, plano/árvore do SketchUp |
| Dados | `props.py` (141), `group_props.py` (43), `window_props.py` (29) | sim | `Object.btm_aggregate`, `Object.btm_group`, `Object.btm_window` |
| Aplicação | `apply.py` (116), `convert.py` (84), `leaf.py` (294), `collision.py` (171), `perforate.py` (161), `production.py` (22), `group.py` (112), `install.py` (110), `skp.py` (36), `skp_build.py` (121) | sim | Posição, conversão, pivô da folha, BVH, recorte, peça de produção, grupo, instalar, leitura e montagem do SKP |
| Interface | `ops_aggregate.py` (322), `ops_group.py` (197), `ops_import.py` (181), `ops_install.py` (98), `overlay.py` (138), `panels.py` (146) | sim (`gpu`, `blf`) | Operadores, importador, simulação gráfica da folha, painel |

`__init__.py` registra (import tardio) `props`, `group_props`, `window_props`, `apply`, `collision`, `ops_import`,
`ops_aggregate`, `ops_group`, `ops_install`, `overlay`, `panels`. Dependências: `inspection/fronts.module_root_of`,
`cutting/machining.AGGREGATE_PREFIX`, `hb_types` (`GeoNodeCage`, `GeoNodeCutpart`, `GeoNodeWall`, `GeoNodeObject`),
`compat.try_get_gn_input/try_set_gn_input`, `operators/doors_windows.cut_wall`, `selection/component`,
`stick/apply.stuck_items`, `stick/link.release`, `ui/save_feedback`, `data/i18n`, `data/units`, wheels `openskp`
(+ `defusedxml`, `mapbox_earcut`, `shapely`) via `blender_manifest.toml`. Dependentes (15): `cabinet_editor/scene_slides`,
`cutting/part_sources`, `inspection/adapters/aggregate_leaf`, `legacy/convert`, `move_over/scene`,
`object_library/item_io`, `openings/sync`, `operators/doors_windows`, `selection/element_size`, `selection/resize`,
`stick/frame`, `stick/link`, `stick/props`, `ui/object_properties`, `__init__`.

### 10.1 Limites e posição (`limits.py`, `apply.py`) 🟢

Referencial local do pai, caixas `(lo, hi)`. O agregado fica preso a uma face (`FACES` = `POS_X`, `NEG_X`, `POS_Y`,
`NEG_Y`, `POS_Z`, `NEG_Z`; `FACE_LABELS` Direita/Esquerda/Fundo/Frente/Topo/Base): `u`, `v` = distância do canto mínimo
do pai ao canto mínimo do agregado nos dois eixos da face; `offset` = distância da face à face do agregado voltada
para ela (> 0 afasta, < 0 afunda).
- `face_axes(face)` → (eixo normal, sinal, eixo u, eixo v). `nearest_face(parent_box, point)`: menor distância do
  centro às seis faces. `limits()`: `u` ∈ [0, `ps[u] − size[u]`] (agregado maior que a face fica preso em 0, RN‑08),
  idem `v`, `offset` ∈ [`−ps[n]`, ∞) (afunda no máximo a espessura, RN‑09). `clamp`, `box_for(..., clamp_to_face=True)`
  (o grudar da 004 usa `False`), `params_from_box` (inverso sem clamp), `sunk_box` (interseção com o pai, `None` se
  não afunda), `sunk_depth`.
- `apply.local_box` (bound box avaliado), `box_in_parent`, `parent_box`, `current_box` (`location + rest_offset`, +
  `size`). `_write(obj, name, value)` grava sem disparar o `update` (`props._guard`). `update_position(obj)`: só para
  agregado `AGGREGATE` com `parent_ref` igual ao pai Blender; `clamp` → grava `u`/`v`/`offset` ajustados → `location =
  lo − rest_offset` → `perforate.sync` se há recorte. `aggregates_of(parent)`. Handler `@persistent
  on_depsgraph_update`: para cada `update.is_updated_geometry` de `Object` com agregados, compara `local_box` com a última
  (`_last_parent_box`) e reposiciona os filhos só quando o pai mudou de tamanho; trava `_busy`. (`_last_parent_box = {}`
  está declarado duas vezes, antes e depois do handler: o segundo é redundante 🟡.)

### 10.2 Converter e desconverter (`convert.py`) 🟢

`can_convert(obj, parent)`: malha ou grupo de peças; pai obrigatório (ativo); pai não pode ser o objeto nem filho dele;
objeto grudado (`btm_stick.is_stuck`) recusa; pai folha `LEAF` recusa. `convert(obj, parent, face=None)`: guarda
`orig_parent`/`orig_matrix` na primeira conversão; parenta mantendo o mundo; `face` = `nearest_face` do centro;
`size`, `rest_offset = box_a.lo − location`, `u/v/offset` por `params_from_box`; `parent_ref`, `is_aggregate`;
`update_position`. `unconvert(obj)`: remove recorte e furo real, pivô da folha, marcação de produção; devolve pai e
matriz originais; `kind = AGGREGATE`, `parent_ref = None`.

### 10.3 Folha de porta (`leaf.py`, `sweep.py`, `slide_limits.py`) 🟢

- Um Empty de pivô "`<folha> - Eixo`" filho do pai, com a folha filha dele; pose fechada em `obj['btm_leaf_rest']`
  (espaço do pai); `pivot['btm_leaf_base']`, `pivot['btm_open_fraction']`. Abrir nunca altera a malha.
- `base_point(box, motion, hinge)`: `SLIDE` → `lo`; `LEFT` → (`lo.x`, `lo.y`, `lo.z`); `RIGHT` → `hi.x`; `TOP` →
  `hi.z`; `BOTTOM` → `lo`. `swing_angle` = `OUT_SIGN[hinge] × (+1 OUT / −1 IN) × fração × max_angle`;
  `pose_matrix`: translação ao longo de ±X × `travel` × fração (correr) ou `Translation(base) @ Rotation(ângulo, Z ou X)`.
- `make_leaf(obj, parent, motion, hinge, swing_sign, max_angle=90, slide_dir, travel=0.5)`: grava `REST_KEY`, campos,
  `parent_ref`, `is_aggregate`; nas folhas irmãs de uma esquadria grava `rest_overlap` (sobreposição dos montantes no
  arquivo, D‑10); `rebuild_pivot`. `rebuild_pivot`: cria/reusa o pivô (`SINGLE_ARROW` giro / `PLAIN_AXES` correr),
  `matrix_basis = Translation(−base) @ rest`, fração 0; folha de correr numa esquadria mede `measure_free_travel`;
  `update_open`. `remove_pivot` devolve a pose fechada e apaga o pivô.
- Esquadria (`frame_of`, `sibling_leaves`, `frame_span`): `default_slide_dir` para o próprio lado (RN‑07a);
  `measure_free_travel`: sonda `travel = largura da esquadria`, varre até o contato → `free_travel` e `travel = max(free,
  1 mm)`, peça de contato em `btm_free_contact` (RN‑07, D‑09); `low_travel` se `free < 10 %` da largura da folha (D‑08).
- `update_open(obj, context)` (RN‑11a): `sweep` de `current` a `target` com `collision.Tester.hit`; passos
  `SWING_STEP` 2°/`SWING_TOLERANCE` 0,25° ou `SLIDE_STEP` 10 mm/`SLIDE_TOLERANCE` 1 mm; na esquadria também testa ao
  fechar com `floor` = `_close_floor` (batente pela outra folha: `close_stop(sinal, deslocamento da outra)`); grava a
  fração alcançada, `contact_name` (ou a peça do fim do curso livre) e `contact_kind` `OPEN`/`CLOSE`.
- `sweep.sweep(current, target, hit, step, tolerance, close, floor, floor_contact)`: fechar sem `close` é livre;
  abrindo, avança em `step` e no primeiro contato bissecta até `tolerance`, devolvendo o último valor livre; com
  `close`, fechar é a mesma varredura espelhada, não passando de `floor`.
- `slide_limits`: `default_direction` (centro da folha vs. da esquadria), `sign`, `low_travel` (`LOW_TRAVEL_RATIO`
  0,10), `rest_overlap`, `close_stop(open_sign, other_shift) = max(0, open_sign × other_shift)`.

### 10.4 Contato (`collision.py`) 🟢

Pré‑filtro por caixa e `BVHTree.overlap`. A folha numa pose é a caixa dela (8 cantos encolhidos `SHRINK` 1 mm).
`_excluded`: a própria folha, pivô e descendentes; na esquadria, as folhas irmãs e o pai (as peças da esquadria
**contam**, D‑07); fora dela, a raiz do módulo do pai e tudo abaixo. `_targets(obj)` (cache por folha): malhas visíveis
fora `WIRE`/`BOUNDS`, `IS_CUTTING_OBJ` e `IS_2D_ANNOTATION`, e fora as peças com `btm_opening_frame` igual ao pai
(marco da porta real, 010). `_bvh` constrói a BVH do alvo sob demanda (`to_mesh`/`to_mesh_clear`). `Tester(obj)`:
`corners_at(fraction)` = `parent_world @ pose_matrix @ matrix_basis @ cantos`; `hit(fraction)` → primeiro alvo cuja BVH
cruza a caixa. Handler `on_depsgraph_update`: qualquer `Object` atualizado fora das folhas e pivôs em cache limpa o
cache.

### 10.5 Recorte, furo real e peça de produção (`perforate.py`, `production.py`) 🟢

- 3D: `_sync_boolean`: cortador "`<agregado> - Recorte`" (caixa do volume afundado expandida `EPSILON` 1 mm além da
  face de entrada e, se atravessa, da oposta), filho do pai, `IS_CUTTING_OBJ`, `WIRE`, oculto; malha refeita só quando
  `btm_box` muda (evita laço com o depsgraph); modificador `BOOLEAN DIFFERENCE EXACT` "Agregado (furo): `<nome>`" no pai.
- Furo real: `real_hole_reason`: o pai precisa ter modificador `GeoNodeCutpart` e a face ser `POS_Z`/`NEG_Z` (entra pela
  chapa). `_sync_cutout`: `CPM_CUTOUT` "`machining.AGGREGATE_PREFIX + nome`" no pai, com `X`, `End X`, `Y`, `End Y`
  (espelhados se `Mirror Y`), `Route Depth = min(afundamento, Thickness)`, `Flip Z = (face == NEG_Z) != Mirror Z`; o
  plano de corte exporta em `machining`.
- `sync(obj)`: `perforate` desligado ou sem afundamento remove tudo; senão booleano e, com `real_hole` possível, o cutout.
- `production.sync`: `btm_geometry.fabrication = production_part`; `sheet(obj)` → (nome, maior, média, menor medida).

### 10.6 Grupos de peças e esquadria (`group_props.py`, `group.py`, `grouping.py`, `ops_group.py`) 🟢

- `Object.btm_group`: `is_group`, `kind` (`PLAIN` grupo, `FRAME` esquadria, `LEAF` folha), `members[]` com `obj`,
  `orig_parent`, `orig_matrix` (desfazer sem perda, RN‑04).
- `group.create_group(objs, kind, name)`: Empty `CUBE` 5 cm no centro da base da caixa mundial das malhas; herda o pai
  comum; cada peça vira filha mantendo o mundo. `ungroup` devolve ao pai original na posição **atual** e apaga o Empty.
  `object_corners` (Empty → união das malhas filhas), `world_box`, `group_box(group, space)`, `box_corners` na ordem do
  `bound_box`.
- `grouping.suggest(names)`: peças cujo nome começa por `Folha`/`Leaf`/`Sash` agrupadas pelos dois primeiros tokens
  (`Folha_Esquerda_Vidro` → `Folha_Esquerda`); o resto é "Esquadria"; sufixos `.001` ignorados; folhas ordenadas,
  esquadria por último.
- `caffmob.group_create` (nome sugerido), `caffmob.group_dissolve` (desconverte as folhas e o grupo antes de desfazer),
  `caffmob.window_assemble`: linhas `BTM_PG_AssembleRow` (rótulo, nomes, contagem, papel `FRAME`/`SLIDE`/`SWING`/
  `IGNORE`) sugeridas por `grouping`; cria a esquadria `FRAME`, uma folha `LEAF` por linha (filha da esquadria) e
  `make_leaf` `SLIDE` (sentido padrão para o próprio lado, que refaz o pivô e mede o curso) ou `SWING`; grupos `PLAIN`
  da importação são desfeitos antes.

### 10.7 Janela na parede (`window_props.py`, `install.py`, `ops_install.py`) 🟢

`Object.btm_window` (`frame`, `frame_matrix`) na jaula. `install(context, frame, wall, sill=1,0 m)`: `GeoNodeCage`
"Window" com `IS_WINDOW_BP`, `WIRE`, `Dim X/Z` = largura/altura da esquadria, `Dim Y` = espessura da parede; filha da
parede em `(x, 0, sill)` com `x` preso a `[0, Length − largura]`; a esquadria vira filha da jaula em `(0, 0, −lo.z)` com
drivers `x = Dim X/2`, `y = Dim Y/2` (continua centrada quando o editor de paredes muda a espessura); `cut_wall`.
`uninstall`: remove drivers, solta a esquadria no mundo, tira o booleano da parede, apaga a jaula. `can_install`: só
parede HB ("Converta a parede pelo editor de paredes antes de instalar").

### 10.8 Importar modelo (`ops_import.py`, `import_units.py`, `skp*.py`) 🟢

- `caffmob.import_model` (`ImportHelper`, `*.obj;*.fbx;*.glb;*.gltf;*.skp`): `unit` (`AUTO`, `MM`, `CM`, `M`, `IN`) e
  `up_axis` (`Z`, `Y`). OBJ/FBX recebem o eixo no importador nativo; a escala é aplicada depois sobre as raízes
  (`_apply_unit`: `AUTO` mede o modelo em escala 1, > `AUTO_LIMIT` 50 unidades = mm; a escala vai para a malha quando
  `data.users == 1`, D‑01); glTF é métrico e Y‑up por especificação. `_group_import` (011, D‑09): com 2+ malhas, várias
  raízes malha → grupo `PLAIN` novo com o nome do arquivo; uma raiz Empty → ela vira o grupo; mistas → só as malhas
  de topo.
- SketchUp (`_import_skp`): `skp.read` (OpenSKP: `SkpFile.parse` + `build_scene`; sem a wheel, `ValueError` com o motivo;
  sem geometria idem) → `skp_build.build`; falha na montagem apaga o que foi criado; relatório com grupos e figuras de
  escala ignoradas; `progress_begin/end`.
- `skp_core` (puro): `to_blender((x, y, z)) = (x, −z, y)` (glTF Y‑up → Z‑up); UV `v` invertido; `material_names`
  casa os materiais glTF com os do SketchUp pela imagem ou pela cor RGB (0–255), senão "SketchUp padrão";
  `clean_material_name` tira `Layer_`; `is_scale_figure` (regex de "2D Woman/Man/Person…" e nomes próprios do SketchUp).
  `tree(scene, model)`: nós da `scene_hierarchy` sem as figuras (e sem a geometria dos caminhos banidos); instâncias
  repetidas (mesmo `path`) recebem a primitiva mais perto da própria `position_mm`; versos emitidos à parte (mesmos
  vértices) são descartados; `_prune` colapsa contêiner sem malha com um filho só; geometria sem nó vai para um grupo
  "SketchUp". `texture_filename` seguro; `failure_message`.
- `skp_build.build`: percorre a árvore criando filhos primeiro; malha por primitiva (`from_pydata`, UV, material);
  material reaproveitado por assinatura `nome|cor|imagem` (`btm_skp_key`, RN‑09); texturas gravadas em pasta temporária
  e empacotadas (`Image.pack`); grupo `PLAIN` por instância (`create_group`) ou Empty contêiner; filhos parentados ao
  pai mantendo a posição.

### 10.9 Operadores de agregado e exclusão (`ops_aggregate.py`) 🟢

- `caffmob.aggregate_convert` (malhas/grupos selecionados + pai ativo; `face` AUTO ou fixa), `caffmob.leaf_convert`
  (diálogo com movimento, eixo, sentido, ângulo 1–180°, ou sentido e curso), `caffmob.aggregate_unconvert`.
- `caffmob.aggregate_move` (`BLOCKING`): arrasta no plano da face do pai (`intersect_line_plane`), somando o `Δ` local
  a `u`/`v`; o `update` aplica o limite; Esc restaura.
- `caffmob.delete_with_aggregates` (teclas **X** e **Delete** em "Object Mode", `head=True`; `poll` só com descendentes
  apagáveis, agregados ou grudados): pergunta "Apagar também os agregados" só quando há agregados próprios;
  `delete_components(targets, keep_aggregates)`: solta os grudados avisando "Vínculo perdido" (`save_feedback`),
  `component.delete_plan`, desconverte os agregados mantidos, remove o booleano do vão na parede, apaga cortadores
  órfãos e tudo em lote com `bpy.data.batch_remove` (012: um a um custava segundos).

### 10.10 Simulação gráfica e painel (`overlay.py`, `panels.py`) 🟢

Dois handlers (`POST_VIEW` 3D e `POST_PIXEL` 2D) registrados com o add‑on: com uma folha ativa (malha, pivô ou peça de
grupo‑folha), desenha o caminho da borda livre em 24 passos, o eixo (ou o trilho), a caixa atual (vermelha se bateu),
a caixa da peça de contato e o texto "Folha bateu em" / "Folha encostou em". `panels.draw_aggregate` é desenhado pela
barra lateral única da 005 (`BTM_PT_Aggregate` definido mas não registrado): importar, converter, montar esquadria,
grupos, Instalar/Desinstalar, campos do agregado com mín./máx., Perfurar, Furo real (com o motivo), Peça de produção
(componente e material de `btm_geometry`), ou da folha (movimento, eixo, sentido, ângulo/curso, aviso de pouco curso,
barra de abertura, contato, pivô ausente).

### 10.11 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `FACES` | 6 faces | `limits.py` | Face do pai |
| `SWING_STEP` / `SWING_TOLERANCE` | 2° / 0,25° | `sweep.py` | Varredura do giro |
| `SLIDE_STEP` / `SLIDE_TOLERANCE` | 10 mm / 1 mm | `sweep.py` | Varredura do correr |
| `LOW_TRAVEL_RATIO` | 0,10 | `slide_limits.py` | Aviso de pouco curso |
| `SHRINK` | 1 mm | `collision.py` | Encolhe a caixa da folha |
| `EPSILON` | 1 mm | `perforate.py` | Cortador além da face |
| `DEFAULT_SILL` | 1,0 m | `install.py` | Peitoril padrão |
| `AUTO_LIMIT`, `SCALE` | 50; mm 0,001, cm 0,01, m 1, pol 0,0254 | `import_units.py` | Unidade automática |
| `max_angle` | 90° (1–180) | `props.py` | Abertura máxima |
| `travel` | 0,5 m (≥ 1 mm) | `props.py` | Curso padrão |
| `ARC_STEPS` | 24 | `overlay.py` | Caminho da borda livre |
| `LEAF_WORDS`, `FRAME_NAME` | folha/leaf/sash; "Esquadria" | `grouping.py` | Sugestão de grupos |
| Teclas | X, Delete | `ops_aggregate.py` | Apagar com agregados |

Tratamento de erros: `ReferenceError` capturado no handler de posição, em `pivot_of`, `_stuck_children` e
`_children_aggregates`; importação nativa com `RuntimeError` → `report({'ERROR'})`; SKP com `ValueError` do leitor e
`Exception` na montagem (desfaz o criado); `batch_remove` só dos vivos; keymaps protegidos.

Testes (18): puros `test_aggregate_limits`, `test_leaf_sweep`, `test_slide_limits`, `test_grouping`, `test_import_units`,
`test_skp_core`, `test_skp_tree`; fumaça `blender_003_aggregates_smoke`, `blender_004_collision_smoke`,
`blender_007_window_smoke`, `blender_009_skp_smoke`, `blender_010_skp_tree_smoke`, `blender_010_openings_smoke`,
`blender_011_component_smoke`, `blender_011_drag_probe` (janela), `blender_012_apply_smoke`, `blender_toast_resize_invert`,
`blender_bug_skp_mover_sobre`. `data/translations/aggregates.json` (129 chaves).

---

## 11. Módulo `collision` (`caffmob_draw/collision/`)

Colisão de corpo entre itens e com paredes, obstáculos, piso e teto (feature 004, incremento I2; RF‑20 a RF‑26,
RN‑11 a RN‑14, D‑12 a D‑19). 9 arquivos, 986 linhas. É a verificação "depois do fato": o item fica onde foi solto e o
sistema só avisa, destaca e oferece "Afastar até encostar" (RF‑23). Não confundir com `aggregates/collision.py`
(contato da folha de porta por BVH) nem com `hb_placement.avoid_overlap` (bloqueio durante o arrasto legado):

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `obb.py` (86), `rules.py` (130) | não | Caixa orientada e teste dos eixos separadores; itens, pares, exclusões, classificação e ordem |
| Dados | `props.py` (52) | sim | `WindowManager.btm_collision` (sessão, não salvo) |
| Aplicação | `scan.py` (273), `stale.py` (66) | sim (`BVHTree`) | Coleta da cena, confirmação pela malha, gravação do resultado; marcador "desatualizado" |
| Interface | `ops_collision.py` (143), `overlay.py` (94), `panels.py` (118) | sim (`gpu`, `blf`) | Verificar, Ir para, Limpar, Afastar; contorno + rótulo na viewport; painéis |

`__init__.py` registra (import tardio, para os testes puros não carregarem `bpy`) `props`, `stale`, `ops_collision`,
`overlay`, `panels`. Dependências: `selection/classify` (`classify`, `movable_root`, `reference_root`, tipos),
`stick/apply` (`local_box`, `linked`, `face_of`, `project`), `stick/ops_stick.item_of`, `ui/save_feedback.show`,
`data/i18n.tr`, `data/properties` (`btm_plane.collision_override`, `btm_settings.collision_global`). Dependentes (6):
`__init__` (registro), `stick/settle._check_collisions` → `scan.check_moved` (fim do assentar do grudar),
`ui/sidebar_check` e `ui/object_properties` (desenham os painéis na barra lateral única da 005), `ui/save_feedback`
(`_collision_note` lê `btm_collision` no `save_post`, RF‑27), `cabinet_editor/validate` (reusa `obb.from_box` e
`obb.overlap` para peças do construtor).

### 11.1 Caixa orientada (`obb.py`) 🟢

`OBB(center, axes, half)` imutável: centro no mundo, três eixos unitários, meias medidas. `corners()` gera os oito
cantos na ordem binária (sx, sy, sz) ∈ {−1, +1}³, a mesma que `overlay._EDGES` e as seis faces de `scan._Meshes`
assumem. `aabb()` = caixa alinhada ao mundo pela soma `|axes[i][k]| · half[i]`. `from_box(origin, axes, lo, hi)`
converte a caixa local `(lo, hi)` (já escalada) de um objeto: centro = origem + eixos · ponto médio; meias medidas =
`|hi − lo| / 2`.

`overlap(a, b)`: teste dos eixos separadores (SAT) com 15 eixos: 3 de A, 3 de B, 9 produtos vetoriais (os quase nulos,
comprimento < 1e‑6, são pulados: caixas paralelas). Para cada eixo normalizado, `amount = raio(A) + raio(B) − |t·eixo|`,
com `raio = Σ half[i] · |axes[i]·eixo|`. Qualquer `amount < −1e‑9` → `None` (separadas). Senão guarda o menor
`amount` como profundidade e `push` = eixo × sinal × profundidade, com o sinal escolhido para afastar A de B
(`−1` quando B está no lado positivo). Devolve `{'depth', 'push', 'axis'}` (`axis`: 0–2 eixos de A, 3–5 de B, 6+
cruzados). `aabb_overlap(a, b, margin)` é o pré‑filtro barato.

### 11.2 Regras do par (`rules.py`) 🟢

`Item(name, box, kind, root, linked, override)`: `kind` ∈ `ITEM`, `WALL`, `OBSTACLE`, `FLOOR`, `CEILING`
(`STATIC` = os quatro últimos); `group` = `root or name`; `linked` = nomes ou raízes que ele pode tocar.
`Conflict(kind, name_a, name_b, depth, push, location)` imutável.
- `excluded(a, b)` (RN‑12): dois estáticos; qualquer `override == 'OFF'`; mesmo `group` (peças do mesmo módulo);
  um nome ou grupo em `linked` do outro (agregado × pai, grudado × hospedeiro, porta/janela × parede).
- `conflict_kind`: parede ou obstáculo no par → `WALL`; senão piso ou teto → `FLOOR_CEILING`; senão `ITEM`.
- `candidate_pairs(items, only)`: varredura ordenada em X das AABBs (`sort` por `x_min`, depois nome); o laço interno
  para quando `x_min(B) > x_max(A) + TOLERANCE`. `only` restringe aos pares que envolvem esses nomes. Aplica `excluded`
  e `aabb_overlap` com a tolerância como margem.
- `evaluate(a, b)`: `overlap` das OBBs; `depth ≤ TOLERANCE` (1 mm) → `None` (encostar não é colisão, RN‑11). Reordena
  para que `name_a` seja o item móvel: estático vai para `b`; entre iguais, o de nome menor fica em `a`, com `push`
  invertido quando troca. `location` = média dos dois centros (ponto do rótulo).
- `sort_key` (RN‑13): tipo (`WALL` 0, `ITEM` 1, `FLOOR_CEILING` 2), profundidade decrescente arredondada a 6 casas,
  nomes. `conflicts(items, confirm, only)`: pares → `evaluate` → `confirm(a, b)` opcional (malha) → ordenação estável.

### 11.3 Varredura na cena (`scan.py`) 🟢

- `_skip`: `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x`, `hide_viewport`, `not visible_get()`
  (`RuntimeError` → pula).
- `box_of(obj, depsgraph)`: `stick/apply.local_box` do avaliado → decompõe `matrix_world` em (loc, rot, scale); eixos =
  colunas da rotação; `lo`/`hi` escalados e reordenados (escala negativa) → `obb.from_box`.
- `_kind_of(obj)` → `(tipo, raiz, confirmar pela malha)` ou `None`, nesta ordem: malha com `btm_wall_segments` →
  `WALL` fino; `btm_aggregate.is_aggregate` → `ITEM` com raiz vazia (o agregado é o próprio grupo) e fino;
  `IS_APPLIANCE` → `ITEM`; depois `classify.classify`: só quando `info.obj is obj` (peças e frentes não entram
  sozinhas, a caixa da raiz cobre o módulo); `MODULE`/`GEOMETRY` → `ITEM`; `ROOM_DOOR`/`WINDOW` → `ITEM` fino;
  `WALL` e `OBSTACLE` → finos; `FLOOR`/`CEILING`; `OTHER` só se malha solta sem pai e não `WIRE`/`BOUNDS` → `ITEM`
  fino. `_FINE_KINDS` força fino para parede e obstáculo.
- `_links(obj)`: pai do agregado (`btm_aggregate.parent_ref`) e sua raiz; hospedeiro do grudado (`btm_stick.host`) e
  raiz; para porta de entrada, janela (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP` ou `classify.WINDOW`) cujo pai é parede
  (`IS_WALL_BP` ou `btm_wall_segments`), o nome da parede. `_override` lê `btm_plane.collision_override`
  (`INHERIT` sem `btm_plane`). `_root_name` = `movable_root` ou `reference_root` ou o próprio.
- `collect(scene, depsgraph)` → lista de `_Entry(item, obj, fine)`. `_Meshes.tree(entry)`: BVH em cache por
  `as_pointer()`; malha avaliada (`to_mesh` → vértices no mundo → `FromPolygons` → `to_mesh_clear` em `finally`), com
  recuo para os 8 cantos e 6 faces da OBB quando não há malha. `_confirm`: só quando um dos dois é fino, `ta.overlap(tb)`
  (respeita o vão de uma porta na parede, D‑13).
- `find(context, only)` → `(ocorrências, entradas)`. `check_all(context, scope)`: `only = selected_names` (raízes
  móveis dos selecionados) em `SELECTED`; qualquer exceção vira `state.error` com a lista vazia e `stale = False`
  (RF‑25: nunca "sem colisões"); `_store` grava linhas, `checked`, `checked_names` (ordenados, separados por `\n`),
  `scope`, zera `stale`/`error`, `stale.reset()`; `_redraw` nas áreas `VIEW_3D` e `PROPERTIES`.
- `check_moved(objs)` (D‑16, RF‑23): sai se `collision_global` desligado; nomes = objetos vivos + `children_recursive`
  (agregados e grudados que andam junto); `find(context, names)`; exceção → `[]` silencioso 🟡 (diferente de
  `check_all`, que mostra o erro); mantém as linhas que não envolvem os movidos e acrescenta as novas;
  `stale.rechecked(names)`; para cada ocorrência, `save_feedback.show("<movido> colide com <outro>")`.
- `enabled(scene)`: `btm_settings.collision_global` (ligado quando a propriedade não existe).

### 11.4 Desatualizado (`stale.py`) 🟢

Conjunto `_changed` em módulo. Handler `@persistent on_depsgraph_update` (padrão de `cutting/stale.py`): sai sem
estado ou com `checked < 0`; nomes vigiados = `checked_names` ∪ nomes das linhas; para cada `update` de geometria ou
transformação de `Object`, sobe pela cadeia de pais (`_checked_root`) até achar um nome vigiado e o acrescenta a
`_changed`; liga `state.stale`. `rechecked(names)` tira os nomes do conjunto e recalcula `stale = bool(_changed)` (só
com `checked ≥ 0`). `reset()` no `_store` e no `unregister`. Lê `bpy.context.window_manager` dentro do handler 🟡
(mesma observação de `aggregates`; funciona porque só roda no thread principal).

### 11.5 Operadores (`ops_collision.py`) 🟢

| `bl_idname` | Rótulo | `bl_options` | Comportamento |
|-------------|--------|--------------|---------------|
| `caffmob.check_collisions` | Verificar colisões | `REGISTER` | `scope` `ALL`/`SELECTED`; desligado → `WARNING` "Colisão desligada"; `SELECTED` sem seleção → `WARNING`; `check_all` `None` → `ERROR` com `state.error`; senão `WARNING` "N colisão(ões) em M item(ns)" ou `INFO` "Sem colisões em M item(ns)" |
| `caffmob.collision_goto` | Ir para a colisão | `REGISTER` | `index` válido; seleciona os dois visíveis, ativa o primeiro, `view3d.view_selected` em `temp_override` para cada área `VIEW_3D` com região `WINDOW` |
| `caffmob.collision_clear` | Limpar colisões | `REGISTER` | Esvazia a lista, `checked = −1`, `checked_names = ""`, zera `stale`/`error`, redesenha |
| `caffmob.collision_push_out` | Afastar até encostar | `REGISTER`, `UNDO` | Move `name_a` por `push`; item grudado (`stick/apply.linked`): projeta `push` no plano da face (`push −= n · (push·n)`, `n` = normal da face do hospedeiro no mundo); resultante < 1e‑6 → `WARNING` "não pode sair da face"; `translation += push`, `view_layer.update()`, `stick/apply.project` se grudado, `scan.check_moved([obj])`, `INFO` "<nome> afastado X mm" |

Nenhum operador é modal; não há `invoke`. Observação 🟡: o requirements (RF‑26) pede "com prévia"; o código aplica
direto com desfazer.

### 11.6 Destaque na viewport (`overlay.py`) 🟢

Dois handlers em `SpaceView3D` registrados com o add‑on (lista `_handles`, removidos no `unregister`): `_draw_3d`
(`POST_VIEW`) desenha as 12 arestas da OBB de cada item envolvido (até `MAX_ROWS = 30` linhas, sem repetir objeto,
só visíveis) com `POLYLINE_UNIFORM_COLOR`, `lineWidth 2.5`, sem teste de profundidade, cor `COLOR` vermelha ou
`STALE_COLOR` laranja quando desatualizado; `_draw_2d` (`POST_PIXEL`) escreve "<Tipo>: A × B" (+ "(desatualizado)")
em `blf` tamanho 13 com sombra preta deslocada 1 px, no ponto `location` projetado por `location_3d_to_region_2d`. Sem
ocorrências os handlers retornam cedo. `box_of` é recalculado a cada redesenho 🟡 (até 60 caixas).

### 11.7 Painéis (`panels.py`) 🟢

`draw_collisions(layout, context)`: linha com "Verificar colisões" (`ALL`), "Selecionado" (`SELECTED`) e `X` (limpar,
só com resultado). Estados, nesta ordem: desligado ("Ligue em Produção/Projeto › Configurações"); `error` (caixa
`alert`); nunca verificado (`checked < 0` e lista vazia); `stale` → caixa "Desatualizado, verifique de novo"; lista
vazia e não desatualizado → "Sem colisões em M item(ns)" (RN‑14: nunca "sem colisões" com `stale` ou `error`); lista →
"N colisão(ões):" e até `MAX_ROWS = 12` linhas "<Tipo>: A × B (P mm)" com `VIEWZOOM` (ir para) e `MOD_OFFSET`
(afastar), mais "… e mais K". `BTM_PT_ItemCollision` (`poll`: `item_of(active)` com `btm_plane`): `collision_override`
e até 5 linhas "Colide com <outro>". Como nos demais módulos da 005, `classes = ()`: `BTM_PT_Collisions` e
`BTM_PT_ItemCollision` não são registrados; `ui/sidebar_check` chama `draw_collisions` e `ui/object_properties` desenha
o painel do item pelo `sidebar_proxy`. `ui/sidebar_vocab` expõe `CHECK_ITEM` → `caffmob.check_collisions`.

### 11.8 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `TOLERANCE` | 0,001 m | `rules.py` | Encostar até 1 mm não é colisão (RN‑11); mesma de `inspection/interference.py` |
| `_EPS` | 1e‑9 | `obb.py` | Empate numérico do SAT |
| Eixos quase nulos | < 1e‑6 | `obb.py` | Produto vetorial de eixos paralelos é descartado |
| `ITEM`, `WALL`, `OBSTACLE`, `FLOOR`, `CEILING`; `STATIC` | — | `rules.py` | Tipos de item |
| `KIND_WALL`, `KIND_ITEM`, `KIND_FLOOR_CEILING`; `_ORDER` | 0, 1, 2 | `rules.py` | Tipos de ocorrência e prioridade (RN‑13) |
| `KIND_ITEMS` | Penetração em parede / Colisão entre itens / Piso ou teto | `props.py` | Rótulos do enum e dos painéis |
| `_SKIP_TAGS` | `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x` | `scan.py` | Fora da verificação |
| `_FINE_KINDS` | `WALL`, `OBSTACLE` | `scan.py` | Sempre confirmados pela malha |
| `COLOR` / `STALE_COLOR` | (1, 0,25, 0,2) / (1, 0,65, 0,2, 0,8) | `overlay.py` | Vermelho em dia, laranja desatualizado |
| `MAX_ROWS` | 30 (viewport) / 12 (painel) | `overlay.py` / `panels.py` | Teto de linhas desenhadas |
| `checked` | −1 = nunca verificado | `props.py` | Sentinela do estado |
| Chave global | `btm_settings.collision_global` ("Evitar Sobreposição", padrão ligado) | `data/properties.py:740` | Desligada: nada roda (D‑18) |
| Exceção por item | `btm_plane.collision_override` `INHERIT`/`ON`/`OFF` | `data/properties.py:240` | `OFF` tira o item de todos os pares |

Tratamento de erros: `check_all` captura `Exception` e grava `state.error` (visível no painel e no `report`);
`check_moved` captura e devolve `[]`; `_skip` e `_Meshes._build` toleram `RuntimeError` do Blender; `stale` tolera
`AttributeError` (sem `window_manager`); `_redraw` tolera `AttributeError`.

Testes (2): puro `test_collision_rules` (6 casos: encostados não colidem, penetração de 20 mm na parede, pares excluídos,
caixa girada, uma ocorrência por par com ordem estável, confirmação pela malha só no item); fumaça
`blender_004_collision_smoke` (balcão 20 mm dentro da parede → `('WALL', 'Balcao', 'Parede', 0.02)`; Ir para; Afastar
volta a `y = 0`; vizinho; porta na parede e nicho não contam; `_collision_note` do salvar; `stale` após mover;
`check_moved`; chave global desligada cancela; 4 vizinhas em ≤ 2 s). Textos em
`data/translations/editor_grudar.json` (136 chaves, compartilhado com `stick`).

---

## 12. Módulo `stick` (`caffmob_draw/stick/`)

Grudar itens em paredes, painéis e outras superfícies planas (feature 004, incremento I1; RF‑11 a RF‑19, RN‑05 a RN‑10a,
D‑01 a D‑11) e prévia do ímã durante o arraste (feature 005, RF‑14/RF‑15, D‑15). 11 arquivos, 1.486 linhas. O vínculo é
"parentesco Blender + `Object.btm_stick`": o item vira filho do hospedeiro com inversa identidade e o resto (face,
`u`/`v`/`distance`/`spin`) fica na propriedade. O vocabulário da interface é "Elemento filho de: <hospedeiro> — <face>",
sem a palavra "pai", para não confundir com o agregado da 003 (D‑11):

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `frame.py` (192) | não | Referencial da face (`BOX_SIDE`/`PLANE`), posição `(u, v, distance)`, fora da face, face plana, escolha da face |
| Dados | `props.py` (73) | sim | `Object.btm_stick` (salvo no `.blend`), `update` guardado |
| Aplicação | `apply.py` (335), `link.py` (175), `settle.py` (102), `migrate.py` (51), `magnet.py` (101) | sim | Posição e handler; grudar/desgrudar; assentar após o movimento; migração dos módulos na parede; ímã |
| Interface | `ops_stick.py` (232), `panels.py` (69), `magnet_preview.py` (131) | sim (`gpu`, `blf`) | Grudar, Desgrudar, Mover no plano; painel "Elemento filho"; prévia do ímã |

`__init__.py` registra (import tardio, `frame` testável sem `bpy`) `props`, `apply`, `ops_stick`, `panels`,
`magnet_preview`. Dependências: `aggregates/limits` (`FACES`, `FACE_LABELS`, `face_axes`, `thickness`),
`selection/classify`, `hb_types.GeoNodeWall` (espessura na migração), `hb_placement.PlacementMixin` (detecção de
modal), `ui/save_feedback`, `data/i18n`, preferências `stick_magnet`/`stick_magnet_distance` em
`caffmob_draw/__init__.py:198-208`. Dependentes (9): `__init__` (registro e `stick.migrate.run` no `load_post`),
`collision/scan`, `collision/panels`, `collision/ops_collision`, `aggregates/ops_aggregate` (apagar hospedeiro solta os
grudados), `aggregates/convert` (recusa item grudado), `selection/component`, `cabinet_editor/bridge` (`local_box`),
`ui/object_properties`, `ui/context_menu`, `ui/sidebar_vocab` (`STICK`, `RELEASE`, `STICK_MOVE`).

### 12.1 Referencial da face (`frame.py`) 🟢

Tudo no espaço local do hospedeiro. Uma face é `(origem, U, V, N)` com N para fora. Dois tipos (D‑02):
- `BOX_SIDE`: `box_frame(host_box, face)` põe a origem em `hi[n]` (sinal +) ou `lo[n]` (sinal −) do eixo normal e
  U/V nos outros dois eixos (ordem de `limits.face_axes`). Acompanha mudança de medida porque `u`/`v` partem da origem
  local do hospedeiro, que não se move ao redimensionar (RN‑08a).
- `PLANE`: `plane_frame(origin, normal, up)`: U = projeção de `up` (Z, ou X quando a normal é quase Z) no plano,
  V = N × U. Guardado como matriz 4×4 em `btm_stick.plane` (`frame_to_matrix`/`matrix_to_frame`, colunas U, V, N,
  origem). Acompanha mover e girar, não medida.
- `to_frame`/`from_frame` convertem ponto ↔ `(u, v, n)`. `footprint(frame, corners)` = caixa do item no referencial;
  `params` = canto mínimo da pegada = `(u, v, distance)` (0 = encostado, negativo = entra no hospedeiro). `shift`
  devolve o deslocamento local que leva o item aos valores pedidos (`None` mantém). `face_extent` = retângulo do lado;
  `out_of_face`: o centro da pegada saiu do retângulo com folga `OUT_TOLERANCE` (face `PLANE` nunca).
- `is_planar(points, normal)`: todos os vértices a ≤ 0,5 mm do plano pelo primeiro ponto (RN‑05). `choose_face(box,
  point, normal)`: percorre as 6 faces; normal a ≤ 1° do eixo (`cos`) e ponto a ≤ 0,5 mm do plano do lado → `BOX_SIDE`;
  senão `PLANE`. `contact_axis(normal)`: `|n·Z| ≥ 0,7` → `BOTTOM` (face deitada, a base do item encosta); senão `BACK`
  (face de pé, o fundo +Y local encosta).

### 12.2 Posição, handler e assentar (`apply.py`) 🟢

- Caixas: `local_box(obj)` = caixa do avaliado no espaço local (`bound_box` para `MESH`/`CURVE`/`FONT`/`SURFACE`/`META`);
  sem geometria própria, a união das caixas dos `children_recursive` (menos cortadores, anotações, `obj_x`), ou a origem.
  `item_corners(item, host)` = cantos do item no espaço do hospedeiro (`host.inv @ item.world`). `face_of(item)` →
  `(frame, extent)` do vínculo atual. Reusado por `collision/scan.box_of` e `cabinet_editor/bridge`.
- `write(item, name, value)` grava sem disparar `update` (chave em `props._guard`). `_translate_local` desloca via
  `matrix_world` (independente de `matrix_parent_inverse`); ignora `|delta| ≤ 1e‑9`.
- `linked(item)`: `is_stuck`, `host` presente e `item.parent == host`. `update_position(item)`: `shift` para
  `u`/`v`/`distance` → `_check_face` (grava `out_of_face` e avisa "Item fora da face" só na transição) → `last_world`.
  `project(item)`: item movido livremente (G nativo, campos) → `_flip_if_across` → recalcula `u`/`v` da posição em que foi
  solto e `update_position` restaura `distance` (RF‑13). `_flip_if_across`: só `BOX_SIDE`; se a pegada está além da
  espessura pela face atual (`d < −thickness − tol`) e não entra pela oposta, o vínculo troca para `_OPPOSITE[face]` com
  `distance` recalculado (o editor de paredes inverteu a direção e devolveu os filhos ao lugar no mundo).
  `update_spin`: gira pelo centro da pegada em torno da normal (mundo), por `spin − applied_spin`, depois reposiciona.
- `lose_link(item)` (RN‑08): restaura `last_world` quando o item ficou sem pai, zera `is_stuck`/`host`/`out_of_face`,
  invalida o índice, avisa "Vínculo perdido".
- Índice hospedeiro → itens (`_index`, `_index_ok`), reconstruído sob demanda varrendo `bpy.data.objects`;
  `stuck_items(host)`; `invalidate()`. Chave `''` = grudados sem hospedeiro (apagado).
- Handler `@persistent on_depsgraph_update` (D‑04): trava `_busy`; para cada `update` de `Object`: geometria de um
  hospedeiro com caixa diferente de `_last_box` → `update_position` em cada grudado (espessura da parede, largura do
  painel, RN‑07); transformação fora do período quieto → anota em `_pending`; grudados com hospedeiro `None` →
  `lose_link`; com pendentes, registra `_settle_timer` (0,2 s). O timer espera enquanto `modal_running()` (algum
  `window.modal_operators` é `transform.*`, um dos `_MOVE_IDS` ou um `PlacementMixin`) e depois chama `settle.run` uma
  vez. `on_load_or_undo` (`load_post`, `undo_post`, `redo_post`): `QUIET_SECONDS` = 0,6 s em que transformações não
  contam como gesto, limpa índice, `_last_box` e pendentes. `unregister` remove handlers e o timer.

### 12.3 Grudar e desgrudar (`link.py`) 🟢

- `host_for(obj)`: raiz do classificado (módulo para peça/frente, parede, geometria) salvo `OTHER`/`ANNOTATION`; objeto
  não reconhecido é o próprio hospedeiro (o vínculo sobrevive às bibliotecas que recriam peças).
- `can_stick(item, host)` → motivo ou `None`: sem item; sem hospedeiro; hospedeiro é o item ou filho dele; item é
  agregado ("desconverta antes de grudar").
- `oriented_matrix(world, normal)`: em face de pé (`BACK`), −Y do item = normal (o fundo encosta), Z = projeção de Z
  mundo no plano (ou do Z atual), X = Y × Z; em face deitada (`BOTTOM`), Z do item = ±normal (para cima), Y = projeção
  do Y atual. Mantém posição e escala (`LocRotScale`). `orient` aplica.
- `_attach`: guarda `orig_parent` (só na primeira vez), `parent = host`, `matrix_parent_inverse = I`,
  `matrix_basis = host.inv @ world` (D‑03, mesmo caminho de `aggregates/convert`).
- `stick(item, hit_obj, point, normal, polygon, center, rotate)`: `host_for` → `can_stick` → `is_planar` do polígono
  (no espaço do hospedeiro) ou `ValueError("A face não é plana")` → `orient` → `_attach` → `choose_face` →
  `box_frame` + `plane = IDENTITY` ou `plane_frame` + matriz → `params`; com `center`, centra a pegada no ponto clicado
  → `_record` (`spin`/`applied_spin` 0, `distance` 0, `is_stuck`) → `update_position` encosta.
- `link_in_place(item, host, face)` (D‑08): grava o vínculo `BOX_SIDE` com a posição atual (inclusive `distance`
  negativo), `orig_parent = host`; não move. `release(item)` (RN‑09): pai anterior (se não for o item nem descendente)
  mantendo o mundo, senão sem pai; zera o vínculo. `face_label`: "<hospedeiro> — frente/trás" para parede
  (`NEG_Y`/`POS_Y`), "plano" para `PLANE`, senão `FACE_LABELS`.

### 12.4 Assentar (`settle.py`) 🟢

`run(names)` trata cada objeto anotado uma vez, quando nenhum modal de movimento está rodando: pula quem voltou à pose
registrada em `_settled` (Esc no G, desfazer: não é gesto novo, o ímã não age); item grudado → `apply.project`;
vínculo quebrado → deixa para o handler; módulo ou geometria raiz (`_MAGNET_KINDS`) → se é filho de parede
(`migrate.wall_of`), `link_in_place` no lado certo (RF‑19, módulo novo posto pela biblioteca); senão `magnet.try_stick`
(RF‑12); grudou → toast "Elemento filho de: …" e `ed.undo_push("Grudar")` em `temp_override` da primeira janela; por
fim `collision.scan.check_moved(moved_roots)` (RF‑23). `is_move_operator(op)`: `bl_idname` normalizado
(`X_OT_y` → `x.y`) começa por `transform.` ou está em `_MOVE_IDS` (`stick_move`, `stick_to_face`, `aggregate_move`,
`move_on_wall`, `move_over_drag`, `move_over_dialog`, `cabinet_editor_modal`) ou é `PlacementMixin`.

### 12.5 Migração (`migrate.py`) 🟢

`run(scene)` no `load_post` (`__init__.py:102`): para cada módulo raiz (`classify.MODULE`, `info.root is obj`) sem
vínculo e filho de `IS_WALL_BP`, `link_in_place` na face dada por `wall_side`: `rotation_euler.z` ≈ 0 (< 0,01 rad) e
`location.y < espessura/2` → `NEG_Y` (frente); senão `POS_Y` (trás, giro de 180°), mesma regra de
`measure/scene_cotas._on_front_side`. Espessura via `GeoNodeWall.get_input('Thickness')` (0 em erro 🟡). Idempotente;
marca `btm_settings.stick_migrated = True`; devolve a contagem.

### 12.6 Ímã (`magnet.py`, `magnet_preview.py`) 🟢

- `preferences()` → `(ligado, distância)` das preferências do add‑on (padrão ligado, 50 mm, quando não instalado).
- `find(item, distance)`: raio a partir do centro do fundo do item (`hi[1]` da caixa local, +Y) na direção +Y mundo,
  começando 1 mm atrás; até `_MAX_STEPS = 8` acertos pulando o próprio item, descendentes, cortadores e anotações;
  `None` se o acerto passa da distância ou a face não está de frente (`n·dir > −0,7`) ou o hospedeiro é piso/teto
  (RN‑05). Devolve `(obj, ponto, normal, vértices do polígono)`.
- `preview_pose(item, hit, normal)`: cantos (mundo) da caixa do item com a orientação de `oriented_matrix` e deslocada
  pela normal até o canto mais próximo tocar o plano, sem alterar o objeto (ordem de `bound_box`). `try_stick(item)` →
  `link.stick(..., center=False, rotate=True)` ou `None`.
- `magnet_preview` (005): handlers `POST_VIEW`/`POST_PIXEL` registrados com o add‑on. `_moving_item`: o
  `preview_cage`/`cabinet`/`obj` de um `PlacementMixin` ativo, ou a raiz do objeto ativo durante um modal de movimento.
  `compute` → `(hospedeiro, ponto, polígono, caixa)` ou `None` (ímã desligado, item já grudado, módulo filho de parede).
  Desenha o contorno da face (`FACE_COLOR` azul, 3 px), a caixa (2 px) e o rótulo "Grudar em: <nome>" com sombra.
  `_draw_3d` recalcula `compute` a cada quadro, com `ray_cast` 🟡.

### 12.7 Operadores (`ops_stick.py`) 🟢

| `bl_idname` | Rótulo | `bl_options` | Comportamento |
|-------------|--------|--------------|---------------|
| `caffmob.stick_to_face` | Grudar | `REGISTER`, `UNDO`, `BLOCKING` | Modal; `poll`: `VIEW_3D` e `item_of(ativo)`. Clique esquerdo: `scene_hit` (até 16 acertos pulando o item, descendentes, cortadores, anotações) → `link.stick(center=True)`; `ValueError` → `WARNING` e cancela; sem face → `WARNING` e continua. Esc/direito cancela. Texto de status. |
| `caffmob.stick_release` | Desgrudar | `REGISTER`, `UNDO` | `poll`: algum selecionado grudado; `link.release` em cada `item_of`; `INFO` "N item(ns) desgrudado(s)" |
| `caffmob.stick_move` | Mover no plano | `REGISTER`, `UNDO`, `BLOCKING` | `poll`: item vinculado. `invoke`: `snapshot` (pai, inversa, mundo, 13 campos), âncora = interseção do raio com o plano da face deslocado por `distance` (`intersect_line_plane`); sem interseção → "Gire a vista". `MOUSEMOVE`: com Ctrl e ímã ligado, `scene_hit` em outro hospedeiro → `link.stick` e nova âncora (troca de face); senão `st.u/st.v = start + (coords − anchor)` (o `update` reposiciona, RN‑06). Clique confirma; Esc/direito → `restore`. |

`item_of(obj)` = `classify.movable_root` ou o próprio; é a definição de "o que se gruda" usada também pelo painel de
colisão. `MIDDLEMOUSE`/roda passam (`PASS_THROUGH`).

### 12.8 Painel (`panels.py`) 🟢

`BTM_PT_Stick` ("Elemento filho", filho de `BTM_PT_object_properties`, `poll` por `item_of`): grudado → caixa com
"Elemento filho de: <face_label>", campos `u`, `v`, `distance`, `spin`, aviso `alert` "Item fora da face" quando
`out_of_face`, botões Mover no plano e Desgrudar; solto → botão Grudar; hospedeiro → "Elementos filhos: N" com
"<nome> — <face>" ordenados. `classes = ()`: desenhado pela barra lateral única da 005 via `sidebar_proxy`
(`ui/object_properties.py:380-384`); `ui/context_menu` mostra Grudar/Desgrudar conforme `is_stuck`.

### 12.9 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `PLANAR_TOLERANCE` | 0,5 mm | `frame.py` | Face plana: vértices a até isso do plano (RN‑05) |
| `ANGLE_TOLERANCE_DEG` | 1° | `frame.py` | Normal coincide com um lado da caixa |
| `SIDE_TOLERANCE` | 0,5 mm | `frame.py` | Ponto no plano do lado da caixa |
| `OUT_TOLERANCE` | 1 mm | `frame.py` | Folga do "fora da face" e do flip |
| `contact_axis` | `|n·Z| ≥ 0,7` | `frame.py` | `BOTTOM` (deitada) × `BACK` (de pé) |
| `BOX_SIDE` / `PLANE` | — | `frame.py`, `props.py` | Tipo de face (D‑02) |
| `FACES`, `FACE_ITEMS` | 6 faces de `aggregates/limits` | `props.py` | Lado da caixa; padrão `NEG_Y` |
| `IDENTITY` | 16 floats | `props.py` | `plane` e `last_world` vazios |
| `SETTLE_SECONDS` | 0,2 s | `apply.py` | Intervalo do temporizador de assentar |
| `QUIET_SECONDS` | 0,6 s | `apply.py` | Após abrir/desfazer/refazer, movimentos não são gesto |
| `_OPPOSITE` | 6 pares | `apply.py` | Face oposta no flip |
| `_MOVE_IDS` | 7 operadores + `transform.*` + `PlacementMixin` | `settle.py` | Modais que adiam o assentar |
| `_MAGNET_KINDS` | `MODULE`, `GEOMETRY` | `settle.py`, `magnet_preview.py` | O que o ímã e a migração tratam |
| `DEFAULT_DISTANCE`, `_MAX_STEPS`, `_FACING` | 50 mm, 8, −0,7 | `magnet.py` | Alcance padrão, acertos pulados, face de frente |
| `stick_magnet`, `stick_magnet_distance` | ligado; 50 mm (1–500 mm) | `__init__.py:198-208` | Preferências do ímã (D‑06) |
| `wall_side` | `rz < 0,01` e `y < espessura/2` | `migrate.py` | Frente `NEG_Y` × trás `POS_Y` |
| `FACE_COLOR`, `BOX_COLOR` | azul (0,35, 0,85, 1) | `magnet_preview.py` | Prévia do ímã |
| `btm_settings.stick_migrated` | Bool | `data/properties.py` | Cena já migrada |

Tratamento de erros: `frame._normalized` levanta `ValueError` em vetor nulo (capturado em `is_planar`/`choose_face`);
`link.stick` levanta `ValueError` com o motivo traduzido (operadores reportam `WARNING`; ímã devolve `None`);
`ReferenceError` capturado no handler, no timer, em `_polygon` e em `compute`; `_undo_push` tolera `IndexError`/
`RuntimeError`/`AttributeError`; `modal_running` tolera `AttributeError`; `wall_side` engole qualquer exceção na
espessura 🟡.

Testes (2): puro `test_stick_frame` (8 casos: ida e volta nas seis faces, aéreo atrás continua encostado quando a parede
engrossa, dez mudanças de espessura sem erro acumulado, frente da parede é `NEG_Y`, plano inclinado, fora da face, face
plana, escolha do tipo de face); fumaça `blender_004_stick_smoke` (10 cenas: migração idempotente frente/trás; parede
engrossa; flip para a face oposta; nicho na lateral de painel girado; G nativo e assentar; ímã desligado/20 mm/50 mm;
placa encolhe → fora da face; apagar hospedeiro pelo operador e direto; desgrudar; salvar e reabrir). Textos em
`data/translations/editor_grudar.json` (136 chaves, compartilhado com `collision`).

---

## 13. Módulo `customize` (`caffmob_draw/customize/`)

Personalização de módulos inseridos e biblioteca de módulos do usuário (feature 003, bloco A; RF‑01 a RF‑10, RN‑01 a
RN‑06, D‑01 a D‑11), estendido pela 006 (estrutura e divisões, manifesto 1.1.0) e pela 008 (fundo recuado, abas novas,
corrediça). 15 arquivos, 3.028 linhas. Princípio: um `Spec` descreve **só o que o usuário mudou** na instância; campo
vazio = segue a biblioteca; estilos, materiais e puxadores sempre **por nome** (RN‑06); os vãos são endereçados por um
caminho estável (`bay0/opening1`) derivado da ordem dos filhos, não do nome do objeto:

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleo puro | `spec.py` (191), `manifest.py` (149) | não | Estrutura da personalização, validação, serialização; manifesto JSON do módulo salvo |
| Dados | `props.py` (76) | sim | `Object.btm_custom` (no vão, na peça ou na raiz; salvo no `.blend`) |
| Adaptadores | `adapters/__init__.py` (40), `common.py` (374), `frameless.py` (399), `face_frame.py` (318), `closets.py` (262), `btm.py` (203) | sim | Um por biblioteca: ler, trocar frente, interior, reaplicar, estrutura |
| Aplicação | `reapply.py` (80), `library_io.py` (262) | sim | Gancho pós‑reconstrução; gravar, listar, inserir, renomear, apagar módulos |
| Interface | `ops_customize.py` (263), `ops_library.py` (232), `panels.py` (154) | sim | 6 operadores de personalização, 5 da biblioteca, painéis |

`__init__.py` registra (import tardio) `props`, `ops_customize`, `ops_library`, `panels`. Dependências: `selection/classify`
(`module_root`, `module_library`), `cutting/part_roles`, `compat` (inputs de Geometry Nodes), `data/units`, `data/i18n`,
`library_common` (`thumbnail`, `world_box`), `hb_placement.PlacementMixin`, `hb_snap`, `hb_project`, `hb_types`,
`hb_utils` (`run_calc_fix`), `geometry/door_controller` e `geometry/mesh_gen` (`btm`), `cabinet_editor`
(`scene_divisions`, `scene_extras`, `scene_interiors`, `scene_slides`, `structure`, `divisions.Box`) e as três
bibliotecas de produto (`types_frameless`, `props_hb_frameless`, `types_face_frame`, `face_frame/pulls`,
`types_closets`, `fronts_closets`, `pulls_closets`). Dependentes (24 arquivos): `__init__`, `data/properties`
(`after_rebuild` no `update` do `btm_cabinet`), as três bibliotecas (gancho `after_rebuild` em `ops_styles`,
`props_hb_frameless`, `ops_opening`, `types_face_frame:8774`, `types_closets:1936`), `cabinet_editor` (7 arquivos:
`bridge`, `ops_editor`, `ops_actions`, `scene_parts`, `scene_divisions`, `reflow_handler`…), `legacy/groups`,
`legacy/convert`, `library_panel/popover`, `library_panel/categories`, `object_library/retexture`, `object_library/item_io`,
`move_over/ops_substitute`, `cutting/drilling`, `ui/object_properties`, `ui/my_modules`, `ui/context_menu`.

### 13.1 Núcleo da personalização (`spec.py`) 🟢

- Domínios: `SECTIONS` (`FRONTS`, `PULLS`, `MATERIALS`, `INTERIOR`), `FRONT_TYPES` (`DOOR_LEFT`, `DOOR_RIGHT`,
  `DOUBLE_DOORS`, `DRAWERS`, `FLIP_UP`, `PANEL`, `OPEN`), `PULL_POSITIONS` (`DEFAULT`, `TOP`, `MIDDLE`, `BOTTOM`,
  `SIDE`), `NO_PULL = "__NONE__"`, `GROUPS` (`CAIXA`, `FRENTES`, `FUNDO`, `INTERNO`), limites `MAX_DRAWERS` 8,
  `MAX_SHELVES` 20, `MAX_DIVIDERS` 10.
- `Interior(shelves, dividers, drawers, heights)`; `Opening(path, front, drawer_count, door_style, drawer_style,
  pull_model, pull_position, front_material, interior)`; `Spec(library, openings, part_materials, group_materials,
  pull_all_fronts, aggregates)` com `opening(path)`, `ensure_opening`, `is_empty`.
- `to_dict`/`from_dict` (campos desconhecidos ignorados; `interior` omitido quando `None`; `heights` convertidas a float).
- `validate(spec)`: caminho vazio ou repetido; frente fora de `FRONT_TYPES`; `DRAWERS` com `drawer_count` fora de 1–8;
  posição de puxador desconhecida; `validate_interior`; grupo desconhecido; material vazio. `validate_interior(interior,
  inner_height)`: faixas; `len(heights) == shelves`; alturas crescentes; primeira > 0 e última < altura interna.
- `shelf_positions(count, inner_height, thickness, heights)`: digitadas, ou vãos livres iguais
  `gap = (H − n·t)/(n+1)`, posição `gap·(i+1) + t·i`.
- `group_of_component`: `POR` → `FRENTES`; `BACK`/`FUN_*` → `FUNDO`; `PRAT`/`DIV` → `INTERNO`; resto `CAIXA`.
  `interior_to_json`/`interior_from_json` (JSON inválido → `None`).

### 13.2 Manifesto do módulo salvo (`manifest.py`) 🟢

`FORMAT = "caffmob_draw.user-module"`, `SCHEMA_VERSION = "1.1.0"`, `SUPPORTED_MAJOR = 1`, `LIBRARIES`
(`FRAMELESS`, `FACE_FRAME`, `CLOSETS`, `BTM`), `ROLES` (`TOP`, `BOTTOM`, `BACK`, `LEFT`, `RIGHT`), `MODES` (`KEEP`,
`EXTEND`, `SHRINK`), `ORIENTATIONS`. `file_stem(name)`: remove `<>:"/\|?*` e controles, tira pontos finais,
vazio → `"modulo"`. `build(...)`: cabeçalho (nome, categoria, biblioteca, raiz, criado, versão do add‑on,
`dimensions_mm`), `styles`, `materials` e `pulls` ordenados e sem repetição (sem `NO_PULL`), `spec` serializado;
opcionais `structure` (por papel: `removed`, `mode`, `thickness_mm`, `material`) e `divisions` (`uid`, `space`
`s<i>(.a|.b)*`, `orientation`, `offset_mm`, `use_front/front_mm`, `use_back/back_mm`, `thickness_mm`, `material`),
medidas em mm com 3 casas. `structure_of`/`divisions_of` devolvem em metros. `validate`: formato, major ≤ 1, biblioteca,
nome, raiz; depois `spec.validate` e `_validate_structure` (papel, modo, orientação, `space` por regex, medidas
negativas). `loads(text)` → `(dados, spec, erros)`; `dumps` JSON indentado sem ordenar chaves.

### 13.3 Propriedade e gancho pós‑reconstrução (`props.py`, `reapply.py`) 🟢

`BTM_PG_CustomSpec` em `Object.btm_custom` (ver dicionário §12.1); `group_material`/`set_group_material` sobre a coleção
`group_materials`. `reapply.has_structure(root)`: `btm_structure.components` ou `back_mode == 'RECESSED'`, assinatura
`btm_division_sig` no idprop ou filho `btm_extra.is_extra`. `has_custom(root)`: estrutura, `group_materials`,
`pull_all_fronts`, ou qualquer campo preenchido em `btm_custom` da raiz ou dos descendentes. `reapply(context, root)`:
`adapters.for_root` → `adapter.reapply`, com trava `_running` por nome (reentrância). `after_rebuild(context, obj)`:
gancho chamado pelas bibliotecas no fim de reconstruções; raiz via `adapters.module_root`; sem personalização sai sem
custo; com estrutura, ainda `reaffirm` (remoções/espessuras), `set_back_recess` quando `auto_back` e `RECESSED`, e
`scene_divisions.reflow`, `scene_extras.sync`, `scene_interiors.reflow`, `scene_slides.reflow` (006, 008).

### 13.4 Contrato dos adaptadores (`adapters/__init__.py`, `common.py`) 🟢

Cada adaptador expõe `LIBRARY`, `capabilities(root)` → `{seção: None | motivo}`, `front_types(root)`,
`openings(root)` → `[(caminho, objeto)]` em ordem estável (`common.ordered`: X crescente, Z decrescente, nome),
`read(root)` → `Spec` (estado atual: biblioteca + `btm_custom`), `set_front`, `set_interior`, `reapply`, `pull_items()`,
`style_names()`; contrato opcional da 006/008 (`inner_spaces`, `structure_parts`, `structure_caps`, `remove_part`,
`restore_part`, `set_part_thickness`, `reaffirm`, `set_back_recess`, `structure_info`, `elevation_parts`,
`opening_boxes`), resolvido por `common.call(adapter, nome, …)` com `default_<nome>` como recuo. `for_root(root)`
escolhe pelo `classify.module_library`; `for_object(obj)` → `(raiz, adaptador)`.

`common`: `material(name, warnings)` por nome (ausente → aviso, `None`); `rotated(mat)` = variante `"<nome> ROTATED"`
(veio girado); `set_cutpart_material(obj, mat)`: `GeoNodeCutpart` → `Top Surface`/`Bottom Surface` via `compat`, mais
`Material`/`Stile Material`/`Panel Material`/`Rail Material` (girado) em outros modificadores de nós; malha sem
modificador → todos os slots; porta 5 peças do face frame (modificador desligado) → slots também. `part_group(obj,
cabinet_type)`: frente por `IS_CABINET_FRONT`/`hb_part_role`, senão `part_roles.classify` → `group_of_component`.
`apply_group_materials`: material da peça vence o do grupo. `run_operator`: `temp_override` com o objeto ativo.
Estrutura (006): `set_removed(obj, removed)` esconde por **driver** em `hide_viewport`/`hide_render` com variável
`btm_rm` lendo o idprop `btm_removed`, somando‑se (`(expr) or btm_rm`) ao driver da biblioteca; ao restaurar, driver
só nosso é removido. `cutpart_thickness`/`set_cutpart_thickness(drop_driver)`; `reaffirm_parts` reaplica remoções,
espessuras e `btm_raw_material`. `clip_space(box, part_boxes)`: recorta o vão pelas faces internas das chapas presentes;
`cage_spaces` monta `{"s<i>": Box}` das jaulas. `set_back_recess`: move a peça do fundo por `delta_location` (−Y da
raiz) para não ser sobrescrito por drivers.

### 13.5 Adaptador frameless (`adapters/frameless.py`) 🟢

Vão estável = jaula `IS_FRAMELESS_OPENING_CAGE` cujo pai não é outro vão, dentro de `IS_FRAMELESS_BAY_CAGE`; caminho
`bay<i>/opening<j>`. `leaf_opening` desce ao vão mais interno; `front_type`: `IS_FLIP_UP_DOOR` → `FLIP_UP`;
`Door Swing` 0/1/2 → esquerda/direita/dupla; gavetas todas `False Front` → `PANEL`; gavetas → `DRAWERS` n; sem frentes
→ `OPEN` (`""` com `APPLIANCE_NAME`). `set_front`: n > 1 gavetas só em vão que ocupa o bay inteiro
(`change_bay_opening` com preset `<n>_DRAWER_STACK`, teto `MAX_STACKED_DRAWERS` 4); senão
`change_opening_type` (`FRONT_TO_TYPE`). `set_interior`: valida com `Dim Z` do vão; remove jaulas `IS_FRAMELESS_INTERIOR_CAGE`;
gavetas internas → `InteriorSplitterVertical` com seção `ROLLOUTS` de `min(0,8·H, 0,18·n)`; divisórias →
`InteriorSplitterHorizontal`; alturas digitadas → seções de cima para baixo (última = resto); só prateleiras →
`CabinetShelves` com `Shelf Quantity`; `run_calc_fix_until_stable`. `reapply`: materiais por grupo; por vão e frente:
estilo por nome (`door_styles.find` → `assign_style_to_front`, grava `DOOR_STYLE_INDEX/NAME`), puxador
(`GeoNodeHardware` input `Object` via `compat`; `NO_PULL` → `None`; posição por idprops `Pull Location` 0/1/2,
`Tall Pull Vertical Location`, `Center Pull`, `Handle Horizontal Location`), material das frentes se a peça não tem o
próprio; `Shelf Quantity` reafirmado; `run_calc_fix`. Estrutura: peças por nome (`Left Side`, `Right Side`, `Bottom`,
`Top`, `Back`); só `KEEP`, exceto `BOTTOM` + `EXTEND` pelo `Remove Bottom` nativo; espessura sobrescrita tira o
driver `Material Thickness` e voltar ao padrão o recria.

### 13.6 Adaptadores face frame e closets (`adapters/face_frame.py`, `adapters/closets.py`) 🟢

- Face frame: vãos = jaulas folha (`TAG_OPENING_CAGE` sem jaula dentro), `opening<i>`; `front_type` por
  `face_frame_opening.front_type`/`hinge_side`. `set_front`: n > 1 gavetas → `split_opening(axis='H', count)`; senão
  grava `front_type`/`hinge_side` e `recalculate_face_frame_cabinet`. `set_interior`: substitui `interior_items`
  (`ADJUSTABLE_SHELF`, `ROLLOUT`); divisória uma por vez via `add_interior_division`, recusada se já há árvore; alturas
  ignoradas com aviso. `reapply`: estilo por `assign_style_to_front(record_override=True)` (pool de gaveta ou porta),
  puxador troca `pull.data` e posiciona em X (`PULL_EDGE` 50 mm), `NO_PULL` remove os objetos. Estrutura: papéis por
  `hb_part_role`; só `KEEP`.
- Closets: vãos `opening<i>` por `TAG_OPENING_CAGE`; estado em idprops (`hb_door_swing`, `hb_drawer_qty`,
  `hb_adj_shelf_qty`, `hb_cubby_cols` → `""`). `front_types` sem basculante nem painel. `set_front`: `apply_opening_config`
  (`DOOR_LEFT`/`DOOR_RIGHT`/`DOOR_DOUBLE`/`DRAWERS_<n≤8>`); `OPEN` → `clear_opening_contents`. `set_interior`: só
  prateleiras; divisórias e gavetas internas avisam. `reapply`: `fronts_closets.apply_style_to_front` por identificador,
  puxador troca `pull.data` e posiciona em Y (no closets `Width` = altura), invalida `_pull_cache`. Estrutura: laterais =
  primeiro e último `CLOSET_PANEL` por `hb_panel_index`; base/tampo/fundo por papel; só `KEEP`.

### 13.7 Adaptador `btm` (`adapters/btm.py`) 🟢

Módulo paramétrico CAFFMob: malha única com portas filhas; um só vão `"module"` = a raiz. `capabilities` tem a chave
extra `STYLES` com motivo ("não tem estilos de porta"). `front_type` por `btm_cabinet.door_swing` (`SWING_TO_FRONT`:
`NONE`→`OPEN`, `LEFT`, `RIGHT`, `DOUBLE`, `FLIP`); `set_front` grava `door_swing` (o `update` refaz malha e portas);
gavetas não existem. `set_interior`: grava `btm_custom.interior` e `btm_cabinet.shelves`; divisórias, gavetas e alturas
avisam. `reapply`: slots `MAT_CARCASS`/`MAT_SHELF`/`MAT_BACK` da malha pelos grupos `CAIXA`/`INTERNO`/`FUNDO`
(recuo para a caixa), porta por `door_controller.set_door_pull` (puxador do frameless) e `set_door_material`.
Estrutura (006): tudo em `btm_cabinet` (`has_*`, `mode_*`, `thickness_*`); os três modos valem em todas as chapas;
`SHRINK` ajusta medidas e `location` por `structure.shrink_change`; `structure_parts` vazio (chapas são faces da
malha), `structure_info`/`elevation_parts` pelo `cabinet_editor/structure.layout`; `reaffirm` vazio.

### 13.8 Biblioteca de módulos do usuário (`library_io.py`) 🟢

Pasta `extension_path_user(pkg, "modules")/<categoria>/`, três arquivos com o mesmo nome base (`file_stem`):
`.blend`, `.png` (256 px), `.json`. `list_modules()` varre categorias e `.blend`; nome vem do manifesto quando válido;
`has_manifest`. `build_manifest`: `adapter.read`, caixa de mundo (`world_box`) em mm, estilos de porta/gaveta,
materiais (frentes + grupos + peças), puxadores, agregados filhos (`btm_aggregate`), `btm_structure.to_dict()`,
`scene_divisions.read`. `save(context, root, name, category, thumbnail)`: `bpy.data.libraries.write` dos blocos
(objetos, dados, materiais, imagens das texturas, node groups) com `path_remap='RELATIVE_ALL'`, `fake_user=True`,
em arquivos temporários na pasta destino e `os.replace` atômico; `OSError`/`RuntimeError` apaga os parciais e devolve a
mensagem; miniatura por `library_common.thumbnail`. `load(context, entry)`: lê e valida o manifesto (inválido → nada
inserido); `libraries.load(link=False)` de todos os objetos; liga à coleção da cena; raiz = objeto sem pai com
`module_library`; objetos referenciados por inputs `NodeSocketObject` de Geometry Nodes (puxadores) ficam ocultos;
estilos ausentes → um aviso geral (substitui os avisos por estilo dos adaptadores); `reapply.reapply`;
`_renew_divisions` (uids novos e `reflow(force=True)`). `delete`, `rename` (recusa nome existente; renomeia os três e
o campo `name` do manifesto).

### 13.9 Operadores (`ops_customize.py`, `ops_library.py`) 🟢

| `bl_idname` | Rótulo | `bl_options` | Comportamento |
|-------------|--------|--------------|---------------|
| `caffmob.customize_set_front` | Trocar frente | `REGISTER`, `UNDO` | `path` do vão; enum dinâmico filtrado por `front_types`; `DRAWERS` abre diálogo com `drawer_count` (1–8); `adapter.set_front` + `reapply` |
| `caffmob.customize_set_style` | Estilo da frente | `REGISTER`, `UNDO` | `kind` `DOOR`/`DRAWER`; grava `door_style`/`drawer_style` no vão (`""` = do módulo); `reapply` |
| `caffmob.customize_set_pull` | Puxador | `REGISTER`, `UNDO` | Diálogo: `model` (projeto / `NO_PULL` / lista), `position`, `all_fronts`; com todas: `pull_model` na raiz e posição em todos os vãos; senão no vão |
| `caffmob.customize_set_material` | Material | `REGISTER`, `UNDO` | `prop_search` em `bpy.data.materials`; alvo `FRONTS` (vão), `GROUP` (raiz) ou `PART` (objeto ativo); `""` = da biblioteca |
| `caffmob.customize_set_interior` | Divisões internas | `REGISTER`, `UNDO` | Diálogo pré‑preenchido com `adapter.read`; alturas "a; b; c" na unidade da cena (`units.parse_length`); `set_interior`, e só sem mensagens `reapply` |
| `caffmob.customize_clear` | Limpar personalização do vão | `REGISTER`, `UNDO` | Zera estilo, puxador, posição e material do vão (não reaplica; pede trocar o estilo do projeto) |
| `caffmob.module_save` | Salvar como módulo | `REGISTER` | Diálogo (nome = raiz, categoria `Geral`, miniatura); nome existente mostra alerta e exige `overwrite` (RF‑08) |
| `caffmob.module_insert` | Inserir módulo | `REGISTER`, `UNDO` | `PlacementMixin`: `load`, registra objetos sem pai, sem raiz desfaz e cancela; `place=False` fica onde foi salvo; modal: snap à grade, `R` gira 90°, Esc cancela |
| `caffmob.module_delete` | Apagar módulo | — | `invoke_confirm`; apaga os três arquivos |
| `caffmob.module_rename` | Renomear módulo | — | Diálogo; `library_io.rename` |
| `caffmob.module_open_folder` | Abrir pasta dos módulos | — | `startfile` / `open` / `xdg-open` |

`_ENUM_CACHE` mantém vivas as strings dos enums dinâmicos (exigência da API). `_OpeningOperator.resolve` avisa "Vão não
encontrado" quando o caminho não casa mais. Observação 🟡: `module_delete`, `module_rename` e `module_open_folder` não
declaram `bl_options`; alteram só o disco, mas o `module_rename` sem `REGISTER` não aparece no histórico.

### 13.10 Painéis (`panels.py`) 🟢

`draw_customize`: sem adaptador → "Selecione um módulo"; por vão (`adapter.read`): rótulo "Vão n: <frente>" (ou "n
gavetas"), `X` limpar, `operator_menu_enum` de frente e de estilo (este só com `FRONTS` e `STYLES` suportados),
puxador, material das frentes, interior "n prat., n div., n gav."; seções não suportadas aparecem desabilitadas com o
motivo (RF‑01); caixa Materiais por grupo e, com peça ativa, "Peça X"; botão Salvar como módulo. `draw_library`:
abrir pasta; lista por categoria com inserir (rótulo "(sem personalização)" sem manifesto), renomear, apagar; erro de
disco vira "Biblioteca indisponível". `BTM_PT_CustomizeModule` e `BTM_PT_ModuleLibrary` com `classes = ()`: desenhados
pela barra lateral única da 005 (`ui/object_properties`, `ui/my_modules`).

### 13.11 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `FRONT_TYPES` | 7 tipos | `spec.py` | Frentes possíveis (cada biblioteca filtra) |
| `PULL_POSITIONS`, `NO_PULL` | 5; `"__NONE__"` | `spec.py` | Posição do puxador; sem puxador |
| `GROUPS` | Caixa, Frentes, Fundo, Interno | `spec.py` | Grupos de material |
| `MAX_DRAWERS`, `MAX_SHELVES`, `MAX_DIVIDERS` | 8, 20, 10 | `spec.py` | Faixas de validação |
| `FORMAT`, `SCHEMA_VERSION`, `SUPPORTED_MAJOR` | `caffmob_draw.user-module`, 1.1.0, 1 | `manifest.py` | Contrato do arquivo |
| `MODULES_DIR`, `GENERAL` | `modules`, `Geral` | `library_io.py` | Pasta e categoria padrão |
| `MAX_STACKED_DRAWERS`, `ROLLOUT_SECTION_HEIGHT` | 4; 0,18 m | `adapters/frameless.py` | Pilha de gavetas; altura por gaveta interna |
| `PULL_EDGE` | 50 mm | `face_frame.py`, `closets.py` | Distância da borda para TOP/BOTTOM |
| `DOOR_SWING_TO_FRONT`, `FRONT_TO_TYPE` | mapas | `frameless.py` | Idprop ↔ frente |
| `HINGE_TO_FRONT`, `FRONT_TO_HINGE`, `FRONT_ROLES`, `DRAWER_ROLES` | mapas | `face_frame.py` | Dobradiça ↔ frente; papéis |
| `SWING_TO_FRONT`, `FRONT_TO_CONFIG` | mapas | `closets.py`, `btm.py` | Idprop/`door_swing` ↔ frente |
| `REMOVED_PROP`, `RAW_MATERIAL_PROP`, `_DRIVER_VAR` | `btm_removed`, `btm_raw_material`, `btm_rm` | `common.py` | Remoção por driver e material bruto |
| `DIVISION_SIGNATURE` | `btm_division_sig` | `reapply.py` | Módulo com divisões |
| `btm_pull_file` | idprop | adaptadores | Objeto de puxador já carregado por chave |
| `MAT_CARCASS`, `MAT_SHELF`, `MAT_BACK` | slots 0–2 | `geometry/mesh_gen` | Materiais da malha `btm` |

Tratamento de erros: `manifest.loads` devolve erros em vez de levantar; `library_io.save` captura `OSError`/`RuntimeError`
e remove parciais; `draw_library` captura `OSError`/`ValueError`; `_heights` captura `ValueError` ("Alturas inválidas");
`_pull_object`/`material`/`_apply_style` acumulam avisos em lista (`common.unique`); adaptadores devolvem listas de
mensagens, nunca exceções; `_addon_version` tolera `ImportError`/`AttributeError`; `set_removed` cria drivers
idempotentes. Observações 🟡: `spec.validate` usa `where` já traduzido nas mensagens de interior sem `tr`;
`interior_from_json` não valida tipos (`int()` em string lança `ValueError` fora do `try`); 🟢 **bug confirmado**: `library_io.load:234` lê `missing` fora do bloco `if data is not None`; ao
inserir um `.blend` sem `.json` (grupo antigo, listado como "sem personalização") a variável nunca é atribuída e o
operador cai com `UnboundLocalError` em vez de inserir sem reaplicar, como o contrato prevê.

Testes (3): puros `test_customize_spec` (8: ida e volta, vão sem interior não grava chave, válido, inválidos, vão
repetido, alturas, posições iguais, grupos e JSON) e `test_module_manifest` (8: montar e ler, major recusado, formato e
biblioteca, JSON inválido, 1.0.0 continua válido, estrutura e divisões ida e volta, erros de estrutura, nome de arquivo);
fumaça `blender_003_customize_smoke` (frameless frente/estilo/puxador/materiais/interior e reaplicação após estilo do
projeto; salvar e inserir; face frame; closets; `btm`; arquivo novo com personalização). Textos em
`data/translations/customize.json` (155 chaves).

---

## 14. Módulo `cabinet_editor` (`caffmob_draw/cabinet_editor/`)

Editor de Armário em janela própria (feature 004), estendido pela 006 (abas Estrutura e Divisão: componentes externos
removíveis, chapas de divisão), pela 008 (Construtor de Armários com 7 abas no modelo do Promob: extras da estrutura,
número de vãos, gavetas, internos para eletro, portas, deslizantes, fundos; Aplicar) e pela 012 (montagem `LATERAL`/
`BASE` e marca de "Padrão próprio"). 34 arquivos `.py`, 5.443 linhas, mais 47 miniaturas em `thumbnails/`.
Princípio (D-21, D-22): o módulo é editado **ao vivo** na cena, mas todo pedido dos botões passa por uma fila que um
único operador modal com `UNDO` executa; o rascunho é uma pilha de instantâneos (`EditorState`) e Cancelar reaplica o
instantâneo inicial. Assim o Blender cria **um** passo de desfazer no OK (ou um por Aplicar):

| Camada | Arquivos | `bpy`? | Papel |
|--------|----------|--------|-------|
| Núcleos puros | `state.py` (80), `validate.py` (118), `elevation.py` (100), `structure.py` (143), `divisions.py` (254), `catalog.py` (171), `extras.py` (97), `bays.py` (54), `slides.py` (66), `appliances.py` (72), `position.py` (35) | não | Rascunho e assinatura; mensagens `DIM/GEO/CAT/STR/DIV`; vista frontal e diff; caixa do `btm` e modos de remoção; subvãos; catálogo; geometria de extras, vãos, deslizantes, eletros; cotas |
| Dados | `data_props.py` (182), `props.py` (431) | sim | `Object.btm_structure`/`btm_division`/`btm_extra` (salvos); `Session` em memória e `WindowManager.btm_cabinet_editor` (campos virtuais) |
| Ponte e cena | `bridge.py` (674), `scene_divisions.py` (184), `scene_parts.py` (152), `scene_extras.py` (44), `scene_interiors.py` (90), `scene_slides.py` (113), `reflow_handler.py` (74) | sim | Ler/levar ao instantâneo; 25 ações de edição; chapas de divisão, extras, internos e deslizantes como objetos filhos da raiz; handlers |
| Interação | `ops_editor.py` (550), `ops_actions.py` (548), `window.py` (259), `previews.py` (36) | sim | Abrir, modal, OK/Cancelar/Fechar/Aplicar; botões que só enfileiram; janela e desenho `POST_PIXEL`; miniaturas |
| Painéis | `panels.py` (304), `panels_structure.py` (172), `panels_divisions.py` (123), `panels_drawers.py` (64), `panels_interior.py` (60), `panels_doors.py` (49), `panels_sliding.py` (48), `panels_backs.py` (48), `panels_tabs_common.py` (15) | sim | Cabeçalho com as 7 abas, um arquivo por aba, mensagens, ajustes, rodapé |

`__init__.py` registra por import tardio (os núcleos puros rodam nos testes sem `bpy`), na ordem `data_props`, `props`,
`previews`, `window`, `ops_editor`, `ops_actions`, `panels`, os 7 painéis de aba e `reflow_handler`; `unregister` na
ordem inversa. Dependências: `customize` (adaptadores, `spec`, `reapply`, `common`, `props.PULL_POSITION_ITEMS`),
`selection` (`classify`, `editing`), `cutting` (`part_roles`, `machining.AGGREGATE_PREFIX`), `collision/obb`
(GEO‑002), `stick/apply.local_box`, `aggregates` (`group`, `leaf`, `convert`: deslizantes da 007), `canvas2d` (`window`,
`draw`, `view.View2D`), `walls2d/history`, `standards` (`api`, `apply_core`, `sync`), `data` (`units`, `i18n`,
`dimension_schema`), `compat`, `hb_types`, `product_libraries/frameless/types_frameless.CabinetPart`, `ui/save_feedback`.
Dependentes (14 arquivos fora do módulo): `__init__`; `customize` (`adapters/btm`, `adapters/common`, `reapply`,
`library_io`: estrutura, divisões, extras); `geometry/mesh_gen` (`structure.layout` monta a malha do `btm`);
`cutting/part_sources` (`carcass_lengths`) e `cutting/drilling` (divisórias móveis); `standards/cabinet_defaults`
(`ROLE_COMPONENT`) e `standards/sync` (`bridge`); `stick/settle` (o modal do editor está na lista de operadores que
suspendem o assentar); `ui/object_properties`, `ui/sidebar_selected`, `ui/sidebar_vocab`, `library_panel/ops_cabinet`
(abrir o editor ao inserir).

### 14.1 Rascunho e histórico (`state.py`) 🟢

`EditorState(dimensions (L, A, P) m, spec dict, structure dict, divisions list, extras dict, slides dict, interiors list,
backs dict)` com `copy` profundo. `signature(state)`: JSON ordenado com floats arredondados a `PRECISION = 6` casas
(1 µm). `Draft(initial)`: `initial` (referência do Cancelar), `current` e `history = walls2d.history.History(current,
signature=signature)` (o mesmo histórico do editor de paredes); `checkpoint`, `undo`, `redo` (devolvem o instantâneo ou
`None`), `dirty()` = assinatura atual ≠ inicial, `apply_point()` (008, D‑04): o atual vira o inicial e o histórico
recomeça.

### 14.2 Validação (`validate.py`) 🟢

`Message(code, severity, component, parameter, value, range, action)`, `blocks` só para `ERROR`. `DEFAULT_LIMITS`
(m): largura e altura 0,01–10, profundidade 0,005–10 (= `selection.editing`); `limits_for(library_limits)` estreita
campo a campo pela faixa da biblioteca (`bridge.library_limits` lê `hard_min`/`hard_max` das propriedades `width`,
`height`, `depth` do `face_frame_cabinet`, `hb_closet_starter` ou `btm_cabinet`). `parse_dimension`: vazio `DIM-001`,
texto inválido `DIM-002` (`units.parse_length`), fora da faixa `DIM-003` (folga 1e‑9). `outside_volume` (`GEO-001`):
peça que passa da largura ou da altura com folga `TOLERANCE` 1 mm (vãos e agregados de fora; a profundidade é livre por
causa do puxador); prateleira/divisória → `ERROR`, o resto `WARNING`. `internal_overlaps` (`GEO-002`): pares de
prateleiras e divisórias com `collision.obb.overlap` > 1 mm → `ERROR`. `unsupported` (`CAT-001`, aviso).
`sort_messages`: gravidade, código, componente, parâmetro.

### 14.3 Vista frontal (`elevation.py`) 🟢

`Part(name, kind, lo, hi)` no referencial da raiz (X largura, Y profundidade com a frente em −Y, Z altura); `rect` =
projeção (x0, z0, x1, z1). Tipos: `FRONT`, `SHELF`, `DIVIDER`, `STRUCTURE`, `OPENING`, `AGGREGATE`, `PART`;
`kind_from_role` pelo código de `cutting/part_roles` (`POR`→frente; `PRAT`→prateleira; `DIV`→divisória; `LAT`, `BAS`,
`ROD`, `TRA`, `FUN_*`, `TAMPON`, `SAR`→estrutura). `draw_order`: Y decrescente (fundo primeiro, frente por cima).
`hit(parts, x, z)`: entre as peças sob o ponto, a de menor Y (mais à frente, arredondado a 0,1 mm), depois a de menor
área. `diff(before, after, targets)` (RF‑07): `ADDED`/`REMOVED`/`RESIZED`/`MOVED` com tolerância 0,1 mm, sem as peças
que o usuário editou (`targets`) — são os "Ajustes automáticos".

### 14.4 Componentes externos e caixa do `btm` (`structure.py`) 🟢

Papéis `TOP`, `BOTTOM`, `BACK`, `LEFT`, `RIGHT`; modos de remoção (RN‑06): `KEEP` (só a chapa sai), `EXTEND` (as
vizinhas avançam até a borda; o vão cresce), `SHRINK` (as medidas externas diminuem pela espessura; o vão fica igual).
`THICKNESS_RANGE` 3–60 mm; `ROLE_COMPONENT` (papel → componente do Configurador: `TOP`/`BOTTOM`→`BAS`, laterais→`LAT`,
`BACK`→`FUN_INF`). `RoleState(removed, mode, thickness 0 = Configurador, material "" = Configurador)` com `changed`;
`state_from_dict`/`state_to_dict` (só papéis válidos; só estados diferentes do padrão). `allowed_mode(mode, caps)`:
modo que a biblioteca não faz cai em `KEEP` com o motivo. `check_thickness` → `STR-002` (erro); `unsupported_mode` →
`STR-001` (aviso).

`layout(width, height, depth, thick, states, back_setback, assembly)` monta a caixa do módulo `btm` (X centrado,
Y de −profundidade a 0, Z de 0 à altura): a espessura que vizinhas e vão respeitam é 0 quando a chapa saiu em
`EXTEND`/`SHRINK`; `LATERAL` (012): laterais do piso ao topo, base e tampo entre elas; `BASE`: a base ocupa a largura
toda e as laterais ficam em cima dela (o tampo segue entre as laterais); fundo entre laterais e entre base e tampo,
recuado `back_setback` (008, D‑11); devolve só as chapas presentes e o vão interno (que termina no fundo recuado).
`carcass_lengths` (012): comprimento de cada chapa pela montagem (usado pelo plano de corte). `shrink_change(role, t)`:
delta da medida e deslocamento local da raiz para as chapas que ficam não saírem do lugar (lateral: largura −t e
X ±t/2; base: altura −t e Z +t; tampo: altura −t; fundo: profundidade −t e Y −t).

### 14.5 Divisões e subvãos (`divisions.py`) 🟢

Referencial da raiz; espaços‑raiz `s0`, `s1`… vêm do adaptador (`inner_spaces`, um por bay). Uma divisão corta um
subvão‑**folha** em dois (`.a` esquerda/baixo, `.b` direita/cima), sempre inteiro (RN‑09); `offset` = distância da face
esquerda/de baixo até a chapa (RN‑11) e fica igual quando o espaço‑raiz muda (RN‑16); recuos só tiram profundidade
(RN‑13). `Division(uid 8 hex, space, orientation, offset, thickness, use_front, front 0,02, use_back, back 0,02,
material, kind FIXED|MOVABLE|SPACER, follow, bay)`.

- `resolve(roots, divisions)`: percorre por profundidade do caminho; subvão inexistente ou já cortado → órfã; o
  distanciador (`SPACER`, 008) ocupa a faixa e o subvão continua com o mesmo caminho, do lado maior; devolve
  `(folhas, cortes {uid: (subvão, chapa)}, órfãs)`.
- `place`: tira os recuos marcados da profundidade. `middle_offset`: chapa centrada. `add`: no meio (distanciador em
  `offset` 0), `ValueError` se o subvão não é folha. `add_many` (008): `count` chapas com `count + 1` subvãos iguais,
  em cadeia pelos `.b`. `remove`: a divisão e tudo o que estava dentro das metades. `remove_in_space` ("Sem
  Divisória"): a divisória (não distanciador) que criou a folha. `offset_range`: mínimo `MIN_SPACE` 50 mm dos dois lados
  (distanciador pode encostar). `validate` → `DIV-001` subvão < mínimo, `DIV-002` profundidade < `MIN_DEPTH` 50 mm,
  `DIV-003` órfã (todos erro). `space_at` (folha de menor área sob o ponto) e `space_tokens` (rótulo "Vão n ›
  esquerdo › de cima").

### 14.6 Catálogo do Construtor (`catalog.py`) 🟢

`Item(id, tab, group, label, description, action, params ((nome, mm|texto),…), size_mm, margin_mm 10, invertible,
filter, groove)`; `thumb` = id em minúsculas; `too_small(space_mm)`: precisa de `size + 2·margem` em largura e altura.
`ITEMS` (47): divisórias com/sem recuo frontal (`DIV_RECESS` frente 20, `DIV_NO_RECESS` frente 0, ambas "trás 15"),
distanciadores 15, 30 e "p/ Divisão" 15 (`follow`); gavetas `DRAWER_CF`, `DRAWER_TALL` (2–4), `DRAWER_INTERNAL`,
`DRAWER_BLUM`; frente `FRONT_RETA`; fundos `BACK_FULL`/`BACK_RECESSED`; internos (externo e embutido: painéis
forno/micro, forno, micro, cafeteira com recorte, frontal sem recorte; eletros soltos forno 595×595×560, micro
595×390×400, cafeteira 595×455×400; respiro 440×30; apoio; pistão); deslizantes: 14 estilos em madeira, 4 com puxador
integrado e quadro de alumínio, `groove` nos de gola/cava/perfil/integrado. `TREE` (20 nós, RN‑07a): Base Superior
Recuada; Pés Plásticos 150 mm com posições 01–04 (ligadas por padrão, `DEFAULT_ON`); Rodapés (frontal, esquerdo,
direito); Rodapés Granito; Fechamentos 50 mm; Vistas e Vistas (alto), 150 mm cada; `TREE_GROUPS`, `CHILDREN`.

### 14.7 Geometria das abas novas (`extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py`) 🟢

- `extras.layout(box carcaça, t, settings, ceiling 2,70)` → `Piece(kind, box, component, hardware, material, slot)` na
  ordem da árvore: base superior recuada (`BAS`, entre laterais, recuo frontal `RECESS` 20 mm); pés (cilindros de raio
  20 mm a `FOOT_INSET` 50 mm dos cantos, **abaixo** da caixa — o módulo não sobe; `PE_PLASTICO`; posição desligada
  pula); rodapé frontal recuado `KICK_SETBACK` 50 mm e laterais (`ROD`, altura = pés); granito (`ROD`, material
  `GRANITO`); fechamentos (`TAMPON`, tiras de largura `value` dos dois lados, por fora); vistas (`ESP`) à esquerda, à
  direita ou em cima; vistas altas sobem até `max(teto, topo)`. Valor 0 volta ao padrão de `DEFAULTS`.
- `bays` (RN‑07b, D‑15): N vãos = N − 1 divisórias verticais `bay` em cadeia `s0`, `s0.b`, `s0.b.b`…, todas com
  `offset` = largura do vão `(L − (N−1)·t)/N`; `apply` mantém as que existem (posição nova), acrescenta ou tira só as
  do fim; `MAX_BAYS` 10; `removed` lista as que saíram.
- `slides.layout(space, leaves, style, invert)` (RN‑13b): folhas dentro do vão, na frente, uma por trilho com
  `PITCH` 20 mm, espessura 18, sobreposição `OVERLAP` 30 mm, largura `(L + (N−1)·30)/N`; trilhos superior e inferior
  de 10 mm na faixa de todos os trilhos; invertido troca a ordem dos trilhos; estilo com `groove` ganha rasgo de
  20 mm na borda de encontro (só a borda direita da folha 0 e a esquerda das demais). `missing_depth`: precisa de
  `N·PITCH + 50 mm`.
- `appliances.layout(space, item, t)` (RN‑13a): painel na largura e altura do vão; **externo** no plano da frente para
  fora (Y −t a 0), **embutido** recuado (Y t a 2t); recorte centrado com a largura do maior eletro e a soma das alturas
  (forno embaixo, micro em cima) ou 440×30 do respiro; eletros de referência atrás do painel; eletro solto sem painel.
  `missing` → medida mínima em mm. `support_offset` existe mas não é chamado (o apoio é posto a 1/3 da altura do vão
  em `scene_interiors`).
- `position` (RN‑07c, D‑16): cotas `front`/`back` (recuos), `low`/`high` (distâncias às faces); `offset_from_cota`;
  `step_move`: seta anda o **Passo**, o primeiro toque usa o **Passo inicial** se > 0, sempre dentro de `offset_range`.

### 14.8 Dados gravados no módulo (`data_props.py`) 🟢

`Object.btm_structure` (`BTM_PG_Structure`, na raiz): `components` (só papéis mexidos: `role`, `removed`, `mode`,
`thickness`, `material`), `back_mode` `FULL`/`RECESSED`, `back_setback` 0,02, `auto_back`, `extras` (árvore: `kind`,
`enabled`, `value`); `item(role, create)`, `extra(kind, create)`, `to_dict`/`from_dict`, `extras_dict`/`extras_from_dict`,
`backs_dict`/`backs_from_dict`. `Object.btm_division` (`BTM_PG_Division`, na chapa): `is_division` + os 13 `FIELDS`
(`uid`…`follow`). `Object.btm_extra` (`BTM_PG_Extra`, nas peças da 008): `is_extra`, `kind` (19 tipos), `catalog_id`,
`space`, `slot`, `params` JSON. Ver dicionário §13.1.

### 14.9 Sessão e campos do painel (`props.py`) 🟢

`Session` (uma por vez, em `_session[0]`): `root_name`, `library`, `draft`, `parts`, `initial_parts`, `selected` (nome do
componente), `messages`, `adjustments`, `limits`, `view`, `window_ptr`/`area_ptr`/`restore_area_type`, `requests`
(fila `(tipo, dados)`), `request` (`ok`/`cancel`), `error`, e da 006/008 `space`, `spaces`, `space_labels`,
`removed_parts`, `library_path`/`library_box`, `last_moved`, `applied`; `dim_messages`, `edited` e `view_key` são
criados por `ops_editor.start_session` e `window.ensure_view`. `push` enfileira e redesenha; `blocking`.

`WindowManager.btm_cabinet_editor` (`BTM_PG_CabinetEditorState`): `width`/`height`/`depth` **virtuais** (`get` lê o
rascunho; `set` só enfileira `dimension`), espelhos `components`/`messages`/`adjustments`/`structure`/`divisions`,
`tab` (7 abas; número do enum estável: o antigo `FINISH` = 2 sumiu e cai em `STRUCTURE`), opções da próxima divisão,
`space` (enum dinâmico dos subvãos com `get`/`set` na sessão), e as opções das abas da 008 (`catalog_item`, `invert`,
`div_mode`, `div_kind`, `div_count`, `drawer_*`, `door_*`, `interior_*`, `slide_*`, `back_tab`, `step` 10 mm,
`step_initial`). `_add_virtual_fields` cria antes do registro, por anotação, `tree_<chave>`/`value_<chave>` (árvore de
extras), `comp_<papel>` (caixa marcada = chapa presente; desmarcar enfileira `REMOVE_PART` em `KEEP`), `bays` e
`pos_front`/`pos_low`/`pos_back`/`pos_high` (cotas da divisória selecionada). Todo `set` só enfileira um pedido
`edit`.

### 14.10 Ponte com a cena (`bridge.py`) 🟢

- `read_state(root)`: medidas por `selection.editing.get_dimension`; `spec.to_dict(adapter.read(root))` mais `_raw`
  (os campos crus de `btm_custom` por vão, `pull_model`/`pull_all_fronts` e grupos da raiz, material por peça), para
  reaplicar um instantâneo devolver exatamente o que havia; estrutura, divisões cruas, extras, deslizantes
  (`scene_slides.state_of`), internos e fundo.
- `apply_state(context, root, target)`: medidas que diferem (> 1e‑7); por vão, `set_front` só se frente/quantidade
  mudou e `set_interior` só se o interior mudou; grava os crus; `reapply.reapply`; `_apply_structure` (restaura, edita,
  remove nessa ordem por papel); fundo; divisões (`apply` se mudaram, senão `reflow(force)`); extras; internos;
  deslizantes refeitos quando mudaram **ou** quando o alvo tem deslizantes (`opens` fora da comparação).
- `edit(context, root, action, data)`: despacha `EDIT_006` (`ADD_DIVISION`, `EDIT_DIVISION`, `REMOVE_DIVISION`,
  `EDIT_PART`, `REMOVE_PART`, `RESTORE_PART`, `SET_ASSEMBLY`) e `EDIT_008` (`TOGGLE_EXTRA`, `SET_BAYS`, `SET_BACK`,
  `ADD_MANY`, `REMOVE_IN_SPACE`, `INSERT_DOORS`, `INSERT_DRAWERS`, `INSERT_INTERIOR`, `REMOVE_INTERIOR`,
  `INSERT_SLIDES`, `REMOVE_SLIDES`); as da 003 (`FRONT` — mesma frente não refaz nada, o face frame reconstruiria o
  vão —, `STYLE`, `PULL`, `MATERIAL`, `INTERIOR`) iguais a `customize/ops_customize`, sem operador. A ordem importa:
  o registro em `btm_structure` muda **antes** do adaptador, porque o recálculo da biblioteca reafirma o que está
  gravado.
- Estrutura: `remove_part` (capacidade por papel; modo efetivo por `allowed_mode`; grava e chama
  `adapter.remove_part`), `restore_part` (desfaz com o modo usado; `_tidy` apaga o registro que voltou ao padrão),
  `edit_part` (espessura recusada se a biblioteca não deixa; `reaffirm`), sempre seguidos de
  `scene_divisions.reflow(force)`. `configured_part(role)`: material e espessura do componente do papel no
  Configurador da linha do módulo (`standards.api`).
- Montagem e padrão (012): `is_caffmob_module` (`btm_kind == 'MODULE'` com `btm_cabinet`), `origin_definition`
  (padrão global pelo `btm_standard_uid`, senão o ativo), `is_own_standard` (`apply_core.is_own`: overrides, montagem
  diferente da origem ou espessura por papel), `set_assembly`.
- Divisões: `division_context` (raízes, núcleo, crus, nomes); `add_division` (espessura do Configurador ou própria do
  distanciador; "p/ Divisão" exige o vão logo à direita/acima de uma divisória, `follow` = uid dela); `edit_division`,
  `remove_division`, `set_bays` (mantém os dicionários crus das que ficam), `add_many`, `remove_in_space`.
- 008: `toggle_extra` (Base Superior Recuada remove/restaura o tampo em `KEEP`), `set_back` ("Este armário não tem
  fundo" fora do `btm` sem peça de fundo; `insert` devolve o fundo removido; `set_back_recess`),
  `library_opening(space)` (vão da biblioteca que contém o **centro** do subvão, o de menor área frontal — D‑05),
  `insert_doors` (`DOOR_FRONTS[(escopo, invertido)]`; basculante por região ou escopo `FLIP`), `insert_drawers`
  (gavetão 2–4; interna só no frameless, via `set_interior(drawers=n)`; Blum grava `btm_custom.slide_kind = 'BLUM'`,
  lido por `cutting/hardware`), `insert_interior` (cabe? `appliances.missing`; `slot` novo = máximo + 1),
  `insert_slides` (avisos de profundidade e de folha bloqueada).
- Vista: `parts(context, root)` (bound box avaliada de cada filho visível, no referencial da raiz e com origem no canto
  mínimo de `stick.apply.local_box`; pula auxiliares `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `obj_x`,
  ocultos e em arame/caixa, menos os vãos; acrescenta as chapas que não são objetos, `elevation_parts` do `btm`);
  `opening_of(root, name)` (o vão mais interno que contém o objeto).

### 14.11 Peças na cena (`scene_divisions.py`, `scene_parts.py`, `scene_extras.py`, `scene_interiors.py`, `scene_slides.py`) 🟢

- Divisão = `CabinetPart` "Divisória N" filho direto da raiz (fora do que as bibliotecas reconstroem), com
  `btm_division` e `btm_component = 'DIV'`; material e espessura do componente Divisória do Configurador na linha
  `btm_line` (padrão `COZ`; closets `DOR`; espessura 15 mm, material MDF se faltar), salvo sobrescrita (RN‑10,
  RN‑12). `apply(wanted)` cria/atualiza/apaga por uid e chama `reflow(force)`. `reflow` recalcula e posiciona
  (`_place`: vertical gira −90° em Y com `Mirror Z`; inputs `Length`/`Width`/`Thickness` via `compat`; idprop
  `btm_raw_material`) e grava a assinatura `btm_division_sig` (vãos arredondados + crus + material + espessura); sai
  sem custo quando a assinatura não mudou; sem divisões, apaga a assinatura. `_borrow_material`: material de
  superfície da primeira chapa da estrutura (ou slot 0 da malha do `btm`).
- `scene_parts`: `extras_of`, `delete` (com descendentes), `place` (espessura no eixo mais fino: Z sem rotação; X com
  −90° em Y; Y com +90° em X), `make_part` (`CabinetPart` com `btm_extra`, `btm_component`, material bruto
  opcional), `make_box`/`make_cylinder` (malha BMesh simples para ferragem e eletro, idprop `btm_hardware`, fora do
  corte), `carcass_box` (caixa só das chapas da estrutura; `btm` pelas `elevation_parts`; recuo `bound_box` da raiz).
- `scene_extras.sync`: apaga e recria todos os extras pela árvore, com a espessura da lateral do Configurador (15 mm se
  faltar). `scene_interiors`: `entries` (um por `(catalogo, subvão, slot)`), `apply` (apaga e recria; item ou subvão
  inexistente vira aviso), recorte do painel = modificador `CPM_CUTOUT` com prefixo de agregado (vai para a usinagem
  da peça), apoio = prateleira `PRAT` a 1/3 da altura, pistão = caixa 20×250×20 mm `PISTAO`; `reflow` = `apply` das
  entradas atuais. `scene_slides`: trilhos `TRILHO_INF`/`TRILHO_SUP` num grupo **FRAME** "Deslizantes" com o estado
  JSON no idprop `btm_slides`; cada folha é `CabinetPart` `POR` num grupo **LEAF** de correr (007), com
  `leaf.make_leaf('SLIDE', slide_dir para o centro, travel 0,5)`; folha com curso livre < 10 mm volta como
  `('BLOCKED', folha, contato)`; reaplica as aberturas (`opens`); usa só o primeiro espaço‑raiz.

### 14.12 Handlers fora do editor (`reflow_handler.py`) 🟢

O frameless muda medidas por driver e força os drivers trocando de quadro (`run_calc_fix`), sem
`depsgraph_update_post` nem `after_rebuild`. Por isso dois handlers `@persistent`: `depsgraph_update_post` (raízes com
`btm_division_sig` entre as atualizações) e `frame_change_post` (todas as raízes com assinatura); ambos chamam
`scene_divisions.reflow` (barato pela assinatura), com trava `_running`, ignoram enquanto há sessão do editor e engolem
`ReferenceError`/`RuntimeError` (objeto apagado no meio). `register`/`unregister` simétricos.

### 14.13 Operadores (`ops_editor.py`, `ops_actions.py`) 🟢

| `bl_idname` | Rótulo | `bl_options` | Comportamento |
|-------------|--------|--------------|---------------|
| `caffmob.cabinet_editor` | Abrir editor de armário | `REGISTER` | `poll`: janela, sem sessão, módulo ativo com adaptador; `start_session`; `window.open_editor` (falha → `end` e erro); chama o modal na área nova |
| `caffmob.cabinet_editor_modal` | Editor de Armário | `REGISTER`, `UNDO`, `INTERNAL` | Timer 0,1 s; executa a fila; OK → `FINISHED` (um passo de desfazer); Cancelar/janela fechada/raiz apagada → `rollback` e `CANCELLED`; Ctrl/Cmd+Z, Ctrl+Shift+Z ou Ctrl+Y; setas; roda zoom 1,15; clique escolhe chapa ou vão; Esc = Fechar |
| `caffmob.cabinet_editor_confirm` | Confirmar | `REGISTER`, `INTERNAL` | `poll` recusa com erro bloqueante; `request = 'ok'` |
| `caffmob.cabinet_editor_cancel` | Cancelar | `REGISTER`, `INTERNAL` | Com rascunho alterado, `invoke_confirm` "Descartar"; `request = 'cancel'` |
| `caffmob.cabinet_editor_close` | Fechar | `REGISTER`, `INTERNAL` | Com alterações, diálogo Continuar / Descartar / Confirmar (este recusa com erro) |
| `caffmob.cabinet_editor_apply` | Aplicar | `REGISTER`, `INTERNAL` | `poll`: sem erro e rascunho alterado; enfileira `apply` (`ed.undo_push` + `apply_point`) |
| `caffmob.cabinet_editor_edit` | Editar componente | `REGISTER`, `INTERNAL` | Ações da 003 sobre `selected_path()` (vão da peça selecionada ou o vão da biblioteca do alvo); diálogos; alturas "a; b" |
| `caffmob.cabinet_editor_history` | Desfazer no editor | `REGISTER`, `INTERNAL` | `redo` |
| `caffmob.cabinet_editor_save_module` | Salvar como módulo | `REGISTER`, `INTERNAL` | Seleciona a raiz e chama `caffmob.module_save` |
| `caffmob.cabinet_editor_division_add` / `_edit` / `_remove` | Divisão | `REGISTER`, `INTERNAL` | Exige subvão; edição pré‑preenchida; material do enum `MATERIAL_ITEMS` |
| `caffmob.cabinet_editor_part_remove` / `_restore` / `_edit` | Componente externo | `REGISTER`, `INTERNAL` | Remover mostra os 3 modos com o motivo dos indisponíveis; espessura 0–60 mm |
| `caffmob.cabinet_editor_insert` | Inserir | `REGISTER`, `INTERNAL` | `tab`; `description` dinâmico com o motivo; `insert_reason` (D‑21) e `insert_payload` por aba |
| `caffmob.cabinet_editor_pick` | Escolher item | `REGISTER`, `INTERNAL` | Grava `catalog_item` |
| `caffmob.cabinet_editor_remove_item` | Remover | `REGISTER`, `INTERNAL` | Interno por `slot` ou os deslizantes |

Todos os botões só fazem `Session.push`; quem muda a cena é o modal (`process`), dentro de um `try` que converte
`ValueError`/`RuntimeError` em `s.error`. `refresh` relê as peças, grava um passo no rascunho (ou só `current`), refaz
os Ajustes automáticos (`elevation.diff` contra `initial_parts`), junta as mensagens (`DIM` guardadas por campo, `GEO`,
`DIV`, `STR`, `LIB-001` para avisos da biblioteca), recalcula subvãos (no referencial da vista), peças removidas (para
o tracejado) e o vão da biblioteca do alvo, e espelha tudo no `WindowManager` (`_sync_ui` desliga a sessão por um
instante para mudar o índice sem disparar o `update`). Clique (D‑06): primeiro as chapas que não são frente nem vão e
que não cobrem o subvão inteiro sob o clique (o fundo não rouba a escolha); sem chapa, escolhe o subvão (folha de
menor área). `_arrow`: só se a orientação andar no eixo da seta.

Payload das abas (`insert_payload`): Divisões → `REMOVE_IN_SPACE` ("Sem Divisória"), distanciador (`ADD_DIVISION`
`SPACER` com a espessura do item), `ADD_MANY` (inserção múltipla) ou `ADD_DIVISION` `FIXED`/`MOVABLE` (item com/sem
recuo muda o recuo frontal); Gavetas → `INSERT_DRAWERS`; Portas → `INSERT_DOORS`; Internos → `INSERT_INTERIOR`;
Deslizantes → `INSERT_SLIDES`; Fundos → `SET_BACK` com `insert`.

### 14.14 Janela e desenho (`window.py`, `previews.py`) 🟢

Mesma mecânica do editor de paredes (`canvas2d/window`): janela nova com Image Editor sem imagem, painéis na aba
"Editor de Armário", um `draw_handler_add` `POST_PIXEL` global em `SpaceImageEditor` que só desenha na área do editor
(removido no `unregister`). `ensure_view` reenquadra (`View2D.fit`, margem 0,18) quando muda o tamanho da área ou os
limites das peças. `draw_editor`: fundo; peças do fundo para a frente com preenchimento por tipo, borda vermelha nas
que têm mensagem; vãos tracejados; peças removidas tracejadas com "removido" e subvãos tracejados (aba Divisões), o
escolhido destacado com rótulo (o estado nunca só na cor); linhas de abertura das portas (`_hinge` pelo **nome** do
objeto: `flip`/`bascul` → em cima; `right`/`_r` no fim/`direit` → direita; senão esquerda); nas abas Gavetas e Portas
o vão da biblioteca contornado, com aviso se for maior que o subvão; seleção; título "nome — L × A × P", estado do
rascunho e barra "Selecionado: …". `previews.icon_id(chave)`: carrega `thumbnails/<chave>.png` sob demanda numa
coleção `bpy.utils.previews` (0 se não há imagem → ícone nativo); `unregister` remove a coleção.

### 14.15 Painéis (`panels*.py`) 🟢

Região lateral do Image Editor, categoria "Editor de Armário", `poll` = área do editor (e a aba, nos `_TabPanel`).
`BTM_PT_CabinetEditorTabs` (tipo pela biblioteca — `CABINET_TYPE`, `hb_closet_starter.closet_type`, `btm_cabinet.cabinet_type`
—, estado "Rascunho alterado/Aplicado/Sem alterações", 7 abas só com ícone, erro da sessão); Estrutura: Definições
(Número de vãos, medidas com a faixa), Componentes (montagem e "Padrão próprio" no módulo CAFFMob; caixa por papel +
✎ editar + ▾ modos; árvore de extras com `layout.panel` recolhível), Posição (cotas, só com divisória selecionada),
Movimentação (passos), Materiais (grupo e frentes do vão); Divisões: Inserir divisão (alvo, chapa do Configurador,
modo, tipo, catálogo, recuos, Inserir, propriedades), lista de divisões (editar, remover), Interior da biblioteca;
Gavetas, Internos (grade apagando o que não cabe; inseridos com remover; subaba Biblioteca só aponta para "Meus
módulos"), Portas, Deslizantes (aviso de profundidade, Remover), Fundos (Inteiro/Recuado, recuo, automático); rodapé:
Mensagens, Ajustes automáticos (até 30), Desfazer/Refazer, OK/Cancelar/Aplicar, Fechar, Salvar como módulo.
Face frame mostra "Face frame ainda não entra no plano de corte". `panels_tabs_common.registrar` gera
`register`/`unregister` das abas da 008.

### 14.16 Constantes de domínio

| Constante | Valor | Onde | Significado |
|-----------|-------|------|-------------|
| `PRECISION` | 6 | `state.py` | Casas (m) da assinatura do rascunho |
| `TOLERANCE`, `DEFAULT_LIMITS` | 1 mm; 0,01–10 / 0,005–10 m | `validate.py` | Folga GEO; faixa geral das medidas |
| `TOLERANCE` | 0,1 mm | `elevation.py` | Peça que não mudou no diff |
| `ROLES`, `MODES`, `THICKNESS_RANGE` | 5 papéis; `KEEP`/`EXTEND`/`SHRINK`; 3–60 mm | `structure.py` | Componentes externos |
| `ROLE_COMPONENT` | `BAS`, `BAS`, `LAT`, `LAT`, `FUN_INF` | `structure.py` | Papel → Configurador |
| `LATERAL`, `BASE` | montagens | `structure.py` | Feature 012 |
| `MIN_SPACE`, `MIN_DEPTH`, `DEFAULT_SETBACK` | 50, 50, 20 mm | `divisions.py` | RN‑13, RN‑14 |
| `FIXED`, `MOVABLE`, `SPACER` | tipos | `divisions.py` | Divisória fixa, móvel, distanciador |
| `ROOT`, `MAX_BAYS` | `s0`; 10 | `bays.py` | Número de vãos |
| `FOOT_RADIUS`, `FOOT_INSET`, `KICK_SETBACK`, `RECESS`, `CEILING` | 20, 50, 50, 20 mm; 2,70 m | `extras.py` | Geometria dos extras |
| `DEFAULTS` | pés 150, fechamento 50, vistas 150 mm | `extras.py` | Valores das capturas do Promob |
| `PITCH`, `LEAF_THICKNESS`, `OVERLAP`, `TRACK_HEIGHT`, `DEPTH_MARGIN`, `GROOVE` | 20, 18, 30, 10, 50 mm; 20×8 mm | `slides.py` | Portas de correr |
| `APPLIANCE_SIZE_MM`, `VENT_SIZE` | forno, micro, cafeteira; 440×30 mm | `catalog.py`, `appliances.py` | Eletros de referência |
| `PANEL_THICKNESS`, `PISTON_BOX` | 18 mm; 20×250×20 mm | `scene_interiors.py` | Painel p/ eletro e pistão |
| `NAME`, `COMPONENT`, `COMPONENT_PROP`, `SIGNATURE_PROP` | "Divisória", `DIV`, `btm_component`, `btm_division_sig` | `scene_divisions.py` | Chapa de divisão |
| `DEFAULT_LINE` | frameless/face frame/btm `COZ`, closets `DOR` | `scene_divisions.py` | Linha do Configurador |
| `HARDWARE_PROP`, `FRAME_TAG` | `btm_hardware`, `btm_slides` | `scene_parts.py`, `scene_slides.py` | Ferragem; estado dos deslizantes |
| `TRACK_CODES` | `TRILHO_INF`, `TRILHO_SUP` | `scene_slides.py` | Ferragem dos trilhos |
| `DOOR_FRONTS` | (escopo, invertido) → frente | `bridge.py` | Aba Portas |
| `CUSTOM_FIELDS`, `_LIBRARY_HOLDER`, `_SKIP_TAGS` | — | `bridge.py` | Crus do instantâneo; faixa por biblioteca; auxiliares fora da vista |
| `TIMER_STEP` | 0,1 s | `ops_editor.py` | Timer do modal |
| `EDITOR_CATEGORY` | "Editor de Armário" | `props.py` | Aba da região lateral |

Tratamento de erros: os núcleos puros devolvem listas de `Message` (só `divisions.add`/`add_many` e o "p/ Divisão"
levantam `ValueError`, que o modal mostra em `s.error`); a ponte devolve listas de avisos da biblioteca (viram
`LIB-001`); `window.open_editor` levanta `RuntimeError` sem janela; `reflow_handler` engole `ReferenceError`/
`RuntimeError`; raiz apagada ou janela fechada encerram a sessão com rollback e aviso. Observações:

- 🟡 **Cancelar não desfaz a troca de montagem**: o painel Componentes edita `root.btm_cabinet.assembly` direto
  (`panels_structure.py:43`), fora da fila do modal, e `EditorState` não guarda a montagem; `apply_state`/`rollback`
  não a tocam. A ação `SET_ASSEMBLY` da ponte existe mas nenhum botão a usa.
- 🟡 **Mover divisória não reposiciona os internos**: `edit_division` (`bridge.py:472`; cotas, setas, diálogo de edição) só chama
  `scene_divisions.apply`; ao contrário de `add_division`/`remove_division`/`set_bays`, não chama `reflow_all`, então
  painéis de eletro, apoios e pistões do subvão afetado ficam na posição antiga até a próxima ação que refaça tudo.
- 🟡 Fora do editor, `reflow_handler` só reposiciona divisões; extras, internos e deslizantes dependem do
  `customize.after_rebuild`, que o frameless não chama ao mudar medida por driver.
- 🟡 Os itens de divisória "Tras 15mm" (`DIV_RECESS`, `DIV_NO_RECESS`) têm `params` `back = 15`, mas
  `ops_actions._division_payload` (`ops_actions.py:420`) só aplica o recuo frontal; o de trás vem das opções do painel.
- 🟡 Na aba Portas, as regiões Inferior/Superior/Alta não mudam nada (`bridge.insert_doors`, `bridge.py:599`, só lê o escopo e
  Basculante).
- 🟡 Nome da divisória = `len(objects) + 1` (`scene_divisions.py:99`): depois de remover uma do meio, a nova repete um nome existente (o Blender
  põe `.001`) e a lista ordena por nome ("Divisória 10" antes de "Divisória 2").
- 🟡 Linha de abertura da porta depende do nome do objeto (`window._hinge`, `window.py:128`), não do idprop de dobradiça.
- 🟢 `appliances.support_offset` (`appliances.py:68`) não é usado (código morto); o apoio fica a 1/3 da altura do vão.

Testes (12 puros, 74 casos, todos passando em 2026‑10‑10): `test_cabinet_editor_state` (4), `_validate` (5),
`_elevation` (4), `_structure` (10), `_divisions` (16), `test_cabinet_catalog` (7), `_extras` (6), `_bays` (5),
`_slides` (5), `_appliances` (5), `_position` (3), `test_structure_assembly` (4); fumaça no Blender
`blender_004_cabinet_editor_smoke`, `blender_006_cabinet_editor_tabs_smoke`, `blender_012_cabinet_standard_smoke`.
Textos em `data/translations/cabinet_editor.json` (288 chaves).


## 15. Módulo `standards` (`caffmob_draw/standards/`)

Análise de 2026-10-10, nível **detalhado**, código do pacote efetivamente empacotado. 🟢 **CONFIRMADO** significa
leitura direta do código ou execução indicada; 🟡 **INFERIDO** indica intenção ou semântica externa não comprovada;
🔴 **LACUNA** requer validação humana. Nenhuma correção de implementação foi feita nesta escavação.

### 15.1. Escopo e responsabilidades

Fonte única de valores do Padrão de Dimensões, com definições nomeadas BR/US persistidas na cena principal,
rascunho do Configurador, migração de projetos antigos e importação/exportação JSON e XML DIMENSIONEXPORT.
Nas features 001/012 passou a fornecer espessuras por papel, montagem e dimensões por linha aos módulos CAFFMob.

| Camada | Arquivos e linhas | Responsabilidade |
|---|---|---|
| Modelo RNA | `standards/model.py:20–146` | Seis PropertyGroups; cena persistente e rascunho no WindowManager |
| Esquema puro compartilhado | `data/dimension_schema.py` | 870 parâmetros, 5 linhas, 20 componentes, 1.042 IDs Promob; validação e destinos legados |
| Embutidas | `standards/builtin.py:9–59` | `builtin-br` / `builtin-us`, preencher apenas valores ausentes |
| API | `standards/api.py:23–478` | Definição ativa, gestão, valores, rascunho, árvore, callbacks e pendências |
| Decisão pura | `standards/apply_core.py:14–42` | `ModuleInfo`, `Plan`, padrão próprio e seleção de alvos |
| Medidas puras | `standards/cabinet_defaults.py:16–64` | Converter mm → m; defaults por tipo e espessura por papel |
| Propagação | `standards/sync.py:22–291` | Cena principal/atual, CAFFMob, suporte legado e overrides |
| Arquivos | `standards/io_json.py:16–186`, `io_promob.py:24–190` | Validação, conversão, preservação de atributos e escrita atômica |
| Migração | `standards/migration.py:21–154` | M-01/M-02 uma vez; M-03 a cada abertura; timer inicial |
| Imagens | `standards/previews.py:13–53` | Cache de previews e aviso único por imagem ausente |
| Operadores e UI | `operators/ops_standards.py:24–615`, `ui/standards_tree.py:14–52` | 13 operadores, árvore e duas confirmações de aplicação |

Dependências internas: `data.dimension_schema`, `data.units`, `data.i18n`, `data.properties`, `hb_project`,
`selection.classify`, `legacy.gate`, `cabinet_editor.bridge/structure`, bibliotecas `frameless` e `closets`.
Integração externa é **arquivo local Promob**, sem requisição HTTP, credenciais ou banco de dados neste módulo.
Consumidores incluem construção de armários, edição/medição, conversão legada e extração de peças para corte.
`surface.json` conserva o inventário original (`blendertomob`, seis módulos); a análise atual usa
`caffmob_draw/` e atualiza `modules.json`, sem tratar o Scout histórico como inventário vigente.

### 15.2. Esquema e domínio dos valores

🟢 `dimension_schema.py` gera 5 medidas máximas globais + 5 × 13 dimensões externas + 5 × 20 × 8 campos de
componente = **870** parâmetros. Linhas: COZ, DOR, BAN, SAL, ESC. Campos por componente: material, largura máxima,
comprimento máximo, espessura e quatro fitas. Materiais: MDF, MDP, COMPENSADO, OSB, VIDRO, OUTRO.

Comprimentos armazenados em **mm**; `get_value_m`, migração inversa e sincronização fazem conversão por 1.000.
Padrão BR: caixa 15 mm, frentes 18 mm, fundos 6 mm, fitas visíveis 0,4 mm; US: caixa/frentes 19,05 mm,
fundos 6,35 mm e fitas 0 mm. As faixas são por parâmetro (espessura 3–60 mm, fita 0–5 mm); zero significa
sem fita/rodapé nos campos indicados. Há **17 chaves** com destino `hb_frameless`/`hb_closets`.

`PROMOB_EDGE_TO_SIDE = {4: 1, 3: 2, 1: 3, 2: 4}` converte numeração Promob para comprimento/largura do projeto.
🟡 A equivalência física de `ALT_ARM`/`PROF_ARM` com altura/profundidade de roupeiro é explicitamente inferida
no esquema, embora o mapeamento em execução seja 🟢 confirmado. Não presumir equivalência para famílias sem chave.

### 15.3. Definições e CRUD

`main_scene(scene=None) -> Scene|None` (`api.py:23`) tenta `hb_project.get_main_scene()`; captura qualquer
exceção e usa a cena fornecida. `ensure_ready` cria/completa embutidas e corrige índice acima da coleção;
indisponibilidade gera `StandardsError`. `active_definition` devolve None se coleção vazia e limita o índice.

`duplicate_definition(scene, definition, name=None)` guarda índice da origem **antes** de `add()` e reobtém
referências: UUID novo, nome único com sufixo `(2)`, USER, versão 1, timestamp, montagem e valores copiados,
atributos crus preservados; a cópia vira ativa. `remove_definition` recusa embutidas e ajusta índice.
`get_definition_value` usa o valor da coleção ou o default do mercado; chave desconhecida gera erro.
`definition_values` completa defaults e sobrepõe itens existentes (inclusive chaves fora do esquema).

`set_value` recusa embutidas; `_write` valida chave/domínio, cria item se necessário e escolhe texto/float.
`set_values` valida **todos os pares antes de gravar**; isso evita aplicação parcial por erro de domínio,
mas não constitui transação com rollback para falhas inesperadas durante escrita RNA.

### 15.4. Rascunho, pendências e árvore

`begin_draft(scene, wm)` copia definição ativa (montagem incluída), limpa erro e `include_manual`, completa
campos ausentes e reconstrói árvore. Não reinicializa `expanded`, `search` ou `selected_key`.
`pending_changes` inclui montagem e parâmetros conhecidos; números usam tolerância **1e-6 mm**;
nome/`include_manual` não contam como alteração de valor. Os valores são formatados na unidade do usuário.

`apply_draft(scene, draft, include_manual=False, modules=None)` exige definição existente/editável, renomeia
se necessário, copia rascunho e incrementa versão/timestamp **apenas se houver pendências de valores/montagem**.
Depois chama `sync.apply_definition` com chaves alteradas e devolve relatório com `changes`.
🟢 Não chama `set_values` nem revalida toda a coleção ao copiar: proteção de domínio ocorre nos setters normais.

Árvore: MAX; linha → EXTERNAL / CHAPAS / COMPONENTES → componente → parâmetro. Grupos fechados ocultam filhos;
busca por rótulo pt-BR, chave ou nome do componente abre todos os grupos relevantes. `expanded` é string `|`;
`rebuild_tree` limita índice com `_suppress` para não disparar edição/expansão recursiva.
`select_param` preenche campo; `commit_edit_text` usa `parse_length`, converte para mm e arredonda a 4 casas;
erros preservam último valor válido e aparecem em `draft.error`. Enum usa cache de strings por opções.

### 15.5. Plano de aplicação e padrão próprio

`apply_core.is_own(overrides, assembly, origin_assembly, role_thickness)` retorna verdadeiro se houver overrides,
montagem divergente ou qualquer espessura explícita > 0. `bridge.is_own_standard` (`bridge.py:335–343`) compara
com definição de origem (se UID não existe, ativa) e espessuras em `btm_structure.components`.

`plan(modules, previous_uid)` produz listas de **nomes**:
- `follow`: CAFFMob sem padrão próprio e UID vazio ou igual ao global anterior;
- `differ`: CAFFMob próprio ou de UID diferente;
- `not_applicable`: LEGACY e OTHER;
- `legacy`: subconjunto LEGACY, para orientação de conversão.

`targets(plan, apply_all, apply_differ)` é função pura testada; os operadores fazem a mesma escolha diretamente
nas listas, sem chamá-la. `scene_modules` reconhece CAFFMob MESH/MODULE com `btm_cabinet`, raízes herdadas pelo
gate e raízes de grupos livres/itens de biblioteca (não cada filho). `plan_for` também retorna mapa nome → objeto.

Configurador/Aplicar gravam com `modules=[]`; Definir ativa captura UID anterior, ativa e sincroniza com lista
vazia. Com janela, `ask_apply` abre a primeira pergunta. Sim aplica `follow`, depois oferece a segunda se houver
`differ`; Não/Cancelar mantém esses módulos. Em EXEC, `apply_differ=True` responde também à segunda pergunta.
Sem janela/background, `ask_apply` retorna e não abre diálogo; a sincronização anterior já gravou propriedades
de cena e, em modo de suporte, pode ter atualizado armários herdados.

### 15.6. Propagação e invariantes de geometria

`apply_definition` incrementa `_SYNC_DEPTH[0]` e restaura em **finally**, mesmo em erro. `is_syncing` permite
que callbacks externos distingam sincronização de edição manual. `_apply_definition`:
1. Expande valores com defaults e grava 17 destinos legados, em metros, na cena principal e na cena atual distinta.
2. Marca linhas ausentes de cages (frameless COZ, closet DOR).
3. Resolve alvos CAFFMob e aplica cada objeto existente em `bpy.data.objects`.
4. Somente com `gate.legacy_ui(context)`, atualiza prompts frameless e starters closets, preservando campos de
   `btm_overrides` quando `include_manual=False` (recalcula closet mesmo se todas as medidas forem puladas).
5. Marca `btm_settings.cut_plan_stale=True`; retorna contagens, destinos, medidas puladas e `without_target`.

🟢 **Diferença script/UI:** com `modules=None`, escolhe todos CAFFMob sem `own`, ou todos com `include_manual`;
**não compara UID ao padrão anterior**. Portanto um móvel de outra origem sem padrão próprio também pode mudar.
`modules=[]` evita alvos CAFFMob, mas não evita destinos de cena, marcação de linhas, invalidação do corte ou
propagação de suporte legado. `without_target` significa sem **destino legado**, não ausência de efeito moderno.

`apply_to_module` (`sync.py:231–250`) lê linha/tipo, mantém **largura e posição Z**, altera altura/profundidade,
espessura de caixa e espessuras por papel; usa 0 para papel igual à caixa (tolerância 1e-9 m), aplica montagem,
zera espessuras explícitas da estrutura, limpa todos overrides, grava UID/linha e reconstrói geometria uma vez
após `suspended_geometry`. Materiais da estrutura, modos de remoção e divisões não são apagados por essa rotina.
A lista explícita de alvos prevalece sobre `include_manual` para CAFFMob; skip por campo é legado.

`cabinet_defaults.defaults(values,line,type)` (`:42–64`) usa BASE se tipo desconhecido; se sem valores/linha inválida
ou sem `line.external.base_height`, devolve fallback com aviso. Larguras BASE/WALL/TALL = 0,8/0,8/0,6 m;
alturas = 0,72/0,70/2,2 m; profundidades = 0,55/0,35/0,55 m; Z = 0/1,5/0 m. Sem padrão, caixa 18 mm/fundo 6 mm.
Com padrão, altura/profundidade/Z vêm de externas e espessuras de `ROLE_COMPONENT`: TOP/BOTTOM→BAS,
LEFT/RIGHT→LAT, BACK→FUN_INF **para todos os tipos**, inclusive WALL/TALL. `carcass = thickness['LEFT']`.

### 15.7. JSON e XML Promob

JSON `.btmdim.json`: identidade `caffmob_draw.dimension-standard`, aceita também `blendertomob.dimension-standard`,
`schema_version=1`, unidade mm; converte chaves planas para máximas, externas, chapas/componentes e `edges[4]`.
Chaves não conhecidas na exportação são omitidas; na leitura linhas/parâmetros desconhecidos viram avisos,
valores de domínio inválidos abortam a importação. Unidade diferente e versão futura são recusadas.
`import_definition`: valida antes de criar, UID novo, USER, mercado BR se inválido, defaults preenchidos;
conflito renomeia ou substitui apenas definição não embutida. A importação **não ativa** a definição.

XML: `read_dimensionexport` exige raiz DIMENSIONEXPORT e ≥1 ATTRIBUTE com ID; normaliza espaços do nome.
`to_definition_data` preserva ordem/strings dos atributos; ID repetido usa **último valor para mapear todas as
ocorrências**, registra duplicados. Número aceita vírgula. Conhecido inválido é preservado com chave vazia,
não substitui default. `CAFF_MONTAGEM` é retirado dos crus, aceito sem diferença de caixa; ausente = LATERAL,
inválido = LATERAL com aviso. Fixture de 692 atributos: **335 ocorrências mapeadas, 357 não reconhecidas,
294 chaves distintas** (contagem executada nesta sessão).

`build_attributes` mantém string numérica original se diferença <1e-6; caso contrário quatro casas, vírgula,
sem zeros finais. Mantém atributos desconhecidos. Exportador usa crus existentes **ou**, se vazios, gera um
atributo por ID conhecido; não acrescenta novos IDs de campos ausentes ao XML de origem. XML exportado usa
VERSION=-1, ISSYSTEM=False, CHANGED=True; atributos da raiz/DEFINITION originais não são preservados.
Escritas JSON/XML usam arquivo temporário no diretório de destino + `os.replace`, limpando temporário em falha.

### 15.8. Migração, ciclo de vida e operadores

`migration.run` resolve cena principal. M-02 cria embutidas e escolhe US se houver cage frameless/closet,
BR caso contrário; não reconhece face_frame nessa decisão. M-01 lê apenas propriedades obsoletas explicitamente
setadas (`is_property_set`), converte m→mm, `config_*` prevalece sobre `dimension_settings`, filtra inválidos e
duplica BR como Migrada/MIGRATED, ativa. Cena recebe `btm_standards_migrated=1` mesmo sem valores migráveis.
M-03 carimba UID ativo nas raízes `classify.module_library` sem UID, sem reconstrução, a cada `run`.
`run` captura apenas StandardsError. `__init__.py:99` chama no load_file_post; timer inicial 0,5 s cobre startup
sem arquivo. Registro model → previews → migration; unregister inverso remove timer, previews e ponteiros RNA.

Todos os operadores de gestão/aplicação/importação têm REGISTER/UNDO; exportação REGISTER; relatório INTERNAL.
`_LAST_REPORT` é global de processo, não persistido. Configurador mostra oito pendências; relatório vinte alterações,
dez overrides e dez chaves sem destino. `standards_duplicate` ativa cópia, mas não aplica à cena automaticamente.
Rename/Delete possuem poll para proteger embutidas. StandardsApplyScene/ApplyDiffer recalculam plano no execute,
evitando usar contagem do invoke como escolha definitiva.

### 15.9. Limitações confirmadas e lacunas

- 🟢 **JSON não leva montagem:** nem `values_to_document`, nem `export_definition`, nem importação incluem assembly.
  Uma definição BASE reimportada recebe default RNA LATERAL. XML preserva o campo por CAFF_MONTAGEM.
- 🟢 **NaN aceito:** `schema.validate` converte float e compara faixa sem `isfinite`; probe com NaN em espessura
  retornou `(True, '')`. Defaults/JSON/parse Promob não fornecem validação adicional de finitude.
- 🟢 **Forma interna do JSON:** `lines={'COZ': []}` gera AttributeError em `document_to_values`; estruturas aninhadas
  e metadados não são integralmente validados. Schema_version checa int e teto, mas aceita bool/inteiro ≤0;
  `version` é convertido depois de criar definição. Não documentar importação como transação integral.
- 🟢 `apply_draft` copia sem revalidar coleção completa; renomear sozinho não incrementa versão/timestamp.
- 🟢 `standards_apply_scene` aplica follow antes da segunda confirmação; não é operação tudo-ou-nada entre as
  perguntas. Em suporte legado, sincronizações de seleção vazia já podem atualizar cages.
- 🟡 Realocação RNA merece revisão: `duplicate_definition` reobtém origem e `ensure_builtins` reobtém retorno,
  mas o laço de duas embutidas guarda referências no dicionário local antes de uma próxima adição. Não foi
  reproduzido crash; não tratar como falha confirmada.
- 🔴 Não foi executada nesta sessão a integração RNA/UI/undo em Blender; testes puros não confirmam ausência de
  invalidação de referências, coerência de cenas múltiplas nem sequência real dos diálogos.
- 🔴 Compatibilidade prática de CAFF_MONTAGEM com Promob depende de validação no aplicativo externo; código
  afirma que ID desconhecido é ignorado, mas o round-trip desta sessão ocorreu apenas nos leitores do projeto.

### 15.10. Verificação e fluxogramas

🟢 `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_dimension_schema test_promob_io
 test_promob_assembly test_standards_apply_core test_cabinet_defaults -v`: **35 testes passaram** em 2026-10-10.
Esquema (14), XML (12), montagem (3), plano (3), defaults (3). Smoke disponível:
`tests/blender_012_cabinet_standard_smoke.py` (não executado nesta análise documental).

Fluxogramas: `flowcharts/standards.md`, `standards-apply_scene.md`, `standards-sync.md`,
`standards-promob_io.md`, `standards-draft.md`, `standards-migration.md`.


## 16. Módulo `legacy`

🟢 **CONFIRMADO** por leitura dos sete arquivos do pacote (705 linhas), em 2026-10-10. Feature 012. A camada mantém frameless, face_frame e closets registrados para carregar e converter dados antigos; esconde as entradas de UI por preferência. Molduras também usam a porta, mas não integram LEGACY_LIBRARIES. Nenhum código alterado.

### Escopo, porta e ciclo de vida

`gate.legacy_ui(context=None)->bool` lê preferences.addons[pacote].preferences.show_legacy_libraries; ausência é false. `is_legacy(obj)` usa selection.classify.module_library. `legacy_roots(scene)->list[Object]` percorre os ancestrais e exclui uma raiz aninhada em outra raiz herdada. Custo aproximado O(objetos + raízes × altura da árvore).

`neutralize_product_tab` atua em todas bpy.data.scenes quando suporte desligado: product_tab=FRAMELESS; seleção frameless/face_frame=Cabinets, closets=Starters. Não remove bibliotecas ou enums. `on_load_post` é persistent, neutraliza e registra timer notify_legacy de 1 s se ausente. O timer avisa só na cena atual, sem suporte; retorna None (uma execução). Register registra dois operadores e handler; unregister remove timer, handler e classes. Neutralização não é chamada diretamente no register. Fonte: __init__.py:19–73; gate.py:13–47.

### Tradução pura e perdas

`convert_core.translate(cabinet)->(dict,list[Loss])` conserva width/height/depth em metros. Tipos BASE/UPPER/WALL/TALL viram BASE/WALL/WALL/TALL; desconhecido vira TALL a partir de 1,2 m, BASE abaixo, com TYPE_APPROX. Linha válida permanece; fallback DOR para CLOSETS e COZ para demais. Soma prateleiras do armário e dos vãos, sem conservar sua distribuição/posição original. Retorna assembly=LATERAL, porém a construção integrada usa montagem do padrão ativo.

Portas somam DOOR_LEFT=1, DOOR_RIGHT=1 e DOUBLE_DOORS=2; ≥2 produz DOUBLE e perda EXTRA_DOORS para o excedente. Uma porta usa lado da primeira ocorrência. Sem portas, FLIP_UP produz FLIP; múltiplos basculantes viram um só sem contagem individual de perda. Com portas e basculante, SPECIAL soma uma perda. DRAWERS perde max(1,drawer_count), PANEL perde um, frente desconhecida e each other_fronts perdem SPECIAL. OPEN/vazio/None não perdem. Quantidades são agregadas por chave; não há validação de dimensões ou teto de prateleiras no tradutor. Fonte: convert_core.py:43–103.

### Leitura, construção e exclusão em lote

`read_cabinet(root)` usa bound_box avaliado da raiz no espaço local; volume com qualquer dimensão ≤1e-6 m cai para selection.editing.get_dimension. Caixa fallback: (0,-depth,0)→(width,0,height). Tipo vem das propriedades face_frame/closet ou CABINET_TYPE. Adaptador customize fornece frentes/prateleiras; exceção em adapter.read é capturada e devolve [] sem aviso. Frentes especiais face_frame são lidas também em children_recursive (PULLOUT/TILT_OUT/INSET_PANEL/APPLIANCE), podendo coexistir com perdas do leitor principal.

`_read` guarda nome, biblioteca, DTO, caixa, cópia matrix_world, pai, primeira coleção (ou context.collection) e contagem dos agregados próprios. `_build` usa chapas/espessuras e montagem do padrão ativo, dimensions originais e frente simplificada. Transformação: world_original @ Translation((lo.x+hi.x)/2, hi.y, lo.z); conserva pai e ajusta matrix_parent_inverse. Isso alinha o módulo CAFFMob centrado em X com a caixa local original; escala/rotação são herdadas da matriz.

`convert_scene(context, roots=None)->list[Result]` filtra raízes existentes/herdadas, lê todas, constrói todas e então delete_components(roots,keep_aggregates=False) em lote. Itens grudados são soltos no lugar pelo helper; agregados próprios são excluídos, com perda AGGREGATES adicionada. Renomeia módulos após apagar originais. Lista explícita não repete a filtragem de aninhamento de gate.legacy_roots. Não há rollback explícito: erro ao construir um item pode deixar os anteriores novos coexistindo com originais. Operador legacy_convert tem REGISTER/UNDO, mas não captura erro do lote; valida only_active em execute; poll exige OBJECT e algum legado na cena. Fonte: convert.py:31–159; aggregates/ops_aggregate.py:235–263.

### Grupos salvos e marcador

`group_items` consulta pasta cabinet_groups pela biblioteca frameless (também usada pelo face_frame); OSError→[]. Marcador em modules_root/legacy_groups.json guarda offered bool e converted list de caminhos. Parse inválido retorna {}; schema-version exportado=1 não é verificado na leitura. Pending é diferença por string de caminho, não hash/mtime; arquivo modificado no mesmo caminho permanece concluído. Oferta no painel usa cache, suporte deve estar desligado e offered=false.

`convert_group(context,name,filepath)->(saved,lines,error)` tira snapshot de 11 coleções bpy.data; cria coleção temporária; carrega todos objetos do .blend, liga ao holder, atualiza view layer, converte raízes não aninhadas presentes. Cada armário vira módulo na categoria Geral; grupo múltiplo vira Nome 1/Nome 2; colisão por casefold recebe (2),(3)…; save com miniatura. Finally remove blocos novos e holder, capturando ReferenceError/RuntimeError por bloco. Original .blend não é sobrescrito. OSError/RuntimeError do processamento viram mensagem; outras exceções propagam após cleanup.

`convert_pending` percorre pendentes, reúne relatórios e marca caminho como convertido quando error é None. Erros retornados por library_io.save entram apenas em lines, **não em error**: grupo parcialmente salvo ou sem armários pode ser marcado concluído. Escrita do marcador usa temporário+os.replace, sem finally de limpeza do temporário em falha. `groups.dismiss` marca offered=true; operador grava isso no invoke **antes** da confirmação (cancelamento também esconde oferta). Esse operador é REGISTER sem UNDO: escreve arquivos externos. Fonte: groups.py:24–154; groups_core.py:12–53; ops.py:75–103.

### Evidência e lacunas

🟢 7 testes existentes passaram: test_legacy_convert (4) e test_legacy_groups (3), executados via PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_legacy_convert test_legacy_groups -v. Cobrem tipos, frentes, perdas, prateleiras, linhas, marcador e nomes. Smokes disponíveis blender_012_legacy_gate_smoke.py e blender_legacy_smoke.py não executados nesta análise.

🔴 **LACUNAS**: integração bpy/undo, transformações com escala/pai complexo e importação real de .blend precisam de verificação de runtime. Relatório 'sem perdas' não garante equivalência estrutural: usa apenas perdas contadas; prateleiras redistribuídas, espessuras/materiais do padrão ativo e leitura do adaptador que falhou não são necessariamente reportados. 🟡 Redistribuição é comportamento esperado do destino simplificado; aceitação pelo usuário deve ser validada.

Fluxogramas: legacy.md, legacy-translate.md, legacy-convert_scene.md e legacy-groups.md.


## 17. Módulo `library_panel`

🟢 **CONFIRMADO**, 11 arquivos/905 linhas do pacote, 2026-10-10. Feature 012: biblioteca de móveis paramétricos no topo de VIEW_3D; distinta da biblioteca object_library (Inserir › Objetos). Não faz download nem usa banco de dados.

### Categorias e arquivos

`categories_core.Category(name,line,fixed)`; fixas ordenadas Cozinha/COZ, Banheiro/BAN, Sala/SAL, Home office/ESC. DOR é linha disponível, mas não categoria fixa. Usuário aparece depois das fixas, ordem de criação. validate_name exige texto não vazio, sem / ou barra invertida, e nome único por strip+casefold contra fixas/usuário. Parse tolera JSON malformado, ignora itens sem nome/duplicados e usa COZ para linha desconhecida; não valida schema-version nem aplica validate_name às categorias importadas. `merge_folders` inclui pastas soltas não ocultas/não conhecidas como COZ. `with_line` altera categoria por casefold sem validar domínio da linha.

`categories.load()->(list[Category],list[str])` cacheia leitura de categories.json na raiz de módulos do usuário. Pasta preexistente vira categoria e, se houver diferença **e nenhum aviso**, grava migração. Sem arquivo usa vazio; OSError distinto de FileNotFoundError retorna aviso sem cachear. `save` mkdir+temporário+os.replace, remove temporário em falha e atualiza cache. `create` valida, mkdir da categoria, depois save: não desfaz pasta se a gravação falhar. `set_line` escreve arquivo; não modifica módulos já salvos. `find` usa igualdade exata de nome. Fontes: categories_core.py:14–100; categories.py:15–91.

### Layout puro, desenho e eventos

`Layout(label,items)` em pixels da região, Y de baixo para cima. Painel fechado só título BIBLIOTECA CAFFMOB; aberto coluna com largura máxima entre textos+padding. Posição x=nav_right+8×scale se HUD ligado, ou x_min+8×scale; topo=y_max-12×scale. Linhas=24×scale, espaçamento=2×scale, padding=12×scale. menu_items: oferta de converter grupos (se pendentes), criar armário, categorias CAT:nome, criar categoria. Hit testa limites inclusivos, título antes de itens; bounds engloba todos retângulos. Não há scroll ou limitação à altura/largura da viewport.

`draw.layout` usa limites visíveis (não tamanho bruto) e cache por region.as_pointer, chave=(x_min,y_max,ui_scale,open,entries,nav_right). Largura de texto via blf. Painel POST_PIXEL registrado sempre, independente do HUD; draw sai cedo fora de VIEW_3D/WINDOW ou sem estado. Usa GPU UNIFORM_COLOR, ALPHA e volta a NONE após retângulos. Cache limpo no unregister, não explicitamente ao fechar uma região. Mouse global guarda pos/region; redraw apenas ao trocar alvo de hover.

Keymap 3D View: LEFTMOUSE PRESS, MOUSEMOVE ANY, ESC PRESS; head=True, any=True exceto Esc. Operadores curtos, sem modal permanente. Clique fora fecha aberto e retorna PASS_THROUGH para seleção; hover também passa adiante; Esc com aberto retorna FINISHED. dispatch LABEL alterna estado e invalida cache de categorias ao abrir; item fecha painel antes de disparar operador com poll. Categoria grava state.category/state.line e abre popover nativo; desconhecida usa COZ. Unregister remove keymaps, operadores e handler. Fontes: layout_core.py:16–79; draw.py:26–127; ops_click.py:16–142.

### Popover, modelos e criação

`popover.show` guarda categoria em global _open e abre popup 16 unidades. `_draw` resolve linha da categoria e mostra modelos prontos em duas colunas, ícone MESH_CUBE; módulos salvos aparecem como botões IMPORT. **Não carrega miniaturas nesse popover**. Listagem de salvos filtra categoria por casefold e captura OSError/ValueError. Modelos são relidos do JSON em cada draw; não há cache de models_core.load_default. Linha de categoria do usuário pode ser editada; as fixas não oferecem esse botão.

`models_core.parse(text)->(list[Model],warnings)` exige ID, tipo BASE/WALL/TALL e swing NONE/LEFT/RIGHT/DOUBLE/FLIP; width_mm/shelves converte int e limita mínimo zero. Não rejeita IDs repetidos, não impõe máximos, e número não conversível propaga ValueError/TypeError. Catálogo do pacote tem 5 modelos: balcão/aéreo de uma porta (450 mm), balcão/aéreo duas portas (800 mm), torre (600 mm, 4 prateleiras); demais têm 1 prateleira. height/depth/thickness/assembly vêm do padrão. JSON schema-version não é validado.

`library_insert_model.execute` procura ID, cancela se ausente; passa tipo, linha válida ou COZ, swing e shelves ao cabinet_builder. Só passa width se width_mm !=0; zero usa fallback de largura do padrão. Não abre editor automaticamente. `library_create_cabinet.invoke` usa última state.line, montagem ativa e largura default, abre diálogo com tipo/largura/montagem/linha. Execute chama cabinet_builder; sucesso pode abrir cabinet_editor se open_editor=true e poll aceita. Builder cria no cursor 3D; WALL com cursor.z≈0 usa altura de instalação. O tipo alterado no diálogo muda dica de altura/profundidade, mas largura não tem callback para voltar ao default de outro tipo.

Criar categoria e trocar linha têm REGISTER sem UNDO (arquivo externo); criar armário e inserir modelo têm REGISTER/UNDO. SetLine protege fixas no invoke, mas execute chama set_line sem repetir a verificação. Operadores de clique/hover/fechar são INTERNAL. Register: props→popover→ops_categories→ops_cabinet→ops_click→draw; unregister inverso. Fontes: popover.py:20–94; ops_cabinet.py:26–70; ops_categories.py:12–83.

### Limitações e verificação

🟢 12 testes existentes passaram (categories 5, layout 5, models 2): PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest discover -s tests -p 'test_library*.py' -v. Cobrem ordem, validação de nomes, parse/migração de pastas, escalas, layout e catálogo. Smoke UI disponível tests/blender_012_library_ui.py não executado.

🟢 Validador de nome não rejeita '.'/'..' ou nomes reservados de SO; create usa nome como componente de caminho. Parse de categories não verifica que categories é lista e pode aceitar nomes com separadores que create recusaria. 🟡 Impacto no acesso a arquivos depende também dos validadores de customize.library_io; não afirmar contenção completa aqui.

🔴 **LACUNAS**: runtime GPU/clicks/popover em múltiplas janelas, UI scale real e cobertura do undo de operadores encadeados não verificados. Estado _open compartilhado significa categoria do último popup para todos os draws, sem isolamento por janela. Sem scroll, muitas categorias podem sair da região visível.

Fluxogramas library_panel.md, library_panel-categories.md, library_panel-layout.md, library_panel-insert.md.


## 18. Módulo `object_library`

🟢 **CONFIRMADO**, nove arquivos/907 linhas, 2026-10-10. Feature 009. Biblioteca de itens não paramétricos de ambiente, independente de library_panel. Cada item guarda hierarquia e marcas de grupo/esquadria/folha/agregado/peça nos próprios objetos. Não integra serviço de rede; origem/licença são metadados fornecidos pelo usuário.

### Catálogo, manifesto e disco

`catalog.Entry` representa manifesto caffmob_draw.object_item versão 1: ID slug, nome, categoria, nome da raiz, origem/autor/licença, tamanho em mm, features/materials, timestamp e addon_version. `slug` NFKD→ASCII→lower, separadores viram hífen; texto vazio vira item. ID novo = slug(nome)+token_hex(3) (6 hex). read_manifest exige formato/versão e strings não vazias item_id/name/root; ID regex impede separadores de caminho; categoria desconhecida vira OTHER; features desconhecidas filtradas. size_mm converte float e pega até três posições, sem exigir três valores/positividade/finitude; tipos aninhados não são integralmente verificados. Busca é substring do slug do nome, ignora acentos.

Sete categorias: DOORS,WINDOWS,COOKTOPS,TABLES,SEATING,DECOR,OTHER. `_scan` percorre subpastas e JSON ordenados, ignora manifesto inválido ou .blend ausente com aviso, miniatura opcional. Caminho do .blend/PNG usa pasta encontrada e entry.item_id, não necessariamente nome-base do JSON. list_items devolve embutidos antes dos do usuário; não deduplica IDs. Categoria da Entry pode diferir da pasta física; by_category usa a Entry. unique_name compara string exata, sufixos ' 2',' 3'. Embutidos em object_library/items; usuário via extension_path_user(path=object_library). Pacote contém seis manifestos e seus .blend/.png: porta, janela, cooktop, mesa, quadro, vaso. check_bundled apenas filtra origem começando por '3D Warehouse'; isto é regra do código, não auditoria de licença nem prova de proveniência. Fontes: catalog.py:17–92; store.py:17–91.

### Salvar e preparar raiz

`prepare_root(objs,name)` reaproveita uma única raiz já grupo/item; senão agrupa malhas de topo PLAIN, ignorando objetos não mesh soltos. tree inclui root+children_recursive. save marca raiz como item **antes** da escrita, usa id fornecido/replace_id/ID novo, computa world_box em mm arredondado a 0,1, lista materiais e features. TEXTURED é detectado por nome de material começando 'Textura: '; produção depende da flag de agregado.

Salva .blend com libraries.write, path_remap RELATIVE_ALL/fake_user; JSON UTF-8; ambos em temporários no destino, os.replace sequencial; miniatura comum é gerada depois (256 px pelo helper). Retorna (Item,[]) ou (None,mensagens) em OSError/RuntimeError. **Não é transação entre .blend, JSON e PNG**: falha no segundo replace pode deixar blend novo/manifesto antigo; alteração das props da raiz não é revertida. Temporário JSON só é adicionado à lista de limpeza depois de json.dump completar. Erros do thumbnail ocorrem fora do try. `folder/item_id` são parâmetros de ferramenta/script, não validados integralmente aqui. Fontes: item_io.py:57–121.

Operador Add REGISTER/UNDO usa seleção ou import_model (snapshot de novos objetos), diálogo com nome/categoria/origem/licença/autor. Nome repetido verifica apenas itens do usuário na categoria, comparação exata; RENAME usa unique_name, REPLACE reaproveita ID. Fallback de nome usa parte antes do primeiro ponto. Falha no save retorna CANCELLED sem desfazer agrupamento/marcação local explicitamente; arquivos externos não são revertidos por undo. Remove é REGISTER sem UNDO, confirmação; store.delete recusa embutidos e apaga .blend/.json/.png/.blend1 pelo prefixo blend, de forma sequencial. Fontes: ops.py:145–239; store.py:78–85.

### Inserção e modal

`item_io.insert(context,item,location=None)->(root,loaded)` append de todos objetos .blend, link=False. Busca raiz por nome exato ou primeiro segmento antes do ponto, depois raiz sem parent marcada is_item; se não encontrar remove objetos carregados e lança ValueError (outros data-blocks carregados não são explicitamente limpos). Liga todos à coleção ativa ou scene.collection, remove fake_user, move root se location e view_layer.update. Conversões gravadas nos próprios dados retornam com a cópia.

Chave UI U|B:categoria:item_id distingue usuário/embutido. `object_insert.execute` insere no cursor 3D e seleciona raiz. Invoke em VIEW_3D abre modal; outras áreas usam execute. Movimento projeta raio da vista sobre plano horizontal **no Z do cursor**, não superfície de objeto; sem snapping/colisão neste modal. Clique esquerdo PRESS confirma; Esc/right PRESS remove carregados em reverso; middle/wheel PASS_THROUGH permite navegar. Header limpo em _end. `cancel()` só limpa header, não remove carregados; remoção existe apenas no ramo explícito Esc/right. `_root` e `_loaded` mantêm referências RNA diretas durante modal, sem reobter por nome ao undo. Unregister remove classes, não percorre sessões ativas. 🔴 Comportamento de cancelamento externo/undo requer teste no Blender. Fonte: ops.py:48–131; item_io.py:124–148.

### Acabamento e textura

Scope PART usa seleção (ou ativo), ITEM usa tree(root_of(active) ou active); targets filtra MESH. Acabamentos unem nomes dos três .blend legados e materiais atuais não iniciados por ponto; nome já em bpy.data é preferido ao arquivo. library_materials cacheia nome→arquivo, primeiro catálogo prevalece; cache não é limpo no unregister deste módulo. apply_finish usa common.set_cutpart_material, compartilhado com personalização, e conta malhas aplicadas.

Imagem: path absoluto+size_mm identificam material existente (tolerância 1e-6 mm). Material 'Textura: basename tamanho mm'; guarda btm_texture_path e btm_texture_size_mm; Image Texture projection BOX/blend=0.2. Coordenadas Object→Mapping→Texture Color→Principled Base Color. Scale=1/max(size_mm/1000,1e-4) em cada eixo. Operador imagem faixa 1–100000 mm, default 600, filtro PNG/JPG/JPEG/TIF/TIFF/WEBP, verifica isfile e captura RuntimeError. Aplicação altera só cópia da cena, não regrava biblioteca. 🔴 Escala física com transformações de objeto não foi medida nesta sessão. Fonte: retexture.py:24–99.

### UI, registro e verificação

Inserir › Objetos: abas de categoria, busca, grid duas colunas com miniaturas e nome, botão remover só para usuário; avisos agregados em contagem. Previews sob demanda cacheiam path:int(mtime); atualização no mesmo segundo pode não trocar preview; versões antigas continuam na coleção até unregister. props registra Object.btm_object_item e WindowManager.btm_object_library; unregister remove ambos. Ordem props→previews→ops; panels são funções usadas pela UI externa. Retexturizar/acrescentar/inserir têm REGISTER/UNDO; remover REGISTER.

🟢 10 testes puros passaram: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_object_library -v. Cobrem contrato, slug/busca, duas raízes de armazenamento, conflitos, exclusão protegida e filtro de origem. tests/blender_009_library_smoke.py disponível, não executado. 🔴 Runtime de materiais, append, escala de textura e cancelamento modal não verificado.

Fluxogramas object_library.md, object_library-save.md, object_library-insert.md, object_library-retexture.md.


## 19. Módulo `inspection`

🟢 **CONFIRMADO**, inspection e seis adaptadores, 2026-10-10. Núcleo de inspeção de portas/basculantes/gavetas, independente do conflito de volumes sólidos em collision. Sem rede ou banco.

### Contrato Front e descoberta

Front(kind,module_root,obj,key) representa peça, vão ou módulo conforme biblioteca. Interface get() lê estado, apply(value) muda pose, commit(value) grava estado, hinge_frame() devolve ponto/eixo/referência mundo, objects() lista peças móveis, can_sweep/is_valid controlam detecção. HINGED={DOOR,FLIP_UP,FLIP_DOWN}; DRAWER/PULLOUT usam fração 0–1. Articuladas comuns até 90°, folhas convertidas podem ter máximo próprio. is_open limiar >0.5° ou >0.005 da fração. iter_fronts agrega na ordem frameless,face_frame,closets,btm,room_doors,aggregate_leaf; não deduplica entre adaptadores. front_for_object resolve na primeira família que reconhece objeto/ancestral. module_root_of reconhece tags cages, porta IS_ENTRY_DOOR_BP ou btm_plane.object_kind MODULE. Fonte: fronts.py:19–128.

| Adaptador | Unidade e persistência | Pose / cobertura |
|---|---|---|
| Frameless | btm_open graus ou fração, ausente=0, remove ao fechar | delta_rotation_euler/delta_location; GeoNodeCutpart e tags de frente, exclui False Front/oculta |
| Face frame | swing_percent 0–1, 90° comum equivale a 0.9 do teto 100° | apply proxy sem recálculo; commit pode reconstruir pivôs; uma Front por vão, exclui manual/sem pivôs |
| Closets | hb_door_open/hb_drawer_open fracionários; porta física até 110° | funções da biblioteca; gaveta inclui caixa irmã pelo índice |
| BTM | Controller.location.y 0–0.2 m → 0–90°, btm_open no commit | uma Front por módulo, todas folhas juntas |
| Ambiente | btm_open graus na raiz, pose lida do pivô | folhas cinzas criadas na primeira abertura; porta real da 010 exclui adaptador ambiente |
| Agregado LEAF | btm_aggregate.open_value fração, max_angle próprio | apply não testa contato; commit passa pela parada de aggregates.leaf |

Frameless deduz eixos pelos extremos com sinal da bound_box avaliada, escala e rotação fechada. Curso drawer: Dim Y da caixa filha, ou profundidade do pai menos 25.4 mm (mín 50 mm), fallback 0.4 m. Face frame apply refaz contexto até duas tentativas em ReferenceError; commit chama cutting.stale.skip_next_update antes de alterar swing_percent, limpa contexto. Closets usa suas marcas de dobradiça/lado/curso e transform do pai. Detecção de frentes não depende de legacy.gate: projetos antigos seguem inspecionáveis com UI antiga oculta.

### Matemática pura e folha de ambiente

pivot_math: clamp graus/fração; snap no mais próximo de 0/45/90 dentro de 5°; conversão graus↔fração legada; normalize recusa vetor <1e-12; Rodrigues gera rotação em eixo arbitrário. matrix_to_euler_xyz usa R=Rz·Ry·Rx, trata trava de cardã com rz=0. Sentido de abertura = sinal de dot(cross(axis,free),outward). edge_rotation retorna Euler e deslocamento h−R·h para manter pivô da aresta; slide = direção normalizada×curso×fração. side/top/bottom_hinge inferem offset e vetor livre pela direção Z do comprimento. Fonte: pivot_math.py:11–175.

room_door_math.leaves gera uma/duas Leaf: dupla metade da largura, hinges X=0/width; simples Is Left coloca hinge em width; Swing Inside coloca Y=wall_depth e abre em −Y, senão hinge Y=0 e abre +Y; rot_sign=sign×dx. Caixa da folha no pivô tem 8 cantos; open_tip é rotação 2D. room_door_leaf.ensure_leaves lê inputs por hb_types, recria pivôs se lados mudaram e reconstrói malha por convex_hull em cada chamada. Folha real já presente impede cinza. Porta sem pivô ainda tem Front, mas can_sweep=false: checagem não cria geometria apenas para verificar. Fonte: room_door_math.py:18–46; room_door_leaf.py:22–112.

### Escopos, animação e saída

scope_fronts ALL=frentes da cena atual (não todas cenas); ACTIVE_MODULE=raiz do ativo; SELECTED agrega todas frentes dos módulos que contêm selecionados e frentes reconhecidas individualmente, dedup por key. FrontsSetOpen REGISTER sem UNDO, mode CLOSE/OPEN_45/OPEN_90; gavetas recebem 0/0.5/1. Conta targets no relatório mesmo se ReferenceError foi ignorado.

InspectFronts é singleton global _active; segunda invocação pede saída e timer 0.001 s. Timer principal 60 Hz, duração 0.35 s e smoothstep t²(3−2t). Clique raycast sobre frente alterna fechada/aberta; durante tween inverte a partir da pose interpolada. apply em passos; commit no término. Default_angle 45/90 só altera graus articulados; open_value de gaveta é 1.0 no clique (diferente de OPEN_45 em massa). HUD/pílulas closets passam adiante. Timer/navegação/eventos sem frente PASS_THROUGH. _finish aplica alvos pendentes, remove dois timers, unregister modal HUD, limpa active/status; Esc/right CANCELLED **não restaura posição anterior**, conclui alvos. cancel externo chama _finish. Unregister do módulo apenas _active=None e classes: não chama _finish da sessão ativa nem remove seus timers explicitamente. Fonte: ops_inspect.py:17–269.

### Gizmo

GizmoGroup dial/arrow persistente na VIEW_3D; cache front por ponteiro ativo selecionado. Frame ortonormal pelo eixo/referência. Dial converte radians↔degrees e snap; arrow converte metros↔fração usando front.travel() e mínimo 1e-6. Setters só apply e guardam pending. Ao soltar, draw_prepare agenda commit em timer de intervalo zero; evita recálculo RNA dentro do desenho. Unregister remove timer, limpa _state e classe. 🟢 AggregateLeafFront deslizante não declara travel() e a classe base Front tampouco; gizmo arrow chama o método. 🔴 Reproduzir impacto na interface e definir adaptação necessária. Pending global pode atravessar mudança de ativo; não é isolado por janela. Fonte: gizmo.py:21–166; adapters/aggregate_leaf.py.

### Proteção ao salvar

save_guard.close_for_save varre todas cenas, ignora save_fronts_open=true, dedup por front.key, guarda valor e commit(0) apenas abertas; _reopen guarda scene_name,key,value. save_post e save_post_fail reconstroem Fronts por cena/key e commit valor original. Handlers persistent, registro sem duplicar, unregister remove todas ocorrências e limpa memória. Referências a Front não são guardadas entre save_pre/post. Erros ReferenceError são ignorados, outras exceções propagam. Estado local de opt-out não evita que objeto compartilhado com outra cena seja fechado ali. _reopen limpa antes de varrer; não há proteção específica para tween ativo/gizmo pending durante save. 🔴 Salvamento durante animação e cenas com objetos compartilhados exigem runtime. Fonte: save_guard.py:16–91.

### Interferência aproximada sob demanda

check_fronts produz (results,checked). Para Front válida/can_sweep, leva apply de 0 até max com passo 15° (ou gaveta 0/1), atualiza view layer, coleta bound_box mundo de objects visíveis; finally restaura pose. Nuvens de duas poses consecutivas viram cascos convexos. _shrink move pontos 1 mm **radialmente em direção ao centro**, no máximo metade da distância; não é offset uniforme de todas faces.

Targets MESH/CURVE visíveis, não WIRE/BOUNDS nem IS_2D_ANNOTATION; precomputa AABB/root, BVH e vértices sob demanda por ponteiro. Exclui próprio module_root e objetos próprios; portanto frentes/peças do mesmo módulo não são alvos. Broadphase AABB, narrowphase BVH.overlap; sem cruzamento de superfícies, amostra vértices do alvo contidos nos planos de casco. Step=max(1,nverts//2000) é aproximação, não limite estrito de 2000 pontos. Centro de choque usa até 32 centros de faces ou vértices contidos. to_mesh_clear após construção normal; BMesh dos cascos liberado em finally depois que _hull_bmesh retornou (falha dentro do construtor não tem esse finally). Fonte: interference.py:19–219.

checked incrementa só frentes com hulls, não todas descobertas. Resultados armazenados por nomes, localização mundo e kind em WindowManager; não têm invalidação automática por alteração de geometria. Check é REGISTER sem UNDO e roda só por comando; mensagem sem choque vale para checked. Goto seleciona frente/alvo que ainda existem e centraliza VIEW_3D. Overlay POST_VIEW cruz vermelha ±0.04 m e POST_PIXEL rótulo; handlers removidos no unregister. _draw_3d altera depth_test para NONE sem restaurar explicitamente. Fonte: ops_interference.py:14–81; overlay.py:17–80.

### Evidência

🟢 15 testes passaram: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_inspection_math test_room_door_math -v (10+5). Validam poses, limites, snap, conversões e folhas de ambiente; não validam BVH/save/handlers. Smoke tests/blender_inspection_smoke.py disponível, não executado. 🔴 Ausência de interferência não prova viabilidade mecânica de todo projeto: ignora próprio módulo, frentes sem folha e geometria não visível; varredura angular é discretizada.

Fluxogramas inspection.md, inspection-animation.md, inspection-interference.md, inspection-save.md, inspection-gizmo.md.


## 20. Módulo `molding`

🟢 **CONFIRMADO por leitura de código**, sem execução no Blender. Cinco arquivos; a implementação não é um gerador universal para todos os armários CAFFMob.

### Escopo e entradas

`adapters.collect_targets(scene, molding_type)` aceita somente cages face frame e frameless. CROWN e CAP: UPPER/TALL; BASE: BASE/TALL/LAP_DRAWER; LIGHT_RAIL: UPPER. Armários modernos BTM e closets não possuem adaptador neste módulo. Eletrodomésticos `IS_APPLIANCE` com origem mundial Z ≤ 0,02 m entram como pontes somente no rodapé.

`build_facts` cria um mapa por `id(obj)` com papel, canto, recuo, montantes, exposição das extremidades e montagem da coroa. Refrigerador face frame não recebe rodapé. NOTCH/LOOSE/FLOATING usam recuo; outros tipos ficam alinhados à frente. No frameless, uma ponta é considerada acabada se a sonda de 3 cm não estiver dentro do AABB XY de alguma parede, expandido em 5 cm. É uma aproximação por caixas, não teste da superfície real.

### Geometria e conectividade

`engine.cage_dims(obj)` tenta Dim X/Y/Z de Geometry Nodes; se algum valor for falso, usa `obj.dimensions`, sem avaliação explícita de depsgraph. `footprint` transforma quatro cantos locais (X positivo, profundidade em Y negativo) em XY mundial. Topo usa translação Z + altura: inclinação e escala vertical não são incorporadas nessa soma.

`members_touch` combina proximidade de AABBs XY e alinhamento de topo ou base com tolerância de 2 cm. `connected_components` percorre pares O(n²) e agrupa por BFS. `order_chain` prefere ponta de grau 1, segue vizinhos e anexa sobras de ramificações; uma componente ramificada não se transforma automaticamente em vários percursos independentes.

O campo corner é um dicionário opcional com profundidades ld/rd e flag diagonal; o motor gera contorno em L ou diagonal conforme esses valores. Dimensão auxiliar padrão de canto: 24 polegadas. `_assemble_front_raw` escolhe orientação pela ponta anterior ou centro do próximo membro e calcula extremos dianteiros/traseiros. `chain_sweep_points` garante orientação de modo que a normal direita aponte para fora, desloca a frente e retorna até a traseira somente nas pontas acabadas.

`offset_polyline_right` usa normal (dy, −dx), interseção entre segmentos para mitras, deduplicação 1e−6 e tratamento de paralelas com limiar 1e−6. `offset_polygon` faz o fechamento equivalente. Não há limite de comprimento de mitra em ângulos agudos.

### Rodapés e ilhas

`_kick_spans_local` separa FRONT, RECESS e SKIP; aplica montantes de piso e recuos, inclusive a cantos. Eletrodomésticos/refrigeradores dão continuidade à cadeia, mas seus vãos são SKIP. `_stretch_segments` mantém FRONT, inclui RECESS quando solicitado, une trechos contíguos e cria retornos nas interrupções.

A identificação de ilha exige todos os membros sem parent, ausência de cantos e no máximo duas fileiras. Ângulos são arredondados a duas casas; oposição aceita diferença de π em 0,05 rad. Uma fileira ou duas opostas produz perímetro com frente, traseira e lados. Uma ilha parentada não entra nessa heurística. Sem trechos descartados, o perímetro é cíclico; com descartes, a costura é reorganizada em trechos abertos.

### Pacotes, perfis e alturas

`packages` procura arquivos `.blend` em caminhos registrados, por categoria. O primeiro objeto com nome igual ao stem encontrado é usado; falhas de carregamento tentam a próxima biblioteca. Na ausência de ativo, seis contornos POLY simples são gerados como fallback (coroa, chapa plana, capa, rodapé, complemento e light rail). São substitutos geométricos, não catálogo comercial validado.

CROWN oferece SIMPLE, STACKED e SPACER; BASE e LIGHT_RAIL têm SIMPLE. Cada entrada é `(profile_ref, fallback_key, dx, dy)`. `_resolve_stack` aplica substituição por categoria, STACK_OFFSET e STACK_FRONT. A frente acumulada é `max(frente, dx + espessura_do_perfil)`. Métricas usam pontos de controle, não extremos exatos de Bézier, e cache por referência sem mtime ou fallback_key.

Datum da coroa face frame = altura − largura do TOP_RAIL + overlay positivo da porta + reveal. Frameless usa altura. Capa = max(topo do armário, topo da pilha de coroas) + cap_offset + dy. BASE/LIGHT_RAIL usam dy relativo à origem do primeiro armário. Padrões: reveal 0,625 polegada (0,015875 m); stack_offset 3,5 polegadas (0,0889 m); recessos, capa e base shoe desativados; cap_offset zero.

### Efeitos e falhas

`apply_scene_packages(scene)` ignora cenas de layout/detalhamento, apaga todas as curvas marcadas e reconstrói os pacotes escolhidos. Capa e base shoe são opções independentes; podem existir sem o pacote principal. Retorno contabiliza sweeps, não armários.

`_spawn_sweep` cria perfil oculto e curva 2D com bevel OBJECT e tampas; parent é o primeiro membro. Pontos mundiais são transformados para seu espaço local; Z dos pontos é descartado em favor do datum. Spline BEZIER usa handles VECTOR, deduplicação 0,1 mm e mínimo de 2 pontos abertos/3 fechados. O primeiro acabamento resolvido é aplicado. Tags armazenam tipo e nomes dos membros separados por vírgula, sem UID estável.

O callback de propriedades reconstrói sincronamente e captura exceções apenas imprimindo erro. Não há rollback entre remoção e reconstrução: uma falha pode deixar resultado parcial e perder sweeps anteriores. Registro/desregistro captura exceções genericamente. Remoção de perfil assume curve data; carregar um objeto de outro tipo não é validado antecipadamente.

🔴 **LACUNAS de validação em runtime:** ilhas parentadas, componentes ramificados, mitras agudas, transformações não unitárias, perfil externo de tipo inesperado e interrupção da reconstrução. Nenhum teste específico de `molding` foi localizado; esta extração valida AST e contratos estáticos, não o comportamento visual.


## 21. Módulo `geometry_free`

🟢 **CONFIRMADO por código** — cinco arquivos. Sete sondagens puras executadas por extração AST de `size`/`sheets`, sem importar ou simular `bpy`. O smoke Blender existente foi inspecionado, mas não executado.

### Modelo e cálculo

`Object.btm_geometry` guarda PLACA/CAIXA, plano XY/XZ/YZ, largura/profundidade/altura/espessura, opção de fabricação, componente, material e acabamento. Medidas padrão: 0,6/0,4/0,4/0,018 m; limites de cada medida: 0,001 a 10 m. Fabricação é false, componente ESP, material MDF e acabamento vazio. Kind/plane/medidas disparam reconstrução; campos produtivos não a disparam.

`mesh.size(kind, plane, width, depth, height, thickness)` retorna dimensões XYZ. PLACA: XY=(w,d,t), XZ=(w,t,h), YZ=(t,d,h). CAIXA=(w,d,h). `update` refaz um cubo com origem no canto mínimo, deslocando vértices em 0,5 e multiplicando por cada dimensão. Cresce em +X/+Y/+Z; alteração de espessura preserva face de apoio. Não existe cavidade visual ou montagem de seis malhas na caixa.

`sheets` retorna uma chapa para placa, com dimensões ordenadas descendentemente; a menor torna-se espessura produtiva. Portanto, se uma medida do plano for menor que `thickness`, essa medida vira a espessura exportada. Caixa gera seis chapas: Fundo/Tampo (w,d,t), laterais (max(0,001,h−2t),d,t), Frente/Trás (max(0,001,w−2t),max(0,001,h−2t),t). Espessura excessiva limita a dimensão interna a 1 mm; não rejeita geometria fisicamente impossível.

`create_object` cria malha, liga à coleção ativa, marca IS_BTM_GEOMETRY e object_kind GEOMETRY, define kind e reconstrói. `is_geometry` verifica MESH, grupos e object_kind; não depende da tag customizada. O callback `_update` aceita qualquer objeto MESH com o grupo, sem verificar sua classificação.

### Criação modal

`CAFFMOB_OT_geometry_create` exige VIEW_3D em OBJECT. `invoke` cria imediatamente um objeto provisório, marca HB_CURRENT_DRAW_OBJ, guarda referência RNA direta e inicia etapa 0. Passos: posicionar origem por `hb_snap` → desenhar largura/profundidade em plano horizontal → caixa desenhar altura em plano vertical → finalizar. Placa termina após largura/profundidade e nasce em XY; plano pode ser editado depois.

Mouse usa valores absolutos mínimos de 1 mm e desloca origem para o canto mínimo quando o movimento X/Y é negativo. Entrada aceita dígitos, ponto e vírgula; parser interpreta conforme unidades da cena. Enter confirma largura, depois profundidade, depois altura da caixa. Letras de unidade e sinal negativo não entram no buffer. Primeiro clique pode usar a localização atual mesmo sem hit de snap. Várias atribuições de medidas causam múltiplas reconstruções da malha.

Navegação passa por `hb_snap.event_is_pass_through`. Esc/cancelamento explícito remove objeto e malha sem usuários e limpa cabeçalho; finalizar remove flag provisória e seleciona o objeto. Não há método `cancel(context)` nem limpeza de sessão ativa no unregister; interrupção externa é uma lacuna. Acesso a context.area e referências RNA não têm proteção geral contra troca de contexto/remoção externa.

### Edição e fabricação

Operadores duplicar/espelhar/apagar possuem REGISTER/UNDO e poll de geometria ativa em modo OBJECT. Duplicar copia objeto e malha, liga a todas as coleções, remove btm_uid e desloca um comprimento X. Calcula posição mundial e a atribui a `location`; com parent, pode misturar coordenadas mundiais e locais. Espelhar alterna btm_mirrored e desloca uma largura: não aplica escala negativa nem espelha vértices. O deslocamento usa vetor mundial somado à location local; caso parentado também precisa validação. Apagar remove objeto e malha sem usuários, sem remoção recursiva dos filhos.

`cutting/part_sources.py:geometry_records` inclui somente geometria visível com fabricação ativa. Emite uma ou seis PartRecord; UID = uid/componente/índice, module_uid=None, module_name=nome do objeto, line vazio, source FREE_GEOMETRY, material/acabamento e medidas em mm. Dimensões vêm das propriedades; escala aplicada ao objeto não é incorporada. Linha vazia não aplica os mesmos limites/bordas de uma linha de armários.

### Verificação e limites

Sondagens confirmaram três orientações de placa, caixa XYZ, seis chapas, ordenação quando espessura supera dimensões do plano e clamp interno a 1 mm. `tests/blender_002_smoke.py` contém atualização de espessura, sete peças (placa+caixa), JSON produtivo e duplicação/espelhamento/remoção sem parent. Isso é cobertura existente, não evidência de execução nesta re-extração.

🔴 **LACUNAS:** cancelamento externo, dimensões incompatíveis com espessura, transformação/parent na edição e na fabricação e significado esperado do comando espelhar. Nenhuma dessas observações foi corrigida no legado.
