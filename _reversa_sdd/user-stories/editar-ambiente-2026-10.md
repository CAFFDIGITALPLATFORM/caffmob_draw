# Histórias de Usuário — Editar o Ambiente (re-extração 2026-10)

> Gerado pelo **Writer** (Reversa) em 2026-10-10 a partir das specs das units `walls2d`, `canvas2d`, `openings`,
> `move_over`, `measure`, `selection`, `stick`, `collision`, `geometry_free` e `inspection`. As histórias descrevem o
> comportamento **atual** do código (engenharia reversa), não um roadmap.
>
> Legenda: 🟢 confirmado no código pela spec da unit · 🟡 inferido (intenção, prioridade, persona) · 🔴 lacuna que depende
> de validação humana ou de execução no Blender. Confirmação de código não implica validação visual no Blender.
> Referências no formato `<unit>/requirements.md#RF-xx` / `#CA-xx` (caminhos relativos a `_reversa_sdd/`).

## Personas

Não existe `_reversa_sdd/personas.md`; as personas vêm de `soul.md` e `domain.md`.

| ID | Persona | Fonte | Confiança |
|---|---|---|---|
| P1 | **Projetista de móveis planejados**: desenha o ambiente (paredes, portas, janelas) e posiciona os módulos para apresentar ao cliente | `soul.md` ("marceneiros e projetistas de móveis planejados no Brasil"); `domain.md` RN-CUSTOMIZE-16 ("o projetista") | 🟡 |
| P2 | **Marceneiro**: confere encaixe, folgas, abertura de portas e colisões antes de produzir | `soul.md`; fluxo "estilo Promob" | 🟡 |

---

## US-AMB-01 — Desenhar as paredes na planta 2D

🟡 **Como** projetista (P1), **quero** desenhar as paredes numa planta vista de cima com medidas digitadas, **para** levantar o ambiente do cliente com precisão de obra, sem modelar em 3D.

Referências: `walls2d/requirements.md#RF-02`, `#RF-04`, `#RF-13`; `canvas2d/requirements.md#RF-04`, `#RF-05`.

**Critérios de aceitação**

- 🟢 **Feliz — lápis com direção travada** (`walls2d#CA-09`): Dado a ferramenta de desenho, o ponto inicial clicado e o mouse a 1° do eixo X; Quando digito "4" (unidade m) e Enter; Então um trecho de 4 m é criado na direção 0° (encaixe ortogonal ≤ 2,5°) e a direção fica travada para os próximos Enter.
- 🟢 **Feliz — fechar contorno** (`walls2d#CA-11`): Dado um desenho com 2+ trechos e o cursor a ≤ 15 px do primeiro nó; Quando clico e respondo "Sim"; Então o trecho de fechamento é acrescentado, a cadeia fecha com a espessura para fora (`outward_side`, RN-04) e a ferramenta volta a Selecionar.
- 🟢 **Falha — Enter sem direção** (`walls2d#CA-10`): Dado o cursor exatamente sobre o ponto inicial; Quando digito "4" e Enter; Então aparece "Mova o mouse na direção da parede ou use as setas do teclado" e nenhum trecho é criado.
- 🟢 **Falha — sem janela disponível** (`walls2d#CA-06`): Dado um contexto sem área ou janela e duplicação impossível; Quando executo `caffmob.wall_editor`; Então aparece o erro "O Editor de Paredes precisa de uma janela do Blender aberta." e a sessão é encerrada.
- 🟢 **Regra — um editor por vez** (RN-27): com o Blender em segundo plano ou com uma sessão já ativa, o operador não fica disponível.

## US-AMB-02 — Ajustar medidas, vértices e tipo de parede

🟡 **Como** projetista (P1), **quero** clicar numa face ou num vértice e corrigir comprimento, espessura, ângulo e tipo (Normal, Divisória, Mureta), **para** acertar a planta com as medidas reais sem redesenhar.

