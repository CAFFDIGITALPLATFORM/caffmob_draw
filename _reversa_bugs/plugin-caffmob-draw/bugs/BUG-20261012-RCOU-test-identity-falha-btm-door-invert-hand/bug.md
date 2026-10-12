---
schema_version: 1
id: BUG-20261012-RCOU
display_number: 139
title: "test_identity falha: btm.door_invert_hand e btm.resize_width fogem do prefixo caffmob"
status: resolved
phase: delivering
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

change_risk:
  classification: baixa
  reasons: ["nome interno do operador muda; atalho do add-on é recriado no register", "scripts do usuário que chamem bpy.ops.btm.* precisam do nome novo"]

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
  root_cause:
    state: confirmed
    hypothesis: "Dois operadores novos (inversão da mão da porta e Redimensionar) entraram com bl_idname btm.*, seguindo a regra do CLAUDE.md, mas a identidade do plugin (NO4Q, ui R-01) exige o prefixo caffmob em todo operador, e o test_identity cobra isso."
    causal_path:
      - "openings/ops.py BTM_OT_DoorInvertHand.bl_idname"
      - "ui/ops_resize.py BTM_OT_ResizeWidth.bl_idname"
      - "tests/test_identity.py test_operadores_com_prefixo_caffmob"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/openings/ops.py, symbol: BTM_OT_DoorInvertHand, commit: b927946}
      - {file: caffmob_draw/ui/ops_resize.py, symbol: BTM_OT_ResizeWidth, commit: b927946}
  reproduction_tests: ["tests/test_identity.py", "tests/blender_toast_resize_invert.py"]
  regression_tests: ["tests/test_identity.py", "tests/blender_toast_resize_invert.py", "tests/blender_toast_resize_invert.py", "tests/blender_identity_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_toast_resize_invert.py
    purpose: "atalho I e Redimensionar pelos nomes novos"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-RCOU-test-identity-falha-btm-door-invert-hand/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/openings/ops.py
    purpose: "caffmob.door_invert_hand"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-RCOU-test-identity-falha-btm-door-invert-hand/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/ui/ops_resize.py
    purpose: "caffmob.resize_width"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-RCOU-test-identity-falha-btm-door-invert-hand/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/ui/sidebar_vocab.py
    purpose: "barra lateral com o nome novo"
    diff: _reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-RCOU-test-identity-falha-btm-door-invert-hand/fix/CHG-004.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
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

- **Lote:** 35 (prefixo dos operadores) (BUG-20261012-RCOU); plano em `_reversa_bugs/plugin-caffmob-draw/bugs/BUG-20261012-RCOU-test-identity-falha-btm-door-invert-hand/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** Dois operadores novos (inversão da mão da porta e Redimensionar) entraram com bl_idname btm.*, seguindo a regra do CLAUDE.md, mas a identidade do plugin (NO4Q, ui R-01) exige o prefixo caffmob em todo operador, e o test_identity cobra isso.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-12):** `spec-correta`: ui R-01 e a identidade de BUG-20261006-NO4Q (todo operador com prefixo caffmob); decisão do titular em 2026-10-12: renomear para caffmob.*.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_toast_resize_invert.py` | atalho I e Redimensionar pelos nomes novos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/openings/ops.py` | caffmob.door_invert_hand | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/ui/ops_resize.py` | caffmob.resize_width | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/ui/sidebar_vocab.py` | barra lateral com o nome novo | `CHG-004.diff` |

**Vermelho (antes da correção):** test_identity listou btm.door_invert_hand e btm.resize_width; com os nomes novos no teste, o atalho I não existia.

**Verde (depois):** `test_identity.py` OK, `blender_toast_resize_invert.py` OK; na cópia isolada também `blender_smoke`, `blender_identity_smoke` e `test_i18n_coverage`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/test_identity.py`, `tests/blender_toast_resize_invert.py`. **Regressão:** `tests/test_identity.py`, `tests/blender_toast_resize_invert.py`, `tests/blender_toast_resize_invert.py`, `tests/blender_identity_smoke.py`.

## Agent Notes

- Item 2 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade low/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
