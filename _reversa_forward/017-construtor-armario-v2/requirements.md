# Requirements: Construtor de armário v2 no CAFFMob Draw

> Identificador: `017-construtor-armario-v2`
> Data: `2026-11-19`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

> **Prevalência da especificação.** O material anexado pelo titular em
> `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/`
> (`__init__.py`, `blender_manifest.toml`, `mockup_construtor_armarios.html` e `assets/slide-st48-0200-0.obj`)
> é a especificação que prevalece. Onde ele divergir do que o construtor atual do pacote faz, este documento
> descreve o comportamento novo; onde ele não disser nada, vale o que a extração reversa confirmou.

## 1. Resumo executivo

O construtor de armário de hoje é um editor que monta o módulo pelas bibliotecas paramétricas do pacote: cada
biblioteca reconstrói as próprias chapas e o editor só empilha pedidos numa fila até o OK. O resultado é um
construtor amarrado à biblioteca do módulo, com regras de peça espalhadas por adaptadores.

O construtor anexado é outro motor: ele mesmo calcula e emite todas as peças em milímetros, a partir de um contrato
de chapas fornecido pelo addon hospedeiro, e entrega a caixa, as divisões, as gavetas com corrediça telescópica 3D,
os internos, as portas de abrir, as portas deslizantes e o fundo. A janela começa vazia e o projetista ativa o que
quer montar.

Esta feature porta esse motor para dentro do pacote e o torna o construtor de armário do addon, com as sete abas do
mockup, o contrato de chapas obrigatório, o plano de corte alimentado pelas peças reais, as abas em português e
inglês e um único passo de desfazer por confirmação.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `novo_arm_building/.../caff_construtor_armarios_blender_5_2/__init__.py#CAFF_ArmarioProps` | Modelo de dados do construtor novo: dimensões, montagem, espessuras, divisões, gavetas, internos, portas, deslizantes, fundo, acabamento | 🟢 |
| `novo_arm_building/.../__init__.py#CAFF_HostContractProps` e `#apply_host_contract` | Contrato do addon hospedeiro: chapa máxima, espessuras por papel, montagem e orientações padrão, injetáveis por função pública | 🟢 |
| `novo_arm_building/.../__init__.py#CAFF_OT_gerar` | Geração em milímetros: validação de chapa antes de desenhar, recuo automático dos internos pela porta deslizante, collection própria e raiz vazia com as peças filhas | 🟢 |
| `novo_arm_building/.../__init__.py#attach_drawer_slide_3d` | Importação do `assets/slide-st48-0200-0.obj` com trilho externo na lateral, interno na gaveta, gaiolas a meio curso e alternativa geométrica quando o arquivo falta | 🟢 |
| `novo_arm_building/.../__init__.py#CAFF_OT_toggle_abrir_fechar` | Animação por timer de gaveta (curso de 72% da caixa), gaiola a 50%, folha deslizante e porta de abrir (95°) | 🟢 |
| `novo_arm_building/.../mockup_construtor_armarios.html#renderPanel` | As sete abas e o conteúdo de cada uma: Estrutura, Divisões (sub-abas Vertical/Horizontal/Múltipla), Gavetas (sub-abas), Internos, Portas, Deslizantes, Fundos | 🟢 |
| `novo_arm_building/.../mockup_construtor_armarios.html#renderInlineHud`, `#renderInlineInspector`, `#openContextMenu` | Estado à mão na vista: alternadores da estrutura, inspetor da peça escolhida, menu de contexto com Duplicar e Excluir | 🟢 |
| `novo_arm_building/.../mockup_construtor_armarios.html#openCutlistModal` | Lista de peças com medidas e espessura, marcando as que passam da chapa e o selo permanente de conformidade | 🟢 |
| `novo_arm_building/.../blender_manifest.toml` | Alvo declarado: extensão para 5.2.0, licença GPL-3.0-or-later | 🟢 |
| `_reversa_sdd/cabinet_editor/requirements.md#Visão Geral` e `#Regras de Negócio` | Construtor atual: janela própria com vista frontal, sete abas, rascunho com desfazer, fila de pedidos e um modal com `UNDO` | 🟢 |
| `caffmob_draw/cabinet_editor/gallery.py` (docstring) | A galeria de estruturas cria o módulo pelo construtor de biblioteca e abre o editor nele | 🟢 |
| `caffmob_draw/cabinet_editor/props.py#TAB_ITEMS` | As sete abas já existem na interface atual, com os mesmos nomes do mockup | 🟢 |
| `caffmob_draw/__init__.py` | Registro e desregistro do `cabinet_editor` estão no ciclo de vida do pacote | 🟢 |
| `_reversa_sdd/cutting/requirements.md#Origem das peças` | O plano de corte lê as peças dos módulos e da geometria livre; objeto marcado como excluído não entra | 🟢 |
| `caffmob_draw/data/i18n.py` (docstring) | Regra de idioma do projeto: texto do código é a chave, catálogo por área com `pt_BR` e `en_US` obrigatórios | 🟢 |
| `_reversa_forward/015-construtor-armario-promob/requirements.md#RN-10` | O corte lista as peças reais com o nome do papel da peça | 🟢 |
| `CLAUDE.md` / `AGENTS.md` (regras do repositório) | Diferenças de versão em `compat.py`, propriedades lidas por atributo, operadores com `UNDO`, handlers removidos no `unregister`, texto novo em português | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro projetista | Montar um armário do zero, peça por peça, conferindo medidas em milímetros | Abre o construtor na janela vazia, ativa laterais, base inferior e base superior e vê a caixa nascer na vista |
| Projetista de dormitório | Roupeiro com divisões, gavetas com corrediça real e portas de correr | Divide em três vãos, insere um bloco de quatro gavetas com corrediça ST48, ativa a porta deslizante com base por dentro e vê os internos recuarem |
| Projetista de cozinha | Balcão e aéreo com espessuras e montagem do padrão da marcenaria | Recebe o contrato de chapas do addon hospedeiro, monta um balcão de 18 mm com base passante e confere que nenhuma peça passa de 2750 × 1830 |
| Marceneiro na produção | Saber o que cortar | Abre a lista de peças e lê nome, largura, altura e espessura de cada chapa, com as peças fora da chapa destacadas |
| Projetista conferindo o projeto | Mostrar o móvel aberto para o cliente | Usa Abrir/Fechar na gaveta, na porta de abrir e na folha deslizante, uma de cada vez ou tudo de uma vez |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** O construtor **começa vazio**. Nenhum componente estrutural vem marcado, nenhuma peça existe na cena e a vista mostra o estado "janela de armário vazia" com as ações de montagem rápida. 🟢
   - Origem: `__init__.py#CAFF_ArmarioProps` ("INICIAM DESMARCADOS") e `mockup_construtor_armarios.html#emptyOverlay`
   - Tipo: alterada (o editor atual abre num módulo já existente)
