---
schema_version: 1
id: BUG-20261011-L5ML
display_number: 45
title: "Grupos soltos (SketchUp, biblioteca de objetos) ficam fora da colisão"
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
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

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
  specs: ["_reversa_sdd/collision/tasks.md#DT-05", "_reversa_sdd/questions.md#pergunta-35"]
  affected_code: ["caffmob_draw/collision/scan.py"]
  root_cause:
    state: confirmed
    hypothesis: "_kind_of descartava o Empty raiz de grupo solto (SketchUp, biblioteca de objetos)."
    causal_path:
      - "collision/scan.py _kind_of"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/collision/scan.py, symbol: _kind_of, commit: 8530606}
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

# Grupos soltos (SketchUp, biblioteca de objetos) ficam fora da colisão

## Summary

Raízes de grupo SketchUp e da biblioteca de objetos não são verificadas.

## Expected Behavior

Raízes de grupo SketchUp e da biblioteca de objetos entram na verificação.

Spec efetiva: `_reversa_sdd/collision/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-35`.

## Actual Behavior

Raízes de grupo SketchUp e da biblioteca de objetos não são verificadas.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 34.

## Suspected Area

- `caffmob_draw/collision/scan.py`

## Acceptance Criteria

- Raízes de grupo SketchUp e da biblioteca de objetos entram na verificação.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-35`
- Código afetado: `caffmob_draw/collision/scan.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 22 (colisão) (BUG-20261011-SRPV, BUG-20261011-KX3O, BUG-20261011-L5ML, BUG-20261011-JUJZ, BUG-20261011-7GRY, BUG-20261011-EWKD, BUG-20261011-ZEN6); plano em `_reversa_bugs/collision/bugs/BUG-20261011-SRPV-tolerancia-de-1-0-mm-instavel-por/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** _kind_of descartava o Empty raiz de grupo solto (SketchUp, biblioteca de objetos).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 35 e collision DT-05.
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

- Item 34 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
