# Canvas 2D — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/canvas2d/` a partir do código de 2026-10-10 (inclui `gestures.py` da feature 013, sem commit). IDs RN/RF/CA de `requirements.md`; fluxos F-xx e casos EC-xx de `design.md` e `edge-cases.md`.

## Pré-requisitos

- [ ] 🟢 `caffmob_draw/hb_gpu_draw.py` com `draw_rect`, `draw_rect_outline`, `draw_lines`, `draw_text`, `vcenter_baseline` (assinaturas em `design.md` › Dependências).
- [ ] 🟢 `caffmob_draw/compat.py` com `get_builtin_shader(name_3d, name_2d)`, `trackpad_delta(event)` e `pinch_delta(event)`.
- [ ] 🟢 `caffmob_draw/data/units.py:format_value` e `caffmob_draw/data/i18n.py:tr` disponíveis.
- [ ] 🟢 Sessões dos editores expõem `window_ptr`, `area_ptr` e `restore_area_type = None` (`walls2d/props.py`, `cabinet_editor/props.py`).
- [ ] 🟢 Sem banco de dados, variáveis de ambiente ou configuração própria.

## Tarefas

- [ ] T-01, Criar o pacote `canvas2d` com `__init__.py` só com docstring (sem reexportar símbolos)
  - Origem no legado: `caffmob_draw/canvas2d/__init__.py:1`
  - Critério de pronto: `from caffmob_draw.canvas2d import view, gestures` funciona fora do Blender sem importar `bpy`
  - Confiança: 🟢

- [ ] T-02, Implementar `View2D` (`__init__`, `to_screen`, `to_world`, `contains`) com conversão a partir do centro do `rect` e bordas inclusivas (RN-01, RN-02, RF-01)
  - Origem no legado: `caffmob_draw/canvas2d/view.py:View2D.__init__/to_screen/to_world/contains`
  - Critério de pronto: CA-01 e CA-02 passam; construtor converte `rect`, `scale`, `center` para `float`, sem validação
  - Confiança: 🟢

- [ ] T-03, Implementar `pan` e `zoom(factor, anchor_px=None)` com piso 1e-6 e correção `center += before − after` (RN-03, RN-04, RF-02)
  - Origem no legado: `caffmob_draw/canvas2d/view.py:View2D.pan/zoom`
  - Critério de pronto: CA-03 e CA-04; ponto sob a âncora não se move (erro ≤ 1 px, como em `test_ancora_parada`); fator 0 ou negativo resulta em escala 1e-6 (EC-02)
  - Confiança: 🟢

- [ ] T-04, Implementar `fit(bounds, margin=0.1)` conforme F-03, sem reordenar bounds e sem piso de escala (RN-05, RF-02)
  - Origem no legado: `caffmob_draw/canvas2d/view.py:View2D.fit`
  - Critério de pronto: centro = centro dos bounds; o eixo limitante cabe inteiro com a margem; bounds degenerados usam extensão 1e-6 m (EC-04)
  - Confiança: 🟢

- [ ] T-05, Implementar `grid_lines(step)` conforme F-04 (guarda `step ≤ 0`, densidade `> 400`, índices `floor..ceil` inclusivos) (RN-09, RF-04)
  - Origem no legado: `caffmob_draw/canvas2d/view.py:View2D.grid_lines`
  - Critério de pronto: CA-08; para densidade exatamente 400 a lista não é vazia e pode ter até 402 itens
  - Confiança: 🟢

- [ ] T-06, Implementar `snap_to_grid`, `ortho_snap` (F-05, `ORTHO_TOLERANCE_DEG = 2.5`, tolerância inclusiva, preserva comprimento), `distance_point_point`, `distance_point_segment` (RN-10, RN-11, RN-12, RF-04)
  - Origem no legado: `caffmob_draw/canvas2d/view.py:snap_to_grid/ortho_snap/distance_point_point/distance_point_segment`
  - Critério de pronto: CA-07; vetor nulo (<1e-12) devolve `(point, False)`; ângulo 358° trava em 0° (EC-05); `round` com empate bancário igual ao Python
  - Confiança: 🟢

- [ ] T-07, Implementar `gestures.py`: constantes `PINCH_SENSITIVITY = 1/150`, `WHEEL_STEP = 1.15`, `ZOOM_WINDOW_MIN_PX = 5`; `pinch_factor`, `wheel_factor`, `zoom_window_bounds` (RN-06, RN-07, RN-08, RF-03)
  - Origem no legado: `caffmob_draw/canvas2d/gestures.py`
  - Critério de pronto: CA-05 e CA-06; `pinch_factor(d)·pinch_factor(−d) == 1`; `wheel_factor(True, True) == 1/1.15`; lado de exatamente 5 px é aceito; o módulo não importa `bpy` nem `view`
  - Confiança: 🟢

