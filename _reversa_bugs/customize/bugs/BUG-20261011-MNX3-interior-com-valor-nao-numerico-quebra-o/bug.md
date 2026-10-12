---
schema_version: 1
id: BUG-20261011-MNX3
display_number: 27
title: "Interior com valor não numérico quebra o módulo"
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
module: customize
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
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-09"]
  affected_code: ["caffmob_draw/customize/spec.py", "caffmob_draw/customize/reapply.py", "caffmob_draw/customize/panels.py"]
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

# Interior com valor não numérico quebra o módulo

## Summary

`interior_from_json` converte os tipos fora do `try`, então `read`, `reapply` e o painel do módulo quebram.

## Expected Behavior

Valor não numérico em `btm_custom.interior` é tratado como inválido (ignorado com aviso), sem quebrar `read`, `reapply` nem o painel.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-09`.

## Actual Behavior

`interior_from_json` converte os tipos fora do `try`, então `read`, `reapply` e o painel do módulo quebram.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 16.

## Suspected Area

- `caffmob_draw/customize/spec.py`
- `caffmob_draw/customize/reapply.py`
- `caffmob_draw/customize/panels.py`

## Acceptance Criteria

- Valor não numérico em `btm_custom.interior` é tratado como inválido (ignorado com aviso), sem quebrar `read`, `reapply` nem o painel.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-09`
- Código afetado: `caffmob_draw/customize/spec.py`, `caffmob_draw/customize/reapply.py`, `caffmob_draw/customize/panels.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 16 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
