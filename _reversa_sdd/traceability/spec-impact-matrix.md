# Matriz de Impacto de Componentes — BlenderToMob

Este documento apresenta a matriz de impacto cruzada entre as especificações e os componentes técnicos do add-on **BlenderToMob**, conduzido pelo agente **Architect** no nível de documentação **Detalhado**.

---

## 1. Matriz de Impacto

A tabela abaixo cruza os componentes do sistema (colunas) com os demais componentes do add-on (linhas), indicando o grau de impacto que mudanças em um exercem sobre o outro:

* 🔴 **Forte Impacto**: Mudanças estruturais exigem refatoração completa do componente impactado.
* 🟡 **Médio Impacto**: Requer alteração pontual de assinaturas ou lógica de consumo.
* ⚪ **Sem Impacto / Baixo**: Mudanças são transparentes e não afetam o componente.

| Componente de Origem | data (Properties) | geometry (mesh_gen) | operators (Wall/Opening) | overlays (draw_handlers) | ui (panels) | cutting (nesting) |
|----------------------|:-----------------:|:-------------------:|:------------------------:|:------------------------:|:-----------:|:-----------------:|
| **data (Properties)** | - | 🔴 Forte | 🔴 Forte | 🟡 Médio | 🔴 Forte | ⚪ Baixo |
| **geometry (mesh_gen)**| ⚪ Baixo | - | 🔴 Forte | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo |
| **operators** | 🟡 Médio | ⚪ Baixo | - | 🔴 Forte | 🟡 Médio | ⚪ Baixo |
| **overlays** | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | - | 🟡 Médio | ⚪ Baixo |
| **ui (panels)** | ⚪ Baixo | ⚪ Baixo | 🟡 Médio | ⚪ Baixo | - | 🟡 Médio |
| **cutting (nesting)** | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | ⚪ Baixo | 🟡 Médio | - |

---

## 2. Descrição das Relações de Dependência Críticas

1. **data → geometry, operators, ui (Forte Impacto 🔴)**:
   - Os dados paramétricos armazenados no módulo `data` servem como a única fonte de verdade para a engine de geometria e as janelas da interface lateral. Se uma propriedade de `properties.py` for renomeada, removida ou tiver seu tipo modificado:
     - O `mesh_gen.py` falhará em ler os argumentos de tamanho, gerando geometrias corrompidas ou zeradas.
     - Os operadores modais e painéis da UI lançarão erros de atributo (`AttributeError`) imediatos ao tentar renderizar ou atualizar valores no painel lateral.
2. **geometry → operators (Forte Impacto 🔴)**:
   - Mudanças nas funções de modelagem `generate_*` (especialmente assinaturas de parâmetros) impactam diretamente os operadores de criação de paredes, pisos e vãos. Se `generate_wall_from_segments` for modificada, o operador modal de paredes quebrará no método `_finish`.
3. **operators → overlays (Forte Impacto 🔴)**:
   - Os operadores modais interativos (`WallBuilder` e `InsertOpening`) dependem dos draw handlers em tempo real para pintar as cotas na viewport. Se a estrutura ou referências do `draw_handlers.py` mudarem, os builders modal falharão em iniciar ou deixarão de desenhar cotas, invalidando o feedback visual do usuário.


## Re-extração 2026-10-10 — arquitetura atual

🟢 Dependências extraídas dos imports AST dos arquivos registrados pela escavação. A direção A → B significa A consome B; alteração de B pode afetar A. Não é ordem de prioridade nem severidade de bug. Imports locais/condicionais também aparecem. Referência a pacote não demonstra que toda função dele é chamada; dispatch por string/bpy.ops e callbacks devem ser cruzados com os fluxos documentados.

