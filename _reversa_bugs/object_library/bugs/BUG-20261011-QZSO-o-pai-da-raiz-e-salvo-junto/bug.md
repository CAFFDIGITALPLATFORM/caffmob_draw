---
schema_version: 1
id: BUG-20261011-QZSO
display_number: 91
title: "O pai da raiz é salvo junto no .blend do item"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: object_library
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
  specs: ["_reversa_sdd/object_library/edge-cases.md#EC-08"]
  affected_code: ["caffmob_draw/object_library/item_io.py"]
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

# O pai da raiz é salvo junto no .blend do item

## Summary

O pai vai para o `.blend` do item.

## Expected Behavior

Só a raiz e seus descendentes vão para o `.blend`.

Spec efetiva: `_reversa_sdd/object_library/edge-cases.md#EC-08`.

## Actual Behavior

O pai vai para o `.blend` do item.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 80.

## Suspected Area

- `caffmob_draw/object_library/item_io.py`

## Acceptance Criteria

- Só a raiz e seus descendentes vão para o `.blend`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/object_library/edge-cases.md#EC-08`
- Código afetado: `caffmob_draw/object_library/item_io.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 80 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `object_library`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
