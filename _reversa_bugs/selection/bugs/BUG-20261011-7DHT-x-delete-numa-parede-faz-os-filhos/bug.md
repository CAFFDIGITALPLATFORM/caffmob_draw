---
schema_version: 1
id: BUG-20261011-7DHT
display_number: 12
title: "X/Delete numa parede faz os filhos não grudados pularem de lugar"
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
  classification: média
  reasons: ["muda o que X/Delete faz em parede (tecla global do modo objeto)", "sem dado persistido nem contrato externo", "reversível por Ctrl+Z (operador com UNDO)"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-TUWO
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/selection/edge-cases.md#EC-18", "_reversa_sdd/selection/tasks.md#DT-05", "_reversa_sdd/questions.md#pergunta-5"]
  affected_code: ["caffmob_draw/selection/component.py", "caffmob_draw/aggregates/ops_aggregate.py", "caffmob_draw/operators/ops_wall_extras.py"]
  root_cause:
    state: confirmed
    hypothesis: "delete_components trata parede como qualquer alvo: batch_remove apaga a parede sem soltar os filhos com a matriz de mundo e sem a regra KEEP_WITH_WALL; e o poll só assume a parede quando há agregado ou grudado, deixando o resto para o Delete nativo, que deixa portas e janelas órfãs."
    causal_path:
      - "aggregates/ops_aggregate.py BTM_OT_DeleteWithAggregates.poll: parede só passa com agregado/grudado"
      - "aggregates/ops_aggregate.py delete_components: bpy.data.batch_remove(plan.remove) sem reparentar filhos que ficam"
      - "operators/ops_wall_extras.py remove_wall: caminho correto (KEEP_WITH_WALL + matriz) não é usado"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sonda no Blender 5.2 reproduz salto, desconversão e diálogo inócuo"
    code_refs:
      - {file: caffmob_draw/aggregates/ops_aggregate.py, symbol: delete_components, commit: 83a6863}
      - {file: caffmob_draw/aggregates/ops_aggregate.py, symbol: BTM_OT_DeleteWithAggregates.poll, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_7DHT_wall_delete.py"]
  regression_tests: ["tests/blender_bug_7DHT_wall_delete.py", "tests/blender_011_component_smoke.py", "tests/test_component_delete.py"]

spec_verdict: spec-desatualizada

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
  - id: CHG-006
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261011-7DHT-v001.md
    purpose: "relê RN-29 (aggregates) e RN-09 (selection) conforme a pergunta 5"
    diff: _reversa_sdd/addenda/bug-BUG-20261011-7DHT-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# X/Delete numa parede faz os filhos não grudados pularem de lugar

## Summary

Pelo X/Delete do plugin ou pelo Delete nativo, portas, janelas, geometrias e cotas filhas não grudadas perdem o pai e saltam de posição. Uma sonda mostrou um filho indo de (5, 1, 0) para (1, 0, 0). Já `caffmob.wall_remove` e o editor de paredes preservam a posição.

## Expected Behavior

X/Delete numa parede usa `operators/ops_wall_extras.remove_wall` (regra `KEEP_WITH_WALL`): os filhos ficam no lugar com a matriz de mundo preservada, e aberturas, cotas e proxy vão junto, como em `caffmob.wall_remove`.

Spec efetiva: `_reversa_sdd/selection/edge-cases.md#EC-18`, `_reversa_sdd/selection/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-5`.

## Actual Behavior

Pelo X/Delete do plugin ou pelo Delete nativo, portas, janelas, geometrias e cotas filhas não grudadas perdem o pai e saltam de posição. Uma sonda mostrou um filho indo de (5, 1, 0) para (1, 0, 0). Já `caffmob.wall_remove` e o editor de paredes preservam a posição.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 1.

## Suspected Area

- `caffmob_draw/selection/component.py`
- `caffmob_draw/aggregates/ops_aggregate.py`
- `caffmob_draw/operators/ops_wall_extras.py`

## Acceptance Criteria

- X/Delete numa parede usa `operators/ops_wall_extras.remove_wall` (regra `KEEP_WITH_WALL`): os filhos ficam no lugar com a matriz de mundo preservada, e aberturas, cotas e proxy vão junto, como em `caffmob.wall_remove`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/selection/edge-cases.md#EC-18`, `_reversa_sdd/selection/tasks.md#DT-05`, `_reversa_sdd/questions.md#pergunta-5`
- Código afetado: `caffmob_draw/selection/component.py`, `caffmob_draw/aggregates/ops_aggregate.py`, `caffmob_draw/operators/ops_wall_extras.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-TUWO (contexto `selection`), state `proposed`

## Resolution

- **Lote:** 1 (exclusão de parede), com #12 BUG-20261011-7DHT, #13 BUG-20261011-TUWO e #14 BUG-20261011-DXOV;
  plano em `_reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `delete_components` apagava a parede em lote sem soltar os filhos com a matriz de mundo, e o `poll` deixava parede sem agregado para o Delete nativo (porta órfã).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-desatualizada`: adendo `_reversa_sdd/addenda/bug-BUG-20261011-7DHT-v001.md` (RN-29 de aggregates e RN-09 de selection).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_component_delete.py` | own_aggregates de parede e de módulo aninhado | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_7DHT_wall_delete.py` | reprodução e regressão da exclusão de parede | `CHG-002.diff` |
| CHG-003 | test | `tests/blender_011_component_smoke.py` | parede passa a ser do plugin | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/selection/component.py` | own_aggregates para em módulo e em parede/piso/teto | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/aggregates/ops_aggregate.py` | poll assume parede HB; remove_wall; filhos no lugar | `CHG-005.diff` |
| CHG-006 | specification | `_reversa_sdd/addenda/bug-BUG-20261011-7DHT-v001.md` | relê RN-29 e RN-09 | adendo |

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

- Item 1 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `selection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
