---
schema_version: 1
id: BUG-20261124-8W4D
display_number: 158
title: Janela sem modelo explícito virava de giro em vez de correr
status: resolved
phase: delivering
severity: high
priority: P0
created: 2026-11-24
updated: 2026-11-24

origin:
  type: inspection
  external_ref: null

area: paredes
module: openings
feature: unclassified
labels: [regressao, janela, modelo]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "2/2 testes (010 e 5EX7)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-5EX7
    type: regression-of
    state: confirmed
    evidence: ["tests/blender_bug_5EX7_gizmo.py volta a falhar com curso 0.000 m", "evidence/antes.log"]

traceability:
  specs: ["_reversa_sdd/openings/requirements.md#RF-03"]
  affected_code: ["caffmob_draw/openings/sync.py"]
  root_cause:
    state: confirmed
    hypothesis: "`sync` passava `data.opening_model or None` para `window_parts` e `is_sliding_window`. A janela criada sem modelo explícito virava `None`, que não está em `SLIDING_WINDOW_MODELS`; a montagem caía no ramo SWING e as folhas deixavam de correr."
    causal_path:
      - "oe.make_cage('WINDOW') cria a caixa sem opening_model"
      - "sync: model = data.opening_model or None"
      - "window_core.is_sliding_window(None) é falso"
      - "leaf.make_leaf recebe motion SWING e travel padrão 0.5, não o curso de 0.535"
    evidence:
      - ref: "evidence/antes.log"
        observation: "janela: 2 folhas de correr até o batente (535 mm) [1.087] e 5EX7 curso 0.000 m"
      - ref: "tests/blender_010_openings_smoke.py"
        observation: "após a correção, moved == [0.535, 0.535]"
    code_refs:
      - file: "caffmob_draw/openings/sync.py"
        symbol: "sync"
        commit: "e7a712eb"
  reproduction_tests: ["tests/blender_010_openings_smoke.py", "tests/blender_bug_5EX7_gizmo.py"]
  regression_tests: ["tests/blender_010_openings_smoke.py", "tests/blender_bug_5EX7_gizmo.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/openings/sync.py"
    purpose: "usar janela_correr_2f como modelo padrão da janela sem opening_model"
    diff: "fix/CHG-001.diff"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Janela sem modelo explícito virava de giro em vez de correr

## Summary

Depois da feature 078, a janela só era montada como de correr quando tinha `opening_model` preenchido. Caixas de janela comuns, criadas sem escolher modelo, caíam no ramo de giro: as duas folhas giravam 90° em vez de correr 535 mm até o batente, e o gizmo de inspeção lia curso 0.000 m.

## Expected Behavior

RF-03: a janela é de correr e cada folha percorre o curso até o batente. Sem modelo explícito, vale o modelo histórico `janela_correr_2f`.

## Actual Behavior

`tests/blender_010_openings_smoke.py` media deslocamento 1.087 m e `tests/blender_bug_5EX7_gizmo.py` lia curso 0.0.

## Steps to Reproduce

1. `blender --background --factory-startup --python tests/blender_010_openings_smoke.py`.
2. Observar a falha "janela: 2 folhas de correr até o batente (535 mm)".

## Evidence

- `evidence/antes.log`

## Suspected Area

`caffmob_draw/openings/sync.py`, escolha do modelo em `_parts` e na montagem das folhas.

## Acceptance Criteria

- [x] Janela sem modelo corre 0.535 m por folha.
- [x] O gizmo lê o curso.
- [x] Porta sem modelo continua de giro.

## Traceability

Spec `_reversa_sdd/openings/requirements.md#RF-03`. Regressão confirmada do BUG-20261011-5EX7.

## Resolution

Causa confirmada: `None` era tratado como modelo e não como "usar o padrão". Correção: `data.opening_model or window_core.SLIDING_WINDOW_MODELS[0]` para WINDOW, mantendo `None` para porta. Os dois testes voltaram a passar.

## Agent Notes

Modelos explícitos de abrir/basculante continuam mandando; só o vazio ganhou o padrão histórico.
