---
schema_version: 1
id: BUG-20261011-73SM
display_number: 54
title: "Item desgrudado de parede é regrudado na carga"
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

relationships:
  - bug: BUG-20261011-XPD2
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/stick/tasks.md#DT-03"]
  affected_code: ["caffmob_draw/stick/settle.py", "caffmob_draw/stick/migrate.py", "caffmob_draw/stick/link.py"]
  root_cause:
    state: confirmed
    hypothesis: "release não deixava marca; settle.run e migrate.run regrudavam na parede todo módulo solto filho dela."
    causal_path:
      - "stick/settle.py run"
      - "stick/migrate.py run"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/stick/link.py, symbol: release, commit: 9674896}
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

# Item desgrudado de parede é regrudado na carga

## Summary

Depois de `link.release` de um item cujo `orig_parent` é parede, `settle.run` e `migrate.run` regrudam o item na carga.

## Expected Behavior

Item desgrudado continua solto depois de salvar e recarregar.

Spec efetiva: `_reversa_sdd/stick/tasks.md#DT-03`.

## Actual Behavior

Depois de `link.release` de um item cujo `orig_parent` é parede, `settle.run` e `migrate.run` regrudam o item na carga.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 43.

## Suspected Area

- `caffmob_draw/stick/settle.py`
- `caffmob_draw/stick/migrate.py`
- `caffmob_draw/stick/link.py`

## Acceptance Criteria

- Item desgrudado continua solto depois de salvar e recarregar.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/stick/tasks.md#DT-03`
- Código afetado: `caffmob_draw/stick/settle.py`, `caffmob_draw/stick/migrate.py`, `caffmob_draw/stick/link.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-XPD2 (contexto `stick`), state `proposed`

## Resolution

- **Lote:** 23 (grudar) (BUG-20261011-XPD2, BUG-20261011-XF4S, BUG-20261011-73SM, BUG-20261011-EE4E, BUG-20261011-I3I3, BUG-20261011-TNY3); plano em `_reversa_bugs/stick/bugs/BUG-20261011-XPD2-vinculo-de-grudar-orfao-quando-o-pai/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** release não deixava marca; settle.run e migrate.run regrudavam na parede todo módulo solto filho dela.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 38 e stick DT-03.
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

- Item 43 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `stick`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
