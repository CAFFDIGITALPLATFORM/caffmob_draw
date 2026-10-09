# Requirements: Biblioteca CAFFMob flutuante e armários por chapas no padrão global

> Identificador: `012-biblioteca-caffmob-chapas`
> Data: `2026-10-09`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA
> Origem: pedido do titular no `/reversa-audit` da 011 e respostas às 3 perguntas da pré-checagem
> (`_reversa_forward/011-selecao-por-componente/audit/cross-check.md`, seção "Fora do escopo").
> Anexos: padrão Promob `PROMOB_CONFIGURAÇÃO_MEDIDAS_MEMOVEIS.dimensionExport` (idêntico a
> `tests/fixtures/dimensionexport_me_moveis.xml`) e o manifesto "Software Planejado".

## 1. Resumo executivo

Para o projetista, a feature tem três partes:
- **Biblioteca CAFFMob:** a biblioteca de módulos sai da barra lateral e vira um painel flutuante compacto no topo da
  viewport, fechado mostrando só "BIBLIOTECA CAFFMOB". Aberto, o primeiro botão é **Criar armário**, seguido das
  categorias Cozinha, Banheiro, Sala, Home office e **Criar categoria**.
- **Armários por chapas no padrão global:** todo armário é montado com as chapas, as espessuras e as medidas do padrão
  de dimensões ativo (o padrão Promob do titular). A montagem pode ser **lateral passante** ou **base passante**, no
  padrão global e por armário. Mudar o padrão pergunta se os móveis da cena devem ser atualizados.
- **Só armários CAFFMob:** as bibliotecas herdadas (frameless, face frame e closets) saem da interface. Todo armário é
  um módulo CAFFMob, montado pelo padrão global. Arquivos antigos oferecem converter os armários dessas bibliotecas
  em módulos CAFFMob.

Resolve quatro problemas do legado:
- a biblioteca disputa espaço com o resto da barra lateral;
- o módulo rápido e o face frame ignoram o padrão;
- a regra de montagem é fixa (lateral passante);
- três bibliotecas paralelas, cada uma com regras e telas próprias, dificultam seguir um padrão só.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_forward/001-addon-moveis-planejados/requirements.md#RN-03` | Construção brasileira padrão: laterais passantes; chapa de 15 ou 18 mm por peça; fundo de 6 mm encaixado | 🟢 |
| `_reversa_forward/001-addon-moveis-planejados/interfaces/promob-dimensionexport.md` | Leitura e gravação do `.dimensionExport`; IDs não mapeados são guardados crus | 🟢 |
| `caffmob_draw/standards/` (`model.py`, `api.py`, `sync.py`, `io_promob.py`) | Padrão ativo por projeto em `Scene.btm_standards` (cena principal); `sync.apply_definition` atualiza módulos frameless e closets existentes, pulando valores editados à mão (`btm_overrides`) | 🟢 |
| `caffmob_draw/data/dimension_schema.py` (l. 24, 62-88, 139, 162-180) | Linhas COZ, DOR, BAN, SAL, ESC; componentes LAT, DIV, BAS, FUN_*, TAMP, PRAT, POR…; só COZ (frameless) e DOR (closets) têm consumidor; BAN, SAL e ESC são guardadas e não usadas | 🟢 |
| `caffmob_draw/operators/ops_standards.py` (l. 110-243) | "Configurador" e "Definir e aplicar" já perguntam ao aplicar, com a contagem de módulos (`sync.affected_modules`), que só conta frameless e closets | 🟢 |
| `caffmob_draw/cabinet_editor/structure.py#layout` (l. 85-97); `cutting/part_sources.py#synthetic_records` (l. 207-236) | Módulo rápido e editor de armário (008): laterais na altura inteira; base e tampo entre as laterais. A lista de corte repete essa regra | 🟢 |
| `caffmob_draw/product_libraries/frameless/types_frameless.py#create_base_carcass` (l. 125-257) | Frameless: base, tampo e travessas com `largura − 2 × espessura` (laterais passantes), por drivers | 🟢 |
| `caffmob_draw/operators/cabinet_builder.py` (l. 8-24) | "Módulo rápido" (`caffmob.cabinet_builder`): cria um armário no cursor 3D com 0,8 × 0,7 × 0,55 fixos; do padrão, lê só a espessura da lateral | 🟢 |
| `caffmob_draw/ui/sidebar_insert.py`; `customize/library_io.py` (l. 21-44) | Biblioteca hoje na seção Inserir da barra lateral. Os módulos do usuário ficam em `extension_path_user(…, "modules")/<categoria>/`, e categoria é só o nome da pasta | 🟢 |
| `caffmob_draw/operators/viewport_hud.py` (l. 547-744); `operators/scene_navigator.py` | O HUD do topo da viewport desenha botões em linhas e um painel fixável (navegador de cenas), com clique pelo keymap sem modal permanente | 🟢 |
| `_reversa_sdd/ui/requirements.md#Regras de Negócio` | Interface da barra lateral e painéis do legado | 🟡 |
| `_reversa_sdd/frameless/requirements.md`; `caffmob_draw/product_libraries/` | Bibliotecas herdadas (frameless, face frame, closets), cada uma com tipos, operadores, modos de seleção e propriedades de cena próprios | 🟢 |
| Levantamento de 2026-10-09 (`grep` por `hb_frameless`, `hb_face_frame`, `hb_closets`, `IS_FRAMELESS`, `IS_FACE_FRAME`, `IS_CLOSET`, `product_tab`) | Cerca de 35 arquivos fora de `product_libraries/` dependem delas: padrão (`standards/sync.py`), lista de corte (`cutting/part_sources.py`), inspeção, molduras, layouts, exportação, HUD, barra lateral, seleção (`selection/classify.py`, `component_select.py`), catálogo e personalização | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de marcenaria | Montar o ambiente sem procurar a biblioteca na barra lateral | Abre "BIBLIOTECA CAFFMOB" no topo da viewport, entra em Cozinha e põe um balcão já com as chapas e medidas do padrão |
| Projetista que cria os próprios módulos | Ter um armário novo do jeito da fábrica dele | Clica em **Criar armário**: o armário nasce com espessuras, altura e profundidade do padrão ativo e montagem lateral passante; muda para base passante só nesse armário |
| Dono da marcenaria (padrão da fábrica) | Trocar o padrão de chapas da empresa | Importa o `.dimensionExport` novo e define como ativo. O sistema pergunta se aplica aos móveis da cena e, havendo móveis com padrão próprio, faz uma segunda pergunta |
| Projetista que organiza a biblioteca | Separar os módulos por ambiente | Cria a categoria "Lavanderia" e salva nela um módulo montado |

