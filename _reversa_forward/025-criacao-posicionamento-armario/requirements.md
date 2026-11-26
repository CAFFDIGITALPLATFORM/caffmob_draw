# Requirements: Criação direta, posicionamento e galeria clara do armário v2

> Identificador: `025-criacao-posicionamento-armario`
> Data: `2026-11-26`
> Origem: pedido do titular na rodada de 2026-11-26 — “Criar armário” deve abrir a viewport direto; depois de
> **Aplicar**, perguntar **Escolher** ou **Cursor 3D**; no modo Escolher, uma prévia em linhas acompanha o mouse e as
> setas mudam a orientação; a galeria de blocos/texturas deve seguir o padrão visual dos dois pacotes em `docs/`.
> Pasta da extração reversa: `_reversa_sdd/`
> Mockup do Construtor: `novo_arm_building/CAFF_MOB_Construtor_Armarios_Blender_5_2/caff_construtor_armarios_blender_5_2/mockup_construtor_armarios.html`
> Galeria: `docs/Caff+Mob+Biblioteca+Mockup.tar.gz` e `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O construtor v2 já monta o armário na viewport, mas o fim do fluxo não dizia **onde** o armário entra na cena: o
**Aplicar** só gravava o passo de desfazer no lugar atual. Esta feature fecha o caminho completo pedido pelo titular:

1. **Criar armário** abre o Construtor v2 na própria **Vista 3D** (sem abrir a janela própria da 023).
2. Depois de **Aplicar** — tanto no painel da Vista 3D quanto no rodapé da janela 023 — aparece o aviso
   **“Onde adicionar o armário?”** com **Escolher na viewport** e **Cursor 3D**.
3. **Escolher** esconde o armário real, mostra uma **caixa de arame** nas medidas do spec acompanhando o mouse no
   piso; as setas **cima/baixo/esquerda/direita** mudam a orientação, o clique confirma e Esc (ou botão direito)
   cancela devolvendo posição, giro e visibilidade.
4. **Cursor 3D** coloca a raiz do armário na posição do cursor da cena, preservando a orientação; as peças filhas
   acompanham.
5. A **galeria de blocos/texturas** (painel Biblioteca CAFFMob) passa a usar a paleta **Light** do mockup da
   Biblioteca, com os tokens de janela, sidebar, card, tinta, primário e teal.

A paridade **integral** do mockup do Construtor (toolbar completa, export JSON, titlebar, abas horizontais, menu de
contexto, popover de medida, arraste de peças, cutlist) já tem escopo e auditoria próprios na feature **023**
(`D-05`, paridade híbrida; `cross-check.md` com 0 HIGH após a decisão). Esta feature **não reabre** esse escopo: ela
entrega o fluxo de criação/posicionamento e a aparência da galeria pedidos agora, e registra a fronteira em §10.

## 2. Contexto a partir do legado e dos artefatos

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `caffmob_draw/library_panel/ops_cabinet.py` | `BTM_OT_LibraryCreateCabinet.invoke` chama `caffmob.cabinet_editor('INVOKE_DEFAULT')`; o construtor v2 abre na Vista 3D, sem janela nova. | 🟢 |
| `caffmob_draw/armario_v2/ops.py` | `BTM_OT_ArmarioV2Abrir` cria/semeia o armário v2 e o painel da Vista 3D; `BTM_OT_ArmarioV2Aplicar` grava o passo de desfazer. | 🟢 |
| `caffmob_draw/armario_v2/ops_window.py` | O Aplicar da janela 023 grava o snapshot e mantém a janela aberta; agora também chama o aviso de posicionamento. | 🟢 |
| `caffmob_draw/armario_v2/build.py` | A raiz é um EMPTY em `Marcenaria`; as cinco chapas são filhas com `matrix_parent_inverse = Identity`; mover/rotacionar a raiz move o conjunto. | 🟢 |
| `_reversa_forward/023-janela-mockup-construtor/requirements.md` | `RN-01`, `RF-01` e `D-05`: janela própria com paridade **híbrida**; sem titlebar/abas horizontais. | 🟢 |
| `_reversa_forward/023-janela-mockup-construtor/audit/cross-check.md` | 0 CRITICAL, 0 HIGH depois da Fase 7; A003 resolvido por decisão (híbrida). | 🟢 |
| `novo_arm_building/.../mockup_construtor_armarios.html` | Toolbar, preview frontal+lateral, 7 abas, empty state, menu de contexto, popover de medida, contrato de chapas, lista de corte, export JSON, tema, animação. | 🟡 |
| `docs/Caff+Mob+Biblioteca+Mockup.tar.gz` | `App.tsx` Light warm: janela `#FFFBF5`, sidebar `#FFF8EC`, card-art `#F5EFE3`, tinta `#2B1A0E`, primário `#B45309`, teal `#0E7C74`. | 🟢 |
| `docs/Elicitacao+Requisitos+Caff+Mob+Biblioteca.tar.gz` | RF01 abas Biblioteca/Blocos/Texturas; RF09 Light padrão/Dark; RF13 alvo de 44 px; RF14 responsivo. | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Marceneiro projetista | Montar e **colocar** o armário no lugar certo da parede | Monta a caixa, Aplicar, escolhe a posição com a prévia em linhas e confirma com o clique. |
| Projetista de interiores | Posicionar vários armários sem errar a frente | Usa as setas para virar a frente do armário para a parede/ambiente e confirma. |
| Usuário do Promob | Manter o fluxo conhecido | Cria pelo botão da Biblioteca, vê o construtor na viewport e usa Cursor 3D quando já posicionou o cursor. |
| Designer da Biblioteca | Reconhecer a mesma linguagem visual do mockup | Abre a galeria e vê sidebar, cards e seleção na paleta clara do pacote de requisitos. |

