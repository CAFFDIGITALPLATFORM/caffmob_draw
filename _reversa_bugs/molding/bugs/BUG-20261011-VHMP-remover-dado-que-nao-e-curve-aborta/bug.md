---
schema_version: 1
id: BUG-20261011-VHMP
display_number: 106
title: "Remover dado que não é Curve aborta a reconstrução das molduras"
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
module: molding
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

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
  specs: ["_reversa_sdd/molding/edge-cases.md#EC-04", "_reversa_sdd/molding/edge-cases.md#EC-11"]
  affected_code: ["caffmob_draw/molding/ops.py"]
  root_cause:
    state: confirmed
    hypothesis: "clear_scene_molding e _profile_metrics removem o dado com bpy.data.curves.remove sem olhar o tipo; malha (sweep convertido, perfil de pack) levanta TypeError depois de as molduras já terem sido apagadas."
    causal_path:
      - "molding/ops.py clear_scene_molding: bpy.data.curves.remove(data)"
      - "molding/packages.py _profile_metrics: idem"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/molding/ops.py, symbol: clear_scene_molding, commit: 83a6863}
      - {file: caffmob_draw/molding/packages.py, symbol: _profile_metrics, commit: 83a6863}
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

# Remover dado que não é Curve aborta a reconstrução das molduras

## Summary

`bpy.data.curves.remove(malha)` levanta `TypeError` depois de todas as molduras já terem sido apagadas. Testar `isinstance(data, bpy.types.Curve)` antes.

## Expected Behavior

Dado que não é Curve é ignorado (ou removido pelo tipo certo) e a reconstrução segue.

Spec efetiva: `_reversa_sdd/molding/edge-cases.md#EC-04`, `_reversa_sdd/molding/edge-cases.md#EC-11`.

## Actual Behavior

`bpy.data.curves.remove(malha)` levanta `TypeError` depois de todas as molduras já terem sido apagadas. Testar `isinstance(data, bpy.types.Curve)` antes.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/molding.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 95.

## Suspected Area

- `caffmob_draw/molding/ops.py`

## Acceptance Criteria

- Dado que não é Curve é ignorado (ou removido pelo tipo certo) e a reconstrução segue.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/molding/edge-cases.md#EC-04`, `_reversa_sdd/molding/edge-cases.md#EC-11`
- Código afetado: `caffmob_draw/molding/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 7 (molduras) (BUG-20261011-VHMP, BUG-20261011-XP5E, BUG-20261011-QT2G, BUG-20261011-MWN5, BUG-20261011-ARCH); plano em `_reversa_bugs/molding/bugs/BUG-20261011-VHMP-remover-dado-que-nao-e-curve-aborta/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `clear_scene_molding` e `_profile_metrics` removiam o dado com `curves.remove` sem olhar o tipo.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: molding EC-04 e EC-11.
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

- Item 95 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: depois do erro todas as molduras já foram apagadas e nenhuma volta: perda total até a correção.
- Unit/contexto: `molding`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
