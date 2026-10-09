# Roadmap: Biblioteca CAFFMob flutuante, só armários CAFFMob e chapas no padrão global

> Identificador: `012-biblioteca-caffmob-chapas`
> Data: `2026-10-09` (versão 3, depois da sessão 4 de esclarecimentos e do cross-check)
> Requirements: `_reversa_forward/012-biblioteca-caffmob-chapas/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA
> Princípios: `.reversa/principles.md` (I a XI)

## 1. Resumo da abordagem

A feature fica grande. Ela sai em **seis incrementos**, cada um entregável e fechando com a sua fumaça e a regressão
(princípio VII). A ordem reduz risco: primeiro a interface fica só CAFFMob; depois o módulo CAFFMob aprende o padrão e
a montagem; só então vêm o painel, as perguntas e a conversão.

| Incremento | Entrega | Requisitos |
|------------|---------|------------|
| **I1, só CAFFMob na interface** | Uma porta única (`legacy/gate.py`) decide se a interface das bibliotecas herdadas aparece; por padrão, não. Os pontos de entrada vivos passam por ela: Inserir, Meus módulos, modos de seleção na barra lateral e no HUD, menu de contexto, opções do face frame em Selecionado e a biblioteca de molduras. Os botões do HUD que hoje dependem das bibliotecas (Mover Sobre, Seleção por componente, Abrir portas) ganham visibilidade própria. O código herdado continua registrado | RN-12, RN-14, RF-13 |
| **I2, armário CAFFMob pelo padrão** | Medidas, chapas, linha, tipo e montagem (lateral ou base passante) do padrão no módulo CAFFMob: `cabinet_defaults` puro, `structure.layout` e `synthetic_records` com a montagem, `cabinet_builder` sem números fixos, campo Montagem e marca "Padrão próprio" no editor | RN-06 a RN-09, RF-05 a RF-07 |
| **I3, Biblioteca CAFFMob** | Painel flutuante sempre visível; categorias fixas e do usuário; Criar categoria; Criar armário (diálogo e editor); modelos prontos de um catálogo de dados, abertos num popover | RN-01 a RN-05, RN-15, RF-01 a RF-04, RF-15 |
| **I4, aplicar o padrão com duas perguntas** | Núcleo puro da decisão; `sync` para módulos CAFFMob, por linha; fluxo de duas perguntas nos quatro pontos que aplicam o padrão | RN-10, RN-11, RF-08 a RF-10 |
| **I5, converter arquivos antigos e grupos salvos** | Núcleo puro que traduz a especificação lida pelos adaptadores (`customize/adapters`) num módulo CAFFMob e lista as perdas; aviso ao abrir e botão na barra lateral; uma etapa de desfazer. Os grupos salvos das bibliotecas herdadas (`cabinet_groups/`) passam pela mesma conversão e viram módulos da biblioteca do usuário | RN-13, RN-16, RF-14, RF-16 |
| **I6, exportar e documentar** | `CAFF_MONTAGEM` no `.dimensionExport`; guias | RF-11, RF-12 |

## 2. Princípios aplicados

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| I. Simples por fora | Uma biblioteca só, num painel compacto; as três bibliotecas paralelas somem da interface | respeita |
| II. Medir antes de cortar | Medidos: os pontos de entrada vivos das bibliotecas (a maioria dos painéis herdados nem está registrada), o que o módulo CAFFMob representa (sem gavetas), os leitores prontos (`customize/adapters`, `selection/editing.get_dimension`), os testes que criam armários herdados e o inventário da barra lateral. Riscos médios ganham ações de prova | respeita |
| III. Nada pregado | A porta da interface herdada é uma preferência (`show_legacy_libraries`), não um `if False`; medidas, chapas e montagem vêm do padrão; modelos prontos e categorias fixas são dados | respeita |
| IV. Cada camada na espessura certa | Núcleos puros: `structure.layout`, `cabinet_defaults`, `categories_core`, `layout_core`, `apply_core`, `legacy/convert_core` | respeita |
| V. Encaixes padronizados | A interface herdada passa por uma função só (`gate.legacy_ui`); a conversão lê pelos adaptadores que já existem (`customize/adapters/<lib>.read`) e escreve pelo caminho do `cabinet_builder` | respeita |
| VI. Chapas padrão | Reaproveita `classify.module_library`, `customize/adapters`, `cabinet_builder`, `cabinet_editor`, `btm_cabinet.cabinet_type`, `WindowManager.popover`, o protocolo do HUD | respeita |
| VII. Caixote no esquadro | Seis incrementos com fumaça; a regressão das features 001 a 011 continua verde. As fumaças que criam armários herdados por código (17 arquivos) seguem válidas, porque o código fica registrado | respeita |
| VIII. Fita de borda | Conversão com relatório de perdas por armário; arquivo de categorias inválido; padrão sem a linha; atributo de montagem desconhecido | respeita |
| IX. Aproveitamento milimétrico | Painel com layout em cache; contagem de herdados só no `load_post` e quando a cena muda de módulos; meta de 5 s para aplicar a 50 armários e para converter 50 | respeita |
| X. Regulagem pelo projetista | Montagem no Configurador e por armário; as duas perguntas; converter só com confirmação | respeita |
| XI. Ergonomia do projetista | Lateral passante continua o padrão; categorias por ambiente; termos do Promob | respeita |

Nenhum conflito com princípio.

## 3. Decisões técnicas

### I1, só CAFFMob na interface

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | `legacy/gate.py`: `legacy_ui(context)` lê a preferência `show_legacy_libraries` (falso por padrão, escondida no grupo "Avançado" das preferências) e `LEGACY_LIBRARIES = {'FRAMELESS', 'FACE_FRAME', 'CLOSETS'}`. A preferência existe só para suporte e para comparar a conversão | Um ponto só decide (princípio V); nada fica pregado (III); o titular decidiu tirar da interface e apagar o código depois (RN-14) | Apagar os `draw` herdados agora (perde a comparação e arrisca 35 arquivos); `if False` espalhado | 🟢 |
| D-02 | Pontos de entrada que passam pela porta (nota D-02 abaixo) | São os pontos vivos medidos no levantamento; os demais painéis herdados (`view3d_sidebar.PANELS`, `ui_face_frame`, `catalog/`) já não são registrados | Desregistrar as classes herdadas (quebraria os arquivos antigos e as fumaças) | 🟢 |
| D-03 | HUD (`operators/viewport_hud.py`): `_MODE_BUTTONS` e `_GRAB_*` passam pela porta. Abrir portas, Mover Sobre e Seleção por componente ganham `room_ui_visible(context)` (cena de ambiente, fora de layout e detalhe), sem depender de `product_tab` | Hoje os três ficam visíveis só pelas fiações herdadas (`_FF/_FL/_CL_SELECTION.ui_visible`, l. 395-464); sem isso, sumiriam junto | Manter `product_tab` como chave | 🟢 |
| D-04 | `product_tab` some da interface. Com a porta fechada, o `load_post` põe `product_tab = 'FRAMELESS'`, o **valor de fábrica do enum** (`hb_props.py`, l. 463-468). Ele é usado só porque os keymaps herdados (`dim_edit_overlay`, `op_grab_closet`, `gpu_overlay_closets`) exigem FACE FRAME ou CLOSET e, com FRAMELESS, ficam inertes; o frameless não registra keymap. **Os itens do enum ficam** até a remoção do código (RN-14): tirá-los quebraria a leitura de arquivos antigos (cross-check A005) | Sem mexer nos keymaps herdados | Apagar os keymaps; item novo "NONE" no enum (mudaria o enum que os arquivos antigos guardam) | 🟡 |
| D-05 | Seleção por componente (011): com a porta fechada, `component_select.cabinet_modes` devolve `{}` (todo módulo sobe), sem ler os modos herdados | RN-12; o módulo CAFFMob já subia sempre (011 D-07) | Manter os modos herdados escondidos ativos | 🟢 |
| D-06 | `tests/blender_005_sidebar_inventory.py`: o inventário passa a declarar como "aposentados pela 012" os operadores das bibliotecas herdadas (lista em dados), em vez de regenerar a linha de base inteira | O teste compara com `fixtures/sidebar_inventory_baseline.json` (RF-08 da 005); regenerar esconderia perdas acidentais | Regenerar com `--baseline` | 🟡 |
| D-28 | Biblioteca de molduras pela porta: o subpainel sai da lista de `ui/sidebar_project.py` com a porta fechada; `molding/adapters.py` continua para os arquivos antigos | RN-12, sessão 4 Q2 | Apagar o subpainel | 🟢 |

**Nota D-02, pontos de entrada:**
1. `ui/sidebar_insert.py`: seletor `product_tab` e as galerias (l. 20-29);
2. `ui/my_modules.py`: origens FRAMELESS e FACE_FRAME (l. 13-32), e o filtro em `ui/sidebar_props.py` (l. 39-40);
3. `ui/view3d_sidebar.py#HOME_BUILDER_PT_hidden_header` (l. 84-144): as três caixas de modo de seleção (fica o interruptor da 011);
4. `ui/context_menu.py` (l. 43-47): o submenu `MENU_ID` de armários herdados;
5. `ui/sidebar_selected.py` (l. 12-38): "Opções do face frame", trocadas pelo aviso "Converter para CAFFMob" (I5);
6. `ui/menus.py` (l. 81-82): "linha de encaixe" do frameless no menu da parede;
7. `ui/sidebar_project.py` (l. 15): o subpainel `HOME_BUILDER_PT_molding_library` (perfis e madeira maciça por
   `caffmob_frameless.add_molding_profile` e `add_solid_lumber`) sai da lista de subpainéis das anotações. Os pacotes de
   moldura do ambiente ficam dentro da interface do face frame (`props_hb_face_frame.py`, l. 7674) e já saem com ela
   (D-28).

