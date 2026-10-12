# Bibliotecas herdadas: porta e conversão (legacy) — Requisitos

🟢 **CONFIRMADO** — contrato extraído em 2026-10-10 dos 7 arquivos de `caffmob_draw/legacy/` (705 linhas: `__init__.py`, `gate.py`, `convert_core.py`, `convert.py`, `groups_core.py`, `groups.py`, `ops.py`), sem alterações sem commit na pasta, e da preferência `show_legacy_libraries` em `caffmob_draw/__init__.py:BTM_AddonPreferences`. Confirmação de código não implica validação no Blender. 🟡 identifica inferência (prioridade, intenção); 🔴 identifica lacuna que depende de validação humana ou de execução no Blender.

🟢 Escopo: esta unit é a camada de **gate e conversão** criada pela feature 012. O código das bibliotecas herdadas do Home Builder 5 em si está especificado em `_reversa_sdd/hb_core/`, `hb_placement/`, `hb_layouts/`, `product_common/`, `frameless/`, `face_frame/`, `closets/` e `catalog_molding/`; aqui só se descreve o que esta unit lê delas.

## Visão Geral

🟢 A unit tira as bibliotecas herdadas (frameless, face frame, closets e, por tabela, molduras) da interface sem desregistrar o código delas, para que arquivos antigos continuem abrindo. Uma porta única (`gate.legacy_ui`) responde se a interface herdada aparece, lendo uma preferência avançada desligada por padrão. Ao abrir um arquivo, a unit põe as propriedades de cena herdadas nos valores de fábrica e avisa quantos armários antigos existem. O usuário converte esses armários em módulos CAFFMob (um de cada vez ou todos, numa etapa de desfazer), com um relatório do que se perdeu. Os grupos salvos em "Meus módulos" das bibliotecas antigas também são convertidos, uma vez, para a biblioteca do usuário (categoria "Geral"). Fontes: `legacy/__init__.py`, `gate.py`, `convert.py`, `groups.py`, `ops.py`; ADR `_reversa_sdd/adrs/0006-biblioteca-propria-e-gate-legado.md`.

## Responsabilidades

