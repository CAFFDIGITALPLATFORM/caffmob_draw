# Requirements: Zoom e navegação por touchpad no editor de parede

> Identificador: `013-touchpad-editor-parede`
> Data: `2026-10-09`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Esta feature é para o projetista que usa notebook só com o touchpad. Ele passa a navegar na planta do Editor de
Paredes com gestos de dois dedos:
- **pinça** muda o zoom: afastar os dedos aproxima, juntar os dedos afasta;
- **arraste com dois dedos** move a vista.

Uma **barra superior** sobre a planta traz a **lupa com quadrado** (zoom janela): o projetista aperta a lupa,
marca um retângulo na planta, e a vista enquadra esse retângulo.

Hoje o editor só navega com o botão do meio, a roda do mouse e a tecla Home. Os gestos do touchpad não chegam à
planta, e quem não tem mouse fica preso no enquadramento inicial. Touchscreen com vários toques fica fora: o Blender
não entrega esses eventos ao Python.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-02` | A planta 2D do editor tem navegação com pan, zoom mais/menos, zoom janela e enquadrar tudo | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16` | O editor trabalha num rascunho: nada muda no 3D até OK; Esc ou Cancelar descartam | 🟢 |
| `caffmob_draw/walls2d/ops_editor.py#BTM_OT_WallEditorModal._handle` (l. 510-523) | A navegação é tratada antes da caixa de pergunta e das ferramentas: botão do meio (pan), `WHEELUPMOUSE`/`WHEELDOWNMOUSE` (zoom de 15% por passo, ancorado no cursor) e `HOME` (enquadrar). Nenhum `TRACKPAD*` | 🟢 |
| `caffmob_draw/walls2d/ops_editor.py#BTM_OT_WallEditorModal.modal` (l. 441-477) | Evento não tratado volta como `PASS_THROUGH` para a área do Blender por baixo | 🟢 |
| `caffmob_draw/walls2d/window.py#register` (l. 53-56) | A planta é desenhada numa área do Editor de Imagem (`SpaceImageEditor`, `POST_PIXEL`). O gesto que passa direto mexe no zoom da imagem por baixo, não na planta | 🟡 |
| `caffmob_draw/canvas2d/view.py#View2D.zoom, View2D.pan` (l. 36-47) | O zoom ancorado e o pan já existem, em Python puro. O único limite de escala é o piso técnico `1e-6` px/m | 🟢 |
| `tests/test_canvas2d_view.py#test_pan_e_zoom_ancorado` | Já há teste puro do zoom ancorado e do pan | 🟢 |
| `caffmob_draw/move_over/ops_dialog.py#NAV_EVENTS` (l. 30); `caffmob_draw/operators/walls.py` (l. 3450-3452) | Outros modais já reconhecem `TRACKPADPAN` e `TRACKPADZOOM`, mas só para deixá-los passar à viewport 3D | 🟢 |
| `docs/rag/blender-api/corpus/bpy_types_enum_items/event_type_items.md` (TRACKPADPAN, TRACKPADZOOM) | O Blender 5.2 tem os tipos de evento "Mouse/Trackpad Pan" e "Mouse/Trackpad Zoom" | 🟢 |
| `docs/rag/blender-api/corpus/bpy.types.Event.md#bpy.types.Event.mouse_prev_x` (e `mouse_prev_y`, `mouse_x`, `mouse_y`, `ctrl`) | Os campos para ler a posição atual e a anterior existem. O corpus **não diz** como o delta do gesto é codificado neles | 🟡 |
| `docs/rag/blender-api/corpus/bpy.types.PreferencesInput.md#bpy.types.PreferencesInput.invert_zoom_wheel` | O Blender tem a preferência "inverter zoom pela roda". O editor de parede hoje a ignora | 🟢 |
| `caffmob_draw/walls2d/panels.py#BTM_PT_WallEditorTools` (l. 27-36) | Hoje as ferramentas e o "Enquadrar" (`caffmob.wall_editor_fit`) ficam só no painel lateral; a planta não tem barra superior | 🟢 |
| `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-02` | A 002 pedia "zoom janela" na navegação da planta; o código atual não tem | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista em visita à obra, só com notebook | Desenhar e conferir a planta sem mouse | Abre o editor, afasta dois dedos sobre um canto da sala para ver o encontro de perto, arrasta com dois dedos até o próximo canto e junta os dedos para ver a sala inteira |
| Projetista com touchpad em Linux X11 ou Windows | Dar zoom mesmo quando a pinça chega como Ctrl + roda | Faz a pinça; o sistema manda Ctrl + roda; a planta dá zoom do mesmo jeito |
| Projetista com mouse | Continuar navegando como hoje | Usa o botão do meio, a roda e Home sem notar diferença |
| Projetista conferindo um detalhe | Ver de perto um encontro de paredes sem várias pinças | Aperta a lupa na barra superior, marca um retângulo em volta do canto, e o canto enche a planta |

