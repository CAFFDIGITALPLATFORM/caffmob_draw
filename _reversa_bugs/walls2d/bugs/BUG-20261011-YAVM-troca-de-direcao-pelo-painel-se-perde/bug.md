---
schema_version: 1
id: BUG-20261011-YAVM
display_number: 17
title: "Troca de Direção pelo painel se perde num Ctrl+Z imediato"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: walls2d
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["rascunho do editor em memória; só o OK grava", "preserva as mudanças locais da feature 013"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261007-ZZUK
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/edge-cases.md#EC-10", "caffmob_draw/walls2d/props.py#L188-L197"]
  affected_code: ["caffmob_draw/walls2d/props.py", "caffmob_draw/walls2d/history.py"]
  root_cause:
    state: confirmed
    hypothesis: "_side_set troca a Direção sem passar por _guard: sem checkpoint, o Ctrl+Z não tem o passo."
    causal_path:
      - "walls2d/props.py _side_set"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/walls2d/props.py, symbol: _side_set, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_YAVM_wall_editor.py"]
  regression_tests: ["tests/blender_bug_YAVM_wall_editor.py", "tests/test_walls2d_history.py", "tests/blender_bug_ZZUK_undo.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_YAVM_wall_editor.py
    purpose: "reprodução e regressão dos seis defeitos"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/walls2d/props.py
    purpose: "_side_set por _guard; confirm_signature"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/walls2d/model.py
    purpose: "Chain.keep_open"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/walls2d/apply.py
    purpose: "respeita keep_open; valida project_height"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/walls2d/ops_editor.py
    purpose: "_answer_no marca keep_open; barra só no PRESS; OK revalida"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/walls2d/panels.py
    purpose: "ângulos desabilitados com a trava"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Troca de Direção pelo painel se perde num Ctrl+Z imediato

## Summary

A troca de Direção pelo painel se perde num Ctrl+Z imediato. `_side_set` não passa por `_guard`.

## Expected Behavior

A troca de Direção pelo painel entra no histórico do rascunho (passa por `_guard`) e o Ctrl+Z desfaz exatamente essa troca.

Spec efetiva: `_reversa_sdd/walls2d/edge-cases.md#EC-10`, `caffmob_draw/walls2d/props.py#L188-L197`.

## Actual Behavior

A troca de Direção pelo painel se perde num Ctrl+Z imediato. `_side_set` não passa por `_guard`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 6.

## Suspected Area

- `caffmob_draw/walls2d/props.py`
- `caffmob_draw/walls2d/history.py`

## Acceptance Criteria

- A troca de Direção pelo painel entra no histórico do rascunho (passa por `_guard`) e o Ctrl+Z desfaz exatamente essa troca.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/walls2d/edge-cases.md#EC-10`, `caffmob_draw/walls2d/props.py#L188-L197`
- Código afetado: `caffmob_draw/walls2d/props.py`, `caffmob_draw/walls2d/history.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261007-ZZUK (contexto `editor-de-paredes`), state `proposed`

## Resolution

- **Lote:** 11 (editor de paredes) (BUG-20261011-YAVM, BUG-20261011-LT3C, BUG-20261011-624G, BUG-20261011-XMZM, BUG-20261011-PJJU, BUG-20261011-Z2BL); plano em `_reversa_bugs/walls2d/bugs/BUG-20261011-YAVM-troca-de-direcao-pelo-painel-se-perde/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `_side_set` não passava por `_guard` (sem checkpoint).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: walls2d EC-10.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_YAVM_wall_editor.py` | reprodução e regressão dos seis defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/walls2d/props.py` | _side_set por _guard; confirm_signature | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/walls2d/model.py` | Chain.keep_open | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/walls2d/apply.py` | respeita keep_open; valida project_height | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/walls2d/ops_editor.py` | _answer_no marca keep_open; barra só no PRESS; OK revalida | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/walls2d/panels.py` | ângulos desabilitados com a trava | `CHG-006.diff` |

**Vermelho (antes da correção):** `blender_bug_YAVM_wall_editor` com 7 falhas no projeto.

**Verde (depois):** `blender_bug_YAVM_wall_editor: OK`, `test_walls2d_model` e `test_walls2d_history` OK; na cópia isolada também `blender_bug_TLPN_remove_node`, `blender_009_walls_smoke`, `blender_002_smoke`, `blender_bug_MMVI_opening_sync`, `test_i18n_coverage` e, com janela, `blender_002_ui_events`, `blender_bug_ZZUK_undo`, `blender_013_touchpad_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_YAVM_wall_editor.py`. **Regressão:** `tests/blender_bug_YAVM_wall_editor.py`, `tests/test_walls2d_history.py`, `tests/blender_bug_ZZUK_undo.py`.

## Agent Notes

- Item 6 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `walls2d`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
