---
schema_version: 1
id: BUG-20261011-SRPV
display_number: 42
title: "Tolerância de 1,0 mm instável por arredondamento de float"
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
module: collision
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["só a verificação de colisão e o painel", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/collision/requirements.md#RN-01", "_reversa_sdd/collision/requirements.md#CA-04", "_reversa_sdd/collision/edge-cases.md#EC-11", "_reversa_sdd/collision/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/collision/rules.py", "caffmob_draw/collision/obb.py"]
  root_cause:
    state: confirmed
    hypothesis: "evaluate comparava depth <= TOLERANCE com float exato: 1,0 mm oscila pelo arredondamento conforme a posição."
    causal_path:
      - "collision/rules.py evaluate"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/collision/rules.py, symbol: evaluate, commit: 8530606}
  reproduction_tests: ["tests/blender_bug_KX3O_collision.py", "tests/test_collision_rules.py"]
  regression_tests: ["tests/blender_bug_KX3O_collision.py", "tests/test_collision_rules.py", "tests/blender_004_collision_smoke.py", "tests/blender_bug_TIPN_stale_results.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_KX3O_collision.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_collision_rules.py
    purpose: "tolerância de 1,0 mm"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/collision/ops_collision.py
    purpose: "Afastar o selecionado"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/collision/panels.py
    purpose: "override do agregado e linhas em alerta"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/collision/rules.py
    purpose: "tolerância estável"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/collision/scan.py
    purpose: "grupo solto, contenção, ordem e erro"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Tolerância de 1,0 mm instável por arredondamento de float

## Summary

Com a borda em 0,999 m conta, com a borda em 0,599 m não conta. Correção: `depth <= TOLERANCE + 1e-9`.

## Expected Behavior

Sobreposição de até 1,0 mm nunca conta, independente da posição (RN-01, CA-04).

Spec efetiva: `_reversa_sdd/collision/requirements.md#RN-01`, `_reversa_sdd/collision/requirements.md#CA-04`, `_reversa_sdd/collision/edge-cases.md#EC-11`, `_reversa_sdd/collision/tasks.md#DT-01`.

## Actual Behavior

Com a borda em 0,999 m conta, com a borda em 0,599 m não conta. Correção: `depth <= TOLERANCE + 1e-9`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 31.

## Suspected Area

- `caffmob_draw/collision/rules.py`
- `caffmob_draw/collision/obb.py`

## Acceptance Criteria

- Sobreposição de até 1,0 mm nunca conta, independente da posição (RN-01, CA-04).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/requirements.md#RN-01`, `_reversa_sdd/collision/requirements.md#CA-04`, `_reversa_sdd/collision/edge-cases.md#EC-11`, `_reversa_sdd/collision/tasks.md#DT-01`
- Código afetado: `caffmob_draw/collision/rules.py`, `caffmob_draw/collision/obb.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 22 (colisão) (BUG-20261011-SRPV, BUG-20261011-KX3O, BUG-20261011-L5ML, BUG-20261011-JUJZ, BUG-20261011-7GRY, BUG-20261011-EWKD, BUG-20261011-ZEN6); plano em `_reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** evaluate comparava depth <= TOLERANCE com float exato: 1,0 mm oscila pelo arredondamento conforme a posição.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 31, RN-01 e CA-04.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_KX3O_collision.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | test | `tests/test_collision_rules.py` | tolerância de 1,0 mm | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/collision/ops_collision.py` | Afastar o selecionado | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/collision/panels.py` | override do agregado e linhas em alerta | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/collision/rules.py` | tolerância estável | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/collision/scan.py` | grupo solto, contenção, ordem e erro | `CHG-006.diff` |

**Vermelho (antes da correção):** Afastar move o item errado e aceita resultado desatualizado; grupo solto fora; override edita o módulo; lista fora de ordem e erro antigo; contenção não detectada; linhas sem alerta; 1,0 mm instável.

**Verde (depois):** `blender_bug_KX3O_collision.py` OK, `test_collision_rules.py` OK; na cópia isolada também `blender_004_collision_smoke`, `blender_bug_TIPN_stale_results`, `blender_bug_NQ2L_aggregates`, `blender_004_stick_smoke`, `blender_009_skp_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_KX3O_collision.py`, `tests/test_collision_rules.py`. **Regressão:** `tests/blender_bug_KX3O_collision.py`, `tests/test_collision_rules.py`, `tests/blender_004_collision_smoke.py`, `tests/blender_bug_TIPN_stale_results.py`.

## Agent Notes

- Item 31 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
