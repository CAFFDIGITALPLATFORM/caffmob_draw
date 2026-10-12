---
schema_version: 1
id: BUG-20261012-YUDY
display_number: 138
title: "Shift+D num módulo repete o btm_uid e as peças dos dois módulos ficam com o mesmo uid"
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-12
updated: 2026-10-12

origin:
  type: inspection
  external_ref: null

area: producao
module: cutting
feature: unclassified
labels: ["achado-lateral-fix-2026-10", "reproduzido", "spec-gap"]

change_risk:
  classification: baixa
  reasons: ["só a cópia com uid repetido muda de uid", "o plano de corte fica marcado como desatualizado quando isso acontece"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261011-SKDL
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/cutting/requirements.md", "_reversa_sdd/geometry_free/edge-cases.md#EC-12"]
  affected_code: ["caffmob_draw/cutting/part_sources.py", "caffmob_draw/cutting/stale.py"]
  root_cause:
    state: confirmed
    hypothesis: "iter_modules usava ensure_module_uid, que só cria uid quando falta; a cópia nativa traz a idprop btm_uid do original e os dois módulos (e suas peças) ficavam com o mesmo uid. A geometria livre já usava _unique_uid."
    causal_path:
      - "cutting/part_sources.py iter_modules"
      - "cutting/part_sources.py ensure_module_uid"
      - "cutting/part_extractor.py extract_production_parts"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho no projeto e na cópia isolada (Blender 5.2)"
    code_refs:
      - {file: caffmob_draw/cutting/part_sources.py, symbol: iter_modules, commit: 38594e6}
  reproduction_tests: ["tests/blender_bug_YUDY_module_uid.py"]
  regression_tests: ["tests/blender_bug_YUDY_module_uid.py", "tests/test_cut_plan_machining.py", "tests/blender_003_aggregates_smoke.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: test
    artifact: tests/blender_bug_YUDY_module_uid.py
    purpose: "reprodução e regressão"
    diff: _reversa_bugs/cutting/bugs/BUG-20261012-YUDY-shift-d-num-modulo-repete-o-btm/fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/cutting/part_sources.py
    purpose: "uid único por módulo"
    diff: _reversa_bugs/cutting/bugs/BUG-20261012-YUDY-shift-d-num-modulo-repete-o-btm/fix/CHG-002.diff
  - id: CHG-003
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261012-YUDY-v001.md
    purpose: "unicidade do btm_uid de módulo"
    diff: _reversa_sdd/addenda/bug-BUG-20261012-YUDY-v001.md
closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Shift+D num módulo repete o btm_uid e as peças dos dois módulos ficam com o mesmo uid

## Summary

Duplicar um módulo CAFFMob pela ferramenta nativa (Shift+D) copia a idprop `btm_uid`. `part_sources.iter_modules` devolve os dois módulos com o mesmo uid, então as peças dos dois (`<btm_uid>/<componente>/<índice>`) colidem na lista de peças e no plano de corte. A geometria livre já ganhou um uid novo na cópia (`_unique_uid`, BUG-20261011-SKDL); o módulo não.

## Expected Behavior

Cada módulo da cena tem um `btm_uid` único: a cópia nativa que trouxe o uid de outro módulo ganha um novo, como já acontece com a geometria livre (geometry_free EC-12).

O comportamento nunca foi especificado para este caso (`spec-gap`): a pergunta "é bug ou nunca foi especificado?" fica aberta para o fix.

Spec efetiva: `_reversa_sdd/cutting/requirements.md`, `_reversa_sdd/geometry_free/edge-cases.md#EC-12`.

## Actual Behavior

Duplicar um módulo CAFFMob pela ferramenta nativa (Shift+D) copia a idprop `btm_uid`. `part_sources.iter_modules` devolve os dois módulos com o mesmo uid, então as peças dos dois (`<btm_uid>/<componente>/<índice>`) colidem na lista de peças e no plano de corte. A geometria livre já ganhou um uid novo na cópia (`_unique_uid`, BUG-20261011-SKDL); o módulo não.

## Steps to Reproduce

Roteiro e saída em `evidence/sonda.md`; o `/reversa-debugger-fix` converte a sonda em teste de reprodução.

## Evidence

- `evidence/sonda.md`: comando e saída da reprodução.
- Relato: `../../intake/relato-20261012-0011.md`, item 1.

## Suspected Area

- `caffmob_draw/cutting/part_sources.py`
- `caffmob_draw/cutting/stale.py`

## Acceptance Criteria

- Cada módulo da cena tem um `btm_uid` único: a cópia nativa que trouxe o uid de outro módulo ganha um novo, como já acontece com a geometria livre (geometry_free EC-12).
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/cutting/requirements.md`, `_reversa_sdd/geometry_free/edge-cases.md#EC-12`
- Código afetado: `caffmob_draw/cutting/part_sources.py`, `caffmob_draw/cutting/stale.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261011-SKDL (contexto `geometry_free`, travado), state `proposed`

## Resolution

- **Lote:** 32 (identidade do módulo) (BUG-20261012-YUDY); plano em `_reversa_bugs/cutting/bugs/BUG-20261012-YUDY-shift-d-num-modulo-repete-o-btm/fix/plan.html`, diffs no mesmo `fix/`.
- **Causa raiz (confirmed):** iter_modules usava ensure_module_uid, que só cria uid quando falta; a cópia nativa traz a idprop btm_uid do original e os dois módulos (e suas peças) ficavam com o mesmo uid. A geometria livre já usava _unique_uid.
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-12):** `spec-gap`: a unicidade do btm_uid de módulo não era especificada; adendo `_reversa_sdd/addenda/bug-BUG-20261012-YUDY-v001.md`.
- **resolution_kind:** fixed

| CHG | tipo | artefato | propósito | diff |
|---|---|---|---|---|
| CHG-001 | test | `tests/blender_bug_YUDY_module_uid.py` | reprodução e regressão | `CHG-001.diff` |
| CHG-002 | code | `caffmob_draw/cutting/part_sources.py` | uid único por módulo | `CHG-002.diff` |
| CHG-003 | specification | `_reversa_sdd/addenda/bug-BUG-20261012-YUDY-v001.md` | unicidade do btm_uid de módulo | `bug-BUG-20261012-YUDY-v001.md` |

**Vermelho (antes da correção):** dois módulos com o uid 4ced2bcfe6d5; 14 peças com 7 uids.

**Verde (depois):** `blender_bug_YUDY_module_uid.py` OK; na cópia isolada também `test_cut_plan_machining`, `blender_003_aggregates_smoke` e, com janela, `blender_006_cabinet_editor_tabs_smoke`; `ruff` limpo; `check_api.py` OK.

- **Reprodução:** `tests/blender_bug_YUDY_module_uid.py`. **Regressão:** `tests/blender_bug_YUDY_module_uid.py`, `tests/test_cut_plan_machining.py`, `tests/blender_003_aggregates_smoke.py`.

## Agent Notes

- Item 1 do relato de 2026-10-12: achado lateral da rodada de correção (lotes 19 a 31), anotado como fora de escopo. Severidade medium/P2 proposta pelo agente e aceita pelo titular.
- `feature: unclassified`: o achado não mapeia para uma única feature do `_reversa_forward/`.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