- 🟢 Decidir, num ponto só, se a interface herdada aparece (`gate.legacy_ui`), consultado por 13 arquivos de interface, seleção e padrão (lista em `design.md` › Consumidores).
- 🟢 Detectar raízes de armários herdados e as de topo da cena (`gate.is_legacy`, `gate.legacy_roots`).
- 🟢 No `load_post`, neutralizar `product_tab` e os modos de seleção herdados quando a porta está fechada, e agendar o aviso de armários antigos (`__init__.py:on_load_post`, `ops.py:notify_legacy`).
- 🟢 Traduzir um armário herdado para os campos do `btm_cabinet` com a lista de perdas, em Python puro (`convert_core.translate`).
- 🟢 Converter em lote os armários da cena: ler, construir os módulos CAFFMob, apagar os herdados e renomear (`convert.convert_scene`).
- 🟢 Converter os grupos salvos das bibliotecas herdadas e controlar a oferta única por um marcador JSON (`groups.py`, `groups_core.py`).
- 🟢 Expor os operadores `caffmob.legacy_convert` e `caffmob.legacy_groups_convert` com relatório (`ops.py`).
- 🟢 Fora da responsabilidade: a classificação de objetos (`_reversa_sdd/selection/`), a leitura de frentes por biblioteca (adaptadores, `_reversa_sdd/customize/`), a criação da geometria do módulo (`operators/cabinet_builder.build_module`, ver `_reversa_sdd/cabinet_editor/` e `_reversa_sdd/operators/`), a exclusão em profundidade (`_reversa_sdd/aggregates/`), as medidas do padrão ativo (`_reversa_sdd/standards/`) e o painel da biblioteca que oferece a conversão de grupos (`library_panel/`, spec em `_reversa_sdd/library_panel/`). _(Revisão 2026-10-10: a pasta de spec existe; texto anterior dizia "sem pasta própria de spec")_

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 A interface herdada só aparece se a preferência `show_legacy_libraries` (BoolProperty, padrão `False`, grupo "Avançado") do add-on estiver ligada. O pacote é `__package__.rsplit('.', 1)[0]`; contexto `None`, add-on ausente ou preferência ausente valem **fechada**. A porta é preferência de visibilidade, não controle de segurança. | `gate.py:_preferences/legacy_ui`; `caffmob_draw/__init__.py:BTM_AddonPreferences.show_legacy_libraries`; ADR 0006 |
| RN-02 | 🟢 Bibliotecas herdadas = `LEGACY_LIBRARIES = frozenset({'FRAMELESS', 'FACE_FRAME', 'CLOSETS'})`. Um objeto é raiz herdada se `selection.classify.module_library(obj)` está nesse conjunto (tags `IS_FRAMELESS_CABINET_CAGE`, `IS_FACE_FRAME_CABINET_CAGE`, `IS_FACE_FRAME_PRODUCT_CAGE`, `IS_CLOSET_STARTER_CAGE`). Molduras não entram no conjunto: usam só a porta. | `gate.py:LEGACY_LIBRARIES/is_legacy`; `selection/classify.py:MODULE_TAGS` |
| RN-03 | 🟢 `legacy_roots(scene)` devolve as raízes herdadas de `scene.objects`, na ordem da cena, **excluindo** as que têm qualquer ancestral também raiz herdada. | `gate.py:legacy_roots` |
| RN-04 | 🟢 Com a porta fechada, `neutralize_product_tab` percorre **todas** as cenas de `bpy.data.scenes` e põe `home_builder.product_tab = 'FRAMELESS'`, `hb_frameless.frameless_selection_mode = 'Cabinets'`, `hb_face_frame.face_frame_selection_mode = 'Cabinets'`, `hb_closets.closet_selection_mode = 'Starters'`; grupos ausentes são pulados; só grava o que difere; devolve se mudou algo. Com a porta aberta não faz nada e devolve `False`. Os itens do enum não são removidos. | `__init__.py:NEUTRAL_TAB/NEUTRAL_MODES/neutralize_product_tab` |
| RN-05 | 🟢 O handler `load_post` (`@persistent`) neutraliza e registra o timer `ops.notify_legacy` com `first_interval=1.0` se ele ainda não estiver registrado. O timer roda uma vez (devolve `None`): sem cena ou com a porta aberta não faz nada; com N > 0 raízes de topo mostra "N armário(s) de bibliotecas antigas: use Converter para CAFFMob na barra lateral" por `ui.save_feedback.show`. | `__init__.py:on_load_post`; `ops.py:notify_legacy` |
| RN-06 | 🟢 Tipo: `BASE→BASE`, `UPPER→WALL`, `WALL→WALL`, `TALL→TALL` (comparação em maiúsculas; `None` vira ""). Qualquer outro (ex.: `LAP_DRAWER`, `PANEL`, `HANGING`, `ISLAND`) vira `TALL` se `height ≥ TALL_FROM = 1.2` m, senão `BASE`, com perda `TYPE_APPROX` (1). | `convert_core.py:_TYPES/TALL_FROM/_type` |
| RN-07 | 🟢 Linha: `cabinet.line` se estiver em `LINES = ('COZ','DOR','BAN','SAL','ESC')`; senão `DOR` para `CLOSETS` e `COZ` para as demais. A linha lida vem da custom property `btm_line` da raiz. | `convert_core.py:LINES/_line`; `convert.py:read_cabinet` |
| RN-08 | 🟢 Frente: portas somam em todas as aberturas (`DOOR_LEFT`=1, `DOOR_RIGHT`=1, `DOUBLE_DOORS`=2). ≥ 2 portas → `door_swing='DOUBLE'` e perda `EXTRA_DOORS` = portas − 2 (só se > 0); 1 porta → `LEFT` se a primeira porta vista é `DOOR_LEFT`, senão `RIGHT`; 0 portas → `FLIP` se houve `FLIP_UP`, senão `NONE`. Basculante junto com portas → 1 perda `SPECIAL`. | `convert_core.py:_DOORS/translate` |
| RN-09 | 🟢 Perdas por abertura: `DRAWERS` soma `max(1, drawer_count)`; `PANEL` soma 1; frente fora de `OPEN`, `''`, `None`, portas, `FLIP_UP`, `DRAWERS`, `PANEL` soma 1 `SPECIAL`; cada item de `other_fronts` soma 1 `SPECIAL`. Quantidades agregadas por chave na ordem da primeira ocorrência; contagem 0 não cria perda. | `convert_core.py:translate.lose` |
| RN-10 | 🟢 Prateleiras = `int(cabinet.shelves or 0)` + Σ `int(opening.shelves or 0)`. A distribuição por vão não é preservada e não há teto. | `convert_core.py:translate` |
| RN-11 | 🟢 `translate` devolve `width/height/depth` sem alteração (metros) e `assembly='LATERAL'`, mas a construção usa a montagem do padrão ativo (`standards.api.active_assembly(scene)`), não esse campo. | `convert_core.py:translate`; `convert.py:_build` |
| RN-12 | 🟢 Medidas da conversão: caixa local pelo `bound_box` do objeto avaliado (depsgraph do `bpy.context`); se alguma dimensão ≤ 1e-6 m, cai para `selection.editing.get_dimension` (largura, altura, profundidade) e caixa `(0, −d, 0)…(w, 0, h)`. Tipo: `face_frame_cabinet.cabinet_type` (FACE_FRAME), `hb_closet_starter.closet_type` (CLOSETS) ou `str(root.get('CABINET_TYPE', 'BASE'))`. | `convert.py:_local_box/_cabinet_type/read_cabinet` |
| RN-13 | 🟢 Aberturas vêm do adaptador da personalização (`customize.adapters.for_object(root)` → `adapter.read(root).openings`): `front or 'OPEN'`, `drawer_count or 0`, `interior.shelves` (0 sem interior). Sem adaptador ou com **qualquer exceção** na leitura → nenhuma abertura, sem aviso. Só para FACE_FRAME, `other_fronts` = `front_type` dos `children_recursive` com `IS_FACE_FRAME_OPENING_CAGE` em `('PULLOUT','TILT_OUT','INSET_PANEL','APPLIANCE')`. | `convert.py:_openings/_other_fronts/SPECIAL_FACE_FRAME` |
| RN-14 | 🟢 Construção: `standard_defaults(context, line, cabinet_type)` dá `carcass`, espessura por papel e a definição ativa; `build_module` cria o módulo com as medidas traduzidas, na primeira coleção do original (ou `context.collection`), gravando `btm_line` e `btm_standard_uid`. Posição: `matrix_world_original @ Translation(((lo.x+hi.x)/2, hi.y, lo.z))`; o pai do original é mantido com `matrix_parent_inverse = pai.matrix_world.inverted()`. | `convert.py:_build`; `operators/cabinet_builder.py:standard_defaults/build_module` |
| RN-15 | 🟢 Lote: lê **todos** os armários, constrói **todos**, apaga os originais de uma vez com `delete_components(roots, keep_aggregates=False)` (solta grudados no lugar, apaga agregados próprios e a subárvore) e só então dá a cada módulo o nome do original. Agregados próprios viram perda `AGGREGATES` com a quantidade. | `convert.py:convert_scene/_read/_build`; `aggregates/ops_aggregate.py:delete_components` |
| RN-16 | 🟢 Raízes explícitas passadas a `convert_scene` são filtradas por "ainda existe em `bpy.data.objects`" e `is_legacy`, mas **não** pelo aninhamento de RN-03. Sem raízes, usa `legacy_roots(context.scene)`. | `convert.py:convert_scene` |
| RN-17 | 🟢 Relatório por armário: `"<nome> (<biblioteca traduzida>) → <módulo>  ·  sem perdas"` ou `"…  ·  perdas: <n> <rótulo>, …"`, com os rótulos de `LOSS_LABELS` traduzidos. | `convert.py:report_lines/LIBRARY_LABELS`; `convert_core.py:LOSS_LABELS` |
| RN-18 | 🟢 `caffmob.legacy_convert` (REGISTER, UNDO): `poll` exige modo OBJECT, cena e ≥ 1 raiz de topo; `invoke` pede confirmação com a contagem (1 se `only_active`); com `only_active`, a raiz do objeto ativo (`classify.module_root`) precisa ser herdada, senão WARNING "Selecione um armário de biblioteca antiga" e CANCELLED. Ao fim: INFO "N armário(s) convertidos; M com perdas" e relatório em popup (só com janela). | `ops.py:BTM_OT_LegacyConvert` |
| RN-19 | 🟢 Grupos salvos = itens de `frameless.operators.ops_library.get_user_library_items()` (todas as pastas `cabinet_groups/`, raiz e subpastas; frameless e face frame usam a mesma pasta), como `(nome, caminho)`; `OSError` → lista vazia. Nome de arquivo repetido entre pastas: só o primeiro visto entra (`seen_names`). _(Revisão 2026-10-10: ops_library.py:get_user_library_items, seen_names)_ | `groups.py:group_items` |
| RN-20 | 🟢 Marcador `legacy_groups.json` em `customize.library_io.modules_root()`: `{"schema-version": 1, "offered": bool, "converted": [caminhos]}`. Ausente, ilegível, JSON inválido, `offered` não-bool ou `converted` não-lista de strings → `{}` (oferece de novo). `schema-version` não é lido. Pendentes = caminhos fora de `converted` (comparação por string). | `groups_core.py:parse_marker/dump_marker/pending`; `groups.py:read_marker` |
| RN-21 | 🟢 A oferta no painel aparece se a porta está fechada, há pendentes e `offered` é falso; o resultado fica em cache até `invalidate()` (chamado por `write_marker`). | `groups.py:should_offer/invalidate`; `groups_core.py:should_offer` |
| RN-22 | 🟢 `caffmob.legacy_groups_convert` (só REGISTER, sem UNDO): sem pendentes → INFO "Nenhum grupo antigo para converter" e CANCELLED; senão grava `offered=True` **antes** da confirmação (cancelar também dispensa a oferta). `execute` converte os pendentes, invalida as categorias do painel, informa "N módulo(s) salvos em Geral" e mostra o relatório. | `ops.py:BTM_OT_LegacyGroupsConvert`; `groups.py:dismiss` |
| RN-23 | 🟢 Cada grupo: os objetos do `.blend` são anexados (`link=False`) numa coleção temporária "CAFFMob conversão" da cena atual; as raízes de topo herdadas viram módulos (RN-15); cada módulo é salvo em "Geral" por `library_io.save` (com miniatura), com o nome do grupo (1 módulo) ou "Nome 1", "Nome 2"…; nomes que colidem (casefold) com módulos de "Geral" recebem " (2)", " (3)"…; no fim tudo o que foi carregado ou criado sai. O `.blend` original nunca é alterado. | `groups.py:convert_group/_existing_names/_cleanup`; `groups_core.py:target_name` |
| RN-24 | 🟢 Um grupo entra em `converted` quando `convert_group` não devolve erro de abertura (`OSError`/`RuntimeError`); erros de `library_io.save` vão só para o relatório e **não** impedem a marcação. O marcador é gravado no fim do lote por arquivo temporário + `os.replace`. | `groups.py:convert_pending/write_marker` |
| RN-25 | 🟢 `register` registra os dois operadores e acrescenta `on_load_post` a `load_post` se ausente; `unregister` remove o timer (se registrado), o handler e as classes registradas, em ordem inversa. `register` não chama a neutralização. | `__init__.py:register/unregister`; `ops.py:register/unregister` |