## 4. Regras de negócio novas ou alteradas

### Biblioteca CAFFMob

1. **RN-01, painel flutuante.** A biblioteca de módulos fica num painel flutuante no topo da viewport 3D, fora da barra
   lateral (CAFFMob Draw). Fechado, ele é compacto e mostra só o rótulo **BIBLIOTECA CAFFMOB**; clicar abre e fecha.
   Ele aparece **sempre**, em toda viewport 3D, com ou sem o HUD ligado nas preferências. 🟢
   (Esclarecimentos 2026-10-09, sessão 2, Q4)
   - Origem no legado: `ui/sidebar_insert.py`; `operators/viewport_hud.py`, `operators/scene_navigator.py`
   - Tipo: alterada
2. **RN-02, ordem do conteúdo.** Aberto, o painel mostra nesta ordem:
   1. o botão **Criar armário**;
   2. as categorias **Cozinha**, **Banheiro**, **Sala** e **Home office**, e depois as criadas pelo usuário;
   3. o botão **Criar categoria**.

   Clicar numa categoria mostra os módulos dela para inserir na cena:
   - os modelos prontos da CAFFMob (RN-15), montados pelo padrão na linha da categoria;
   - os módulos que o usuário salvou naquela categoria.

   A biblioteca de objetos (009: SketchUp, decoração) continua separada e não entra nas categorias. 🟢
   (Esclarecimentos 2026-10-09, sessão 2, Q3)
   - Tipo: nova
3. **RN-03, categoria e linha do padrão.** Cada categoria usa uma linha do padrão de dimensões:
   - Cozinha → COZ;
   - Banheiro → BAN;
   - Sala → SAL;
   - Home office → ESC.

   Uma categoria criada pelo usuário usa a linha escolhida ao criá-la (Cozinha, Dormitório, Banheiro, Sala ou
   Escritório), e a linha pode ser trocada depois. 🟢 (Esclarecimentos 2026-10-09, sessão 2, Q1)
   - Origem no legado: `data/dimension_schema.py` (linhas COZ, DOR, BAN, SAL, ESC)
   - Tipo: nova
