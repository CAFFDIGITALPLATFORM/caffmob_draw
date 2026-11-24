---
schema_version: 1
id: BUG-20261124-3Q9X
display_number: 157
title: Plano de corte quebra em parte sem grain_angle
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-11-24
updated: 2026-11-24

origin:
  type: inspection
  external_ref: null

area: producao
module: cutting
feature: unclassified
labels: [spec-gap, compatibilidade, veio]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/cutting/requirements.md#R-03"]
  affected_code: ["caffmob_draw/cutting/part_sources.py"]
  root_cause:
    state: confirmed
    hypothesis: "O adaptador ARMARIO_V2 lê `parte.grain_angle` diretamente; fontes antigas ou fixtures sem essa propriedade quebram a extração, embora `part_roles.grain_direction` já trate o campo como opcional."
    causal_path:
      - "part_sources.armario_v2_records monta PartRecord"
      - "parte.grain_angle sem getattr"
      - "AttributeError em objeto sem o campo"
    evidence:
      - ref: "evidence/suite-antes.log"
        observation: "tests/test_017_corte.py: AttributeError: '_Parte' object has no attribute 'grain_angle'"
    code_refs:
      - file: "caffmob_draw/cutting/part_sources.py"
        symbol: "armario_v2_records"
        commit: null
  reproduction_tests: ["tests/test_017_corte.py"]
  regression_tests: ["tests/test_017_corte.py", "tests/test_cutting_*"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/cutting/part_sources.py"
    purpose: "ler grain_angle com getattr e assumir 0.0 quando a fonte não tem o campo"
    diff: "fix/CHG-001.diff"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Plano de corte quebra em parte sem grain_angle

## Summary

A extração de chapas do armário v2 acessava `parte.grain_angle` sem tolerância. Objetos de fontes antigas, ou fixtures que reproduzem o formato antigo, não têm o campo e a extração inteira falhava.

## Expected Behavior

A orientação do veio é lida quando existe; sem o campo, vale o padrão 0.0, como já faz `part_roles.grain_direction`.

## Actual Behavior

`AttributeError: '_Parte' object has no attribute 'grain_angle'` em `tests/test_017_corte.py`.

## Steps to Reproduce

1. `python3 tests/test_017_corte.py`.

## Evidence

- `evidence/suite-antes.log`

## Suspected Area

`caffmob_draw/cutting/part_sources.py`, adaptador ARMARIO_V2.

## Acceptance Criteria

- [x] Fonte sem `grain_angle` produz o plano com veio 0.0.
- [x] `tests/test_017_corte.py` passa.

## Traceability

Spec de veio em `_reversa_sdd/cutting/requirements.md#R-03`; tolerância a fonte antiga não estava especificada (`spec-gap`).

## Resolution

Causa confirmada: acesso direto ao campo opcional. Correção de uma linha com `getattr(parte, 'grain_angle', 0.0)`. Suíte pura completa verde.

## Agent Notes

Manter o mesmo padrão de leitura tolerante usado em `part_roles.grain_direction`.
