---
schema_version: 1
id: BUG-20261011-NTM3
display_number: 81
title: "Dupla contagem de frentes no face frame"
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
labels: ["revisao-specs-2026-10"]

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
  specs: ["_reversa_sdd/legacy/tasks.md#DT-02"]
  affected_code: ["caffmob_draw/legacy/convert_core.py"]
  root_cause:
    state: confirmed
    hypothesis: "_other_fronts somava as gaiolas folha PULLOUT/TILT_OUT/INSET_PANEL que o adaptador já tinha lido como gaveta ou painel."
    causal_path:
      - "legacy/convert.py _other_fronts"
      - "customize/adapters/face_frame.py openings/front_type"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/legacy/convert.py, symbol: _other_fronts, commit: 6d2d9b6}
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

# Dupla contagem de frentes no face frame

## Summary

`_other_fronts` conta de novo PULLOUT/TILT_OUT/INSET_PANEL.

## Expected Behavior

Cada frente conta uma vez.

Spec efetiva: `_reversa_sdd/legacy/tasks.md#DT-02`.

## Actual Behavior

`_other_fronts` conta de novo PULLOUT/TILT_OUT/INSET_PANEL.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 70.

## Suspected Area

- `caffmob_draw/legacy/convert_core.py`

## Acceptance Criteria

- Cada frente conta uma vez.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/legacy/tasks.md#DT-02`
- Código afetado: `caffmob_draw/legacy/convert_core.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 26 (conversão das bibliotecas herdadas) (BUG-20261011-5NLX, BUG-20261011-NTM3, BUG-20261011-HUWF, BUG-20261011-ORRG); plano em `_reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** _other_fronts somava as gaiolas folha PULLOUT/TILT_OUT/INSET_PANEL que o adaptador já tinha lido como gaveta ou painel.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 55 e legacy DT-02.
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

- Item 70 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `legacy`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