### I2, armário CAFFMob pelo padrão

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-07 | `standards/cabinet_defaults.py` puro: `defaults(values, line, cabinet_type)` → largura padrão, altura, profundidade, Z de instalação e espessura por papel (`ROLE_COMPONENT`), lendo as medidas externas da linha (`base_height`, `base_depth`, `upper_mid`, `upper_depth`, `install_height_upper`, `tall_height`, `tall_depth`); fallback nomeado sem padrão | RN-06, RN-07; princípios III e IV | Ler do padrão dentro do operador | 🟡 |
| D-08 | Tipo: reaproveita `btm_cabinet.cabinet_type` (BASE, WALL, TALL). Não há campo novo de tipo | Já existe (`data/properties.py:288`); princípio VI | Campo `kind` novo (versão 1 deste roadmap) | 🟢 |
| D-09 | Montagem no núcleo: `structure.layout(..., assembly='LATERAL'|'BASE')`. Em BASE, a base vai de −w/2 a w/2, as laterais começam em `t[BOTTOM]` e o tampo continua entre as laterais. A mesma regra entra em `part_sources.synthetic_records` e é repassada por `mesh_gen.generate_cabinet_mesh` | RN-08; a regra de hoje mora nesses dois pontos | Função por montagem | 🟢 |
| D-10 | Campos: `assembly` no padrão (`BTM_PG_StandardDefinition`) e no módulo (`btm_cabinet.assembly`); `btm_cabinet.line`; `btm_standard_uid` na raiz | RN-08, RN-09, D-13 | Número no esquema em mm | 🟡 |
| D-11 | `cabinet_builder` preenche tudo por `cabinet_defaults` no `invoke` (e no `execute` chamado por código); 0,8/0,7/0,55/0,018 viram fallback nomeado | Princípio III | — | 🟢 |
| D-12 | Editor de armário: campo **Montagem** na aba Estrutura; "Padrão próprio" quando há `btm_overrides`, montagem diferente da do padrão de origem ou espessura por papel própria (`RoleState.thickness`) | RN-09, RF-07 | Interruptor manual | 🟡 |

