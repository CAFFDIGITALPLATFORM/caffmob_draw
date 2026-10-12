---
schema_version: 1
id: BUG-20261011-HLV6
display_number: 69
title: "apply_state recria internos, extras e deslizantes sem mudança"
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
  specs: ["_reversa_sdd/cabinet_editor/tasks.md#DT-09"]
  affected_code: ["caffmob_draw/cabinet_editor/bridge.py"]
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

# apply_state recria internos, extras e deslizantes sem mudança

## Summary

Internos, extras e deslizantes são recriados mesmo sem mudança.

## Expected Behavior

Só o que mudou é recriado.

Spec efetiva: `_reversa_sdd/cabinet_editor/tasks.md#DT-09`.

## Actual Behavior

Internos, extras e deslizantes são recriados mesmo sem mudança.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 58.

## Suspected Area

- `caffmob_draw/cabinet_editor/bridge.py`

## Acceptance Criteria

- Só o que mudou é recriado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/tasks.md#DT-09`
- Código afetado: `caffmob_draw/cabinet_editor/bridge.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 58 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
