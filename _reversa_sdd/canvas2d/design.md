# Canvas 2D — Design Técnico

🟢 **CONFIRMADO** — desenho extraído de `caffmob_draw/canvas2d/` em 2026-10-10, incluindo a árvore de trabalho sem commit da feature 013 (`gestures.py`). Os IDs RN-xx, RF-xx e CA-xx são os de `requirements.md`. 🟡 marca inferência; 🔴 marca lacuna que exige validação no Blender.

## Visão de Camadas

| Camada | Arquivo | Importa `bpy`/`gpu`/`blf`? | Papel | Confiança |
|---|---|---|---|---|
| Núcleo puro | `view.py` | não (só `math`) | `View2D`, encaixes e distâncias | 🟢 |
| Núcleo puro | `gestures.py` | não (só `math`) | Fatores de zoom e bounds do zoom janela | 🟢 |
| Apresentação | `draw.py` | `gpu`, `blf`; `compat`, `hb_gpu_draw`, `data.units`, `data.i18n.tr` | Primitivas GPU em pixels e no mundo | 🟢 |
| Integração com o host | `window.py` | `bpy` | Área Image Editor própria, painel lateral, fechamento diferido | 🟢 |
| Pacote | `__init__.py` | não | Só docstring; não reexporta símbolos | 🟢 |

🟢 Os núcleos puros não dependem de `draw.py` nem de `window.py`; `gestures.zoom_window_bounds` só usa `view.to_world` por *duck typing* (não importa `View2D`). Fonte: `gestures.py`.

## Interface

### `view.py`

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `ORTHO_TOLERANCE_DEG` | constante | `2.5` | Tolerância padrão de `ortho_snap` | 🟢 |
| `View2D.__init__` | `(rect, scale=100.0, center=(0.0, 0.0))` | — | Converte tudo para `float`; `rect` vira tupla de 4; sem validação (RN-01, RN-04) | 🟢 |
| `View2D.to_screen` | `(point)` | `(px_x, px_y)` | `x + w/2 + (p.x − c.x)·scale`, idem Y (RN-02) | 🟢 |
| `View2D.to_world` | `(pixel)` | `(m_x, m_y)` | `c.x + (px − x − w/2)/scale`, idem Y; inversa exata de `to_screen` | 🟢 |
| `View2D.contains` | `(pixel)` | `bool` | `x ≤ px ≤ x+w and y ≤ py ≤ y+h` (bordas inclusivas) | 🟢 |
| `View2D.pan` | `(dx_px, dy_px)` | `None` | `center −= d/scale` (RN-03) | 🟢 |
| `View2D.zoom` | `(factor, anchor_px=None)` | `None` | `scale = max(1e-6, scale·factor)`; com âncora corrige `center += before − after` (RN-03, RN-04) | 🟢 |
| `View2D.fit` | `(bounds, margin=0.1)` | `None` | `bounds = ((x0,y0),(x1,y1))`; ver Fluxo F-03 (RN-05) | 🟢 |
| `View2D.grid_lines` | `(step)` | `(xs, ys)` listas de coordenadas do mundo | Ver Fluxo F-04 (RN-09) | 🟢 |
| `snap_to_grid` | `(point, step)` | `tuple` | `round(c/step)·step` por eixo; `step ≤ 0` → `tuple(point)` (RN-10) | 🟢 |
| `ortho_snap` | `(origin, point, tolerance_deg=2.5)` | `((x, y), locked: bool)` | Ver Fluxo F-05 (RN-11) | 🟢 |
| `distance_point_point` | `(a, b)` | `float` | `hypot` | 🟢 |
| `distance_point_segment` | `(point, a, b)` | `float` | Projeção com `t` limitado a `[0, 1]`; `|ab|² < 1e-18` → distância a `a` (RN-12) | 🟢 |

🟢 `round` é o embutido do Python 3 (arredondamento bancário em empates exatos, ex. `round(0.5) == 0`). Reimplementações em outra linguagem devem reproduzir isso se a paridade em empates importar. Fonte: `view.py:snap_to_grid`, `view.py:ortho_snap`.

