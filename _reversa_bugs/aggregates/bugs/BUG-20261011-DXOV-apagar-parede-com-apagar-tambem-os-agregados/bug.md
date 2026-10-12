---
schema_version: 1
id: BUG-20261011-DXOV
display_number: 14
title: "Apagar parede com 'Apagar também os agregados' ligado não apaga os agregados dos módulos"
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
module: aggregates
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["mesma correção do #13"]

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
    state: confirmed
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/aggregates/edge-cases.md#EC-16", "_reversa_sdd/questions.md#pergunta-2", "_reversa_sdd/questions.md#pergunta-4", "_reversa_sdd/selection/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/selection/component.py", "caffmob_draw/aggregates/ops_aggregate.py"]
  root_cause:
    state: confirmed
    hypothesis: "Mesma causa do #13: a pergunta lista agregados de módulos filhos da parede, mas delete_plan não desce na parede (deletes_subtree falso), então 'ligado' não apaga nada além da parede."
    causal_path:
      - "selection/component.py own_aggregates (pergunta aparece)"
      - "selection/component.py delete_plan/deletes_subtree (parede sai sozinha)"
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

# Apagar parede com 'Apagar também os agregados' ligado não apaga os agregados dos módulos

## Summary

`delete_plan` não desce na parede, então nenhuma das duas respostas do diálogo faz o que promete. Mesma decisão do item 2.

## Expected Behavior

Com a decisão das perguntas 2 e 4 (parar em raízes de módulo e em parede/piso/teto), a pergunta não aparece para agregados de módulos filhos e nenhuma das respostas mexe neles; a resposta dada vale só para os agregados próprios do alvo.

Spec efetiva: `_reversa_sdd/aggregates/edge-cases.md#EC-16`, `_reversa_sdd/questions.md#pergunta-2`, `_reversa_sdd/questions.md#pergunta-4`, `_reversa_sdd/selection/tasks.md#DT-01`.

## Actual Behavior

`delete_plan` não desce na parede, então nenhuma das duas respostas do diálogo faz o que promete. Mesma decisão do item 2.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 3.

## Suspected Area

- `caffmob_draw/selection/component.py`
- `caffmob_draw/aggregates/ops_aggregate.py`

## Acceptance Criteria

- Com a decisão das perguntas 2 e 4 (parar em raízes de módulo e em parede/piso/teto), a pergunta não aparece para agregados de módulos filhos e nenhuma das respostas mexe neles; a resposta dada vale só para os agregados próprios do alvo.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/edge-cases.md#EC-16`, `_reversa_sdd/questions.md#pergunta-2`, `_reversa_sdd/questions.md#pergunta-4`, `_reversa_sdd/selection/tasks.md#DT-01`
- Código afetado: `caffmob_draw/selection/component.py`, `caffmob_draw/aggregates/ops_aggregate.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-TUWO (contexto `selection`), state `proposed`

## Resolution

- **Lote:** 1 (exclusão de parede), com #12 BUG-20261011-7DHT, #13 BUG-20261011-TUWO e #14 BUG-20261011-DXOV;
  plano em `_reversa_bugs/selection/bugs/BUG-20261011-7DHT-x-delete-numa-parede-faz-os-filhos/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** mesma do #13: a pergunta listava agregados do módulo filho, mas `delete_plan` não desce na parede.
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

- Item 3 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
