# Requirements: Janela própria do Construtor de Armários igual ao mockup

> Identificador: `023-janela-mockup-construtor`
> Data: `2026-11-24`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Entregar uma janela própria (Image Editor sem imagem, com barra lateral) que abra o Construtor de Armários com o preview frontal e lateral dividido, o painel de 7 abas (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos), o empty state de "Janela de Armário Vazia" e os botões OK / Aplicar / Cancelar, tudo igual ao mockup de referência em `novo_arm_building/.../mockup_construtor_armarios.html`. O usuário constrói o armário paramétrico dentro dessa janela e confirma para gravar na cena do Blender.

Situação em 2026-11-25: a janela **abre como janela nova** (`canvas2d.window.open_window`), tem entrada no painel da Vista 3D, abre na aba Construtor Armário com a Estrutura aberta, seleciona peça por clique, valida GEO-001/GEO-002 e desenha o preview dentro da largura visível. O que resta é a decisão de **paridade visual** (ver §10).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#Limites e organização` | Camada "Mobiliário" agrupa `cabinet_editor`, `customize`, `standards` (responsável por chapas/subvãos, personalização e padrão de origem). | 🟢 |
| `_reversa_sdd/domain.md#cabinet_editor` | Regras RN-CABINET_EDITOR-01 a RN-CABINET_EDITOR-21: fila de pedidos + modal UNDO, erro bloqueia OK, medidas limitadas, divisão corta subvão-folha, gavetas/portas no vão da biblioteca, deslizantes, fundo, montagem LATERAL/BASE, clique escolhe chapa ou vão. | 🟢 |
| `_reversa_sdd/domain.md#canvas2d` | RN-CANVAS2D-08: a tela 2D é um Image Editor sem imagem, sem cabeçalho, menus nem barra de ferramentas; só a região lateral. | 🟢 |
| `_reversa_sdd/cabinet_editor/requirements.md#Visão Geral` | Janela própria com vista frontal (x, z) e painel lateral de 7 abas no modelo do Construtor do Promob; OK fecha mantendo, Aplicar grava passo sem fechar, Cancelar reaplica instantâneo. | 🟢 |
| `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html` | Layout visual de referência: titlebar, toolbar, preview dividido (frontal + corte lateral), empty-overlay, painel lateral de 7 abas, Movimentação, footer OK/Cancelar/Aplicar. | 🟡 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de móveis (marceneiro) | Construir um armário paramétrico visualmente | Abre a janela, ativa laterais/bases/fundo na Estrutura, adiciona prateleiras e gavetas, clica OK para gerar as chapas na cena do Blender |
| Usuário do Promob | Reproduzir a experiência do Construtor do Promob | A janela se comporta como o Construtor do Promob (preview ao vivo, painel lateral, confirmação explícita) |

## 4. Regras de negócio novas ou alteradas

1. **RN-01:** A janela do Construtor de Armários deve abrir como uma **nova janela do sistema** (Image Editor sem imagem, restaura a área ao fechar) com barra lateral e painel de 7 abas, com **paridade híbrida** com o mockup: mesmas funções e o chrome equivalente do Blender, mais paleta, espaçamento e ícones do HTML onde a UI do Blender permitir; **sem titlebar própria** nem abas horizontais (decisão de 2026-11-25). Edita o **armário v2** (`armario_v2`, `btm_armario`). 🟢
   - Origem no legado: `_reversa_sdd/cabinet_editor/requirements.md#Visão Geral` (descreve janela própria) e `_reversa_sdd/domain.md#canvas2d` (RN-CANVAS2D-08).
   - Tipo: alterada (o construtor v2 atual, feature 017, usa um painel na Vista 3D, não janela própria; a janela agora edita o armário v2, não o módulo legado).
2. **RN-02:** Toda edição dentro da janela passa por uma fila executada por um único modal com `UNDO`; OK grava um passo de desfazer e fecha, Aplicar grava um passo sem fechar, Cancelar reaplica o instantâneo inicial. Decisão de 2026-11-25: a fila **entra nesta feature** (os painéis passam a enfileirar; o modal processa), em vez de ficar como dívida. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-01).
   - Tipo: alterada (reaproveita a regra do editor antigo, hoje ausente do registro).