### `gestures.py`

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `PINCH_SENSITIVITY` | constante | `1/150` | Comentário do código: "calibrado na prova D-02" | 🟢 |
| `WHEEL_STEP` | constante | `1.15` | Passo da roda anterior à 013 | 🟢 |
| `ZOOM_WINDOW_MIN_PX` | constante | `5` | Lado mínimo do retângulo da lupa | 🟢 |
| `pinch_factor` | `(delta, sensitivity=PINCH_SENSITIVITY)` | `float` | `math.exp(float(delta)·sensitivity)` (RN-06) | 🟢 |
| `wheel_factor` | `(up, inverted=False)` | `float` | `WHEEL_STEP` se `bool(up) != bool(inverted)`, senão `1/WHEEL_STEP` (RN-07) | 🟢 |
| `zoom_window_bounds` | `(view, p0_px, p1_px, min_px=ZOOM_WINDOW_MIN_PX)` | `((xmin,ymin),(xmax,ymax))` ou `None` | `None` se `|Δx| < min_px` ou `|Δy| < min_px` (lado exatamente 5 é aceito); não altera a vista (RN-08) | 🟢 |

### `draw.py`

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `FONT`, `FONT_SIZE` | constantes | `0`, `12` | Fonte padrão do `blf` | 🟢 |
| `COLORS` | `dict[str, RGBA]` | — | 13 entradas, valores na tabela abaixo | 🟢 |
| `shader` | `()` | shader ligado | `compat.get_builtin_shader('UNIFORM_COLOR')` + `bind()` | 🟢 |
| `begin` | `()` | shader | `gpu.state.blend_set('ALPHA')` e depois `shader()` | 🟢 |
| `end` | `()` | `None` | `gpu.state.blend_set('NONE')` (não restaura o estado anterior) | 🟢 |
| `rect` / `outline` | `(sh, r, color)` | `None` | `r = (x, y, w, h)` em px; delegam a `hb_gpu_draw.draw_rect` / `draw_rect_outline` | 🟢 |
| `lines` | `(sh, points, color)` | `None` | Lista plana de pontos consumidos em pares (`'LINES'`); lista vazia não desenha | 🟢 |
| `dashed` | `(p0, p1, dash=6.0, gap=4.0)` | lista de pontos (pares) | Só gera pontos, não desenha; ver Fluxo F-06 | 🟢 |
| `text` | `(x, y, value, color=None, size=FONT_SIZE)` | `None` | `hb_gpu_draw.draw_text(FONT, x, y, size, color or COLORS['text'], tr(value))`; `(x, y)` é a linha de base | 🟢 |
| `text_width` | `(value, size=FONT_SIZE)` | `float` | `blf.size` + `blf.dimensions(FONT, tr(value))[0]` (mede o texto **traduzido**) | 🟢 |
| `button` | `(sh, r, label, hot=False, primary=False)` | `None` | Fundo `button_primary` > `button_hot` > `button`; contorno `border`; rótulo centrado na horizontal e com `vcenter_baseline` | 🟢 |
| `length_label` | `(meters)` | `str` | `units.format_value(meters)` | 🟢 |
| `box` | `(sh, view, lo, hi, color, fill=None)` | `r` em px | Converte `lo`/`hi`, normaliza com `min`/`abs`, preenche se `fill` e contorna | 🟢 |
| `segment` | `(sh, view, p0, p1, color, dashed_line=False)` | `None` | Converte e desenha linha cheia ou `dashed` com padrão 6/4 | 🟢 |

Paleta `COLORS` (RGBA) 🟢 `draw.py:COLORS`:

| Chave | Valor | Uso documentado |
|---|---|---|
| `panel` | (0.11, 0.11, 0.12, 0.94) | fundo de painel |
| `pane` | (0.17, 0.17, 0.18, 1.0) | fundo de quadro |
| `border` | (1.0, 1.0, 1.0, 0.18) | contornos |
| `text` | (0.92, 0.92, 0.92, 1.0) | texto padrão |
| `muted` | (0.65, 0.65, 0.68, 1.0) | texto secundário |
| `reference` | (0.25, 0.65, 1.0, 1.0) | objeto "B" (comentário) |
| `moving` | (1.0, 0.62, 0.15, 1.0) | objeto "A" (comentário) |
| `target` | (0.55, 0.55, 0.6, 0.55) | alvo inativo |
| `target_hot` | (0.35, 1.0, 0.45, 1.0) | alvo sob o cursor |
| `warning` | (1.0, 0.35, 0.3, 1.0) | aviso |
| `button` / `button_hot` / `button_primary` | (0.26, 0.26, 0.28, 1) / (0.36, 0.36, 0.40, 1) / (0.2, 0.45, 0.8, 1) | estados do botão |

🟢 Os usos "fundo de painel/quadro/alvo" são inferidos dos nomes e dos consumidores (`move_over/ops_dialog.py`); só "A"/"B" estão escritos no código. _(Revisão 2026-10-10: confirmado nos consumidores: `pane` em move_over/ops_dialog.py:179, `target`/`target_hot` em :186, `panel` em :197 e walls2d/ops_editor.py:232, `muted` em walls2d/ops_editor.py:187, `warning` em :189)_

### `window.py`

| Símbolo | Assinatura | Retorno | Observação | Confiança |
|---|---|---|---|---|
| `editor_area` | `(context, s)` | `(window, area, region)` ou `(None, None, None)` | Varre `context.window_manager.windows` → `screen.areas` comparando `area.as_pointer() == s.area_ptr`; `region` = primeira `type == 'WINDOW'` (pode ser `None`); `s is None` → triplo `None` | 🟢 |
| `side_panel` | `(area)` | região `UI` ou `None` | `None` se `area is None`, sem região UI, ou `width ≤ 1` ou `height ≤ 1` (RN-16) | 🟢 |
| `over_side_panel` | `(area, mouse_x, mouse_y)` | `bool` | Coordenadas da janela; `ui.x ≤ mx < ui.x+w` e `ui.y ≤ my < ui.y+h` (limite superior exclusivo) | 🟢 |
| `visible_width` | `(area, region)` | `float` | `region.width` se sem painel ou `ui.x ≤ region.x` ou `ui.x ≥ region.x + region.width`; senão `ui.x − region.x` | 🟢 |
| `is_editor_area` | `(context, s)` | `bool` | `context.area.as_pointer() == s.area_ptr` | 🟢 |
| `prepare` | `(area)` | região `WINDOW` ou `None` | Ver Fluxo F-07 (RN-15) | 🟢 |
| `focus_tab` | `(area, category)` | `bool` | Ver Fluxo F-08 | 🟢 |
| `open_window` | `(context, s, missing_window_message)` | `(window, area, region)` | Ver Fluxo F-09; pode levantar `RuntimeError(missing_window_message)` (RN-14) | 🟢 |
| `_close` | `(window_ptr, area_ptr, restore_area_type)` | `None` (desregistra o timer) | Ver Fluxo F-10 (RN-17) | 🟢 |
| `close_later` | `(window_ptr, area_ptr, restore_area_type)` | `None` | `bpy.app.timers.register(lambda: _close(...), first_interval=0.05)` | 🟢 |
| `window_alive` | `(context, s)` | `bool` | `editor_area(context, s)[1] is not None` | 🟢 |

🟢 Contrato da sessão `s` (duck typing): atributos `window_ptr: int`, `area_ptr: int`, `restore_area_type: str | None` (inicializado `None` em `walls2d/props.py` e `cabinet_editor/props.py`). `open_window` escreve os três; os demais só leem `area_ptr`.

## Fluxo Principal

Uso típico por um editor (Editor de Paredes, Editor de Armário):