Referências: `walls2d/requirements.md#RF-01`, `#RF-03`, `#RF-05`, `#RF-06`.

- 🟢 **Feliz — medida na face selecionada** (`walls2d#CA-07`, RN-05): Dado a face externa de um trecho selecionada e o projeto em mm; Quando digito "2*1500" e Enter; Então a face externa passa a medir 3000 mm (ajuste iterativo por causa da esquadria) e um passo de desfazer é gravado; na face interna o nó final anda na direção do trecho.
- 🟢 **Feliz — campo com unidade** (`walls2d#CA-13`, RN-28): Dado o painel do trecho; Quando escrevo "2,5 m" no comprimento com o projeto em mm; Então o trecho passa a 2,5 m e o painel mostra "2500 mm"; sem sufixo vale a unidade do projeto.
- 🟢 **Falha — fora do limite** (`walls2d#CA-02`, RN-02): Quando gravo comprimento fora de 0,01–100 m (ou espessura fora de 0,01–2 m); Então aparece "Valor Inválido: {campo} deve estar entre {lo} e {hi} (recebido: {v})" e o rascunho não muda.
- 🟢 **Falha — remover vértice da única parede** (`walls2d#CA-04`, RN-08): Dado uma cadeia com um só trecho; Quando removo um vértice; Então aparece "Uma cadeia precisa de pelo menos um trecho." e a cadeia continua intacta.

## US-AMB-03 — Navegar na planta com mouse e touchpad

🟡 **Como** projetista (P1) trabalhando num notebook, **quero** dar zoom e mover a planta pela roda, pela pinça e pelo arraste do touchpad, **para** editar detalhes sem perder o que estou digitando.

Referências: `walls2d/requirements.md#RF-10`, `#RF-11`; `canvas2d/requirements.md#RF-02`, `#RF-03`.

- 🟢 **Feliz — pinça durante a digitação** (`walls2d#CA-20`, RN-24): Dado uma medida sendo digitada; Quando faço pinça no touchpad; Então o zoom é ancorado no cursor, a digitação continua e nenhum passo de desfazer é criado.
- 🟢 **Feliz — zoom janela** (`walls2d#CA-22`, RN-25): Dado a lupa armada na barra superior; Quando arrasto um retângulo ≥ 5 px por lado; Então a vista enquadra o retângulo.
- 🟢 **Falha — retângulo curto ou cancelado** (`walls2d#CA-23`; `canvas2d#CA-06`): Quando o retângulo tem menos de 5 px ou aperto Esc; Então a vista não muda e Esc cancela só o modo lupa.
- 🟢 **Regra — roda invertida** (`walls2d#CA-21`): o sentido da roda segue `PreferencesInput.invert_zoom_wheel`.

## US-AMB-04 — Confirmar ou descartar o rascunho das paredes

🟡 **Como** projetista (P1), **quero** que nada mude no 3D até eu confirmar, e ser avisado do que vai quebrar, **para** experimentar a planta sem estragar o projeto.

Referências: `walls2d/requirements.md#RF-07`, `#RF-08`, `#RF-09`, `#RF-12`.

- 🟢 **Feliz — OK aplica** (`walls2d#CA-18`): Dado um rascunho com um trecho novo, um alterado e um removido; Quando o OK é aceito; Então o relatório diz 1 nova, 1 atualizada, 1 removida e esquadrias, piso/teto e portas/janelas reais são refeitos.
- 🟢 **Feliz — desfazer no rascunho** (`walls2d#CA-15`, RN-26): Ctrl+Z / Ctrl+Shift+Z agem no rascunho (até 100 passos), sem chegar ao desfazer do Blender.
- 🟢 **Falha — OK com avisos** (`walls2d#CA-17`): Dado um trecho encurtado de modo que um módulo passa do fim; Quando clico OK pela primeira vez; Então o painel lista "{módulo} não cabe em {parede}" e nada é aplicado; o 2º OK aplica.
- 🟢 **Falha — cancelar sujo** (`walls2d#CA-19`): Dado um rascunho alterado; Quando clico Cancelar ou Esc; Então é pedida a confirmação "Descartar as alterações e fechar o editor?".
- 🟢 **Regra — pé-direito** (`walls2d#CA-24`, RN-22): "Igualar ao pé-direito do projeto" (ligado por padrão) grava a altura do projeto no OK, exceto em Mureta e meia-parede/parede falsa do legado.

