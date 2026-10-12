---
schema_version: 1
id: BUG-20261011-ZATR
display_number: 78
title: "Import com 'replace' desloca a definição ativa sem aviso"
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
module: standards
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
  specs: ["_reversa_sdd/standards/edge-cases.md#EC-06"]
  affected_code: ["caffmob_draw/standards/io_json.py", "caffmob_draw/standards/api.py"]
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

# Import com 'replace' desloca a definição ativa sem aviso

## Summary

Acontece com a homônima antes da ativa.

## Expected Behavior

A definição ativa continua a mesma depois do import com replace.

Spec efetiva: `_reversa_sdd/standards/edge-cases.md#EC-06`.

## Actual Behavior

Acontece com a homônima antes da ativa.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 67.

## Suspected Area

- `caffmob_draw/standards/io_json.py`
- `caffmob_draw/standards/api.py`

## Acceptance Criteria

- A definição ativa continua a mesma depois do import com replace.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/standards/edge-cases.md#EC-06`
- Código afetado: `caffmob_draw/standards/io_json.py`, `caffmob_draw/standards/api.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 67 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `standards`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
