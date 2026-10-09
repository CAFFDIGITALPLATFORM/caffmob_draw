# Actions: Biblioteca CAFFMob flutuante, só armários CAFFMob e chapas no padrão global

> Identificador: `012-biblioteca-caffmob-chapas`
> Data: `2026-10-09` (versão 3, sobre o roadmap versão 3)
> Roadmap: `_reversa_forward/012-biblioteca-caffmob-chapas/roadmap.md` (D-01 a D-31, P3 a P6)
> Data delta: `_reversa_forward/012-biblioteca-caffmob-chapas/data-delta.md`
> Interfaces: `interfaces/promob-dimensionexport.md`
> IDs: a versão 1 tinha T001 a T043, nenhum executado. Os que continuam valendo mantêm o número (alguns com a
> descrição ajustada); os que deixaram de valer estão em "Removidas"; os novos começam em T044 (IDs não são
> reciclados).
> Incrementos (roadmap §1):
> - I1 só CAFFMob na interface: T044, T048 a T056, T064
> - I2 armário CAFFMob pelo padrão: T001, T002, T005, T010 a T012, T017, T018, T026, T028, T029, T036, T038
> - I3 Biblioteca CAFFMob: T003, T006, T008, T013, T015, T019 a T025, T027, T040, T042, T047, T057
> - I4 aplicar com duas perguntas: T004, T007, T014, T031 a T034, T039, T043
> - I5 converter arquivos antigos e grupos salvos: T046, T058 a T062, T065 a T069
> - I6 exportar: T009, T016
> - T037 (traduções), T063 (registro de `legacy/`) e T041 (regressão) atravessam todos
>
> P1 e P2 confirmadas pelo titular (sessão 4): 5 modelos sem gaveteiro, gavetas na feature 013, gavetas como perda na
> conversão. O `requirements.md` já diz 5 modelos.
>
> Caminhos relativos à raiz do repositório.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 67 ativas (41 da versão 1 + 26 novas, T044 e T046 a T070; T030 e T035 removidas; T045 não usado) |
| Paralelizáveis (`[//]`) | 53 |
| Maior cadeia de dependência | 9 (T008 → T015 → T020 → T021 → T022 → T023 → T024 → T037 → T041) |
| Ordem de entrega | I1 → I2 → I3 → I4 → I5 → I6; provas T023 (popover) e T032 (dois diálogos) no começo do I3 e do I4; T070 prova o Ctrl+Z da conversão |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T044 | Preferência `show_legacy_libraries` (falso por padrão) no grupo "Avançado" de `BTM_AddonPreferences` (D-01) | - | `[//]` | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T001 | `assembly` (LATERAL/BASE, padrão LATERAL) em `BTM_PG_StandardDefinition`, com `api.active_assembly(scene)` (D-10) | - | `[//]` | `caffmob_draw/standards/model.py` | 🟡 | `[X]` |
| T002 | `assembly` (LATERAL/BASE) e `line` (COZ, DOR, BAN, SAL, ESC) em `BTM_PG_CabinetProperties`; o tipo continua em `cabinet_type` (D-08, D-10) | - | `[//]` | `caffmob_draw/data/properties.py` | 🟢 | `[X]` |
| T003 | `BTM_PG_LibraryState` (`open`, `category`, `line`) em `WindowManager.btm_library`, com `register`/`unregister` | - | `[//]` | `caffmob_draw/library_panel/props.py` | 🟢 | `[X]` |
| T004 | Migração M-03 no `load_post` (data-delta §5): `btm_standard_uid` nas raízes de módulo; `line` e `assembly` nos módulos CAFFMob antigos | T001, T002 | - | `caffmob_draw/standards/migration.py` | 🟡 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Testes da montagem: `layout` em LATERAL igual ao de hoje; em BASE, base de largura inteira, laterais de `t[BOTTOM]` à altura, tampo entre as laterais; com remoção de chapa; `synthetic_records` de um balcão de 800 mm com chapa de 18: base 764 / lateral altura toda (LATERAL), base 800 / lateral altura − 18 (BASE) | - | `[//]` | `tests/test_structure_assembly.py` | 🟢 | `[X]` |
| T006 | Testes das categorias: ordem (fixas e depois as do usuário); nome vazio, repetido (sem diferenciar maiúsculas), igual a uma fixa ou com `/` recusado com motivo; JSON inválido ou linha desconhecida → COZ com aviso; pastas sem entrada viram categoria COZ | - | `[//]` | `tests/test_library_categories.py` | 🟡 | `[X]` |
| T007 | Testes da decisão de aplicar (D-20): módulo CAFFMob que segue, que difere (overrides, montagem, espessura por papel, uid de outro padrão) e não aplicável (herdado não convertido, importado, objeto da biblioteca); respostas Não, Sim + Não, Sim + Sim | - | `[//]` | `tests/test_standards_apply_core.py` | 🟢 | `[X]` |
| T008 | Testes do layout do painel: rótulo fechado no canto superior esquerdo (com e sem o HUD), coluna aberta na ordem da RN-02, acerto de clique por item, fora do painel = nada, escala da interface | - | `[//]` | `tests/test_library_layout.py` | 🟡 | `[X]` |
| T009 | Testes do Promob: ler o fixture dá LATERAL e mantém os 692 atributos crus; exportar acrescenta só `CAFF_MONTAGEM`; ler BASE; valor desconhecido → LATERAL com aviso | - | `[//]` | `tests/test_promob_assembly.py` | 🟢 | `[X]` |
| T010 | Testes das medidas pelo padrão: por linha e `cabinet_type` (BASE, WALL, TALL), altura, profundidade, Z de instalação do aéreo e espessura por papel, lidas do fixture; padrão sem a linha → fallback nomeado com aviso | - | `[//]` | `tests/test_cabinet_defaults.py` | 🟡 | `[X]` |
| T046 | Testes da tradução para CAFFMob (D-24): tipos (BASE, UPPER → WALL, TALL, LAP_DRAWER, PANEL, HANGING, ISLAND), frentes (porta esquerda, direita, dupla, basculante, aberto), várias aberturas (a maior manda), gavetas e frentes especiais como perda com quantidade, prateleiras somadas, linha (btm_line, DOR para closets, COZ) | - | `[//]` | `tests/test_legacy_convert.py` | 🟡 | `[X]` |
| T047 | Testes do catálogo de modelos prontos: lê `library_models.json`, valida `cabinet_type` e `door_swing`, largura 0 = do padrão, item inválido é pulado com aviso | - | `[//]` | `tests/test_library_models.py` | 🟡 | `[X]` |
| T065 | Testes dos grupos antigos: lista de pendentes (arquivos em `cabinet_groups/` menos os convertidos), leitura e gravação do marcador `legacy_groups.json`, marcador inválido = oferta de novo, nome de destino sem colidir com módulo existente (sufixo " (2)") (D-29, D-30) | - | `[//]` | `tests/test_legacy_groups.py` | 🟡 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T048 | `legacy/gate.py`: `LEGACY_LIBRARIES`, `legacy_ui(context)` (lê `show_legacy_libraries`), `is_legacy(obj)` por `classify.module_library` e `legacy_roots(scene)` (D-01, D-23) | T044 | `[//]` | `caffmob_draw/legacy/gate.py` | 🟢 | `[X]` |
| T011 | `structure.layout(..., assembly='LATERAL')`: em BASE, base de −w/2 a w/2 e laterais de `t[BOTTOM]` à altura; vão interno e fundo acompanham (D-09) | T005 | `[//]` | `caffmob_draw/cabinet_editor/structure.py` | 🟢 | `[X]` |
| T012 | `part_sources.synthetic_records` pela montagem do módulo (`btm_cabinet.assembly`) (D-09) | T005 | `[//]` | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T013 | `categories_core`: categorias fixas (Cozinha → COZ, Banheiro → BAN, Sala → SAL, Home office → ESC), validação de nome, leitura e montagem do JSON (D-17) | T006 | `[//]` | `caffmob_draw/library_panel/categories_core.py` | 🟡 | `[X]` |
| T014 | `standards/apply_core.plan(modules, previous_uid)` → `(segue, difere, nao_aplicavel)` e `targets(plan, answer1, answer2)` (D-20) | T007 | `[//]` | `caffmob_draw/standards/apply_core.py` | 🟢 | `[X]` |
| T015 | `layout_core`: retângulos do rótulo e da coluna, acerto de clique, âncora com e sem o HUD, item opcional "Converter grupos antigos" no topo da coluna (D-14, D-30) | T008 | `[//]` | `caffmob_draw/library_panel/layout_core.py` | 🟡 | `[X]` |
| T016 | `io_promob`: grava `CAFF_MONTAGEM` no fim e o lê fora de `raw_attributes`; valor inválido avisa (D-27) | T009, T001 | `[//]` | `caffmob_draw/standards/io_promob.py` | 🟡 | `[X]` |
| T017 | `standards/cabinet_defaults.py`: `defaults(values, line, cabinet_type)` → largura, altura, profundidade, Z de instalação, espessura por papel; fallback nomeado (D-07) | T010 | `[//]` | `caffmob_draw/standards/cabinet_defaults.py` | 🟡 | `[X]` |
| T057 | `data/library_models.json` (5 modelos, data-delta §3a) e `library_panel/models_core.py` para ler e validar (D-16, P1) | T047 | `[//]` | `caffmob_draw/library_panel/models_core.py` | 🟡 | `[X]` |
| T058 | `legacy/convert_core.translate(spec, line)` → `(campos do btm_cabinet, perdas)` (D-24, P2) | T046 | `[//]` | `caffmob_draw/legacy/convert_core.py` | 🟡 | `[X]` |
| T066 | `legacy/groups_core.py` puro: pendentes, marcador e nome de destino (D-29, D-30) | T065 | `[//]` | `caffmob_draw/legacy/groups_core.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T049 | Inserir e Meus módulos pela porta: sem `product_tab` e galerias herdadas (`sidebar_insert.py`, l. 20-29), sem as origens FRAMELESS e FACE_FRAME (`my_modules.py`) nem os itens do filtro (`sidebar_props.py`); Inserir mostra "Biblioteca no topo da viewport" (D-02 itens 1 e 2, D-19) | T048 | `[//]` | `caffmob_draw/ui/sidebar_insert.py` | 🟢 | `[X]` |
| T050 | `HOME_BUILDER_PT_hidden_header`: as três caixas de modo de seleção pela porta; fica o interruptor da 011 (D-02 item 3) | T048 | `[//]` | `caffmob_draw/ui/view3d_sidebar.py` | 🟢 | `[X]` |
| T051 | Menu de contexto sem o submenu `MENU_ID` de armário herdado e menu da parede sem a "linha de encaixe" do frameless, pela porta (D-02 itens 4 e 6) | T048 | `[//]` | `caffmob_draw/ui/context_menu.py` | 🟢 | `[X]` |
| T052 | HUD: `room_ui_visible(context)` para Abrir portas, Mover Sobre e Seleção por componente; `_MODE_BUTTONS` e `_GRAB_*` pela porta (D-03) | T048 | `[//]` | `caffmob_draw/operators/viewport_hud.py` | 🟢 | `[X]` |
| T053 | `component_select.cabinet_modes`: com a porta fechada, devolve `{}` (todo módulo sobe) (D-05) | T048 | `[//]` | `caffmob_draw/selection/component_select.py` | 🟢 | `[X]` |
| T054 | `legacy/__init__.py`: `register`/`unregister` e `load_post` `@persistent` que põe `product_tab = 'FRAMELESS'` com a porta fechada (D-04) | T048 | `[//]` | `caffmob_draw/legacy/__init__.py` | 🟡 | `[X]` |
| T018 | `generate_cabinet_mesh` repassa `btm_cabinet.assembly` para `structure.layout` (D-09) | T011, T002 | `[//]` | `caffmob_draw/geometry/mesh_gen.py` | 🟢 | `[X]` |
| T019 | `categories.py`: lê e grava `categories.json` em `extension_path_user(pkg, "modules")` com escrita atômica, cria a pasta da categoria e migra as pastas soltas (D-17) | T013 | `[//]` | `caffmob_draw/library_panel/categories.py` | 🟡 | `[X]` |
| T020 | Desenho `POST_PIXEL` do painel, sempre registrado: rótulo, coluna, hover; sai cedo fora da `VIEW_3D`; layout em cache por região (D-13, D-14) | T003, T015 | `[//]` | `caffmob_draw/library_panel/draw.py` | 🟢 | `[X]` |
| T021 | `caffmob.library_click` e `caffmob.library_hover` em "3D View" `head=True`, com poll só sobre o painel; Esc e clique fora fecham; o item clicado despacha, inclusive "Converter grupos antigos" (D-13, D-30) | T020 | - | `caffmob_draw/library_panel/ops_click.py` | 🟢 | `[X]` |
| T022 | Registro do pacote `library_panel` (props, desenho, operadores; `unregister` remove desenho e keymaps) | T003, T020, T021 | - | `caffmob_draw/library_panel/__init__.py` | 🟢 | `[X]` |
| T023 | Prova com eventos simulados: o painel aparece com o HUD desligado, abre com clique, e um item abre um popover de teste (`WindowManager.popover`) a partir do keymap; se falhar, registrar e usar o plano B (`invoke_popup`) no T024 (P5) | T022 | - | `tests/blender_012_library_ui.py` | 🟡 | `[X]` |
| T024 | Popover da categoria: os modelos prontos (`models_core`) e os módulos salvos na categoria (`ui/my_modules.py`, origem MODULES); inserir um modelo chama o `cabinet_builder` com a linha da categoria; grava categoria e linha em `btm_library` (D-15, D-16) | T019, T023, T057, T026 | `[//]` | `caffmob_draw/library_panel/popover.py` | 🟡 | `[X]` |
| T025 | "Criar categoria" (`caffmob.library_category_create`): diálogo com nome e linha, validação do `categories_core`, mensagem de recusa; "Trocar linha" da categoria do usuário; o mesmo diálogo leva a "Converter grupos antigos" (RN-03, RN-04, D-30) | T019, T022 | `[//]` | `caffmob_draw/library_panel/ops_categories.py` | 🟢 | `[X]` |
| T026 | `cabinet_builder`: `invoke` e `execute` preenchem largura, altura, profundidade, espessuras por papel, linha, `cabinet_type`, montagem e Z de instalação por `cabinet_defaults`; gravam `btm_standard_uid`; 0,8/0,7/0,55/0,018 viram fallback (D-11) | T002, T017 | `[//]` | `caffmob_draw/operators/cabinet_builder.py` | 🟢 | `[X]` |
| T027 | "Criar armário" (`caffmob.library_create_cabinet`): diálogo tipo, largura, montagem e linha preenchidos pelo padrão; confirmar cria pelo `cabinet_builder` e chama `caffmob.cabinet_editor('INVOKE_DEFAULT')`; cancelar não cria (D-18) | T026, T018, T022 | - | `caffmob_draw/library_panel/ops_cabinet.py` | 🟢 | `[X]` |
| T028 | Editor de armário (`bridge`): lê e grava a montagem, refaz malha e lista de corte; detecta "padrão próprio" (D-12) | T011, T002 | `[//]` | `caffmob_draw/cabinet_editor/bridge.py` | 🟡 | `[X]` |
| T029 | Aba Estrutura: campo **Montagem** e a marca "Padrão próprio" (RN-08, RN-09) | T028 | - | `caffmob_draw/cabinet_editor/panels_structure.py` | 🟢 | `[X]` |
| T031 | `sync.apply_definition(scene, definition, modules=...)`: só módulos CAFFMob (espessuras, montagem, altura e profundidade do tipo), na linha de cada um; grava `btm_standard_uid`; refaz malha e portas; contagens por `apply_core`; `write_legacy_targets` continua (D-21) | T014, T017, T002, T048 | `[//]` | `caffmob_draw/standards/sync.py` | 🟡 | `[X]` |
| T032 | Prova com eventos simulados: operador com `invoke_props_dialog` chama no `execute` outro operador com diálogo, e as duas respostas chegam (P5) | - | `[//]` | `tests/blender_012_dialogs_probe.py` | 🟡 | `[X]` |
| T033 | `caffmob.standards_apply_scene` (pergunta 1 com segue, difere e não aplicável) e `caffmob.standards_apply_differ` (pergunta 2), aplicando por `sync` numa etapa de desfazer; plano B se o T032 reprovar (D-22) | T031, T032, T014 | - | `caffmob_draw/operators/ops_standards.py` | 🟡 | `[X]` |
| T034 | Configurador, Aplicar, Definir ativa e importar Promob gravam e ativam sem aplicar e chamam `standards_apply_scene`; sai "Incluir medidas manuais"; campo **Montagem** no Configurador (D-22) | T033, T001, T016 | - | `caffmob_draw/operators/ops_standards.py` | 🟡 | `[X]` |
| T036 | Seção Selecionado: "Padrão próprio" e o padrão de origem do módulo CAFFMob (RF-07) | T028 | `[//]` | `caffmob_draw/ui/sidebar_selected.py` | 🟢 | `[X]` |
| T059 | `legacy/convert.py`: para cada raiz herdada, lê pelo adaptador (`customize/adapters.for_object(root).read`), traduz (`convert_core`), cria o módulo pelo caminho do `cabinet_builder` na mesma posição, rotação e pai, e apaga o herdado (`delete_components`, 011); devolve o relatório (D-23, D-25) | T058, T026, T048 | `[//]` | `caffmob_draw/legacy/convert.py` | 🟡 | `[X]` |
| T060 | `caffmob.legacy_convert` (UNDO, uma etapa para o lote) com o relatório por armário; aviso no `load_post` com a contagem (uma vez por arquivo) (D-26) | T059, T054 | - | `caffmob_draw/legacy/ops.py` | 🟡 | `[X]` |
| T061 | Barra lateral: caixa "N armários de bibliotecas antigas · Converter para CAFFMob" enquanto houver herdados; em Selecionado, "Opções do face frame" trocadas pelo botão de converter o armário ativo (D-02 item 5, D-26) | T060, T036 | - | `caffmob_draw/ui/sidebar_selected.py` | 🟡 | `[X]` |
| T063 | Registro de `legacy/` na extensão (gate, load_post, operadores), com remoção no `unregister` | T054, T060 | - | `caffmob_draw/__init__.py` | 🟢 | `[X]` |
| T064 | Biblioteca de molduras pela porta: `HOME_BUILDER_PT_molding_library` sai da lista de subpainéis de `ui/sidebar_project.py` com a porta fechada (D-28) | T048 | `[//]` | `caffmob_draw/ui/sidebar_project.py` | 🟢 | `[X]` |
| T067 | `legacy/groups.py`: para cada grupo pendente, carrega os objetos numa cena temporária, converte as raízes herdadas (`legacy/convert.py`), junta em grupo PLAIN se forem vários, salva por `customize/library_io.save(..., "Geral")`, apaga a cena e os dados carregados; não toca no `.blend` original; relatório por grupo (D-29) | T059, T066 | `[//]` | `caffmob_draw/legacy/groups.py` | 🟡 | `[X]` |
| T068 | `caffmob.legacy_groups_convert` (relatório por grupo, grava o marcador) e `caffmob.legacy_groups_dismiss` (só grava o marcador) (D-30) | T067, T060 | - | `caffmob_draw/legacy/ops.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T055 | Inventário da barra lateral: os operadores das bibliotecas herdadas e da biblioteca de molduras viram "aposentados pela 012" numa lista de dados, sem regenerar a linha de base (D-06) | T049, T050, T051, T052, T064 | `[//]` | `tests/blender_005_sidebar_inventory.py` | 🟡 | `[X]` |
| T056 | Fumaça da porta (fundo): com a porta fechada, nenhum desenho de barra lateral, HUD ou menu de contexto mostra frameless, face frame, closets ou a biblioteca de molduras; Mover Sobre, Seleção por componente e Abrir portas continuam; com a preferência ligada, tudo volta | T049, T050, T051, T052, T053, T063, T064 | `[//]` | `tests/blender_012_legacy_gate_smoke.py` | 🟢 | `[X]` |
| T037 | Traduções pt-BR/en-US dos textos novos (painel, categorias, Criar armário, Montagem, padrão próprio, as duas perguntas, conversão e perdas, grupos antigos, preferência); "BIBLIOTECA CAFFMOB" sem tradução; `test_i18n_coverage` verde | T021, T024, T025, T027, T029, T033, T034, T049, T052, T060, T061, T068 | - | `caffmob_draw/data/translations/library.json` | 🟢 | `[X]` |
| T038 | Fumaça de Criar armário (fundo): balcão, aéreo e torre com as medidas e espessuras do fixture; Cancelar não cria; base passante na malha e na lista de corte; padrão próprio; categoria Lavanderia (DOR) dá chapas de DOR | T027, T029, T012, T018 | `[//]` | `tests/blender_012_cabinet_standard_smoke.py` | 🟢 | `[X]` |
| T039 | Fumaça de aplicar (fundo): 5 módulos CAFFMob, 1 com padrão próprio; Não; Sim + Não; Sim + Sim; OBJ e frameless não convertido como não aplicáveis; balcão de Banheiro com chapas BAN; 50 módulos em menos de 5 s; M-03 num arquivo antigo | T034, T004 | `[//]` | `tests/blender_012_apply_smoke.py` | 🟢 | `[X]` |
| T062 | Fumaça da conversão (fundo): arquivo com 3 frameless (um com gavetas), 1 face frame e 1 closet → aviso com 5; converter deixa 5 módulos CAFFMob nas mesmas posições e medidas externas; relatório com as gavetas perdidas; 50 armários em menos de 5 s (o Ctrl+Z é provado no T070, D-31) | T061, T063 | `[//]` | `tests/blender_012_convert_smoke.py` | 🟡 | `[X]` |
| T040 | Interface com eventos simulados: ordem dos botões, Cozinha abre os modelos prontos, Criar categoria, Criar armário até o editor abrir, Inserir sem bibliotecas herdadas, convivência com o HUD, a seleção por componente (011) e o Mover Sobre | T024, T025, T027, T049 | `[//]` | `tests/blender_012_library_ui.py` | 🟡 | `[X]` |
| T041 | Regressão: fumaças das features 001 a 011 verdes (as que criam armários herdados por código continuam válidas) (princípio VII) | T037, T038, T039, T040, T055, T056, T062, T069, T070 | - | `tests/blender_smoke.py` | 🟢 | `[X]` |
| T042 | Guia novo: Biblioteca CAFFMob, categorias, modelos prontos, Criar armário, montagem lateral e base passante, padrão próprio, conversão de arquivos antigos e dos grupos salvos; guias das bibliotecas herdadas marcados como descontinuados | T040, T062, T069 | `[//]` | `docs/usuario/biblioteca-caffmob.md` | 🟢 | `[X]` |
| T043 | Guia do Configurador: as duas perguntas, o campo Montagem, "não aplicável" e `CAFF_MONTAGEM` | T039 | `[//]` | `docs/usuario/configurador-e-producao.md` | 🟢 | `[X]` |
| T069 | Fumaça dos grupos salvos (fundo): 2 grupos frameless em `cabinet_groups/` (um com gavetas) → 2 módulos em "Geral" com os mesmos nomes e miniatura; relatório com as gavetas; originais na pasta; `bpy.data` com a mesma contagem de objetos, malhas e materiais antes e depois; a oferta não volta | T068 | `[//]` | `tests/blender_012_groups_smoke.py` | 🟡 | `[X]` |
| T070 | Prova do Ctrl+Z da conversão com janela e eventos simulados: converter um arquivo com 3 armários herdados e teclar Ctrl+Z volta os 3 originais e tira os módulos CAFFMob (D-31) | T061, T063 | `[//]` | `tests/blender_012_convert_undo.py` | 🟢 | `[X]` |

## Removidas

| ID | Descrição na versão 1 | Motivo |
|----|------------------------|--------|
| T030 | Frameless inserido pela categoria grava `btm_line` e recebe as chapas da linha | Sessão 3: as bibliotecas herdadas saem da interface; nada herdado é inserido pela categoria |
| T035 | Inserir na barra lateral sem catálogo e "Meus módulos" | Absorvida pelo T049 (mesmos arquivos, agora pela porta única) |

## Notas de execução

- **T023, 2026-10-09:** o popover nativo (`WindowManager.popover`) abre a partir do operador de keymap do painel; o
  plano B (`invoke_popup`) não foi necessário. O painel passou a se ancorar na parte **visível** da viewport
  (`hb_gpu_draw.get_visible_window_bounds`): o cabeçalho e a barra de ferramentas se sobrepõem à região e pegavam o
  clique no topo.
- **T032:** dois diálogos encadeados funcionam (o 1º chama o 2º no `execute`; Esc no 2º cancela só ele). Com isso,
  "Sim" na 1ª pergunta já aplica os módulos que seguem; a 2ª aplica os que diferem. São duas etapas de desfazer
  quando as duas respostas são Sim.
- **T031:** `sync.apply_definition` atualiza só os módulos CAFFMob; os herdados só no modo de suporte
  (`show_legacy_libraries`). Um bloqueio (`properties.suspended_geometry`) evita refazer a malha a cada propriedade:
  50 módulos em 0,12 s.
- **T026/T059:** o `cabinet_builder` ganhou `build_module`, usado também pela conversão.
- **T062:** a conversão lê todos os armários numa avaliação só e apaga os herdados de uma vez: 50 armários em 3,8 s
  (antes, 9,4 s).
- **T067 (desvio da P6):** `customize/library_io.save` grava um módulo por arquivo; um grupo salvo com vários
  armários vira um módulo por armário ("Nome 1", "Nome 2"), e não um grupo PLAIN.
- **T068:** abrir a confirmação de "Converter grupos antigos" já grava a oferta como feita (aceitando ou não); o
  operador separado de dispensar não foi necessário.
- **T070:** no ambiente de teste, a tecla Ctrl+Z simulada não chega ao `ed.undo` da tela (nem com o Ctrl apertado);
  a prova usa `ed.undo`/`ed.redo` com a janela real, o mesmo sistema de memória do Ctrl+Z: uma etapa desfaz a
  conversão inteira.
- **T055:** os operadores das bibliotecas herdadas estão declarados em `tests/fixtures/sidebar_retired_012.json`.
- **T041 (regressão), 2026-10-09:** 37 fumaças em segundo plano e 6 com janela verdes. Ajustes:
  - `blender_increment1_smoke` cobre a sincronização herdada no modo de suporte (D-21);
  - `blender_011_component_smoke` testa o modo Parts no modo de suporte;
  - `delete_components` (011) passou a remover em lote (`bpy.data.batch_remove`): a conversão de 50 armários foi de
    4,1 s para 1,8 s;
  - o traceback `KeyError: "caffmob_draw"` da `blender_inspection_smoke` já existia antes (ambiente sem
    preferências).
- **T054 (corrigida):** o `load_post` também devolve os modos de seleção herdados ao de gabinete; num arquivo salvo em
  "Parts", a caixa do armário ficava sem seleção e a seleção por componente não a alcançava.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-09 | Versão 2 sobre o roadmap versão 2: I1 (porta das bibliotecas herdadas), I5 (conversão), modelos prontos; T044 a T063 novas; T030 e T035 removidas; T002, T006, T010, T017, T024, T026, T031, T037, T039, T040, T041 e T042 ajustadas | reversa |
| 2026-10-09 | Versão 3 sobre o roadmap versão 3: T064 (molduras), T065 a T069 (grupos salvos), T070 (Ctrl+Z com janela); T015, T021, T025, T037, T041, T042, T055, T056 e T062 ajustadas | reversa |
