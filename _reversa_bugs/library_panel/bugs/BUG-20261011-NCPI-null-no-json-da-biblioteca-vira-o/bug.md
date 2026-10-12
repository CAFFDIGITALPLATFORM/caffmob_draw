---
schema_version: 1
id: BUG-20261011-NCPI
display_number: 88
title: "null no JSON da biblioteca vira o texto 'None'"
status: open
phase: triaging
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: library_panel
feature: unclassified
labels: ["revisao-specs-2026-10"]

visibility: normal
security_suspected: false

reproduction:
  classification: unknown
  rate: "não executado (confirmado por leitura do código)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/library_panel/design.md#F-06"]
  affected_code: ["caffmob_draw/library_panel/models_core.py", "caffmob_draw/library_panel/categories_core.py"]
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---

# null no JSON da biblioteca vira o texto 'None'

## Summary

`"name": null` vira categoria "None", `label: null` vira "None" e `door_swing: null` é recusado.

## Expected Behavior

`null` é tratado como ausente (F-06).

Spec efetiva: `_reversa_sdd/library_panel/design.md#F-06`.

## Actual Behavior

`"name": null` vira categoria "None", `label: null` vira "None" e `door_swing: null` é recusado.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 77.

## Suspected Area

- `caffmob_draw/library_panel/models_core.py`
- `caffmob_draw/library_panel/categories_core.py`

## Acceptance Criteria

- `null` é tratado como ausente (F-06).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/library_panel/design.md#F-06`
- Código afetado: `caffmob_draw/library_panel/models_core.py`, `caffmob_draw/library_panel/categories_core.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 77 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `library_panel`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
