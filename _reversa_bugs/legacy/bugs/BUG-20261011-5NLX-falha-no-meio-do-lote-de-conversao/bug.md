---
schema_version: 1
id: BUG-20261011-5NLX
display_number: 80
title: "Falha no meio do lote de conversão deixa lixo na cena"
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
module: legacy
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

change_risk:
  classification: baixa
  reasons: ["conversão ganha caminho de erro; caminho feliz igual (fumaça 012 verde)", "lista de grupos pode crescer com homônimos, já desempatados no nome salvo"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/legacy/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/legacy/convert.py", "caffmob_draw/legacy/ops.py"]
  root_cause:
    state: confirmed
    hypothesis: "convert_scene criava os módulos um a um sem proteção; uma exceção no meio deixava os já criados (e o parcial) ao lado dos originais e subia como traceback."
    causal_path:
      - "legacy/ops.py LegacyConvert.execute"
      - "legacy/convert.py convert_scene"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/legacy/convert.py, symbol: convert_scene, commit: 6d2d9b6}
      - {file: caffmob_draw/legacy/ops.py, symbol: BTM_OT_LegacyConvert.execute, commit: 6d2d9b6}
  reproduction_tests: ["tests/blender_bug_5NLX_legacy.py"]
  regression_tests: ["tests/blender_bug_5NLX_legacy.py", "tests/blender_012_convert_smoke.py", "tests/test_legacy_convert.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_5NLX_legacy.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/data/translations/library.json
    purpose: "mensagens novas"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/legacy/convert.py
    purpose: "rollback, folhas lidas e leitura falha"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/legacy/convert_core.py
    purpose: "perda Frentes não lidas"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/legacy/groups.py
    purpose: "todos os grupos, sem descarte"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/legacy/ops.py
    purpose: "ERROR e CANCELLED"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Falha no meio do lote de conversão deixa lixo na cena

## Summary

Sai um traceback, e o módulo parcial "BTM_Cabinet" fica ao lado dos originais.

## Expected Behavior

Remover o que foi criado, reportar ERROR e devolver CANCELLED.

Spec efetiva: `_reversa_sdd/legacy/tasks.md#DT-01`.

## Actual Behavior

Sai um traceback, e o módulo parcial "BTM_Cabinet" fica ao lado dos originais.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/legacy.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 69.

## Suspected Area

- `caffmob_draw/legacy/convert.py`
- `caffmob_draw/legacy/ops.py`

## Acceptance Criteria

- Remover o que foi criado, reportar ERROR e devolver CANCELLED.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/legacy/tasks.md#DT-01`
- Código afetado: `caffmob_draw/legacy/convert.py`, `caffmob_draw/legacy/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 26 (conversão das bibliotecas herdadas) (BUG-20261011-5NLX, BUG-20261011-NTM3, BUG-20261011-HUWF, BUG-20261011-ORRG); plano em `_reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** convert_scene criava os módulos um a um sem proteção; uma exceção no meio deixava os já criados (e o parcial) ao lado dos originais e subia como traceback.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 54 e legacy DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_5NLX_legacy.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/data/translations/library.json` | mensagens novas | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/legacy/convert.py` | rollback, folhas lidas e leitura falha | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/legacy/convert_core.py` | perda Frentes não lidas | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/legacy/groups.py` | todos os grupos, sem descarte | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/legacy/ops.py` | ERROR e CANCELLED | `CHG-006.diff` |

**Vermelho (antes da correção):** 8 objetos do lote ficaram na cena e saiu traceback; PULLOUT contou DRAWERS e SPECIAL; 'sem perdas' com o leitor falhando; o homônimo em Cozinha/ sumiu.

**Verde (depois):** `blender_bug_5NLX_legacy.py` OK; na cópia isolada também `blender_012_convert_smoke`, `test_legacy_convert`, `test_legacy_groups` e `test_i18n_coverage`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_5NLX_legacy.py`. **Regressão:** `tests/blender_bug_5NLX_legacy.py`, `tests/blender_012_convert_smoke.py`, `tests/test_legacy_convert.py`.

## Agent Notes

- Item 69 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `legacy`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