## 4. Regras de negócio novas ou alteradas

1. **RN-01, a pinça dá zoom na planta.** Com o cursor sobre a planta, um gesto `TRACKPADZOOM` muda a escala da
   vista. Afastar os dedos aproxima (a escala sobe). Juntar os dedos afasta (a escala desce). O ponto da planta sob
   o cursor fica parado na tela. 🟢
   - Origem: `caffmob_draw/canvas2d/view.py#View2D.zoom`
   - Tipo: nova
2. **RN-02, o zoom acompanha o gesto.** O fator de zoom é proporcional ao tamanho do movimento da pinça em cada
   evento. Um gesto curto muda pouco, um gesto longo muda muito, sem degraus fixos. A mesma pinça, feita com a mesma
   amplitude, dá o mesmo resultado não importa o zoom de partida. 🟡
   - Sem limite de zoom: a escala segue só o piso técnico de `View2D.zoom`, como a roda hoje (esclarecimento
     2026-10-10, Q1).
   - Tipo: nova
3. **RN-03, arraste com dois dedos move a vista.** Um gesto `TRACKPADPAN` desloca a vista como o botão do meio:
   o conteúdo da planta segue os dedos. 🟢
   - Origem: `caffmob_draw/canvas2d/view.py#View2D.pan`
   - Tipo: nova
4. **RN-04, Ctrl + roda é zoom.** Ctrl + `WHEELUPMOUSE`/`WHEELDOWNMOUSE` dá zoom na planta, como a roda sem Ctrl.
   Isso cobre os sistemas onde a pinça chega como Ctrl + roda (X11, alguns drivers do Windows). Ctrl + roda não
   dispara nenhum outro atalho do editor. Hoje isso já acontece, porque o editor ignora o Ctrl na roda. A feature
   torna esse comportamento um requisito, para ninguém quebrá-lo depois. 🟢
   - Origem: `caffmob_draw/walls2d/ops_editor.py#_handle` (l. 519-521)
   - Tipo: alterada (de comportamento implícito para regra)
   - A roda e o Ctrl + roda obedecem à preferência do Blender `PreferencesInput.invert_zoom_wheel`: com ela ligada,
     roda para cima afasta. A pinça não muda com essa preferência (esclarecimento 2026-10-10, Q2).
5. **RN-05, navegar não mexe no desenho.** Pinça e arraste com dois dedos funcionam em todas as ferramentas
   (Selecionar/Mover, Construir Parede) e estados (mira ativa, digitação de medida, caixa de pergunta aberta,
   arraste de vértice em curso). Eles não criam, não fecham, não cancelam e não confirmam nada. Também não gravam
   passo de desfazer. A medida digitada, o trecho em construção e a pergunta aberta continuam como estavam. 🟢
   - Origem: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16`; ordem atual de `_handle`
   - Tipo: nova
6. **RN-06, o gesto fica com a planta.** Um gesto de touchpad sobre a planta é consumido pelo editor. Ele não chega
   ao Editor de Imagem por baixo. Fora da planta (painel lateral, cabeçalho), o gesto segue para o Blender como
   hoje. 🟡
   - Origem: `caffmob_draw/walls2d/ops_editor.py#_local`, `modal`
   - Tipo: nova
