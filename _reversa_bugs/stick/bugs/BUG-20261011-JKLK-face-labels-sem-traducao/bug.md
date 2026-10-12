---
schema_version: 1
id: BUG-20261011-JKLK
display_number: 58
title: "FACE_LABELS sem tradução"
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
module: stick
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["catálogo de traduções e uma mensagem", "sem mudança de dado"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-35HE
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/stick/tasks.md#T-15"]
  affected_code: ["caffmob_draw/aggregates/limits.py"]
  root_cause:
    state: confirmed
    hypothesis: "Os 6 rótulos de FACE_LABELS não têm entrada de catálogo: enum e tr() não acham tradução."
    causal_path:
      - "aggregates/limits.py FACE_LABELS"
      - "data/translations: sem entradas"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2, en_US)"
    code_refs:
      - {file: caffmob_draw/aggregates/limits.py, symbol: FACE_LABELS, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_35HE_i18n.py"]
  regression_tests: ["tests/blender_bug_35HE_i18n.py", "tests/test_i18n_coverage.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_35HE_i18n.py
    purpose: "reprodução e regressão (en_US)"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/aggregates/limits.py
    purpose: "FACE_LABELS com N_"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/aggregates/ops_aggregate.py
    purpose: "rótulo da face por tr no aviso"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/geometry_free/mesh.py
    purpose: "nomes das chapas com N_"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/cabinet_editor/scene_slides.py
    purpose: "avisos com código"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/cabinet_editor/bridge.py
    purpose: "mensagens dos deslizantes"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/data/translations/aggregates.json
    purpose: "6 rótulos das faces"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/data/translations/geometry_free.json
    purpose: "Trás"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-008.diff
  - id: CHG-009
    kind: code
    artifact: caffmob_draw/data/translations/cabinet_editor.json
    purpose: "Sem vão interno para os deslizantes"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/CHG-009.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# FACE_LABELS sem tradução

## Summary

Os 6 rótulos de `aggregates/limits.FACE_LABELS` não têm entrada de catálogo e aparecem em português no en_US.

## Expected Behavior

Os 6 rótulos têm entrada de catálogo e aparecem em inglês no en_US (T-15).

Spec efetiva: `_reversa_sdd/stick/tasks.md#T-15`.

## Actual Behavior

Os 6 rótulos de `aggregates/limits.FACE_LABELS` não têm entrada de catálogo e aparecem em português no en_US.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 47.

## Suspected Area

- `caffmob_draw/aggregates/limits.py`

## Acceptance Criteria

- Os 6 rótulos têm entrada de catálogo e aparecem em inglês no en_US (T-15).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/tasks.md#T-15`
- Código afetado: `caffmob_draw/aggregates/limits.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-35HE (contexto `customize`), state `proposed`

## Resolution

- **Lote:** 17 (traduções) (BUG-20261011-JKLK, BUG-20261011-DLHX, BUG-20261011-FGTR); plano em `_reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** os 6 rótulos de `FACE_LABELS` não tinham entrada de catálogo.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: stick T-15 já pedia os rótulos no catálogo.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_35HE_i18n.py` | reprodução e regressão (en_US) | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/aggregates/limits.py` | FACE_LABELS com N_ | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/aggregates/ops_aggregate.py` | rótulo da face por tr no aviso | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/geometry_free/mesh.py` | nomes das chapas com N_ | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/cabinet_editor/scene_slides.py` | avisos com código | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/cabinet_editor/bridge.py` | mensagens dos deslizantes | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/data/translations/aggregates.json` | 6 rótulos das faces | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/data/translations/geometry_free.json` | Trás | `CHG-008.diff` |
| CHG-009 | code | `caffmob_draw/data/translations/cabinet_editor.json` | Sem vão interno para os deslizantes | `CHG-009.diff` |

**Vermelho (antes da correção):** `blender_bug_35HE_i18n` com 4 falhas no projeto.

**Verde (depois):** `blender_bug_35HE_i18n: OK`, `test_i18n_coverage` e `test_aggregate_limits` OK; na cópia isolada também `blender_bug_FLZO_i18n`, `blender_003_aggregates_smoke`, `blender_004_stick_smoke`, `blender_002_smoke`, `blender_008_construtor_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_35HE_i18n.py`. **Regressão:** `tests/blender_bug_35HE_i18n.py`, `tests/test_i18n_coverage.py`.

## Agent Notes

- Item 47 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