4. **RN-04, criar categoria.** "Criar categoria" pede um nome e a linha do padrão (RN-03) e cria uma categoria na biblioteca do usuário, que fica
   disponível em todos os projetos. Nome repetido ou vazio é recusado com o motivo. 🟡
   - Origem no legado: `customize/library_io.py` (categoria = pasta em `extension_path_user`)
   - Tipo: alterada
5. **RN-05, Criar armário.** "Criar armário" abre um diálogo curto, já preenchido com o padrão ativo:
   - tipo: balcão, aéreo ou torre;
   - largura;
   - montagem: lateral passante ou base passante (o padrão global vem marcado).

   Ao confirmar, o armário nasce no cursor 3D, montado por chapas no padrão (RN-06 a RN-08), e o editor de armário
   (008) abre nele para os ajustes. Cancelar não cria nada. 🟢 (Esclarecimentos 2026-10-09, sessão 2, Q2)
   - Origem no legado: `operators/cabinet_builder.py`; `cabinet_editor/ops_editor.py`
   - Tipo: alterada

### Armários por chapas no padrão global

6. **RN-06, sempre por chapas.** Todo armário é montado por chapas: cada peça da carcaça (laterais, base, tampo,
   fundo, divisórias, prateleiras) é uma chapa. A espessura e o material vêm do componente correspondente do padrão
   ativo, na linha da categoria do armário. 🟢
   - Origem no legado: `_reversa_forward/001-addon-moveis-planejados/requirements.md#RN-03`; `cabinet_editor/bridge.py#configured_part`
   - Tipo: alterada (o módulo rápido passa a ler todas as chapas, não só a lateral)
7. **RN-07, medidas do padrão.** Altura, profundidade e altura de instalação de um armário novo vêm das medidas
   externas do padrão ativo, por tipo: balcão, aéreo, torre e ilha. Nenhum valor fixo no código decide a medida
   (manifesto: "evite o pregado"). 🟡
   - Origem no legado: `data/dimension_schema.py` (l. 139); `operators/cabinet_builder.py` (0,8 × 0,7 × 0,55 fixos)
   - Tipo: alterada
8. **RN-08, montagem passante.** A montagem tem duas regras:
   - **lateral passante** (como hoje): as laterais vão do piso ao topo, e base e tampo ficam entre elas;
   - **base passante**: a base ocupa a largura toda, e as laterais ficam em cima dela.

   A escolha fica no padrão global (padrão inicial: lateral passante, RN-03 da 001) e pode ser trocada por armário.
   A lista de corte segue a regra de cada armário. Vale para **todos** os armários, porque todos passam a ser módulos
   CAFFMob (RN-12). 🟢 (Respostas do titular, item 2; Esclarecimentos sessão 3, Q1)
   - Origem no legado: `cabinet_editor/structure.py#layout`; `cutting/part_sources.py#synthetic_records`
   - Tipo: nova
   - O `.dimensionExport` do Promob não tem esse atributo: o valor é guardado no padrão do CAFFMob (e exportado num
     atributo próprio, sem afetar a importação no Promob).
9. **RN-09, armário com padrão próprio.** Um armário pode ter espessuras, medidas e montagem diferentes do padrão
   global. Ele fica marcado como "padrão próprio" e guarda contra qual padrão global foi personalizado. 🟢
   (Respostas do titular, item 2)
   - Origem no legado: `standards/sync.py` (`btm_overrides`, valores editados à mão)
   - Tipo: alterada
10. **RN-10, mudar o padrão global pergunta.** Ao mudar o padrão global (trocar o ativo, editar ou importar), o
    sistema pergunta:
    1. **"Aplicar a todos os módulos existentes na cena?"** (Sim / Não). Não: só os armários novos usam o padrão.
    2. Se houver armários com padrão próprio diferente do padrão global anterior, uma segunda pergunta: **"Aplicar
       também nos móveis que diferem do padrão global anterior?"** (Sim / Não). Não: esses ficam como estão.

    🟢 (Respostas do titular, itens 1 e 2)
    - Origem no legado: `operators/ops_standards.py` (confirmação com contagem e `include_manual`)
    - Tipo: alterada
