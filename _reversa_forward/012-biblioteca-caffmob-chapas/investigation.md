# Investigation: Biblioteca CAFFMob e armários por chapas no padrão global

> Identificador: `012-biblioteca-caffmob-chapas`
> Data: `2026-10-09`

## 1. O que já existe no código

| Tema | Onde | Achado |
|------|------|--------|
| Padrão ativo | `standards/model.py:126` (`Scene.btm_standards`), `standards/api.py:23` (`main_scene`) | Por projeto, na cena principal; definições BUILTIN, USER, PROMOB_IMPORT e MIGRATED |
| Esquema | `data/dimension_schema.py` (l. 24, 62-88, 139, 162-183, 211-234, 343) | Linhas COZ, DOR, BAN, SAL, ESC; componentes de chapa (C, L, ESP, MAT, FIT); medidas externas por linha. Só COZ (frameless) e DOR (closets) têm consumidor. `ALT_ARM` → `DOR.external.tall_height` |
| Promob | `standards/io_promob.py:65` | IDs não mapeados ficam crus e voltam na exportação; o fixture `dimensionexport_me_moveis.xml` (694 atributos) é idêntico ao anexo do titular |
| Aplicação | `standards/sync.py:84, 96, 160` | `affected_modules` conta só frameless e closets; `apply_definition` escreve as propriedades da cena e refaz os módulos, pulando `btm_overrides` sem `include_manual`; marca `cut_plan_stale` |
| Perguntas de hoje | `operators/ops_standards.py:110-243` | Configurador, Aplicar e Definir ativa: uma confirmação com a contagem e o interruptor "Incluir medidas manuais" |
| Montagem | `cabinet_editor/structure.py:85-97`; `cutting/part_sources.py:207-236`; `product_libraries/frameless/types_frameless.py:125-257`; `types_face_frame.py:1346-1383`; `types_closets.py` | Todas as bibliotecas fazem lateral passante. O módulo CAFFMob tem a regra em duas funções puras; o frameless, em drivers (`dim_x-(mt*2)`) com lateral recortada para o rodapé (`CabinetSideNotched`) |
| Módulo rápido | `operators/cabinet_builder.py:8-60` | 0,8 × 0,7 × 0,55 fixos; do padrão, só a espessura da lateral (COZ) |
| Editor (008) | `cabinet_editor/ops_editor.py:310`; `bridge.py:311` (`configured_part`); `scene_divisions.py:36-46` | Pede um módulo selecionado; lê espessura e material por linha (`btm_line`, ou COZ) |
| Biblioteca | `ui/sidebar_insert.py:13`; `props_hb_frameless.py:2388` (`draw_library_ui`); `ui/my_modules.py`; `customize/library_io.py:21-44` | Galeria com miniaturas por biblioteca; módulos do usuário em `modules/<categoria>/`, categoria = pasta |
| Topo da viewport | `operators/viewport_hud.py:547-829`; `operators/scene_navigator.py:192-452` | Desenho `POST_PIXEL` + keymap de clique e hover com `PASS_THROUGH`; painel fixável do navegador como modelo de coluna |

## 1a. Medição da sessão 3 (só CAFFMob)

| Tema | Onde | Achado |
|------|------|--------|
| Painéis herdados | `ui/view3d_sidebar.py:1392` (`PANELS` só pelo proxy), `ui/panels.py:384` (`classes = ()`), `ui_face_frame.py:1698` (`classes = ()`), `catalog/` (não importado) | A maioria dos painéis herdados já não é registrada; os pontos vivos são poucos (roadmap, nota D-02) |
| HUD | `operators/viewport_hud.py:97-104, 356-464` | Modos e "Grab" herdados; Abrir portas, Mover Sobre e Seleção por componente dependem das fiações herdadas para aparecer |
| Keymaps herdados | `face_frame/dim_edit_overlay.py:875`, `closets/operators/op_grab_closet.py:882`, `closets/gpu_overlay_closets.py:972` | Já exigem `product_tab` FACE FRAME ou CLOSET |
| Leitores para a conversão | `customize/adapters/{frameless,face_frame,closets}.py` (`read` → `spec.Spec`), `selection/editing.get_dimension`, `inspection/fronts.fronts_of` | Medidas, aberturas com `front`, `drawer_count`, prateleiras |
| Módulo CAFFMob | `data/properties.py:288`; `customize/adapters/btm.py:15-17, 51-55`; `cabinet_editor/panels_drawers.py:31-34` | `cabinet_type` BASE/WALL/TALL; uma frente (NONE, LEFT, RIGHT, DOUBLE, FLIP); prateleiras; **sem gavetas** |
| Detecção de herdados | `selection/classify.py:32, 62` (`MODULE_TAGS`, `module_library`) | A mais completa; `cutting/part_sources.iter_modules` e `standards/sync.affected_modules` não veem face frame |
| Testes | 17 fumaças criam armários herdados por código; `blender_005_sidebar_inventory.py` compara com a linha de base | As fumaças seguem válidas (código registrado); o inventário precisa declarar os operadores aposentados |

