---
schema_version: 1
id: BUG-20261117-6OXN
display_number: 147
title: Editor de parede só no tema escuro, sem opção de fundo branco
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
labels: [spec-gap, interface, tema]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (leitura do código e sondagem MCP no Blender 5.2 instalado: nenhuma propriedade de tema, fundo ou cor na sessão)"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261117-JXDJ
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-13"]
  affected_code: ["caffmob_draw/walls2d/ops_editor.py", "caffmob_draw/walls2d/classico_v2.py", "caffmob_draw/walls2d/props.py"]
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
# Editor de parede só no tema escuro, sem opção de fundo branco

## Summary

O titular pede a opção de trocar a cor do editor, que hoje é sempre escuro, para branco.

## Expected Behavior

Pedido do titular (2026-11-17): opção de escolher a cor do editor, que hoje prevalece preto, incluindo branco.

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-13 descreve o desenho da planta e os painéis (Ferramentas,
Painel, Grid, Confirmar) e não trata de tema ou cor de fundo: `spec-gap` provável.

## Actual Behavior

O fundo é um valor fixo da paleta: `draw_plan` pinta a região inteira com `COLORS['background']`
(`caffmob_draw/walls2d/ops_editor.py`) e o caminho v2 faz o mesmo em `classico_v2.desenhar`. Não existe preferência,
toggle na sessão nem no painel Grid para trocar o tema.

As cores das linhas (parede, seleção, grade, referência) também são fixas na paleta: um fundo branco sem revisar o
contraste deixaria rótulos e linhas claras ilegíveis.

## Steps to Reproduce

1. Abrir o Editor de Paredes.
2. Procurar em qualquer painel do editor uma opção de cor de fundo ou tema claro.

Resultado: não existe.

## Evidence

- `../../intake/editor-de-paredes-titulo-e-ferramentas-20261117.webp`: fundo escuro no editor, sem controle de cor.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 4).
- `../../intake/sondagem-mcp-20261117.md`: a sessão `btm_wall_editor` do addon instalado não tem nenhuma propriedade
  com `theme`, `background` ou `color`.

## Suspected Area

`caffmob_draw/walls2d/ops_editor.py` (`COLORS`, `draw_plan`), `classico_v2.py` (desenho da cena v2), `props.py`
(onde caberia a preferência da sessão).

## Acceptance Criteria

- Uma opção no editor alterna entre tema escuro e tema claro (fundo branco).
- Com o tema claro, linhas, rótulos de medida, grade, seleção e mensagens continuam legíveis (contraste conferido nos
  dois temas).
- A escolha sobrevive ao fechar e reabrir o editor, sem gravar dados da cena.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-13`
- Código suspeito: `caffmob_draw/walls2d/ops_editor.py`, `caffmob_draw/walls2d/classico_v2.py`,
  `caffmob_draw/walls2d/props.py`
- Testes existentes relacionados: `tests/blender_002_ui_events.py`

## Resolution

A preencher pelo `/reversa-debugger-fix`.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (low/P3), a confirmar pelo titular.
- Não basta trocar o fundo: a paleta inteira precisa de dois conjuntos coerentes, senão o tema claro nasce ilegível.
  O ponto de mudança tem de ser único, compartilhado por `ops_editor` e `classico_v2`.
- Guardar a preferência pelo caminho de preferências já usado pelo add-on (`bpy.utils.extension_path_user` para
  arquivos do usuário), e não em propriedades da cena.
