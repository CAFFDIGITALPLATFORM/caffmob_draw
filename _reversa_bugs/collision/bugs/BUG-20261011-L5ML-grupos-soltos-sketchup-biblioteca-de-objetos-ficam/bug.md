---
schema_version: 1
id: BUG-20261011-L5ML
display_number: 45
title: "Grupos soltos (SketchUp, biblioteca de objetos) ficam fora da colisão"
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
module: collision
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
  specs: ["_reversa_sdd/collision/tasks.md#DT-05", "_reversa_sdd/questions.md#pergunta-35"]
  affected_code: ["caffmob_draw/collision/scan.py"]
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

# Grupos soltos (SketchUp, biblioteca de objetos) ficam fora da colisão

## Summary

Raízes de grupo SketchUp e da biblioteca de objetos não são verificadas.

## Expected Behavior

Raízes de grupo SketchUp e da biblioteca de objetos entram na verificação.

Spec efetiva: `_reversa_sdd/collision/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-35`.

## Actual Behavior

Raízes de grupo SketchUp e da biblioteca de objetos não são verificadas.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 34.

## Suspected Area

- `caffmob_draw/collision/scan.py`

## Acceptance Criteria

- Raízes de grupo SketchUp e da biblioteca de objetos entram na verificação.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-35`
- Código afetado: `caffmob_draw/collision/scan.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 34 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
