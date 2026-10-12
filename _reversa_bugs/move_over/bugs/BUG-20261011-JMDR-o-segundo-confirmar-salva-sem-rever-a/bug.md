---
schema_version: 1
id: BUG-20261011-JMDR
display_number: 127
title: "O segundo Confirmar salva sem rever a sobreposição"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: move_over
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["janela Mover Sobre: teclado e mensagem", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-XMZM
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/move_over/tasks.md#DT-04", "_reversa_sdd/questions.md#pergunta-18"]
  affected_code: ["caffmob_draw/move_over/ops_dialog.py"]
  root_cause:
    state: confirmed
    hypothesis: "O passo pelo teclado move A sem zerar warned."
    causal_path:
      - "move_over/ops_dialog.py modal: ARROWS"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/move_over/ops_dialog.py, symbol: BTM_OT_MoveOverDialog.modal, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_CKVJ_move_over_dialog.py"]
  regression_tests: ["tests/blender_bug_CKVJ_move_over_dialog.py", "tests/blender_003_move_over_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_CKVJ_move_over_dialog.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-CKVJ-tab-na-janela-de-mover-sobre-vai/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/move_over/ops_dialog.py
    purpose: "Tab, passo e rotação"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-CKVJ-tab-na-janela-de-mover-sobre-vai/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/data/translations/move_over.json
    purpose: "mensagem da rotação"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-CKVJ-tab-na-janela-de-mover-sobre-vai/fix/CHG-003.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# O segundo Confirmar salva sem rever a sobreposição

## Summary

Setas e Page Up/Down depois do aviso não zeram `warned`.

## Expected Behavior

Mover A com setas ou Page Up/Down zera o aviso.

Spec efetiva: `_reversa_sdd/move_over/tasks.md#DT-04`, `_reversa_sdd/questions.md#pergunta-18`.

## Actual Behavior

Setas e Page Up/Down depois do aviso não zeram `warned`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 116.

## Suspected Area

- `caffmob_draw/move_over/ops_dialog.py`

## Acceptance Criteria

- Mover A com setas ou Page Up/Down zera o aviso.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/move_over/tasks.md#DT-04`, `_reversa_sdd/questions.md#pergunta-18`
- Código afetado: `caffmob_draw/move_over/ops_dialog.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-XMZM (contexto `walls2d`), state `proposed`

## Resolution

- **Lote:** 16 (janela Mover Sobre) (BUG-20261011-CKVJ, BUG-20261011-JMDR, BUG-20261011-CNTL); plano em `_reversa_bugs/move_over/bugs/BUG-20261011-CKVJ-tab-na-janela-de-mover-sobre-vai/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** o passo pelo teclado não zerava `warned`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 18 e move_over DT-04.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_CKVJ_move_over_dialog.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/move_over/ops_dialog.py` | Tab, passo e rotação | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/data/translations/move_over.json` | mensagem da rotação | `CHG-003.diff` |

**Vermelho (antes da correção):** `blender_bug_CKVJ_move_over_dialog` com 4 falhas no projeto.

**Verde (depois):** `blender_bug_CKVJ_move_over_dialog: OK`, `test_i18n_coverage` OK; na cópia isolada também `test_move_over_align`, `test_reposition`, `blender_003_move_over_smoke`, `blender_bug_skp_mover_sobre`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_CKVJ_move_over_dialog.py`. **Regressão:** `tests/blender_bug_CKVJ_move_over_dialog.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 116 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `move_over`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
