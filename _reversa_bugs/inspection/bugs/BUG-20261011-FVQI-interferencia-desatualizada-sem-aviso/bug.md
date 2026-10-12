---
schema_version: 1
id: BUG-20261011-FVQI
display_number: 102
title: "Interferência desatualizada sem aviso"
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
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["handlers de depsgraph só ligam um aviso (não recalculam nada)", "painel mostra 'Desatualizado' no lugar de 'Sem interferência'"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-TIPN
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/inspection/tasks.md#DT-05"]
  affected_code: ["caffmob_draw/inspection/interference.py", "caffmob_draw/inspection/ops_interference.py"]
  root_cause:
    state: confirmed
    hypothesis: "A inspeção não tem handler de desatualização: o resultado da interferência vale para sempre depois da verificação."
    causal_path:
      - "inspection/interference.py store_results: sem estado 'desatualizado'"
      - "inspection/ops_interference.py register: sem depsgraph_update_post"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/inspection/interference.py, symbol: store_results, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_TIPN_stale_results.py"]
  regression_tests: ["tests/blender_bug_TIPN_stale_results.py", "tests/blender_004_collision_smoke.py", "tests/blender_inspection_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_TIPN_stale_results.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/collision/stale.py
    purpose: "novo/apagado/renomeado ligam stale"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/collision/scan.py
    purpose: "check_moved marca checked"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/inspection/props.py
    purpose: "stale da interferência"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/inspection/interference.py
    purpose: "handler de desatualização"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/inspection/ops_interference.py
    purpose: "registra e remove o handler"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/ui/panels.py
    purpose: "aviso de desatualizado no painel"
    diff: _reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/CHG-007.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Interferência desatualizada sem aviso

## Summary

O resultado não fica "desatualizado" quando um objeto se move.

## Expected Behavior

Mover objeto marca o resultado de interferência como desatualizado.

Spec efetiva: `_reversa_sdd/inspection/tasks.md#DT-05`.

## Actual Behavior

O resultado não fica "desatualizado" quando um objeto se move.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 91.

## Suspected Area

- `caffmob_draw/inspection/interference.py`
- `caffmob_draw/inspection/ops_interference.py`

## Acceptance Criteria

- Mover objeto marca o resultado de interferência como desatualizado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/inspection/tasks.md#DT-05`
- Código afetado: `caffmob_draw/inspection/interference.py`, `caffmob_draw/inspection/ops_interference.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-TIPN (contexto `collision`), state `proposed`

## Resolution

- **Lote:** 14 (resultados desatualizados) (BUG-20261011-TIPN, BUG-20261011-FVQI); plano em `_reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** a inspeção não tinha estado nem handler de desatualização da interferência.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 93 e inspection DT-05.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_TIPN_stale_results.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/collision/stale.py` | novo/apagado/renomeado ligam stale | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/collision/scan.py` | check_moved marca checked | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/inspection/props.py` | stale da interferência | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/inspection/interference.py` | handler de desatualização | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/inspection/ops_interference.py` | registra e remove o handler | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/ui/panels.py` | aviso de desatualizado no painel | `CHG-007.diff` |

**Vermelho (antes da correção):** `blender_bug_TIPN_stale_results` com 5 falhas e 1 exceção no projeto.

**Verde (depois):** `blender_bug_TIPN_stale_results: OK`, `blender_004_collision_smoke` OK (200 itens ≤ 2 s); na cópia isolada também `test_collision_rules`, `test_i18n_coverage`, `test_inspection_math`, `blender_004_stick_smoke`, `blender_inspection_smoke`, `blender_007_window_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_TIPN_stale_results.py`. **Regressão:** `tests/blender_bug_TIPN_stale_results.py`, `tests/blender_004_collision_smoke.py`, `tests/blender_inspection_smoke.py`.

## Agent Notes

- Item 91 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `inspection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
