---
schema_version: 1
id: BUG-20261011-TLCT
display_number: 114
title: "Interromper o modal de criar geometria deixa resíduos"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: geometry_free
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

relationships: []

traceability:
  specs: ["_reversa_sdd/geometry_free/edge-cases.md#EC-01"]
  affected_code: ["caffmob_draw/geometry_free/ops_create.py"]
  root_cause:
    state: confirmed
    hypothesis: "BTM_OT_GeometryCreate não define cancel(): quando o Blender interrompe o modal, a peça provisória e o cabeçalho ficam."
    causal_path:
      - "geometry_free/ops_create.py: sem cancel()"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste com janela (xvfb) vermelho na cópia isolada"
    code_refs:
      - {file: caffmob_draw/geometry_free/ops_create.py, symbol: BTM_OT_GeometryCreate, commit: 83a6863}
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

# Interromper o modal de criar geometria deixa resíduos

## Summary

`GeometryCreate` não tem `cancel()`, então o objeto provisório e o cabeçalho ficam presos.

## Expected Behavior

Ao ser interrompido, o modal remove o provisório e restaura o cabeçalho.

Spec efetiva: `_reversa_sdd/geometry_free/edge-cases.md#EC-01`.

## Actual Behavior

`GeometryCreate` não tem `cancel()`, então o objeto provisório e o cabeçalho ficam presos.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 103.

## Suspected Area

- `caffmob_draw/geometry_free/ops_create.py`

## Acceptance Criteria

- Ao ser interrompido, o modal remove o provisório e restaura o cabeçalho.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/geometry_free/edge-cases.md#EC-01`
- Código afetado: `caffmob_draw/geometry_free/ops_create.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 9 (modais interrompidos) (BUG-20261011-TLCT, BUG-20261011-3T7M, BUG-20261011-JDYP); plano em `_reversa_bugs/geometry_free/bugs/BUG-20261011-TLCT-interromper-o-modal-de-criar-geometria-deixa/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `BTM_OT_GeometryCreate` não definia `cancel()`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: geometry_free EC-01.
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

- Item 103 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `geometry_free`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