## 4. Regras de negócio novas ou alteradas

1. **RN-01 (Criar armário abre a viewport, não a janela 023):** o botão **Criar armário** da Biblioteca e a ação
   `caffmob.cabinet_editor` abrem o Construtor v2 **na Vista 3D atual**; a contagem de janelas do Blender não aumenta
   e a Vista 3D do usuário não muda de tipo. A janela própria da 023 continua existindo por **Abrir Janela**, mas não
   é o caminho de “Criar armário”. 🟢
   - Origem: pedido do titular; `ops_cabinet.invoke`; `BTM_OT_ArmarioV2Abrir`.
   - Tipo: confirmada/verificada.
2. **RN-02 (Aplicar pergunta onde adicionar):** todo **Aplicar** do armário v2 — no painel da Vista 3D
   (`BTM_OT_ArmarioV2Aplicar`) e no rodapé da janela 023 (`BTM_OT_ArmarioV2WindowAplicar`) — grava o snapshot e, em
   seguida, abre o aviso **“Onde adicionar o armário?”** com exatamente dois caminhos: **Escolher na viewport** e
   **Cursor 3D**. O aviso não escreve na cena; só encaminha. 🟢
   - Origem: pedido do titular; `ops_placement.abrir_prompt`.
   - Tipo: nova.
3. **RN-03 (Escolher = caixa de arame que acompanha o mouse):** no modo Escolher, o armário real fica **oculto** e
   uma **caixa de arame** com as medidas do spec (8 vértices, 12 arestas, nenhuma face, `display_type='WIRE'`)
   acompanha o mouse no piso (`z = 0`). A caixa representa o volume do armário, não as chapas individuais. 🟢
   - Origem: pedido do titular; `placement.criar_cage`, `placement.chao`.
   - Tipo: nova.
4. **RN-04 (Setas cardeais):** com a prévia ativa, **seta cima** = 0° (frente de construção), **seta direita** = 90°,
   **seta baixo** = 180°, **seta esquerda** = 270°; **R** gira +90°. A rotação é em torno de Z, no centro da raiz, e
   as peças filhas acompanham. 🟢
   - Origem: pedido do titular; `placement.ORIENTACOES`, `placement.seta_para_yaw`.
   - Tipo: nova.