### I3, Biblioteca CAFFMob

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-13 | `library_panel/`: desenho `POST_PIXEL` sempre registrado e keymap de clique e hover em "3D View" (`head=True`), com poll só sobre o painel e `PASS_THROUGH` fora dele | RN-01, Q4; mesmo encaixe do HUD, sem a preferência dele | Widget do HUD; cabeçalho `VIEW3D_HT` | 🟢 |
| D-14 | Canto superior esquerdo; com o HUD ligado, à direita do botão de navegação. Fechado: uma linha "BIBLIOTECA CAFFMOB"; aberto: coluna. Esc ou clique fora fecha | O topo central é do HUD e o canto direito é do gizmo de navegação | — | 🟡 |
| D-15 | Categoria abre um popover nativo (`WindowManager.popover`) com os modelos prontos e os módulos salvos na categoria (`ui/my_modules.py`, só origem MODULES). Plano B: `invoke_popup` com `draw` próprio | Princípio VI; prova na primeira ação do I3 | Galeria desenhada em GPU | 🟡 |
| D-16 | **Modelos prontos** em `data/library_models.json` (lista de dados): id, rótulo, `cabinet_type`, largura em mm (0 = do padrão), `door_swing`, prateleiras. Lista inicial: balcão 1 porta, balcão 2 portas, aéreo 1 porta, aéreo 2 portas, torre. **Sem o balcão gaveteiro**, porque o módulo CAFFMob não tem gavetas (`customize/adapters/btm.py`, l. 15-17 e 51-55). Inserir um modelo = `cabinet_builder` com a linha da categoria | RN-15 (🟡); princípio III. Gavetas no módulo CAFFMob ficam para uma feature própria | Gaveteiro com gavetas falsas | 🟡 |
| D-17 | Categorias: as fixas num catálogo de dados (Cozinha → COZ, Banheiro → BAN, Sala → SAL, Home office → ESC); as do usuário em `extension_path_user(pkg, "modules")/categories.json` (`{nome, linha}`), com as pastas de módulos que já existem migradas como COZ | RN-02 a RN-04 | Categorias no `.blend` | 🟡 |
| D-18 | Criar armário (`caffmob.library_create_cabinet`): `invoke_props_dialog` com tipo, largura, montagem e linha (padrão: a da última categoria, senão COZ), preenchidos por `cabinet_defaults`; confirmar cria pelo `cabinet_builder` e chama `caffmob.cabinet_editor('INVOKE_DEFAULT')` | RN-05, Q2 | Criar sem diálogo | 🟢 |
| D-19 | Inserir na barra lateral fica com Módulo rápido, Objetos e Importar, mais "Biblioteca no topo da viewport" | RF-01, D-05 da versão 1 | — | 🟢 |

