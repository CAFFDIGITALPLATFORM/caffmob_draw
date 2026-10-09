# Requirements: Seleção por componente e porta e janela na região selecionada

> Identificador: `011-selecao-por-componente`
> Data: `2026-10-09`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

Para o projetista que monta o ambiente, a feature tem duas partes:
- **Seleção por componente.** Cada porta, janela, item importado (SketchUp, OBJ) ou da biblioteca passa a se comportar
  como um componente único:
  - clicar numa peça dele seleciona o componente inteiro (a raiz);
  - mover, girar ou excluir afeta o componente inteiro.

  Hoje, ao clicar na maçaneta, só a maçaneta é selecionada, e excluir uma porta deixa folha e ferragens soltas na cena.
  Um interruptor **Seleção por componente** na viewport liga e desliga o comportamento. Ele vem ligado.
- **Porta e janela na região selecionada.** Se o projetista marca uma região na parede (um retângulo de dois cliques)
  antes de inserir a porta ou a janela, ela entra com a largura e a altura exatas da região, sem nenhum milímetro a
  mais.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#3` | Modelo de entidades: parede, abertura (vão `GeoNodeCage`) presa à parede, módulos com peças filhas | 🟢 |
| `_reversa_sdd/domain.md#2.2` (R-04 a R-08) | A abertura se prende ao segmento de parede, herda rotação e espessura; a porta tem peitoril fixo em 0 | 🟢 |
| `_reversa_sdd/hb_placement/requirements.md` | Inserção de aberturas: posição na parede, vão livre, digitação de medidas (W, H, ←/→) | 🟢 |
| `_reversa_forward/010-porta-real-textura-linha/requirements.md#RN-01, RN-10` | Porta e janela reais: vão (`GeoNodeCage`, raiz) → grupo FRAME → grupos LEAF → peças e ferragens | 🟢 |
| `_reversa_forward/009-mira-calculo-skp-biblioteca/requirements.md#RN-10 a RN-14` | Itens da biblioteca e SketchUp importado viram grupos (`btm_group`) com hierarquia; o item da biblioteca tem raiz marcada (`btm_object_item`); RN-12 retexturiza uma parte do item | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RF-11, RN-11` | Importar OBJ/FBX/glTF cria malhas soltas, sem raiz; agrupar é um passo manual (`caffmob.group_create`, `caffmob.window_assemble`) | 🟢 |
| `caffmob_draw/operators/doors_windows.py#delete_door_window` (l. 1317-1350) | Excluir porta ou janela remove só os filhos diretos do vão: folhas, ferragens e peças do OBJ instalado ficam na cena (defeito) | 🟢 |
| `caffmob_draw/aggregates/ops_aggregate.py#delete_with_aggregates` (l. 202-238, 285-293) | Único operador preso a X/Delete; só age quando o objeto tem agregados ou itens grudados; não remove os demais descendentes | 🟢 |
| `caffmob_draw/selection/classify.py` (`classify`, `module_root`, `free_group`, `movable_root`) | Já existe a resolução da raiz de porta, janela, módulo e grupo livre, usada pela seção Selecionado | 🟢 |
| `caffmob_draw/ui/sidebar_selection.py` (l. 14-49) | A troca do objeto ativo já é observada (abre a seção Selecionado), mas não altera a seleção | 🟢 |
| `caffmob_draw/operators/doors_windows.py#_PlaceWallObjectBase` (l. 694-1055); `operators/walls.py#draw_wall_cutter` (l. 5516-5700) | Inserção da porta: arraste na parede, Enter só confirma o valor digitado, clique coloca; modo D de largura por dois pontos. O recorte de parede já desenha um retângulo na parede com dois cliques | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Mexer num objeto como um todo | Clica na maçaneta de uma porta, e a porta inteira fica selecionada; tecla X e a porta some com folha, batente e ferragens |
| Projetista que traz modelos de fora | Usar um SketchUp ou OBJ como um bloco | Importa uma cadeira em OBJ, clica num pé, arrasta e a cadeira inteira se move |
| Projetista que precisa editar uma peça | Trocar o material de uma só parte | Desliga "Seleção por componente", clica na almofada da porta e troca o material só dela |
| Projetista que já sabe o vão | Encaixar a porta num vão definido | Marca na parede a região do vão (por exemplo, 82 × 212 cm), escolhe a porta, tecla Enter e a porta entra com 82 × 212 cm exatos |