## US-AMB-05 — Marcar uma região na parede e inserir porta ou janela nela

🟡 **Como** projetista (P1), **quero** marcar na parede o retângulo do vão e escolher a porta ou janela, **para** que a esquadria entre com as medidas exatas da obra.

Referências: `openings/requirements.md#RF-10`, `#RF-11`.

- 🟢 **Feliz — marcar** (`openings#CA-11`): Dado uma parede 4,00 × 2,70 × 0,15; Quando executo `caffmob.wall_region` e clico os dois cantos; Então a região fica ativa, arredondada à grade de 10 mm (Shift: 1 mm), com o aviso "Região marcada: L × A. Escolha a porta ou a janela".
- 🟢 **Feliz — encaixe** (`openings#CA-13`): Quando a porta entra na região; Então ela vai do piso (peitoril 0) com a largura e a altura da região; a janela respeita o peitoril marcado.
- 🟢 **Falha — encaixe recusado** (`openings#CA-14`): Quando a região é um clique só, passa da ponta, tem z negativo, sobe além do pé-direito ou cruza outra abertura em mais de 1 mm; Então `fit` devolve `EMPTY`/`OUTSIDE`/`TOO_TALL`/`OVERLAP` e o aviso "<motivo>: a inserção segue presa ao cursor".
- 🟢 **Falha — cancelar/limpar** (`openings#CA-12`): Esc ou botão direito cancelam sem região; "Limpar região" ou abrir outro arquivo desativam a região.

## US-AMB-06 — Ver portas e janelas reais e inverter a mão da porta

🟡 **Como** projetista (P1), **quero** que portas e janelas apareçam como peças reais (batente, folha, maçaneta, vidro) e que eu inverta a mão com uma tecla, **para** apresentar o ambiente sem perder o furo na parede.

Referências: `openings/requirements.md#RF-01` a `#RF-09`.

- 🟢 **Feliz — porta real montada** (`openings#CA-04`): a caixa da parede vira referência em arame (sem o texto "DOOR"/"WINDOW") e a porta é montada em poucas malhas com materiais compartilhados.
- 🟢 **Feliz — tecla I** (`openings#CA-09`): Dado a maçaneta de uma porta real selecionada; Quando aperto I; Então a dobradiça troca de lado, o lado de abertura é mantido e aparece "Giro da porta invertido".
- 🟢 **Falha — tecla I sem porta** (`openings#CA-10`): Dado um balcão ou um vão aberto; Quando aperto I; Então o atalho do Blender segue normalmente.
- 🟢 **Falha proposital — sem mudança não refaz** (`openings#CA-06`): sem mudança de assinatura a montagem não é refeita (preserva abertura e produção).

## US-AMB-07 — Mover um módulo sobre outro e alinhar

🟡 **Como** projetista (P1), **quero** arrastar um módulo A sobre uma referência B com o botão direito e alinhar por lados, frente, altura ou empilhar, **para** compor o ambiente como no Promob.

Referências: `move_over/requirements.md#RF-01` a `#RF-07`; `selection/requirements.md#RF-02`.

