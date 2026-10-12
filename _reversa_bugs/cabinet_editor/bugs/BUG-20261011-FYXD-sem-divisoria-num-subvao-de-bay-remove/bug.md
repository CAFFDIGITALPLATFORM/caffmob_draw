---
schema_version: 1
id: BUG-20261011-FYXD
display_number: 71
title: "'Sem Divisória' num subvão de bay remove a bay sem aviso"
status: resolved
phase: delivering
severity: low
priority: P3
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
  classification: média
  reasons: ["editor de armário: várias ações passam a recusar com mensagem", "eletro de 560 mm passa a não caber em vão de 535 mm de profundidade (testes puros ajustados)"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/cabinet_editor/edge-cases.md#EC-20"]
  affected_code: ["caffmob_draw/cabinet_editor/bays.py", "caffmob_draw/cabinet_editor/divisions.py"]
  root_cause:
    state: confirmed
    hypothesis: "remove_in_space removia a divisória de vão (bay) como qualquer outra, sem aviso."
    causal_path:
      - "cabinet_editor/bridge.py remove_in_space"
      - "cabinet_editor/divisions.py remove_in_space"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/cabinet_editor/bridge.py, symbol: remove_in_space, commit: 166ff1b}
  reproduction_tests: ["tests/blender_bug_5R7U_cabinet_editor.py", "tests/test_cabinet_appliances.py", "tests/test_cabinet_catalog.py"]
  regression_tests: ["tests/blender_bug_5R7U_cabinet_editor.py", "tests/test_cabinet_appliances.py", "tests/test_cabinet_catalog.py", "tests/blender_008_construtor_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_5R7U_cabinet_editor.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_cabinet_appliances.py
    purpose: "forno embaixo e profundidade"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/test_cabinet_catalog.py
    purpose: "profundidade no cabe"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/cabinet_editor/appliances.py
    purpose: "ordem dos eletros"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/cabinet_editor/bridge.py
    purpose: "recusas e apply_state enxuto"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/cabinet_editor/catalog.py
    purpose: "profundidade no too_small"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/cabinet_editor/ops_actions.py
    purpose: "recuo de 15 mm e item da aba"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/data/translations/cabinet_editor.json
    purpose: "mensagens novas"
    diff: _reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/CHG-008.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# 'Sem Divisória' num subvão de bay remove a bay sem aviso

## Summary

"Sem Divisória" num subvão de bay remove a bay sem aviso.

## Expected Behavior

A remoção da bay é avisada (ou recusada).

Spec efetiva: `_reversa_sdd/cabinet_editor/edge-cases.md#EC-20`.

## Actual Behavior

"Sem Divisória" num subvão de bay remove a bay sem aviso.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 60.

## Suspected Area

- `caffmob_draw/cabinet_editor/bays.py`
- `caffmob_draw/cabinet_editor/divisions.py`

## Acceptance Criteria

- A remoção da bay é avisada (ou recusada).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cabinet_editor/edge-cases.md#EC-20`
- Código afetado: `caffmob_draw/cabinet_editor/bays.py`, `caffmob_draw/cabinet_editor/divisions.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 24 (editor de armário) (BUG-20261011-5R7U, BUG-20261011-FHQN, BUG-20261011-HF2J, BUG-20261011-HVYM, BUG-20261011-HR3U, BUG-20261011-TFC7, BUG-20261011-HLV6, BUG-20261011-FYXD); plano em `_reversa_bugs/cabinet_editor/bugs/BUG-20261011-5R7U-mudar-o-numero-de-vaos-com-s0/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** remove_in_space removia a divisória de vão (bay) como qualquer outra, sem aviso.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: cabinet_editor EC-20.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_5R7U_cabinet_editor.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | test | `tests/test_cabinet_appliances.py` | forno embaixo e profundidade | `CHG-002.diff` |
| CHG-003 | test | `tests/test_cabinet_catalog.py` | profundidade no cabe | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/cabinet_editor/appliances.py` | ordem dos eletros | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/cabinet_editor/bridge.py` | recusas e apply_state enxuto | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/cabinet_editor/catalog.py` | profundidade no too_small | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/cabinet_editor/ops_actions.py` | recuo de 15 mm e item da aba | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/data/translations/cabinet_editor.json` | mensagens novas | `CHG-008.diff` |

**Vermelho (antes da correção):** Número de vãos aceito com s0 cortado; deslizantes esbarram na divisória de vão; recuo de trás ignorado; item de outra aba aceito; 7 objetos recriados pelo apply_state; bay removida sem aviso; micro embaixo; forno cabendo em vão raso.

**Verde (depois):** `blender_bug_5R7U_cabinet_editor.py` OK, `test_cabinet_appliances.py` OK, `test_cabinet_catalog.py` OK; na cópia isolada também `test_cabinet_bays`, `test_cabinet_editor_divisions`, `test_cabinet_slides`, `test_i18n_coverage`, `blender_bug_6JIM_cabinet_queue`, `blender_bug_35HE_i18n`, `blender_012_cabinet_standard_smoke` e, com janela, `blender_004_cabinet_editor_smoke`, `blender_006_cabinet_editor_tabs_smoke`, `blender_008_construtor_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_5R7U_cabinet_editor.py`, `tests/test_cabinet_appliances.py`, `tests/test_cabinet_catalog.py`. **Regressão:** `tests/blender_bug_5R7U_cabinet_editor.py`, `tests/test_cabinet_appliances.py`, `tests/test_cabinet_catalog.py`, `tests/blender_008_construtor_smoke.py`.

## Agent Notes

- Item 60 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `cabinet_editor`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
