---
schema_version: 1
id: BUG-20261011-6JIM
display_number: 59
title: "Cancelar não desfaz a Montagem"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: cabinet_editor
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["editor de armário: rascunho e fila", "OK e Cancelar mantêm o resultado de sempre quando a fila está vazia"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-N2D4
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/cabinet_editor/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-42"]
  affected_code: ["caffmob_draw/cabinet_editor/panels_structure.py", "caffmob_draw/cabinet_editor/ops_editor.py"]
  root_cause:
    state: confirmed
    hypothesis: "O painel grava direto em btm_cabinet.assembly (fora da fila) e EditorState não tem assembly: o rollback não a restaura."
    causal_path:
      - "cabinet_editor/panels_structure.py draw_assembly: row.prop(root.btm_cabinet, 'assembly')"
      - "cabinet_editor/state.py EditorState: sem assembly"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/cabinet_editor/panels_structure.py, symbol: draw_assembly, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_6JIM_cabinet_queue.py"]
  regression_tests: ["tests/blender_bug_6JIM_cabinet_queue.py", "tests/blender_004_cabinet_editor_smoke.py", "tests/test_cabinet_editor_state.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_6JIM_cabinet_queue.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/cabinet_editor/ops_editor.py
    purpose: "ordem OK/Cancelar; erro limpo antes"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/cabinet_editor/ops_actions.py
    purpose: "operador da Montagem"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/cabinet_editor/panels_structure.py
    purpose: "botões da Montagem pela fila"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/cabinet_editor/state.py
    purpose: "assembly no EditorState e na assinatura"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/cabinet_editor/bridge.py
    purpose: "read_state/apply_state com assembly"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/data/translations/cabinet_editor.json
    purpose: "dica do operador novo"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/CHG-007.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Cancelar não desfaz a Montagem

## Summary

O painel escreve direto em `btm_cabinet.assembly`, e `SET_ASSEMBLY` nunca é enfileirado.

## Expected Behavior

A Montagem passa pela fila (`SET_ASSEMBLY`) e o Cancelar volta ao valor de abertura.

Spec efetiva: `_reversa_sdd/cabinet_editor/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-42`.

## Actual Behavior

O painel escreve direto em `btm_cabinet.assembly`, e `SET_ASSEMBLY` nunca é enfileirado.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 48.

## Suspected Area

- `caffmob_draw/cabinet_editor/panels_structure.py`
- `caffmob_draw/cabinet_editor/ops_editor.py`

## Acceptance Criteria

- A Montagem passa pela fila (`SET_ASSEMBLY`) e o Cancelar volta ao valor de abertura.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-42`
- Código afetado: `caffmob_draw/cabinet_editor/panels_structure.py`, `caffmob_draw/cabinet_editor/ops_editor.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-N2D4 (contexto `cabinet_editor`), state `proposed`

## Resolution

- **Lote:** 12 (fila do editor de armário) (BUG-20261011-6JIM, BUG-20261011-N2D4, BUG-20261011-E33D); plano em `_reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** o painel gravava a Montagem direto, fora da fila, e o `EditorState` não a tinha.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 42 e cabinet_editor DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_6JIM_cabinet_queue.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/cabinet_editor/ops_editor.py` | ordem OK/Cancelar; erro limpo antes | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/cabinet_editor/ops_actions.py` | operador da Montagem | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/cabinet_editor/panels_structure.py` | botões da Montagem pela fila | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/cabinet_editor/state.py` | assembly no EditorState e na assinatura | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/cabinet_editor/bridge.py` | read_state/apply_state com assembly | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/data/translations/cabinet_editor.json` | dica do operador novo | `CHG-007.diff` |

**Vermelho (antes da correção):** `blender_bug_6JIM_cabinet_queue` com 5 falhas no projeto.

**Verde (depois):** `blender_bug_6JIM_cabinet_queue: OK`, `test_cabinet_editor_state` e `test_i18n_coverage` OK; na cópia isolada também `blender_004_cabinet_editor_smoke`, `blender_006_cabinet_editor_tabs_smoke`, `blender_008_construtor_smoke` (xvfb) e `blender_012_cabinet_standard_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_6JIM_cabinet_queue.py`. **Regressão:** `tests/blender_bug_6JIM_cabinet_queue.py`, `tests/blender_004_cabinet_editor_smoke.py`, `tests/test_cabinet_editor_state.py`.

## Agent Notes

- Item 48 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
