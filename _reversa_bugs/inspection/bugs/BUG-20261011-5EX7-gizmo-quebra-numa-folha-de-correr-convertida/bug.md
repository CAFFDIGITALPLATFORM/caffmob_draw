---
schema_version: 1
id: BUG-20261011-5EX7
display_number: 97
title: "Gizmo quebra numa folha de correr convertida"
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
module: inspection
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

change_risk:
  classification: baixa
  reasons: ["gizmo de inspeção", "Abrir 90° e o clique continuam em 90°"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/inspection/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/inspection/adapters/aggregate_leaf.py", "caffmob_draw/inspection/gizmo.py"]
  root_cause:
    state: confirmed
    hypothesis: "AggregateLeafFront não tem travel() e a base Front também não; o gizmo chama front.travel() na seta da folha de correr."
    causal_path:
      - "inspection/gizmo.py _arrow_get/_arrow_set"
      - "inspection/adapters/aggregate_leaf.py: sem travel"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/inspection/adapters/aggregate_leaf.py, symbol: AggregateLeafFront, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_5EX7_gizmo.py"]
  regression_tests: ["tests/blender_bug_5EX7_gizmo.py", "tests/test_inspection_math.py", "tests/blender_inspection_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_5EX7_gizmo.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_inspection_math.py
    purpose: "snap_angle com máximo da folha"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/inspection/gizmo.py
    purpose: "dial pelo max_value; pendente com a frente; seta oculta sem curso"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/inspection/fronts.py
    purpose: "travel() na base"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/inspection/pivot_math.py
    purpose: "snap_angle com maximum"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/inspection/adapters/aggregate_leaf.py
    purpose: "travel() da folha convertida"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Gizmo quebra numa folha de correr convertida

## Summary

`AggregateLeafFront` não tem `travel()`.

## Expected Behavior

O gizmo funciona em folha de correr convertida.

Spec efetiva: `_reversa_sdd/inspection/tasks.md#DT-01`.

## Actual Behavior

`AggregateLeafFront` não tem `travel()`.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/inspection.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 86.

## Suspected Area

- `caffmob_draw/inspection/adapters/aggregate_leaf.py`
- `caffmob_draw/inspection/gizmo.py`

## Acceptance Criteria

- O gizmo funciona em folha de correr convertida.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/inspection/tasks.md#DT-01`
- Código afetado: `caffmob_draw/inspection/adapters/aggregate_leaf.py`, `caffmob_draw/inspection/gizmo.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 15 (gizmo de inspeção) (BUG-20261011-5EX7, BUG-20261011-GBPG, BUG-20261011-PGMI); plano em `_reversa_bugs/inspection/bugs/BUG-20261011-5EX7-gizmo-quebra-numa-folha-de-correr-convertida/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `AggregateLeafFront` e a base `Front` não tinham `travel()`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 61 e inspection DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_5EX7_gizmo.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | test | `tests/test_inspection_math.py` | snap_angle com máximo da folha | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/inspection/gizmo.py` | dial pelo max_value; pendente com a frente; seta oculta sem curso | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/inspection/fronts.py` | travel() na base | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/inspection/pivot_math.py` | snap_angle com maximum | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/inspection/adapters/aggregate_leaf.py` | travel() da folha convertida | `CHG-006.diff` |

**Vermelho (antes da correção):** `test_inspection_math` com erro; `blender_bug_5EX7_gizmo` com 3 falhas no projeto.

**Verde (depois):** `test_inspection_math` OK, `blender_bug_5EX7_gizmo: OK`; na cópia isolada também `test_i18n_coverage`, `blender_inspection_smoke`, `blender_bug_porta_real_abre`, `blender_007_window_smoke`, `blender_bug_TIPN_stale_results`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_5EX7_gizmo.py`. **Regressão:** `tests/blender_bug_5EX7_gizmo.py`, `tests/test_inspection_math.py`, `tests/blender_inspection_smoke.py`.

## Agent Notes

- Item 86 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `inspection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
