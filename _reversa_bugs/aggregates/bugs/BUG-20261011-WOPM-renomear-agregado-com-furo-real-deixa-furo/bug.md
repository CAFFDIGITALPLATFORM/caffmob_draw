---
schema_version: 1
id: BUG-20261011-WOPM
display_number: 34
title: "Renomear agregado com furo real deixa furo fantasma na usinagem"
status: resolved
phase: delivering
severity: high
priority: P1
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: producao
module: aggregates
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["só renomeia modificadores existentes", "arquivo antigo coberto pelo fallback"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/aggregates/edge-cases.md#EC-09"]
  affected_code: ["caffmob_draw/aggregates/perforate.py"]
  root_cause:
    state: confirmed
    hypothesis: "BOOLEAN e CPM_CUTOUT eram achados pelo nome atual do agregado: depois de renomear, sync criava outros e os antigos ficavam no pai e na usinagem."
    causal_path:
      - "aggregates/perforate.py _sync_boolean/_sync_cutout: parent.modifiers.get(PREFIX + obj.name)"
      - "cutting/machining: exporta todo CPM_CUTOUT 'Agregado: …'"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/aggregates/perforate.py, symbol: sync, commit: a67387a}
  reproduction_tests: ["tests/blender_bug_WOPM_perforate_rename.py"]
  regression_tests: ["tests/blender_bug_WOPM_perforate_rename.py", "tests/blender_003_aggregates_smoke.py", "tests/blender_012_apply_smoke.py", "tests/test_cut_plan_machining.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_WOPM_perforate_rename.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-WOPM-renomear-agregado-com-furo-real-deixa-furo/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/aggregates/perforate.py
    purpose: "modificadores do furo seguem o nome do agregado"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-WOPM-renomear-agregado-com-furo-real-deixa-furo/fix/CHG-002.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Renomear agregado com furo real deixa furo fantasma na usinagem

## Summary

Renomear um agregado com furo real deixa o `CPM_CUTOUT` antigo no pai, e a usinagem continua exportando esse furo, porque o vínculo é por nome em `perforate.py`.

## Expected Behavior

Renomear o agregado mantém um único recorte, vinculado ao agregado; nenhum furo antigo é exportado.

Spec efetiva: `_reversa_sdd/aggregates/edge-cases.md#EC-09`.

## Actual Behavior

Renomear um agregado com furo real deixa o `CPM_CUTOUT` antigo no pai, e a usinagem continua exportando esse furo, porque o vínculo é por nome em `perforate.py`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 23.

## Suspected Area

- `caffmob_draw/aggregates/perforate.py`

## Acceptance Criteria

- Renomear o agregado mantém um único recorte, vinculado ao agregado; nenhum furo antigo é exportado.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/aggregates/edge-cases.md#EC-09`
- Código afetado: `caffmob_draw/aggregates/perforate.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 19 (furo fantasma ao renomear agregado) (BUG-20261011-WOPM); plano em `_reversa_bugs/aggregates/bugs/BUG-20261011-WOPM-renomear-agregado-com-furo-real-deixa-furo/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** BOOLEAN e CPM_CUTOUT eram achados pelo nome atual do agregado: depois de renomear, sync criava outros e os antigos ficavam no pai e na usinagem.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: aggregates EC-09 descreve o furo fantasma como defeito.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_WOPM_perforate_rename.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/aggregates/perforate.py` | modificadores do furo seguem o nome do agregado | `CHG-002.diff` |

**Vermelho (antes da correção):** dois BOOLEAN e dois CPM_CUTOUT depois de renomear; a usinagem exporta 2 furos; desligar Perfurar deixa os antigos (arquivo novo e antigo).

**Verde (depois):** `blender_bug_WOPM_perforate_rename.py` OK; na cópia isolada também `blender_003_aggregates_smoke`, `blender_012_apply_smoke` e `test_cut_plan_machining`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_WOPM_perforate_rename.py`. **Regressão:** `tests/blender_bug_WOPM_perforate_rename.py`, `tests/blender_003_aggregates_smoke.py`, `tests/blender_012_apply_smoke.py`, `tests/test_cut_plan_machining.py`.

## Agent Notes

- Item 23 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: usinagem exporta furo que não existe: erro físico na fabricação.
- Unit/contexto: `aggregates`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