11. **RN-11, abrangência.** A aplicação vale para todos os móveis da cena:
    - os módulos CAFFMob (Criar armário, modelos prontos, módulo rápido);
    - os que o usuário criou ou montou (editor de armário, módulos salvos);
    - os convertidos das bibliotecas herdadas (RN-13).

    Armários herdados ainda não convertidos, itens importados (SketchUp, OBJ) e objetos da biblioteca de objetos não
    mudam e entram na contagem como "não aplicável" (o herdado com a dica "converta para CAFFMob"). 🟢
    (Respostas do titular, item 3; Esclarecimentos sessão 3)
    - Origem no legado: `standards/sync.py#affected_modules` (hoje só frameless e closets)
    - Tipo: alterada

### Só armários CAFFMob

12. **RN-12, bibliotecas herdadas fora da interface.** Frameless, face frame e closets saem de toda a interface:
    - galerias e seletor de biblioteca (`product_tab`);
    - modos de seleção delas na barra lateral e no HUD;
    - menus de contexto e atalhos de criação;
    - padrões de estilo e opções delas;
    - a biblioteca de molduras (perfis e madeira maciça) e os pacotes de moldura do ambiente, que dependem delas.

    Nenhum armário novo dessas bibliotecas pode ser criado. A seleção por componente (011) passa a valer para todo
    armário, já que o módulo CAFFMob não tem modo de seleção (011 RN-04 deixa de depender dos modos herdados). 🟢
    (Esclarecimentos sessão 3, Q1)
    - Origem no legado: `product_libraries/`; `ui/view3d_sidebar.py`; `operators/viewport_hud.py`
    - Tipo: removida (da interface)
13. **RN-13, converter arquivos antigos.** Ao abrir um arquivo com armários das bibliotecas herdadas, o sistema avisa
    quantos são e oferece **Converter para CAFFMob**. A mesma ação fica na barra lateral enquanto houver armário
    herdado. A conversão de cada armário:
    1. cria um módulo CAFFMob com as mesmas medidas externas, posição, rotação e parede de origem;
    2. usa a linha do armário (`btm_line`, ou COZ; closets → DOR), o padrão ativo e montagem lateral passante;
    3. mantém a quantidade de portas e gavetas quando o módulo CAFFMob sabe fazer; o que ele não sabe (estilo de porta,
       acessório específico, frente especial) vai para um relatório por armário;
    4. remove o armário herdado.

    Tudo numa etapa só de desfazer. Recusar deixa os armários como estão ("não aplicável" na RN-11). Gavetas e frentes
    que o módulo CAFFMob não tem viram perda no relatório (gavetas no CAFFMob ficam para a feature 013). 🟢
    (Esclarecimentos sessões 3 e 4)
    - Tipo: nova
14. **RN-14, código herdado só para converter.** O código das bibliotecas herdadas fica no pacote nesta feature,
    usado só para abrir arquivos antigos e converter. A remoção do código é de uma feature seguinte, com as fumaças de
    prova. 🟢 (Esclarecimentos sessão 3, Q3)
    - Tipo: nova
15. **RN-15, modelos prontos CAFFMob.** No lugar das galerias herdadas, cada categoria mostra modelos prontos da
    CAFFMob, gerados pelo mesmo caminho do Criar armário, com o padrão na linha da categoria:
    - balcão 1 porta, balcão 2 portas;
    - aéreo 1 porta, aéreo 2 portas;
    - torre.

    A lista é um catálogo de dados (princípio III), que cresce sem mudar código. O balcão gaveteiro entra quando o
    módulo CAFFMob tiver gavetas (feature 013). 🟢 (Esclarecimentos sessão 4, Q1)
    - Origem no legado: `cabinet_editor/catalog.py` (catálogo do Construtor 008)
    - Tipo: nova
