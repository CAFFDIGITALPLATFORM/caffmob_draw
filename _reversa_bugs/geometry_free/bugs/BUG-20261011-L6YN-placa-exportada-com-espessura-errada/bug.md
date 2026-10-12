---
schema_version: 1
id: BUG-20261011-L6YN
display_number: 116
title: "Placa exportada com espessura errada"
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
module: geometry_free
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: média
  reasons: ["muda o que sai na lista de peças e no JSON global (contrato da produção)", "sem migração: o uid novo só é gravado na cópia que repetia o da original", "placa com medida menor que a espessura muda de medidas no plano de corte"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/geometry_free/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/geometry_free/mesh.py"]
  root_cause:
    state: confirmed
    hypothesis: "mesh.sheets ordena as três medidas da placa e usa a menor como espessura; uma medida do plano menor que thickness vira a espessura."
    causal_path:
      - "geometry_free/mesh.py sheets: sorted(size(...)) na placa"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/geometry_free/mesh.py, symbol: sheets, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_3VD7_production_uid.py"]
  regression_tests: ["tests/blender_bug_3VD7_production_uid.py", "tests/blender_002_smoke.py", "tests/test_production_contracts.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_3VD7_production_uid.py
    purpose: "reprodução e regressão dos três defeitos"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/cutting/part_sources.py
    purpose: "pula geometria no laço de agregados; _unique_uid"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/geometry_free/mesh.py
    purpose: "placa com thickness como espessura; thinner_than_thickness"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/ui/object_properties.py
    purpose: "aviso no painel da geometria"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/data/translations/ui.json
    purpose: "texto do aviso em pt_BR e en_US"
    diff: _reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/CHG-005.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Placa exportada com espessura errada

## Summary

`mesh.sheets` não usa sempre `thickness` como espessura.

## Expected Behavior

A espessura exportada é sempre `thickness`.

Spec efetiva: `_reversa_sdd/geometry_free/tasks.md#DT-03`.

## Actual Behavior

`mesh.sheets` não usa sempre `thickness` como espessura.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 105.

## Suspected Area

- `caffmob_draw/geometry_free/mesh.py`

## Acceptance Criteria

- A espessura exportada é sempre `thickness`.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/geometry_free/tasks.md#DT-03`
- Código afetado: `caffmob_draw/geometry_free/mesh.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 5 (uid e espessura na produção) (BUG-20261011-3VD7, BUG-20261011-SKDL, BUG-20261011-L6YN); plano em `_reversa_bugs/aggregates/bugs/BUG-20261011-3VD7-geometria-livre-convertida-em-agregado-sai-duplicada/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `mesh.sheets` ordenava as três medidas da placa e usava a menor como espessura.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 66 e geometry_free DT-03.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_3VD7_production_uid.py` | reprodução e regressão dos três defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/cutting/part_sources.py` | pula geometria no laço de agregados; _unique_uid | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/geometry_free/mesh.py` | placa com thickness como espessura; thinner_than_thickness | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/ui/object_properties.py` | aviso no painel da geometria | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/data/translations/ui.json` | texto do aviso em pt_BR e en_US | `CHG-005.diff` |

**Vermelho (antes da correção):** `blender_bug_3VD7_production_uid` com 6 falhas no projeto (uids duplicados e JSON inválido; placa com 10 mm de espessura; sem aviso).

**Verde (depois):** `blender_bug_3VD7_production_uid: OK`, `blender_002_smoke: OK`, `test_i18n_coverage` e `test_production_contracts` OK; na cópia isolada também `blender_003_aggregates_smoke` e `blender_012_apply_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_3VD7_production_uid.py`. **Regressão:** `tests/blender_bug_3VD7_production_uid.py`, `tests/blender_002_smoke.py`, `tests/test_production_contracts.py`.

## Agent Notes

- Item 105 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Reclassificado para high/P1: a produção exporta chapa com espessura errada.
- Unit/contexto: `geometry_free`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