1. 🟢 O operador chama `open_window(context, s, msg)`; recebe `(window, area, region)` com a área já preparada como IMAGE_EDITOR. Fonte: `walls2d/window.py`, `cabinet_editor/window.py:open_window`.
2. 🟢 O consumidor cria `View2D(rect)` com `rect = (0, 0, visible_width(area, region), altura útil)` (coordenadas **locais da região**, não da janela) e chama `fit(bounds, margin)` (paredes 0,15; armário 0,18; Mover Sobre 0,15). Fonte: `walls2d/ops_editor.py:_region_rect/ensure_view`, `cabinet_editor/window.py:ensure_view`, `move_over/ops_dialog.py`.
3. 🟢 No modal, cada evento: se `over_side_panel(area, event.mouse_x, event.mouse_y)` e não há arraste/pan em curso, o evento passa ao Blender; senão `pixel = (mouse_x − region.x, mouse_y − region.y)` e `view.to_world(pixel)` dá o cursor no mundo. Fonte: `walls2d/ops_editor.py:_local`.
4. 🟢 Navegação: botão do meio arrasta (`pan` com delta entre pixels), roda → `zoom(wheel_factor(up, prefs.inputs.invert_zoom_wheel), pixel)`, `TRACKPADZOOM` → `zoom(pinch_factor(compat.pinch_delta(event)), pixel)`, `TRACKPADPAN` → `pan(*compat.trackpad_delta(event))`, `HOME` → `fit(bounds, 0.15)`, lupa → `zoom_window_bounds` + `fit(bounds, margin=0)`. Fonte: `walls2d/ops_editor.py` (linhas 640-656, 268-282). _(Revisão 2026-10-10: no disco atual, `_handle` 642-657 e `handle_zoom_window` 265-281)_
5. 🟢 No handler `POST_PIXEL`: `sh = draw.begin()` → fundo → `grid_lines(step)` convertidas por `to_screen` → entidades com `box`/`segment`/`lines`/`dashed` → `text`/`length_label` → `button` → `draw.end()`. Fonte: `_reversa_sdd/flowcharts/canvas2d.md` §3; `walls2d/ops_editor.py:113`.
6. 🟢 Enquanto a aba não estiver ativa, o editor chama `focus_tab(area, category)` em eventos `TIMER` até receber `True`. Fonte: `cabinet_editor/ops_editor.py:402`.
7. 🟢 Ao concluir/cancelar, o editor chama `close_later(s.window_ptr, s.area_ptr, s.restore_area_type)`; o fechamento real acontece 0,05 s depois, fora do modal. Fonte: `walls2d/ops_editor.py:545`, `cabinet_editor/window.py:close_later`.

### F-03 `View2D.fit` 🟢 `view.py:fit`
1. `w_world = max(x1 − x0, 1e-6)·(1 + 2·margin)`; `h_world` idem com Y.
2. `scale = min(rect.w / w_world, rect.h / h_world)` (sem piso 1e-6, sem teto).
3. `center = ((x0+x1)/2, (y0+y1)/2)`.
- Não reordena os bounds: `x1 < x0` vira extensão `1e-6` (ver `edge-cases.md` EC-04).

### F-04 `View2D.grid_lines` 🟢 `view.py:grid_lines`
1. `step ≤ 0` → `([], [])`.
2. `(x0, y0) = to_world((rect.x, rect.y))`, `(x1, y1) = to_world((rect.x+w, rect.y+h))`.
3. Se `(x1−x0)/step > 400` ou `(y1−y0)/step > 400` → `([], [])`.
4. `xs = [i·step for i in range(floor(x0/step), ceil(x1/step)+1)]`, idem `ys`. A contagem pode chegar a ~402 por eixo, e as linhas extremas podem estar fora do retângulo; o recorte é do consumidor.