2. **RN-02:** O construtor **exige um contrato de chapas** fornecido pelo addon hospedeiro: comprimento e largura máximos da chapa, espessura padrão por papel (lateral esquerda, lateral direita, base inferior, base superior, divisória, prateleira, fundo, gaveta), montagem padrão, orientação padrão da contra-frente e da peça de trás. Sem contrato, gerar é recusado com mensagem clara. 🟢
   - Origem: `__init__.py#CAFF_HostContractProps`, `#apply_host_contract`
   - Tipo: nova
3. **RN-03:** Toda peça é conferida **contra a chapa máxima** antes de a geometria ser criada, comparando o maior lado da peça com o maior lado da chapa e o menor com o menor. A violação é listada por nome de peça e medida. Com "bloquear se extrapolar" ligado, a geração é cancelada; desligado, o armário é gerado com aviso. 🟢
   - Origem: `__init__.py#validate_part_against_sheet`, `#CAFF_OT_gerar`
   - Tipo: nova
4. **RN-04:** A **montagem** define o encontro das chapas. Em "lateral passante" as laterais vão do piso ao topo e as bases ficam entre elas; em "base passante" as bases cobrem a largura total e as laterais ficam entre elas. Contra-frente e peça de trás podem ser "em pé" ou "deitadas", trocando altura por profundidade. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-20); `__init__.py#CAFF_ArmarioProps.tipo_montagem`
   - Tipo: alterada (passa a valer no motor novo)
5. **RN-05:** A **espessura é por papel** e só aceita 6, 15, 18 ou 25 mm. O fundo nasce com 6 mm e as demais peças com 15 mm, salvo o que o contrato do hospedeiro trouxer. 🟢
   - Origem: `__init__.py#THICKNESS_ITEMS`
   - Tipo: nova
6. **RN-06:** Com **porta deslizante** ativa, a posição das bases decide o recuo: "dentro do armário" recua divisórias, prateleiras, gavetas e internos na profundidade do trilho e mantém laterais e bases na profundidade total; "na frente" não redimensiona nada. 🟢
   - Origem: `__init__.py#CAFF_OT_gerar` (`sliding_recede`), `mockup_construtor_armarios.html#renderPanel` (aba Deslizantes)
   - Origem no legado: `_reversa_sdd/cabinet_editor/requirements.md#RN-27`
   - Tipo: alterada
7. **RN-07:** O **bloco de gavetas** ocupa o vão escolhido com folga de 3 mm entre gavetas e entre a primeira/última e o limite do bloco; a altura de cada gaveta é a altura do bloco dividida pela quantidade, descontadas as folgas. A frente de cada gaveta é escolhida entre dez modelos: cinco sem contra-frente e cinco com contra-frente, nas variantes reta, normal, vidro, gola e cava. 🟢
   - Origem: `__init__.py#DRAWER_MODEL_ITEMS`, `#CAFF_OT_gerar`
   - Tipo: nova
8. **RN-08:** Com **corrediça 3D** ligada, cada gaveta recebe o conjunto telescópico importado do arquivo de modelo: trilho externo preso na lateral do armário, trilho interno preso na gaveta e gaiolas de esferas a meio curso. Sem o arquivo, entra o conjunto geométrico equivalente com as mesmas três partes marcadas. 🟢
   - Origem: `__init__.py#attach_drawer_slide_3d`
   - Tipo: nova
