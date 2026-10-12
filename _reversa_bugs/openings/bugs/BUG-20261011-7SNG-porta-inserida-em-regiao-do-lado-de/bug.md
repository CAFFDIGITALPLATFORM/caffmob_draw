---
schema_version: 1
id: BUG-20261011-7SNG
display_number: 123
title: "Porta inserida em região do lado de trás abre invertida"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: openings
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["só a inserção em região BACK muda o giro", "Redimensionar some do menu da janela BTM (antes sempre falhava)"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/openings/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-22"]
  affected_code: ["caffmob_draw/openings/region.py", "caffmob_draw/openings/region_core.py"]
  root_cause:
    state: confirmed
    hypothesis: "place_in_region punha a caixa em y = 0 sem rotação e aplicava o giro escolhido como se a região fosse da frente; o lado (side) só servia para o desenho."
    causal_path:
      - "operators/doors_windows.py place_in_region"
      - "openings/region.py _face_y"
      - "openings/sync.py _swing (Swing Inside = lado −Y)"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/operators/doors_windows.py, symbol: _PlaceWallObjectBase.place_in_region, commit: e884554}
      - {file: caffmob_draw/operators/doors_windows.py, symbol: apply_door_swing_type, commit: e884554}
  reproduction_tests: ["tests/blender_bug_7SNG_openings.py"]
  regression_tests: ["tests/blender_bug_7SNG_openings.py", "tests/blender_011_region_smoke.py", "tests/blender_010_openings_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_7SNG_openings.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/openings/region.py
    purpose: "draw_regions só lê"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/openings/region_props.py
    purpose: "region_wall sem gravar no desenho"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/operators/doors_windows.py
    purpose: "giro espelhado na face de trás"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/selection/resize.py
    purpose: "janela BTM bloqueada"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/CHG-005.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Porta inserida em região do lado de trás abre invertida

## Summary

Numa região `BACK`, a porta é inserida com a abertura invertida.

## Expected Behavior

A porta abre para o lado da face da região (011 RN-11).

Spec efetiva: `_reversa_sdd/openings/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-22`.

## Actual Behavior

Numa região `BACK`, a porta é inserida com a abertura invertida.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 112.

## Suspected Area

- `caffmob_draw/openings/region.py`
- `caffmob_draw/openings/region_core.py`

## Acceptance Criteria

- A porta abre para o lado da face da região (011 RN-11).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/openings/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-22`
- Código afetado: `caffmob_draw/openings/region.py`, `caffmob_draw/openings/region_core.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 30 (aberturas e seleção) (BUG-20261011-7SNG, BUG-20261011-D3GC, BUG-20261011-CHWX); plano em `_reversa_bugs/openings/bugs/BUG-20261011-7SNG-porta-inserida-em-regiao-do-lado-de/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** place_in_region punha a caixa em y = 0 sem rotação e aplicava o giro escolhido como se a região fosse da frente; o lado (side) só servia para o desenho.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: 011 RN-11, questions.md pergunta 22 e openings DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_7SNG_openings.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/openings/region.py` | draw_regions só lê | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/openings/region_props.py` | region_wall sem gravar no desenho | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/operators/doors_windows.py` | giro espelhado na face de trás | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/selection/resize.py` | janela BTM bloqueada | `CHG-005.diff` |

**Vermelho (antes da correção):** Swing Inside verdadeiro na face de trás; o desenho desligou a região; can_resize verdadeiro para a janela BTM.

**Verde (depois):** `blender_bug_7SNG_openings.py` OK; na cópia isolada também `blender_011_region_smoke`, `blender_toast_resize_invert`, `blender_010_openings_smoke` e `blender_bug_TBY3_walls`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_7SNG_openings.py`. **Regressão:** `tests/blender_bug_7SNG_openings.py`, `tests/blender_011_region_smoke.py`, `tests/blender_010_openings_smoke.py`.

## Agent Notes

- Item 112 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `openings`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
