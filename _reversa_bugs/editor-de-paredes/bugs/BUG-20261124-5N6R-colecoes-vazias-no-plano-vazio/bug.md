---
schema_version: 1
id: BUG-20261124-5N6R
display_number: 159
title: Plano vazio recria Arquitetura com Piso e Teto vazios
status: resolved
phase: delivering
severity: medium
priority: P1
created: 2026-11-24
updated: 2026-11-24

origin:
  type: inspection
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [regressao, colecoes, camadas]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-4MF7
    type: regression-of
    state: confirmed
    evidence: ["tests/blender_bug_4MF7_colecoes.py#6 volta a falhar", "evidence/antes.log"]

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-08", "_reversa_sdd/addenda/bug-BUG-20261117-4MF7-v001.md"]
  affected_code: ["caffmob_draw/walls2d/apply.py"]
  root_cause:
    state: confirmed
    hypothesis: "`refresh_floors_and_ceilings` chamava `ensure_arquitetura` para Piso e Teto antes de saber se havia piso ou teto para colocar. Um plano vazio recriava `Arquitetura` vazia, violando a regra de não criar coleção órfã."
    causal_path:
      - "apply_plan([]) chama refresh_floors_and_ceilings"
      - "ensure_arquitetura(scene, 'FLOOR') e 'CEILING' criam Arquitetura > Piso/Teto"
      - "assert de nenhuma coleção Arquitetura/Parede falha"
    evidence:
      - ref: "evidence/antes.log"
        observation: "AssertionError na etapa 6 do teste 4MF7"
    code_refs:
      - file: "caffmob_draw/walls2d/apply.py"
        symbol: "refresh_floors_and_ceilings"
        commit: null
  reproduction_tests: ["tests/blender_bug_4MF7_colecoes.py"]
  regression_tests: ["tests/blender_bug_4MF7_colecoes.py", "tests/blender_065_walls2d_v2.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/walls2d/apply.py"
    purpose: "criar as coleções Piso/Teto só ao colocar o primeiro objeto"
    diff: "fix/CHG-001.diff"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Plano vazio recria Arquitetura com Piso e Teto vazios

## Summary

A organização em camadas da feature 021 passou a criar `Arquitetura > Piso` e `Arquitetura > Teto` sempre que `apply_plan` rodava, mesmo sem nenhum piso, teto ou parede. Um plano vazio deixava coleções órfãs e quebrava a regressão do BUG-20261117-4MF7.

## Expected Behavior

Coleções nascem sob demanda, apenas quando há objeto para colocar nelas; OK sem parede nenhuma não cria coleção vazia.

## Actual Behavior

`tests/blender_bug_4MF7_colecoes.py` falhava no passo 6: `any(c.name in (ARQUITETURA, PAREDE))` ainda era verdadeiro.

## Steps to Reproduce

1. `blender --background --factory-startup --python tests/blender_bug_4MF7_colecoes.py`.

## Evidence

- `evidence/antes.log`

## Suspected Area

`caffmob_draw/walls2d/apply.py`, `refresh_floors_and_ceilings`.

## Acceptance Criteria

- [x] Plano vazio não cria `Arquitetura`, `Piso` nem `Teto`.
- [x] Piso/teto existentes continuam organizados nas subcoleções.
- [x] Teste 4MF7 completo passa.

## Traceability

Spec `_reversa_sdd/walls2d/requirements.md#RF-08` e adendo do 4MF7. Regressão confirmada do bug travado.

## Resolution

Causa confirmada: `ensure_arquitetura` era chamado incondicionalmente. Correção: criação preguiçosa dentro dos laços, no primeiro objeto de cada tipo. Teste 4MF7 passou inteiro.

## Agent Notes

Não voltar a criar coleções fora dos laços; a regra do adendo é "nenhuma pasta vazia".
