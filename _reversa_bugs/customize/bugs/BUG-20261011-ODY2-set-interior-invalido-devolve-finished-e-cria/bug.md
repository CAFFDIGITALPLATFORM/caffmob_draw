---
schema_version: 1
id: BUG-20261011-ODY2
display_number: 30
title: "set_interior inválido devolve FINISHED e cria passo de desfazer vazio"
status: open
phase: triaging
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: customize
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
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-20"]
  affected_code: ["caffmob_draw/customize/ops_customize.py"]
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

# set_interior inválido devolve FINISHED e cria passo de desfazer vazio

## Summary

`set_interior` inválido devolve `FINISHED`. Fica um passo de desfazer vazio.

## Expected Behavior

`set_interior` com entrada inválida devolve `CANCELLED`, sem passo de desfazer.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-20`.

## Actual Behavior

`set_interior` inválido devolve `FINISHED`. Fica um passo de desfazer vazio.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 19.

## Suspected Area

- `caffmob_draw/customize/ops_customize.py`

## Acceptance Criteria

- `set_interior` com entrada inválida devolve `CANCELLED`, sem passo de desfazer.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-20`
- Código afetado: `caffmob_draw/customize/ops_customize.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 19 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
