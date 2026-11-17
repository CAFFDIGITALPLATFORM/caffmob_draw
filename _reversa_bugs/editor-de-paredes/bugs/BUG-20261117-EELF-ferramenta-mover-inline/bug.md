---
schema_version: 1
id: BUG-20261117-EELF
display_number: 146
title: Sem ferramenta Mover inline para deslocar paredes com medida digitada
status: resolved
phase: delivering
severity: high
priority: P1
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, interface, mover, produtividade]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código e sondagem MCP no Blender 5.2 instalado: ferramentas do addon são SELECT, DRAW, INVERT, ADD_NODE e REMOVE_NODE)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-03", "_reversa_sdd/walls2d/requirements.md#RN-25", "_reversa_sdd/walls2d/design.md#Interface"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/model.py", "caffmob_draw/walls2d/classico_v2.py", "caffmob_draw/walls2d/panels.py"]
  root_cause:
    state: supported
    hypothesis: "A capacidade nunca existiu: o modal do editor só sabe arrastar vértice. O enum de ferramentas tem SELECT, DRAW, INVERT, ADD_NODE e REMOVE_NODE, o ramo SELECT de _handle_click inicia self.dragging com um nó, e o MOUSEMOVE chama chain.move_node(k, point). O modelo não tem translação de trecho nem de conjunto, e a seleção em lote (s.multi) é usada só para apagar e para colorir."
    causal_path:
      - "props.py: TOOLS com 5 itens, sem MOVE (confirmado no addon instalado via MCP)"
      - "ops_editor.py:_handle_click, ramo SELECT: self.dragging = node e s.multi preenchido, sem ação de translação"
      - "ops_editor.py:_handle, MOUSEMOVE com self.dragging: chain.move_node(k, point), um vértice por vez"
      - "model.py: move_node muda um nó; não há translate de trechos nem de cadeias"
    evidence:
      - ref: evidence/reproduction.md
        observation: "enum tool do addon 5.2 instalado sem MOVE; leitura do modal e do modelo sem caminho de translação"
    code_refs:
      - {file: caffmob_draw/walls2d/props.py, symbol: TOOLS}
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: BTM_OT_WallEditorModal._handle_click}
      - {file: caffmob_draw/walls2d/model.py, symbol: Chain.move_node}
  reproduction_tests: ["tests/test_walls2d_move.py#test_move_um_trecho_desloca_os_dois_nos", "tests/test_walls2d_move.py#test_vizinha_estica_com_o_no_compartilhado", "tests/test_walls2d_move.py#test_move_dois_trechos_juntos", "tests/blender_bug_EELF_move.py#1-2"]
  regression_tests: ["tests/test_walls2d_move.py#test_move_nao_muda_espessura_altura_nem_tipo", "tests/test_walls2d_move.py#test_move_zero_nao_muda_o_rascunho", "tests/test_walls2d_move.py#test_indice_invalido_levanta", "tests/blender_bug_EELF_move.py#3-4", "tests/blender_002_ui_events.py"]

spec_verdict: spec-gap

change_risk:
  classification: média
  reasons: ["mexe no modal e no modelo do editor, o núcleo da edição de paredes", "sem dados persistidos: o rascunho vive em memória e o Ctrl+Z cobre o passo", "a regra do nó compartilhado com parede não ativa é decisão de domínio e afeta a geometria que vai para a cena no OK", "duas telas para manter em sincronia: editor clássico e modelo v2 (classico_v2.py)"]

