# Roadmap: Seleção por componente e porta e janela na região selecionada

> Identificador: `011-selecao-por-componente`
> Data: `2026-10-09`
> Requirements: `_reversa_forward/011-selecao-por-componente/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

A feature tem três frentes.

**Seleção por componente.** Um núcleo puro novo, `selection/component.py`, responde "qual é a raiz deste objeto?". Ele
reaproveita as funções de `selection/classify.py` (`classify`, `module_root`, `free_group`) e lê o modo de seleção dos
armários. Um **normalizador de seleção** (`selection/component_select.py`, handler `depsgraph_update_post`) troca as
peças selecionadas pelas raízes, seja qual for a origem da seleção: clique, caixa ou lista de objetos. Alt + clique é
um operador próprio no keymap, que seleciona a peça e a marca como exceção para o normalizador.

**Exclusão.** O `caffmob.delete_with_aggregates`, que já está em X/Delete, vira a porta de entrada única da exclusão.
O poll dele passa também para raízes com descendentes, e a execução remove a subárvore inteira. O
`delete_door_window` passa a apagar em profundidade.

**Região na parede.** Um operador modal novo, `btm.wall_region`, desenha um retângulo na parede com dois cliques e o
guarda na `WindowManager`, como estado de sessão. A geometria do recorte de parede é a base. As inserções de porta e
de janela leem a região: com uma região válida, a abertura já aparece no lugar, com as medidas exatas, e Enter ou
clique confirma. As contas (medidas, peitoril, cabe ou não cabe) ficam num núcleo puro, `openings/region_core.py`.

## 2. Princípios aplicados

`.reversa/principles.md` não existe. Valem as regras do `CLAUDE.md`, que a feature respeita:

| Princípio | Como a feature se relaciona | Status |
|-----------|------------------------------|--------|
| Diferenças de versão só em `compat.py` | Nenhuma API dependente de versão é nova; nada a mudar em `compat.py` | respeita |
| Handlers com remoção em todos os caminhos e `@persistent` | O normalizador (`depsgraph_update_post`), o desenho da região (`draw_handler_add`) e os keymaps têm remoção no `unregister()`; o desenho da região também sai no Esc, na confirmação e no `load_post` | respeita |
| `bpy.props` lidas por atributo; `# type: ignore` | `Scene.btm_component_select`, `WindowManager.btm_wall_region` | respeita |
| Operadores que alteram dados com `UNDO` | Exclusão, região confirmada e inserção com `{'REGISTER', 'UNDO'}`; Alt + clique com `UNDO` como o `view3d.select` | respeita |
| Textos em português, com tradução | Catálogos `selection.json` e `openings.json`; `test_i18n_coverage` | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | Núcleo puro `selection/component.py`: `component_root(obj, modes)` e `collapse(objs, modes)` (raízes sem repetir, na ordem), com a precedência da nota D-01 abaixo | Fica testável fora do Blender, como `classify` (`tests/test_classify.py`, objetos simulados); reaproveita resolvedores que já existem | Espalhar a regra no handler e no delete; marcar a raiz com propriedade nova em todo objeto | 🟢 |
| D-02 | Normalizador em `depsgraph_update_post`: compara a assinatura da seleção (nomes selecionados e ativo) com a última vista. Se mudou e o interruptor está ligado, desmarca as peças e marca as raízes, e a raiz da peça ativa vira a ativa. Uma trava de reentrada evita laço | Cobre clique, caixa, lista de objetos, `select_all` e scripts num ponto só; o `msgbus` atual (`ui/sidebar_selection.py`) só vê o ativo, não a seleção por caixa | Sobrescrever `view3d.select` no keymap (não cobre caixa, laço nem lista de objetos); só `msgbus` do ativo | 🟡 |
| D-03 | Arrastar uma peça logo após o clique: validar na primeira ação que a raiz já está selecionada quando o `transform.translate` do arraste começa. Se não estiver, um operador de clique no keymap (`btm.component_click`, `LEFTMOUSE` `PRESS`, `head=True`) chama `view3d.select` e promove na hora, devolvendo `PASS_THROUGH` para o arraste seguir | RF-05: arrastar o pé move a cadeira inteira. O normalizador roda depois do redesenho e talvez antes do limiar de arraste, mas isso precisa ser provado | Assumir sem testar | 🟡 |
| D-04 | Alt + clique: `btm.component_pick` (`LEFTMOUSE` `CLICK` `alt=True`, `head=True`; Alt + Shift soma), com poll que exige o interruptor ligado. Chama `view3d.select(location=…)` e guarda o nome da peça em `WindowManager.btm_component_exempt`. O normalizador deixa as peças isentas em paz enquanto continuam selecionadas, e a isenção some quando a seleção muda sem Alt | RN-06; com o interruptor desligado, Alt + clique volta ao comportamento do Blender (lista de objetos sob o cursor) | Duplo clique para entrar no componente (descartado pelo titular, Q2) | 🟢 |
| D-05 | Exclusão: o `caffmob.delete_with_aggregates` (`aggregates/ops_aggregate.py`) continua sendo o único item de X/Delete. O poll passa também quando algum selecionado tem descendentes. A execução segue a nota D-05 abaixo | Um item só em X/Delete evita dois keymaps `head=True` competindo; mantém a pergunta dos agregados (RN-03) e solta os itens grudados como hoje | Operador novo também em X/Delete (ordem entre os dois `head=True` não é garantida) | 🟢 |
| D-06 | Corrigir `delete_door_window` (`operators/doors_windows.py`, l. 1317-1350) para apagar `children_recursive`, pela mesma rotina do D-05 | O caminho do menu (`caffmob_general.delete`) também deixava folha e ferragens soltas | Corrigir só o atalho | 🟢 |
| D-07 | "Modo gabinete" é o valor `Cabinets` do modo de seleção da biblioteca do armário: `frameless_selection_mode`, `face_frame_selection_mode` (quando `..._enabled`) e `closet_selection_mode` (quando `..._enabled`). Módulo rápido (`btm_plane MODULE`), que não tem modo, sobe sempre. Os modos chegam ao núcleo como um dicionário `{biblioteca: está_no_modo_gabinete}` | RN-04, Q1; o núcleo continua puro | Modo global novo | 🟡 |
| D-08 | Interruptor `Scene.btm_component_select` (Bool, padrão ligado; salvo no arquivo; arquivo antigo sem a propriedade lê o padrão). Ele aparece no bloco do topo da barra lateral, junto dos modos de seleção (`ui/view3d_sidebar.py`), e no HUD da viewport quando o HUD está ligado (`operators/viewport_hud.py`) | RN-09; premissa da seção 10 do requirements | Preferência da extensão (não fica no arquivo) | 🟡 |
| D-09 | Importação de OBJ/FBX/glTF (`aggregates/ops_import.py`) com mais de uma malha chama `group.create_group(meshes, 'PLAIN', <nome do arquivo>)` e seleciona o grupo. Com uma malha só, ela fica como está | RN-02; o comando "Montar janela" continua funcionando sobre as malhas do grupo | Pedir ao usuário se quer agrupar | 🟢 |
| D-10 | Região: `btm.wall_region` (modal, `UNDO` só na confirmação). Faz dois cliques na parede, com raycast e projeção no plano da parede iguais aos do `draw_wall_cutter` (`operators/walls.py`, l. 5534-5572), e desenha com `draw_handler_add` `POST_VIEW`. A região fica em `WindowManager.btm_wall_region`: nome da parede, `x0`, `x1`, `z0`, `z1` locais e lado da face. Ela não é salva e some ao abrir outro arquivo | RN-10, Q3; a região é estado de sessão, não dado do projeto | Objeto na cena para a região (sujaria o arquivo e o undo) | 🟢 |
| D-11 | Núcleo puro `openings/region_core.py`: `fit(region, wall_length, wall_height, kind, gaps)`. Devolve a posição x, a largura, a altura e o peitoril exatos, ou o motivo da recusa. Porta: peitoril 0 e altura `z1` (RN-11). Janela: peitoril `z0` e altura `z1 − z0`. Sem grade e sem folga | RF-09, RF-10; testável fora do Blender | Conta dentro do modal | 🟢 |
| D-12 | `_PlaceWallObjectBase` (`operators/doors_windows.py`): com uma região válida para a parede, `execute` posiciona o vão por `fit` (`Dim X`, `Dim Z`, x, z) sem passar por `find_placement_gap` nem pela grade. O modal ganha o estado "na região": Enter ou clique confirma (`cut_wall` + `_sync_opening`, como o clique de hoje), Esc cancela e mantém a região. Região inválida mostra o aviso e cai no modo de hoje | RN-11, RN-12; reaproveita a confirmação atual | Inserir direto, sem confirmação (o pedido fala em teclar Enter) | 🟡 |