16. **RN-16, converter os grupos salvos.** Os grupos que o usuário salvou nas bibliotecas herdadas ("Grupos frameless"
    e "Grupos face frame" de "Meus módulos") também são convertidos. A conversão:
    1. abre cada grupo salvo, converte os armários dele pela RN-13 e salva o resultado como módulo CAFFMob na
       biblioteca do usuário, na categoria "Geral" (linha COZ), com o mesmo nome e a miniatura refeita;
    2. não apaga o arquivo original do grupo (fica para a remoção do código, RN-14);
    3. faz um relatório por grupo, com as perdas.

    Ela é oferecida uma vez, na primeira vez que o painel abre com grupos herdados salvos, e fica disponível em
    "Criar categoria" › "Converter grupos antigos". 🟡 (Esclarecimentos sessão 4, Q3)
    - Origem no legado: `ui/my_modules.py`; `product_libraries/frameless/operators/ops_library.py#get_user_library_path`
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Painel flutuante "BIBLIOTECA CAFFMOB" no topo da viewport, sempre visível, compacto quando fechado, fora da barra lateral (RN-01) | Must | Com a extensão ativa, com o HUD ligado ou desligado, a viewport mostra o rótulo no topo; clicar abre e fecha; a seção Inserir da barra lateral não mostra mais o catálogo de módulos | 🟢 |
| RF-02 | Aberto: Criar armário, categorias fixas, categorias do usuário e Criar categoria, nessa ordem; cada categoria lista os modelos prontos CAFFMob e os do usuário (RN-02, RN-15) | Must | A ordem dos botões confere; clicar em Cozinha lista os 5 modelos prontos e os módulos salvos em Cozinha, sem itens da biblioteca de objetos nem das bibliotecas herdadas | 🟢 |
| RF-03 | Criar categoria com nome e linha do padrão, salva na biblioteca do usuário (RN-03, RN-04) | Must | "Lavanderia" com a linha Dormitório aparece depois de Home office, também num arquivo novo, e um armário criado nela usa as chapas de DOR; nome vazio ou repetido mostra o motivo | 🟢 |
| RF-04 | Criar armário: diálogo (tipo, largura, montagem) preenchido pelo padrão; ao confirmar, o armário nasce no cursor e o editor de armário abre (RN-05) | Must | Clicar em Criar armário, escolher balcão de 600 mm e confirmar cria um balcão de 600 mm com a altura e a profundidade de balcão do padrão e abre o editor nele; Cancelar não cria objeto | 🟢 |
| RF-05 | Armário novo com todas as chapas e medidas do padrão ativo na linha da categoria (RN-06, RN-07) | Must | Com o padrão do titular ativo, um balcão de Cozinha nasce com a altura e a profundidade de balcão do padrão e com lateral, base, tampo e fundo nas espessuras de COZ | 🟡 |
| RF-06 | Montagem lateral passante ou base passante, no padrão global e por armário, refletida na geometria e na lista de corte (RN-08) | Must | Balcão de 800 mm com chapa de 18 mm: com lateral passante, a base mede 764 mm e as laterais a altura toda; com base passante, a base mede 800 mm e as laterais a altura menos 18 mm | 🟡 |
| RF-07 | Armário com padrão próprio marcado, com referência ao padrão global de origem (RN-09) | Must | Mudar a espessura da lateral de um armário o marca como "padrão próprio"; a seção Selecionado mostra a marca | 🟢 |
| RF-08 | Mudar o padrão global faz a primeira pergunta e aplica ou não aos módulos da cena (RN-10.1) | Must | Com 5 armários na cena, trocar o padrão e responder Sim refaz os 5; responder Não mantém os 5 e só os novos usam o padrão novo | 🟢 |
| RF-09 | Segunda pergunta quando há armários com padrão próprio (RN-10.2) | Must | Com 1 desses 5 em padrão próprio: a segunda pergunta aparece; Sim aplica também nele; Não o mantém | 🟢 |
| RF-10 | Aplicação para todos os módulos CAFFMob da cena, com "não aplicável" para importados e herdados não convertidos (RN-11) | Must | A contagem da pergunta soma os módulos CAFFMob; um OBJ importado e um frameless não convertido aparecem como não aplicáveis e não mudam | 🟢 |
| RF-11 | Importar o `.dimensionExport` do titular sem perda e exportar de volta com a montagem passante (RN-08) | Should | Importar o anexo e reexportar mantém os 692 atributos; o arquivo ganha só o atributo da montagem | 🟢 |
| RF-12 | Guia do usuário: biblioteca flutuante, categorias, Criar armário, montagem passante, as perguntas ao mudar o padrão e a conversão de arquivos antigos | Should | `docs/usuario/` atualizado; guias das bibliotecas herdadas marcados como descontinuados | 🟢 |
| RF-13 | Bibliotecas herdadas e a biblioteca de molduras fora da interface (RN-12) | Must | Nenhum painel, menu, botão do HUD ou atalho cria ou mostra frameless, face frame, closets ou a biblioteca de molduras; as fumaças das features 001 a 011 continuam verdes | 🟢 |
| RF-14 | Converter para CAFFMob, com aviso ao abrir e relatório por armário (RN-13) | Must | Um arquivo com 3 frameless, 1 face frame e 1 closet abre com o aviso "5 armários de bibliotecas antigas"; converter deixa 5 módulos CAFFMob nas mesmas posições e medidas externas; Ctrl+Z volta os 5 originais | 🟡 |
| RF-15 | Modelos prontos CAFFMob por categoria, de um catálogo de dados (RN-15) | Must | Cozinha mostra os 5 modelos; um balcão 2 portas inserido em Banheiro tem as chapas de BAN | 🟢 |
| RF-16 | Converter os grupos salvos das bibliotecas herdadas em módulos CAFFMob da biblioteca do usuário (RN-16) | Must | Com 2 grupos frameless salvos, a conversão cria 2 módulos em "Geral", com o mesmo nome e miniatura; os arquivos originais continuam na pasta; o relatório lista as perdas | 🟡 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | O painel fechado não pesa na viewport: desenhar e responder ao mouse em menos de 1 ms por quadro; aplicar o padrão a 50 armários em menos de 5 s, com uma etapa só de desfazer | O HUD redesenha a cada quadro (`viewport_hud.py`); `sync.apply_definition` refaz módulos | 🟡 |
| Compatibilidade | Arquivos antigos abrem iguais: armários existentes ficam com lateral passante (a montagem de hoje) e nada é refeito sem a pergunta | RN-03 da 001; RN-10 | 🟢 |
| Persistência | Categorias e módulos do usuário ficam em `extension_path_user` (todos os projetos); o padrão ativo e a montagem por armário ficam no arquivo do projeto | `customize/library_io.py`; `standards/model.py` | 🟢 |
| Design (/impeccable) | Painel compacto, sem cobrir a área de trabalho: fechado ocupa uma linha; aberto, uma coluna que fecha com Esc ou ao clicar fora; segue o visual do HUD | Padrão do HUD e das features 008 a 011; manifesto: "esconder as ferragens" | 🟡 |
| Internacionalização | Textos em pt-BR e en-US; "BIBLIOTECA CAFFMOB" é nome próprio e não se traduz | `CLAUDE.md` | 🟢 |
| Testes | Núcleos puros (peças da carcaça por montagem, mapeamento categoria → linha, decisão das duas perguntas) testados fora do Blender; fumaças do painel (com eventos simulados), da aplicação do padrão e da lista de corte | Padrão 004 a 011 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Painel compacto no topo da viewport
  Dado a extensão ativa e uma cena aberta
  Quando o projetista olha a viewport
  Então vê só o rótulo "BIBLIOTECA CAFFMOB" no topo
  E ao clicar nele vê, em ordem, Criar armário, Cozinha, Banheiro, Sala, Home office e Criar categoria

