---
schema_version: 1
id: BUG-20261011-WOPM
display_number: 34
title: "Renomear agregado com furo real deixa furo fantasma na usinagem"
status: open
phase: triaging
severity: high
priority: P1
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: producao
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
  specs: ["_reversa_sdd/aggregates/edge-cases.md#EC-09"]
  affected_code: ["caffmob_draw/aggregates/perforate.py"]
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

# Renomear agregado com furo real deixa furo fantasma na usinagem

## Summary

Renomear um agregado com furo real deixa o `CPM_CUTOUT` antigo no pai, e a usinagem continua exportando esse furo, porque o vínculo é por nome em `perforate.py`.

## Expected Behavior

Renomear o agregado mantém um único recorte, vinculado ao agregado; nenhum furo antigo é exportado.

Spec efetiva: `_reversa_sdd/aggregates/edge-cases.md#EC-09`.

## Actual Behavior

Renomear um agregado com furo real deixa o `CPM_CUTOUT` antigo no pai, e a usinagem continua exportando esse furo, porque o vínculo é por nome em `perforate.py`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 23.

## Suspected Area

- `caffmob_draw/aggregates/perforate.py`

## Acceptance Criteria

- Renomear o agregado mantém um único recorte, vinculado ao agregado; nenhum furo antigo é exportado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/edge-cases.md#EC-09`
- Código afetado: `caffmob_draw/aggregates/perforate.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 23 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: usinagem exporta furo que não existe: erro físico na fabricação.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
