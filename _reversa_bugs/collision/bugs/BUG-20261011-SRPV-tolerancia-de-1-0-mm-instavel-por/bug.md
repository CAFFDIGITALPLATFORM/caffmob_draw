---
schema_version: 1
id: BUG-20261011-SRPV
display_number: 42
title: "Tolerância de 1,0 mm instável por arredondamento de float"
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
module: collision
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
  specs: ["_reversa_sdd/collision/requirements.md#RN-01", "_reversa_sdd/collision/requirements.md#CA-04", "_reversa_sdd/collision/edge-cases.md#EC-11", "_reversa_sdd/collision/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/collision/rules.py", "caffmob_draw/collision/obb.py"]
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

# Tolerância de 1,0 mm instável por arredondamento de float

## Summary

Com a borda em 0,999 m conta, com a borda em 0,599 m não conta. Correção: `depth <= TOLERANCE + 1e-9`.

## Expected Behavior

Sobreposição de até 1,0 mm nunca conta, independente da posição (RN-01, CA-04).

Spec efetiva: `_reversa_sdd/collision/requirements.md#RN-01`, `_reversa_sdd/collision/requirements.md#CA-04`, `_reversa_sdd/collision/edge-cases.md#EC-11`, `_reversa_sdd/collision/tasks.md#DT-01`.

## Actual Behavior

Com a borda em 0,999 m conta, com a borda em 0,599 m não conta. Correção: `depth <= TOLERANCE + 1e-9`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 31.

## Suspected Area

- `caffmob_draw/collision/rules.py`
- `caffmob_draw/collision/obb.py`

## Acceptance Criteria

- Sobreposição de até 1,0 mm nunca conta, independente da posição (RN-01, CA-04).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/requirements.md#RN-01`, `_reversa_sdd/collision/requirements.md#CA-04`, `_reversa_sdd/collision/edge-cases.md#EC-11`, `_reversa_sdd/collision/tasks.md#DT-01`
- Código afetado: `caffmob_draw/collision/rules.py`, `caffmob_draw/collision/obb.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 31 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