9. **RN-09:** O **separador de gaveta** divide o interior da caixa em colunas e linhas com chapas de 6 mm, e os **afastadores** frontal e traseiro, esquerdo e direito, são quatro chaves independentes. 🟢
   - Origem: `__init__.py#CAFF_ArmarioProps`
   - Tipo: nova
10. **RN-10:** **Abrir/Fechar** age no objeto sob o cursor pela hierarquia e anima um alvo por vez: gaveta desloca-se 72% da profundidade da caixa com as gaiolas a 50% do curso; folha deslizante corre 80% da própria largura, em sentidos opostos entre folhas; porta de abrir gira 95° no sentido da dobradiça. O estado aberto/fechado fica gravado no objeto e o rótulo do menu é sempre o da ação oposta ao estado atual. 🟢
   - Origem: `__init__.py#CAFF_OT_toggle_abrir_fechar`, `#draw_viewport_context_menu`
   - Tipo: nova
11. **RN-11:** **Duplicar** divisória ou prateleira só acontece se o vão livre vizinho comportar no mínimo 80 mm; a peça nova nasce no meio do maior vão livre disponível, e o comando é recusado com aviso quando não há espaço. 🟢
   - Origem: `__init__.py#CAFF_OT_duplicar_divisoria`
   - Tipo: nova
12. **RN-12:** A **inserção múltipla** (matriz) cria divisórias verticais distribuídas no vão escolhido e prateleiras em cada vão resultante, com linhas e colunas informadas; a prioridade vertical ou horizontal define o eixo que manda na distribuição. 🟢
   - Origem: `mockup_construtor_armarios.html#renderPanel` (aba Divisões, sub-aba Inserção múltipla)
   - Tipo: nova
13. **RN-13:** Os **internos** do vão escolhido são cabideiro, calceiro, sapateira e maleiro, cada um com posição vertical definida na inserção e ajustável depois. Calceiro e sapateira nascem a **480 mm do piso do vão** e o maleiro a **420 mm abaixo do topo do vão**, como no mockup. 🟢
   - Origem: `mockup_construtor_armarios.html#renderPanel` (aba Internos); `__init__.py#cabideiro`; resposta do titular em `/reversa-clarify` (2026-11-19)
   - Tipo: alterada (o motor atual só tem cabideiro)
14. **RN-14:** A **porta deslizante** tem de 2 a 4 folhas, sobreposição padrão de 30 mm e largura de folha `(comprimento + (n − 1) × sobreposição) / n`; o material da folha pode ser MDF amadeirado, vidro ou alumínio, e o vidro entra translúcido. Deslizantes e portas de abrir são mutuamente exclusivas. 🟢
   - Origem: `__init__.py#CAFF_ArmarioProps`, `#CAFF_OT_gerar`; `mockup_construtor_armarios.html#renderPanel` (aba Deslizantes)
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-18)
   - Tipo: alterada
15. **RN-15:** O **fundo** pode ser encaixado em canal ou sobreposto, com recuo configurável; encaixado, o recuo afasta o painel da face de trás e não consome a profundidade útil dos internos além do próprio painel. 🟢
   - Origem: `__init__.py#CAFF_ArmarioProps.fundo_fixacao`, `.fundo_recuo`
   - Tipo: nova
16. **RN-16:** A **lista de peças** mostra nome, largura, altura, espessura e a marca de fora-da-chapa de cada peça gerada, e o estado de conformidade com a chapa fica visível o tempo todo, também em texto. 🟢
   - Origem: `mockup_construtor_armarios.html#openCutlistModal`, `#updateStatusBar`
   - Origem no legado: `_reversa_forward/015-construtor-armario-promob/requirements.md#RN-10`
   - Tipo: alterada (o corte passa a ler o motor novo)
17. **RN-17:** Todo parâmetro do armário fica gravado no próprio armário, de modo que reabrir o construtor no mesmo móvel devolva exatamente o que foi gerado, com as peças na cena e as abas no estado salvo. 🟢
   - Origem no legado: `_reversa_sdd/cabinet_editor/requirements.md#RN-03` (instantâneo do módulo)
   - Tipo: alterada (novo conjunto de parâmetros)
18. **RN-18:** A confirmação grava **um passo de desfazer**: OK mantém a cena, Aplicar grava um passo sem fechar, Cancelar devolve o armário ao estado da abertura. Erro bloqueante impede OK e Aplicar. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-01, -02)
   - Tipo: mantida
19. **RN-19:** As **peças geradas são peças de produção**: cada uma leva o papel que desempenha (lateral, base, divisória, prateleira, fundo, frente, caixa de gaveta, folha, trilho) e entra no plano de corte com esse nome, sem duplicar peça de ferragem. 🟢
   - Origem no legado: `_reversa_sdd/cutting/requirements.md#Origem das peças`
   - Tipo: nova (o motor novo não passa pelas bibliotecas que hoje alimentam o corte)
20. **RN-20:** Todo texto novo de interface entra em português no código e no catálogo em `pt_BR` e `en_US`, nas duas línguas e nos contextos padrão e de operador. 🟢
   - Origem: `caffmob_draw/data/i18n.py` (docstring); `CLAUDE.md`
   - Tipo: mantida
