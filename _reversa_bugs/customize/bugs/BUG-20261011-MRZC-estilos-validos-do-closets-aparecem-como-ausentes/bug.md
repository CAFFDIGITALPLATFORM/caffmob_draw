---
schema_version: 1
id: BUG-20261011-MRZC
display_number: 24
title: "Estilos válidos do closets aparecem como ausentes"
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
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10", "reproduzido"]

change_risk:
  classification: baixa
  reasons: ["só a biblioteca própria (arquivos em extension_path_user)", "sem mudança de formato do manifesto"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-J2NY
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-02"]
  affected_code: ["caffmob_draw/customize/library_io.py", "caffmob_draw/product_libraries/closets/fronts_closets.py"]
  root_cause:
    state: confirmed
    hypothesis: "_missing_styles só conhece frameless e face frame (closets cai em set()) e o filtro por prefixo \"Estilo '\" apaga avisos de estilos que não estão entre os ausentes."
    causal_path:
      - "customize/library_io.py _missing_styles: `existing = set()` para CLOSETS"
      - "customize/library_io.py load: filtro por prefixo"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/customize/library_io.py, symbol: _missing_styles, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_J2NY_library_io.py"]
  regression_tests: ["tests/blender_bug_J2NY_library_io.py", "tests/blender_003_customize_smoke.py", "tests/blender_003_move_over_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_J2NY_library_io.py
    purpose: "reprodução e regressão dos três defeitos"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-J2NY-inserir-um-blend-sem-json-quebra-a/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/customize/library_io.py
    purpose: "missing inicial; estilos pelo adaptador; troca do par com volta"
    diff: _reversa_bugs/customize/bugs/BUG-20261011-J2NY-inserir-um-blend-sem-json-quebra-a/fix/CHG-002.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Estilos válidos do closets aparecem como ausentes

## Summary

`_missing_styles` não conhece `fronts_closets.FRONT_STYLES` (`existing = set()`). Além disso, o filtro por prefixo "Estilo '" apaga o aviso real de estilo inexistente.

## Expected Behavior

Estilos de `fronts_closets.FRONT_STYLES` são reconhecidos; só estilo de fato inexistente gera o aviso "Estilo '{}' não existe no closets", que não é filtrado.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-02`.

## Actual Behavior

`_missing_styles` não conhece `fronts_closets.FRONT_STYLES` (`existing = set()`). Além disso, o filtro por prefixo "Estilo '" apaga o aviso real de estilo inexistente.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/customize.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 13.

## Suspected Area

- `caffmob_draw/customize/library_io.py`
- `caffmob_draw/product_libraries/closets/fronts_closets.py`

## Acceptance Criteria

- Estilos de `fronts_closets.FRONT_STYLES` são reconhecidos; só estilo de fato inexistente gera o aviso "Estilo '{}' não existe no closets", que não é filtrado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-02`
- Código afetado: `caffmob_draw/customize/library_io.py`, `caffmob_draw/product_libraries/closets/fronts_closets.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 4 (library_io da biblioteca própria) (BUG-20261011-J2NY, BUG-20261011-MRZC, BUG-20261011-OJBL); plano em `_reversa_bugs/customize/bugs/BUG-20261011-J2NY-inserir-um-blend-sem-json-quebra-a/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `_missing_styles` não conhecia os estilos do closets (`set()`) e o filtro por prefixo apagava avisos de outros estilos.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: customize EC-02 já definia o certo.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_J2NY_library_io.py` | reprodução e regressão dos três defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/customize/library_io.py` | missing inicial; estilos pelo adaptador; troca do par com volta | `CHG-002.diff` |

**Vermelho (antes da correção):** `blender_bug_J2NY_library_io` com 5 falhas no projeto (UnboundLocalError em load e no Inserir; WIDE_SHAKER como ausente; .blend trocado com .json antigo).

**Verde (depois):** `blender_bug_J2NY_library_io: OK`, `blender_003_customize_smoke: OK`, `test_i18n_coverage` OK; na cópia isolada também `blender_003_move_over_smoke` e `blender_009_library_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_J2NY_library_io.py`. **Regressão:** `tests/blender_bug_J2NY_library_io.py`, `tests/blender_003_customize_smoke.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 13 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