### I4, aplicar o padrão com duas perguntas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-20 | `standards/apply_core.py` puro: `plan(modules, previous_uid)` → `(segue, difere, nao_aplicavel)`. "Difere" = padrão próprio (D-12) ou `btm_standard_uid` diferente do padrão global anterior. "Não aplicável" = herdado não convertido (com a dica de converter), importado, objeto da biblioteca de objetos | RN-10, RN-11 | Decidir no operador | 🟢 |
| D-21 | `sync.apply_definition(scene, definition, modules=...)`: atualiza só módulos CAFFMob (espessuras, montagem, altura e profundidade do tipo; largura fica), na linha de cada um; grava `btm_standard_uid`; refaz malha e portas; marca `cut_plan_stale`. A escrita nas propriedades de cena herdadas (`write_legacy_targets`) continua, para os arquivos antigos abrirem coerentes | RN-11 versão 3: só CAFFMob muda | Continuar atualizando frameless e closets (a interface deles saiu) | 🟢 |
| D-22 | Duas perguntas: `caffmob.standards_apply_scene` (pergunta 1, com segue/difere/não aplicável) e `caffmob.standards_apply_differ` (pergunta 2), encadeadas pelo `execute`; plano B, os dois passos no mesmo operador. Configurador, Aplicar, Definir ativa e importar Promob gravam e ativam sem aplicar e chamam o fluxo; "Incluir medidas manuais" sai da tela; campo Montagem no Configurador | RN-10 com as palavras do titular; prova na primeira ação do I4 | Um diálogo com dois interruptores | 🟡 |

