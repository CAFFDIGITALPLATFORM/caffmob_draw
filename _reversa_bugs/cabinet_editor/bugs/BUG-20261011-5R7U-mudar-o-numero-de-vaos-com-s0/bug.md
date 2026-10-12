---
schema_version: 1
id: BUG-20261011-5R7U
display_number: 62
title: "Mudar o Número de vãos com s0 cortado por divisória comum quebra o layout"
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
module: cabinet_editor
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
  specs: ["_reversa_sdd/cabinet_editor/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/cabinet_editor/bays.py", "caffmob_draw/cabinet_editor/divisions.py"]
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

# Mudar o Número de vãos com s0 cortado por divisória comum quebra o layout

## Summary

Mudar o Número de vãos com `s0` cortado por divisória comum quebra o layout.

## Expected Behavior

A mudança é recusada com mensagem clara.

Spec efetiva: `_reversa_sdd/cabinet_editor/tasks.md#DT-03`.

## Actual Behavior

Mudar o Número de vãos com `s0` cortado por divisória comum quebra o layout.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 51.

## Suspected Area

- `caffmob_draw/cabinet_editor/bays.py`
- `caffmob_draw/cabinet_editor/divisions.py`

## Acceptance Criteria

- A mudança é recusada com mensagem clara.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/tasks.md#DT-03`
- Código afetado: `caffmob_draw/cabinet_editor/bays.py`, `caffmob_draw/cabinet_editor/divisions.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 51 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
