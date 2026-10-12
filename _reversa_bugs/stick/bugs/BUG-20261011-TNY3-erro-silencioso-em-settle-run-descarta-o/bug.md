---
schema_version: 1
id: BUG-20261011-TNY3
display_number: 57
title: "Erro silencioso em settle.run descarta o lote pendente"
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
module: stick
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
  specs: ["_reversa_sdd/stick/edge-cases.md#EC-15"]
  affected_code: ["caffmob_draw/stick/settle.py"]
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

# Erro silencioso em settle.run descarta o lote pendente

## Summary

Uma exceção que não seja `ReferenceError` descarta o lote `_pending` e encerra o temporizador sem log.

## Expected Behavior

Exceção inesperada é registrada em log e não descarta silenciosamente os itens pendentes.

Spec efetiva: `_reversa_sdd/stick/edge-cases.md#EC-15`.

## Actual Behavior

Uma exceção que não seja `ReferenceError` descarta o lote `_pending` e encerra o temporizador sem log.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 46.

## Suspected Area

- `caffmob_draw/stick/settle.py`

## Acceptance Criteria

- Exceção inesperada é registrada em log e não descarta silenciosamente os itens pendentes.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/edge-cases.md#EC-15`
- Código afetado: `caffmob_draw/stick/settle.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 46 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