21. **RN-21:** O motor novo é o **construtor de todos os armários** do pacote: além dos armários CAFF MOBI, ele passa a desenhar os módulos das bibliotecas frameless, face frame e closets. A montagem por bibliotecas deixa de alimentar o editor: os parâmetros do módulo viram parâmetros do motor novo e as peças saem do mesmo cálculo. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-19); `caffmob_draw/cabinet_editor/gallery.py`
   - Tipo: alterada (o editor atual monta o módulo pela biblioteca antes de abrir)
22. **RN-22:** O construtor vive **na vista 3D**: painel lateral com as sete abas, estado da montagem e inspetor da peça escolhida na própria vista e **menu de botão direito** nas peças, com Abrir/Fechar, Duplicar e Excluir. A janela própria com vista frontal 2D do editor atual deixa de ser a superfície do construtor. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-19); `mockup_construtor_armarios.html#renderPanel`, `#renderInlineHud`, `#renderInlineInspector`, `#openContextMenu`; `__init__.py#draw_viewport_context_menu`
   - Tipo: alterada (o editor atual é janela própria)
23. **RN-23:** Armário gerado pelo construtor atual **mantém a construção antiga**: as peças continuam na cena e no plano de corte, mas o motor novo não as edita nem converte. Ao abrir o construtor num armário assim, o painel avisa que o móvel é da construção antiga e que a edição exige recriá-lo pelo motor novo. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-19); precedente `_reversa_forward/015-construtor-armario-promob/requirements.md#RN-22`
   - Tipo: nova
24. **RN-24:** O **plano de corte** lê as peças do motor novo por um adaptador próprio: toda malha gerada leva gravado o papel que desempenha e as medidas de corte, e o adaptador entrega essas peças ao corte sem passar pelas bibliotecas. Peça sem papel gravado não entra como peça de chapa. 🟢
   - Origem: resposta do titular em `/reversa-clarify` (2026-11-19); `caffmob_draw/cutting/part_sources.py`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | O construtor abre num armário vazio, com a vista no estado "janela vazia" e as ações Montar Caixa e Limpar (RN-01) | Must | Abrir o construtor não cria nenhuma peça; Montar Caixa liga laterais, base inferior, base superior e fundo e gera o armário; Limpar volta ao estado vazio | 🟢 |