- 🟢 **Feliz — arraste abre a janela** (`move_over#CA-02`): Dado o modo ligado; Quando arrasto ≥ 5 px de uma porta de A até B; Então a janela abre com A = raiz de A e B = raiz de B, com a linha tracejada "A → B" durante o arraste.
- 🟢 **Feliz — confirmar** (`move_over#CA-09`): Enter grava num único passo de desfazer; com sobreposição e colisão global ligada, pede "Confirme de novo para gravar mesmo assim".
- 🟢 **Falha — arraste sem efeito** (`move_over#CA-03`): clique no vazio, soltar sobre A ou mover menos de 5 px não abre nada e não abre o menu de contexto; com o modo desligado vale o menu do Blender.
- 🟢 **Falha — valor inválido** (`move_over#CA-07`): Passo "0" ou "-5" mostra a mensagem de `units.parse_length` e não muda.
- 🟢 **Cancelar** (`move_over#CA-10`): Esc, botão direito ou Cancelar devolvem pai, matriz e posição originais.

## US-AMB-08 — Deslizar um módulo na parede e escolher o plano de inserção

🟡 **Como** projetista (P1), **quero** deslizar um módulo ao longo da parede parando no vizinho, **para** encostar módulos sem sobrepor.

Referências: `move_over/requirements.md#RF-10`, `#RF-11`; `measure/requirements.md#RF-05`.

- 🟢 **Feliz** (`move_over#CA-13`): Dado "Evitar Sobreposição" ligado e um vizinho à direita; Quando arrasto além dele; Então o módulo para encostado e o afastamento da parede não muda; Esc devolve a posição.
- 🟢 **Falha** (`move_over#CA-13`): se o raio do mouse não corta o plano da frente da parede, o operador avisa e devolve `CANCELLED`.
- 🟢 **Plano de inserção** (`move_over#CA-14`): "Usar como plano de inserção" + clique numa face ativa o plano daquela face; "Limpar" volta ao piso.
- 🟢 **Falha — plano sem face** (`move_over#CA-14`): clicar fora de qualquer face avisa "Nenhuma face sob o cursor" e cancela.

## US-AMB-09 — Ler e digitar as cotas de um módulo na parede

🟡 **Como** projetista (P1), **quero** ver e digitar afastamento, anterior, posterior, inferior e superior, **para** posicionar o módulo por medida, sem mudar o tamanho dele.

Referências: `measure/requirements.md#RF-01` a `#RF-04`, `#RF-07`.

- 🟢 **Feliz** (`measure#CA-02`): Dado um balcão de 0,6 m; Quando aplico anterior = 0,075; Então x0 = 0,875, a largura continua 0,6 e o recálculo devolve 0,075.
- 🟢 **Feliz — a partir de uma porta** (`measure#CA-09`): as cotas aparecem com qualquer peça ou frente do módulo selecionada.
- 🟢 **Falha** (`measure#CA-04`): cota negativa, que tira o módulo da parede ou maior que o espaço até o piso gera "Valor Inválido…" e a posição não é gravada.
- 🟢 **Módulo livre** (`measure#CA-05`): fora da parede só as cotas verticais valem; as demais são rejeitadas.

## US-AMB-10 — Selecionar o componente inteiro (e a peça quando preciso)

🟡 **Como** projetista (P1), **quero** que um clique numa maçaneta selecione o módulo/vão inteiro e Alt + clique pegue só a peça, **para** não desmontar um módulo sem querer.

Referências: `selection/requirements.md#RF-06`, `#RF-07`, `#RF-08`.

- 🟢 **Feliz** (`selection#CA-08`): Dado o interruptor "Seleção por componente" ligado; Quando clico na maçaneta de uma porta real; Então o vão fica selecionado e ativo.
- 🟢 **Feliz — Alt + clique** (`selection#CA-11`): Alt + clique e Alt + Shift + clique selecionam peças isoladas; um clique comum volta ao componente.
- 🟢 **Falha — normalizador inativo** (`selection#CA-09`): com o interruptor desligado, fora do modo objeto ou com modal rodando, o clique é o do Blender.

## US-AMB-11 — Redimensionar e apagar um componente

