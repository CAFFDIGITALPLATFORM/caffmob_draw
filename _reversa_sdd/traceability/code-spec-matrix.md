# Matriz de Rastreabilidade (Código x Especificação) — BlenderToMob

Este documento mapeia a cobertura de arquivos do código legado do add-on **BlenderToMob** pelas especificações de unidades de design criadas no nível **Detalhado**.

---

## 1. Matriz de Cobertura

| Arquivo do Legado | Unit Correspondente | Cobertura de Requisitos | Confiança |
|-------------------|---------------------|:-----------------------:|:---------:|
| `blendertomob/data/properties.py` | `data/` | 🟢 Completa (Mapeia PropertyGroups e reatividade) | 🟢 |
| `blendertomob/geometry/mesh_gen.py` | `geometry/` | 🟢 Completa (Mapeia modeladores bmesh e Convex Hull) | 🟢 |
| `blendertomob/geometry/materials.py` | `geometry/` | 🟢 Completa (Mapeia registro de materiais e HSV) | 🟢 |
| `blendertomob/operators/wall_builder.py` | `operators/` | 🟢 Completa (Mapeia desenho modal de polilinhas) | 🟢 |
| `blendertomob/operators/opening_builder.py` | `operators/` | 🟢 Completa (Mapeia snaps, peitoril e transições de vãos) | 🟢 |
| `blendertomob/operators/floor_builder.py` | `operators/` | 🟢 Completa (Mapeia acionador do Convex Hull do piso) | 🟢 |
| `blendertomob/overlays/draw_handlers.py` | `overlays/` | 🟢 Completa (Mapeia cotas visual e grades de piso GPU) | 🟢 |
| `blendertomob/ui/panels.py` | `ui/` | 🟢 Completa (Mapeia árvore Sidebar e reatividade reativa) | 🟢 |
| `blendertomob/cutting/nesting.py` | `cutting/` | 🟢 Completa (Mapeia otimização Next-Fit Decreasing) | 🟢 |

---

## 2. Estatísticas de Cobertura

- **Total de Arquivos Código Fonte do Legado**: 9
- **Arquivos Mapeados em Especificações**: 9
- **Percentual de Cobertura**: 100% 🟢

---

## Re-extração 2026-10

> Seção aditiva gerada pelo **Writer** (Reversa) em 2026-10-10. As seções 1 e 2 acima descrevem a extração de 2026-07
> sobre o pacote antigo `blendertomob/` (9 arquivos) e ficam preservadas como registro histórico. Esta seção mapeia o
> pacote atual `caffmob_draw/` (391 arquivos `.py`, sem `__pycache__`) contra as 18 units da re-extração 2026-10.
> Posse dos arquivos: `primary_files` de `.reversa/context/modules.json`. Caminhos relativos a `caffmob_draw/`.
> Cobertura: 🟢 arquivo descrito pela spec a partir do código (citado na rastreabilidade da unit) · 🟡 coberto só
> parcialmente ou por spec de versão anterior / citação transversal · n/a nenhuma unit cobre.

### R1. Matriz das 18 units

