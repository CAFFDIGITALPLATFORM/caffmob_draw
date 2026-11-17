---
schema_version: 1
id: BUG-20261117-RP9Q
display_number: 152
title: Menu lateral de paredes com estilo antigo; quer botão de toggle moderno
status: open
phase: triaging
severity: medium
priority: P2
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [ui-design, menu-lateral, toggle, estilo-antigo, ux]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (abrir editor de paredes; painel lateral mostra controles padrão do Blender com layout antigo)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13", "_reversa_sdd/walls2d/design.md#Interface"]
  affected_code: ["caffmob_draw/walls2d/panels.py", "caffmob_draw/walls2d/classico_v2.py"]
  root_cause: null
  reproduction_tests: []
  regression_tests: []

spec_verdict: null

change_set: []

closure:
  policy: local-software
  satisfied: false
resolution_kind: null
---
# Menu lateral de paredes com estilo antigo; quer botão de toggle moderno

## Summary

O titular considera que o menu lateral do Editor de Paredes tem um "estilo antigo" e pede um visual moderno com botões de toggle de verdade (ao invés de controles padrão `layout.prop` do Blender). Além disso, relata que ao tocar em "Mover" e selecionar uma parede ocorre um erro (imagem em anexo no relato).

## Expected Behavior

- Menu lateral com visual moderno: botões de toggle com feedback visual (ativo/inativo), ícones claros, layout organizado
- Ferramenta Mover funciona sem erro ao selecionar uma parede

## Actual Behavior

- Painel lateral usa controles padrão do Blender (`layout.prop`) com aparência antiga
- Erro ao usar Mover + selecionar parede: `AttributeError: 'WallPlan' object has no attribute 'move_segments'` (já corrigido no BUG-20261117-JXDJ)

## Steps to Reproduce

1. Abrir o Editor de Paredes
2. Observar o menu lateral (Ferramentas, Painel, Grid, Confirmar)
3. Tocar em "Mover" e selecionar uma parede → erro (já corrigido)

## Evidence

- Relatório do usuário com imagem em anexo (Relatório: Erro)
- Código: `caffmob_draw/walls2d/panels.py` e `caffmob_draw/walls2d/classico_v2.py` usam `layout.prop` em todo o painel

## Suspected Area

`caffmob_draw/walls2d/panels.py` (painéis do editor do addon) e `caffmob_draw/walls2d/classico_v2.py` (painéis da cena v2) — ambos desenham a UI com controles padrão do Blender sem estilo moderno de toggle.

## Acceptance Criteria

- Menu lateral com botões de toggle modernos (feedback visual ativo/inativo)
- Ícones e labels claros para cada ferramenta
- Layout organizado e consistente com o restante da UI do addon
- Nenhuma regressão na funcionalidade existente

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13` (desenho da planta e painéis laterais), `_reversa_sdd/walls2d/design.md#Interface`
- Código suspeito: `caffmob_draw/walls2d/panels.py`, `caffmob_draw/walls2d/classico_v2.py`

## Resolution

A preencher pelo `/reversa-debugger-fix`.

## Agent Notes

- O erro de `move_segments` (WallPlan) já foi corrigido no BUG-20261117-JXDJ; este bug foca no design visual do menu lateral
- É um pedido de UX/design, não um defeito de comportamento: provavelmente `spec-gap` para especificar o estilo moderno
- Consultar `docs/rag/` para diretrizes de UI do addon, se existirem