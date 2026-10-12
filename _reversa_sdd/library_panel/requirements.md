# Biblioteca CAFFMob (library_panel) — Requisitos

🟢 **CONFIRMADO** — contrato extraído de `caffmob_draw/library_panel/` (11 arquivos, 905 linhas) e `caffmob_draw/data/library_models.json` em 2026-10-10. A árvore de trabalho não tem alterações sem commit nesta pasta (`git status` limpo para `caffmob_draw/library_panel/`). Confirmação de código não implica validação visual no Blender. 🟡 marca prioridade ou intenção inferida; 🔴 marca lacuna que exige validação no host.

## Visão Geral

🟢 O módulo desenha, no canto superior esquerdo de toda viewport 3D, o rótulo fixo "BIBLIOTECA CAFFMOB". Um clique abre uma coluna com "Criar armário", as categorias (fixas e do usuário) e "Criar categoria", e, quando houver grupos herdados pendentes, "Converter grupos antigos" no topo. Uma categoria abre um popover nativo com os modelos prontos CAFFMob (catálogo em JSON) e os módulos que o usuário salvou naquela categoria. Os modelos e o "Criar armário" constroem o módulo pelo `caffmob.cabinet_builder`, que lê altura, profundidade, chapas e montagem do Padrão de Dimensões na linha da categoria. Fontes: `__init__.py` (docstring), `draw.py`, `ops_click.py`, `popover.py`, `ops_cabinet.py`.

🟢 É distinto da biblioteca de objetos não paramétricos (`object_library`, Inserir › Objetos) — `popover.py` (docstring). Não faz download, não usa banco de dados e não grava nada no `.blend` além do que os operadores consumidos criam.

## Responsabilidades

- 🟢 Manter o estado de sessão do painel em `WindowManager.btm_library` (aberto, última categoria, linha dessa categoria) (`props.py:BTM_PG_LibraryState`).
- 🟢 Definir as 4 categorias fixas e ler/gravar as do usuário em `<modules_root>/categories.json`, migrando pastas de módulos soltas como categoria Cozinha (`categories_core.py`, `categories.py`).
- 🟢 Ler e validar o catálogo de modelos prontos `data/library_models.json` (`models_core.py`).
- 🟢 Calcular o layout em pixels do painel e o teste de acerto, em Python puro (`layout_core.py`).
- 🟢 Desenhar o painel por um handler `POST_PIXEL` sempre registrado e cachear o layout por região (`draw.py`).
- 🟢 Tratar clique, hover e Esc por itens de keymap em "3D View" (`head=True`), sem modal permanente (`ops_click.py`).
- 🟢 Mostrar o conteúdo da categoria num popover nativo e inserir modelos prontos (`popover.py`).
- 🟢 Diálogos "Criar categoria" e "Trocar linha" (`ops_categories.py`) e "Criar armário" (`ops_cabinet.py`).
- 🟢 Fora da responsabilidade (contratos citados, não redescritos): construção da geometria e medidas do padrão (`_reversa_sdd/operators/`, `_reversa_sdd/standards/` F-09 `cabinet_defaults.defaults`), raiz da biblioteca e inserção de módulos salvos (`_reversa_sdd/customize/`, `library_io.modules_root/list_modules`, `caffmob.module_insert`), oferta e conversão de grupos herdados (`_reversa_sdd/legacy/` RN-19 a RN-21, F-08 `caffmob.legacy_groups_convert`), editor de armário (`_reversa_sdd/cabinet_editor/`), widget de navegação do HUD (`operators/viewport_hud.py`).

## Regras de Negócio

