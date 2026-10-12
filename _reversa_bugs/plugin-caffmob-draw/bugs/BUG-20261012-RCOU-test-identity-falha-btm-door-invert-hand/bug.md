---
schema_version: 1
id: BUG-20261012-RCOU
display_number: 139
title: "test_identity falha: btm.door_invert_hand e btm.resize_width fogem do prefixo caffmob"
status: open
phase: triaging
severity: low
priority: P2
created: 2026-10-12
updated: 2026-10-12

origin:
  type: inspection
  external_ref: null

area: plugin
module: ui
feature: unclassified
labels: ["achado-lateral-fix-2026-10", "reproduzido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261006-NO4Q
    type: regression-of
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/ui/requirements.md#R-01", "_reversa_sdd/architecture.md"]
  affected_code: ["caffmob_draw/openings/ops.py", "caffmob_draw/ui/ops_resize.py", "tests/test_identity.py"]
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

# test_identity falha: btm.door_invert_hand e btm.resize_width fogem do prefixo caffmob

## Summary

`tests/test_identity.py::test_operadores_com_prefixo_caffmob` falha no master (já falhava no commit base da rodada, db450a6): `caffmob_draw/openings/ops.py: btm.door_invert_hand` e `caffmob_draw/ui/ops_resize.py: btm.resize_width`. O teste exige o prefixo `caffmob` (BUG-20261006-NO4Q); o `CLAUDE.md` do repositório diz que código novo usa `btm.*` ou `caffmob_draw.*`.

## Expected Behavior

O teste de identidade e a regra do repositório concordam: ou os dois operadores passam para `caffmob.*` (mantendo chamadas, keymaps e menus), ou o teste aceita `btm.*` como prefixo permitido. Decisão do titular.

Spec efetiva: `_reversa_sdd/ui/requirements.md#R-01`, `_reversa_sdd/architecture.md`.

## Actual Behavior

`tests/test_identity.py::test_operadores_com_prefixo_caffmob` falha no master (já falhava no commit base da rodada, db450a6): `caffmob_draw/openings/ops.py: btm.door_invert_hand` e `caffmob_draw/ui/ops_resize.py: btm.resize_width`. O teste exige o prefixo `caffmob` (BUG-20261006-NO4Q); o `CLAUDE.md` do repositório diz que código novo usa `btm.*` ou `caffmob_draw.*`.

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 2.

## Suspected Area

- `caffmob_draw/openings/ops.py`
- `caffmob_draw/ui/ops_resize.py`
- `tests/test_identity.py`

## Acceptance Criteria

- O teste de identidade e a regra do repositório concordam: ou os dois operadores passam para `caffmob.*` (mantendo chamadas, keymaps e menus), ou o teste aceita `btm.*` como prefixo permitido. Decisão do titular.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/ui/requirements.md#R-01`, `_reversa_sdd/architecture.md`
- Código afetado: `caffmob_draw/openings/ops.py`, `caffmob_draw/ui/ops_resize.py`, `tests/test_identity.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- regression-of → BUG-20261006-NO4Q (contexto `plugin-caffmob-draw`, travado), state `proposed`

## Resolution

_Pendente._

## Agent Notes

- Item 2 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade low/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
