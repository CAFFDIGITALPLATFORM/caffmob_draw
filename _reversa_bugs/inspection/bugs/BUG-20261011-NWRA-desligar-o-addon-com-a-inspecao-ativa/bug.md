---
schema_version: 1
id: BUG-20261011-NWRA
display_number: 101
title: "Desligar o addon com a inspeção ativa deixa resíduos"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: plugin
module: inspection
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["painel: 'Abrir tudo' mostra o ângulo escolhido e o outro ângulo ao lado", "save_pre passa a gravar o alvo das animações"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/inspection/tasks.md#DT-04"]
  affected_code: ["caffmob_draw/inspection/__init__.py", "caffmob_draw/inspection/ops_inspect.py"]
  root_cause:
    state: confirmed
    hypothesis: "ops_inspect.unregister só zerava _active; timers, modal e o registro no HUD da sessão ficavam."
    causal_path:
      - "inspection/ops_inspect.py unregister"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/inspection/ops_inspect.py, symbol: unregister, commit: 7925071}
  reproduction_tests: ["tests/blender_bug_B5JP_inspection.py"]
  regression_tests: ["tests/blender_bug_B5JP_inspection.py", "tests/blender_inspection_smoke.py", "tests/blender_bug_5EX7_gizmo.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_B5JP_inspection.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/data/translations/inspection.json
    purpose: "rótulos novos"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/inspection/ops_inspect.py
    purpose: "settle_running, unregister, contagem e OPEN_DEFAULT"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/inspection/overlay.py
    purpose: "depth test restaurado"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/inspection/save_guard.py
    purpose: "conclui animações antes de fechar"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/ui/context_menu.py
    purpose: "Abrir frentes no ângulo escolhido"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/ui/panels.py
    purpose: "Abrir tudo no ângulo escolhido"
    diff: _reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/CHG-007.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Desligar o addon com a inspeção ativa deixa resíduos

## Summary

Timers, modal handler e o registro no HUD continuam.

## Expected Behavior

`unregister()` remove timers, modal handler e o registro no HUD.

Spec efetiva: `_reversa_sdd/inspection/tasks.md#DT-04`.

## Actual Behavior

Timers, modal handler e o registro no HUD continuam.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 90.

## Suspected Area

- `caffmob_draw/inspection/__init__.py`
- `caffmob_draw/inspection/ops_inspect.py`

## Acceptance Criteria

- `unregister()` remove timers, modal handler e o registro no HUD.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/inspection/tasks.md#DT-04`
- Código afetado: `caffmob_draw/inspection/__init__.py`, `caffmob_draw/inspection/ops_inspect.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 29 (inspeção de frentes) (BUG-20261011-B5JP, BUG-20261011-NWRA, BUG-20261011-UURX, BUG-20261011-6AX3, BUG-20261011-B54S); plano em `_reversa_bugs/inspection/bugs/BUG-20261011-B5JP-salvar-durante-a-animacao-grava-estado-intermediario/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** ops_inspect.unregister só zerava _active; timers, modal e o registro no HUD da sessão ficavam.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 92 e inspection DT-04 (EC-04).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_B5JP_inspection.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/data/translations/inspection.json` | rótulos novos | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/inspection/ops_inspect.py` | settle_running, unregister, contagem e OPEN_DEFAULT | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/inspection/overlay.py` | depth test restaurado | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/inspection/save_guard.py` | conclui animações antes de fechar | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/ui/context_menu.py` | Abrir frentes no ângulo escolhido | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/ui/panels.py` | Abrir tudo no ângulo escolhido | `CHG-007.diff` |

**Vermelho (antes da correção):** frente em animação reabriu em 0° e pendente perdido; unregister não encerrou a sessão; depth test ficou NONE; '3 frente(s)' com uma pulada; OPEN_DEFAULT inexistente.

**Verde (depois):** `blender_bug_B5JP_inspection.py` OK; na cópia isolada também `blender_inspection_smoke`, `blender_bug_5EX7_gizmo`, `blender_bug_TIPN_stale_results`, `test_i18n_coverage` e `blender_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_B5JP_inspection.py`. **Regressão:** `tests/blender_bug_B5JP_inspection.py`, `tests/blender_inspection_smoke.py`, `tests/blender_bug_5EX7_gizmo.py`.

## Agent Notes

- Item 90 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `inspection`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
