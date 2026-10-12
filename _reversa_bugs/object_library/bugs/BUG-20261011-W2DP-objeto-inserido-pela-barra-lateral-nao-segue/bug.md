---
schema_version: 1
id: BUG-20261011-W2DP
display_number: 89
title: "Objeto inserido pela barra lateral não segue o mouse"
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
module: object_library
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "reproduzido na revisão de 2026-10-10"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/object_library/requirements.md#RN-14", "_reversa_sdd/object_library/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/object_library/ops.py"]
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

# Objeto inserido pela barra lateral não segue o mouse

## Summary

O modal recebe a região UI sem `RegionView3D`. Contradiz RN-14.

## Expected Behavior

RN-14: o objeto segue o mouse no viewport também quando inserido pela barra lateral.

Spec efetiva: `_reversa_sdd/object_library/requirements.md#RN-14`, `_reversa_sdd/object_library/tasks.md#DT-01`.

## Actual Behavior

O modal recebe a região UI sem `RegionView3D`. Contradiz RN-14.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/object_library.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 78.

## Suspected Area

- `caffmob_draw/object_library/ops.py`

## Acceptance Criteria

- RN-14: o objeto segue o mouse no viewport também quando inserido pela barra lateral.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/object_library/requirements.md#RN-14`, `_reversa_sdd/object_library/tasks.md#DT-01`
- Código afetado: `caffmob_draw/object_library/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 78 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `object_library`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
