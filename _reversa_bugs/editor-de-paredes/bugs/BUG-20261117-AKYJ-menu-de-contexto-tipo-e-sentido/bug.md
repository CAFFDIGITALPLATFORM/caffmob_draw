---
schema_version: 1
id: BUG-20261117-AKYJ
display_number: 145
title: Falta menu de contexto na parede com toggles de linha, sentido e tipo
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, interface, ergonomia, toque, cores-por-tipo]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código e sondagem MCP no Blender 5.2 instalado: sem ferramenta nem operador de menu de contexto)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-EELF
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-05", "_reversa_sdd/walls2d/requirements.md#RF-13"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/classico_v2.py"]
  root_cause:
    state: confirmed
    hypothesis: "A capacidade nunca existiu e por três motivos distintos: o modal não tem estrutura de menu (nenhum `bpy.types.Menu` nem ramo de `RIGHTMOUSE` no caminho Selecionar), o desenho usa uma cor única para todo trecho (`COLORS['wall']`), e a Direção (lado da espessura) só tem caminho de escrita no trecho selecionado, sem versão em lote."
    causal_path:
      - "ops_editor.py `_handle`: sem ramo para `RIGHTMOUSE`; o evento cai em `return False` no modo Selecionar"
      - "ops_editor.py `_handle_draw`: `RIGHTMOUSE` encerra o lápis, comportamento correto a preservar"
      - "ops_editor.py `draw_plan`: pinta todo trecho com `COLORS['wall']`, sem olhar `seg.wall_type`"
      - "props.py `_side_set`: aplica em `s.segment()` apenas; não há caminho de lote como em `_type_set`"
      - "props.py `_line_set`: grava `s.line`, que é a linha de medição global, não o lado da espessura"
    evidence:
      - ref: evidence/reproduction.md
        observation: "grep sem resultado para Menu/call_menu/popup_menu em walls2d; cor única no draw_plan; Direção sem lote"
    code_refs:
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: BTM_OT_WallEditorModal._handle}
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: draw_plan}
      - {file: caffmob_draw/walls2d/props.py, symbol: _side_set}
      - {file: caffmob_draw/walls2d/model.py, symbol: Chain.invert}
  reproduction_tests: ["tests/test_walls2d_menu_contexto.py", "tests/blender_bug_AKYJ_menu.py"]
  regression_tests: ["tests/blender_bug_AKYJ_menu.py", "tests/test_walls2d_model.py", "tests/test_walls2d_selecao.py", "tests/test_walls2d_move.py", "tests/test_walls2d_history.py"]

spec_verdict: spec-gap

change_set:
  - {id: CHG-001, kind: code, artifact: "caffmob_draw/walls2d/menu_contexto.py", purpose: "módulo puro da caixa: linhas, layout preso na região, alvo do clique e regra de abertura", diff: fix/CHG-001.diff, status: applied}
  - {id: CHG-002, kind: code, artifact: "caffmob_draw/walls2d/cores.py", purpose: "cor por tipo de parede, com o NORMAL no cinza que o editor já usava", diff: fix/CHG-002.diff, status: applied}
  - {id: CHG-003, kind: code, artifact: "caffmob_draw/walls2d/props.py", purpose: "estado da caixa na sessão, inverter todas as ativas, Direção e tipo em lote, cada ação num passo de desfazer", diff: fix/CHG-003.diff, status: applied}
  - {id: CHG-004, kind: code, artifact: "caffmob_draw/walls2d/ops_editor.py", purpose: "botão direito abre a caixa no modo Selecionar, clique executa, Esc e clique fora fecham, desenho da caixa e cor por tipo na planta", diff: fix/CHG-004.diff, status: applied}
  - {id: CHG-005, kind: code, artifact: "caffmob_draw/walls2d/classico_v2.py", purpose: "mesma caixa na cena v2, com a navegação por botão direito preservada no vazio, e cor por tipo", diff: fix/CHG-005.diff, status: applied}
  - {id: CHG-006, kind: configuration, artifact: "caffmob_draw/data/translations/walls2d.json", purpose: "pt_BR e en_US de Múltiplas e Inverter sentido, exigidos pela cobertura de i18n", diff: fix/CHG-006.diff, status: applied}
  - {id: CHG-007, kind: specification, artifact: "_reversa_sdd/addenda/bug-BUG-20261117-AKYJ-v001.md", purpose: "adendo aditivo (spec-gap): abertura, Linha, Direção, inverter, tipo, cor por tipo e fechamento", diff: null, status: applied}

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Falta menu de contexto na parede com toggles de linha, sentido e tipo

