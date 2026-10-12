---
schema_version: 1
id: BUG-20261011-UJ5Q
display_number: 25
title: "Trocar para 2 a 4 gavetas no frameless perde a personalização"
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
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["personalização de módulos", "sem mudança de formato"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-04", "_reversa_sdd/customize/tasks.md#DT-02", "_reversa_sdd/questions.md#pergunta-41"]
  affected_code: ["caffmob_draw/customize/adapters/frameless.py", "caffmob_draw/customize/reapply.py"]
  root_cause:
    state: confirmed
    hypothesis: "change_bay_opening recria os vãos do compartimento e o btm_custom do vão antigo sai junto."
    causal_path:
      - "customize/adapters/frameless.py set_front: change_bay_opening no bay"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/customize/adapters/frameless.py, symbol: set_front, commit: a67387a}
  reproduction_tests: ["tests/blender_bug_UJ5Q_customize.py"]
  regression_tests: ["tests/blender_bug_UJ5Q_customize.py", "tests/blender_003_customize_smoke.py", "tests/blender_bug_J2NY_library_io.py", "tests/test_customize_spec.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_UJ5Q_customize.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/customize/adapters/frameless.py
    purpose: "personalização segue para as gavetas novas"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/customize/ops_customize.py
    purpose: "interior recusado devolve CANCELLED"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/customize/ops_library.py
    purpose: "R gira o conjunto"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/customize/panels.py
    purpose: "menu de estilo de gaveta"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/customize/spec.py
    purpose: "interior torto ignorado"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Trocar para 2 a 4 gavetas no frameless perde a personalização

## Summary

O vão antigo é apagado e o `btm_custom` vai junto.

## Expected Behavior

Ao trocar para 2 a 4 gavetas, o `btm_custom` do vão antigo é copiado para os vãos novos, exceto o interior.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-04`, `_reversa_sdd/customize/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-41`.

## Actual Behavior

O vão antigo é apagado e o `btm_custom` vai junto.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/customize.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 14.

## Suspected Area

- `caffmob_draw/customize/adapters/frameless.py`
- `caffmob_draw/customize/reapply.py`

## Acceptance Criteria

- Ao trocar para 2 a 4 gavetas, o `btm_custom` do vão antigo é copiado para os vãos novos, exceto o interior.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-04`, `_reversa_sdd/customize/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-41`
- Código afetado: `caffmob_draw/customize/adapters/frameless.py`, `caffmob_draw/customize/reapply.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 20 (personalização de módulos (customize)) (BUG-20261011-UJ5Q, BUG-20261011-XMUG, BUG-20261011-MNX3, BUG-20261011-GL62, BUG-20261011-ODY2); plano em `_reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** change_bay_opening recria os vãos do compartimento e o btm_custom do vão antigo sai junto.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 41 e customize DT-02.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_UJ5Q_customize.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/customize/adapters/frameless.py` | personalização segue para as gavetas novas | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/customize/ops_customize.py` | interior recusado devolve CANCELLED | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/customize/ops_library.py` | R gira o conjunto | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/customize/panels.py` | menu de estilo de gaveta | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/customize/spec.py` | interior torto ignorado | `CHG-006.diff` |

**Vermelho (antes da correção):** material e puxador perdidos nas gavetas novas; sem menu de estilo de gaveta; ValueError no interior; R não gira o solto; FINISHED no interior inválido.

**Verde (depois):** `blender_bug_UJ5Q_customize.py` OK; na cópia isolada também `blender_003_customize_smoke`, `blender_bug_J2NY_library_io`, `test_customize_spec`, `test_i18n_coverage`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_UJ5Q_customize.py`. **Regressão:** `tests/blender_bug_UJ5Q_customize.py`, `tests/blender_003_customize_smoke.py`, `tests/blender_bug_J2NY_library_io.py`, `tests/test_customize_spec.py`.

## Agent Notes

- Item 14 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: perda silenciosa de dado do usuário (personalização) num fluxo comum, reproduzida.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
