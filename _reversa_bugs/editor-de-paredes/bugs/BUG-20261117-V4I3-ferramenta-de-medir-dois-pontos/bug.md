---
schema_version: 1
id: BUG-20261117-V4I3
display_number: 150
title: Sem ferramenta de medir entre dois pontos dentro do editor
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
labels: [spec-gap, medicao, interface]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (dois testes vermelhos antes do change set, ImportError de `caffmob_draw.walls2d.medir`; verdes depois)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-EELF
    type: related-to
    state: supported
    evidence:
      - ref: "tests/blender_bug_V4I3_medir.py"
        observation: "Medir e Mover entram no mesmo despacho de ferramentas (`classico_v2.tratar`) e usam o mesmo estado de sessão; por isso as regressões cobrem as duas"

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "_reversa_sdd/measure/requirements.md", "_reversa_sdd/addenda/bug-BUG-20261117-V4I3-v001.md"]
  affected_code: ["caffmob_draw/walls2d/medir.py", "caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/classico_v2.py", "caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/panels.py"]
  root_cause:
    state: confirmed
    hypothesis: "A lista de ferramentas (`props.BTM_PG_WallEditorState.tool`) não tinha Medir e nenhum dos dois caminhos de tela tratava um clique de medição: o modal do rascunho e o `classico_v2.tratar` só conheciam SELECT, DRAW, INVERT, MOVE, ADD_NODE e REMOVE_NODE, então não havia onde guardar o primeiro ponto nem desenho da medida."
    causal_path:
      - "props.py BTM_PG_WallEditorState.tool: sem item MEASURE (a lista de Ferramentas do painel sai do enum)"
      - "ops_editor.py BTM_OT_WallEditorModal._handle: despacha DRAW, MOVE e clique de seleção; nenhum estado de medição na Session"
      - "classico_v2.py tratar: ferramentas da cena v2 antes do Studio; nenhum caminho de medição"
    evidence:
      - ref: "evidence/reproduction.md"
        observation: "ImportError do módulo nos dois testes e lista de ferramentas sem MEASURE"
      - ref: "evidence/gate1-red.md"
        observation: "vermelho nas duas pernas antes do change set"
      - ref: "evidence/gate2-green.md"
        observation: "verde nos dois testes e nas regressões depois"
    code_refs:
      - file: "caffmob_draw/walls2d/props.py"
        symbol: "BTM_PG_WallEditorState.tool"
        commit: "88c63c7e"
      - file: "caffmob_draw/walls2d/ops_editor.py"
        symbol: "BTM_OT_WallEditorModal._handle"
        commit: "88c63c7e"
      - file: "caffmob_draw/walls2d/classico_v2.py"
        symbol: "tratar"
        commit: "88c63c7e"
  reproduction_tests: ["tests/test_walls2d_medir.py", "tests/blender_bug_V4I3_medir.py"]
  regression_tests: ["tests/blender_bug_V4I3_medir.py", "tests/test_walls2d_model.py", "tests/test_walls2d_history.py", "tests/test_walls2d_selecao.py", "tests/test_walls2d_move.py", "tests/test_walls2d_convert.py", "tests/test_walls2d_heights.py", "tests/test_walls2d_studio.py", "tests/test_walls2d_menu_contexto.py", "tests/blender_bug_AKYJ_menu.py", "tests/blender_002_ui_events.py"]

spec_verdict: spec-gap

change_set:
  - {id: CHG-001, kind: test, artifact: "tests/test_walls2d_medir.py", purpose: "estado e ímã da medição em Python puro", diff: "fix/CHG-001.diff"}
  - {id: CHG-002, kind: test, artifact: "tests/blender_bug_V4I3_medir.py", purpose: "modal real: ferramenta, dois cliques, ímã, Esc e regressão", diff: "fix/CHG-002.diff"}
  - {id: CHG-003, kind: code, artifact: "caffmob_draw/walls2d/medir.py", purpose: "estado, distância e ímã dos vértices (arquivo novo)", diff: "fix/CHG-003.diff"}
  - {id: CHG-004, kind: code, artifact: "caffmob_draw/walls2d/props.py", purpose: "ferramenta MEASURE na lista e o estado da medição na sessão", diff: "fix/CHG-004.diff"}
  - {id: CHG-005, kind: code, artifact: "caffmob_draw/walls2d/ops_editor.py", purpose: "captura, desenho da medida e dica no rascunho clássico", diff: "fix/CHG-005.diff"}
  - {id: CHG-006, kind: code, artifact: "caffmob_draw/walls2d/classico_v2.py", purpose: "captura, desenho e dica na cena v2", diff: "fix/CHG-006.diff"}
  - {id: CHG-007, kind: configuration, artifact: "caffmob_draw/data/translations/walls2d.json", purpose: "textos de Medir em pt_BR e en_US", diff: "fix/CHG-007.diff"}
  - {id: CHG-008, kind: configuration, artifact: "caffmob_draw/data/translations/walls2d.json", purpose: "rótulos da planta baixa (#148) que faltavam no catálogo", diff: "fix/CHG-007b.diff"}
  - {id: CHG-009, kind: specification, artifact: "_reversa_sdd/addenda/bug-BUG-20261117-V4I3-v001.md", purpose: "adendo aditivo (spec-gap)", diff: null}

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Sem ferramenta de medir entre dois pontos dentro do editor

