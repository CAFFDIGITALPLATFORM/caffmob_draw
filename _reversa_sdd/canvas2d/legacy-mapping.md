# Legacy mapping: unit `canvas2d`

> Archaeologist, re-extração 2026-10-10. Arquivos de `caffmob_draw/canvas2d/` com as funções principais e linhas.

| Arquivo | Linhas | Símbolos principais |
|---------|--------|---------------------|
| `caffmob_draw/canvas2d/__init__.py` | 1 | pacote (feature 002) |
| `caffmob_draw/canvas2d/view.py` | 106 | `View2D` (l. 14-68: `to_screen` 21, `to_world` 26, `contains` 31, `pan` 36, `zoom` 39, `fit` 49, `grid_lines` 58); `snap_to_grid` 71; `ortho_snap` 77; `distance_point_point` 92; `distance_point_segment` 96 |
| `caffmob_draw/canvas2d/gestures.py` | 41 | `PINCH_SENSITIVITY`, `WHEEL_STEP`, `ZOOM_WINDOW_MIN_PX` (l. 17-19); `pinch_factor` 22; `wheel_factor` 27; `zoom_window_bounds` 32 _(Revisão 2026-10-10: linhas conferidas no disco; arquivo tem 38 linhas)_ |
| `caffmob_draw/canvas2d/draw.py` | 117 | `COLORS` 19; `shader` 36; `begin` 42; `end` 47; `rect` 53; `outline` 57; `lines` 61; `dashed` 66; `text` 80; `text_width` 85; `button` 90; `length_label` 97; `box` 103; `segment` 114 |
| `caffmob_draw/canvas2d/window.py` | 128 | `editor_area` 14; `side_panel` 26; `over_side_panel` 32; `visible_width` 39; `is_editor_area` 47; `prepare` 51; `focus_tab` 64; `open_window` 79; `_close` 105; `close_later` 125; `window_alive` 130 _(Revisão 2026-10-10: linhas conferidas no disco; arquivo tem 132 linhas)_ |

Testes: `tests/test_canvas2d_view.py`, `tests/test_canvas2d_gestures.py` (puros, via `tests/_bootstrap.py`).

Origem no git: `adcd52f` (2026-10-07, identidade CAFFMob Draw), `53f594c` (2026-10-07), `00ac2f6` (2026-10-08, editor de
armário), feature 013 (2026-10-10, `gestures.py`, ainda sem commit).
