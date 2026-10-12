---
schema_version: 1
id: BUG-20261011-QP4R
display_number: 93
title: "Malhas e materiais inseridos somem ao recarregar"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: modulos
module: object_library
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["nenhuma mudança de código"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "0/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/object_library/edge-cases.md#EC-07"]
  affected_code: ["caffmob_draw/object_library/item_io.py", "caffmob_draw/object_library/ops.py"]
  root_cause:
    state: rejected
    hypothesis: "Malhas e materiais inseridos sem fake user somem ao salvar e recarregar."
    causal_path:
      - "object_library/item_io.py insert: use_fake_user=False só nos objetos"
    evidence:
      - ref: evidence/reproduction.md
        observation: "após salvar e recarregar, 3/3 objetos, 2/2 malhas e 2/2 materiais continuam"
    code_refs:
      - {file: caffmob_draw/object_library/item_io.py, symbol: insert, commit: c989c10}
  reproduction_tests: []
  regression_tests: []

spec_verdict: spec-correta

change_set: []

closure:
  policy: local-software
  satisfied: true
resolution_kind: invalid
---

# Malhas e materiais inseridos somem ao recarregar

## Summary

Chegam sem fake user e não ficam no arquivo depois de salvar e recarregar.

## Expected Behavior

O que foi inserido continua no arquivo depois de salvar e recarregar.

Spec efetiva: `_reversa_sdd/object_library/edge-cases.md#EC-07`.

## Actual Behavior

Chegam sem fake user e não ficam no arquivo depois de salvar e recarregar.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 82.

## Suspected Area

- `caffmob_draw/object_library/item_io.py`
- `caffmob_draw/object_library/ops.py`

## Acceptance Criteria

- O que foi inserido continua no arquivo depois de salvar e recarregar.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/object_library/edge-cases.md#EC-07`
- Código afetado: `caffmob_draw/object_library/item_io.py`, `caffmob_draw/object_library/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 28 (biblioteca de objetos); sonda em `evidence/reproduction.md`.
- **Causa raiz (rejected):** o inserido é usado pelos objetos ligados à coleção e persiste ao salvar e recarregar; sem fake
  user só os dados de uma inserção cancelada (Esc ou `cancel()`) ficam órfãos e somem ao recarregar, o que é a limpeza
  esperada.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11, aprovação geral dos lotes):** `spec-correta`: EC-07
  revisado já registra que os dados indiretos chegam sem fake user e só os órfãos somem.
- **resolution_kind:** invalid. Nenhuma mudança de código.

## Agent Notes

- Item 82 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `object_library`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