| Arquivo do legado | Unit correspondente | Cobertura |
|---|---|---|
| `canvas2d/__init__.py` | [`canvas2d`](../canvas2d/requirements.md) | 🟢 |
| `canvas2d/draw.py` | [`canvas2d`](../canvas2d/requirements.md) | 🟢 |
| `canvas2d/gestures.py` | [`canvas2d`](../canvas2d/requirements.md) | 🟢 |
| `canvas2d/view.py` | [`canvas2d`](../canvas2d/requirements.md) | 🟢 |
| `canvas2d/window.py` | [`canvas2d`](../canvas2d/requirements.md) | 🟢 |
| `walls2d/__init__.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/apply.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/convert.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/direction.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/heights.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/history.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/inference.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/model.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/ops_editor.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/panels.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/props.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/scene_io.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `walls2d/window.py` | [`walls2d`](../walls2d/requirements.md) | 🟢 |
| `openings/__init__.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/build.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/door_core.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/materials.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/ops.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/props.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/region.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/region_core.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/region_props.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/sync.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `openings/window_core.py` | [`openings`](../openings/requirements.md) | 🟢 |
| `move_over/__init__.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/align.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/insertion_plane.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/ops_dialog.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/ops_drag.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/ops_move_on_wall.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/ops_substitute.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/props.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/reposition.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `move_over/scene.py` | [`move_over`](../move_over/requirements.md) | 🟢 |
| `measure/__init__.py` | [`measure`](../measure/requirements.md) | 🟢 |
| `measure/cotas.py` | [`measure`](../measure/requirements.md) | 🟢 |
| `measure/scene_cotas.py` | [`measure`](../measure/requirements.md) | 🟢 |
| `selection/__init__.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/classify.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/component.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/component_pick.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/component_props.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/component_select.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/editing.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/element_size.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `selection/resize.py` | [`selection`](../selection/requirements.md) | 🟢 |
| `stick/__init__.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/apply.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/frame.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/link.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/magnet.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/magnet_preview.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/migrate.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/ops_stick.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/panels.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/props.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `stick/settle.py` | [`stick`](../stick/requirements.md) | 🟢 |
| `collision/__init__.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/obb.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/ops_collision.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/overlay.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/panels.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/props.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/rules.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/scan.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `collision/stale.py` | [`collision`](../collision/requirements.md) | 🟢 |
| `geometry_free/__init__.py` | [`geometry_free`](../geometry_free/requirements.md) | 🟢 |
| `geometry_free/mesh.py` | [`geometry_free`](../geometry_free/requirements.md) | 🟢 |
| `geometry_free/ops_create.py` | [`geometry_free`](../geometry_free/requirements.md) | 🟢 |
| `geometry_free/ops_edit.py` | [`geometry_free`](../geometry_free/requirements.md) | 🟢 |
| `geometry_free/props.py` | [`geometry_free`](../geometry_free/requirements.md) | 🟢 |
| `inspection/__init__.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/__init__.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/aggregate_leaf.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/btm.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/closets.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/face_frame.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/frameless.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/adapters/room_doors.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/fronts.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/gizmo.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/interference.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/ops_inspect.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/ops_interference.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/overlay.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/pivot_math.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/props.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/room_door_leaf.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/room_door_math.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `inspection/save_guard.py` | [`inspection`](../inspection/requirements.md) | 🟢 |
| `cabinet_editor/__init__.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/appliances.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/bays.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/bridge.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/catalog.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/data_props.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/divisions.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/elevation.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/extras.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/ops_actions.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/ops_editor.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_backs.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_divisions.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_doors.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_drawers.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_interior.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_sliding.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_structure.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/panels_tabs_common.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/position.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/previews.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/props.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/reflow_handler.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/scene_divisions.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/scene_extras.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/scene_interiors.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/scene_parts.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/scene_slides.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/slides.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/state.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/structure.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/validate.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `cabinet_editor/window.py` | [`cabinet_editor`](../cabinet_editor/requirements.md) | 🟢 |
| `data/dimension_schema.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `operators/ops_standards.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/__init__.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/api.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/apply_core.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/builtin.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/cabinet_defaults.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/io_json.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/io_promob.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/migration.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/model.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/previews.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `standards/sync.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `ui/standards_tree.py` | [`standards`](../standards/requirements.md) | 🟢 |
| `customize/__init__.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/__init__.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/btm.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/closets.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/common.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/face_frame.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/adapters/frameless.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/library_io.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/manifest.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/ops_customize.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/ops_library.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/panels.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/props.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/reapply.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `customize/spec.py` | [`customize`](../customize/requirements.md) | 🟢 |
| `aggregates/__init__.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/apply.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/collision.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/convert.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/group.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/group_props.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/grouping.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/import_units.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/install.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/leaf.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/limits.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/ops_aggregate.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/ops_group.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/ops_import.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/ops_install.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/overlay.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/panels.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/perforate.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/production.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/props.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/skp.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/skp_build.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/skp_core.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/slide_limits.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/sweep.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `aggregates/window_props.py` | [`aggregates`](../aggregates/requirements.md) | 🟢 |
| `molding/__init__.py` | [`molding`](../molding/requirements.md) | 🟢 |
| `molding/adapters.py` | [`molding`](../molding/requirements.md) | 🟢 |
| `molding/engine.py` | [`molding`](../molding/requirements.md) | 🟢 |
| `molding/ops.py` | [`molding`](../molding/requirements.md) | 🟢 |
| `molding/packages.py` | [`molding`](../molding/requirements.md) | 🟢 |
| `legacy/__init__.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/convert.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/convert_core.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/gate.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/groups.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/groups_core.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `legacy/ops.py` | [`legacy`](../legacy/requirements.md) | 🟢 |
| `library_panel/__init__.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/categories.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/categories_core.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/draw.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/layout_core.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/models_core.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/ops_cabinet.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/ops_categories.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/ops_click.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/popover.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `library_panel/props.py` | [`library_panel`](../library_panel/requirements.md) | 🟢 |
| `object_library/__init__.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/catalog.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/item_io.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/ops.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/panels.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/previews.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/props.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/retexture.py` | [`object_library`](../object_library/requirements.md) | 🟢 |
| `object_library/store.py` | [`object_library`](../object_library/requirements.md) | 🟢 |

### R2. Arquivos mapeados por unit (18 units)

| Unit | Arquivos `.py` | Linhas | 🟢 | 🟡 | Observação |
|---|---:|---:|---:|---:|---|
| `canvas2d` | 5 | 392 | 5 | 0 |  |
| `walls2d` | 13 | 2.497 | 13 | 0 |  |
| `openings` | 11 | 1.169 | 11 | 0 |  |
| `move_over` | 10 | 1.338 | 10 | 0 |  |
| `measure` | 3 | 220 | 3 | 0 |  |
| `selection` | 9 | 949 | 9 | 0 |  |
| `stick` | 11 | 1.486 | 11 | 0 |  |
| `collision` | 9 | 986 | 9 | 0 |  |
| `geometry_free` | 5 | 458 | 5 | 0 |  |
| `inspection` | 19 | 2.200 | 19 | 0 | `adapters/__init__.py` coberto pela linha `adapters/*.py` da rastreabilidade |
| `cabinet_editor` | 34 | 5.443 | 34 | 0 | 34 arquivos; linhas agrupadas por padrão (`scene_*.py`, `panels*.py`) na rastreabilidade |
| `standards` | 14 | 2.734 | 14 | 0 | inclui 3 arquivos fora da pasta: `data/dimension_schema.py`, `operators/ops_standards.py`, `ui/standards_tree.py` |
| `customize` | 15 | 3.028 | 15 | 0 |  |
| `aggregates` | 26 | 3.000 | 26 | 0 |  |
| `molding` | 5 | 1.687 | 5 | 0 | mesma pasta já coberta por `catalog_molding` (2026-10-01); a posse passa a `molding` |
| `legacy` | 7 | 705 | 7 | 0 |  |
| `library_panel` | 11 | 905 | 11 | 0 |  |
| `object_library` | 9 | 907 | 9 | 0 |  |
| **Total** | **216** | **30.104** | **216** | **0** | |

### R3. Cobertura estimada do pacote `caffmob_draw/`

| Origem da cobertura | Arquivos | Linhas | Cobertura |
|---|---:|---:|---|
| 18 units da re-extração 2026-10 | 216 | 30.104 | 🟢 |
| Units legadas de 2026-10-01 (`hb_core`, `hb_placement`, `hb_layouts`, `product_common`, `frameless`, `face_frame`, `closets`, `catalog_molding`) — ver [`code-spec-matrix-legacy.md`](code-spec-matrix-legacy.md) | 103 | 109.456 | 🟢 |
| Units antigas de 2026-07 (`data`, `geometry`, `operators`, `overlays`, `ui`, `cutting`, `wall_editor`), arquivos só citados por units legadas e transversais | 30 | 24.921 | 🟡 |
| Sem unit | 42 | 6.362 | n/a |
| **Total do pacote** | **391** | **170.843** | |

- 🟢 Arquivos com alguma unit: **349 de 391 (89,3%)**; só 🟢: 319 (81,6%).
- 🟡 Cobertura estimada ponderada (🟢 = 1, 🟡 = 0,5): **85,4%** dos arquivos.
- 🟢 Por linhas: 96,3% das 170.843 linhas do pacote estão em arquivos com alguma unit; os 42 arquivos sem unit somam 6.362 linhas.
- 🟡 Os 🟡 de 2026-07 descrevem o pacote `blendertomob/` daquela data: `data/properties.py`, `ui/panels.py`, `operators/wall_builder.py` e afins cresceram desde então e a spec antiga não cobre os acréscimos (ex.: `data/properties.py` tem hoje 925 linhas).
- 🟡 `compat.py` é transversal: citado por `hb_core`, `canvas2d` e `walls2d` (feature 013), sem unit própria.

#### Arquivos 🟡 fora das 18 units

| Arquivo | Unit (spec antiga ou citação) | Cobertura |
|---|---|---|
| `__init__.py` | `hb_core` | 🟡 |
| `compat.py` | `transversal (hb_core/canvas2d/walls2d)` | 🟡 |
| `cutting/__init__.py` | `cutting` | 🟡 |
| `cutting/nesting.py` | `cutting` | 🟡 |
| `cutting/part_extractor.py` | `frameless (citado)` | 🟡 |
| `data/__init__.py` | `data` | 🟡 |
| `data/properties.py` | `data` | 🟡 |
| `data/units.py` | `hb_core (citado)` | 🟡 |
| `geometry/__init__.py` | `geometry` | 🟡 |
| `geometry/materials.py` | `geometry` | 🟡 |
| `geometry/mesh_gen.py` | `geometry` | 🟡 |
| `operators/__init__.py` | `operators` | 🟡 |
| `operators/details.py` | `hb_placement/hb_layouts (citado)` | 🟡 |
| `operators/doors_windows.py` | `hb_placement (citado)` | 🟡 |
| `operators/floor_builder.py` | `operators` | 🟡 |
| `operators/layouts.py` | `hb_core/hb_placement/hb_layouts (citado)` | 🟡 |
| `operators/opening_builder.py` | `operators` | 🟡 |
| `operators/ops_general.py` | `closets (citado)` | 🟡 |
| `operators/ops_obstacles.py` | `hb_core/hb_placement (citado)` | 🟡 |
| `operators/scene_navigator.py` | `hb_placement (citado)` | 🟡 |
| `operators/viewport_hud.py` | `hb_placement/closets (citado)` | 🟡 |
| `operators/wall_builder.py` | `operators` | 🟡 |
| `operators/walls.py` | `wall_editor` | 🟡 |
| `overlays/__init__.py` | `overlays` | 🟡 |
| `overlays/draw_handlers.py` | `overlays` | 🟡 |
| `ui/__init__.py` | `ui` | 🟡 |
| `ui/menu_apend.py` | `face_frame (citado)` | 🟡 |
| `ui/menus.py` | `hb_core (citado)` | 🟡 |
| `ui/panels.py` | `ui` | 🟡 |
| `ui/view3d_sidebar.py` | `hb_layouts (citado)` | 🟡 |

### R4. Arquivos `.py` do pacote sem unit (candidatos a análise adicional)

🔴 Nenhuma spec descreve estes arquivos. "Citado por" lista as units da re-extração que os mencionam como dependência ou consumidor (não é cobertura). "Novo" = o caminho não existia em `blendertomob/` no commit `f053c6f` (2026-08-01, matriz de 2026-07).

| Arquivo | Linhas | Novo após 2026-07 | Citado por |
|---|---:|:---:|---|
| `compat_identity.py` | 64 | sim | — |
| `cutting/csv_exporter.py` | 81 | sim | — |
| `cutting/drilling.py` | 136 | sim | `customize` |
| `cutting/hardware.py` | 71 | sim | — |
| `cutting/json_exporter.py` | 431 | sim | — |
| `cutting/machining.py` | 48 | sim | — |
| `cutting/part_roles.py` | 115 | sim | — |
| `cutting/part_sources.py` | 307 | sim | `aggregates`, `geometry_free` |
| `cutting/stale.py` | 86 | sim | `collision`, `inspection`, `geometry_free` |
| `data/dimensions_preset.py` | 142 | sim | — |
| `data/expr.py` | 147 | sim | `walls2d`, `move_over`, `measure` |
| `data/i18n.py` | 83 | não | `canvas2d`, `walls2d`, `move_over`, `measure`, `selection`, `openings`, `aggregates`, `collision`, `standards`, `library_panel`, `object_library`, `inspection` |
| `geometry/door_controller.py` | 319 | não | `customize` |
| `geometry/floor_outline.py` | 53 | sim | `walls2d` |
| `library_common.py` | 54 | sim | `object_library` |
| `operators/cabinet_builder.py` | 107 | não | `standards`, `legacy`, `library_panel` |
| `operators/export.py` | 211 | não | — |
| `operators/ops_cutting.py` | 239 | sim | `standards` |
| `operators/ops_dimensions.py` | 59 | sim | — |
| `operators/ops_stairs.py` | 756 | não | — |
| `operators/ops_wall_extras.py` | 260 | sim | `walls2d` |
| `operators/rooms.py` | 671 | não | — |
| `overlays/element_toast.py` | 93 | sim | `canvas2d`, `selection` |
| `overlays/selection_cotas.py` | 87 | sim | `measure` |
| `ui/context_menu.py` | 78 | sim | `move_over`, `stick`, `customize`, `legacy`, `inspection` |
| `ui/layout_probe.py` | 152 | sim | — |
| `ui/my_modules.py` | 48 | sim | `customize`, `legacy`, `library_panel` |
| `ui/object_properties.py` | 538 | sim | `move_over`, `measure`, `selection`, `aggregates`, `collision`, `stick`, `customize`, `cabinet_editor`, `inspection`, `geometry_free` |
| `ui/ops_resize.py` | 71 | sim | `selection` |
| `ui/save_feedback.py` | 90 | sim | `collision`, `stick` |
| `ui/sidebar.py` | 104 | sim | `object_library` |
| `ui/sidebar_build.py` | 122 | sim | `walls2d`, `openings`, `legacy`, `geometry_free` |
| `ui/sidebar_check.py` | 19 | sim | `collision` |
| `ui/sidebar_insert.py` | 40 | sim | `aggregates`, `legacy`, `object_library`, `molding` |
| `ui/sidebar_project.py` | 97 | sim | `legacy` |
| `ui/sidebar_props.py` | 65 | sim | — |
| `ui/sidebar_proxy.py` | 49 | sim | — |
| `ui/sidebar_selected.py` | 79 | sim | `legacy`, `object_library` |
| `ui/sidebar_selection.py` | 55 | sim | — |
| `ui/sidebar_vocab.py` | 44 | sim | `move_over`, `collision`, `stick`, `cabinet_editor`, `inspection` |
| `ui/view_mode.py` | 66 | sim | `openings` |
| `ui/view_mode_core.py` | 25 | sim | — |

Total: **42 arquivos** sem unit, dos quais **36** surgiram depois de 2026-07.

### R5. Arquivos novos (após 2026-07) fora das 18 units e sem cobertura

- 🔴 **Produção (`cutting/` e operadores)**: `cutting/csv_exporter.py`, `cutting/drilling.py`, `cutting/hardware.py`, `cutting/json_exporter.py`, `cutting/machining.py`, `cutting/part_roles.py`, `cutting/part_sources.py`, `cutting/stale.py`, `operators/ops_cutting.py`.
- 🔴 **Interface lateral e menus (`ui/`)**: `ui/context_menu.py`, `ui/layout_probe.py`, `ui/my_modules.py`, `ui/object_properties.py`, `ui/ops_resize.py`, `ui/save_feedback.py`, `ui/sidebar.py`, `ui/sidebar_build.py`, `ui/sidebar_check.py`, `ui/sidebar_insert.py`, `ui/sidebar_project.py`, `ui/sidebar_props.py`, `ui/sidebar_proxy.py`, `ui/sidebar_selected.py`, `ui/sidebar_selection.py`, `ui/sidebar_vocab.py`, `ui/view_mode.py`, `ui/view_mode_core.py`.
- 🔴 **Overlays**: `overlays/element_toast.py`, `overlays/selection_cotas.py`.
- 🔴 **Dados e núcleo**: `compat_identity.py`, `data/dimensions_preset.py`, `data/expr.py`, `geometry/floor_outline.py`, `library_common.py`.
- 🔴 **Outros operadores**: `operators/ops_dimensions.py`, `operators/ops_wall_extras.py`.

Sugestão de próximas units (🟡, derivada do agrupamento acima): `production` (lista de peças, furação, ferragens, JSON/CSV, plano de corte desatualizado — substitui a unit `cutting/` de 2026-07, que só cobre `nesting.py`), `sidebar` (barra lateral única, menu de contexto, propriedades do objeto, vocabulário, aviso ao salvar) e `core_data` (`data/expr.py`, `data/units.py`, `data/i18n.py`, `data/dimensions_preset.py`, `compat_identity.py`). Arquivos antigos ainda sem unit: `operators/export.py`, `operators/ops_stairs.py`, `operators/rooms.py`, `geometry/door_controller.py`, `operators/cabinet_builder.py`.

### R6. Conferência da revisão cruzada (2026-10-10)

- 🟢 Os 391 arquivos `.py` de `caffmob_draw/` (sem `__pycache__`) aparecem nesta matriz (R1, R3 ou R4) ou em [`code-spec-matrix-legacy.md`](code-spec-matrix-legacy.md); nenhum caminho citado deixou de existir. Linhas por unit (R2) e por arquivo sem unit (R4) conferem com `wc -l` do disco.
- 🟡 Posse: `molding/*.py` é da unit `molding` (a matriz legada foi corrigida para não manter duas specs vivas do mesmo código). `catalog/*.py` (7 arquivos) continua só em `catalog_molding` e não é importado pelo add-on.
- 🔴 Continuam sem unit os 42 arquivos de R4 mais `compat.py` (transversal); agrupamento sugerido em `.reversa/context/review-2026-10/_cross.json` › `missing_units`.