## Requisitos Funcionais

🟡 Prioridades inferidas por número de consumidores, posição na cadeia e testes; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Porta única da interface herdada pela preferência | Must | CA-01, CA-02; `blender_012_legacy_gate_smoke` |
| RF-02 | 🟢 Detecção de raízes herdadas de topo | Must | CA-03 |
| RF-03 | 🟢 Neutralização de `product_tab` e modos de seleção no `load_post` | Should | CA-04 |
| RF-04 | 🟢 Aviso de armários antigos ao abrir o arquivo | Should | CA-05 |
| RF-05 | 🟢 Tradução pura com contagem de perdas | Must | CA-06, CA-07, CA-08, CA-09; `test_legacy_convert` |
| RF-06 | 🟢 Conversão em lote da cena (ler, construir, apagar, renomear) | Must | CA-10, CA-12, CA-13; `blender_012_convert_smoke` |
| RF-07 | 🟢 Operador "Converter para CAFFMob" (todos ou o ativo) com etapa de desfazer | Must | CA-10, CA-11; `blender_012_convert_undo` |
| RF-08 | 🟢 Relatório de perdas por armário | Should | CA-08, CA-10 |
| RF-09 | 🟢 Conversão dos grupos salvos para a biblioteca do usuário | Should | CA-14, CA-15, CA-16 |
| RF-10 | 🟢 Marcador e oferta única dos grupos | Could | CA-17, CA-18, CA-19; `test_legacy_groups` |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desempenho | Ler todos, construir todos e apagar em lote para não reavaliar a cena (com drivers herdados) a cada armário; fumaça exige 50 armários em menos de 5 s | `convert.py:convert_scene` (docstring, "princípio IX"); `aggregates/ops_aggregate.py:delete_components` (`batch_remove`); `tests/blender_012_convert_smoke.py` | 🟢 _(Revisão 2026-10-10: blender_012_convert_smoke executado no Blender 5.2: 50 armários em 1,05 s)_ |
| Desempenho de desenho | Oferta de grupos em cache porque o painel desenha a cada quadro | `groups.py:should_offer/_offer_cache` | 🟢 |
| Desfazer | Conversão da cena numa etapa de desfazer (`{'REGISTER','UNDO'}`); conversão de grupos sem UNDO (grava arquivos externos) | `ops.py:BTM_OT_LegacyConvert/BTM_OT_LegacyGroupsConvert`; `tests/blender_012_convert_undo.py` | 🟢 _(Revisão 2026-10-10: blender_012_convert_undo executado com xvfb-run: uma etapa desfaz os 3 e refazer volta)_ |
| Separação do cálculo | `convert_core` e `groups_core` não importam `bpy` (testes puros) | `tests/test_legacy_convert.py`, `tests/test_legacy_groups.py` | 🟢 |
| Integridade de arquivo | Marcador gravado por temporário na mesma pasta + `os.replace` (sem limpeza do temporário em falha) | `groups.py:write_marker` | 🟢 |
| Preservação de dados do usuário | `.blend` dos grupos nunca é sobrescrito nem apagado | `groups.py` (docstring, RN-14 da 012); `convert_group` só lê | 🟢 |
| Ciclo de vida | `unregister` desfaz `register` (timer, handler, classes); handler `@persistent` | `__init__.py`; `ops.py` | 🟢 |

