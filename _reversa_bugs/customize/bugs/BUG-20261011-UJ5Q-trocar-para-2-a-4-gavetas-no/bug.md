---
schema_version: 1
id: BUG-20261011-UJ5Q
display_number: 25
title: "Trocar para 2 a 4 gavetas no frameless perde a personalização"
status: open
phase: triaging
severity: high
priority: P1
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido", "decisao-do-titular"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "reproduzido na revisão de 2026-10-10"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-04", "_reversa_sdd/customize/tasks.md#DT-02", "_reversa_sdd/questions.md#pergunta-41"]
  affected_code: ["caffmob_draw/customize/adapters/frameless.py", "caffmob_draw/customize/reapply.py"]
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

# Trocar para 2 a 4 gavetas no frameless perde a personalização

## Summary

O vão antigo é apagado e o `btm_custom` vai junto.

## Expected Behavior

Ao trocar para 2 a 4 gavetas, o `btm_custom` do vão antigo é copiado para os vãos novos, exceto o interior.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-04`, `_reversa_sdd/customize/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-41`.

## Actual Behavior

O vão antigo é apagado e o `btm_custom` vai junto.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/customize.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 14.

## Suspected Area

- `caffmob_draw/customize/adapters/frameless.py`
- `caffmob_draw/customize/reapply.py`

## Acceptance Criteria

- Ao trocar para 2 a 4 gavetas, o `btm_custom` do vão antigo é copiado para os vãos novos, exceto o interior.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-04`, `_reversa_sdd/customize/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-41`
- Código afetado: `caffmob_draw/customize/adapters/frameless.py`, `caffmob_draw/customize/reapply.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 14 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: perda silenciosa de dado do usuário (personalização) num fluxo comum, reproduzida.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
