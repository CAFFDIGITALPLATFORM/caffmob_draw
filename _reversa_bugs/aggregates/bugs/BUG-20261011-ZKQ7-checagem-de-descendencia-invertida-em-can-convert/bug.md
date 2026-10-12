---
schema_version: 1
id: BUG-20261011-ZKQ7
display_number: 32
title: "Checagem de descendência invertida em can_convert permite ciclo de parentesco"
status: resolved
phase: delivering
severity: critical
priority: P0
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: aggregates
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["uma condição em can_convert", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/aggregates/requirements.md#RN-05", "_reversa_sdd/aggregates/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-3", "caffmob_draw/aggregates/convert.py#L126"]
  affected_code: ["caffmob_draw/aggregates/convert.py"]
  root_cause:
    state: confirmed
    hypothesis: "O 3º teste de can_convert usa `obj in parent.children_recursive` (objeto descendente do pai) em vez de `parent in obj.children_recursive` (pai descendente do objeto), o contrário da mensagem e de RN-05."
    causal_path:
      - "aggregates/convert.py can_convert linha 23: teste invertido"
      - "aggregates/convert.py convert: obj.parent = parent ignorado pelo Blender, mas o agregado é gravado"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sonda no Blender 5.2"
    code_refs:
      - {file: caffmob_draw/aggregates/convert.py, symbol: can_convert, commit: 83a6863}
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

# Checagem de descendência invertida em can_convert permite ciclo de parentesco

## Summary

O 3º teste usa `obj in parent.children_recursive`, o contrário da mensagem. Um objeto que já é filho do pai é recusado, e um pai descendente do objeto passa, o que cria ciclo de parentesco. Correção: `parent in obj.children_recursive`.

## Expected Behavior

O 3º teste recusa 'pai descendente do objeto' (como diz a mensagem) e aceita objeto que já é filho do pai.

Spec efetiva: `_reversa_sdd/aggregates/requirements.md#RN-05`, `_reversa_sdd/aggregates/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-3`, `caffmob_draw/aggregates/convert.py#L126`.

## Actual Behavior

O 3º teste usa `obj in parent.children_recursive`, o contrário da mensagem. Um objeto que já é filho do pai é recusado, e um pai descendente do objeto passa, o que cria ciclo de parentesco. Correção: `parent in obj.children_recursive`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 21.

## Suspected Area

- `caffmob_draw/aggregates/convert.py`

## Acceptance Criteria

- O 3º teste recusa 'pai descendente do objeto' (como diz a mensagem) e aceita objeto que já é filho do pai.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/requirements.md#RN-05`, `_reversa_sdd/aggregates/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-3`, `caffmob_draw/aggregates/convert.py#L126`
- Código afetado: `caffmob_draw/aggregates/convert.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 2 (checagem de descendência) (BUG-20261011-ZKQ7, BUG-20261011-VVEJ); plano em `_reversa_bugs/aggregates/bugs/BUG-20261011-ZKQ7-checagem-de-descendencia-invertida-em-can-convert/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** o 3º teste de `can_convert` estava invertido (`obj in parent.children_recursive`); a peça filha do pai era recusada e o pai descendente do objeto passava, gerando agregado sem pai (o Blender 5.2 recusa o ciclo em silêncio).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: RN-05 e questions.md pergunta 3 já definiam o teste certo.
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

- Item 21 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