| Consumidor / unit | Dependência | Evidência do import | Contrato a conferir |
|---|---|---|---|
| aggregates | compat | `caffmob_draw/aggregates/perforate.py:14` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | cutting | `caffmob_draw/aggregates/perforate.py:15` → `caffmob_draw.cutting` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | data | `caffmob_draw/aggregates/convert.py:13` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | hb_types | `caffmob_draw/aggregates/perforate.py:14` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | inspection | `caffmob_draw/aggregates/collision.py:22` → `caffmob_draw.inspection` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | operators | `caffmob_draw/aggregates/install.py:54` → `caffmob_draw.operators.doors_windows` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | selection | `caffmob_draw/aggregates/ops_aggregate.py:241` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | stick | `caffmob_draw/aggregates/ops_aggregate.py:265` → `caffmob_draw.stick` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| aggregates | ui | `caffmob_draw/aggregates/ops_aggregate.py:275` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/aggregates |
| cabinet_editor | aggregates | `caffmob_draw/cabinet_editor/scene_slides.py:14` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | canvas2d | `caffmob_draw/cabinet_editor/window.py:19` → `caffmob_draw.canvas2d` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | collision | `caffmob_draw/cabinet_editor/validate.py:15` → `caffmob_draw.collision` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | compat | `caffmob_draw/cabinet_editor/scene_divisions.py:21` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | customize | `caffmob_draw/cabinet_editor/bridge.py:19` → `caffmob_draw.customize` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | cutting | `caffmob_draw/cabinet_editor/bridge.py:21` → `caffmob_draw.cutting` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | data | `caffmob_draw/cabinet_editor/validate.py:16` → `caffmob_draw.data` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | hb_types | `caffmob_draw/cabinet_editor/scene_interiors.py:9` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | product_libraries | `caffmob_draw/cabinet_editor/scene_divisions.py:97` → `caffmob_draw.product_libraries.frameless.types_frameless` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | selection | `caffmob_draw/cabinet_editor/bridge.py:22` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | standards | `caffmob_draw/cabinet_editor/bridge.py:314` → `caffmob_draw.standards` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | stick | `caffmob_draw/cabinet_editor/bridge.py:238` → `caffmob_draw.stick` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | ui | `caffmob_draw/cabinet_editor/ops_editor.py:387` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| cabinet_editor | walls2d | `caffmob_draw/cabinet_editor/state.py:12` → `caffmob_draw.walls2d` | Dados/assinaturas e fluxo em code-analysis/cabinet_editor |
| canvas2d | compat | `caffmob_draw/canvas2d/draw.py:12` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/canvas2d |
| canvas2d | data | `caffmob_draw/canvas2d/draw.py:13` → `caffmob_draw.data` | Dados/assinaturas e fluxo em code-analysis/canvas2d |
| canvas2d | hb_gpu_draw | `caffmob_draw/canvas2d/draw.py:12` → `caffmob_draw.hb_gpu_draw` | Dados/assinaturas e fluxo em code-analysis/canvas2d |
| collision | data | `caffmob_draw/collision/scan.py:20` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/collision |
| collision | selection | `caffmob_draw/collision/scan.py:21` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/collision |
| collision | stick | `caffmob_draw/collision/scan.py:46` → `caffmob_draw.stick` | Dados/assinaturas e fluxo em code-analysis/collision |
| collision | ui | `caffmob_draw/collision/scan.py:258` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/collision |
| customize | cabinet_editor | `caffmob_draw/customize/reapply.py:67` → `caffmob_draw.cabinet_editor` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | compat | `caffmob_draw/customize/library_io.py:173` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | cutting | `caffmob_draw/customize/adapters/common.py:7` → `caffmob_draw.cutting` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | data | `caffmob_draw/customize/spec.py:9` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | geometry | `caffmob_draw/customize/adapters/btm.py:11` → `caffmob_draw.geometry` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | hb_placement | `caffmob_draw/customize/ops_library.py:12` → `caffmob_draw.hb_placement` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | hb_project | `caffmob_draw/customize/library_io.py:189` → `caffmob_draw.hb_project` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | hb_snap | `caffmob_draw/customize/ops_library.py:12` → `caffmob_draw.hb_snap` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | hb_types | `caffmob_draw/customize/adapters/frameless.py:14` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | hb_utils | `caffmob_draw/customize/adapters/frameless.py:14` → `caffmob_draw.hb_utils` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | library_common | `caffmob_draw/customize/library_io.py:16` → `caffmob_draw.library_common` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | product_libraries | `caffmob_draw/customize/adapters/frameless.py:173` → `caffmob_draw.product_libraries.frameless` | Dados/assinaturas e fluxo em code-analysis/customize |
| customize | selection | `caffmob_draw/customize/library_io.py:18` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/customize |
| geometry_free | data | `caffmob_draw/geometry_free/ops_create.py:16` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/geometry_free |
| geometry_free | hb_snap | `caffmob_draw/geometry_free/ops_create.py:17` → `caffmob_draw.hb_snap` | Dados/assinaturas e fluxo em code-analysis/geometry_free |
| geometry_free | standards | `caffmob_draw/geometry_free/props.py:15` → `caffmob_draw.data.dimension_schema` (arquivo da unit standards) | Limites e padrões dimensionais da geometria _(Revisão cruzada 2026-10-10: `data/dimension_schema.py` pertence a standards na code-spec-matrix; aparecia só como `data`)_ |
| inspection | aggregates | `caffmob_draw/inspection/adapters/aggregate_leaf.py:15` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | compat | `caffmob_draw/inspection/adapters/frameless.py:15` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | cutting | `caffmob_draw/inspection/adapters/face_frame.py:107` → `caffmob_draw.cutting` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | data | `caffmob_draw/inspection/fronts.py:13` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | hb_types | `caffmob_draw/inspection/room_door_leaf.py:14` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | operators | `caffmob_draw/inspection/ops_inspect.py:109` → `caffmob_draw.operators.viewport_hud` | Dados/assinaturas e fluxo em code-analysis/inspection |
| inspection | product_libraries | `caffmob_draw/inspection/ops_inspect.py:115` → `caffmob_draw.product_libraries.closets` | Dados/assinaturas e fluxo em code-analysis/inspection |
| legacy | aggregates | `caffmob_draw/legacy/convert.py:135` → `caffmob_draw.aggregates.ops_aggregate` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | customize | `caffmob_draw/legacy/convert.py:51` → `caffmob_draw.customize` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | data | `caffmob_draw/legacy/convert_core.py:14` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | library_panel | `caffmob_draw/legacy/ops.py:96` → `caffmob_draw.library_panel` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | operators | `caffmob_draw/legacy/convert.py:108` → `caffmob_draw.operators.cabinet_builder` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | product_libraries | `caffmob_draw/legacy/groups.py:32` → `caffmob_draw.product_libraries.frameless.operators` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | selection | `caffmob_draw/legacy/gate.py:28` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | standards | `caffmob_draw/legacy/convert.py:109` → `caffmob_draw.standards` | Dados/assinaturas e fluxo em code-analysis/legacy |
| legacy | ui | `caffmob_draw/legacy/ops.py:26` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/legacy |
| library_panel | customize | `caffmob_draw/library_panel/categories.py:11` → `caffmob_draw.customize` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | data | `caffmob_draw/library_panel/categories_core.py:11` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | hb_gpu_draw | `caffmob_draw/library_panel/draw.py:13` → `caffmob_draw.hb_gpu_draw` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | legacy | `caffmob_draw/library_panel/draw.py:49` → `caffmob_draw.legacy` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | operators | `caffmob_draw/library_panel/draw.py:37` → `caffmob_draw.operators` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | standards | `caffmob_draw/library_panel/ops_cabinet.py:42` → `caffmob_draw.standards` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| library_panel | units | `caffmob_draw/library_panel/ops_cabinet.py:60` → `caffmob_draw.units` | Dados/assinaturas e fluxo em code-analysis/library_panel |
| measure | data | `caffmob_draw/measure/cotas.py:11` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/measure |
| measure | hb_placement | `caffmob_draw/measure/scene_cotas.py:93` → `caffmob_draw.hb_placement` | Dados/assinaturas e fluxo em code-analysis/measure |
| measure | hb_project | `caffmob_draw/measure/scene_cotas.py:56` → `caffmob_draw.hb_project` | Dados/assinaturas e fluxo em code-analysis/measure |
| measure | hb_types | `caffmob_draw/measure/scene_cotas.py:15` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/measure |
| measure | selection | `caffmob_draw/measure/scene_cotas.py:16` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/measure |
| molding | data | `caffmob_draw/molding/ops.py:12` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/molding |
| molding | hb_project | `caffmob_draw/molding/adapters.py:147` → `caffmob_draw.hb_project` | Dados/assinaturas e fluxo em code-analysis/molding |
| molding | hb_types | `caffmob_draw/molding/adapters.py:12` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/molding |
| molding | product_libraries | `caffmob_draw/molding/adapters.py:137` → `caffmob_draw.product_libraries.face_frame` | Dados/assinaturas e fluxo em code-analysis/molding |
| molding | units | `caffmob_draw/molding/engine.py:28` → `caffmob_draw.units` | Dados/assinaturas e fluxo em code-analysis/molding |
| move_over | aggregates | `caffmob_draw/move_over/scene.py:15` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | canvas2d | `caffmob_draw/move_over/align.py:96` → `caffmob_draw.canvas2d.view` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | customize | `caffmob_draw/move_over/ops_substitute.py:12` → `caffmob_draw.customize` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | data | `caffmob_draw/move_over/scene.py:16` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | hb_gpu_draw | `caffmob_draw/move_over/ops_dialog.py:26` → `caffmob_draw.hb_gpu_draw` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | hb_placement | `caffmob_draw/move_over/ops_move_on_wall.py:82` → `caffmob_draw.hb_placement` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | measure | `caffmob_draw/move_over/ops_move_on_wall.py:17` → `caffmob_draw.measure` | Dados/assinaturas e fluxo em code-analysis/move_over |
| move_over | selection | `caffmob_draw/move_over/scene.py:17` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/move_over |
| object_library | aggregates | `caffmob_draw/object_library/item_io.py:18` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/object_library |
| object_library | customize | `caffmob_draw/object_library/item_io.py:37` → `caffmob_draw.customize` | Dados/assinaturas e fluxo em code-analysis/object_library |
| object_library | data | `caffmob_draw/object_library/catalog.py:12` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/object_library |
| object_library | library_common | `caffmob_draw/object_library/item_io.py:20` → `caffmob_draw.library_common` | Dados/assinaturas e fluxo em code-analysis/object_library |
| openings | aggregates | `caffmob_draw/openings/sync.py:21` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | data | `caffmob_draw/openings/region_core.py:15` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | hb_placement | `caffmob_draw/openings/region.py:24` → `caffmob_draw.hb_placement` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | hb_snap | `caffmob_draw/openings/region.py:24` → `caffmob_draw.hb_snap` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | hb_types | `caffmob_draw/openings/sync.py:20` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | inspection | `caffmob_draw/openings/sync.py:22` → `caffmob_draw.inspection` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | ui | `caffmob_draw/openings/__init__.py:12` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/openings |
| openings | units | `caffmob_draw/openings/region.py:24` → `caffmob_draw.units` | Dados/assinaturas e fluxo em code-analysis/openings |
| selection | aggregates | `caffmob_draw/selection/element_size.py:42` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | data | `caffmob_draw/selection/classify.py:15` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | hb_types | `caffmob_draw/selection/editing.py:15` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | hb_utils | `caffmob_draw/selection/editing.py:91` → `caffmob_draw.hb_utils` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | legacy | `caffmob_draw/selection/component_select.py:49` → `caffmob_draw.legacy` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | openings | `caffmob_draw/selection/element_size.py:36` → `caffmob_draw.openings` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | operators | `caffmob_draw/selection/editing.py:124` → `caffmob_draw.operators` | Dados/assinaturas e fluxo em code-analysis/selection |
| selection | standards | `caffmob_draw/selection/editing.py:89` → `caffmob_draw.standards` | Dados/assinaturas e fluxo em code-analysis/selection |
| standards | cabinet_editor | `caffmob_draw/standards/cabinet_defaults.py:15` → `caffmob_draw.cabinet_editor.structure` | Dados/assinaturas e fluxo em code-analysis/standards |
| standards | data | `caffmob_draw/standards/api.py:9` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/standards |
| standards | hb_project | `caffmob_draw/standards/api.py:26` → `caffmob_draw.hb_project` | Dados/assinaturas e fluxo em code-analysis/standards |
| standards | legacy | `caffmob_draw/standards/sync.py:92` → `caffmob_draw.legacy` | Dados/assinaturas e fluxo em code-analysis/standards |
| standards | product_libraries | `caffmob_draw/standards/sync.py:128` → `caffmob_draw.product_libraries.frameless.operators` | Dados/assinaturas e fluxo em code-analysis/standards |
| standards | selection | `caffmob_draw/standards/migration.py:113` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/standards |
| stick | aggregates | `caffmob_draw/stick/frame.py:18` → `caffmob_draw.aggregates` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | collision | `caffmob_draw/stick/settle.py:99` → `caffmob_draw.collision` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | data | `caffmob_draw/stick/apply.py:19` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | hb_placement | `caffmob_draw/stick/settle.py:35` → `caffmob_draw.hb_placement` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | hb_types | `caffmob_draw/stick/migrate.py:21` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | selection | `caffmob_draw/stick/link.py:13` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/stick |
| stick | ui | `caffmob_draw/stick/apply.py:198` → `caffmob_draw.ui` | Dados/assinaturas e fluxo em code-analysis/stick |
| walls2d | canvas2d | `caffmob_draw/walls2d/ops_editor.py:28` → `caffmob_draw.canvas2d` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | compat | `caffmob_draw/walls2d/ops_editor.py:27` → `caffmob_draw.compat` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | data | `caffmob_draw/walls2d/model.py:17` → `caffmob_draw.data.i18n` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | hb_gpu_draw | `caffmob_draw/walls2d/ops_editor.py:227` → `caffmob_draw.hb_gpu_draw` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | hb_types | `caffmob_draw/walls2d/apply.py:21` → `caffmob_draw.hb_types` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | measure | `caffmob_draw/walls2d/ops_editor.py:498` → `caffmob_draw.measure` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | openings | `caffmob_draw/walls2d/apply.py:175` → `caffmob_draw.openings` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | operators | `caffmob_draw/walls2d/apply.py:23` → `caffmob_draw.operators` | Dados/assinaturas e fluxo em code-analysis/walls2d |
| walls2d | selection | `caffmob_draw/walls2d/scene_io.py:102` → `caffmob_draw.selection` | Dados/assinaturas e fluxo em code-analysis/walls2d |

