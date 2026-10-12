---
schema_version: 1
id: BUG-20261011-NWRA
display_number: 101
title: "Desligar o addon com a inspeção ativa deixa resíduos"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: plugin
module: inspection
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
  specs: ["_reversa_sdd/inspection/tasks.md#DT-04"]
  affected_code: ["caffmob_draw/inspection/__init__.py", "caffmob_draw/inspection/ops_inspect.py"]
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

# Desligar o addon com a inspeção ativa deixa resíduos

## Summary

Timers, modal handler e o registro no HUD continuam.

## Expected Behavior

`unregister()` remove timers, modal handler e o registro no HUD.

Spec efetiva: `_reversa_sdd/inspection/tasks.md#DT-04`.

## Actual Behavior

Timers, modal handler e o registro no HUD continuam.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 90.

## Suspected Area

- `caffmob_draw/inspection/__init__.py`
- `caffmob_draw/inspection/ops_inspect.py`

## Acceptance Criteria

- `unregister()` remove timers, modal handler e o registro no HUD.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/inspection/tasks.md#DT-04`
- Código afetado: `caffmob_draw/inspection/__init__.py`, `caffmob_draw/inspection/ops_inspect.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 90 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `inspection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