🟡 **Como** projetista (P1), **quero** mudar a largura pelo botão direito (Redimensionar) e apagar com X/Delete escolhendo o destino dos agregados, **para** ajustar o ambiente rapidamente.

Referências: `selection/requirements.md#RF-05`, `#RF-11`, `#RF-12`; `aggregates/requirements.md#RF-16`.

- 🟢 **Feliz — redimensionar** (`selection#CA-16`): Dado um balcão de 0,60 m com agregado frontal e lateral; Quando redimensiono para 0,90; Então o agregado frontal estica ×1,5 e o lateral só é reposicionado.
- 🟢 **Falha — redimensionar** (`selection#CA-17`): piso, parede BTM, ou largura fora de 0,01–100 m geram "Valor Inválido…" e nada muda.
- 🟢 **Feliz — apagar** (`aggregates#CA-23`; `selection#CA-06`): Dado um balcão com uma fruteira agregada; Quando aperto X; Então abre "O objeto tem agregados" com a opção ligada; confirmando, tudo sai em lote; desligando, a fruteira é desconvertida e fica.
- 🟢 **Falha — X sem componente** (`aggregates#CA-24`): sem nada da unit selecionado o atalho segue o padrão do Blender.

## US-AMB-12 — Grudar itens em paredes e painéis

🟡 **Como** projetista (P1), **quero** grudar um nicho ou painel numa face plana e que ele acompanhe o hospedeiro quando este muda de medida, **para** não reposicionar à mão depois de cada ajuste.

Referências: `stick/requirements.md#RF-02` a `#RF-08`, `#RF-11` a `#RF-14`.

- 🟢 **Feliz** (`stick#CA-04`): Dado um painel de 18 mm e um nicho solto; Quando gruda na face +X; Então o nicho vira filho do painel, distância 0 e o rótulo da face cita "Painel".
- 🟢 **Feliz — acompanha** (`stick#CA-08`): quando a espessura do hospedeiro muda, o item continua encostado na face.
- 🟢 **Falha** (`stick#CA-05`): face não plana, o próprio item, um filho dele ou item agregado geram aviso com o motivo e `CANCELLED`; nada muda.
- 🟢 **Falha — sem face** (`stick#CA-06`): clique onde o raio não acerta nada avisa "Nenhuma face sob o cursor" e o comando continua esperando.
- 🟢 **Falha — fora da face** (`stick#CA-12`): se o hospedeiro encolhe e o item sai da face, ele não se move e a barra mostra "Item fora da face: Livre".
- 🟢 **Desgrudar** (`stick#CA-15`): o item fica na posição atual, sem vínculo.

## US-AMB-13 — Verificar colisões no ambiente

🟡 **Como** marceneiro (P2), **quero** verificar se módulos entram na parede, no teto ou em outro módulo, **para** não mandar para produção um projeto que não monta.

Referências: `collision/requirements.md#RF-01`, `#RF-04` a `#RF-07`, `#RF-09`, `#RF-11`.

- 🟢 **Feliz** (`collision#CA-01`): Dado um balcão 20 mm dentro de uma parede; Quando executo a verificação em `ALL`; Então a lista mostra (WALL, "Balcao", "Parede", 0,02 m) e o aviso "1 colisão(ões) em M item(ns)".
- 🟢 **Feliz — ao soltar** (`collision#CA-15`): ao fim do assentar do grudar, "Balcao colide com Vizinho" aparece na barra e o item fica onde foi solto.
- 🟢 **Falha — desatualizado** (`collision#CA-13`): ao mover um item verificado, o painel mostra "Desatualizado, verifique de novo".
- 🟢 **Falha — erro nunca vira "sem colisões"** (`collision#CA-10`).
- 🟢 **Regra — encostar não é colisão** (`collision#CA-04`).

## US-AMB-14 — Criar placas e caixas livres

