---
schema_version: 1
id: BUG-20261011-EWKD
display_number: 49
title: "Contenção total em objeto fino pode passar sem detecção (a confirmar)"
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
labels: ["revisao-specs-2026-10", "a-confirmar"]

visibility: normal
security_suspected: false

reproduction:
  classification: unknown
  rate: "não executado (a confirmar com sonda)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/collision/edge-cases.md#EC-01", "_reversa_sdd/collision/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/collision/obb.py"]
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

# Contenção total em objeto fino pode passar sem detecção (a confirmar)

## Summary

Contenção total em objeto fino pode passar sem detecção.

## Expected Behavior

Um objeto inteiramente contido em outro (inclusive fino) é detectado como colisão.

Spec efetiva: `_reversa_sdd/collision/edge-cases.md#EC-01`, `_reversa_sdd/collision/tasks.md#DT-03`.

## Actual Behavior

Contenção total em objeto fino pode passar sem detecção.

## Steps to Reproduce

A confirmar. Pelo relato, rodar uma sonda no Blender 5.2 (`xvfb-run /opt/blender/blender --background --factory-startup --python <sonda>`) que monte o cenário descrito em Actual Behavior.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 38.

## Suspected Area

- `caffmob_draw/collision/obb.py`

## Acceptance Criteria

- Um objeto inteiramente contido em outro (inclusive fino) é detectado como colisão.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/edge-cases.md#EC-01`, `_reversa_sdd/collision/tasks.md#DT-03`
- Código afetado: `caffmob_draw/collision/obb.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 38 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