## Summary

O titular quer pressionar e segurar (toque) ou clicar com o botão direito sobre uma parede e receber uma caixa moderna
na posição do toque, com três controles: Linha/Direção (externo e interno), inverter o sentido das paredes ativas e
mudar o tipo de parede, com a cor das linhas seguindo o tipo. Hoje o botão direito cancela e o caminho custa quatro
passos manuais.

## Expected Behavior

Decisão do titular em 2026-11-17 (registrada em `../../intake/relato-20261117-1520.md`):

1. Pressão longa no toque ou botão direito abre a caixa de seleção na posição do toque/clique, sobre a área do editor.
2. O primeiro toggle é **Linha / Direção (externo e interno)**: a linha de medição (`INNER`/`OUTER`) e o lado para onde
   a espessura cresce. Vale para todas as paredes ativas.
3. Um controle **inverter sentido da parede ativa**, aplicado de uma vez a todas as paredes ativas.
4. Uma opção de **mudar o tipo de parede** (`NORMAL`, `DIVISORIA`, `MURETA`), com a cor das linhas mudando para os três
   tipos. O tipo normal mantém a aparência atual do editor.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-05 descreve as ferramentas Inverter, Adicionar Vértice e
Remover Vértice por clique; RF-13 descreve os painéis laterais. Nenhum requisito prevê menu de contexto, toggles
inline ou cor por tipo de parede: `spec-gap` provável.

## Actual Behavior

`RIGHTMOUSE` encerra o modal de desenho na mesma condição de Esc (`caffmob_draw/walls2d/ops_editor.py:874`), então o
botão direito cancela em vez de abrir menu. Não existe menu de contexto em nenhum ponto do editor.

Hoje os três controles pedidos só existem assim:
- Linha pelo campo `line` (`INNER`/`OUTER`) do painel Painel, um trecho por vez.
- Sentido pela ferramenta `INVERT` (item "Inverter Sentido", `props.py:326`), que exige um clique por parede e uma
  troca de ferramenta em cada passo.
- Tipo pelo campo `wall_type` (`NORMAL`, `DIVISORIA`, `MURETA`, `props.py:360`), sem nenhuma cor associada: a planta
  desenha todas as paredes com a mesma cor (`COLORS['wall']` em `draw_plan`).

Resultado: para inverter uma parede o usuário faz quatro passos, e não há como distinguir tipo pela cor.

## Steps to Reproduce

1. Abrir o Editor de Paredes com paredes desenhadas.
2. Clicar com o botão direito sobre uma parede: nada é selecionado e nenhum menu aparece; em modo de desenho o botão
   direito cancela.
3. Selecionar a linha, escolher Inverter Sentido e clicar na parede; depois voltar a Selecionar/Mover e clicar de novo:
   a parede só aparece com o novo sentido depois dos quatro passos.
4. Trocar o Tipo de Parede para Mureta no painel: a cor da linha não muda.

## Evidence

- `evidence/painel-ferramentas-inverter-sentido.webp`: captura do titular com a seta vermelha sobre "Inverter Sentido"
  e o painel Painel com Tipo de Parede e Direção.