Cenário: Criar categoria
  Dado o painel aberto
  Quando o projetista cria a categoria "Lavanderia" com a linha Dormitório
  Então "Lavanderia" aparece depois de Home office, também ao abrir outro projeto
  E um armário criado em Lavanderia usa as chapas da linha Dormitório

Cenário: Categoria com nome repetido
  Dado a categoria "Cozinha"
  Quando o projetista tenta criar outra "Cozinha"
  Então a categoria não é criada e o motivo aparece

Cenário: Criar armário pelo diálogo
  Dado o padrão do titular ativo e o painel aberto
  Quando o projetista clica em Criar armário, escolhe balcão de 600 mm com lateral passante e confirma
  Então um balcão de 600 mm nasce no cursor 3D com a altura e a profundidade de balcão do padrão
  E o editor de armário abre nele

Cenário: Cancelar Criar armário
  Dado o diálogo de Criar armário aberto
  Quando o projetista cancela
  Então nenhum objeto é criado

Cenário: Painel sem o HUD
  Dado o HUD da viewport desligado nas preferências
  Quando o projetista olha a viewport
  Então o rótulo "BIBLIOTECA CAFFMOB" continua no topo

Cenário: Armário novo no padrão
  Dado o padrão do titular ativo
  Quando o projetista põe um balcão de Cozinha de 800 mm
  Então as chapas têm as espessuras de COZ e o balcão tem a altura e a profundidade de balcão do padrão

