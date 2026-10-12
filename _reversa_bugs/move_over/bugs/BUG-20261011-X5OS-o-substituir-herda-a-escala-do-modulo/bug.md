---
schema_version: 1
id: BUG-20261011-X5OS
display_number: 129
title: "O Substituir herda a escala do módulo antigo"
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
module: move_over
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
  specs: ["_reversa_sdd/move_over/tasks.md#DT-05", "_reversa_sdd/questions.md#pergunta-19"]
  affected_code: ["caffmob_draw/move_over/ops_substitute.py"]
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

# O Substituir herda a escala do módulo antigo

## Summary

O Substituir herda a escala do módulo antigo.

## Expected Behavior

O novo módulo recebe posição e rotação de A, sem a escala.

Spec efetiva: `_reversa_sdd/move_over/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-19`.

## Actual Behavior

O Substituir herda a escala do módulo antigo.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 118.

## Suspected Area

- `caffmob_draw/move_over/ops_substitute.py`

## Acceptance Criteria

- O novo módulo recebe posição e rotação de A, sem a escala.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/move_over/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-19`
- Código afetado: `caffmob_draw/move_over/ops_substitute.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 118 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `move_over`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
