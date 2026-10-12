---
schema_version: 1
id: BUG-20261011-J2NY
display_number: 23
title: "Inserir um .blend sem .json quebra a inserção com UnboundLocalError"
status: resolved
phase: delivering
severity: critical
priority: P0
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

relationships: []

traceability:
  specs: ["_reversa_sdd/customize/edge-cases.md#EC-01", "_reversa_sdd/move_over/edge-cases.md#EC-21", "_reversa_sdd/domain.md#RN-CUSTOMIZE-13", "_reversa_sdd/gaps.md#parte-b--crítico"]
  affected_code: ["caffmob_draw/customize/library_io.py", "caffmob_draw/customize/ops_library.py", "caffmob_draw/move_over/ops_substitute.py"]
  root_cause:
    state: confirmed
    hypothesis: "library_io.load só define `missing` dentro de `if data is not None` e o lê depois; sem .json, UnboundLocalError com os objetos já ligados à cena."
    causal_path:
      - "customize/library_io.py load: `if missing:` no fim, com `missing` só atribuído quando há manifesto"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/customize/library_io.py, symbol: load, commit: 83a6863}
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

# Inserir um .blend sem .json quebra a inserção com UnboundLocalError

## Summary

`library_io.load` usa `missing` sem defini-lo e levanta `UnboundLocalError`, deixando 26 objetos ligados à cena. Afeta `module_insert` e o Substituir (`move_over/ops_substitute`). Correção sugerida: `missing = []` antes do `if data is not None`.

## Expected Behavior

Um grupo antigo sem `.json` é inserido normalmente (sem manifesto, sem avisos de ausentes), no `module_insert` e no Substituir.

Spec efetiva: `_reversa_sdd/customize/edge-cases.md#EC-01`, `_reversa_sdd/move_over/edge-cases.md#EC-21`, `_reversa_sdd/domain.md#RN-CUSTOMIZE-13`, `_reversa_sdd/gaps.md#parte-b--crítico`.

## Actual Behavior

`library_io.load` usa `missing` sem defini-lo e levanta `UnboundLocalError`, deixando 26 objetos ligados à cena. Afeta `module_insert` e o Substituir (`move_over/ops_substitute`). Correção sugerida: `missing = []` antes do `if data is not None`.

## Steps to Reproduce

Reproduzido na revisão de 2026-10-10 (Blender 5.2 ou Python puro). O roteiro exato está no relatório bruto `.reversa/context/review-2026-10/customize.json`; o `/reversa-debugger-fix` deve convertê-lo em teste de reprodução.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 12.

## Suspected Area

- `caffmob_draw/customize/library_io.py`
- `caffmob_draw/customize/ops_library.py`
- `caffmob_draw/move_over/ops_substitute.py`

## Acceptance Criteria

- Um grupo antigo sem `.json` é inserido normalmente (sem manifesto, sem avisos de ausentes), no `module_insert` e no Substituir.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/edge-cases.md#EC-01`, `_reversa_sdd/move_over/edge-cases.md#EC-21`, `_reversa_sdd/domain.md#RN-CUSTOMIZE-13`, `_reversa_sdd/gaps.md#parte-b--crítico`
- Código afetado: `caffmob_draw/customize/library_io.py`, `caffmob_draw/customize/ops_library.py`, `caffmob_draw/move_over/ops_substitute.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 4 (library_io da biblioteca própria) (BUG-20261011-J2NY, BUG-20261011-MRZC, BUG-20261011-OJBL); plano em `_reversa_bugs/customize/bugs/BUG-20261011-J2NY-inserir-um-blend-sem-json-quebra-a/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `load` só definia `missing` com manifesto e o lia depois: `UnboundLocalError` com os objetos já na cena.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: RN-CUSTOMIZE-13 e a intenção da 003 já pediam inserção sem personalização.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_J2NY_library_io.py` | reprodução e regressão dos três defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/customize/library_io.py` | missing inicial; estilos pelo adaptador; troca do par com volta | `CHG-002.diff` |

**Vermelho (antes da correção):** `blender_bug_J2NY_library_io` com 5 falhas no projeto (UnboundLocalError em load e no Inserir; WIDE_SHAKER como ausente; .blend trocado com .json antigo).

**Verde (depois):** `blender_bug_J2NY_library_io: OK`, `blender_003_customize_smoke: OK`, `test_i18n_coverage` OK; na cópia isolada também `blender_003_move_over_smoke` e `blender_009_library_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_J2NY_library_io.py`. **Regressão:** `tests/blender_bug_J2NY_library_io.py`, `tests/blender_003_customize_smoke.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 12 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