**Nota D-01, precedência da raiz** (a primeira regra que casa vale):
1. agregado ou item grudado: a raiz é o próprio agregado ou item (RN-03);
2. vão de porta ou janela (`IS_ENTRY_DOOR_BP`, `IS_WINDOW_BP`, `btm_plane OPENING`), inclusive as peças, o símbolo e
   o texto 2D filhos do vão;
3. módulo, só no modo gabinete (D-07);
4. raiz de item da biblioteca (`btm_object_item.is_item`);
5. grupo mais alto (`free_group`);
6. senão, o próprio objeto.

Paredes, piso, teto, obstáculos e cotas soltas não sobem.

**Nota D-05, execução da exclusão:**
1. expande cada alvo com `children_recursive`, sem os agregados quando o usuário escolhe mantê-los e sem os itens
   grudados, que se soltam no lugar;
2. tira o booleano da parede dos vãos de porta e janela;
3. remove de baixo para cima.

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| O interruptor fica na barra lateral, junto dos modos de seleção, e no HUD | §10 Lacunas (🟡) | Baixo: só muda onde o controle aparece |
| Selecionar dispara `depsgraph_update_post` em tempo de clicar e arrastar | D-02, D-03 | Médio: o arraste moveria só a peça. O D-03 tem o plano B |
| O módulo rápido (`btm_plane MODULE`) sobe sempre, por não ter modo de seleção | D-07 | Baixo |
| Apagar uma peça intermediária (por exemplo, o grupo FRAME, com o interruptor desligado) leva os descendentes dela, para não deixar peças órfãs | RN-08, RN-09 | Baixo: Ctrl+Z desfaz |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Resolução de componente | `selection/component.py` (novo) | componente-novo | Raiz e colapso de raízes, puro |
| Normalizador de seleção | `selection/component_select.py` (novo) | componente-novo | `depsgraph_update_post`, Alt + clique, propriedades, keymaps, `load_post` |
| Classificação | `selection/classify.py` | n/a (reuso) | Sem mudança; usado pelo D-01 |
| Exclusão | `aggregates/ops_aggregate.py#BTM_OT_DeleteWithAggregates` | regra-alterada | Poll e execução por subárvore (D-05) |
| Exclusão de porta e janela | `operators/doors_windows.py#delete_door_window` | regra-alterada | Apaga em profundidade (D-06) |
| Importação | `aggregates/ops_import.py` | regra-alterada | Agrupa várias malhas (D-09) |
| Região na parede | `openings/region_core.py`, `openings/region.py` (novos) | componente-novo | Núcleo puro e operador modal com desenho |
| Inserção de aberturas | `operators/doors_windows.py#_PlaceWallObjectBase` | regra-alterada | Estado "na região" (D-12) |
| Barra lateral e HUD | `ui/view3d_sidebar.py`, `ui/sidebar_build.py`, `operators/viewport_hud.py` | regra-alterada | Interruptor e botão "Marcar região" em Construir › Aberturas |
| Traduções | `data/translations/selection.json`, `openings.json` | regra-alterada | Textos novos |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - uma propriedade de cena salva (`btm_component_select`);
  - estado de sessão na `WindowManager`: região e peças isentas;
  - nenhuma marca nova nos objetos, porque a raiz é calculada pelas marcas que já existem.
