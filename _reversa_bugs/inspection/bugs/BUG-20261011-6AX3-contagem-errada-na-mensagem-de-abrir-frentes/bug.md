---
schema_version: 1
id: BUG-20261011-6AX3
display_number: 104
title: "Contagem errada na mensagem de abrir frentes"
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
  specs: ["_reversa_sdd/inspection/edge-cases.md#EC-14"]
  affected_code: ["caffmob_draw/inspection/fronts.py"]
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

# Contagem errada na mensagem de abrir frentes

## Summary

`fronts_set_open` conta também as frentes puladas.

## Expected Behavior

A mensagem conta só as frentes alteradas.

Spec efetiva: `_reversa_sdd/inspection/edge-cases.md#EC-14`.

## Actual Behavior

`fronts_set_open` conta também as frentes puladas.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 93.

## Suspected Area

- `caffmob_draw/inspection/fronts.py`

## Acceptance Criteria

- A mensagem conta só as frentes alteradas.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/inspection/edge-cases.md#EC-14`
- Código afetado: `caffmob_draw/inspection/fronts.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 93 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `inspection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
