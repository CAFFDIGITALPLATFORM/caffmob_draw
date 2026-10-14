# Actions: Construtor de armário CAFF MOBI com a arquitetura do Promob

> Identificador: `015-construtor-armario-promob`
> Data: `2026-10-14`
> Roadmap: `_reversa_forward/015-construtor-armario-promob/roadmap.md` (D-01 a D-19)
> Data delta: `_reversa_forward/015-construtor-armario-promob/data-delta.md`
> Interfaces: `interfaces/catalogo-estruturas.md`, `interfaces/padrao-dimensoes-io.md`, `interfaces/cut-plan-json.md`
> (todos arquivo)
> Caminhos relativos à raiz do repositório. Escopo (clarify Q1): Cozinhas e Dormitórios; Salas, Escritórios, Outros,
> caixa de gaveta e conjunto deslizante "Sobre a caixa" ficam fora.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 44 |
| Paralelizáveis (`[//]`) | 22 |
| Maior cadeia de dependência | 13 (T001 → T014 → T015 → T016 → T017 → T018 → T026 → T028 → T029 → T030 → T031 → T042 → T044) |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | Catálogo inicial no formato de `interfaces/catalogo-estruturas.md`, com os ambientes COZ e DOR e estas estruturas: <br>• Cozinhas: Inferior c/ Divisória; Inferior c/ Divisória e Rod; Inferior c/ Divisória até Piso; Inferior c/ Divisória até Piso e Rod; Inferior c/ 2 Laterais até Piso; Inferior c/ 2 Laterais até Piso e Rod; Gaveteiro; Gaveteiro c/ Rodapé; Superior c/ Divisória; Superior c/ 2 Laterais; Torre p/ Eletros; Torre p/ Eletros c/ Rod; <br>• Dormitórios: Armário; Armário s/ Lat Esq; Armário s/ Lat Dir; Armário s/ Laterais; Armário Divisória sobre Base. <br>Componentes, vãos e larguras da tabela RN-03 do requirements, `label_en` de cada uma e o `legacy_map` do contrato | - | `[//]` | `caffmob_draw/data/cabinet_structures.json` | 🟡 | `[X]` |
| T002 | Três campos novos em `_EXTERNAL_FIELDS`, com rótulos pt/en, valores BR/EUA e faixas do `data-delta.md#2.1`: `stretcher_width`, `shelf_setback`, `hanger_rod_drop` (D-07) | - | `[//]` | `caffmob_draw/data/dimension_schema.py` | 🟢 | `[X]` |
| T003 | `group_assembly` na definição do padrão (`data-delta.md#2.2`): valor padrão vazio, validação de `assembly`, `back_kind` e `rear_stretcher` com aviso por campo, entrada na comparação de rascunho como a `assembly` da 012 (D-08) | - | `[//]` | `caffmob_draw/standards/model.py` | 🟡 | `[X]` |
| T004 | `btm_cabinet.structure_id` (`StringProperty`, padrão vazio, `update=update_cabinet_geom`, `# type: ignore`), lido por atributo (D-05) | - | `[//]` | `caffmob_draw/data/properties.py` | 🟢 | `[X]` |
| T005 | Acrescentar **no fim** de `EXTRA_KIND_ITEMS`: `HANGER_ROD`, `PANTS_RACK`, `SHOE_RACK`, `BELT_RACK`, `CASTER`, `STRETCHER`, `TOE_KICK_STRUCT`; e no fim de `DIVISION_KIND_ITEMS`: `INVISIBLE`, `DIVISION_ONLY`. Criar `btm_division.variant` (texto) e `btm_division.bay_width` (m, padrão 0) (`data-delta.md#1.3`, `#1.4`) | - | `[//]` | `caffmob_draw/cabinet_editor/data_props.py` | 🟢 | `[X]` |
| T006 | `structure_id` em cada modelo da biblioteca: balcão 1p/2p → `coz_inferior_divisoria`, aéreo 1p/2p → `coz_superior_divisoria`, torre → `coz_torre_eletros` (D-16) | T001 | - | `caffmob_draw/data/library_models.json` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T007 | Teste puro de `structures_core`: <br>• o catálogo real carrega as 17 estruturas sem aviso; <br>• `schema-version` 2 recusa o catálogo com aviso; <br>• id repetido, ambiente ou grupo desconhecido, papel desconhecido e medida não numérica pulam só a estrutura com "Estrutura <id>: <motivo>"; <br>• `legacy_map`: (COZ, BASE) → `coz_inferior_divisoria`, linha `*` como reserva, entrada para id inexistente pulada | T001 | `[//]` | `tests/test_cabinet_structures.py` | 🟢 | `[X]` |
| T008 | Teste puro de `structure.carcass_parts`, um caso por estrutura de T001: <br>• Inferior c/ Divisória 500 × 720 × 550, chapa 15: lista com Sarrafo frontal e Sarrafo traseiro de 470 × 100, sem Base superior; <br>• Superior c/ Divisória 800 × 700 × 550: com Base superior; <br>• Armário 3000 × 2500 × 550, chapa 18, rodapé 80: altura interna 2384; <br>• Armário Divisória sobre Base: sem Base inferior; <br>• "até Piso": laterais começando em z = 0; <br>• montagem BASE; <br>• os 4 tipos de fundo com as medidas de D-09 | T001 | `[//]` | `tests/test_carcass_parts.py` | 🟢 | `[X]` |
| T009 | Teste puro de `gallery_core`: <br>• abas na ordem dos ambientes do catálogo, com as estruturas ordenadas por `order`; <br>• colunas pela largura da região; <br>• acerto de célula com rolagem; <br>• setas e Enter escolhem, Esc cancela; <br>• catálogo vazio mostra o estado vazio com o aviso; <br>• o rótulo de estado em texto ("Selecionado: <nome>") | - | `[//]` | `tests/test_structure_gallery.py` | 🟢 | `[X]` |
| T010 | Casos novos de vão digitável: 3000, 3 vãos, chapa 18 → 976 cada; digitar 900 no vão do meio → 1014 nas pontas; digitar além do possível (vizinho < 50) é recusado com o mínimo (D-15) | - | `[//]` | `tests/test_cabinet_bays.py` | 🟡 | `[X]` |
| T011 | Casos novos do catálogo das abas: <br>• Divisões de um Armário (DOR) mostram Montante e Invisível e escondem Corta Sar; <br>• no Inferior (COZ) é o contrário; <br>• Internos (DOR) com Cabideiro 01, Cabideiro 02, Cab Extensível, Tubo, Tubo s/ Reforço, Calceiros, Sapateiras, Porta Cintos/Gravatas; <br>• Gavetas (DOR) com Interna p/ trilho, Sapateira, Prateleira Corrediça, Externas; <br>• árvore com as chaves novas (D-03) | - | `[//]` | `tests/test_cabinet_catalog.py` | 🟢 | `[X]` |
| T012 | Teste puro de ida e volta do padrão: <br>• JSON e XML com `group_assembly` e os 3 valores novos voltam iguais; <br>• arquivo sem os campos novos importa com 100, 20 e 70 e `group_assembly` vazio; <br>• `CAFF_GRUPO_INFERIOR` com 2 partes e `back_kind` inválido avisam e caem no valor da estrutura (`interfaces/padrao-dimensoes-io.md`) | T002, T003 | `[//]` | `tests/test_standards_group_assembly.py` | 🟢 | `[X]` |
| T013 | Teste de regressão do corte com módulos falsos (sem `bpy`, como os testes de `part_sources` existentes): <br>• módulo sem `structure_id` gera os mesmos registros, nomes e uids de antes (fixture gravada antes da mudança); <br>• módulo com `structure_id` gera um registro por peça de `carcass_parts`, com o nome e o componente do `data-delta.md#4` | T004 | `[//]` | `tests/test_cut_structure.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T014 | `structures_core.py` (Python puro): `parse(text) → (estruturas, avisos)`, `Structure` imutável, `load()` com cache, `by_environment()`, `legacy_structure(line, cabinet_type)`, `group_type(group)` → BASE/WALL/TALL, nunca levantando exceção (D-01, D-06) | T001, T007 | - | `caffmob_draw/cabinet_editor/structures_core.py` | 🟢 | `[X]` |
| T015 | `carcass_parts(recipe, w, h, d, thick, states, settings, params, back_setback, assembly) → [Part]`, com `Part(role, box, component, name, length, width, edges)`: os papéis LEFT, RIGHT, BOTTOM e TOP pela receita, com montagem LATERAL/BASE e `sides_to_floor`. `layout` e `carcass_lengths` ficam intocados (D-02) | T008, T014 | - | `caffmob_draw/cabinet_editor/structure.py` | 🟢 | `[X]` |
| T016 | Em `carcass_parts`: Sarrafo Frontal e Sarrafo Traseiro (largura `params.stretcher_width`, traseiro deitado ou em pé por `rear_stretcher`), Sarrafo Inteiro e Tampo Linear (profundidade + `top_overhang`) (D-03) | T015 | - | `caffmob_draw/cabinet_editor/structure.py` | 🟡 | `[X]` |
| T017 | Em `carcass_parts`: rodapé da estrutura (D-04). A caixa sobe `toe_kick_height` dentro da altura total, com o rodapé recuado `toe_kick_setback`; "até Piso" põe a base inferior entre as laterais, na altura do rodapé | T016 | - | `caffmob_draw/cabinet_editor/structure.py` | 🟡 | `[X]` |
| T018 | Em `carcass_parts`: tipos de fundo ENCAIXADO, REBAIXADO (+8 por lado no corte), PREGADO (sobre a face traseira, medidas externas) e TRAVESSAS (duas TRA de 100 e fundo entre elas); "Inteiro Recuado" da 008; componente FUN_INF, FUN_SUP ou FUN_ALT pelo grupo (D-09) | T017 | - | `caffmob_draw/cabinet_editor/structure.py` | 🟡 | `[X]` |
| T019 | Larguras digitadas por vão: com `bay_width > 0` nas divisórias de vão inteiro, a diferença vai igualmente para os vizinhos imediatos; recusa quando um vizinho fica abaixo de 50 mm (D-15) | T005, T010 | `[//]` | `caffmob_draw/cabinet_editor/bays.py` | 🟡 | `[X]` |
| T020 | `gallery_core.py` (Python puro): abas por ambiente, grade com as medidas de `library_panel/grid_core.py`, acerto de célula, rolagem, teclado, estado vazio e texto de estado (D-10) | T009, T014 | `[//]` | `caffmob_draw/cabinet_editor/gallery_core.py` | 🟢 | `[X]` |
| T021 | Catálogo das abas: campo `environments` nos itens e filtro em `items()`; itens novos de Divisões, Gavetas e Internos de dormitório; chaves novas na `TREE` (STRETCHER_FRONT, STRETCHER_BACK, STRETCHER_FULL, TOP_LINEAR, TOE_KICK, CASTERS e SIDES_EXTENDED desabilitado com o motivo) (D-03, D-13) | T011 | `[//]` | `caffmob_draw/cabinet_editor/catalog.py` | 🟢 | `[X]` |
| T022 | Extras com estrutura: no módulo com `structure_id`, as chaves de Rodapés não geram rodapé abaixo da caixa (o rodapé vem de `carcass_parts`); Rodízios como ferragem `RODIZIO`; `KICK_SETBACK` lido do padrão (`toe_kick_setback`), com a constante só como reserva (D-04) | T021 | - | `caffmob_draw/cabinet_editor/extras.py` | 🟡 | `[X]` |
| T023 | Núcleo puro dos internos de dormitório: tubo do cabideiro a `hanger_rod_drop` abaixo da prateleira de cima, na largura do vão; calceiro de madeira (chapa ESP) e aramado (ferragem); sapateira (chapa); porta-cintos (ferragem). Devolve `Piece` como `extras.py` (D-14) | T021 | `[//]` | `caffmob_draw/cabinet_editor/wardrobe.py` | 🟡 | `[X]` |
| T024 | Divisões novas: `INVISIBLE` e `DIVISION_ONLY` dividem o subvão sem peça e sem corte; variantes Corta Sar (divisória até o topo, sarrafo cortado em dois), c/ Reb (rebaixo para o fundo), Não Divide o Fundo (o fundo continua inteiro); recuo das móveis por `shelf_setback` | T005, T021 | - | `caffmob_draw/cabinet_editor/divisions.py` | 🟡 | `[X]` |
| T025 | Medidas pela estrutura: `defaults_for_structure(values, structure)` dá a largura da estrutura e a altura e profundidade do padrão pela linha e pelo grupo (D-19); `params` com `stretcher_width`, `shelf_setback`, `hanger_rod_drop`, `toe_kick_*` e `top_overhang`; montagem e fundo do `group_assembly`, com o da estrutura como reserva | T002, T003, T014 | - | `caffmob_draw/standards/cabinet_defaults.py` | 🟢 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T026 | `generate_cabinet_mesh`: com `btm_cabinet.structure_id` conhecido, monta as caixas de `carcass_parts`, com índices de material (caixa, prateleira e fundo; sarrafo e rodapé = caixa); `SHELF_SETBACK` vem do padrão. Sem `structure_id`, ou com id desconhecido (com aviso), o caminho de hoje (D-02) | T018, T025 | - | `caffmob_draw/geometry/mesh_gen.py` | 🟢 | `[X]` |
| T027 | `synthetic_records`: com `structure_id`, um registro por `Part`, com nome, componente e fitas do `data-delta.md#4`; caminho antigo intocado; T013 verde | T013, T018, T025 | - | `caffmob_draw/cutting/part_sources.py` | 🟢 | `[X]` |
| T028 | `build_module` e `caffmob.cabinet_builder` recebem `structure_id`, preenchem `cabinet_type`, `line` e `assembly` pela estrutura, e gravam em `btm_structure.extras` só o que difere do padrão da estrutura | T004, T026 | - | `caffmob_draw/operators/cabinet_builder.py` | 🟢 | `[X]` |
| T029 | Abrir o editor (`bridge`): tira o instantâneo de Cancelar **antes** e depois converte o módulo sem `structure_id` pelo `legacy_map` (RN-22, D-06); "Tipo:" passa a ser o rótulo da estrutura; a árvore lê a presença padrão da estrutura | T028 | - | `caffmob_draw/cabinet_editor/bridge.py` | 🟢 | `[X]` |
| T030 | Aba Estrutura e cabeçalho: "Tipo: <estrutura>", árvore só com os componentes da estrutura, Laterais Engrossuradas desabilitada com o motivo, campo de largura do vão selecionado (RF-12, RF-14) | T021, T029 | - | `caffmob_draw/cabinet_editor/panels_structure.py` | 🟢 | `[X]` |
| T031 | Abas Divisões, Gavetas e Internos filtram pelo ambiente da estrutura e mostram os itens novos com miniatura (ícone nativo quando faltar PNG) | T030 | - | `caffmob_draw/cabinet_editor/panels_interior.py` | 🟢 | `[X]` |
| T032 | `insert_payload` e cena: inserir os internos de dormitório (T023) como `btm_extra`/`CabinetPart`, as divisões `INVISIBLE`/`DIVISION_ONLY` e as variantes (T024), e a gaveta Interna p/ trilho: a de baixo fica mais alta pela altura do trilho inferior, valor 🟡 editável | T023, T024, T029 | - | `caffmob_draw/cabinet_editor/ops_actions.py` | 🟡 | `[X]` |
| T033 | Aba Deslizantes: seletor "No vão" / "Sobre a caixa"; "Sobre a caixa" desabilitado com "Disponível numa próxima versão" (D-17) | - | `[//]` | `caffmob_draw/cabinet_editor/panels_sliding.py` | 🟡 | `[X]` |
| T034 | `gallery.py`: operador modal `caffmob.structure_gallery` com handler `POST_PIXEL` no `VIEW_3D`, desenho com `draw_kit` e `style`, título em Sora e miniaturas da elevação frontal de `carcass_parts` em cache `GPUOffScreen` por (estrutura, escala). OK chama `caffmob.cabinet_builder(structure_id=…)` e abre o editor; Cancelar e Esc removem o handler sem criar nada nem gerar passo de desfazer (D-10, D-11). Conferir antes as assinaturas no RAG (`investigation.md#5`) | T020, T028 | - | `caffmob_draw/cabinet_editor/gallery.py` | 🟡 | `[X]` |
| T035 | Vista do editor com os tokens CAFF MOBI: `FILL`, `EDGE`, `SELECTED` e `BACKGROUND` vêm de `library_panel/style.py` (Noite, laranja na seleção, teal no vão alvo); cabeçalho "Tipo: …" em Sora; estado continua também em texto (D-12) | - | `[//]` | `caffmob_draw/cabinet_editor/window.py` | 🟢 | `[X]` |
| T036 | Biblioteca: "Criar armário" abre a galeria na aba da linha atual; `models_core.parse` valida `structure_id` (ausente = `legacy_map`, desconhecido = modelo pulado com aviso) e `ops_cabinet` passa o id ao builder (D-16) | T006, T034 | - | `caffmob_draw/library_panel/ops_cabinet.py` | 🟢 | `[X]` |
| T037 | `sync.apply_to_module`: converte o módulo sem `structure_id` pelo `legacy_map`, aplica `group_assembly` e os parâmetros novos; o diálogo de reaplicar ganha a linha "N módulos passam para a estrutura nova" (D-06, D-08) | T025, T028 | - | `caffmob_draw/standards/sync.py` | 🟢 | `[X]` |
| T038 | JSON do padrão: grava e lê `group_assembly` e os 3 valores novos; arquivo antigo importa com os de fábrica (`interfaces/padrao-dimensoes-io.md`) | T003, T012 | `[//]` | `caffmob_draw/standards/io_json.py` | 🟢 | `[X]` |
| T039 | XML do Promob: atributos `CAFF_GRUPO_INFERIOR`/`SUPERIOR`/`DESPENSEIRO` e `CAFF_SARRAFO_<LINHA>`, `CAFF_RECUO_PRAT_<LINHA>`, `CAFF_CABIDEIRO_<LINHA>` no fim, como o `CAFF_MONTAGEM`; leitura tolerante com aviso por campo | T003, T012 | `[//]` | `caffmob_draw/standards/io_promob.py` | 🟢 | `[X]` |
| T040 | Exportação de produção 2.3.0: `modules[].structure_id`, códigos de ferragem `TUBO_CABIDEIRO`, `CALCEIRO_ARAMADO`, `PORTA_CINTOS` e `RODIZIO`, e `limit_status` `STRUCTURE_UNKNOWN` e `PART_DEGENERATE` (`interfaces/cut-plan-json.md`) | T027 | - | `caffmob_draw/cutting/json_exporter.py` | 🟢 | `[X]` |
| T041 | Registro: `gallery` em `register()`/`unregister()`, remoção do handler da galeria em todos os caminhos de saída e no `unregister`, e cache de miniaturas liberado | T034 | - | `caffmob_draw/cabinet_editor/__init__.py` | 🟢 | `[X]` |
| T042 | Fumaça no Blender. A cena deve passar por estes casos: <br>• galeria → Inferior c/ Divisória → corte com dois sarrafos e sem Base superior; <br>• Superior com Base superior; <br>• Armário 3 vãos com 976 e rodapé; <br>• digitar 900 no vão do meio; <br>• Cabideiro 01 na lista de ferragens; <br>• prateleira Invisível sem peça; <br>• `.blend` antigo: Cancelar não muda, OK converte; <br>• sarrafo 80 no padrão reaplicado só nos balcões; <br>• abrir um `.blend` da 014 (enums intactos) | T031, T032, T036, T037, T040, T041 | - | `tests/blender_015_construtor_smoke.py` | 🟢 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T043 | Textos novos em pt-BR e en-US no catálogo de tradução da área (`{"texto": {"pt_BR", "en_US"}}`; `tests/test_i18n_coverage.py` confere): galeria ("Select a carcass structure to start building"), ambientes, avisos do catálogo, papéis de peça, itens das abas e "Disponível numa próxima versão" (RF-22, D-18) | T031, T033, T034 | `[//]` | `caffmob_draw/data/translations/cabinet_editor.json` | 🟢 | `[X]` |
| T044 | Ajustar as fumaças 006, 008 e 012 ao caminho novo (módulo criado pela biblioteca agora tem `structure_id`), sem afrouxar asserções: o que mudou de propósito é conferido pelo valor novo | T042 | `[//]` | `tests/blender_008_construtor_smoke.py` | 🟢 | `[X]` |
