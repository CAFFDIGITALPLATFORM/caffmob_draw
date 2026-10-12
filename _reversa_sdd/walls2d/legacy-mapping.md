# Legacy mapping: unit `walls2d`

> Archaeologist, re-extração 2026-10-10. Arquivos de `caffmob_draw/walls2d/` com símbolos e linhas.

| Arquivo | Linhas | Símbolos principais |
|---------|--------|---------------------|
| `walls2d/__init__.py` | 25 | `register`/`unregister` (props, window, ops_editor, panels) |
| `walls2d/model.py` | 351 | `LIMITS` 24; `validate` 32; `Segment` 48; `Chain` 59 (`miter_angles` 105, `is_ccw` 115, `outward_side` 125, `outer_line` 133, `shifted_nodes` 153, `hb_order` 175, `set_length` 185, `move_node` 216, `split` 247, `remove_node` 260, `invert` 273, `close_if_touching` 292); `WallPlan` 311; `plan_signature` 336; `rectangle` 346 |
| `walls2d/history.py` | 58 | `History` 17 (`checkpoint` 26, `undo` 52, `redo` 56) |
| `walls2d/inference.py` | 43 | `Index` 11 (`query` 32); `plan_points` 40 |
| `walls2d/direction.py` | 47 | `ARROWS` 11; `initial_direction` 31; `label` 43 |
| `walls2d/heights.py` | 30 | `follows_project_height` 12; `walls_to_equalize` 19 |
| `walls2d/convert.py` | 49 | `chains_from_segments` 22 |
| `walls2d/scene_io.py` | 136 | `walls_in` 37; `reference_segments` 41; `read_plan` 60; `_chain_from` 82; `is_other_layer_wall` 100; `convert_into` 106 |
| `walls2d/apply.py` | 262 | `items_that_do_not_fit` 28; `modules_of_removed` 53; `height_mismatches` 82; `apply_plan` 95; `_rehost_opening` 186; `refresh_floors_and_ceilings` 211; `sync_project_height` 237 |
| `walls2d/props.py` | 352 | `Session` 17; `session`/`start`/`end` 108-117; `_guard` 123; campos virtuais 136-277; `BTM_PG_WallEditorState` 286 _(Revisão 2026-10-10: linhas conferidas no disco com a 013)_ |
| `walls2d/ops_editor.py` | 944 | `_region_rect` 85; `draw_plan` 104; barra superior 196-281; `handle_zoom_window` 250 _(Revisão 2026-10-10: linhas conferidas no disco com a 013)_; `resolve_point`; `BTM_OT_WallEditor`; `BTM_OT_WallEditorModal` (`modal`, `_handle`, `_handle_click`, `_handle_typing`, `_handle_draw`, `_handle_prompt`); `BTM_OT_WallEditorOk`; `BTM_OT_WallEditorCancel`; `BTM_OT_WallEditorFit` |
| `walls2d/panels.py` | 140 | `BTM_PT_WallEditorTools` 27; `BTM_PT_WallEditorSegment` 39; `BTM_PT_WallEditorGrid` 69; `BTM_PT_WallEditorConfirm` 88 |
| `walls2d/window.py` | 60 | `editor_area`, `is_editor_area`, `focus_editor_tab`, `open_editor`, `_draw` (handler `SpaceImageEditor` POST_PIXEL) |

Testes: `tests/blender_002_smoke.py`, `tests/blender_002_ui_events.py`, `tests/blender_009_walls_smoke.py`, `tests/blender_013_touchpad_smoke.py`, `tests/test_wall_direction.py`, `tests/test_wall_inference.py`, `tests/test_walls2d_convert.py`, `tests/test_walls2d_heights.py`, `tests/test_walls2d_history.py`, `tests/test_walls2d_model.py`

Origem no git:
- `fa24c0e 2026-10-09 feat: cabinet builder tabs, wall crosshair and math input, object library, SketchUp import, real doors and windows`
- `00ac2f6 2026-10-08 feat: cabinet editor, stick to flat faces, body collision and a single sidebar`
- `53f594c 2026-10-07 fix: openings follow the wall editor; full pt_BR/en_US interface`
- `b92ac2e 2026-10-07 fix: objects without a recorded type are no longer treated as walls`
- `499068f 2026-10-07 fix(wall-editor): segment panel shows and accepts the project unit`
- `9cd1d21 2026-10-07 fix(wall-editor): Ctrl+Z / Ctrl+Shift+Z inside the wall editor draft`
- `adcd52f 2026-10-07 feat: CAFFMob Draw identity, customizable modules, aggregates and floor fix`
