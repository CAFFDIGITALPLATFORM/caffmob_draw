---
schema_version: 1
id: BUG-20261011-ODY2
display_number: 30
title: "set_interior inválido devolve FINISHED e cria passo de desfazer vazio"
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10"]

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
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-20"]
  affected_code: ["caffmob_draw/customize/ops_customize.py"]
  root_cause:
    state: confirmed
    hypothesis: "set_interior inválido devolve FINISHED, criando passo de desfazer vazio."
    causal_path:
      - "customize/ops_customize.py BTM_OT_CustomizeSetInterior.execute"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/customize/ops_customize.py, symbol: BTM_OT_CustomizeSetInterior.execute, commit: a67387a}
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

# set_interior inválido devolve FINISHED e cria passo de desfazer vazio

## Summary

`set_interior` inválido devolve `FINISHED`. Fica um passo de desfazer vazio.

## Expected Behavior

`set_interior` com entrada inválida devolve `CANCELLED`, sem passo de desfazer.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-20`.

## Actual Behavior

`set_interior` inválido devolve `FINISHED`. Fica um passo de desfazer vazio.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 19.

## Suspected Area

- `caffmob_draw/customize/ops_customize.py`

## Acceptance Criteria

- `set_interior` com entrada inválida devolve `CANCELLED`, sem passo de desfazer.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-20`
- Código afetado: `caffmob_draw/customize/ops_customize.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 20 (personalização de módulos (customize)) (BUG-20261011-UJ5Q, BUG-20261011-XMUG, BUG-20261011-MNX3, BUG-20261011-GL62, BUG-20261011-ODY2); plano em `_reversa_bugs/customize/bugs/BUG-20261011-UJ5Q-trocar-para-2-a-4-gavetas-no/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** set_interior inválido devolve FINISHED, criando passo de desfazer vazio.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: customize EC-20.
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

- Item 19 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