| ID | Regra confirmada | Fonte |
|---|---|---|
| RN-01 | 🟢 Categorias fixas, nesta ordem: Cozinha→`COZ`, Banheiro→`BAN`, Sala→`SAL`, Home office→`ESC` (`fixed=True`). `DOR` (Dormitório) é linha válida, mas não é categoria fixa. As do usuário vêm depois das fixas, na ordem do arquivo (ordem de criação). | categories_core.py:FIXED/all_categories |
| RN-02 | 🟢 Linhas válidas: `COZ, DOR, BAN, SAL, ESC`; `DEFAULT_LINE = 'COZ'`. Rótulos: Cozinha, Dormitório, Banheiro, Sala, Escritório. | categories_core.py:LINES/LINE_LABELS |
| RN-03 | 🟢 Nome de categoria nova: após `strip()`, não vazio; sem `/` nem `\`; único contra fixas e usuário por `strip().casefold()`. Ordem dos testes: vazio → caractere inválido → repetido. Não há outras restrições (`.`, `..`, `:` e nomes reservados passam). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-57):** `validate_name` recusa os mesmos caracteres que `customize.manifest.file_stem` troca (e ponto final), evitando a divergência de pasta e a falha no Windows. Pendência de implementação: DT-01. | categories_core.py:validate_name |
| RN-04 | 🟢 Leitura de `categories.json` é tolerante: texto vazio → nenhuma categoria, sem aviso; JSON inválido → nenhuma, com aviso; item não-dict ou sem nome → aviso e pula (mas `"name": null` vira a categoria "None", porque `str(None)` não é vazio _(Revisão 2026-10-10: sonda categories_core.parse('{"categories":[{"name":null}]}'))_); nome igual a fixa ou já lido (casefold) → aviso e pula; linha fora de `LINES` → aviso e usa `COZ`. `schema-version` não é verificada. | categories_core.py:parse |
| RN-05 | 🟢 Cada subpasta de `modules_root` que não começa com `.` e não é categoria conhecida (casefold) entra como categoria do usuário `COZ`, em ordem alfabética, depois das existentes. A lista migrada só é gravada se mudou **e** a leitura não gerou avisos. | categories_core.py:merge_folders; categories.py:load |
| RN-06 | 🟢 Criar categoria cria também a pasta `<modules_root>/<nome limpo>` e acrescenta `{name, line}` ao fim; linha inválida vira `COZ`. Gravação atômica (temporário + `os.replace`). | categories.py:create/save |
| RN-07 | 🟢 Só categorias do usuário trocam de linha; a troca reescreve o arquivo e não altera módulos já salvos nem armários na cena. | ops_categories.py:BTM_OT_LibraryCategorySetLine.invoke; categories.py:set_line |
| RN-08 | 🟢 Modelo pronto válido exige `id` não vazio, `cabinet_type ∈ {BASE, WALL, TALL}` e `door_swing ∈ {NONE, LEFT, RIGHT, DOUBLE, FLIP}` (ausente = `NONE`); `width_mm` e `shelves` viram `int` com piso 0; `label` ausente = `id` (`label: null` vira "None"; `door_swing: null` é recusado como frente desconhecida _(Revisão 2026-10-10: sonda models_core.parse; models_core.py:225-228)_). Item inválido é pulado com aviso. | models_core.py:parse |
| RN-09 | 🟢 Inserir modelo pronto = `caffmob.cabinet_builder(cabinet_type, line, door_swing, shelves[, width])`, com `width = width_mm/1000` só quando `width_mm ≠ 0`; altura, profundidade, chapas e montagem vêm do padrão ativo na linha. Linha fora de `LINES` vira `COZ`. Não abre o editor de armário. | popover.py:BTM_OT_LibraryInsertModel.execute |
| RN-10 | 🟢 "Criar armário" abre diálogo com tipo, largura, montagem e linha; padrões: linha = `btm_library.line` (se válida, senão `COZ`), montagem = `standards.api.active_assembly(scene)`, largura = largura do padrão para a linha e o tipo atual. Confirmar cria pelo `cabinet_builder` (frente e prateleiras com os padrões do builder) e abre `caffmob.cabinet_editor` se `open_editor` e o poll do editor permitirem; cancelar não cria nada. | ops_cabinet.py:BTM_OT_LibraryCreateCabinet |
| RN-11 | 🟢 Ordem da coluna: [Converter grupos antigos, se houver oferta] → Criar armário → categorias (`CAT:<nome>`) → Criar categoria. | layout_core.py:menu_items |
| RN-12 | 🟢 Posição: com o HUD ligado, `x = borda direita do botão de navegação + 8·escala`; senão `x = x_min visível + 8·escala`; topo = `y_max visível − 12·escala`. Linhas de 24·escala, intervalo 2·escala, padding horizontal 12·escala. Fechado: só o rótulo; aberto: rótulo e itens com a mesma largura (a maior entre textos + 2·padding). | layout_core.py:panel_layout; draw.py:layout/_nav_right |
| RN-13 | 🟢 Clique no rótulo alterna aberto/fechado (abrir invalida o cache de categorias). Clique em item fecha o painel e executa a ação. Clique fora com o painel aberto fecha e deixa o clique seguir (seleção); com o painel fechado, só segue. Esc fecha quando aberto; fechado, o Esc não é consumido. | ops_click.py:dispatch/BTM_OT_LibraryClick/BTM_OT_LibraryClose |
| RN-14 | 🟢 Escolher uma categoria grava `btm_library.category` e `btm_library.line` (linha da categoria; desconhecida → `COZ`) e abre o popover dela. | ops_click.py:dispatch |
| RN-15 | 🟢 O popover mostra: cabeçalho (nome + "Linha: <rótulo>"; botão de engrenagem só para categoria do usuário), "Modelos prontos" em grade de 2 colunas (ícone `MESH_CUBE`, sem miniaturas), avisos do catálogo, "Meus módulos" (entradas de `library_io.list_modules()` cuja pasta casa com o nome por casefold, botão `caffmob.module_insert`, ícone `IMPORT`) ou a dica "Nenhum módulo salvo nesta categoria". | popover.py:_draw |
| RN-16 | 🟢 O título "BIBLIOTECA CAFFMOB" é nome próprio e não passa por tradução; rótulos dos itens passam por `tr`. | layout_core.py:TITLE; draw.py:items |
| RN-17 | 🟢 Criar/Trocar linha de categoria não entram no desfazer (`{'REGISTER'}`; alteram arquivo externo); Criar armário e Inserir modelo entram (`{'REGISTER', 'UNDO'}`). | ops_categories.py; ops_cabinet.py; popover.py |

## Requisitos Funcionais

🟡 Prioridades inferidas do roadmap da feature 012 (D-13 a D-18, D-30) e dos testes existentes; não constituem roadmap aprovado.

| ID | Requisito | Prioridade | Critério de aceite |
|---|---|---|---|
| RF-01 | 🟢 Painel desenhado em toda viewport 3D, com ou sem HUD, abrindo/fechando por clique, Esc ou clique fora | Must | CA-01, CA-02, CA-03 |
| RF-02 | 🟢 Categorias fixas + do usuário persistidas em `categories.json`, com migração de pastas soltas | Must | CA-04, CA-05 |
| RF-03 | 🟢 Criar categoria com validação do nome e escolha da linha | Must | CA-06, CA-07 |
| RF-04 | 🟢 Popover da categoria com modelos prontos e módulos salvos | Must | CA-08, CA-09 |
| RF-05 | 🟢 Inserir modelo pronto pelo padrão da linha da categoria | Must | CA-10, CA-11 |
| RF-06 | 🟢 Criar armário por diálogo e abrir o editor de armário | Must | CA-12, CA-13 |
| RF-07 | 🟢 Trocar a linha de uma categoria do usuário | Should | CA-14, CA-15 |
| RF-08 | 🟢 Oferecer "Converter grupos antigos" (topo da coluna e no diálogo Criar categoria) | Could | CA-16 |

## Requisitos Não Funcionais

| Tipo | Requisito observado | Evidência | Confiança |
|---|---|---|---|
| Desempenho do desenho | Não ler disco a cada quadro: categorias em cache até `invalidate()`; layout em cache por região com chave `(x_min, y_max, escala, aberto, itens, nav_right)`; oferta de grupos em cache no `legacy.groups` | categories.py:_cache; draw.py:layout; legacy/groups.py:should_offer | 🟢 |
| Desempenho do hover | Redesenhar a região só quando o alvo sob o mouse muda | ops_click.py:BTM_OT_LibraryHover.invoke | 🟢 |
| Não bloquear o host | Sem modal permanente: operadores curtos por keymap devolvem `PASS_THROUGH` fora do painel (o salvamento automático continua) | ops_click.py (docstring) | 🟢 |
| Integridade do arquivo | `categories.json` gravado por temporário na mesma pasta + `os.replace`; temporário removido em falha | categories.py:save | 🟢 |
| Separação do cálculo | `categories_core`, `models_core`, `layout_core` sem `bpy` (testáveis fora do Blender) | imports; tests/test_library_*.py | 🟢 |
| i18n | Textos de UI marcados com `N_`/`tr`; título sem tradução | categories_core.py; layout_core.py; draw.py | 🟢 |
| Ciclo de vida | `unregister` remove keymaps, operadores, handler, cache e a propriedade em `WindowManager` | __init__.py; draw.py:unregister; ops_click.py:unregister; props.py:unregister | 🟢 |

## Critérios de Aceitação

🟢 Cenários derivados do código atual. CA-01 a CA-03, CA-08, CA-12 e CA-13 são cobertos por `tests/blender_012_library_ui.py` (exige janela; não executado nesta extração). CA-04 a CA-07 e CA-10 parcialmente por testes puros. _(Revisão 2026-10-10: blender_012_library_ui executado com xvfb-run: OK, mas cobre CA-01, CA-02, CA-08 e CA-12; não exercita CA-03 (clique fora/Esc) nem CA-13. CA-10 e CA-11 conferidos por sonda e por blender_012_cabinet_standard_smoke (OK))_

```gherkin
CA-01 — Rótulo no canto, sem HUD
Dado HUD desligado, escala 1 e limites visíveis (x_min, y_max)
Quando a viewport desenha
Então o rótulo "BIBLIOTECA CAFFMOB" ocupa (x_min+8, y_max−12−24, largura do texto+24, 24)