## Summary

O titular pede uma ferramenta de medir: tocar num ponto, tocar noutro e ver a distância entre eles, dentro do editor
de paredes.

## Expected Behavior

Pedido do titular (2026-11-17): ferramenta de medir para tocar numa área, depois noutra, e ver a medida entre elas.
A spec efetiva é a do adendo `_reversa_sdd/addenda/bug-BUG-20261117-V4I3-v001.md`: `RF-13` descreve a planta e os
painéis, mas não tinha medição livre; `measure/requirements.md` trata das cotas de módulo e do pé-direito.

## Actual Behavior

Antes da correção, dentro do editor o usuário via apenas o comprimento do trecho selecionado (rótulo no meio do trecho)
e podia digitar uma medida para alterar a parede. Não existia modo de medir distância entre dois pontos quaisquer.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Procurar uma ferramenta de medir na lista de Ferramentas e na barra superior.

Resultado: só Selecionar/Mover, Construir Parede, Inverter Sentido, Mover, Adicionar Vértice, Remover Vértice e
Enquadrar.

## Evidence

- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: lista de Ferramentas do editor, sem medir.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 7).
- `evidence/reproduction.md`, `evidence/gate1-red.md`, `evidence/gate2-green.md`.

## Acceptance Criteria

- Uma ferramenta Medir na barra/lista do editor captura o primeiro ponto e mostra a medida em tempo real até o segundo
  clique. **Atendido:** a ferramenta entra no enum de `tool` (lista de Ferramentas do painel) e a prévia segue o cursor.
- A medida aparece na unidade do projeto, com a mesma formatação da planta. **Atendido:** `draw.length_label`, o mesmo
  do rótulo dos trechos.
- Esc cancela a medição sem alterar paredes; a medida não entra no desfazer do rascunho. **Atendido:** Esc (ou o botão
  direito) limpa; o teste prova `s.undo() is False` e a assinatura do plano intacta.
- Os pontos se apoiam nos vértices e nas faces existentes quando o cursor chega perto (mesmo ímã das outras
  ferramentas). **Atendido para vértices:** `medir.snap` usa 9 px, como `NODE_HIT_PX`; o apoio em faces ficou fora
  (ver Agent Notes).

## Resolution

- **Causa raiz:** `confirmed` — a ferramenta não existia (enum, sessão e despacho dos dois caminhos de tela).
- **Estratégia:** correção direta, risco baixo (só acrescenta leitura e desenho; nada muda no rascunho nem no documento).
- **Veredito de spec:** `spec-gap`, aprovado pelo titular no fechamento; adendo aditivo versionado.
- **resolution_kind:** `fixed`.
- **Closure policy:** `local-software` satisfeita — regressão passando + veredito de spec.

### Change set

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | test | `tests/test_walls2d_medir.py` | estado e ímã em Python puro |
| CHG-002 | test | `tests/blender_bug_V4I3_medir.py` | modal real: ferramenta, dois cliques, ímã, Esc e regressão |
| CHG-003 | code | `caffmob_draw/walls2d/medir.py` | estado, distância e ímã (novo) |
| CHG-004 | code | `caffmob_draw/walls2d/props.py` | `MEASURE` no enum e `Session.medir` |
| CHG-005 | code | `caffmob_draw/walls2d/ops_editor.py` | captura, desenho e dica no rascunho clássico |
| CHG-006 | code | `caffmob_draw/walls2d/classico_v2.py` | captura, desenho e dica na cena v2 |
| CHG-007 | configuration | `caffmob_draw/data/translations/walls2d.json` | textos de Medir |
| CHG-008 | configuration | `caffmob_draw/data/translations/walls2d.json` | rótulos da planta baixa (#148) |
| CHG-009 | specification | `_reversa_sdd/addenda/bug-BUG-20261117-V4I3-v001.md` | adendo aditivo |

Diffs em `fix/CHG-001.diff` … `fix/CHG-007b.diff`; o plano visual está em `fix/plan.html`.

### Testes (vermelho → verde)

- Gate 1 (`evidence/gate1-red.md`): `ImportError` do módulo nos dois testes, exit 1.
- Gate 2 (`evidence/gate2-green.md`): `Ran 9 tests … OK` no puro e `blender_bug_V4I3_medir: OK` no Blender; i18n com
  `sem tradução: 0` e `test_i18n_coverage` OK; regressões de `walls2d`, `AKYJ` e `002_ui_events` verdes.

## Agent Notes

- O apoio em **faces** (além dos vértices) ficou fora: o ímã de face das outras ferramentas é o do despacho do Studio e
  não foi reaproveitado para não acoplar a medição à prancheta. Fica como pedido do titular se ele sentir falta.
- O CHG-008 completa 10 rótulos da planta baixa (#148) que estavam no working tree sem catálogo; sem isso o
  `test_i18n_coverage` ficava vermelho e não servia de regressão para os textos novos.
- Medir não é documentado nos arquivos de spec originais: o comportamento vive só no adendo.
