---
schema_version: 1
id: BUG-20261012-WBKI
display_number: 142
title: "get_user_preferences quebra sem o add-on habilitado e a fumaça de inspeção imprime 17 tracebacks"
status: open
phase: triaging
severity: low
priority: P3
created: 2026-10-12
updated: 2026-10-12

origin:
  type: inspection
  external_ref: null

area: plugin
module: hb_core
feature: unclassified
labels: ["achado-lateral-fix-2026-10", "reproduzido", "spec-gap"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/hb_core/design.md"]
  affected_code: ["caffmob_draw/hb_props.py", "caffmob_draw/product_libraries/frameless/operators/ops_placement.py", "caffmob_draw/product_libraries/face_frame/types_face_frame.py", "tests/blender_inspection_smoke.py"]
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

# get_user_preferences quebra sem o add-on habilitado e a fumaça de inspeção imprime 17 tracebacks

## Summary

`tests/blender_inspection_smoke.py` passa, mas imprime 17 tracebacks iguais: no recálculo do face frame, `_reapply_selection_mode_highlights` → `toggle_cabinet_color` → `hb_props.get_user_preferences` faz `preferences.addons[__package__]` e levanta `KeyError: key "caffmob_draw" not found` quando o pacote é registrado direto (sem estar habilitado nas preferências), como nos testes. O erro é engolido no update da propriedade e esconde falhas reais na saída dos testes.

## Expected Behavior

`get_user_preferences` não levanta quando o add-on não está em `preferences.addons` (devolve os padrões), e a fumaça de inspeção roda sem tracebacks.

O comportamento nunca foi especificado para este caso (`spec-gap`): a pergunta "é bug ou nunca foi especificado?" fica aberta para o fix.

Spec efetiva: `_reversa_sdd/hb_core/design.md`.

## Actual Behavior

`tests/blender_inspection_smoke.py` passa, mas imprime 17 tracebacks iguais: no recálculo do face frame, `_reapply_selection_mode_highlights` → `toggle_cabinet_color` → `hb_props.get_user_preferences` faz `preferences.addons[__package__]` e levanta `KeyError: key "caffmob_draw" not found` quando o pacote é registrado direto (sem estar habilitado nas preferências), como nos testes. O erro é engolido no update da propriedade e esconde falhas reais na saída dos testes.

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 5.

## Suspected Area

- `caffmob_draw/hb_props.py`
- `caffmob_draw/product_libraries/frameless/operators/ops_placement.py`
- `caffmob_draw/product_libraries/face_frame/types_face_frame.py`
- `tests/blender_inspection_smoke.py`

## Acceptance Criteria

- `get_user_preferences` não levanta quando o add-on não está em `preferences.addons` (devolve os padrões), e a fumaça de inspeção roda sem tracebacks.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/hb_core/design.md`
- Código afetado: `caffmob_draw/hb_props.py`, `caffmob_draw/product_libraries/frameless/operators/ops_placement.py`, `caffmob_draw/product_libraries/face_frame/types_face_frame.py`, `tests/blender_inspection_smoke.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

_Pendente._

## Agent Notes

- Item 5 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade low/P3 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