5. **RN-05 (Clique confirma; Esc/botão direito cancelam):** o clique esquerdo confirma a posição e o giro da prévia,
   remove a caixa, revela o armário e grava um passo de desfazer; **Esc** ou **botão direito** cancelam, removem a
   caixa e restauram a posição, o giro e a visibilidade anteriores. 🟢
   - Origem: pedido do titular; `BTM_OT_ArmarioV2PlaceChoose`.
   - Tipo: nova.
6. **RN-06 (Cursor 3D):** a opção **Cursor 3D** move a raiz para `scene.cursor.location` no plano do cursor,
   preservando o giro atual, e as peças filhas acompanham; é um passo de desfazer. 🟢
   - Origem: pedido do titular; `placement.no_cursor`.
   - Tipo: nova.
7. **RN-07 (Sem viewport, cai no Cursor 3D):** quando não há uma área `VIEW_3D` (scripts, `--background`, contexto de
   janela sem viewport), o modo Escolher executa o caminho determinístico do Cursor 3D em vez de falhar. 🟢
   - Origem: robustez de plataforma; ensaio `EXEC_DEFAULT`.
   - Tipo: nova.
8. **RN-08 (Galeria na paleta Light do mockup):** o painel da Biblioteca usa os tokens do pacote:
   janela `#FFFBF5`, sidebar `#FFF8EC`, card-art `#F5EFE3`, tinta `#2B1A0E`, primário `#B45309` e teal `#0E7C74`,
   com texto legível e cards/controles sobre fundo claro. A estrutura funcional (abas, busca, categorias, grade 2×3,
   seleção laranja, filtros Madeira/Alumínio/Blindex, avatar/Pin/controles) permanece a existente. 🟢
   - Origem: pedido do titular; `library_panel/style.py`, `draw.py`, `detail_core.py`.
   - Tipo: alterada (aparência).
