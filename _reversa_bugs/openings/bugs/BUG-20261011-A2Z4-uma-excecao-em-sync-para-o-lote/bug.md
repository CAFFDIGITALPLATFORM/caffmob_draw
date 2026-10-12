---
schema_version: 1
id: BUG-20261011-A2Z4
display_number: 118
title: "Uma exceção em sync para o lote de aberturas"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: openings
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: média
  reasons: ["toca a montagem de todas as portas e janelas reais", "Toggle e painel passam a refazer a porta real", "montagem antiga sem marca usa o nome da caixa para saber o que é dela"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-MMVI
    type: related-to
    state: supported
    evidence: ["evidence/reproduction.md"]

traceability:
  specs: ["_reversa_sdd/openings/edge-cases.md#EC-11"]
  affected_code: ["caffmob_draw/openings/sync.py", "caffmob_draw/openings/ops.py", "caffmob_draw/walls2d/apply.py"]
  root_cause:
    state: confirmed
    hypothesis: "openings_update e walls2d/apply.apply_plan chamam sync caixa a caixa sem try: a exceção de uma interrompe o lote."
    causal_path:
      - "openings/ops.py BTM_OT_OpeningsUpdate.execute"
      - "walls2d/apply.py apply_plan: report['openings']"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/openings/ops.py, symbol: BTM_OT_OpeningsUpdate, commit: 83a6863}
      - {file: caffmob_draw/walls2d/apply.py, symbol: apply_plan, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_MMVI_opening_sync.py"]
  regression_tests: ["tests/blender_bug_MMVI_opening_sync.py", "tests/blender_010_openings_smoke.py", "tests/blender_toast_resize_invert.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_MMVI_opening_sync.py
    purpose: "reprodução e regressão dos cinco defeitos"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/openings/sync.py
    purpose: "marca, clear seletivo, sync_each, kind_of pelo símbolo, _swing filtrado"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/openings/ops.py
    purpose: "Atualizar usa sync_each e avisa falhas"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/walls2d/apply.py
    purpose: "OK usa sync_each"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/walls2d/ops_editor.py
    purpose: "aviso das caixas com erro no OK"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/operators/doors_windows.py
    purpose: "Toggle atualiza kind e refaz"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/selection/editing.py
    purpose: "porta/janela HB pelo caminho do Redimensionar"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/selection/element_size.py
    purpose: "sem conversão dupla folha/caixa"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-008.diff
  - id: CHG-009
    kind: code
    artifact: caffmob_draw/data/translations/openings.json
    purpose: "texto do aviso em pt_BR e en_US"
    diff: _reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/CHG-009.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Uma exceção em sync para o lote de aberturas

## Summary

`openings_update` e `walls2d/apply.apply_plan` chamam `sync` sem `try`, e as caixas seguintes não são processadas.

## Expected Behavior

Falha numa caixa é reportada e as seguintes continuam.

Spec efetiva: `_reversa_sdd/openings/edge-cases.md#EC-11`.

## Actual Behavior

`openings_update` e `walls2d/apply.apply_plan` chamam `sync` sem `try`, e as caixas seguintes não são processadas.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 107.

## Suspected Area

- `caffmob_draw/openings/sync.py`
- `caffmob_draw/openings/ops.py`
- `caffmob_draw/walls2d/apply.py`

## Acceptance Criteria

- Falha numa caixa é reportada e as seguintes continuam.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/openings/edge-cases.md#EC-11`
- Código afetado: `caffmob_draw/openings/sync.py`, `caffmob_draw/openings/ops.py`, `caffmob_draw/walls2d/apply.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 6 (porta real) (BUG-20261011-MMVI, BUG-20261011-A2Z4, BUG-20261011-IDPP, BUG-20261011-UV6S, BUG-20261011-SX4T); plano em `_reversa_bugs/openings/bugs/BUG-20261011-MMVI-reconstruir-a-porta-apaga-objetos-do-usuario/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `openings_update` e `walls2d/apply.apply_plan` chamavam `sync` sem `try`.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: openings EC-11 já descreve a falha isolada por caixa.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_MMVI_opening_sync.py` | reprodução e regressão dos cinco defeitos | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/openings/sync.py` | marca, clear seletivo, sync_each, kind_of pelo símbolo, _swing filtrado | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/openings/ops.py` | Atualizar usa sync_each e avisa falhas | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/walls2d/apply.py` | OK usa sync_each | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/walls2d/ops_editor.py` | aviso das caixas com erro no OK | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/operators/doors_windows.py` | Toggle atualiza kind e refaz | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/selection/editing.py` | porta/janela HB pelo caminho do Redimensionar | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/selection/element_size.py` | sem conversão dupla folha/caixa | `CHG-008.diff` |
| CHG-009 | code | `caffmob_draw/data/translations/openings.json` | texto do aviso em pt_BR e en_US | `CHG-009.diff` |

**Vermelho (antes da correção):** `blender_bug_MMVI_opening_sync` com 7 falhas no projeto.

**Verde (depois):** `blender_bug_MMVI_opening_sync: OK`, `blender_toast_resize_invert` exit 0, `blender_010_openings_smoke: OK`, `test_i18n_coverage` e `test_door_core` OK; na cópia isolada também `blender_011_region_smoke`, `blender_bug_YIMY_openings`, `blender_bug_porta_real_abre`, `blender_011_component_smoke`, `blender_009_walls_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_MMVI_opening_sync.py`. **Regressão:** `tests/blender_bug_MMVI_opening_sync.py`, `tests/blender_010_openings_smoke.py`, `tests/blender_toast_resize_invert.py`.

## Agent Notes

- Item 107 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `openings`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
