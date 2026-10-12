---
schema_version: 1
id: BUG-20261011-ORRG
display_number: 83
title: "Grupo homônimo em outra pasta descartado sem aviso"
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
module: legacy
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
  specs: ["_reversa_sdd/legacy/requirements.md#RN-19"]
  affected_code: ["caffmob_draw/legacy/groups.py", "caffmob_draw/product_libraries/frameless/operators/ops_library.py"]
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

# Grupo homônimo em outra pasta descartado sem aviso

## Summary

Em `get_user_library_items`, um grupo com o mesmo nome de arquivo em outra pasta some sem aviso.

## Expected Behavior

O usuário é avisado do grupo descartado (ou ele é listado com a pasta).

Spec efetiva: `_reversa_sdd/legacy/requirements.md#RN-19`.

## Actual Behavior

Em `get_user_library_items`, um grupo com o mesmo nome de arquivo em outra pasta some sem aviso.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 72.

## Suspected Area

- `caffmob_draw/legacy/groups.py`
- `caffmob_draw/product_libraries/frameless/operators/ops_library.py`

## Acceptance Criteria

- O usuário é avisado do grupo descartado (ou ele é listado com a pasta).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/legacy/requirements.md#RN-19`
- Código afetado: `caffmob_draw/legacy/groups.py`, `caffmob_draw/product_libraries/frameless/operators/ops_library.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 72 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `legacy`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