3. **RN-03:** O clique na vista escolhe a chapa sob o cursor (não frente, não vão, não chapa que cobre o subvão inteiro); sem chapa, escolhe o subvão-folha de menor área sob o ponto. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-21).
   - Tipo: reutilizada.
4. **RN-04:** Medidas do módulo limitadas à faixa geral (largura 0,01–10 m, altura 0,01–10 m, profundidade 0,005–10 m) estreitada pela biblioteca; valor fora da faixa → erro de campo e medida não aplicada. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-03).
   - Tipo: reutilizada.
5. **RN-05:** Erro (severity ERROR) bloqueia OK e Aplicar; aviso não bloqueia. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-02).
   - Tipo: reutilizada.
6. **RN-06:** Seleção de peças: clique simples seleciona uma peça e limpa a seleção no vazio; Shift/Ctrl+clique acumula peças na seleção; com mais de uma peça, as ações de mover, apagar e espelhar valem para o conjunto, num único passo de desfazer. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-21, ampliada de uma para várias peças).
   - Tipo: alterada (decisão de 2026-11-25).
7. **RN-07:** A janela lembra, **por cena**, a última aba ativa e o último tamanho de janela; ao abrir numa cena sem histórico, usa a aba Estrutura e o tamanho padrão do mockup (1009×831). Limite de plataforma medido em 2026-11-25: `Window.width/height` são **readonly** no Blender 5.2 e `area_dupli` não aceita tamanho — a aba é restaurada e o tamanho fica **registrado** na cena, mas não pode ser reaplicado por script. 🟢 (aba) · 🟡 (tamanho: só registro)
   - Origem no legado: nenhuma (comportamento novo do construtor em janela).
   - Tipo: nova (decisão de 2026-11-25).

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Abrir uma janela própria do Construtor de Armários, com o layout do mockup de referência (preview dividido, painel lateral de 7 abas, empty state, botões OK/Aplicar/Cancelar), editando o **armário v2** (`armario_v2`, `btm_armario`). | Must | No modo objeto, ao executar a ação de abrir (botão "Abrir Janela" do painel ou busca), surge uma **nova janela do sistema** com Image Editor sem imagem — a contagem de janelas do Blender aumenta em 1 e a Vista 3D do usuário não muda de tipo —, barra lateral ativa na categoria do construtor, preview frontal e corte lateral visíveis, painel de 7 abas com a aba Estrutura aberta e a barra "Selecionado: …", com a paleta, o espaçamento e os ícones do mockup onde a UI do Blender permitir. | 🟢 (janela, aba e entrada medidas na sonda de 2026-11-25; paridade híbrida decidida) |
| RF-02 | Construir o armário dentro da janela: ativar laterais, base inferior, base superior e fundo; adicionar prateleiras, divisórias, gavetas, internos, portas, deslizantes e fundo. | Must | Cada ativação/inserção aparece ao vivo no preview; clicar numa peça a seleciona (barra "Selecionado: …"); as medidas refletem os campos da aba Estrutura. | 🟢 |
| RF-03 | Validar medidas e geometria em tempo real: fora da faixa → erro de campo; peça fora da largura/altura do módulo > 1 mm → GEO-001; sobreposição de prateleiras/divisórias > 1 mm → GEO-002. | Must | OK fica bloqueado enquanto houver erro; mensagens com códigos DIM/GEO/DIV/STR/LIB aparecem no painel. | 🟢 |
| RF-04 | Confirmar (OK) grava um passo de desfazer do Blender, fecha a janela e mantém as peças geradas na cena. | Must | Após OK, Ctrl+Z na cena desfaz todo o conjunto gerado; a janela fecha 0,05 s depois. | 🟢 |
| RF-05 | Aplicar grava um passo de desfazer sem fechar a janela e vira o novo ponto de retorno do Cancelar. | Must | Após Aplicar, Cancelar volta ao estado do último Aplicar, não ao da abertura. | 🟢 |
| RF-06 | Cancelar (ou fechar a janela pelo sistema) reaplica o instantâneo inicial e descarta as alterações não confirmadas. | Must | Após Cancelar, o armário volta ao estado da abertura; ao fechar pelo sistema com alterações, avisa "Editor fechado: alterações descartadas". | 🟢 |
| RF-07 | Empty state: quando nenhuma estrutura está ativa, mostrar "Janela de Armário Vazia" com botão de montagem rápida (Montar Caixa). | Must | Sem laterais/bases/fundo, o preview exibe o empty card e não há peças para selecionar. | 🟡 |
| RF-08 | Selecionar várias peças com Shift/Ctrl+clique e aplicar ações em lote (mover, apagar, espelhar). | Should | Com 2+ peças selecionadas, a barra mostra a contagem, cada ação em lote altera todas as peças num único passo de desfazer e a seleção continua válida depois da ação. | 🟢 (decidido em 2026-11-25) |
| RF-09 | Lembrar por cena a última aba ativa e o último tamanho da janela. | Should | Fechar na aba Gavetas com 1200×900 e reabrir na mesma cena volta em Gavetas nesse tamanho; numa cena nova, abre em Estrutura no tamanho padrão. | 🟢 (decidido em 2026-11-25) |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Abrir a janela em **menos de 2 s** e redesenhar o preview em **menos de 200 ms** por interação, medidos por sonda com o armário montado, sem travar o Blender. | `_reversa_sdd/architecture.md#Limites e organização` (interação na thread principal do Blender); meta definida em 2026-11-25. | 🟢 |
| Segurança | Nenhuma escrita direta na cena fora do modal UNDO; botões só enfileiram pedidos. | `_reversa_sdd/domain.md#cabinet_editor` (RN-CABINET_EDITOR-01). | 🟢 |
| Observabilidade | Mensagens de erro/aviso visíveis no painel com código e componente; barra "Selecionado: …" sempre presente. | `_reversa_sdd/domain.md#cabinet_editor` (RN-22). | 🟢 |
| Acessibilidade | Peças removidas e subvão escolhido têm texto, não só cor. | `_reversa_sdd/cabinet_editor/requirements.md` (Acessibilidade do estado). | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Abrir a janela do Construtor igual ao mockup
  Dado o Blender em modo objeto e nenhuma sessão de construtor ativa
  Quando executo a ação de abrir o Construtor de Armários
  Então surge uma janela própria com Image Editor sem imagem, barra lateral ativa, preview dividido (frontal e corte lateral), painel de 7 abas com Estrutura selecionada e o empty state "Janela de Armário Vazia"