### F-05 `ortho_snap` 🟢 `view.py:ortho_snap`
1. `dx, dy = point − origin`; `length = hypot(dx, dy)`; `length < 1e-12` → `(tuple(point), False)`.
2. `angle = degrees(atan2(dy, dx)) % 360` (faixa `[0, 360)`).
3. `nearest = round(angle/90)·90` (pode ser 360).
4. `|angle − nearest| ≤ tolerance_deg` → `(origin + length·(cos, sin)(nearest), True)`; senão `(tuple(point), False)`.
- 🟢 Conserva o comprimento radial, não a projeção sobre o eixo. `walls2d/direction.py` replica a mesma tolerância 2,5° numa constante própria.

### F-06 `dashed` 🟢 `draw.py:dashed`
1. `length = hypot(p1 − p0)`; `< 1e-6` → `[]`.
2. Vetor unitário `u`; `t = 0`; enquanto `t < length`: `e = min(t + dash, length)`, acrescenta os pontos `p0 + u·t` e `p0 + u·e`, `t = e + gap`.
3. O último traço é cortado no fim; a lista sempre tem número par de pontos.

### F-07 `prepare` 🟢 `window.py:prepare`
Ordem: `area.type = 'IMAGE_EDITOR'` → `space = area.spaces.active` → `space.image = None` → `space.show_region_ui = True` → `show_region_toolbar = False` → `show_region_tool_header = False` → `area.show_menus = False` → `space.show_region_header = False` → devolve a região `WINDOW`.

### F-08 `focus_tab` 🟢 `window.py:focus_tab`
1. Sem área ou sem região `UI` → `False`.
2. Se `ui.active_panel_category != category`: tenta atribuir; `TypeError`/`AttributeError`/`ValueError` → `False`; se atribuiu, `area.tag_redraw()`.
3. Devolve `ui.active_panel_category == category`.
- 🟢 Docstring: a aba só existe depois do primeiro desenho da região, por isso o chamador repete.

### F-09 `open_window` 🟢 `window.py:open_window`
1. `source = context.area` só se `context.area.type == 'VIEW_3D'`.
2. Se há `source` e `context.window`: guarda os ponteiros das janelas existentes; executa `bpy.ops.screen.area_dupli('INVOKE_DEFAULT')` dentro de `context.temp_override(window=context.window, area=source)`, engolindo `RuntimeError`; janelas novas = as que não estavam no conjunto; se houver, `window = new[0]` e `area` = a de maior `width·height` nessa janela.
3. Se `area is None` (fallback): sem `context.area` ou `context.window` → `RuntimeError(missing_window_message)` (antes de escrever ponteiros); senão `window, area = context.window, context.area` e `s.restore_area_type = area.type` (tipo original).
4. `region = prepare(area)`; `s.window_ptr`, `s.area_ptr` = `as_pointer()`; devolve `(window, area, region)`.
- 🟢 No caminho de sucesso da duplicação, `s.restore_area_type` não é tocado (fica o valor anterior da sessão, normalmente `None`).

### F-10 `_close` 🟢 `window.py:_close`
1. Usa `bpy.context.window_manager` (não o contexto do modal). Procura a área com `as_pointer() == area_ptr` em todas as janelas.
2. Primeira área encontrada: se `restore_area_type` → `area.show_menus = True`, `area.spaces.active.show_region_header = True` (no espaço ainda IMAGE_EDITOR), `area.type = restore_area_type`.
3. Senão, se `win.as_pointer() == window_ptr` e há mais de uma janela → `wm.window_close()` em `temp_override(window=win)`; `RuntimeError` → `area.type = 'VIEW_3D'`.
4. Senão nada é feito. Devolve sempre `None` (o timer não se repete). Área não encontrada → `None` silencioso.

## Fluxos Alternativos