CA-02 — Abrir e escolher
Dado o painel fechado
Quando clico no rótulo
Então btm_library.open fica verdadeiro e a coluna lista CREATE_CABINET, CAT:Cozinha, CAT:Banheiro, CAT:Sala, CAT:Home office, …, CREATE_CATEGORY

CA-03 — Clique fora e Esc
Dado o painel aberto
Quando clico fora do rótulo e dos itens (ou pressiono Esc)
Então o painel fecha; o clique segue para a seleção (PASS_THROUGH) e o Esc é consumido (FINISHED)
E com o painel fechado o Esc não é consumido (poll de library_close falso)

CA-04 — Pastas soltas
Dado categories.json com Lavanderia/DOR e as pastas Geral, Lavanderia, Cozinha e .oculta
Quando load() é chamado sem avisos de leitura
Então o resultado é [Lavanderia/DOR, Geral/COZ] e o arquivo é regravado com essa lista

CA-05 — Arquivo inválido
Dado categories.json com texto que não é JSON
Quando load() é chamado
Então as categorias do usuário são só as pastas soltas (COZ), há um aviso e o arquivo NÃO é regravado

CA-06 — Criar categoria
Dado o diálogo Criar categoria com nome " Closet " e linha DOR
Quando confirmo
Então surge a pasta <modules_root>/Closet, categories.json termina com {"name": "Closet", "line": "DOR"}, aparece INFO "Categoria criada: Closet" e o painel redesenha