| RF-02 | As sete abas Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes e Fundos, com o conteúdo do mockup (RN-02 a RN-15, RN-22) | Must | Cada aba mostra os campos da seção 4 e o cabeçalho mostra o tipo e o vão ativo | 🟢 |
| RF-03 | Contrato de chapas obrigatório, injetável pelo addon hospedeiro e editável na aba Estrutura (RN-02) | Must | A função pública de injeção grava chapa, espessuras, montagem e orientações; sem contrato, gerar devolve recusa com mensagem | 🟢 |
| RF-04 | Validação de todas as peças contra a chapa máxima, com bloqueio opcional (RN-03) | Must | Armário de 3000 mm com chapa de 2750 mm lista a peça e a medida; com bloqueio ligado não gera nada; desligado gera com aviso | 🟢 |
| RF-05 | Dimensões, montagem e orientações de contra-frente e peça de trás (RN-04) | Must | Trocar lateral passante por base passante muda o comprimento das bases e a posição das laterais; trocar a orientação troca altura por profundidade na peça | 🟢 |
| RF-06 | Espessura por papel, restrita a 6, 15, 18 e 25 mm (RN-05) | Must | Mudar a espessura da lateral para 25 muda a espessura da chapa gerada e a posição das peças vizinhas | 🟢 |
| RF-07 | Divisões: vertical com quatro variantes, horizontal com quatro variantes e inserção múltipla em matriz (RN-12) | Must | Inserir matriz de 2 linhas por 1 coluna num vão cria uma divisória e duas prateleiras em cada vão resultante | 🟢 |
| RF-08 | Duplicar divisória e prateleira respeitando o vão livre mínimo de 80 mm (RN-11) | Should | Duplicar em vão apertado é recusado com aviso; em vão amplo, a peça nova fica no meio do maior espaço livre | 🟢 |
| RF-09 | Editor de gavetas com quantidade, altura do bloco, modelo único ou por gaveta, dez modelos de frente (RN-07) | Must | Quatro gavetas num bloco de 760 mm saem com folgas de 3 mm e alturas iguais; escolher "c/ CF Vidro" na segunda gaveta muda só aquela frente | 🟢 |
| RF-10 | Corrediça telescópica 3D com trilho externo, trilho interno e gaiolas, e alternativa geométrica sem o arquivo (RN-08) | Must | Cada gaveta recebe duas corrediças; sem o arquivo de modelo, as três partes aparecem com os mesmos papéis e a gaveta continua abrindo | 🟢 |
| RF-11 | Separador de gaveta por colunas e linhas e os quatro afastadores (RN-09) | Should | Separador de 3 × 2 cria duas chapas verticais e uma horizontal dentro da caixa; desmarcar o afastador frontal direito remove só aquela chapa | 🟢 |
| RF-12 | Internos cabideiro, calceiro, sapateira e maleiro no vão escolhido, com calceiro e sapateira a 480 mm do piso e maleiro a 420 mm abaixo do topo (RN-13) | Must | Cada item inserido aparece no vão ativo com a posição inicial do mockup e pode ser excluído; a posição vertical é editável | 🟢 |
| RF-13 | Portas de abrir com quantidade de folhas, espessura e dobradiça alternada (RN-10) | Must | Duas folhas num armário de 1000 mm saem com 18 mm e abrem em sentidos opostos | 🟢 |
| RF-14 | Porta deslizante com posição das bases, espessura da base, profundidade do trilho, material, folhas e sobreposição (RN-06, RN-14) | Must | Com base por dentro, os internos recuam a profundidade do trilho e as bases aparecem; com base na frente, nenhuma peça interna muda; ativar deslizante desliga portas de abrir | 🟢 |
| RF-15 | Fundo encaixado ou sobreposto, com espessura e recuo (RN-15) | Must | Fundo encaixado com recuo de 10 mm afasta o painel 10 mm da face de trás; sobreposto encosta a face de trás | 🟢 |
| RF-16 | Abrir/Fechar por objeto, no menu de contexto e no painel, com curso e estado gravados (RN-10) | Must | Selecionar uma gaveta e usar Abrir mostra o rótulo Fechar na próxima vez; a gaveta sai 72% da profundidade, as gaiolas 50%; Esc/segundo toque não deixa passo de desfazer | 🟢 |
| RF-17 | Acabamento entre madeirado, branco, cinza e preto, aplicado às chapas e às frentes, com vidro e metal próprios (RN-14) | Should | Trocar o acabamento muda a cor das chapas e das frentes na cena, mantendo vidro e alumínio distintos | 🟢 |
| RF-18 | Estado sempre visível em texto: dimensões, montagem, vão e peça escolhidos, conformidade de chapa (RN-16) | Should | A barra de estado acompanha cada mudança e o selo de chapa muda para vermelho quando alguma peça passa da chapa | 🟢 |
| RF-19 | Lista de peças com nome, largura, altura, espessura e marca de fora-da-chapa, lida pelo adaptador de corte a partir do papel gravado em cada malha (RN-16, RN-19, RN-24) | Must | O plano de corte de um armário com duas gavetas lista laterais, bases, divisória, prateleiras, as peças das gavetas e as folhas, sem listar a corrediça como peça de chapa | 🟢 |
| RF-20 | Os parâmetros ficam gravados no armário e reabrir o construtor devolve o mesmo estado (RN-17) | Must | Gerar, salvar o arquivo, reabrir e abrir o construtor mostra as mesmas medidas, divisões, gavetas, portas e fundo | 🟢 |
| RF-21 | Textos novos em português e inglês (RN-20) | Must | Em inglês, as abas e os modelos de frente aparecem traduzidos e o teste de cobertura de i18n passa | 🟢 |
| RF-22 | Um passo de desfazer por confirmação; Cancelar devolve o estado da abertura; erro bloqueia OK e Aplicar (RN-18) | Must | Gerar, alterar e usar OK deixa um passo de desfazer; Cancelar depois de Aplicar volta ao ponto aplicado; com erro bloqueante OK fica desabilitado | 🟢 |
| RF-23 | O construtor substitui o motor do construtor atual no pacote, sem deixar dois construtores registrados (RN-01, RN-17) | Must | Abrir o construtor chega ao motor novo; o construtor antigo não aparece em menu, painel ou atalho; desregistrar o addon não deixa operador, propriedade, handler ou timer pendurado | 🟢 |
| RF-24 | O motor novo passa a desenhar também os módulos das bibliotecas frameless, face frame e closets (RN-21) | Must | Inserir um módulo de cada biblioteca abre o construtor novo com os parâmetros do módulo e gera as peças pelo cálculo do motor; nenhum módulo é montado pelo caminho de bibliotecas | 🟢 |
| RF-25 | Superfície na vista 3D: painel com as sete abas, estado e inspetor da peça na vista e menu de botão direito com Abrir/Fechar, Duplicar e Excluir (RN-22, RN-10) | Must | Com um armário selecionado o painel mostra as sete abas; o botão direito numa divisória oferece Duplicar e Excluir e numa gaveta oferece Abrir/Fechar | 🟢 |
| RF-26 | Armário do construtor atual permanece intacto e não é convertido; o painel avisa que a edição exige recriar pelo motor novo (RN-23) | Must | Abrir o construtor num armário antigo não altera peças nem parâmetros e mostra o aviso; o plano de corte continua listando as peças antigas | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Gerar um armário de até 4 vãos, 20 divisões e 10 gavetas em até 0,5 s; a lista de peças abre em até 0,3 s | Mesma meta das features 006, 008 e 015; geração inteira em milímetros, sem consulta a biblioteca | 🟡 |
| Desempenho | A animação de abrir/fechar usa timer de 16 ms e no máximo 18 quadros por alvo, sem travar a interface | `__init__.py#CAFF_OT_toggle_abrir_fechar` | 🟢 |
| Compatibilidade | Alvo Blender 5.2; diferenças de versão ficam em `compat.py`, e nenhuma leitura de input de Geometry Nodes usa caminho anterior a 5.2 | `CLAUDE.md`; `docs/rag/project/03_compatibilidade_5x.md` | 🟢 |
| Compatibilidade | O arquivo de modelo da corrediça é versionado dentro do pacote e empacotado pelo `build.py` | `build.py` recusa empacotar sem os arquivos do pacote; o motor novo depende do modelo para a corrediça 3D | 🟢 |
| Manutenibilidade | O cálculo das peças (medidas, recuos, chapa, corte) é núcleo puro, testável fora do Blender, separado do desenho e da cena | Regras do repositório (arquitetura limpa, núcleo sem `bpy`) | 🟢 |
| Confiabilidade | Cada regra de negócio da seção 4 tem um caso de referência na suíte pura; a geração tem uma fumaça no Blender | Padrão das features 004, 006 e 008 | 🟢 |
| Robustez | Contrato ausente, chapa inválida, arquivo de modelo ausente e valores fora de faixa não podem deixar traceback: devolvem mensagem e não geram geometria parcial | `__init__.py#CAFF_OT_gerar` recusa sem contrato; `attach_drawer_slide_3d` já tem alternativa | 🟢 |
| Idioma | Texto novo em português no código e catálogo com `pt_BR` e `en_US` nos contextos padrão e de operador | `caffmob_draw/data/i18n.py`; teste `tests/test_i18n_coverage.py` | 🟢 |
| Acessibilidade | Estado nunca só por cor: seleção, conformidade de chapa e chave ligada aparecem também em texto | `mockup_construtor_armarios.html#updateStatusBar` | 🟢 |
| Custo | Nenhuma chamada a modelo de IA ou serviço externo: o construtor é regra determinística local | Diretriz de controle de custo do projeto | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Construtor abre vazio e monta a caixa padrão
  Dado um arquivo aberto com o addon carregado
  Quando o projetista abre o construtor
  Então nenhuma peça existe na cena e a vista mostra a janela vazia
  Quando ele usa Montar Caixa
  Então laterais, base inferior, base superior e fundo aparecem nas medidas do contrato

