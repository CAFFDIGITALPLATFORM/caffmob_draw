---
schema_version: 1
id: BUG-20261117-744U
display_number: 149
title: Sem botão de imprimir a planta baixa
status: open
phase: triaging
severity: low
priority: P3
created: 2026-11-17
updated: 2026-11-17

origin:
  type: manual-report
  external_ref: null

area: paredes
module: walls2d
feature: 002-editor-parede-mover-sobre
labels: [spec-gap, impressao, exportacao]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código e sondagem MCP no Blender 5.2 instalado: nenhum operador de impressão no editor)"
  suspected_triggers: []

blocking:
  - kind: bug
    target: BUG-20261117-JXDJ

relationships:
  - bug: BUG-20261117-JXDJ
    type: blocked-by
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/operators/layouts.py", "caffmob_draw/ui/view3d_sidebar.py"]
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
# Sem botão de imprimir a planta baixa

## Summary

O titular pede um botão para imprimir a planta baixa. O editor de paredes não tem nenhum botão de impressão ou
exportação da vista.

## Expected Behavior

Pedido do titular (2026-11-17): botão de imprimir a planta baixa a partir do editor.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-13 cobre o desenho da planta e os painéis laterais
(Ferramentas, Painel, Grid, Confirmar) e não menciona impressão nem exportação: `spec-gap` provável.

## Actual Behavior

O painel Confirmar do editor só tem OK e Cancelar. Não há botão, operador nem atalho de impressão.

O que existe, fora do editor: `caffmob_layouts.export_all_to_pdf` (`caffmob_draw/operators/layouts.py:804`, botão em
`caffmob_draw/ui/view3d_sidebar.py:923`), que renderiza layouts para PDF. Não imprime a planta do editor de paredes.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Procurar no painel, na barra superior e no menu de contexto qualquer ação de imprimir ou exportar a planta.

Resultado: não existe.

## Evidence

- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 6).
- `../../intake/relato-20261117-1520.md` e `../../intake/manual-ctb-cores-espessuras-20261117.webp`: espessuras de
  pena do padrão CTB (paredes 0,35 a 0,50 mm; estrutura 0,60 a 0,70 mm; muretas 0,15 a 0,20 mm; acima do corte 0,10 a
  0,15 mm), que a impressão precisa respeitar.
- Código lido: `caffmob_draw/operators/layouts.py` (`export_all_to_pdf`), `caffmob_draw/ui/view3d_sidebar.py`.
- `../../intake/sondagem-mcp-20261117.md`: nenhum operador `caffmob.*` de imprimir ou exportar a planta do editor;
  `export_cut_plan_json` é plano de corte de peças.

## Suspected Area

Funcionalidade inexistente. Depende da decisão do que é "a planta baixa" a imprimir (ver BUG-20261117-JXDJ).

## Acceptance Criteria

- O editor tem uma ação de imprimir a planta baixa, com o mesmo conteúdo que a tela mostra.
- A saída respeita a unidade do projeto e o enquadramento atual da vista.
- Cancelar o diálogo de impressão não altera o rascunho nem a cena.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/operators/layouts.py`,
  `caffmob_draw/ui/view3d_sidebar.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`

## Resolution

A preencher pelo `/reversa-debugger-fix`.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (low/P3), a confirmar pelo titular.
- Bloqueio: o conteúdo impresso depende de qual planta baixa existir (BUG-20261117-JXDJ). Se a impressão sair antes,
  imprime a planta de paredes atual.
- Reaproveitar `export_all_to_pdf` reduz o custo: ele já sabe renderizar e salvar em PDF.