- Detalhe completo em: `_reversa_forward/011-selecao-por-componente/data-delta.md`

## 7. Delta de contratos externos

n/a: a feature não toca contrato externo (HTTP, fila, arquivo de troca).

## 8. Plano de migração

1. Arquivo antigo abre com o interruptor ligado (padrão da propriedade), sem script de migração.
2. OBJ importados antes da feature continuam como malhas soltas, cada uma um componente de um objeto só. Para juntar,
   o usuário usa o "Agrupar" que já existe.
3. Portas e janelas antigas já têm o vão como raiz: nada a migrar.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| O normalizador chega depois do início do arraste e a peça se move sozinha | alto | médio | Primeira ação de código é uma fumaça de prova (D-03); plano B com o operador de clique |
| Laço ou custo do handler em cena grande | médio | baixo | Assinatura da seleção e trava de reentrada; o handler sai cedo se a seleção não mudou; meta abaixo de 50 ms com 2.000 objetos |
| Undo guarda a seleção da peça antes da promoção (a etapa do `view3d.select` é gravada antes do handler) | baixo | médio | Aceitar: desfazer a seleção não muda dado. Registrar no `regression-watch` |
| Alt + clique conflita com "Emular mouse de 3 botões" (Alt + clique orbita) | médio | baixo | Aviso no guia; com a emulação ligada, a seção Selecionado lista as peças da raiz para escolher |
| Promover para o módulo atrapalha o editor de armário (004/006) ou o "Mover sobre" (002) | médio | baixo | O normalizador não age com modal da extensão rodando (sinal do `move_over` e `cabinet_editor`) e só no modo gabinete; fumaças 002, 004 e 006 verdes |
| Excluir em profundidade apaga peça compartilhada (malha ou material) | baixo | baixo | `bpy.data.objects.remove` remove objetos, não malhas compartilhadas |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Testes puros (`test_component_core.py`, `test_wall_region_core.py`) e fumaças da 011 verdes; fumaças 002, 003, 004,
      007 e 010 continuam verdes
- [ ] `ruff check caffmob_draw/` e `python3 docs/rag/tools/check_api.py` sem erro
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-09 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-10-09 | `/reversa-coding`: operadores novos com prefixo `caffmob.` (`caffmob.component_pick`, `caffmob.component_click_reset`, `caffmob.wall_region`, `caffmob.wall_region_clear`), como exige o `tests/test_identity.py`; o plano B do D-03 não foi necessário (T011) | reversa |
