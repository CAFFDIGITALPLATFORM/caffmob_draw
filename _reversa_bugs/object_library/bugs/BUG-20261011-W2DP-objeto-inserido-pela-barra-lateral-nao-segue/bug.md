---
schema_version: 1
id: BUG-20261011-W2DP
display_number: 89
title: "Objeto inserido pela barra lateral não segue o mouse"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: object_library
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

change_risk:
  classification: baixa
  reasons: ["gravação mexe no pai só durante o write e restaura", "imagens de textura própria passam a ficar empacotadas também no projeto"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/object_library/requirements.md#RN-14", "_reversa_sdd/object_library/tasks.md#DT-01"]
  affected_code: ["caffmob_draw/object_library/ops.py"]
  root_cause:
    state: confirmed
    hypothesis: "_follow usava context.region/region_data; invocado pela barra lateral, a região do modal é a UI e region_data é None, então saía cedo."
    causal_path:
      - "object_library/ops.py BTM_OT_ObjectInsert._follow"
      - "ui/sidebar.py BTM_PT_Sidebar"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/object_library/ops.py, symbol: BTM_OT_ObjectInsert._follow, commit: c989c10}
  reproduction_tests: ["tests/test_object_library.py", "tests/blender_bug_QZSO_object_library.py", "tests/blender_bug_W2DP_object_insert.py"]
  regression_tests: ["tests/test_object_library.py", "tests/blender_bug_QZSO_object_library.py", "tests/blender_bug_W2DP_object_insert.py", "tests/blender_009_library_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_QZSO_object_library.py
    purpose: "pai fora do .blend e textura empacotada"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_W2DP_object_insert.py
    purpose: "seguir o mouse pela barra lateral"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/test_object_library.py
    purpose: "item_id e manifesto de tipo inesperado"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/object_library/catalog.py
    purpose: "fullmatch"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/object_library/item_io.py
    purpose: "gravar sem o pai e empacotar"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/object_library/ops.py
    purpose: "região WINDOW no _follow"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/object_library/store.py
    purpose: "TypeError vira aviso"
    diff: _reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/CHG-007.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Objeto inserido pela barra lateral não segue o mouse

## Summary

O modal recebe a região UI sem `RegionView3D`. Contradiz RN-14.

## Expected Behavior

RN-14: o objeto segue o mouse no viewport também quando inserido pela barra lateral.

Spec efetiva: `_reversa_sdd/object_library/requirements.md#RN-14`, `_reversa_sdd/object_library/tasks.md#DT-01`.

## Actual Behavior

O modal recebe a região UI sem `RegionView3D`. Contradiz RN-14.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/object_library.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 78.

## Suspected Area

- `caffmob_draw/object_library/ops.py`

## Acceptance Criteria

- RN-14: o objeto segue o mouse no viewport também quando inserido pela barra lateral.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/object_library/requirements.md#RN-14`, `_reversa_sdd/object_library/tasks.md#DT-01`
- Código afetado: `caffmob_draw/object_library/ops.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 28 (biblioteca de objetos) (BUG-20261011-W2DP, BUG-20261011-KKHH, BUG-20261011-QZSO, BUG-20261011-JKZJ, BUG-20261011-EVT6); plano em `_reversa_bugs/object_library/bugs/BUG-20261011-W2DP-objeto-inserido-pela-barra-lateral-nao-segue/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** _follow usava context.region/region_data; invocado pela barra lateral, a região do modal é a UI e region_data é None, então saía cedo.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: RN-14, questions.md pergunta 59 e object_library DT-01.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_QZSO_object_library.py` | pai fora do .blend e textura empacotada | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_W2DP_object_insert.py` | seguir o mouse pela barra lateral | `CHG-002.diff` |
| CHG-003 | test | `tests/test_object_library.py` | item_id e manifesto de tipo inesperado | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/object_library/catalog.py` | fullmatch | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/object_library/item_io.py` | gravar sem o pai e empacotar | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/object_library/ops.py` | região WINDOW no _follow | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/object_library/store.py` | TypeError vira aviso | `CHG-007.diff` |

**Vermelho (antes da correção):** raiz parada em (0,0,0) pela barra lateral; TypeError na listagem; 'PaiX' no .blend do item; textura não empacotada; item_id com '\n' aceito.

**Verde (depois):** `test_object_library.py` OK, `blender_bug_QZSO_object_library.py` OK, `blender_bug_W2DP_object_insert.py` OK; na cópia isolada também `blender_009_library_smoke` e `blender_011_component_smoke`; W2DP com janela (xvfb); `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/test_object_library.py`, `tests/blender_bug_QZSO_object_library.py`, `tests/blender_bug_W2DP_object_insert.py`. **Regressão:** `tests/test_object_library.py`, `tests/blender_bug_QZSO_object_library.py`, `tests/blender_bug_W2DP_object_insert.py`, `tests/blender_009_library_smoke.py`.

## Agent Notes

- Item 78 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `object_library`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