### I5, converter arquivos antigos

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-23 | Leitura: `customize/adapters.for_object(root).read(root)` → `spec.Spec` (medidas, aberturas com `front`, `drawer_count`, `interior.shelves`), mais posição, rotação, pai (parede) e `btm_line`. Detecção: `classify.module_library(obj) in LEGACY_LIBRARIES` | Leitores prontos para as três bibliotecas (`customize/adapters/frameless.py:117`, `face_frame.py:87`, `closets.py:70`); princípio VI | Ler prompts e drivers diretamente | 🟢 |
| D-24 | `legacy/convert_core.py` puro: `translate(spec, line)` → `(campos do btm_cabinet, perdas)`, pelas regras da nota D-24 abaixo | O módulo CAFFMob tem uma abertura frontal só, sem gavetas (`data/properties.py:288`); o resto vira perda declarada (princípio VIII) | Estender o módulo CAFFMob com gavetas nesta feature | 🟡 |
| D-25 | `legacy/convert.py`: cria o módulo pelo caminho do `cabinet_builder`, na mesma posição, rotação e pai; dá a montagem e as chapas do padrão ativo; apaga o herdado pela exclusão em profundidade da 011 (`delete_components`); uma etapa de desfazer para o lote; relatório por armário | RN-13; reaproveita a 011 | Esconder o herdado em vez de apagar | 🟢 |
| D-29 | Grupos salvos: `legacy/groups.py` percorre `get_all_cabinet_group_paths()` do frameless e o caminho de `cabinet_groups` do face frame. Para cada `.blend`: carrega os objetos (`bpy.data.libraries.load`) numa cena temporária, converte as raízes herdadas pelo D-25, junta os módulos convertidos num grupo PLAIN se forem vários e salva por `customize/library_io.save(context, raiz, nome, "Geral")`. A cena temporária e os dados carregados saem depois de cada grupo; o arquivo original fica (RN-14). Relatório por grupo | RN-16; reaproveita a conversão e o salvar da biblioteca do usuário (princípio VI) | Converter só quando o grupo é inserido (o usuário não acharia o grupo, que sumiu da interface) | 🟡 |
| D-30 | Oferta única: na primeira abertura do painel com grupos herdados salvos e sem o marcador `legacy_groups.json` (em `extension_path_user(pkg, "modules")`), o painel mostra "Converter grupos antigos" no topo da coluna; aceitar ou dispensar grava o marcador. O mesmo comando fica em "Criar categoria" › "Converter grupos antigos" | RN-16 (oferta e caminho fixo) | Diálogo ao abrir o Blender | 🟡 |
| D-31 | Prova do desfazer da conversão (RF-14) com janela e eventos simulados (Ctrl+Z pelo caminho real, como `tests/blender_bug_ZZUK_undo.py`); a fumaça em fundo confere só o resto (cross-check A004) | O desfazer em segundo plano não é confiável neste projeto (011) | `ed.undo` em segundo plano | 🟢 |
| D-26 | Aviso no `load_post` (uma vez por arquivo, `save_feedback`) com a contagem e o botão **Converter para CAFFMob** na barra lateral enquanto houver herdados; Selecionado mostra o mesmo botão para o armário herdado ativo (D-02, item 5) | RN-13 | Diálogo modal ao abrir (atrapalha quem só quer olhar o arquivo) | 🟡 |

