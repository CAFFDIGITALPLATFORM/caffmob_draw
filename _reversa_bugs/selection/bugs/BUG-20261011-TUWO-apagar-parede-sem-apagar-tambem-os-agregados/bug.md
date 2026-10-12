---
schema_version: 1
id: BUG-20261011-TUWO
display_number: 13
title: "Apagar parede sem 'Apagar também os agregados' solta os agregados dos módulos que ficam"
status: resolved
phase: delivering
severity: critical
priority: P0
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: selection
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["só a lista da pergunta 'O objeto tem agregados'", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/selection/edge-cases.md#EC-07", "_reversa_sdd/selection/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-2", "_reversa_sdd/questions.md#pergunta-4", "_reversa_sdd/aggregates/edge-cases.md#EC-16"]
  affected_code: ["caffmob_draw/selection/component.py", "caffmob_draw/aggregates/ops_aggregate.py"]
  root_cause:
    state: confirmed
    hypothesis: "own_aggregates desce por toda a subárvore do alvo, inclusive quando o alvo é parede/piso/teto (que não leva a subárvore) e através de raízes de módulo; com keep_aggregates, delete_components desconverte agregados de módulos que não são apagados."
    causal_path:
      - "selection/component.py own_aggregates.walk: sem parada em raiz de módulo nem em alvo que não leva a subárvore"
      - "aggregates/ops_aggregate.py delete_components: convert.unconvert em cada own_aggregates(target)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sonda no Blender 5.2 reproduz salto, desconversão e diálogo inócuo"
    code_refs:
      - {file: caffmob_draw/selection/component.py, symbol: own_aggregates, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_7DHT_wall_delete.py"]
  regression_tests: ["tests/test_component_delete.py", "tests/blender_bug_7DHT_wall_delete.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_component_delete.py
    purpose: "own_aggregates de parede e de módulo aninhado"
    diff: _reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_7DHT_wall_delete.py
    purpose: "reprodução e regressão da exclusão de parede"
    diff: _reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/blender_011_component_smoke.py
    purpose: "parede passa a ser do plugin"
    diff: _reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/selection/component.py
    purpose: "own_aggregates para em módulo e em parede/piso/teto"
    diff: _reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/aggregates/ops_aggregate.py
    purpose: "poll assume parede HB; remove_wall; filhos no lugar"
    diff: _reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/CHG-005.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Apagar parede sem 'Apagar também os agregados' solta os agregados dos módulos que ficam

## Summary

`component.own_aggregates(parede)` desce até os módulos da parede, e os agregados de um módulo que não foi apagado viram objetos soltos (desconvertidos).

## Expected Behavior

`own_aggregates` para em raízes de módulo e em parede, piso e teto: agregados de módulos filhos não entram na pergunta 'O objeto tem agregados' nem são desconvertidos.

Spec efetiva: `_reversa_sdd/selection/edge-cases.md#EC-07`, `_reversa_sdd/selection/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-2`, `_reversa_sdd/questions.md#pergunta-4`, `_reversa_sdd/aggregates/edge-cases.md#EC-16`.

## Actual Behavior

`component.own_aggregates(parede)` desce até os módulos da parede, e os agregados de um módulo que não foi apagado viram objetos soltos (desconvertidos).

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 2.

## Suspected Area

- `caffmob_draw/selection/component.py`
- `caffmob_draw/aggregates/ops_aggregate.py`

## Acceptance Criteria

- `own_aggregates` para em raízes de módulo e em parede, piso e teto: agregados de módulos filhos não entram na pergunta 'O objeto tem agregados' nem são desconvertidos.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/selection/edge-cases.md#EC-07`, `_reversa_sdd/selection/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-2`, `_reversa_sdd/questions.md#pergunta-4`, `_reversa_sdd/aggregates/edge-cases.md#EC-16`
- Código afetado: `caffmob_draw/selection/component.py`, `caffmob_draw/aggregates/ops_aggregate.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 1 (exclusão de parede), com #12 BUG-20261011-7DHT, #13 BUG-20261011-TUWO e #14 BUG-20261011-DXOV;
  plano em `_reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `own_aggregates` descia em parede/piso/teto e em módulos filhos; `delete_components` desconvertia agregados de módulos que ficavam.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: a decisão das perguntas 2 e 4 já estava em `selection/requirements.md`, aggregates EC-16 e DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_component_delete.py` | own_aggregates de parede e de módulo aninhado | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_7DHT_wall_delete.py` | reprodução e regressão da exclusão de parede | `CHG-002.diff` |
| CHG-003 | test | `tests/blender_011_component_smoke.py` | parede passa a ser do plugin | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/selection/component.py` | own_aggregates para em módulo e em parede/piso/teto | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/aggregates/ops_aggregate.py` | poll assume parede HB; remove_wall; filhos no lugar | `CHG-005.diff` |

**Vermelho (antes do CHG-004/005):** `test_component_delete` falhou (`own_aggregates(wall)` = `[Fruteira]`);
`blender_bug_7DHT_wall_delete` com 8 falhas (poll falso na parede, porta órfã, geo 1,811 m e balcão 2,236 m de
salto, Fruteira desconvertida, pergunta listando a Fruteira); `blender_011_component_smoke` falhou em "X numa parede usa
o caminho do plugin".

**Verde (depois):** `test_component_delete` + `test_component_core` 11 OK; `blender_bug_7DHT_wall_delete: OK`;
`blender_011_component_smoke: OK`; sem regressão em `blender_003_aggregates_smoke`, `blender_012_convert_smoke`,
`blender_004_stick_smoke`, `blender_009_walls_smoke`. `ruff` limpo; `check_api.py` sem API desconhecida no 5.2.

- **Reprodução:** `tests/blender_bug_7DHT_wall_delete.py`. **Regressão:** `tests/test_component_delete.py`,
  `tests/blender_011_component_smoke.py`, `tests/blender_bug_7DHT_wall_delete.py`.

## Agent Notes

- Item 2 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `selection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
