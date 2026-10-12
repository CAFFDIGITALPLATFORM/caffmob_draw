---
schema_version: 1
id: BUG-20261011-QO2H
display_number: 76
title: "A segunda pergunta de Definir ativa repete módulos já aplicados"
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
  reasons: ["mudanças locais em migração, plano da 2ª pergunta e índice da ativa", "a 1ª pergunta e o caminho EXEC (apply_differ) não mudam"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/standards/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/standards/apply_core.py", "caffmob_draw/operators/ops_standards.py"]
  root_cause:
    state: confirmed
    hypothesis: "standards_apply_differ recalculava o plano com o previous_uid; os módulos que a 1ª pergunta acabara de levar ao padrão novo têm uid diferente do anterior e caíam em 'difere'."
    causal_path:
      - "operators/ops_standards.py StandardsApplyDiffer"
      - "standards/apply_core.py plan"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/standards/apply_core.py, symbol: plan, commit: db450a6}
      - {file: caffmob_draw/operators/ops_standards.py, symbol: BTM_OT_StandardsApplyDiffer, commit: db450a6}
  reproduction_tests: ["tests/blender_bug_MTPU_standards.py"]
  regression_tests: ["tests/blender_bug_MTPU_standards.py", "tests/blender_012_apply_smoke.py", "tests/test_standards_apply_core.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_MTPU_standards.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/operators/ops_standards.py
    purpose: "2ª pergunta com o plano filtrado"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/standards/api.py
    purpose: "ativa preservada"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/standards/apply_core.py
    purpose: "plano sem os já aplicados"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/standards/migration.py
    purpose: "falha registrada e face frame legado"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/standards/sync.py
    purpose: "repassa o padrão novo ao plano"
    diff: _reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# A segunda pergunta de Definir ativa repete módulos já aplicados

## Summary

Depois de "Definir ativa" com Sim, a 2ª pergunta inclui os módulos já aplicados na 1ª.

## Expected Behavior

A 2ª pergunta lista só os módulos que ainda não receberam o padrão.

Spec efetiva: `_reversa_sdd/standards/tasks.md#DT-03`.

## Actual Behavior

Depois de "Definir ativa" com Sim, a 2ª pergunta inclui os módulos já aplicados na 1ª.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 65.

## Suspected Area

- `caffmob_draw/standards/apply_core.py`
- `caffmob_draw/operators/ops_standards.py`

## Acceptance Criteria

- A 2ª pergunta lista só os módulos que ainda não receberam o padrão.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/standards/tasks.md#DT-03`
- Código afetado: `caffmob_draw/standards/apply_core.py`, `caffmob_draw/operators/ops_standards.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 25 (padrões dimensionais) (BUG-20261011-MTPU, BUG-20261011-QO2H, BUG-20261011-64UD, BUG-20261011-ZATR); plano em `_reversa_bugs/standards/bugs/BUG-20261011-MTPU-falha-na-migracao-de-padroes-interrompe-o/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** standards_apply_differ recalculava o plano com o previous_uid; os módulos que a 1ª pergunta acabara de levar ao padrão novo têm uid diferente do anterior e caíam em 'difere'.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 50 e standards DT-03.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_MTPU_standards.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/operators/ops_standards.py` | 2ª pergunta com o plano filtrado | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/standards/api.py` | ativa preservada | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/standards/apply_core.py` | plano sem os já aplicados | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/standards/migration.py` | falha registrada e face frame legado | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/standards/sync.py` | repassa o padrão novo ao plano | `CHG-006.diff` |

**Vermelho (antes da correção):** RuntimeError da migração subiu; a 2ª pergunta regravou a linha do módulo já aplicado; a ativa virou 'Depois ZATR'; projeto face frame ficou com o Padrão Brasil.

**Verde (depois):** `blender_bug_MTPU_standards.py` OK; na cópia isolada também `blender_012_apply_smoke`, `blender_012_cabinet_standard_smoke`, `test_standards_apply_core` e `blender_bug_KVDM_standards`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_MTPU_standards.py`. **Regressão:** `tests/blender_bug_MTPU_standards.py`, `tests/blender_012_apply_smoke.py`, `tests/test_standards_apply_core.py`.

## Agent Notes

- Item 65 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `standards`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
