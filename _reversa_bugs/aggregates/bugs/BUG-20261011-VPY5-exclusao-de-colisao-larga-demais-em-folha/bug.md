---
schema_version: 1
id: BUG-20261011-VPY5
display_number: 36
title: "Exclusão de colisão larga demais em folha sem módulo"
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
  specs: ["_reversa_sdd/aggregates/tasks.md#DT-04"]
  affected_code: ["caffmob_draw/aggregates/collision.py"]
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

# Exclusão de colisão larga demais em folha sem módulo

## Summary

`collision._excluded` exclui a subárvore inteira do pai quando `module_root_of(pai)` é None.

## Expected Behavior

Sem módulo, a exclusão fica restrita à folha e à sua esquadria, não à subárvore inteira do pai.

Spec efetiva: `_reversa_sdd/aggregates/tasks.md#DT-04`.

## Actual Behavior

`collision._excluded` exclui a subárvore inteira do pai quando `module_root_of(pai)` é None.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 25.

## Suspected Area

- `caffmob_draw/aggregates/collision.py`

## Acceptance Criteria

- Sem módulo, a exclusão fica restrita à folha e à sua esquadria, não à subárvore inteira do pai.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/tasks.md#DT-04`
- Código afetado: `caffmob_draw/aggregates/collision.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 25 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
