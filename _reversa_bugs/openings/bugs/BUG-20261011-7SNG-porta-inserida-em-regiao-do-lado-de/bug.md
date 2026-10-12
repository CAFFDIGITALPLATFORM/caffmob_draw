---
schema_version: 1
id: BUG-20261011-7SNG
display_number: 123
title: "Porta inserida em região do lado de trás abre invertida"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: openings
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
  specs: ["_reversa_sdd/openings/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-22"]
  affected_code: ["caffmob_draw/openings/region.py", "caffmob_draw/openings/region_core.py"]
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

# Porta inserida em região do lado de trás abre invertida

## Summary

Numa região `BACK`, a porta é inserida com a abertura invertida.

## Expected Behavior

A porta abre para o lado da face da região (011 RN-11).

Spec efetiva: `_reversa_sdd/openings/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-22`.

## Actual Behavior

Numa região `BACK`, a porta é inserida com a abertura invertida.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 112.

## Suspected Area

- `caffmob_draw/openings/region.py`
- `caffmob_draw/openings/region_core.py`

## Acceptance Criteria

- A porta abre para o lado da face da região (011 RN-11).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/openings/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-22`
- Código afetado: `caffmob_draw/openings/region.py`, `caffmob_draw/openings/region_core.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 112 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `openings`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
