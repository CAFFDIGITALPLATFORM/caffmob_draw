---
schema_version: 1
id: BUG-20261011-XMUG
display_number: 26
title: "Estilo de gaveta não é editável pelo painel"
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
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-06", "_reversa_sdd/customize/requirements.md#RF-03"]
  affected_code: ["caffmob_draw/customize/panels.py"]
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

# Estilo de gaveta não é editável pelo painel

## Summary

`panels.draw_customize` não passa `kind` ao menu Estilo, embora RF-03 prometa estilo de gaveta.

## Expected Behavior

O painel permite escolher o estilo de gaveta (`drawer_style`), conforme RF-03.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-06`, `_reversa_sdd/customize/requirements.md#RF-03`.

## Actual Behavior

`panels.draw_customize` não passa `kind` ao menu Estilo, embora RF-03 prometa estilo de gaveta.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 15.

## Suspected Area

- `caffmob_draw/customize/panels.py`

## Acceptance Criteria

- O painel permite escolher o estilo de gaveta (`drawer_style`), conforme RF-03.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-06`, `_reversa_sdd/customize/requirements.md#RF-03`
- Código afetado: `caffmob_draw/customize/panels.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 15 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
