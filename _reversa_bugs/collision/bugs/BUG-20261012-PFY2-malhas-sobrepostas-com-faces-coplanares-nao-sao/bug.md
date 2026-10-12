---
schema_version: 1
id: BUG-20261012-PFY2
display_number: 140
title: "Malhas sobrepostas com faces coplanares não são confirmadas pela BVH da colisão"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-12
updated: 2026-10-12

origin:
  type: inspection
  external_ref: null

area: modulos
module: collision
feature: unclassified
labels: ["achado-lateral-fix-2026-10", "reproduzido"]

change_risk:
  classification: baixa
  reasons: ["mesma confirmação, com triângulos em vez de quads", "encostado continua sem colisão (coberto no teste)"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-EWKD
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/collision/requirements.md#RN-09"]
  affected_code: ["caffmob_draw/collision/scan.py"]
  root_cause:
    state: confirmed
    hypothesis: "_Meshes._build montava a BVH por BVHTree.FromPolygons com os quads da malha; com faces coplanares sobrepostas, overlap() não acha pares entre quads, embora ache entre os triângulos (BVHTree.FromObject triangula)."
    causal_path:
      - "collision/scan.py _Meshes._build"
      - "collision/scan.py _confirm (ta.overlap(tb))"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/collision/scan.py, symbol: _Meshes._build, commit: cde31ac}
  reproduction_tests: ["tests/blender_bug_PFY2_collision.py"]
  regression_tests: ["tests/blender_bug_PFY2_collision.py", "tests/blender_004_collision_smoke.py", "tests/test_collision_rules.py"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_PFY2_collision.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/collision/bugs/BUG-20261012-PFY2-malhas-sobrepostas-com-faces-coplanares-nao-sao/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/collision/scan.py
    purpose: "BVH por triângulos"
    diff: _reversa_bugs/collision/bugs/BUG-20261012-PFY2-malhas-sobrepostas-com-faces-coplanares-nao-sao/fix/CHG-002.diff
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Malhas sobrepostas com faces coplanares não são confirmadas pela BVH da colisão

## Summary

Dois cubos de 1 m soltos (malhas sem pai, confirmados pela malha real) com a mesma altura e profundidade, sobrepostos em X, só viram colisão quando a sobreposição é grande (0,5 m). Com 0,2, 0,1 ou 0,05 m a verificação não acusa nada, embora `BVHTree.FromObject` ache 2 pares em todos os casos. O `_Meshes._build` monta a BVH por `BVHTree.FromPolygons` com os quads; o caso coplanar escapa.

## Expected Behavior

Par fino que se sobrepõe de fato vira ocorrência (RN-09), também quando as faces de cima, de baixo e laterais são coplanares.

Spec efetiva: `_reversa_sdd/collision/requirements.md#RN-09`.

## Actual Behavior

Dois cubos de 1 m soltos (malhas sem pai, confirmados pela malha real) com a mesma altura e profundidade, sobrepostos em X, só viram colisão quando a sobreposição é grande (0,5 m). Com 0,2, 0,1 ou 0,05 m a verificação não acusa nada, embora `BVHTree.FromObject` ache 2 pares em todos os casos. O `_Meshes._build` monta a BVH por `BVHTree.FromPolygons` com os quads; o caso coplanar escapa.

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 3.

## Suspected Area

- `caffmob_draw/collision/scan.py`

## Acceptance Criteria

- Par fino que se sobrepõe de fato vira ocorrência (RN-09), também quando as faces de cima, de baixo e laterais são coplanares.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/collision/requirements.md#RN-09`
- Código afetado: `caffmob_draw/collision/scan.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-EWKD (contexto `collision`, travado), state `proposed`

## Resolution

- **Lote:** 33 (colisão coplanar) (BUG-20261012-PFY2); plano em `_reversa_bugs/collision/bugs/BUG-20261012-PFY2-malhas-sobrepostas-com-faces-coplanares-nao-sao/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** _Meshes._build montava a BVH por BVHTree.FromPolygons com os quads da malha; com faces coplanares sobrepostas, overlap() não acha pares entre quads, embora ache entre os triângulos (BVHTree.FromObject triangula).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-12):** `spec-correta`: collision RN-09 (par fino que se sobrepõe vira ocorrência).
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_PFY2_collision.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/collision/scan.py` | BVH por triângulos | `CHG-002.diff` |

**Vermelho (antes da correção):** sobreposições de 0,20, 0,10 e 0,05 m entre cubos com faces coplanares não viraram colisão.

**Verde (depois):** `blender_bug_PFY2_collision.py` OK; na cópia isolada também `blender_bug_KX3O_collision`, `test_collision_rules` e `blender_004_collision_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_PFY2_collision.py`. **Regressão:** `tests/blender_bug_PFY2_collision.py`, `tests/blender_004_collision_smoke.py`, `tests/test_collision_rules.py`.

## Agent Notes

- Item 3 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade medium/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
