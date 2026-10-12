---
schema_version: 1
id: BUG-20261011-VVEJ
display_number: 51
title: "Checagem de descendente em link.release nunca barra nada"
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
module: stick
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["uma condição em link.release", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-ZKQ7
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/stick/edge-cases.md#EC-09"]
  affected_code: ["caffmob_draw/stick/link.py"]
  root_cause:
    state: confirmed
    hypothesis: "link.release compara `parent.name` (str) com os objetos de `item.children_recursive`; o teste sempre passa e o item é posto no espaço de um descendente."
    causal_path:
      - "stick/link.py release linha 150: `parent.name not in item.children_recursive`"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sonda no Blender 5.2"
    code_refs:
      - {file: caffmob_draw/stick/link.py, symbol: release, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_ZKQ7_parent_cycle.py"]
  regression_tests: ["tests/blender_bug_ZKQ7_parent_cycle.py", "tests/blender_003_aggregates_smoke.py", "tests/blender_004_stick_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_ZKQ7_parent_cycle.py
    purpose: "reprodução e regressão das duas checagens"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-ZKQ7-checagem-de-descendencia-invertida-em-can-convert/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/aggregates/convert.py
    purpose: "can_convert: parent in obj.children_recursive"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-ZKQ7-checagem-de-descendencia-invertida-em-can-convert/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/stick/link.py
    purpose: "release compara objetos"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-ZKQ7-checagem-de-descendencia-invertida-em-can-convert/fix/CHG-003.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Checagem de descendente em link.release nunca barra nada

## Summary

Compara `parent.name` (string) com objetos em `children_recursive`, o que pode criar ciclo de parentesco. Correção: `parent not in item.children_recursive`.

## Expected Behavior

`release` não reparenta no `orig_parent` quando ele virou descendente do item.

Spec efetiva: `_reversa_sdd/stick/edge-cases.md#EC-09`.

## Actual Behavior

Compara `parent.name` (string) com objetos em `children_recursive`, o que pode criar ciclo de parentesco. Correção: `parent not in item.children_recursive`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 40.

## Suspected Area

- `caffmob_draw/stick/link.py`

## Acceptance Criteria

- `release` não reparenta no `orig_parent` quando ele virou descendente do item.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/edge-cases.md#EC-09`
- Código afetado: `caffmob_draw/stick/link.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-ZKQ7 (contexto `aggregates`), state `proposed`

## Resolution

- **Lote:** 2 (checagem de descendência) (BUG-20261011-ZKQ7, BUG-20261011-VVEJ); plano em `_reversa_bugs/aggregates/bugs/BUG-20261011-ZKQ7-checagem-de-descendencia-invertida-em-can-convert/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `link.release` comparava `parent.name` (str) com objetos; o teste sempre passava e o item era posto no espaço de um descendente (salto de lugar).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: stick EC-09 já definia a comparação por objeto.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_ZKQ7_parent_cycle.py` | reprodução e regressão das duas checagens | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/aggregates/convert.py` | can_convert: parent in obj.children_recursive | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/stick/link.py` | release compara objetos | `CHG-003.diff` |

**Vermelho (antes da correção):** `blender_bug_ZKQ7_parent_cycle` com 3 falhas no projeto (peça filha recusada; pai descendente aceito; item em (0, 0, -1)).

**Verde (depois):** `blender_bug_ZKQ7_parent_cycle: OK`, `blender_003_aggregates_smoke: OK`, `blender_004_stick_smoke` exit 0, `blender_007_window_smoke: OK` (cópia isolada); `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_ZKQ7_parent_cycle.py`. **Regressão:** `tests/blender_bug_ZKQ7_parent_cycle.py`, `tests/blender_003_aggregates_smoke.py`, `tests/blender_004_stick_smoke.py`.

## Agent Notes

- Item 40 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: mesmo efeito do #21 (ciclo de parentesco), que foi proposto como crítico.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