9. **RN-09 (Fronteira de paridade do mockup):** a paridade visual/funcional **integral** do mockup do Construtor é
   escopo da 023, com a decisão híbrida `D-05` e o `cross-check.md` de 0 HIGH. Esta feature cobre o fluxo
   criar → aplicar → escolher/cursor e a galeria; não adiciona toolbar completa, export JSON, titlebar, abas
   horizontais, menu de contexto, popover de medida, arraste de peças, cutlist ou troca de tema. 🟢
   - Origem: 023 `D-05`/`A003`; pedido atual.
   - Tipo: confirmada (fronteira de escopo, não lacuna).

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | **Criar armário** abre o Construtor v2 na Vista 3D direto, sem criar janela nova. | Must | Na Biblioteca, acionar “Criar armário” deixa o armário v2 ativo, o painel do construtor disponível na Vista 3D e `len(window_manager.windows)` inalterado; a janela 023 só abre por “Abrir Janela”. | 🟢 |
| RF-02 | Depois de **Aplicar**, perguntar onde adicionar, com **Escolher na viewport** e **Cursor 3D**. | Must | Aplicar no painel da Vista 3D e Aplicar no rodapé da janela 023 chamam o aviso uma vez; o popup tem os dois botões e não escreve na cena. | 🟢 |
| RF-03 | No modo **Escolher**, mostrar a caixa de arame do armário acompanhando o mouse. | Must | O armário real fica oculto; a caixa tem 8 vértices, 12 arestas, 0 faces, `WIRE` e as medidas do spec; ao mover o mouse no piso, a caixa se desloca no plano `z = 0`. | 🟢 |
| RF-04 | As setas cima/baixo/esquerda/direita mudam a orientação da prévia; R gira +90°. | Must | Cima = 0°, direita = 90°, baixo = 180°, esquerda = 270°; R soma 90°; o giro é aplicado à caixa e, ao confirmar, à raiz. | 🟢 |
| RF-05 | Clique confirma; Esc/botão direito cancelam restaurando o estado. | Must | Clique remove a caixa, revela o armário na posição/giro escolhidos e grava undo; Esc/botão direito removem a caixa e devolvem loc/rot/hide anteriores. | 🟢 |
| RF-06 | **Cursor 3D** cria/posiciona o armário na posição do Cursor 3D. | Must | A raiz vai para `scene.cursor.location`, o giro atual é preservado, as peças filhas acompanham e há um passo de desfazer. | 🟢 |
| RF-07 | Sem viewport, o modo Escolher cai no Cursor 3D. | Should | `armario_v2_place_choose('EXEC_DEFAULT')` posiciona no cursor e retorna `FINISHED`, sem exceção. | 🟢 |
| RF-08 | A galeria de blocos/texturas segue a paleta Light do mockup da Biblioteca. | Must | Os tokens de janela/sidebar/card/tinta/primário/teal são os do pacote; cartões e controles continuam legíveis; abas, busca, grade, seleção e filtros existentes não somem. | 🟢 |
| RF-09 | O fluxo e a aparência têm prova automatizada e a versão é fechada. | Must | Testes puros das setas/caixa/tokens e ensaio de janela com 16 checagens passam; `check_api.py` limpo; CHANGELOG e versão coerentes. | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Criar a caixa e responder ao mouse/setas em menos de um frame perceptível, sem regenerar as chapas. | A caixa é uma malha de 8 vértices; mover/rotacionar só altera a transformação. | 🟢 |
| Segurança | O aviso não escreve na cena; Esc restaura o estado exato; Aplicar continua sendo um passo de desfazer. | `BTM_OT_ArmarioV2PlacePrompt` só encaminha; `_restaurar`/`_limpar` guardam loc/rot/hide. | 🟢 |
| Compatibilidade | Sem viewport (`--background`, scripts), o fluxo não quebra: cai no Cursor 3D. | Ensaio `EXEC_DEFAULT` e `abrir_prompt` com `bpy.app.background`. | 🟢 |
| Acessibilidade | O aviso nomeia os dois caminhos por texto e ícone; a caixa de arame é distinguível do armário real. | `draw` do popup; `WIRE` + ocultação do real. | 🟢 |
| i18n | Rótulos novos (“Onde adicionar o armário?”, “Escolher na viewport”, “Cursor 3D”) entram em pt_BR/en_US. | `tr()` e catálogos do add-on. | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Criar armário abre a viewport direto
  Dado o Blender em modo objeto e a Biblioteca CAFFMob aberta
  Quando aciono "Criar armário"
  Então o Construtor v2 fica ativo na Vista 3D e nenhuma janela nova do Blender é criada

Cenário: Aplicar pergunta onde adicionar
  Dado um armário v2 montado na Vista 3D
  Quando clico em Aplicar no painel do construtor
  Então o aviso "Onde adicionar o armário?" aparece com "Escolher na viewport" e "Cursor 3D"
  E nada na cena mudou de posição ainda

Cenário: Escolher mostra a caixa de arame e acompanha o mouse
  Dado o aviso aberto
  Quando escolho "Escolher na viewport" e movo o mouse sobre o piso
  Então o armário real fica oculto e uma caixa de arame com as medidas do armário acompanha o mouse

Cenário: Setas mudam a orientação e o clique confirma
  Dado o modo Escolher ativo com a caixa de arame
  Quando pressiono a seta direita e clico no piso
  Então a caixa gira 90° e o armário é revelado naquela posição e orientação, num passo de desfazer

Cenário: Esc cancela e restaura
  Dado o modo Escolher ativo depois de mover a caixa
  Quando pressiono Esc
  Então a caixa some e o armário volta à posição, ao giro e à visibilidade anteriores

Cenário: Cursor 3D posiciona o armário
  Dado o Cursor 3D em (1,2, -0,8, 0)
  Quando escolho "Cursor 3D"
  Então a raiz do armário vai para essa posição, mantém o giro e leva as peças filhas

Cenário: Aplicar na janela 023 também pergunta
  Dado o armário v2 aberto na janela própria da 023
  Quando clico em Aplicar no rodapé
  Então o aviso de posicionamento abre na Vista 3D principal com os dois caminhos

