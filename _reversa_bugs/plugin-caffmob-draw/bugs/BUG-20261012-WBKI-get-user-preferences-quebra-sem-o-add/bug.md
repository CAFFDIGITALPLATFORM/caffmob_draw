---
schema_version: 1
id: BUG-20261012-WBKI
display_number: 142
title: "get_user_preferences quebra sem o add-on habilitado e a fumaça de inspeção imprime 17 tracebacks"
status: resolved
phase: delivering
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

change_risk:
  classification: baixa
  reasons: ["instalação normal não muda (o add-on está em preferences.addons)", "só testes e scripts que registram o pacote direto passam a ter os padrões"]

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
  root_cause:
    state: confirmed
    hypothesis: "get_user_preferences indexava preferences.addons[__package__] direto; com o pacote registrado sem estar habilitado (import + register(), como na fumaça de inspeção), levantava KeyError dentro do update do face frame, que imprimia o traceback 17 vezes."
    causal_path:
      - "hb_props.py Home_Builder_Window_Manager_Props.get_user_preferences"
      - "frameless/operators/ops_placement.py toggle_cabinet_color"
      - "face_frame/types_face_frame.py _reapply_selection_mode_highlights"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/hb_props.py, symbol: get_user_preferences, commit: 8c1687e}
  reproduction_tests: ["tests/blender_bug_WBKI_preferences.py"]
  regression_tests: ["tests/blender_bug_WBKI_preferences.py", "tests/blender_inspection_smoke.py", "tests/blender_smoke.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_WBKI_preferences.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-WBKI-get-user-preferences-quebra-sem-o-add/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/hb_props.py
    purpose: "padrões sem o add-on habilitado"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-WBKI-get-user-preferences-quebra-sem-o-add/fix/CHG-002.diff
  - id: CHG-003
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261012-WBKI-v001.md
    purpose: "padrões quando o add-on não está em preferences.addons"
    diff: _reversa_sdd/addenda/bug-BUG-20261012-WBKI-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
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

- **Lote:** 36 (preferências do add-on) (BUG-20261012-WBKI); plano em `_reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-WBKI-get-user-preferences-quebra-sem-o-add/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** get_user_preferences indexava preferences.addons[__package__] direto; com o pacote registrado sem estar habilitado (import + register(), como na fumaça de inspeção), levantava KeyError dentro do update do face frame, que imprimia o traceback 17 vezes.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-12):** `spec-gap`: o caso sem o add-on habilitado não era especificado; adendo `_reversa_sdd/addenda/bug-BUG-20261012-WBKI-v001.md`.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_WBKI_preferences.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/hb_props.py` | padrões sem o add-on habilitado | `CHG-002.diff` |
| CHG-003 | specification | `_reversa_sdd/addenda/bug-BUG-20261012-WBKI-v001.md` | padrões quando o add-on não está em preferences.addons | `bug-BUG-20261012-WBKI-v001.md` |

**Vermelho (antes da correção):** KeyError: key "caffmob_draw" not found ao ler as preferências e no destaque do armário.

**Verde (depois):** `blender_bug_WBKI_preferences.py` OK; na cópia isolada também `blender_inspection_smoke` (0 tracebacks, eram 17), `blender_smoke`, `blender_identity_smoke` e `blender_002_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_WBKI_preferences.py`. **Regressão:** `tests/blender_bug_WBKI_preferences.py`, `tests/blender_inspection_smoke.py`, `tests/blender_smoke.py`.

## Agent Notes

- Item 5 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade low/P3 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
