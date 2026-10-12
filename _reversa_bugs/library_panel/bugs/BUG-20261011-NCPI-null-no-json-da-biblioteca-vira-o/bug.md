---
schema_version: 1
id: BUG-20261011-NCPI
display_number: 88
title: "null no JSON da biblioteca vira o texto 'None'"
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: library_panel
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["validação de nome mais estrita só para nomes novos", "categorias existentes com ':' continuam listadas"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/library_panel/design.md#F-06"]
  affected_code: ["caffmob_draw/library_panel/models_core.py", "caffmob_draw/library_panel/categories_core.py"]
  root_cause:
    state: confirmed
    hypothesis: "item.get(chave, padrão) só usa o padrão sem a chave; com null, str(None) virava 'None' e door_swing None era frente desconhecida."
    causal_path:
      - "library_panel/models_core.py parse"
      - "library_panel/categories_core.py parse"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/library_panel/models_core.py, symbol: parse, commit: 20d7f0a}
      - {file: caffmob_draw/library_panel/categories_core.py, symbol: parse, commit: 20d7f0a}
  reproduction_tests: ["tests/test_library_categories.py", "tests/test_library_models.py", "tests/blender_bug_C7IK_library_panel.py"]
  regression_tests: ["tests/test_library_categories.py", "tests/test_library_models.py", "tests/blender_bug_C7IK_library_panel.py", "tests/blender_009_library_smoke.py"]

spec_verdict: spec-desatualizada

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_C7IK_library_panel.py
    purpose: "backup do arquivo inválido e recusa no create"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/test_library_categories.py
    purpose: "nome com caractere trocado e name null"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/test_library_models.py
    purpose: "não numérico e null"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/data/translations/library.json
    purpose: "mensagens novas"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/library_panel/categories.py
    purpose: "categories.json.bak"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/library_panel/categories_core.py
    purpose: "nome igual ao file_stem e null"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/library_panel/models_core.py
    purpose: "_count e null"
    diff: _reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/CHG-007.diff
  - id: CHG-008
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261011-NCPI-v001.md
    purpose: "F-06: null vale como ausente"
    diff: _reversa_sdd/addenda/bug-BUG-20261011-NCPI-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# null no JSON da biblioteca vira o texto 'None'

## Summary

`"name": null` vira categoria "None", `label: null` vira "None" e `door_swing: null` é recusado.

## Expected Behavior

`null` é tratado como ausente (F-06).

Spec efetiva: `_reversa_sdd/library_panel/design.md#F-06`.

## Actual Behavior

`"name": null` vira categoria "None", `label: null` vira "None" e `door_swing: null` é recusado.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 77.

## Suspected Area

- `caffmob_draw/library_panel/models_core.py`
- `caffmob_draw/library_panel/categories_core.py`

## Acceptance Criteria

- `null` é tratado como ausente (F-06).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/library_panel/design.md#F-06`
- Código afetado: `caffmob_draw/library_panel/models_core.py`, `caffmob_draw/library_panel/categories_core.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 27 (painel da biblioteca) (BUG-20261011-3UWR, BUG-20261011-C7IK, BUG-20261011-2HDG, BUG-20261011-NCPI); plano em `_reversa_bugs/library_panel/bugs/BUG-20261011-3UWR-no-nome-da-categoria-grava-o-modulo/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** item.get(chave, padrão) só usa o padrão sem a chave; com null, str(None) virava 'None' e door_swing None era frente desconhecida.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-desatualizada`: F-06 registrava 'None'; adendo `_reversa_sdd/addenda/bug-BUG-20261011-NCPI-v001.md`.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_C7IK_library_panel.py` | backup do arquivo inválido e recusa no create | `CHG-001.diff` |
| CHG-002 | test | `tests/test_library_categories.py` | nome com caractere trocado e name null | `CHG-002.diff` |
| CHG-003 | test | `tests/test_library_models.py` | não numérico e null | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/data/translations/library.json` | mensagens novas | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/library_panel/categories.py` | categories.json.bak | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/library_panel/categories_core.py` | nome igual ao file_stem e null | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/library_panel/models_core.py` | _count e null | `CHG-007.diff` |
| CHG-008 | specification | `_reversa_sdd/addenda/bug-BUG-20261011-NCPI-v001.md` | F-06: null vale como ausente | `bug-BUG-20261011-NCPI-v001.md` |

**Vermelho (antes da correção):** 'Pia: Lavabo' aceita e pasta criada; arquivo inválido sobrescrito sem .bak; ValueError com 'abc'; label 'None' e door_swing null recusado; categoria 'None'.

**Verde (depois):** `test_library_categories.py` OK, `test_library_models.py` OK, `blender_bug_C7IK_library_panel.py` OK; na cópia isolada também `blender_009_library_smoke`, `test_i18n_coverage` e `blender_bug_J2NY_library_io`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/test_library_categories.py`, `tests/test_library_models.py`, `tests/blender_bug_C7IK_library_panel.py`. **Regressão:** `tests/test_library_categories.py`, `tests/test_library_models.py`, `tests/blender_bug_C7IK_library_panel.py`, `tests/blender_009_library_smoke.py`.

## Agent Notes

- Item 77 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `library_panel`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