## 2. API do Blender 5.2 consultada

- `bpy.types.WindowManager.popover(draw_func, *, ui_units_x=0, keymap=None, from_active_button=False)`:
  `docs/rag/blender-api/corpus/bpy.types.WindowManager.md#bpy.types.WindowManager.popover`. Usado no D-03.
- `bpy.types.WindowManager.invoke_popup(operator, *, width=300)`: plano B do D-03.
- `bpy.ops.wm.call_panel(*, name='', keep_open=True)`: descartado (exige `Panel` registrado numa região).
- `SpaceView3D.draw_handler_add` `POST_PIXEL` e `KeyMapItems.new(..., head=True)`: padrão já usado no HUD
  (`docs/rag/project/02_padroes_blender_5_2.md`, modal + GPU).

## 3. Alternativas avaliadas

| Tema | Alternativa | Veredito |
|------|-------------|----------|
| Onde fica o painel | Widget dentro do HUD | Descartada: o HUD depende de `use_viewport_hud`, e o titular quer o painel sempre (Q4) |
| | Cabeçalho da viewport (`VIEW3D_HT`) | Descartada: não é flutuante e disputa espaço com o menu do Blender |
| | Desenho próprio + keymap de clique | **Escolhida** (D-01) |
| Conteúdo da categoria | Galeria desenhada em GPU | Descartada: texturas de miniatura, rolagem e clique por célula; muito código novo para o que o Blender já faz |
| | Popover nativo com `draw_library_ui` | **Escolhida** (D-03, princípio VI) |
| Montagem base passante | Nos drivers do frameless | Desnecessária: o titular tirou as bibliotecas herdadas (sessão 3) |
| | No módulo CAFFMob (`structure.layout`, `synthetic_records`) | **Escolhida** (D-09) |
| Bibliotecas herdadas | Apagar o código agora | Descartada pelo titular (Q3 da sessão 3): ~35 arquivos dependem delas |
| | Porta única na interface (`legacy/gate.py`) | **Escolhida** (D-01) |
| Conversão | Ler prompts e drivers de cada biblioteca | Descartada: os adaptadores da personalização já leem as três (D-23) |
| | Estender o módulo CAFFMob com gavetas nesta feature | Adiada para a 013 (sessão 4) |
| Grupos salvos herdados | Converter só ao inserir | Descartada: o grupo some da interface e o usuário não o acharia |
| | Converter em lote para a biblioteca do usuário (`library_io.save`) | **Escolhida** (D-29), oferta única (D-30) |
| Prova do Ctrl+Z da conversão | `ed.undo` em segundo plano | Descartada (cross-check A004): com janela e eventos simulados (D-31) |
| Valor de `product_tab` com a porta fechada | Item novo "NONE" no enum | Descartada: mudaria o enum guardado nos arquivos antigos; fica FRAMELESS, o valor de fábrica (D-04) |
| Duas perguntas | Um diálogo com dois interruptores | Descartada: o titular pediu duas perguntas em sequência |
| Montagem no padrão | Número 0/1 no esquema em mm | Descartada: o esquema é numérico e exportado para o Promob; enumeração própria (D-08) + atributo cru (D-14) |

## 4. Padrões do projeto aplicados

- Núcleos puros com testes fora do Blender (`tests/test_*.py`, `_bootstrap.py`), como `structure`, `classify` e
  `region_core`.
- Fumaças por incremento (`tests/blender_012_*`), e prova com eventos simulados para clique e popover
  (`--enable-event-simulate`, padrão da `blender_011_drag_probe.py`).
- Arquivos do usuário em `bpy.utils.extension_path_user(__package__, path=..., create=True)` (`CLAUDE.md`).
- Princípios I a XI (`.reversa/principles.md`).