- `../../intake/sondagem-mcp-20261117.md`: lista de ferramentas do addon instalado
  (`SELECT, DRAW, INVERT, ADD_NODE, REMOVE_NODE`) e valores reais do Tipo de Parede (`NORMAL, DIVISORIA, MURETA`).
- `../../intake/relato-20261117-1520.md` e `../../intake/manual-ctb-cores-espessuras-20261117.webp`: decisão dos três
  toggles e padrão de cores e espessuras (CTB) usado como referência de cor por tipo.
- Relato bruto original: `../../intake/relato-20261117-1430.md` (Problema 2).

## Suspected Area

`caffmob_draw/walls2d/ops_editor.py` (modal: tratamento de `RIGHTMOUSE`, seleção por clique, desenho e `COLORS`),
`props.py` (lista de ferramentas, `line`, `wall_type`), `panels.py` e `classico_v2.py` (caminho v2, com painel
segmentado e seleção múltipla).

## Acceptance Criteria

- Pressão longa no toque ou botão direito sobre uma linha abre uma caixa na posição do clique, dentro da área do editor.
- A caixa mostra os controles já com o valor atual da parede: Linha/Direção (interno/externo), sentido e tipo.
- Trocar Linha/Direção aplica na hora em todas as paredes ativas, sem trocar de ferramenta e sem novo clique na linha.
- O controle de sentido inverte todas as paredes ativas de uma vez, como a ferramenta Inverter Sentido faz hoje numa
  parede por clique, e um único Ctrl+Z desfaz a ação inteira.
- Trocar o tipo de parede muda a cor das linhas do trecho: `NORMAL` mantém a cor atual, `DIVISORIA` e `MURETA` ganham
  cores próprias conforme o padrão CTB anexado pelo titular.
- Esc, clique fora ou um segundo botão direito fecham a caixa sem alterar nada.
- O menu não aparece sobre o painel lateral nem fora da área do editor.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-05`, `_reversa_sdd/walls2d/requirements.md#RF-13`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/walls2d/props.py`,
  `caffmob_draw/walls2d/panels.py`, `caffmob_draw/walls2d/classico_v2.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`, `tests/blender_013_touchpad_smoke.py`

## Resolution

**Causa raiz (estado final: confirmed).** A capacidade nunca existiu, por três motivos independentes, todos verificados
no código e na sondagem do addon instalado: o modal não tinha estrutura de menu (nenhuma classe `bpy.types.Menu` nem
ramo de `RIGHTMOUSE` no caminho do modo Selecionar), o desenho pintava todo trecho com `COLORS['wall']` sem olhar
`seg.wall_type`, e a Direção só tinha escrita no trecho selecionado (`_side_set`), sem caminho de lote.

**Estratégia:** correção direta, escolhida pelo titular. Duas decisões dele nesta sessão: caixa **desenhada no canvas**
(seguindo o padrão de `studio_painel.menu_rects`, que já existe no projeto) e não menu nativo; e o subconjunto de cores
**cinza atual, azul e amarelo**, assumido a partir da recomendação porque a pergunta de cores ficou sem resposta.

**Correção do relato:** no modo Selecionar o botão direito não cancelava nada, apenas não tinha efeito. Quem encerra o
lápis com o botão direito é o modo Desenhar, e esse comportamento foi preservado com teste de regressão.