7. **RN-07, barra superior com zoom janela.** A planta ganha uma barra no topo. O primeiro botão é a lupa com
   quadrado (zoom janela). Apertar a lupa liga o modo zoom janela, e o botão fica realçado. O projetista marca um
   retângulo na planta (clicar e arrastar). Ao soltar, a vista enquadra o retângulo: o centro dele vai para o centro
   da planta, e o lado que limita cabe inteiro. Depois o modo desliga e a ferramenta anterior volta. Esc ou clicar
   de novo na lupa cancela o modo sem mexer na vista. Um retângulo menor que 5 px de lado não muda a vista. O modo
   zoom janela não cria, não seleciona e não altera paredes, e não grava passo de desfazer (esclarecimento
   2026-10-10). 🟡
   - Origem: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-02`; `View2D.fit`
   - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Pinça com dois dedos sobre a planta dá zoom ancorado no cursor, no sentido da RN-01 | Must | Afastar os dedos sobre um vértice aumenta a escala, e o vértice continua sob o cursor com erro ≤ 1 px | 🟢 |
| RF-02 | O fator de zoom vem do tamanho do gesto (RN-02), sem passo fixo de 15% | Must | Dois eventos de pinça com deltas diferentes produzem fatores diferentes; uma pinça de ida seguida da mesma pinça de volta devolve a escala inicial com erro ≤ 0,1% | 🟡 |
| RF-03 | Arraste com dois dedos sobre a planta move a vista (RN-03) | Must | Um arraste de 100 px para a direita leva um ponto da planta 100 px para a direita na tela (± 1 px) | 🟢 |
| RF-04 | Ctrl + roda sobre a planta dá zoom, igual à roda sem Ctrl (RN-04) | Must | Ctrl + roda para cima aproxima 15% ancorado no cursor; nada mais muda na sessão | 🟢 |
| RF-05 | Os gestos funcionam em todos os estados do editor e não alteram o rascunho (RN-05) | Must | Com "2.4" digitado no meio de um trecho, a pinça muda o zoom, e o texto digitado, o trecho em curso e o histórico de desfazer continuam iguais | 🟢 |
| RF-06 | O gesto sobre a planta não vaza para o Editor de Imagem por baixo; fora da planta, passa direto (RN-06) | Must | Depois de uma pinça sobre a planta, o zoom do Editor de Imagem da área é o mesmo de antes; uma pinça sobre o painel lateral não muda a escala da planta | 🟡 |
| RF-07 | Mouse continua igual: botão do meio, roda (15% por passo) e Home | Must | Os testes atuais do editor passam sem mudança; roda para cima aproxima 15% como antes | 🟢 |
| RF-08 | Teste automatizado, sem touchpad físico, da conversão gesto → zoom/pan: fator a partir do delta, sentido, ponto âncora parado, ida e volta | Must | O teste puro passa no `pytest` sem Blender; um teste no Blender em segundo plano envia eventos simulados ao modal e confere a escala | 🟢 |
| RF-10 | Barra superior na planta com a lupa com quadrado (zoom janela), conforme a RN-07 | Must | Apertar a lupa e marcar um retângulo em volta de um canto de 600 × 400 mm faz o canto ocupar a planta, com o retângulo inteiro visível e centrado (± 2 px) | 🟡 |
| RF-11 | A roda e o Ctrl + roda obedecem à preferência "inverter zoom pela roda" (RN-04) | Must | Com a preferência ligada, roda para cima diminui a escala em 15%; com ela desligada, aumenta | 🟢 |
| RF-09 | Registrar o editor de armário (`cabinet_editor/ops_editor.py`, zoom só por roda) como candidato a feature seguinte | Could | O roadmap da 013 tem a nota de feature seguinte | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Compatibilidade | Antes de escrever o núcleo, uma **prova** no Blender 5.2 mostra como o delta da pinça e do arraste chega no `Event` (posição atual × anterior, sinal, unidade). Se a codificação mudar entre versões, a diferença fica em `caffmob_draw/compat.py` | O corpus confirma os tipos e os campos, mas não a codificação do delta (Princípio II, "Medir antes de cortar") | 🟡 |
| Desempenho | Cada evento de gesto faz só a conta do zoom ou do pan e um redesenho, sem recalcular encaixe nem índice de inferência por causa do gesto | O touchpad manda dezenas de eventos por segundo; `_update_snap` roda em todo evento hoje | 🟡 |
| Manutenibilidade | A conversão gesto → fator/deslocamento fica numa função pura (sem `bpy`), testável fora do Blender, junto do núcleo 2D | Padrão de `canvas2d/view.py` e `tests/test_canvas2d_view.py` | 🟢 |
| Qualidade | `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erro; textos e comentários novos em português | `CLAUDE.md`, "Comandos" e "Regras do código" | 🟢 |
| Usabilidade | Nenhum controle novo na interface: o gesto funciona sem configuração (Princípio I, "Simples por fora") | `.reversa/principles.md#I` | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Funcionalidade: Navegação por touchpad no Editor de Paredes

  Contexto:
    Dado o Editor de Paredes aberto com uma sala de 3.900 × 2.700 mm
    E o cursor sobre o vértice do canto inferior esquerdo da planta

  Cenário: Afastar os dedos aproxima, ancorado no cursor (RF-01)
    Quando o projetista afasta dois dedos no touchpad
    Então a escala da planta aumenta
    E o vértice continua sob o cursor, com erro de no máximo 1 px

  Cenário: Juntar os dedos afasta (RF-01)
    Quando o projetista junta dois dedos no touchpad
    Então a escala da planta diminui
    E o vértice continua sob o cursor, com erro de no máximo 1 px

  Cenário: O zoom acompanha o tamanho do gesto (RF-02)
    Quando chegam dois eventos de pinça, um com o dobro do delta do outro
    Então o evento maior muda a escala mais que o menor
    E nenhum dos dois muda a escala em exatamente 15%

  Cenário: Ida e volta devolvem a escala (RF-02)
    Dado a escala inicial da planta
    Quando o projetista afasta os dedos e depois os junta na mesma amplitude
    Então a escala volta à inicial, com erro de no máximo 0,1%

  Cenário: Arraste com dois dedos move a vista (RF-03)
    Quando o projetista arrasta dois dedos 100 px para a direita
    Então o vértice aparece 100 px mais à direita na tela, com erro de no máximo 1 px
    E a escala não muda

  Cenário: Ctrl + roda dá zoom (RF-04)
    Quando o sistema manda Ctrl + roda para cima
    Então a escala aumenta 15%, ancorada no cursor
    E nenhuma ferramenta, seleção ou medida muda

  Cenário: Pinça durante a digitação de medida (RF-05)
    Dado a ferramenta Construir Parede com um trecho em curso
    E "2.4" digitado como comprimento
    Quando o projetista faz uma pinça
    Então a escala muda
    E o texto digitado continua "2.4"
    E o trecho em curso não foi criado nem cancelado
    E o histórico de desfazer tem o mesmo número de passos

  Cenário: Pinça com a caixa de pergunta aberta (RF-05)
    Dado a pergunta "Fechar o contorno?" aberta
    Quando o projetista faz uma pinça
    Então a escala muda
    E a pergunta continua aberta, sem resposta

  Cenário: Pinça durante o arraste de um vértice (RF-05)
    Dado um vértice sendo arrastado com a Selecionar/Mover
    Quando o projetista faz uma pinça
    Então a escala muda
    E o arraste continua em curso

  Cenário: O gesto não vaza para o Editor de Imagem (RF-06)
    Quando o projetista faz uma pinça sobre a planta
    Então o zoom do Editor de Imagem da área continua o mesmo

  Cenário: Gesto fora da planta segue para o Blender (RF-06)
    Quando o projetista faz uma pinça sobre o painel lateral
    Então a escala da planta não muda

  Cenário: Mouse continua igual (RF-07)
    Quando o projetista gira a roda para cima, sem Ctrl
    Então a escala aumenta 15%, ancorada no cursor
    E o botão do meio continua arrastando a vista
    E Home continua enquadrando a planta

  Cenário: Roda obedece à preferência de inverter zoom (RF-11)
    Dado a preferência "Inverter zoom pela roda" ligada
    Quando o projetista gira a roda para cima
    Então a escala diminui 15%, ancorada no cursor
    E uma pinça de afastar os dedos continua aumentando a escala

  Cenário: Zoom janela enquadra o retângulo (RF-10)
    Quando o projetista aperta a lupa na barra superior
    E marca um retângulo em volta do canto da sala
    Então a vista enquadra o retângulo, centrado na planta
    E o modo zoom janela desliga e a ferramenta anterior volta
    E nenhuma parede foi criada, selecionada ou alterada

  Cenário: Cancelar o zoom janela (RF-10, caso negativo)
    Dado o modo zoom janela ligado
    Quando o projetista tecla Esc
    Então a vista não muda
    E o desenho em curso não é cancelado

  Cenário: Retângulo pequeno demais (RF-10, caso negativo)
    Dado o modo zoom janela ligado
    Quando o projetista marca um retângulo de 3 × 3 px
    Então a vista não muda

  Cenário: Gesto com delta nulo não muda nada (caso negativo, RF-02)
    Quando chega um evento de pinça com delta zero
    Então a escala e o centro da vista continuam iguais
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02 | Must | É o pedido central: zoom por pinça no notebook |
| RF-03 | Must | Sem arraste, o zoom por pinça leva a pontos de onde o projetista sem mouse não sai |
| RF-04 | Must | Em X11 e em parte do Windows, a pinça só chega assim |
| RF-05, RF-06 | Must | Navegar não pode estragar o desenho, nem mexer na área escondida |
| RF-07 | Must | Não quebrar quem usa mouse |
| RF-08 | Must | Sem touchpad no teste automatizado, só a prova simulada protege a regra |
| RF-10 | Must | Pedido do titular no esclarecimento de 2026-10-10; cobre o "zoom janela" da 002 |
| RF-11 | Must | Resposta Q2 do esclarecimento |
| RF-09 | Could | Só registro; a implementação é outra feature |
| RNF de compatibilidade (prova do delta) | Must | O corpus não documenta a codificação do delta |
| RNF de desempenho | Should | Evita tremedeira no gesto, mas não bloqueia o uso |

## 9. Esclarecimentos

### Sessão 2026-10-10

- **Q:** Limites de zoom: manter sem limite, como a roda, ou criar mínimo e máximo?
  **R:** a) Manter sem limite, como a roda faz hoje. → RN-02.
- **Q:** A roda e o Ctrl + roda devem obedecer à preferência "Inverter zoom pela roda" do Blender?
  **R:** a) Sim, a roda e o Ctrl + roda obedecem; a pinça não muda. → RN-04, RF-11.
- **Acréscimo do titular:** "Deve ter um toolbar superior: uma lupa com quadrado que, ao apertar nela, focará no
  quadrado." Interpretado como zoom janela (marcar um retângulo e enquadrá-lo), o mesmo "zoom janela" da 002 RF-02.
  → RN-07, RF-10.

## 10. Lacunas

n/a: nenhuma lacuna aberta.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-10 | Esclarecimentos: sem limite de zoom; roda obedece a "inverter zoom"; barra superior com zoom janela (RN-07, RF-10, RF-11) | reversa-clarify |
