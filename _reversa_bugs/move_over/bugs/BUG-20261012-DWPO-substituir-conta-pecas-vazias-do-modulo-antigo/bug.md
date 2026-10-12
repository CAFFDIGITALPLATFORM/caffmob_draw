---
schema_version: 1
id: BUG-20261012-DWPO
display_number: 141
title: "Substituir conta peças vazias do módulo antigo e a caixa vai até a origem do mundo"
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
module: move_over
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
  - bug: BUG-20261011-LWF6
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/move_over/requirements.md#RN-19", "_reversa_sdd/move_over/tasks.md#DT-02", "_reversa_sdd/questions.md#pergunta-16"]
  affected_code: ["caffmob_draw/move_over/ops_substitute.py", "caffmob_draw/move_over/scene.py"]
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

# Substituir conta peças vazias do módulo antigo e a caixa vai até a origem do mundo

## Summary

`ops_substitute._tree_box` usa toda malha visível da árvore do módulo antigo, inclusive peças vazias (no frameless, `Top` e `Sink Apron` desligados têm a caixa num ponto só, na origem do mundo). A caixa de A passa a ir de x = −5,0 a 0,914 para um balcão em x = 5, e o encosto do módulo novo pode sair errado. O `scene.tree_corners` do Mover Sobre já ignora essas peças (BUG-20261011-LWF6).

## Expected Behavior

O Substituir usa a mesma caixa da árvore visível do Mover Sobre, sem peças vazias, como pede a decisão da pergunta 16 (alinhamento, sobreposição e Substituir concordam).

Spec efetiva: `_reversa_sdd/move_over/requirements.md#RN-19`, `_reversa_sdd/move_over/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-16`.

## Actual Behavior

`ops_substitute._tree_box` usa toda malha visível da árvore do módulo antigo, inclusive peças vazias (no frameless, `Top` e `Sink Apron` desligados têm a caixa num ponto só, na origem do mundo). A caixa de A passa a ir de x = −5,0 a 0,914 para um balcão em x = 5, e o encosto do módulo novo pode sair errado. O `scene.tree_corners` do Mover Sobre já ignora essas peças (BUG-20261011-LWF6).

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 4.

## Suspected Area

- `caffmob_draw/move_over/ops_substitute.py`
- `caffmob_draw/move_over/scene.py`

## Acceptance Criteria

- O Substituir usa a mesma caixa da árvore visível do Mover Sobre, sem peças vazias, como pede a decisão da pergunta 16 (alinhamento, sobreposição e Substituir concordam).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/move_over/requirements.md#RN-19`, `_reversa_sdd/move_over/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-16`
- Código afetado: `caffmob_draw/move_over/ops_substitute.py`, `caffmob_draw/move_over/scene.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-LWF6 (contexto `move_over`, travado), state `proposed`

## Resolution

_Pendente._

## Agent Notes

- Item 4 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade medium/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