Cenário: Montar caixa e confirmar
  Dado a janela do Construtor aberta no empty state
  Quando clico em "Montar Caixa" e depois em OK
  Então as chapas laterais, bases e fundo são geradas na cena do Blender e a janela fecha

Cenário: Cancelar descarta alterações
  Dado a janela aberta com o armário montado
  Quando clico em Cancelar e confirmo "Descartar"
  Então o armário volta ao estado da abertura (sem peças geradas) e a janela fecha

Cenário: Medida fora da faixa bloqueia o OK
  Dado a janela aberta com o armário montado
  Quando defino a largura para um valor fora da faixa da biblioteca
  Então aparece DIM-003 (ERRO) no campo e o botão OK fica desabilitado

Cenário: Seleção múltipla e ação em lote
  Dado o armário montado com duas prateleiras
  Quando clico na primeira, seguro Shift e clico na segunda, e movo as duas 10 mm
  Então a barra mostra "2 peças selecionadas", as duas se deslocam juntas e um único Ctrl+Z desfaz o movimento das duas

Cenário: Reabrir lembra aba e tamanho por cena
  Dado que fechei a janela na aba Gavetas com 1200×900 na cena SALAS
  Quando abro a janela de novo na cena SALAS
  Então ela abre em Gavetas com 1200×900; numa cena sem histórico, abre em Estrutura no tamanho padrão
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | Caminho crítico: sem a janela própria igual ao mockup, a feature não entrega o solicitado. |
| RF-02 | Must | Entrega o propósito de construção visual do armário. |
| RF-03 | Must | Garante integridade dos dados e evita peças inválidas na cena. |
| RF-04 | Must | O Confirmar (OK) é o ponto de fechamento da edição. |
| RF-05 | Should | Aplicar sem fechar é conveniência, não essencial. |
| RF-06 | Must | Cancelar/fechar deve restaurar o estado anterior. |
| RF-07 | Should | Empty state orienta o usuário no primeiro uso. |
| RF-08 | Should | Acelera a edição de armários com muitas peças; não bloqueia o fluxo de uma peça. |
| RF-09 | Should | Continuidade de trabalho entre aberturas, sem quebrar o padrão na primeira vez. |

