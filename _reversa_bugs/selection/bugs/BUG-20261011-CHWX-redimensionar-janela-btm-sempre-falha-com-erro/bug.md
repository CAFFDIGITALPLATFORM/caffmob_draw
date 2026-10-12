---
schema_version: 1
id: BUG-20261011-CHWX
display_number: 125
title: "Redimensionar janela BTM sempre falha com erro em inglês"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: selection
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

visibility: normal
security_suspected: false

reproduction:
  classification: unknown
  rate: "não executado (confirmado por leitura do código)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/selection/edge-cases.md#EC-10", "_reversa_sdd/selection/tasks.md#DT-03", "_reversa_sdd/questions.md#pergunta-21"]
  affected_code: ["caffmob_draw/selection/editing.py"]
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

# Redimensionar janela BTM sempre falha com erro em inglês

## Summary

Ela não tem Geometry Nodes e sai um erro em inglês.

## Expected Behavior

Bloquear em `can_resize`.

Spec efetiva: `_reversa_sdd/selection/edge-cases.md#EC-10`, `_reversa_sdd/selection/tasks.md#DT-03`, `_reversa_sdd/questions.md#pergunta-21`.

## Actual Behavior

Ela não tem Geometry Nodes e sai um erro em inglês.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 114.

## Suspected Area

- `caffmob_draw/selection/editing.py`

## Acceptance Criteria

- Bloquear em `can_resize`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/selection/edge-cases.md#EC-10`, `_reversa_sdd/selection/tasks.md#DT-03`, `_reversa_sdd/questions.md#pergunta-21`
- Código afetado: `caffmob_draw/selection/editing.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 114 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `selection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