Cenário: Galeria na paleta clara
  Dado o painel da Biblioteca CAFFMob aberto
  Então a janela, a sidebar, os cards, a tinta, o primário e o teal usam os tokens Light do mockup
  E abas, busca, grade, seleção e filtros continuam funcionando
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 | Must | É o começo do fluxo pedido; sem ele o usuário cai numa janela que não quer. |
| RF-02 | Must | É a pergunta central do pedido depois do Aplicar. |
| RF-03 | Must | Sem a prévia em linhas, “Escolher” não tem feedback. |
| RF-04 | Must | As setas são o controle de orientação pedido. |
| RF-05 | Must | Confirmação/cancelamento são o fecho seguro do posicionamento. |
| RF-06 | Must | É o segundo caminho do aviso. |
| RF-07 | Should | Robustez para scripts e `--background`; não bloqueia a GUI. |
| RF-08 | Must | Aparência da galeria é pedido explícito do titular. |
| RF-09 | Must | Fechamento com prova e versão, no padrão do projeto. |

## 9. Esclarecimentos e decisões desta rodada

- **Q:** “Criar armário” deve abrir a janela 023 ou a viewport?
  **R:** A viewport, direto. A 023 continua acessível por **Abrir Janela**; este pedido não muda a 023.
- **Q:** O aviso aparece também quando o Aplicar vem da janela 023?
  **R:** Sim. O aviso é aberto na Vista 3D principal; o Aplicar da 023 grava o snapshot e pergunta em seguida.
- **Q:** Qual é a “frente” do armário no giro?
  **R:** 0° é a frente de construção; cima = 0°, direita = 90°, baixo = 180°, esquerda = 270°.
- **Q:** A prévia é o armário inteiro em arame ou só o volume?
  **R:** O volume do armário (caixa de 8 vértices, 12 arestas, sem faces), nas medidas do spec; o real fica oculto.
- **Q:** O que acontece sem viewport?
  **R:** O modo Escolher cai no Cursor 3D, que é determinístico.
- **Q:** A galeria precisa mudar de categorias (Armários/Portas/Janelas) e ter tema escuro?
  **R:** Nesta rodada, **aparência**: paleta Light do mockup. Categorias e alternador Dark não entram; a estrutura
  funcional existente é preservada.
- **Q:** A paridade integral do mockup do Construtor entra nesta feature?
  **R:** Não. Ela é escopo da 023 (D-05 híbrida); a 025 entrega o fluxo pedido e a galeria, e a fronteira fica
  registrada em §10 e no `cross-check.md`.

## 10. Fora de escopo (fronteira explícita)

- Toolbar completa do mockup do Construtor (views frontal/lateral/top, export JSON, tema, painel lateral, abrir/fechar
  tudo), menu de contexto da janela 023, popover de medida, arraste de peças, grade da matriz, “Apenas Laterais”,
  contrato de chapas na janela 023, cutlist modal e troca Light/Dark: **escopo da 023** (`D-05`, `A003`), não desta
  feature. O `cross-check.md` da 023 registra 0 HIGH depois da decisão híbrida.
- Categorias da Biblioteca (Armários/Portas/Janelas/Armários autorais): mudança de conteúdo, não de aparência; a
  paleta é o que esta feature entrega.
- Tema escuro alternável: a paleta Light é o padrão; o alternador não foi pedido nesta rodada.
- Persistir a posição escolhida como propriedade do armário: a posição já é a transformação da raiz; não há campo novo.

## 11. Lacunas

Nenhuma lacuna aberta para o fluxo pedido. A fronteira de paridade do mockup está **decidida** na 023 e não é uma
lacuna desta feature. O que ainda não tem prova visual é o desenho do popup em si (o print do Blender não captura
popups), registrado nas limitações da auditoria.

## 12. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-26 | Versão inicial gerada para o ciclo `/reversa-audit` do pedido de criação/posicionamento e galeria | reversa |
