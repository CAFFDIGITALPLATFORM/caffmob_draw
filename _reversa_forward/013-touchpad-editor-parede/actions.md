# Actions: Zoom e navegação por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-10`
> Roadmap: `_reversa_forward/013-touchpad-editor-parede/roadmap.md` (D-01 a D-12)
> Data delta: `_reversa_forward/013-touchpad-editor-parede/data-delta.md`
> Interfaces: nenhuma (sem contrato externo)
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 18 |
| Paralelizáveis (`[//]`) | 11 |
| Maior cadeia de dependência | 8 (T001 → T002 → T003 → T008 → T009 → T015 → T016 → T018) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Prova D-02: script com janela (`--enable-event-simulate`) que abre o Editor de Paredes, envia `TRACKPADZOOM` e `TRACKPADPAN` por `Window.event_simulate` e imprime `type`, `mouse_x/y`, `mouse_prev_x/y` e `ctrl` de cada evento recebido pelo modal. Se a simulação não produzir delta, o script deixa um `print` ligado para a prova manual no notebook | - | `[//]` | `tests/blender_013_trackpad_probe.py` | 🟡 | `[X]` |
| T002 | Registrar o resultado da prova em `investigation.md` §6: eixo que leva a pinça, sinal de "afastar os dedos", sinal do arraste, unidade típica do delta por evento e o valor inicial de `PINCH_SENSITIVITY` | T001 | `[//]` | `_reversa_forward/013-touchpad-editor-parede/investigation.md` | 🟡 | `[X]` |
| T003 | `compat.trackpad_delta(event)` → `(dx, dy)` a partir de `mouse_x − mouse_prev_x` e `mouse_y − mouse_prev_y`, com o ajuste de eixo e sinal fixado em T002; docstring em português citando o corpus (D-03) | T002 | `[//]` | `caffmob_draw/compat.py` | 🟡 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T004 | Teste puro de `canvas2d/gestures.py` (D-12): `pinch_factor` sobe com delta positivo e desce com negativo; delta maior dá fator maior; nenhum fator igual a 1,15; ida e volta devolvem a escala com erro ≤ 0,1%; delta zero dá fator 1; âncora parada ≤ 1 px via `View2D.zoom`; `wheel_factor` com e sem inversão; `zoom_window_bounds` devolve `None` para lado < 5 px e bounds centrados (± 2 px) para um retângulo válido | - | `[//]` | `tests/test_canvas2d_gestures.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Módulo puro `canvas2d/gestures.py` (D-01): constantes `PINCH_SENSITIVITY` (provisória), `WHEEL_STEP = 1.15`, `ZOOM_WINDOW_MIN_PX = 5`; `pinch_factor(delta, sensitivity)` = `exp(delta × sensitivity)`; `wheel_factor(up, inverted)`; `zoom_window_bounds(view, p0_px, p1_px, min_px)` → bounds do mundo ou `None`. Sem `bpy`; faz T004 passar | - | `[//]` | `caffmob_draw/canvas2d/gestures.py` | 🟢 | `[X]` |
| T006 | Campos transitórios na `Session` (D-09): `zoom_window = None` (`None` / `'ARMED'` / pixel de início) e `zoom_box_end = None`; comentário explicando que ficam fora do histórico | - | `[//]` | `caffmob_draw/walls2d/props.py` | 🟢 | `[X]` |
| T007 | Constante `TOOLBAR_HEIGHT = 32` (× `ui_scale`) e `_region_rect` descontando a barra no topo, para que `fit`, Home e o zoom janela não escondam paredes atrás dela (D-08) | - | `[//]` | `caffmob_draw/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T008 | Navegação em `_handle` (D-04, D-05): `TRACKPADZOOM` → `view.zoom(gestures.pinch_factor(delta), pixel)`; `TRACKPADPAN` → `view.pan(dx, dy)` com o sinal de T002; roda e Ctrl + roda → `gestures.wheel_factor(up, context.preferences.inputs.invert_zoom_wheel)`; os três devolvem `True` (consumidos) | T003, T005, T007 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T009 | `modal` pula `_update_snap` nos eventos de navegação (`TRACKPADZOOM`, `TRACKPADPAN`, `WHEELUPMOUSE`, `WHEELDOWNMOUSE`, `MIDDLEMOUSE` e `MOUSEMOVE` durante o pan), mantendo `s.cursor` atualizado (D-06) | T008 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟢 | `[X]` |
| T010 | Calibração final: `PINCH_SENSITIVITY` e sinais em `gestures.py` e `compat.trackpad_delta` conforme `investigation.md` §6; a mesma pinça dá o mesmo resultado em qualquer escala de partida (RF-02) | T002, T005, T008 | - | `caffmob_draw/canvas2d/gestures.py` | 🟡 | `[ ]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T011 | Barra superior em `draw_plan` (D-07): faixa de `TOOLBAR_HEIGHT` na largura visível (`window.visible_width`), com `rect`/`outline` de `canvas2d/draw.py`; botão da lupa com quadrado desenhado em linhas (círculo, cabo, quadrado); realce quando `s.zoom_window` está ligado ou o mouse está em cima; função `_toolbar_rects(region)` devolve o retângulo do botão | T006, T007 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T012 | Dica "Zoom janela: marque um retângulo para enquadrar" ao passar o mouse sobre a lupa (via `tr`) e retângulo elástico tracejado entre `s.zoom_window` e `s.zoom_box_end` enquanto o projetista marca | T011 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T013 | Modo zoom janela em `_handle`, na ordem D-10: clique na lupa liga (`'ARMED'`) ou desliga; com o modo ligado, Esc ou segundo clique na lupa cancela sem mexer na vista; `LEFTMOUSE` PRESS na planta grava o início, `MOUSEMOVE` atualiza `zoom_box_end`, RELEASE chama `gestures.zoom_window_bounds` e `view.fit(bounds, margin=0)` quando não é `None`, depois desliga o modo; com o modo ligado nenhum outro clique ou tecla chega às ferramentas, exceto navegação (T008) e Ctrl+Z; nada entra no histórico (RN-07) | T005, T006, T008, T011 | - | `caffmob_draw/walls2d/ops_editor.py` | 🟡 | `[X]` |
| T014 | Tradução pt_BR e en_US da dica da lupa no catálogo do editor de paredes (D-11); `tests/test_i18n_coverage.py` passa | T012 | `[//]` | `caffmob_draw/data/translations/walls2d.json` | 🟢 | `[X]` |
| T015 | Fumaça em segundo plano (D-12): abre o editor com a sala de 3.900 × 2.700, chama `modal` com eventos falsos (`types.SimpleNamespace`) e confere: pinça aproxima e afasta com âncora ≤ 1 px; `TRACKPADPAN` move 100 px (± 1 px) sem mudar a escala; Ctrl + roda = 1,15; roda invertida pela preferência; com "2.4" digitado e com a pergunta aberta a escala muda e `s.typed`/`s.prompt` não; contagem de passos do desfazer igual antes e depois; evento sobre o painel lateral devolve `PASS_THROUGH`; zoom janela enquadra, Esc cancela, retângulo de 3 px não muda a vista | T009, T013 | `[//]` | `tests/blender_013_touchpad_smoke.py` | 🟢 | `[X]` |
| T016 | Regressão: `tests/test_canvas2d_view.py`, `tests/test_canvas2d_gestures.py`, `tests/test_i18n_coverage.py`, fumaças 002 e 009 do editor de parede (`blender_002_smoke.py`, `blender_009_walls_smoke.py`) e `blender_013_touchpad_smoke.py`; `ruff check caffmob_draw/` e `check_api.py` sem erro | T010, T014, T015 | - | `tests/` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T017 | Docstring de `gestures.py` e cabeçalho de `ops_editor.py` citam a 013, as decisões (D-01, D-04 a D-10) e o corpus dos eventos e da preferência, em português | T010, T013 | `[//]` | `caffmob_draw/canvas2d/gestures.py` | 🟢 | `[X]` |
| T018 | `onboarding.md`: registrar o valor calibrado, as plataformas em que a prova rodou (Wayland, X11, macOS, Windows) e o que ficou sem teste à mão | T016 | `[//]` | `_reversa_forward/013-touchpad-editor-parede/onboarding.md` | 🟢 | `[X]` |

## Notas de execução

- 2026-10-10: T001 rodou com janela no próprio ambiente (Wayland, Blender 5.2.0). A simulação fixou a codificação do
  delta, não o sinal do gesto real; T010 fica aberto até a prova à mão num notebook com touchpad (`onboarding.md` §4).
  `compat.pinch_delta` segue a convenção do Blender (afastar = `mouse_prev_x > mouse_x`).
- `_handle_zoom_window` virou função de módulo (`handle_zoom_window`): as fumaças 002 e 009 ligam ao modal falso uma
  lista fixa de métodos, e um método novo chamado por `_handle` as quebrava.
- Em segundo plano `ui_scale` vem 0; `_ui_scale` cai em 1,0.
- T016 rodou sobre o código atual (002, 009, 013 em segundo plano; 002 UI com janela; 18 testes puros; ruff;
  check_api). Se T010 mudar o sinal ou a sensibilidade, T016 roda de novo.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-10 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-10 | 17 de 18 ações concluídas por `/reversa-coding`; T010 aguarda a prova à mão | reversa-coding |
