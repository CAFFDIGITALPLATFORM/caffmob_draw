---
schema_version: 1
id: BUG-20261011-MWN5
display_number: 109
title: "_spawn_sweep deixa dados de curva órfãos"
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
module: molding
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: média
  reasons: ["reconstrução de todas as molduras da cena muda de ordem (novas antes de apagar as velhas)", "X/Delete de armário deixa de levar a moldura da corrida", "sem dado persistido novo"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/molding/edge-cases.md#EC-03"]
  affected_code: ["caffmob_draw/molding/ops.py"]
  root_cause:
    state: confirmed
    hypothesis: "_spawn_sweep remove os objetos do sweep descartado mas não os dados de curva."
    causal_path:
      - "molding/ops.py _spawn_sweep: bpy.data.objects.remove sem remover a curva"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/molding/ops.py, symbol: _spawn_sweep, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_VHMP_molding.py"]
  regression_tests: ["tests/blender_bug_VHMP_molding.py", "tests/test_component_delete.py", "tests/blender_bug_7DHT_wall_delete.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_VHMP_molding.py
    purpose: "reprodução e regressão dos cinco defeitos"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_component_delete.py
    purpose: "delete_plan não leva a moldura da corrida"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/molding/ops.py
    purpose: "scene_molding, _remove, rollback, Refresh com ERROR"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/molding/packages.py
    purpose: "free_object pelo tipo do dado"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/selection/component.py
    purpose: "delete_plan pula IS_HB_MOLDING_SWEEP"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/data/translations/molding.json
    purpose: "texto do erro do Refresh"
    diff: _reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# _spawn_sweep deixa dados de curva órfãos

## Summary

`_spawn_sweep` deixa dados de curva órfãos.

## Expected Behavior

Sweep descartado remove também os dados de curva.

Spec efetiva: `_reversa_sdd/molding/edge-cases.md#EC-03`.

## Actual Behavior

`_spawn_sweep` deixa dados de curva órfãos.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 98.

## Suspected Area

- `caffmob_draw/molding/ops.py`

## Acceptance Criteria

- Sweep descartado remove também os dados de curva.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/molding/edge-cases.md#EC-03`
- Código afetado: `caffmob_draw/molding/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 7 (molduras) (BUG-20261011-VHMP, BUG-20261011-XP5E, BUG-20261011-QT2G, BUG-20261011-MWN5, BUG-20261011-ARCH); plano em `_reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `_spawn_sweep` não removia os dados de curva do sweep descartado.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: molding EC-03.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_VHMP_molding.py` | reprodução e regressão dos cinco defeitos | `CHG-001.diff` |
| CHG-002 | test | `tests/test_component_delete.py` | delete_plan não leva a moldura da corrida | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/molding/ops.py` | scene_molding, _remove, rollback, Refresh com ERROR | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/molding/packages.py` | free_object pelo tipo do dado | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/selection/component.py` | delete_plan pula IS_HB_MOLDING_SWEEP | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/data/translations/molding.json` | texto do erro do Refresh | `CHG-006.diff` |

**Vermelho (antes da correção):** `test_component_delete` falhou; `blender_bug_VHMP_molding` com 5 falhas no projeto.

**Verde (depois):** `blender_bug_VHMP_molding: OK`, `blender_bug_7DHT_wall_delete: OK`, `test_component_delete` e `test_i18n_coverage` OK; na cópia isolada também `blender_011_component_smoke`, `blender_012_legacy_gate_smoke`, `blender_012_convert_smoke`, `test_leaf_sweep`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_VHMP_molding.py`. **Regressão:** `tests/blender_bug_VHMP_molding.py`, `tests/test_component_delete.py`, `tests/blender_bug_7DHT_wall_delete.py`.

## Agent Notes

- Item 98 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `molding`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
