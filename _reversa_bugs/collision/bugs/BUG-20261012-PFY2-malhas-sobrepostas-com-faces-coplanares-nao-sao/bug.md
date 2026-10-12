---
schema_version: 1
id: BUG-20261012-PFY2
display_number: 140
title: "Malhas sobrepostas com faces coplanares não são confirmadas pela BVH da colisão"
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-10-12
updated: 2026-10-12

origin:
  type: inspection
  external_ref: null

area: modulos
module: collision
feature: unclassified
labels: ["achado-lateral-fix-2026-10", "reproduzido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-EWKD
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/collision/requirements.md#RN-09"]
  affected_code: ["caffmob_draw/collision/scan.py"]
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---

# Malhas sobrepostas com faces coplanares não são confirmadas pela BVH da colisão

## Summary

Dois cubos de 1 m soltos (malhas sem pai, confirmados pela malha real) com a mesma altura e profundidade, sobrepostos em X, só viram colisão quando a sobreposição é grande (0,5 m). Com 0,2, 0,1 ou 0,05 m a verificação não acusa nada, embora `BVHTree.FromObject` ache 2 pares em todos os casos. O `_Meshes._build` monta a BVH por `BVHTree.FromPolygons` com os quads; o caso coplanar escapa.

## Expected Behavior

Par fino que se sobrepõe de fato vira ocorrência (RN-09), também quando as faces de cima, de baixo e laterais são coplanares.

Spec efetiva: `_reversa_sdd/collision/requirements.md#RN-09`.

## Actual Behavior

Dois cubos de 1 m soltos (malhas sem pai, confirmados pela malha real) com a mesma altura e profundidade, sobrepostos em X, só viram colisão quando a sobreposição é grande (0,5 m). Com 0,2, 0,1 ou 0,05 m a verificação não acusa nada, embora `BVHTree.FromObject` ache 2 pares em todos os casos. O `_Meshes._build` monta a BVH por `BVHTree.FromPolygons` com os quads; o caso coplanar escapa.

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 3.

## Suspected Area

- `caffmob_draw/collision/scan.py`

## Acceptance Criteria

- Par fino que se sobrepõe de fato vira ocorrência (RN-09), também quando as faces de cima, de baixo e laterais são coplanares.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/requirements.md#RN-09`
- Código afetado: `caffmob_draw/collision/scan.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-EWKD (contexto `collision`, travado), state `proposed`

## Resolution

_Pendente._

## Agent Notes

- Item 3 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade medium/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