## Critérios de Aceitação

🟢 Derivados do código e dos testes. CA-06 a CA-09 e CA-17 a CA-19 são cobertos por testes puros executados nesta extração; CA-01 a CA-05 e CA-10 a CA-16 dependem do Blender e não foram executados. _(Revisão 2026-10-10: na revisão, blender_012_legacy_gate_smoke cobriu CA-01, CA-02 e CA-04 (neutralização chamada direto, não via load_post) e blender_012_convert_smoke cobriu CA-10; CA-13 conferido por sonda; CA-03, CA-05, CA-11, CA-12, CA-14 a CA-16 seguem sem execução)_

```gherkin
CA-01 — Porta fechada por padrão
Dado o add-on instalado com show_legacy_libraries = False (ou sem preferências acessíveis)
Quando um ponto de interface chama gate.legacy_ui(context)
Então recebe False; Inserir não mostra product_tab, o HUD não mostra os modos herdados e a seleção por componente sobe todo módulo (cabinet_modes == {})

CA-02 — Porta aberta para suporte
Dado show_legacy_libraries = True
Quando os mesmos pontos desenham
Então a interface herdada reaparece e notify_legacy, should_offer e neutralize_product_tab não fazem nada

CA-03 — Raízes de topo
Dado um armário frameless "A" e um armário herdado "B" cujo pai (direto ou indireto) é "A"
Quando chamo gate.legacy_roots(scene)
Então recebo só [A]; is_legacy(B) continua True

CA-04 — Neutralização no load_post
Dado um arquivo salvo com product_tab = 'FACE FRAME' e frameless_selection_mode = 'Parts', porta fechada
Quando o arquivo é aberto
Então product_tab = 'FRAMELESS', frameless/face_frame_selection_mode = 'Cabinets', closet_selection_mode = 'Starters' em todas as cenas; com a porta aberta nada muda

CA-05 — Aviso ao abrir
Dado um arquivo com 3 armários herdados de topo, porta fechada
Quando o arquivo é aberto
Então após ~1 s a barra de status mostra "3 armário(s) de bibliotecas antigas: use Converter para CAFFMob na barra lateral", uma vez; sem herdados, nada aparece

CA-06 — Tipos
Dado LegacyCabinet de 0,8 × 0,72 × 0,55 m
Quando traduzo com cabinet_type BASE, UPPER, TALL, LAP_DRAWER e (CLOSETS, HANGING, 2,2 m)
Então recebo BASE, WALL, TALL, BASE + perda TYPE_APPROX e TALL; PANEL de 0,7 m vira BASE

CA-07 — Frentes
Dado aberturas [DOOR_LEFT], [DOOR_RIGHT], [DOUBLE_DOORS], [DOOR_LEFT, DOOR_RIGHT], [FLIP_UP], [OPEN] ou nenhuma
Quando traduzo
Então door_swing = LEFT, RIGHT, DOUBLE, DOUBLE, FLIP, NONE, NONE, sem perdas nos casos de uma única frente suportada

CA-08 — Perdas contadas
Dado aberturas [DOOR_LEFT, DRAWERS(3), DRAWERS(2), PANEL] e other_fronts [PULLOUT, APPLIANCE]
Quando traduzo
Então door_swing = LEFT e perdas DRAWERS 5, PANEL 1, SPECIAL 2, sem EXTRA_DOORS; [DOUBLE_DOORS, DOOR_LEFT] dá EXTRA_DOORS 1

CA-09 — Prateleiras, linha e medidas
Dado shelves = 1 e aberturas com 2 e 1 prateleiras
Quando traduzo
Então shelves = 4; linha '' → COZ, 'BAN' → BAN, 'XYZ' → COZ, CLOSETS → DOR; largura/altura/profundidade iguais às de entrada e assembly = 'LATERAL'

CA-10 — Converter a cena (feliz)
Dado 3 frameless (um com 3 gavetas), 1 face frame e 1 starter de closet, porta fechada
Quando executo caffmob.legacy_convert
Então não sobra raiz herdada nem peça herdada, há 5 módulos CAFFMob (object_kind = 'MODULE') com os nomes originais e a mesma caixa no mundo (tolerância 2 mm), o closet tem linha DOR, o gaveteiro tem door_swing NONE e o relatório cita "Gaveteiro" com 3 gavetas perdidas

CA-11 — Converter só o ativo sem armário antigo (falha)
Dado uma cena com herdados e o objeto ativo sendo um módulo CAFFMob (ou nenhum)
Quando executo caffmob.legacy_convert(only_active=True)
Então recebo WARNING "Selecione um armário de biblioteca antiga", retorno CANCELLED e nada muda

CA-12 — Leitor do adaptador falha (falha tolerada)
Dado um armário herdado cujo adapter.read levanta exceção
Quando converto
Então o módulo nasce sem frentes nem prateleiras de vão (door_swing NONE) e o relatório não registra essa perda

CA-13 — Erro na construção no meio do lote (falha)
Dado 3 armários e build_module levantando exceção no 2º
Quando executo convert_scene
Então a exceção sobe ao operador, o 1º módulo novo já existe ao lado do original e nenhum original foi apagado (sem rollback explícito)

CA-14 — Converter grupos (feliz)
Dado 2 grupos pendentes, "Cozinha L" com 2 armários e "Ilha" com 1, e já existindo "Ilha" em Geral
Quando confirmo caffmob.legacy_groups_convert
Então são salvos "Cozinha L 1", "Cozinha L 2" e "Ilha (2)" em Geral, o marcador fica {offered: true, converted: [os 2 caminhos]} e nenhum dado carregado sobra na cena

CA-15 — Grupo ilegível (falha)
Dado um .blend pendente que bpy.data.libraries.load não consegue abrir
Quando converto os pendentes
Então o relatório traz "Não foi possível abrir o grupo <nome>: <erro>", o caminho não entra em converted e a coleção temporária é removida

CA-16 — Nada pendente (falha)
Dado o marcador com todos os caminhos em converted
Quando invoco caffmob.legacy_groups_convert
Então recebo INFO "Nenhum grupo antigo para converter" e CANCELLED, sem gravar o marcador

CA-17 — Marcador inválido
Dado legacy_groups.json com "{ruim" ou {"offered": "sim"}
Quando leio o marcador
Então ele vale {} e a oferta volta (should_offer verdadeiro se houver arquivos)

CA-18 — Nome de destino
Dado existing = {"cozinha l", "cozinha l (2)"}
Quando calculo target_name("Cozinha L", existing)
Então recebo "Cozinha L (3)"; sem colisão, o próprio nome

CA-19 — Cancelar a oferta
Dado 1 grupo pendente e offered = false
Quando invoco caffmob.legacy_groups_convert e cancelo a confirmação
Então o marcador já tem offered = true (o painel deixa de oferecer), nada é convertido e o comando continua em "Criar categoria" › "Converter grupos antigos"
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01, RF-02 | 🟡 Must | Porta lida por 13 arquivos (UI, HUD, seleção, padrão); `legacy_roots` também por `standards/sync.scene_modules` e `ui/sidebar_build` |
| RF-05, RF-06, RF-07 | 🟡 Must | Único caminho para levar arquivos antigos ao módulo CAFFMob; testes puros e duas fumaças dedicadas |
| RF-03, RF-04, RF-08, RF-09 | 🟡 Should | Melhoram a transição; há alternativa (converter manualmente, porta aberta) |
| RF-10 | 🟡 Could | Oferta única; o comando fica disponível em "Criar categoria" |
| Remoção do código herdado | 🟡 Won't (nesta unit) | Adiada para uma feature seguinte (012 RN-14); a unit só esconde e converte |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| `caffmob_draw/legacy/__init__.py` | `NEUTRAL_TAB`, `NEUTRAL_MODES`, `neutralize_product_tab`, `on_load_post`, `register`, `unregister` | 🟢 Código; `blender_012_legacy_gate_smoke` (não executado) |
| `caffmob_draw/legacy/gate.py` | `LEGACY_LIBRARIES`, `legacy_ui`, `is_legacy`, `legacy_roots` | 🟢 Código; `blender_012_legacy_gate_smoke` |
| `caffmob_draw/legacy/convert_core.py` | `LegacyOpening`, `Loss`, `LegacyCabinet`, `LINES`, `TALL_FROM`, chaves de perda, `LOSS_LABELS`, `translate` | 🟢 Código; `test_legacy_convert` (4 testes) |
| `caffmob_draw/legacy/convert.py` | `Result`, `Reading`, `read_cabinet`, `convert_scene`, `report_lines` | 🟢 Código; `blender_012_convert_smoke`, `blender_012_convert_undo` (não executados) |
| `caffmob_draw/legacy/groups_core.py` | `pending`, `should_offer`, `parse_marker`, `mark`, `dump_marker`, `target_name` | 🟢 Código; `test_legacy_groups` (3 testes) |
| `caffmob_draw/legacy/groups.py` | `group_items`, marcador, `should_offer`, `convert_group`, `convert_pending`, `dismiss` | 🟢 Código; sem teste de integração |
| `caffmob_draw/legacy/ops.py` | `notify_legacy`, `BTM_OT_LegacyConvert`, `BTM_OT_LegacyGroupsConvert` | 🟢 Código |

🟢 Executado em 2026-10-10, de dentro de `tests/`: `python3 -m unittest test_legacy_convert test_legacy_groups -v` → **7 testes aprovados** (4 + 3). Blender não está disponível neste ambiente: `tests/blender_012_legacy_gate_smoke.py`, `blender_012_convert_smoke.py` e `blender_012_convert_undo.py` (este exige janela) não foram rodados. _(Revisão 2026-10-10: rodados no Blender 5.2.0 LTS: as 3 fumaças passaram (undo com xvfb-run))_ `tests/blender_legacy_smoke.py`, listado em `.reversa/context/modules.json` para esta unit, exercita a calculadora e a duplicação de ambiente do HB (unit `hb_core`), não `legacy/`.

## Lacunas e Pré-condições

- 🟢 Comportamento do desfazer quando `convert_scene` levanta exceção no meio do lote: o operador falha sem etapa própria, o módulo parcial ("BTM_Cabinet") fica ao lado dos originais e um Ctrl+Z o remove, mantendo os originais (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-54):** o lote ganha rollback: `try/except` no operador remove os módulos já criados, reporta ERROR com o nome do armário e devolve CANCELLED. Pendência de implementação: DT-01. _(Revisão 2026-10-10: sonda com build_module falhando no 2º armário, xvfb-run)_
- 🟢 Equivalência produtiva do módulo convertido (chapas, espessuras e montagem passam a ser as do padrão ativo; prateleiras redistribuídas) não é reportada como perda, nem as frentes não lidas por falha do adaptador (EC-04). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-56):** a falha do adaptador vira perda declarada (uma linha "frentes não lidas"); a troca de chapas, espessuras e montagem pelo padrão ativo e a redistribuição de prateleiras ganham só uma nota geral no topo do relatório. Pendência de implementação: DT-03, DT-04.
- 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-55):** manter a soma de portas entre aberturas (o módulo CAFFMob só tem uma frente e `DOUBLE` é a melhor aproximação); a nota D-24 da 012 fica superada (EC-02). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-55):** eliminar a dupla contagem no face frame: `_other_fronts` ignora as gaiolas folha já lidas pelo adaptador (EC-01). Pendência de implementação: DT-02.
- 🟡 Coleções de dados fora de `_DATA_KINDS` trazidas por um grupo podem ficar órfãs na sessão (EC-11).
- 🟢 Pré-condição: `selection.classify`/`editing`/`component`, `customize.adapters`/`library_io`, `operators.cabinet_builder`, `standards.api`, `aggregates.ops_aggregate.delete_components`, `operators.ops_standards` (relatório), `ui.save_feedback`, `library_panel.categories`, `product_libraries.frameless.operators.ops_library` e `data.i18n` disponíveis (ver `design.md` › Dependências).
