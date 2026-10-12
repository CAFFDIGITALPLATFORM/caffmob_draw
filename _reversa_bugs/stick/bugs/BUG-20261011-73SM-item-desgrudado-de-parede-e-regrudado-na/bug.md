---
schema_version: 1
id: BUG-20261011-73SM
display_number: 54
title: "Item desgrudado de parede é regrudado na carga"
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
labels: ["revisao-specs-2026-10"]

visibility: normal
security_suspected: false

reproduction:
  classification: unknown
  rate: "não executado (confirmado por leitura do código)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-XPD2
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/stick/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/stick/settle.py", "caffmob_draw/stick/migrate.py", "caffmob_draw/stick/link.py"]
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

# Item desgrudado de parede é regrudado na carga

## Summary

Depois de `link.release` de um item cujo `orig_parent` é parede, `settle.run` e `migrate.run` regrudam o item na carga.

## Expected Behavior

Item desgrudado continua solto depois de salvar e recarregar.

Spec efetiva: `_reversa_sdd/stick/tasks.md#DT-03`.

## Actual Behavior

Depois de `link.release` de um item cujo `orig_parent` é parede, `settle.run` e `migrate.run` regrudam o item na carga.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 43.

## Suspected Area

- `caffmob_draw/stick/settle.py`
- `caffmob_draw/stick/migrate.py`
- `caffmob_draw/stick/link.py`

## Acceptance Criteria

- Item desgrudado continua solto depois de salvar e recarregar.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/tasks.md#DT-03`
- Código afetado: `caffmob_draw/stick/settle.py`, `caffmob_draw/stick/migrate.py`, `caffmob_draw/stick/link.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-XPD2 (contexto `stick`), state `proposed`

## Resolution

_Pendente._

## Agent Notes

- Item 43 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