**Nota D-24, tradução para o módulo CAFFMob:**
- tipo: BASE → BASE, UPPER → WALL, TALL → TALL; LAP_DRAWER, PANEL, HANGING e ISLAND → BASE ou TALL pela altura, com perda "tipo aproximado";
- frente: DOOR_LEFT → LEFT, DOOR_RIGHT → RIGHT, DOUBLE_DOORS → DOUBLE, FLIP_UP → FLIP, OPEN → NONE;
- várias aberturas: a maior manda; as outras são perda;
- gavetas, puxador de gaveta, PULLOUT, TILT_OUT, INSET_PANEL e APPLIANCE: perda com a quantidade;
- prateleiras: soma das prateleiras do interior;
- linha: `btm_line`, ou DOR para closets, ou COZ.

### I6, exportar e documentar

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-27 | `CAFF_MONTAGEM` no `.dimensionExport`: grava no fim e lê fora de `raw_attributes` (interface) | RF-11 | Arquivo paralelo | 🟡 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| ~~P1~~ Confirmada (sessão 4): 5 modelos sem gaveteiro; gavetas na feature 013 | RN-15 | — |
| ~~P2~~ Confirmada (sessão 4): gavetas e frentes que o CAFFMob não tem viram perda no relatório | RN-13 | — |
| P6. Grupos convertidos vão para "Geral" (linha COZ); grupos com vários armários viram um grupo PLAIN de módulos CAFFMob (D-29) | RN-16 (proposta) | Baixo: o usuário move e troca a linha depois |
| P3. A interface herdada fica escondida por uma preferência avançada, não apagada (D-01) | RN-12, RN-14 | Baixo |
| P4. Posição do painel no canto superior esquerdo (D-14) | RN-01 | Baixo |
| P5. Popover a partir do keymap e dois diálogos encadeados funcionam; provados na primeira ação do I3 e do I4 | II | Médio: planos B prontos |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Porta da interface herdada | `legacy/gate.py` (novo); preferências (`__init__.py#BTM_AddonPreferences`) | componente-novo | `show_legacy_libraries` e `legacy_ui()` |
| Barra lateral | `ui/sidebar_insert.py`, `ui/my_modules.py`, `ui/sidebar_props.py`, `ui/view3d_sidebar.py`, `ui/sidebar_selected.py`, `ui/context_menu.py`, `ui/menus.py` | regra-alterada | Sem bibliotecas herdadas; aviso do painel e de conversão |
| HUD | `operators/viewport_hud.py` | regra-alterada | Modos herdados pela porta; visibilidade própria dos botões gerais |
| Seleção por componente | `selection/component_select.py#cabinet_modes` | regra-alterada | Sem modos herdados com a porta fechada |
| Módulo CAFFMob | `operators/cabinet_builder.py`; `cabinet_editor/structure.py`, `bridge.py`, `panels_structure.py`; `geometry/mesh_gen.py`; `cutting/part_sources.py`; `data/properties.py`; `standards/cabinet_defaults.py` (novo) | regra-alterada / componente-novo | Padrão, linha, montagem, padrão próprio |
| Painel da biblioteca | `library_panel/` (novo); `data/library_models.json` (novo) | componente-novo | Painel, categorias, modelos prontos, Criar armário |
| Padrão de dimensões | `standards/model.py`, `sync.py`, `migration.py`, `io_promob.py`; `standards/apply_core.py` (novo) | regra-alterada / componente-novo | Montagem, aplicação só CAFFMob e por linha, M-03 |
| Configurador | `operators/ops_standards.py` | regra-alterada | Duas perguntas; campo Montagem |
| Conversão | `legacy/convert_core.py`, `legacy/convert.py`, `legacy/ops.py`, `legacy/groups.py` (novos) | componente-novo | Ler, traduzir, criar, apagar, relatar; grupos salvos |
| Biblioteca de molduras | `ui/sidebar_project.py` | regra-alterada | Subpainel pela porta (D-28) |
| Testes de inventário | `tests/blender_005_sidebar_inventory.py`; `tests/fixtures/` | regra-alterada | Operadores herdados aposentados declarados |
| Traduções | `data/translations/` | regra-alterada | Textos novos |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - preferência `show_legacy_libraries`;
  - `assembly` no padrão e no módulo;
  - `line` no módulo e `btm_standard_uid` na raiz;
  - estado de sessão do painel;
  - `categories.json` e `library_models.json`;
  - `CAFF_MONTAGEM` no `.dimensionExport`;
  - migração M-03.
