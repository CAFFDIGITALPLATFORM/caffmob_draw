---
schema_version: 1
id: BUG-20261011-LM42
display_number: 134
title: "Fechar o editor com uma janela só deixa a área sem cabeçalho"
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
  specs: ["_reversa_sdd/canvas2d/edge-cases.md#EC-07", "_reversa_sdd/canvas2d/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-6"]
  affected_code: ["caffmob_draw/canvas2d/window.py"]
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

# Fechar o editor com uma janela só deixa a área sem cabeçalho

## Summary

A área fica como Image Editor.

## Expected Behavior

A área volta a VIEW_3D com cabeçalho e menus.

Spec efetiva: `_reversa_sdd/canvas2d/edge-cases.md#EC-07`, `_reversa_sdd/canvas2d/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-6`.

## Actual Behavior

A área fica como Image Editor.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 123.

## Suspected Area

- `caffmob_draw/canvas2d/window.py`

## Acceptance Criteria

- A área volta a VIEW_3D com cabeçalho e menus.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/canvas2d/edge-cases.md#EC-07`, `_reversa_sdd/canvas2d/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-6`
- Código afetado: `caffmob_draw/canvas2d/window.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 123 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `canvas2d`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
