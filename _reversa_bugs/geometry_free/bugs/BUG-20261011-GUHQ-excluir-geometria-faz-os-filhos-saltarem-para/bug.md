---
schema_version: 1
id: BUG-20261011-GUHQ
display_number: 112
title: "Excluir geometria faz os filhos saltarem para a origem do mundo"
status: resolved
phase: delivering
severity: high
priority: P1
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: geometry_free
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["três operadores da geometria livre", "sem dado persistido", "Ctrl+Z desfaz"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-ELOZ
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]
  - bug: BUG-20261011-7DHT
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/geometry_free/tasks.md#DT-02"]
  affected_code: ["caffmob_draw/geometry_free/ops_edit.py"]
  root_cause:
    state: confirmed
    hypothesis: "Excluir remove o objeto sem soltar os filhos com a matriz de mundo: a location local deles passa a valer como mundial."
    causal_path:
      - "geometry_free/ops_edit.py BTM_OT_GeometryDelete: bpy.data.objects.remove(obj)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/geometry_free/ops_edit.py, symbol: BTM_OT_GeometryDelete, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_ELOZ_geometry_parent.py"]
  regression_tests: ["tests/blender_bug_ELOZ_geometry_parent.py", "tests/blender_002_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_ELOZ_geometry_parent.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-ELOZ-duplicar-ou-espelhar-geometria-com-pai-da/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/geometry_free/ops_edit.py
    purpose: "duplicar/espelhar no espaço da peça; excluir mantém os filhos"
    diff: _reversa_bugs/geometry_free/bugs/BUG-20261011-ELOZ-duplicar-ou-espelhar-geometria-com-pai-da/fix/CHG-002.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Excluir geometria faz os filhos saltarem para a origem do mundo

## Summary

Excluir faz os filhos saltarem para a origem do mundo.

## Expected Behavior

Os filhos ficam no lugar (matriz de mundo preservada).

Spec efetiva: `_reversa_sdd/geometry_free/tasks.md#DT-02`.

## Actual Behavior

Excluir faz os filhos saltarem para a origem do mundo.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 101.

## Suspected Area

- `caffmob_draw/geometry_free/ops_edit.py`

## Acceptance Criteria

- Os filhos ficam no lugar (matriz de mundo preservada).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/geometry_free/tasks.md#DT-02`
- Código afetado: `caffmob_draw/geometry_free/ops_edit.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-7DHT (contexto `selection`), state `proposed`
- related-to → BUG-20261011-ELOZ (contexto `geometry_free`), state `proposed`

## Resolution

- **Lote:** 8 (geometria livre com pai e filhos) (BUG-20261011-ELOZ, BUG-20261011-GUHQ); plano em `_reversa_bugs/geometry_free/bugs/BUG-20261011-ELOZ-duplicar-ou-espelhar-geometria-com-pai-da/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** Excluir removia a peça sem soltar os filhos com a matriz de mundo.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 65 e geometry_free EC-14/DT-02.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_ELOZ_geometry_parent.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/geometry_free/ops_edit.py` | duplicar/espelhar no espaço da peça; excluir mantém os filhos | `CHG-002.diff` |

**Vermelho (antes da correção):** `blender_bug_ELOZ_geometry_parent` com 3 falhas no projeto.

**Verde (depois):** `blender_bug_ELOZ_geometry_parent: OK`, `blender_002_smoke: OK`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_ELOZ_geometry_parent.py`. **Regressão:** `tests/blender_bug_ELOZ_geometry_parent.py`, `tests/blender_002_smoke.py`.

## Agent Notes

- Item 101 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: mesmo efeito do #1 (filhos saltam de lugar ao excluir), que foi proposto como crítico.
- Unit/contexto: `geometry_free`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
