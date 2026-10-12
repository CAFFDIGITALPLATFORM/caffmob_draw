---
schema_version: 1
id: BUG-20261011-MTPU
display_number: 75
title: "Falha na migração de padrões interrompe o carregamento do arquivo"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: plugin
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
  specs: ["_reversa_sdd/standards/edge-cases.md#EC-14", "caffmob_draw/__init__.py#L99"]
  affected_code: ["caffmob_draw/standards/migration.py", "caffmob_draw/__init__.py"]
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

# Falha na migração de padrões interrompe o carregamento do arquivo

## Summary

`migration.run` só captura `StandardsError`. Outra exceção interrompe o resto do `load_file_post` (`stick.migrate.run`, HUD).

## Expected Behavior

Falha na migração é registrada e o resto do `load_file_post` continua.

Spec efetiva: `_reversa_sdd/standards/edge-cases.md#EC-14`, `caffmob_draw/__init__.py#L99`.

## Actual Behavior

`migration.run` só captura `StandardsError`. Outra exceção interrompe o resto do `load_file_post` (`stick.migrate.run`, HUD).

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 64.

## Suspected Area

- `caffmob_draw/standards/migration.py`
- `caffmob_draw/__init__.py`

## Acceptance Criteria

- Falha na migração é registrada e o resto do `load_file_post` continua.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/standards/edge-cases.md#EC-14`, `caffmob_draw/__init__.py#L99`
- Código afetado: `caffmob_draw/standards/migration.py`, `caffmob_draw/__init__.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 64 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `standards`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
