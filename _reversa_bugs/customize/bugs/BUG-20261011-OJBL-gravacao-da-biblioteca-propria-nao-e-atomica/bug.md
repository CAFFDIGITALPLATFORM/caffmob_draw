---
schema_version: 1
id: BUG-20261011-OJBL
display_number: 28
title: "Gravação da biblioteca própria não é atômica entre .blend e .json"
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
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10"]

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
  specs: ["_reversa_sdd/customize/requirements.md#RN-15"]
  affected_code: ["caffmob_draw/customize/library_io.py"]
  root_cause:
    state: confirmed
    hypothesis: "save troca o .blend e depois o .json com dois os.replace; falha no segundo deixa o .blend novo com o .json antigo."
    causal_path:
      - "customize/library_io.py save: os.replace(.blend) e os.replace(.json) sem volta"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/customize/library_io.py, symbol: save, commit: 83a6863}
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

# Gravação da biblioteca própria não é atômica entre .blend e .json

## Summary

Uma falha entre os dois `os.replace` em `library_io.save` deixa o `.blend` novo com o `.json` antigo.

## Expected Behavior

Gravação sem resto (RN-15): uma falha não deixa par `.blend`/`.json` inconsistente.

Spec efetiva: `_reversa_sdd/customize/requirements.md#RN-15`.

## Actual Behavior

Uma falha entre os dois `os.replace` em `library_io.save` deixa o `.blend` novo com o `.json` antigo.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 17.

## Suspected Area

- `caffmob_draw/customize/library_io.py`

## Acceptance Criteria

- Gravação sem resto (RN-15): uma falha não deixa par `.blend`/`.json` inconsistente.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/requirements.md#RN-15`
- Código afetado: `caffmob_draw/customize/library_io.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 4 (library_io da biblioteca própria) (BUG-20261011-J2NY, BUG-20261011-MRZC, BUG-20261011-OJBL); plano em `_reversa_bugs/customize/bugs/BUG-20261011-J2NY-inserir-um-blend-sem-json-quebra-a/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** dois `os.replace` sem volta: falha no segundo deixava `.blend` novo com `.json` antigo.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: RN-15 promete gravação sem resto.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_J2NY_library_io.py` | reprodução e regressão dos três defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/customize/library_io.py` | missing inicial; estilos pelo adaptador; troca do par com volta | `CHG-002.diff` |

**Vermelho (antes da correção):** `blender_bug_J2NY_library_io` com 5 falhas no projeto (UnboundLocalError em load e no Inserir; WIDE_SHAKER como ausente; .blend trocado com .json antigo).

**Verde (depois):** `blender_bug_J2NY_library_io: OK`, `blender_003_customize_smoke: OK`, `test_i18n_coverage` OK; na cópia isolada também `blender_003_move_over_smoke` e `blender_009_library_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_J2NY_library_io.py`. **Regressão:** `tests/blender_bug_J2NY_library_io.py`, `tests/blender_003_customize_smoke.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 17 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
