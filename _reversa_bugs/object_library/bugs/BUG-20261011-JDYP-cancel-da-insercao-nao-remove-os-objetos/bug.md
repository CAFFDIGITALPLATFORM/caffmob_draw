---
schema_version: 1
id: BUG-20261011-JDYP
display_number: 94
title: "cancel() da inserção não remove os objetos carregados"
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: object_library
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["só o caminho de interrupção dos modais (Esc e clique não mudam)", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-TLCT
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/object_library/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/object_library/ops.py"]
  root_cause:
    state: confirmed
    hypothesis: "O cancel() da inserção da biblioteca só limpa o cabeçalho; os objetos carregados (_loaded) só saem no Esc."
    causal_path:
      - "object_library/ops.py BTM_OT_ObjectInsert.cancel: só _end"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste com janela (xvfb) vermelho na cópia isolada"
    code_refs:
      - {file: caffmob_draw/object_library/ops.py, symbol: BTM_OT_ObjectInsert.cancel, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_TLCT_modal_cancel.py"]
  regression_tests: ["tests/blender_bug_TLCT_modal_cancel.py", "tests/blender_003_move_over_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_TLCT_modal_cancel.py
    purpose: "reprodução e regressão com janela"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/geometry_free/ops_create.py
    purpose: "cancel() e _cancel protegido"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/move_over/ops_move_on_wall.py
    purpose: "cancel() devolve a posição"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/move_over/insertion_plane.py
    purpose: "cancel() limpa status e cursor"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/object_library/ops.py
    purpose: "_discard comum ao Esc e ao cancel()"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/CHG-005.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# cancel() da inserção não remove os objetos carregados

## Summary

`cancel()` não remove os objetos de `_loaded`. Ao contrário do Esc.

## Expected Behavior

`cancel()` remove os objetos de `_loaded`, como o Esc.

Spec efetiva: `_reversa_sdd/object_library/tasks.md#DT-03`.

## Actual Behavior

`cancel()` não remove os objetos de `_loaded`. Ao contrário do Esc.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 83.

## Suspected Area

- `caffmob_draw/object_library/ops.py`

## Acceptance Criteria

- `cancel()` remove os objetos de `_loaded`, como o Esc.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/object_library/tasks.md#DT-03`
- Código afetado: `caffmob_draw/object_library/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-TLCT (contexto `geometry_free`), state `proposed`

## Resolution

- **Lote:** 9 (modais interrompidos) (BUG-20261011-TLCT, BUG-20261011-3T7M, BUG-20261011-JDYP); plano em `_reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** o `cancel()` da inserção não descartava `_loaded`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: object_library DT-03.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_TLCT_modal_cancel.py` | reprodução e regressão com janela | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/geometry_free/ops_create.py` | cancel() e _cancel protegido | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/move_over/ops_move_on_wall.py` | cancel() devolve a posição | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/move_over/insertion_plane.py` | cancel() limpa status e cursor | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/object_library/ops.py` | _discard comum ao Esc e ao cancel() | `CHG-005.diff` |

**Vermelho (antes da correção):** `blender_bug_TLCT_modal_cancel` com 3 falhas no projeto (peça provisória, objetos do vaso, módulo fora do lugar).

**Verde (depois):** `blender_bug_TLCT_modal_cancel: OK`, `blender_003_move_over_smoke: OK`; na cópia isolada também `blender_002_smoke`, `blender_009_library_smoke`, `blender_bug_skp_mover_sobre`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_TLCT_modal_cancel.py`. **Regressão:** `tests/blender_bug_TLCT_modal_cancel.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 83 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `object_library`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
