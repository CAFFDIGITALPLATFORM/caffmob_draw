# Requirements: Seletor de objetos sobrepostos da viewport 3D

> Identificador: `016-seletor-sobreposicao`
> Data: `2026-11-18`
> Pasta da extração reversa: `_reversa_sdd/`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O projetista que monta o ambiente perde tempo quando vários objetos ficam empilhados no mesmo ponto da viewport: o
clique pega sempre o primeiro do Blender e os de trás só aparecem girando a câmera. A feature traz para dentro da
extensão o seletor de sobreposição do pacote anexado (`overlap_selector.py` e `README.md`): um atalho abre, sobre o
cursor, a lista dos objetos atingidos pelo raio, com pré-visualização, marcação item a item, isolar e confirmar ou
cancelar. A seleção preparada só é aplicada no fim; cancelar devolve a seleção anterior intacta.

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` | Camadas da extensão: Interação (`ui`, `library_panel`, `canvas2d`), Posicionamento (`selection`, `measure`, `move_over`, `stick`), e a extensão roda no processo do Blender, sem serviço externo | 🟢 |
| `_reversa_sdd/inventory.md#overlays` | `overlays/` é a camada de desenho em viewport por GPU (`draw_handlers.py`); é onde vivem os desenhos sobre a vista 3D | 🟢 |
| `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-09) | Alt + clique seleciona só a peça e a marca isenta; Alt + Shift soma à seleção; sem modificador o clique limpa as isenções | 🟢 |
| `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-07) | O normalizador da seleção não age com o interruptor desligado, fora do modo objeto ou com modal da extensão rodando | 🟢 |
| `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-04) | Raiz do componente: vão, cota solta, grudado ou agregado, módulo no modo gabinete, item da biblioteca, grupo mais alto, senão o próprio objeto | 🟢 |
| `caffmob_draw/selection/component_pick.py#register` | O keymap de Alt + clique e Alt + Shift + clique já ocupa `LEFTMOUSE`/`CLICK` com `head=True` no mapa `3D View`, com poll por `scene.btm_component_select` | 🟢 |
| `caffmob_draw/__init__.py#_submodule_names, register, unregister` | Contrato de módulo: `classes`, `register()`, `unregister()`, entrada na lista de hot-reload e nas cascatas de registro e remoção | 🟢 |
| Sonda no Blender 5.2 (2026-11-19) | O `view3d.select` ocupa os oito combos de `LEFTMOUSE` no mapa `3D View`; `ray_cast` por objeto devolve falso em curva e em texto; malha com instâncias de Geometry Nodes fica com zero faces na geometria avaliada | 🟢 |
| `_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md` | Curva, texto, vazio e malha vazia ficam fora da planta baixa sem derrubar o desenho; só malha entra | 🟢 |
| `_reversa_sdd/architecture.md#4. Dívidas Técnicas e Lacunas Identificadas` (D-02) | Consulta de geometria por raio na viewport a cada movimento do mouse é dívida conhecida de desempenho em cenas grandes | 🟢 |
| `_reversa_sdd/selection/requirements.md#Regras de Negócio` | Seleção por componente é interruptor por cena, ligado por padrão e salvo no arquivo | 🟢 |
| `caffmob_draw/operators/viewport_hud.py#BTM_OT_active_component_select` (l. 459-471) | Já existe um interruptor na viewport que liga e desliga `Scene.btm_component_select` | 🟢 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Escolher a peça certa quando várias estão empilhadas | Três módulos ocupam o mesmo canto; ele abre a lista sob o cursor e escolhe o de trás sem girar a câmera |
| Projetista que importa modelos de fora | Encontrar o objeto escondido atrás do modelo importado | Um OBJ de decoração cobre a parede; ele percorre a lista e isola o item para conferir antes de selecionar |
| Projetista que trabalha em cena cheia | Não perder a seleção que já montou | Ele já tinha seis peças selecionadas, abre o seletor, marca mais duas e confirma; as seis continuam na seleção |
| Projetista que errou | Voltar atrás sem efeito colateral | Ele abre, mexe na lista e cancela com Esc; seleção, objeto ativo e visibilidade voltam ao que eram |

## 4. Regras de negócio novas ou alteradas

1. **RN-01, o que entra na lista.** Só objetos `MESH` do view layer ativo que estejam visíveis (`visible_get()`) e
   selecionáveis (`hide_select` falso). Curva, texto, vazio e malha sem vértices ficam fora sem levantar exceção, e
   objeto de biblioteca linkada só entra se for selecionável. O raio olha a malha avaliada do próprio objeto: as
   instâncias de Geometry Nodes, que não fazem parte dela, e a geometria de curva ou texto não entram nesta versão
   (Esclarecimentos 2026-11-19, Q2). 🟢
   - Origem no legado: `_reversa_sdd/addenda/bug-BUG-20261118-PLNT-v001.md` (mesmo cuidado com tipos que não são malha); sonda de 2026-11-19
   - Tipo: nova
