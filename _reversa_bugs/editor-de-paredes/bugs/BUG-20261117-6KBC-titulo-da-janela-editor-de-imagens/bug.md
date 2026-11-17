---
schema_version: 1
id: BUG-20261117-6KBC
display_number: 144
title: Janela do editor mostra Editor de Imagens em vez de Editor de Paredes CAFF MOB DRAW
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
labels: [spec-gap, interface, titulo-da-janela]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (captura do titular e sondagem MCP no Blender 5.2 instalado, 2026-11-17)"
  suspected_triggers: []

blocking: []

relationships: []

traceability:
  specs: ["_reversa_sdd/walls2d/requirements.md#RF-02", "_reversa_sdd/walls2d/design.md#Interface"]
  affected_code: ["caffmob_draw/canvas2d/window.py", "caffmob_draw/walls2d/window.py"]
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
# Janela do editor mostra Editor de Imagens em vez de Editor de Paredes CAFF MOB DRAW

## Summary

A janela do Editor de Paredes aparece com o título do editor de imagens do Blender ("Editor de Imagens"), e não com o
nome do editor. O titular pede "Editor de Paredes CAFF MOB DRAW" (TT 001).

## Expected Behavior

Pedido do titular (2026-11-17): a janela do editor deve se chamar "Editor de Paredes CAFF MOB DRAW".

Spec efetiva: `_reversa_sdd/walls2d/requirements.md` RF-02 descreve abrir o editor (ler paredes, converter a camada
nova, criar a sessão, abrir a janela, iniciar o modal) sem dizer nada sobre o título da janela; o guia do usuário só
diz que "o editor abre numa janela própria". Nenhum requisito cobre o nome exibido: `spec-gap` provável.

## Actual Behavior

A barra da janela do editor mostra "Editor de Imagens" (marcado com seta vermelha na captura do titular).

O texto é o nome traduzido do tipo de área `IMAGE_EDITOR` do Blender: `caffmob_draw/canvas2d/window.py:prepare` faz
`area.type = 'IMAGE_EDITOR'` e esconde cabeçalho, menus e barras. Nenhuma linha do add-on desenha ou define um título
próprio para a janela.

## Steps to Reproduce

1. Abrir o Editor de Paredes (Construir > Editor de Paredes).
2. Olhar o topo da janela nova.

Resultado: "Editor de Imagens".

## Evidence

- `evidence/titulo-editor-de-imagens.webp`: captura do titular, com a seta vermelha sobre o título.
- `../../intake/sondagem-mcp-20261117.md`: no Blender 5.2 instalado, `pgettext_iface("Image Editor")` devolve
  "Editor de Imagens" com locale `pt_BR`, e `window.title` não existe.
- Relato bruto: `../../intake/relato-20261117-1430.md` (Problema 1).

## Suspected Area

`caffmob_draw/canvas2d/window.py:prepare` (troca do tipo de área) e `caffmob_draw/walls2d/window.py`
(`EDITOR_CATEGORY`, `open_editor`). A mecânica de janela é compartilhada com o Editor de Armário
(`caffmob_draw/cabinet_editor/window.py`), então qualquer mudança em `canvas2d` afeta os dois.

## Acceptance Criteria

- A janela do Editor de Paredes exibe "Editor de Paredes CAFF MOB DRAW" no lugar de "Editor de Imagens".
- O editor de armário não é renomeado por essa mudança sem decisão própria.
- Fechar o editor devolve a área 3D ao estado anterior, como hoje.

## Traceability

- Specs: `_reversa_sdd/walls2d/requirements.md#RF-02`, `_reversa_sdd/walls2d/design.md#Interface`
- Código suspeito: `caffmob_draw/canvas2d/window.py`, `caffmob_draw/walls2d/window.py`
- Testes existentes relacionados: `tests/blender_002_smoke.py`, `tests/test_identity.py`

## Resolution

A preencher pelo `/reversa-debugger-fix`.

## Agent Notes

- Severidade e prioridade propostas pelo agente nesta triagem (low/P3), a confirmar pelo titular.
- O texto não vem do add-on: vem do tipo de área do Blender. Antes de codar, confirmar em `docs/rag/` se a API 5.2
  oferece título por janela (`window.title`, `screen.name`, `wm.window_new`) ou se o caminho é desenhar o título dentro
  da área do editor, no `draw_plan`, que já desenha a barra superior.
- Se a única saída for desenhar dentro da área, decidir com o titular se o nome do tipo de área pode continuar visível
  na barra de título do sistema, porque isso não é controlável por add-on.