🟡 **Como** projetista (P1), **quero** desenhar uma placa ou caixa por cliques e medidas digitadas e marcá-la como peça de fabricação, **para** resolver tampos, prateleiras soltas e acabamentos fora dos módulos.

Referências: `geometry_free/requirements.md#RF-01` a `#RF-08`.

- 🟢 **Feliz** (`geometry_free#CA-01`): Dado a vista 3D em modo objeto; Quando aciono "Placa" e clico dois cantos no piso; Então surge a malha "Placa" com largura 0,6, profundidade 0,4 e espessura 0,018, selecionada e ativa.
- 🟢 **Falha — medida inválida** (`geometry_free#CA-05`): "0" ou "1,2,3" mostram "Valor Inválido…" e o passo não muda.
- 🟢 **Falha — cancelar** (`geometry_free#CA-07`): Esc ou botão direito removem objeto e malha.
- 🟢 **Fabricação** (`geometry_free#CA-10`, `#CA-11`): placa gera 1 chapa e caixa gera 6.

## US-AMB-15 — Abrir portas e gavetas para apresentar e conferir

🟡 **Como** projetista (P1), **quero** abrir as frentes por clique, em massa ou por um controle 3D, e salvar o arquivo com elas fechadas, **para** mostrar o interior ao cliente sem bagunçar o projeto.

Referências: `inspection/requirements.md#RF-01` a `#RF-05`, `#RF-08`, `#RF-09`.

- 🟢 **Feliz — abrir tudo** (`inspection#CA-03`): Quando `caffmob.fronts_set_open(scope='ALL', mode='OPEN_90')`; Então portas leem 90° e gavetas abrem nas seis famílias, sem marcar o plano de corte como desatualizado.
- 🟢 **Feliz — clique anima** (`inspection#CA-05`): no modo de inspeção, um clique no puxador anima 0,35 s até o ângulo escolhido.
- 🟢 **Falha — clique fora de frente** (`inspection#CA-06`): vazio, parede ou HUD deixam o evento passar e nada abre.
- 🟢 **Salvar fechado** (`inspection#CA-10`): o `.blend` é gravado com frentes fechadas e a tela volta a mostrar as abertas.
- 🟢 **Porta de ambiente** (`inspection#CA-16`): a primeira abertura cria a folha 3D da porta de ambiente sem porta real.

## US-AMB-16 — Detectar interferência na abertura das frentes

🟡 **Como** marceneiro (P2), **quero** saber se uma porta bate em algo ao abrir, **para** corrigir antes de montar na obra.

Referências: `inspection/requirements.md#RF-06`, `#RF-07`.

- 🟢 **Feliz** (`inspection#CA-12`): Dado um cubo no arco de abertura da porta de "Balcao"; Quando verifico; Então a lista traz (Balcao, Obstaculo), as frentes voltam fechadas e aparece "N interferência(s) em M frente(s) verificada(s)".
- 🟢 **Falha** (`inspection#CA-13`): escopo sem frentes gera "Nenhuma frente foi verificada: não há portas ou gavetas no escopo.".
- 🟢 **Ir até** (`inspection#CA-14`, `#CA-15`): "Ir até" enquadra a interferência; índice inválido é recusado.

---

## Lacunas (🔴 relevantes das units)

