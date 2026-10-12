---
schema_version: 1
id: BUG-20261011-53DV
display_number: 48
title: "Colisão falsa entre folha e caixa da porta/janela ou parede (a confirmar)"
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

relationships:
  - bug: BUG-20261011-VPY5
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/collision/edge-cases.md#EC-22", "_reversa_sdd/collision/tasks.md#DT-90"]
  affected_code: ["caffmob_draw/collision/rules.py", "caffmob_draw/aggregates/collision.py"]
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

# Colisão falsa entre folha e caixa da porta/janela ou parede (a confirmar)

## Summary

Pela leitura do código, folha aberta × caixa da porta/janela e folha × parede não são excluídas da colisão. Rodar a sonda com porta real a 90° e janela instalada.

## Expected Behavior

Folha aberta não colide com a própria caixa da porta/janela nem com a parede que a hospeda.

Spec efetiva: `_reversa_sdd/collision/edge-cases.md#EC-22`, `_reversa_sdd/collision/tasks.md#DT-90`.

## Actual Behavior

Pela leitura do código, folha aberta × caixa da porta/janela e folha × parede não são excluídas da colisão. Rodar a sonda com porta real a 90° e janela instalada.

## Steps to Reproduce

A confirmar. Pelo relato, rodar uma sonda no Blender 5.2 (`xvfb-run /opt/blender/blender --background --factory-startup --python <sonda>`) que monte o cenário descrito em Actual Behavior.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 37.

## Suspected Area

- `caffmob_draw/collision/rules.py`
- `caffmob_draw/aggregates/collision.py`

## Acceptance Criteria

- Folha aberta não colide com a própria caixa da porta/janela nem com a parede que a hospeda.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/edge-cases.md#EC-22`, `_reversa_sdd/collision/tasks.md#DT-90`
- Código afetado: `caffmob_draw/collision/rules.py`, `caffmob_draw/aggregates/collision.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-VPY5 (contexto `aggregates`), state `proposed`

## Resolution

_Pendente._

## Agent Notes

- Item 37 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