Cenário: Base passante
  Dado um balcão de 800 mm com chapa de 18 mm
  Quando o projetista muda a montagem desse armário para base passante
  Então a base passa a medir 800 mm e as laterais a altura menos 18 mm, na vista e na lista de corte
  E o armário fica marcado como padrão próprio

Cenário: Mudar o padrão e aplicar
  Dado 5 armários na cena, todos no padrão global
  Quando o projetista define outro padrão como ativo e responde Sim
  Então os 5 armários são refeitos com o padrão novo

Cenário: Mudar o padrão sem aplicar
  Dado 5 armários na cena
  Quando o projetista define outro padrão como ativo e responde Não
  Então os 5 ficam como estavam e o próximo armário inserido usa o padrão novo

Cenário: Segunda pergunta para armários com padrão próprio
  Dado 5 armários na cena, 1 deles com base passante própria
  Quando o projetista muda o padrão global e responde Sim à primeira pergunta
  Então aparece "Aplicar também nos móveis que diferem do padrão global anterior?"
  E respondendo Não, o armário de padrão próprio fica como está e os outros 4 mudam

Cenário: Bibliotecas herdadas fora da interface
  Dado a extensão instalada num arquivo novo
  Quando o projetista procura frameless, face frame ou closets na barra lateral, no HUD e nos menus
  Então não encontra nenhum deles

Cenário: Converter um arquivo antigo
  Dado um arquivo com 3 armários frameless, 1 face frame e 1 closet
  Quando o projetista abre o arquivo e escolhe Converter para CAFFMob
  Então ficam 5 módulos CAFFMob nas mesmas posições e com as mesmas medidas externas
  E o relatório lista o que cada armário perdeu (por exemplo, estilo de porta)
  E um Ctrl+Z volta os 5 armários originais

Cenário: Não converter
  Dado o mesmo arquivo antigo
  Quando o projetista recusa a conversão
  Então os 5 armários ficam como estão e aparecem como "não aplicável" ao aplicar o padrão

Cenário: Converter grupos salvos
  Dado 2 grupos frameless salvos em "Meus módulos" (um deles com gavetas)
  Quando o projetista abre o painel e aceita "Converter grupos antigos"
  Então "Geral" passa a ter 2 módulos CAFFMob com os mesmos nomes
  E o relatório diz que as gavetas do segundo grupo foram perdidas
  E os 2 arquivos originais continuam na pasta da biblioteca antiga

Cenário: Biblioteca de molduras fora da interface
  Dado uma cena de detalhe de moldura
  Quando o projetista abre a barra lateral
  Então a biblioteca de molduras e os pacotes de moldura do ambiente não aparecem

Cenário: Modelo pronto na categoria
  Dado o padrão do titular ativo
  Quando o projetista insere o balcão 2 portas pela categoria Banheiro
  Então o balcão tem as chapas e as medidas de balcão da linha BAN

Cenário: Item importado não muda
  Dado um OBJ importado e 2 armários na cena
  Quando o projetista aplica um padrão novo
  Então os 2 armários mudam, o OBJ não, e a pergunta mostra 1 item não aplicável
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-04 | Must | Núcleo pedido: biblioteca fora da barra lateral, com Criar armário e categorias |
| RF-05, RF-06 | Must | Núcleo pedido: armário por chapas no padrão, com montagem passante |
| RF-07, RF-08, RF-09, RF-10 | Must | Respostas do titular sobre aplicar o padrão |
| RF-03 | Must | Pedido explícito ("criar categoria") |
| RF-13, RF-14, RF-15, RF-16 | Must | Decisão do titular (sessões 3 e 4): só armários CAFFMob, com conversão dos antigos e dos grupos salvos |
| RF-11 | Should | O padrão do titular já é importado; falta só gravar a montagem |
| RF-12 | Should | Guia do usuário |
| RNF de desempenho | Should | Painel redesenhado a cada quadro |

## 9. Esclarecimentos

### Sessão 2026-10-09 (pré-checagem do `/reversa-audit` da 011)

- **Q:** Os armários já colocados mudam quando o padrão global muda, ou só os novos seguem o padrão?
  **R:** Ao mudar o padrão global, perguntar "Aplicar a todos os módulos existentes na cena?" (Sim / Não) (RN-10).
