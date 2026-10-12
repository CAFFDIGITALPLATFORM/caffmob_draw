---
schema_version: 1
id: BUG-20261011-3HN6
display_number: 74
title: "Documento de padrões malformado quebra o operador"
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
module: standards
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["formato .btmdim.json ganha um campo opcional, sem subir schema_version", "validação mais estrita só recusa o que era inválido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-KVDM
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/standards/edge-cases.md#EC-05"]
  affected_code: ["caffmob_draw/standards/io_json.py", "caffmob_draw/operators/ops_standards.py"]
  root_cause:
    state: confirmed
    hypothesis: "document_to_values chama .get/.items sem conferir a forma; AttributeError/TypeError escapam do operador, que só captura StandardFileError; bool passa por int."
    causal_path:
      - "standards/io_json.py document_to_values"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/standards/io_json.py, symbol: document_to_values, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_KVDM_standards.py"]
  regression_tests: ["tests/blender_bug_KVDM_standards.py", "tests/test_dimension_schema.py", "tests/blender_012_cabinet_standard_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_KVDM_standards.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-KVDM-a-montagem-se-perde-na-ida-e/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/standards/io_json.py
    purpose: "assembly no formato; forma interna conferida"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-KVDM-a-montagem-se-perde-na-ida-e/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/data/dimension_schema.py
    purpose: "isfinite; mensagens com faixa e valor"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-KVDM-a-montagem-se-perde-na-ida-e/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/data/translations/standards.json
    purpose: "mensagem de estrutura inválida"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-KVDM-a-montagem-se-perde-na-ida-e/fix/CHG-004.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Documento de padrões malformado quebra o operador

## Summary

`document_to_values` não valida a forma interna e levanta `AttributeError`/`TypeError` não capturado.

## Expected Behavior

Documento malformado é recusado com mensagem, sem exceção.

Spec efetiva: `_reversa_sdd/standards/edge-cases.md#EC-05`.

## Actual Behavior

`document_to_values` não valida a forma interna e levanta `AttributeError`/`TypeError` não capturado.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 63.

## Suspected Area

- `caffmob_draw/standards/io_json.py`
- `caffmob_draw/operators/ops_standards.py`

## Acceptance Criteria

- Documento malformado é recusado com mensagem, sem exceção.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/standards/edge-cases.md#EC-05`
- Código afetado: `caffmob_draw/standards/io_json.py`, `caffmob_draw/operators/ops_standards.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 13 (padrões dimensionais) (BUG-20261011-KVDM, BUG-20261011-ZK42, BUG-20261011-3HN6, BUG-20261011-EKM7); plano em `_reversa_bugs/standards/bugs/BUG-20261011-KVDM-a-montagem-se-perde-na-ida-e/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `document_to_values` não conferia a forma interna e aceitava bool como versão.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: standards EC-05 descreve o erro Python como defeito.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_KVDM_standards.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/standards/io_json.py` | assembly no formato; forma interna conferida | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/data/dimension_schema.py` | isfinite; mensagens com faixa e valor | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/data/translations/standards.json` | mensagem de estrutura inválida | `CHG-004.diff` |

**Vermelho (antes da correção):** `blender_bug_KVDM_standards` com 9 falhas no projeto.

**Verde (depois):** `blender_bug_KVDM_standards: OK`, `test_dimension_schema` e `test_i18n_coverage` OK; na cópia isolada também `test_promob_io`, `test_promob_assembly`, `test_standards_apply_core`, `blender_012_cabinet_standard_smoke`, `blender_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_KVDM_standards.py`. **Regressão:** `tests/blender_bug_KVDM_standards.py`, `tests/test_dimension_schema.py`, `tests/blender_012_cabinet_standard_smoke.py`.

## Agent Notes

- Item 63 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `standards`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
