---
schema_version: 1
id: BUG-20261011-TRMB
display_number: 61
title: "Sem rollback do editor de armário se a raiz foi apagada"
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
module: cabinet_editor
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["nenhuma mudança de código"]

visibility: normal
security_suspected: false

reproduction:
  classification: not-reproduced
  rate: "0/1 (sem defeito: comportamento definido pela RN-06 revisada)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/cabinet_editor/requirements.md#RN-06", "caffmob_draw/cabinet_editor/ops_editor.py#L275-L279"]
  affected_code: ["caffmob_draw/cabinet_editor/ops_editor.py"]
  root_cause:
    state: rejected
    hypothesis: "Faltaria rollback com a raiz apagada. Refutado: rollback reaplica o instantâneo na raiz; sem raiz não há o que reaplicar, e tudo o que o editor cria (peças, divisórias, deslizantes) é filho da raiz e sai com ela."
    causal_path:
      - "cabinet_editor/scene_parts.py _link: obj.parent = root"
      - "cabinet_editor/scene_divisions.py: obj.parent = root"
      - "cabinet_editor/scene_slides.py: grupo FRAME das peças da raiz"
    evidence:
      - ref: _reversa_sdd/cabinet_editor/requirements.md#RN-06
        observation: "revisão de 2026-10-10 corrigiu RN-06 para 'raiz apagada encerra com WARNING e CANCELLED, sem rollback'"
    code_refs:
      - {file: caffmob_draw/cabinet_editor/ops_editor.py, symbol: rollback, commit: 83a6863}
  reproduction_tests: []
  regression_tests: []

spec_verdict: spec-correta

change_set: []

closure:
  policy: local-software
  satisfied: true
resolution_kind: invalid
---

# Sem rollback do editor de armário se a raiz foi apagada

## Summary

`rollback` exige `s.root()`.

## Expected Behavior

RN-06: o Cancelar desfaz o que o editor criou mesmo se a raiz sumiu.

Spec efetiva: `_reversa_sdd/cabinet_editor/requirements.md#RN-06`, `caffmob_draw/cabinet_editor/ops_editor.py#L275-L279`.

## Actual Behavior

`rollback` exige `s.root()`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 50.

## Suspected Area

- `caffmob_draw/cabinet_editor/ops_editor.py`

## Acceptance Criteria

- RN-06: o Cancelar desfaz o que o editor criou mesmo se a raiz sumiu.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/requirements.md#RN-06`, `caffmob_draw/cabinet_editor/ops_editor.py#L275-L279`
- Código afetado: `caffmob_draw/cabinet_editor/ops_editor.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 12 (fila do editor de armário); plano em `_reversa_bugs/cabinet_editor/bugs/BUG-20261011-6JIM-cancelar-nao-desfaz-a-montagem/fix/plan.html`.
- **Causa raiz (rejected):** a hipótese de rollback faltando foi refutada: sem raiz não há instantâneo a reaplicar e tudo o
  que o editor cria é filho da raiz (ver `evidence/reproduction.md`).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11, aprovação geral dos lotes):** `spec-correta`: a RN-06
  revisada já define "sem rollback" quando a raiz some.
- **resolution_kind:** invalid. Nenhuma mudança de código.

## Agent Notes

- Item 50 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
