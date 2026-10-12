# Molduras de ambiente por pacote (molding) — Tarefas de Implementação

🟢 **CONFIRMADO** — sequência para reimplementar `caffmob_draw/molding/` a partir do código de 2026-10-10. IDs RN/RF/CA de `requirements.md`; algoritmos A-xx e fluxos F-xx de `design.md`; casos EC-xx de `edge-cases.md`. As tarefas de evolução (motor único, closets, desatualizado, preset BR) seguem em `_reversa_sdd/catalog_molding/tasks.md` (T-02, T-07, T-09) e não são repetidas aqui.

## Pré-requisitos

- [ ] 🟢 `units.inch` (`data/units.py:inch`, `v · 0,0254`).
- [ ] 🟢 `hb_types.GeoNodeObject(obj).get_input(nome)` para `Dim X/Y/Z` e `Width`.
- [ ] 🟢 Bibliotecas face frame (`Object.face_frame_cabinet`, `props_hb_face_frame.get_style_props`, `cabinet_styles[].get_finish_material()`) e frameless (`Scene.hb_frameless.cabinet_styles`, idprops do cage) carregadas; `hb_project.get_main_scene()`.
- [ ] 🟢 `data.i18n.tr` e catálogo `data/translations/molding.json` (17 chaves).
- [ ] 🟢 `hb_props.Home_Builder_Scene_Props` com as 14 propriedades `molding_*` e `update_molding_package` (fora desta unit; ver `design.md` › Propriedades da sala).
- [ ] 🟢 Sem banco de dados, rede ou variáveis de ambiente; packs de perfis são opcionais.

## Tarefas

- [ ] T-01, Criar `packages.py`: registro de packs (`register_profile_path`, `unregister_profile_path`, `profile_paths`), caches, `profile_enum_items`, pacotes `CROWN/BASE/LIGHT_RAIL`, `FURNITURE_CAP_STACK`, `BASE_SHOE_*`, `PACKAGES`, `package_stack`, `stack_has_adjustable_offset`, `stack_uses_category`, `_ENUM_CACHE`/`enum_items` (RN-13, RN-14, RN-15)
  - Origem no legado: `caffmob_draw/molding/packages.py:1-172`
  - Critério de pronto: `enum_items('CROWN')` = `NONE, SIMPLE, STACKED, SPACER`; `stack_has_adjustable_offset('CROWN','STACKED')` verdadeiro e `'SIMPLE'` falso; `stack_uses_category('CROWN','STACKED','Spacer')` verdadeiro; `profile_enum_items` sem packs = só `DEFAULT`
  - Confiança: 🟢

- [ ] T-02, Contornos embutidos e perfis: `_PROFILE_OUTLINES` (6 chaves, polegadas), `_finish_profile` (ordem `dimensions='2D'` → `bevel_depth=0` → `fill_mode='NONE'`), `_load_library_profile`, `_curve_metrics`, `_profile_metrics` (cache por ref), `profile_top_height`, `profile_front_depth`, `make_profile_object` (RN-16)
  - Origem no legado: `caffmob_draw/molding/packages.py:175-347`
  - Critério de pronto: sem pack, métricas = tabela de `design.md` (crown 3"/0,875", flat 3,5"/0,75", cap 1"/1,125", base 3"/0,625", shoe 0,75"/0,4375", light rail 0"/0,75"); perfil embutido é curva POLY cíclica oculta com `IS_HB_MOLDING_PROFILE`; CA-12, CA-13
  - Confiança: 🟢

- [ ] T-03, `engine.py` — medidas e agrupamento: `cage_dims` (fallback `obj.dimensions`), `footprint_xy`, `top_z`, `bottom_z`, `front_normal_xy`, `members_touch` (0,02 m), `connected_components`, `order_chain` (RN-03, RN-04)
  - Origem no legado: `caffmob_draw/molding/engine.py:29-152`
  - Critério de pronto: CA-02 (topos a 0,025 m → 2 componentes); T de 4 membros produz cadeia com o ramo sobrante no fim (EC-06)
  - Confiança: 🟢