- **Q:** Base passante ou lateral passante é escolhido por módulo, por categoria ou só no padrão global?
  **R:** No padrão global e, claro, por armário. Ao mudar o padrão global, se houver armários com padrão diferente do
  global anterior, fazer outra pergunta: "Aplicar em todos os móveis, até nos que diferem do global anterior?"
  (Sim / Não) (RN-08, RN-09, RN-10).
- **Q:** As categorias trazem só armários do CAFFMob, ou também itens da biblioteca de objetos?
  **R:** Todos: os do CAFFMob, os que o usuário criou ou montou e os demais presentes na cena (RN-11).

### Sessão 2026-10-09 (2)

- **Q:** Uma categoria criada pelo usuário usa qual linha do padrão de dimensões?
  **R:** A linha é escolhida ao criar a categoria, e pode ser trocada depois (RN-03, RN-04, RF-03).
- **Q:** O que o botão "Criar armário" faz?
  **R:** Abre um diálogo (tipo, largura, montagem) preenchido pelo padrão; ao confirmar, o armário nasce no cursor e o
  editor de armário abre (RN-05, RF-04).
- **Q:** O que aparece dentro de cada categoria do painel?
  **R:** Os módulos prontos da CAFFMob da linha e os módulos salvos pelo usuário; a biblioteca de objetos continua
  separada (RN-02, RF-02).
- **Q:** O painel aparece sempre, ou só com o HUD ligado?
  **R:** Sempre, em toda viewport 3D (RN-01, RF-01).

### Sessão 2026-10-09 (3)

- **Q:** A base passante vale só para os módulos CAFFMob ou também para o frameless?
  **R:** O frameless deve ser removido; fica só o CAFFMob, e todos os armários seguem as configurações globais,
  inclusive base passante e lateral passante (RN-08, RN-12).
- **Q:** Quais bibliotecas saem?
  **R:** Frameless, face frame e closets (RN-12).
- **Q:** O que acontece com arquivos antigos que já têm esses armários?
  **R:** Converter em CAFFMob, com as mesmas medidas, posição e padrão; o relatório diz o que se perdeu (RN-13).
- **Q:** O código das bibliotecas removidas sai agora ou só some da interface?
  **R:** Some da interface agora; o código sai numa feature seguinte (RN-14).

### Sessão 2026-10-09 (4, depois do `/reversa-audit`)

- **Q:** O módulo CAFFMob não tem gavetas: como ficam o balcão gaveteiro e as gavetas dos armários convertidos?
  **R:** Gavetas numa feature própria (013). A 012 sai com 5 modelos prontos; na conversão, gavetas viram perda no
  relatório (RN-13, RN-15, RF-02, RF-15).
- **Q:** A biblioteca de molduras, que usa operadores do frameless, fica ou sai?
  **R:** Sai junto com as bibliotecas herdadas (RN-12, RF-13).
- **Q:** Os grupos salvos das bibliotecas antigas ("Meus módulos") ficam inacessíveis?
  **R:** Converter (RN-16, RF-16).

## 10. Lacunas

- Nenhuma dúvida aberta. O manifesto anexo virou `.reversa/principles.md` (I a XI) em 2026-10-09.
- 🟡 A categoria de destino dos grupos convertidos ("Geral", linha COZ) e o momento da oferta (primeira abertura do
  painel) são propostas (RN-16).
- 🟡 O que a conversão consegue manter de portas e gavetas (RN-13) só se conhece medindo o módulo CAFFMob contra os
  tipos herdados; o relatório por armário cobre o que ficar de fora.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-requirements`, com as 3 respostas da pré-checagem da 011 | reversa |
| 2026-10-09 | `/reversa-clarify`: linha da categoria nova, diálogo de Criar armário, conteúdo das categorias, painel sempre visível | reversa |
| 2026-10-09 | Sessão 3 (decisão do titular depois do plano): só armários CAFFMob, bibliotecas herdadas fora da interface, conversão de arquivos antigos, modelos prontos; RN-12 a RN-15, RF-13 a RF-15; 694 → 692 atributos | reversa |
| 2026-10-09 | Sessão 4 (respostas ao cross-check A001 a A003): 5 modelos sem gaveteiro, gavetas na 013, biblioteca de molduras fora, conversão dos grupos salvos (RN-16, RF-16) | reversa |

## Pendências de Qualidade

- RF-11 (reexportar o `.dimensionExport` com a montagem) não tem cenário Gherkin; o critério de aceite da tabela
  (692 atributos mantidos) vale até lá.
