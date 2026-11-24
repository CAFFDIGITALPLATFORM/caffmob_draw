---
schema_version: 1
id: BUG-20261124-2C8T
display_number: 160
title: Redimensionar módulo das 5 famílias não adapta os agregados
status: resolved
phase: delivering
severity: medium
priority: P1
created: 2026-11-24
updated: 2026-11-24

origin:
  type: inspection
  external_ref: null

area: modulos
module: selection
feature: unclassified
labels: [regressao, redimensionar, agregados]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/selection/requirements.md#RN-24", "_reversa_sdd/selection/requirements.md#RF-12"]
  affected_code: ["caffmob_draw/selection/resize.py"]
  root_cause:
    state: confirmed
    hypothesis: "A feature 080 mandou os módulos das 5 famílias direto para `editing.set_dimension`, sem passar pelo trecho de `_resize` que mede e estica os agregados. A transação preserva os agregados, então o Puxador ficou com 0,20 m enquanto o módulo dobrou de largura."
    causal_path:
      - "resize.resize vê module_resize.handles(info)"
      - "retorna editing.set_dimension sem _resize"
      - "o trecho de adaptação de agregados não roda"
      - "agregado mantém size 0,20 e u antigo"
    evidence:
      - ref: "evidence/antes.log"
        observation: "agregado esticado (0.2, 0.2) e malha com 0,20 m após módulo de 1,8288 m"
    code_refs:
      - file: "caffmob_draw/selection/resize.py"
        symbol: "resize"
        commit: null
  reproduction_tests: ["tests/blender_toast_resize_invert.py"]
  regression_tests: ["tests/blender_toast_resize_invert.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/selection/resize.py"
    purpose: "guardar o estado dos agregados antes da transação e adaptá-los depois, também no caminho direto"
    diff: "fix/CHG-001.diff"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Redimensionar módulo das 5 famílias não adapta os agregados

## Summary

O Redimensionar de um módulo passou a chamar a transação da feature 080 diretamente. A transação preserva os agregados sem esticá-los, então o Puxador na frente do balcão continuou com 0,20 m e na posição antiga depois de o módulo dobrar de largura.

## Expected Behavior

RN-24/RF-12: ao mudar a largura, os agregados são medidos antes e depois, esticados no eixo X do pai e reposicionados na proporção; folhas LEAF não mudam.

## Actual Behavior

`tests/blender_toast_resize_invert.py` falhava em três checagens: agregado esticado, reposicionado e malha com a largura nova.

## Steps to Reproduce

1. `blender --background --factory-startup --python tests/blender_toast_resize_invert.py`.

## Evidence

- `evidence/antes.log`

## Suspected Area

`caffmob_draw/selection/resize.py`, caminho direto de `resize` para `editing.set_dimension`.

## Acceptance Criteria

- [x] Módulo dobra e o agregado dobra junto.
- [x] O agregado é reposicionado na proporção.
- [x] A malha do agregado acompanha a largura.

## Traceability

Spec `_reversa_sdd/selection/requirements.md#RN-24` e `#RF-12`.

## Resolution

Causa confirmada: o caminho novo pulava a adaptação. Correção: extrair `_aggregate_state`/`_resize_aggregates` e chamá-los também no caminho direto, mantendo `_resize` igual. Teste do aviso/Redimensionar passou inteiro.

## Agent Notes

A transação 080 continua atômica; a adaptação roda depois dela, com o mesmo estado medido antes.
