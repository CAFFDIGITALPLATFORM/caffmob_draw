---
schema_version: 1
id: BUG-20261011-53DV
display_number: 48
title: "Colisão falsa entre folha e caixa da porta/janela ou parede (a confirmar)"
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
module: collision
feature: unclassified
labels: ["revisao-specs-2026-10", "a-confirmar"]

change_risk:
  classification: média
  reasons: ["desconverter muda de comportamento (fica no lugar)", "colisão das folhas de porta/janela real", "smoke 003 ajustado para a decisão da pergunta 27"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-VPY5
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/collision/edge-cases.md#EC-22", "_reversa_sdd/collision/tasks.md#DT-90"]
  affected_code: ["caffmob_draw/collision/rules.py", "caffmob_draw/aggregates/collision.py"]
  root_cause:
    state: confirmed
    hypothesis: "A folha LEAF da porta/janela real só era ligada ao grupo FRAME; a caixa da abertura e a parede dela entravam na colisão."
    causal_path:
      - "collision/scan.py _links: só parent_ref e a raiz dele"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/collision/scan.py, symbol: _links, commit: 4431333}
  reproduction_tests: ["tests/blender_bug_NQ2L_aggregates.py", "tests/blender_003_aggregates_smoke.py"]
  regression_tests: ["tests/blender_bug_NQ2L_aggregates.py", "tests/blender_003_aggregates_smoke.py", "tests/blender_007_window_smoke.py", "tests/blender_004_collision_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_003_aggregates_smoke.py
    purpose: "desconverter fica onde está (pergunta 27)"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_NQ2L_aggregates.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/aggregates/apply.py
    purpose: "caixa de pai Empty"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/aggregates/collision.py
    purpose: "exclusão sem módulo"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/aggregates/convert.py
    purpose: "unconvert mantém a posição atual"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/aggregates/install.py
    purpose: "esquadria sem peças"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/aggregates/leaf.py
    purpose: "ícone do pivô"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/aggregates/ops_install.py
    purpose: "parede BTM chega ao aviso"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-008.diff
  - id: CHG-009
    kind: code
    artifact: caffmob_draw/aggregates/props.py
    purpose: "fecha e reabre pela varredura"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-009.diff
  - id: CHG-010
    kind: code
    artifact: caffmob_draw/collision/scan.py
    purpose: "folha ligada à abertura e à parede"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-010.diff
  - id: CHG-011
    kind: code
    artifact: caffmob_draw/data/translations/aggregates.json
    purpose: "mensagem da esquadria vazia"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/CHG-011.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Colisão falsa entre folha e caixa da porta/janela ou parede (a confirmar)

## Summary

Pela leitura do código, folha aberta × caixa da porta/janela e folha × parede não são excluídas da colisão. Rodar a sonda com porta real a 90° e janela instalada.

## Expected Behavior

Folha aberta não colide com a própria caixa da porta/janela nem com a parede que a hospeda.

Spec efetiva: `_reversa_sdd/collision/edge-cases.md#EC-22`, `_reversa_sdd/collision/tasks.md#DT-90`.

## Actual Behavior

Pela leitura do código, folha aberta × caixa da porta/janela e folha × parede não são excluídas da colisão. Rodar a sonda com porta real a 90° e janela instalada.

## Steps to Reproduce

A confirmar. Pelo relato, rodar uma sonda no Blender 5.2 (`xvfb-run /opt/blender/blender --background --factory-startup --python <sonda>`) que monte o cenário descrito em Actual Behavior.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 37.

## Suspected Area

- `caffmob_draw/collision/rules.py`
- `caffmob_draw/aggregates/collision.py`

## Acceptance Criteria

- Folha aberta não colide com a própria caixa da porta/janela nem com a parede que a hospeda.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/edge-cases.md#EC-22`, `_reversa_sdd/collision/tasks.md#DT-90`
- Código afetado: `caffmob_draw/collision/rules.py`, `caffmob_draw/aggregates/collision.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-VPY5 (contexto `aggregates`), state `proposed`

## Resolution

- **Lote:** 21 (agregados e folhas) (BUG-20261011-NQ2L, BUG-20261011-VPY5, BUG-20261011-I7QE, BUG-20261011-PON4, BUG-20261011-4OV4, BUG-20261011-MQPR, BUG-20261011-5DDZ, BUG-20261011-53DV); plano em `_reversa_bugs/aggregates/bugs/BUG-20261011-NQ2L-desconverter-depois-de-mover-o-pai-deixa/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** A folha LEAF da porta/janela real só era ligada ao grupo FRAME; a caixa da abertura e a parede dela entravam na colisão.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 68 e collision DT-90 (sonda confirmou a colisão falsa).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_003_aggregates_smoke.py` | desconverter fica onde está (pergunta 27) | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_NQ2L_aggregates.py` | reprodução e regressão | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/aggregates/apply.py` | caixa de pai Empty | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/aggregates/collision.py` | exclusão sem módulo | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/aggregates/convert.py` | unconvert mantém a posição atual | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/aggregates/install.py` | esquadria sem peças | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/aggregates/leaf.py` | ícone do pivô | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/aggregates/ops_install.py` | parede BTM chega ao aviso | `CHG-008.diff` |
| CHG-009 | code | `caffmob_draw/aggregates/props.py` | fecha e reabre pela varredura | `CHG-009.diff` |
| CHG-010 | code | `caffmob_draw/collision/scan.py` | folha ligada à abertura e à parede | `CHG-010.diff` |
| CHG-011 | code | `caffmob_draw/data/translations/aggregates.json` | mensagem da esquadria vazia | `CHG-011.diff` |

**Vermelho (antes da correção):** oito cenários falham: posição ao desconverter, exclusão larga, folha que atravessa obstáculo, caixa de Empty nula, TypeError na esquadria vazia, ícone do pivô, mensagem da parede, colisão falsa da folha.

**Verde (depois):** `blender_bug_NQ2L_aggregates.py` OK, `blender_003_aggregates_smoke.py` OK; na cópia isolada também `blender_004_collision_smoke`, `blender_007_window_smoke`, `blender_bug_MMVI_opening_sync`, `blender_bug_7DHT_wall_delete`, `blender_012_convert_smoke`, `blender_012_groups_smoke`, `blender_004_stick_smoke`, `blender_009_skp_smoke`, `blender_010_skp_tree_smoke`, `test_collision_rules`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_NQ2L_aggregates.py`, `tests/blender_003_aggregates_smoke.py`. **Regressão:** `tests/blender_bug_NQ2L_aggregates.py`, `tests/blender_003_aggregates_smoke.py`, `tests/blender_007_window_smoke.py`, `tests/blender_004_collision_smoke.py`.

## Agent Notes

- Item 37 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `collision`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
