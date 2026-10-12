---
schema_version: 1
id: BUG-20261011-TLPN
display_number: 15
title: "Remover Vértice deixa a parede antiga órfã na cena"
status: resolved
phase: delivering
severity: critical
priority: P0
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: paredes
module: walls2d
feature: unclassified
labels: ["revisao-specs-2026-10", "decisao-do-titular"]

change_risk:
  classification: baixa
  reasons: ["rascunho do editor em memória; só o OK grava", "mesma regra que o Delete já usa", "preserva as mudanças locais da feature 013 em ops_editor.py"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/edge-cases.md#EC-01", "_reversa_sdd/walls2d/tasks.md#DT-01", "_reversa_sdd/questions.md#pergunta-1", "caffmob_draw/walls2d/model.py#L260-L271", "caffmob_draw/walls2d/ops_editor.py#L718-L726"]
  affected_code: ["caffmob_draw/walls2d/model.py", "caffmob_draw/walls2d/ops_editor.py"]
  root_cause:
    state: confirmed
    hypothesis: "Chain.remove_node apaga o trecho e não devolve nada; a ferramenta Remover Vértice chama o modelo direto e ninguém registra o source em plan.removed_sources, então apply_plan não remove a parede original."
    causal_path:
      - "walls2d/model.py Chain.remove_node: del self.segments[...] sem devolver o trecho"
      - "walls2d/ops_editor.py ferramenta REMOVE_NODE: s.plan.chains[ci].remove_node(k) sem registrar o source"
      - "walls2d/apply.py apply_plan: só remove o que está em removed_sources"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada do projeto (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/walls2d/model.py, symbol: Chain.remove_node, commit: 83a6863}
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: BTM_OT_WallEditorModal (REMOVE_NODE), commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_TLPN_remove_node.py"]
  regression_tests: ["tests/blender_bug_TLPN_remove_node.py", "tests/test_walls2d_model.py", "tests/blender_009_walls_smoke.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/test_walls2d_model.py
    purpose: "remove_node devolve o trecho eliminado"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-TLPN-remover-vertice-deixa-a-parede-antiga-orfa/fix/CHG-001.diff
  - id: CHG-002
    kind: test
    artifact: tests/blender_bug_TLPN_remove_node.py
    purpose: "reprodução e regressão do lote"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-TLPN-remover-vertice-deixa-a-parede-antiga-orfa/fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/walls2d/model.py
    purpose: "remove_node devolve o trecho"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-TLPN-remover-vertice-deixa-a-parede-antiga-orfa/fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/walls2d/ops_editor.py
    purpose: "helper remove_node registra o source; remove_segment limpa a seleção"
    diff: _reversa_bugs/walls2d/bugs/BUG-20261011-TLPN-remover-vertice-deixa-a-parede-antiga-orfa/fix/CHG-004.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Remover Vértice deixa a parede antiga órfã na cena

## Summary

`model.remove_node` não põe o `source` do trecho eliminado em `plan.removed_sources`, ao contrário do que `remove_segment` faz. A parede original fica na cena, fora do rascunho e sobreposta ao trecho novo.

## Expected Behavior

Remover Vértice registra o `source` do trecho eliminado em `removed_sources`, como o Delete; ao aplicar, a parede original é removida.

Spec efetiva: `_reversa_sdd/walls2d/edge-cases.md#EC-01`, `_reversa_sdd/walls2d/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-1`, `caffmob_draw/walls2d/model.py#L260-L271`, `caffmob_draw/walls2d/ops_editor.py#L718-L726`.

## Actual Behavior

`model.remove_node` não põe o `source` do trecho eliminado em `plan.removed_sources`, ao contrário do que `remove_segment` faz. A parede original fica na cena, fora do rascunho e sobreposta ao trecho novo.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 4.

## Suspected Area

- `caffmob_draw/walls2d/model.py`
- `caffmob_draw/walls2d/ops_editor.py`

## Acceptance Criteria

- Remover Vértice registra o `source` do trecho eliminado em `removed_sources`, como o Delete; ao aplicar, a parede original é removida.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/walls2d/edge-cases.md#EC-01`, `_reversa_sdd/walls2d/tasks.md#DT-01`, `_reversa_sdd/questions.md#pergunta-1`, `caffmob_draw/walls2d/model.py#L260-L271`, `caffmob_draw/walls2d/ops_editor.py#L718-L726`
- Código afetado: `caffmob_draw/walls2d/model.py`, `caffmob_draw/walls2d/ops_editor.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- nenhuma

## Resolution

- **Lote:** 3 (editor de paredes) (BUG-20261011-TLPN, BUG-20261011-GKUE); plano em `_reversa_bugs/walls2d/bugs/BUG-20261011-TLPN-remover-vertice-deixa-a-parede-antiga-orfa/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** `Chain.remove_node` apagava o trecho sem devolvê-lo e a ferramenta Remover Vértice não registrava o `source` em `removed_sources`; `apply_plan` deixava a parede original órfã.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11):** `spec-correta`: questions.md pergunta 1 e walls2d EC-01/DT-01 já definiam o registro do source.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/test_walls2d_model.py` | remove_node devolve o trecho eliminado | `CHG-001.diff` |
| CHG-002 | test | `tests/blender_bug_TLPN_remove_node.py` | reprodução e regressão do lote | `CHG-002.diff` |
| CHG-003 | code | `caffmob_draw/walls2d/model.py` | remove_node devolve o trecho | `CHG-003.diff` |
| CHG-004 | code | `caffmob_draw/walls2d/ops_editor.py` | helper remove_node registra o source; remove_segment limpa a seleção | `CHG-004.diff` |

**Vermelho (antes da correção):** `test_walls2d_model` falhou; `blender_bug_TLPN_remove_node` com 3 falhas no projeto (4 → 4 paredes, `removed_sources` vazio, seleção (0, 1)).

**Verde (depois):** `test_walls2d_model` + `test_walls2d_history` OK; `blender_bug_TLPN_remove_node: OK`; `blender_009_walls_smoke: OK`; na cópia isolada também `blender_002_smoke`, `blender_002_ui_events`, `blender_bug_ZZUK_undo` e `blender_013_touchpad_smoke` (xvfb, `--enable-event-simulate`); `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_TLPN_remove_node.py`. **Regressão:** `tests/blender_bug_TLPN_remove_node.py`, `tests/test_walls2d_model.py`, `tests/blender_009_walls_smoke.py`.

## Agent Notes

- Item 4 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: crítico. Mantido como critical/P0.
- Unit/contexto: `walls2d`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