- Detalhe completo em: `_reversa_forward/012-biblioteca-caffmob-chapas/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| Promob `.dimensionExport` (`CAFF_MONTAGEM`) | arquivo | `_reversa_forward/012-biblioteca-caffmob-chapas/interfaces/promob-dimensionexport.md` |

## 8. Plano de migração

1. Abrir um arquivo antigo não refaz nada:
   - padrão sem `assembly` lê LATERAL;
   - módulos CAFFMob sem `line` ficam COZ;
   - raízes recebem `btm_standard_uid` do padrão ativo (M-03).
2. Armários herdados continuam funcionando como hoje (o código fica registrado). O aviso oferece a conversão (I5),
   que só acontece com confirmação.
3. `product_tab` volta a FRAMELESS com a porta fechada (D-04); nenhum keymap herdado fica ativo pela interface.
4. Pastas de módulos do usuário entram em `categories.json` como COZ.
5. A remoção do código herdado é uma feature seguinte, com as fumaças de prova (RN-14).

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| A feature é grande e mexe em muitas telas | alto | médio | Seis incrementos entregáveis, cada um com fumaça e regressão; I1 primeiro, porque é o de menor risco e destrava o resto |
| Algum ponto de entrada herdado escapa da porta | médio | médio | Inventário da barra lateral (D-06) e teste de interface com eventos simulados percorrendo barra lateral, HUD e menu de contexto |
| Conversão perde detalhe (gavetas, frentes especiais) | médio | alto | Relatório por armário; Ctrl+Z; "não converter" mantém o arquivo como está; perdas confirmadas pelo titular (sessão 4); gavetas na 013 |
| Converter grupos salvos deixa dados soltos no arquivo aberto (objetos, malhas, materiais carregados) | médio | médio | Cena temporária por grupo, apagada com os dados carregados; fumaça confere `bpy.data` igual antes e depois |
| Os botões do HUD somem junto com os modos herdados | médio | médio | D-03 antes de esvaziar `_MODE_BUTTONS` |
| Popover ou diálogos encadeados não funcionam (P5) | médio | baixo | Provas no começo do I3 e do I4; planos B |
| Aplicar ou converter 50 armários trava | médio | baixo | Uma etapa de desfazer; meta de 5 s medida na fumaça |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Fumaças das features 001 a 011 verdes, mais as fumaças de cada incremento da 012 (princípio VII)
- [ ] `ruff check caffmob_draw/`, `python3 docs/rag/tools/check_api.py` e `test_i18n_coverage` sem erro
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-10-09 | Versão 2 (sessão 3): só CAFFMob na interface (I1), conversão (I5), modelos prontos sem gaveteiro, `cabinet_type` em vez de `kind`, aplicação só em módulos CAFFMob; seis incrementos | reversa |
| 2026-10-09 | Versão 3 (sessão 4 e cross-check): molduras pela porta (D-28), grupos salvos (D-29, D-30), desfazer provado com janela (D-31), D-04 explicado (A005); P1 e P2 confirmadas, P6 nova | reversa |
