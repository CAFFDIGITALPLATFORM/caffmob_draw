---
schema_version: 1
id: BUG-20261011-PON4
display_number: 38
title: "Caixa local errada quando o pai é Empty ou grupo"
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
module: aggregates
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
  specs: ["_reversa_sdd/aggregates/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/aggregates/apply.py"]
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

# Caixa local errada quando o pai é Empty ou grupo

## Summary

`apply.local_box` usa o `bound_box` do Empty em vez da união das malhas. Confirmar no 5.2.

## Expected Behavior

Com pai Empty/grupo, a caixa é a união das malhas descendentes.

Spec efetiva: `_reversa_sdd/aggregates/tasks.md#DT-03`.

## Actual Behavior

`apply.local_box` usa o `bound_box` do Empty em vez da união das malhas. Confirmar no 5.2.

## Steps to Reproduce

A confirmar. Pelo relato, rodar uma sonda no Blender 5.2 (`xvfb-run /opt/blender/blender --background --factory-startup --python <sonda>`) que monte o cenário descrito em Actual Behavior.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 27.

## Suspected Area

- `caffmob_draw/aggregates/apply.py`

## Acceptance Criteria

- Com pai Empty/grupo, a caixa é a união das malhas descendentes.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/tasks.md#DT-03`
- Código afetado: `caffmob_draw/aggregates/apply.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 27 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
