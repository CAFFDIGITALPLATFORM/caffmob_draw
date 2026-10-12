---
schema_version: 1
id: BUG-20261011-S6I6
display_number: 135
title: "View2D sem guarda contra escala zero"
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
module: canvas2d
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
  specs: ["_reversa_sdd/canvas2d/requirements.md#RN-04", "_reversa_sdd/canvas2d/requirements.md#RN-05"]
  affected_code: ["caffmob_draw/canvas2d/view.py"]
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

# View2D sem guarda contra escala zero

## Summary

Um `rect` com lado 0 em `fit` dá `ZeroDivisionError`.

## Expected Behavior

`fit` aplica o mesmo piso de escala de `zoom` (RN-04, RN-05).

Spec efetiva: `_reversa_sdd/canvas2d/requirements.md#RN-04`, `_reversa_sdd/canvas2d/requirements.md#RN-05`.

## Actual Behavior

Um `rect` com lado 0 em `fit` dá `ZeroDivisionError`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 124.

## Suspected Area

- `caffmob_draw/canvas2d/view.py`

## Acceptance Criteria

- `fit` aplica o mesmo piso de escala de `zoom` (RN-04, RN-05).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/canvas2d/requirements.md#RN-04`, `_reversa_sdd/canvas2d/requirements.md#RN-05`
- Código afetado: `caffmob_draw/canvas2d/view.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 124 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `canvas2d`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
