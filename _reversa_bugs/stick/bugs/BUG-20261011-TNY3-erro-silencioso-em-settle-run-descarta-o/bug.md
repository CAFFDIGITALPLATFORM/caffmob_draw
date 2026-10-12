---
schema_version: 1
id: BUG-20261011-TNY3
display_number: 57
title: "Erro silencioso em settle.run descarta o lote pendente"
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
module: stick
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: média
  reasons: ["handler de depsgraph do grudar (roda em toda atualização)", "orientação depois de giro livre muda", "migração ganha uma marca nova (opt_out)"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/stick/edge-cases.md#EC-15"]
  affected_code: ["caffmob_draw/stick/settle.py"]
  root_cause:
    state: confirmed
    hypothesis: "_settle_timer só tratava ReferenceError; outra exceção saía do temporizador sem log."
    causal_path:
      - "stick/apply.py _settle_timer"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/stick/apply.py, symbol: _settle_timer, commit: 9674896}
  reproduction_tests: ["tests/blender_bug_XPD2_stick.py"]
  regression_tests: ["tests/blender_bug_XPD2_stick.py", "tests/blender_004_stick_smoke.py", "tests/blender_bug_ZKQ7_parent_cycle.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_XPD2_stick.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/stick/apply.py
    purpose: "pai trocado, índice por ponteiro, orientação e log"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/stick/link.py
    purpose: "marca opt_out ao desgrudar da parede"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/stick/migrate.py
    purpose: "respeita opt_out"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/stick/ops_stick.py
    purpose: "filtro único stickable"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/stick/panels.py
    purpose: "painel pelo filtro único"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/stick/props.py
    purpose: "opt_out"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/stick/settle.py
    purpose: "respeita opt_out"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-008.diff
  - id: CHG-009
    kind: code
    artifact: caffmob_draw/ui/context_menu.py
    purpose: "menu pelo filtro único"
    diff: _reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/CHG-009.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Erro silencioso em settle.run descarta o lote pendente

## Summary

Uma exceção que não seja `ReferenceError` descarta o lote `_pending` e encerra o temporizador sem log.

## Expected Behavior

Exceção inesperada é registrada em log e não descarta silenciosamente os itens pendentes.

Spec efetiva: `_reversa_sdd/stick/edge-cases.md#EC-15`.

## Actual Behavior

Uma exceção que não seja `ReferenceError` descarta o lote `_pending` e encerra o temporizador sem log.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 46.

## Suspected Area

- `caffmob_draw/stick/settle.py`

## Acceptance Criteria

- Exceção inesperada é registrada em log e não descarta silenciosamente os itens pendentes.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/edge-cases.md#EC-15`
- Código afetado: `caffmob_draw/stick/settle.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 23 (grudar) (BUG-20261011-XPD2, BUG-20261011-XF4S, BUG-20261011-73SM, BUG-20261011-EE4E, BUG-20261011-I3I3, BUG-20261011-TNY3); plano em `_reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** _settle_timer só tratava ReferenceError; outra exceção saía do temporizador sem log.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: stick EC-15.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_XPD2_stick.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/stick/apply.py` | pai trocado, índice por ponteiro, orientação e log | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/stick/link.py` | marca opt_out ao desgrudar da parede | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/stick/migrate.py` | respeita opt_out | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/stick/ops_stick.py` | filtro único stickable | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/stick/panels.py` | painel pelo filtro único | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/stick/props.py` | opt_out | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/stick/settle.py` | respeita opt_out | `CHG-008.diff` |
| CHG-009 | code | `caffmob_draw/ui/context_menu.py` | menu pelo filtro único | `CHG-009.diff` |

**Vermelho (antes da correção):** vínculo órfão com pai trocado; índice velho com hospedeiro renomeado/apagado; regrudado na carga; painel para parede; giro livre mantido; RuntimeError do temporizador.

**Verde (depois):** `blender_bug_XPD2_stick.py` OK; na cópia isolada também `blender_004_stick_smoke`, `blender_bug_ZKQ7_parent_cycle`, `blender_bug_7DHT_wall_delete`, `blender_009_walls_smoke`, `blender_bug_KX3O_collision`, `blender_004_collision_smoke`, `blender_003_move_over_smoke`, `blender_002_smoke`, `test_stick_frame`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_XPD2_stick.py`. **Regressão:** `tests/blender_bug_XPD2_stick.py`, `tests/blender_004_stick_smoke.py`, `tests/blender_bug_ZKQ7_parent_cycle.py`.

## Agent Notes

- Item 46 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