## 4. Regras de negócio novas ou alteradas

### Componente

1. **RN-01, o que é componente.** Componente é um objeto raiz com todos os seus descendentes. São raízes:
   - o vão de porta ou janela da parede (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`);
   - o grupo mais alto de um item importado do SketchUp (`btm_group`);
   - a raiz de um item da biblioteca (`btm_object_item`);
   - o grupo de um OBJ/FBX/glTF importado (RN-02).

   Peça solta, sem pai, é um componente de um objeto só. 🟢
   - Origem: `caffmob_draw/selection/classify.py`; 009 RN-10 a RN-14; 010 RN-01
   - Tipo: nova
2. **RN-02, importar já agrupa.** Importar um OBJ, FBX ou glTF com mais de uma malha agrupa as malhas num grupo
   (PLAIN), que vira a raiz do componente. Hoje elas entram soltas e agrupar é manual. Os comandos "Agrupar" e
   "Montar janela" continuam disponíveis sobre o grupo. 🟡
   - Origem: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#RF-11`; `aggregates/ops_import.py`
   - Tipo: alterada
3. **RN-03, agregados e itens grudados.** Um agregado (003) ou um item grudado (004) num móvel é um componente
   próprio: clicar nele seleciona o agregado, não o móvel hospedeiro. Excluir o móvel segue a pergunta de hoje
   ("levar os agregados junto?") e solta os itens grudados no lugar. 🟡
   - Origem: `aggregates/ops_aggregate.py#delete_with_aggregates`
   - Tipo: nova (preserva o comportamento atual)
4. **RN-04, armários no modo gabinete.** Os módulos (armários com corpo, portas e gavetas) entram na seleção por
   componente **só quando o modo de seleção é gabinete**: clicar em qualquer peça do armário seleciona o armário
   inteiro (a raiz do módulo, `classify.module_root`). Nos modos abertura e peça, a seleção continua como hoje. 🟢
   (Esclarecimentos 2026-10-09, Q1)
   - Origem: `caffmob_draw/selection/classify.py#MODULE_TAGS`; modos de seleção do frameless, face frame e closets
   - Tipo: alterada

### Seleção por componente

5. **RN-05, clicar seleciona a raiz.** Com a seleção por componente ligada, selecionar qualquer peça de um
   componente seleciona a raiz no lugar dela, e ela vira o objeto ativo. Isso vale para o clique, a seleção por
   caixa e a seleção pela lista de objetos. Selecionar peças de dois componentes seleciona as duas raízes. 🟡
   - Tipo: nova
6. **RN-06, Alt + clique seleciona a peça.** Com a seleção por componente ligada, **Alt + clique** seleciona só a peça
   clicada, sem subir para a raiz e sem desligar o interruptor. Assim o projetista abre a folha pela alça ou troca o
   material de uma parte (009 RN-12). Alt + Shift + clique soma a peça à seleção. O clique sem Alt volta a
   selecionar o componente. 🟢 (Esclarecimentos 2026-10-09, Q2)
   - Atenção para o plano: no Blender, Alt + clique na vista 3D já tem uso próprio (lista os objetos sob o cursor);
     o atalho da extensão passa na frente dele só com o interruptor ligado. 🟡
   - Tipo: nova
7. **RN-07, mover e girar o todo.** Mover, girar e o "Mover sobre" (002) agem na raiz e levam o componente inteiro.
   A porta e a janela continuam presas à parede (R-04 a R-07). 🟢
   - Origem: `_reversa_sdd/domain.md#2.2`
   - Tipo: alterada
8. **RN-08, excluir leva tudo.** Excluir a raiz (X, Delete ou menu) remove a raiz e **todos** os descendentes, em
   qualquer profundidade, e desfaz os efeitos dela:
   - a porta e a janela tiram o furo da parede;
   - o agregado tira o próprio recorte.

   Um único Ctrl+Z traz o componente inteiro de volta. Isso vale mesmo com a seleção por componente desligada,
   quando a raiz é excluída. 🟢
   - Origem: `operators/doors_windows.py#delete_door_window` (hoje só os filhos diretos)
   - Tipo: alterada (corrige o defeito de peças que ficam soltas)
9. **RN-09, interruptor.** "Seleção por componente" (en-US: "Component Selection") é um interruptor na viewport,
   ligado por padrão em arquivo novo e em arquivo antigo, e salvo no arquivo. Desligado, a seleção e a exclusão de
   uma peça voltam ao comportamento do Blender: só a peça. 🟡
   - Tipo: nova

### Porta e janela na região selecionada

10. **RN-10, região antes da abertura.** O projetista marca a região na parede **antes** de escolher a porta ou a
    janela: um retângulo desenhado na parede com dois cliques (cantos opostos), como o recorte de parede de hoje
    (`draw_wall_cutter`). A região fica visível na parede até virar abertura ou ser cancelada (Esc). 🟢
    (Esclarecimentos 2026-10-09, Q3 e Q4)
    - Origem: `caffmob_draw/operators/walls.py#draw_wall_cutter`
    - Tipo: nova
11. **RN-11, medida exata.** Com uma região marcada, escolher a porta ou a janela e teclar Enter (ou clicar) insere a
    abertura centrada na região, com largura e altura do vão **iguais** às da região, sem arredondar para a grade e
    sem folga somada. 🟡
    - A porta encosta no piso (peitoril 0, R-08); quando a região não começa no piso, ela vai do piso até a borda de
      cima da região.
    - A janela usa a borda de baixo da região como peitoril.
    - A abertura segue o lado da parede onde a região foi marcada.
    - Origem: `_reversa_sdd/domain.md#2.2` (R-08)
    - Tipo: nova
12. **RN-12, sem região.** Sem região marcada, a inserção da porta e da janela continua como hoje (arraste,
    W/H/←/→, modo D, clique coloca). Uma região que não cabe na parede (largura maior que o trecho livre, ou altura maior que a
    parede) é recusada com aviso, e a inserção segue no modo de hoje. 🟡
    - Origem: `_reversa_sdd/hb_placement/requirements.md`
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Clicar numa peça de porta, janela, SketchUp, OBJ importado ou item da biblioteca seleciona a raiz do componente (RN-01, RN-05) | Must | Clicar na maçaneta de uma porta deixa o vão selecionado e ativo, e nenhuma outra peça selecionada | 🟡 |
| RF-02 | Seleção por caixa e pela lista de objetos também sobe para a raiz, sem repetir raízes (RN-05) | Should | Uma caixa que pega 3 peças de uma janela e 1 de uma cadeira deixa 2 objetos selecionados: a janela e a cadeira | 🟡 |
| RF-03 | Excluir a raiz remove todos os descendentes em qualquer profundidade, e um Ctrl+Z traz tudo de volta (RN-08) | Must | Excluir uma porta real (010) deixa zero objetos dela na cena e a parede sem furo; Ctrl+Z traz a porta e o furo | 🟢 |
| RF-04 | Importar OBJ/FBX/glTF com várias malhas cria um grupo raiz (RN-02) | Must | Um OBJ com 5 malhas entra como 1 grupo com 5 peças; clicar numa peça seleciona o grupo | 🟡 |
| RF-05 | Mover, girar e "Mover sobre" levam o componente inteiro; porta e janela continuam presas à parede (RN-07) | Must | Arrastar uma cadeira importada clicando num pé move as 5 peças juntas; arrastar a porta pela maçaneta a desliza na parede | 🟢 |
| RF-06 | Agregados e itens grudados continuam componentes próprios; excluir o móvel mantém a pergunta de hoje (RN-03) | Must | Clicar num agregado seleciona o agregado; as fumaças da 003 e 004 continuam verdes | 🟡 |
| RF-07 | Interruptor "Seleção por componente" na viewport, ligado por padrão e salvo no arquivo (RN-09) | Must | Arquivo novo abre com o interruptor ligado; desligado, clicar na maçaneta seleciona só a maçaneta; salvar e reabrir mantém o estado | 🟡 |
| RF-08 | Alt + clique seleciona só a peça com o interruptor ligado; Alt + Shift + clique soma a peça (RN-06) | Must | Alt + clique na almofada da porta deixa só a almofada selecionada; trocar o material muda só ela | 🟢 |
| RF-12 | Armários entram na seleção por componente só no modo gabinete (RN-04) | Must | No modo gabinete, clicar numa porta do armário seleciona o armário; no modo peça, seleciona a porta | 🟢 |
| RF-09 | Porta ou janela inserida numa região marcada (retângulo de dois cliques na parede) entra com a largura e a altura exatas da região (RN-10, RN-11) | Must | Região de 820 × 2120 mm: o vão da porta tem 820 × 2120 mm (diferença 0 mm), centrado na região; região de 1200 × 1000 mm a 1100 mm do piso: janela de 1200 × 1000 com peitoril de 1100 | 🟢 |
| RF-10 | Sem região, ou com região que não cabe, a inserção é a de hoje, com aviso no segundo caso (RN-12) | Must | Região de 5 m num trecho de 3 m mostra o aviso e abre a inserção normal | 🟡 |
| RF-11 | Guia do usuário: seleção por componente, interruptor, Alt + clique, exclusão e porta e janela na região | Should | `docs/usuario/` atualizado | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Subir para a raiz não atrasa o clique perceptivelmente: até 2.000 objetos na cena e componentes com até 10 níveis de profundidade, resposta em menos de 50 ms | Cenas da 009/010 com SketchUp aninhado e portas reais | 🟡 |
| Compatibilidade | Clique de seleção, clique do HUD da viewport (`viewport_hud`), "Mover sobre" (botão direito) e a tecla I de inverter a porta continuam funcionando | `operators/viewport_hud.py` (l. 818-829); `move_over/ops_drag.py`; `openings/ops.py` | 🟢 |
| Compatibilidade | Arquivos antigos abrem sem erro; OBJ importados antes da feature (malhas soltas) continuam como estão, cada um como componente de um objeto só | RN-01, RN-02 | 🟡 |
| Desfazer | Seleção, exclusão e inserção na região entram no histórico do Ctrl+Z como uma única etapa cada | Convenção `UNDO` do `CLAUDE.md` | 🟢 |
| Design (/impeccable) | O interruptor mostra o estado escrito (ligado/desligado) e segue o padrão visual das seções da barra lateral da 008-010 | Padrão das features 008 a 010 | 🟢 |
| Internacionalização | Textos novos em pt-BR e en-US; `test_i18n_coverage` verde | `CLAUDE.md`; `tests/test_i18n_coverage.py` | 🟢 |
| Testes | Núcleos puros (resolver a raiz, juntar raízes sem repetir, medir a porta pela região) testados fora do Blender; fumaças de seleção, exclusão e porta na região | Padrão 004 a 010 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Clicar na maçaneta seleciona a porta
  Dado uma porta real numa parede e a seleção por componente ligada
  Quando o projetista clica na maçaneta
  Então o vão da porta fica selecionado e ativo
  E nenhuma outra peça da porta fica selecionada

Cenário: Seleção por caixa sem repetir raízes
  Dado uma janela real e uma cadeira importada com a seleção por componente ligada
  Quando o projetista arrasta uma caixa que pega 3 peças da janela e 1 pé da cadeira
  Então ficam selecionados 2 objetos: a janela e a cadeira

Cenário: Excluir a porta leva tudo
  Dado uma porta real numa parede de 150 mm
  Quando o projetista seleciona a porta e tecla X
  Então nenhuma peça da porta fica na cena
  E a parede fica sem o furo
  E um Ctrl+Z traz a porta inteira e o furo de volta

Cenário: Importar OBJ com várias malhas
  Dado um OBJ com 5 malhas
  Quando o projetista o importa
  Então ele entra como 1 grupo com 5 peças
  E arrastar um pé move as 5 peças juntas

Cenário: Agregado continua independente
  Dado um móvel com um agregado
  Quando o projetista clica no agregado
  Então o agregado fica selecionado, e não o móvel

Cenário: Alt + clique edita uma peça
  Dado uma porta real e a seleção por componente ligada
  Quando o projetista dá Alt + clique na almofada da porta
  Então só a almofada fica selecionada
  E um clique sem Alt na almofada volta a selecionar a porta inteira

Cenário: Armário no modo gabinete
  Dado um armário com porta e o modo de seleção gabinete
  Quando o projetista clica na porta do armário
  Então o armário inteiro fica selecionado
  E no modo peça o mesmo clique seleciona só a porta do armário

Cenário: Interruptor desligado
  Dado a seleção por componente desligada
  Quando o projetista clica na maçaneta
  Então só a maçaneta fica selecionada
  E salvar e reabrir o arquivo mantém o interruptor desligado

Cenário: Porta na região marcada
  Dado uma região de 820 × 2120 mm marcada numa parede a partir do piso
  Quando o projetista escolhe a porta simples e tecla Enter
  Então o vão da porta tem 820 × 2120 mm, centrado na região
  E o furo na parede tem 820 × 2120 mm

Cenário: Janela na região marcada
  Dado uma região de 1200 × 1000 mm marcada numa parede, com a borda de baixo a 1100 mm do piso
  Quando o projetista escolhe a janela e tecla Enter
  Então a janela tem 1200 × 1000 mm, centrada na região, com peitoril de 1100 mm

Cenário: Região que não cabe
  Dado uma região de 5.000 mm marcada num trecho livre de 3.000 mm
  Quando o projetista escolhe a porta simples
  Então aparece um aviso de que a região não cabe na parede
  E a inserção segue no modo de hoje, presa ao cursor

Cenário: Sem região marcada
  Dado nenhuma região marcada
  Quando o projetista escolhe a porta simples
  Então a inserção é a de hoje: arraste na parede, medidas digitadas e clique para colocar
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-03, RF-05, RF-07, RF-08, RF-12 | Must | Núcleo pedido: o componente é selecionado, movido e excluído como um todo, com interruptor e Alt + clique para a peça |
| RF-03 (exclusão em profundidade) | Must | Corrige um defeito atual: peças da porta e da janela ficam na cena |
| RF-04 | Must | Sem raiz, o OBJ importado não tem componente para selecionar |
| RF-06 | Must | Não pode quebrar agregados e itens grudados (003, 004) |
| RF-09, RF-10 | Must | Segunda parte pedida: porta e janela na medida exata da região |
| RF-02 | Should | Seleção por caixa é menos frequente que o clique |
| RF-11 | Should | Guia do usuário |
| RNF de desempenho | Should | Clique precisa continuar instantâneo |

## 9. Esclarecimentos

### Sessão 2026-10-09

- **Q:** A seleção por componente também vale para os armários (módulos), que já têm os modos de seleção gabinete,
  abertura e peça?
  **R:** Sim, só no modo gabinete. Nos modos abertura e peça, a seleção continua como hoje (RN-04, RF-12).
- **Q:** Com o interruptor ligado, como o projetista edita uma peça só?
  **R:** Alt + clique seleciona só a peça, sem desligar o interruptor (RN-06, RF-08).
- **Q:** O que é a "região selecionada" na parede antes de inserir a porta?
  **R:** Um retângulo desenhado na parede com dois cliques, como o recorte de parede atual (RN-10).
- **Q:** A inserção na região marcada vale também para a janela?
  **R:** Sim, para porta e janela; a janela usa a borda de baixo da região como peitoril (RN-10, RN-11, RF-09).

## 10. Lacunas

- 🟡 Onde fica o interruptor: a premissa é a barra lateral (bloco do topo, junto dos modos de seleção) e o HUD da
  viewport quando ligado (RN-09).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-09 | `/reversa-clarify`: armários no modo gabinete, Alt + clique, região de dois cliques, janela na região | reversa |