- **Duplicação indisponível** (contexto fora de VIEW_3D, `area_dupli` falhou ou não criou janela): o editor ocupa a própria área e a devolve ao fechar (RN-14, CA-11). 🟢 `window.py:open_window`
- **Sem área/janela no contexto**: `RuntimeError` com a mensagem do consumidor; o Editor de Armário passa `tr("O Editor de Armário precisa de uma janela do Blender aberta.")` (CA-12). 🟢 `cabinet_editor/window.py:open_window`
- **Usuário fechou a janela do sistema**: `window_alive` devolve `False` e o consumidor encerra a sessão. 🟢 `window.py:window_alive`; `cabinet_editor/ops_editor.py:383`
- **Única janela e sem `restore_area_type`** no fechamento: nenhuma ação (ver EC-07). 🟢 `window.py:_close`
- **Grade inválida ou densa**: listas vazias, nada a desenhar (RN-09, CA-08). 🟢
- **Zoom janela de clique sem arraste**: `None`, vista intacta (RN-08, CA-06). 🟢

## Dependências

| Dependência | Uso | Confiança |
|---|---|---|
| `caffmob_draw/hb_gpu_draw.py` | `draw_rect` (2 triângulos), `draw_rect_outline` (4 segmentos `LINES`), `draw_lines` (`LINES`), `draw_text` (`blf.size/color/position/draw`), `vcenter_baseline` (altura de `"Aj"`) | 🟢 |
| `caffmob_draw/compat.py:get_builtin_shader` | Tenta `UNIFORM_COLOR`, depois `2D_UNIFORM_COLOR`, depois `UNIFORM_COLOR` | 🟢 |
| `caffmob_draw/compat.py:trackpad_delta`, `pinch_delta` | Leitura do evento fora da unit: `(mouse_x − mouse_prev_x, mouse_y − mouse_prev_y)` e `−(dx + dy)` | 🟢 |
| `caffmob_draw/data/units.py:format_value` | Rótulos de cota na unidade do usuário | 🟢 |
| `caffmob_draw/data/i18n.py:tr` | Tradução no momento do desenho (texto do código é a chave) | 🟢 |
| `bpy.ops.screen.area_dupli`, `bpy.ops.wm.window_close`, `bpy.app.timers`, `Context.temp_override` | Janela própria e fechamento | 🟢 |

Consumidores 🟢 (grep): `walls2d/ops_editor.py` (draw, gestures, View2D, distâncias, snaps), `walls2d/window.py` (reexporta `side_panel`, `over_side_panel`, `visible_width`, `close_later` e embrulha os demais), `cabinet_editor/window.py` (draw, window, View2D), `move_over/ops_dialog.py` (draw, View2D), `move_over/ops_drag.py` (draw), `move_over/align.py` (`distance_point_segment`), `overlays/element_toast.py` (draw, import tardio), `walls2d/direction.py` (cópia da constante 2,5°), `data/i18n.py` (citação em docstring).

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---|---|---|
| Separar cálculo puro (sem `bpy`) de desenho/janela, para testar fora do Blender | Docstrings "Python puro, sem `bpy`" em `view.py`, `gestures.py`; `tests/test_canvas2d_*.py` | 🟢 |
| Escala sem teto, só piso técnico 1e-6 px/m | `view.py:zoom`; `code-analysis.md` §4.1 (013, Q1) | 🟢 |
| Pinça exponencial, simétrica e independente da escala | `gestures.py` docstring e `pinch_factor` | 🟢 |
| Leitura do evento isolada em `compat.py` | `gestures.py` docstring (D-03); `compat.trackpad_delta` | 🟢 |
| Tela 2D = Image Editor sem imagem, sem cabeçalho; barra superior desenhada em GPU pelo consumidor | `window.py:prepare`; `walls2d/ops_editor.py` docstring | 🟢 |
| Janela extraída de `walls2d/window.py` para servir também ao Editor de Armário (004, D-20) | Docstring de `window.py` | 🟢 |
| Fechamento num timer, fora do modal que roda na janela | `window.py:close_later` | 🟢 |
| Tradução no desenho (`tr` dentro de `text`/`text_width`) em vez de no chamador | `draw.py:text`; `data/i18n.py:16` | 🟢 |
| Coordenadas de `rect` locais da região (origem 0,0), não da janela | Editores de paredes e de armário passam `(0.0, 0.0, w, h)`; o Mover Sobre passa retângulos de quadro deslocados (`inner(self.pane_top)`), também em pixels locais da região _(Revisão 2026-10-10: texto dizia "Consumidores passam (0.0, 0.0, w, h)"; move_over/ops_dialog.py:146-151 usa `(rect[0]+inset, rect[1]+inset, ...)`; walls2d/ops_editor.py:_region_rect e cabinet_editor/window.py:_rect usam origem 0)_ | 🟢 |

