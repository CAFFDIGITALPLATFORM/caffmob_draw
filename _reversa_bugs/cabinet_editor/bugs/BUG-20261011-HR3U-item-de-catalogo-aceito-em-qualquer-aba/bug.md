---
schema_version: 1
id: BUG-20261011-HR3U
display_number: 66
title: "Item de catálogo aceito em qualquer aba do editor de armário"
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
module: cabinet_editor
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
  specs: ["_reversa_sdd/cabinet_editor/edge-cases.md#EC-05"]
  affected_code: ["caffmob_draw/cabinet_editor/validate.py", "caffmob_draw/cabinet_editor/catalog.py"]
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

# Item de catálogo aceito em qualquer aba do editor de armário

## Summary

`insert_reason` não confere a aba: Internos com `SLIDE_*` cria painel sem recorte, e Deslizantes com `OVEN` cria folhas com esse "estilo".

## Expected Behavior

`insert_reason` recusa item de catálogo de outra aba.

Spec efetiva: `_reversa_sdd/cabinet_editor/edge-cases.md#EC-05`.

## Actual Behavior

`insert_reason` não confere a aba: Internos com `SLIDE_*` cria painel sem recorte, e Deslizantes com `OVEN` cria folhas com esse "estilo".

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 55.

## Suspected Area

- `caffmob_draw/cabinet_editor/validate.py`
- `caffmob_draw/cabinet_editor/catalog.py`

## Acceptance Criteria

- `insert_reason` recusa item de catálogo de outra aba.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/edge-cases.md#EC-05`
- Código afetado: `caffmob_draw/cabinet_editor/validate.py`, `caffmob_draw/cabinet_editor/catalog.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 55 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
