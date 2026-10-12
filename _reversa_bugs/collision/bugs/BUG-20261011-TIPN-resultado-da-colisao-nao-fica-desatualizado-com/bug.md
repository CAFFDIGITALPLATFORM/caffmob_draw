---
schema_version: 1
id: BUG-20261011-TIPN
display_number: 44
title: "Resultado da colisão não fica desatualizado com objeto novo, apagado ou renomeado"
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
  reasons: ["handlers de depsgraph só ligam um aviso (não recalculam nada)", "painel mostra 'Desatualizado' no lugar de 'Sem interferência'"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/collision/edge-cases.md#EC-04", "_reversa_sdd/collision/tasks.md#DT-04"]
  affected_code: ["caffmob_draw/collision/stale.py", "caffmob_draw/collision/ops_collision.py"]
  root_cause:
    state: confirmed
    hypothesis: "stale.on_depsgraph_update só olha objetos dentro de checked_names (e nomes das linhas): objeto novo, apagado ou renomeado não liga stale; check_moved sem verificação prévia deixa checked = -1 e o handler sai cedo."
    causal_path:
      - "collision/stale.py on_depsgraph_update: _checked_root(obj, names) só"
      - "collision/scan.py check_moved: não marca checked"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/collision/stale.py, symbol: on_depsgraph_update, commit: 83a6863}
      - {file: caffmob_draw/collision/scan.py, symbol: check_moved, commit: 83a6863}
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

# Resultado da colisão não fica desatualizado com objeto novo, apagado ou renomeado

## Summary

`stale.on_depsgraph_update` só olha `checked_names`, e `check_moved` sem verificação prévia não marca `checked`.

## Expected Behavior

Criar, apagar ou renomear objeto marca o resultado como desatualizado; `check_moved` marca `checked`.

Spec efetiva: `_reversa_sdd/collision/edge-cases.md#EC-04`, `_reversa_sdd/collision/tasks.md#DT-04`.

## Actual Behavior

`stale.on_depsgraph_update` só olha `checked_names`, e `check_moved` sem verificação prévia não marca `checked`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 33.

## Suspected Area

- `caffmob_draw/collision/stale.py`
- `caffmob_draw/collision/ops_collision.py`

## Acceptance Criteria

- Criar, apagar ou renomear objeto marca o resultado como desatualizado; `check_moved` marca `checked`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/edge-cases.md#EC-04`, `_reversa_sdd/collision/tasks.md#DT-04`
- Código afetado: `caffmob_draw/collision/stale.py`, `caffmob_draw/collision/ops_collision.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 14 (resultados desatualizados) (BUG-20261011-TIPN, BUG-20261011-FVQI); plano em `_reversa_bugs/collision/bugs/BUG-20261011-TIPN-resultado-da-colisao-nao-fica-desatualizado-com/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** o handler de colisão só vigiava os itens verificados e `check_moved` sem verificação não marcava `checked`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 34 e collision DT-04.
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

- Item 33 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
