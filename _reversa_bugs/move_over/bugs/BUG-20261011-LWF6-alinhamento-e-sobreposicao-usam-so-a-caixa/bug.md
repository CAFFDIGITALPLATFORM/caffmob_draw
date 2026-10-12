---
schema_version: 1
id: BUG-20261011-LWF6
display_number: 128
title: "Alinhamento e sobreposição usam só a caixa da raiz"
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
module: move_over
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: média
  reasons: ["alinhamento e sobreposição passam a contar frentes e puxadores (posições alinhadas podem mudar alguns mm)", "peças vazias (tampo/avental desligados) ficam fora da caixa"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/move_over/tasks.md#DT-02", "_reversa_sdd/questions.md#pergunta-16"]
  affected_code: ["caffmob_draw/move_over/align.py", "caffmob_draw/move_over/scene.py"]
  root_cause:
    state: confirmed
    hypothesis: "scene._local_box e overlapping usavam o bound_box só da raiz; frentes e puxadores que saem da caixa ficavam fora, ao contrário do Substituir."
    causal_path:
      - "move_over/scene.py _local_box/original_box_a/overlapping"
      - "move_over/ops_substitute.py _tree_box"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/move_over/scene.py, symbol: _local_box, commit: 0126c64}
      - {file: caffmob_draw/move_over/scene.py, symbol: MoveOver.overlapping, commit: 0126c64}
  reproduction_tests: ["tests/test_canvas2d_view.py", "tests/blender_bug_LWF6_move_over.py", "tests/blender_bug_LM42_canvas2d.py"]
  regression_tests: ["tests/test_canvas2d_view.py", "tests/blender_bug_LWF6_move_over.py", "tests/blender_bug_LM42_canvas2d.py", "tests/blender_003_move_over_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_LM42_canvas2d.py
    purpose: "fechar com janela única"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_LWF6_move_over.py
    purpose: "caixas pela árvore, Substituir sem escala e medida digitada"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-002.diff
  - id: CHG-003
    kind: test
    artifact: tests/test_canvas2d_view.py
    purpose: "fit com área sem lado"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/canvas2d/view.py
    purpose: "piso de escala no fit"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/canvas2d/window.py
    purpose: "volta à vista 3D"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-005.diff
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/geometry_free/ops_create.py
    purpose: "canto mantido e medida limitada"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-006.diff
  - id: CHG-007
    kind: code
    artifact: caffmob_draw/move_over/ops_substitute.py
    purpose: "posição e rotação de A sem escala"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-007.diff
  - id: CHG-008
    kind: code
    artifact: caffmob_draw/move_over/scene.py
    purpose: "tree_corners nas caixas e na sobreposição"
    diff: _reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/CHG-008.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Alinhamento e sobreposição usam só a caixa da raiz

## Summary

O Substituir usa a árvore visível.

## Expected Behavior

As caixas incluem a árvore de malhas visíveis, como o Substituir.

Spec efetiva: `_reversa_sdd/move_over/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-16`.

## Actual Behavior

O Substituir usa a árvore visível.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 117.

## Suspected Area

- `caffmob_draw/move_over/align.py`
- `caffmob_draw/move_over/scene.py`

## Acceptance Criteria

- As caixas incluem a árvore de malhas visíveis, como o Substituir.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/move_over/tasks.md#DT-02`, `_reversa_sdd/questions.md#pergunta-16`
- Código afetado: `caffmob_draw/move_over/align.py`, `caffmob_draw/move_over/scene.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 31 (Mover Sobre, geometria livre e telas 2D) (BUG-20261011-LWF6, BUG-20261011-X5OS, BUG-20261011-NOAU, BUG-20261011-LM42, BUG-20261011-S6I6); plano em `_reversa_bugs/move_over/bugs/BUG-20261011-LWF6-alinhamento-e-sobreposicao-usam-so-a-caixa/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** scene._local_box e overlapping usavam o bound_box só da raiz; frentes e puxadores que saem da caixa ficavam fora, ao contrário do Substituir.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 16 e move_over DT-02 (EC-15).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_LM42_canvas2d.py` | fechar com janela única | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_LWF6_move_over.py` | caixas pela árvore, Substituir sem escala e medida digitada | `CHG-002.diff` |
| CHG-003 | test | `tests/test_canvas2d_view.py` | fit com área sem lado | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/canvas2d/view.py` | piso de escala no fit | `CHG-004.diff` |
| CHG-005 | code | `caffmob_draw/canvas2d/window.py` | volta à vista 3D | `CHG-005.diff` |
| CHG-006 | code | `caffmob_draw/geometry_free/ops_create.py` | canto mantido e medida limitada | `CHG-006.diff` |
| CHG-007 | code | `caffmob_draw/move_over/ops_substitute.py` | posição e rotação de A sem escala | `CHG-007.diff` |
| CHG-008 | code | `caffmob_draw/move_over/scene.py` | tree_corners nas caixas e na sobreposição | `CHG-008.diff` |

**Vermelho (antes da correção):** caixas de A e B sem a porta e sobreposição não vista; escala 1,5 herdada; canto deslocado e 15 m aceitos; área ficou Image Editor; escala 0 no fit.

**Verde (depois):** `test_canvas2d_view.py` OK, `blender_bug_LWF6_move_over.py` OK, `blender_bug_LM42_canvas2d.py` OK; na cópia isolada também `blender_003_move_over_smoke`, `blender_bug_CKVJ_move_over_dialog`, `test_move_over_align` e `blender_002_smoke`; LM42 com janela (xvfb); `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/test_canvas2d_view.py`, `tests/blender_bug_LWF6_move_over.py`, `tests/blender_bug_LM42_canvas2d.py`. **Regressão:** `tests/test_canvas2d_view.py`, `tests/blender_bug_LWF6_move_over.py`, `tests/blender_bug_LM42_canvas2d.py`, `tests/blender_003_move_over_smoke.py`.

## Agent Notes

- Item 117 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: moderado. Mantido como medium/P2.
- Unit/contexto: `move_over`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