Cenário: Chapa máxima respeitada
  Dado o contrato com chapa de 2750 por 1830 e bloqueio ligado
  Quando o projetista pede um armário de 3000 mm de largura com lateral inteira
  Então a geração é cancelada com a lista de peças e medidas que passam da chapa
  E nenhuma geometria é criada

Cenário: Peça fora da chapa com bloqueio desligado
  Dado o mesmo contrato com o bloqueio desligado
  Quando o projetista gera o armário
  Então o armário é gerado
  E a lista de peças e o aviso mostram quais peças passam da chapa

Cenário: Contrato do hospedeiro ausente
  Dado que nenhum contrato foi fornecido
  Quando o projetista usa Gerar
  Então a geração é recusada com a mensagem de contrato não configurado
  E a cena não muda

Cenário: Porta deslizante com base por dentro recua os internos
  Dado um armário com duas prateleiras e um bloco de gavetas
  Quando o projetista ativa a porta deslizante com base por dentro e trilho de 70 mm
  Então as prateleiras, as divisórias e as gavetas recuam 70 mm
  E as laterais e as bases da porta mantêm a profundidade total

Cenário: Porta deslizante na frente não redimensiona nada
  Dado o mesmo armário
  Quando o projetista escolhe base na frente
  Então nenhuma peça interna muda de profundidade
  E as bases da porta aparecem à frente da caixa

Cenário: Deslizante e portas de abrir são exclusivas
  Dado um armário com portas de abrir ativas
  Quando o projetista ativa a porta deslizante
  Então as portas de abrir são desligadas
  E as folhas deslizantes aparecem

Cenário: Corrediça 3D ausente do pacote
  Dado que o arquivo de modelo da corrediça não está disponível
  Quando o projetista gera um bloco de gavetas com corrediça 3D ligada
  Então cada gaveta recebe o conjunto geométrico equivalente
  E Abrir/Fechar continua funcionando com o trilho interno acompanhando a gaveta

Cenário: Duplicar sem vão livre
  Dado um vão com divisória a menos de 80 mm da peça vizinha do lado maior
  Quando o projetista usa Duplicar
  Então o comando é recusado com aviso de vão insuficiente
  E nenhuma peça nova aparece

Cenário: Cancelar devolve o estado da abertura
  Dado o construtor aberto num armário gerado
  Quando o projetista muda a largura e usa Cancelar
  Então o armário volta à largura anterior
  E não fica passo de desfazer da alteração descartada

Cenário: Erro bloqueante impede OK
  Dado um valor que viola a faixa de uma medida
  Quando o projetista tenta OK
  Então o botão está desabilitado com a mensagem de correção
  E nada é aplicado

Cenário: Reabrir mantém o armário
  Dado um armário gerado com três vãos, quatro gavetas e folha deslizante
  Quando o projetista salva, fecha e reabre o arquivo e o construtor
  Então as sete abas mostram os mesmos valores gravados
  E a cena continua com as peças geradas

