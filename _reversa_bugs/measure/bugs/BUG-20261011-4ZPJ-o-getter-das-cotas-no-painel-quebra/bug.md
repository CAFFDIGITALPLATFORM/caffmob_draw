---
schema_version: 1
id: BUG-20261011-4ZPJ
display_number: 133
title: "O getter das cotas no painel quebra o desenho"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: measure
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["cotas de módulo: validação mais estrita e obstáculos com largura real", "sem dado persistido"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/measure/edge-cases.md#EC-08"]
  affected_code: ["caffmob_draw/ui/object_properties.py"]
  root_cause:
    state: confirmed
    hypothesis: "_cota_getter constrói ModuleCotas sem try; GeoNodeWall.get_input('Length') levanta ValueError no desenho do painel."
    causal_path:
      - "ui/object_properties.py _cota_getter"
      - "measure/scene_cotas.py ModuleCotas.__init__"
    evidence:
      - ref: evidence/reproduction.md
        observation: "testes vermelhos (Python puro e Blender 5.2) na cópia isolada"
    code_refs:
      - {file: caffmob_draw/ui/object_properties.py, symbol: _cota_getter, commit: 83a6863}
  reproduction_tests: ["tests/test_cotas.py", "tests/blender_bug_NBKB_measure.py"]
  regression_tests: ["tests/test_cotas.py", "tests/blender_bug_NBKB_measure.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_cotas.py
    purpose: "vizinho oposto, teto e campo desconhecido"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_NBKB_measure.py
    purpose: "módulo rápido vizinho; parede quebrada"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/measure/cotas.py
    purpose: "validação do campo, vizinho oposto e teto"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/measure/scene_cotas.py
    purpose: "obstáculos com largura real"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/ui/object_properties.py
    purpose: "getter tolerante a parede quebrada"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/data/translations/measure.json
    purpose: "três mensagens novas"
    diff: _reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/CHG-006.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# O getter das cotas no painel quebra o desenho

## Summary

`_cota_getter` não trata o `ValueError` de `get_input('Length')`.

## Expected Behavior

O getter devolve um valor neutro e o painel desenha.

Spec efetiva: `_reversa_sdd/measure/edge-cases.md#EC-08`.

## Actual Behavior

`_cota_getter` não trata o `ValueError` de `get_input('Length')`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 122.

## Suspected Area

- `caffmob_draw/ui/object_properties.py`

## Acceptance Criteria

- O getter devolve um valor neutro e o painel desenha.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/measure/edge-cases.md#EC-08`
- Código afetado: `caffmob_draw/ui/object_properties.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 18 (cotas de módulo) (BUG-20261011-3W52, BUG-20261011-NBKB, BUG-20261011-4ZPJ, BUG-20261011-WJHO); plano em `_reversa_bugs/measure/bugs/BUG-20261011-3W52-apply-das-cotas-nao-valida-o-vizinho/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `_cota_getter` construía `ModuleCotas` sem tratar o `ValueError` da parede.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: measure EC-08 descreve o erro no desenho como defeito.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_cotas.py` | vizinho oposto, teto e campo desconhecido | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_NBKB_measure.py` | módulo rápido vizinho; parede quebrada | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/measure/cotas.py` | validação do campo, vizinho oposto e teto | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/measure/scene_cotas.py` | obstáculos com largura real | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/ui/object_properties.py` | getter tolerante a parede quebrada | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/data/translations/measure.json` | três mensagens novas | `CHG-006.diff` |

**Vermelho (antes da correção):** `test_cotas` com 1 falha e 1 erro; `blender_bug_NBKB_measure` com 2 falhas no projeto.

**Verde (depois):** `test_cotas` e `test_i18n_coverage` OK, `blender_bug_NBKB_measure: OK`; na cópia isolada também `blender_002_smoke`, `blender_009_walls_smoke`, `blender_003_move_over_smoke`, `blender_bug_TLCT_modal_cancel`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/test_cotas.py`, `tests/blender_bug_NBKB_measure.py`. **Regressão:** `tests/test_cotas.py`, `tests/blender_bug_NBKB_measure.py`.

## Agent Notes

- Item 122 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `measure`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