change_set:
  - {id: CHG-001, kind: code, artifact: "caffmob_draw/walls2d/model.py", purpose: "WallPlan.move_segments: translação das paredes ativas, com o nó compartilhado andando uma vez só", diff: fix/CHG-001.diff, status: applied}
  - {id: CHG-002, kind: code, artifact: "caffmob_draw/walls2d/props.py", purpose: "ferramenta MOVE no enum (rótulo Mover) e o estado do movimento na sessão", diff: fix/CHG-002.diff, status: applied}
  - {id: CHG-003, kind: code, artifact: "caffmob_draw/walls2d/ops_editor.py", purpose: "modal: arraste, setas de 90°, medida digitada, Esc, um passo de desfazer e a dica da ferramenta", diff: fix/CHG-003-004.diff, status: applied}
  - {id: CHG-004, kind: code, artifact: "caffmob_draw/walls2d/ops_editor.py", purpose: "botão Mover na barra superior e leitura de direção e medida junto ao ponteiro", diff: fix/CHG-003-004.diff, status: applied}
  - {id: CHG-005, kind: code, artifact: "caffmob_draw/walls2d/classico_v2.py", purpose: "cena v2 recusa a ferramenta com mensagem, em vez de ignorar o clique", diff: fix/CHG-005.diff, status: applied}
  - {id: CHG-006, kind: configuration, artifact: "caffmob_draw/data/translations/walls2d.json, walls2d_classico_v2.json", purpose: "pt_BR e en_US das 7 frases novas, exigidas pela cobertura de i18n", diff: fix/CHG-006.diff, status: applied}
  - {id: CHG-007, kind: specification, artifact: "_reversa_sdd/addenda/bug-BUG-20261117-EELF-v001.md", purpose: "adendo aditivo (spec-gap): ferramenta Mover, regra da vizinha estica e desfazer", diff: null, status: applied}

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Sem ferramenta Mover inline para deslocar paredes com medida digitada

## Summary

O titular pede ferramentas inline no topo do editor, com uma função "Mover" que desloca as paredes selecionadas em
qualquer direção, pelo mouse ou por seta do teclado mais medida digitada, com a direção do movimento indicada na tela.
Hoje não existe mover de parede: só arrastar vértice.

## Expected Behavior

Pedido do titular (2026-11-17): selecionar uma ou mais paredes e ter ferramentas inline estilo grid no topo do editor;
tocar em qualquer parede mostra a função gráfica "Mover"; acionando-a, as paredes ativas andam em qualquer direção com
o mouse, ou por seta do teclado mais medida digitada, e a tela mostra a direção para onde a medida vai levar a parede.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-03 cobre selecionar face/vértice, arrastar vértice com travas e
digitar medida; RN-25 cobre a barra superior, que hoje só tem a lupa de zoom. Nada especifica mover a parede inteira
nem medida direcional na barra. `spec-gap` provável.

## Actual Behavior

O modal arrasta um vértice por vez (`model.move_node`, RN-05/RN-06): ao mover um vértice, os trechos vizinhos mudam de
comprimento e de ângulo, o que não é mover a parede.

A barra superior (`RN-25`, `caffmob_draw/walls2d/ops_editor.py`) contém só o botão de zoom janela. As ferramentas do
editor são SELECT, DRAW, INVERT, ADD_NODE e REMOVE_NODE (`props.py`, dicionário de dicas do `draw_plan`): nenhuma move
a parede.

Arrastar com o botão esquerdo no vazio não move a seleção, e não existe modo em que uma medida digitada desloque a
parede na direção indicada.

## Steps to Reproduce

1. Abrir o Editor de Paredes e selecionar uma parede na linha interna.
2. Procurar a função "Mover" na barra superior e no painel Ferramentas.

Resultado: não existe. Arrastar só funciona em vértice (muda comprimento e ângulo, não desloca a parede).

## Evidence

- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: barra superior com apenas a lupa e painel
  Ferramentas sem Mover.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 3).
- `../../intake/sondagem-mcp-20261117.md`: no addon instalado, `btm_wall_editor.tool` enumera apenas
  `SELECT, DRAW, INVERT, ADD_NODE, REMOVE_NODE`.

## Suspected Area

`caffmob_draw/walls2d/ops_editor.py` (barra superior, modal, desenho da seleção), `props.py` (lista de ferramentas e
estado), `classico_v2.py` (caminho v2 com seleção múltipla e `studio_*`), `panels.py` (atalhos no painel).

## Acceptance Criteria

- Selecionada uma ou mais paredes, a barra do topo mostra o botão Mover junto das demais ferramentas inline.
- Com Mover ativo, as paredes selecionadas acompanham o mouse em qualquer direção, com prévia antes de confirmar.
- Com Mover ativo, as setas do teclado escolhem a direção e a medida digitada (na unidade do projeto, aceitando contas)
  desloca a seleção nessa direção; a tela mostra a direção ativa e o valor antes de aplicar.