Cenário: Montagem e espessura por papel
  Dado um armário de 1000 por 900 por 550 com montagem lateral passante
  Quando o projetista troca para base passante e muda a lateral para 25 mm
  Então a base inferior passa a ter a largura total e as laterais ficam sobre ela
  E a lateral gerada sai com 25 mm de espessura

Cenário: Matriz de prateleiras
  Dado um vão único sem divisões
  Quando o projetista insere uma matriz de 2 linhas por 1 coluna
  Então surge uma divisória vertical no meio do vão
  E cada vão resultante recebe duas prateleiras distribuídas na altura

Cenário: Gavetas com separador e afastadores
  Dado um bloco de quatro gavetas com separador de 3 por 2 marcado
  Quando o projetista desmarca o afastador frontal direito
  Então a caixa de cada gaveta mantém as duas chapas verticais e a horizontal do separador
  E só a chapa do afastador frontal direito sai

Cenário: Interno no vão ativo
  Dado um armário com três vãos
  Quando o projetista escolhe o vão 2 e insere um cabideiro
  Então o cabideiro aparece só no vão 2
  E a posição vertical dele é editável depois da inserção

Cenário: Posições iniciais dos internos
  Dado um vão vazio de 2000 mm de altura
  Quando o projetista insere calceiro, sapateira e maleiro
  Então o calceiro e a sapateira nascem a 480 mm do piso do vão
  E o maleiro nasce a 420 mm abaixo do topo do vão
  E as três posições ficam editáveis depois da inserção

Cenário: Fundo encaixado com recuo
  Dado um armário sem fundo
  Quando o projetista liga o fundo, escolhe encaixado e recuo de 10 mm
  Então o painel de 6 mm fica a 10 mm da face de trás
  E a profundidade útil dos internos desconta o painel e o recuo

Cenário: Ciclo completo de abrir e fechar
  Dado um armário com gaveta, porta de abrir e folha deslizante
  Quando o projetista usa Abrir/Fechar Tudo
  Então todos os alvos vão ao estado aberto
  Quando ele usa de novo
  Então todos voltam ao estado fechado
  E o armário aceita as duas operações num único desfazer cada

Cenário: Acabamento trocado
  Dado um armário com acabamento madeirado
  Quando o projetista escolhe branco
  Então as chapas e as frentes mudam de cor
  E o vidro e o alumínio continuam com os materiais próprios

Cenário: Construtor antigo substituído
  Dado o addon carregado com o motor novo
  Quando o projetista procura o construtor de armário no menu, no painel e no atalho
  Então só existe o construtor novo
  E desregistrar o addon não deixa operador, propriedade, handler de menu ou timer pendurado

Cenário: Módulo de biblioteca pelo motor novo
  Dado o addon carregado com o motor novo
  Quando o projetista insere um módulo frameless e um módulo face frame
  Então os dois abrem no painel do construtor novo com os parâmetros do módulo
  E as peças saem do cálculo do motor novo, sem montagem pelo caminho de bibliotecas

Cenário: Armário do construtor atual permanece como está
  Dado um armário gerado pelo construtor atual, com divisórias e gavetas gravadas
  Quando o projetista abre o construtor novo nele
  Então nenhuma peça e nenhum parâmetro são alterados
  E o painel avisa que o móvel é da construção antiga e que a edição exige recriá-lo

Cenário: Menu de botão direito nas peças
  Dado um armário gerado no motor novo
  Quando o projetista clica com o botão direito numa divisória e depois numa gaveta
  Então a divisória oferece Duplicar e Excluir
  E a gaveta oferece Abrir/Fechar com o rótulo da ação oposta ao estado atual

Cenário: Plano de corte lê o papel gravado
  Dado um armário gerado pelo motor novo
  Quando o projetista abre o plano de corte
  Então cada malha entra com o papel gravado e as medidas de corte
  E uma malha sem papel gravado não é listada como peça de chapa

Cenário: Lista de peças no plano de corte
  Dado um armário gerado com duas gavetas e uma porta de abrir
  Quando o projetista abre o plano de corte
  Então as peças das gavetas e a folha aparecem com nome, largura, altura e espessura
  E a corrediça não aparece como peça de chapa

Cenário: Interface em inglês
  Dado o Blender com a interface em inglês
  Quando o projetista abre o construtor
  Então as abas, os modelos de frente e as ações aparecem em inglês
  E o teste de cobertura de i18n passa
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 a RF-07, RF-09, RF-10, RF-13 a RF-16, RF-19, RF-20, RF-22 a RF-26 | Must | É a substituição pedida: o motor novo com as sete abas na vista 3D, o contrato de chapas, a geração completa, todos os módulos e o corte, sem conviver com o construtor antigo |
| RF-21 | Must | Regra de idioma do projeto e condição do teste de cobertura |
| RF-08, RF-11, RF-12, RF-17, RF-18 | Should | Completam a operação diária do construtor sem bloquear a primeira entrega |
| Inserção múltipla com prioridade por eixo | Should | O mockup define; sem ela o construtor continua utilizável peça por peça |
| Inspetor da peça escolhida na vista | Should | O mockup mostra o inspetor inline; o estado principal já aparece no painel e no menu de contexto (RN-22) |
| Vista de corte lateral | Could | O mockup mostra; a vista 3D resolve a conferência principal |
| Exportação do estado em JSON e tema claro/escuro | Won't (nesta feature) | Pertencem ao protótipo de navegador; no pacote o estado fica no armário e o tema é do Blender |
| Portas de correr "sobre a caixa" com os três sistemas internos, externo e embutido | Won't (feature seguinte) | A especificação anexa só define a porta deslizante de bases; os três sistemas ficam para a decisão da 015 |

