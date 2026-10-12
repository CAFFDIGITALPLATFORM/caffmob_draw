---
schema_version: 1
id: BUG-20261011-SWAD
display_number: 84
title: "write_marker deixa .tmp para trás quando a escrita falha"
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
module: legacy
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["só o caminho de falha da gravação", "comportamento de sucesso inalterado"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-OJBL
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/legacy/edge-cases.md#EC-09"]
  affected_code: ["caffmob_draw/legacy/gate.py"]
  root_cause:
    state: confirmed
    hypothesis: "write_marker grava o .tmp e faz os.replace sem try: uma falha deixa o .tmp na pasta."
    causal_path:
      - "legacy/groups.py write_marker: sem limpeza do temporário"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/legacy/groups.py, symbol: write_marker, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_SWAD_temp_files.py"]
  regression_tests: ["tests/blender_bug_SWAD_temp_files.py", "tests/test_legacy_groups.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_SWAD_temp_files.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-SWAD-write-marker-deixa-tmp-para-tras-quando/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/legacy/groups.py
    purpose: "write_marker limpa o .tmp em falha"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-SWAD-write-marker-deixa-tmp-para-tras-quando/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/object_library/item_io.py
    purpose: "tmp_json na lista de limpeza antes do dump"
    diff: _reversa_bugs/legacy/bugs/BUG-20261011-SWAD-write-marker-deixa-tmp-para-tras-quando/fix/CHG-003.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# write_marker deixa .tmp para trás quando a escrita falha

## Summary

`write_marker` não remove o `.tmp` quando a escrita falha.

## Expected Behavior

Falha de escrita não deixa `.tmp`.

Spec efetiva: `_reversa_sdd/legacy/edge-cases.md#EC-09`.

## Actual Behavior

`write_marker` não remove o `.tmp` quando a escrita falha.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 73.

## Suspected Area

- `caffmob_draw/legacy/gate.py`

## Acceptance Criteria

- Falha de escrita não deixa `.tmp`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/legacy/edge-cases.md#EC-09`
- Código afetado: `caffmob_draw/legacy/gate.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-OJBL (contexto `customize`), state `proposed`

## Resolution

- **Lote:** 10 (temporários) (BUG-20261011-SWAD, BUG-20261011-5JLF); plano em `_reversa_bugs/legacy/bugs/BUG-20261011-SWAD-write-marker-deixa-tmp-para-tras-quando/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `write_marker` gravava e trocava o arquivo sem `try`; a falha deixava o `.tmp`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: legacy EC-09 descreve o resto como defeito.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_SWAD_temp_files.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/legacy/groups.py` | write_marker limpa o .tmp em falha | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/object_library/item_io.py` | tmp_json na lista de limpeza antes do dump | `CHG-003.diff` |

**Vermelho (antes da correção):** `blender_bug_SWAD_temp_files` com 2 falhas no projeto.

**Verde (depois):** `blender_bug_SWAD_temp_files: OK`, `test_legacy_groups` e `test_object_library` OK; na cópia isolada também `blender_012_groups_smoke` e `blender_009_library_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_SWAD_temp_files.py`. **Regressão:** `tests/blender_bug_SWAD_temp_files.py`, `tests/test_legacy_groups.py`.

## Agent Notes

- Item 73 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `legacy`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
