---
schema_version: 1
id: BUG-20261011-ELOZ
display_number: 111
title: "Duplicar ou espelhar geometria com pai dá posição errada"
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
module: geometry_free
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

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

relationships: []

traceability:
  specs: ["_reversa_sdd/geometry_free/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/geometry_free/ops_edit.py"]
  root_cause:
    state: confirmed
    hypothesis: "Duplicar atribui um ponto mundial a copy.location (relativa ao pai) e Espelhar soma um vetor mundial à location local."
    causal_path:
      - "geometry_free/ops_edit.py BTM_OT_GeometryDuplicate: copy.location = obj.matrix_world @ (x,0,0)"
      - "geometry_free/ops_edit.py BTM_OT_GeometryMirror: obj.location ± matrix_world.to_3x3() @ (x,0,0)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/geometry_free/ops_edit.py, symbol: BTM_OT_GeometryDuplicate, commit: 83a6863}
      - {file: caffmob_draw/geometry_free/ops_edit.py, symbol: BTM_OT_GeometryMirror, commit: 83a6863}
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

# Duplicar ou espelhar geometria com pai dá posição errada

## Summary

Mediu-se (1,5, 2, 0) em vez de (2, 0,5, 0).

## Expected Behavior

Duplicar/espelhar respeita o espaço do pai.

Spec efetiva: `_reversa_sdd/geometry_free/tasks.md#DT-01`.

## Actual Behavior

Mediu-se (1,5, 2, 0) em vez de (2, 0,5, 0).

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/geometry_free.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 100.

## Suspected Area

- `caffmob_draw/geometry_free/ops_edit.py`

## Acceptance Criteria

- Duplicar/espelhar respeita o espaço do pai.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/geometry_free/tasks.md#DT-01`
- Código afetado: `caffmob_draw/geometry_free/ops_edit.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 8 (geometria livre com pai e filhos) (BUG-20261011-ELOZ, BUG-20261011-GUHQ); plano em `_reversa_bugs/geometry_free/bugs/BUG-20261011-ELOZ-duplicar-ou-espelhar-geometria-com-pai-da/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** Duplicar gravava um ponto mundial em `copy.location` (relativa ao pai) e Espelhar somava um vetor mundial à `location` local.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 65 e geometry_free EC-09/DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_ELOZ_geometry_parent.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/geometry_free/ops_edit.py` | duplicar/espelhar no espaço da peça; excluir mantém os filhos | `CHG-002.diff` |

**Vermelho (antes da correção):** `blender_bug_ELOZ_geometry_parent` com 3 falhas no projeto.

**Verde (depois):** `blender_bug_ELOZ_geometry_parent: OK`, `blender_002_smoke: OK`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_ELOZ_geometry_parent.py`. **Regressão:** `tests/blender_bug_ELOZ_geometry_parent.py`, `tests/blender_002_smoke.py`.

## Agent Notes

- Item 100 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `geometry_free`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
