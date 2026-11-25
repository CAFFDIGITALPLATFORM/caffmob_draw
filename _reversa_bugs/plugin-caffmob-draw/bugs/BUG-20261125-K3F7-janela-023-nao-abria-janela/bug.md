---
schema_version: 1
id: BUG-20261125-K3F7
display_number: 163
title: Janela do construtor 023 não abria janela própria e não entregava o mockup
status: resolved
phase: closed
severity: high
priority: P1
created: 2026-11-25
updated: 2026-11-25

origin:
  type: inspection
  external_ref: null

area: plugin
module: armario_v2
feature: 023-janela-mockup-construtor
labels: [interface, janela, mockup, spec-correta]
visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: ["abrir o Construtor de Armários pelo operador de janela no Blender 5.2"]

blocking: []

relationships: []

traceability:
  specs:
    - "_reversa_forward/023-janela-mockup-construtor/requirements.md#5. Requisitos Funcionais"
    - "_reversa_forward/023-janela-mockup-construtor/roadmap.md#3. Decisões técnicas"
  affected_code:
    - caffmob_draw/armario_v2/window.py
    - caffmob_draw/armario_v2/ops_window.py
    - caffmob_draw/armario_v2/panel_window.py
    - caffmob_draw/armario_v2/preview.py
    - caffmob_draw/armario_v2/props.py
    - caffmob_draw/armario_v2/panel.py
  root_cause:
    state: confirmed
    hypothesis: "`open_editor` convertia a primeira área VIEW_3D em IMAGE_EDITOR no lugar em vez de usar
      `canvas2d.window.open_window` (o caminho do Editor de Paredes); o operador de abertura não tinha chamador na
      interface; a categoria do painel não era focada; as abas nasciam fechadas; e o preview não desenhava peças
      com o deslocamento/ordem corretos."
    causal_path:
      - "open_editor trocava o tipo da área 3D e guardava restore_area_type='VIEW_3D'"
      - "nenhuma referência a caffmob.armario_v2_window_open em painel, menu ou cabeçalho"
      - "canvas2d.window.focus_tab existe e não era chamado; aba medida = UNSUPPORTED"
      - "7 painéis com bl_options DEFAULT_CLOSED"
      - "preview._vista ignorava o deslocamento da vista frontal e o FUNDO era desenhado por cima das peças"
      - "sem handler de mouse, sem GEO-001/GEO-002 e sem largura visível (painel cobria o corte lateral)"
    evidence:
      - ref: "../../../plugin-caffmob-draw/inspections/2026-11-25-janela-023/01_janela_aberta.png"
        observation: "captura antes da correção: 2 janelas antes e depois do invoke, área 3D virou Image Editor"
      - ref: "../../../plugin-caffmob-draw/inspections/2026-11-25-janela-023/04_janela_montada.png"
        observation: "captura depois: janela nova, aba Construtor Armário ativa, peças no preview e peça selecionada"
    code_refs:
      - file: caffmob_draw/armario_v2/window.py
        symbol: open_editor
        commit: null
      - file: caffmob_draw/armario_v2/ops_window.py
        symbol: BTM_OT_ArmarioV2WindowOpen
        commit: null
      - file: caffmob_draw/armario_v2/panel_window.py
        symbol: BTM_PT_ArmarioV2WindowHeader
        commit: null
  reproduction_tests:
    - "python .blender-mcp/_mcp.py _reversa_bugs/plugin-caffmob-draw/inspections/2026-11-25-janela-023/probe_janela_023.py"
    - "cd tests && python -m unittest test_janela_023_core"
  regression_tests:
    - "cd tests && python -m unittest test_janela_023_core"
    - "blender --background --factory-startup --python-exit-code 1 --python tests/blender_017_armario_smoke.py"
    - "blender --background --factory-startup --python-exit-code 1 --python tests/blender_021_mcp_e2e.py"

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: code
    artifact: caffmob_draw/armario_v2/window.py
    purpose: "abrir pelo canvas2d.window.open_window, focar a categoria, guardar hits/seleção e opções de desenho"
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/armario_v2/ops_window.py
    purpose: "modal na janela nova, seleção por clique, alternadores, aviso ao fechar pelo sistema e gate GEO"
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/armario_v2/panel_window.py
    purpose: "barra de título/ferramentas, Estrutura aberta, barra de seleção, lista de peças e rodapé com bloqueio"
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/armario_v2/preview.py
    purpose: "largura visível, offsets corretos, ordem de pintura e registro dos hits"
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/armario_v2/selecao.py + validar.py
    purpose: "núcleos puros de seleção e de GEO-001/GEO-002"
  - id: CHG-006
    kind: code
    artifact: caffmob_draw/armario_v2/panel.py + props.py
    purpose: "botão Abrir Janela no painel da vista 3D; medidas em mm sem subtype DISTANCE"
  - id: CHG-007
    kind: test
    artifact: tests/test_janela_023_core.py
    purpose: "11 ensaios puros de clique e validação geométrica"

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---