## 9. Esclarecimentos

### Sessão 2026-11-19

- **Q:** Até onde o motor novo substitui o construtor legado do addon?
  **R:** Todos os armários: o motor novo passa a desenhar também os módulos de biblioteca. Aplicado em RN-21 e RF-24.
- **Q:** Onde o construtor novo vive no Blender?
  **R:** Painel na vista 3D com as sete abas e menu de botão direito, como o add-on anexo. Aplicado em RN-22 e RF-25.
- **Q:** O que acontece com os armários já criados pelo construtor atual?
  **R:** Mantêm a construção antiga até o projetista recriar pelo construtor novo. Aplicado em RN-23 e RF-26.
- **Q:** Qual posição inicial usam calceiro, sapateira e maleiro?
  **R:** A do mockup: calceiro e sapateira a 480 mm, maleiro 420 mm abaixo do topo, tudo editável. Aplicado em RN-13 e RF-12.
- **Q:** Como o plano de corte lê as peças do motor novo?
  **R:** Adaptador novo lê as malhas com papel gravado. Aplicado em RN-24 e RF-19.

**Consequências registradas**

- O caminho de montagem por bibliotecas sai do fluxo do construtor; as bibliotecas continuam existindo como origem dos parâmetros dos módulos prontos.
- A janela própria 2D deixa de ser a superfície do construtor, e as sete abas passam a viver no painel da vista 3D, com o menu de botão direito nas peças.
- O construtor antigo não fica registrado (RF-23) e os móveis gerados por ele ficam somente leitura no motor novo: nenhuma conversão automática de parâmetros antigos.
- O adaptador de corte é parte da entrega, porque as peças do motor novo não passam pelas bibliotecas que hoje alimentam o plano de corte.

### Sessão 2026-11-21 (fechamento do cross-check)

- **Q:** A001, o módulo de biblioteca convertido continua gerando peças sintéticas no plano de corte porque `iter_modules` e `synthetic_records` não consultam `btm_cut_exclude`. Onde o filtro deve viver?
  **R:** Em `iter_modules`: módulo oculto ou com `btm_cut_exclude` deixa de ser módulo do projeto. Aplicado em D-17 e T035.
- **Q:** A002, o D-04 tirava `gallery` do registro e `library_panel/ops_cabinet.py:46` chama `caffmob.structure_gallery` sem guarda. A galeria sobrevive?
  **R:** Sim: a galeria é seletor de estrutura, não a janela 2D que a RN-22 aposenta. `gallery` continua registrado e `ops_cabinet.py` não é editado. Aplicado em D-04 e T027.
- **Q:** A003, RN-01/RF-01 exigem construtor vazio e Montar Caixa ligando laterais e bases, mas o modelo não tem flag de presença. Quais campos entram?
  **R:** Não houve resposta do titular nesta sessão; a derivação está registrada como premissa 🟡 em D-18 (quatro flags mais o `fundo_ativo` existente) e precisa de confirmação no T003.

**Consequências registradas**

- O plano de corte passa a ter uma regra só sobre módulo convertido: a marca vale na origem, não só no fim da leitura.
- O diferencial da feature 015 ("Criar armário" com galeria de estruturas) fica preservado durante a troca do construtor.

## 10. Lacunas

- 🟡 Sem dúvidas abertas em RN e RF: as cinco perguntas de 2026-11-19 foram respondidas.
- 🟡 A003 ficou sem resposta do titular em 2026-11-21: as quatro flags de presença de D-18 são derivação do RF-01, não decisão confirmada. Confirmar ou corrigir no T003.
- 🟡 A faixa exata das posições editáveis dos internos, os limites dentro do vão e a ordem de prioridade quando dois internos disputam a mesma altura ficam para o `/reversa-plan`.
- 🟡 O mapeamento dos parâmetros de cada biblioteca de módulo (frameless, face frame, closets) para o modelo do motor novo é trabalho de plano, a validar módulo a módulo.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-19 | Versão inicial gerada por `/reversa-requirements` a partir do add-on anexo, do mockup e da extração reversa | reversa |
| 2026-11-19 | `/reversa-clarify`: escopo em todos os armários, superfície na vista 3D, móveis antigos preservados, posições iniciais dos internos e adaptador de corte; RN-21 a RN-24 e RF-24 a RF-26 acrescentados | reversa |
| 2026-11-21 | Esclarecimentos do cross-check: filtro de `btm_cut_exclude` em `iter_modules` (A001), galeria mantida registrada (A002), flags de presença derivadas do RF-01 (A003, pendente) | reversa |
