---
schema_version: 1
id: BUG-20261011-3UWR
display_number: 85
title: "':' no nome da categoria grava o módulo na pasta errada"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: library_panel
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "reproduzido na revisão de 2026-10-10"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/library_panel/edge-cases.md#EC-04", "_reversa_sdd/library_panel/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/library_panel/categories_core.py", "caffmob_draw/library_panel/ops_categories.py"]
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

# ':' no nome da categoria grava o módulo na pasta errada

## Summary

"Pia: Lavabo" grava em "Pia_ Lavabo/", o módulo não aparece na categoria e nasce uma categoria fantasma.

## Expected Behavior

Recusar os caracteres trocados por `file_stem` e nome terminado em ".".

Spec efetiva: `_reversa_sdd/library_panel/edge-cases.md#EC-04`, `_reversa_sdd/library_panel/tasks.md#DT-01`.

## Actual Behavior

"Pia: Lavabo" grava em "Pia_ Lavabo/", o módulo não aparece na categoria e nasce uma categoria fantasma.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/library_panel.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 74.

## Suspected Area

- `caffmob_draw/library_panel/categories_core.py`
- `caffmob_draw/library_panel/ops_categories.py`

## Acceptance Criteria

- Recusar os caracteres trocados por `file_stem` e nome terminado em ".".
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/library_panel/edge-cases.md#EC-04`, `_reversa_sdd/library_panel/tasks.md#DT-01`
- Código afetado: `caffmob_draw/library_panel/categories_core.py`, `caffmob_draw/library_panel/ops_categories.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 74 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `library_panel`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