**Veredito de spec:** `spec-gap`, aprovado pelo titular no fechamento. RF-05 e RF-13 não descrevem menu de contexto,
toggle inline nem cor por tipo. Adendo aditivo: `_reversa_sdd/addenda/bug-BUG-20261117-AKYJ-v001.md` (CHG-007).

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/menu_contexto.py` | seis linhas da caixa, layout preso na região, alvo do clique e regra de abertura |
| CHG-002 | code | `caffmob_draw/walls2d/cores.py` | cor por tipo, com o NORMAL no cinza atual |
| CHG-003 | code | `caffmob_draw/walls2d/props.py` | `inverter_ativas`, `aplicar_direcao`, `aplicar_tipo`, `estado_da_caixa` e o estado da caixa na sessão |
| CHG-004 | code | `caffmob_draw/walls2d/ops_editor.py` | abertura, execução, fechamento, desenho da caixa e cor por tipo na planta |
| CHG-005 | code | `caffmob_draw/walls2d/classico_v2.py` | a mesma caixa na cena v2 e cor por tipo, sem perder o arraste de navegação no vazio |
| CHG-006 | configuration | `caffmob_draw/data/translations/walls2d.json` | `Múltiplas` e `Inverter sentido` em pt_BR e en_US |
| CHG-007 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-AKYJ-v001.md` | adendo aditivo do veredito `spec-gap` |

Diffs: `fix/CHG-001.diff` a `fix/CHG-006.diff`. Os de `props.py` e `ops_editor.py` incluem também o change set do #146,
que está no mesmo working tree sem commit.

**Testes (vermelho para verde).** Antes: os dois arquivos novos nem importavam
(`ImportError: cannot import name 'cores' from 'caffmob_draw.walls2d'`), registrado em `evidence/gate1-red.md`. Depois:
10 testes puros OK, `blender_bug_AKYJ_menu: OK`, i18n sem tradução faltando, cobertura de i18n OK e sete regressões de
`walls2d` OK (`evidence/gate2-green.md`).

**Não coberto:** o modal não foi exercitado com janela e mouse, então a abertura da caixa é provada pela regra e pelo
módulo puro, não por um clique real; a caixa na cena v2 compila e é desenhada pelo mesmo código, sem teste automatizado
próprio; `ruff` não existe neste host, no lugar dele `py_compile` e a checagem de coluna (120).

**Fechamento:** closure policy `local-software` satisfeita (reprodução e regressão passando mais veredito aprovado).
Trava em `DONE.md`.

## Agent Notes

- Severidade e prioridade propostas pelo agente na triagem (medium/P2), a confirmar pelo titular.
- Decisão de vocabulário resolvida pelo titular em 2026-11-17: o toggle é **Linha/Direção**, não o campo Tipo de
  Parede. O tipo de parede entra como quarto controle, com cor.
- Cores por tipo (referência CTB do titular): verde para paredes de alvenaria, azul para estrutura, vermelho ou amarelo
  para meia-parede e mureta em vista, tracejado para o que fica acima do plano de corte, cinza 253 na hachura. O fix
  deve escolher um subconjunto coerente para a tela e registrar a decisão, porque o manual é de prancha impressa.
- Hoje Esc e botão direito saem pelo mesmo ramo: separar os dois muda o comportamento do modal e precisa de teste de
  regressão antes (Esc tem de continuar cancelando).
- O desenho é todo em `POST_PIXEL` com GPU/blf: a caixa e os toggles precisam ser desenhados e testados contra o
  painel lateral sobreposto. Consultar `docs/rag/` para `gpu`/`blf` no 5.2 e para eventos de toque.
- Pressão longa no toque não existe como evento hoje: o editor usa `TRACKPAD*` só para navegação. Sem emenda, o
  caminho realista nesta fase é o botão direito, com o toque entrando depois.
- Reaproveitar o mesmo menu para o modelo v2 (`classico_v2.py`), senão as duas telas divergem.
- Custo: um menu desenhado à mão em GPU dá trabalho e não tem acessibilidade de widget. Alternativa a avaliar com o
  titular: popover de verdade do Blender (`UILayout`) em vez de desenho próprio.
- Fechamento em 2026-11-17: o titular escolheu a caixa desenhada no canvas, seguindo o padrão que já existe em
  `studio_painel.py`. Cores por tipo: NORMAL no cinza atual, DIVISORIA em azul, MURETA em amarelo (a pergunta ficou sem
  resposta e a recomendação foi assumida). A pressão longa no toque segue fora, numa rodada própria.