### Consumidores sem unit da re-extração → units (impacto reverso)

_(Revisão cruzada 2026-10-10: grafo AST dos `from .`/`from ..` dos 175 arquivos fora das 18 units; o quadro acima só lista as 18 units como consumidoras. Alterar a unit à direita pode quebrar o consumidor à esquerda, que não tem spec própria — ver code-spec-matrix R4.)_

| Consumidor (pasta ou módulo) | Unit consumida | Imports | Primeira evidência |
|---|---|---:|---|
| __init__ | aggregates | 1 | `caffmob_draw/__init__.py:36` |
| __init__ | cabinet_editor | 1 | `caffmob_draw/__init__.py:40` |
| __init__ | collision | 1 | `caffmob_draw/__init__.py:39` |
| __init__ | customize | 1 | `caffmob_draw/__init__.py:35` |
| __init__ | geometry_free | 1 | `caffmob_draw/__init__.py:34` |
| __init__ | inspection | 1 | `caffmob_draw/__init__.py:31` |
| __init__ | legacy | 1 | `caffmob_draw/__init__.py:44` |
| __init__ | library_panel | 1 | `caffmob_draw/__init__.py:45` |
| __init__ | molding | 1 | `caffmob_draw/__init__.py:74` |
| __init__ | move_over | 1 | `caffmob_draw/__init__.py:32` |
| __init__ | object_library | 1 | `caffmob_draw/__init__.py:41` |
| __init__ | openings | 1 | `caffmob_draw/__init__.py:42` |
| __init__ | selection | 1 | `caffmob_draw/__init__.py:43` |
| __init__ | standards | 1 | `caffmob_draw/__init__.py:28` |
| __init__ | stick | 2 | `caffmob_draw/__init__.py:37` |
| __init__ | walls2d | 1 | `caffmob_draw/__init__.py:33` |
| cutting | aggregates | 1 | `caffmob_draw/cutting/part_sources.py:295` |
| cutting | cabinet_editor | 3 | `caffmob_draw/cutting/drilling.py:89` |
| cutting | customize | 1 | `caffmob_draw/cutting/drilling.py:91` |
| cutting | geometry_free | 1 | `caffmob_draw/cutting/part_sources.py:280` |
| cutting | inspection | 1 | `caffmob_draw/cutting/stale.py:46` |
| cutting | standards | 2 | `caffmob_draw/cutting/part_extractor.py:7` |
| data | customize | 1 | `caffmob_draw/data/properties.py:80` |
| data | standards | 1 | `caffmob_draw/data/i18n.py:46` |
| geometry | cabinet_editor | 1 | `caffmob_draw/geometry/mesh_gen.py:258` |
| geometry | walls2d | 1 | `caffmob_draw/geometry/floor_outline.py:13` |
| hb_props | molding | 9 | `caffmob_draw/hb_props.py:180` |
| hb_props | walls2d | 1 | `caffmob_draw/hb_props.py:83` |
| operators | aggregates | 1 | `caffmob_draw/operators/doors_windows.py:1396` |
| operators | legacy | 2 | `caffmob_draw/operators/viewport_hud.py:108` |
| operators | openings | 6 | `caffmob_draw/operators/doors_windows.py:193` |
| operators | selection | 2 | `caffmob_draw/operators/opening_builder.py:50` |
| operators | standards | 5 | `caffmob_draw/operators/cabinet_builder.py:19` |
| overlays | canvas2d | 1 | `caffmob_draw/overlays/element_toast.py:68` |
| overlays | measure | 2 | `caffmob_draw/overlays/selection_cotas.py:25` |
| overlays | selection | 3 | `caffmob_draw/overlays/draw_handlers.py:182` |
| product_libraries/closets | customize | 1 | `caffmob_draw/product_libraries/closets/types_closets.py:1935` |
| product_libraries/closets | inspection | 2 | `caffmob_draw/product_libraries/closets/operators/op_open_door_closet.py:12` |
| product_libraries/closets | standards | 1 | `caffmob_draw/product_libraries/closets/props_closets.py:99` |
| product_libraries/face_frame | customize | 1 | `caffmob_draw/product_libraries/face_frame/types_face_frame.py:8773` |
| product_libraries/face_frame | molding | 1 | `caffmob_draw/product_libraries/face_frame/props_hb_face_frame.py:7674` |
| product_libraries/frameless | customize | 3 | `caffmob_draw/product_libraries/frameless/operators/ops_opening.py:1094` |
| product_libraries/frameless | standards | 1 | `caffmob_draw/product_libraries/frameless/operators/ops_cabinet.py:70` |
| ui | aggregates | 2 | `caffmob_draw/ui/object_properties.py:391` |
| ui | cabinet_editor | 1 | `caffmob_draw/ui/sidebar_selected.py:37` |
| ui | collision | 2 | `caffmob_draw/ui/object_properties.py:392` |
| ui | customize | 3 | `caffmob_draw/ui/context_menu.py:28` |
| ui | inspection | 2 | `caffmob_draw/ui/context_menu.py:33` |
| ui | legacy | 9 | `caffmob_draw/ui/context_menu.py:41` |
| ui | measure | 2 | `caffmob_draw/ui/object_properties.py:23` |
| ui | object_library | 2 | `caffmob_draw/ui/sidebar_insert.py:39` |
| ui | openings | 1 | `caffmob_draw/ui/sidebar_build.py:74` |
| ui | selection | 12 | `caffmob_draw/ui/context_menu.py:10` |
| ui | standards | 3 | `caffmob_draw/ui/__init__.py:1` |
| ui | stick | 2 | `caffmob_draw/ui/context_menu.py:22` |

