---
schema_version: 1
id: BUG-20261011-XPD2
display_number: 52
title: "Vínculo de grudar órfão quando o pai é trocado à mão"
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
module: stick
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
  specs: ["_reversa_sdd/stick/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-36"]
  affected_code: ["caffmob_draw/stick/link.py"]
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

# Vínculo de grudar órfão quando o pai é trocado à mão

## Summary

`is_stuck` continua verdadeiro mesmo com `item.parent != host`.

## Expected Behavior

Trocar o pai à mão desfaz o vínculo (`is_stuck` falso).

Spec efetiva: `_reversa_sdd/stick/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-36`.

## Actual Behavior

`is_stuck` continua verdadeiro mesmo com `item.parent != host`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 41.

## Suspected Area

- `caffmob_draw/stick/link.py`

## Acceptance Criteria

- Trocar o pai à mão desfaz o vínculo (`is_stuck` falso).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-36`
- Código afetado: `caffmob_draw/stick/link.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 41 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