- [ ] T-08, Implementar `draw.py` base: `FONT = 0`, `FONT_SIZE = 12`, `COLORS` (13 entradas, valores em `design.md`), `shader`, `begin` (blend ALPHA), `end` (blend NONE) (RN-13, RF-05)
  - Origem no legado: `caffmob_draw/canvas2d/draw.py:COLORS/shader/begin/end`
  - Critério de pronto: `begin()` devolve shader `UNIFORM_COLOR` já ligado via `compat.get_builtin_shader`; `end()` deixa blend `NONE`
  - Confiança: 🟢

- [ ] T-09, Implementar primitivas em pixels `rect`, `outline`, `lines` (ignora lista vazia), `dashed` (F-06, padrão 6/4), `text`/`text_width` (traduzem com `tr`), `button` (precedência primary > hot > normal), `length_label` (RF-05)
  - Origem no legado: `caffmob_draw/canvas2d/draw.py:rect/outline/lines/dashed/text/text_width/button/length_label`
  - Critério de pronto: CA-10; `dashed` devolve número par de pontos e o último traço termina exatamente em `p1`; `text` com `color=None` usa `COLORS['text']`
  - Confiança: 🟢

- [ ] T-10, Implementar primitivas no mundo `box` (normaliza retângulo, `fill` opcional, devolve `r` em px) e `segment` (cheio ou tracejado) (RF-05)
  - Origem no legado: `caffmob_draw/canvas2d/draw.py:box/segment`
  - Critério de pronto: CA-09; `box` com `lo > hi` desenha o mesmo retângulo que com `lo < hi`
  - Confiança: 🟢

- [ ] T-11, Implementar localização da área e painel lateral: `editor_area`, `is_editor_area`, `window_alive`, `side_panel` (>1 px), `over_side_panel` (superior exclusivo), `visible_width` (RN-16, RF-06)
  - Origem no legado: `caffmob_draw/canvas2d/window.py:editor_area/is_editor_area/window_alive/side_panel/over_side_panel/visible_width`
  - Critério de pronto: com a sobreposição de regiões ligada, cliques sobre o painel N chegam aos botões e a largura útil desconta o painel; sessão `None` → `(None, None, None)`
  - Confiança: 🟢

- [ ] T-12, Implementar `prepare(area)` na ordem de F-07 e `focus_tab(area, category)` conforme F-08 (RN-15, RF-06)
  - Origem no legado: `caffmob_draw/canvas2d/window.py:prepare/focus_tab`
  - Critério de pronto: área vira IMAGE_EDITOR sem imagem, com N visível e sem cabeçalho/menus/barras; `focus_tab` devolve `False` até a aba existir e `True` depois
  - Confiança: 🟢

- [ ] T-13, Implementar `open_window(context, s, missing_window_message)` conforme F-09 (duplicação preferida, maior área da janela nova, fallback na área atual com `restore_area_type`, `RuntimeError` sem área/janela) (RN-14, RF-06)
  - Origem no legado: `caffmob_draw/canvas2d/window.py:open_window`
  - Critério de pronto: CA-11 e CA-12; ponteiros só são gravados após `prepare`
  - Confiança: 🟢

- [ ] T-14, Implementar `_close` (F-10) e `close_later` com `bpy.app.timers.register(..., first_interval=0.05)` (RN-17, RF-06)
  - Origem no legado: `caffmob_draw/canvas2d/window.py:_close/close_later`
  - Critério de pronto: fechar pelo OK/Cancelar do editor não fecha a janela dentro do modal; no fallback a área volta ao tipo original com menus e cabeçalho; o callback devolve `None` (não repete)
  - Confiança: 🟢