| Unit | Caso | Lacuna | Fonte |
|---|---|---|---|
| geral | — | 🔴 Nenhuma das histórias acima foi validada visualmente no Blender nesta extração; parte dos CA tem só fumaça ou teste puro | requirements de cada unit |
| `canvas2d` | EC-07 | 🔴 Fechar editor em janela duplicada quando só resta uma janela: a área continua Image Editor | `canvas2d/edge-cases.md` |
| `canvas2d` | EC-08 | 🔴 Fallback na própria área religa menus/cabeçalho que já estavam ocultos | `canvas2d/edge-cases.md` |
| `walls2d` | EC-01 | 🔴 Remover Vértice entre paredes existentes não põe o `source` em `removed_sources`: a parede antiga não é removida no OK | `walls2d/edge-cases.md` |
| `walls2d` | EC-03 | 🔴 Responder "Não" ao fechar por arraste: o OK fecha a cadeia mesmo assim (`close_if_touching`) | `walls2d/edge-cases.md` |
| `walls2d` | EC-05 | 🔴 Soltar o botão sobre a barra superior durante um arraste: a barra consome o evento | `walls2d/edge-cases.md` |
| `walls2d` | EC-14 | 🔴 Várias salas fechadas: pisos/tetos emparelhados por nome, sem associação geométrica | `walls2d/edge-cases.md` |
| `openings` | EC-02 | 🔴 Cota/texto 2D filho antes do símbolo de giro quebra a leitura de `Is Left` | `openings/edge-cases.md` |
| `openings` | EC-04 | 🔴 "Toggle Double Door" numa porta real não chama `sync` | `openings/edge-cases.md` |
| `openings` | EC-07 | 🔴 Região marcada na face de fundo: a caixa é posta com rotação zero, do lado errado | `openings/edge-cases.md` |
| `openings` | EC-10 | 🔴 Parede da região apagada/renomeada: o desenho `POST_PIXEL` grava propriedade | `openings/edge-cases.md` |
| `move_over` | EC-10 | 🔴 Modal de Mover na Parede / plano de inserção interrompido pelo Blender não restaura a posição (sem `cancel()`) | `move_over/edge-cases.md` |
| `move_over` | EC-15 | 🔴 Frentes que saem do `bound_box` da raiz não contam no alinhamento nem na sobreposição | `move_over/edge-cases.md` |
| `measure` | EC-01 | 🔴 Cota anterior/posterior grande atravessa o vizinho do outro lado (só a parede é checada) | `measure/edge-cases.md` |
| `measure` | EC-03 | 🔴 Vizinho sem `mod_name` (módulo rápido, importado) vira um ponto no cálculo dos limites | `measure/edge-cases.md` |
| `selection` | EC-07 | 🔴 Delete de parede com balcão que tem agregado: a pergunta não aparece | `selection/edge-cases.md` |
| `selection` | EC-08 | 🔴 Largura/altura de porta pelo painel não refaz a porta real | `selection/edge-cases.md` |
| `stick` | EC-18 | 🔴 "Grudar" aceita parede, piso, teto, cota ou objeto não-item como item | `stick/edge-cases.md` |
| `collision` | EC-15 | 🔴 Grupos soltos (SketchUp, biblioteca de objetos) e malhas filhas ficam fora da verificação | `collision/edge-cases.md` |
| `geometry_free` | EC-01 | 🔴 Modal interrompido de fora deixa o objeto provisório na cena (sem `cancel()`) | `geometry_free/edge-cases.md` |
| `geometry_free` | EC-06 | 🔴 Arrastar para −X/−Y e digitar as medidas: posição só se corrige no próximo movimento | `geometry_free/edge-cases.md` |
| `geometry_free` | EC-09 | 🔴 Duplicar/espelhar geometria com pai usa coordenada de mundo como local | `geometry_free/edge-cases.md` |
| `geometry_free` | EC-14 | 🔴 Excluir geometria com filhos deixa os filhos soltos | `geometry_free/edge-cases.md` |
| `inspection` | EC-01 | 🔴 Folha convertida de correr mostra a seta de gaveta no gizmo | `inspection/edge-cases.md` |
| `inspection` | EC-04 | 🔴 Desativar a extensão com a inspeção rodando deixa timers e handler do modal | `inspection/edge-cases.md` |
| `inspection` | EC-16 | 🔴 Ctrl+Z depois da primeira abertura de porta de ambiente: pivô e folha podem sumir ou não | `inspection/edge-cases.md` |
| `inspection` | EC-17 | 🔴 O overlay 3D não restaura o depth test ao fim do desenho | `inspection/edge-cases.md` |