- [ ] T-04, `engine.py` — offsets: `offset_polyline_right` (A-01) e `offset_polygon_right` (A-02), tolerâncias 1e-6 / 1e-9, sem limite de mitra
  - Origem no legado: `caffmob_draw/molding/engine.py:155-226`
  - Critério de pronto: CA-16 e as sondas de A-01/A-02 e EC-05 reproduzidas
  - Confiança: 🟢

- [ ] T-05, `engine.py` — percurso frontal: `corner_plan_data` (24" padrão), `_assemble_front_raw` (A-03), `chain_sweep_points` (A-04) com normalização de sentido e retornos em pontas acabadas (RN-05, RN-06)
  - Origem no legado: `caffmob_draw/molding/engine.py:229-392`
  - Critério de pronto: CA-01 (retorno só na ponta acabada), CA-10 (canto notch com 3 pontos de frente, diagonal com 2)
  - Confiança: 🟢

- [ ] T-06, `engine.py` — rodapé: `_kick_spans_local`, `_assemble_kick_spans` (A-06), `_stretch_segments` (A-07), `_island_perimeter_spans` (A-08), `kick_sweep_segments` (A-05) (RN-08, RN-09, RN-10)
  - Origem no legado: `caffmob_draw/molding/engine.py:395-736`
  - Critério de pronto: CA-04, CA-05 (com e sem `include_recessed`), CA-11 (laço cíclico costas com costas); ilha parentada vira corrida (EC-14)
  - Confiança: 🟢

- [ ] T-07, `adapters.py`: tipos por moldura, `collect_targets`, `collect_bridges` (Z ≤ 0,02), `_RECESSED_FF_KICKS`, `_top_rail_width`, `_wall_bounds`/`_near_wall`/`_frameless_end_finished` (0,03 / 0,05), `finish_material`, `build_facts` (RN-01, RN-02, RN-07, RN-08, RN-17)
  - Origem no legado: `caffmob_draw/molding/adapters.py`
  - Critério de pronto: CA-06 (módulos CAFFMob/closets ignorados); refrigerador FF vira `SKIP`; frameless a 4 cm da parede = não acabado (EC-13); `crown_mount` só no FF com TOP_RAIL
  - Confiança: 🟢

- [ ] T-08, `ops.py` — limpeza, pilha e cotas: tags, `_TYPES`, `clear_scene_molding` (F-02), `_resolve_stack` (F-05), `_crown_datum`, `_crown_stack_top`, `_sweep_z`, `_base_stack` (RN-11 a RN-14)
  - Origem no legado: `caffmob_draw/molding/ops.py:15-124,227-244`
  - Critério de pronto: CA-03 (crown empilhada com dx 0,01905 e dy = stack offset), CA-08 (capa em altura + 0,0762), CA-09 (shoe dx 0 sem pacote e 0,015875 com pacote)
  - Confiança: 🟢

- [ ] T-09, `ops.py` — criação e orquestração: `_spawn_sweep` (F-04, deduplicação 1e-4, mínimo 2/3 pontos, material), `_apply_type` (F-03), `apply_scene_packages` (F-01), `on_package_changed` (RN-18, RN-19)
  - Origem no legado: `caffmob_draw/molding/ops.py:127-308`
  - Critério de pronto: CA-01, CA-07, CA-14 (idempotência), CA-15 (cena de layout intocada); callback com erro só imprime `CAFFMob Draw molding: apply failed: …`
  - Confiança: 🟢

- [ ] T-10, Operador `home_builder_OT_refresh_room_molding` (`caffmob.refresh_room_molding`, `{'UNDO'}`, relatório traduzido) e `register`/`unregister` tolerantes a reregistro; `__init__.py` delegando a `ops` (RF-08)
  - Origem no legado: `caffmob_draw/molding/ops.py:311-349`; `caffmob_draw/molding/__init__.py`
  - Critério de pronto: recarregar a extensão duas vezes não falha; o botão reporta "Rebuilt N molding run(s)" com N = nº de sweeps; Ctrl+Z desfaz a reconstrução feita pelo botão
  - Confiança: 🟢 (código) / 🟡 (desfazer não verificado no Blender)

- [ ] T-11, Ligar a unit ao pacote: `from . import molding` e `molding.register()` após as bibliotecas herdadas; `molding.unregister()` no desligamento; callbacks de itens e `update` em `hb_props.py`; UI `draw_molding_ui` no face frame (F-06)
  - Origem no legado: `caffmob_draw/__init__.py:74,321,347`; `caffmob_draw/hb_props.py:177-221,509-599`; `caffmob_draw/product_libraries/face_frame/props_hb_face_frame.py:draw_molding_ui`
  - Critério de pronto: com a porta legado aberta, a aba OPTIONS › Molding do face frame mostra as 3 caixas e o botão; campos dependentes habilitam conforme F-06
  - Confiança: 🟢 / 🟡 (caminhos de UI fora da barra principal)

## Tarefas de Teste

- [ ] TT-01, Testes puros de `offset_polyline_right`/`offset_polygon_right` com um `Vector` mínimo injetado como `mathutils` (CA-16, EC-05) — 🟢 viável hoje via extração por AST, como na sonda desta extração _(Revisão 2026-10-10: os mesmos valores foram reproduzidos com `mathutils.Vector` real no Blender 5.2)_
- [ ] TT-02, Testes puros de `_resolve_stack`, `_crown_datum`, `_sweep_z` e `_base_stack` com métricas dos contornos embutidos (CA-03, CA-08, CA-09) — 🟡 exigem isolar `packages` de `bpy`
- [ ] TT-03, Smoke Blender: corrida de 3 aéreos FF, canto em L, rodapé com eletrodoméstico e recuo, ilha costas com costas; conferir nº de sweeps, splines, `use_cyclic_u` e Z (CA-01, CA-04, CA-05, CA-10, CA-11) — 🟡 decisão: testar (DT-01, questions.md#pergunta-64); inexistente
- [ ] TT-04, Smoke Blender de idempotência e órfãos: aplicar 10× e contar objetos e curvas órfãs (CA-14, EC-03, EC-12) — 🔴 inexistente
- [ ] TT-05, Smoke Blender com pack falso contendo curva e malha (CA-12, EC-04) — 🔴 inexistente

## Ordem Sugerida

1. T-01, T-02 (catálogo de perfis sem dependência de geometria).
2. T-03, T-04 (base geométrica), TT-01.
3. T-05, T-06 (percursos), T-07 (fatos).
4. T-08, T-09, T-10, TT-02.
5. T-11 e smokes TT-03 a TT-05.

## Lacunas Pendentes (🔴)

- 🟡 decisão: testar (DT-01) — **Decisão do titular (2026-10-10, questions.md#pergunta-64):** rodar um smoke visual no Blender 5.2 com 3 aéreos face frame, um canto em L e uma ilha (TT-03) e conferir por captura de tela o lado do perfil no bevel, retornos e meias-esquadrias; expectativa: lado correto (direita do percurso = fora), salvo EC-07/EC-08.
- 🟡 decisão: testar (DT-01, questions.md#pergunta-64) Pai com escala/inclinação (EC-08) e cadeias só de cantos (EC-07) sem validação visual.
- 🔴 Perfil de pack não-curva (EC-04) e cadeias ramificadas (EC-06) sem validação visual.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-95):** aceita a reconstrução a cada passo do arraste enquanto as linhas herdadas estão atrás da porta legado (ADR 0006); se o uso crescer, agendar a reconstrução com `bpy.app.timers` (ex. 0,2 s) cancelando a anterior (EC-17).
- 🔴 Nenhum teste automatizado da unit.

## Tarefas por decisão do titular (2026-10-10)

- [ ] DT-01 Rodar no Blender 5.2 o smoke visual TT-03 (3 aéreos face frame, canto em L, ilha), incluindo corrida só de cantos (EC-07) e pai com escala/inclinação (EC-08), e conferir por captura de tela o lado do perfil no bevel, os retornos nas pontas e as meias-esquadrias (decisão questions.md#pergunta-64)