- [ ] T-15, Integrar os consumidores: `walls2d/window.py` reexporta `side_panel`, `over_side_panel`, `visible_width`, `close_later` e embrulha os demais com a sessão e `EDITOR_CATEGORY`; `cabinet_editor/window.py` idem com sua mensagem traduzida; `walls2d/ops_editor.py` liga roda/pinça/pan de touchpad/Home/lupa conforme `design.md` › Fluxo Principal passo 4
  - Origem no legado: `caffmob_draw/walls2d/window.py`, `caffmob_draw/cabinet_editor/window.py`, `caffmob_draw/walls2d/ops_editor.py:_handle/handle_zoom_window/_region_rect`
  - Critério de pronto: os dois editores abrem, navegam e fecham; a lupa usa `fit(bounds, margin=0)`; `Home` usa margem 0,15
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Conversão ida e volta e `contains` (CA-01, CA-02) — já coberto em `tests/test_canvas2d_view.py:test_ida_e_volta` 🟢 (`contains` com borda exata: 🟢 não identificado nos testes atuais _(Revisão 2026-10-10: grep `contains` em tests/test_canvas2d_*.py sem ocorrência)_)
- [ ] TT-02, Pan e zoom ancorado (CA-03) — `test_canvas2d_view.py:test_pan_e_zoom_ancorado`, `test_canvas2d_gestures.py:test_ancora_parada` 🟢
- [ ] TT-03, Piso do zoom com fator 0 e negativo (CA-04, EC-02) — 🟢 sem teste atual identificado _(Revisão 2026-10-10: tests só chamam `zoom` com 2.0 e `pinch_factor(...)`, nunca fator ≤ 0)_
- [ ] TT-04, `fit` e zoom janela (CA-05, CA-06) — `test_enquadrar`, `test_enquadra_centrado`, `test_retangulo_pequeno_nao_muda_a_vista` 🟢
- [ ] TT-05, Pinça: sentido, proporcionalidade, ida e volta, delta zero, mesma pinça em qualquer escala; roda normal e invertida — `test_canvas2d_gestures.py` (`test_sentido`, `test_proporcional_ao_gesto_sem_degrau`, `test_ida_e_volta`, `test_delta_zero`, `test_mesma_pinca_em_qualquer_escala`, `test_roda`, `test_roda_invertida_pela_preferencia`) 🟢
- [ ] TT-06, Snaps, distâncias e grade (CA-07, CA-08) — `test_trava_ortogonal`, `test_distancias_e_grade` 🟢; adicionar caso de ângulo perto de 360° (EC-05) 🟢 _(Revisão 2026-10-10: test_trava_ortogonal cobre só ~2°, ~3° e ~270°)_
- [ ] TT-07, `dashed` com comprimento < 1e-6 e paridade dos pontos (CA-10) — 🟢 sem teste atual _(Revisão 2026-10-10: nenhum teste importa `canvas2d.draw`)_; é Python puro exceto pelos imports de `gpu`/`blf` do módulo, exige *stub* desses módulos
- [ ] TT-08, Abertura, fallback e fechamento da janela (CA-11, CA-12, EC-07) — 🔴 só verificável no Blender (`tests/blender_smoke.py` ou teste manual); não há teste automatizado identificado _(Revisão 2026-10-10: a abertura bem-sucedida tem cobertura indireta em tests/blender_004_cabinet_editor_smoke.py:104, blender_006:193 e blender_008:236 ("abre o editor" + `editor_area`); fallback, CA-12 e fechamento/EC-07 seguem sem teste)_

Comando dos testes puros 🟢 (de `requirements.md`): `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tests python3 -m unittest test_canvas2d_view test_canvas2d_gestures -v` (15 testes).

## Tarefas de Migração de Dados

🟢 Não se aplica: a unit não persiste dados (`View2D` e sessões vivem em memória).

## Ordem Sugerida

1. 🟢 T-01 → T-02 → T-03/T-04 → T-05/T-06: o núcleo puro primeiro, testável sem Blender; T-03 e T-04 dependem das conversões de T-02.
2. 🟢 T-07 depende só da interface `to_world` de T-02 (zoom janela) e pode correr em paralelo a T-05/T-06.
3. 🟢 T-08 → T-09 → T-10: desenho; T-10 depende de T-02 e T-09.
4. 🟢 T-11 → T-12 → T-13 → T-14: janela; `open_window` chama `prepare`, e `window_alive` usa `editor_area`.
5. 🟢 T-15 por último, com TT-08 como validação no Blender.

## Lacunas Pendentes (🔴)

- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-71):** snapshot mínimo (`show_menus`, `show_region_header`, `show_region_ui`) guardado em `open_window` e restaurado no fechamento (EC-08). Pendência de implementação: DT-02.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-6):** nesse ramo a área volta a `VIEW_3D` com `show_menus`/`show_region_header` ligados (EC-07). Pendência de implementação: DT-01.
- 🟡 Confirmar no Blender, por plataforma, o sinal de `compat.pinch_delta` e a sensibilidade 1/150 — decisão: medir/testar (DT-03; questions.md#pergunta-7).

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Em `window._close`, quando não há `restore_area_type` e a janela duplicada não pode ser fechada (única janela ou `window_ptr` diferente), voltar a área para `VIEW_3D` com `show_menus`/`show_region_header` ligados (decisão questions.md#pergunta-6)
- [ ] DT-02 Guardar em `open_window` (fallback) um snapshot de `show_menus`, `show_region_header` e `show_region_ui` e restaurá-lo em `_close` (decisão questions.md#pergunta-71)
- [ ] DT-03 Rodar `tests/blender_013_touchpad_smoke.py` e a prova manual de pinça em cada plataforma suportada (macOS, Wayland, X11/Windows) e registrar sinal e sensibilidade 1/150 em `investigation.md` §6 da 013 (decisão questions.md#pergunta-7)
- [ ] DT-04 Commitar a feature 013 (`canvas2d/gestures.py`, `compat.trackpad_delta`/`pinch_delta`, testes) antes de congelar as specs; até lá esses itens ficam pendentes de commit (decisão questions.md#pergunta-70)