Dispatch por string não aparece no grafo e também liga units: `library_panel/ops_click.py:dispatch` → `caffmob.legacy_groups_convert` (legacy) e `caffmob.library_create_cabinet`/`library_category_create` (próprios); `legacy/ops.py` → `operators.ops_standards`; `ui/context_menu.py`/`ui/sidebar_vocab.py` (`draw_action` por chave do vocabulário) → operadores de `move_over`, `stick`, `cabinet_editor`, `collision`, `inspection` e `btm.resize_width` (`ui/ops_resize.py`, sobre `selection.resize`).

### Encadeamentos funcionais não representados integralmente por imports

| Alteração de origem | Consumidores a validar | Efeito |
|---|---|---|
| Schema dimensional / standards | builder, editor, customize, cutting | Unidades, limites, espessuras e montagem |
| Geometria de paredes | openings, move_over, measure, stick | Hospedeiro, cotas e planos de face |
| Reconstrução de módulo | customize, editor, aggregates, inspection | Reaplicação, filhos e redescoberta de frentes |
| Manifesto de biblioteca | library_panel, object_library/customize | Listagem, validação e inserção |
| Transformação de objeto | collision, cutting, stick | Stale, vínculos e extração |

🟡 O alcance de quebra deve ser validado por contrato e testes; a matriz histórica que equiparava dependência forte a refatoração completa era uma estimativa, não evidência direta.
