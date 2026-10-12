---
schema_version: 1
id: BUG-20261011-35HE
display_number: 31
title: "Textos em português no en_US (customize)"
status: resolved
phase: delivering
severity: low
priority: P3
created: 2026-10-11
updated: 2026-10-11

origin:
  type: inspection
  external_ref: null

area: interface
module: customize
feature: unclassified
labels: ["revisao-specs-2026-10"]

change_risk:
  classification: baixa
  reasons: ["nenhuma mudança de código"]

visibility: normal
security_suspected: false

reproduction:
  classification: not-reproduced
  rate: "0/1 (o aviso já sai em inglês)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261007-FLZO
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/customize/requirements.md"]
  affected_code: ["caffmob_draw/customize/ops_customize.py", "caffmob_draw/customize/ops_library.py"]
  root_cause:
    state: rejected
    hypothesis: "Os seis self.report e o rótulo do menu Frente usam texto literal sem tr(). Refutado como defeito: o Blender 5.2 traduz o texto do report e o text= do layout pelo catálogo registrado, e esses textos já têm entrada em customize.json/geral.json."
    causal_path:
      - "Blender: use_translate_reports/use_translate_interface traduzem pelo dicionário registrado"
    evidence:
      - ref: evidence/reproduction.md
        observation: "teste vermelho na cópia isolada (Blender 5.2, en_US)"
    code_refs:
      - {file: caffmob_draw/customize/ops_library.py, symbol: BTM_OT_ModuleSave, commit: 83a6863}
  reproduction_tests: ["tests/blender_bug_35HE_i18n.py"]
  regression_tests: []

spec_verdict: spec-correta

change_set: []

closure:
  policy: local-software
  satisfied: true
resolution_kind: invalid
---

# Textos em português no en_US (customize)

## Summary

Seis `self.report` com texto literal sem `tr`, e o rótulo de `btm.set_front` também sem `tr`.

## Expected Behavior

Todo texto de UI passa por `tr`/`N_` com entrada no catálogo; no en_US aparece em inglês.

Spec efetiva: `_reversa_sdd/customize/requirements.md`.

## Actual Behavior

Seis `self.report` com texto literal sem `tr`, e o rótulo de `btm.set_front` também sem `tr`.

## Steps to Reproduce

Confirmado por leitura do código, sem reprodução executada. Montar o cenário descrito em Actual Behavior a partir das referências em Traceability; o teste de reprodução fica com o fix.

## Evidence

- `evidence/origem.md`: de onde veio o achado (relato, revisão e referências).
- Relato bruto: `../../intake/relato-20261011-0910.md`, item 20.

## Suspected Area

- `caffmob_draw/customize/ops_customize.py`
- `caffmob_draw/customize/ops_library.py`

## Acceptance Criteria

- Todo texto de UI passa por `tr`/`N_` com entrada no catálogo; no en_US aparece em inglês.
- Um teste de reprodução falha antes da correção e passa depois; o teste de regressão fica em `tests/`.

## Traceability

- Specs: `_reversa_sdd/customize/requirements.md`
- Código afetado: `caffmob_draw/customize/ops_customize.py`, `caffmob_draw/customize/ops_library.py`
- Causa raiz: não investigada (fica com o `/reversa-debugger-fix`).
- Relações propostas:
- related-to → BUG-20261007-FLZO (contexto `plugin-caffmob-draw`), state `proposed`

## Resolution

- **Lote:** 17 (traduções); plano em `_reversa_bugs/stick/bugs/BUG-20261011-JKLK-face-labels-sem-traducao/fix/plan.html`.
- **Causa raiz (rejected):** os textos literais sem `tr()` não deixam a interface em português no en_US: o Blender 5.2 traduz
  o texto de `self.report` (com "Traduzir relatórios") e o `text=` do layout pelo catálogo registrado, e os seis avisos e
  o rótulo "Frente" já têm entrada em `customize.json`/`geral.json`. O teste do lote mostra "Type a name for the module"
  com o código antigo (`evidence/reproduction.md`).
- **Veredito de spec (aprovado por Leonardo Lima em 2026-10-11, aprovação geral dos lotes):** `spec-correta`.
- **resolution_kind:** invalid. Nenhuma mudança de código (a troca para `tr()` foi retirada do lote por ser desnecessária).

## Agent Notes

- Item 20 do relato de 2026-10-11 (revisão das specs de 2026-10-10). Proposta do relato: cosmético. Mantido como low/P3.
- Unit/contexto: `customize`. `feature: unclassified` porque a unit não mapeia para uma única feature do `_reversa_forward/`.
- Quando a referência cita `questions.md`, a decisão do titular já foi aceita: o comportamento esperado acima segue essa decisão.
- Não corrigir neste registro: a correção é do `/reversa-debugger-fix` com os gates do `control_mode: gated`.
