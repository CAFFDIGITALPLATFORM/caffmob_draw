---
schema_version: 1
id: BUG-20261011-ORRG
display_number: 83
title: "Grupo homônimo em outra pasta descartado sem aviso"
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
  specs: ["_reversa_sdd/legacy/requirements.md#RN-19"]
  affected_code: ["caffmob_draw/legacy/groups.py", "caffmob_draw/product_libraries/frameless/operators/ops_library.py"]
  root_cause:
    state: confirmed
    hypothesis: "group_items usava get_user_library_items, que descarta por seen_names o arquivo homônimo de outra pasta."
    causal_path:
      - "legacy/groups.py group_items"
      - "frameless/operators/ops_library.py get_user_library_items seen_names"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/legacy/groups.py, symbol: group_items, commit: 6d2d9b6}
  reproduction_tests: ["tests/blender_bug_5NLX_legacy.py"]
  regression_tests: ["tests/blender_bug_5NLX_legacy.py", "tests/blender_012_convert_smoke.py", "tests/test_legacy_convert.py"]

spec_verdict: spec-desatualizada

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
  - id: CHG-007
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261011-ORRG-v001.md
    purpose: "RN-19: homônimos de outra pasta entram"
    diff: _reversa_sdd/addenda/bug-BUG-20261011-ORRG-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Grupo homônimo em outra pasta descartado sem aviso

## Summary

Em `get_user_library_items`, um grupo com o mesmo nome de arquivo em outra pasta some sem aviso.

## Expected Behavior

O usuário é avisado do grupo descartado (ou ele é listado com a pasta).

Spec efetiva: `_reversa_sdd/legacy/requirements.md#RN-19`.

## Actual Behavior

Em `get_user_library_items`, um grupo com o mesmo nome de arquivo em outra pasta some sem aviso.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 72.

## Suspected Area

- `caffmob_draw/legacy/groups.py`
- `caffmob_draw/product_libraries/frameless/operators/ops_library.py`

## Acceptance Criteria

- O usuário é avisado do grupo descartado (ou ele é listado com a pasta).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/legacy/requirements.md#RN-19`
- Código afetado: `caffmob_draw/legacy/groups.py`, `caffmob_draw/product_libraries/frameless/operators/ops_library.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 26 (conversão das bibliotecas herdadas) (BUG-20261011-5NLX, BUG-20261011-NTM3, BUG-20261011-HUWF, BUG-20261011-ORRG); plano em `_reversa_bugs/legacy/bugs/BUG-20261011-5NLX-falha-no-meio-do-lote-de-conversao/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** group_items usava get_user_library_items, que descarta por seen_names o arquivo homônimo de outra pasta.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-desatualizada`: RN-19 registrava o descarte silencioso; adendo `_reversa_sdd/addenda/bug-BUG-20261011-ORRG-v001.md` (todos os arquivos entram; o nome salvo desempata).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_5NLX_legacy.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/data/translations/library.json` | mensagens novas | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/legacy/convert.py` | rollback, folhas lidas e leitura falha | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/legacy/convert_core.py` | perda Frentes não lidas | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/legacy/groups.py` | todos os grupos, sem descarte | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/legacy/ops.py` | ERROR e CANCELLED | `CHG-006.diff` |
| CHG-007 | specification | `_reversa_sdd/addenda/bug-BUG-20261011-ORRG-v001.md` | RN-19: homônimos de outra pasta entram | `bug-BUG-20261011-ORRG-v001.md` |

**Vermelho (antes da correção):** 8 objetos do lote ficaram na cena e saiu traceback; PULLOUT contou DRAWERS e SPECIAL; 'sem perdas' com o leitor falhando; o homônimo em Cozinha/ sumiu.

**Verde (depois):** `blender_bug_5NLX_legacy.py` OK; na cópia isolada também `blender_012_convert_smoke`, `test_legacy_convert`, `test_legacy_groups` e `test_i18n_coverage`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_5NLX_legacy.py`. **Regressão:** `tests/blender_bug_5NLX_legacy.py`, `tests/blender_012_convert_smoke.py`, `tests/test_legacy_convert.py`.

## Agent Notes

- Item 72 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `legacy`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