2. **RN-02, ordem da lista.** Da frente para trás: a distância de cada objeto é a do primeiro impacto do raio da
   viewport naquele objeto, e cada objeto é testado individualmente, para que os de trás apareçam. 🟢
   - Origem no legado: `overlap_selector.py#_objects_under_cursor` (pacote anexado); `_reversa_sdd/architecture.md#4` (D-02)
   - Tipo: nova
3. **RN-03, inspeção não mexe na seleção.** A seleção viva e o objeto ativo originais ficam guardados na abertura. A
   seleção preparada é aplicada **só** no confirmar; cancelar restaura exatamente a seleção e o ativo anteriores. 🟢
   - Origem no legado: `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-07, RN-SELECTION-09)
   - Tipo: alterada (a versão anexada usa a seleção como pré-visualização; aqui isso não é permitido)
4. **RN-04, pré-visualização por destaque, não por seleção.** O objeto em foco recebe destaque no desenho da
   viewport e a seleção permanece intocada durante a inspeção. A razão é a seleção por componente: ela normaliza
   qualquer seleção para a raiz (RN-SELECTION-04) e reagiria a cada movimento do mouse (RN-SELECTION-07). 🟢
   - Origem no legado: `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-04, RN-SELECTION-07)
   - Tipo: alterada
5. **RN-05, isolar é reversível por `hide_set`.** Isolar esconde com `hide_set` todos os objetos do view layer, menos
   o objeto em foco, guardando o `hide_get()` de cada um na abertura; restaurar devolve exatamente esse estado em toda
   saída: restaurar, cancelar, confirmar, erro ou `unregister`. A Local View nativa fica de fora porque isola o que
   está selecionado e mexeria na seleção que deve permanecer intocada (RN-03, RN-04), além de reenquadrar a vista. 🟢
   - Origem no legado: `overlap_selector.py#_toggle_isolation` (pacote anexado); Esclarecimentos 2026-11-19, Q3
   - Tipo: nova
6. **RN-06, marcação item a item.** A lista mostra todos os achados; cada linha tem caixa de marcação e o item em
   foco fica realçado. Rolar a lista com a roda não muda a marcação nem a pré-visualização. 🟢
   - Origem no legado: `overlap_selector.py#_draw, modal` (pacote anexado)
   - Tipo: nova
7. **RN-07, teclado e mouse.** `Ctrl+A` marca todos, `Ctrl+/` inverte a marcação dos achados, `+` marca e `-`
   desmarca o item em foco, setas cima e baixo navegam, roda rola a lista, `I` alterna isolar, `Enter` confirma,
   `Esc` e botão direito cancelam. Clique na linha alterna a marcação; clique nos botões Selecionar Todos, Inverter e
   Isolar executa a ação correspondente. 🟢
   - Origem no legado: `overlap_selector.py#modal`; `README.md#3.2` (pacote anexado)
   - Tipo: nova
8. **RN-08, abertura e atalho.** A abertura acontece na `3D View`, só em Object Mode, por
   `Ctrl + Alt + botão esquerdo`, e a mesma ação aparece no menu de contexto da viewport
   (`caffmob_draw/ui/context_menu.py#draw_context_menu`), para quem não usa o atalho. O `Alt` e o `Alt + Shift`
   continuam com o `caffmob.component_pick`. Como o `view3d.select` do Blender já ocupa os oito combos de `LEFTMOUSE`,
   o item da extensão entra com `head=True` e, com ele, o `Ctrl + Alt + clique` deixa de executar a variante de
   seleção do Blender nessa vista (Esclarecimentos 2026-11-19, Q1). 🟢
   - Origem no legado: `caffmob_draw/selection/component_pick.py#register`; `_reversa_sdd/domain.md#Catálogo de regras extraídas` (RN-SELECTION-09); sonda de 2026-11-19
   - Tipo: nova
9. **RN-09, sem nada sob o cursor.** Sem objeto elegível sob o cursor, o seletor não abre, avisa em uma linha e a
   seleção não muda. 🟢
   - Origem no legado: `overlap_selector.py#invoke` (pacote anexado)
   - Tipo: nova