## 9. Esclarecimentos

### Sessão 2026-11-25 (esclarecimentos antes do plano)

- **Q:** Qual é o alvo real de "igual ao mockup"?
  **R:** Híbrido: paridade funcional com o chrome equivalente do Blender + paleta, espaçamento e ícones do HTML onde
  a UI permitir; **sem titlebar própria** nem abas horizontais.
- **Q:** A fila + modal UNDO (RN-02) entra nesta feature ou fica para depois?
  **R:** Entra agora: todos os botões passam por `enfileirar`/`processar_fila` com um único modal UNDO.
- **Q:** A seleção é uma peça por vez ou múltipla?
  **R:** Múltipla com Shift/Ctrl e ações em lote (mover, apagar, espelhar); clique simples continua uma peça.
- **Q:** O que a janela lembra entre aberturas?
  **R:** Última aba ativa e último tamanho, por cena; cena sem histórico abre em Estrutura no tamanho padrão.
- **Q:** Qual a meta mensurável de desempenho?
  **R:** Abrir < 2 s e preview < 200 ms por interação, medidos por sonda.

### Sessão 2026-11-25 (auditoria e correção)

- **Q:** A sonda de auditoria mediu janelas 2 → 2 e aba `UNSUPPORTED`. O que mudou?
  **R:** A abertura passou a usar `canvas2d.window.open_window` (o mesmo caminho do Editor de Paredes), com entrada
  "Abrir Janela" no painel da Vista 3D, foco da categoria no timer e Estrutura aberta. Nova medição: janelas 1 → 2 e
  `aba_ativa = "Construtor Armário"`.
- **Q:** O preview desenhava peças fora do quadro e o FUNDO cobria tudo?
  **R:** Corrigido: a vista frontal recebe o deslocamento de meio módulo, a ordem de pintura põe o FUNDO primeiro e o
  desenho usa a largura visível (sem ficar sob o painel lateral).
- **Q:** Clique e validação geométrica existiam?
  **R:** Não; agora `selecao.peca_no_ponto` escolhe a peça sob o clique (barra "Selecionado: …") e `validar` aplica
  GEO-001/GEO-002, bloqueando OK e Aplicar.

### Sessão 2026-11-24

- **Q:** A janela própria do Construtor deve ser uma nova janela do sistema (como o editor antigo de paredes: Image Editor em janela nova, restaura a área ao fechar) ou ocupar a área da Vista 3D atual?
  **R:** Nova janela do sistema (abre janela própria com Image Editor).
- **Q:** A janela deve editar o armário v2 (`armario_v2`, painel CAFFMob Draw na Vista 3D) ou o módulo legado (`cabinet_editor`, `btm_cabinet`)?
  **R:** Armário v2 (`armario_v2`, `btm_armario`).
- **Q:** O mockup deve ser replicado pixel-perfeito (paleta, espaçamento, ícones) ou apenas o comportamento equivalente (preview dividido, 7 abas, OK/Aplicar/Cancelar)?
  **R:** Pixel-perfeito (paleta, espaçamento, ícones iguais ao HTML).

## 10. Lacunas

Nenhuma lacuna pendente: as duas dúvidas abertas (paridade visual e fila/modal UNDO) foram decididas na sessão de
esclarecimentos de 2026-11-25 e viraram `RF-08`, `RF-09` e as ações T019–T023.

Fora de escopo por decisão: réplica pixel a pixel da janela inteira em GPU (titlebar própria, abas horizontais,
barra "Movimentação & Precisão"). Se voltar, é feature nova, não esta.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-24 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-11-25 | Auditoria mediu a janela real; requisito de abertura atualizado para "nova janela" verificável e lacuna de paridade registrada | reversa |
| 2026-11-25 | Sessão de esclarecimentos: paridade híbrida, fila agora, seleção múltipla, memória por cena e meta de desempenho integradas (RN-06, RN-07, RF-08, RF-09, NFR) | reversa |