## Estado Interno

- 🟢 `View2D` tem três campos mutáveis: `rect` (o consumidor reatribui a cada desenho: `walls2d/ops_editor.py:ensure_view`), `scale` e `center`. Nenhuma persistência; vive na sessão em memória do editor.
- 🟢 `draw.py` não guarda estado próprio; altera o estado global do GPU (`blend` e shader ligado) e do `blf` (tamanho e cor da fonte 0).
- 🟢 `window.py` não guarda estado; lê e escreve `s.window_ptr`, `s.area_ptr`, `s.restore_area_type` e registra um timer anônimo por fechamento.

## Observabilidade

- 🟢 Nenhum log, métrica ou relatório. Falhas de `area_dupli` e de `window_close` (`RuntimeError`) e de troca de aba (`TypeError`/`AttributeError`/`ValueError`) são engolidas com caminho alternativo. Fonte: `window.py`.

## Riscos e Lacunas

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-71):** guardar snapshot mínimo (`show_menus`, `show_region_header`, `show_region_ui`) em `open_window` e restaurá-lo. 🟢 (código) hoje a restauração liga sempre menus e cabeçalho, sem lembrar os valores originais (EC-08). Pendência de implementação: DT-02.
- 🟡 Sinal real de `compat.pinch_delta` em cada plataforma e comportamento multi-janela precisam de teste no Blender; os testes puros cobrem só as contas — decisão: medir/testar (DT-03; questions.md#pergunta-7).
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-6):** restaurar `VIEW_3D` com `show_menus`/`show_region_header` ligados nesse ramo. 🟢 (código) hoje, com uma única janela e sem `restore_area_type`, `_close` não faz nada: a área fica como IMAGE_EDITOR sem cabeçalho (EC-07). Pendência de implementação: DT-01.
- 🟡 `_close` usa `bpy.context` global no timer; supõe-se que `bpy.context.window_manager` esteja disponível nesse momento.
- 🟢 Escala zero (construtor ou `fit` com `rect` de largura/altura 0) gera `ZeroDivisionError` em `to_world`/`pan`; não há guarda (EC-01).

## Divergências entre artefatos e código

- 🟢 `code-analysis.md` §4.1 e `domain.md` RN-CANVAS2D-04 dizem "400 linhas por eixo"; o código testa `extensão/step > 400`, o que permite até ~402 linhas. Vale o código (já registrado em `requirements.md`). _(Revisão cruzada 2026-10-10: domain.md e code-analysis.md corrigidos)_
- 🟢 `_reversa_sdd/flowcharts/canvas2d.md` §1 mostra "não há mais de uma janela → `area.type = VIEW_3D`"; no código, `VIEW_3D` só acontece se `window_close` levantar `RuntimeError`; com uma janela nada é feito.
- 🟢 `code-analysis.md` §4.5 marca `PINCH_SENSITIVITY` como "🟡 a calibrar"; o comentário atual em `gestures.py` diz "calibrado na prova D-02".
- 🟢 Contagens de linhas em `code-analysis.md`/`legacy-mapping.md` (view 106, gestures 41, draw 117, window 128) diferem de `wc -l` atual (105, 38, 116, 132); as linhas citadas em `legacy-mapping.md` estão deslocadas em ±1 (ex. `editor_area` está na linha 14, `pinch_factor` na 22). _(Revisão 2026-10-10: em `window.py` o deslocamento chega a 6 linhas: `open_window` 79, `_close` 105, `close_later` 125, `window_alive` 130; `legacy-mapping.md` corrigido)_