10. **RN-10, nada persiste.** A feature não cria passo de desfazer, não altera malha, material, camada nem
    visibilidade permanente, e não grava estado na cena. Abrir e cancelar deixam o arquivo idêntico. 🟢
    - Origem no legado: `README.md#1.4` (pacote anexado)
    - Tipo: nova
11. **RN-11, registro no addon.** O seletor vive em módulo próprio da extensão, com `classes`, `register()` e
    `unregister()`; entra na lista de hot-reload e nas cascatas de `caffmob_draw/__init__.py`; o keymap vai para o
    mapa `3D View` com `head=True` e é removido no `unregister`; o `draw_handler` é removido em todos os caminhos de
    saída e no `unregister`. 🟢
    - Origem no legado: `caffmob_draw/__init__.py#_submodule_names, register, unregister`; `caffmob_draw/selection/component_pick.py#register`
    - Tipo: nova
12. **RN-12, textos nas duas línguas.** Rótulos, avisos e legendas entram em `pt_BR` e `en_US` no arquivo de
    traduções do módulo, sem texto solto na interface. 🟢
    - Origem no legado: `_reversa_sdd/architecture.md#Re-extração 2026-10-10 — arquitetura atual` e a convenção de `data/translations/*.json`
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Detectar todos os objetos de malha elegíveis sob o cursor, inclusive os que estão atrás de outros | Must | Com três cubos alinhados no mesmo ponto do raio, a lista traz os três, na ordem de distância | 🟢 |
| RF-02 | Exibir a lista sobre a viewport, desenhada na própria vista, com cabeçalho, contagem, linhas e rodapé de atalhos | Must | Abrir com 5 objetos mostra 5 linhas, o total no cabeçalho e os atalhos no rodapé | 🟢 |
| RF-03 | Rolar a lista quando os achados passam de 12, sem perder a linha em foco | Must | Abrir com 20 objetos, rolar até a última linha e ver todas uma vez | 🟢 |
| RF-04 | Pré-visualizar o objeto em foco com destaque no desenho, sem alterar a seleção durante a inspeção | Must | Passar o mouse pelas linhas muda o destaque e a seleção continua a mesma até o desfim | 🟢 |
| RF-05 | Marcar e desmarcar objetos individualmente, por clique na linha e pelos atalhos `+` e `-` | Must | Clicar na linha 2 marca; clicar de novo desmarca; `+` marca o item em foco | 🟢 |
| RF-06 | Marcar todos com `Ctrl+A` e pelo botão Selecionar Todos | Must | Com 4 achados, `Ctrl+A` deixa as 4 linhas marcadas | 🟢 |
| RF-07 | Inverter a marcação com `Ctrl+/` e pelo botão Inverter | Must | Com 2 de 4 marcados, inverter deixa as outras 2 marcadas | 🟢 |
| RF-08 | Isolar temporariamente o objeto em foco e restaurar, por `I` ou botão | Must | Isolar mostra só o objeto em foco; restaurar devolve a visibilidade anterior dos demais | 🟢 |
| RF-09 | Navegar pela lista com as setas, mantendo o item em foco visível | Must | Seta para baixo 13 vezes, com 20 achados, mantém a linha em foco visível na lista rolada | 🟢 |
| RF-10 | Confirmar com `Enter`, aplicando a seleção preparada e deixando o item em foco como objeto ativo quando ele estiver marcado | Must | Confirmar com 2 de 3 marcados seleciona exatamente esses 2 e ativa o item em foco | 🟢 |
| RF-11 | Cancelar com `Esc` ou botão direito, devolvendo seleção, objeto ativo e visibilidade originais | Must | Antes e depois de cancelar, o conjunto de selecionados e o ativo são idênticos | 🟢 |
| RF-12 | Preservar a seleção que existia antes da abertura, somando ou subtraindo apenas o que o usuário marcou | Must | Abrir com 3 objetos já selecionados, marcar 1 novo e confirmar seleciona os 4 | 🟢 |
| RF-13 | Avisar e não abrir quando não houver objeto elegível sob o cursor | Must | Clicar no vazio do céu não abre painel e não muda a seleção | 🟢 |
| RF-14 | Ser aberto na viewport 3D, em Object Mode, por `Ctrl + Alt + botão esquerdo` e pelo menu de contexto | Must | O atalho abre o seletor com o cursor sobre objetos sobrepostos e não faz nada fora do Object Mode; o item de menu abre o mesmo seletor | 🟢 |
| RF-15 | Recusar objetos ocultos, bloqueados para seleção e não malha | Must | Cena com curva, texto, vazio, objeto oculto e objeto com `hide_select`: a lista traz só a malha elegível | 🟢 |
| RF-16 | Usar a interface nas duas línguas da extensão | Should | Em `en_US` a lista e o rodapé aparecem em inglês; em `pt_BR`, em português | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | Um raio por objeto no momento da abertura, sem recalcular no `MOUSEMOVE`; o movimento do mouse só troca o destaque e redesenha | D-02 em `_reversa_sdd/architecture.md#4`: consulta por raio a cada movimento é dívida conhecida | 🟢 |
| Desempenho | Abrir com a cena real do titular (mais de 2.000 objetos) sem travar a interface por mais de 1 s | Cena do titular medida nas entregas do editor de paredes | 🟡 |
| Compatibilidade | Só API de Blender 5.2, com `docs/rag/tools/check_api.py` limpo | `AGENTS.md#API do Blender` | 🟢 |
| Compatibilidade | Sem biblioteca externa: apenas `bpy`, `blf`, `gpu` e `bpy_extras` | `README.md#1.4` do pacote anexado | 🟢 |
| Compatibilidade | O atalho `Ctrl + Alt + clique` sobrepõe a variante de `view3d.select` nessa vista, então a ação também fica no menu de contexto e o rodapé do painel lembra o atalho | Sonda de 2026-11-19: `view3d.select` ocupa os oito combos de `LEFTMOUSE` | 🟢 |
| Desempenho | A abertura não converte geometria (`to_mesh`) nem varre `depsgraph.object_instances`: testa só a malha avaliada de objetos `MESH` | Esclarecimento Q2: curva, texto e instâncias de Geometry Nodes fora | 🟢 |
| Segurança de dados | Nenhuma escrita em malha, material, camada, preferência ou arquivo do usuário; o máximo é visibilidade temporária restaurada | `README.md#1.4` e `#5` do pacote anexado | 🟢 |
| Robustez | Objeto apagado, renomeado ou em biblioteca durante a inspeção não pode levantar exceção: a linha sai da lista ou o seletor fecha devolvendo o estado anterior | `overlap_selector.py` engole `ReferenceError` e `RuntimeError`; o requisito mantém esse cuidado | 🟡 |
| Ciclo de vida | Todo `draw_handler_add` e todo item de keymap têm remoção em todos os caminhos e no `unregister` | `AGENTS.md#Regras do código` | 🟢 |
| Internacionalização | Textos em `data/translations/<módulo>.json`, com `tools/i18n_scan.py` sem faltantes | Convenção de tradução da extensão | 🟢 |
| Testes | Teste puro para a ordenação e o recorte da lista e teste no Blender 5.2 para abrir, marcar, isolar, confirmar e cancelar | Convenção de `tests/` da extensão | 🟢 |
| Observabilidade | Só um aviso ao usuário quando não há objeto sob o cursor; nada de log por movimento de mouse | `overlap_selector.py#invoke` | 🟡 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Abrir a lista com objetos sobrepostos
  Dado uma cena em Object Mode com três cubos alinhados no mesmo ponto da tela
  Quando o projetista usa o atalho do seletor com o cursor sobre os cubos
  Então a lista abre com os três objetos, do mais próximo ao mais distante
  E a seleção existente antes da abertura continua igual

