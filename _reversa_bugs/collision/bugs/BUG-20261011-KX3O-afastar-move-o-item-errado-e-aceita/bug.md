---
schema_version: 1
id: BUG-20261011-KX3O
display_number: 43
title: "Afastar move o item errado e aceita resultado desatualizado"
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
  specs: ["_reversa_sdd/collision/tasks.md#DT-02"]
  affected_code: ["caffmob_draw/collision/ops_collision.py"]
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

# Afastar move o item errado e aceita resultado desatualizado

## Summary

`BTM_OT_CollisionPushOut` não move o item selecionado quando ele é um dos dois do par, e aceita resultado desatualizado.

## Expected Behavior

Afastar move o item selecionado do par e recusa resultado marcado como desatualizado.

Spec efetiva: `_reversa_sdd/collision/tasks.md#DT-02`.

## Actual Behavior

`BTM_OT_CollisionPushOut` não move o item selecionado quando ele é um dos dois do par, e aceita resultado desatualizado.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 32.

## Suspected Area

- `caffmob_draw/collision/ops_collision.py`

## Acceptance Criteria

- Afastar move o item selecionado do par e recusa resultado marcado como desatualizado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/tasks.md#DT-02`
- Código afetado: `caffmob_draw/collision/ops_collision.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 32 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