# Janela do construtor 023 não abria janela própria e não entregava o mockup

## Summary

A auditoria de 2026-11-25 mediu, no Blender aberto, que o operador da janela convertia a Vista 3D no lugar
(`janelas_antes: 2`, `janelas_depois: 2`), não tinha entrada na interface, abria na categoria errada, nascia com as
7 abas fechadas e desenhava o preview sem peças visíveis. A correção abre uma janela nova pelo caminho do Editor de
Paredes e fecha as lacunas funcionais do mockup.

## Expected Behavior

`RF-01`: nova janela do sistema com o construtor, painel de 7 abas com Estrutura aberta, preview dividido, empty
state e OK/Aplicar/Cancelar. `RF-02`: clique seleciona peça. `RF-03`: GEO-001/GEO-002 bloqueiam OK/Aplicar.

## Actual Behavior (antes)

Área 3D trocada por Image Editor, sem janela nova; operador sem botão; aba `UNSUPPORTED`; peças fora de quadro;
FUNDO cobrindo tudo; sem clique, sem GEO, corte lateral sob o painel.

## Steps to Reproduce

1. Abrir o Blender 5.2 com o add-on e uma cena qualquer.
2. Rodar a sonda `probe_janela_023.py` (MCP 127.0.0.1:9877) ou clicar "Abrir Janela" no painel do armário.
3. Antes da correção: contar janelas antes/depois (2 → 2) e ler a categoria ativa (`UNSUPPORTED`).

## Evidence

- `_reversa_bugs/plugin-caffmob-draw/inspections/2026-11-25-janela-023/` (capturas 01–04 e JSON das sondas).
- Depois: `janelas 1 → 2`, `aba_ativa = "Construtor Armário"`, `hits = 10`, seleção de "Lateral esquerda",
  montagem da caixa com 5 peças.

## Acceptance Criteria

- [x] Abrir cria janela nova (contagem incrementa) e mantém a Vista 3D do usuário.
- [x] Operador tem botão no painel do armário ("Abrir Janela").
- [x] Aba do construtor ativa e Estrutura aberta.
- [x] Preview desenha as peças dentro do quadro, com FUNDO ao fundo.
- [x] Clique seleciona peça e a barra mostra o nome.
- [x] GEO-001/GEO-002 bloqueiam OK/Aplicar.
- [ ] Paridade pixel a pixel com o mockup (pergunta aberta para o `/reversa-clarify`).

## Traceability

`spec-correta`: `RF-01`/`D-01` já exigiam a janela nova; o código é que divergia. Nenhuma spec foi alterada.

## Resolution

Correção aplicada em 2026-11-25. Provas: sonda MCP com contagem de janelas 1 → 2 e aba correta; `probe_editor_021.py`
22/22 (colisão, criação do zero, redimensionamento 5 → 5 sem peça achatada, edições 5 → 33); suíte pura 1593 com
apenas a falha de permissão POSIX no NTFS; `blender_017_armario_smoke.py` OK; `blender_021_mcp_e2e.py` 52/52.

## Agent Notes

A paridade visual total (titlebar própria, abas horizontais, mov-bar) não cabe no Image Editor do Blender sem uma
camada de desenho própria; a decisão entre réplica pixel a pixel e paridade funcional é do titular, no clarify.