Cenário: Marcar, marcar todos e inverter
  Dado a lista aberta com quatro achados
  Quando o projetista marca o primeiro pela linha, usa Ctrl+A e depois Ctrl+/
  Então os quatro começam marcados depois do Ctrl+A
  E depois do Ctrl+/ só o primeiro continua marcado

Cenário: Rolar a lista cheia
  Dado a lista aberta com vinte achados
  Quando o projetista gira a roda até o fim da lista
  Então a última linha aparece e todas puderam ser vistas uma vez
  E a marcação e o item em foco não mudaram por causa da rolagem

Cenário: Confirmar uma seleção preparada
  Dado a lista aberta com quatro achados e dois deles marcados
  Quando o projetista pressiona Enter
  Então exatamente os dois marcados ficam selecionados
  E o objeto em foco entre os marcados vira o objeto ativo
  E nenhum passo de desfazer foi criado

Cenário: Cancelar devolve o estado anterior
  Dado três objetos selecionados antes de abrir o seletor
  Quando o projetista marca outros dois e pressiona Esc
  Então a seleção volta a ser exatamente os três objetos anteriores
  E o objeto ativo é o mesmo de antes
  E a visibilidade de todos os objetos é a mesma de antes

Cenário: Isolar e restaurar
  Dado a lista aberta com cinco achados
  Quando o projetista pressiona I e depois I de novo
  Então no primeiro toque só o objeto em foco fica visível
  E no segundo a visibilidade de todos volta ao que era