- Esc cancela o movimento em curso; Ctrl+Z desfaz um movimento concluído, como qualquer outra edição do rascunho.
- Paredes ligadas às movidas continuam encadeadas (sem furos nem cruzamentos) e as aberturas acompanham, como no OK.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-03`, `_reversa_sdd/walls2d/requirements.md#RN-25`,
  `_reversa_sdd/walls2d/design.md#Interface`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/walls2d/props.py`,
  `caffmob_draw/walls2d/classico_v2.py`, `caffmob_draw/walls2d/panels.py`
- Testes existentes relacionados: `tests/test_walls2d_model.py`, `tests/blender_002_ui_events.py`

## Resolution

**Causa raiz (estado final: supported).** A capacidade nunca existiu: o modal do editor só arrasta vértice
(`Chain.move_node`), o enum de ferramentas não tem mover, e o modelo não tinha translação de trecho. Confirmado pelo
enum do addon instalado no Blender 5.2 e pela leitura de `_handle_click`/`_handle`.

**Estratégia:** correção direta, com a regra aprovada pelo titular em 2026-11-17 ("A vizinha estica"): o nó
compartilhado anda junto e a parede não ativa muda comprimento e ângulo.

**Veredito de spec:** `spec-gap`, escolhido pelo titular no fechamento. Nada em RF-03 nem em RN-25 descrevia mover a
parede inteira ou medida direcional na barra. Adendo aditivo: `_reversa_sdd/addenda/bug-BUG-20261117-EELF-v001.md`
(CHG-007).

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/walls2d/model.py` | `WallPlan.move_segments`: translação das paredes ativas, validação de índice, nó compartilhado uma vez só |
| CHG-002 | code | `caffmob_draw/walls2d/props.py` | ferramenta `MOVE` no enum e o estado do movimento na sessão |
| CHG-003 | code | `caffmob_draw/walls2d/ops_editor.py` | modal: arraste com Shift no eixo, setas de 90°, medida digitada, Esc, um passo de desfazer, dica da ferramenta |
| CHG-004 | code | `caffmob_draw/walls2d/ops_editor.py` | botão Mover na barra superior e leitura de direção e medida junto ao ponteiro |
| CHG-005 | code | `caffmob_draw/walls2d/classico_v2.py` | cena v2 recusa a ferramenta com mensagem, em vez de ignorar o clique |
| CHG-006 | configuration | `caffmob_draw/data/translations/*.json` | pt_BR e en_US das 7 frases novas (cobertura de i18n) |
| CHG-007 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-EELF-v001.md` | adendo aditivo do veredito `spec-gap` |

Diffs: `fix/CHG-001.diff`, `fix/CHG-002.diff`, `fix/CHG-003-004.diff`, `fix/CHG-005.diff`, `fix/CHG-006.diff`.

**Testes (vermelho para verde).** Antes da correção: `tests/test_walls2d_move.py` com 6 erros
(`AttributeError: 'WallPlan' object has no attribute 'move_segments'`) e `tests/blender_bug_EELF_move.py` com
`AssertionError: ferramentas do editor hoje: ['SELECT', 'DRAW', 'INVERT', 'ADD_NODE', 'REMOVE_NODE']`
(`evidence/gate1-red.md`). Depois: 6 testes OK, `blender_bug_EELF_move: OK` no addon carregado, i18n OK e as seis
regressões de `walls2d` OK (`evidence/gate2-green.md`).

**Não coberto:** arraste real na interface (o modal não foi exercitado com janela e mouse) e `ruff`, ausente no host;
no lugar dele, compilação e checagem de coluna (120).

**Fechamento:** closure policy `local-software` satisfeita (regressão passando mais veredito aprovado). Trava em
`DONE.md`.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (high/P1), a confirmar pelo titular: é a operação que ele
  repete em toda planta, e hoje não tem substituto.
- Ponto delicado de domínio: mover parede com vizinhas encadeadas obriga a decidir o que acontece com o vértice
  compartilhado e com o ângulo. Esse desenho tem de virar adendo de spec antes do código, não pode ser improvisado no
  modal.
- Reaproveitar `model.move_node` e a trava ortogonal já testada reduz risco; evitar duplicar geometria em `classico_v2`.
- O desenho é `POST_PIXEL` com `gpu`/`blf`: consultar `docs/rag/` (5.2) para eventos de mouse/setas e para a barra
  superior antes de codar.
