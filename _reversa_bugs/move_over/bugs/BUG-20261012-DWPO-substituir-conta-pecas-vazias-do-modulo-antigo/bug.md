---
schema_version: 1
id: BUG-20261012-DWPO
display_number: 141
title: "Substituir conta peças vazias do módulo antigo e a caixa vai até a origem do mundo"
status: resolved
phase: delivering
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

change_risk:
  classification: baixa
  reasons: ["só a caixa do Substituir muda, para a mesma do Mover Sobre", "módulos sem peças vazias têm a mesma caixa de antes"]

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
  root_cause:
    state: confirmed
    hypothesis: "ops_substitute._tree_box juntava a caixa de toda malha visível da árvore, inclusive peças vazias do frameless (Top e Sink Apron desligados, caixa num ponto na origem do mundo); a caixa de A ia até a origem e o canto de encosto saía errado."
    causal_path:
      - "move_over/ops_substitute.py _tree_box/_box_in"
      - "move_over/ops_substitute.py substitute (side_of, dx)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/move_over/ops_substitute.py, symbol: _tree_box, commit: feaeeb3}
  reproduction_tests: ["tests/blender_bug_DWPO_substitute.py"]
  regression_tests: ["tests/blender_bug_DWPO_substitute.py", "tests/blender_003_move_over_smoke.py", "tests/blender_bug_LWF6_move_over.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_DWPO_substitute.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/move_over/bugs/BUG-20261012-DWPO-substituir-conta-pecas-vazias-do-modulo-antigo/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/move_over/ops_substitute.py
    purpose: "caixa pelo tree_corners"
    diff: _reversa_bugs/move_over/bugs/BUG-20261012-DWPO-substituir-conta-pecas-vazias-do-modulo-antigo/fix/CHG-002.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
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

- **Lote:** 34 (Substituir sem peças vazias) (BUG-20261012-DWPO); plano em `_reversa_bugs/move_over/bugs/BUG-20261012-DWPO-substituir-conta-pecas-vazias-do-modulo-antigo/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** ops_substitute._tree_box juntava a caixa de toda malha visível da árvore, inclusive peças vazias do frameless (Top e Sink Apron desligados, caixa num ponto na origem do mundo); a caixa de A ia até a origem e o canto de encosto saía errado.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-12):** `spec-correta`: move_over RN-19, DT-02 e questions.md pergunta 16 (Substituir, alinhamento e sobreposição com a mesma caixa).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_DWPO_substitute.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/move_over/ops_substitute.py` | caixa pelo tree_corners | `CHG-002.diff` |

**Vermelho (antes da correção):** caixa do balcão em x 0,000 a 5,914; canto do antigo calculado em −5,0 e o novo encostado em 2,0.

**Verde (depois):** `blender_bug_DWPO_substitute.py` OK; na cópia isolada também `blender_003_move_over_smoke` e `blender_bug_LWF6_move_over`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_DWPO_substitute.py`. **Regressão:** `tests/blender_bug_DWPO_substitute.py`, `tests/blender_003_move_over_smoke.py`, `tests/blender_bug_LWF6_move_over.py`.

## Agent Notes

- Item 4 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade medium/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