CA-07 — Nome recusado
Dado as categorias fixas
Quando confirmo o nome "COZINHA" (ou "", ou "a/b")
Então o operador reporta WARNING com o motivo ("Já existe…", "Digite um nome…", "O nome não pode ter / nem \"), devolve CANCELLED e nada é gravado

CA-08 — Popover da categoria
Dado a categoria Cozinha
Quando clico nela no painel
Então btm_library.category = "Cozinha", btm_library.line = 'COZ', o painel fecha e o popover lista os 5 modelos do catálogo e os módulos da pasta Cozinha

CA-09 — Biblioteca indisponível
Dado list_modules levantando OSError ou ValueError
Quando o popover desenha
Então mostra "Biblioteca indisponível: <erro>" com ícone ERROR, sem quebrar os modelos prontos

CA-10 — Inserir modelo
Dado o modelo balcao_2p (BASE, 800 mm, DOUBLE, 1 prateleira) e a linha BAN
Quando aciono caffmob.library_insert_model(model_id='balcao_2p', line='BAN')
Então cabinet_builder recebe cabinet_type BASE, line BAN, door_swing DOUBLE, shelves 1, width 0.8 e o módulo é criado no cursor 3D

CA-11 — Modelo inexistente
Dado um model_id ausente do catálogo
Quando aciono caffmob.library_insert_model
Então reporta ERROR "Modelo não encontrado: <id>" e devolve CANCELLED sem criar nada

CA-12 — Criar armário
Dado a última categoria aberta com linha DOR e o modo OBJECT
Quando abro Criar armário e confirmo (Enter)
Então o diálogo veio com linha DOR, montagem do padrão ativo e largura do padrão; um módulo é criado e o editor de armário abre nele

CA-13 — Criar armário fora do modo objeto ou cancelado
Dado o modo EDIT (ou o diálogo cancelado)
Quando escolho Criar armário
Então nada é criado: em EDIT o poll falha e o clique só fecha o painel; cancelado, o diálogo fecha sem criar

CA-14 — Trocar linha
Dado a categoria do usuário Lavanderia/DOR
Quando uso a engrenagem do popover e escolho SAL
Então categories.json grava Lavanderia/SAL

CA-15 — Categoria fixa não troca de linha
Dado a categoria fixa Cozinha
Quando invoco caffmob.library_category_set_line(category="Cozinha")
Então reporta WARNING "Só as categorias do usuário trocam de linha" e devolve CANCELLED

CA-16 — Oferta de grupos
Dado legacy.groups.should_offer() verdadeiro
Quando abro o painel
Então "Converter grupos antigos" é o primeiro item; clicá-lo fecha o painel e invoca caffmob.legacy_groups_convert
E se legacy.groups não puder ser importado (ImportError/AttributeError/OSError) o item não aparece
```

## Prioridade (MoSCoW)

| Requisitos | Classificação | Justificativa |
|---|---|---|
| RF-01 a RF-06 | 🟡 Must | Ponto de entrada da biblioteca própria que substitui as bibliotecas herdadas na interface (ADR 0006; D-13 a D-18 da 012) |
| RF-07 | 🟡 Should | Ajuste de categoria do usuário; sem ele a linha fica a da criação |
| RF-08 | 🟡 Could | Oferta única de migração; o comando também existe no diálogo Criar categoria (D-30) |
| Galeria com miniaturas, rolagem da coluna | 🟡 Won't (nesta versão) | O popover usa botões sem miniatura; o layout não tem rolagem (D-15: galeria GPU foi alternativa descartada) |

## Rastreabilidade de Código e Verificação

| Arquivo | Símbolos / responsabilidade | Evidência |
|---|---|---|
| caffmob_draw/library_panel/__init__.py | `_modules`, `register`, `unregister` (ordem props→popover→ops_categories→ops_cabinet→ops_click→draw) | 🟢 Código |
| caffmob_draw/library_panel/props.py | `BTM_PG_LibraryState`, `WindowManager.btm_library` | 🟢 Código |
| caffmob_draw/library_panel/categories_core.py | `Category`, `LINES`, `FIXED`, `validate_name`, `parse`, `dump`, `merge_folders`, `with_line` | 🟢 Código; test_library_categories |
| caffmob_draw/library_panel/categories.py | `load`, `save`, `create`, `set_line`, `find`, `all_categories`, `invalidate` | 🟢 Código; fumaça UI |
| caffmob_draw/library_panel/models_core.py | `Model`, `parse`, `load_default`, `find` | 🟢 Código; test_library_models |
| caffmob_draw/library_panel/layout_core.py | `menu_items`, `panel_layout`, `hit`, `category_of`, `bounds` | 🟢 Código; test_library_layout |
| caffmob_draw/library_panel/draw.py | handler `POST_PIXEL`, `layout`, `items`, `offer_groups`, `tag_redraw` | 🟢 Código; validação visual pendente |
| caffmob_draw/library_panel/ops_click.py | `caffmob.library_click/library_hover/library_close`, keymap, `dispatch` | 🟢 Código; fumaça UI |
| caffmob_draw/library_panel/popover.py | `show`, `_draw`, `caffmob.library_insert_model` | 🟢 Código; fumaça UI |
| caffmob_draw/library_panel/ops_categories.py | `caffmob.library_category_create`, `caffmob.library_category_set_line` | 🟢 Código |
| caffmob_draw/library_panel/ops_cabinet.py | `caffmob.library_create_cabinet` | 🟢 Código; fumaça UI |
| caffmob_draw/data/library_models.json | 5 modelos, `schema-version` 1 | 🟢 Dado; test_library_models |

🟢 Executado em 2026-10-10: `cd tests && python3 -m unittest test_library_layout test_library_models test_library_categories -v` → **12 testes aprovados** (layout 5, modelos 2, categorias 5). `tests/blender_012_library_ui.py` (precisa de janela e `--enable-event-simulate`) não foi executado. _(Revisão 2026-10-10: executado com xvfb-run no Blender 5.2.0 LTS: 9 verificações OK)_

## Lacunas e Pré-condições

- 🟢 Comportamento com muitas categorias: sem rolagem nem limite, itens podem sair da área visível e ficar inalcançáveis (EC-05). 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-88):** limitar a coluna à altura visível e, acima disso, agrupar as categorias do usuário num item "Mais…" que abre um popover (sem rolagem em GPU). Pendência de implementação: DT-03.
- 🟢 Várias janelas/viewports: estado `open` e `_open['category']` são globais por `WindowManager`/processo; não exercitado. 🟢 **Decisão do titular (2026-10-10, questions.md#pergunta-89):** aceito por ora o estado único por `WindowManager` com várias viewports/janelas (uso típico é uma viewport).
- 🟡 decisão: testar (DT-04) — **Decisão do titular (2026-10-10, questions.md#pergunta-89):** acrescentar à fumaça de UI um caso com o HUD ligado para fixar a ordem do keymap. Ordem efetiva do keymap com o HUD e a seleção por componente (todos `head=True`) só verificável no Blender.
- 🟢 Pré-condição: `customize.library_io.modules_root()` disponível (cria a pasta via `extension_path_user`); `operators.cabinet_builder` e `standards.api` registrados.