Cenário: Nada sob o cursor
  Dado o cursor sobre o fundo da viewport, sem objeto
  Quando o projetista usa o atalho do seletor
  Então nenhum painel abre
  E aparece o aviso de que não há objeto elegível
  E a seleção não muda

Cenário: Objetos que não são malha
  Dado uma cena com curva, texto, vazio, um objeto oculto e um objeto bloqueado para seleção no mesmo ponto
  Quando o projetista abre o seletor
  Então a lista traz apenas as malhas visíveis e selecionáveis
  E nenhuma exceção aparece no console
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | Sem detecção e lista não existe a feature |
| RF-05 a RF-12 | Must | É o contrato do anexo: marcar, isolar, confirmar e cancelar |
| RF-13 a RF-15 | Must | Evitam abrir um painel vazio e objetos que o usuário não pode selecionar |
| RF-04 | Must | Sem pré-visualização o usuário escolhe no escuro |
| RF-14 (atalho) | Must | Esclarecimento de 2026-11-19: `Ctrl + Alt + botão esquerdo`, mais o menu de contexto, sem tocar no `Alt` do componente |
| RF-16 | Should | A extensão é bilíngue; a feature entra na regra |
| Instâncias de Geometry Nodes, curva e texto na lista | Won't (nesta versão) | Esclarecimento de 2026-11-19, Q2: só malha avaliada; instâncias exigiriam varrer `depsgraph.object_instances` e curva ou texto exigiriam conversão |

## 9. Esclarecimentos

### Sessão 2026-11-19

- **Q:** Qual atalho abre o seletor, sem colidir com o `Alt + Shift` do `caffmob.component_pick`?
  **R:** `Ctrl + Alt + botão esquerdo`, com a mesma ação num item do menu de contexto da viewport; o `Alt` e o
  `Alt + Shift` continuam sendo do componente. → RN-08, RF-14, RNF de compatibilidade.
  Sonda no Blender 5.2: o `view3d.select` já ocupa os oito combos de `LEFTMOUSE` no mapa `3D View` (sem modificador,
  `Shift`, `Ctrl`, `Alt`, `Shift + Ctrl`, `Alt + Ctrl`, `Alt + Shift` e os três juntos), então todo atalho novo
  sobrepõe alguma variante; o item da extensão entra com `head=True`, como o do componente.
- **Q:** Instâncias de Geometry Nodes, curva e texto entram na lista dos achados?
  **R:** Não nesta versão: entram só objetos `MESH` visíveis e selecionáveis. → RN-01, RF-15, MoSCoW.
  Sonda no Blender 5.2: `ray_cast` por objeto devolveu falso em curva e em texto, e uma malha com Geometry Nodes que
  instancia cubos ficou com zero faces na geometria avaliada, porque as instâncias não fazem parte da malha do
  objeto.
- **Q:** O isolamento usa `hide_set` ou a Local View nativa?
  **R:** `hide_set`, guardando `hide_get()` de cada objeto na abertura e restaurando em toda saída. → RN-05, RF-08,
  RF-11.
  Sonda e docs de 5.2: `view3d.localview` isola o que está selecionado, o que contraria a regra de não mexer na
  seleção durante a inspeção (RN-03, RN-04), e ainda reenquadra a vista do usuário.

## 10. Lacunas

- 🟡 Se o Blender for fechado à força com o seletor aberto, o `hide_set` do isolamento fica no arquivo; não existe
  estado em disco para restaurar. Risco aceito na decisão de isolamento (Q3).
- 🟡 Numa sonda com cena mista, o `ray_cast` numa curva derrubou o Blender 5.2 com access violation uma vez; isolada, a mesma chamada devolveu falso. O filtro por `MESH` antes de avaliar evita o caso, mas o teste no Blender do plano deve abrir o seletor numa cena com curva, texto, vazio e instâncias junto da malha.
- 🟡 O tempo de abertura na cena real do titular (mais de 2.000 objetos) ainda não foi medido; a primeira tarefa do plano deve medir antes de fechar o RNF de desempenho.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-11-18 | Versão inicial gerada por `/reversa-requirements` a partir do pacote anexado (`overlap_selector.py` e `README.md`) e da extração em `_reversa_sdd/` | reversa |
| 2026-11-19 | Esclarecimentos: atalho `Ctrl + Alt + botão esquerdo` mais menu de contexto (RN-08, RF-14); só malha na lista, sem instâncias de Geometry Nodes, curva nem texto (RN-01, RF-15); isolar por `hide_set` com restaurar (RN-05, RF-08) | reversa-clarify |
